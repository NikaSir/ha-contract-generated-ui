const ROOT_PREFIX = "/dashboard-rooms/room-";
const ROOT_ID = "nikas-room-equipment-runtime";
const LEGACY_MARK = "nikas-room-equipment-legacy-hidden";
const HIDE_LABEL_PATTERN = /(?:^|[: _-])(rooms?|помещени[ея])?(?:[: _-])?(?:hide|hidden|exclude|скрыть|скрыто|не[_ -]?показывать)(?:$|[: _-])/i;
const ACTIVE_LABEL_ID = "v_ekspluatatsii";
const EXCLUDED_LABEL_IDS = new Set([
  "rezerv",
  "na_obsluzhivanii",
  "trebuet_zameny",
  "vyvedeno_iz_ekspluatatsii",
]);

const ROOM_NAMES = Object.freeze({
  bathroom: "Ванная",
  bedroom: "Спальня",
  wardrobe: "Гардероб",
  sasha: "У Саши",
  ilya: "У Ильи",
  stairs: "Лестница",
  corridor: "Коридор",
  hall: "Холл",
  boiler: "Котельная",
  kitchen: "Кухня",
  dining: "Столовая",
  living: "Гостиная",
  toilet: "Туалет",
  vestibule: "Тамбур",
  veranda: "Веранда",
  garage: "Гараж",
  attic: "Чердак",
  greenhouse: "Теплица",
});

let renderTimer = null;
let cache = null;
let cacheAt = 0;
let observer = null;
let mountedRoot = null;
const hiddenLegacyHosts = new Set();

function roomSlug(pathname = window.location.pathname) {
  if (!pathname.startsWith(ROOT_PREFIX)) return null;
  return pathname.slice(ROOT_PREFIX.length).split("/")[0] || null;
}

function norm(value) {
  return String(value || "").trim().toLocaleLowerCase("ru-RU").replace(/ё/g, "е").replace(/\s+/g, " ");
}

function normAreaName(value) {
  return norm(value).replace(/^\d+(?:[.,]\d+)?\s*(?:[-–—.:)]\s*)?/, "").trim();
}

function findRoomArea(areas, roomName) {
  const target = norm(roomName);
  return (areas || []).find((item) => {
    const rawName = norm(item?.name);
    return rawName === target || normAreaName(item?.name) === target;
  }) || null;
}

function getHass() {
  const home = document.querySelector("home-assistant");
  if (home?.hass) return home.hass;
  let found = null;
  walkRoots(document, (node) => {
    if (!found && node?.hass?.callWS) found = node.hass;
  });
  return found;
}

function walkRoots(start, visitor) {
  const stack = [start];
  const seen = new Set();
  while (stack.length) {
    const root = stack.pop();
    if (!root || seen.has(root)) continue;
    seen.add(root);
    for (const node of root.querySelectorAll?.("*") || []) {
      visitor(node);
      if (node.shadowRoot) stack.push(node.shadowRoot);
    }
  }
}

async function loadRegistries(hass) {
  const fresh = cache && Date.now() - cacheAt < 15000;
  if (fresh) return cache;
  const [areas, devices, entities, labels] = await Promise.all([
    hass.callWS({ type: "config/area_registry/list" }),
    hass.callWS({ type: "config/device_registry/list" }),
    hass.callWS({ type: "config/entity_registry/list" }),
    hass.callWS({ type: "config/label_registry/list" }).catch(() => []),
  ]);
  cache = { areas, devices, entities, labels };
  cacheAt = Date.now();
  return cache;
}

function labelIds(item) {
  const labels = item?.labels;
  if (!labels) return [];
  if (Array.isArray(labels)) return labels;
  if (labels instanceof Set) return [...labels];
  if (typeof labels === "object") return Object.keys(labels).filter((key) => labels[key]);
  return [];
}

function labelIdSet(item) {
  return new Set(labelIds(item));
}

function hasExcludedOperationalLabel(item) {
  const ids = labelIdSet(item);
  return [...EXCLUDED_LABEL_IDS].some((id) => ids.has(id));
}

function isOperationalItem(item) {
  const ids = labelIdSet(item);
  return ids.has(ACTIVE_LABEL_ID) && ![...EXCLUDED_LABEL_IDS].some((id) => ids.has(id));
}

function buildLabelMap(labels) {
  const map = new Map();
  for (const label of labels || []) {
    if (!label?.label_id) continue;
    map.set(label.label_id, label.name || label.label_id);
  }
  return map;
}

function hiddenByLabel(item, labelMap) {
  return labelIds(item).some((id) => HIDE_LABEL_PATTERN.test(labelMap.get(id) || id));
}

function effectiveAreaId(entity, deviceMap) {
  if (entity?.area_id) return entity.area_id;
  if (entity?.device_id) return deviceMap.get(entity.device_id)?.area_id || null;
  return null;
}

