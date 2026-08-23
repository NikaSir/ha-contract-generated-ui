// Semantic read-only ZONT panel for Contract Generated UI.
// Inspired by the information density of the native ZONT app, without controls.
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

    connectedCallback() {
      window.addEventListener("hashchange", this._onHash);
      this._active = this._tabFromLocation();
      this._load();
      this._queue();
    }
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
    _text(item) {
      return low(item.entry.entity_id, this._rawName(item), item.entry.original_name, item.entry.name, item.state?.attributes?.device_class);
    }
    _number(item) {
      const value = Number(String(item?.state?.state ?? "").replace(",", "."));
      return Number.isFinite(value) ? value : null;
    }
    _unit(item) { return item?.state?.attributes?.unit_of_measurement || ""; }
    _formatted(item) {
      if (!item) return "—";
      if (typeof this._hass?.formatEntityState === "function") {
        try { return this._hass.formatEntityState(item.state); } catch (_error) { /* factual fallback */ }
      }
      return `${item.state?.state ?? "—"}${this._unit(item) ? ` ${this._unit(item)}` : ""}`;
    }

    _semanticName(item) {
      let name = String(this._rawName(item)).trim();
      name = name
        .replace(/^NikaS[_\s-]*H[-_ ]?2000\+?Pro[_\s:·—–-]*/i, "")
        .replace(/^NikaS[_\s-]*H[-_ ]?2000\+?[_\s:·—–-]*/i, "")
        .replace(/^ZONT[_\s:·—–-]*/i, "")
        .replace(/^H[-_ ]?2000\+?Pro[_\s:·—–-]*/i, "")
        .replace(/^eBUS[_\s:·—–-]*/i, "")
        .replace(/^TH[_\s:·—–-]*/i, "")
        .replace(/^ГВ[_\s:·—–-]*/i, "")
        .replace(/^Основной\s*№?\s*2[_\s:·—–-]*/i, "")
        .replace(/^Основной[_\s:·—–-]*/i, "")
        .replace(/[_]+/g, " ")
        .replace(/\s{2,}/g, " ")
        .trim();
      return name || "Параметр";
    }

    _find(items, include, exclude = []) {
      return items.find((item) => has(this._text(item), include) && (!exclude.length || !has(this._text(item), exclude)));
    }
    _filter(items, include, exclude = []) {
      return items.filter((item) => has(this._text(item), include) && (!exclude.length || !has(this._text(item), exclude)));
    }
    _unique(items) {
      const seen = new Set();
      return items.filter((item) => item && !seen.has(item.entry.entity_id) && seen.add(item.entry.entity_id));
    }

    _role(item) {
      const t = this._text(item);
      if (has(t, ["ошиб", "error", "fault", "авар"])) return "error";
      if (has(t, ["модуляц", "modulation"])) return "modulation";
      if (has(t, ["давлен", "pressure"])) {
        if (has(t, ["питьев", "хвс"])) return "pressure_dhw";
        if (has(t, ["полив"])) return "pressure_irrigation";
        if (has(t, ["теплонос", "систем"])) return "pressure_system";
        return "pressure_boiler";
      }
      if (has(t, ["гидрострел", "hydraulic"])) return "hydraulic";
      if (has(t, ["обратн", "return", "<<<", "←"])) return "return";
      if (has(t, ["подач", "supply", ">>>", "→"])) return "supply";
      if (has(t, ["гвс", "горяч", "dhw"])) return "dhw";
      if (has(t, ["циркуляц", "circulation"])) return "circulation";
      if (has(t, ["rssi", "signal"])) return "rssi";
      if (has(t, ["батар", "battery"])) return "battery";
      if (has(t, ["влаж", "humidity"])) return "humidity";
      if (has(t, ["online", "подключ", "controller online"])) return "online";
      if (has(t, ["питан", "power"])) return "power";
      if (has(t, ["напряж", "voltage"])) return "voltage";
      if (has(t, ["состояни", "status", "state"])) return "state";
      if (has(t, ["целев", "target", "расчёт", "расчет", "уставк"])) return "target";
      if (has(t, ["температур", "temperature", "t°", "градус"])) return "temperature";
      return "other";
    }

    _shortLabel(item) {
      const role = this._role(item);
      const map = {
        error: "Ошибка", modulation: "Модуляция", pressure_boiler: "Давление котла",
        pressure_system: "Давление системы", pressure_dhw: "Питьевая вода",
        pressure_irrigation: "Вода на полив", hydraulic: "Гидрострелка", return: "Обратка",
        supply: "Подача", dhw: "ГВС", circulation: "Циркуляция", rssi: "RSSI",
        battery: "Батарея", humidity: "Влажность", online: "Контроллер",
        power: "Питание", voltage: "Напряжение", state: "Состояние",
        target: "Расчётная", temperature: "Температура",
      };
      return map[role] || this._semanticName(item).replace(/\s*(?:>>>|<<<|->|<-)+\s*$/g, "").slice(0, 28);
    }

    _icon(item, context = "") {
      const t = `${this._text(item)} ${context}`;
      if (has(t, ["радиатор"])) return "mdi:radiator";
      if (has(t, ["тёпл", "тепл", "floor"])) return "mdi:heating-coil";
      if (has(t, ["гвс", "горяч", "dhw"])) return "mdi:water-boiler";
      if (has(t, ["циркуляц"])) return "mdi:pump";
      if (has(t, ["котел", "котёл", "boiler"])) return "mdi:water-boiler";
      if (has(t, ["давлен", "pressure"])) return "mdi:gauge";
      if (has(t, ["влаж", "humidity"])) return "mdi:water-percent";
      if (has(t, ["батар", "battery"])) return "mdi:battery";
      if (has(t, ["rssi", "signal"])) return "mdi:wifi";
      if (has(t, ["ошиб", "error", "fault"])) return "mdi:wrench-outline";
      return item?.state?.attributes?.icon || item?.entry?.icon || "mdi:thermometer";
    }

    _value(item, fallback = "—") { return item ? this._formatted(item) : fallback; }
    _isProblem(item) { return item && ["unknown", "unavailable"].includes(item.state?.state); }

    _meterScale(item) {
      const role = this._role(item);
      const t = this._text(item);
      if (role.startsWith("pressure_")) return [0, 4];
      if (role === "humidity" || role === "modulation" || role === "battery") return [0, 100];
      if (has(t, ["улиц", "вне дома", "weather", "погод"])) return [-40, 50];
      if (has(t, ["комнат", "гостиная", "детская"])) return [15, 40];
      return [5, 75];
    }

    _meterCard(item, label = null, icon = null) {
      if (!item) return "";
      const value = this._number(item);
      if (value == null) return this._compactCard(item, label);
      const [min, max] = this._meterScale(item);
      const pct = Math.max(0, Math.min(1, (value - min) / (max - min)));
      return `<div class="meter-card ${this._isProblem(item) ? "problem" : ""}">
        <div class="meter"><span class="meter-max">${esc(max)}</span><i></i><b style="bottom:${(pct * 100).toFixed(1)}%"></b><span class="meter-min">${esc(min)}</span></div>
        <div class="meter-body"><div class="meter-value">${esc(this._formatted(item))}</div><ha-icon icon="${esc(icon || this._icon(item))}"></ha-icon><div class="meter-label">${esc(label || this._shortLabel(item))}</div></div>
      </div>`;
    }

    _compactCard(item, label = null) {
      if (!item) return "";
      return `<div class="compact-card ${this._isProblem(item) ? "problem" : ""}"><ha-icon icon="${esc(this._icon(item))}"></ha-icon><div><strong>${esc(label || this._shortLabel(item))}</strong><span>${esc(this._formatted(item))}</span></div></div>`;
    }

    _boilerSet(items, reserve = false) {
      const key = reserve ? ["резерв", "reserve"] : ["основн", "main", "ebus"];
      const reject = reserve ? [] : ["резерв", "reserve"];
      const scoped = items.filter((item) => has(this._text(item), key) && (!reject.length || !has(this._text(item), reject)));
      const source = scoped.length ? scoped : items;
      return {
        state: this._find(source, ["состояни", "status", "state"], ["контур"]),
        current: this._find(source, ["текущ", "сейчас", "current", "t°", "температур"], ["гвс", "обрат", "подач", "вне дома", "улиц"]),
        target: this._find(source, ["целев", "target", "расчёт", "расчет", "уставк"]),
        modulation: this._find(source, ["модуляц", "modulation"]),
        pressure: this._find(source, ["давлен", "pressure"], ["полив", "питьев", "хвс"]),
        error: this._find(source, ["ошиб", "error", "fault"]),
        supply: this._find(source, ["подач", "supply", ">>>"]),
        ret: this._find(source, ["обрат", "return", "<<<"]),
      };
    }

    _boilerCard(title, set, reserve = false) {
      const rows = [
        ["Состояние", this._value(set.state, reserve ? "Резерв" : "—")],
        ["Сейчас", this._value(set.current)], ["Расчётная", this._value(set.target)],
        ["Модуляция", this._value(set.modulation)], ["Давление", this._value(set.pressure)],
        ["Ошибка", this._value(set.error, "Ошибок нет")],
      ].filter(([, value]) => value !== "—");
      return `<div class="system-card boiler-card"><div class="system-title"><ha-icon icon="${reserve ? "mdi:water-boiler-off" : "mdi:water-boiler"}"></ha-icon><strong>${esc(title)}</strong></div><div class="system-rows">${rows.map(([k,v]) => `<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}</div>${set.supply || set.ret ? `<div class="flow-line"><span>→ ${esc(this._value(set.supply))}</span><span>← ${esc(this._value(set.ret))}</span></div>` : ""}</div>`;
    }

    _circuitItems(items, words) { return items.filter((item) => has(this._text(item), words)); }
    _circuitCard(items, title, words, icon) {
      const scoped = this._circuitItems(items, words);
      if (!scoped.length) return "";
      const current = this._find(scoped, ["текущ", "current", "температур", "t°"], ["целев", "target", ">>>", "<<<"] ) || scoped.find((i) => this._number(i) != null);
      const target = this._find(scoped, ["целев", "target", "расчёт", "расчет", "уставк"]);
      const supply = this._find(scoped, ["подач", "supply", ">>>"]);
      const ret = this._find(scoped, ["обрат", "return", "<<<"]);
      const state = this._find(scoped, ["включ", "active", "состояни", "status"]);
      return `<div class="system-card circuit-card"><div class="system-title"><ha-icon icon="${esc(icon)}"></ha-icon><strong>${esc(title)}</strong></div><div class="current-line"><span>Сейчас</span><b>${esc(this._value(current))}</b></div>${target ? `<div class="target-line"><span>Расчётная</span><b>${esc(this._value(target))}</b></div>` : ""}${supply || ret ? `<div class="flow-line"><span>→ ${esc(this._value(supply))}</span><span>← ${esc(this._value(ret))}</span></div>` : ""}${state ? `<div class="card-foot">${esc(this._formatted(state))}</div>` : ""}</div>`;
    }

    _roomName(item) {
      const t = this._text(item);
      const known = ["Гостиная", "Детская 1", "Детская 2", "Спальня", "Кухня", "Холл", "Котельная"];
      for (const name of known) if (t.includes(name.toLocaleLowerCase())) return name;
      if (has(t, ["улиц", "вне дома", "outdoor"])) return "Улица";
      if (has(t, ["погод", "weather", "internet"])) return "Погода";
      return null;
    }

    _roomGroups(items) {
      const groups = new Map();
      for (const item of items) {
        const name = this._roomName(item);
        if (!name) continue;
        if (!groups.has(name)) groups.set(name, []);
        groups.get(name).push(item);
      }
      return groups;
    }

    _roomCard(name, items) {
      const temp = this._find(items, ["температур", "temperature", "t°"]) || items.find((i) => this._unit(i).includes("°"));
      const hum = this._find(items, ["влаж", "humidity"]);
      const bat = this._find(items, ["батар", "battery"]);
      const rssi = this._find(items, ["rssi", "signal"]);
      const main = temp || hum || items[0];
      const value = this._value(main);
      const [min,max] = this._meterScale(main);
      const n = this._number(main);
      const pct = n == null ? 0 : Math.max(0, Math.min(1, (n-min)/(max-min)));
      return `<div class="room-card"><div class="room-meter"><span>${esc(max)}</span><i></i><b style="bottom:${(pct*100).toFixed(1)}%"></b><small>${esc(min)}</small></div><div class="room-body"><div class="room-value">${esc(value)}</div><ha-icon icon="${name === "Улица" ? "mdi:weather-partly-cloudy" : "mdi:home-thermometer-outline"}"></ha-icon><strong>${esc(name)}</strong><div class="room-meta">${hum ? `<span>💧 ${esc(this._formatted(hum))}</span>` : ""}${bat ? `<span>🔋 ${esc(this._formatted(bat))}</span>` : ""}${rssi ? `<span>📶 ${esc(this._formatted(rssi))}</span>` : ""}</div></div></div>`;
    }

    _section(title, content) { return content ? `<section><h2>${esc(title)}</h2>${content}</section>` : ""; }
    _grid(content, cls = "card-grid") { return content ? `<div class="${cls}">${content}</div>` : ""; }

    _overview(items) {
      const boilers = this._grid(this._boilerCard("Основной котёл", this._boilerSet(items, false)) + this._boilerCard("Резервный котёл", this._boilerSet(items, true)));
      const circuits = [
        this._circuitCard(items, "Радиаторы", ["радиатор"], "mdi:radiator"),
        this._circuitCard(items, "Тёплый пол", ["тёпл", "тепл", "floor"], "mdi:heating-coil"),
        this._circuitCard(items, "ГВС", ["гвс", "горяч", "dhw"], "mdi:water-boiler"),
        this._circuitCard(items, "Циркуляция", ["циркуляц", "circulation"], "mdi:pump"),
      ].join("");
      const rooms = [...this._roomGroups(items).entries()].slice(0, 4).map(([n,e]) => this._roomCard(n,e)).join("");
      return `${this._section("Котлы", boilers)}${this._section("Отопление", this._grid(circuits))}${this._section("Дом", this._grid(rooms))}`;
    }

    _boilers(items) {
      const main = this._boilerSet(items, false);
      const reserve = this._boilerSet(items, true);
      const meters = this._unique([main.current, main.target, main.modulation, main.pressure, main.supply, main.ret, reserve.current, reserve.target]).map((i) => this._meterCard(i)).join("");
      return `${this._section("Котловые контуры", this._grid(this._boilerCard("Основной", main) + this._boilerCard("Резервный", reserve)))}${this._section("Параметры", this._grid(meters))}`;
    }

    _heating(items) {
      const cards = [
        this._circuitCard(items, "Радиаторы", ["радиатор"], "mdi:radiator"),
        this._circuitCard(items, "Тёплый пол", ["тёпл", "тепл", "floor"], "mdi:heating-coil"),
        this._circuitCard(items, "ГВС", ["гвс", "горяч", "dhw"], "mdi:water-boiler"),
        this._circuitCard(items, "Циркуляция", ["циркуляц", "circulation"], "mdi:pump"),
        this._circuitCard(items, "Резервный контур", ["резерв", "reserve"], "mdi:water-boiler-off"),
      ].join("");
      const metricWords = ["радиатор", "тёпл", "тепл", "гвс", "циркуляц", "резерв", "гидрострел"];
      const metrics = this._unique(items.filter((i) => has(this._text(i), metricWords) && this._number(i) != null)).slice(0, 12).map((i) => this._meterCard(i)).join("");
      return `${this._section("Отопительные контуры", this._grid(cards))}${this._section("Температуры", this._grid(metrics))}`;
    }

    _sensors(items) {
      const rooms = [...this._roomGroups(items).entries()].map(([name,entries]) => this._roomCard(name, entries)).join("");
      const pressures = this._unique(items.filter((i) => this._role(i).startsWith("pressure_") && !has(this._text(i), ["котел", "котёл", "ebus"]))).slice(0, 6).map((i) => this._meterCard(i)).join("");
      return `${this._section("Помещения и улица", this._grid(rooms))}${this._section("Давление", this._grid(pressures))}`;
    }

    _diagnostics(items) {
      const controller = this._unique(items.filter((i) => ["online","power","voltage"].includes(this._role(i)))).slice(0, 8).map((i) => this._compactCard(i)).join("");
      const errors = this._unique(items.filter((i) => this._role(i) === "error"));
      const actualProblems = this._unique(items.filter((i) => this._isProblem(i) && !["rssi","battery"].includes(this._role(i)))).slice(0, 8);
      const eBus = this._unique(items.filter((i) => has(this._text(i), ["ebus"]) && ["modulation","pressure_boiler","temperature","dhw","return","supply"].includes(this._role(i)))).slice(0, 8).map((i) => this._compactCard(i)).join("");
      const errorHtml = errors.length ? errors.slice(0, 6).map((i) => this._compactCard(i)).join("") : `<div class="ok-card"><ha-icon icon="mdi:check-circle-outline"></ha-icon><span>Ошибок нет</span></div>`;
      const problemsHtml = actualProblems.length ? actualProblems.map((i) => this._compactCard(i)).join("") : "";
      return `${this._section("Контроллер", this._grid(controller))}${this._section("Ошибки", this._grid(errorHtml))}${problemsHtml ? this._section("Проблемы доступности", this._grid(problemsHtml)) : ""}${this._section("eBUS", this._grid(eBus))}`;
    }

    _content(active, items) {
      if (this._error) return `<div class="empty problem">Ошибка чтения реестра: ${esc(this._error)}</div>`;
      if (!Array.isArray(this._registry)) return `<div class="empty">Читаю данные ZONT…</div>`;
      if (!items.length) return `<div class="empty">Сущности ZONT не найдены.</div>`;
      if (active.id === "overview") return this._overview(items);
      if (active.id === "boilers") return this._boilers(items);
      if (active.id === "heating") return this._heating(items);
      if (active.id === "sensors") return this._sensors(items);
      if (active.id === "diagnostics") return this._diagnostics(items);
      return this._overview(items);
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
          :host{display:block;min-height:100vh;background:var(--primary-background-color,#f2f3f5);color:var(--primary-text-color,#202124);font-family:var(--paper-font-body1_-_font-family,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}*{box-sizing:border-box}
          .app{min-height:100vh;padding-bottom:calc(82px + env(safe-area-inset-bottom,0px))}.header{position:sticky;top:0;z-index:10;display:grid;grid-template-columns:50px 1fr 50px;align-items:center;min-height:70px;padding:max(6px,env(safe-area-inset-top,0px)) 10px 6px;background:var(--card-background-color,#fff);border-bottom:1px solid var(--divider-color,#ddd)}.rail{width:46px;height:46px;border:0;background:transparent;color:var(--primary-text-color,#202124);display:grid;place-items:center}.rail ha-icon{--mdc-icon-size:28px}.heading{text-align:center;min-width:0}.heading strong,.heading span{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.heading strong{font-size:21px}.heading span{margin-top:3px;font-size:12px;color:var(--secondary-text-color,#777)}
          main{width:min(100%,920px);margin:auto;padding:14px 16px 28px}section{margin-bottom:24px}section h2{margin:0 0 11px 3px;font-size:18px;font-weight:500}.card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.system-card,.meter-card,.room-card,.compact-card,.ok-card{background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd);border-radius:16px}.system-card{padding:14px}.system-title{display:flex;align-items:center;gap:9px;font-size:18px}.system-title ha-icon{color:var(--primary-color,#0097a7);--mdc-icon-size:28px}.system-title strong{font-weight:600}.system-rows{margin-top:12px;display:grid;gap:7px}.system-rows>div,.flow-line,.current-line,.target-line{display:flex;justify-content:space-between;gap:8px;align-items:baseline}.system-rows span,.target-line span{color:var(--secondary-text-color,#777);font-size:12px}.system-rows b,.current-line b,.target-line b{font-size:15px;font-weight:650}.current-line{margin-top:12px}.current-line span{color:#ef8b00;font-size:13px}.current-line b{font-size:20px}.target-line{margin-top:5px}.flow-line{margin-top:9px;padding-top:8px;border-top:1px solid var(--divider-color,#eee);font-size:12px;color:var(--secondary-text-color,#666)}.card-foot{margin-top:8px;font-size:12px;color:var(--secondary-text-color,#777)}
          .meter-card{min-height:170px;padding:12px;display:grid;grid-template-columns:42px 1fr;gap:7px}.meter{position:relative;height:140px}.meter i{position:absolute;left:20px;top:8px;bottom:8px;width:5px;border-radius:6px;background:color-mix(in srgb,var(--primary-color,#00aeb7) 22%,transparent)}.meter b{position:absolute;left:16px;width:13px;height:4px;border-radius:4px;background:var(--primary-color,#00aeb7);transform:translateY(50%)}.meter-max,.meter-min{position:absolute;left:0;font-size:10px;color:var(--secondary-text-color,#777)}.meter-max{top:0}.meter-min{bottom:0}.meter-body{min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:space-between}.meter-value{align-self:flex-start;font-size:25px;font-weight:450;white-space:nowrap}.meter-body ha-icon{--mdc-icon-size:46px;color:var(--primary-color,#0097a7)}.meter-label{width:100%;font-size:14px;line-height:1.2;text-align:left;overflow:hidden;text-overflow:ellipsis}
          .room-card{min-height:185px;padding:12px;display:grid;grid-template-columns:42px 1fr;gap:8px}.room-meter{position:relative;height:160px}.room-meter i{position:absolute;left:20px;top:7px;bottom:7px;width:5px;border-radius:6px;background:color-mix(in srgb,var(--primary-color,#00aeb7) 22%,transparent)}.room-meter b{position:absolute;left:16px;width:13px;height:4px;border-radius:4px;background:var(--primary-color,#00aeb7);transform:translateY(50%)}.room-meter span,.room-meter small{position:absolute;left:0;font-size:10px;color:var(--secondary-text-color,#777)}.room-meter span{top:0}.room-meter small{bottom:0}.room-body{min-width:0;display:flex;flex-direction:column;align-items:center}.room-value{align-self:flex-start;font-size:25px}.room-body>ha-icon{margin:9px 0 7px;--mdc-icon-size:48px;color:var(--primary-color,#0097a7)}.room-body>strong{font-size:15px}.room-meta{margin-top:auto;display:flex;flex-wrap:wrap;justify-content:center;gap:4px 8px;font-size:10px;color:var(--secondary-text-color,#777)}
          .compact-card{min-height:72px;padding:11px 13px;display:grid;grid-template-columns:38px minmax(0,1fr);gap:9px;align-items:center}.compact-card ha-icon{--mdc-icon-size:25px;color:var(--primary-color,#0097a7)}.compact-card strong,.compact-card span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.compact-card strong{font-size:14px}.compact-card span{margin-top:3px;font-size:12px;color:var(--secondary-text-color,#777)}.ok-card{min-height:72px;padding:14px;display:flex;align-items:center;gap:9px;color:var(--success-color,#43a047)}.ok-card ha-icon{--mdc-icon-size:25px}.problem{border-color:var(--warning-color,#ff9800)!important}.empty{padding:18px;border:1px solid var(--divider-color,#ddd);border-radius:16px;background:var(--card-background-color,#fff)}
          .bottom{position:fixed;left:0;right:0;bottom:0;z-index:20;padding:6px 8px calc(6px + env(safe-area-inset-bottom,0px));background:var(--card-background-color,#fff);border-top:1px solid var(--divider-color,#ddd)}nav{width:min(100%,700px);margin:auto;display:grid;grid-template-columns:repeat(${tabs.length},minmax(0,1fr));gap:3px}.tab{border:0;background:transparent;color:var(--secondary-text-color,#777);min-width:0;min-height:60px;border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:5px 2px}.tab.active{color:var(--primary-color,#0097a7);background:color-mix(in srgb,var(--primary-color,#0097a7) 10%,transparent)}.tab ha-icon{--mdc-icon-size:24px}.tab span{width:100%;font-size:10.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
          @media(max-width:420px){main{padding-left:10px;padding-right:10px}.system-card{padding:12px}.system-title{font-size:16px}.meter-card{min-height:160px}.meter-value,.room-value{font-size:23px}.room-card{min-height:175px}.room-meta{font-size:9.5px}}
        </style>
        <div class="app"><header class="header"><button class="rail" id="back" aria-label="Назад"><ha-icon icon="mdi:arrow-left"></ha-icon></button><div class="heading"><strong>ZONT</strong><span>${esc(config.subtitle || "Отопление и ГВС")}</span></div><button class="rail" id="refresh" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button></header><main>${this._content(active, items)}</main><div class="bottom"><nav>${nav}</nav></div></div>`;
      this.shadowRoot.getElementById("back").onclick = () => navigate(config.parent?.path || "/dashboard-house/heating");
      this.shadowRoot.getElementById("refresh").onclick = () => { this._registry = null; this._load(true); };
      for (const button of this.shadowRoot.querySelectorAll("button[data-tab]")) button.onclick = () => this._selectTab(button.dataset.tab);
    }
  }

  customElements.define(ELEMENT_NAME, NikasGeneratedZont);
})();
