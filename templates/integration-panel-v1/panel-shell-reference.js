// NikaS Integration Panel Template v1.0
// Reference implementation only. Copy/adapt into the integration repository.
// Production rule: build one self-contained integration-owned JS bundle.

const APP = {
  title: "Example Panel",
  subtitle: "Device model · UI v1.0.0",
  parentPath: "/dashboard-actions",
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
    this._activeView = "overview";
    this._selectedDevice = null;
    this._loading = true;
    this._devices = [];
  }

  set hass(value) {
    this._hass = value;
    this._loading = false;
    this._render();
  }

  set panel(value) {
    this._panel = value;
    this._activeView = value?.config?.preferred_view || "overview";
    this._render();
  }

  connectedCallback() {
    this._render();
  }

  _config() {
    return {
      title: this._panel?.config?.title || APP.title,
      subtitle: this._panel?.config?.subtitle || APP.subtitle,
      parentPath: this._panel?.config?.parent_path || APP.parentPath,
      tabs: this._panel?.config?.tabs || APP.tabs,
    };
  }

  _tone(value) {
    return TONES.has(value) ? value : "unknown";
  }

  _renderHeader() {
    const config = this._config();
    return `<header class="app-header">
      <button type="button" class="header-action back" id="back" aria-label="Назад">
        <ha-icon icon="mdi:arrow-left"></ha-icon>
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
    if (this._devices.length < 2) return "";
    if (!this._selectedDevice) this._selectedDevice = this._devices[0]?.id || null;

    return `<div class="device-selector" role="tablist" aria-label="Устройство">
      ${this._devices
        .map((device) => {
          const selected = device.id === this._selectedDevice;
          const tone = this._tone(device.tone);
          return `<button type="button" data-device="${esc(device.id)}" class="${selected ? "active" : ""}" role="tab" aria-selected="${selected}">
            <i class="status-dot ${tone}"></i><span>${esc(device.label)}</span>
          </button>`;
        })
        .join("")}
    </div>`;
  }

  _renderHero() {
    // Integration replaces these factual placeholders with its domain state.
    return `<article class="card hero">
      <div class="hero-kicker">ТЕКУЩЕЕ СОСТОЯНИЕ</div>
      <div class="hero-state unknown"><i class="status-dot unknown"></i>Состояние неизвестно</div>
      <p>Интеграция должна вывести здесь краткий фактический статус, а не реестр датчиков.</p>
    </article>`;
  }

  _renderMetric(label, value, unit = "", tone = "active", entityId = "") {
    const safeTone = this._tone(tone);
    const entityAttr = entityId ? ` data-entity="${esc(entityId)}" tabindex="0"` : "";
    const displayValue = value === null || value === undefined || value === ""
      ? "Нет данных"
      : `${value}${unit ? ` ${unit}` : ""}`;
    return `<div class="metric ${safeTone}"${entityAttr}>
      <span>${esc(label)}</span>
      <strong>${esc(displayValue)}</strong>
    </div>`;
  }

  _renderAlert(title, text, tone = "warn") {
    const safeTone = this._tone(tone);
    const icon = safeTone === "bad" ? "mdi:alert-circle" : safeTone === "warn" ? "mdi:alert" : "mdi:information-outline";
    return `<div class="alert ${safeTone}">
      <ha-icon icon="${icon}"></ha-icon>
      <div><strong>${esc(title)}</strong><span>${esc(text)}</span></div>
    </div>`;
  }

  _renderViewContent() {
    if (this._activeView === "diagnostics") {
      return `<section class="content-grid">
        <article class="card">
          <h2>Диагностика</h2>
          ${this._renderMetric("Источник данных", "Неизвестно", "", "unknown")}
          ${this._renderMetric("Последнее обновление", "Нет данных", "", "unknown")}
        </article>
      </section>`;
    }

    if (this._activeView === "control") {
      return `<section class="content-grid">
        <article class="card">
          <h2>Управление</h2>
          ${this._renderAlert("Нет действий в reference template", "Добавляйте только подтверждённые действия интеграции.", "active")}
        </article>
      </section>`;
    }

    return `<section class="content-grid metrics">
      ${this._renderMetric("Показатель", "Нет данных", "", "unknown")}
      ${this._renderMetric("Показатель", "Нет данных", "", "unknown")}
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
    const tabs = this._config().tabs.slice(0, 5);
    return `<nav class="tabbar" aria-label="Разделы">
      ${tabs
        .map(([view, icon, label]) => `<button type="button" data-view="${esc(view)}" class="${this._activeView === view ? "active" : ""}">
          <ha-icon icon="${esc(icon)}"></ha-icon><span>${esc(label)}</span>
        </button>`)
        .join("")}
    </nav>`;
  }

  _attachInteractions() {
    this.shadowRoot.getElementById("back")?.addEventListener("click", () => {
      navigateExplicit(this._config().parentPath);
    });

    this.shadowRoot.getElementById("refresh")?.addEventListener("click", () => {
      // Replace with one integration-level refresh action/service when supported.
      this.dispatchEvent(new CustomEvent("nikas-panel-refresh", { bubbles: true, composed: true }));
    });

    this.shadowRoot.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => {
        this._activeView = button.dataset.view || "overview";
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
      const openMoreInfo = () => {
        const entityId = element.dataset.entity;
        if (!entityId) return;
        this.dispatchEvent(new CustomEvent("hass-more-info", {
          detail: { entityId },
          bubbles: true,
          composed: true,
        }));
      };
      element.addEventListener("pointerdown", () => {
        timer = window.setTimeout(openMoreInfo, 550);
      });
      ["pointerup", "pointercancel", "pointerleave"].forEach((name) => {
        element.addEventListener(name, () => {
          if (timer) window.clearTimeout(timer);
          timer = null;
        });
      });
    });
  }

  _render() {
    const shell = `${this._renderHeader()}
      <main class="scroll-region">
        ${this._renderDeviceSelector()}
        ${this._loading ? this._renderLoading() : `${this._renderHero()}${this._renderViewContent()}`}
      </main>
      ${this._renderTabBar()}`;

    this.shadowRoot.innerHTML = `<style>${NIKAS_PANEL_CSS}</style><div class="app-shell">${shell}</div>`;
    this._attachInteractions();
  }
}

