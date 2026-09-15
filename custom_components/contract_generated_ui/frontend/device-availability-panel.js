import {
  buildAvailabilitySnapshot,
  filterAvailabilityItems,
} from "./device-availability-model.js?build=b002";

export const UI_VERSION = "1.0.0-beta004";
const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

export function dispatchMoreInfo(target, entityId) {
  if (!target?.dispatchEvent || typeof entityId !== "string" || !entityId) return false;
  target.dispatchEvent(new CustomEvent("hass-more-info", {
    bubbles: true,
    composed: true,
    detail: { entityId },
  }));
  return true;
}

export function navigatePanel(path, environment = window) {
  if (typeof path !== "string" || !path.startsWith("/") || path.startsWith("//")) return false;
  const target = new URL(path, environment.location.origin);
  if (target.origin !== environment.location.origin) return false;
  environment.history.pushState(null, "", `${target.pathname}${target.search}${target.hash}`);
  environment.dispatchEvent(new Event("location-changed"));
  return true;
}

export async function refreshAvailabilitySources(hass, snapshot, sleeper = sleep) {
  const refresh = async () => {
    const entityIds = Array.isArray(snapshot?.updateEntityIds)
      ? snapshot.updateEntityIds.filter(Boolean)
      : [];
    if (!entityIds.length) throw new Error("Источники Entity Availability не найдены");
    if (typeof hass?.callService !== "function") throw new Error("Обновление недоступно");
    const result = await hass.callService("homeassistant", "update_entity", { entity_id: entityIds });
    if (result === false) throw new Error("Запрос обновления отклонён");
  };
  // Even an immediate failure keeps the minimum busy interval. Neither timer
  // completion nor a resolved false result is a successful refresh request.
  const results = await Promise.allSettled([refresh(), sleeper(900)]);
  const failure = results.find((result) => result.status === "rejected");
  if (failure) throw failure.reason;
}

const CONDITION = Object.freeze({
  online: ["Доступно", "ok", "mdi:check-circle-outline"],
  offline: ["Недоступно", "bad", "mdi:lan-disconnect"],
  stale: ["Данные устарели", "warn", "mdi:clock-alert-outline"],
  low_battery: ["Низкий заряд", "warn", "mdi:battery-alert-variant-outline"],
  poor_signal: ["Слабый сигнал", "warn", "mdi:signal-cellular-1"],
  suppressed: ["Исключено", "muted", "mdi:bell-off-outline"],
  no_data: ["Нет данных", "muted", "mdi:help-circle-outline"],
});

function statusMeta(status) {
  if (status === "healthy") return ["Всё доступно", "ok", "mdi:shield-check-outline"];
  if (status === "problem") return ["Есть проблемы", "bad", "mdi:shield-alert-outline"];
  if (status === "no_data") return ["Есть источники без данных", "warn", "mdi:database-alert-outline"];
  return ["Entity Availability не обнаружена", "muted", "mdi:shield-off-outline"];
}

function formatTimestamp(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
  }).format(date);
}

// Reconcile only the work view. Never replace a mounted input/select during
// telemetry; native pickers and the browser's scroll anchor belong to these nodes.
function workNodeKey(node) {
  if (node.nodeType !== 1) return null;
  return node.id ? `id:${node.id}` : node.getAttribute("data-key");
}

function patchWorkNode(current, next, telemetry) {
  if (current.nodeType !== 1) {
    if (current.nodeValue !== next.nodeValue) current.nodeValue = next.nodeValue;
    return;
  }
  const focused = current.getRootNode().activeElement === current;
  // Changing even the options of a focused native select may dismiss its picker.
  // The delegated focusout handler applies the latest options after it closes.
  if (focused && current.localName === "select") return;
  for (const attribute of [...current.attributes]) {
    if (focused && current.localName === "input" && attribute.name === "value") continue;
    if (!next.hasAttribute(attribute.name)) current.removeAttribute(attribute.name);
  }
  for (const attribute of [...next.attributes]) {
    if (focused && current.localName === "input" && attribute.name === "value") continue;
    if (current.getAttribute(attribute.name) !== attribute.value) {
      current.setAttribute(attribute.name, attribute.value);
    }
  }
  if (current.localName === "input") {
    if (!focused && current.value !== next.value) current.value = next.value;
    return;
  }
  patchWorkChildren(current, next, telemetry);
  if (current.localName === "select" && current.value !== next.value) {
    current.value = next.value;
  }
}

