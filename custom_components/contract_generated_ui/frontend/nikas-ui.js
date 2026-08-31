import "/contract_generated_ui/frontend/nikas-house-hero.js?build=b013";

const BOOTSTRAP_KEY = "__nikas_ui_bootstrapped_v1";
const BOOTSTRAP_VERSION = "b018";
const SHOULD_BOOTSTRAP = window[BOOTSTRAP_KEY] !== BOOTSTRAP_VERSION;
if (SHOULD_BOOTSTRAP) window[BOOTSTRAP_KEY] = BOOTSTRAP_VERSION;

const BAR_ID = "nikas-global-tabbar";
const HEADER_ID = "nikas-generated-subpanel-header";
const REGISTRY_URL = "/contract_generated_ui/navigation.json";
const SPECIALIZED_SOURCE_ROUTE_KEY = "nikas.specialized.source_route.v1";
const SPECIALIZED_SOURCE_ROUTE_AT_KEY = "nikas.specialized.source_route_at.v1";
const SPECIALIZED_PANEL_PATHS = new Set([
  "/dashboard-zont",
  "/starline",
  "/dashboard-s8-omni",
  "/dashboard-irrigation",
  "/dashboard-ups",
  "/dashboard-keenetic",
  "/dashboard-lider",
]);
const INTEGRATION_OWNED_PANEL_PREFIXES = ["/dashboard-house-v11", "/dashboard-infrastructure"];

const FALLBACK_ITEMS = [
  { id: "home", label: "Дом", icon: "mdi:home-outline", path: "/dashboard-house-v11/home" },
  { id: "rooms", label: "Помещения", icon: "mdi:floor-plan", path: "/dashboard-rooms/rooms" },
  { id: "actions", label: "Действия", icon: "mdi:lightning-bolt-outline", path: "/dashboard-actions/home" },
  { id: "infrastructure", label: "Инфра", icon: "mdi:server-network", path: "/dashboard-infrastructure/overview" },
];

const ACTIONS_HEADER_MODEL = {
  id: "global-actions",
  title: "Действия · v11.0",
  subtitle: "Быстрые команды · UI v0.37.6",
};

const ROOMS_ROOT_PATH = "/dashboard-rooms/rooms";
const ROOMS_UI_VERSION = "10.8.26";
const ROOM_VIEW_TITLES = Object.freeze({
  "/dashboard-rooms/room-bathroom": "Ванная",
  "/dashboard-rooms/room-bedroom": "Спальня",
  "/dashboard-rooms/room-wardrobe": "Гардероб",
  "/dashboard-rooms/room-sasha": "У Саши",
  "/dashboard-rooms/room-ilya": "У Ильи",
  "/dashboard-rooms/room-stairs": "Лестница",
  "/dashboard-rooms/room-corridor": "Коридор",
  "/dashboard-rooms/room-hall": "Холл",
  "/dashboard-rooms/room-boiler": "Котельная",
  "/dashboard-rooms/room-kitchen": "Кухня",
  "/dashboard-rooms/room-dining": "Столовая",
  "/dashboard-rooms/room-living": "Гостиная",
  "/dashboard-rooms/room-toilet": "Туалет",
  "/dashboard-rooms/room-vestibule": "Тамбур",
  "/dashboard-rooms/room-veranda": "Веранда",
  "/dashboard-rooms/room-garage": "Гараж",
  "/dashboard-rooms/room-attic": "Чердак",
  "/dashboard-rooms/room-greenhouse": "Теплица",
});

let navigationRegistry = null;
let syncFrame = null;
let chromeHostObserver = null;
let hiddenRoomsHeading = null;
let roomsHeadingRetryTimer = null;
let roomsHeadingRetryCount = 0;
let roomsOverviewHost = null;
let roomsOverviewOriginalMargin = "";
let roomsOverviewOriginalPriority = "";

function sourceBaseRoute(pathname) {
  if (pathname === "/dashboard-house-v11" || pathname.startsWith("/dashboard-house-v11/")) return "/dashboard-house-v11/home";
  if (pathname === "/dashboard-rooms" || pathname.startsWith("/dashboard-rooms/")) return "/dashboard-rooms/rooms";
  if (pathname === "/dashboard-actions" || pathname.startsWith("/dashboard-actions/")) return "/dashboard-actions/home";
  if (pathname.startsWith("/dashboard-infrastructure")) return "/dashboard-infrastructure/overview";
  return null;
}

