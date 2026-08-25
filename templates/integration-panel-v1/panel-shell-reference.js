// NikaS Integration Panel Template v1.2
// Development-time structural reference for Shell/Zoom v1.4.
// Production rule: copy/adapt into the integration repository and build one
// self-contained integration-owned frontend bundle. Never import this at runtime.
// Production adoption must attach the transform-owned canvas controller and
// interaction guards required by SPECIALIZED_PANEL_ZOOM_STANDARD.md v1.4.

const APP = {
  title: "Example Panel",
  subtitle: "Device model · UI v1.0.0",
  parentPath: "/dashboard-actions",
  preferredView: "overview",
  tabs: [
    ["overview", "mdi:view-dashboard-outline", "Обзор"],
    ["control", "mdi:tune", "Управление"],
    ["diagnostics", "mdi:stethoscope", "Диагностика"],
  ],
};

const TONES = new Set(["ok", "active", "warn", "bad", "unknown"]);

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function navigateExplicit(path) {
  if (!path) return;
  history.pushState(null, "", path);
  window.dispatchEvent(new Event("location-changed"));
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
  }

  set hass(value) {
    this._hass = value;
    this._loading = false;
    this._render();
  }

  set panel(value) {
    this._panel = value;
    this._activeView = value?.config?.preferred_view || APP.preferredView;
    this._render();
  }

  connectedCallback() {
    this._render();
  }

  _config() {
    const tabs = (this._panel?.config?.tabs || APP.tabs).slice(0, 5);
    return {
      title: this._panel?.config?.title || APP.title,
      subtitle: this._panel?.config?.subtitle || APP.subtitle,
      parentPath: this._panel?.config?.parent_path || APP.parentPath,
      tabs,
    };
  }

  _tone(value) {
    return TONES.has(value) ? value : "unknown";
  }

  _renderHeader() {
    const config = this._config();
    return `<header class="app-header">
      <button type="button" class="header-action" id="ha-menu" aria-label="Открыть меню Home Assistant">
        <ha-icon icon="mdi:menu"></ha-icon>
      </button>
      <div class="header-title">
        <strong>${esc(config.title)}</strong>
        <span>${esc(config.subtitle)}</span>
      </div>
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

  _attachInteractions() {
    this.shadowRoot.getElementById("ha-menu")?.addEventListener("click", () => {
      this.dispatchEvent(new CustomEvent("hass-toggle-menu", {
        bubbles: true,
        composed: true,
      }));
    });

    this.shadowRoot.getElementById("refresh")?.addEventListener("click", () => {
      this.dispatchEvent(new CustomEvent("nikas-panel-refresh", { bubbles: true, composed: true }));
    });

    this.shadowRoot.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => {
        this._activeView = button.dataset.view || APP.preferredView;
        this._render();
      });
    });

    this.shadowRoot.querySelectorAll("[data-device]").forEach((button) => {
      button.addEventListener("click", () => {
        this._selectedDevice = button.dataset.device || this._selectedDevice;
        this._render();
      });
    });

    this.shadowRoot.querySelectorAll("[data-entity]").forEach((element) => {
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

  _render() {
    const shell = `${this._renderHeader()}
      <div class="device-selector-band">${this._renderDeviceSelector()}</div>
      <main class="canvas-viewport" data-zoom-viewport data-engine="transform-owned-canvas">
        <div class="canvas-content content-width" data-zoom-content>
          ${this._loading ? this._renderLoading() : `${this._renderHeroStatus()}${this._renderViewContent()}`}
        </div>
      </main>
      ${this._renderTabBar()}`;

    this.shadowRoot.innerHTML = `<style>${NIKAS_PANEL_CSS}</style><div class="app-shell">${shell}</div>`;
    this._attachInteractions();
  }
}

const NIKAS_PANEL_CSS = `
:host {
  display:block;
  width:100%;
  min-height:100dvh;
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
  padding:max(5px,env(safe-area-inset-top)) max(8px,env(safe-area-inset-right)) 5px max(8px,env(safe-area-inset-left));
  background:var(--nika-surface);border-bottom:1px solid var(--nika-border);z-index:3;
}
.header-action{
  width:52px;min-width:52px;min-height:44px;border:0;border-radius:14px;
  background:transparent;color:var(--primary-text-color);display:grid;place-items:center;
}
.header-action ha-icon{--mdc-icon-size:24px}
.header-title{min-width:0;text-align:center;line-height:1.1}
.header-title strong,.header-title span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.header-title strong{font-size:18px;font-weight:760}
.header-title span{margin-top:2px;color:var(--nika-muted);font-size:12px;font-weight:600}
.device-selector-band{min-width:0;background:var(--primary-background-color)}
.canvas-viewport{position:relative;min-width:0;min-height:0;overflow:hidden;touch-action:none;overscroll-behavior:none}
.canvas-content{transform-origin:0 0;transform:translate3d(0,0,0) scale(1);will-change:transform}
.content-width{width:100%;max-width:1280px;margin:0 auto;padding:14px max(12px,env(safe-area-inset-right)) 22px max(12px,env(safe-area-inset-left))}
.device-selector{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:14px}
.device-selector button{min-width:0;min-height:52px;border:1px solid var(--nika-border);border-radius:20px;background:var(--nika-surface);color:var(--primary-text-color);display:flex;align-items:center;justify-content:center;gap:8px;padding:8px 10px;font-size:15px;font-weight:650}
.device-selector button.active{border-color:var(--nika-primary);color:var(--nika-primary);background:color-mix(in srgb,var(--nika-primary) 9%,var(--nika-surface))}
.status-dot{width:9px;height:9px;flex:0 0 9px;border-radius:50%;background:var(--nika-unknown)}
.status-dot.ok{background:var(--nika-ok)}.status-dot.active{background:var(--nika-primary)}.status-dot.warn{background:var(--nika-warn)}.status-dot.bad{background:var(--nika-bad)}.status-dot.unknown{background:var(--nika-unknown)}
.card{border:1px solid var(--nika-border);border-radius:22px;background:var(--nika-surface);padding:18px;margin-bottom:14px;box-shadow:0 2px 10px color-mix(in srgb,#000 5%,transparent)}
.card h2{margin:0 0 12px;font-size:18px}
.hero-line{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.hero-state{display:flex;align-items:center;gap:9px;font-size:24px;font-weight:800}
.hero p{margin:7px 0 0;color:var(--nika-muted);font-size:14px;line-height:1.4}
.hero-state.ok{color:var(--nika-ok)}.hero-state.warn{color:var(--nika-warn)}.hero-state.bad{color:var(--nika-bad)}.hero-state.unknown{color:var(--nika-unknown)}
.status-badge{flex:0 0 auto;border-radius:999px;padding:5px 8px;background:color-mix(in srgb,var(--nika-unknown) 10%,transparent);color:var(--nika-unknown);font-size:11px;font-weight:700}
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
.tabbar{width:100%;display:grid;grid-template-columns:repeat(var(--nika-tab-count),minmax(0,1fr));gap:2px;padding:6px max(6px,env(safe-area-inset-right)) calc(6px + env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left));background:var(--nika-surface);border-top:1px solid var(--nika-border);box-shadow:0 -3px 14px color-mix(in srgb,#000 7%,transparent);z-index:4}
.tabbar button{min-width:0;min-height:56px;border:0;border-radius:14px;background:transparent;color:var(--nika-muted);display:grid;place-items:center;align-content:center;gap:2px;padding:4px 2px}.tabbar button.active{color:var(--nika-primary);background:color-mix(in srgb,var(--nika-primary) 11%,transparent)}.tabbar ha-icon{--mdc-icon-size:23px}.tabbar span{width:100%;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;font-weight:700}
@media(max-width:390px){.app-header{grid-template-columns:48px minmax(0,1fr) 48px}.header-action{width:48px;min-width:48px}.header-title strong{font-size:16px}.header-title span{font-size:10px}.content-width{padding-left:10px;padding-right:10px}.tabbar span{font-size:11px}}
@media(min-width:760px){.content-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
`;

if (!customElements.get("nikas-integration-panel-reference")) {
  customElements.define("nikas-integration-panel-reference", NikaSIntegrationPanelReference);
}
