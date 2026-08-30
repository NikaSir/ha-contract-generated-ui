const ELEMENT_NAME = "nikas-rooms-v11-10824";
const UI_VERSION = "11.0.0";
const ROOT_PATH = "/dashboard-rooms/rooms";
const HEADER_ID = "nikas-generated-subpanel-header";
const BAR_ID = "nikas-global-tabbar";
const ACTIVE_LABEL = "v_ekspluatatsii";
const CLIMATE_LABEL = "datchik_klimata_pomeshcheniia";
const EXCLUDED_LABELS = new Set([
  "rezerv",
  "na_obsluzhivanii",
  "trebuet_zameny",
  "vyvedeno_iz_ekspluatatsii",
]);
const BAD_STATES = new Set(["unknown", "unavailable", "none", "null", ""]);
const SUMMARY_CLASSES = ["yellow", "blue", "orange", "green", "grey"];
const REGISTRY_TIMEOUT_MS = 12000;
const LOAD_WATCHDOG_MS = 6000;
const OPENING_CLASSES = new Set([
  "door", "window", "opening", "garage_door", "shutter", "blind", "curtain", "awning",
]);
const ACTIVITY_CLASSES = new Set(["motion", "occupancy", "presence"]);

const ROOMS = [
  ["bathroom", "01", "Ванная", "mdi:bathtub-outline", 2],
  ["bedroom", "02", "Спальня", "mdi:bed-outline", 2],
  ["wardrobe", "03", "Гардероб", "mdi:hanger", 2],
  ["sasha", "04", "У Саши", "mdi:account", 2],
  ["ilya", "05", "У Ильи", "mdi:account-outline", 2],
  ["stairs", "06", "Лестница", "mdi:stairs", 2],
  ["corridor", "07", "Коридор", "mdi:door-open", 2],
  ["hall", "08", "Холл", "mdi:sofa-outline", 2],
  ["boiler", "09", "Котельная", "mdi:water-boiler", 1],
  ["kitchen", "10", "Кухня", "mdi:fridge-outline", 1],
  ["dining", "11.1", "Столовая", "mdi:table-chair", 1],
  ["living", "11.2", "Гостиная", "mdi:sofa", 1],
  ["toilet", "12", "Туалет", "mdi:toilet", 1],
  ["vestibule", "13", "Тамбур", "mdi:door-closed-lock", 1],
  ["veranda", "14", "Веранда", "mdi:home-outline", 1],
  ["garage", "15", "Гараж", "mdi:garage", 1],
  ["attic", "16", "Чердак", "mdi:home-roof", 0],
  ["greenhouse", "17", "Теплица", "mdi:greenhouse", 0],
].map(([slug, no, name, icon, floor]) => ({ slug, no, name, icon, floor }));

function norm(value) {
  return String(value ?? "")
    .trim()
    .toLocaleLowerCase("ru-RU")
    .replace(/ё/g, "е")
    .replace(/\s+/g, " ");
}

function normArea(value) {
  return norm(value).replace(/^\d+(?:[.,]\d+)?\s*(?:[-–—.:)]\s*)?/, "").trim();
}

function labelsOf(item) {
  const labels = item?.labels;
  if (!labels) return [];
  if (Array.isArray(labels)) return labels;
  if (labels instanceof Set) return [...labels];
  if (typeof labels === "object") return Object.keys(labels).filter((key) => labels[key]);
  return [];
}

function hasExcludedLabel(item) {
  return labelsOf(item).some((label) => EXCLUDED_LABELS.has(label));
}

function operational(item) {
  const labels = new Set(labelsOf(item));
  return labels.has(ACTIVE_LABEL) && ![...EXCLUDED_LABELS].some((label) => labels.has(label));
}

function domain(entityId) {
  return String(entityId || "").split(".")[0];
}

function stateClass(entity, hass) {
  return entity?.device_class || hass?.states?.[entity?.entity_id]?.attributes?.device_class || "";
}

function openingKind(entity, hass) {
  const deviceClass = stateClass(entity, hass);
  if (deviceClass === "window") return "windows";
  if (deviceClass === "garage_door") return "gates";
  if (["shutter", "blind", "curtain", "awning"].includes(deviceClass)) return "shutters";
  if (["door", "opening"].includes(deviceClass)) return "doors";
  if (domain(entity?.entity_id) === "cover") return "shutters";
  return null;
}

function isOpenState(entity, state) {
  if (domain(entity?.entity_id) === "cover") return ["open", "opening", "on"].includes(state);
  return state === "on";
}

function titleOfEntity(entity, hass) {
  return entity?.name
    || hass?.states?.[entity?.entity_id]?.attributes?.friendly_name
    || entity?.original_name
    || entity?.entity_id
    || "Сущность";
}

function titleOfDevice(device) {
  return device?.name_by_user || device?.name || device?.model || "Устройство";
}