function isSpecializedPanelRoute(path) {
  if (!path) return false;
  try {
    const target = new URL(String(path), window.location.origin);
    if (target.origin !== window.location.origin) return false;
    return [...SPECIALIZED_PANEL_PATHS].some(
      (root) => target.pathname === root || target.pathname.startsWith(`${root}/`)
    );
  } catch (_err) {
    return false;
  }
}

function sameOriginNavigationPath(path) {
  if (!path || typeof path !== "string" || !path.startsWith("/")) return null;
  try {
    const target = new URL(path, window.location.origin);
    if (target.origin !== window.location.origin) return null;
    return `${target.pathname}${target.search}${target.hash}`;
  } catch (_err) {
    return null;
  }
}

function clearSpecializedSourceRoute() {
  try {
    window.sessionStorage.removeItem(SPECIALIZED_SOURCE_ROUTE_KEY);
    window.sessionStorage.removeItem(SPECIALIZED_SOURCE_ROUTE_AT_KEY);
  } catch (_err) {
    // Storage is optional; the specialized panel retains its safe fallback.
  }
}

function rememberSpecializedSourceRoute(pathname, destination) {
  if (!isSpecializedPanelRoute(destination)) return false;
  const route = sourceBaseRoute(pathname);
  if (!route) return false;
  const timestamp = String(Date.now());
  try {
    window.sessionStorage.setItem(SPECIALIZED_SOURCE_ROUTE_KEY, route);
    window.sessionStorage.setItem(SPECIALIZED_SOURCE_ROUTE_AT_KEY, timestamp);
  } catch (_err) {
    // Never leave a partial route/timestamp pair behind.
    clearSpecializedSourceRoute();
    return false;
  }
  return true;
}

function navigateWithSourceHandoff(path) {
  const target = sameOriginNavigationPath(path);
  if (!target) return false;
  const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (current === target) return false;
  rememberSpecializedSourceRoute(window.location.pathname, target);
  window.history.pushState(null, "", target);
  window.dispatchEvent(new Event("location-changed"));
  return true;
}

window.NikasPanelNavigation = Object.freeze({
  contractVersion: "1.1",
  navigate: navigateWithSourceHandoff,
});

function fallbackSurface(pathname) {
  if (pathname.startsWith("/dashboard-house-v11")) return "home";
  if (pathname.startsWith("/dashboard-rooms")) return "rooms";
  if (pathname.startsWith("/dashboard-actions")) return "actions";
  if (pathname.startsWith("/dashboard-infrastructure")) return "infrastructure";
  return null;
}

function dashboardPrefix(path) {
  const parts = String(path || "").split("/").filter(Boolean);
  return parts.length ? `/${parts[0]}` : "";
}

function registrySubpanelModel(pathname) {
  const groups = navigationRegistry?.subpanels;
  if (!Array.isArray(groups)) return null;

  for (const group of groups) {
    if (!group || !Array.isArray(group.tabs) || !group.tabs.length) continue;
    const active = group.tabs.find(
      (tab) => pathname === tab.path || pathname.startsWith(`${tab.path}/`)
    );
    if (active) {
      return {
        mode: `subpanel:${group.id}`,
        active: active.id,
        items: group.tabs,
        group,
      };
    }
    if (!group.embedded && pathname === group.dashboard_path) {
      return {
        mode: `subpanel:${group.id}`,
        active: group.tabs[0].id,
        items: group.tabs,
        group,
      };
    }
  }
  return null;
}

function registryGlobalModel(pathname) {
  const tabs = navigationRegistry?.global_tabs;
  if (!Array.isArray(tabs) || !tabs.length) return null;

  let active = tabs.find((tab) => pathname === tab.path)?.id ?? null;
  if (!active) {
    const pathPrefix = dashboardPrefix(pathname);
    const tab = tabs.find((item) => dashboardPrefix(item.path) === pathPrefix);
    active = tab?.id ?? null;
  }
  if (!active) return null;
  return { mode: "global", active, items: tabs, group: null };
}

function fallbackGlobalModel(pathname) {
  const active = fallbackSurface(pathname);
  if (!active) return null;
  return { mode: "global-fallback", active, items: FALLBACK_ITEMS, group: null };
}

function navigationModel(pathname) {
  if (INTEGRATION_OWNED_PANEL_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  )) return null;
  return (
    registrySubpanelModel(pathname) ||
    registryGlobalModel(pathname) ||
    fallbackGlobalModel(pathname)
  );
}

