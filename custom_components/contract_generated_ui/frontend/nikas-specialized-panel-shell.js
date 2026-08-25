// Shared application-chrome policy for specialized NikaS panels.
// Owns safe-area Header/Bottom Tab Bar geometry and binds the common zoom controller to <main>.
(() => {
  const TARGETS = ["nikas-generated-subpanel", "nikas-generated-zont"];
  const PATCH_FLAG = Symbol.for("nikas.specializedPanelShell.patched");
  const STYLE_ID = "nikas-specialized-panel-shell-policy";

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

  function ensureShell(host) {
    const root = host?.shadowRoot;
    if (!root) return;
    ensurePolicyStyle(root);

    // Zoom controller scales only the work <main>. Header, controls and bottom
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
