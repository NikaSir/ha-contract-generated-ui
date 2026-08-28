class NikaSAppShell extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
  }

  setConfig(config) {
    if (!config || !Array.isArray(config.items) || !config.items.length) {
      throw new Error("nikas-app-shell requires a non-empty items list");
    }
    this._config = config;
    this._render();
  }

  set hass(value) {
    this._hass = value;
  }

  getCardSize() {
    return 2;
  }

  _navigate(path) {
    if (!path || typeof path !== "string") return;
    window.NikasPanelNavigation?.navigate?.(path);
  }

  _render() {
    if (!this._config) return;

    const active = this._config.active;
    const items = this._config.items;
    const itemMarkup = items
      .map((item) => {
        const isActive = item.id === active;
        const current = isActive ? ' aria-current="page"' : "";
        const disabled = isActive ? " disabled" : "";
        const title = item.title || item.label || item.id;
        return `
          <button class="nav-item${isActive ? " active" : ""}"
                  data-path="${item.path}"
                  title="${title}"
                  aria-label="${title}"${current}${disabled}>
            <ha-icon icon="${item.icon}"></ha-icon>
            <span>${item.label}</span>
          </button>`;
      })
      .join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
          min-height: calc(76px + env(safe-area-inset-bottom, 0px));
        }

        .shell {
          position: fixed;
          z-index: 20;
          left: 0;
          right: 0;
          bottom: 0;
          box-sizing: border-box;
          padding: 6px max(8px, env(safe-area-inset-right, 0px))
                   calc(6px + env(safe-area-inset-bottom, 0px))
                   max(8px, env(safe-area-inset-left, 0px));
          background: var(--card-background-color, var(--ha-card-background, #fff));
          border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
          box-shadow: 0 -4px 18px rgba(0, 0, 0, 0.08);
        }

        nav {
          width: min(100%, 720px);
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(${items.length}, minmax(0, 1fr));
          gap: 4px;
        }

        .nav-item {
          appearance: none;
          border: 0;
          background: transparent;
          color: var(--secondary-text-color, #666);
          min-width: 0;
          min-height: 62px;
          padding: 7px 4px 5px;
          border-radius: 16px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
          font: inherit;
          cursor: pointer;
          -webkit-tap-highlight-color: transparent;
        }

        .nav-item ha-icon {
          --mdc-icon-size: 25px;
          width: 25px;
          height: 25px;
        }

        .nav-item span {
          display: block;
          width: 100%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          text-align: center;
          font-size: 12px;
          line-height: 16px;
          font-weight: 500;
        }

        .nav-item.active {
          color: var(--primary-color, #03a9f4);
          background: var(--ha-color-primary-95, rgba(3, 169, 244, 0.12));
          cursor: default;
        }

        .nav-item:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4);
          outline-offset: 1px;
        }

        @media (min-width: 900px) {
          nav {
            width: min(70vw, 720px);
          }
        }
      </style>
      <div class="shell" role="navigation" aria-label="NikaS">
        <nav>${itemMarkup}</nav>
      </div>`;

    this.shadowRoot.querySelectorAll("button[data-path]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!button.disabled) this._navigate(button.dataset.path);
      });
    });
  }
}

class NikaSInfrastructureSummary extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  setConfig(config) {
    const supported = new Set(["power_grid", "ups", "keenetic"]);
    if (!config || !supported.has(config.variant) || !config.roles) {
      throw new Error("nikas-infrastructure-summary requires a supported variant and roles");
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

  _navigate(path) {
    if (!path || typeof path !== "string") return;
    window.NikasPanelNavigation?.navigate?.(path);
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
      <div class="card-header">
        <div><h2>${this._escape(this._config.title)}</h2><p>${this._escape(this._format("operating_mode"))}</p></div>
        ${status}
      </div>
      <div class="metric-grid two">
        ${this._metric("АКБ", this._format("battery_capacity"), "mdi:battery")}
        ${this._metric("Нагрузка", this._format("output_load"), "mdi:gauge")}
      </div>
      <div class="summary-line">
        <span>${this._escape(cloudText)}</span>
        <span>·</span>
        <span>${this._escape(staleText)}</span>
      </div>
      ${details}`;
  }

  _keeneticMarkup() {
    const wanUnreliable = this._unreliable("active_wan");
    const wan = this._format("active_wan");
    const status = wanUnreliable
      ? this._status("WAN неизвестен", "unreliable")
      : this._status(`WAN · ${wan}`, "info");
    const reason = this._format("last_wan_switch_reason");

    return `
      <div class="card-header">
        <div><h2>${this._escape(this._config.title)}</h2><p>WAN / LTE</p></div>
        ${status}
      </div>
      <div class="keenetic-primary">
        <div><span>Активный WAN</span><strong>${this._escape(wan)}</strong></div>
        <div><span>Последняя смена</span><strong>${this._escape(this._format("last_wan_switch"))}</strong></div>
      </div>
      <div class="reason" title="${this._escape(reason)}">${this._escape(reason)}</div>
      <div class="metric-grid three">
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
          padding: 18px;
          border-radius: var(--ha-card-border-radius, 24px);
          box-sizing: border-box;
          overflow: hidden;
        }
        .card-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 16px;
        }
        h2 { margin: 0; font-size: 22px; line-height: 1.15; font-weight: 700; }
        p { margin: 5px 0 0; color: var(--secondary-text-color); font-size: 14px; }
        .status {
          flex: 0 0 auto;
          border-radius: 999px;
          padding: 8px 11px;
          font-size: 13px;
          line-height: 1;
          font-weight: 700;
          white-space: nowrap;
        }
        .status.ok { color: var(--success-color, #43a047); background: color-mix(in srgb, var(--success-color, #43a047) 13%, transparent); }
        .status.warning { color: var(--warning-color, #ff9800); background: color-mix(in srgb, var(--warning-color, #ff9800) 14%, transparent); }
        .status.event { color: var(--error-color, #db4437); background: color-mix(in srgb, var(--error-color, #db4437) 12%, transparent); }
        .status.unreliable { color: var(--secondary-text-color); background: var(--secondary-background-color, #eee); }
        .status.info { color: var(--primary-color); background: color-mix(in srgb, var(--primary-color) 12%, transparent); }
        .phase-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; }
        .phase {
          min-width: 0;
          padding: 12px 8px;
          border-radius: 16px;
          background: var(--secondary-background-color, #f4f4f4);
          text-align: center;
          border: 1px solid transparent;
        }
        .phase.ok { border-color: color-mix(in srgb, var(--success-color, #43a047) 30%, transparent); }
        .phase.event { border-color: color-mix(in srgb, var(--error-color, #db4437) 40%, transparent); }
        .phase.unreliable { opacity: .68; }
        .phase-name { display: block; color: var(--secondary-text-color); font-size: 13px; margin-bottom: 3px; }
        .phase strong { display: block; font-size: 17px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .metric-grid { display: grid; gap: 8px; }
        .metric-grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .metric-grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .metric {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: 9px;
          padding: 11px;
          border-radius: 16px;
          background: var(--secondary-background-color, #f4f4f4);
        }
        .metric ha-icon { color: var(--primary-color); --mdc-icon-size: 22px; flex: 0 0 auto; }
        .metric > div { min-width: 0; }
        .metric-label { display: block; color: var(--secondary-text-color); font-size: 12px; line-height: 1.2; }
        .metric strong { display: block; margin-top: 2px; font-size: 16px; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .summary-line { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 11px; color: var(--secondary-text-color); font-size: 13px; }
        .details {
          appearance: none;
          border: 0;
          background: transparent;
          color: var(--primary-color);
          min-height: 44px;
          margin: 8px -6px -8px auto;
          padding: 8px 6px;
          display: flex;
          align-items: center;
          gap: 2px;
          font: inherit;
          font-weight: 700;
          cursor: pointer;
        }
        .details ha-icon { --mdc-icon-size: 20px; }
        .keenetic-primary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-bottom: 9px; }
        .keenetic-primary > div { padding: 12px; border-radius: 16px; background: var(--secondary-background-color, #f4f4f4); min-width: 0; }
        .keenetic-primary span { display: block; color: var(--secondary-text-color); font-size: 12px; }
        .keenetic-primary strong { display: block; margin-top: 3px; font-size: 17px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .reason { margin: 0 2px 11px; color: var(--secondary-text-color); font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        @media (max-width: 420px) {
          ha-card { padding: 16px; }
          h2 { font-size: 20px; }
          .status { font-size: 12px; padding: 7px 9px; }
          .metric-grid.three .metric { display: block; padding: 10px 8px; text-align: center; }
          .metric-grid.three .metric ha-icon { margin-bottom: 4px; }
          .metric-grid.three .metric strong { font-size: 14px; }
        }
      </style>
      <ha-card>${content}</ha-card>`;

    const details = this.shadowRoot.querySelector("button.details");
    if (details && this._config.details_path) {
      details.addEventListener("click", () => this._navigate(this._config.details_path));
    }
  }
}

if (!customElements.get("nikas-app-shell")) {
  customElements.define("nikas-app-shell", NikaSAppShell);
}
if (!customElements.get("nikas-infrastructure-summary")) {
  customElements.define("nikas-infrastructure-summary", NikaSInfrastructureSummary);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "nikas-app-shell")) {
  window.customCards.push({
    type: "nikas-app-shell",
    name: "NikaS App Shell",
    description: "Fixed bottom navigation for NikaS central dashboards",
    preview: false,
  });
}
if (!window.customCards.some((card) => card.type === "nikas-infrastructure-summary")) {
  window.customCards.push({
    type: "nikas-infrastructure-summary",
    name: "NikaS Infrastructure Summary",
    description: "Compact infrastructure status card for generated NikaS dashboards",
    preview: false,
  });
}
