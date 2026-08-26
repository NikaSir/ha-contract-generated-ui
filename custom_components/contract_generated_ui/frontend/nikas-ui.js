import "/contract_generated_ui/frontend/nikas-house-hero.js?build=b011";

const BOOTSTRAP_KEY = "__nikas_ui_bootstrapped_v1";
const BOOTSTRAP_VERSION = "b010";
const SHOULD_BOOTSTRAP = window[BOOTSTRAP_KEY] !== BOOTSTRAP_VERSION;
if (SHOULD_BOOTSTRAP) window[BOOTSTRAP_KEY] = BOOTSTRAP_VERSION;

const BAR_ID = "nikas-global-tabbar";
const HEADER_ID = "nikas-generated-subpanel-header";
const REGISTRY_URL = "/contract_generated_ui/navigation.json";
const INTEGRATION_OWNED_PANEL_PREFIXES = ["/dashboard-house-v11", "/dashboard-infrastructure"];

const FALLBACK_ITEMS = [
  { id: "home", label: "Дом", icon: "mdi:home-outline", path: "/dashboard-house" },
  { id: "actions", label: "Действия", icon: "mdi:lightning-bolt-outline", path: "/dashboard-actions" },
  { id: "infrastructure", label: "Инфра", icon: "mdi:server-network", path: "/dashboard-infrastructure/overview" },
];

const ACTIONS_HEADER_MODEL = {
  id: "global-actions",
  title: "Действия · v11.0",
  subtitle: "Быстрые команды · UI v0.37.3",
};

let navigationRegistry = null;
let syncFrame = null;
let chromeHostObserver = null;

function navigate(path) {
  if (!path || window.location.pathname === path) return;
  window.history.pushState(null, "", path);
  window.dispatchEvent(new Event("location-changed"));
}

function fallbackSurface(pathname) {
  if (pathname.startsWith("/dashboard-house")) return "home";
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
      if (!isActive) navigate(item.path);
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
  shadow.querySelector(".title strong").textContent = group.title || "";
  shadow.querySelector(".title span").textContent = group.subtitle || group.parent?.title || "";
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

function syncHeader(model) {
  let root = document.getElementById(HEADER_ID);
  const group = model?.group || (model?.active === "actions" ? ACTIONS_HEADER_MODEL : null);
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
  const model = navigationModel(window.location.pathname);
  syncBar(model);
  syncHeader(model);
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
    if (chromeRemoved) scheduleSync();
  });
  chromeHostObserver.observe(document.body, { childList: true });
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
