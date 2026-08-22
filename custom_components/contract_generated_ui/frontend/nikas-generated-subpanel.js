// Shared generated application-panel host for Contract Generated UI.
// One self-contained bundle serves ZONT, StarLine and future manifest-defined panels.

(() => {
  const ELEMENT_NAME = "nikas-generated-subpanel";
  if (customElements.get(ELEMENT_NAME)) return;

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function navigate(path) {
    if (!path) return;
    window.history.pushState(null, "", path);
    window.dispatchEvent(new Event("location-changed"));
  }

  class NikasGeneratedSubpanel extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._hass = null;
      this._panel = null;
      this._active = null;
      this._renderQueued = false;
      this._onHashChange = () => {
        this._active = this._tabFromLocation();
        this._queueRender();
      };
    }

    set hass(value) {
      this._hass = value;
      this._queueRender();
    }

    get hass() {
      return this._hass;
    }

    set panel(value) {
      this._panel = value;
      this._active = this._tabFromLocation();
      this._queueRender();
    }

    get panel() {
      return this._panel;
    }

    connectedCallback() {
      window.addEventListener("hashchange", this._onHashChange);
      this._active = this._tabFromLocation();
      this._queueRender();
    }

    disconnectedCallback() {
      window.removeEventListener("hashchange", this._onHashChange);
    }

    _config() {
      return this._panel?.config || this._panel || {};
    }

    _tabs() {
      const tabs = this._config().tabs;
      return Array.isArray(tabs) ? tabs : [];
    }

    _tabFromLocation() {
      const tabs = this._tabs();
      const hash = window.location.hash.replace(/^#/, "");
      if (hash && tabs.some((tab) => tab.id === hash)) return hash;
      return tabs[0]?.id || null;
    }

    _activeTab() {
      const tabs = this._tabs();
      return tabs.find((tab) => tab.id === this._active) || tabs[0] || null;
    }

    _selectTab(id) {
      if (!id || id === this._active) return;
      this._active = id;
      window.history.replaceState(null, "", `${window.location.pathname}#${encodeURIComponent(id)}`);
      this._queueRender();
    }

    _back() {
      navigate(this._config().parent?.path || "/dashboard-house");
    }

    _refresh() {
      this._queueRender();
    }

    _queueRender() {
      if (this._renderQueued) return;
      this._renderQueued = true;
      requestAnimationFrame(() => {
        this._renderQueued = false;
        this._render();
      });
    }

    _render() {
      const config = this._config();
      const tabs = this._tabs();
      const active = this._activeTab();
      if (!config.title || !tabs.length || !active) {
        this.shadowRoot.innerHTML = `<div style="padding:24px;font:16px sans-serif">Панель ещё не настроена.</div>`;
        return;
      }

      const navButtons = tabs
        .map((tab) => {
          const selected = tab.id === active.id;
          return `
            <button class="tab ${selected ? "active" : ""}" data-tab="${escapeHtml(tab.id)}" ${selected ? "disabled" : ""} aria-current="${selected ? "page" : "false"}">
              <ha-icon icon="${escapeHtml(tab.icon || "mdi:view-dashboard-outline")}"></ha-icon>
              <span>${escapeHtml(tab.label || tab.id)}</span>
            </button>`;
        })
        .join("");

      this.shadowRoot.innerHTML = `
        <style>
          :host{
            display:block;
            min-height:100vh;
            background:var(--primary-background-color,#f6f7f9);
            color:var(--primary-text-color,#111827);
            font-family:var(--paper-font-body1_-_font-family,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif);
          }
          *{box-sizing:border-box}
          .app{min-height:100vh;padding-bottom:calc(82px + env(safe-area-inset-bottom,0px))}
          .header{
            position:sticky;top:0;z-index:10;
            display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;
            min-height:70px;
            padding:max(6px,env(safe-area-inset-top,0px)) max(10px,env(safe-area-inset-right,0px)) 6px max(10px,env(safe-area-inset-left,0px));
            background:var(--card-background-color,var(--ha-card-background,#fff));
            border-bottom:1px solid var(--divider-color,rgba(127,127,127,.18));
          }
          .rail{
            width:48px;height:48px;border:0;border-radius:16px;
            display:grid;place-items:center;
            background:var(--secondary-background-color,rgba(127,127,127,.08));
            color:var(--primary-text-color,#111827);cursor:pointer;
            -webkit-tap-highlight-color:transparent;
          }
          .rail ha-icon{--mdc-icon-size:26px}
          .heading{min-width:0;text-align:center;line-height:1.12}
          .heading strong,.heading span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
          .heading strong{font-size:21px;font-weight:780;letter-spacing:-.02em}
          .heading span{margin-top:3px;font-size:12px;font-weight:600;color:var(--secondary-text-color,#6b7280)}
          main{width:min(100%,1120px);margin:0 auto;padding:18px 16px 28px}
          .hero,.card{
            border:1px solid var(--divider-color,rgba(127,127,127,.22));
            background:var(--card-background-color,var(--ha-card-background,#fff));
            border-radius:24px;
          }
          .hero{padding:22px;position:relative;overflow:hidden}
          .hero::after{
            content:"";position:absolute;right:-46px;top:-54px;width:150px;height:150px;border-radius:50%;
            background:color-mix(in srgb,var(--primary-color,#03a9f4) 12%,transparent);
          }
          .eyebrow{font-size:11px;letter-spacing:.13em;font-weight:800;color:var(--secondary-text-color,#6b7280)}
          .hero-line{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-top:7px}
          .hero h1{margin:0;font-size:34px;line-height:1.04;letter-spacing:-.035em;font-weight:820}
          .hero p{margin:8px 0 0;color:var(--secondary-text-color,#6b7280);font-size:15px;line-height:1.4}
          .badge{position:relative;z-index:1;display:inline-flex;align-items:center;gap:7px;padding:9px 12px;border-radius:999px;background:color-mix(in srgb,var(--success-color,#43a047) 12%,var(--card-background-color,#fff));color:var(--success-color,#43a047);font-weight:750;white-space:nowrap}
          .badge ha-icon{--mdc-icon-size:19px}
          .card{margin-top:14px;padding:20px}
          .card-title{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:780}
          .card-title ha-icon{color:var(--primary-color,#03a9f4);--mdc-icon-size:25px}
          .placeholder{margin-top:14px;padding:16px;border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.08));font-size:15px;line-height:1.5;color:var(--primary-text-color,#111827)}
          .meta{margin-top:12px;color:var(--secondary-text-color,#6b7280);font-size:12px;line-height:1.45}
          .bottom{
            position:fixed;z-index:20;left:0;right:0;bottom:0;
            padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));
            background:var(--card-background-color,var(--ha-card-background,#fff));
            border-top:1px solid var(--divider-color,rgba(127,127,127,.18));
            box-shadow:0 -4px 18px rgba(0,0,0,.08);
          }
          nav{width:min(100%,720px);margin:0 auto;display:grid;grid-template-columns:repeat(${tabs.length},minmax(0,1fr));gap:4px}
          .tab{
            appearance:none;border:0;background:transparent;color:var(--secondary-text-color,#6b7280);
            min-width:0;min-height:60px;padding:7px 2px 5px;border-radius:16px;
            display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
            font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent;
          }
          .tab ha-icon{--mdc-icon-size:24px;width:24px;height:24px}
          .tab span{width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;font-size:11.5px;line-height:15px;font-weight:600}
          .tab.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);cursor:default}
          @media(max-width:390px){
            .header{grid-template-columns:48px minmax(0,1fr) 48px}.rail{width:44px;height:44px;border-radius:14px}
            .heading strong{font-size:19px}.hero h1{font-size:30px}.hero{padding:19px}.card{padding:18px}
            .badge{font-size:13px;padding:8px 10px}
          }
          @media(min-width:900px){main{padding-top:22px}.hero h1{font-size:38px}}
        </style>
        <div class="app">
          <header class="header">
            <button class="rail" id="back" type="button" aria-label="Назад"><ha-icon icon="mdi:arrow-left"></ha-icon></button>
            <div class="heading"><strong>${escapeHtml(config.title)}</strong><span>${escapeHtml(config.subtitle || config.parent?.title || "")}</span></div>
            <button class="rail" id="refresh" type="button" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button>
          </header>
          <main>
            <section class="hero">
              <div class="eyebrow">СОСТОЯНИЕ</div>
              <div class="hero-line">
                <div>
                  <h1>Каркас готов</h1>
                  <p>Подсистема подключена к единому шаблону Contract Generated UI.</p>
                </div>
                <div class="badge"><ha-icon icon="mdi:check-circle-outline"></ha-icon><span>Готово</span></div>
              </div>
            </section>
            <section class="card">
              <div class="card-title"><ha-icon icon="${escapeHtml(active.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${escapeHtml(active.label || active.id)}</span></div>
              <div class="placeholder">${escapeHtml(active.placeholder || "Раздел готов к наполнению.")}</div>
              <div class="meta">Навигация, заголовок, кнопка «Назад» и нижние вкладки формируются централизованно. Предметные сущности будут подключены отдельным контрактом.</div>
            </section>
          </main>
          <div class="bottom"><nav>${navButtons}</nav></div>
        </div>`;

      this.shadowRoot.getElementById("back").onclick = () => this._back();
      this.shadowRoot.getElementById("refresh").onclick = () => this._refresh();
      for (const button of this.shadowRoot.querySelectorAll("button[data-tab]")) {
        button.onclick = () => this._selectTab(button.dataset.tab);
      }
    }
  }

  customElements.define(ELEMENT_NAME, NikasGeneratedSubpanel);
})();
