// Shared zoom viewport for specialized NikaS Home Assistant panels.
// Scales only assigned panel work content; shell/header/navigation stay at native scale.
(() => {
  const ELEMENT_NAME = "nikas-panel-zoom";
  if (customElements.get(ELEMENT_NAME)) return;

  const DEFAULT_MIN = 0.75;
  const DEFAULT_MAX = 2.0;
  const DEFAULT_STEP = 0.10;

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const finite = (value, fallback) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  class NikasPanelZoom extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._scale = 1;
      this._pinch = null;
      this._boundTouchStart = (event) => this._touchStart(event);
      this._boundTouchMove = (event) => this._touchMove(event);
      this._boundTouchEnd = (event) => this._touchEnd(event);
    }

    connectedCallback() {
      this._render();
      this._scale = this._loadScale();
      this._applyScale(false);
      this._installTouchHandlers();
    }

    disconnectedCallback() {
      this._removeTouchHandlers();
    }

    static get observedAttributes() {
      return ["panel-key", "min", "max", "step"];
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (oldValue === newValue || !this.isConnected) return;
      if (name === "panel-key") this._scale = this._loadScale();
      this._applyScale(false);
    }

    _min() { return clamp(finite(this.getAttribute("min"), DEFAULT_MIN), 0.25, 1); }
    _max() { return clamp(finite(this.getAttribute("max"), DEFAULT_MAX), 1, 4); }
    _step() { return clamp(finite(this.getAttribute("step"), DEFAULT_STEP), 0.01, 0.5); }

    _storageKey() {
      const panelKey = this.getAttribute("panel-key") || window.location.pathname || "specialized-panel";
      return `nikas:panel-zoom:v1:${window.location.pathname}:${panelKey}`;
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
        window.localStorage.setItem(this._storageKey(), this._scale.toFixed(3));
      } catch (_error) {
        // Storage can be unavailable in hardened/private WebViews. Zoom still works for this session.
      }
    }

    _render() {
      this.shadowRoot.innerHTML = `
        <style>
          :host{display:block;min-width:0;position:relative}
          *{box-sizing:border-box}
          .viewport{min-width:0;width:100%;overflow-x:auto;overflow-y:visible;overscroll-behavior-x:contain;scrollbar-width:thin;touch-action:pan-x pan-y;-webkit-overflow-scrolling:touch}
          .scaled{display:block;min-width:100%;transform-origin:0 0;zoom:var(--nika-panel-scale,1)}
          .controls{position:fixed;z-index:35;right:max(12px,env(safe-area-inset-right,0px));bottom:calc(86px + env(safe-area-inset-bottom,0px));display:grid;grid-template-columns:40px 58px 40px;align-items:center;min-height:40px;padding:3px;border:1px solid var(--divider-color,rgba(127,127,127,.22));border-radius:16px;background:color-mix(in srgb,var(--card-background-color,var(--ha-card-background,#fff)) 94%,transparent);box-shadow:0 4px 18px rgba(0,0,0,.13);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
          button{appearance:none;border:0;background:transparent;color:var(--primary-text-color,#111827);min-width:40px;height:38px;border-radius:12px;font:inherit;font-size:22px;font-weight:650;line-height:1;display:grid;place-items:center;-webkit-tap-highlight-color:transparent;cursor:pointer}
          button:active{background:var(--secondary-background-color,rgba(127,127,127,.12))}
          button:disabled{opacity:.32;cursor:default}
          .percent{font-size:12px;font-weight:760;letter-spacing:-.01em}
          @media(min-width:900px){.controls{right:20px;bottom:94px}}
        </style>
        <div class="viewport" part="viewport">
          <div class="scaled" part="content"><slot></slot></div>
        </div>
        <div class="controls" part="controls" aria-label="Масштаб панели">
          <button id="minus" type="button" aria-label="Уменьшить масштаб">−</button>
          <button id="percent" class="percent" type="button" aria-label="Сбросить масштаб до 100 процентов">100%</button>
          <button id="plus" type="button" aria-label="Увеличить масштаб">+</button>
        </div>`;
      this.shadowRoot.getElementById("minus").onclick = () => this._stepBy(-1);
      this.shadowRoot.getElementById("plus").onclick = () => this._stepBy(1);
      this.shadowRoot.getElementById("percent").onclick = () => this._setScale(1, this._viewportCenter());
    }

    _viewport() { return this.shadowRoot?.querySelector(".viewport") || null; }
    _scaled() { return this.shadowRoot?.querySelector(".scaled") || null; }

    _installTouchHandlers() {
      const viewport = this._viewport();
      if (!viewport) return;
      viewport.addEventListener("touchstart", this._boundTouchStart, { passive: false });
      viewport.addEventListener("touchmove", this._boundTouchMove, { passive: false });
      viewport.addEventListener("touchend", this._boundTouchEnd, { passive: false });
      viewport.addEventListener("touchcancel", this._boundTouchEnd, { passive: false });
    }

    _removeTouchHandlers() {
      const viewport = this._viewport();
      if (!viewport) return;
      viewport.removeEventListener("touchstart", this._boundTouchStart);
      viewport.removeEventListener("touchmove", this._boundTouchMove);
      viewport.removeEventListener("touchend", this._boundTouchEnd);
      viewport.removeEventListener("touchcancel", this._boundTouchEnd);
    }

    _distance(touches) {
      const dx = touches[0].clientX - touches[1].clientX;
      const dy = touches[0].clientY - touches[1].clientY;
      return Math.hypot(dx, dy);
    }

    _focal(touches) {
      return {
        x: (touches[0].clientX + touches[1].clientX) / 2,
        y: (touches[0].clientY + touches[1].clientY) / 2,
      };
    }

    _viewportCenter() {
      const viewport = this._viewport();
      if (!viewport) return null;
      const rect = viewport.getBoundingClientRect();
      const visibleTop = Math.max(rect.top, 0);
      const visibleBottom = Math.min(rect.bottom, window.innerHeight);
      return { x: rect.left + rect.width / 2, y: visibleTop + Math.max(0, visibleBottom - visibleTop) / 2 };
    }

    _touchStart(event) {
      if (event.touches.length !== 2) return;
      const distance = this._distance(event.touches);
      if (!distance) return;
      this._pinch = { distance, scale: this._scale };
      event.preventDefault();
    }

    _touchMove(event) {
      if (!this._pinch || event.touches.length !== 2) return;
      const distance = this._distance(event.touches);
      if (!distance) return;
      const next = this._pinch.scale * (distance / this._pinch.distance);
      this._setScale(next, this._focal(event.touches), false);
      event.preventDefault();
    }

    _touchEnd(event) {
      if (!this._pinch) return;
      if (event.touches.length >= 2) return;
      this._pinch = null;
      this._saveScale();
    }

    _stepBy(direction) {
      const raw = this._scale + direction * this._step();
      const next = Math.round(raw * 100) / 100;
      this._setScale(next, this._viewportCenter());
    }

    _setScale(value, focal = null, persist = true) {
      const next = clamp(finite(value, 1), this._min(), this._max());
      if (Math.abs(next - this._scale) < 0.001) {
        if (persist) this._saveScale();
        return;
      }

      const viewport = this._viewport();
      const oldScale = this._scale;
      let contentX = null;
      let contentY = null;
      let localX = null;
      let contentTopDocument = null;

      if (viewport && focal) {
        const rect = viewport.getBoundingClientRect();
        localX = focal.x - rect.left;
        contentX = (viewport.scrollLeft + localX) / oldScale;
        contentTopDocument = rect.top + window.scrollY;
        contentY = (window.scrollY + focal.y - contentTopDocument) / oldScale;
      }

      this._scale = next;
      this._applyScale(false);

      if (viewport && focal && contentX !== null) {
        viewport.scrollLeft = Math.max(0, contentX * next - localX);
        if (contentY !== null && contentTopDocument !== null) {
          const targetScrollY = contentTopDocument + contentY * next - focal.y;
          window.scrollTo(window.scrollX, Math.max(0, targetScrollY));
        }
      }

      if (persist) this._saveScale();
    }

    _applyScale(persist = false) {
      this._scale = clamp(this._scale, this._min(), this._max());
      const scaled = this._scaled();
      if (scaled) scaled.style.setProperty("--nika-panel-scale", String(this._scale));
      const percent = this.shadowRoot?.getElementById("percent");
      if (percent) percent.textContent = `${Math.round(this._scale * 100)}%`;
      const minus = this.shadowRoot?.getElementById("minus");
      const plus = this.shadowRoot?.getElementById("plus");
      if (minus) minus.disabled = this._scale <= this._min() + 0.001;
      if (plus) plus.disabled = this._scale >= this._max() - 0.001;
      if (persist) this._saveScale();
    }
  }

  customElements.define(ELEMENT_NAME, NikasPanelZoom);
})();
