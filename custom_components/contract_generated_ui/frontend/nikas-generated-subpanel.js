// Shared generated application-panel host for Contract Generated UI.
// One self-contained bundle serves non-specialized manifest-defined panels.

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

  function sameTreeShape(current, desired) {
    if (!current || !desired || current.nodeType !== desired.nodeType) return false;
    if (current.nodeType === Node.ELEMENT_NODE && current.tagName !== desired.tagName) return false;
    if (current.childNodes.length !== desired.childNodes.length) return false;
    for (let index = 0; index < current.childNodes.length; index += 1) {
      if (!sameTreeShape(current.childNodes[index], desired.childNodes[index])) return false;
    }
    return true;
  }

  function syncTree(current, desired) {
    if (current.nodeType === Node.TEXT_NODE || current.nodeType === Node.COMMENT_NODE) {
      if (current.nodeValue !== desired.nodeValue) current.nodeValue = desired.nodeValue;
      return;
    }
    if (current.nodeType === Node.ELEMENT_NODE) {
      for (const attribute of [...current.attributes]) {
        if (!desired.hasAttribute(attribute.name)) current.removeAttribute(attribute.name);
      }
      for (const attribute of [...desired.attributes]) {
        if (current.getAttribute(attribute.name) !== attribute.value) current.setAttribute(attribute.name, attribute.value);
      }
    }
    for (let index = 0; index < current.childNodes.length; index += 1) {
      syncTree(current.childNodes[index], desired.childNodes[index]);
    }
  }

  function commitStableMarkup(root, markup) {
    if (typeof document === "undefined" || typeof document.createElement !== "function" || typeof Node === "undefined") {
      root.innerHTML = markup;
      return true;
    }
    const template = document.createElement("template");
    template.innerHTML = markup;
    const current = [...root.childNodes];
    const desired = [...template.content.childNodes];
    const compatible = current.length === desired.length && current.every((node, index) => sameTreeShape(node, desired[index]));
    if (!compatible) {
      root.replaceChildren(template.content.cloneNode(true));
      return true;
    }
    current.forEach((node, index) => syncTree(node, desired[index]));
    return false;
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
      this._devices = new Map();
      this._registryError = null;
      this._registryPromise = null;
      this._registryPlatformsKey = "";
      this._selectedDeviceId = null;
      this._viewCache = new Map();
      this._shellMounted = false;
      this._onHashChange = () => {
        this._active = this._tabFromLocation();
        window.NikasPanelZoom?.attach?.(this)?.resetPosition?.();
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
      this._selectedDeviceId = null;
      this._viewCache.clear();
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
      window.NikasPanelZoom?.attach?.(this)?.resetPosition?.();
      this._active = id;
      window.history.replaceState(null, "", `${window.location.pathname}#${encodeURIComponent(id)}`);
      this._queueRender();
    }

    _selectDevice(id) {
      if (!id || id === this._selectedDeviceId) return;
      this._selectedDeviceId = id;
      window.NikasPanelZoom?.attach?.(this)?.contextChanged?.();
      this._queueRender();
    }

    _toggleMenu() {
      this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
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
      this._devices = new Map();
      this._registryPromise = Promise.all([
        this._hass.callWS({ type: "config/entity_registry/list" }),
        this._hass.callWS({ type: "config/device_registry/list" }),
      ])
        .then(([entries, devices]) => {
          this._registry = Array.isArray(entries) ? entries : [];
          this._devices = new Map(
            (Array.isArray(devices) ? devices : [])
              .filter((device) => device?.id)
              .map((device) => [device.id, device]),
          );
          this._registryError = null;
        })
        .catch((error) => {
          this._registry = [];
          this._devices = new Map();
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

    _deviceLabel(deviceId) {
      const device = this._devices.get(deviceId);
      return device?.name_by_user || device?.name || device?.model || "Устройство";
    }

    _deviceGroups(items) {
      const groups = new Map();
      for (const item of items) {
        const key = item.entry.device_id || "__unassigned__";
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(item);
      }
      return [...groups.entries()]
        .map(([id, entries]) => ({
          id,
          label: id === "__unassigned__" ? "Без устройства" : this._deviceLabel(id),
          entries,
        }))
        .sort((left, right) => left.label.localeCompare(right.label, "ru"));
    }

    _ensureSelectedDevice(groups) {
      if (!groups.length) {
        this._selectedDeviceId = null;
        return null;
      }
      if (!groups.some((group) => group.id === this._selectedDeviceId)) {
        this._selectedDeviceId = groups[0].id;
      }
      return groups.find((group) => group.id === this._selectedDeviceId) || groups[0];
    }

    _sourceLooksLikeVehicle() {
      return Array.isArray(this._source()?.platforms) && this._source().platforms.includes("starline");
    }

    _deviceSelectorHtml(groups) {
      if (groups.length < 2) return "";
      const icon = this._sourceLooksLikeVehicle() ? "mdi:car" : "mdi:devices";
      return `
        <div class="device-selector" aria-label="Выбор устройства">
          ${groups
            .map((group) => {
              const selected = group.id === this._selectedDeviceId;
              return `<button class="device-button ${selected ? "active" : ""}" data-device="${escapeHtml(group.id)}" ${selected ? "disabled" : ""}>
                <ha-icon icon="${icon}"></ha-icon><span>${escapeHtml(group.label)}</span>
              </button>`;
            })
            .join("")}
        </div>`;
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

    _secondaryText(item, showEntityId = false) {
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
      return showEntityId ? item.entry.entity_id : "";
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

    _entityRows(items, showEntityId = false) {
      if (!items.length) return "";
      return `
        <div class="entity-grid">
          ${items
            .map((item) => {
              const unavailable = ["unknown", "unavailable"].includes(item.state?.state);
              const secondary = this._secondaryText(item, showEntityId);
              return `
                <div class="entity ${unavailable ? "unreliable" : ""}">
                  <div class="entity-icon"><ha-icon icon="${escapeHtml(this._iconFor(item))}"></ha-icon></div>
                  <div class="entity-copy">
                    <div class="entity-name">${escapeHtml(this._friendlyName(item))}</div>
                    ${secondary ? `<div class="entity-secondary">${escapeHtml(secondary)}</div>` : ""}
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

    _deviceOverviewHtml(groups, active) {
      const icon = this._sourceLooksLikeVehicle() ? "mdi:car" : "mdi:devices";
      return groups
        .map((group) => {
          const visible = this._filterForView(group.entries, active);
          return `
            <section class="device-block">
              <div class="device-heading"><ha-icon icon="${icon}"></ha-icon><span>${escapeHtml(group.label)}</span></div>
              ${visible.length ? this._entityRows(visible) : `<div class="placeholder">Для устройства нет данных этого раздела.</div>`}
            </section>`;
        })
        .join("");
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
          <div class="placeholder unreliable-box">Не удалось прочитать реестры Home Assistant: ${escapeHtml(this._registryError)}</div>
          <div class="meta">Панель ничего не изменяет в Home Assistant и не выполняет команды интеграции.</div>`;
      }

      if (!Array.isArray(this._registry)) {
        return `<div class="placeholder">Читаю реестры Home Assistant…</div>`;
      }

      const all = this._integrationEntries();
      const groups = this._deviceGroups(all);
      const selected = this._ensureSelectedDevice(groups);
      const stats = this._stats(all);
      const healthOnly = active.readonly?.unavailable_only === true;
      const emptyMessage = healthOnly
        ? "Недоступных или неизвестных сущностей сейчас нет."
        : "Для этого раздела подходящие сущности не найдены.";

      if (active.id === "overview" && groups.length > 1) {
        return `
          ${this._deviceOverviewHtml(groups, active)}
          <div class="meta">Только просмотр: сводка сгруппирована по устройствам из Home Assistant Device Registry. Управляющие вызовы отсутствуют.</div>`;
      }

      const scope = selected ? selected.entries : all;
      const visible = this._filterForView(scope, active);
      const showEntityId = active.readonly?.unavailable_only === true;

      return `
        ${showEntityId ? this._statsHtml(stats) : ""}
        ${visible.length ? this._entityRows(visible, showEntityId) : `<div class="placeholder">${escapeHtml(emptyMessage)}</div>`}
        <div class="meta">Только просмотр: состояния читаются из Home Assistant. Кнопки, toggle и service-вызовы интеграции не используются.</div>`;
    }

    _peerSelectorHtml(active) {
      if (!active || this._source()?.kind !== "entity_registry" || !Array.isArray(this._registry)) return "";
      const groups = this._deviceGroups(this._integrationEntries());
      this._ensureSelectedDevice(groups);
      return groups.length > 1 ? this._deviceSelectorHtml(groups) : "";
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
            <div><h1>Читаю данные</h1><p>${escapeHtml(config.title)}: загрузка реестров Home Assistant.</p></div>
            <div class="badge neutral"><ha-icon icon="mdi:progress-clock"></ha-icon><span>Загрузка</span></div>
          </div>`;
      }

      const entries = this._integrationEntries();
      const stats = this._stats(entries);
      const groups = this._deviceGroups(entries);
      const multi = groups.length > 1;
      const heading = multi
        ? `${groups.length} ${this._sourceLooksLikeVehicle() ? "автомобиля" : "устройства"}`
        : stats.total
          ? "Данные подключены"
          : "Сущности не найдены";
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

    _mountShell() {
      if (this._shellMounted) return;
      this.shadowRoot.innerHTML = `
        <style>
          :host{display:block;width:100%;height:100dvh;overflow:hidden;background:var(--primary-background-color,#f6f7f9);color:var(--primary-text-color,#111827);font-family:var(--paper-font-body1_-_font-family,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}
          *{box-sizing:border-box}.app{position:relative;width:100%;height:100dvh;display:grid;grid-template-rows:auto auto minmax(0,1fr);overflow:hidden}
          button{font:inherit}.header{z-index:20;display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;min-height:62px;padding:max(5px,env(safe-area-inset-top,0px)) max(8px,env(safe-area-inset-right,0px)) 5px max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-bottom:1px solid var(--divider-color,rgba(127,127,127,.18));box-shadow:0 2px 12px rgba(0,0,0,.06)}
          .rail{width:44px;height:44px;border:1px solid var(--divider-color,rgba(127,127,127,.18));border-radius:16px;display:grid;place-items:center;padding:0;background:var(--card-background-color,var(--ha-card-background,#fff));color:var(--primary-text-color,#111827);box-shadow:0 7px 20px rgba(23,45,76,.08);cursor:pointer;-webkit-tap-highlight-color:transparent}.rail ha-icon{--mdc-icon-size:25px;width:25px;height:25px}.rail#refresh{color:var(--primary-color,#03a9f4)}
          .rail:focus-visible,.tab:focus-visible{outline:2px solid var(--primary-color,#03a9f4);outline-offset:1px}.heading{min-width:0;text-align:center;line-height:1.12}.heading strong,.heading span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.heading strong{font-size:23px;font-weight:800;letter-spacing:-.02em}.heading span{margin-top:3px;font-size:14px;font-weight:560;color:var(--secondary-text-color,#6b7280)}
          .peer-selector:empty{display:none}.peer-selector{z-index:15;padding:8px 16px 0;background:var(--primary-background-color,#f6f7f9)}.peer-selector .device-selector{width:min(100%,1120px);margin:0 auto}
          .canvas-viewport{position:relative;min-width:0;min-height:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior-x:none;overscroll-behavior-y:none;touch-action:pan-y}.canvas-viewport.zoomed{overflow:hidden;overscroll-behavior:none;touch-action:none;user-select:none;-webkit-user-select:none}
          .work-canvas{position:relative;width:min(calc(100% - 32px),1120px);min-height:100%;margin:0 auto;padding:18px 0 82px;transform-origin:0 0;visibility:hidden}.work-canvas.ready{visibility:visible}.canvas-viewport.zoomed .work-canvas{position:absolute;left:16px;right:16px;width:auto;margin:0}.view{display:block;min-width:0}
          .hero,.card{border:1px solid var(--divider-color,rgba(127,127,127,.22));background:var(--card-background-color,var(--ha-card-background,#fff));border-radius:24px}.hero{padding:22px;position:relative;overflow:hidden}.hero::after{content:"";position:absolute;right:-46px;top:-54px;width:150px;height:150px;border-radius:50%;background:color-mix(in srgb,var(--primary-color,#03a9f4) 12%,transparent)}
          .eyebrow{font-size:12px;letter-spacing:.13em;font-weight:800;color:var(--secondary-text-color,#6b7280)}.hero-line{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-top:7px}.hero h1{margin:0;font-size:25px;line-height:1.08;letter-spacing:-.025em;font-weight:820}.hero p{margin:8px 0 0;color:var(--secondary-text-color,#6b7280);font-size:15px;line-height:1.4}.badge{position:relative;z-index:1;display:inline-flex;align-items:center;gap:7px;padding:9px 12px;border-radius:999px;background:color-mix(in srgb,var(--success-color,#43a047) 12%,var(--card-background-color,#fff));color:var(--success-color,#43a047);font-size:14px;font-weight:750;white-space:nowrap}.badge.neutral{background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--secondary-text-color,#6b7280)}.badge.warn{background:color-mix(in srgb,var(--warning-color,#ff9800) 14%,var(--card-background-color,#fff));color:var(--warning-color,#ff9800)}.badge ha-icon{--mdc-icon-size:19px}
          .card{margin-top:14px;padding:20px}.card-title{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:780}.card-title ha-icon{color:var(--primary-color,#03a9f4);--mdc-icon-size:25px}.placeholder{margin-top:14px;padding:16px;border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.08));font-size:15px;line-height:1.5;color:var(--primary-text-color,#111827)}.unreliable-box{border:1px solid color-mix(in srgb,var(--warning-color,#ff9800) 35%,transparent)}.meta{margin-top:12px;color:var(--secondary-text-color,#6b7280);font-size:12px;line-height:1.45}
          .device-block{margin-top:18px}.device-block:first-of-type{margin-top:14px}.device-heading{display:flex;align-items:center;gap:9px;font-size:18px;font-weight:780}.device-heading ha-icon{--mdc-icon-size:23px;color:var(--secondary-text-color,#6b7280)}
          .device-selector{display:flex;gap:8px;overflow-x:auto;margin-top:14px;padding-bottom:2px;scrollbar-width:none}.device-selector::-webkit-scrollbar{display:none}.device-button{appearance:none;border:1px solid var(--divider-color,rgba(127,127,127,.22));background:var(--secondary-background-color,rgba(127,127,127,.05));color:var(--secondary-text-color,#6b7280);min-height:44px;padding:8px 13px;border-radius:15px;display:inline-flex;align-items:center;gap:7px;font-size:13px;font-weight:700;white-space:nowrap}.device-button.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);border-color:color-mix(in srgb,var(--primary-color,#03a9f4) 28%,var(--divider-color,transparent))}.device-button ha-icon{--mdc-icon-size:20px}
          .stats{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}.chip{display:inline-flex;align-items:center;min-height:28px;padding:5px 9px;border-radius:999px;background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--secondary-text-color,#6b7280);font-size:12px;font-weight:650}.chip.strong{color:var(--primary-text-color,#111827);font-weight:760}
          .entity-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}.entity{min-width:0;display:grid;grid-template-columns:38px minmax(0,1fr) auto;align-items:center;gap:10px;padding:12px 13px;border:1px solid var(--divider-color,rgba(127,127,127,.18));border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.045))}.entity.unreliable{border-color:color-mix(in srgb,var(--warning-color,#ff9800) 38%,var(--divider-color,transparent))}.entity-icon{width:38px;height:38px;border-radius:13px;display:grid;place-items:center;background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,transparent);color:var(--primary-color,#03a9f4)}.entity-icon ha-icon{--mdc-icon-size:21px}.entity-copy{min-width:0}.entity-name,.entity-secondary{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-name{font-size:14px;font-weight:720}.entity-secondary{margin-top:2px;font-size:12px;color:var(--secondary-text-color,#6b7280)}.entity-state{max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right;font-size:13px;font-weight:760}
          .bottom{position:fixed;z-index:20;left:0;right:0;bottom:0;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-top:1px solid var(--divider-color,rgba(127,127,127,.18));box-shadow:0 -4px 18px rgba(0,0,0,.08)}
          nav{width:min(100%,720px);margin:0 auto;display:grid;grid-template-columns:repeat(var(--tab-count,1),minmax(0,1fr));gap:4px}.tab{appearance:none;border:0;background:transparent;color:var(--secondary-text-color,#6b7280);min-width:0;min-height:52px;padding:4px 2px;border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;-webkit-tap-highlight-color:transparent}.tab ha-icon{--mdc-icon-size:28px;width:28px;height:28px}.tab span{width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;font-size:12px;line-height:15px;font-weight:700}.tab.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);cursor:default}
          .scale-status{position:absolute;z-index:40;left:50%;bottom:calc(76px + env(safe-area-inset-bottom,0px));transform:translate(-50%,10px);opacity:0;pointer-events:none;padding:9px 14px;border-radius:999px;background:rgba(20,27,34,.88);color:#fff;font-size:13px;font-weight:720;transition:opacity .14s ease,transform .14s ease}.scale-status.visible{opacity:1;transform:translate(-50%,0)}
          @media(max-width:680px){:host{position:fixed;inset:0;width:auto;height:auto}.app{position:absolute;inset:0;width:auto;height:auto}.entity-grid{grid-template-columns:1fr}}
          @media(max-width:390px){.header{grid-template-columns:48px minmax(0,1fr) 48px;min-height:60px}.heading strong{font-size:21px}.heading span{font-size:13px}.hero h1{font-size:23px}.hero{padding:19px}.card{padding:18px}.badge{font-size:13px;padding:8px 10px}.entity-state{max-width:115px}}
          @media(min-width:900px){.work-canvas{padding-top:22px}}
          @media(prefers-reduced-motion:reduce){.scale-status{transition:none}}
        </style>
        <div class="app">
          <header class="header">
            <button class="rail" id="menu" type="button" aria-label="Меню Home Assistant"><ha-icon icon="mdi:menu"></ha-icon></button>
            <div class="heading"><strong></strong><span></span></div>
            <button class="rail" id="refresh" type="button" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button>
          </header>
          <div class="peer-selector"></div>
          <main class="canvas-viewport" aria-label="Рабочая область специализированной панели"><div class="work-canvas"></div></main>
          <div class="bottom"><nav aria-label="Навигация панели"></nav></div>
          <div class="scale-status" role="status" aria-live="polite">Масштаб 100%</div>
        </div>`;
      this.shadowRoot.addEventListener("click", (event) => {
        const button = event.target?.closest?.("button");
        if (!button) return;
        if (button.id === "menu") this._toggleMenu();
        else if (button.id === "refresh") this._refresh();
        else if (button.dataset.tab) this._selectTab(button.dataset.tab);
        else if (button.dataset.device) this._selectDevice(button.dataset.device);
      });
      this._shellMounted = true;
    }

    _viewKey(active) {
      return `${active.id}:${this._selectedDeviceId || "panel"}`;
    }

    _render() {
      const config = this._config();
      const tabs = this._tabs();
      const active = this._activeTab();
      if (!config.title || !tabs.length || !active) {
        if (!this._shellMounted && !this.shadowRoot.firstChild) {
          this.shadowRoot.innerHTML = `<div style="padding:24px;font:16px sans-serif">Панель ещё не настроена.</div>`;
        }
        return;
      }

      this._mountShell();
      this.shadowRoot.querySelector(".heading strong").textContent = config.title;
      this.shadowRoot.querySelector(".heading span").textContent = config.subtitle || config.parent?.title || "";

      const peerSelector = this.shadowRoot.querySelector(".peer-selector");
      commitStableMarkup(peerSelector, this._peerSelectorHtml(active));

      const navButtons = tabs.map((tab) => {
        const selected = tab.id === active.id;
        return `<button class="tab${selected ? " active" : ""}" data-tab="${escapeHtml(tab.id)}" type="button"${selected ? " disabled" : ""} aria-current="${selected ? "page" : "false"}"><ha-icon icon="${escapeHtml(tab.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${escapeHtml(tab.label || tab.id)}</span></button>`;
      }).join("");
      const nav = this.shadowRoot.querySelector("nav");
      nav.style.setProperty("--tab-count", String(Math.max(1, tabs.length)));
      commitStableMarkup(nav, navButtons);

      const viewKey = this._viewKey(active);
      let view = this._viewCache.get(viewKey);
      if (!view) {
        view = document.createElement("div");
        view.className = "view";
        view.dataset.viewKey = viewKey;
        this._viewCache.set(viewKey, view);
      }
      const viewMarkup = `
        <section class="hero">${this._heroHtml(config)}</section>
        <section class="card">
          <div class="card-title"><ha-icon icon="${escapeHtml(active.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${escapeHtml(active.label || active.id)}</span></div>
          ${this._contentHtml(config, active)}
        </section>`;
      commitStableMarkup(view, viewMarkup);

      const canvas = this.shadowRoot.querySelector(".work-canvas");
      if (canvas.firstElementChild !== view || canvas.childElementCount !== 1) canvas.replaceChildren(view);
      window.NikasPanelZoom?.attach?.(this)?.bind?.();
    }
  }

  customElements.define(ELEMENT_NAME, NikasGeneratedSubpanel);
})();
