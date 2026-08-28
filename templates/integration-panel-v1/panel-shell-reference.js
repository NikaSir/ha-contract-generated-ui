// NikaS Integration Panel Template v1.7
// Canonical copy/adapt reference implementation.
// Production rule: copy/adapt into the integration repository and build one
// self-contained integration-owned frontend bundle. Never import this at runtime.

const APP = {
  title: "Example Panel",
  uiVersion: "1.0.0",
  preferredView: "overview",
  tabs: [
    ["overview", "mdi:view-dashboard-outline", "Обзор"],
    ["control", "mdi:tune", "Управление"],
    ["diagnostics", "mdi:stethoscope", "Диагностика"],
  ],
};

const TONES = new Set(["ok", "active", "warn", "bad", "unknown"]);
const SOURCE_ROUTE_KEY = "nikas.specialized.source_route.v1";
const RETURN_ROUTE_KEY = "nikas.example.return_route.v1";
const SAFE_DEFAULT_ROUTE = "/dashboard-infrastructure/overview";
const SAFE_ROUTE_PREFIXES = ["/dashboard-house", "/dashboard-actions", "/dashboard-infrastructure"];

function safeReturnRoute(value) {
  if (!value) return null;
  try {
    const url = new URL(decodeURIComponent(String(value).trim()), window.location.origin);
    if (url.origin !== window.location.origin) return null;
    return SAFE_ROUTE_PREFIXES.some((prefix) => url.pathname === prefix || url.pathname.startsWith(`${prefix}/`))
      ? `${url.pathname}${url.search}${url.hash}`
      : null;
  } catch (_err) {
    return null;
  }
}

function resolveReturnRoute(panel) {
  const current = new URL(window.location.href);
  const explicit = ["return_to", "from"]
    .map((key) => safeReturnRoute(current.searchParams.get(key)))
    .find(Boolean) || null;
  let handedOff = null;
  let saved = null;
  try {
    handedOff = safeReturnRoute(sessionStorage.getItem(SOURCE_ROUTE_KEY));
    sessionStorage.removeItem(SOURCE_ROUTE_KEY);
    saved = safeReturnRoute(sessionStorage.getItem(RETURN_ROUTE_KEY));
  } catch (_err) {}
  const configured = safeReturnRoute(panel?._panel?.config?.parent_route);
  const route = explicit || handedOff || saved || safeReturnRoute(document.referrer) || configured || SAFE_DEFAULT_ROUTE;
  try { sessionStorage.setItem(RETURN_ROUTE_KEY, route); } catch (_err) {}
  return route;
}

