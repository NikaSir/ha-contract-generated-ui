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
      if (current.getAttribute(attribute.name) !== attribute.value) {
        current.setAttribute(attribute.name, attribute.value);
      }
    }
  }
  for (let index = 0; index < current.childNodes.length; index += 1) {
    syncTree(current.childNodes[index], desired.childNodes[index]);
  }
}

function commitStableMarkup(root, markup) {
  if (typeof document === "undefined" || typeof document.createElement !== "function" || typeof Node === "undefined") {
    root.innerHTML = markup;
    return true;
  }
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

class NikaSInfrastructureSummaryV2 extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  setConfig(config) {
    const supported = new Set(["power_grid", "ups", "keenetic"]);
    if (!config || !supported.has(config.variant) || !config.roles) {
      throw new Error("nikas-infrastructure-summary-v2 requires a supported variant and roles");
    }
    this._config = config;
    this._render();
  }

  set hass(value) {
    this._hass = value;
    this._render();
  }

  getCardSize() {
    return 3;
  }

  getGridOptions() {
    return { columns: "full", rows: "auto" };
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _role(role) {
    return this._config?.roles?.[role];
  }

  _state(role) {
    const entity = this._role(role)?.entity;
    return entity && this._hass?.states ? this._hass.states[entity] : undefined;
  }

  _unreliable(role) {
    const state = this._state(role);
    return !state || state.state === "unknown" || state.state === "unavailable";
  }

  _binary(role) {
    if (this._unreliable(role)) return null;
    return this._state(role).state === "on";
  }

  _number(role) {
    if (this._unreliable(role)) return null;
    const value = Number.parseFloat(String(this._state(role)?.state ?? "").replace(",", "."));
    return Number.isFinite(value) ? value : null;
  }

  _inputVoltageTone(role) {
    const value = this._number(role);
    if (value === null) return "unreliable";
    if (value < 125 || value > 275) return "event";
    if (value < 150 || value > 265) return "warning";
    return "ok";
  }

  _gostVoltageTone(role) {
    const value = this._number(role);
    if (value === null) return "unreliable";
    return value < 198 || value > 242 ? "event" : "ok";
  }

  _lineTone() {
    const stale = this._binary("non_interruptible_data_stale");
    if (stale === null) return "unreliable";
    if (stale) return "warning";
    return this._gostVoltageTone("non_interruptible_voltage");
  }

  _lineCaption() {
    const tone = this._lineTone();
    if (tone === "unreliable") return "Нет данных";
    if (tone === "warning") return "Данные устарели";
    if (tone === "event") return "Вне ГОСТ";
    return "UPS Котёл";
  }

  _format(role) {
    const state = this._state(role);
    if (!state) return "Нет данных";
    if (state.state === "unknown") return "Неизвестно";
    if (state.state === "unavailable") return "Недоступно";
    if (this._hass && typeof this._hass.formatEntityState === "function") {
      try {
        return this._hass.formatEntityState(state);
      } catch (_err) {
        // Fall through to deterministic state + unit formatting.
      }
    }
    const unit = state.attributes?.unit_of_measurement;
    return `${state.state}${unit ? ` ${unit}` : ""}`;
  }

  _relativeTime(role) {
    const state = this._state(role);
    if (!state || this._unreliable(role)) return this._format(role);
    const timestamp = Date.parse(state.state);
    if (!Number.isFinite(timestamp)) return this._format(role);

    const diffMs = Date.now() - timestamp;
    if (diffMs < 0) return this._format(role);
    const minutes = Math.floor(diffMs / 60000);
    if (minutes < 1) return "только что";
    if (minutes < 60) return `${minutes} мин назад`;
    const hours = Math.floor(minutes / 60);
    if (hours < 48) return `${hours} ч назад`;
    const days = Math.floor(hours / 24);
    if (days < 30) return `${days} дн назад`;
    const months = Math.floor(days / 30);
    if (months < 12) return `${months} мес назад`;
    const years = Math.floor(days / 365);
    return `${Math.max(1, years)} г назад`;
  }

  _navigate(path) {
    if (!path || typeof path !== "string") return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  _status(label, tone) {
    return `<span class="status ${tone}">${this._escape(label)}</span>`;
  }

  _metric(label, value, icon) {
    return `
      <div class="metric">
        <ha-icon icon="${icon}"></ha-icon>
        <div>
          <span class="metric-label">${this._escape(label)}</span>
          <strong>${this._escape(value)}</strong>
        </div>
      </div>`;
  }

  _powerMarkup() {
    const required = [
      "grid_ok",
      "meter_online",
      "phase_loss",
      "phase_a_present",
      "phase_b_present",
      "phase_c_present",
      "voltage_a",
      "voltage_b",
      "voltage_c",
      "voltage_imbalance",
      "total_power",
    ];
    const unreliable = required.some((role) => this._unreliable(role));
    const event =
      !unreliable &&
      (this._binary("grid_ok") === false ||
        this._binary("meter_online") === false ||
        this._binary("phase_loss") === true ||
        this._binary("phase_a_present") === false ||
        this._binary("phase_b_present") === false ||
        this._binary("phase_c_present") === false);
    const phaseTones = ["voltage_a", "voltage_b", "voltage_c"].map((role) => this._inputVoltageTone(role));
    const outsidePassport = phaseTones.includes("event");
    const workingLimit = phaseTones.includes("warning");
    const status = unreliable
      ? this._status("Данные неполные", "unreliable")
      : event || outsidePassport
        ? this._status("Авария", "event")
        : workingLimit
          ? this._status("Рабочий предел", "warning")
        : this._status("Нормально", "ok");

    const phase = (name, voltageRole, presentRole) => {
      const present = this._binary(presentRole);
      const tone = present === null ? "unreliable" : present ? this._inputVoltageTone(voltageRole) : "event";
      return `
        <div class="phase ${tone}">
          <span class="phase-name">${name}</span>
          <strong>${this._escape(this._format(voltageRole))}</strong>
        </div>`;
    };

    return `
      <div class="card-header">
        <div><h2>${this._escape(this._config.title)}</h2><p>До стабилизаторов · LIDER PS7500W-30</p></div>
        ${status}
      </div>
      <div class="phase-grid">
        ${phase("A", "voltage_a", "phase_a_present")}
        ${phase("B", "voltage_b", "phase_b_present")}
        ${phase("C", "voltage_c", "phase_c_present")}
      </div>
      <div class="metric-grid two">
        ${this._metric("Перекос", this._format("voltage_imbalance"), "mdi:sine-wave")}
        ${this._metric("Мощность", this._format("total_power"), "mdi:flash")}
      </div>
      <div class="policy">Паспорт: номинальный диапазон 150–265 В · рабочий 125–275 В</div>
      <div class="control-grid">
        <div class="control-point unreliable"><span>После стабилизаторов</span><strong>Ожидает датчиков</strong><small>ГОСТ · 198–242 В</small></div>
        <div class="control-point ${this._lineTone()}"><span>Неотключаемая линия</span><strong>${this._escape(this._format("non_interruptible_voltage"))}</strong><small>${this._escape(this._lineCaption())}</small></div>
      </div>
      ${this._config.details_path ? '<button class="details power-details" type="button">Подробнее <ha-icon icon="mdi:chevron-right"></ha-icon></button>' : ""}`;
  }

  _upsMarkup() {
    const core = [
      "operating_mode",
      "battery_capacity",
      "output_load",
      "data_stale",
      "on_battery",
    ];
    const unreliable = core.some((role) => this._unreliable(role));
    const onBattery = this._binary("on_battery");
    const stale = this._binary("data_stale");
    const cloud = this._binary("cloud_telemetry");

    let status;
    if (unreliable) status = this._status("Нет данных", "unreliable");
    else if (onBattery) status = this._status("От батареи", "event");
    else if (stale) status = this._status("Данные устарели", "warning");
    else if (cloud === false) status = this._status("Облако отключено", "warning");
    else if (cloud === null) status = this._status("Облако неизвестно", "unreliable");
    else status = this._status("Нормально", "ok");

    const cloudText = cloud === null ? "Облако: неизвестно" : cloud ? "Облако: подключено" : "Облако: отключено";
    const staleText = stale === null ? "Свежесть: неизвестно" : stale ? "Данные устарели" : "Данные актуальны";
    const details = this._config.details_path
      ? `<button class="details" type="button">Подробнее <ha-icon icon="mdi:chevron-right"></ha-icon></button>`
      : "";

    return `
      <div class="card-header ups-header">
        <div><h2>${this._escape(this._config.title)}</h2><p>${this._escape(this._format("operating_mode"))}</p></div>
        ${status}
      </div>
      <div class="metric-grid two ups-metrics">
        ${this._metric("АКБ", this._format("battery_capacity"), "mdi:battery")}
        ${this._metric("Нагрузка", this._format("output_load"), "mdi:gauge")}
      </div>
      <div class="ups-footer">
        <div class="summary-line ups-summary">
          <span>${this._escape(cloudText)}</span>
          <span>·</span>
          <span>${this._escape(staleText)}</span>
        </div>
        ${details}
      </div>`;
  }

  _keeneticMarkup() {
    const wanUnreliable = this._unreliable("active_wan");
    const wan = this._format("active_wan");
    const status = wanUnreliable
      ? this._status("WAN неизвестен", "unreliable")
      : this._status(`WAN · ${wan}`, "info");
    const reason = this._format("last_wan_switch_reason");
    const switchTime = this._relativeTime("last_wan_switch");

    return `
      <div class="card-header keenetic-header">
        <div><h2>${this._escape(this._config.title)}</h2><p>WAN / LTE</p></div>
        ${status}
      </div>
      <div class="keenetic-primary">
        <div><span>Активный WAN</span><strong>${this._escape(wan)}</strong></div>
        <div><span>Последняя смена</span><strong>${this._escape(switchTime)}</strong></div>
      </div>
      <div class="reason" title="${this._escape(reason)}"><span>Причина ·</span> ${this._escape(reason)}</div>
      <div class="metric-grid three keenetic-metrics">
        ${this._metric("Смен сегодня", this._format("wan_switches_today"), "mdi:swap-horizontal")}
        ${this._metric("LTE сегодня", this._format("lte_time_today"), "mdi:timer-outline")}
        ${this._metric("Температура", this._format("temperature"), "mdi:thermometer")}
      </div>`;
  }

  _render() {
    if (!this._config || !this.shadowRoot) return;
    let content = "";
    if (this._config.variant === "power_grid") content = this._powerMarkup();
    if (this._config.variant === "ups") content = this._upsMarkup();
    if (this._config.variant === "keenetic") content = this._keeneticMarkup();

    const markup = `
      <style>
        :host { display: block; width: 100%; }
        ha-card {
          padding: 14px 16px;
          border-radius: var(--ha-card-border-radius, 24px);
          box-sizing: border-box;
          overflow: hidden;
        }
        ha-card.ups { padding: 12px 16px 8px; }
        ha-card.keenetic { padding: 14px 16px 13px; }
        .card-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 10px;
          margin-bottom: 10px;
        }
        .ups-header { margin-bottom: 8px; }
        .keenetic-header { margin-bottom: 8px; }
        h2 { margin: 0; font-size: 21px; line-height: 1.12; font-weight: 700; }
        p { margin: 3px 0 0; color: var(--secondary-text-color); font-size: 13px; }
        .status {
          flex: 0 0 auto;
          border-radius: 999px;
          padding: 7px 10px;
          font-size: 12px;
          line-height: 1;
          font-weight: 700;
          white-space: nowrap;
        }
        .status.ok { color: var(--success-color, #43a047); background: color-mix(in srgb, var(--success-color, #43a047) 13%, transparent); }
        .status.warning { color: var(--warning-color, #ff9800); background: color-mix(in srgb, var(--warning-color, #ff9800) 14%, transparent); }
        .status.event { color: var(--error-color, #db4437); background: color-mix(in srgb, var(--error-color, #db4437) 12%, transparent); }
        .status.unreliable { color: var(--secondary-text-color); background: var(--secondary-background-color, #eee); }
        .status.info { color: var(--primary-color); background: color-mix(in srgb, var(--primary-color) 12%, transparent); }
        .phase-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; margin-bottom: 7px; }
        .phase {
          min-width: 0;
          padding: 8px 6px;
          border-radius: 14px;
          background: var(--secondary-background-color, #f4f4f4);
          text-align: center;
          border: 1px solid transparent;
        }
        .phase.ok { border-color: color-mix(in srgb, var(--success-color, #43a047) 30%, transparent); }
        .phase.warning { border-color: color-mix(in srgb, var(--warning-color, #ff9800) 50%, transparent); }
        .phase.event { border-color: color-mix(in srgb, var(--error-color, #db4437) 40%, transparent); }
        .phase.unreliable { opacity: .68; }
        .phase-name { display: block; color: var(--secondary-text-color); font-size: 12px; margin-bottom: 1px; }
        .phase strong { display: block; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .metric-grid { display: grid; gap: 6px; }
        .metric-grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .metric-grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .metric {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 10px;
          border-radius: 14px;
          background: var(--secondary-background-color, #f4f4f4);
        }
        .ups-metrics .metric { padding: 7px 10px; }
        .metric ha-icon { color: var(--primary-color); --mdc-icon-size: 20px; flex: 0 0 auto; }
        .metric > div { min-width: 0; }
        .metric-label { display: block; color: var(--secondary-text-color); font-size: 12px; line-height: 1.15; }
        .metric strong { display: block; margin-top: 1px; font-size: 15.5px; line-height: 1.15; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .summary-line { display: flex; gap: 4px; flex-wrap: wrap; color: var(--secondary-text-color); font-size: 12px; line-height: 1.2; }
        .ups-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          min-height: 44px;
          margin-top: 5px;
        }
        .ups-summary { min-width: 0; flex: 1 1 auto; }
        .details {
          appearance: none;
          border: 0;
          background: transparent;
          color: var(--primary-color);
          min-height: 44px;
          margin: 0 -4px 0 0;
          padding: 6px 4px;
          display: flex;
          align-items: center;
          gap: 1px;
          font: inherit;
          font-weight: 700;
          cursor: pointer;
          flex: 0 0 auto;
        }
        .details ha-icon { --mdc-icon-size: 19px; }
        .keenetic-primary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; margin-bottom: 6px; }
        .keenetic-primary > div { padding: 9px 10px; border-radius: 14px; background: var(--secondary-background-color, #f4f4f4); min-width: 0; }
        .keenetic-primary span { display: block; color: var(--secondary-text-color); font-size: 12px; }
        .keenetic-primary strong { display: block; margin-top: 2px; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .reason { margin: 0 2px 7px; color: var(--secondary-text-color); font-size: 12.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .reason span { font-weight: 600; color: var(--primary-text-color); }
        .keenetic-metrics .metric { padding: 7px 8px; }
        .policy { margin: 7px 2px 0; color: var(--secondary-text-color); font-size: 12px; line-height: 1.25; }
        .control-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 6px; margin-top: 7px; }
        .control-point { min-width: 0; padding: 8px 10px; border-radius: 14px; background: var(--secondary-background-color,#f4f4f4); border: 1px solid transparent; }
        .control-point span,.control-point small { display:block; color:var(--secondary-text-color); font-size:12px; line-height:1.15; }
        .control-point strong { display:block; margin:3px 0; font-size:14px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .control-point.ok { border-color:color-mix(in srgb,var(--success-color,#43a047) 30%,transparent); }
        .control-point.warning { border-color:color-mix(in srgb,var(--warning-color,#ff9800) 50%,transparent); }
        .control-point.event { border-color:color-mix(in srgb,var(--error-color,#db4437) 45%,transparent); }
        .control-point.unreliable { opacity:.76; }
        .power-details { width:100%; justify-content:flex-end; min-height:36px; margin-top:2px; }
        @media (max-width: 420px) {
          ha-card { padding: 13px 14px; }
          ha-card.ups { padding: 11px 14px 6px; }
          ha-card.keenetic { padding: 13px 14px 11px; }
          h2 { font-size: 19px; }
          .status { font-size: 12px; padding: 6px 8px; }
          .phase { padding: 7px 4px; }
          .metric-grid.three .metric { display: block; padding: 7px 5px; text-align: center; }
          .metric-grid.three .metric ha-icon { --mdc-icon-size: 18px; margin-bottom: 2px; }
          .metric-grid.three .metric strong { font-size: 13.5px; }
          .ups-footer { gap: 6px; }
          .ups-summary { font-size: 12px; }
        }
      </style>
      <ha-card class="${this._config.variant}">${content}</ha-card>`;

    const replaced = commitStableMarkup(this.shadowRoot, markup);

    const details = this.shadowRoot.querySelector("button.details");
    if (details && this._config.details_path && (replaced || !details._nikasDetailsBound)) {
      details._nikasDetailsBound = true;
      details.addEventListener("click", () => this._navigate(this._config.details_path));
    }
  }
}

if (!customElements.get("nikas-infrastructure-summary-v2")) {
  customElements.define("nikas-infrastructure-summary-v2", NikaSInfrastructureSummaryV2);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "nikas-infrastructure-summary-v2")) {
  window.customCards.push({
    type: "nikas-infrastructure-summary-v2",
    name: "NikaS Infrastructure Summary v2",
    description: "Compact infrastructure summary for generated NikaS dashboards",
    preview: false,
  });
}

(() => {
  const ELEMENT_NAME = "nikas-infrastructure-overview";
  const UI_VERSION = "0.37.1";
  if (customElements.get(ELEMENT_NAME)) return;

  const MIN_SCALE = 0.75;
  const MAX_SCALE = 2.0;
  const PAN_THRESHOLD = 6;
  const TAP_DURATION = 300;
  const DOUBLE_TAP_GAP = 420;
  const CLICK_GUARD = 460;

  function navigate(path) {
    if (!path || window.location.pathname === path) return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  function distance(left, right) {
    return Math.hypot(right.clientX - left.clientX, right.clientY - left.clientY);
  }

  function midpoint(left, right) {
    return {
      clientX: (left.clientX + right.clientX) / 2,
      clientY: (left.clientY + right.clientY) / 2,
    };
  }

  function finite(value, fallback) {
    return Number.isFinite(Number(value)) ? Number(value) : fallback;
  }

  class NikasInfrastructureOverview extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._hass = null;
      this._panel = null;
      this._pointers = new Map();
      this._session = null;
      this._pinch = null;
      this._lastTwoFingerTap = 0;
      this._suppressClicksUntil = 0;
      this._sendingPointerCancel = false;
      this._statusTimer = null;
      this._resizeObserver = null;
      this._frame = null;
      this._state = { scale: 1, x: 0, y: 0 };

      this._onPointerDown = (event) => this._pointerDown(event);
      this._onPointerMove = (event) => this._pointerMove(event);
      this._onPointerUp = (event) => this._pointerEnd(event, false);
      this._onPointerCancel = (event) => this._pointerEnd(event, true);
      this._onGuardedActivation = (event) => this._guardActivation(event);
      this._renderShell();
    }

    set hass(value) {
      this._hass = value;
      this.shadowRoot?.querySelectorAll("nikas-infrastructure-summary-v2").forEach((card) => {
        card.hass = value;
      });
    }

    get hass() {
      return this._hass;
    }

    set panel(value) {
      this._panel = value;
      this._loadState();
      this._renderPanelConfig();
      this._applyTransform();
      this._scheduleClamp();
    }

    get panel() {
      return this._panel;
    }

    connectedCallback() {
      this._installGestureListeners();
      this._observeGeometry();
      this._renderPanelConfig();
      this._applyTransform();
      this._scheduleClamp();
    }

    disconnectedCallback() {
      this._removeGestureListeners();
      this._resizeObserver?.disconnect();
      this._resizeObserver = null;
      if (this._frame !== null) {
        (window.cancelAnimationFrame || window.clearTimeout)(this._frame);
        this._frame = null;
      }
      if (this._statusTimer !== null) window.clearTimeout(this._statusTimer);
      this._statusTimer = null;
    }

    _config() {
      return this._panel?.config || this._panel || {};
    }

    _renderShell() {
      this.shadowRoot.innerHTML = `
        <style>
          :host{display:block;width:100%;height:100dvh;min-height:100%;overflow:hidden;background:var(--primary-background-color,#f4f6f8);color:var(--primary-text-color,#111827);font-family:var(--paper-font-body1_-_font-family,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}
          *{box-sizing:border-box}
          .app{position:relative;width:100%;height:100dvh;min-height:100%;display:grid;grid-template-rows:auto minmax(0,1fr) auto;overflow:hidden;background:var(--primary-background-color,#f4f6f8)}
          .header{z-index:20;display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;min-height:62px;padding:max(5px,env(safe-area-inset-top,0px)) max(8px,env(safe-area-inset-right,0px)) 5px max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-bottom:1px solid var(--divider-color,rgba(0,0,0,.12));box-shadow:0 2px 12px rgba(0,0,0,.06)}
          .rail{width:44px;height:44px;border:1px solid var(--divider-color,rgba(0,0,0,.12));border-radius:16px;display:grid;place-items:center;padding:0;background:var(--card-background-color,var(--ha-card-background,#fff));color:var(--primary-text-color,#111827);box-shadow:0 7px 20px rgba(23,45,76,.08);cursor:pointer;-webkit-tap-highlight-color:transparent}
          #refresh{color:var(--primary-color,#03a9f4)}
          .rail:focus-visible,.tab:focus-visible{outline:2px solid var(--primary-color,#03a9f4);outline-offset:1px}
          .rail ha-icon{--mdc-icon-size:25px;width:25px;height:25px}
          .heading{min-width:0;align-self:center;text-align:center;line-height:1.12}
          .heading strong,.heading span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.heading strong{font-size:23px;font-weight:800;letter-spacing:-.02em}.heading span{margin-top:3px;font-size:14px;font-weight:560;color:var(--secondary-text-color,#6b7280)}
          .canvas-viewport{position:relative;min-width:0;min-height:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior-x:none;overscroll-behavior-y:none;touch-action:pan-y;background:var(--primary-background-color,#f4f6f8)}
          .canvas-viewport.zoomed{overflow:hidden;overscroll-behavior:none;touch-action:none;user-select:none;-webkit-user-select:none}
          .work-canvas{position:relative;margin:8px 12px 10px;min-width:0;min-height:calc(100% - 18px);height:max-content;padding-bottom:10px;transform-origin:0 0;transform:translate3d(0px,0px,0) scale(1);will-change:transform;contain:layout style;visibility:hidden}
          .canvas-viewport.zoomed .work-canvas{position:absolute;left:12px;right:12px;top:8px;margin:0}
          .work-canvas.ready{visibility:visible}
          .overview{width:min(100%,980px);margin:0 auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;align-items:start}
          nikas-infrastructure-summary-v2{display:block;min-width:0}
          nikas-infrastructure-summary-v2:first-child{grid-column:1/-1}
          .bottom{z-index:20;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-top:1px solid var(--divider-color,rgba(0,0,0,.12));box-shadow:0 -4px 18px rgba(0,0,0,.08)}
          nav{width:min(100%,720px);margin:0 auto;display:grid;grid-template-columns:repeat(var(--house-tab-count,3),minmax(0,1fr));gap:4px}
          .tab{appearance:none;border:0;background:transparent;color:var(--secondary-text-color,#5f6368);min-width:0;min-height:52px;padding:4px;border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}
          .tab ha-icon{--mdc-icon-size:28px;width:28px;height:28px}.tab span{display:block;width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;font-size:12px;line-height:15px;font-weight:700}
          .tab.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);cursor:default}
          .scale-status{position:absolute;z-index:40;left:50%;bottom:calc(82px + env(safe-area-inset-bottom,0px));transform:translate(-50%,10px);opacity:0;pointer-events:none;padding:9px 14px;border-radius:999px;background:rgba(20,27,34,.88);color:#fff;font-size:13px;font-weight:720;white-space:nowrap;transition:opacity .14s ease,transform .14s ease}
          .scale-status.visible{opacity:1;transform:translate(-50%,0)}
          @media(max-width:700px){.overview{grid-template-columns:1fr}.overview nikas-infrastructure-summary-v2:first-child{grid-column:auto}}
          @media(max-width:600px){:host{position:fixed;inset:0;width:auto;height:auto;min-height:0}.app{position:absolute;inset:0;width:auto;height:auto;min-height:0}}
          @media(max-width:390px){.header{grid-template-columns:48px minmax(0,1fr) 48px;min-height:60px}.heading strong{font-size:21px}.heading span{font-size:13px}.tab{padding-left:2px;padding-right:2px}.work-canvas{margin:7px 9px 8px;padding-bottom:8px}.canvas-viewport.zoomed .work-canvas{left:9px;right:9px;top:7px;margin:0}}
          @media(min-width:900px){.work-canvas{margin:14px 18px 16px;padding-bottom:16px}.canvas-viewport.zoomed .work-canvas{left:18px;right:18px;top:14px;margin:0}}
          @media(prefers-reduced-motion:reduce){.scale-status{transition:none}}
        </style>
        <div class="app">
          <header class="header">
            <button class="rail" id="menu" type="button" aria-label="Меню Home Assistant"><ha-icon icon="mdi:menu"></ha-icon></button>
            <div class="heading"><strong>Инфраструктура</strong><span>Сводка · UI v${UI_VERSION}</span></div>
            <button class="rail" id="refresh" type="button" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button>
          </header>
          <main class="canvas-viewport" aria-label="Рабочая область панели Инфраструктура">
            <div class="work-canvas"><div class="overview"></div></div>
          </main>
          <div class="bottom"><nav aria-label="Основная навигация"></nav></div>
          <div class="scale-status" role="status" aria-live="polite">Масштаб 100%</div>
        </div>`;

      this.shadowRoot.getElementById("menu").onclick = () => {
        this.dispatchEvent(new CustomEvent("hass-toggle-menu", {
          bubbles: true,
          composed: true,
        }));
      };
      this.shadowRoot.getElementById("refresh").onclick = () => window.location.reload();
    }

    _renderPanelConfig() {
      const config = this._config();
      const title = this.shadowRoot?.querySelector(".heading strong");
      if (title && config.title) title.textContent = config.title;

      const overview = this.shadowRoot?.querySelector(".overview");
      const cards = Array.isArray(config.cards) ? config.cards : [];
      if (overview && overview._nikasCards !== cards) {
        overview._nikasCards = cards;
        overview.replaceChildren();
        for (const cardConfig of cards) {
          const card = document.createElement("nikas-infrastructure-summary-v2");
          card.setConfig(cardConfig);
          if (this._hass) card.hass = this._hass;
          overview.appendChild(card);
        }
      }
      this._renderTabs();
      this._scheduleClamp();
    }

    _renderTabs() {
      const nav = this.shadowRoot?.querySelector("nav");
      if (!nav) return;
      const tabs = Array.isArray(this._config().tabs) ? this._config().tabs : [];
      nav.style.setProperty("--house-tab-count", String(Math.max(tabs.length, 1)));
      nav.replaceChildren();

      for (const tab of tabs) {
        const button = document.createElement("button");
        const active = tab.id === "infrastructure" || window.location.pathname === tab.path;
        button.type = "button";
        button.className = `tab${active ? " active" : ""}`;
        button.disabled = active;
        if (active) button.setAttribute("aria-current", "page");

        const icon = document.createElement("ha-icon");
        icon.setAttribute("icon", tab.icon || "mdi:view-dashboard-outline");
        const label = document.createElement("span");
        label.textContent = tab.label || tab.title || tab.id;
        button.append(icon, label);
        button.onclick = () => {
          if (!active) {
            this._resetForNavigation();
            navigate(tab.path);
          }
        };
        nav.appendChild(button);
      }
    }

    _storageKey() {
      const panelId = String(this._config().id || "infrastructure-overview").replace(/[^a-z0-9._-]/gi, "_");
      return `nikas:transform-canvas:v1:${panelId}`;
    }

    _loadState() {
      this._state = { scale: 1, x: 0, y: 0 };
      try {
        const stored = JSON.parse(window.localStorage.getItem(this._storageKey()) || "null");
        if (!stored || typeof stored !== "object") return;
        this._state = {
          scale: Math.min(MAX_SCALE, Math.max(MIN_SCALE, finite(stored.scale, 1))),
          x: finite(stored.x, 0),
          y: finite(stored.y, 0),
        };
        if (this._state.scale <= 1) this._state = { scale: this._state.scale, x: 0, y: 0 };
      } catch (_error) {
        // Local preference storage is optional; the in-memory transform remains usable.
      }
    }

    _persistState() {
      try {
        window.localStorage.setItem(this._storageKey(), JSON.stringify(this._state));
      } catch (_error) {
        // Keep the current session functional when storage is unavailable.
      }
    }

    _canvas() {
      return this.shadowRoot?.querySelector(".work-canvas");
    }

    _viewport() {
      return this.shadowRoot?.querySelector(".canvas-viewport");
    }

    _contentBounds(scale = this._state.scale) {
      const canvas = this._canvas();
      const viewport = this._viewport();
      if (!canvas || !viewport || scale <= 1) return { minX: 0, minY: 0 };
      const viewportWidth = Math.max(0, (viewport.clientWidth || 0) - (canvas.offsetLeft || 0));
      const viewportHeight = Math.max(0, (viewport.clientHeight || 0) - (canvas.offsetTop || 0));
      const contentWidth = Math.max(canvas.offsetWidth || 0, canvas.scrollWidth || 0);
      const contentHeight = Math.max(canvas.offsetHeight || 0, canvas.scrollHeight || 0);
      return {
        minX: Math.min(0, viewportWidth - contentWidth * scale),
        minY: Math.min(0, viewportHeight - contentHeight * scale),
      };
    }

    _clampedState(scale, x, y) {
      const safeScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, finite(scale, 1)));
      if (safeScale <= 1) return { scale: safeScale, x: 0, y: 0 };
      const bounds = this._contentBounds(safeScale);
      return {
        scale: safeScale,
        x: Math.min(0, Math.max(bounds.minX, finite(x, 0))),
        y: Math.min(0, Math.max(bounds.minY, finite(y, 0))),
      };
    }

    _setTransform(scale, x, y) {
      this._state = this._clampedState(scale, x, y);
      this._applyTransform();
    }

    _applyTransform() {
      const canvas = this._canvas();
      const viewport = this._viewport();
      if (!canvas || !viewport) return;
      const zoomed = this._state.scale > 1.0001;
      if (!zoomed) this._state = { scale: this._state.scale, x: 0, y: 0 };
      viewport.classList.toggle("zoomed", zoomed);
      const { scale, x, y } = this._state;
      canvas.style.transform = `translate3d(${x}px, ${y}px, 0) scale(${scale})`;
      canvas.classList.add("ready");
    }

    _scheduleClamp() {
      if (this._frame !== null) {
        (window.cancelAnimationFrame || window.clearTimeout)(this._frame);
      }
      const schedule = window.requestAnimationFrame || ((callback) => window.setTimeout(callback, 0));
      this._frame = schedule(() => {
        this._frame = null;
        const current = this._state;
        this._state = this._clampedState(current.scale, current.x, current.y);
        this._applyTransform();
        this._persistState();
      });
    }

    _observeGeometry() {
      if (this._resizeObserver || typeof ResizeObserver !== "function") return;
      this._resizeObserver = new ResizeObserver(() => this._scheduleClamp());
      const viewport = this._viewport();
      const canvas = this._canvas();
      if (viewport) this._resizeObserver.observe(viewport);
      if (canvas) this._resizeObserver.observe(canvas);
    }

    _installGestureListeners() {
      const viewport = this._viewport();
      if (!viewport || viewport.dataset.gesturesInstalled === "true") return;
      viewport.dataset.gesturesInstalled = "true";
      viewport.addEventListener("pointerdown", this._onPointerDown, { passive: false });
      viewport.addEventListener("pointermove", this._onPointerMove, { passive: false });
      viewport.addEventListener("pointerup", this._onPointerUp, { passive: false });
      viewport.addEventListener("pointercancel", this._onPointerCancel, { passive: false });
      viewport.addEventListener("click", this._onGuardedActivation, true);
      viewport.addEventListener("contextmenu", this._onGuardedActivation, true);
    }

    _removeGestureListeners() {
      const viewport = this._viewport();
      if (!viewport || viewport.dataset.gesturesInstalled !== "true") return;
      delete viewport.dataset.gesturesInstalled;
      viewport.removeEventListener("pointerdown", this._onPointerDown);
      viewport.removeEventListener("pointermove", this._onPointerMove);
      viewport.removeEventListener("pointerup", this._onPointerUp);
      viewport.removeEventListener("pointercancel", this._onPointerCancel);
      viewport.removeEventListener("click", this._onGuardedActivation, true);
      viewport.removeEventListener("contextmenu", this._onGuardedActivation, true);
    }

    _pointerRecord(event) {
      return {
        id: event.pointerId,
        clientX: event.clientX,
        clientY: event.clientY,
        startX: event.clientX,
        startY: event.clientY,
        holdTarget: event.composedPath?.()[0] || event.target,
      };
    }

    _pointerDown(event) {
      if (event.pointerType !== "touch") return;
      const record = this._pointerRecord(event);
      this._pointers.set(event.pointerId, record);
      if (this._state.scale > 1) this._capturePointer(event.pointerId);

      if (this._pointers.size === 1) {
        this._session = {
          startedAt: performance.now(),
          maxPointers: 1,
          moved: false,
          multi: false,
          cancelledHold: false,
          startState: { ...this._state },
          startX: record.clientX,
          startY: record.clientY,
        };
      } else if (this._pointers.size === 2 && this._session) {
        for (const pointer of this._pointers.values()) this._capturePointer(pointer.id);
        this._session.multi = true;
        this._session.maxPointers = 2;
        this._cancelPendingHolds();
        this._suppressClicksUntil = Date.now() + CLICK_GUARD;
        this._beginPinch();
        event.preventDefault();
      } else if (this._session) {
        this._session.maxPointers = Math.max(this._session.maxPointers, this._pointers.size);
        this._session.moved = true;
        this._cancelPendingHolds();
        event.preventDefault();
      }
    }

    _beginPinch() {
      const points = [...this._pointers.values()].slice(0, 2);
      if (points.length !== 2) return;
      const mid = midpoint(points[0], points[1]);
      const canvas = this._canvas();
      const viewport = this._viewport();
      if (!canvas || !viewport) return;
      const rect = viewport.getBoundingClientRect();
      const localX = mid.clientX - rect.left - canvas.offsetLeft;
      const localY = mid.clientY - rect.top - canvas.offsetTop;
      const nativeScrollY = this._state.scale <= 1 ? viewport.scrollTop : 0;
      this._pinch = {
        distance: Math.max(1, distance(points[0], points[1])),
        scale: this._state.scale,
        contentX: (localX - this._state.x) / this._state.scale,
        contentY: (localY + nativeScrollY - this._state.y) / this._state.scale,
        startMidX: mid.clientX,
        startMidY: mid.clientY,
      };
    }

    _pointerMove(event) {
      if (event.pointerType !== "touch") return;
      const record = this._pointers.get(event.pointerId);
      if (!record || !this._session) return;
      record.clientX = event.clientX;
      record.clientY = event.clientY;

      if (this._session.multi) {
        if (this._pointers.size < 2 || !this._pinch) return;
        const points = [...this._pointers.values()].slice(0, 2);
        const currentDistance = Math.max(1, distance(points[0], points[1]));
        const mid = midpoint(points[0], points[1]);
        const distanceDelta = Math.abs(currentDistance - this._pinch.distance);
        const midpointDelta = Math.hypot(
          mid.clientX - this._pinch.startMidX,
          mid.clientY - this._pinch.startMidY,
        );
        if (!this._session.moved && distanceDelta < PAN_THRESHOLD && midpointDelta < PAN_THRESHOLD) {
          return;
        }
        this._session.moved = true;
        const canvas = this._canvas();
        const viewport = this._viewport();
        if (!canvas || !viewport) return;
        const rect = viewport.getBoundingClientRect();
        const localX = mid.clientX - rect.left - canvas.offsetLeft;
        const localY = mid.clientY - rect.top - canvas.offsetTop;
        const scale = this._pinch.scale * currentDistance / this._pinch.distance;
        const boundedScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale));
        const x = localX - this._pinch.contentX * boundedScale;
        const y = localY - this._pinch.contentY * boundedScale;
        if (boundedScale > 1) viewport.scrollTop = 0;
        this._setTransform(boundedScale, x, y);
        this._suppressClicksUntil = Date.now() + CLICK_GUARD;
        event.preventDefault();
        return;
      }

      if (this._state.scale <= 1) return;
      const deltaX = event.clientX - this._session.startX;
      const deltaY = event.clientY - this._session.startY;
      if (!this._session.moved && Math.hypot(deltaX, deltaY) < PAN_THRESHOLD) return;
      if (!this._session.moved) {
        this._session.moved = true;
        this._cancelPendingHolds();
      }
      this._setTransform(
        this._session.startState.scale,
        this._session.startState.x + deltaX,
        this._session.startState.y + deltaY,
      );
      this._suppressClicksUntil = Date.now() + CLICK_GUARD;
      event.preventDefault();
    }

    _pointerEnd(event, cancelled) {
      if (this._sendingPointerCancel || event.pointerType !== "touch") return;
      const session = this._session;
      if (!session || !this._pointers.has(event.pointerId)) return;
      this._pointers.delete(event.pointerId);
      try {
        this._viewport()?.releasePointerCapture?.(event.pointerId);
      } catch (_error) {
        // The browser may already have released capture.
      }

      if (cancelled) session.moved = true;
      if (session.multi && this._pointers.size < 2 && this._pinch) {
        this._pinch = null;
        if (session.moved && this._state.scale >= 0.97 && this._state.scale <= 1.03) {
          this._resetTransform(true);
        } else {
          this._persistState();
        }
      }

      if (this._pointers.size !== 0) return;
      const elapsed = performance.now() - session.startedAt;
      const twoFingerTap = !cancelled
        && session.multi
        && session.maxPointers === 2
        && !session.moved
        && elapsed <= TAP_DURATION;

      if (twoFingerTap) {
        const now = performance.now();
        if (now - this._lastTwoFingerTap <= DOUBLE_TAP_GAP) {
          this._lastTwoFingerTap = 0;
          this._resetTransform(true);
        } else {
          this._lastTwoFingerTap = now;
        }
      } else if (session.moved || session.multi) {
        this._persistState();
      }

      if (session.moved || session.multi) {
        this._suppressClicksUntil = Date.now() + CLICK_GUARD;
      }
      this._session = null;
      this._pinch = null;
    }

    _cancelPendingHolds() {
      if (!this._session || this._session.cancelledHold) return;
      this._session.cancelledHold = true;
      this._sendingPointerCancel = true;
      try {
        for (const pointer of this._pointers.values()) {
          const target = pointer.holdTarget;
          if (!target?.dispatchEvent) continue;
          const init = {
            bubbles: true,
            composed: true,
            cancelable: false,
            pointerId: pointer.id,
            pointerType: "touch",
          };
          const cancelEvent = typeof PointerEvent === "function"
            ? new PointerEvent("pointercancel", init)
            : new Event("pointercancel", init);
          target.dispatchEvent(cancelEvent);
        }
      } finally {
        this._sendingPointerCancel = false;
      }
    }

    _guardActivation(event) {
      if (Date.now() >= this._suppressClicksUntil && !this._session?.moved && !this._session?.multi) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation?.();
    }

    _resetTransform(showStatus) {
      this._state = { scale: 1, x: 0, y: 0 };
      const viewport = this._viewport();
      if (viewport) viewport.scrollTop = 0;
      this._applyTransform();
      this._persistState();
      if (showStatus) this._showScaleStatus();
    }

    _resetForNavigation() {
      const viewport = this._viewport();
      if (viewport) viewport.scrollTop = 0;
      const current = this._state;
      this._state = this._clampedState(current.scale, 0, 0);
      this._applyTransform();
      this._persistState();
    }

    _capturePointer(pointerId) {
      try {
        this._viewport()?.setPointerCapture?.(pointerId);
      } catch (_error) {
        // Pointer capture is an optimization, not a state dependency.
      }
    }

    _showScaleStatus() {
      const status = this.shadowRoot?.querySelector(".scale-status");
      if (!status) return;
      if (this._statusTimer !== null) window.clearTimeout(this._statusTimer);
      status.classList.add("visible");
      this._statusTimer = window.setTimeout(() => {
        status.classList.remove("visible");
        this._statusTimer = null;
      }, 1100);
    }
  }

  customElements.define(ELEMENT_NAME, NikasInfrastructureOverview);
})();
