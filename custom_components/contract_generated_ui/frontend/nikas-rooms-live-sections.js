const ROOT_PREFIX = "/dashboard-rooms/room-";
const ROOT_ID = "nikas-room-live-sections-runtime";
const ACTIVE_LABEL_ID = "v_ekspluatatsii";
const CLIMATE_LABEL_ID = "datchik_klimata_pomeshcheniia";
const EXCLUDED = new Set(["rezerv", "na_obsluzhivanii", "trebuet_zameny", "vyvedeno_iz_ekspluatatsii"]);
const ROOM_NAMES = Object.freeze({bathroom:"Ванная",bedroom:"Спальня",wardrobe:"Гардероб",sasha:"У Саши",ilya:"У Ильи",stairs:"Лестница",corridor:"Коридор",hall:"Холл",boiler:"Котельная",kitchen:"Кухня",dining:"Столовая",living:"Гостиная",toilet:"Туалет",vestibule:"Тамбур",veranda:"Веранда",garage:"Гараж",attic:"Чердак",greenhouse:"Теплица"});
let timer=null, cache=null, cacheAt=0, mounted=null;
const hiddenHosts=new Set();
function slug(){const p=window.location.pathname;if(!p.startsWith(ROOT_PREFIX))return null;return p.slice(ROOT_PREFIX.length).split("/")[0]||null;}
function norm(v){return String(v||"").trim().toLocaleLowerCase("ru-RU").replace(/ё/g,"е").replace(/\s+/g," ");}
function normArea(v){return norm(v).replace(/^\d+(?:[.,]\d+)?\s*(?:[-–—.:)]\s*)?/,"").trim();}
function findArea(areas,name){const n=norm(name);return (areas||[]).find(a=>norm(a?.name)===n||normArea(a?.name)===n)||null;}
function labels(x){const v=x?.labels;if(!v)return[];if(Array.isArray(v))return v;if(v instanceof Set)return[...v];if(typeof v==="object")return Object.keys(v).filter(k=>v[k]);return[];}
function operational(x){const s=new Set(labels(x));return s.has(ACTIVE_LABEL_ID)&&![...EXCLUDED].some(id=>s.has(id));}
function walk(root,fn){const stack=[root],seen=new Set();while(stack.length){const r=stack.pop();if(!r||seen.has(r))continue;seen.add(r);for(const n of r.querySelectorAll?.("*")||[]){fn(n);if(n.shadowRoot)stack.push(n.shadowRoot);}}}
function hass(){const h=document.querySelector("home-assistant")?.hass;if(h)return h;let found=null;walk(document,n=>{if(!found&&n?.hass?.callWS)found=n.hass;});return found;}
async function registries(h){if(cache&&Date.now()-cacheAt<15000)return cache;const [areas,devices,entities]=await Promise.all([h.callWS({type:"config/area_registry/list"}),h.callWS({type:"config/device_registry/list"}),h.callWS({type:"config/entity_registry/list"})]);cache={areas,devices,entities};cacheAt=Date.now();return cache;}
function mountHost(){let x=null;walk(document,n=>{if(!x&&(n.localName==="hui-view"||n.localName==="hui-panel-view"))x=n;});return x;}
function stateClass(h,e){return h.states?.[e.entity_id]?.attributes?.device_class||e.device_class||e.original_device_class||"";}
function effectiveArea(e,dm){return e.area_id||(e.device_id?dm.get(e.device_id)?.area_id:null);}
function title(e,h){return e.name||h.states?.[e.entity_id]?.attributes?.friendly_name||e.original_name||e.entity_id;}
function deviceTitle(d){return d?.name_by_user||d?.name||d?.model||"Датчик";}
function stateText(e,h){const s=h.states?.[e.entity_id];if(!s)return"—";const u=s.attributes?.unit_of_measurement||"";return `${s.state}${u?` ${u}`:""}`;}
function model(reg,name,h){
  const area=findArea(reg.areas,name);
  if(!area)return{area:null,primaryClimate:[],extraClimate:[],activity:[],security:[],cameras:[]};
  const dm=new Map(reg.devices.map(d=>[d.id,d]));
  const allowedDevices=reg.devices.filter(d=>d.area_id===area.area_id&&!d.disabled_by&&operational(d));
  const allowed=new Set(allowedDevices.map(d=>d.id));
  const primaryDevices=new Set(allowedDevices.filter(d=>labels(d).includes(CLIMATE_LABEL_ID)).map(d=>d.id));
  const groups={primaryClimate:[],extraClimate:[],activity:[],security:[],cameras:[]};
  const extraByDevice=new Map();
  for(const e of reg.entities){
    if(e.disabled_by||e.hidden_by)continue;
    if(effectiveArea(e,dm)!==area.area_id)continue;
    if(e.device_id&&!allowed.has(e.device_id))continue;
    if(!e.device_id&&!operational(e))continue;
    const domain=e.entity_id.split(".")[0];
    const dc=stateClass(h,e);
    const row={entity:e.entity_id,name:title(e,h),value:stateText(e,h),deviceClass:dc};
    if(domain==="camera")groups.cameras.push(row);
    if(["temperature","humidity"].includes(dc)){
      if(e.device_id&&primaryDevices.has(e.device_id)) groups.primaryClimate.push(row);
      else {
        const key=e.device_id||`entity:${e.entity_id}`;
        if(!extraByDevice.has(key)) extraByDevice.set(key,{title:e.device_id?deviceTitle(dm.get(e.device_id)):title(e,h),rows:[]});
        extraByDevice.get(key).rows.push(row);
      }
    }
    if(["motion","occupancy","presence","illuminance"].includes(dc))groups.activity.push(row);
    if(["door","window","opening","garage_door"].includes(dc))groups.security.push(row);
  }
  groups.extraClimate=[...extraByDevice.values()].filter(g=>g.rows.length).sort((a,b)=>a.title.localeCompare(b.title,"ru"));
  return{area,...groups};
}
function hideLegacy(){walk(document,n=>{if(!["hui-section","hui-grid-section"].includes(n.localName))return;if(n.closest?.(`#${ROOT_ID}`))return;if(n.style?.display==="none")return;n.style?.setProperty("display","none","important");hiddenHosts.add(n);});}
function restore(){for(const n of hiddenHosts)n?.style?.removeProperty("display");hiddenHosts.clear();}
function cleanup(){mounted?.remove();mounted=null;restore();}
class LiveSections extends HTMLElement{
  constructor(){super();this.attachShadow({mode:"open"});this._m=null;}
  set model(v){this._m=v;this.render();}
  more(id){this.dispatchEvent(new CustomEvent("hass-more-info",{bubbles:true,composed:true,detail:{entityId:id}}));}
  row(r){return `<button class="tile" data-id="${r.entity}"><span>${r.name}</span><strong>${r.value}</strong></button>`;}
  flatSection(name,icon,rows){if(!rows.length)return"";return `<section><h2><ha-icon icon="${icon}"></ha-icon>${name}</h2><div class="grid">${rows.map(r=>this.row(r)).join("")}</div></section>`;}
  climateSection(m){
    let html="";
    if(m.primaryClimate.length) html+=`<section><h2><ha-icon icon="mdi:thermometer"></ha-icon>Климат</h2><div class="grid">${m.primaryClimate.map(r=>this.row(r)).join("")}</div></section>`;
    if(m.extraClimate.length) html+=`<section><h2><ha-icon icon="mdi:thermometer-lines"></ha-icon>Дополнительные климатические датчики</h2><div class="grid extra">${m.extraClimate.map(g=>`<div class="sensor"><div class="sensor-name">${g.title}</div>${g.rows.map(r=>this.row(r)).join("")}</div>`).join("")}</div></section>`;
    return html;
  }
  render(){
    if(!this._m)return;
    const m=this._m;
    this.shadowRoot.innerHTML=`<style>
      :host{display:block;margin:16px 8px 10px;color:var(--primary-text-color)}
      .wrap{display:grid;gap:22px}
      section{display:block}
      h2{display:flex;align-items:center;gap:8px;margin:0 4px 10px;font-size:18px;line-height:24px;font-weight:500}
      h2 ha-icon{--mdc-icon-size:20px}
      .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
      .tile{min-height:54px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;border:1px solid var(--divider-color,rgba(0,0,0,.12));border-radius:13px;background:var(--card-background-color,var(--ha-card-background,#fff));padding:10px 12px;text-align:left;color:inherit;font:inherit;box-shadow:none}
      .tile span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:14px}
      .tile strong{white-space:nowrap;font-size:13px;color:var(--secondary-text-color)}
      .sensor{border:1px solid var(--divider-color,rgba(0,0,0,.12));border-radius:13px;background:var(--card-background-color,var(--ha-card-background,#fff));padding:9px 10px}
      .sensor-name{font-size:14px;font-weight:700;margin:1px 2px 6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
      .sensor .tile{min-height:38px;border:0;border-top:1px solid var(--divider-color,rgba(0,0,0,.08));border-radius:0;padding:7px 2px;background:transparent}
      .sensor .tile:first-of-type{border-top:0}
      .empty{padding:10px 4px;color:var(--secondary-text-color);font-size:13px}
      @media(max-width:460px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.tile{padding:9px 10px}.tile span{font-size:13px}.tile strong{font-size:12px}}
    </style><div class="wrap">${this.climateSection(m)}${this.flatSection("Активность","mdi:motion-sensor",m.activity)}${this.flatSection("Безопасность","mdi:shield-home",m.security)}${this.flatSection("Камеры","mdi:cctv",m.cameras)}${(!m.primaryClimate.length&&!m.extraClimate.length&&!m.activity.length&&!m.security.length&&!m.cameras.length)?'<div class="empty">Нет эксплуатационных сущностей для помещения.</div>':""}</div>`;
    for(const b of this.shadowRoot.querySelectorAll("button[data-id]"))b.onclick=()=>this.more(b.dataset.id);
  }
}
if(!customElements.get("nikas-room-live-sections"))customElements.define("nikas-room-live-sections",LiveSections);
async function sync(){timer=null;const s=slug();if(!s){cleanup();return;}const name=ROOM_NAMES[s],h=hass();if(!name||!h?.callWS){cleanup();return;}try{const reg=await registries(h);if(slug()!==s){cleanup();return;}const host=mountHost();if(!host){cleanup();return;}const m=model(reg,name,h);hideLegacy();if(!mounted?.isConnected){mounted=document.createElement("nikas-room-live-sections");mounted.id=ROOT_ID;const equipment=[...host.children].find(n=>n.id==="nikas-room-equipment-runtime");equipment?host.insertBefore(mounted,equipment):host.append(mounted);}mounted.model=m;}catch(e){console.warn("[NikaS Rooms] Cannot build live room sections",e);}}
function schedule(){if(timer!==null)return;timer=window.setTimeout(sync,100);}window.addEventListener("location-changed",schedule);window.addEventListener("popstate",schedule);document.addEventListener("visibilitychange",()=>{if(!document.hidden)schedule();});new MutationObserver(schedule).observe(document.documentElement,{childList:true,subtree:true});schedule();