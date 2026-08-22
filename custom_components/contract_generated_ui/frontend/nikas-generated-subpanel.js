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

  function domainOf(entityId) {
    return String(entityId || "").split(".", 1)[0];
  }

  function normalizedText(...values) {
    return values
      .filter((value) => value !== null && value !== undefined)
      .map((value) => String(value).toLocaleLowerCase())
      .join(" ");
  }

  function matchesAny(text, values) {
    if (!Array.isArray(values) || !values.length) return false;
    return values.some((value) => text.includes(String(value).toLocaleLowerCase()));
  }

  class NikasGeneratedSubpanel extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._hass = null;
      this._panel = null;
      this._active = null;
      this._renderQueued = false;
      this._registry = null;
      this._registryError = null;
      this._registryPromise = null;
      this._registryPlatformsKey = "";
      this._onHashChange = () => {
        this._active = this._tabFromLocation();
        this._queueRender();
      };
    }

    set hass(value) {
      this._hass = value;
      this._ensureRegistry();
      this._queueRender();
    }

    get hass() {
      return this._hass;
    }

    set panel(value) {
      this._panel = value;
      this._active = this._tabFromLocation();
      this._ensureRegistry(true);
      this._queueRender();
    }

    get panel() {
      return this._panel;
    }

    connectedCallback() {
      window.addEventListener("hashchange", this._onHashChange);
      this._active = this._tabFromLocation();
      this._ensureRegistry();
      this._queueRender();
    }

    disconnectedCallback() {
      window.removeEventListener("hashchange", this._onHashChange);
    }

    _config() {
      return this._panel?.config || this._panel || {};
    }

    _source() {
      return this._config().source || null;
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
      this._ensureRegistry(true);
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

    _sourceKey() {
      const source = this._source();
      const platforms = Array.isArray(source?.platforms) ? source.platforms : [];
      return JSON.stringify(platforms.slice().sort());
    }

    _ensureRegistry(force = false) {
      const source = this._source();
      if (!source || source.kind !== "entity_registry" || !this._hass?.callWS) return;

      const sourceKey = this._sourceKey();
      if (!force && this._registry && this._registryPlatformsKey === sourceKey) return;
      if (!force && this._registryPromise && this._registryPlatformsKey === sourceKey) return;

      this._registryPlatformsKey = sourceKey;
      this._registryError = null;
      this._registry = null;
      this._registryPromise = this._hass
        .callWS({ type: "config/entity_registry/list" })
        .then((entries) => {
          this._registry = Array.isArray(entries) ? entries : [];
          this._registryError = null;
        })
        .catch((error) => {
          this._registry = [];
          this._registryError = error instanceof Error ? error.message : String(error);
        })
        .finally(() => {
          this._registryPromise = null;
          this._queueRender();
        });
    }

    _integrationEntries() {
      const source = this._source();
      const platforms = new Set(Array.isArray(source?.platforms) ? source.platforms : []);
      if (!platforms.size || !Array.isArray(this._registry)) return [];
      const includeDisabled = source?.include_disabled === true;
      return this._registry
        .filter((entry) => platforms.has(entry.platform))
        .filter((entry) => includeDisabled || !entry.disabled_by)
        .filter((entry) => this._hass?.states?.[entry.entity_id])
        .map((entry) => ({ entry, state: this._hass.states[entry.entity_id] }));
    }

    _entryText(item) {
      return normalizedText(
        item.entry.entity_id,
        item.entry.name,
        item.entry.original_name,
        item.state?.attributes?.friendly_name,
        item.state?.attributes?.device_class,
      );
    }

    _filterForView(items, view) {
      const rule = view?.readonly;
      if (!rule) return [];

      let result = items.slice();
      const domains = Array.isArray(rule.domains) ? new Set(rule.domains) : null;
      if (domains?.size) {
        result = result.filter((item) => domains.has(domainOf(item.entry.entity_id)));
      }

      if (Array.isArray(rule.include_keywords) && rule.include_keywords.length) {
        const matched = result.filter((item) => matchesAny(this._entryText(item), rule.include_keywords));
        if (matched.length) result = matched;
      }

      if (Array.isArray(rule.exclude_keywords) && rule.exclude_keywords.length) {
        result = result.filter((item) => !matchesAny(this._entryText(item), rule.exclude_keywords));
      }

      if (rule.unavailable_only === true) {
        result = result.filter((item) => ["unknown", "unavailable"].includes(item.state?.state));
      }

      const priorities = Array.isArray(rule.priority_keywords) ? rule.priority_keywords : [];
      result.sort((left, right) => {
        const leftText = this._entryText(left);
        const rightText = this._entryText(right);
        const leftPriority = priorities.findIndex((value) => leftText.includes(String(value).toLocaleLowerCase()));
        const rightPriority = priorities.findIndex((value) => rightText.includes(String(value).toLocaleLowerCase()));
        const leftScore = leftPriority < 0 ? 999 : leftPriority;
        const rightScore = rightPriority < 0 ? 999 : rightPriority;
        if (leftScore !== rightScore) return leftScore - rightScore;
        return this._friendlyName(left).localeCompare(this._friendlyName(right), "ru");
      });

      const limit = Number(rule.limit || 0);
      if (Number.isFinite(limit) && limit > 0) result = result.slice(0, limit);
      return result;
    }

    _friendlyName(item) {
      return (
        item.state?.attributes?.friendly_name ||
        item.entry.name ||
        item.entry.original_name ||
        item.entry.entity_id
      );
    }

    _formatState(item) {
      if (typeof this._hass?.formatEntityState === "function") {
        try {
          return this._hass.formatEntityState(item.state);
        } catch (_error) {
          // Fall through to factual raw state.
        }
      }
      const unit = item.state?.attributes?.unit_of_measurement;
      return `${item.state?.state ?? "—"}${unit ? ` ${unit}` : ""}`;
    }

    _secondaryText(item) {
      const domain = domainOf(item.entry.entity_id);
      const attrs = item.state?.attributes || {};
      if (domain === "climate") {
        const parts = [];
        if (attrs.current_temperature !== undefined) parts.push(`Сейчас ${attrs.current_temperature}°`);
        if (attrs.temperature !== undefined) parts.push(`Уставка ${attrs.temperature}°`);
        return parts.join(" · ");
      }
      if (domain === "device_tracker" && attrs.latitude !== undefined && attrs.longitude !== undefined) {
        return `GPS ${Number(attrs.latitude).toFixed(4)}, ${Number(attrs.longitude).toFixed(4)}`;
      }
      return item.entry.entity_id;
    }

    _iconFor(item) {
      return (
        item.state?.attributes?.icon ||
        item.entry.icon ||
        ({
          binary_sensor: "mdi:checkbox-marked-circle-outline",
          climate: "mdi:thermostat",
          device_tracker: "mdi:map-marker-outline",
          lock: "mdi:lock-outline",
          sensor: "mdi:gauge",
          switch: "mdi:toggle-switch-outline",
        }[domainOf(item.entry.entity_id)] || "mdi:information-outline")
      );
    }

    _entityRows(items) {
      if (!items.length) return "";
      return `
        <div class="entity-grid">
          ${items
            .map((item) => {
              const unavailable = ["unknown", "unavailable"].includes(item.state?.state);
              return `
                <div class="entity ${unavailable ? "unreliable" : ""}">
                  <div class="entity-icon"><ha-icon icon="${escapeHtml(this._iconFor(item))}"></ha-icon></div>
                  <div class="entity-copy">
                    <div class="entity-name">${escapeHtml(this._friendlyName(item))}</div>
                    <div class="entity-secondary">${escapeHtml(this._secondaryText(item))}</div>
                  </div>
                  <div class="entity-state">${escapeHtml(this._formatState(item))}</div>
                </div>`;
            })
            .join("")}
        </div>`;
    }

    _stats(items) {
      const domains = new Map();
      let unreliable = 0;
      for (const item of items) {
        const domain = domainOf(item.entry.entity_id);
        domains.set(domain, (domains.get(domain) || 0) + 1);
        if (["unknown", "unavailable"].includes(item.state?.state)) unreliable += 1;
      }
      return { domains, unreliable, total: items.length };
    }

    _statsHtml(stats) {
      const chips = [...stats.domains.entries()]
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([domain, count]) => `<span class="chip">${escapeHtml(domain)} ${count}</span>`)
        .join("");
      return `<div class="stats"><span class="chip strong">Всего ${stats.total}</span>${chips}</div>`;
    }

    _contentHtml(config, active) {
      const source = this._source();
      if (!source) {
        return `
          <div class="placeholder">${escapeHtml(active.placeholder || "Раздел готов к наполнению.")}</div>
          <div class="meta">Предметные сущности ещё не подключены к панели.</div>`;
      }

      if (this._registryError) {
        return `
          <div class="placeholder unreliable-box">Не удалось прочитать реестр сущностей: ${escapeHtml(this._registryError)}</div>
          <div class="meta">Панель ничего не изменяет в Home Assistant и не выполняет команды интеграции.</div>`;
      }

      if (!Array.isArray(this._registry)) {
        return `<div class="placeholder">Читаю реестр сущностей Home Assistant…</div>`;
      }

      const all = this._integrationEntries();
      const visible = this._filterForView(all, active);
      const stats = this._stats(all);
      const healthOnly = active.readonly?.unavailable_only === true;
      const emptyMessage = healthOnly
        ? "Недоступных или неизвестных сущностей сейчас нет."
        : "Для этого раздела подходящие сущности не найдены.";

      return `
        ${this._statsHtml(stats)}
        ${visible.length ? this._entityRows(visible) : `<div class="placeholder">${escapeHtml(emptyMessage)}</div>`}
        <div class="meta">Только просмотр: состояния читаются из Home Assistant. Кнопки, toggle и service-вызовы интеграции не используются.</div>`;
    }

    _heroHtml(config) {
      const source = this._source();
      if (!source) {
        return `
          <div class="eyebrow">СОСТОЯНИЕ</div>
          <div class="hero-line">
            <div><h1>Каркас готов</h1><p>Подсистема подключена к единому шаблону Contract Generated UI.</p></div>
            <div class="badge"><ha-icon icon="mdi:check-circle-outline"></ha-icon><span>Готово</span></div>
          </div>`;
      }

      if (!Array.isArray(this._registry)) {
        return `
          <div class="eyebrow">СОСТОЯНИЕ</div>
          <div class="hero-line">
            <div><h1>Читаю данные</h1><p>${escapeHtml(config.title)}: загрузка реестра сущностей Home Assistant.</p></div>
            <div class="badge neutral"><ha-icon icon="mdi:progress-clock"></ha-icon><span>Загрузка</span></div>
          </div>`;
      }

      const stats = this._stats(this._integrationEntries());
      const heading = stats.total ? "Данные подключены" : "Сущности не найдены";
      const detail = stats.total
        ? `Найдено ${stats.total} сущностей · недоступно/unknown: ${stats.unreliable}.`
        : `В реестре Home Assistant нет активных сущностей платформ ${source.platforms?.join(", ") || "—"}.`;
      const badge = stats.unreliable ? `Недоступно ${stats.unreliable}` : "Только просмотр";
      const badgeClass = stats.unreliable ? "warn" : "neutral";
      const badgeIcon = stats.unreliable ? "mdi:alert-circle-outline" : "mdi:eye-outline";
      return `
        <div class="eyebrow">СОСТОЯНИЕ</div>
        <div class="hero-line">
          <div><h1>${escapeHtml(heading)}</h1><p>${escapeHtml(detail)}</p></div>
          <div class="badge ${badgeClass}"><ha-icon icon="${badgeIcon}"></ha-icon><span>${escapeHtml(badge)}</span></div>
        </div>`;
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
          :host{display:block;min-height:100vh;background:var(--primary-background-color,#f6f7f9);color:var(--primary-text-color,#111827);font-family:var(--paper-font-body1_-_font-family,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}
          *{box-sizing:border-box}
          .app{min-height:100vh;padding-bottom:calc(82px + env(safe-area-inset-bottom,0px))}
          .header{position:sticky;top:0;z-index:10;display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;min-height:70px;padding:max(6px,env(safe-area-inset-top,0px)) max(10px,env(safe-area-inset-right,0px)) 6px max(10px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-bottom:1px solid var(--divider-color,rgba(127,127,127,.18))}
          .rail{width:48px;height:48px;border:0;border-radius:16px;display:grid;place-items:center;background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--primary-text-color,#111827);cursor:pointer;-webkit-tap-highlight-color:transparent}
          .rail ha-icon{--mdc-icon-size:26px}.heading{min-width:0;text-align:center;line-height:1.12}.heading strong,.heading span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.heading strong{font-size:21px;font-weight:780;letter-spacing:-.02em}.heading span{margin-top:3px;font-size:12px;font-weight:600;color:var(--secondary-text-color,#6b7280)}
          main{width:min(100%,1120px);margin:0 auto;padding:18px 16px 28px}.hero,.card{border:1px solid var(--divider-color,rgba(127,127,127,.22));background:var(--card-background-color,var(--ha-card-background,#fff));border-radius:24px}.hero{padding:22px;position:relative;overflow:hidden}.hero::after{content:"";position:absolute;right:-46px;top:-54px;width:150px;height:150px;border-radius:50%;background:color-mix(in srgb,var(--primary-color,#03a9f4) 12%,transparent)}
          .eyebrow{font-size:11px;letter-spacing:.13em;font-weight:800;color:var(--secondary-text-color,#6b7280)}.hero-line{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-top:7px}.hero h1{margin:0;font-size:34px;line-height:1.04;letter-spacing:-.035em;font-weight:820}.hero p{margin:8px 0 0;color:var(--secondary-text-color,#6b7280);font-size:15px;line-height:1.4}.badge{position:relative;z-index:1;display:inline-flex;align-items:center;gap:7px;padding:9px 12px;border-radius:999px;background:color-mix(in srgb,var(--success-color,#43a047) 12%,var(--card-background-color,#fff));color:var(--success-color,#43a047);font-weight:750;white-space:nowrap}.badge.neutral{background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--secondary-text-color,#6b7280)}.badge.warn{background:color-mix(in srgb,var(--warning-color,#ff9800) 14%,var(--card-background-color,#fff));color:var(--warning-color,#ff9800)}.badge ha-icon{--mdc-icon-size:19px}
          .card{margin-top:14px;padding:20px}.card-title{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:780}.card-title ha-icon{color:var(--primary-color,#03a9f4);--mdc-icon-size:25px}.placeholder{margin-top:14px;padding:16px;border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.08));font-size:15px;line-height:1.5;color:var(--primary-text-color,#111827)}.unreliable-box{border:1px solid color-mix(in srgb,var(--warning-color,#ff9800) 35%,transparent)}.meta{margin-top:12px;color:var(--secondary-text-color,#6b7280);font-size:12px;line-height:1.45}
          .stats{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}.chip{display:inline-flex;align-items:center;min-height:28px;padding:5px 9px;border-radius:999px;background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--secondary-text-color,#6b7280);font-size:11px;font-weight:650}.chip.strong{color:var(--primary-text-color,#111827);font-weight:760}
          .entity-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:14px}.entity{min-width:0;display:grid;grid-template-columns:38px minmax(0,1fr) auto;align-items:center;gap:10px;padding:12px 13px;border:1px solid var(--divider-color,rgba(127,127,127,.18));border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.045))}.entity.unreliable{border-color:color-mix(in srgb,var(--warning-color,#ff9800) 38%,var(--divider-color,transparent))}.entity-icon{width:38px;height:38px;border-radius:13px;display:grid;place-items:center;background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,transparent);color:var(--primary-color,#03a9f4)}.entity-icon ha-icon{--mdc-icon-size:21px}.entity-copy{min-width:0}.entity-name,.entity-secondary{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-name{font-size:14px;font-weight:720}.entity-secondary{margin-top:2px;font-size:10.5px;color:var(--secondary-text-color,#6b7280)}.entity-state{max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right;font-size:13px;font-weight:760}
          .bottom{position:fixed;z-index:20;left:0;right:0;bottom:0;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-top:1px solid var(--divider-color,rgba(127,127,127,.18));box-shadow:0 -4px 18px rgba(0,0,0,.08)}
          nav{width:min(100%,720px);margin:0 auto;display:grid;grid-template-columns:repeat(${tabs.length},minmax(0,1fr));gap:4px}.tab{appearance:none;border:0;background:transparent;color:var(--secondary-text-color,#6b7280);min-width:0;min-height:60px;padding:7px 2px 5px;border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}.tab ha-icon{--mdc-icon-size:24px;width:24px;height:24px}.tab span{width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;font-size:11.5px;line-height:15px;font-weight:600}.tab.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);cursor:default}
          @media(max-width:680px){.entity-grid{grid-template-columns:1fr}}@media(max-width:390px){.header{grid-template-columns:48px minmax(0,1fr) 48px}.rail{width:44px;height:44px;border-radius:14px}.heading strong{font-size:19px}.hero h1{font-size:30px}.hero{padding:19px}.card{padding:18px}.badge{font-size:13px;padding:8px 10px}.entity-state{max-width:115px}}
          @media(min-width:900px){main{padding-top:22px}.hero h1{font-size:38px}}
        </style>
        <div class="app">
          <header class="header">
            <button class="rail" id="back" type="button" aria-label="Назад"><ha-icon icon="mdi:arrow-left"></ha-icon></button>
            <div class="heading"><strong>${escapeHtml(config.title)}</strong><span>${escapeHtml(config.subtitle || config.parent?.title || "")}</span></div>
            <button class="rail" id="refresh" type="button" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button>
          </header>
          <main>
            <section class="hero">${this._heroHtml(config)}</section>
            <section class="card">
              <div class="card-title"><ha-icon icon="${escapeHtml(active.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${escapeHtml(active.label || active.id)}</span></div>
              ${this._contentHtml(config, active)}
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
