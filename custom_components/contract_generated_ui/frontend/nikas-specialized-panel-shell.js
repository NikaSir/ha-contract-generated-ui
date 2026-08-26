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
      .header .rail ha-icon{--mdc-icon-size:25px!important;width:25px!important;height:25px!important}
      .header .heading{text-align:center;min-width:0}
      .header .heading strong{font-size:23px!important;font-weight:800!important}
      .header .heading span{font-size:14px!important;font-weight:560!important}
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
      .bottom nav .tab{min-height:52px!important;border-radius:16px!important}
      .bottom nav .tab ha-icon{--mdc-icon-size:28px!important;width:28px!important;height:28px!important}
      .bottom nav .tab span{font-size:12px!important;line-height:15px!important;font-weight:700!important}
      @media(max-width:680px){
        :host{position:fixed!important;inset:0!important;width:auto!important;height:auto!important;min-height:0!important}
      }
      @media(max-width:390px){
        .header{grid-template-columns:48px minmax(0,1fr) 48px!important;min-height:60px!important}
        .header .heading strong{font-size:21px!important}
        .header .heading span{font-size:13px!important}
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
