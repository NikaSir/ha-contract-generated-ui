const BOOTSTRAP_KEY = "__nikas_ui_bootstrapped_v1";
const SHOULD_BOOTSTRAP = !window[BOOTSTRAP_KEY];
if (SHOULD_BOOTSTRAP) window[BOOTSTRAP_KEY] = true;

const BAR_ID = "nikas-global-tabbar";
const REGISTRY_URL = "/contract_generated_ui/navigation.json";

const FALLBACK_ITEMS = [
  {
    id: "home",
    label: "Дом",
    icon: "mdi:home-outline",
    path: "/dashboard-house",
  },
  {
    id: "actions",
    label: "Действия",
    icon: "mdi:lightning-bolt-outline",
    path: "/dashboard-actions",
  },
  {
    id: "infrastructure",
    label: "Инфра",
    icon: "mdi:server-network",
    path: "/dashboard-infrastructure/overview",
  },
];

let navigationRegistry = null;

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
      };
    }
    if (!group.embedded && pathname === group.dashboard_path) {
      return {
        mode: `subpanel:${group.id}`,
        active: group.tabs[0].id,
        items: group.tabs,
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
  return {
    mode: "global",
    active,
    items: tabs,
  };
}

function fallbackGlobalModel(pathname) {
  const active = fallbackSurface(pathname);
  if (!active) return null;
  return {
    mode: "global-fallback",
    active,
    items: FALLBACK_ITEMS,
  };
}

function navigationModel(pathname) {
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
      :host {
        position: fixed;
        z-index: 20;
        left: 0;
        right: 0;
        bottom: 0;
        display: block;
        pointer-events: none;
      }
      .shell {
        pointer-events: auto;
        box-sizing: border-box;
        padding: 6px max(8px, env(safe-area-inset-right, 0px))
                 calc(6px + env(safe-area-inset-bottom, 0px))
                 max(8px, env(safe-area-inset-left, 0px));
        background: var(--card-background-color, var(--ha-card-background, #fff));
        border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
        box-shadow: 0 -4px 18px rgba(0, 0, 0, 0.08);
      }
      nav {
        width: min(100%, 720px);
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(var(--nikas-nav-columns, 3), minmax(0, 1fr));
        gap: 4px;
      }
      button {
        appearance: none;
        border: 0;
        background: transparent;
        color: var(--secondary-text-color, #666);
        min-width: 0;
        min-height: 62px;
        padding: 7px 4px 5px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font: inherit;
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
      }
      button ha-icon {
        --mdc-icon-size: 25px;
        width: 25px;
        height: 25px;
      }
      button span {
        display: block;
        width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: center;
        font-size: 12px;
        line-height: 16px;
        font-weight: 500;
      }
      button.active {
        color: var(--primary-color, #03a9f4);
        background: var(--ha-color-primary-95, rgba(3, 169, 244, 0.12));
        cursor: default;
      }
      button:focus-visible {
        outline: 2px solid var(--primary-color, #03a9f4);
        outline-offset: 1px;
      }
      @media (max-width: 430px) {
        button {
          min-height: 60px;
          padding-left: 2px;
          padding-right: 2px;
        }
        button span {
          font-size: 11.5px;
        }
      }
      @media (min-width: 900px) {
        nav { width: min(70vw, 720px); }
      }
    </style>
    <div class="shell">
      <nav></nav>
    </div>`;

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
    const label = item.label ?? item.title ?? item.id;
    button.innerHTML = `<ha-icon icon="${item.icon}"></ha-icon><span>${label}</span>`;
    button.onclick = () => {
      if (!isActive) navigate(item.path);
    };
    nav.appendChild(button);
  }
  root.dataset.mode = model.mode;
}

function syncBar() {
  if (!document.body) return;
  const model = navigationModel(window.location.pathname);
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

function scheduleSync() {
  window.requestAnimationFrame(syncBar);
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
        scheduleSync();
        loadNavigationRegistry();
      },
      { once: true }
    );
  } else {
    scheduleSync();
    loadNavigationRegistry();
  }

  // Legacy custom-card modules remain a migration fallback only. Generated
  // subpanels use native Home Assistant views plus this data-driven tab overlay.
  Promise.allSettled([
    import("./nikas-app-shell.js"),
    import("./nikas-infrastructure-summary.js"),
  ]);
}