function patchWorkChildren(parent, nextParent, telemetry) {
  const previous = [...parent.childNodes];
  const keyed = new Map(previous.filter(workNodeKey).map(node => [workNodeKey(node), node]));
  const used = new Set();
  const desired = [];
  for (const next of nextParent.childNodes) {
    const key = workNodeKey(next);
    let current = key ? keyed.get(key) : previous.find(node => (
      !used.has(node) && !workNodeKey(node)
      && node.nodeType === next.nodeType && node.nodeName === next.nodeName
    ));
    if (current && (used.has(current) || current.nodeName !== next.nodeName)) current = null;
    if (current) {
      used.add(current);
      patchWorkNode(current, next, telemetry);
      desired.push(current);
    } else {
      desired.push(next.cloneNode(true));
    }
  }
  // A health change must not move the group the user is reading. Re-sort on an
  // explicit filter/tab change; append newly discovered rows during telemetry.
  const stableOrder = telemetry && parent.matches?.(".groups,.device-list");
  const ordered = stableOrder
    ? [...previous.filter(node => used.has(node)), ...desired.filter(node => !used.has(node))]
    : desired;
  let cursor = parent.firstChild;
  for (const node of ordered) {
    if (node === cursor) cursor = cursor.nextSibling;
    else parent.insertBefore(node, cursor);
  }
  for (const node of previous) {
    if (!used.has(node)) node.remove();
  }
}

