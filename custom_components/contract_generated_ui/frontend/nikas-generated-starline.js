// Semantic read-only StarLine panel for Contract Generated UI.
// Native StarLine inspired information hierarchy without vehicle control commands.
(() => {
  const ELEMENT_NAME = "nikas-generated-starline";
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

  function haversineKm(a, b) {
    const toRad = (value) => value * Math.PI / 180;
    const r = 6371;
    const dLat = toRad(b.lat - a.lat);
    const dLon = toRad(b.lon - a.lon);
    const lat1 = toRad(a.lat);
    const lat2 = toRad(b.lat);
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
    return 2 * r * Math.asin(Math.sqrt(x));
  }

  class NikasGeneratedStarline extends HTMLElement {
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
      this._selectedDeviceId = null;
      this._historyCache = new Map();
      this._historyLoading = new Set();
      this._onHash = () => { this._active = this._tabFromLocation(); this._queue(); };
    }

    set hass(value) { this._hass = value; this._load(); this._queue(); }
    get hass() { return this._hass; }
    set panel(value) {
      this._panel = value;
      this._active = this._tabFromLocation();
      this._selectedDeviceId = null;
      this._load(true);
      this._queue();
    }
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
    _selectDevice(id) {
      if (!id || id === this._selectedDeviceId) return;
      this._selectedDeviceId = id;
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
      return this._registry
        .filter((entry) => entry.platform === "starline" && !entry.disabled_by)
        .filter((entry) => this._hass?.states?.[entry.entity_id])
        .map((entry) => ({ entry, state: this._hass.states[entry.entity_id] }));
    }

    _groups(items) {
      const groups = new Map();
      for (const item of items) {
        const id = item.entry.device_id || "__unassigned__";
        if (!groups.has(id)) groups.set(id, []);
        groups.get(id).push(item);
      }
      return [...groups.entries()].map(([id, entries]) => {
        const device = this._devices.get(id);
        return { id, label: device?.name_by_user || device?.name || device?.model || "Автомобиль", entries };
      }).sort((a, b) => a.label.localeCompare(b.label, "ru"));
    }

    _selectedGroup(groups) {
      if (!groups.length) return null;
      if (!groups.some((group) => group.id === this._selectedDeviceId)) this._selectedDeviceId = groups[0].id;
      return groups.find((group) => group.id === this._selectedDeviceId) || groups[0];
    }

    _rawName(item) {
      return item?.state?.attributes?.friendly_name || item?.entry?.name || item?.entry?.original_name || item?.entry?.entity_id || "";
    }
    _text(item) {
      return low(item?.entry?.entity_id, this._rawName(item), item?.entry?.original_name, item?.entry?.name, item?.state?.attributes?.device_class, item?.state?.attributes?.icon);
    }
    _semanticName(item, vehicleLabel = "") {
      let name = String(this._rawName(item)).trim();
      if (vehicleLabel && name.startsWith(vehicleLabel)) name = name.slice(vehicleLabel.length);
      return name.replace(/^StarLine[ _·:—–-]*/i, "").replace(/^Старлайн[ _·:—–-]*/i, "").replace(/[_]+/g, " ").replace(/\s{2,}/g, " ").replace(/^[ _·:—–-]+/, "").trim() || "Параметр";
    }
    _formatted(item) {
      if (!item) return "—";
      if (typeof this._hass?.formatEntityState === "function") {
        try { return this._hass.formatEntityState(item.state); } catch (_error) { /* raw fallback */ }
      }
      const unit = item.state?.attributes?.unit_of_measurement;
      return `${item.state?.state ?? "—"}${unit ? ` ${unit}` : ""}`;
    }
    _isProblem(item) { return item && ["unknown", "unavailable"].includes(item.state?.state); }

    _role(item) {
      const t = this._text(item);
      const domain = domainOf(item?.entry?.entity_id);
      if (domain === "device_tracker") return "tracker";
      if (has(t, ["obd", "ошиб", "error", "fault"])) return "obd";
      if (has(t, ["gsm"])) return "gsm";
      if (has(t, ["gps", "спутник", "satellite"])) return "gps";
      if (has(t, ["пробег", "mileage", "odometer"])) return "mileage";
      if (has(t, ["моточас", "engine hour", "engine_hours", "hours"])) return "engine_hours";
      if (has(t, ["топлив", "fuel"])) return "fuel";
      if (has(t, ["акб", "battery", "напряж", "voltage"])) return "battery";
      if (has(t, ["температур", "temperature", "temp"])) {
        if (has(t, ["двиг", "engine", "motor"])) return "engine_temp";
        if (has(t, ["салон", "cabin", "interior"])) return "cabin_temp";
      }
      if (has(t, ["капот", "hood"])) return "hood";
      if (has(t, ["багаж", "trunk"])) return "trunk";
      if (has(t, ["двер", "door"])) return "door";
      if (has(t, ["ручн", "parking brake", "handbrake", "hand_brake"])) return "handbrake";
      if (has(t, ["зажиган", "ignition"])) return "ignition";
      if (has(t, ["двиг", "engine"]) && !has(t, ["temperature", "температур", "hours", "моточас"])) return "engine";
      if (has(t, ["охран", "alarm", "security", "armed"])) return "security";
      if (domain === "lock" || has(t, ["замок", "lock", "центральн"])) return "lock";
      if (has(t, ["hands free", "hands_free", "свободн рук"])) return "hands_free";
      if (has(t, ["запрет движ", "movement", "immobil", "block movement"])) return "movement";
      if (has(t, ["webasto", "отопител", "heater"])) return "heater";
      if (has(t, ["скорост", "speed"])) return "speed";
      return "other";
    }

    _find(items, role) { return items.find((item) => this._role(item) === role); }
    _filter(items, role) { return items.filter((item) => this._role(item) === role); }

    _shortLabel(item, vehicleLabel = "") {
      const role = this._role(item);
      const labels = {
        tracker: "Местоположение", obd: "Ошибки OBD", gsm: "GSM", gps: "GPS",
        mileage: "Пробег", engine_hours: "Моточасы", fuel: "Топливо", battery: "АКБ",
        engine_temp: "Двигатель", cabin_temp: "Салон", hood: "Капот", trunk: "Багажник",
        handbrake: "Ручной тормоз", ignition: "Зажигание", engine: "Двигатель",
        security: "Охрана", lock: "Замки", hands_free: "Hands Free",
        movement: "Запрет движения", heater: "Отопитель", speed: "Скорость",
      };
      if (role === "door") {
        const name = this._semanticName(item, vehicleLabel).toLocaleLowerCase();
        if (name.includes("водител")) return "Дверь водителя";
        if (name.includes("пассажир")) return "Дверь пассажира";
        if (name.includes("задн")) return "Задняя дверь";
        return "Двери";
      }
      return labels[role] || this._semanticName(item, vehicleLabel).slice(0, 32);
    }

    _icon(item) {
      return ({
        tracker: "mdi:map-marker", obd: "mdi:alert-octagon-outline", gsm: "mdi:signal-cellular-3",
        gps: "mdi:crosshairs-gps", mileage: "mdi:counter", engine_hours: "mdi:engine-outline",
        fuel: "mdi:gas-station", battery: "mdi:car-battery", engine_temp: "mdi:thermometer",
        cabin_temp: "mdi:car-seat", hood: "mdi:car-lifted-pickup", trunk: "mdi:car-back",
        door: "mdi:car-door", handbrake: "mdi:car-brake-parking", ignition: "mdi:key-variant",
        engine: "mdi:engine", security: "mdi:shield-check-outline", lock: "mdi:lock-outline",
        hands_free: "mdi:hand-wave-outline", movement: "mdi:car-off", heater: "mdi:radiator",
        speed: "mdi:speedometer",
      }[this._role(item)] || item?.state?.attributes?.icon || item?.entry?.icon || "mdi:information-outline");
    }

    _stateText(item) {
      if (!item) return "—";
      const role = this._role(item);
      const raw = String(item.state?.state ?? "").toLocaleLowerCase();
      const on = ["on", "open", "true", "1", "armed", "locked", "home"].includes(raw);
      if (role === "security") return on ? "Под охраной" : "Охрана снята";
      if (role === "lock") return ["locked", "on"].includes(raw) ? "Заблокировано" : ["unlocked", "off"].includes(raw) ? "Разблокировано" : this._formatted(item);
      if (["door", "hood", "trunk"].includes(role)) return on ? "Открыто" : "Закрыто";
      if (role === "handbrake") return on ? "Поднят" : "Опущен";
      if (role === "ignition") return on ? "Включено" : "Выключено";
      if (role === "engine") return on ? "Запущен" : "Остановлен";
      if (["hands_free", "movement", "heater"].includes(role)) return on ? "Включено" : "Выключено";
      return this._formatted(item);
    }

    _isOnline(items) {
      return items.filter((item) => !["unknown", "unavailable"].includes(item.state?.state)).length >= Math.max(1, Math.floor(items.length / 2));
    }

    _vehicleSelector(groups) {
      if (groups.length < 2) return "";
      return `<div class="vehicle-switcher">${groups.map((group) => `<button type="button" data-device="${esc(group.id)}" class="${group.id === this._selectedDeviceId ? "active" : ""}"><ha-icon icon="mdi:car-side"></ha-icon><span>${esc(group.label)}</span></button>`).join("")}</div>`;
    }

    _telemetryChip(item, label, icon = null) {
      if (!item) return "";
      return `<div class="telemetry-chip ${this._isProblem(item) ? "problem" : ""}"><ha-icon icon="${esc(icon || this._icon(item))}"></ha-icon><span>${esc(label)}</span><strong>${esc(this._formatted(item))}</strong></div>`;
    }

    _statusCard(item, label) {
      if (!item) return "";
      return `<div class="status-card ${this._isProblem(item) ? "problem" : ""}"><ha-icon icon="${esc(this._icon(item))}"></ha-icon><div><strong>${esc(label)}</strong><span>${esc(this._stateText(item))}</span></div></div>`;
    }

    _eventText(item, state, vehicleLabel = "") {
      const role = this._role(item);
      const label = this._shortLabel(item, vehicleLabel);
      const raw = String(state ?? "").toLocaleLowerCase();
      const on = ["on", "open", "true", "1", "armed", "locked", "home"].includes(raw);
      if (role === "door") return `${label} ${on ? "открыта" : "закрыта"}`;
      if (role === "hood") return `Капот ${on ? "открыт" : "закрыт"}`;
      if (role === "trunk") return `Багажник ${on ? "открыт" : "закрыт"}`;
      if (role === "handbrake") return `Ручник ${on ? "поднят" : "опущен"}`;
      if (role === "ignition") return `Зажигание ${on ? "включено" : "отключено"}`;
      if (role === "engine") return `Двигатель ${on ? "запущен" : "остановлен"}`;
      if (role === "security") return on ? "Охрана включена" : "Охрана снята";
      if (role === "lock") return ["locked", "on"].includes(raw) ? "Замки заблокированы" : "Замки разблокированы";
      return `${label}: ${state}`;
    }

    _lastEvent(items, vehicleLabel = "") {
      const candidates = items.filter((item) => ["door", "hood", "trunk", "handbrake", "ignition", "engine", "security", "lock"].includes(this._role(item)));
      candidates.sort((a, b) => new Date(b.state?.last_changed || 0) - new Date(a.state?.last_changed || 0));
      const item = candidates[0];
      return item ? { at: item.state?.last_changed, text: this._eventText(item, item.state?.state, vehicleLabel) } : null;
    }

    _timeAgo(iso) {
      if (!iso) return "";
      const minutes = Math.floor(Math.max(0, Date.now() - new Date(iso).getTime()) / 60000);
      if (minutes < 1) return "только что";
      if (minutes < 60) return `${minutes} мин назад`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours} ч назад`;
      return `${Math.floor(hours / 24)} дн назад`;
    }

    _overview(items, group) {
      const last = this._lastEvent(items, group.label);
      const telemetry = [
        this._telemetryChip(this._find(items, "gps"), "GPS"),
        this._telemetryChip(this._find(items, "gsm"), "GSM"),
        this._telemetryChip(this._find(items, "battery"), "АКБ"),
        this._telemetryChip(this._find(items, "fuel"), "Топливо"),
        this._telemetryChip(this._find(items, "cabin_temp"), "Салон"),
        this._telemetryChip(this._find(items, "engine_temp"), "Двигатель"),
        this._telemetryChip(this._find(items, "engine_hours"), "Моточасы"),
        this._telemetryChip(this._find(items, "mileage"), "Пробег"),
        this._telemetryChip(this._find(items, "handbrake"), "Паркинг", "mdi:car-brake-parking"),
      ].filter(Boolean).join("");
      const tracker = this._find(items, "tracker");
      return `<section class="hero"><div class="hero-heading"><div><strong>${esc(group.label)}</strong><span>${this._isOnline(items) ? "В сети" : "Связь ограничена"}</span></div><ha-icon icon="mdi:car-connected"></ha-icon></div><div class="telemetry-grid">${telemetry || '<div class="placeholder">Телеметрия не найдена.</div>'}</div><div class="car-visual"><ha-icon icon="mdi:car-side"></ha-icon></div>${last ? `<div class="last-event"><span>${esc(this._timeAgo(last.at))}</span><strong>${esc(last.text)}</strong></div>` : ""}</section>${tracker ? `<section><h2>Местоположение</h2><div id="overview-map" class="map-host"></div></section>` : ""}<section><h2>Связь и диагностика</h2><div class="status-grid">${this._statusCard(this._find(items, "security"), "Охрана")}${this._statusCard(this._find(items, "obd"), "OBD")}</div></section>`;
    }

    _security(items, group) {
      const cards = [];
      for (const role of ["security", "lock", "door", "hood", "trunk", "handbrake", "hands_free", "movement"]) {
        const list = role === "door" ? this._filter(items, role) : [this._find(items, role)].filter(Boolean);
        for (const item of list) cards.push(this._statusCard(item, this._shortLabel(item, group.label)));
      }
      return `<section><h2>Охрана и периметр</h2><div class="status-grid">${cards.join("") || '<div class="placeholder">Охранные состояния не найдены.</div>'}</div></section>`;
    }

    _engine(items, group) {
      const states = ["engine", "ignition", "heater"].map((role) => this._find(items, role)).filter(Boolean);
      const telemetry = ["engine_temp", "cabin_temp", "battery", "fuel", "engine_hours", "mileage", "obd"].map((role) => this._find(items, role)).filter(Boolean);
      return `<section><h2>Состояние</h2><div class="status-grid">${states.map((item) => this._statusCard(item, this._shortLabel(item, group.label))).join("") || '<div class="placeholder">Состояния двигателя не найдены.</div>'}</div></section><section><h2>Телеметрия</h2><div class="detail-grid">${telemetry.map((item) => `<div class="detail-card"><ha-icon icon="${esc(this._icon(item))}"></ha-icon><strong>${esc(this._formatted(item))}</strong><span>${esc(this._shortLabel(item, group.label))}</span></div>`).join("")}</div></section>`;
    }

    _historyTime(row) {
      const value = row?.last_changed || row?.last_updated || row?.lc || row?.lu;
      return typeof value === "number" ? new Date(value * 1000).toISOString() : value || null;
    }
    _historyValue(row) { return row?.state ?? row?.s ?? ""; }
    _historyAttrs(row) { return row?.attributes || row?.a || {}; }

    _loadEvents(group) {
      if (!this._hass?.callWS || !group) return;
      const key = `${group.id}:events`;
      if (this._historyLoading.has(key)) return;
      const cached = this._historyCache.get(key);
      if (cached && Date.now() - cached.loadedAt < 60000) return;
      const entities = group.entries.filter((item) => ["door", "hood", "trunk", "handbrake", "ignition", "engine", "security", "lock"].includes(this._role(item)));
      if (!entities.length) { this._historyCache.set(key, { loadedAt: Date.now(), events: [] }); return; }
      this._historyLoading.add(key);
      this._hass.callWS({ type: "history/history_during_period", start_time: new Date(Date.now() - 86400000).toISOString(), entity_ids: entities.map((item) => item.entry.entity_id), include_start_time_state: true, significant_changes_only: false, minimal_response: false, no_attributes: true })
        .then((history) => {
          const byId = new Map(entities.map((item) => [item.entry.entity_id, item]));
          const events = [];
          for (const [entityId, rows] of Object.entries(history || {})) {
            if (!Array.isArray(rows) || !rows.length) continue;
            const item = byId.get(entityId);
            for (const row of (rows.length > 1 ? rows.slice(1) : [])) {
              const at = this._historyTime(row);
              if (at && item) events.push({ at, text: this._eventText(item, this._historyValue(row), group.label), icon: this._icon(item) });
            }
          }
          events.sort((a, b) => new Date(b.at) - new Date(a.at));
          this._historyCache.set(key, { loadedAt: Date.now(), events: events.slice(0, 120) });
        }).catch((error) => this._historyCache.set(key, { loadedAt: Date.now(), events: [], error: error instanceof Error ? error.message : String(error) }))
        .finally(() => { this._historyLoading.delete(key); this._queue(); });
    }

    _loadRoute(group) {
      if (!this._hass?.callWS || !group) return;
      const tracker = this._find(group.entries, "tracker");
      if (!tracker) return;
      const key = `${group.id}:route`;
      if (this._historyLoading.has(key)) return;
      const cached = this._historyCache.get(key);
      if (cached && Date.now() - cached.loadedAt < 60000) return;
      this._historyLoading.add(key);
      this._hass.callWS({ type: "history/history_during_period", start_time: new Date(Date.now() - 86400000).toISOString(), entity_ids: [tracker.entry.entity_id], include_start_time_state: true, significant_changes_only: false, minimal_response: false, no_attributes: false })
        .then((history) => {
          const rows = history?.[tracker.entry.entity_id] || [];
          const coords = rows.map((row) => this._historyAttrs(row)).filter((attrs) => attrs?.latitude != null && attrs?.longitude != null).map((attrs) => ({ lat: Number(attrs.latitude), lon: Number(attrs.longitude) })).filter((point) => Number.isFinite(point.lat) && Number.isFinite(point.lon));
          let distance = 0;
          for (let i = 1; i < coords.length; i += 1) distance += haversineKm(coords[i - 1], coords[i]);
          this._historyCache.set(key, { loadedAt: Date.now(), route: { points: coords.length, distance } });
        }).catch(() => this._historyCache.set(key, { loadedAt: Date.now(), route: { points: 0, distance: 0 } }))
        .finally(() => { this._historyLoading.delete(key); this._queue(); });
    }

    _location(items, group) {
      const tracker = this._find(items, "tracker");
      if (!tracker) return '<div class="placeholder">Сущность местоположения автомобиля не найдена.</div>';
      const attrs = tracker.state?.attributes || {};
      const coords = attrs.latitude != null && attrs.longitude != null ? `${Number(attrs.latitude).toFixed(5)}, ${Number(attrs.longitude).toFixed(5)}` : "Координаты недоступны";
      const cache = this._historyCache.get(`${group.id}:route`);
      return `<section><h2>Сейчас</h2><div class="location-summary"><ha-icon icon="mdi:map-marker-radius"></ha-icon><div><strong>${esc(tracker.state?.state || "Местоположение")}</strong><span>${esc(coords)}</span></div></div></section><section><h2>Карта и маршрут</h2><div id="location-map" class="map-host tall"></div></section>${cache?.route ? `<section><h2>Последние 24 часа</h2><div class="route-summary"><div><strong>${esc(cache.route.distance.toFixed(1))}</strong><span>км по истории HA</span></div><div><strong>${esc(cache.route.points)}</strong><span>точек маршрута</span></div></div></section>` : ""}`;
    }

    _history(group) {
      const cache = this._historyCache.get(`${group.id}:events`);
      if (!cache) return '<div class="placeholder">Загрузка истории за 24 часа…</div>';
      if (cache.error) return `<div class="placeholder problem">История недоступна: ${esc(cache.error)}</div>`;
      if (!cache.events.length) return '<div class="placeholder">За последние 24 часа событий не найдено.</div>';
      return `<section><h2>История · 24 часа</h2><div class="timeline">${cache.events.map((event) => `<div class="timeline-row"><time>${esc(new Date(event.at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit", second: "2-digit" }))}</time><ha-icon icon="${esc(event.icon)}"></ha-icon><span>${esc(event.text)}</span></div>`).join("")}</div></section>`;
    }

    _ensureHistory(group) {
      if (!group) return;
      if (this._active === "history") this._loadEvents(group);
      if (this._active === "location") this._loadRoute(group);
    }

    _mountMap(id, tracker, hours = 0) {
      const host = this.shadowRoot?.getElementById(id);
      if (!host || !tracker) return;
      try {
        const card = document.createElement("hui-map-card");
        if (typeof card.setConfig !== "function") { host.innerHTML = '<div class="placeholder">Карта Home Assistant загружается…</div>'; return; }
        card.setConfig({ type: "map", entities: [tracker.entry.entity_id], hours_to_show: hours, auto_fit: true });
        card.hass = this._hass;
        host.replaceChildren(card);
      } catch (_error) { host.innerHTML = '<div class="placeholder">Не удалось встроить карту Home Assistant.</div>'; }
    }

    _content(group) {
      if (!group) return '<div class="placeholder">Автомобили StarLine не найдены.</div>';
      if (this._active === "security") return this._security(group.entries, group);
      if (this._active === "engine") return this._engine(group.entries, group);
      if (this._active === "location") return this._location(group.entries, group);
      if (this._active === "history") return this._history(group);
      return this._overview(group.entries, group);
    }

    _render() {
      const config = this._config();
      const tabs = this._tabs();
      if (!tabs.length) return;
      if (!this._active) this._active = tabs[0].id;
      const groups = this._groups(this._entries());
      const selected = this._selectedGroup(groups);
      this.shadowRoot.innerHTML = `<style>
        :host{display:block;min-height:100vh;background:var(--primary-background-color,#f5f5f5);color:var(--primary-text-color,#111);font-family:var(--paper-font-body1_-_font-family,Roboto,Arial,sans-serif)}*{box-sizing:border-box}
        .header{position:sticky;top:0;z-index:8;display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;min-height:72px;padding:max(8px,env(safe-area-inset-top,0px)) 8px 7px;background:var(--card-background-color,#fff);border-bottom:1px solid var(--divider-color,#ddd)}.header button{border:0;background:transparent;color:inherit;width:48px;height:48px;border-radius:16px;display:grid;place-items:center}.header ha-icon{--mdc-icon-size:28px}.header .title{text-align:center;min-width:0}.header strong,.header span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.header strong{font-size:22px}.header span{font-size:13px;color:var(--secondary-text-color,#666);margin-top:3px}
        main{width:min(100%,760px);margin:0 auto;padding:14px 14px calc(92px + env(safe-area-inset-bottom,0px))}.vehicle-switcher{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:14px}.vehicle-switcher button{border:1px solid var(--divider-color,#ddd);background:var(--card-background-color,#fff);color:var(--secondary-text-color,#666);border-radius:16px;min-height:46px;padding:8px 12px;display:flex;align-items:center;justify-content:center;gap:7px;font:inherit;font-weight:700}.vehicle-switcher button.active{border-color:var(--primary-color,#03a9f4);color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,var(--card-background-color,#fff))}section{margin:0 0 22px}h2{font-size:18px;margin:0 0 10px;font-weight:700}
        .hero{border-radius:24px;padding:18px;background:linear-gradient(165deg,color-mix(in srgb,var(--primary-color,#0b6ea8) 88%,#07527d),var(--primary-color,#0b6ea8));color:#fff;box-shadow:0 8px 28px rgba(0,0,0,.12)}.hero-heading{display:flex;justify-content:space-between;align-items:center}.hero-heading strong{font-size:24px}.hero-heading span{display:block;font-size:13px;opacity:.82;margin-top:2px}.hero-heading>ha-icon{--mdc-icon-size:34px;opacity:.9}.telemetry-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:16px}.telemetry-chip{min-width:0;border-radius:15px;padding:8px 9px;background:rgba(0,0,0,.16);display:grid;grid-template-columns:24px minmax(0,1fr);grid-template-areas:"i l" "i v";column-gap:7px;align-items:center}.telemetry-chip ha-icon{grid-area:i;--mdc-icon-size:21px;color:#56d5ff}.telemetry-chip span{grid-area:l;font-size:10px;opacity:.76;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.telemetry-chip strong{grid-area:v;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.telemetry-chip.problem{outline:1px solid #ffb300}.car-visual{height:150px;display:grid;place-items:center}.car-visual ha-icon{--mdc-icon-size:132px;color:rgba(255,255,255,.92);filter:drop-shadow(0 12px 12px rgba(0,0,0,.25))}.last-event{text-align:center;display:flex;justify-content:center;gap:10px;align-items:center;font-size:14px}.last-event span{opacity:.72}.last-event strong{font-weight:650}
        .status-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.status-card{min-height:94px;border:1px solid var(--divider-color,#ddd);background:var(--card-background-color,#fff);border-radius:18px;padding:14px;display:flex;align-items:center;gap:13px}.status-card>ha-icon{--mdc-icon-size:31px;color:var(--primary-color,#3f86c7)}.status-card strong,.status-card span{display:block}.status-card strong{font-size:15px}.status-card span{font-size:14px;color:var(--secondary-text-color,#666);margin-top:4px}.status-card.problem{border-color:#ff9800}.detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.detail-card{min-height:125px;border:1px solid var(--divider-color,#ddd);background:var(--card-background-color,#fff);border-radius:18px;padding:15px;display:grid;grid-template-columns:40px minmax(0,1fr);grid-template-rows:auto auto;grid-template-areas:"i v" "i l";align-items:center;column-gap:12px}.detail-card ha-icon{grid-area:i;--mdc-icon-size:34px;color:var(--primary-color,#3f86c7)}.detail-card strong{grid-area:v;font-size:22px}.detail-card span{grid-area:l;color:var(--secondary-text-color,#666);font-size:13px}
        .map-host{min-height:300px;border-radius:20px;overflow:hidden;border:1px solid var(--divider-color,#ddd);background:var(--card-background-color,#fff)}.map-host.tall{min-height:440px}.map-host hui-map-card{display:block;height:100%;min-height:inherit}.location-summary{display:flex;gap:12px;align-items:center;padding:14px;border-radius:18px;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd)}.location-summary ha-icon{--mdc-icon-size:30px;color:var(--primary-color,#3f86c7)}.location-summary strong,.location-summary span{display:block}.location-summary span{margin-top:4px;color:var(--secondary-text-color,#666);font-size:13px}.route-summary{display:grid;grid-template-columns:1fr 1fr;gap:10px}.route-summary>div{border-radius:18px;padding:15px;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd)}.route-summary strong,.route-summary span{display:block}.route-summary strong{font-size:26px}.route-summary span{font-size:12px;color:var(--secondary-text-color,#666);margin-top:4px}
        .timeline{background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd);border-radius:18px;overflow:hidden}.timeline-row{display:grid;grid-template-columns:74px 30px minmax(0,1fr);gap:9px;align-items:center;min-height:58px;padding:8px 13px;border-bottom:1px solid var(--divider-color,#eee)}.timeline-row:last-child{border-bottom:0}.timeline-row time{font-variant-numeric:tabular-nums;color:var(--secondary-text-color,#777);font-size:12px}.timeline-row ha-icon{--mdc-icon-size:21px;color:var(--primary-color,#3f86c7)}.timeline-row span{font-size:14px}.placeholder{padding:16px;border-radius:16px;background:var(--card-background-color,#fff);color:var(--secondary-text-color,#666);border:1px dashed var(--divider-color,#ccc)}.placeholder.problem{border-color:#ff9800}.error{margin:12px 0;padding:12px;border-radius:14px;border:1px solid #ff9800;background:rgba(255,152,0,.08)}
        nav{position:fixed;z-index:12;left:0;right:0;bottom:0;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,#fff);border-top:1px solid var(--divider-color,#ddd);display:grid;grid-template-columns:repeat(${tabs.length},minmax(0,1fr));gap:4px}nav button{border:0;background:transparent;color:var(--secondary-text-color,#666);min-height:62px;border-radius:16px;padding:7px 3px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font:inherit;font-size:11px;font-weight:600}nav button ha-icon{--mdc-icon-size:25px}nav button.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,transparent)}@media(max-width:430px){main{padding-left:10px;padding-right:10px}.status-grid,.detail-grid{gap:8px}.status-card{padding:12px;min-height:88px}.car-visual{height:132px}.car-visual ha-icon{--mdc-icon-size:118px}nav button{font-size:10.5px}}
      </style><div class="header"><button id="back" type="button"><ha-icon icon="mdi:arrow-left"></ha-icon></button><div class="title"><strong>${esc(config.title || "StarLine")}</strong><span>${esc(config.subtitle || "Автомобили")}</span></div><button id="refresh" type="button"><ha-icon icon="mdi:refresh"></ha-icon></button></div><main>${this._error ? `<div class="error">Не удалось прочитать реестры Home Assistant: ${esc(this._error)}</div>` : ""}${this._vehicleSelector(groups)}${this._content(selected)}</main><nav>${tabs.map((tab) => `<button type="button" data-tab="${esc(tab.id)}" class="${tab.id === this._active ? "active" : ""}"><ha-icon icon="${esc(tab.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${esc(tab.label || tab.title || tab.id)}</span></button>`).join("")}</nav>`;
      this.shadowRoot.getElementById("back")?.addEventListener("click", () => navigate(config.parent?.path || "/dashboard-house"));
      this.shadowRoot.getElementById("refresh")?.addEventListener("click", () => { this._registry = null; this._historyCache.clear(); this._load(true); });
      this.shadowRoot.querySelectorAll("[data-tab]").forEach((button) => button.addEventListener("click", () => this._selectTab(button.dataset.tab)));
      this.shadowRoot.querySelectorAll("[data-device]").forEach((button) => button.addEventListener("click", () => this._selectDevice(button.dataset.device)));
      if (selected) {
        const tracker = this._find(selected.entries, "tracker");
        if (this._active === "overview") this._mountMap("overview-map", tracker, 0);
        if (this._active === "location") this._mountMap("location-map", tracker, 24);
        this._ensureHistory(selected);
      }
    }
  }

  customElements.define(ELEMENT_NAME, NikasGeneratedStarline);
})();
