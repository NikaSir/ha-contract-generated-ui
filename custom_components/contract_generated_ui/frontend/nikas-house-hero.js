const ELEMENT_NAME = "nikas-house-hero";
const DEFAULT_ASSET = "/contract_generated_ui/frontend/assets/house-hero-photo-day-v3.webp?build=0340b001";
const GLOBAL_TABBAR_ID = "nikas-global-tabbar";
const BAD_STATES = new Set(["unknown", "unavailable", "none", "null", ""]);

const WEATHER_LABELS = {
  sunny: "Ясно",
  "clear-night": "Ясно",
  partlycloudy: "Переменная облачность",
  cloudy: "Облачно",
  rainy: "Дождь",
  pouring: "Ливень",
  snowy: "Снег",
  fog: "Туман",
  windy: "Ветрено",
  lightning: "Гроза",
  "lightning-rainy": "Гроза с дождём",
};

const WEATHER_ICONS = {
  sunny: "mdi:weather-sunny",
  "clear-night": "mdi:weather-night",
  partlycloudy: "mdi:weather-partly-cloudy",
  cloudy: "mdi:weather-cloudy",
  rainy: "mdi:weather-rainy",
  pouring: "mdi:weather-pouring",
  snowy: "mdi:weather-snowy",
  fog: "mdi:weather-fog",
  windy: "mdi:weather-windy",
  lightning: "mdi:weather-lightning",
  "lightning-rainy": "mdi:weather-lightning-rainy",
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function numeric(value) {
  const parsed = Number.parseFloat(String(value ?? "").replace(",", "."));
  return Number.isFinite(parsed) ? parsed : null;
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

class NikasHouseHero extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._timer = null;
    this._fitFrame = null;
    this._boundViewportFit = () => this._scheduleViewportFit();
  }

  setConfig(config) {
    if (!config || typeof config !== "object") throw new Error("nikas-house-hero requires a config object");
    this._config = config;
    this.toggleAttribute("standalone", config.standalone === true);
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 9; }

  connectedCallback() {
    if (!this._timer) this._timer = window.setInterval(() => this._render(), 60_000);
    window.addEventListener?.("resize", this._boundViewportFit, { passive: true });
    window.visualViewport?.addEventListener?.("resize", this._boundViewportFit, { passive: true });
    this._scheduleViewportFit();
  }

  disconnectedCallback() {
    if (this._timer) window.clearInterval(this._timer);
    this._timer = null;
    window.removeEventListener?.("resize", this._boundViewportFit);
    window.visualViewport?.removeEventListener?.("resize", this._boundViewportFit);
    if (this._fitFrame !== null) {
      (window.cancelAnimationFrame || window.clearTimeout)(this._fitFrame);
      this._fitFrame = null;
    }
  }

  _scheduleViewportFit() {
    if (!this.isConnected || typeof document === "undefined") return;
    if (this._fitFrame !== null) {
      (window.cancelAnimationFrame || window.clearTimeout)(this._fitFrame);
    }
    const schedule = window.requestAnimationFrame || ((callback) => window.setTimeout(callback, 0));
    this._fitFrame = schedule(() => {
      this._fitFrame = null;
      this._fitViewport();
    });
  }

  _fitViewport() {
    if (this._config?.standalone === true) return;
    const hero = this.shadowRoot?.querySelector(".hero");
    const tabBar = document.getElementById(GLOBAL_TABBAR_ID);
    if (!hero || !tabBar || typeof hero.getBoundingClientRect !== "function" || typeof tabBar.getBoundingClientRect !== "function") {
      return;
    }
    const top = hero.getBoundingClientRect().top;
    const bottom = tabBar.getBoundingClientRect().top;
    const available = Math.floor(bottom - top);
    if (!Number.isFinite(available) || available <= 0) return;
    const value = `${available}px`;
    if (this.style.getPropertyValue("--house-hero-available-height") !== value) {
      this.style.setProperty("--house-hero-available-height", value);
    }
  }

  _entity(id) { return id && this._hass?.states?.[id] ? this._hass.states[id] : null; }
  _state(id) { return this._entity(id)?.state ?? "unknown"; }
  _available(id) { return !BAD_STATES.has(String(this._state(id)).toLowerCase()); }
  _countOn(ids) { return (Array.isArray(ids) ? ids : []).filter((id) => this._state(id) === "on").length; }
  _countUnavailable(ids) { return (Array.isArray(ids) ? ids : []).filter((id) => !this._available(id)).length; }

  _security(ids) {
    const alarm = this._countOn(ids);
    const bad = this._countUnavailable(ids);
    if (alarm > 0) return { label: `Тревога ${alarm}`, tone: "red", icon: "mdi:shield-alert" };
    if (bad > 0) return { label: "Внимание", tone: "orange", icon: "mdi:shield-alert-outline" };
    return { label: "В норме", tone: "green", icon: "mdi:shield-check" };
  }

  _power(ids) {
    const values = (Array.isArray(ids) ? ids : []).map((id) => numeric(this._state(id)));
    if (values.length !== 3 || values.some((value) => value === null)) {
      return { label: "Нет данных", tone: "grey", detail: "Фазы недоступны", icon: "mdi:home-lightning-bolt-outline" };
    }
    const min = Math.min(...values);
    const max = Math.max(...values);
    // These three phases are measured before the LIDER PS7500W-30
    // stabilizers. Evaluate them against the stabilizer passport, not the
    // downstream ГОСТ voltage-quality policy.
    let label = "В норме";
    let tone = "green";
    if (min < 125 || max > 275) { label = "Авария"; tone = "red"; }
    else if (min < 150 || max > 265) { label = "Рабочий предел"; tone = "orange"; }
    return { label, tone, detail: `${min.toFixed(0)}–${max.toFixed(0)} В`, icon: "mdi:home-lightning-bolt" };
  }

  _water(id) {
    const value = numeric(this._state(id));
    if (value === null) return { label: "Нет данных", tone: "grey", detail: "Давление неизвестно", icon: "mdi:water-alert-outline" };
    if (value === 0) return { label: "Нет давления", tone: "red", detail: "0 бар", icon: "mdi:water-alert" };
    if (value < 2.4 || value > 3.6) return { label: "Отклонение", tone: "orange", detail: `${value.toFixed(1)} бар`, icon: "mdi:water-alert-outline" };
    return { label: "Есть", tone: "green", detail: `${value.toFixed(1)} бар`, icon: "mdi:water" };
  }

  _internet(id) {
    const state = this._state(id);
    if (state === "on") return { label: "Доступен", tone: "green", detail: "Онлайн", icon: "mdi:web" };
    if (state === "off") return { label: "Нет связи", tone: "red", detail: "Проверить WAN", icon: "mdi:web-off" };
    return { label: "Нет данных", tone: "grey", detail: "Статус неизвестен", icon: "mdi:web-off" };
  }

  _heating(cfg) {
    if (!cfg || typeof cfg !== "object") return { label: "Нет данных", tone: "grey", detail: "", icon: "mdi:radiator-disabled" };
    const main = this._state(cfg.main);
    const reserve = this._state(cfg.reserve);
    const circuits = [cfg.radiators, cfg.floor, cfg.circulation].filter(Boolean);
    const active = this._countOn(circuits);
    const bad = this._countUnavailable(circuits);
    const mainTemp = numeric(this._state(cfg.main_temp));
    const reserveTemp = numeric(this._state(cfg.reserve_temp));
    if (main === "on") return { label: "Активно", tone: "orange", detail: `Основной${mainTemp === null ? "" : ` · ${mainTemp.toFixed(0)} °C`}`, icon: "mdi:radiator" };
    if (reserve === "on") return { label: "Активно", tone: "orange", detail: `Резервный${reserveTemp === null ? "" : ` · ${reserveTemp.toFixed(0)} °C`}`, icon: "mdi:radiator" };
    if (active > 0) return { label: "Активно", tone: "orange", detail: "Контуры активны", icon: "mdi:radiator" };
    if (BAD_STATES.has(String(main).toLowerCase()) || BAD_STATES.has(String(reserve).toLowerCase()) || bad > 0) {
      return { label: "Нет данных", tone: "grey", detail: "Проверить отопление", icon: "mdi:radiator-disabled" };
    }
    return { label: "Ожидание", tone: "green", detail: "Система готова", icon: "mdi:radiator" };
  }

  _weather(id) {
    const entity = this._entity(id);
    if (!entity || BAD_STATES.has(String(entity.state).toLowerCase())) return { label: "Погода", detail: "Нет данных", icon: "mdi:weather-cloudy", tone: "grey" };
    const temperature = numeric(entity.attributes?.temperature);
    return {
      label: temperature === null ? WEATHER_LABELS[entity.state] ?? entity.state : `${temperature.toFixed(1)}°`,
      detail: WEATHER_LABELS[entity.state] ?? entity.state,
      icon: WEATHER_ICONS[entity.state] ?? "mdi:weather-partly-cloudy",
      tone: "blue",
    };
  }

  _camera(ids) {
    const total = Array.isArray(ids) ? ids.length : 0;
    const ok = (Array.isArray(ids) ? ids : []).filter((id) => this._available(id)).length;
    if (total === 0) return { label: "Камеры", detail: "Нет данных", tone: "grey", icon: "mdi:cctv-off" };
    return { label: `Камеры ${ok}/${total}`, detail: ok === total ? "Онлайн" : "Проверить", tone: ok === total ? "green" : ok > 0 ? "orange" : "red", icon: "mdi:cctv" };
  }

  _access(id, label, kind = "door") {
    const state = this._state(id);
    const openIcon = kind === "gate" ? "mdi:garage-open" : "mdi:door-open";
    const closedIcon = kind === "gate" ? "mdi:garage" : "mdi:door-closed";
    if (state === "on") return { label, detail: "Открыто", tone: "yellow", icon: openIcon };
    if (state === "off") return { label, detail: "Закрыто", tone: "green", icon: closedIcon };
    return { label, detail: "Нет данных", tone: "grey", icon: kind === "gate" ? "mdi:garage-alert" : "mdi:door-alert" };
  }

  _navigate(path) {
    if (!path || !String(path).startsWith("/")) return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  _bindRoutes() {
    this.shadowRoot?.querySelectorAll("[data-route]").forEach((node) => {
      if (node._nikasRouteBound) return;
      node._nikasRouteBound = true;
      node.addEventListener("click", () => this._navigate(node.dataset.route));
      node.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          this._navigate(node.dataset.route);
        }
      });
    });
  }

  _card(icon, title, value, tone, route, extra = "", utility = false) {
    return `<button class="${utility ? "utility-card" : "status-card"} ${tone}" data-route="${escapeHtml(route)}" type="button">
      <ha-icon icon="${escapeHtml(icon)}"></ha-icon>
      <span class="${utility ? "utility-copy" : "status-copy"}"><small>${escapeHtml(title)}</small><strong>${escapeHtml(value)}</strong><em${extra ? "" : " hidden"}>${escapeHtml(extra)}</em></span>
    </button>`;
  }

  _render() {
    if (!this._config || !this.shadowRoot) return;
    if (!this._hass) {
      if (!this.shadowRoot.firstChild) {
        this.shadowRoot.innerHTML = `<ha-card><div style="padding:24px;font-size:16px">Дом сейчас · загрузка…</div></ha-card>`;
      }
      return;
    }

    const entities = this._config.entities ?? {};
    const routes = this._config.routes ?? {};
    const asset = this._config.asset || DEFAULT_ASSET;
    const security = this._security(entities.safety);
    const openings = this._countOn(entities.openings);
    const openingBad = this._countUnavailable(entities.openings);
    const motion = this._countOn(entities.motion);
    const motionBad = this._countUnavailable(entities.motion);
    const lights = this._countOn(entities.lights);
    const lightBad = this._countUnavailable(entities.lights);
    const climateIds = Array.isArray(entities.climate) ? entities.climate : [];
    const climateActive = climateIds.filter((id) => ["heating", "cooling"].includes(this._entity(id)?.attributes?.hvac_action)).length;
    const climateBad = this._countUnavailable(climateIds);
    const windows = this._countOn(entities.windows);
    const gate = this._access(entities.access?.sectional, "Ворота", "gate");
    const entrance = this._access(entities.access?.entrance, "Входная");
    const weather = this._weather(entities.weather);
    const cameras = this._camera(entities.cameras);
    const power = this._power(entities.power);
    const water = this._water(entities.water);
    const internet = this._internet(entities.internet);
    const heating = this._heating(entities.heating);

    const openingsTone = openings > 0 ? "yellow" : openingBad > 0 ? "orange" : "green";
    const motionTone = motionBad > 0 ? "orange" : motion > 0 ? "yellow" : "green";
    const lightsTone = lightBad > 0 ? "orange" : lights > 0 ? "yellow" : "green";
    const climateTone = climateBad > 0 ? "orange" : climateActive > 0 ? "yellow" : "green";
    const windowTone = windows > 0 ? "yellow" : openingBad > 0 ? "orange" : "green";
    const now = new Date();
    const time = now.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
    const date = now.toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });

    const markup = `<style>
      :host{display:block;--green:#2ebd59;--yellow:#ffbf00;--orange:#f28b00;--red:#e53935;--blue:#209cee;--grey:#85929b;--ink:#15202b;--muted:#4f5d69}
      ha-card{overflow:hidden;border-radius:28px;background:#edf8ff;border:1px solid rgba(255,255,255,.9);box-shadow:0 16px 40px rgba(41,82,110,.14)}
      .hero{position:relative;height:760px;min-height:calc(100svh - 166px);max-height:850px;overflow:hidden;background:linear-gradient(180deg,rgba(255,255,255,.16),rgba(255,255,255,0) 30%,rgba(255,255,255,.06) 76%,rgba(235,248,255,.18)),url("${escapeHtml(asset)}") center 50%/cover no-repeat;color:var(--ink);font-family:var(--paper-font-body1_-_font-family,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}
      .hero::after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,rgba(255,255,255,.07),transparent 22%,transparent 78%,rgba(255,255,255,.07))}
      button{font:inherit;color:inherit}
      .top-grid{position:absolute;z-index:4;left:12px;right:12px;top:12px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
      .status-card,.float-card,.utility-card,.callout{border:1px solid rgba(255,255,255,.88);background:rgba(255,255,255,.86);backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);box-shadow:0 8px 24px rgba(64,91,108,.15)}
      .status-card{min-width:0;height:74px;padding:9px 8px;border-radius:18px;display:flex;gap:7px;align-items:center;cursor:pointer;text-align:left;appearance:none}
      [hidden]{display:none!important}.status-card ha-icon{width:24px;flex:0 0 24px}.status-copy{min-width:0;display:flex;flex-direction:column;line-height:1.1}.status-copy small{font-size:12px;font-weight:750;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.status-copy strong{margin-top:5px;font-size:15px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.status-copy em{margin-top:4px;font-size:12px;font-style:normal;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .green ha-icon,.green strong{color:var(--green)}.yellow ha-icon,.yellow strong{color:var(--yellow)}.orange ha-icon,.orange strong{color:var(--orange)}.red ha-icon,.red strong{color:var(--red)}.blue ha-icon,.blue strong{color:var(--blue)}.grey ha-icon,.grey strong{color:var(--grey)}
      .float-card{position:absolute;z-index:4;top:102px;border-radius:20px;padding:12px 14px;cursor:pointer;appearance:none}.weather{left:14px;min-width:118px}.clock{right:14px;text-align:right;min-width:148px}.float-main{display:flex;align-items:center;gap:9px;font-size:25px;font-weight:850}.float-main ha-icon{color:var(--blue)}.float-sub{display:block;margin-top:5px;font-size:12px;color:var(--muted)}
      .clock-camera{margin:6px -4px -4px auto;padding:4px;border:0;background:transparent;color:var(--orange);display:flex;align-items:center;justify-content:flex-end;gap:5px;font:inherit;font-size:12px;font-weight:800;cursor:pointer;appearance:none}.clock-camera ha-icon{--mdc-icon-size:17px;width:17px;height:17px}
      .clock-camera.green{color:var(--green)}.clock-camera.red{color:var(--red)}.clock-camera.grey{color:var(--grey)}
      .zones{position:absolute;z-index:2;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}.zone{fill:none;stroke:var(--green);stroke-width:4;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 7px rgba(46,189,89,.34))}.zone.yellow{stroke:var(--yellow);filter:drop-shadow(0 0 7px rgba(255,191,0,.42))}.zone.orange{stroke:var(--orange);filter:drop-shadow(0 0 7px rgba(242,139,0,.42))}.zone.red{stroke:var(--red);filter:drop-shadow(0 0 7px rgba(229,57,53,.4))}.zone.grey{stroke:rgba(122,137,148,.6);filter:none}
      .callout{position:absolute;z-index:4;border-radius:17px;padding:9px 12px;cursor:pointer;min-width:108px;appearance:none}.callout b{display:block;font-size:13px;color:var(--ink)}.callout span{display:block;margin-top:3px;font-size:12px;font-weight:800}.window-callout{left:7%;top:39%}.gate-callout{left:4%;top:59%}.door-callout{right:5%;top:56%}
      .utilities{position:absolute;z-index:4;left:12px;right:12px;bottom:14px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}.utility-card{border-radius:19px;padding:12px 11px;min-height:88px;cursor:pointer;appearance:none;text-align:left;display:grid;grid-template-columns:28px 1fr;column-gap:8px;align-items:start}.utility-card ha-icon{margin-top:2px}.utility-copy{min-width:0;display:flex;flex-direction:column}.utility-copy small{font-size:12px;font-weight:750;color:var(--ink)}.utility-copy strong{margin-top:5px;font-size:15px;font-weight:850}.utility-copy em{margin-top:5px;font-size:12px;font-style:normal;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      [data-route]:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
      @media(max-width:600px){
        ha-card{border-radius:22px}.hero{height:var(--house-hero-available-height,calc(100dvh - 224px));min-height:0;max-height:none;background-size:cover;background-position:center 50%}
        .top-grid{gap:5px;left:8px;right:8px;top:8px}.status-card{height:68px;padding:5px 3px;gap:2px;border-radius:14px;flex-direction:column;justify-content:center;text-align:center}.status-card ha-icon{width:20px;flex:0 0 20px}.status-copy{width:100%;align-items:center}.status-copy small{font-size:12px}.status-copy strong{margin-top:2px;font-size:14px}.status-copy em{display:none}
        .float-card{top:84px;padding:9px 10px}.float-main{font-size:21px}.float-sub{font-size:12px}.clock-camera{font-size:12px;margin-top:4px}.clock-camera ha-icon{--mdc-icon-size:15px;width:15px;height:15px}
        .window-callout{left:5%;top:38%}.gate-callout{left:3%;top:57%}.door-callout{right:3%;top:55%}.callout{min-width:92px;padding:7px 8px}.callout b{font-size:12px}.callout span{font-size:12px}
        .utilities{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;left:8px;right:8px;bottom:8px}.utility-card{min-height:68px;padding:8px;grid-template-columns:24px 1fr}.utility-copy small{font-size:12px}.utility-copy strong{font-size:14px}.utility-copy em{font-size:12px}
      }
      :host([standalone]){height:100%;min-height:0}
      :host([standalone]) ha-card,:host([standalone]) .hero{height:100%;min-height:0;max-height:none}
    </style>
    <ha-card><div class="hero" aria-label="${escapeHtml(this._config.title || "Дом сейчас")}">
      <div class="top-grid">
        ${this._card(security.icon,"Безопасность",security.label,security.tone,routes.safety)}
        ${this._card("mdi:door-open","Открыто",String(openings),openingsTone,routes.open)}
        ${this._card("mdi:motion-sensor","Движение",String(motion),motionTone,routes.activity)}
        ${this._card("mdi:lightbulb-group","Свет",String(lights),lightsTone,routes.lights)}
        ${this._card("mdi:thermostat","Климат",String(climateActive),climateTone,routes.climate)}
      </div>
      <button class="float-card weather ${weather.tone}" data-route="${escapeHtml(routes.weather)}" type="button"><span class="float-main"><ha-icon icon="${escapeHtml(weather.icon)}"></ha-icon>${escapeHtml(weather.label)}</span><span class="float-sub">${escapeHtml(weather.detail)}</span></button>
      <div class="float-card clock"><span class="float-main">${escapeHtml(time)}</span><span class="float-sub">${escapeHtml(date)}</span><button class="clock-camera ${cameras.tone}" data-route="${escapeHtml(routes.cameras)}" type="button"><ha-icon icon="${escapeHtml(cameras.icon)}"></ha-icon>${escapeHtml(cameras.label)}</button></div>
      <svg class="zones" viewBox="0 0 1024 1536" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <rect class="zone ${windowTone}" x="182" y="738" width="170" height="158" rx="14"></rect>
        <rect class="zone ${gate.tone}" x="112" y="986" width="260" height="188" rx="14"></rect>
        <rect class="zone ${entrance.tone}" x="724" y="974" width="128" height="200" rx="14"></rect>
      </svg>
      <button class="callout window-callout ${windowTone}" data-route="${escapeHtml(routes.open)}" type="button"><b>Окна</b><span>${escapeHtml(windows)} открыто</span></button>
      <button class="callout gate-callout ${gate.tone}" data-route="${escapeHtml(routes.open)}" type="button"><b>${escapeHtml(gate.label)}</b><span>${escapeHtml(gate.detail)}</span></button>
      <button class="callout door-callout ${entrance.tone}" data-route="${escapeHtml(routes.open)}" type="button"><b>${escapeHtml(entrance.label)}</b><span>${escapeHtml(entrance.detail)}</span></button>
      <div class="utilities">
        ${this._card(power.icon,"Электросеть",power.label,power.tone,routes.electricity,power.detail,true)}
        ${this._card(water.icon,"Вода",water.label,water.tone,routes.water,water.detail,true)}
        ${this._card(internet.icon,"Интернет",internet.label,internet.tone,routes.network,internet.detail,true)}
        ${this._card(heating.icon,"Отопление",heating.label,heating.tone,routes.heating,heating.detail,true)}
      </div>
    </div></ha-card>`;
    const replaced = commitStableMarkup(this.shadowRoot, markup);
    if (replaced) this._bindRoutes();
    this._scheduleViewportFit();
  }
}

if (!customElements.get(ELEMENT_NAME)) customElements.define(ELEMENT_NAME, NikasHouseHero);
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === ELEMENT_NAME)) {
  window.customCards.push({ type: ELEMENT_NAME, name: "NikaS House Visual State Scene", description: "Daytime visual state scene for the NikaS Home dashboard.", preview: false });
}
