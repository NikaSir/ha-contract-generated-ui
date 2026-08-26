// Gesture-only hybrid zoom controller for specialized NikaS panels.
// At 100% the viewport owns native vertical scrolling. Transform panning starts only above 100%.
(() => {
  if (window.NikasPanelZoom?.version === 2) return;

  const DEFAULT_MIN = 0.75;
  const DEFAULT_MAX = 2.0;
  const PAN_THRESHOLD = 6;
  const TAP_DURATION = 300;
  const DOUBLE_TAP_GAP = 420;
  const CLICK_GUARD = 460;
  const AUTO_TARGETS = new Set(["NIKAS-GENERATED-SUBPANEL"]);
  const controllers = new WeakMap();
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const finite = (value, fallback) => Number.isFinite(Number(value)) ? Number(value) : fallback;

  class ZoomController {
    constructor(host, options = {}) {
      this.host = host;
      this.options = options;
      this.root = host.shadowRoot || host;
      this.viewport = null;
      this.canvas = null;
      this.state = { scale: 1, x: 0, y: 0 };
      this.session = null;
      this.lastTwoFingerTap = 0;
      this.suppressClicksUntil = 0;
      this.resizeObserver = null;
      this.boundStart = (event) => this._touchStart(event);
      this.boundMove = (event) => this._touchMove(event);
      this.boundEnd = (event) => this._touchEnd(event);
      this.boundGuard = (event) => this._guardActivation(event);
      this.observer = new MutationObserver(() => queueMicrotask(() => this.bind()));
      this.observer.observe(this.root, { childList: true, subtree: true });
      this.bind();
    }

    _min() { return clamp(finite(this.options.min, DEFAULT_MIN), 0.25, 1); }
    _max() { return clamp(finite(this.options.max, DEFAULT_MAX), 1, 4); }

    _panelKey() {
      const config = this.host?.panel?.config || this.host?.panel || {};
      const panel = this.options.key || config.id || this.host.localName || "specialized-panel";
      const device = this.host?._selectedDeviceId || "panel";
      return `${window.location.pathname}:${panel}:${device}`;
    }

    _storageKey() { return `nikas:panel-transform:v2:${this._panelKey()}`; }

    _loadState() {
      this.state = { scale: 1, x: 0, y: 0 };
      try {
        const stored = JSON.parse(window.localStorage.getItem(this._storageKey()) || "null");
        if (!stored) return;
        this.state = {
          scale: clamp(finite(stored.scale, 1), this._min(), this._max()),
          x: finite(stored.x, 0),
          y: finite(stored.y, 0),
        };
        if (this.state.scale <= 1) this.state = { scale: this.state.scale, x: 0, y: 0 };
      } catch (_error) {
        // Local persistence is optional.
      }
    }

    _saveState() {
      try { window.localStorage.setItem(this._storageKey(), JSON.stringify(this.state)); }
      catch (_error) { /* Keep the current session operational. */ }
    }

    bind() {
      const viewport = this.root.querySelector?.(".canvas-viewport");
      const canvas = viewport?.querySelector?.(":scope > .work-canvas");
      if (!viewport || !canvas) return;
      if (viewport === this.viewport && canvas === this.canvas) return;
      this._detach();
      this.viewport = viewport;
      this.canvas = canvas;
      this._loadState();
      viewport.addEventListener("touchstart", this.boundStart, { passive: false });
      viewport.addEventListener("touchmove", this.boundMove, { passive: false });
      viewport.addEventListener("touchend", this.boundEnd, { passive: false });
      viewport.addEventListener("touchcancel", this.boundEnd, { passive: false });
      viewport.addEventListener("click", this.boundGuard, true);
      viewport.addEventListener("contextmenu", this.boundGuard, true);
      if (typeof ResizeObserver === "function") {
        this.resizeObserver = new ResizeObserver(() => this._clampAndApply());
        this.resizeObserver.observe(viewport);
        this.resizeObserver.observe(canvas);
      }
      this._clampAndApply();
    }

    _detach() {
      this.resizeObserver?.disconnect();
      this.resizeObserver = null;
      if (!this.viewport) return;
      this.viewport.removeEventListener("touchstart", this.boundStart);
      this.viewport.removeEventListener("touchmove", this.boundMove);
      this.viewport.removeEventListener("touchend", this.boundEnd);
      this.viewport.removeEventListener("touchcancel", this.boundEnd);
      this.viewport.removeEventListener("click", this.boundGuard, true);
      this.viewport.removeEventListener("contextmenu", this.boundGuard, true);
      this.viewport = null;
      this.canvas = null;
    }

    _distance(touches) {
      return Math.hypot(touches[0].clientX - touches[1].clientX, touches[0].clientY - touches[1].clientY);
    }

    _midpoint(touches) {
      return { x: (touches[0].clientX + touches[1].clientX) / 2, y: (touches[0].clientY + touches[1].clientY) / 2 };
    }

    _bounds(scale = this.state.scale) {
      if (!this.viewport || !this.canvas || scale <= 1) return { minX: 0, minY: 0 };
      const width = Math.max(this.canvas.offsetWidth, this.canvas.scrollWidth);
      const height = Math.max(this.canvas.offsetHeight, this.canvas.scrollHeight);
      const availableWidth = Math.max(0, this.viewport.clientWidth - this.canvas.offsetLeft);
      const availableHeight = Math.max(0, this.viewport.clientHeight - this.canvas.offsetTop);
      return {
        minX: Math.min(0, availableWidth - width * scale),
        minY: Math.min(0, availableHeight - height * scale),
      };
    }

    _clampState(scale, x, y) {
      const safeScale = clamp(finite(scale, 1), this._min(), this._max());
      if (safeScale <= 1) return { scale: safeScale, x: 0, y: 0 };
      const bounds = this._bounds(safeScale);
      return {
        scale: safeScale,
        x: clamp(finite(x, 0), bounds.minX, 0),
        y: clamp(finite(y, 0), bounds.minY, 0),
      };
    }

    _apply() {
      if (!this.viewport || !this.canvas) return;
      const zoomed = this.state.scale > 1.0001;
      if (!zoomed) this.state = { scale: this.state.scale, x: 0, y: 0 };
      this.viewport.classList.toggle("zoomed", zoomed);
      this.canvas.style.transform = `translate3d(${this.state.x}px, ${this.state.y}px, 0) scale(${this.state.scale})`;
      this.canvas.classList.add("ready");
    }

    _clampAndApply() {
      this.state = this._clampState(this.state.scale, this.state.x, this.state.y);
      this._apply();
      this._saveState();
    }

    _cancelPendingHold(target) {
      if (!target?.dispatchEvent) return;
      const init = { bubbles: true, composed: true, cancelable: false, pointerType: "touch" };
      const event = typeof PointerEvent === "function" ? new PointerEvent("pointercancel", init) : new Event("pointercancel", init);
      target.dispatchEvent(event);
    }

    _touchStart(event) {
      if (event.touches.length === 1) {
        const touch = event.touches[0];
        this.session = {
          startedAt: performance.now(), maxTouches: 1, moved: false, multi: false,
          startX: touch.clientX, startY: touch.clientY, startState: { ...this.state }, target: event.composedPath?.()[0] || event.target,
        };
        return;
      }
      if (event.touches.length !== 2) return;
      const mid = this._midpoint(event.touches);
      const rect = this.viewport.getBoundingClientRect();
      const localX = mid.x - rect.left - this.canvas.offsetLeft;
      const localY = mid.y - rect.top - this.canvas.offsetTop;
      const nativeScrollY = this.state.scale <= 1 ? this.viewport.scrollTop : 0;
      this.session = {
        ...(this.session || {}), startedAt: this.session?.startedAt || performance.now(), maxTouches: 2, moved: false, multi: true,
        distance: Math.max(1, this._distance(event.touches)), scale: this.state.scale,
        contentX: (localX - this.state.x) / this.state.scale,
        contentY: (localY + nativeScrollY - this.state.y) / this.state.scale,
        midX: mid.x, midY: mid.y, target: this.session?.target || event.target,
      };
      this._cancelPendingHold(this.session.target);
      this.suppressClicksUntil = Date.now() + CLICK_GUARD;
      event.preventDefault();
    }

    _touchMove(event) {
      if (!this.session) return;
      if (this.session.multi && event.touches.length === 2) {
        const mid = this._midpoint(event.touches);
        const currentDistance = Math.max(1, this._distance(event.touches));
        const delta = Math.hypot(mid.x - this.session.midX, mid.y - this.session.midY);
        if (!this.session.moved && Math.abs(currentDistance - this.session.distance) < PAN_THRESHOLD && delta < PAN_THRESHOLD) return;
        this.session.moved = true;
        const rect = this.viewport.getBoundingClientRect();
        const localX = mid.x - rect.left - this.canvas.offsetLeft;
        const localY = mid.y - rect.top - this.canvas.offsetTop;
        const scale = clamp(this.session.scale * currentDistance / this.session.distance, this._min(), this._max());
        if (scale > 1) this.viewport.scrollTop = 0;
        this.state = this._clampState(scale, localX - this.session.contentX * scale, localY - this.session.contentY * scale);
        this._apply();
        this.suppressClicksUntil = Date.now() + CLICK_GUARD;
        event.preventDefault();
        return;
      }
      if (this.state.scale <= 1 || event.touches.length !== 1 || this.session.multi) return;
      const touch = event.touches[0];
      const dx = touch.clientX - this.session.startX;
      const dy = touch.clientY - this.session.startY;
      if (!this.session.moved && Math.hypot(dx, dy) < PAN_THRESHOLD) return;
      if (!this.session.moved) this._cancelPendingHold(this.session.target);
      this.session.moved = true;
      this.state = this._clampState(this.session.startState.scale, this.session.startState.x + dx, this.session.startState.y + dy);
      this._apply();
      this.suppressClicksUntil = Date.now() + CLICK_GUARD;
      event.preventDefault();
    }

    _touchEnd(event) {
      if (!this.session || event.touches.length) return;
      const session = this.session;
      const twoFingerTap = session.multi && !session.moved && performance.now() - session.startedAt <= TAP_DURATION;
      if (session.moved && this.state.scale >= 0.97 && this.state.scale <= 1.03) {
        this.reset(true);
      } else if (twoFingerTap) {
        const now = performance.now();
        if (now - this.lastTwoFingerTap <= DOUBLE_TAP_GAP) {
          this.lastTwoFingerTap = 0;
          this.reset(true);
        } else {
          this.lastTwoFingerTap = now;
        }
      } else {
        this._clampAndApply();
      }
      if (session.moved || session.multi) this.suppressClicksUntil = Date.now() + CLICK_GUARD;
      this.session = null;
    }

    _guardActivation(event) {
      if (Date.now() >= this.suppressClicksUntil) return;
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation?.();
    }

    reset(showStatus = false) {
      this.state = { scale: 1, x: 0, y: 0 };
      if (this.viewport) this.viewport.scrollTop = 0;
      this._apply();
      this._saveState();
      if (showStatus) {
        const status = this.root.querySelector?.(".scale-status");
        status?.classList.add("visible");
        window.setTimeout(() => status?.classList.remove("visible"), 1100);
      }
    }

    resetPosition() {
      if (this.viewport) this.viewport.scrollTop = 0;
      this.state = this._clampState(this.state.scale, 0, 0);
      this._apply();
      this._saveState();
    }

    contextChanged() {
      this._loadState();
      this.resetPosition();
    }

    destroy() { this.observer.disconnect(); this._detach(); }
  }

  function attach(host, options = {}) {
    if (!host?.shadowRoot) return null;
    const existing = controllers.get(host);
    if (existing) { existing.bind(); return existing; }
    const controller = new ZoomController(host, options);
    controllers.set(host, controller);
    return controller;
  }

  function discover(root = document) {
    const visit = (node) => {
      if (!node) return;
      if (node.nodeType === Node.ELEMENT_NODE) {
        if (AUTO_TARGETS.has(node.tagName) || node.getAttribute?.("data-nikas-panel-zoom") === "true") attach(node);
        if (node.shadowRoot) visit(node.shadowRoot);
      }
      for (const child of node.children || node.childNodes || []) visit(child);
    };
    visit(root);
  }

  window.NikasPanelZoom = { version: 2, attach, discover, defaults: { min: DEFAULT_MIN, max: DEFAULT_MAX } };
  const observer = new MutationObserver((records) => {
    for (const record of records) for (const node of record.addedNodes) discover(node);
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
  discover(document);
})();
// Shared application-chrome policy for specialized NikaS panels.
// Owns safe-area Header/Bottom Tab Bar geometry and binds the common zoom controller to <main>.
(() => {
  const TARGETS = ["nikas-generated-subpanel"];
  const PATCH_FLAG = Symbol.for("nikas.specializedPanelShell.patched");
  const STYLE_ID = "nikas-specialized-panel-shell-policy";

  function policyCss() {
    return `
      .header{
        grid-template-columns:52px minmax(0,1fr) 52px!important;
        min-height:62px!important;
        padding:
          max(5px,env(safe-area-inset-top,0px))
          max(8px,env(safe-area-inset-right,0px))
          5px
          max(8px,env(safe-area-inset-left,0px))!important;
      }
      .header .rail{width:44px!important;height:44px!important;border-radius:16px!important}
      .header .heading{text-align:center;min-width:0}
      .bottom{
        left:0!important;
        right:0!important;
        bottom:0!important;
        padding:
          6px
          max(8px,env(safe-area-inset-right,0px))
          calc(6px + env(safe-area-inset-bottom,0px))
          max(8px,env(safe-area-inset-left,0px))!important;
      }
      @media(max-width:390px){
        .header{grid-template-columns:48px minmax(0,1fr) 48px!important;min-height:60px!important}
      }
    `;
  }

  function ensurePolicyStyle(root) {
    if (!root || root.getElementById(STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = policyCss();
    root.appendChild(style);
  }

  function ensureShell(host) {
    const root = host?.shadowRoot;
    if (!root) return;
    ensurePolicyStyle(root);

    // Zoom controller transforms only the work canvas. Header, selector and bottom
    // navigation remain siblings at native scale.
    if (window.NikasPanelZoom?.attach) {
      window.NikasPanelZoom.attach(host, { min: 0.75, max: 2.0, step: 0.10 });
    }
  }

  function patchElement(name) {
    customElements.whenDefined(name).then(() => {
      const ctor = customElements.get(name);
      const proto = ctor?.prototype;
      if (!proto || proto[PATCH_FLAG]) return;

      const originalRender = proto._render;
      if (typeof originalRender !== "function") return;

      Object.defineProperty(proto, PATCH_FLAG, { value: true });
      proto._render = function (...args) {
        const result = originalRender.apply(this, args);
        queueMicrotask(() => ensureShell(this));
        return result;
      };

      const originalConnected = proto.connectedCallback;
      proto.connectedCallback = function (...args) {
        const result = typeof originalConnected === "function"
          ? originalConnected.apply(this, args)
          : undefined;
        queueMicrotask(() => ensureShell(this));
        return result;
      };
    });
  }

  for (const name of TARGETS) patchElement(name);

  window.NikasSpecializedPanelShell = Object.freeze({
    register: patchElement,
    ensure: ensureShell,
  });
})();
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
      this._selectedDeviceId = null;
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
          :host{display:block;width:100%;height:100dvh;overflow:hidden;background:var(--primary-background-color,#f6f7f9);color:var(--primary-text-color,#111827);font-family:var(--paper-font-body1_-_font-family,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif)}
          *{box-sizing:border-box}.app{height:100dvh;display:grid;grid-template-rows:auto auto minmax(0,1fr);overflow:hidden}
          .header{z-index:20;display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;min-height:62px;padding:max(5px,env(safe-area-inset-top,0px)) max(8px,env(safe-area-inset-right,0px)) 5px max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-bottom:1px solid var(--divider-color,rgba(127,127,127,.18))}
          .rail{width:44px;height:44px;border:1px solid var(--divider-color,rgba(127,127,127,.18));border-radius:16px;display:grid;place-items:center;background:var(--card-background-color,var(--ha-card-background,#fff));color:var(--primary-text-color,#111827);box-shadow:0 7px 20px rgba(23,45,76,.08);cursor:pointer;-webkit-tap-highlight-color:transparent}.rail ha-icon{--mdc-icon-size:25px}.rail#refresh{color:var(--primary-color,#03a9f4)}
          .heading{min-width:0;text-align:center;line-height:1.12}.heading strong,.heading span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.heading strong{font-size:21px;font-weight:800;letter-spacing:-.02em}.heading span{margin-top:3px;font-size:12px;font-weight:560;color:var(--secondary-text-color,#6b7280)}
          .peer-selector:empty{display:none}.peer-selector{z-index:15;padding:8px 16px 0;background:var(--primary-background-color,#f6f7f9)}.peer-selector .device-selector{width:min(100%,1120px);margin:0 auto}
          .canvas-viewport{position:relative;min-width:0;min-height:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior-x:none;overscroll-behavior-y:contain;touch-action:pan-y}.canvas-viewport.zoomed{overflow:hidden;overscroll-behavior:none;touch-action:none;user-select:none;-webkit-user-select:none}
          .work-canvas{position:relative;width:min(calc(100% - 32px),1120px);min-height:100%;margin:0 auto;padding:18px 0 82px;transform-origin:0 0;visibility:hidden}.work-canvas.ready{visibility:visible}.canvas-viewport.zoomed .work-canvas{position:absolute;left:16px;right:16px;width:auto;margin:0}
          .hero,.card{border:1px solid var(--divider-color,rgba(127,127,127,.22));background:var(--card-background-color,var(--ha-card-background,#fff));border-radius:24px}.hero{padding:22px;position:relative;overflow:hidden}.hero::after{content:"";position:absolute;right:-46px;top:-54px;width:150px;height:150px;border-radius:50%;background:color-mix(in srgb,var(--primary-color,#03a9f4) 12%,transparent)}
          .eyebrow{font-size:11px;letter-spacing:.13em;font-weight:800;color:var(--secondary-text-color,#6b7280)}.hero-line{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-top:7px}.hero h1{margin:0;font-size:34px;line-height:1.04;letter-spacing:-.035em;font-weight:820}.hero p{margin:8px 0 0;color:var(--secondary-text-color,#6b7280);font-size:15px;line-height:1.4}.badge{position:relative;z-index:1;display:inline-flex;align-items:center;gap:7px;padding:9px 12px;border-radius:999px;background:color-mix(in srgb,var(--success-color,#43a047) 12%,var(--card-background-color,#fff));color:var(--success-color,#43a047);font-weight:750;white-space:nowrap}.badge.neutral{background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--secondary-text-color,#6b7280)}.badge.warn{background:color-mix(in srgb,var(--warning-color,#ff9800) 14%,var(--card-background-color,#fff));color:var(--warning-color,#ff9800)}.badge ha-icon{--mdc-icon-size:19px}
          .card{margin-top:14px;padding:20px}.card-title{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:780}.card-title ha-icon{color:var(--primary-color,#03a9f4);--mdc-icon-size:25px}.placeholder{margin-top:14px;padding:16px;border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.08));font-size:15px;line-height:1.5;color:var(--primary-text-color,#111827)}.unreliable-box{border:1px solid color-mix(in srgb,var(--warning-color,#ff9800) 35%,transparent)}.meta{margin-top:12px;color:var(--secondary-text-color,#6b7280);font-size:12px;line-height:1.45}
          .device-block{margin-top:18px}.device-block:first-of-type{margin-top:14px}.device-heading{display:flex;align-items:center;gap:9px;font-size:18px;font-weight:780}.device-heading ha-icon{--mdc-icon-size:23px;color:var(--secondary-text-color,#6b7280)}
          .device-selector{display:flex;gap:8px;overflow-x:auto;margin-top:14px;padding-bottom:2px;scrollbar-width:none}.device-selector::-webkit-scrollbar{display:none}.device-button{appearance:none;border:1px solid var(--divider-color,rgba(127,127,127,.22));background:var(--secondary-background-color,rgba(127,127,127,.05));color:var(--secondary-text-color,#6b7280);min-height:44px;padding:8px 13px;border-radius:15px;display:inline-flex;align-items:center;gap:7px;font:inherit;font-size:13px;font-weight:700;white-space:nowrap}.device-button.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);border-color:color-mix(in srgb,var(--primary-color,#03a9f4) 28%,var(--divider-color,transparent))}.device-button ha-icon{--mdc-icon-size:20px}
          .stats{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}.chip{display:inline-flex;align-items:center;min-height:28px;padding:5px 9px;border-radius:999px;background:var(--secondary-background-color,rgba(127,127,127,.08));color:var(--secondary-text-color,#6b7280);font-size:11px;font-weight:650}.chip.strong{color:var(--primary-text-color,#111827);font-weight:760}
          .entity-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}.entity{min-width:0;display:grid;grid-template-columns:38px minmax(0,1fr) auto;align-items:center;gap:10px;padding:12px 13px;border:1px solid var(--divider-color,rgba(127,127,127,.18));border-radius:18px;background:var(--secondary-background-color,rgba(127,127,127,.045))}.entity.unreliable{border-color:color-mix(in srgb,var(--warning-color,#ff9800) 38%,var(--divider-color,transparent))}.entity-icon{width:38px;height:38px;border-radius:13px;display:grid;place-items:center;background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,transparent);color:var(--primary-color,#03a9f4)}.entity-icon ha-icon{--mdc-icon-size:21px}.entity-copy{min-width:0}.entity-name,.entity-secondary{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity-name{font-size:14px;font-weight:720}.entity-secondary{margin-top:2px;font-size:10.5px;color:var(--secondary-text-color,#6b7280)}.entity-state{max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right;font-size:13px;font-weight:760}
          .bottom{position:fixed;z-index:20;left:0;right:0;bottom:0;padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));background:var(--card-background-color,var(--ha-card-background,#fff));border-top:1px solid var(--divider-color,rgba(127,127,127,.18));box-shadow:0 -4px 18px rgba(0,0,0,.08)}
          nav{width:min(100%,720px);margin:0 auto;display:grid;grid-template-columns:repeat(${tabs.length},minmax(0,1fr));gap:4px}.tab{appearance:none;border:0;background:transparent;color:var(--secondary-text-color,#6b7280);min-width:0;min-height:52px;padding:4px 2px;border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}.tab ha-icon{--mdc-icon-size:28px;width:28px;height:28px}.tab span{width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;font-size:12px;line-height:15px;font-weight:700}.tab.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 11%,transparent);cursor:default}
          .scale-status{position:absolute;z-index:40;left:50%;bottom:calc(76px + env(safe-area-inset-bottom,0px));transform:translate(-50%,10px);opacity:0;pointer-events:none;padding:9px 14px;border-radius:999px;background:rgba(20,27,34,.88);color:#fff;font-size:13px;font-weight:720;transition:opacity .14s ease,transform .14s ease}.scale-status.visible{opacity:1;transform:translate(-50%,0)}
          @media(max-width:680px){.entity-grid{grid-template-columns:1fr}}@media(max-width:390px){.header{grid-template-columns:48px minmax(0,1fr) 48px;min-height:60px}.hero h1{font-size:30px}.hero{padding:19px}.card{padding:18px}.badge{font-size:13px;padding:8px 10px}.entity-state{max-width:115px}}
          @media(min-width:900px){.work-canvas{padding-top:22px}.hero h1{font-size:38px}}
        </style>
        <div class="app">
          <header class="header">
            <button class="rail" id="menu" type="button" aria-label="Меню Home Assistant"><ha-icon icon="mdi:menu"></ha-icon></button>
            <div class="heading"><strong>${escapeHtml(config.title)}</strong><span>${escapeHtml(config.subtitle || config.parent?.title || "")}</span></div>
            <button class="rail" id="refresh" type="button" aria-label="Обновить"><ha-icon icon="mdi:refresh"></ha-icon></button>
          </header>
          <div class="peer-selector">${this._peerSelectorHtml(active)}</div>
          <main class="canvas-viewport">
            <div class="work-canvas">
              <section class="hero">${this._heroHtml(config)}</section>
              <section class="card">
                <div class="card-title"><ha-icon icon="${escapeHtml(active.icon || "mdi:view-dashboard-outline")}"></ha-icon><span>${escapeHtml(active.label || active.id)}</span></div>
                ${this._contentHtml(config, active)}
              </section>
            </div>
          </main>
          <div class="bottom"><nav>${navButtons}</nav></div>
          <div class="scale-status" role="status" aria-live="polite">Масштаб 100%</div>
        </div>`;

      this.shadowRoot.getElementById("menu").onclick = () => this._toggleMenu();
      this.shadowRoot.getElementById("refresh").onclick = () => this._refresh();
      for (const button of this.shadowRoot.querySelectorAll("button[data-tab]")) {
        button.onclick = () => this._selectTab(button.dataset.tab);
      }
      for (const button of this.shadowRoot.querySelectorAll("button[data-device]")) {
        button.onclick = () => this._selectDevice(button.dataset.device);
      }
    }
  }

  customElements.define(ELEMENT_NAME, NikasGeneratedSubpanel);
})();