function panelStyles() {
  return `
    :host{container-type:inline-size;display:block;position:relative;width:100%;height:100%;overflow:hidden;color:var(--primary-text-color,#17191c);background:var(--primary-background-color,#f4f6f8);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    *{box-sizing:border-box}[hidden]{display:none!important}button,input,select{font:inherit}button{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
    .shell{position:absolute;inset:0;display:grid;grid-template-rows:calc(60px + env(safe-area-inset-top,0px)) minmax(0,1fr) calc(68px + env(safe-area-inset-bottom,0px));overflow:hidden}
    header{padding:env(safe-area-inset-top,0px) calc(12px + env(safe-area-inset-right,0px)) 0 calc(12px + env(safe-area-inset-left,0px));display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;background:color-mix(in srgb,var(--primary-background-color,#f4f6f8) 97%,transparent);border-bottom:1px solid color-mix(in srgb,var(--divider-color,#dfe3e8) 70%,transparent);backdrop-filter:blur(18px) saturate(130%);-webkit-backdrop-filter:blur(18px) saturate(130%);z-index:3}
    .header-action{grid-row:1;width:44px;height:44px;padding:0;justify-self:center;border:1px solid color-mix(in srgb,var(--divider-color,#dfe3e8) 72%,transparent);border-radius:16px;background:var(--card-background-color,#fff);color:var(--primary-text-color,#17191c);box-shadow:0 7px 20px rgba(23,45,76,.08);display:grid;place-items:center;cursor:pointer}.header-action ha-icon{--mdc-icon-size:25px}.menu{grid-column:1}.header-action:active{transform:scale(.985)}
    .title{grid-area:1/2;min-width:0;width:min(360px,100%);height:52px;padding:5px 14px;justify-self:center;border:1px solid color-mix(in srgb,var(--primary-color,#03a9d9) 24%,var(--divider-color,#dfe3e8));border-radius:16px;background:color-mix(in srgb,var(--primary-color,#03a9d9) 5%,var(--card-background-color,#fff));color:inherit;display:flex;flex-direction:column;justify-content:center;text-align:center;cursor:pointer;box-shadow:0 5px 16px rgba(23,45,76,.06)}
    .title-heading{display:flex;align-items:center;justify-content:center;gap:6px;min-width:0}.title-compact{display:none}@container(max-width:519px){.title-full{display:none}.title-compact{display:inline}}.title strong{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:23px;font-weight:800;line-height:1.05}.title small{font-size:14px;font-weight:560;color:var(--secondary-text-color,#68737d);line-height:1.1;margin-top:3px;white-space:nowrap}
    .title:active{background:color-mix(in srgb,var(--primary-color,#03a9d9) 13%,var(--card-background-color,#fff));border-color:color-mix(in srgb,var(--primary-color,#03a9d9) 42%,var(--divider-color,#dfe3e8));box-shadow:0 2px 7px rgba(23,45,76,.05);transform:scale(.985)}.title:focus-visible,.header-action:focus-visible{outline:2px solid var(--primary-color,#03a9d9);outline-offset:2px}
    .refresh{grid-column:3;color:var(--primary-color,#03a9d9)}.refresh:disabled{opacity:.62;cursor:wait}.refresh.busy ha-icon{animation:spin .9s linear infinite}.refresh.success ha-icon{color:#43a047}.refresh.error ha-icon{color:#e53935}@keyframes spin{to{transform:rotate(360deg)}}
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.refresh-error{position:absolute;inset-inline:12px;top:calc(68px + env(safe-area-inset-top,0px));max-width:580px;margin-inline:auto;padding:12px 16px;border:1px solid #e53935;border-radius:14px;background:var(--card-background-color,#fff);color:var(--primary-text-color,#17191c);box-shadow:0 7px 20px rgba(23,45,76,.12);z-index:5}
    @container(max-width:359px){header{grid-template-columns:48px minmax(0,1fr) 48px}.title{width:100%;padding-inline:8px}.title strong{font-size:21px}.title small{font-size:13px}}
    .viewport{min-width:0;min-height:0;overflow-y:auto;overflow-x:hidden;touch-action:pan-y;overscroll-behavior:none;-webkit-overflow-scrolling:touch}.viewport.zoomed{overflow:hidden;touch-action:none}
    .canvas{width:100%;min-height:100%;transform-origin:0 0}.content{width:100%;max-width:1280px;min-height:100%;margin:0 auto;padding:14px 12px 24px}
    nav{padding:6px calc(6px + env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) calc(6px + env(safe-area-inset-left,0px));display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px;background:var(--card-background-color,#fff);border-top:1px solid var(--divider-color,#dfe3e8);box-shadow:0 -5px 22px rgba(23,45,76,.08);z-index:3}
    .tab{height:54px;border:0;border-radius:16px;background:transparent;color:var(--secondary-text-color,#68737d);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-weight:700;cursor:pointer}.tab ha-icon{--mdc-icon-size:25px}.tab span{font-size:12px}.tab.active{color:var(--primary-color,#2186d7);background:color-mix(in srgb,var(--primary-color,#2186d7) 11%,transparent)}
    .hero,.card,.empty,.controls{background:var(--card-background-color,#fff);border:1px solid color-mix(in srgb,var(--divider-color,#dfe3e8) 82%,transparent);border-radius:22px;box-shadow:0 8px 24px rgba(23,45,76,.07)}
    .hero{padding:18px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:center}.hero-status{display:flex;align-items:center;gap:14px;min-width:0}.hero-icon{width:52px;height:52px;border-radius:18px;display:grid;place-items:center;background:color-mix(in srgb,var(--status-color) 13%,transparent);color:var(--status-color)}.hero-icon ha-icon{--mdc-icon-size:30px}.hero h2{margin:0;font-size:23px}.hero p{margin:4px 0 0;color:var(--secondary-text-color,#68737d)}
    .ok{--status-color:#43a047}.bad{--status-color:#e05252}.warn{--status-color:#ef9f25}.muted{--status-color:#7b8792}
    .stats{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:12px 0}.stat{padding:14px 10px;border-radius:18px;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#dfe3e8);text-align:center}.stat b{display:block;font-size:25px}.stat span{font-size:12px;color:var(--secondary-text-color,#68737d)}
    .composition{padding:14px 16px;display:grid;gap:10px;margin-bottom:12px}.composition-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center}.composition-label{font-size:14px}.composition-label b{font-size:18px}.composition-detail{font-size:12px;color:var(--secondary-text-color,#68737d);text-align:right}.composition-row+.composition-row{padding-top:10px;border-top:1px solid color-mix(in srgb,var(--divider-color,#dfe3e8) 70%,transparent)}
    .section-title{margin:18px 3px 9px;font-size:16px;font-weight:800}.groups{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.group{padding:15px}.group-head{display:flex;justify-content:space-between;gap:10px;align-items:center}.group h3{margin:0;font-size:17px}.pill{padding:5px 9px;border-radius:999px;background:color-mix(in srgb,var(--status-color) 13%,transparent);color:var(--status-color);font-size:12px;font-weight:800}.group-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:13px}.metric{padding:9px 5px;border-radius:13px;background:color-mix(in srgb,var(--primary-background-color,#f4f6f8) 88%,transparent);text-align:center}.metric b{display:block;font-size:17px}.metric small{color:var(--secondary-text-color,#68737d)}
    .group-reference{margin-top:10px;padding:9px 11px;border-radius:13px;background:color-mix(in srgb,var(--primary-background-color,#f4f6f8) 88%,transparent);font-size:12px;color:var(--secondary-text-color,#68737d)}.group-reference b{color:var(--primary-text-color,#17191c)}
    .empty{padding:28px;text-align:center}.empty ha-icon{--mdc-icon-size:46px;color:var(--secondary-text-color,#68737d)}.empty h2{margin:10px 0 6px}.empty p{margin:0 auto;max-width:560px;color:var(--secondary-text-color,#68737d)}.empty button{margin-top:17px;border:0;border-radius:14px;padding:11px 16px;background:#111418;color:#fff;font-weight:750;cursor:pointer}
    .controls{padding:10px;display:grid;grid-template-columns:minmax(220px,1fr) 220px 220px;gap:8px;position:sticky;top:0;z-index:2}.controls input,.controls select{height:44px;border:1px solid var(--divider-color,#dfe3e8);border-radius:14px;background:var(--card-background-color,#fff);color:inherit;padding:0 13px;min-width:0}
    .device-list{display:grid;gap:8px;margin-top:10px}.device{width:100%;padding:13px 14px;border:1px solid var(--divider-color,#dfe3e8);border-radius:17px;background:var(--card-background-color,#fff);color:inherit;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;text-align:left;cursor:pointer}.device-main{min-width:0;display:grid;gap:4px}.device-name{font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.device-sub{display:block;color:var(--secondary-text-color,#68737d);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.device-side{text-align:right}.device-side .pill{display:inline-block}.health{display:block;margin-top:5px;font-size:12px;color:var(--secondary-text-color,#68737d)}
    .diag{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.diag .card{padding:17px}.diag h3{margin:0 0 12px}.diag-row{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid color-mix(in srgb,var(--divider-color,#dfe3e8) 65%,transparent)}.diag-row:last-child{border:0}.diag-row span{color:var(--secondary-text-color,#68737d)}code{word-break:break-all;font-size:12px}
    @media(max-width:850px){.stats{grid-template-columns:repeat(3,1fr)}.groups{grid-template-columns:repeat(2,1fr)}.controls{grid-template-columns:1fr 1fr}.controls input{grid-column:1/-1}.diag{grid-template-columns:1fr}}
    @media(max-width:560px){.content{padding:10px 9px 18px}.hero{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr);gap:7px}.composition-row{grid-template-columns:1fr;gap:3px}.composition-detail{text-align:left}.groups{grid-template-columns:1fr}.controls{grid-template-columns:1fr;position:static}.controls input{grid-column:auto}.device{grid-template-columns:minmax(0,1fr)}.device-side{text-align:left}}
    @media(prefers-reduced-motion:reduce){.refresh.busy ha-icon{animation:none}}
  `;
}

export class NikasDeviceAvailabilityPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._panel = null;
    this._snapshot = buildAvailabilitySnapshot({});
    this._snapshotSignature = JSON.stringify(this._snapshot);
    this._activeTab = "summary";
    this._query = "";
    this._groupFilter = "all";
    this._conditionFilter = "all";
    this._shellRendered = false;
    this._refreshState = "idle";
    this._refreshTimer = null;
    this._refreshGeneration = 0;
    this._refreshError = "";
    this._zoom = 1;
    this._pinch = null;
  }

  set hass(value) {
    this._hass = value;
    const snapshot = buildAvailabilitySnapshot(value?.states || {});
    const signature = JSON.stringify(snapshot);
    if (signature === this._snapshotSignature) return;
    this._snapshot = snapshot;
    this._snapshotSignature = signature;
    if (this._shellRendered) this._patchTelemetry();
  }
  get hass() { return this._hass; }
  set panel(value) { this._panel = value; }
  get panel() { return this._panel; }

  connectedCallback() {
    if (!this._shellRendered) this._renderShell();
    this._patchRefreshButton();
    this._patchActiveView();
  }

  disconnectedCallback() {
    ++this._refreshGeneration;
    if (this._refreshTimer !== null) clearTimeout(this._refreshTimer);
    this._refreshTimer = null;
    this._refreshState = "idle";
    this._refreshError = "";
    this._removeZoomListeners?.();
  }

  _renderShell() {
    this.shadowRoot.innerHTML = `
      <style>${panelStyles()}</style>
      <div class="shell">
        <header aria-label="Верхнее меню">
          <button id="menu" type="button" class="header-action menu" title="Меню Home Assistant" aria-label="Меню Home Assistant"><ha-icon icon="mdi:menu" aria-hidden="true"></ha-icon></button>
          <button id="title" type="button" class="title" title="Доступность устройств — обзор Home Assistant" aria-label="Доступность устройств. Вернуться в обзор Home Assistant">
            <span class="title-heading"><strong><span class="title-full">Доступность устройств</span><span class="title-compact" aria-hidden="true">Доступность</span></strong></span><small>UI v${UI_VERSION}</small>
          </button>
          <button id="refresh" type="button" class="header-action refresh idle" title="Обновить" aria-label="Обновить" aria-busy="false"><ha-icon icon="mdi:refresh" aria-hidden="true"></ha-icon></button>
        </header>
        <div id="refresh-status" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></div>
        <div id="refresh-error" class="refresh-error" role="alert" hidden></div>
        <main id="viewport" class="viewport"><div id="canvas" class="canvas"><section id="content" class="content"></section></div></main>
        <nav aria-label="Разделы панели">
          <button class="tab active" data-tab="summary"><ha-icon icon="mdi:view-dashboard-outline"></ha-icon><span>Сводка</span></button>
          <button class="tab" data-tab="devices"><ha-icon icon="mdi:access-point-check"></ha-icon><span>Устройства</span></button>
          <button class="tab" data-tab="diagnostics"><ha-icon icon="mdi:stethoscope"></ha-icon><span>Диагностика</span></button>
        </nav>
      </div>`;
    this._shellRendered = true;
    this.shadowRoot.getElementById("menu")?.addEventListener("click", () => {
      this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
    });
    this.shadowRoot.getElementById("refresh")?.addEventListener("click", () => this._refresh());
    this.shadowRoot.getElementById("title")?.addEventListener("click", () => {
      const declared = this._panel?.config?.parent_route;
      const parent = typeof declared === "string" && declared.split(/[?#]/)[0] !== window.location.pathname
        ? declared : "/home/overview";
      if (!navigatePanel(parent)) navigatePanel("/home/overview");
    });
    this.shadowRoot.querySelectorAll(".tab").forEach((button) => {
      button.addEventListener("click", () => this._activateTab(button.dataset.tab));
    });
    this._installViewListeners();
    this._installZoom();
  }

  _installViewListeners() {
    const content = this.shadowRoot.getElementById("content");
    if (!content) return;
    // One delegated listener per event, not one new handler per HA update.
    content.addEventListener("input", event => {
      if (event.target.id !== "search") return;
      this._query = event.target.value;
      this._renderDevices(content);
    });
    content.addEventListener("change", event => {
      if (event.target.id === "group-filter") this._groupFilter = event.target.value;
      else if (event.target.id === "condition-filter") this._conditionFilter = event.target.value;
      else return;
      this._renderDevices(content);
    });
    content.addEventListener("focusout", event => {
      if (event.target.localName !== "select") return;
      queueMicrotask(() => {
        if (this.isConnected && this._activeTab === "devices") this._renderDevices(content, true);
      });
    });
    content.addEventListener("click", event => {
      const device = event.target.closest?.(".device[data-entity]");
      if (device) dispatchMoreInfo(this, device.dataset.entity);
      else if (event.target.closest?.("#open-integration")) navigatePanel("/config/integrations");
    });
  }

  _activateTab(tab) {
    if (!["summary", "devices", "diagnostics"].includes(tab) || tab === this._activeTab) return;
    this._activeTab = tab;
    this.shadowRoot.querySelectorAll(".tab").forEach((button) => {
      button.classList.toggle("active", button.dataset.tab === tab);
    });
    const viewport = this.shadowRoot.getElementById("viewport");
    if (viewport) viewport.scrollTop = 0;
    this._patchActiveView();
  }

  _patchTelemetry() {
    this._patchActiveView(true);
  }

  _patchViewMarkup(content, markup, telemetry = false) {
    const template = content.ownerDocument.createElement("template");
    template.innerHTML = markup;
    patchWorkChildren(content, template.content, telemetry);
  }

  _patchActiveView(telemetry = false) {
    const content = this.shadowRoot.getElementById("content");
    if (!content) return;
    if (this._activeTab === "devices") this._renderDevices(content, telemetry);
    else if (this._activeTab === "diagnostics") this._renderDiagnostics(content, telemetry);
    else this._renderSummary(content, telemetry);
  }

  _renderSummary(content, telemetry = false) {
    const snapshot = this._snapshot;
    if (snapshot.status === "no_integration") {
      this._patchViewMarkup(content, `<div class="empty"><ha-icon icon="mdi:shield-off-outline"></ha-icon><h2>Entity Availability не обнаружена</h2><p>Установите или запустите интеграцию и создайте группы контролируемых сущностей.</p><button id="open-integration">Открыть интеграции</button></div>`, telemetry);
      return;
    }
    const [label, tone, icon] = statusMeta(snapshot.status);
    const t = snapshot.totals;
    this._patchViewMarkup(content, `
      <section class="hero ${tone}"><div class="hero-status"><div class="hero-icon"><ha-icon icon="${icon}"></ha-icon></div><div><h2>${label}</h2><p>${snapshot.groups.length} групп · ${t.total} контролируемых сущностей</p></div></div></section>
      <section class="stats">
        ${this._stat("Всего",t.total)}${this._stat("Доступно",t.online)}${this._stat("Недоступно",t.offline)}${this._stat("Устарели",t.stale)}${this._stat("Батарея",t.low_battery)}${this._stat("Сигнал",t.poor_signal)}
      </section>
      ${this._compositionCard(snapshot.composition)}
      <h2 class="section-title">Группы контроля</h2>
      <section class="groups" data-key="groups">${snapshot.groups.map((group) => this._groupCard(group)).join("")}</section>`, telemetry);
  }

  _stat(label, value) { return `<div class="stat"><b>${value}</b><span>${label}</span></div>`; }

  _compositionCard(composition) {
    const mainSuppressed = composition.suppressed
      ? ` · ${composition.suppressed} исключено`
      : "";
    const referenceSuppressed = composition.non_essential_suppressed
      ? ` · ${composition.non_essential_suppressed} исключено`
      : "";
    return `<section class="card composition"><div class="composition-row"><span class="composition-label"><b>${composition.essential}</b> основных</span><span class="composition-detail">${this._snapshot.totals.online} доступно · ${this._snapshot.totals.offline} недоступно${mainSuppressed}</span></div><div class="composition-row"><span class="composition-label"><b>${composition.non_essential}</b> не влияют на статус</span><span class="composition-detail">${composition.non_essential_online} доступно · ${composition.non_essential_offline} отключено${referenceSuppressed}</span></div></section>`;
  }

  _groupCard(group) {
    const meta = group.condition === "healthy"
      ? ["Всё доступно", "ok"]
      : group.condition === "problem" ? ["Есть проблемы", "bad"] : ["Нет данных", "muted"];
    const reference = group.nonEssential
      ? `<div class="group-reference"><b>${group.nonEssential}</b> не влияют на статус · ${group.nonEssentialOnline} доступно · ${group.nonEssentialOffline} отключено${group.nonEssentialSuppressed ? ` · ${group.nonEssentialSuppressed} исключено` : ""}</div>`
      : "";
    return `<article class="card group ${meta[1]}" data-key="group:${escapeHtml(group.slug)}"><div class="group-head"><h3>${escapeHtml(group.name)}</h3><span class="pill">${meta[0]}</span></div><div class="group-metrics"><div class="metric"><b>${group.online}</b><small>доступно</small></div><div class="metric"><b>${group.offline}</b><small>недоступно</small></div><div class="metric"><b>${group.stale + group.lowBattery + group.poorSignal}</b><small>внимание</small></div></div>${reference}</article>`;
  }

  _renderDevices(content, telemetry = false) {
    const groups = [...this._snapshot.groups].sort((left, right) => left.name.localeCompare(right.name, "ru"));
    // Keep a removed selected group visible until the user chooses a new filter.
    if (this._groupFilter !== "all" && !groups.some(group => group.slug === this._groupFilter)) {
      groups.push({ slug: this._groupFilter, name: `${this._groupFilter} (нет данных)` });
    }
    const items = filterAvailabilityItems(this._snapshot, this._query, this._groupFilter, this._conditionFilter);
    this._patchViewMarkup(content, `
      <section class="controls"><input id="search" type="search" value="${escapeHtml(this._query)}" placeholder="Поиск устройства или entity ID" aria-label="Поиск"><select id="group-filter" aria-label="Группа"><option value="all">Все группы</option>${groups.map((group) => `<option data-key="option:${escapeHtml(group.slug)}" value="${escapeHtml(group.slug)}" ${this._groupFilter === group.slug ? "selected" : ""}>${escapeHtml(group.name)}</option>`).join("")}</select><select id="condition-filter" aria-label="Состояние"><option value="all">Все состояния</option>${Object.entries(CONDITION).filter(([key]) => key !== "no_data").map(([key,value]) => `<option value="${key}" ${this._conditionFilter === key ? "selected" : ""}>${value[0]}</option>`).join("")}</select></section>
      <div class="device-list" data-key="device-list">${items.length ? items.map((item) => this._deviceRow(item)).join("") : `<div class="empty"><ha-icon icon="mdi:magnify-close"></ha-icon><h2>Ничего не найдено</h2><p>Измените строку поиска или фильтры.</p></div>`}</div>`, telemetry);

  }

  _deviceRow(item) {
    const [label,tone] = CONDITION[item.condition] || CONDITION.no_data;
    const details = [];
    if (item.battery !== null) details.push(`АКБ ${item.battery}%`);
    if (item.signal) details.push(`Сигнал ${item.signal.value}${item.signal.unit ? ` ${escapeHtml(item.signal.unit)}` : ""}`);
    if (item.offlineSince) details.push(`с ${formatTimestamp(item.offlineSince)}`);
    else if (item.lastSeen) details.push(`данные ${formatTimestamp(item.lastSeen)}`);
    if (item.nonEssential) details.push("не влияет на статус");
    return `<button class="device" data-key="device:${escapeHtml(item.group)}:${escapeHtml(item.entityId)}" data-entity="${escapeHtml(item.entityId)}"><span class="device-main"><span class="device-name">${escapeHtml(item.name)}</span><span class="device-sub">${escapeHtml(item.groupName)} · ${escapeHtml(item.entityId)}</span></span><span class="device-side ${tone}"><span class="pill">${label}</span><span class="health">${details.join(" · ") || " "}</span></span></button>`;
  }

  _renderDiagnostics(content, telemetry = false) {
    const snapshot = this._snapshot;
    const sourceRows = snapshot.groups.map((group) => `<div class="diag-row"><span>${escapeHtml(group.name)}</span><code>${escapeHtml(group.sourceEntityId)}</code></div>`).join("");
    this._patchViewMarkup(content, `<section class="diag"><article class="card"><h3>Источник данных</h3><div class="diag-row"><span>Интеграция</span><b>${snapshot.status === "no_integration" ? "Не обнаружена" : "Entity Availability 0.5.3+"}</b></div><div class="diag-row"><span>Групп</span><b>${snapshot.groups.length}</b></div><div class="diag-row"><span>Без данных</span><b>${snapshot.diagnostics.unavailableSources.length}</b></div><div class="diag-row"><span>Последнее обновление панели</span><b>${new Intl.DateTimeFormat("ru-RU",{hour:"2-digit",minute:"2-digit",second:"2-digit"}).format(new Date())}</b></div></article><article class="card"><h3>Обнаруженные группы</h3>${sourceRows || `<p>Источники не найдены.</p>`}</article></section>`, telemetry);
  }

  _patchRefreshButton() {
    const button = this.shadowRoot.getElementById("refresh");
    if (!button) return;
    const state = this._refreshState;
    const labels = {
      idle: "Обновить", busy: "Обновление данных",
      success: "Запрос обновления выполнен", error: "Не удалось обновить данные",
    };
    const label = labels[state];
    const className = `header-action refresh ${state}`;
    if (button.className !== className) button.className = className;
    if (button.disabled !== (state === "busy")) button.disabled = state === "busy";
    for (const [name, value] of Object.entries({ "aria-label": label, "aria-busy": String(state === "busy"), title: label })) {
      if (button.getAttribute(name) !== value) button.setAttribute(name, value);
    }
    const glyph = state === "success" ? "mdi:check" : state === "error" ? "mdi:alert-circle-outline" : "mdi:refresh";
    const icon = button.querySelector("ha-icon");
    if (icon && icon.getAttribute("icon") !== glyph) icon.setAttribute("icon", glyph);
    const status = this.shadowRoot.getElementById("refresh-status");
    const announcement = state === "idle" || state === "error" ? "" : label;
    if (status && status.textContent !== announcement) status.textContent = announcement;
    const error = this.shadowRoot.getElementById("refresh-error");
    if (error) {
      if (error.textContent !== this._refreshError) error.textContent = this._refreshError;
      if (error.hidden !== !this._refreshError) error.hidden = !this._refreshError;
    }
  }

  async _refresh() {
    if (this._refreshState === "busy" || !this.isConnected) return;
    // A deliberate retry cancels the previous result deadline before starting.
    if (this._refreshTimer !== null) clearTimeout(this._refreshTimer);
    this._refreshTimer = null;
    const generation = ++this._refreshGeneration;
    this._refreshState = "busy";
    this._refreshError = "";
    this._patchRefreshButton();
    let result = "success";
    try {
      await refreshAvailabilitySources(this._hass, this._snapshot);
    } catch (_error) {
      result = "error";
    }
    if (generation !== this._refreshGeneration || !this.isConnected) return;
    this._refreshState = result;
    if (result === "error") this._refreshError = "Не удалось обновить данные. Повторите попытку.";
    this._patchRefreshButton();
    // Successful API completion is not new telemetry. The normal hass setter
    // remains the only data source; the request never rebuilds the work view.
    this._refreshTimer = setTimeout(() => {
      if (generation !== this._refreshGeneration || !this.isConnected) return;
      this._refreshTimer = null;
      this._refreshState = "idle";
      this._patchRefreshButton();
    }, 1400);
  }

  _installZoom() {
    const viewport = this.shadowRoot.getElementById("viewport");
    const canvas = this.shadowRoot.getElementById("canvas");
    if (!viewport || !canvas || !this.addEventListener) return;
    const distance = (touches) => Math.hypot(
      touches[0].clientX - touches[1].clientX,
      touches[0].clientY - touches[1].clientY,
    );
    let lastTwoFingerTap = 0;
    const start = (event) => {
      if (event.touches?.length !== 2) return;
      const now = Date.now();
      if (now - lastTwoFingerTap < 340) {
        this._zoom = 1;
        canvas.style.transform = "";
        canvas.style.width = "";
        viewport.classList.remove("zoomed");
      }
      lastTwoFingerTap = now;
      this._pinch = { distance: distance(event.touches), zoom: this._zoom };
    };
    const move = (event) => {
      if (event.touches?.length !== 2 || !this._pinch) return;
      event.preventDefault();
      this._zoom = Math.min(1.8, Math.max(.8, this._pinch.zoom * distance(event.touches) / this._pinch.distance));
      canvas.style.transform = `scale(${this._zoom})`;
      canvas.style.width = `${100 / this._zoom}%`;
      viewport.classList.toggle("zoomed", Math.abs(this._zoom - 1) > .01);
    };
    const end = () => { this._pinch = null; };
    this.addEventListener("touchstart", start, { passive: true });
    this.addEventListener("touchmove", move, { passive: false });
    this.addEventListener("touchend", end, { passive: true });
    this._removeZoomListeners = () => {
      this.removeEventListener("touchstart", start);
      this.removeEventListener("touchmove", move);
      this.removeEventListener("touchend", end);
    };
  }
}

if (!customElements.get("nikas-device-availability-panel")) {
  customElements.define("nikas-device-availability-panel", NikasDeviceAvailabilityPanel);
}