const NIKAS_PANEL_CSS = `
:host {
  display: block;
  min-height: 100dvh;
  color: var(--primary-text-color);
  background: var(--primary-background-color);
  --nika-surface: var(--ha-card-background, var(--card-background-color, #fff));
  --nika-border: color-mix(in srgb, var(--primary-text-color) 12%, transparent);
  --nika-muted: var(--secondary-text-color, #6b7280);
  --nika-primary: var(--primary-color, #03a9f4);
  --nika-ok: #35a853;
  --nika-warn: #e19b00;
  --nika-bad: #d94b4b;
  --nika-unknown: #7b8794;
}
* { box-sizing: border-box; }
button { font: inherit; }
.app-shell {
  min-height: 100dvh;
  height: 100dvh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
}
.app-header {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) 52px;
  align-items: center;
  min-height: 62px;
  padding: max(5px, env(safe-area-inset-top)) max(8px, env(safe-area-inset-right)) 5px max(8px, env(safe-area-inset-left));
  background: var(--nika-surface);
  border-bottom: 1px solid var(--nika-border);
  z-index: 3;
}
.header-action {
  min-width: 44px;
  min-height: 44px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: var(--primary-text-color);
  display: grid;
  place-items: center;
}
.header-action ha-icon { --mdc-icon-size: 25px; }
.header-title { min-width: 0; text-align: center; line-height: 1.12; }
.header-title strong {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 18px;
  font-weight: 760;
}
.header-title span {
  display: block;
  margin-top: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--nika-muted);
  font-size: 14px;
}
.scroll-region {
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
  padding: 12px max(12px, env(safe-area-inset-right)) 20px max(12px, env(safe-area-inset-left));
}
.device-selector {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.device-selector button {
  min-height: 52px;
  border: 1px solid var(--nika-border);
  border-radius: 20px;
  background: var(--nika-surface);
  color: var(--primary-text-color);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 10px;
  font-size: 16px;
  font-weight: 650;
}
.device-selector button.active {
  border-color: var(--nika-primary);
  color: var(--nika-primary);
  background: color-mix(in srgb, var(--nika-primary) 9%, var(--nika-surface));
}
.status-dot { width: 9px; height: 9px; flex: 0 0 9px; border-radius: 50%; background: var(--nika-unknown); }
.status-dot.ok { background: var(--nika-ok); }
.status-dot.active { background: var(--nika-primary); }
.status-dot.warn { background: var(--nika-warn); }
.status-dot.bad { background: var(--nika-bad); }
.status-dot.unknown { background: var(--nika-unknown); }
.card {
  border: 1px solid var(--nika-border);
  border-radius: 22px;
  background: var(--nika-surface);
  padding: 18px;
  margin-bottom: 14px;
}
.card h2 { margin: 0 0 12px; font-size: 18px; }
.hero-kicker { color: var(--nika-muted); font-size: 14px; font-weight: 700; letter-spacing: .04em; }
.hero-state { display: flex; align-items: center; gap: 9px; margin-top: 5px; font-size: 24px; font-weight: 800; }
.hero p { margin: 8px 0 0; color: var(--nika-muted); font-size: 15px; line-height: 1.4; }
.hero-state.ok { color: var(--nika-ok); }
.hero-state.warn { color: var(--nika-warn); }
.hero-state.bad { color: var(--nika-bad); }
.hero-state.unknown { color: var(--nika-unknown); }
.content-grid { display: grid; gap: 14px; }
.metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.metric {
  min-width: 0;
  min-height: 76px;
  border: 1px solid var(--nika-border);
  border-radius: 20px;
  background: var(--nika-surface);
  padding: 14px 15px;
}
.metric span, .metric strong { display: block; }
.metric span { color: var(--nika-muted); font-size: 15px; line-height: 1.25; }
.metric strong { margin-top: 4px; font-size: 18px; line-height: 1.2; }
.metric.unknown strong { color: var(--nika-unknown); }
.alert { display: flex; gap: 10px; padding: 14px; border: 1px solid var(--nika-border); border-radius: 18px; }
.alert ha-icon { --mdc-icon-size: 23px; }
.alert strong, .alert span { display: block; }
.alert strong { font-size: 16px; }
.alert span { margin-top: 2px; color: var(--nika-muted); font-size: 14px; line-height: 1.35; }
.alert.active ha-icon { color: var(--nika-primary); }
.alert.warn ha-icon { color: var(--nika-warn); }
.alert.bad ha-icon { color: var(--nika-bad); }
.loading { display: grid; gap: 12px; }
.loading > span { color: var(--nika-muted); text-align: center; font-size: 15px; }
.skeleton { border-radius: 20px; background: color-mix(in srgb, var(--primary-text-color) 7%, transparent); }
.hero-skeleton { min-height: 150px; }
.row-skeleton { min-height: 72px; }
.tabbar {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 2px;
  padding: 6px max(6px, env(safe-area-inset-right)) calc(6px + env(safe-area-inset-bottom)) max(6px, env(safe-area-inset-left));
  background: var(--nika-surface);
  border-top: 1px solid var(--nika-border);
  box-shadow: 0 -3px 14px color-mix(in srgb, #000 7%, transparent);
  z-index: 4;
}
.tabbar button {
  min-width: 0;
  min-height: 58px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: var(--nika-muted);
  display: grid;
  place-items: center;
  align-content: center;
  gap: 2px;
  padding: 4px 2px;
}
.tabbar button.active {
  color: var(--nika-primary);
  background: color-mix(in srgb, var(--nika-primary) 11%, transparent);
}
.tabbar ha-icon { --mdc-icon-size: 24px; }
.tabbar span { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; font-weight: 700; }
@media (max-width: 390px) {
  .app-header { grid-template-columns: 48px minmax(0, 1fr) 48px; }
  .scroll-region { padding-left: 10px; padding-right: 10px; }
  .metrics { grid-template-columns: 1fr; }
}
@media (min-width: 760px) {
  .scroll-region { width: min(100%, 1240px); margin: 0 auto; }
  .content-grid:not(.metrics) { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .metrics { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
`;

if (!customElements.get("nikas-integration-panel-reference")) {
  customElements.define("nikas-integration-panel-reference", NikaSIntegrationPanelReference);
}
