const EQUIPMENT_ID = "nikas-room-equipment-runtime";
const LIVE_ID = "nikas-room-live-sections-runtime";
const ROOMS_ROOT = "/dashboard-rooms/rooms";
const ROOM_PREFIX = "/dashboard-rooms/room-";

let stateUnsubscribe = null;
let stateSubscribing = false;
let refreshTimer = null;
let lastRouteKey = "";
let overviewHost = null;
let overviewOriginalMargin = "";
let overviewOriginalPriority = "";

function diagnostics() {
  return new URLSearchParams(window.location.search).get("view") === "diagnostics";
}

function isRoomDetail() {
  return window.location.pathname.startsWith(ROOM_PREFIX);
}

function walk(root, fn) {
  const stack = [root];
  const seen = new Set();
  while (stack.length) {
    const current = stack.pop();
    if (!current || seen.has(current)) continue;
    seen.add(current);
    for (const node of current.querySelectorAll?.("*") || []) {
      fn(node);
      if (node.shadowRoot) stack.push(node.shadowRoot);
    }
  }
}

function findById(id) {
  let found = null;
  walk(document, (node) => {
    if (!found && node.id === id) found = node;
  });
  return found;
}

function getHass() {
  const home = document.querySelector("home-assistant");
  if (home?.hass) return home.hass;
  let found = null;
  walk(document, (node) => {
    if (!found && node?.hass?.callWS) found = node.hass;
  });
  return found;
}

function clearOverviewFit() {
  if (!overviewHost?.style) return;
  if (overviewOriginalMargin) {
    overviewHost.style.setProperty("margin-top", overviewOriginalMargin, overviewOriginalPriority);
  } else {
    overviewHost.style.removeProperty("margin-top");
  }
  delete overviewHost.dataset.nikasRoomsLift;
  overviewHost = null;
  overviewOriginalMargin = "";
  overviewOriginalPriority = "";
}

function fitRoomsOverview() {
  if (window.location.pathname !== ROOMS_ROOT) {
    clearOverviewFit();
    return;
  }

  const header = document.getElementById("nikas-generated-subpanel-header");
  const headerBottom = header?.getBoundingClientRect?.().bottom;
  if (!Number.isFinite(headerBottom)) return;

  let first = null;
  let firstTop = Number.POSITIVE_INFINITY;
  walk(document, (node) => {
    if (!["hui-section", "hui-grid-section"].includes(node.localName)) return;
    if (node.style?.display === "none") return;
    const rect = node.getBoundingClientRect?.();
    if (!rect || rect.height <= 0 || rect.top < headerBottom - 2) return;
    if (rect.top < firstTop) {
      first = node;
      firstTop = rect.top;
    }
  });
  if (!first) return;

  if (overviewHost !== first) {
    clearOverviewFit();
    overviewHost = first;
    overviewOriginalMargin = first.style.getPropertyValue("margin-top");
    overviewOriginalPriority = first.style.getPropertyPriority("margin-top");
  }

  const currentLift = Number(first.dataset.nikasRoomsLift || 0);
  const baseTop = first.getBoundingClientRect().top + currentLift;
  const desiredGap = 12;
  const lift = Math.max(0, Math.round(baseTop - headerBottom - desiredGap));
  first.dataset.nikasRoomsLift = String(lift);
  first.style.setProperty("margin-top", `${-lift}px`, "important");
}

function visibleLiveEntityIds() {
  const live = findById(LIVE_ID);
  const ids = new Set();
  for (const button of live?.shadowRoot?.querySelectorAll?.("button[data-id]") || []) {
    if (button.dataset.id) ids.add(button.dataset.id);
  }
  return ids;
}

function scheduleStateRefresh() {
  if (refreshTimer !== null) return;
  refreshTimer = window.setTimeout(() => {
    refreshTimer = null;
    if (!isRoomDetail()) return;
    window.dispatchEvent(new Event("location-changed"));
  }, 90);
}

async function ensureStateSubscription() {
  if (stateUnsubscribe || stateSubscribing) return;
  const hass = getHass();
  if (!hass?.connection?.subscribeEvents) return;
  stateSubscribing = true;
  try {
    stateUnsubscribe = await hass.connection.subscribeEvents((event) => {
      if (!isRoomDetail()) return;
      const entityId = event?.data?.entity_id;
      if (!entityId) return;
      if (diagnostics() || visibleLiveEntityIds().has(entityId)) scheduleStateRefresh();
    }, "state_changed");
  } catch (err) {
    console.warn("[NikaS Rooms] Cannot subscribe to state changes", err);
  } finally {
    stateSubscribing = false;
  }
}

function scheduleWarmup(routeKey) {
  if (routeKey === lastRouteKey) return;
  lastRouteKey = routeKey;
  if (!isRoomDetail()) return;
  for (const delay of [350, 1200, 3000]) {
    window.setTimeout(() => {
      if (`${window.location.pathname}${window.location.search}` === routeKey) scheduleStateRefresh();
    }, delay);
  }
}

function sync() {
  const routeKey = `${window.location.pathname}${window.location.search}`;
  scheduleWarmup(routeKey);
  fitRoomsOverview();
  ensureStateSubscription();

  if (!isRoomDetail()) return;
  const showDiagnostics = diagnostics();
  const equipment = findById(EQUIPMENT_ID);
  const live = findById(LIVE_ID);

  if (equipment) {
    equipment.style.setProperty("display", showDiagnostics ? "block" : "none", "important");
  }
  if (live) live.toggleAttribute("data-diagnostics", showDiagnostics);

  // Diagnostics is a real second-level view. Keep the complete equipment block,
  // but place it directly after the diagnostics submenu instead of leaving it
  // at the legacy Lovelace mount position lower on the page.
  if (showDiagnostics && live && equipment && live.parentNode === equipment.parentNode && live.nextSibling !== equipment) {
    live.after(equipment);
  }
}

window.addEventListener("location-changed", () => window.setTimeout(sync, 0));
window.addEventListener("popstate", () => window.setTimeout(sync, 0));
window.addEventListener("pageshow", () => window.setTimeout(sync, 0));
new MutationObserver(sync).observe(document.documentElement, { childList: true, subtree: true });
sync();
