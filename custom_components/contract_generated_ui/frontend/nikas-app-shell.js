class NikaSAppShell extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
  }

  setConfig(config) {
    if (!config || !Array.isArray(config.items) || !config.items.length) {
      throw new Error("nikas-app-shell requires a non-empty items list");
    }
    this._config = config;
    this._render();
  }

  set hass(value) {
    this._hass = value;
  }

  getCardSize() {
    return 2;
  }

  _navigate(path) {
    if (!path || typeof path !== "string") return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  _render() {
    if (!this._config) return;

    const active = this._config.active;
    const items = this._config.items;
    const itemMarkup = items
      .map((item) => {
        const isActive = item.id === active;
        const current = isActive ? ' aria-current="page"' : "";
        const disabled = isActive ? " disabled" : "";
        const title = item.title || item.label || item.id;
        return `
          <button class="nav-item${isActive ? " active" : ""}"
                  data-path="${item.path}"
                  title="${title}"
                  aria-label="${title}"${current}${disabled}>
            <ha-icon icon="${item.icon}"></ha-icon>
            <span>${item.label}</span>
          </button>`;
      })
      .join("");

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
          min-height: calc(76px + env(safe-area-inset-bottom, 0px));
        }

        .shell {
          position: fixed;
          z-index: 20;
          left: 0;
          right: 0;
          bottom: 0;
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
          grid-template-columns: repeat(${items.length}, minmax(0, 1fr));
          gap: 4px;
        }

        .nav-item {
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

        .nav-item ha-icon {
          --mdc-icon-size: 25px;
          width: 25px;
          height: 25px;
        }

        .nav-item span {
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

        .nav-item.active {
          color: var(--primary-color, #03a9f4);
          background: var(--ha-color-primary-95, rgba(3, 169, 244, 0.12));
          cursor: default;
        }

        .nav-item:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4);
          outline-offset: 1px;
        }

        @media (min-width: 900px) {
          nav {
            width: min(70vw, 720px);
          }
        }
      </style>
      <div class="shell" role="navigation" aria-label="NikaS">
        <nav>${itemMarkup}</nav>
      </div>`;

    this.shadowRoot.querySelectorAll("button[data-path]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!button.disabled) this._navigate(button.dataset.path);
      });
    });
  }
}

if (!customElements.get("nikas-app-shell")) {
  customElements.define("nikas-app-shell", NikaSAppShell);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "nikas-app-shell")) {
  window.customCards.push({
    type: "nikas-app-shell",
    name: "NikaS App Shell",
    description: "Fixed bottom navigation for NikaS central dashboards",
    preview: false,
  });
}
