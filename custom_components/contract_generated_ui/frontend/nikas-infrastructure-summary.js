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
    const status = unreliable
      ? this._status("Данные неполные", "unreliable")
      : event
        ? this._status("Отклонение", "event")
        : this._status("Нормально", "ok");

    const phase = (name, voltageRole, presentRole) => {
      const present = this._binary(presentRole);
      const tone = present === null ? "unreliable" : present ? "ok" : "event";
      return `
        <div class="phase ${tone}">
          <span class="phase-name">${name}</span>
          <strong>${this._escape(this._format(voltageRole))}</strong>
        </div>`;
    };

    return `
      <div class="card-header">
        <div><h2>${this._escape(this._config.title)}</h2><p>Трёхфазная сеть</p></div>
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
      </div>`;
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

    this.shadowRoot.innerHTML = `
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
        .metric-label { display: block; color: var(--secondary-text-color); font-size: 11.5px; line-height: 1.15; }
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
        .keenetic-primary span { display: block; color: var(--secondary-text-color); font-size: 11.5px; }
        .keenetic-primary strong { display: block; margin-top: 2px; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .reason { margin: 0 2px 7px; color: var(--secondary-text-color); font-size: 12.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .reason span { font-weight: 600; color: var(--primary-text-color); }
        .keenetic-metrics .metric { padding: 7px 8px; }
        @media (max-width: 420px) {
          ha-card { padding: 13px 14px; }
          ha-card.ups { padding: 11px 14px 6px; }
          ha-card.keenetic { padding: 13px 14px 11px; }
          h2 { font-size: 19px; }
          .status { font-size: 11.5px; padding: 6px 8px; }
          .phase { padding: 7px 4px; }
          .metric-grid.three .metric { display: block; padding: 7px 5px; text-align: center; }
          .metric-grid.three .metric ha-icon { --mdc-icon-size: 18px; margin-bottom: 2px; }
          .metric-grid.three .metric strong { font-size: 13.5px; }
          .ups-footer { gap: 6px; }
          .ups-summary { font-size: 11.5px; }
        }
      </style>
      <ha-card class="${this._config.variant}">${content}</ha-card>`;

    const details = this.shadowRoot.querySelector("button.details");
    if (details && this._config.details_path) {
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