function goodState(state) {
  return !BAD_STATES.has(norm(state));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

class NikasRoomsV11 extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._panel = null;
    this._registries = null;
    this._rooms = [];
    this._loading = false;
    this._loadGeneration = 0;
    this._hassWaitTimer = null;
    this._loadWatchdogTimer = null;
    this._mounted = false;
    this._routeKey = "";
    this._diagnosticFilter = "*";
    this._fitFrame = null;
    this._stateFrame = null;
    this._chromeFrame = null;
    this._bodyObserver = null;
    this._headerObserver = null;
    this._observedHeader = null;
    this._onLocation = () => {
      if (!this.isRoomsPath()) {
        this.restoreSharedChrome();
        return;
      }
      this.renderRoute();
    };
    this._onResize = () => this.scheduleChromeSync();
  }

  set panel(value) {
    this._panel = value;
    if (this.isConnected && !this._registries) {
      this._loadGeneration += 1;
      this._loading = false;
      this.loadRegistries();
    }
  }

  set hass(value) {
    const first = !this._hass;
    this._hass = value;
    if (this._hassWaitTimer !== null) {
      window.clearTimeout(this._hassWaitTimer);
      this._hassWaitTimer = null;
    }
    if (!this.isConnected) return;
    if (first || !this._registries) this.loadRegistries();
    else this.scheduleStatePatch();
  }

  connectedCallback() {
    this.mountShell();
    this.startLoadWatchdog();
    window.addEventListener("location-changed", this._onLocation);
    window.addEventListener("popstate", this._onLocation);
    window.addEventListener("resize", this._onResize, { passive: true });
    window.visualViewport?.addEventListener?.("resize", this._onResize, { passive: true });
    this.observeSharedChrome();
    this.scheduleChromeSync();
    if (this._registries) this.renderRoute(true);
    else this.loadRegistries();
  }

  disconnectedCallback() {
    this._loadGeneration += 1;
    this._loading = false;
    if (this._hassWaitTimer !== null) window.clearTimeout(this._hassWaitTimer);
    this._hassWaitTimer = null;
    if (this._loadWatchdogTimer !== null) window.clearTimeout(this._loadWatchdogTimer);
    this._loadWatchdogTimer = null;
    window.removeEventListener("location-changed", this._onLocation);
    window.removeEventListener("popstate", this._onLocation);
    window.removeEventListener("resize", this._onResize);
    window.visualViewport?.removeEventListener?.("resize", this._onResize);
    this._bodyObserver?.disconnect();
    this._headerObserver?.disconnect();
    this.restoreSharedChrome();
    this._bodyObserver = null;
    this._headerObserver = null;
    this._observedHeader = null;
    if (this._fitFrame !== null) window.cancelAnimationFrame(this._fitFrame);
    if (this._stateFrame !== null) window.cancelAnimationFrame(this._stateFrame);
    if (this._chromeFrame !== null) window.cancelAnimationFrame(this._chromeFrame);
  }

  registryRequest(type, timeoutMs = REGISTRY_TIMEOUT_MS) {
    let timeoutId = null;
    const request = Promise.resolve().then(() => this._hass.callWS({ type }));
    const timeout = new Promise((_, reject) => {
      timeoutId = window.setTimeout(() => reject(new Error(`Registry request timed out: ${type}`)), timeoutMs);
    });
    return Promise.race([request, timeout]).finally(() => {
      if (timeoutId !== null) window.clearTimeout(timeoutId);
    });
  }

  showRegistryError(detail = "Не удалось прочитать реестры Home Assistant.") {
    this.clearLoadWatchdog();
    const canvas = this.shadowRoot?.getElementById("canvas");
    if (!canvas) return;
    canvas.innerHTML = `
      <div class="loading registry-error">
        <b>Не удалось загрузить помещения</b>
        <span>${escapeHtml(detail)}</span>
        <button type="button" id="retry-registries">Повторить</button>
      </div>`;
    canvas.querySelector("#retry-registries")?.addEventListener("click", () => this.loadRegistries(true));
  }

  startLoadWatchdog() {
    if (this._loadWatchdogTimer !== null || this._registries) return;
    this._loadWatchdogTimer = window.setTimeout(() => {
      this._loadWatchdogTimer = null;
      if (!this.isConnected || this._registries) return;
      this._loadGeneration += 1;
      this._loading = false;
      this.showRegistryError("Начальные данные помещений не были подготовлены вовремя.");
      this.syncRefreshState();
    }, LOAD_WATCHDOG_MS);
  }

  clearLoadWatchdog() {
    if (this._loadWatchdogTimer !== null) window.clearTimeout(this._loadWatchdogTimer);
    this._loadWatchdogTimer = null;
  }

  normalizeRegistries(value) {
    if (!value || typeof value !== "object") return null;
    const areas = Array.isArray(value.areas) ? value.areas.filter(Boolean) : [];
    if (!areas.length) return null;
    return {
      areas,
      devices: Array.isArray(value.devices) ? value.devices.filter(Boolean) : [],
      entities: Array.isArray(value.entities) ? value.entities.filter(Boolean) : [],
      labels: Array.isArray(value.labels) ? value.labels.filter(Boolean) : [],
    };
  }

  panelRegistryBootstrap() {
    return this.normalizeRegistries(
      this._panel?.config?.registry_bootstrap || this._panel?.registry_bootstrap,
    );
  }

  resolveHass() {
    if (this._hass?.states || this._hass?.callWS) return this._hass;
    const hass = document.querySelector("home-assistant")?.hass || null;
    if (hass) this._hass = hass;
    return hass;
  }

  adoptRegistries(value) {
    const registries = this.normalizeRegistries(value);
    if (!registries) throw new Error("Registry payload has no areas");
    this._registries = registries;
    this.buildRooms();
    this.renderRoute(true);
    this.clearLoadWatchdog();
    this.syncRefreshState();
  }

  registrySnapshot() {
    const hass = this.resolveHass();
    const areas = hass?.areas;
    const devices = hass?.devices;
    const entities = hass?.entities;
    if (!areas || !devices || !entities || typeof areas !== "object"
      || typeof devices !== "object" || typeof entities !== "object") return null;
    const areaEntries = Object.values(areas);
    if (!areaEntries.length) return null;
    return {
      areas: areaEntries,
      devices: Object.values(devices),
      entities: Object.values(entities),
      labels: hass?.labels && typeof hass.labels === "object"
        ? Object.values(hass.labels)
        : [],
    };
  }

  waitForHass() {
    if (this._hassWaitTimer !== null) return;
    this._hassWaitTimer = window.setTimeout(() => {
      this._hassWaitTimer = null;
      if (!this.isConnected || this._registries) return;
      if (this.resolveHass()?.callWS || this.registrySnapshot()) this.loadRegistries();
      else this.showRegistryError("Панель не получила данные от Home Assistant.");
    }, 3000);
  }

  mountShell() {
    if (this._mounted) return;
    this._mounted = true;
    this.shadowRoot.innerHTML = `
      <style>${this.styles()}</style>
      <div class="viewport" id="viewport">
        <div class="canvas" id="canvas">
          <div class="loading">Загрузка помещений…</div>
        </div>
      </div>`;
  }

  observeSharedChrome() {
    if (this._bodyObserver || !document.body || typeof MutationObserver !== "function") return;
    this._bodyObserver = new MutationObserver(() => this.scheduleChromeSync());
    this._bodyObserver.observe(document.body, { childList: true, subtree: true });
  }

  observeHeader(header) {
    if (this._observedHeader === header) return;
    this._headerObserver?.disconnect();
    this._headerObserver = null;
    this._observedHeader = header || null;
    if (!header?.shadowRoot || typeof MutationObserver !== "function") return;
    this._headerObserver = new MutationObserver(() => this.scheduleChromeSync());
    this._headerObserver.observe(header.shadowRoot, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  }

  async loadRegistries(force = false) {
    if (this._loading || !this.isConnected) return;
    this.mountShell();
    this.startLoadWatchdog();
    try {
      if (!force) {
        const bootstrap = this.panelRegistryBootstrap();
        if (bootstrap) {
          this.adoptRegistries(bootstrap);
          return;
        }
        const snapshot = this.registrySnapshot();
        if (snapshot) {
          this.adoptRegistries(snapshot);
          return;
        }
      }

      const hass = this.resolveHass();
      if (!hass?.callWS) {
        this.waitForHass();
        return;
      }

      const generation = ++this._loadGeneration;
      this._loading = true;
      if (!this._registries) {
        const canvas = this.shadowRoot?.getElementById("canvas");
        if (canvas) canvas.innerHTML = '<div class="loading">Загрузка помещений…</div>';
      }
      this.syncRefreshState();
      const labelsPromise = this.registryRequest("config/label_registry/list", 5000).catch(() => []);
      const [areas, devices, entities, labels] = await Promise.all([
        this.registryRequest("config/area_registry/list"),
        this.registryRequest("config/device_registry/list"),
        this.registryRequest("config/entity_registry/list"),
        labelsPromise,
      ]);
      if (!this.isConnected || generation !== this._loadGeneration) return;
      this.adoptRegistries({
        areas: Array.isArray(areas) ? areas : [],
        devices: Array.isArray(devices) ? devices : [],
        entities: Array.isArray(entities) ? entities : [],
        labels: Array.isArray(labels) ? labels : [],
      });
    } catch (error) {
      console.warn("[NikaS Rooms v11] registry load failed", error);
      if (!this._registries) {
        const detail = error instanceof Error && error.message
          ? `Не удалось подготовить данные: ${error.message}`
          : "Не удалось прочитать реестры Home Assistant.";
        this.showRegistryError(detail);
      }
    } finally {
      this._loading = false;
      this.syncRefreshState();
    }
  }

  buildRooms() {
    const { areas, devices, entities, labels } = this._registries;
    const deviceMap = new Map(devices.map((device) => [device.id, device]));
    const labelMap = new Map(labels.map((label) => [label.label_id, label.name || label.label_id]));

    this._rooms = ROOMS.map((definition) => {
      const area = areas.find((item) =>
        norm(item.name) === norm(definition.name)
        || normArea(item.name) === norm(definition.name)
        || norm(item.area_id) === norm(definition.name));

      if (!area) {
        return {
          ...definition,
          area: null,
          devices: [],
          entities: [],
          standalone: [],
          diagnosticDevices: [],
          diagnosticEntities: [],
          diagnosticStandalone: [],
          labelMap,
        };
      }

      const diagnosticDevices = devices.filter((device) => device.area_id === area.area_id);
      const roomDevices = diagnosticDevices.filter((device) => !device.disabled_by && operational(device));
      const deviceIds = new Set(roomDevices.map((device) => device.id));

      const diagnosticEntities = entities.filter((entity) => {
        if (entity.device_id) {
          const effectiveArea = entity.area_id || deviceMap.get(entity.device_id)?.area_id || null;
          return effectiveArea === area.area_id;
        }
        return entity.area_id === area.area_id;
      });

      const roomEntities = diagnosticEntities.filter((entity) => {
        if (entity.disabled_by || entity.hidden_by || hasExcludedLabel(entity)) return false;
        if (entity.device_id) return deviceIds.has(entity.device_id);
        return operational(entity);
      });

      return {
        ...definition,
        area,
        devices: roomDevices,
        entities: roomEntities,
        standalone: roomEntities.filter((entity) => !entity.device_id),
        diagnosticDevices,
        diagnosticEntities,
        diagnosticStandalone: diagnosticEntities.filter((entity) => !entity.device_id),
        labelMap,
      };
    });
  }

  isRoomsPath() {
    return window.location.pathname === "/dashboard-rooms"
      || window.location.pathname.startsWith("/dashboard-rooms/");
  }

  route() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    if (parts[0] !== "dashboard-rooms") return { kind: "overview" };
    if (parts[1]?.startsWith("room-")) {
      const slug = parts[1].slice(5);
      return { kind: parts[2] === "diagnostics" ? "diagnostics" : "room", slug };
    }
    return { kind: "overview" };
  }

  routeKey(route) {
    return `${route.kind}:${route.slug || ""}`;
  }

  navigate(path) {
    if (!path || !path.startsWith("/")) return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  room(slug) {
    return this._rooms.find((room) => room.slug === slug) || null;
  }

  entityState(entity) {
    return this._hass?.states?.[entity.entity_id] || null;
  }

  summary(room) {
    if (!room?.area) return { text: "Система не настроена", tone: "orange" };
    const entities = room.entities.filter((entity) => {
      const deviceClass = stateClass(entity, this._hass);
      return openingKind(entity, this._hass)
        || (domain(entity.entity_id) === "binary_sensor" && ACTIVITY_CLASSES.has(deviceClass));
    });

    if (!entities.length) return { text: "Нет датчиков", tone: "grey" };

    const open = { windows: 0, doors: 0, gates: 0, shutters: 0 };
    let activity = 0;
    let unavailable = 0;
    let missing = 0;
    for (const entity of entities) {
      const stateObject = this.entityState(entity);
      if (!stateObject) {
        missing += 1;
        continue;
      }
      const state = stateObject.state;
      const deviceClass = stateClass(entity, this._hass);
      if (!goodState(state)) {
        unavailable += 1;
        continue;
      }
      const kind = openingKind(entity, this._hass);
      if (kind && isOpenState(entity, state)) open[kind] += 1;
      if (state === "on" && ACTIVITY_CLASSES.has(deviceClass)) activity += 1;
    }

    const openLabels = [
      ["windows", "Окна"],
      ["doors", "Двери"],
      ["gates", "Ворота"],
      ["shutters", "Роллеты"],
    ].filter(([kind]) => open[kind]).map(([kind, label]) => `${label} ${open[kind]}`);
    if (openLabels.length) {
      const suffix = unavailable ? ` · недоступно ${unavailable}` : missing ? ` · нет связи ${missing}` : "";
      return { text: `${openLabels.join(" · ")}${suffix}`, tone: "yellow" };
    }
    if (activity) return { text: `Активность ${activity}`, tone: "blue" };
    if (missing) return { text: "Соединение с HA потеряно", tone: "orange" };
    if (unavailable) return { text: `Недоступно ${unavailable}`, tone: "orange" };
    return { text: "Спокойно", tone: "green" };
  }

  formatEntity(entity) {
    const stateObject = this.entityState(entity);
    if (!stateObject) return "Соединение с HA потеряно";
    if (stateObject.state === "unavailable") return "Недоступно";
    if (!goodState(stateObject.state)) return "Состояние неизвестно";
    const state = stateObject.state;
    const unit = stateObject.attributes?.unit_of_measurement || "";
    const deviceClass = stateClass(entity, this._hass);

    if (openingKind(entity, this._hass)) {
      return isOpenState(entity, state) ? "Открыто" : "Закрыто";
    }
    if (domain(entity.entity_id) === "binary_sensor") {
      if (ACTIVITY_CLASSES.has(deviceClass)) return state === "on" ? "Обнаружено" : "Не обнаружено";
    }
    return `${state}${unit ? ` ${unit}` : ""}`;
  }

  isClimateEntity(entity) {
    return ["temperature", "humidity"].includes(stateClass(entity, this._hass));
  }

  isPrimaryClimateEntity(room, entity) {
    if (labelsOf(entity).includes(CLIMATE_LABEL)) return true;
    if (!entity.device_id) return false;
    const device = room.devices.find((item) => item.id === entity.device_id);
    return labelsOf(device).includes(CLIMATE_LABEL);
  }

  primaryClimateEntities(room) {
    return room.entities.filter((entity) =>
      this.isClimateEntity(entity) && this.isPrimaryClimateEntity(room, entity));
  }

  extraClimateGroups(room, primaryEntities) {
    const primaryIds = new Set(primaryEntities.map((entity) => entity.entity_id));
    const groups = new Map();
    for (const entity of room.entities) {
      if (!this.isClimateEntity(entity) || primaryIds.has(entity.entity_id)) continue;
      const key = entity.device_id ? `device:${entity.device_id}` : `entity:${entity.entity_id}`;
      if (!groups.has(key)) {
        const device = entity.device_id
          ? room.devices.find((item) => item.id === entity.device_id)
          : null;
        groups.set(key, {
          title: device ? titleOfDevice(device) : titleOfEntity(entity, this._hass),
          entities: [],
        });
      }
      groups.get(key).entities.push(entity);
    }
    return [...groups.values()];
  }

  entityDisplayName(entity) {
    const deviceClass = stateClass(entity, this._hass);
    const names = {
      temperature: "Температура",
      humidity: "Влажность",
      illuminance: "Освещённость",
      motion: "Движение",
      occupancy: "Присутствие",
      presence: "Присутствие",
      door: "Дверь",
      window: "Окно",
      opening: "Открытие",
      garage_door: "Ворота",
      shutter: "Роллета",
      blind: "Жалюзи",
      curtain: "Штора",
      awning: "Маркиза",
    };
    return names[deviceClass] || titleOfEntity(entity, this._hass);
  }

  entityIcon(entity) {
    const deviceClass = stateClass(entity, this._hass);
    const icons = {
      temperature: "mdi:thermometer",
      humidity: "mdi:water-percent",
      illuminance: "mdi:brightness-6",
      motion: "mdi:motion-sensor",
      occupancy: "mdi:home-account",
      presence: "mdi:account-check-outline",
      door: "mdi:door",
      window: "mdi:window-closed-variant",
      opening: "mdi:door-open",
      garage_door: "mdi:garage",
      shutter: "mdi:window-shutter",
      blind: "mdi:blinds-horizontal",
      curtain: "mdi:curtains",
      awning: "mdi:awning-outline",
    };
    if (domain(entity.entity_id) === "camera") return "mdi:cctv";
    return icons[deviceClass] || "mdi:information-outline";
  }

  renderRoute(force = false) {
    if (!this.isRoomsPath()) return;
    this.mountShell();
    const route = this.route();
    const key = this.routeKey(route);
    this.syncSharedChrome(route);

    if (!this._registries) {
      this.scheduleChromeSync();
      return;
    }
    if (!force && key === this._routeKey) {
      this.scheduleStatePatch();
      return;
    }

    this._routeKey = key;
    this._diagnosticFilter = "*";
    const room = route.slug ? this.room(route.slug) : null;
    const canvas = this.shadowRoot.getElementById("canvas");
    canvas.innerHTML = route.kind === "overview"
      ? this.overviewMarkup()
      : route.kind === "diagnostics"
        ? this.diagnosticsMarkup(room)
        : this.roomMarkup(room);
    canvas.className = `canvas ${route.kind}`;
    this.bindView(room);
    const viewport = this.shadowRoot.getElementById("viewport");
    if (viewport) viewport.scrollTop = 0;
    this.scheduleChromeSync();
  }

  overviewMarkup() {
    const group = (floor, label, icon) => `
      <section class="floor">
        <h2><ha-icon icon="${icon}"></ha-icon>${label}</h2>
        <div class="room-grid">
          ${this._rooms.filter((room) => room.floor === floor).map((room) => this.roomCard(room)).join("")}
        </div>
      </section>`;
    return `<div class="overview">
      ${group(2, "2 этаж", "mdi:home-floor-2")}
      ${group(1, "1 этаж", "mdi:home-floor-1")}
      ${group(0, "Технические помещения", "mdi:tools")}
    </div>`;
  }

  roomCard(room) {
    const summary = this.summary(room);
    return `
      <button class="room-card tone-${summary.tone}" type="button"
              data-room="${room.slug}" data-summary-room="${room.slug}">
        <ha-icon icon="${room.icon}"></ha-icon>
        <span>
          <b>${escapeHtml(room.name)} [${room.no}]</b>
          <small data-summary-text>${escapeHtml(summary.text)}</small>
        </span>
      </button>`;
  }

  section(title, icon, entities) {
    if (!entities.length) return "";
    return `
      <section class="section">
        <h2><ha-icon icon="${icon}"></ha-icon>${title}</h2>
        <div class="entity-grid">
          ${entities.map((entity) => `
            <button class="entity" type="button" data-entity="${entity.entity_id}">
              <ha-icon icon="${this.entityIcon(entity)}"></ha-icon>
              <span>${escapeHtml(this.entityDisplayName(entity))}</span>
              <b data-value="${entity.entity_id}">${escapeHtml(this.formatEntity(entity))}</b>
            </button>`).join("")}
        </div>
      </section>`;
  }

  extraClimate(room, primaryEntities) {
    return this.extraClimateGroups(room, primaryEntities)
      .map((group) => `
        <div class="sensor-card">
          <b>${escapeHtml(group.title)}</b>
          ${group.entities.map((entity) => `
            <button type="button" data-entity="${entity.entity_id}">
              <ha-icon icon="${this.entityIcon(entity)}"></ha-icon>
              <span>${escapeHtml(this.entityDisplayName(entity))}</span>
              <strong data-value="${entity.entity_id}">${escapeHtml(this.formatEntity(entity))}</strong>
            </button>`).join("")}
        </div>`)
      .join("");
  }

  roomMarkup(room) {
    if (!room?.area) return '<div class="loading">Помещение не найдено в реестре Home Assistant</div>';
    const primaryClimate = this.primaryClimateEntities(room);
    const activity = room.entities.filter((entity) => {
      const deviceClass = stateClass(entity, this._hass);
      return ACTIVITY_CLASSES.has(deviceClass) || deviceClass === "illuminance";
    });
    const security = room.entities.filter((entity) => openingKind(entity, this._hass));
    const cameras = room.entities.filter((entity) => domain(entity.entity_id) === "camera");
    const extraClimate = this.extraClimate(room, primaryClimate);

    return `
      <div class="room-view">
        ${this.section("Климат", "mdi:thermometer", primaryClimate)}
        ${extraClimate ? `
          <section class="section">
            <h2><ha-icon icon="mdi:thermometer-lines"></ha-icon>Дополнительные климатические датчики</h2>
            <div class="sensor-grid">${extraClimate}</div>
          </section>` : ""}
        ${this.section("Активность", "mdi:motion-sensor", activity)}
        ${this.section("Безопасность", "mdi:shield-home", security)}
        ${this.section("Камеры", "mdi:cctv", cameras)}
        <button class="diagnostics" id="diagnostics" type="button">Диагностика</button>
      </div>`;
  }

  diagnosticItems(room) {
    const deviceItems = room.diagnosticDevices.map((device) => {
      const entities = room.diagnosticEntities.filter((entity) => entity.device_id === device.id);
      const labels = new Set(labelsOf(device));
      for (const entity of entities) for (const label of labelsOf(entity)) labels.add(label);
      return {
        key: `device:${device.id}`,
        title: titleOfDevice(device),
        labels,
        entities,
      };
    });
    const standaloneItems = room.diagnosticStandalone.map((entity) => ({
      key: `entity:${entity.entity_id}`,
      title: titleOfEntity(entity, this._hass),
      labels: new Set(labelsOf(entity)),
      entities: [entity],
    }));
    return [...deviceItems, ...standaloneItems].sort((left, right) => left.title.localeCompare(right.title, "ru"));
  }

  diagnosticsMarkup(room) {
    if (!room?.area) return '<div class="loading">Помещение не найдено</div>';
    const items = this.diagnosticItems(room);
    const labels = new Map();
    for (const item of items) {
      for (const label of item.labels) labels.set(label, room.labelMap.get(label) || label);
    }
    const choices = [["*", "Все"], ...[...labels.entries()].sort((a, b) => a[1].localeCompare(b[1], "ru"))];

    return `
      <div class="diagnostic-view">
        <section class="diagnostic-card">
          <h2>Оборудование</h2>
          <p>${escapeHtml(room.area.name)} · ${items.length} поз.</p>
          <div class="filters" aria-label="Фильтр по ярлыкам">
            ${choices.map(([id, name]) => `
              <button type="button" class="${id === "*" ? "active" : ""}" data-filter="${escapeHtml(id)}">
                ${escapeHtml(name)}
              </button>`).join("")}
          </div>
          <div class="devices">
            ${items.map((item) => `
              <article class="device" data-diagnostic-item data-labels="${escapeHtml([...item.labels].join(" "))}">
                <h3>${escapeHtml(item.title)}</h3>
                <div class="chips">
                  ${[...item.labels].map((label) => `<span>${escapeHtml(room.labelMap.get(label) || label)}</span>`).join("")}
                </div>
                ${item.entities.map((entity) => `
                  <button type="button" data-entity="${entity.entity_id}">
                    <span>${escapeHtml(titleOfEntity(entity, this._hass))}</span>
                    <b data-value="${entity.entity_id}">${escapeHtml(this.formatEntity(entity))}</b>
                  </button>`).join("")}
              </article>`).join("") || '<div class="loading">Нет оборудования</div>'}
          </div>
          <div class="diagnostic-empty" id="diagnostic-empty" hidden>Нет оборудования для выбранного ярлыка.</div>
        </section>
      </div>`;
  }

  bindView(room) {
    this.shadowRoot.querySelectorAll("[data-room]").forEach((button) => {
      button.onclick = () => this.navigate(`/dashboard-rooms/room-${button.dataset.room}`);
    });
    this.shadowRoot.querySelectorAll("[data-entity]").forEach((button) => {
      button.onclick = () => this.dispatchEvent(new CustomEvent("hass-more-info", {
        bubbles: true,
        composed: true,
        detail: { entityId: button.dataset.entity },
      }));
    });
    this.shadowRoot.getElementById("diagnostics")?.addEventListener("click", () => {
      this.navigate(`/dashboard-rooms/room-${room.slug}/diagnostics`);
    });
    this.shadowRoot.querySelectorAll("[data-filter]").forEach((button) => {
      button.onclick = () => this.applyDiagnosticFilter(button.dataset.filter || "*");
    });
  }

  applyDiagnosticFilter(filter) {
    this._diagnosticFilter = filter;
    let visible = 0;
    for (const button of this.shadowRoot.querySelectorAll("[data-filter]")) {
      button.classList.toggle("active", button.dataset.filter === filter);
    }
    for (const item of this.shadowRoot.querySelectorAll("[data-diagnostic-item]")) {
      const labels = new Set(String(item.dataset.labels || "").split(/\s+/).filter(Boolean));
      const show = filter === "*" || labels.has(filter);
      item.hidden = !show;
      if (show) visible += 1;
    }
    const empty = this.shadowRoot.getElementById("diagnostic-empty");
    if (empty) empty.hidden = visible !== 0;
  }

  scheduleStatePatch() {
    if (this._stateFrame !== null) return;
    this._stateFrame = window.requestAnimationFrame(() => {
      this._stateFrame = null;
      this.patchStates();
    });
  }

  patchStates() {
    if (!this._registries || !this.isConnected) return;
    const allEntities = this._rooms.flatMap((room) => room.diagnosticEntities);
    const byId = new Map(allEntities.map((entity) => [entity.entity_id, entity]));

    for (const node of this.shadowRoot.querySelectorAll("[data-value]")) {
      const entity = byId.get(node.dataset.value);
      if (!entity) continue;
      const value = this.formatEntity(entity);
      if (node.textContent !== value) node.textContent = value;
    }

    for (const card of this.shadowRoot.querySelectorAll("[data-summary-room]")) {
      const room = this.room(card.dataset.summaryRoom);
      const summary = this.summary(room);
      const text = card.querySelector("[data-summary-text]");
      if (text && text.textContent !== summary.text) text.textContent = summary.text;
      for (const tone of SUMMARY_CLASSES) {
        card.classList.toggle(`tone-${tone}`, tone === summary.tone);
      }
    }
    this.syncSharedChrome();
  }

  scheduleChromeSync() {
    if (this._chromeFrame !== null) return;
    this._chromeFrame = window.requestAnimationFrame(() => {
      this._chromeFrame = null;
      this.syncSharedChrome();
      this.scheduleFit();
    });
  }

  ensureRoomsHeaderStyle(shadow) {
    if (shadow.getElementById("nikas-rooms-v11-header-style")) return;
    const style = document.createElement("style");
    style.id = "nikas-rooms-v11-header-style";
    style.textContent = `
      button.title{
        appearance:none;width:auto;height:auto;min-width:0;max-width:100%;min-height:0;
        justify-self:center;padding:0;border:0;border-radius:0;background:transparent;
        color:inherit;display:block;box-shadow:none;text-align:center;line-height:1.15;
        font:inherit;cursor:default;-webkit-tap-highlight-color:transparent
      }
      button.title:disabled{opacity:1;color:inherit}
      button.title.rooms-return{
        cursor:pointer;min-width:min(290px,100%);min-height:44px;padding:5px 14px;
        border:1px solid color-mix(in srgb,var(--primary-color,#03a9d9) 24%,var(--divider-color,#dfe3e8));
        border-radius:16px;
        background:color-mix(in srgb,var(--primary-color,#03a9d9) 5%,var(--card-background-color,#fff));
        box-shadow:0 5px 16px rgba(23,45,76,.06)
      }
      button.title.rooms-return:active{
        transform:scale(.985);
        border-color:color-mix(in srgb,var(--primary-color,#03a9d9) 42%,var(--divider-color,#dfe3e8));
        background:color-mix(in srgb,var(--primary-color,#03a9d9) 13%,var(--card-background-color,#fff));
        box-shadow:0 2px 7px rgba(23,45,76,.05)
      }
      button.title.rooms-return:focus-visible{
        outline:2px solid var(--primary-color,#03a9d9);outline-offset:2px
      }
      @media(max-width:390px){
        button.title.rooms-return{min-width:0;width:100%;padding-inline:8px}
      }`;
    shadow.appendChild(style);
  }

  ensureTitleButton(shadow) {
    let title = shadow.querySelector(".title");
    if (!title) return null;
    if (title.localName === "button") return title;
    const button = document.createElement("button");
    button.type = "button";
    button.className = title.className;
    while (title.firstChild) button.appendChild(title.firstChild);
    title.replaceWith(button);
    return button;
  }

  headerModel(route = this.route()) {
    const room = route.slug ? this.room(route.slug) : null;
    if (route.kind === "overview") {
      return { title: "Помещения", subtitle: `Обзор · UI v${UI_VERSION}`, backPath: null };
    }
    if (route.kind === "diagnostics") {
      return {
        title: room?.name || "Помещение",
        subtitle: `Диагностика · UI v${UI_VERSION}`,
        backPath: room ? `/dashboard-rooms/room-${room.slug}` : ROOT_PATH,
      };
    }
    return {
      title: room?.name || "Помещение",
      subtitle: `Помещения · UI v${UI_VERSION}`,
      backPath: ROOT_PATH,
    };
  }

  syncSharedChrome(route = this.route()) {
    if (!this.isRoomsPath()) return;
    const header = document.getElementById(HEADER_ID);
    const bar = document.getElementById(BAR_ID);
    this.observeHeader(header);
    if (!header?.shadowRoot) return;

    const shadow = header.shadowRoot;
    this.ensureRoomsHeaderStyle(shadow);
    const title = this.ensureTitleButton(shadow);
    const strong = title?.querySelector("strong");
    const secondary = title?.querySelector("span");
    if (!title || !strong || !secondary) return;

    const model = this.headerModel(route);
    if (strong.textContent !== model.title) strong.textContent = model.title;
    if (secondary.textContent !== model.subtitle) secondary.textContent = model.subtitle;

    title.classList.toggle("rooms-return", Boolean(model.backPath));
    title.classList.toggle("link", Boolean(model.backPath));
    title.disabled = !model.backPath;
    title.onclick = model.backPath ? () => this.navigate(model.backPath) : null;
    title.onkeydown = null;
    if (model.backPath) {
      const label = `Вернуться: ${model.backPath === ROOT_PATH ? "Помещения" : model.title}`;
      if (title.getAttribute("aria-label") !== label) title.setAttribute("aria-label", label);
    } else {
      title.removeAttribute("aria-label");
    }

    const refresh = shadow.getElementById("refresh");
    if (refresh) {
      refresh.onclick = () => this.loadRegistries(true);
      if (refresh.disabled !== this._loading) refresh.disabled = this._loading;
      const busy = this._loading ? "true" : "false";
      if (refresh.getAttribute("aria-busy") !== busy) refresh.setAttribute("aria-busy", busy);
    }
    const subpanel = `rooms-v11-${route.kind}`;
    if (header.dataset.subpanel !== subpanel) header.dataset.subpanel = subpanel;
    if (bar && bar.dataset.roomsV11 !== "true") bar.dataset.roomsV11 = "true";
  }

  restoreSharedChrome() {
    const header = document.getElementById(HEADER_ID);
    const shadow = header?.shadowRoot;
    const title = shadow?.querySelector("button.title");
    if (title) {
      const replacement = document.createElement("div");
      replacement.className = "title";
      while (title.firstChild) replacement.appendChild(title.firstChild);
      title.replaceWith(replacement);
    }
    shadow?.getElementById("nikas-rooms-v11-header-style")?.remove();
    const refresh = shadow?.getElementById("refresh");
    if (refresh) {
      refresh.disabled = false;
      refresh.removeAttribute("aria-busy");
      refresh.onclick = () => window.location.reload();
    }
    if (header?.dataset?.subpanel?.startsWith("rooms-v11-")) delete header.dataset.subpanel;
    const bar = document.getElementById(BAR_ID);
    if (bar?.dataset?.roomsV11) delete bar.dataset.roomsV11;
  }

  syncRefreshState() {
    const header = document.getElementById(HEADER_ID);
    const refresh = header?.shadowRoot?.getElementById("refresh");
    if (!refresh) return;
    if (refresh.disabled !== this._loading) refresh.disabled = this._loading;
    const busy = this._loading ? "true" : "false";
    if (refresh.getAttribute("aria-busy") !== busy) refresh.setAttribute("aria-busy", busy);
  }

  scheduleFit() {
    if (this._fitFrame !== null) window.cancelAnimationFrame(this._fitFrame);
    this._fitFrame = window.requestAnimationFrame(() => {
      this._fitFrame = null;
      this.fitViewport();
    });
  }

  fitViewport() {
    const viewport = this.shadowRoot?.getElementById("viewport");
    const header = document.getElementById(HEADER_ID);
    const bar = document.getElementById(BAR_ID);
    if (!viewport) return;

    const top = header?.getBoundingClientRect?.().bottom ?? 0;
    const bottom = bar?.getBoundingClientRect?.().top ?? window.innerHeight;
    if (!Number.isFinite(top) || !Number.isFinite(bottom) || bottom <= top) return;

    const nextTop = `${Math.round(top)}px`;
    const nextHeight = `${Math.round(bottom - top)}px`;
    if (viewport.style.top !== nextTop) viewport.style.top = nextTop;
    if (viewport.style.height !== nextHeight) viewport.style.height = nextHeight;
  }

  styles() {
    return `
      :host{
        position:fixed;inset:0;z-index:1;pointer-events:none;
        color:var(--primary-text-color,#111);
        font-family:var(--paper-font-body1_-_font-family,Arial,sans-serif)
      }
      *{box-sizing:border-box}
      button{font:inherit;-webkit-tap-highlight-color:transparent}
      .viewport{
        position:fixed;left:0;right:0;top:70px;height:calc(100dvh - 140px);
        overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;touch-action:pan-y;
        pointer-events:auto;background:var(--primary-background-color,#f7f7f7);
        -webkit-overflow-scrolling:touch
      }
      .canvas{min-height:100%;padding:10px 8px max(18px,env(safe-area-inset-bottom,0px))}
      .loading{padding:24px;text-align:center;color:var(--secondary-text-color,#666);font-size:14px}
      .registry-error{display:grid;justify-items:center;gap:10px;padding-top:32px}
      .registry-error b{font-size:17px;color:var(--primary-text-color,#111)}
      .registry-error span{font-size:13px}
      .registry-error button{
        min-width:140px;min-height:42px;padding:8px 16px;border:1px solid var(--divider-color,#ddd);
        border-radius:14px;background:var(--card-background-color,#fff);color:var(--primary-text-color,#111);
        font-weight:750
      }
      .overview{min-height:100%;display:flex;flex-direction:column;justify-content:flex-start;gap:14px}
      .floor h2{
        height:22px;margin:0 0 4px;display:flex;align-items:center;gap:7px;
        font-size:16px;font-weight:650
      }
      .floor h2 ha-icon{--mdc-icon-size:20px}
      .room-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px 7px}
      .room-card{
        min-height:46px;border:1px solid var(--divider-color,#ddd);border-radius:14px;
        background:var(--card-background-color,#fff);padding:5px 9px;
        display:grid;grid-template-columns:32px minmax(0,1fr);gap:5px;align-items:center;
        text-align:left;color:inherit
      }
      .room-card:focus-visible,.entity:focus-visible,.sensor-card button:focus-visible,
      .device button:focus-visible,.diagnostics:focus-visible,.filters button:focus-visible{
        outline:2px solid var(--primary-color,#2196f3);outline-offset:2px
      }
      .room-card>ha-icon{--mdc-icon-size:25px;color:var(--primary-color,#2196f3)}
      .room-card b,.room-card small{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .room-card b{font-size:14px}
      .room-card small{font-size:12px;margin-top:1px}
      .tone-yellow>ha-icon{color:#f2c400}.tone-orange>ha-icon{color:#fb8c00}
      .tone-green>ha-icon{color:#2dbd65}.tone-blue>ha-icon{color:#2196f3}.tone-grey>ha-icon{color:#999}
      .section{margin:0 0 13px}
      .section h2{display:flex;align-items:center;gap:8px;margin:0 0 7px;font-size:19px}
      .section h2 ha-icon{--mdc-icon-size:23px}
      .entity-grid,.sensor-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
      .entity,.sensor-card{
        min-height:52px;border:1px solid var(--divider-color,#ddd);border-radius:14px;
        background:var(--card-background-color,#fff);color:inherit;padding:9px 10px
      }
      .entity{display:grid;grid-template-columns:24px minmax(0,1fr) auto;align-items:center;gap:7px;text-align:left}
      .entity>ha-icon,.sensor-card button>ha-icon{--mdc-icon-size:21px;color:var(--primary-color,#2196f3)}
      .entity span,.sensor-card button span,.device button span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
      .entity span,.sensor-card button span,.device button span{font-size:13px}
      .entity b,.sensor-card strong,.device button b{white-space:nowrap;font-size:12px;color:var(--secondary-text-color,#666)}
      .sensor-card>b{display:block;margin-bottom:5px;font-size:14px}
      .sensor-card button,.device button{
        width:100%;border:0;border-top:1px solid var(--divider-color,#ddd);background:transparent;
        color:inherit;padding:7px 0;display:grid;grid-template-columns:24px minmax(0,1fr) auto;
        gap:7px;align-items:center;text-align:left
      }
      .device button{grid-template-columns:minmax(0,1fr) auto}
      .diagnostics{
        width:100%;min-height:52px;border:1px solid var(--divider-color,#ddd);border-radius:16px;
        background:var(--card-background-color,#fff);font-size:17px;font-weight:800;color:inherit
      }
      .diagnostic-card{
        background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd);
        border-radius:18px;padding:13px
      }
      .diagnostic-card h2{margin:0;font-size:20px}
      .diagnostic-card p{margin:3px 0 10px;color:var(--secondary-text-color,#666);font-size:13px}
      .filters{display:flex;gap:7px;overflow-x:auto;padding:1px 0 10px;scrollbar-width:none}
      .filters::-webkit-scrollbar{display:none}
      .filters button{
        flex:0 0 auto;min-height:34px;padding:6px 10px;border:1px solid var(--divider-color,#ddd);
        border-radius:999px;background:transparent;color:inherit;font-size:12px;font-weight:700
      }
      .filters button.active{background:var(--primary-color,#2196f3);border-color:var(--primary-color,#2196f3);color:#fff}
      .devices{display:grid;gap:9px}
      .device{
        background:var(--secondary-background-color,#eee);border:1px solid var(--divider-color,#ddd);
        border-radius:14px;padding:10px
      }
      .device[hidden]{display:none}
      .device h3{margin:0 0 7px;font-size:16px}
      .chips{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:5px}
      .chips span{
        padding:3px 6px;border-radius:999px;background:var(--card-background-color,#fff);
        font-size:12px;color:var(--secondary-text-color,#666)
      }
      .diagnostic-empty{padding:12px 2px;color:var(--secondary-text-color,#666);font-size:13px}
      @media(max-height:780px){
        .canvas{padding-top:7px}.room-card{min-height:43px}.room-card b{font-size:13px}
        .floor h2{height:20px;margin-bottom:2px}.overview{gap:10px}
      }
      @media(min-width:850px){.canvas{width:min(900px,100%);margin:0 auto}}
    `;
  }
}

if (!customElements.get(ELEMENT_NAME)) customElements.define(ELEMENT_NAME, NikasRoomsV11);
