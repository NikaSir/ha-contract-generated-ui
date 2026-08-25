// Shared application-chrome policy for specialized NikaS panels.
// Owns safe-area Header/Bottom Tab Bar geometry and inserts the common zoom viewport.
(() => {
  const TARGETS = ["nikas-generated-subpanel", "nikas-generated-zont"];
  const PATCH_FLAG = Symbol.for("nikas.specializedPanelShell.patched");
  const STYLE_ID = "nikas-specialized-panel-shell-policy";

  function panelKey(host) {
    const config = host?.panel?.config || host?.panel || {};
    return String(config.id || window.location.pathname || host.localName || "specialized-panel");
  }

  function policyCss() {
    return `
      .app{padding-bottom:calc(82px + env(safe-area-inset-bottom,0px))!important}
      .header{
        top:0!important;
        grid-template-columns:52px minmax(0,1fr) 52px!important;
        min-height:70px!important;
        padding:
          max(6px,env(safe-area-inset-top,0px))
          max(10px,env(safe-area-inset-right,0px))
          6px
          max(10px,env(safe-area-inset-left,0px))!important;
      }
      .header .rail{min-width:44px;min-height:44px}
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
        .header{grid-template-columns:48px minmax(0,1fr) 48px!important}
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

  function ensureZoomViewport(host) {
    const root = host?.shadowRoot;
    if (!root || !customElements.get("nikas-panel-zoom")) return;
    ensurePolicyStyle(root);

    const main = root.querySelector(".app > main");
    if (!main) return;
    if (main.parentElement?.localName === "nikas-panel-zoom") {
      main.parentElement.setAttribute("panel-key", panelKey(host));
      return;
    }

    const zoom = document.createElement("nikas-panel-zoom");
    zoom.setAttribute("panel-key", panelKey(host));
    zoom.setAttribute("min", "0.75");
    zoom.setAttribute("max", "2");
    zoom.setAttribute("step", "0.10");
    main.replaceWith(zoom);
    zoom.appendChild(main);
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
        queueMicrotask(() => ensureZoomViewport(this));
        return result;
      };

      const originalConnected = proto.connectedCallback;
      proto.connectedCallback = function (...args) {
        const result = typeof originalConnected === "function"
          ? originalConnected.apply(this, args)
          : undefined;
        queueMicrotask(() => ensureZoomViewport(this));
        return result;
      };
    });
  }

  for (const name of TARGETS) patchElement(name);

  window.NikasSpecializedPanelShell = Object.freeze({
    register: patchElement,
    ensure: ensureZoomViewport,
  });
})();
