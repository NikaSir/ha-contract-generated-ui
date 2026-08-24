// ZONT UI v0.8.0 application shell and live heating overview.
// Canonical source: NikaSir/ha-zont. Loaded by Contract Generated UI.
import "/contract_generated_ui/frontend/nikas-generated-zont.js";

const ELEMENT_NAME = "nikas-generated-zont";

const esc080 = (value) => String(value ?? "—")
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;").replaceAll("'", "&#039;");

function installV080() {
  const ElementClass = customElements.get(ELEMENT_NAME);
  if (!ElementClass || ElementClass.prototype.__zontV080) return false;

  const originalRender = ElementClass.prototype._render;
  if (typeof originalRender !== "function") return false;

  ElementClass.prototype._systemOverviewV080 = function systemOverviewV080(items) {
    const main = this._boilerSet(items, false);
    const radiators = this._findState(items, ["радиатор"], ["температур", "t°", ">>>", "<<<", "датчик"]);
    const floor = this._findState(items, ["тёпл", "тепл", "floor"], ["температур", "t°", ">>>", "<<<", "датчик"]);
    const circulation = this._findState(items, ["циркуляц"], ["температур", "t°", "гвс"]);
    const reserve = this._findState(items, ["резерв", "reserve"], ["температур", "t°", "котел", "котёл", "ошиб"]);
    const dhw = this._find(items, ["гвс", "dhw", "горяч"], ["циркуляц", "режим", "кнопк", "button"]);
    const outdoor = this._find(items, ["улиц", "outdoor", "вне дома", "weather"], ["влаж", "humidity"]);
    const indoor = this._find(items, ["гостиная", "комнат", "в доме", "indoor"], ["влаж", "humidity", "целев", "target"]);
    const online = this._find(items, ["online", "подключ", "controller online"]);
    const errors = items.filter((item) => this._role(item) === "error" && !this._isInactive(item));
    const problems = items.filter((item) => this._isProblem(item) && !["rssi", "battery"].includes(this._role(item)));
    const attention = errors.length > 0 || problems.length > 0;
    const title = attention ? "Требует внимания" : "Система работает";
    const subtitle = attention ? "Есть ошибка или недоступный источник" : "Отопление и ГВС в норме";
    const onlineText = online ? (this._isProblem(online) ? "Нет данных" : this._stateText(online)) : "Данные доступны";
    const mode = this._currentMode(items);

    const node = (label, item, icon, state = null) => `<div class="v080-node">
      <ha-icon icon="${icon}"></ha-icon><span>${esc080(label)}</span>
      <strong>${esc080(item ? this._value(item) : "—")}</strong>
      ${state ? `<small>${esc080(state)}</small>` : ""}
    </div>`;
    const metric = (label, item, icon, fallback = "—") => `<div class="v080-metric">
      <ha-icon icon="${icon}"></ha-icon><div><span>${esc080(label)}</span><strong>${esc080(item ? this._value(item) : fallback)}</strong></div>
    </div>`;
    const status = (label, item, icon) => `<div class="v080-status ${item && this._isActive(item) ? "on" : ""} ${item && this._isProblem(item) ? "problem" : ""}">
      <ha-icon icon="${icon}"></ha-icon><strong>${esc080(label)}</strong><span>${esc080(this._stateText(item))}</span>
    </div>`;

    const modes = this._modeButtons(items);
    const modeButtons = modes.length ? modes.map((item) => `<button class="v080-mode ${this._modeActive(item, mode) ? "selected" : ""}" data-mode-entity="${esc080(item.entry.entity_id)}" data-mode-label="${esc080(this._modeLabel(item))}" ${this._busyMode === item.entry.entity_id ? "disabled" : ""}>
      <ha-icon icon="mdi:radiator"></ha-icon><span>${esc080(this._modeLabel(item))}</span>
    </button>`).join("") : `<div class="empty">Кнопки режимов ZONT в Home Assistant не найдены.</div>`;

    return `<div class="v080-overview ${attention ? "attention" : ""}">
      <div class="v080-head"><div><span class="eyebrow">СОСТОЯНИЕ СИСТЕМЫ</span><h1>${title}</h1><p>${subtitle}</p></div><div class="v080-online"><i></i>${esc080(onlineText)}</div></div>
      <div class="v080-scheme">
        <div class="v080-pipes" aria-hidden="true"><i class="hot a"></i><i class="hot b"></i><i class="hot c"></i><i class="cold a"></i><i class="cold b"></i><i class="cold c"></i></div>
        ${node("Котёл", main.current || main.supply, "mdi:water-boiler", this._value(main.state, ""))}
        <div class="v080-circuits"><span>КОНТУРЫ</span>${node("Радиаторы", main.supply, "mdi:radiator", this._stateText(radiators))}${node("Тёплый пол", main.ret, "mdi:heating-coil", this._stateText(floor))}</div>
        ${node("ГВС", dhw, "mdi:water-boiler", dhw ? "" : "Нет данных")}
        <div class="v080-pump"><ha-icon icon="mdi:pump"></ha-icon><strong>Циркуляция</strong><span>${esc080(this._stateText(circulation))}</span></div>
      </div>
      <div class="v080-metrics">${metric("Режим", null, "mdi:home-thermometer-outline", mode)}${metric("Температура в доме", indoor, "mdi:thermometer")}${metric("Улица", outdoor, "mdi:weather-partly-cloudy")}${metric("Давление", main.pressure, "mdi:gauge")}</div>
    </div>
    <section><h2>Основные узлы</h2><div class="v080-statuses">${status("Радиаторы", radiators, "mdi:radiator")}${status("Тёплый пол", floor, "mdi:heating-coil")}${status("Циркуляция", circulation, "mdi:pump")}${status("Резерв", reserve, "mdi:water-boiler-off")}</div></section>
    <section><h2>Текущий режим</h2><div class="v080-modes">${modeButtons}</div></section>`;
  };

  ElementClass.prototype._states = function statesV080(items) {
    return this._systemOverviewV080(items);
  };

  ElementClass.prototype._render = function patchedRender(...args) {
    const result = originalRender.apply(this, args);
    const root = this.shadowRoot;
    if (!root) return result;

    if (!root.getElementById("zont-v080-style")) {
      const style = document.createElement("style");
      style.id = "zont-v080-style";
      style.textContent = `
        .header{grid-template-columns:64px 1fr 64px!important;min-height:92px!important;padding:max(10px,env(safe-area-inset-top,0px)) 20px 10px!important;border-bottom:1px solid var(--divider-color,#e3e3e3)!important;box-shadow:none!important}.rail{width:52px!important;height:52px!important;border-radius:16px!important;background:var(--card-background-color,#fff)!important;box-shadow:0 6px 20px rgba(0,0,0,.06)!important}.rail ha-icon{--mdc-icon-size:31px!important}#back{justify-self:start}#refresh{justify-self:end;color:var(--primary-color,#009fc2)!important}.heading{align-self:center;line-height:1.15}.heading strong{font-size:24px!important;font-weight:750!important;letter-spacing:-.25px}.heading span{margin-top:5px!important;font-size:14px!important;color:var(--secondary-text-color,#666)!important}
        .v080-overview{background:linear-gradient(135deg,var(--card-background-color,#fff) 58%,color-mix(in srgb,var(--primary-color,#00a6c7) 8%,#fff));border:1px solid var(--divider-color,#ddd);border-radius:24px;padding:18px;margin-bottom:24px;overflow:hidden}.v080-overview.attention{border-color:var(--warning-color,#ff9800)}.v080-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.eyebrow{font-size:11px;font-weight:750;letter-spacing:.14em;color:var(--secondary-text-color,#666)}.v080-head h1{margin:7px 0 3px;font-size:29px;line-height:1.05}.v080-head p{margin:0;color:var(--secondary-text-color,#666);font-size:14px}.v080-online{display:flex;align-items:center;gap:7px;flex:none;padding:9px 12px;border-radius:999px;background:color-mix(in srgb,var(--success-color,#43a047) 10%,var(--card-background-color,#fff));font-size:12px;font-weight:700;color:var(--success-color,#43a047)}.v080-online i{width:8px;height:8px;border-radius:50%;background:currentColor}
        .v080-scheme{position:relative;margin-top:18px;min-height:250px;padding:18px 12px;display:grid;grid-template-columns:1fr 1.25fr 1fr;gap:12px;align-items:center;border-radius:20px;background:color-mix(in srgb,var(--secondary-background-color,#f2f2f2) 78%,transparent);overflow:hidden}.v080-node,.v080-circuits,.v080-pump{position:relative;z-index:2}.v080-node{min-height:132px;padding:14px 8px;border:1px solid var(--divider-color,#ddd);border-radius:18px;background:color-mix(in srgb,var(--card-background-color,#fff) 92%,transparent);display:flex;flex-direction:column;align-items:center;text-align:center}.v080-node>ha-icon{--mdc-icon-size:40px;color:var(--primary-color,#009fc2);margin:5px 0 8px}.v080-node>span,.v080-circuits>span{font-size:11px;color:var(--secondary-text-color,#777)}.v080-node>strong{font-size:18px;margin-top:5px}.v080-node>small{font-size:10px;margin-top:5px;color:var(--secondary-text-color,#777)}.v080-circuits{display:grid;gap:7px}.v080-circuits>.v080-node{min-height:86px;display:grid;grid-template-columns:34px 1fr;grid-template-rows:auto auto;align-items:center;text-align:left;padding:9px}.v080-circuits>.v080-node ha-icon{grid-row:1/3;margin:0;--mdc-icon-size:29px}.v080-circuits>.v080-node span{font-size:11px}.v080-circuits>.v080-node strong{font-size:15px;margin:0}.v080-circuits>.v080-node small{grid-column:2;font-size:9px;margin:0}.v080-pump{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);display:grid;grid-template-columns:27px auto;gap:0 6px;align-items:center;padding:7px 11px;border-radius:14px;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd)}.v080-pump ha-icon{grid-row:1/3;color:var(--success-color,#43a047)}.v080-pump strong{font-size:11px}.v080-pump span{font-size:9px;color:var(--secondary-text-color,#777)}.v080-pipes i{position:absolute;z-index:1;border-radius:8px}.v080-pipes .hot{height:6px;background:#e4564f}.v080-pipes .cold{height:6px;background:#3d9bc9}.v080-pipes .hot.a{left:19%;right:52%;top:42%}.v080-pipes .hot.b{left:47%;right:18%;top:42%}.v080-pipes .hot.c{width:6px;height:34%;left:19%;top:42%}.v080-pipes .cold.a{left:19%;right:52%;bottom:22%}.v080-pipes .cold.b{left:47%;right:18%;bottom:22%}.v080-pipes .cold.c{width:6px;height:22%;right:18%;bottom:22%}
        .v080-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:14px}.v080-metric{min-height:75px;border:1px solid var(--divider-color,#ddd);border-radius:16px;padding:10px;display:flex;gap:8px;align-items:center;background:color-mix(in srgb,var(--card-background-color,#fff) 88%,transparent)}.v080-metric ha-icon{color:var(--secondary-text-color,#666)}.v080-metric span,.v080-metric strong{display:block}.v080-metric span{font-size:9.5px;color:var(--secondary-text-color,#777)}.v080-metric strong{font-size:14px;margin-top:3px}.v080-statuses{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.v080-status{min-height:105px;padding:12px 6px;border:1px solid var(--divider-color,#ddd);border-radius:17px;background:var(--card-background-color,#fff);display:flex;flex-direction:column;align-items:center;text-align:center}.v080-status ha-icon{--mdc-icon-size:31px;color:var(--secondary-text-color,#777);margin-bottom:8px}.v080-status strong{font-size:11px}.v080-status span{font-size:10px;margin-top:6px;color:var(--secondary-text-color,#777)}.v080-status.on ha-icon,.v080-status.on span{color:var(--success-color,#43a047)}.v080-status.problem{border-color:var(--warning-color,#ff9800)}.v080-modes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.v080-mode{min-height:68px;border:1.5px solid var(--divider-color,#ddd);border-radius:16px;background:var(--card-background-color,#fff);color:inherit;display:flex;align-items:center;gap:9px;padding:10px 12px;text-align:left}.v080-mode ha-icon{color:var(--primary-color,#009fc2)}.v080-mode span{font-size:12px;font-weight:650}.v080-mode.selected{border-color:var(--primary-color,#009fc2);background:color-mix(in srgb,var(--primary-color,#009fc2) 9%,var(--card-background-color,#fff))}.v080-mode:disabled{opacity:.55}
        @media(max-width:420px){main{padding-top:12px!important}.header{grid-template-columns:58px 1fr 58px!important;min-height:86px!important;padding-left:12px!important;padding-right:12px!important}.rail{width:48px!important;height:48px!important}.heading strong{font-size:22px!important}.heading span{font-size:12.5px!important}.v080-overview{padding:14px;border-radius:21px}.v080-head h1{font-size:25px}.v080-online{padding:7px 9px;font-size:10px}.v080-scheme{min-height:235px;padding-left:7px;padding-right:7px;gap:7px}.v080-node{padding-left:5px;padding-right:5px}.v080-node>strong{font-size:16px}.v080-metrics,.v080-statuses{grid-template-columns:repeat(2,minmax(0,1fr))}}
      `;
      root.appendChild(style);
    }

    const menu = root.getElementById("back");
    if (menu) {
      const icon = menu.querySelector("ha-icon");
      if (icon) icon.setAttribute("icon", "mdi:menu");
      menu.querySelector(".back-label")?.remove();
      menu.setAttribute("aria-label", "Меню Home Assistant");
      menu.onclick = () => this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }));
    }

    const heading = root.querySelector(".heading span");
    if (heading) {
      const base = String(heading.textContent || "Отопление и ГВС").replace(/\s*·\s*UI\s*v?[0-9.]+\s*$/i, "");
      heading.textContent = `${base} · UI v0.8.0`;
    }
    return result;
  };

  ElementClass.prototype.__zontV080 = true;
  return true;
}

if (!installV080()) customElements.whenDefined(ELEMENT_NAME).then(() => installV080());
