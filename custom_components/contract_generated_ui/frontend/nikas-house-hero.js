const ELEMENT_NAME = "nikas-house-hero";
const DEFAULT_ASSET = "/contract_generated_ui/frontend/assets/house-hero-dusk-v1.svg?build=0300b001";
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

class NikasHouseHero extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._timer = null;
  }

  setConfig(config) {
    if (!config || typeof config !== "object") {
      throw new Error("nikas-house-hero requires a config object");
    }
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 9;
  }

  connectedCallback() {
    if (!this._timer) this._timer = window.setInterval(() => this._render(), 60_000);
  }

  disconnectedCallback() {
    if (this._timer) window.clearInterval(this._timer);
    this._timer = null;
  }

  _entity(id) {
    return id && this._hass?.states?.[id] ? this._hass.states[id] : null;
  }

  _state(id) {
    return this._entity(id)?.state ?? "unknown";
  }

  _available(id) {
    return !BAD_STATES.has(String(this._state(id)).toLowerCase());
  }

  _countOn(ids) {
    return (Array.isArray(ids) ? ids : []).reduce(
      (count, id) => count + (this._state(id) === "on" ? 1 : 0),
      0
    );
  }

  _countUnavailable(ids) {
    return (Array.isArray(ids) ? ids : []).reduce(
      (count, id) => count + (this._available(id) ? 0 : 1),
      0
    );
  }

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
    let label = "В норме";
    let tone = "green";
    if (min < 198 || max > 242) {
      label = "Авария";
      tone = "red";
    } else if (min < 205 || max > 235) {
      label = "Отклонение";
      tone = "orange";
    } else if (min < 210 || max > 230) {
      label = "Внимание";
      tone = "yellow";
    }
    return { label, tone, detail: `${min.toFixed(0)}–${max.toFixed(0)} В`, icon: "mdi:home-lightning-bolt" };
  }

  _water(id) {
    const value = numeric(this._state(id));
    if (value === null) return { label: "Нет данных", tone: "grey", detail: "Давление неизвестно", icon: "mdi:water-alert-outline" };
    if (value === 0) return { label: "Нет давления", tone: "red", detail: "0 бар", icon: "mdi:water-alert" };
    if (value < 2.4 || value > 3.6) {
      return { label: "Отклонение", tone: "orange", detail: `${value.toFixed(1)} бар`, icon: "mdi:water-alert-outline" };
    }
    return { label: "Есть", tone: "green", detail: `${value.toFixed(1)} бар`, icon: "mdi:water" };
  }

  _internet(id) {
    const state = this._state(id);
    if (state === "on") return { label: "Доступен", tone: "green", detail: "Онлайн", icon: "mdi:web" };
    if (state === "off") return { label: "Нет связи", tone: "red", detail: "Проверить WAN", icon: "mdi:web-off" };
    return { label: "Нет данных", tone: "grey", detail: "Статус неизвестен", icon: "mdi:web-off" };
  }

  _heating(cfg) {
    if (!cfg || typeof cfg !== "object") {
      return { label: "Нет данных", tone: "grey", detail: "", icon: "mdi:radiator-disabled" };
    }
    const main = this._state(cfg.main);
    const reserve = this._state(cfg.reserve);
    const circuits = [cfg.radiators, cfg.floor, cfg.circulation].filter(Boolean);
    const active = this._countOn(circuits);
    const bad = this._countUnavailable(circuits);
    const mainTemp = numeric(this._state(cfg.main_temp));
    const reserveTemp = numeric(this._state(cfg.reserve_temp));

    if (main === "on") {
      return { label: "Активно", tone: "orange", detail: `Основной${mainTemp === null ? "" : ` · ${mainTemp.toFixed(0)} °C`}`, icon: "mdi:radiator" };
    }
    if (reserve === "on") {
      return { label: "Активно", tone: "orange", detail: `Резервный${reserveTemp === null ? "" : ` · ${reserveTemp.toFixed(0)} °C`}`, icon: "mdi:radiator" };
    }
    if (active > 0) return { label: "Активно", tone: "orange", detail: "Контуры активны", icon: "mdi:radiator" };
    if (BAD_STATES.has(String(main).toLowerCase()) || BAD_STATES.has(String(reserve).toLowerCase()) || bad > 0) {
      return { label: "Нет данных", tone: "grey", detail: "Проверить отопление", icon: "mdi:radiator-disabled" };
    }
    return { label: "Ожидание", tone: "green", detail: "Система готова", icon: "mdi:radiator" };
  }

  _weather(id) {
    const entity = this._entity(id);
    if (!entity || BAD_STATES.has(String(entity.state).toLowerCase())) {
      return { label: "Погода", detail: "Нет данных", icon: "mdi:weather-cloudy", tone: "grey" };
    }
    const temperature = numeric(entity.attributes?.temperature);
    return {
      label: temperature === null ? WEATHER_LABELS[entity.state] ?? entity.state : `${temperature.toFixed(1)}°`,
      detail: WEATHER_LABELS[entity.state] ?? entity.state,
      icon: WEATHER_ICONS[entity.state] ?? "mdi:weather-partly-cloudy",
      tone: "blue",
    };
  }

  _camera(ids) {
    const total = (Array.isArray(ids) ? ids : []).length;
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
    return `
      <button class="${utility ? "utility-card" : "status-card"} ${tone}" data-route="${escapeHtml(route)}" type="button">
        <ha-icon icon="${escapeHtml(icon)}"></ha-icon>
        <span class="${utility ? "utility-copy" : "status-copy"}">
          <small>${escapeHtml(title)}</small>
          <strong>${escapeHtml(value)}</strong>
          ${extra ? `<em>${escapeHtml(extra)}</em>` : ""}
        </span>
      </button>`;
  }

  _render() {
    if (!this._config || !this.shadowRoot) return;
    if (!this._hass) {
      this.shadowRoot.innerHTML = `<ha-card><div style="padding:24px">Дом сейчас · загрузка…</div></ha-card>`;
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
    const climateActive = climateIds.filter((id) => {
      const entity = this._entity(id);
      return entity && ["heating", "cooling"].includes(entity.attributes?.hvac_action);
    }).length;
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

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; --green:#35c759; --yellow:#ffd60a; --orange:#ff9f0a; --red:#ff453a; --blue:#3aa8ff; --grey:#9aa6af; }
        ha-card { overflow:hidden; border-radius:28px; background:#071622; border:1px solid rgba(255,255,255,.08); box-shadow:0 18px 44px rgba(0,0,0,.22); }
        .hero { position:relative; min-height:calc(100vh - 166px); min-height:calc(100svh - 166px); max-height:850px; height:760px; overflow:hidden; background:linear-gradient(180deg,rgba(3,14,26,.12),rgba(3,14,26,.2) 30%,rgba(3,14,26,.74) 100%),url("${escapeHtml(asset)}") center/cover no-repeat; color:#fff; font-family:var(--paper-font-body1_-_font-family,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif); }
        .hero::after { content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(90deg,rgba(3,13,24,.28),transparent 28%,transparent 72%,rgba(3,13,24,.24)); }
        button { font:inherit; color:inherit; }
        .top-grid { position:absolute; z-index:4; left:12px; right:12px; top:12px; display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:8px; }
        .status-card,.float-card,.utility-card,.callout,.camera-pill { border:1px solid rgba(255,255,255,.18); background:rgba(7,24,38,.78); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); box-shadow:0 10px 28px rgba(0,0,0,.18); }
        .status-card { min-width:0; height:74px; padding:9px 8px; border-radius:16px; display:flex; gap:7px; align-items:center; cursor:pointer; text-align:left; appearance:none; }
        .status-card ha-icon { width:24px; flex:0 0 24px; } .status-copy { min-width:0; display:flex; flex-direction:column; line-height:1.1; }
        .status-copy small { font-size:11px; font-weight:700; opacity:.92; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .status-copy strong { margin-top:5px; font-size:15px; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .status-copy em { margin-top:4px; font-size:10px; font-style:normal; opacity:.68; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .green ha-icon,.green strong { color:var(--green); } .yellow ha-icon,.yellow strong { color:var(--yellow); } .orange ha-icon,.orange strong { color:var(--orange); } .red ha-icon,.red strong { color:var(--red); } .blue ha-icon,.blue strong { color:var(--blue); } .grey ha-icon,.grey strong { color:var(--grey); }
        .float-card { position:absolute; z-index:4; top:102px; border-radius:18px; padding:12px 14px; cursor:pointer; } .weather { left:14px; min-width:116px; } .clock { right:14px; text-align:right; min-width:126px; }
        .float-main { display:flex; align-items:center; gap:9px; font-size:25px; font-weight:800; } .float-main ha-icon { color:var(--blue); } .float-sub { display:block; margin-top:5px; font-size:12px; opacity:.82; }
        .camera-pill { position:absolute; z-index:4; right:14px; top:190px; padding:8px 11px; border-radius:999px; display:flex; gap:7px; align-items:center; cursor:pointer; font-size:12px; font-weight:700; }
        .zone { position:absolute; z-index:2; border:3px solid var(--green); border-radius:8px; box-shadow:0 0 20px rgba(53,199,89,.45); pointer-events:none; } .zone.yellow { border-color:var(--yellow); box-shadow:0 0 22px rgba(255,214,10,.58); } .zone.orange { border-color:var(--orange); box-shadow:0 0 22px rgba(255,159,10,.58); } .zone.grey { border-color:rgba(178,188,196,.72); box-shadow:none; }
        .window-zone { left:22.5%; top:40.5%; width:17%; height:16%; } .gate-zone { left:17.8%; top:59%; width:25%; height:18%; } .door-zone { right:20.6%; top:60%; width:8.5%; height:17%; }
        .callout { position:absolute; z-index:4; border-radius:15px; padding:9px 11px; cursor:pointer; min-width:108px; } .callout b { display:block; font-size:13px; } .callout span { display:block; margin-top:3px; font-size:11px; font-weight:700; }
        .window-callout { left:9%; top:32%; } .gate-callout { left:4%; top:55%; } .door-callout { right:5%; top:50%; }
        .utilities { position:absolute; z-index:4; left:12px; right:12px; bottom:14px; display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:9px; }
        .utility-card { border-radius:17px; padding:12px 11px; min-height:88px; cursor:pointer; appearance:none; text-align:left; display:grid; grid-template-columns:28px 1fr; column-gap:8px; align-items:start; } .utility-card ha-icon { margin-top:2px; }
        .utility-copy { min-width:0; display:flex; flex-direction:column; } .utility-copy small { font-size:11px; font-weight:700; opacity:.9; } .utility-copy strong { margin-top:5px; font-size:15px; font-weight:800; } .utility-copy em { margin-top:5px; font-size:11px; font-style:normal; opacity:.76; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        [data-route]:focus-visible { outline:2px solid var(--blue); outline-offset:2px; }
        @media (max-width:600px) {
          ha-card { border-radius:22px; }
          .hero { height:clamp(620px,calc(100svh - 184px),680px); min-height:0; max-height:none; background-size:125% auto; background-position:center 48%; background-color:#071622; }
          .top-grid { gap:5px; left:8px; right:8px; top:8px; }
          .status-card { height:64px; padding:5px 3px; gap:2px; border-radius:13px; flex-direction:column; justify-content:center; text-align:center; }
          .status-card ha-icon { width:19px; flex:0 0 19px; }
          .status-copy { width:100%; align-items:center; }
          .status-copy small { font-size:8px; }
          .status-copy strong { margin-top:2px; font-size:12px; }
          .status-copy em { display:none; }
          .float-card { top:80px; padding:9px 10px; } .float-main { font-size:21px; } .float-sub { font-size:10px; } .camera-pill { top:150px; font-size:10px; }
          .window-callout { left:5%; top:34%; } .gate-callout { left:3%; top:51%; } .door-callout { right:3%; top:49%; } .callout { min-width:92px; padding:7px 8px; } .callout b { font-size:11px; } .callout span { font-size:10px; }
          .utilities { grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px; left:8px; right:8px; bottom:8px; }
          .utility-card { min-height:64px; padding:8px; grid-template-columns:24px 1fr; } .utility-copy small { font-size:10px; } .utility-copy strong { font-size:13px; } .utility-copy em { font-size:10px; }
          .window-zone { left:16%; top:45.5%; width:18%; height:8.2%; } .gate-zone { left:10%; top:54%; width:29%; height:12%; } .door-zone { right:13.5%; top:55.5%; width:11.5%; height:10.8%; }
        }
      </style>
      <ha-card>
        <div class="hero" aria-label="${escapeHtml(this._config.title || "Дом сейчас")}">
          <div class="top-grid">
            ${this._card(security.icon,"Безопасность",security.label,security.tone,routes.safety)}
            ${this._card("mdi:door-open","Открыто",String(openings),openingsTone,routes.open)}
            ${this._card("mdi:motion-sensor","Движение",String(motion),motionTone,routes.activity)}
            ${this._card("mdi:lightbulb-group","Свет",String(lights),lightsTone,routes.lights)}
            ${this._card("mdi:thermostat","Климат",String(climateActive),climateTone,routes.climate)}
          </div>
          <button class="float-card weather ${weather.tone}" data-route="${escapeHtml(routes.weather)}" type="button"><span class="float-main"><ha-icon icon="${escapeHtml(weather.icon)}"></ha-icon>${escapeHtml(weather.label)}</span><span class="float-sub">${escapeHtml(weather.detail)}</span></button>
          <div class="float-card clock"><span class="float-main">${escapeHtml(time)}</span><span class="float-sub">${escapeHtml(date)}</span></div>
          <button class="camera-pill ${cameras.tone}" data-route="${escapeHtml(routes.cameras)}" type="button"><ha-icon icon="${escapeHtml(cameras.icon)}"></ha-icon>${escapeHtml(cameras.label)}</button>
          <div class="zone window-zone ${windowTone}"></div><div class="zone gate-zone ${gate.tone}"></div><div class="zone door-zone ${entrance.tone}"></div>
          <button class="callout window-callout ${windowTone}" data-route="${escapeHtml(routes.open)}" type="button"><b>Окна</b><span>${escapeHtml(windows)} открыто</span></button>
          <button class="callout gate-callout ${gate.tone}" data-route="${escapeHtml(routes.open)}" type="button"><b>${escapeHtml(gate.label)}</b><span>${escapeHtml(gate.detail)}</span></button>
          <button class="callout door-callout ${entrance.tone}" data-route="${escapeHtml(routes.open)}" type="button"><b>${escapeHtml(entrance.label)}</b><span>${escapeHtml(entrance.detail)}</span></button>
          <div class="utilities">
            ${this._card(power.icon,"Электросеть",power.label,power.tone,routes.electricity,power.detail,true)}
            ${this._card(water.icon,"Вода",water.label,water.tone,routes.water,water.detail,true)}
            ${this._card(internet.icon,"Интернет",internet.label,internet.tone,routes.network,internet.detail,true)}
            ${this._card(heating.icon,"Отопление",heating.label,heating.tone,routes.heating,heating.detail,true)}
          </div>
        </div>
      </ha-card>`;
    this._bindRoutes();
  }
}

if (!customElements.get(ELEMENT_NAME)) customElements.define(ELEMENT_NAME, NikasHouseHero);
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === ELEMENT_NAME)) {
  window.customCards.push({ type: ELEMENT_NAME, name: "NikaS House Visual State Scene", description: "Full-screen visual state scene for the NikaS Home dashboard.", preview: false });
}