function deviceTitle(device) {
  return device?.name_by_user || device?.name || device?.model || "Устройство";
}

function entityTitle(entity, hass) {
  const state = hass.states?.[entity.entity_id];
  return entity.name || state?.attributes?.friendly_name || entity.original_name || entity.entity_id;
}

function collectRoomEquipment(registries, roomName, hass) {
  const labelMap = buildLabelMap(registries.labels);
  const area = findRoomArea(registries.areas, roomName);
  if (!area) return { area: null, items: [], labelMap };

  const deviceMap = new Map(registries.devices.map((device) => [device.id, device]));
  const roomDevices = registries.devices.filter((device) =>
    device.area_id === area.area_id
    && !device.disabled_by
    && isOperationalItem(device)
    && !hiddenByLabel(device, labelMap)
  );
  const byDevice = new Map();

  for (const device of roomDevices) {
    byDevice.set(device.id, {
      key: `device:${device.id}`,
      title: deviceTitle(device),
      device,
      entities: [],
      labelIds: new Set(labelIds(device)),
    });
  }

  const standalone = [];
  for (const entity of registries.entities) {
    if (entity.disabled_by || entity.hidden_by) continue;
    if (effectiveAreaId(entity, deviceMap) !== area.area_id) continue;
    if (hiddenByLabel(entity, labelMap) || hasExcludedOperationalLabel(entity)) continue;

    if (entity.device_id) {
      if (byDevice.has(entity.device_id)) {
        const row = byDevice.get(entity.device_id);
        row.entities.push(entity);
        for (const id of labelIds(entity)) row.labelIds.add(id);
      }
      // Entity-backed rows never bypass the device's operational status.
      continue;
    }

    // A standalone entity is equipment only when it is explicitly in operation.
    if (!isOperationalItem(entity)) continue;
    standalone.push({
      key: `entity:${entity.entity_id}`,
      title: entityTitle(entity, hass),
      device: null,
      entities: [entity],
      labelIds: new Set(labelIds(entity)),
    });
  }

  const items = [...byDevice.values(), ...standalone]
    .filter((item) => item.entities.length || item.device)
    .sort((a, b) => a.title.localeCompare(b.title, "ru"));
  return { area, items, labelMap };
}

function findMountHost() {
  let candidate = null;
  walkRoots(document, (node) => {
    if (candidate) return;
    if (node.localName === "hui-view" || node.localName === "hui-panel-view") candidate = node;
  });
  return candidate;
}

function restoreLegacyEquipmentSections() {
  for (const host of hiddenLegacyHosts) {
    if (!host?.style) continue;
    host.style.removeProperty("display");
    if (host.dataset) delete host.dataset[LEGACY_MARK];
  }
  hiddenLegacyHosts.clear();
}

function cleanupRuntime() {
  mountedRoot?.remove();
  mountedRoot = null;
  restoreLegacyEquipmentSections();
}

function hideLegacyEquipmentSection() {
  walkRoots(document, (node) => {
    if (node.dataset?.[LEGACY_MARK]) return;
    const config = node._config || node.config || {};
    const heading = config.heading || config.title || "";
    if (!/^оборудование$/i.test(String(heading).trim())) return;
    const host = node.closest?.("hui-section, hui-grid-section, section, ha-card") || node;
    host.style.setProperty("display", "none", "important");
    host.dataset[LEGACY_MARK] = "1";
    hiddenLegacyHosts.add(host);
  });
}