function roomsHeaderModel(pathname) {
  if (!pathname.startsWith("/dashboard-rooms")) return null;
  const root = pathname === "/dashboard-rooms" || pathname === ROOMS_ROOT_PATH;
  return {
    id: root ? "global-rooms" : "global-room-detail",
    title: root ? "Помещения" : (ROOM_VIEW_TITLES[pathname] || "Помещение"),
    subtitle: root
      ? `Обзор · UI v${ROOMS_UI_VERSION}`
      : `Помещения · UI v${ROOMS_UI_VERSION}`,
    back_path: root ? null : ROOMS_ROOT_PATH,
  };
}

function walkOpenShadowRoots(start, visitor) {
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

function scheduleRoomsHeadingRetry() {
  if (roomsHeadingRetryTimer !== null || roomsHeadingRetryCount >= 24) return;
  roomsHeadingRetryCount += 1;
  roomsHeadingRetryTimer = window.setTimeout(() => {
    roomsHeadingRetryTimer = null;
    scheduleSync();
  }, 100);
}

function syncRoomsLegacyHeading(pathname) {
  if (pathname !== ROOMS_ROOT_PATH) {
    hiddenRoomsHeading = null;
    roomsHeadingRetryCount = 0;
    if (roomsHeadingRetryTimer !== null) window.clearTimeout(roomsHeadingRetryTimer);
    roomsHeadingRetryTimer = null;
    return;
  }
  if (hiddenRoomsHeading?.isConnected) return;

  let match = null;
  walkOpenShadowRoots(document, (node) => {
    if (match || node.localName !== "hui-heading-card") return;
    const heading = node._config?.heading || node.config?.heading || node.textContent || "";
    if (/^Помещения\s*·\s*v\d/i.test(String(heading).trim())) match = node;
  });
  if (!match) {
    scheduleRoomsHeadingRetry();
    return;
  }

  if (roomsHeadingRetryTimer !== null) window.clearTimeout(roomsHeadingRetryTimer);
  roomsHeadingRetryTimer = null;
  roomsHeadingRetryCount = 0;
  const host = match.closest?.("hui-section, hui-grid-section, section") || match;
  host.style.setProperty("display", "none", "important");
  hiddenRoomsHeading = host;
}

function clearRoomsOverviewFit() {
  if (!roomsOverviewHost?.style) return;
  if (roomsOverviewOriginalMargin) {
    roomsOverviewHost.style.setProperty(
      "margin-top",
      roomsOverviewOriginalMargin,
      roomsOverviewOriginalPriority,
    );
  } else {
    roomsOverviewHost.style.removeProperty("margin-top");
  }
  delete roomsOverviewHost.dataset.nikasRoomsLift;
  roomsOverviewHost = null;
  roomsOverviewOriginalMargin = "";
  roomsOverviewOriginalPriority = "";
}

function fitRoomsOverview(pathname) {
  if (pathname !== ROOMS_ROOT_PATH) {
    clearRoomsOverviewFit();
    return;
  }

  const header = document.getElementById(HEADER_ID);
  const headerBottom = header?.getBoundingClientRect?.().bottom;
  if (!Number.isFinite(headerBottom)) return;

  let first = null;
  let firstTop = Number.POSITIVE_INFINITY;
  walkOpenShadowRoots(document, (node) => {
    if (!["hui-section", "hui-grid-section"].includes(node.localName)) return;
    if (node.style?.display === "none") return;
    const rect = node.getBoundingClientRect?.();
    if (!rect || rect.height <= 0 || rect.top < headerBottom - 2) return;
    if (rect.top < firstTop) {
      first = node;
      firstTop = rect.top;
    }
  });
  if (!first) {
    scheduleRoomsHeadingRetry();
    return;
  }

  if (roomsOverviewHost !== first) {
    clearRoomsOverviewFit();
    roomsOverviewHost = first;
    roomsOverviewOriginalMargin = first.style.getPropertyValue("margin-top");
    roomsOverviewOriginalPriority = first.style.getPropertyPriority("margin-top");
  }

  const currentLift = Number(first.dataset.nikasRoomsLift || 0);
  const baseTop = first.getBoundingClientRect().top + currentLift;
  const desiredGap = 8;
  const lift = Math.max(0, Math.round(baseTop - headerBottom - desiredGap));
  first.dataset.nikasRoomsLift = String(lift);
  first.style.setProperty("margin-top", `${-lift}px`, "important");
}

function createBar(model) {
  const root = document.createElement("div");
  root.id = BAR_ID;
  root.setAttribute("role", "navigation");
  root.setAttribute("aria-label", "NikaS");

  const shadow = root.attachShadow({ mode: "open" });
  shadow.innerHTML = `
    <style>
      :host{position:fixed;z-index:20;left:0;right:0;bottom:0;display:block;pointer-events:none}
      .shell{pointer-events:auto;box-sizing:border-box;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-top:1px solid var(--divider-color,rgba(0,0,0,.12));box-shadow:0 -4px 18px rgba(0,0,0,.08)}
      nav{width:min(100%,720px);margin:0 auto;display:grid;grid-template-columns:repeat(var(--nikas-nav-columns,3),minmax(0,1fr));gap:4px}
      button{appearance:none;border:0;background:transparent;color:var(--secondary-text-color,#666);min-width:0;min-height:52px;padding:4px 2px;border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}
      button ha-icon{--mdc-icon-size:28px;width:28px;height:28px}
      button span{display:block;width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;font-size:12px;line-height:15px;font-weight:700}
      button.active{color:var(--primary-color,#03a9f4);background:var(--ha-color-primary-95,rgba(3,169,244,.12));cursor:default}
      button:focus-visible{outline:2px solid var(--primary-color,#03a9f4);outline-offset:1px}
      @media(max-width:430px){button{padding-left:2px;padding-right:2px}}
      @media(min-width:900px){nav{width:min(70vw,720px)}}
    </style>
    <div class="shell"><nav></nav></div>`;

  renderBar(root, model);
  return root;
}

function renderBar(root, model) {
  const nav = root.shadowRoot.querySelector("nav");
  nav.style.setProperty("--nikas-nav-columns", String(model.items.length));
  nav.replaceChildren();

  for (const item of model.items) {
    const button = document.createElement("button");
    const isActive = item.id === model.active;
    button.dataset.surface = item.id;
    button.type = "button";
    button.classList.toggle("active", isActive);
    button.disabled = isActive;
    if (isActive) button.setAttribute("aria-current", "page");

    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", item.icon);
    const label = document.createElement("span");
    label.textContent = item.label ?? item.title ?? item.id;
    button.append(icon, label);
    button.onclick = () => {
      if (!isActive) navigateWithSourceHandoff(item.path);
    };
    nav.appendChild(button);
  }
  root.dataset.mode = model.mode;
}

function createHeader(group) {
  const root = document.createElement("div");
  root.id = HEADER_ID;
  const shadow = root.attachShadow({ mode: "open" });
  shadow.innerHTML = `
    <style>
      :host{position:fixed;z-index:35;left:0;right:0;top:0;display:block;pointer-events:none}
      .shell{pointer-events:auto;display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;min-height:62px;padding:max(5px,env(safe-area-inset-top,0px)) max(8px,env(safe-area-inset-right,0px)) 5px max(8px,env(safe-area-inset-left,0px));box-sizing:border-box;background:var(--card-background-color,var(--ha-card-background,#fff));border-bottom:1px solid var(--divider-color,rgba(0,0,0,.12));box-shadow:0 2px 12px rgba(0,0,0,.08);color:var(--primary-text-color,#111)}
      button,.rail{width:44px;height:44px;min-width:44px;border:1px solid var(--divider-color,rgba(0,0,0,.12));border-radius:16px;background:var(--card-background-color,var(--ha-card-background,#fff));color:inherit;display:grid;place-items:center;padding:0;box-shadow:0 7px 20px rgba(23,45,76,.08)}
      button{cursor:pointer;-webkit-tap-highlight-color:transparent}
      button ha-icon{--mdc-icon-size:25px}
      .title{min-width:0;text-align:center;line-height:1.15}
      .title strong,.title span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
      .title strong{font-size:23px;font-weight:800}
      .title span{margin-top:3px;color:var(--secondary-text-color,#6b7280);font-size:14px;font-weight:560}
      .title.link{cursor:pointer;border-radius:12px}
      .title.link:focus-visible{outline:2px solid var(--primary-color,#03a9f4);outline-offset:3px}
      #refresh{color:var(--primary-color,#03a9f4)}
      @media(max-width:390px){.shell{grid-template-columns:48px minmax(0,1fr) 48px}.title strong{font-size:21px}.title span{font-size:13px}}
    </style>
    <div class="shell">
      <button id="menu" type="button" aria-label="Меню Home Assistant"><ha-icon icon="mdi:menu"></ha-icon></button>
      <div class="title"><strong></strong><span></span></div>
      <button id="refresh" type="button" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button>
    </div>`;
  shadow.getElementById("menu").onclick = () => {
    root.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
  };
  shadow.getElementById("refresh").onclick = () => window.location.reload();
  renderHeader(root, group);
  return root;
}

function renderHeader(root, group) {
  const shadow = root.shadowRoot;
  const title = shadow.querySelector(".title");
  shadow.querySelector(".title strong").textContent = group.title || "";
  shadow.querySelector(".title span").textContent = group.subtitle || group.parent?.title || "";

  const backPath = sameOriginNavigationPath(group.back_path);
  title.classList.toggle("link", Boolean(backPath));
  if (backPath) {
    title.setAttribute("role", "button");
    title.tabIndex = 0;
  } else {
    title.removeAttribute("role");
    title.removeAttribute("tabindex");
  }
  title.onclick = backPath ? () => navigateWithSourceHandoff(backPath) : null;
  title.onkeydown = backPath
    ? (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        navigateWithSourceHandoff(backPath);
      }
    : null;
  root.dataset.subpanel = group.id || "";
}

function syncBar(model) {
  let root = document.getElementById(BAR_ID);
  if (!model) {
    if (root) root.remove();
    return;
  }
  if (!root) {
    root = createBar(model);
    document.body.appendChild(root);
  } else {
    renderBar(root, model);
  }
}

function syncHeader(model, pathname) {
  let root = document.getElementById(HEADER_ID);
  const group =
    model?.group ||
    (model?.active === "actions" ? ACTIONS_HEADER_MODEL : null) ||
    (model?.active === "rooms" ? roomsHeaderModel(pathname) : null);
  if (!group) {
    if (root) root.remove();
    return;
  }
  if (!root) {
    root = createHeader(group);
    document.body.appendChild(root);
  } else {
    renderHeader(root, group);
  }
}

function syncChrome() {
  if (!document.body) return;
  const pathname = window.location.pathname;
  const model = navigationModel(pathname);
  syncBar(model);
  syncHeader(model, pathname);
  syncRoomsLegacyHeading(pathname);
  fitRoomsOverview(pathname);
}

function scheduleSync() {
  if (syncFrame !== null) return;
  syncFrame = window.requestAnimationFrame(() => {
    syncFrame = null;
    syncChrome();
  });
}

function observeChromeHost() {
  if (!document.body || chromeHostObserver || typeof MutationObserver !== "function") return;
  chromeHostObserver = new MutationObserver((records) => {
    const chromeRemoved = records.some((record) => [...record.removedNodes].some(
      (node) => node?.id === BAR_ID || node?.id === HEADER_ID
    ));
    const roomsContentAdded =
      window.location.pathname === ROOMS_ROOT_PATH &&
      !hiddenRoomsHeading?.isConnected &&
      records.some((record) => record.addedNodes.length > 0);
    if (chromeRemoved || roomsContentAdded) scheduleSync();
  });
  chromeHostObserver.observe(document.body, { childList: true, subtree: true });
}

async function loadNavigationRegistry() {
  try {
    const response = await fetch(REGISTRY_URL, {
      cache: "no-store",
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const candidate = await response.json();
    if (
      candidate?.api_version !== "nikas.home-assistant/navigation-registry/v1" ||
      !Array.isArray(candidate.global_tabs) ||
      !Array.isArray(candidate.subpanels)
    ) {
      throw new Error("invalid navigation registry");
    }
    navigationRegistry = candidate;
  } catch (err) {
    console.warn("NikaS navigation registry unavailable; using global fallback", err);
    navigationRegistry = null;
  }
  scheduleSync();
}

if (SHOULD_BOOTSTRAP) {
  window.addEventListener("location-changed", scheduleSync);
  window.addEventListener("popstate", scheduleSync);
  window.addEventListener("pageshow", scheduleSync);

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      () => {
        observeChromeHost();
        scheduleSync();
        loadNavigationRegistry();
      },
      { once: true }
    );
  } else {
    observeChromeHost();
    scheduleSync();
    loadNavigationRegistry();
  }

  // Legacy custom-card modules remain migration fallbacks only. Generated
  // subpanels use native Lovelace content with common Header/Bottom overlays.
  Promise.allSettled([
    import("./nikas-app-shell.js"),
    import("./nikas-infrastructure-summary.js"),
  ]);
}
