// Prototype-style read-only ZONT panel for Contract Generated UI.
// Intentionally contains no Home Assistant service calls or entity controls.
(() => {
  const ELEMENT_NAME = "nikas-generated-zont";
  if (customElements.get(ELEMENT_NAME)) return;

  const esc = (value) => String(value ?? "")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const low = (...values) => values.filter((v) => v != null).map((v) => String(v).toLocaleLowerCase()).join(" ");
  const has = (text, words) => words.some((word) => text.includes(String(word).toLocaleLowerCase()));
  const domainOf = (entityId) => String(entityId || "").split(".", 1)[0];

  function navigate(path) {
    if (!path) return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  class NikasGeneratedZont extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._hass = null;
      this._panel = null;
      this._active = null;
      this._registry = null;
      this._devices = new Map();
      this._loading = null;
      this._error = null;
      this._queued = false;
      this._onHash = () => { this._active = this._tabFromLocation(); this._queue(); };
    }

    set hass(value) { this._hass = value; this._load(); this._queue(); }
    get hass() { return this._hass; }
    set panel(value) { this._panel = value; this._active = this._tabFromLocation(); this._load(true); this._queue(); }
    get panel() { return this._panel; }

    connectedCallback() { window.addEventListener("hashchange", this._onHash); this._active = this._tabFromLocation(); this._load(); this._queue(); }
    disconnectedCallback() { window.removeEventListener("hashchange", this._onHash); }

    _config() { return this._panel?.config || this._panel || {}; }
    _tabs() { return Array.isArray(this._config().tabs) ? this._config().tabs : []; }
    _activeTab() { return this._tabs().find((tab) => tab.id === this._active) || this._tabs()[0]; }
    _tabFromLocation() {
      const hash = window.location.hash.replace(/^#/, "");
      return this._tabs().some((tab) => tab.id === hash) ? hash : this._tabs()[0]?.id;
    }
    _selectTab(id) {
      if (!id || id === this._active) return;
      this._active = id;
      window.history.replaceState(null, "", `${window.location.pathname}#${encodeURIComponent(id)}`);
      this._queue();
    }
    _queue() {
      if (this._queued) return;
      this._queued = true;
      requestAnimationFrame(() => { this._queued = false; this._render(); });
    }

    _load(force = false) {
      if (!this._hass?.callWS || (this._loading && !force) || (this._registry && !force)) return;
      this._error = null;
      this._loading = Promise.all([
        this._hass.callWS({ type: "config/entity_registry/list" }),
        this._hass.callWS({ type: "config/device_registry/list" }),
      ]).then(([entries, devices]) => {
        this._registry = Array.isArray(entries) ? entries : [];
        this._devices = new Map((Array.isArray(devices) ? devices : []).filter((d) => d?.id).map((d) => [d.id, d]));
      }).catch((error) => {
        this._registry = [];
        this._devices = new Map();
        this._error = error instanceof Error ? error.message : String(error);
      }).finally(() => { this._loading = null; this._queue(); });
    }

    _entries() {
      if (!Array.isArray(this._registry)) return [];
      const platforms = new Set(this._config().source?.platforms || ["zont", "zont_ha"]);
      return this._registry
        .filter((entry) => platforms.has(entry.platform) && !entry.disabled_by)
        .filter((entry) => this._hass?.states?.[entry.entity_id])
        .map((entry) => ({ entry, state: this._hass.states[entry.entity_id] }));
    }

    _rawName(item) {
      return item.state?.attributes?.friendly_name || item.entry.name || item.entry.original_name || item.entry.entity_id;
    }

    _deviceName(item) {
      const device = this._devices.get(item.entry.device_id);
      return device?.name_by_user || device?.name || device?.model || "";
    }

    _semanticName(item) {
      let name = String(this._rawName(item)).trim();
      const deviceName = String(this._deviceName(item)).trim();
      const prefixes = [deviceName, "ZONT", "Zont", "zont", "ZONT H-2000+", "ZONT H2000+", "H-2000+", "H2000+"]
        .filter(Boolean)
        .sort((a, b) => b.length - a.length);
      for (const prefix of prefixes) {
        const escaped = prefix.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        name = name.replace(new RegExp(`^${escaped}(?:\\s*[·:—–-]\\s*|\\s+)`, "i"), "");
        name = name.replace(new RegExp(`(?:\\s*[·:—–-]\\s*)${escaped}$`, "i"), "");
      }
      name = name
        .replace(/^датчик\s+/i, "")
        .replace(/^сенсор\s+/i, "")
        .replace(/\s{2,}/g, " ")
        .trim();
      return name || this._rawName(item);
    }

    _text(item) { return low(item.entry.entity_id, this._rawName(item), this._semanticName(item), item.state?.attributes?.device_class); }
    _number(item) {
      const value = Number(String(item.state?.state ?? "").replace(",", "."));
      return Number.isFinite(value) ? value : null;
    }
    _unit(item) { return item.state?.attributes?.unit_of_measurement || ""; }
    _formatted(item) {
      if (typeof this._hass?.formatEntityState === "function") {
        try { return this._hass.formatEntityState(item.state); } catch (_error) { /* factual fallback */ }
      }
      return `${item.state?.state ?? "—"}${this._unit(item) ? ` ${this._unit(item)}` : ""}`;
    }
    _icon(item) {
      const text = this._text(item);
      if (has(text, ["давлен", "pressure"])) return "mdi:gauge";
      if (has(text, ["температур", "temperature", "подача", "обратка", "гвс"])) return "mdi:thermometer";
      if (has(text, ["модуляц", "modulation", "горел", "flame"])) return "mdi:fire";
      if (has(text, ["батар", "battery"])) return "mdi:battery";
      if (has(text, ["rssi", "signal"])) return "mdi:wifi";
      if (has(text, ["ошиб", "fault", "error"])) return "mdi:wrench-outline";
      if (has(text, ["online", "контроллер", "controller"])) return "mdi:monitor-cellphone";
      if (has(text, ["питан", "напряж", "voltage", "power"])) return "mdi:sine-wave";
      if (has(text, ["влаж", "humidity"])) return "mdi:water-percent";
      return item.state?.attributes?.icon || item.entry.icon || (domainOf(item.entry.entity_id) === "binary_sensor" ? "mdi:checkbox-marked-circle-outline" : "mdi:gauge");
    }

    _filter(items, include = [], exclude = []) {
      let result = items.filter((item) => !include.length || has(this._text(item), include));
      if (exclude.length) result = result.filter((item) => !has(this._text(item), exclude));
      return result;
    }
    _first(items, words) { return items.find((item) => has(this._text(item), words)); }
    _all(items, words) { return items.filter((item) => has(this._text(item), words)); }
    _unique(items) {
      const seen = new Set();
      return items.filter((item) => !seen.has(item.entry.entity_id) && seen.add(item.entry.entity_id));
    }

    _gaugeScale(item) {
      const text = this._text(item);
      const unit = this._unit(item).toLocaleLowerCase();
      if (unit.includes("bar") || has(text, ["давлен", "pressure"])) return [0, 4];
      if (unit === "%" || has(text, ["модуляц", "modulation"])) return [0, 100];
      if (has(text, ["комнат", "гостиная", "детская", "улиц", "weather", "погод"])) return [-20, 40];
      if (has(text, ["радиатор", "тёпл", "тепл", "контур", "подача", "обратка", "котел", "котёл", "гвс"])) return [0, 90];
      if (unit.includes("°c") || unit.includes("°c") || has(text, ["температур", "temperature"])) return [0, 60];
      return [0, 100];
    }

    _gauge(item, label = null) {
      if (!item) return "";
      const value = this._number(item);
      if (value == null) return this._statusCard(item, label);
      const [min, max] = this._gaugeScale(item);
      const pct = Math.max(0, Math.min(1, (value - min) / (max - min)));
      const length = 251.3;
      const dash = (length * pct).toFixed(1);
      const unit = this._unit(item);
      const pretty = Number.isInteger(value) ? value.toFixed(0) : value.toLocaleString("ru-RU", { maximumFractionDigits: 1, minimumFractionDigits: unit.toLowerCase().includes("bar") ? 1 : 0 });
      return `<div class="gauge-card ${["unknown", "unavailable"].includes(item.state.state) ? "unreliable" : ""}">
        <svg viewBox="0 0 200 112" aria-hidden="true">
          <path class="gauge-track" d="M 25 100 A 75 75 0 0 1 175 100" pathLength="251.3"></path>
          <path class="gauge-value" d="M 25 100 A 75 75 0 0 1 175 100" pathLength="251.3" stroke-dasharray="${dash} ${length}"></path>
        </svg>
        <div class="gauge-number">${esc(pretty)} <small>${esc(unit)}</small></div>
        <div class="gauge-label">${esc(label || this._semanticName(item))}</div>
      </div>`;
    }

    _statusCard(item, label = null) {
      if (!item) return "";
      const unavailable = ["unknown", "unavailable"].includes(item.state?.state);
      return `<div class="status-card ${unavailable ? "unreliable" : ""}">
        <ha-icon icon="${esc(this._icon(item))}"></ha-icon>
        <div class="status-copy"><strong>${esc(label || this._semanticName(item))}</strong><span>${esc(this._formatted(item))}</span></div>
      </div>`;
    }

    _section(title, content, cls = "") {
      if (!content || !String(content).trim()) return "";
      return `<section class="subject ${esc(cls)}"><h2>${esc(title)}</h2>${content}</section>`;
    }
    _grid(items, mapper = (item) => this._statusCard(item)) {
      const html = this._unique(items).map(mapper).filter(Boolean).join("");
      return html ? `<div class="tile-grid">${html}</div>` : "";
    }
    _gaugeGrid(items, labels = []) {
      const html = this._unique(items).map((item, index) => this._gauge(item, labels[index] || null)).filter(Boolean).join("");
      return html ? `<div class="gauge-grid">${html}</div>` : "";
    }

    _overview(items) {
      const modulation = this._first(items, ["модуляц", "modulation"]);
      const hydro = this._first(items, ["гидрострел", "hydraulic", "гидро"]);
      const supply = this._first(items, ["котёл →", "котел →", "boiler supply", "подача кот", "подача"]);
      const ret = this._first(items, ["котёл ←", "котел ←", "boiler return", "обратка кот", "обратка"]);
      const pressures = this._all(items, ["давлен", "pressure"]).slice(0, 4);
      const main = this._filter(items, ["основн", "main boiler", "котел", "котёл"], ["резерв", "давлен", "pressure", "подача", "обратка", "модуляц", "ebus"]).slice(0, 6);
      const reserve = this._filter(items, ["резерв", "reserve"], ["контур"]).slice(0, 6);
      let html = "";
      html += this._section("Температура и модуляция", this._gaugeGrid([modulation, hydro, supply, ret].filter(Boolean)));
      html += this._section("Давление", this._gaugeGrid(pressures));
      html += this._section("Основной котёл", this._grid(main));
      html += this._section("Резервный котёл", this._grid(reserve));
      if (!html) html = this._section("Состояние", this._grid(items.slice(0, 20)));
      return html;
    }

    _circuits(items) {
      const groups = [
        ["Радиаторы", ["радиатор", "radiator"]],
        ["Тёплый пол", ["тёплый пол", "теплый пол", "warm floor", "floor"]],
        ["Резервный контур", ["резервный контур", "reserve circuit"]],
        ["Циркуляция", ["циркуляц", "circulation"]],
      ];
      let html = "";
      for (const [title, words] of groups) {
        const entries = this._filter(items, words);
        if (!entries.length) continue;
        const numeric = entries.filter((item) => this._number(item) != null && (this._unit(item).includes("°") || this._unit(item).toLowerCase().includes("bar")));
        const other = entries.filter((item) => !numeric.includes(item));
        html += this._section(title, `${this._gaugeGrid(numeric.slice(0, 2))}${this._grid(other.slice(0, 6))}`);
      }
      const dhw = this._filter(items, ["гвс", "dhw"]);
      html += this._section("ГВС", `${this._gaugeGrid(dhw.filter((i) => this._number(i) != null).slice(0, 2))}${this._grid(dhw.filter((i) => this._number(i) == null).slice(0, 4))}`);
      return html || this._section("Контуры", this._grid(items.slice(0, 30)));
    }

    _roomKey(item) {
      const semantic = this._semanticName(item);
      const known = ["Гостиная", "Детская 1", "Детская 2", "Спальня", "Кухня", "Холл", "Котельная", "Улица", "Погода"];
      for (const room of known) if (semantic.toLocaleLowerCase().includes(room.toLocaleLowerCase())) return room;
      const device = this._deviceName(item);
      if (device && !/zont|h-?2000/i.test(device)) return device;
      return semantic.split(/[·:—–-]/)[0].trim().split(/\s+(?:температура|влажность|батарея|rssi)/i)[0].trim() || "Датчики";
    }

    _rooms(items) {
      const relevant = this._filter(items, ["температур", "temperature", "влаж", "humidity", "battery", "батар", "rssi", "signal", "улиц", "weather", "погод"]);
      const groups = new Map();
      for (const item of relevant) {
        const key = this._roomKey(item);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(item);
      }
      let html = "";
      for (const [title, entries] of groups) html += this._section(title, this._grid(entries.slice(0, 8)));
      return html || this._section("Помещения", this._grid(items.slice(0, 30)));
    }

    _diagnostics(items) {
      const controller = this._filter(items, ["контроллер", "controller", "online", "питание", "power", "напряж", "voltage"]);
      const actuators = this._filter(items, ["открытие", "closing", "закрытие", "opening", "исполн", "actuator"]);
      const problems = items.filter((item) => ["unknown", "unavailable"].includes(item.state.state) || has(this._text(item), ["ошиб", "error", "fault", "авар"]));
      return `${this._section("Контроллер", this._grid(controller))}${this._section("Исполнительные механизмы", this._grid(actuators))}${this._section("Ошибки и доступность", this._grid(problems, (i) => this._statusCard(i)))}` || this._section("Диагностика", this._grid(items.slice(0, 30)));
    }

    _ebus(items) {
      const ebus = this._filter(items, ["ebus"]);
      const numeric = ebus.filter((item) => this._number(item) != null && (this._unit(item).includes("°") || this._unit(item).toLowerCase().includes("bar") || this._unit(item) === "%"));
      const other = ebus.filter((item) => !numeric.includes(item));
      return this._section("eBUS — дополнительный канал", `${this._gaugeGrid(numeric.slice(0, 6))}${this._grid(other.slice(0, 12))}`) || this._section("eBUS", this._grid(items.slice(0, 30)));
    }

    _content(active, items) {
      if (this._error) return `<div class="empty unreliable">Ошибка чтения реестра: ${esc(this._error)}</div>`;
      if (!Array.isArray(this._registry)) return `<div class="empty">Читаю данные ZONT…</div>`;
      if (!items.length) return `<div class="empty">Сущности ZONT не найдены.</div>`;
      if (active.id === "overview") return this._overview(items);
      if (active.id === "circuits") return this._circuits(items);
      if (active.id === "rooms") return this._rooms(items);
      if (active.id === "diagnostics") return this._diagnostics(items);
      if (active.id === "ebus") return this._ebus(items);
      return this._section(active.label || "ZONT", this._grid(items.slice(0, 30)));
    }

    _render() {
      const config = this._config();
      const tabs = this._tabs();
      const active = this._activeTab();
      if (!active || !tabs.length) return;
      const items = this._entries();
      const nav = tabs.map((tab) => `<button class="tab ${tab.id === active.id ? "active" : ""}" data-tab="${esc(tab.id)}" ${tab.id === active.id ? "disabled" : ""}><ha-icon icon="${esc(tab.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${esc(tab.label || tab.id)}</span></button>`).join("");
      this.shadowRoot.innerHTML = `
        <style>
          :host{display:block;min-height:100vh;background:var(--primary-background-color,#0f0f10);color:var(--primary-text-color,#eee);font-family:var(--paper-font-body1_-_font-family,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}*{box-sizing:border-box}
          .app{min-height:100vh;padding-bottom:calc(84px + env(safe-area-inset-bottom,0px))}.header{position:sticky;top:0;z-index:10;display:grid;grid-template-columns:52px 1fr 52px;align-items:center;min-height:72px;padding:max(7px,env(safe-area-inset-top,0px)) 10px 7px;background:var(--card-background-color,#1c1c1d);border-bottom:1px solid var(--divider-color,#333)}
          .rail{width:46px;height:46px;border:0;border-radius:14px;background:transparent;color:var(--primary-text-color,#eee);display:grid;place-items:center}.rail ha-icon{--mdc-icon-size:28px}.heading{text-align:center;min-width:0}.heading strong,.heading span{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.heading strong{font-size:21px}.heading span{margin-top:3px;font-size:12px;color:var(--secondary-text-color,#aaa)}
          main{width:min(100%,900px);margin:auto;padding:14px 16px 28px}.subject{margin:0 0 24px}.subject h2{margin:0 0 12px 7px;font-size:18px;font-weight:450;color:var(--primary-text-color,#eee)}
          .gauge-grid,.tile-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.gauge-card,.status-card{border:1px solid var(--divider-color,#3a3a3c);background:var(--card-background-color,#1c1c1d);border-radius:16px}.gauge-card{min-height:196px;padding:12px 10px 14px;text-align:center;position:relative}.gauge-card svg{width:100%;height:108px;overflow:visible}.gauge-track,.gauge-value{fill:none;stroke-width:25;stroke-linecap:butt}.gauge-track{stroke:#0c0c0d}.gauge-value{stroke:var(--success-color,#43a047)}.gauge-number{margin-top:-42px;font-size:35px;font-weight:350;line-height:1.1}.gauge-number small{font-size:.55em;color:var(--secondary-text-color,#aaa);font-weight:350}.gauge-label{margin-top:20px;font-size:15px;color:var(--primary-text-color,#eee)}
          .status-card{min-height:78px;padding:12px 14px;display:grid;grid-template-columns:40px minmax(0,1fr);gap:10px;align-items:center}.status-card ha-icon{--mdc-icon-size:27px;color:#4f8bc9}.status-copy{min-width:0}.status-copy strong,.status-copy span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.status-copy strong{font-size:15px;font-weight:700}.status-copy span{margin-top:4px;font-size:14px;color:var(--secondary-text-color,#c7c7c7)}.unreliable{border-color:var(--warning-color,#f9a825)!important}.empty{padding:18px;border:1px solid var(--divider-color,#333);border-radius:16px;background:var(--card-background-color,#1c1c1d);color:var(--secondary-text-color,#aaa)}
          .bottom{position:fixed;left:0;right:0;bottom:0;z-index:20;padding:6px 8px calc(6px + env(safe-area-inset-bottom,0px));background:var(--card-background-color,#1c1c1d);border-top:1px solid var(--divider-color,#333)}nav{width:min(100%,700px);margin:auto;display:grid;grid-template-columns:repeat(${tabs.length},minmax(0,1fr));gap:3px}.tab{border:0;background:transparent;color:var(--secondary-text-color,#999);min-width:0;min-height:61px;border-radius:13px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:5px 2px}.tab.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,transparent)}.tab ha-icon{--mdc-icon-size:24px}.tab span{width:100%;font-size:10.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
          @media(max-width:420px){main{padding-left:10px;padding-right:10px}.gauge-card{min-height:180px}.gauge-number{font-size:31px}.gauge-label{font-size:14px}.status-card{padding:10px 11px}.status-copy strong{font-size:14px}.status-copy span{font-size:13px}}
        </style>
        <div class="app"><header class="header"><button class="rail" id="back"><ha-icon icon="mdi:arrow-left"></ha-icon></button><div class="heading"><strong>ZONT</strong><span>${esc(config.subtitle || "Отопление и ГВС")}</span></div><button class="rail" id="refresh"><ha-icon icon="mdi:refresh"></ha-icon></button></header><main>${this._content(active, items)}</main><div class="bottom"><nav>${nav}</nav></div></div>`;
      this.shadowRoot.getElementById("back").onclick = () => navigate(config.parent?.path || "/dashboard-house/heating");
      this.shadowRoot.getElementById("refresh").onclick = () => { this._registry = null; this._load(true); };
      for (const button of this.shadowRoot.querySelectorAll("button[data-tab]")) button.onclick = () => this._selectTab(button.dataset.tab);
    }
  }

  customElements.define(ELEMENT_NAME, NikasGeneratedZont);
})();