class NikasRoomEquipment extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._filter = "*";
    this._model = null;
  }

  set model(value) {
    this._model = value;
    this.render();
  }

  openMoreInfo(entityId) {
    this.dispatchEvent(new CustomEvent("hass-more-info", {
      bubbles: true,
      composed: true,
      detail: { entityId },
    }));
  }

  render() {
    const model = this._model;
    if (!model) return;
    const labels = new Map();
    for (const item of model.items) {
      for (const id of item.labelIds) labels.set(id, model.labelMap.get(id) || id);
    }
    const visible = this._filter === "*"
      ? model.items
      : model.items.filter((item) => item.labelIds.has(this._filter));

    const style = `
      :host{display:block;margin:16px 8px 96px;box-sizing:border-box;color:var(--primary-text-color)}
      .card{background:var(--card-background-color,var(--ha-card-background,#fff));border-radius:18px;padding:14px;box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.08));border:1px solid var(--divider-color,rgba(0,0,0,.1))}
      h2{font-size:20px;line-height:24px;margin:0 0 4px;font-weight:700}.sub{font-size:13px;color:var(--secondary-text-color);margin-bottom:12px}
      .filters{display:flex;gap:7px;overflow:auto;padding:2px 0 10px;scrollbar-width:none}.filters::-webkit-scrollbar{display:none}
      .filters button{white-space:nowrap;border:1px solid var(--divider-color,rgba(0,0,0,.12));background:transparent;color:var(--primary-text-color);border-radius:999px;padding:7px 11px;font:inherit;font-size:12px;font-weight:700}.filters button.active{background:var(--primary-color);color:var(--text-primary-color,#fff);border-color:var(--primary-color)}
      .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:10px}.device{border:1px solid var(--divider-color,rgba(0,0,0,.1));border-radius:15px;padding:11px;background:var(--secondary-background-color,rgba(0,0,0,.025))}.name{font-size:15px;font-weight:700;margin-bottom:7px}.labels{display:flex;gap:5px;flex-wrap:wrap;margin:0 0 7px}.label{font-size:10px;padding:3px 6px;border-radius:999px;background:var(--primary-background-color,rgba(0,0,0,.06));color:var(--secondary-text-color)}
      .entity{width:100%;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border:0;border-top:1px solid var(--divider-color,rgba(0,0,0,.08));background:transparent;color:inherit;padding:8px 0 0;margin-top:7px;text-align:left;font:inherit}.entity-name{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}.state{font-size:12px;font-weight:700;color:var(--secondary-text-color);white-space:nowrap}.empty{padding:10px 0;color:var(--secondary-text-color);font-size:13px}
    `;

    const wrapper = document.createElement("div");
    wrapper.className = "card";
    wrapper.innerHTML = `<h2>Оборудование</h2><div class="sub">${model.area?.name || "Помещение"} · ${model.items.length} поз.</div>`;

    const filters = document.createElement("div");
    filters.className = "filters";
    const choices = [["*", "Все"], ...[...labels.entries()].sort((a,b) => a[1].localeCompare(b[1], "ru"))];
    for (const [id, name] of choices) {
      const button = document.createElement("button");
      button.type = "button";
      button.classList.toggle("active", this._filter === id);
      button.textContent = name;
      button.onclick = () => { this._filter = id; this.render(); };
      filters.append(button);
    }
    wrapper.append(filters);

    const grid = document.createElement("div");
    grid.className = "grid";
    for (const item of visible) {
      const card = document.createElement("div");
      card.className = "device";
      const name = document.createElement("div");
      name.className = "name";
      name.textContent = item.title;
      card.append(name);

      if (item.labelIds.size) {
        const chips = document.createElement("div");
        chips.className = "labels";
        for (const id of item.labelIds) {
          const chip = document.createElement("span");
          chip.className = "label";
          chip.textContent = model.labelMap.get(id) || id;
          chips.append(chip);
        }
        card.append(chips);
      }

      for (const entity of item.entities) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "entity";
        const entityName = document.createElement("span");
        entityName.className = "entity-name";
        entityName.textContent = entityTitle(entity, model.hass);
        const state = document.createElement("span");
        state.className = "state";
        state.textContent = model.hass.states?.[entity.entity_id]?.state ?? "—";
        button.append(entityName, state);
        button.onclick = () => this.openMoreInfo(entity.entity_id);
        card.append(button);
      }
      grid.append(card);
    }
    if (!visible.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = "Нет оборудования для выбранного ярлыка.";
      grid.append(empty);
    }
    wrapper.append(grid);
    this.shadowRoot.innerHTML = `<style>${style}</style>`;
    this.shadowRoot.append(wrapper);
  }
}

if (!customElements.get("nikas-room-equipment")) customElements.define("nikas-room-equipment", NikasRoomEquipment);

async function sync() {
  renderTimer = null;
  const slug = roomSlug();
  if (!slug) {
    cleanupRuntime();
    return;
  }

  const roomName = ROOM_NAMES[slug];
  const hass = getHass();
  if (!roomName || !hass?.callWS) {
    cleanupRuntime();
    return;
  }

  try {
    const registries = await loadRegistries(hass);

    // Navigation may have changed while the registry requests were in flight.
    // Never mount room content into a different Home Assistant surface.
    if (roomSlug() !== slug || ROOM_NAMES[roomSlug()] !== roomName) {
      cleanupRuntime();
      return;
    }

    const mountHost = findMountHost();
    if (!mountHost) {
      cleanupRuntime();
      return;
    }

    const model = collectRoomEquipment(registries, roomName, hass);
    hideLegacyEquipmentSection();

    if (!mountedRoot?.isConnected) {
      mountedRoot = document.createElement("nikas-room-equipment");
      mountedRoot.id = ROOT_ID;
      mountHost.append(mountedRoot);
    }
    mountedRoot.model = { ...model, hass };
  } catch (err) {
    console.warn("[NikaS Rooms] Cannot build dynamic equipment list", err);
  }
}

function schedule() {
  if (renderTimer !== null) return;
  renderTimer = window.setTimeout(sync, 80);
}

window.addEventListener("location-changed", schedule);
window.addEventListener("popstate", schedule);
document.addEventListener("visibilitychange", () => { if (!document.hidden) schedule(); });
observer = new MutationObserver(schedule);
observer.observe(document.documentElement, { childList: true, subtree: true });
schedule();