function navigateToSource(panel) {
  const route = safeReturnRoute(panel._returnRoute) || SAFE_DEFAULT_ROUTE;
  window.history.pushState(null, "", route);
  window.dispatchEvent(new Event("location-changed"));
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function sameTreeShape(current, desired) {
  if (!current || !desired || current.nodeType !== desired.nodeType) return false;
  if (current.nodeType === Node.ELEMENT_NODE && current.tagName !== desired.tagName) return false;
  if (current.childNodes.length !== desired.childNodes.length) return false;
  for (let index = 0; index < current.childNodes.length; index += 1) {
    if (!sameTreeShape(current.childNodes[index], desired.childNodes[index])) return false;
  }
  return true;
}

function syncTree(current, desired) {
  if (current.nodeType === Node.TEXT_NODE || current.nodeType === Node.COMMENT_NODE) {
    if (current.nodeValue !== desired.nodeValue) current.nodeValue = desired.nodeValue;
    return;
  }
  if (current.nodeType === Node.ELEMENT_NODE) {
    for (const attribute of [...current.attributes]) {
      if (!desired.hasAttribute(attribute.name)) current.removeAttribute(attribute.name);
    }
    for (const attribute of [...desired.attributes]) {
      if (current.getAttribute(attribute.name) !== attribute.value) current.setAttribute(attribute.name, attribute.value);
    }
  }
  for (let index = 0; index < current.childNodes.length; index += 1) {
    syncTree(current.childNodes[index], desired.childNodes[index]);
  }
}

function commitStableMarkup(root, markup) {
  const template = document.createElement("template");
  template.innerHTML = markup;
  const current = [...root.childNodes];
  const desired = [...template.content.childNodes];
  const compatible = current.length === desired.length && current.every((node, index) => sameTreeShape(node, desired[index]));
  if (!compatible) {
    root.replaceChildren(template.content.cloneNode(true));
    return true;
  }
  current.forEach((node, index) => syncTree(node, desired[index]));
  return false;
}

class NikaSIntegrationPanelReference extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._panel = null;
    this._activeView = APP.preferredView;
    this._selectedDevice = null;
    this._devices = [];
    this._loading = true;
    this._shellMounted = false;
    this._renderQueued = false;
    this._returnRoute = null;
  }

  set hass(value) {
    this._hass = value;
    this._loading = false;
    this._queueRender();
  }

  set panel(value) {
    this._panel = value;
    this._activeView = value?.config?.preferred_view || APP.preferredView;
    this._queueRender();
  }

  connectedCallback() {
    this._queueRender();
  }

  _config() {
    const tabs = (this._panel?.config?.tabs || APP.tabs).slice(0, 5);
    const requestedUiVersion = String(this._panel?.config?.ui_version || APP.uiVersion).replace(/^v/i, "");
    const uiVersion = /^\d+\.\d+\.\d+$/.test(requestedUiVersion) ? requestedUiVersion : APP.uiVersion;
    return {
      title: this._panel?.config?.title || APP.title,
      subtitle: `UI v${uiVersion}`,
      tabs,
    };
  }

  _tone(value) {
    return TONES.has(value) ? value : "unknown";
  }

  _renderHeader() {
    const config = this._config();
    return `<header class="app-header">
      <button type="button" class="header-action" id="menu" aria-label="Меню Home Assistant">
        <ha-icon icon="mdi:menu"></ha-icon>
      </button>
      <button type="button" class="header-title" id="return-source" aria-label="Вернуться в базовую панель NikaS">
        <strong>${esc(config.title)}</strong>
        <span>${esc(config.subtitle)}</span>
      </button>
      <button type="button" class="header-action" id="refresh" aria-label="Обновить">
        <ha-icon icon="mdi:refresh"></ha-icon>
      </button>
    </header>`;
  }

  _renderDeviceSelector() {
    // Optional. Populate this._devices only for peer physical devices owned by
    // one specialized panel. Domain channels/modes are not Device Selector items.
    if (this._devices.length < 2) return "";
    if (!this._selectedDevice) this._selectedDevice = this._devices[0]?.id || null;

    return `<div class="device-selector" role="tablist" aria-label="Устройство">
      ${this._devices.map((device) => {
        const selected = device.id === this._selectedDevice;
        const tone = this._tone(device.tone);
        return `<button type="button" data-device="${esc(device.id)}" class="${selected ? "active" : ""}" role="tab" aria-selected="${selected}">
          <i class="status-dot ${tone}"></i><span>${esc(device.label)}</span>
        </button>`;
      }).join("")}
    </div>`;
  }

  _renderHeroStatus({ status = "Состояние неизвестно", detail = "Нет достоверной телеметрии", tone = "unknown", badge = "" } = {}) {
    const safeTone = this._tone(tone);
    return `<article class="card hero">
      <div class="hero-line">
        <div>
          <div class="hero-state ${safeTone}"><i class="status-dot ${safeTone}"></i>${esc(status)}</div>
          <p>${esc(detail)}</p>
        </div>
        ${badge ? `<span class="status-badge ${safeTone}">${esc(badge)}</span>` : ""}
      </div>
    </article>`;
  }

  _renderMetric(label, value, unit = "", tone = "active", entityId = "") {
    const safeTone = this._tone(tone);
    const entityAttr = entityId ? ` data-entity="${esc(entityId)}" tabindex="0"` : "";
    const missing = value === null || value === undefined || value === "" || value === "unknown" || value === "unavailable";
    const displayValue = missing ? "Нет данных" : `${value}${unit ? ` ${unit}` : ""}`;
    return `<div class="metric ${missing ? "unknown" : safeTone}"${entityAttr}>
      <span>${esc(label)}</span><strong>${esc(displayValue)}</strong>
    </div>`;
  }

  _renderStateRow(icon, label, value, entityId = "") {
    const entityAttr = entityId ? ` data-entity="${esc(entityId)}" tabindex="0"` : "";
    const safeValue = value === null || value === undefined || value === "" ? "Нет данных" : value;
    return `<div class="state-row"${entityAttr}>
      <ha-icon icon="${esc(icon)}"></ha-icon>
      <span>${esc(label)}</span>
      <strong>${esc(safeValue)}</strong>
      <ha-icon class="chevron" icon="mdi:chevron-right"></ha-icon>
    </div>`;
  }

  _renderActionCard(icon, label, detail, actionId) {
    return `<button type="button" class="action-card" data-action="${esc(actionId)}">
      <ha-icon icon="${esc(icon)}"></ha-icon>
      <span><strong>${esc(label)}</strong><small>${esc(detail)}</small></span>
    </button>`;
  }

  _renderAlert(title, text, tone = "warn") {
    const safeTone = this._tone(tone);
    const icon = safeTone === "bad" ? "mdi:alert-circle" : safeTone === "warn" ? "mdi:alert" : "mdi:information-outline";
    return `<div class="alert ${safeTone}">
      <ha-icon icon="${icon}"></ha-icon>
      <div><strong>${esc(title)}</strong><span>${esc(text)}</span></div>
    </div>`;
  }

  _renderDiagramPlaceholder() {
    return `<article class="card diagram">
      <strong>Diagram</strong>
      <span>Используйте схему только если она помогает понять фактическое состояние системы.</span>
    </article>`;
  }

  _renderViewContent() {
    if (this._activeView === "diagnostics") {
      return `<section class="content-grid">
        <article class="card"><h2>Диагностика</h2>
          ${this._renderStateRow("mdi:database-outline", "Источник данных", "Неизвестно")}
          ${this._renderStateRow("mdi:clock-outline", "Последнее обновление", "Нет данных")}
        </article>
      </section>`;
    }

    if (this._activeView === "control") {
      return `<section class="content-grid">
        <article class="card"><h2>Управление</h2>
          ${this._renderAlert("Reference template", "Добавляйте только подтверждённые действия интеграции.", "active")}
        </article>
      </section>`;
    }

    return `<section class="content-grid metrics">
      ${this._renderMetric("Показатель", null, "V", "unknown")}
      ${this._renderMetric("Показатель", null, "%", "unknown")}
    </section>`;
  }

  _renderLoading() {
    return `<section class="loading" aria-live="polite">
      <div class="skeleton hero-skeleton"></div>
      <div class="skeleton row-skeleton"></div>
      <div class="skeleton row-skeleton"></div>
      <span>Загрузка…</span>
    </section>`;
  }

  _renderTabBar() {
    const tabs = this._config().tabs;
    const count = Math.max(1, tabs.length);
    return `<nav class="tabbar" style="--nika-tab-count:${count}" aria-label="Разделы">
      ${tabs.map(([view, icon, label]) => `<button type="button" data-view="${esc(view)}" class="${this._activeView === view ? "active" : ""}" aria-current="${this._activeView === view ? "page" : "false"}">
        <ha-icon icon="${esc(icon)}"></ha-icon><span>${esc(label)}</span>
      </button>`).join("")}
    </nav>`;
  }

  _attachEntityInteractions() {
    this.shadowRoot.querySelectorAll("[data-entity]").forEach((element) => {
      if (element._nikasHoldBound) return;
      element._nikasHoldBound = true;
      let timer = null;
      let fired = false;
      const clear = () => {
        if (timer) window.clearTimeout(timer);
        timer = null;
      };
      const openMoreInfo = () => {
        const entityId = element.dataset.entity;
        if (!entityId) return;
        fired = true;
        this.dispatchEvent(new CustomEvent("hass-more-info", {
          detail: { entityId }, bubbles: true, composed: true,
        }));
      };
      element.addEventListener("pointerdown", () => {
        fired = false;
        clear();
        timer = window.setTimeout(openMoreInfo, 550);
      });
      ["pointerup", "pointercancel", "pointerleave"].forEach((name) => element.addEventListener(name, clear));
      element.addEventListener("click", (event) => {
        if (fired) event.preventDefault();
      });
    });
  }

  _queueRender() {
    if (this._renderQueued) return;
    this._renderQueued = true;
    const schedule = window.requestAnimationFrame || ((callback) => queueMicrotask(callback));
    schedule(() => {
      this._renderQueued = false;
      this._render();
    });
  }

  _mountShell() {
    if (this._shellMounted) return;
    this._returnRoute = resolveReturnRoute(this);
    this.shadowRoot.innerHTML = `<style>${NIKAS_PANEL_CSS}</style>
      <div class="app-shell">
        ${this._renderHeader()}
        <div class="device-selector-slot"></div>
        <main class="canvas-viewport" aria-label="Рабочая область панели">
          <div class="work-canvas"></div>
        </main>
        <div class="bottom-slot"></div>
        <div class="scale-status" role="status" aria-live="polite">Масштаб 100%</div>
      </div>`;

    this.shadowRoot.addEventListener("click", (event) => {
      const button = event.target?.closest?.("button");
      if (!button) return;
      if (button.id === "menu") {
        this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
      } else if (button.id === "return-source") {
        navigateToSource(this);
      } else if (button.id === "refresh") {
        this.dispatchEvent(new CustomEvent("nikas-panel-refresh", { bubbles: true, composed: true }));
      } else if (button.dataset.view) {
        this._activeView = button.dataset.view || APP.preferredView;
        const controller = window.NikasPanelZoom?.attach?.(this);
        if (controller?.resetPosition) controller.resetPosition();
        else this.shadowRoot.querySelector(".canvas-viewport").scrollTop = 0;
        this._queueRender();
      } else if (button.dataset.device) {
        this._selectedDevice = button.dataset.device || this._selectedDevice;
        window.NikasPanelZoom?.attach?.(this)?.contextChanged?.();
        this._queueRender();
      }
    });
    this._shellMounted = true;
  }

  _render() {
    this._mountShell();
    const config = this._config();
    this.shadowRoot.querySelector(".header-title strong").textContent = config.title;
    this.shadowRoot.querySelector(".header-title span").textContent = config.subtitle;
    commitStableMarkup(this.shadowRoot.querySelector(".device-selector-slot"), this._renderDeviceSelector());
    commitStableMarkup(
      this.shadowRoot.querySelector(".work-canvas"),
      this._loading ? this._renderLoading() : `${this._renderHeroStatus()}${this._renderViewContent()}`,
    );
    commitStableMarkup(this.shadowRoot.querySelector(".bottom-slot"), this._renderTabBar());
    this._attachEntityInteractions();

    // Production bundles concatenate the v1.7 zoom controller before this
    // component. No repository or network runtime import is allowed.
    window.NikasPanelZoom?.attach?.(this, { min: 0.75, max: 2.0 })?.bind?.();
  }
}

