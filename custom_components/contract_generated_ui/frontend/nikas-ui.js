const BAR_ID = "nikas-global-tabbar";

const BASE_ITEMS = [
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

function surfaceForPath(pathname) {
  if (pathname.startsWith("/dashboard-house")) return "home";
  if (pathname.startsWith("/dashboard-actions")) return "actions";
  if (pathname.startsWith("/dashboard-infrastructure")) return "infrastructure";
  return null;
}

function routesForPath(pathname) {
  const preview =
    pathname.startsWith("/dashboard-house-preview") ||
    pathname.startsWith("/dashboard-actions-preview");

  return preview
    ? {
        home: "/dashboard-house-preview/home",
        actions: "/dashboard-actions-preview/home",
        infrastructure: "/dashboard-infrastructure/overview",
      }
    : Object.fromEntries(BASE_ITEMS.map((item) => [item.id, item.path]));
}

function navigate(path) {
  if (!path || window.location.pathname === path) return;
  window.history.pushState(null, "", path);
  window.dispatchEvent(new Event("location-changed"));
}

function createBar(active, routes) {
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
        grid-template-columns: repeat(3, minmax(0, 1fr));
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
      @media (min-width: 900px) {
        nav { width: min(70vw, 720px); }
      }
    </style>
    <div class="shell">
      <nav></nav>
    </div>`;

  const nav = shadow.querySelector("nav");
  for (const item of BASE_ITEMS) {
    const button = document.createElement("button");
    button.dataset.surface = item.id;
    button.type = "button";
    button.innerHTML = `<ha-icon icon="${item.icon}"></ha-icon><span>${item.label}</span>`;
    nav.appendChild(button);
  }

  updateBar(root, active, routes);
  return root;
}

function updateBar(root, active, routes) {
  root.shadowRoot.querySelectorAll("button[data-surface]").forEach((button) => {
    const surface = button.dataset.surface;
    const isActive = surface === active;
    button.classList.toggle("active", isActive);
    button.disabled = isActive;
    if (isActive) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
    button.onclick = () => {
      if (!isActive) navigate(routes[surface]);
    };
  });
}

function syncBar() {
  if (!document.body) return;
  const pathname = window.location.pathname;
  const active = surfaceForPath(pathname);
  let root = document.getElementById(BAR_ID);

  if (!active) {
    if (root) root.remove();
    return;
  }

  const routes = routesForPath(pathname);
  if (!root) {
    root = createBar(active, routes);
    document.body.appendChild(root);
  } else {
    updateBar(root, active, routes);
  }
}

function scheduleSync() {
  window.requestAnimationFrame(syncBar);
}

window.addEventListener("location-changed", scheduleSync);
window.addEventListener("popstate", scheduleSync);
window.addEventListener("pageshow", scheduleSync);

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", scheduleSync, { once: true });
} else {
  scheduleSync();
}

// Keep old card modules available for already-generated dashboards during the
// migration to native cards. Their success or failure no longer affects the
// native v0.11+ dashboard or the global bottom navigation above.
Promise.allSettled([
  import("./nikas-app-shell.js"),
  import("./nikas-infrastructure-summary.js"),
]);
