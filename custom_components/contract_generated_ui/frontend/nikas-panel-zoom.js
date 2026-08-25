// Shared zoom controller for specialized NikaS Home Assistant panels.
// It scales only the work area (<main>); panel header, zoom controls, HA chrome and bottom navigation stay native.
(() => {
  if (window.NikasPanelZoom?.version === 1) return;

  const DEFAULT_MIN = 0.75;
  const DEFAULT_MAX = 2.0;
  const DEFAULT_STEP = 0.10;
  const AUTO_TARGETS = new Set(["NIKAS-GENERATED-SUBPANEL", "NIKAS-GENERATED-ZONT"]);
  const controllers = new WeakMap();

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const finite = (value, fallback) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  class ZoomController {
    constructor(host, options = {}) {
      this.host = host;
      this.options = options;
      this.root = host.shadowRoot || host;
      this.main = null;
      this.scale = this._loadScale();
      this.pinch = null;
      this._boundStart = (event) => this._touchStart(event);
      this._boundMove = (event) => this._touchMove(event);
      this._boundEnd = (event) => this._touchEnd(event);
      this.observer = new MutationObserver(() => queueMicrotask(() => this.bind()));
      this.observer.observe(this.root, { childList: true, subtree: true });
      this.bind();
    }

    _min() { return clamp(finite(this.options.min, DEFAULT_MIN), 0.25, 1); }
    _max() { return clamp(finite(this.options.max, DEFAULT_MAX), 1, 4); }
    _step() { return clamp(finite(this.options.step, DEFAULT_STEP), 0.01, 0.5); }

    _panelKey() {
      const config = this.host?.panel?.config || this.host?.panel || {};
      return this.options.key || config.id || this.host.getAttribute?.("data-nikas-panel-id") || this.host.localName || "specialized-panel";
    }

    _storageKey() {
      return `nikas:panel-zoom:v1:${window.location.pathname}:${this._panelKey()}`;
    }

    _loadScale() {
      try {
        return clamp(finite(window.localStorage.getItem(this._storageKey()), 1), this._min(), this._max());
      } catch (_error) {
        return 1;
      }
    }

    _saveScale() {
      try {
        window.localStorage.setItem(this._storageKey(), this.scale.toFixed(3));
      } catch (_error) {
        // Private/hardened WebViews may reject storage. Session zoom still works.
      }
    }

    bind() {
      const main = this.root.querySelector?.("main");
      if (!main) return;
      if (main !== this.main) {
        this._detachMain();
        this.main = main;
        this.main.style.transformOrigin = "0 0";
        this.main.style.touchAction = "pan-x pan-y";
        this.main.addEventListener("touchstart", this._boundStart, { passive: false });
        this.main.addEventListener("touchmove", this._boundMove, { passive: false });
        this.main.addEventListener("touchend", this._boundEnd, { passive: false });
        this.main.addEventListener("touchcancel", this._boundEnd, { passive: false });
      }
      this.host.style.overflowX = "auto";
      this.host.style.overscrollBehaviorX = "contain";
      this._ensureControls();
      this._applyScale();
    }

    _detachMain() {
      if (!this.main) return;
      this.main.removeEventListener("touchstart", this._boundStart);
      this.main.removeEventListener("touchmove", this._boundMove);
      this.main.removeEventListener("touchend", this._boundEnd);
      this.main.removeEventListener("touchcancel", this._boundEnd);
      this.main = null;
    }

    _ensureControls() {
      if (this.root.querySelector?.("[data-nikas-zoom-controls]")) return;
      const style = document.createElement("style");
      style.dataset.nikasZoomStyle = "1";
      style.textContent = `
        [data-nikas-zoom-controls]{position:fixed;z-index:35;right:max(12px,env(safe-area-inset-right,0px));bottom:calc(86px + env(safe-area-inset-bottom,0px));display:grid;grid-template-columns:40px 58px 40px;align-items:center;min-height:40px;padding:3px;border:1px solid var(--divider-color,rgba(127,127,127,.22));border-radius:16px;background:color-mix(in srgb,var(--card-background-color,var(--ha-card-background,#fff)) 94%,transparent);box-shadow:0 4px 18px rgba(0,0,0,.13);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
        [data-nikas-zoom-controls] button{appearance:none;border:0;background:transparent;color:var(--primary-text-color,#111827);min-width:40px;height:38px;border-radius:12px;font:inherit;font-size:22px;font-weight:650;line-height:1;display:grid;place-items:center;-webkit-tap-highlight-color:transparent;cursor:pointer}
        [data-nikas-zoom-controls] button:active{background:var(--secondary-background-color,rgba(127,127,127,.12))}
        [data-nikas-zoom-controls] button:disabled{opacity:.32;cursor:default}
        [data-nikas-zoom-percent]{font-size:12px!important;font-weight:760!important;letter-spacing:-.01em}
        @media(min-width:900px){[data-nikas-zoom-controls]{right:20px;bottom:94px}}
      `;
      const controls = document.createElement("div");
      controls.dataset.nikasZoomControls = "1";
      controls.setAttribute("aria-label", "Масштаб панели");
      controls.innerHTML = `
        <button type="button" data-nikas-zoom-minus aria-label="Уменьшить масштаб">−</button>
        <button type="button" data-nikas-zoom-percent aria-label="Сбросить масштаб до 100 процентов">100%</button>
        <button type="button" data-nikas-zoom-plus aria-label="Увеличить масштаб">+</button>`;
      controls.querySelector("[data-nikas-zoom-minus]").onclick = () => this.stepBy(-1);
      controls.querySelector("[data-nikas-zoom-plus]").onclick = () => this.stepBy(1);
      controls.querySelector("[data-nikas-zoom-percent]").onclick = () => this.setScale(1, this._visibleCenter());
      this.root.append(style, controls);
    }

    _distance(touches) {
      const dx = touches[0].clientX - touches[1].clientX;
      const dy = touches[0].clientY - touches[1].clientY;
      return Math.hypot(dx, dy);
    }

    _focal(touches) {
      return { x: (touches[0].clientX + touches[1].clientX) / 2, y: (touches[0].clientY + touches[1].clientY) / 2 };
    }

    _visibleCenter() {
      if (!this.main) return null;
      const rect = this.main.getBoundingClientRect();
      const top = Math.max(rect.top, 0);
      const bottom = Math.min(rect.bottom, window.innerHeight);
      return { x: Math.max(rect.left, 0) + Math.min(rect.width, window.innerWidth) / 2, y: top + Math.max(0, bottom - top) / 2 };
    }

    _touchStart(event) {
      if (event.touches.length !== 2) return;
      const distance = this._distance(event.touches);
      if (!distance) return;
      this.pinch = { distance, scale: this.scale };
      event.preventDefault();
    }

    _touchMove(event) {
      if (!this.pinch || event.touches.length !== 2) return;
      const distance = this._distance(event.touches);
      if (!distance) return;
      this.setScale(this.pinch.scale * (distance / this.pinch.distance), this._focal(event.touches), false);
      event.preventDefault();
    }

    _touchEnd(event) {
      if (!this.pinch || event.touches.length >= 2) return;
      this.pinch = null;
      this._saveScale();
    }

    stepBy(direction) {
      const next = Math.round((this.scale + direction * this._step()) * 100) / 100;
      this.setScale(next, this._visibleCenter());
    }

    setScale(value, focal = null, persist = true) {
      const next = clamp(finite(value, 1), this._min(), this._max());
      if (Math.abs(next - this.scale) < 0.001) {
        if (persist) this._saveScale();
        return;
      }

      const old = this.scale;
      const rect = this.main?.getBoundingClientRect();
      const hostScrollLeft = this.host.scrollLeft || 0;
      let contentX = null;
      let contentY = null;
      let localX = null;
      let topDocument = null;

      if (rect && focal) {
        localX = focal.x - rect.left;
        contentX = (hostScrollLeft + localX) / old;
        topDocument = rect.top + window.scrollY;
        contentY = (window.scrollY + focal.y - topDocument) / old;
      }

      this.scale = next;
      this._applyScale();

      if (focal && contentX !== null) {
        this.host.scrollLeft = Math.max(0, contentX * next - localX);
        if (contentY !== null && topDocument !== null) {
          window.scrollTo(window.scrollX, Math.max(0, topDocument + contentY * next - focal.y));
        }
      }
      if (persist) this._saveScale();
    }

    _applyScale() {
      this.scale = clamp(this.scale, this._min(), this._max());
      if (this.main) this.main.style.zoom = String(this.scale);
      const percent = this.root.querySelector?.("[data-nikas-zoom-percent]");
      const minus = this.root.querySelector?.("[data-nikas-zoom-minus]");
      const plus = this.root.querySelector?.("[data-nikas-zoom-plus]");
      if (percent) percent.textContent = `${Math.round(this.scale * 100)}%`;
      if (minus) minus.disabled = this.scale <= this._min() + 0.001;
      if (plus) plus.disabled = this.scale >= this._max() - 0.001;
    }

    destroy() {
      this.observer.disconnect();
      this._detachMain();
    }
  }

  function isTarget(element) {
    return AUTO_TARGETS.has(element.tagName) || element.getAttribute?.("data-nikas-panel-zoom") === "true";
  }

  function attach(host, options = {}) {
    if (!host || !host.shadowRoot) return null;
    const existing = controllers.get(host);
    if (existing) return existing;
    const controller = new ZoomController(host, options);
    controllers.set(host, controller);
    return controller;
  }

  function discover(root = document) {
    const visit = (node) => {
      if (!node) return;
      if (node.nodeType === Node.ELEMENT_NODE) {
        if (isTarget(node)) attach(node);
        if (node.shadowRoot) visit(node.shadowRoot);
      }
      const children = node.children || node.childNodes || [];
      for (const child of children) visit(child);
    };
    visit(root);
  }

  window.NikasPanelZoom = { version: 1, attach, discover, defaults: { min: DEFAULT_MIN, max: DEFAULT_MAX, step: DEFAULT_STEP } };

  const observer = new MutationObserver((records) => {
    for (const record of records) for (const node of record.addedNodes) discover(node);
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
  discover(document);
  window.setInterval(() => discover(document), 1500);
})();