const NIKAS_PANEL_CSS = `
:host {
  display:block;
  width:100%;
  height:100dvh;
  min-height:0;
  overflow:hidden;
  color:var(--primary-text-color);
  background:var(--primary-background-color);
  --nika-surface:var(--ha-card-background,var(--card-background-color,#fff));
  --nika-border:color-mix(in srgb,var(--primary-text-color) 12%,transparent);
  --nika-muted:var(--secondary-text-color,#6b7280);
  --nika-primary:var(--primary-color,#03a9f4);
  --nika-ok:#35a853;
  --nika-warn:#e19b00;
  --nika-bad:#d94b4b;
  --nika-unknown:#7b8794;
}
*{box-sizing:border-box}
button{font:inherit}
.app-shell{
  width:100%;height:100dvh;min-height:0;
  display:grid;grid-template-rows:auto auto minmax(0,1fr) auto;
  overflow:hidden;background:var(--primary-background-color);
}
.app-header{
  display:grid;grid-template-columns:52px minmax(0,1fr) 52px;
  align-items:center;min-height:62px;
  padding:max(5px,env(safe-area-inset-top,0px)) max(8px,env(safe-area-inset-right,0px)) 5px max(8px,env(safe-area-inset-left,0px));
  background:var(--nika-surface);border-bottom:1px solid var(--nika-border);box-shadow:0 2px 12px rgba(0,0,0,.06);z-index:3;
}
.header-action{
  width:44px;height:44px;min-width:44px;border:1px solid var(--nika-border);border-radius:16px;
  background:var(--nika-surface);color:var(--primary-text-color);display:grid;place-items:center;padding:0;box-shadow:0 7px 20px rgba(23,45,76,.08);
}
.header-action ha-icon{--mdc-icon-size:25px;width:25px;height:25px}.header-action#refresh{color:var(--nika-primary)}
.header-title{min-width:0;min-height:44px;border:1px solid var(--nika-border);border-radius:16px;background:var(--nika-surface);color:var(--primary-text-color);text-align:center;line-height:1.1;padding:4px 12px;box-shadow:0 4px 14px rgba(23,45,76,.06)}
.header-title:active{transform:scale(.985);background:color-mix(in srgb,var(--nika-primary) 8%,var(--nika-surface))}
.header-title:focus-visible{outline:2px solid var(--nika-primary);outline-offset:2px}
.header-title strong,.header-title span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.header-title strong{font-size:23px;font-weight:800}
.header-title span{margin-top:3px;color:var(--nika-muted);font-size:14px;font-weight:560}
.device-selector-slot:empty{display:none}.device-selector-slot{z-index:2;padding:8px max(12px,env(safe-area-inset-right,0px)) 0 max(12px,env(safe-area-inset-left,0px));background:var(--primary-background-color)}
.device-selector{width:min(100%,1280px);margin:0 auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.device-selector button{min-width:0;min-height:52px;border:1px solid var(--nika-border);border-radius:20px;background:var(--nika-surface);color:var(--primary-text-color);display:flex;align-items:center;justify-content:center;gap:8px;padding:8px 10px;font-size:15px;font-weight:650}
.device-selector button.active{border-color:var(--nika-primary);color:var(--nika-primary);background:color-mix(in srgb,var(--nika-primary) 9%,var(--nika-surface))}
.canvas-viewport{position:relative;min-width:0;min-height:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior-x:none;overscroll-behavior-y:none;touch-action:pan-y;-webkit-overflow-scrolling:touch}
.canvas-viewport.zoomed{overflow:hidden;overscroll-behavior:none;touch-action:none;user-select:none;-webkit-user-select:none}
.work-canvas{position:relative;width:min(calc(100% - 24px),1280px);min-height:100%;margin:0 auto;padding:14px 0 22px;transform-origin:0 0}
.canvas-viewport.zoomed .work-canvas{position:absolute;left:12px;right:12px;width:auto;margin:0}
.status-dot{width:9px;height:9px;flex:0 0 9px;border-radius:50%;background:var(--nika-unknown)}
.status-dot.ok{background:var(--nika-ok)}.status-dot.active{background:var(--nika-primary)}.status-dot.warn{background:var(--nika-warn)}.status-dot.bad{background:var(--nika-bad)}.status-dot.unknown{background:var(--nika-unknown)}
.card{border:1px solid var(--nika-border);border-radius:22px;background:var(--nika-surface);padding:18px;margin-bottom:14px;box-shadow:0 2px 10px color-mix(in srgb,#000 5%,transparent)}
.card h2{margin:0 0 12px;font-size:18px}
.hero-line{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.hero-state{display:flex;align-items:center;gap:9px;font-size:24px;font-weight:800}
.hero p{margin:7px 0 0;color:var(--nika-muted);font-size:14px;line-height:1.4}
.hero-state.ok{color:var(--nika-ok)}.hero-state.warn{color:var(--nika-warn)}.hero-state.bad{color:var(--nika-bad)}.hero-state.unknown{color:var(--nika-unknown)}
.status-badge{flex:0 0 auto;border-radius:999px;padding:5px 8px;background:color-mix(in srgb,var(--nika-unknown) 10%,transparent);color:var(--nika-unknown);font-size:12px;font-weight:700}
.status-badge.ok{color:var(--nika-ok);background:color-mix(in srgb,var(--nika-ok) 10%,transparent)}.status-badge.active{color:var(--nika-primary);background:color-mix(in srgb,var(--nika-primary) 10%,transparent)}.status-badge.warn{color:var(--nika-warn);background:color-mix(in srgb,var(--nika-warn) 10%,transparent)}.status-badge.bad{color:var(--nika-bad);background:color-mix(in srgb,var(--nika-bad) 10%,transparent)}
.content-grid{display:grid;grid-template-columns:1fr;gap:14px}
.metrics{grid-template-columns:1fr}
.metric{min-width:0;min-height:76px;border:1px solid var(--nika-border);border-radius:20px;background:var(--nika-surface);padding:14px 15px}
.metric span,.metric strong{display:block}.metric span{color:var(--nika-muted);font-size:14px;line-height:1.25}.metric strong{margin-top:4px;font-size:18px;line-height:1.2}.metric.unknown strong{color:var(--nika-unknown)}
.state-row{min-height:52px;display:grid;grid-template-columns:28px minmax(0,1fr) auto 20px;gap:8px;align-items:center;padding:8px 0;border-top:1px solid var(--nika-border)}
.state-row:first-of-type{border-top:0}.state-row>ha-icon{--mdc-icon-size:22px;color:var(--nika-primary)}.state-row span{min-width:0}.state-row strong{text-align:right}.state-row .chevron{--mdc-icon-size:18px;color:var(--nika-muted)}
.action-card{width:100%;min-height:64px;border:1px solid var(--nika-border);border-radius:20px;background:var(--nika-surface);color:var(--primary-text-color);display:grid;grid-template-columns:34px minmax(0,1fr);gap:10px;align-items:center;text-align:left;padding:12px 14px}.action-card>ha-icon{--mdc-icon-size:26px;color:var(--nika-primary)}.action-card strong,.action-card small{display:block}.action-card small{margin-top:2px;color:var(--nika-muted)}
.alert{display:flex;gap:10px;padding:14px;border:1px solid var(--nika-border);border-radius:18px}.alert ha-icon{--mdc-icon-size:23px}.alert strong,.alert span{display:block}.alert span{margin-top:2px;color:var(--nika-muted);font-size:13px;line-height:1.35}.alert.active ha-icon{color:var(--nika-primary)}.alert.warn ha-icon{color:var(--nika-warn)}.alert.bad ha-icon{color:var(--nika-bad)}
.diagram{display:grid;gap:5px}.diagram span{color:var(--nika-muted);font-size:13px}
.loading{display:grid;gap:12px}.loading>span{color:var(--nika-muted);text-align:center;font-size:14px}.skeleton{border-radius:20px;background:color-mix(in srgb,var(--primary-text-color) 7%,transparent)}.hero-skeleton{min-height:140px}.row-skeleton{min-height:72px}
.bottom-slot{z-index:4}.tabbar{width:100%;display:grid;grid-template-columns:repeat(var(--nika-tab-count),minmax(0,1fr));gap:4px;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--nika-surface);border-top:1px solid var(--nika-border);box-shadow:0 -4px 18px color-mix(in srgb,#000 8%,transparent)}
.tabbar button{min-width:0;min-height:52px;border:0;border-radius:16px;background:transparent;color:var(--nika-muted);display:grid;place-items:center;align-content:center;gap:3px;padding:4px 2px}.tabbar button.active{color:var(--nika-primary);background:color-mix(in srgb,var(--nika-primary) 11%,transparent)}.tabbar ha-icon{--mdc-icon-size:28px;width:28px;height:28px}.tabbar span{width:100%;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;line-height:15px;font-weight:700}
.scale-status{position:absolute;z-index:40;left:50%;bottom:calc(76px + env(safe-area-inset-bottom,0px));transform:translate(-50%,10px);opacity:0;pointer-events:none;padding:9px 14px;border-radius:999px;background:rgba(20,27,34,.88);color:#fff;font-size:13px;font-weight:720;transition:opacity .14s ease,transform .14s ease}.scale-status.visible{opacity:1;transform:translate(-50%,0)}
@media(max-width:680px){:host{position:fixed;inset:0;width:auto;height:auto}.app-shell{position:absolute;inset:0;width:auto;height:auto}}
@media(max-width:390px){.app-header{grid-template-columns:48px minmax(0,1fr) 48px}.header-title strong{font-size:21px}.header-title span{font-size:13px}.work-canvas{width:min(calc(100% - 20px),1280px)}.canvas-viewport.zoomed .work-canvas{left:10px;right:10px}}
@media(min-width:760px){.content-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(prefers-reduced-motion:reduce){.scale-status{transition:none}}
`;

if (!customElements.get("nikas-integration-panel-reference")) {
  customElements.define("nikas-integration-panel-reference", NikaSIntegrationPanelReference);
}
