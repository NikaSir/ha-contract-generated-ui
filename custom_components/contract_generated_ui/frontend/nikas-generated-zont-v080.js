// ZONT UI v0.8.0 header shell.
// Canonical source: NikaSir/ha-zont. Loaded by Contract Generated UI.
import "/contract_generated_ui/frontend/nikas-generated-zont.js";

const ELEMENT_NAME = "nikas-generated-zont";

function installHeaderV080() {
  const ElementClass = customElements.get(ELEMENT_NAME);
  if (!ElementClass || ElementClass.prototype.__zontHeaderV080) return false;
  const originalRender = ElementClass.prototype._render;
  if (typeof originalRender !== "function") return false;

  ElementClass.prototype._render = function patchedRender(...args) {
    const result = originalRender.apply(this, args);
    const root = this.shadowRoot;
    if (!root) return result;

    if (!root.getElementById("zont-header-v080-style")) {
      const style = document.createElement("style");
      style.id = "zont-header-v080-style";
      style.textContent = `
        .header{grid-template-columns:minmax(92px,1fr) auto minmax(92px,1fr)!important;min-height:92px!important;padding:max(10px,env(safe-area-inset-top,0px)) 20px 10px!important;border-bottom:1px solid var(--divider-color,#e3e3e3)!important;box-shadow:none!important}
        .rail{width:auto!important;min-width:52px;height:48px!important;padding:0!important;display:flex!important;align-items:center!important;gap:6px;font:inherit;font-size:16px;font-weight:650}
        #back{justify-self:start}#refresh{justify-self:end;color:var(--primary-color,#009fc2)!important}.rail ha-icon{--mdc-icon-size:31px!important}
        .heading{align-self:center;line-height:1.15}.heading strong{font-size:24px!important;font-weight:750!important;letter-spacing:-.25px}.heading span{margin-top:5px!important;font-size:14px!important;font-weight:450;color:var(--secondary-text-color,#666)!important}
        @media(max-width:420px){.header{grid-template-columns:minmax(76px,1fr) auto minmax(76px,1fr)!important;min-height:86px!important;padding-left:14px!important;padding-right:14px!important}.rail{font-size:14px;gap:3px}.heading strong{font-size:22px!important}.heading span{font-size:12.5px!important}}
      `;
      root.appendChild(style);
    }

    const back = root.getElementById("back");
    if (back && !back.querySelector(".back-label")) {
      const label = document.createElement("span");
      label.className = "back-label";
      label.textContent = "Назад";
      back.appendChild(label);
    }

    const heading = root.querySelector(".heading span");
    if (heading) {
      const base = String(heading.textContent || "Отопление и ГВС").replace(/\s*·\s*UI\s*v?[0-9.]+\s*$/i, "");
      heading.textContent = `${base} · UI v0.8.0`;
    }
    return result;
  };

  ElementClass.prototype.__zontHeaderV080 = true;
  return true;
}

if (!installHeaderV080()) customElements.whenDefined(ELEMENT_NAME).then(() => installHeaderV080());
