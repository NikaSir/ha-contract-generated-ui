const ELEMENT_NAME = "nikas-rooms-v11";
const ACTIVE_LABEL = "v_ekspluatatsii";
const CLIMATE_LABEL = "datchik_klimata_pomeshcheniia";
const EXCLUDED_LABELS = new Set(["rezerv", "na_obsluzhivanii", "trebuet_zameny", "vyvedeno_iz_ekspluatatsii"]);
const BAD = new Set(["unknown", "unavailable", "none", "null", ""]);

const ROOMS = [
  ["bathroom","01","Ванная","mdi:bathtub-outline",2], ["bedroom","02","Спальня","mdi:bed-outline",2],
  ["wardrobe","03","Гардероб","mdi:hanger",2], ["sasha","04","У Саши","mdi:account",2],
  ["ilya","05","У Ильи","mdi:account-outline",2], ["stairs","06","Лестница","mdi:stairs",2],
  ["corridor","07","Коридор","mdi:door-open",2], ["hall","08","Холл","mdi:sofa-outline",2],
  ["boiler","09","Котельная","mdi:water-boiler",1], ["kitchen","10","Кухня","mdi:fridge-outline",1],
  ["dining","11.1","Столовая","mdi:table-chair",1], ["living","11.2","Гостиная","mdi:sofa",1],
  ["toilet","12","Туалет","mdi:toilet",1], ["vestibule","13","Тамбур","mdi:door-closed-lock",1],
  ["veranda","14","Веранда","mdi:home-outline",1], ["garage","15","Гараж","mdi:garage",1],
  ["attic","16","Чердак","mdi:home-roof",0], ["greenhouse","17","Теплица","mdi:greenhouse",0],
].map(([slug,no,name,icon,floor]) => ({slug,no,name,icon,floor}));

function norm(v){return String(v??"").trim().toLocaleLowerCase("ru-RU").replace(/ё/g,"е").replace(/\s+/g," ")}
function normArea(v){return norm(v).replace(/^\d+(?:[.,]\d+)?\s*(?:[-–—.:)]\s*)?/,"").trim()}
function labelsOf(x){const v=x?.labels;if(!v)return[];if(Array.isArray(v))return v;if(v instanceof Set)return[...v];if(typeof v==="object")return Object.keys(v).filter(k=>v[k]);return[]}
function operational(x){const s=new Set(labelsOf(x));return s.has(ACTIVE_LABEL)&&![...EXCLUDED_LABELS].some(id=>s.has(id))}
function domain(id){return String(id||"").split(".")[0]}
function stateClass(e,hass){return e?.device_class||hass.states?.[e?.entity_id]?.attributes?.device_class||""}
function titleOfEntity(e,hass){return e?.name||hass.states?.[e?.entity_id]?.attributes?.friendly_name||e?.original_name||e?.entity_id||"Сущность"}
function titleOfDevice(d){return d?.name_by_user||d?.name||d?.model||"Устройство"}
function goodState(s){return !BAD.has(norm(s))}
function esc(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}

class NikasRoomsV11 extends HTMLElement {
  constructor(){super();this.attachShadow({mode:"open"});this._hass=null;this._panel=null;this._registries=null;this._rooms=[];this._loading=false;this._unsub=null;this._lastPath=""}
  set panel(p){this._panel=p;this.render()}
  set hass(h){const first=!this._hass;this._hass=h;if(first)this.load();else this.patchStates()}
  connectedCallback(){window.addEventListener("location-changed",this._onLocation=()=>this.render());window.addEventListener("popstate",this._onLocation);this.render()}
  disconnectedCallback(){window.removeEventListener("location-changed",this._onLocation);window.removeEventListener("popstate",this._onLocation)}

  async load(){if(this._loading||!this._hass?.callWS)return;this._loading=true;try{const [areas,devices,entities,labels]=await Promise.all([
    this._hass.callWS({type:"config/area_registry/list"}),this._hass.callWS({type:"config/device_registry/list"}),this._hass.callWS({type:"config/entity_registry/list"}),this._hass.callWS({type:"config/label_registry/list"}).catch(()=>[])
  ]);this._registries={areas,devices,entities,labels};this.buildRooms();this.render()}catch(err){console.warn("[NikaS Rooms v11] registry load failed",err);this.renderError("Не удалось прочитать реестр Home Assistant")}finally{this._loading=false}}

  buildRooms(){const {areas,devices,entities,labels}=this._registries;const deviceMap=new Map(devices.map(d=>[d.id,d]));const labelMap=new Map(labels.map(l=>[l.label_id,l.name||l.label_id]));this._rooms=ROOMS.map(def=>{
    const area=areas.find(a=>norm(a.name)===norm(def.name)||normArea(a.name)===norm(def.name)||norm(a.area_id)===norm(def.name));
    if(!area)return {...def,area:null,devices:[],entities:[],labelMap};
    const roomDevices=devices.filter(d=>d.area_id===area.area_id&&!d.disabled_by&&operational(d));
    const ids=new Set(roomDevices.map(d=>d.id));
    const roomEntities=entities.filter(e=>!e.disabled_by&&!e.hidden_by&&((e.area_id===area.area_id)||(!e.area_id&&e.device_id&&ids.has(e.device_id))));
    return {...def,area,devices:roomDevices,entities:roomEntities,deviceMap,labelMap};
  })}

  route(){const parts=location.pathname.split("/").filter(Boolean);if(parts[0]!=="dashboard-rooms")return {kind:"overview"};if(parts[1]?.startsWith("room-")){const slug=parts[1].slice(5);return {kind:parts[2]==="diagnostics"?"diagnostics":"room",slug}}return {kind:"overview"}}
  nav(path){history.pushState(null,"",path);window.dispatchEvent(new Event("location-changed"))}
  room(slug){return this._rooms.find(r=>r.slug===slug)}
  entityState(e){return this._hass?.states?.[e.entity_id]}

  roomSummary(room){if(!room?.area)return {text:"Нет данных",tone:"grey"};const important=room.entities.filter(e=>{
    const d=domain(e.entity_id),c=stateClass(e,this._hass);return d==="binary_sensor"&&["door","window","opening","garage_door","motion","occupancy","presence"].includes(c)
  });
    let open=0,motion=0,bad=0;for(const e of important){const s=this.entityState(e)?.state;if(!goodState(s)){bad++;continue}const c=stateClass(e,this._hass);if(s==="on"&&["door","window","opening","garage_door"].includes(c))open++;if(s==="on"&&["motion","occupancy","presence"].includes(c))motion++}
    if(open)return {text:`Открыто ${open}`,tone:"yellow"};if(motion)return {text:`Активность ${motion}`,tone:"blue"};if(bad)return {text:"Требует внимания",tone:"orange"};return {text:"Спокойно",tone:"green"}
  }

  formatEntity(e){const st=this.entityState(e);if(!st)return "Нет данных";const s=st.state;if(!goodState(s))return "Нет данных";const unit=st.attributes?.unit_of_measurement||"";const c=stateClass(e,this._hass);if(domain(e.entity_id)==="binary_sensor"){if(["door","window","opening","garage_door"].includes(c))return s==="on"?"Открыто":"Закрыто";if(["motion","occupancy","presence"].includes(c))return s==="on"?"Обнаружено":"Не обнаружено"}return `${s}${unit?` ${unit}`:""}`}
  operationalDeviceForEntity(room,e){return e.device_id?room.devices.find(d=>d.id===e.device_id):null}
  climateDevices(room){return room.devices.filter(d=>labelsOf(d).includes(CLIMATE_LABEL))}
  entitiesForDevices(room,devices){const ids=new Set(devices.map(d=>d.id));return room.entities.filter(e=>e.device_id&&ids.has(e.device_id))}
  climatePairs(room,devices){const es=this.entitiesForDevices(room,devices);return {temp:es.filter(e=>stateClass(e,this._hass)==="temperature"),hum:es.filter(e=>stateClass(e,this._hass)==="humidity")}}

  render(){if(!this.shadowRoot)return;const r=this.route();const room=r.slug?this.room(r.slug):null;const title=r.kind==="overview"?"Помещения":room?.name||"Помещение";const subtitle=r.kind==="overview"?"Обзор · UI v11.0.0":r.kind==="diagnostics"?"Диагностика · UI v11.0.0":"Помещения · UI v11.0.0";
    this.shadowRoot.innerHTML=`<style>${this.styles()}</style><div class="app"><header><button id="menu"><ha-icon icon="mdi:menu"></ha-icon></button><div class="head-title"><strong>${esc(title)}</strong><span>${esc(subtitle)}</span></div><button id="refresh"><ha-icon icon="mdi:refresh"></ha-icon></button></header><main>${!this._registries?'<div class="loading">Загрузка помещений…</div>':r.kind==="overview"?this.overview():r.kind==="diagnostics"?this.diagnostics(room):this.roomView(room)}</main>${this.bottom()}</div>`;
    this.bind(r,room)}

  patchStates(){if(!this.isConnected||!this._registries)return;this.render()}
  renderError(text){this.shadowRoot.innerHTML=`<style>${this.styles()}</style><div class="loading">${esc(text)}</div>`}

  overview(){const group=(floor,label,icon)=>`<section class="floor"><h2><ha-icon icon="${icon}"></ha-icon>${label}</h2><div class="room-grid">${this._rooms.filter(r=>r.floor===floor).map(r=>this.roomCard(r)).join("")}</div></section>`;return `<div class="overview">${group(2,"2 этаж","mdi:home-floor-2")}${group(1,"1 этаж","mdi:home-floor-1")}${group(0,"Технические помещения","mdi:tools")}</div>`}
  roomCard(room){const s=this.roomSummary(room);return `<button class="room-card tone-${s.tone}" data-room="${room.slug}"><ha-icon icon="${room.icon}"></ha-icon><span><b>${esc(room.name)} [${room.no}]</b><small>${esc(s.text)}</small></span></button>`}

  section(title,icon,entities){if(!entities.length)return"";return `<section class="section"><h2><ha-icon icon="${icon}"></ha-icon>${title}</h2><div class="entity-grid">${entities.map(e=>`<button class="entity" data-entity="${e.entity_id}"><span>${esc(titleOfEntity(e,this._hass))}</span><b>${esc(this.formatEntity(e))}</b></button>`).join("")}</div></section>`}
  extraClimate(room,primary){const primaryIds=new Set(primary.map(d=>d.id));const candidates=room.devices.filter(d=>!primaryIds.has(d.id));return candidates.map(d=>{const pairs=this.climatePairs(room,[d]);if(!pairs.temp.length&&!pairs.hum.length)return"";return `<div class="sensor-card"><b>${esc(titleOfDevice(d))}</b>${[...pairs.temp,...pairs.hum].map(e=>`<button data-entity="${e.entity_id}"><span>${esc(titleOfEntity(e,this._hass))}</span><strong>${esc(this.formatEntity(e))}</strong></button>`).join("")}</div>`}).join("")}

  roomView(room){if(!room?.area)return `<div class="empty">Помещение не найдено в реестре HA.</div>`;const primary=this.climateDevices(room);const cp=this.climatePairs(room,primary);const activity=room.entities.filter(e=>["motion","occupancy","presence","illuminance"].includes(stateClass(e,this._hass)));const security=room.entities.filter(e=>["door","window","opening","garage_door"].includes(stateClass(e,this._hass)));const cameras=room.entities.filter(e=>domain(e.entity_id)==="camera");const extra=this.extraClimate(room,primary);
    return `<div class="room-view">${this.section("Климат","mdi:thermometer",[...cp.temp,...cp.hum])}${extra?`<section class="section"><h2><ha-icon icon="mdi:thermometer-lines"></ha-icon>Дополнительные климатические датчики</h2><div class="sensor-grid">${extra}</div></section>`:""}${this.section("Активность","mdi:motion-sensor",activity)}${this.section("Безопасность","mdi:shield-home",security)}${this.section("Камеры","mdi:cctv",cameras)}<button class="diagnostics" id="diagnostics">Диагностика</button></div>`}

  diagnostics(room){if(!room?.area)return `<div class="empty">Помещение не найдено.</div>`;const rows=room.devices.map(d=>{const es=room.entities.filter(e=>e.device_id===d.id);return `<article class="device"><h3>${esc(titleOfDevice(d))}</h3><div class="chips">${labelsOf(d).map(id=>`<span>${esc(room.labelMap.get(id)||id)}</span>`).join("")}</div>${es.map(e=>`<button data-entity="${e.entity_id}"><span>${esc(titleOfEntity(e,this._hass))}</span><b>${esc(this.formatEntity(e))}</b></button>`).join("")}</article>`}).join("");return `<div class="diag"><button class="back-plaque" id="back-room">${esc(room.name)}</button><section class="diag-card"><h2>Оборудование</h2><p>${esc(room.area.name)} · ${room.devices.length} поз.</p><div class="devices">${rows||'<div class="empty">Нет оборудования</div>'}</div></section></div>`}

  bottom(){const items=[["Дом","mdi:home-outline","/dashboard-house-v11/home"],["Помещения","mdi:floor-plan","/dashboard-rooms/rooms"],["Действия","mdi:lightning-bolt-outline","/dashboard-actions/home"],["Инфра","mdi:server-network","/dashboard-infrastructure/overview"]];return `<nav>${items.map(([n,i,p])=>`<button class="${p.startsWith('/dashboard-rooms')?'active':''}" data-nav="${p}"><ha-icon icon="${i}"></ha-icon><span>${n}</span></button>`).join("")}</nav>`}

  bind(route,room){this.shadowRoot.getElementById("menu")?.addEventListener("click",()=>this.dispatchEvent(new CustomEvent("hass-toggle-menu",{bubbles:true,composed:true})));this.shadowRoot.getElementById("refresh")?.addEventListener("click",()=>{this._registries=null;this.load();this.render()});this.shadowRoot.querySelectorAll("[data-nav]").forEach(b=>b.onclick=()=>this.nav(b.dataset.nav));this.shadowRoot.querySelectorAll("[data-room]").forEach(b=>b.onclick=()=>this.nav(`/dashboard-rooms/room-${b.dataset.room}`));this.shadowRoot.querySelectorAll("[data-entity]").forEach(b=>b.onclick=()=>this.dispatchEvent(new CustomEvent("hass-more-info",{bubbles:true,composed:true,detail:{entityId:b.dataset.entity}})));this.shadowRoot.getElementById("diagnostics")?.addEventListener("click",()=>this.nav(`/dashboard-rooms/room-${room.slug}/diagnostics`));this.shadowRoot.getElementById("back-room")?.addEventListener("click",()=>this.nav(`/dashboard-rooms/room-${room.slug}`))}

  styles(){return `:host{display:block;height:100dvh;overflow:hidden;background:var(--primary-background-color,#f6f6f6);color:var(--primary-text-color,#111);font-family:var(--paper-font-body1_-_font-family,Arial,sans-serif)}*{box-sizing:border-box}.app{height:100%;display:grid;grid-template-rows:auto minmax(0,1fr) auto}header{display:grid;grid-template-columns:52px minmax(0,1fr) 52px;align-items:center;padding:6px max(8px,env(safe-area-inset-right)) 6px max(8px,env(safe-area-inset-left));background:var(--card-background-color,#fff);border-bottom:1px solid var(--divider-color,#ddd);box-shadow:0 2px 10px #0001;z-index:3}header button{width:44px;height:44px;border:1px solid var(--divider-color,#ddd);border-radius:16px;background:var(--card-background-color,#fff)}header ha-icon{--mdc-icon-size:25px}.head-title{text-align:center;line-height:1.12}.head-title strong{display:block;font-size:23px;font-weight:800}.head-title span{display:block;margin-top:3px;font-size:14px;font-weight:600;color:var(--secondary-text-color,#666)}main{min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:10px 8px 12px}.loading,.empty{padding:24px;text-align:center;color:var(--secondary-text-color,#666)}nav{display:grid;grid-template-columns:repeat(4,1fr);gap:3px;padding:5px 8px calc(5px + env(safe-area-inset-bottom));background:var(--card-background-color,#fff);border-top:1px solid var(--divider-color,#ddd);box-shadow:0 -3px 14px #0001;z-index:3}nav button{border:0;background:transparent;color:var(--secondary-text-color,#666);min-height:54px;border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-weight:700}nav button.active{color:var(--primary-color,#03a9f4);background:color-mix(in srgb,var(--primary-color,#03a9f4) 10%,transparent)}nav ha-icon{--mdc-icon-size:27px}nav span{font-size:12px}.overview{height:100%;display:flex;flex-direction:column;justify-content:space-between;gap:7px}.floor{margin:0}.floor h2{height:24px;margin:0 0 5px;display:flex;align-items:center;gap:8px;font-size:16px;font-weight:650}.floor h2 ha-icon{--mdc-icon-size:20px}.room-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px 7px}.room-card{min-height:48px;border:1px solid var(--divider-color,#ddd);border-radius:14px;background:var(--card-background-color,#fff);padding:5px 9px;display:grid;grid-template-columns:34px minmax(0,1fr);gap:5px;align-items:center;text-align:left;color:inherit}.room-card>ha-icon{--mdc-icon-size:25px;color:var(--primary-color,#2196f3)}.room-card span{min-width:0}.room-card b,.room-card small{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.room-card b{font-size:14px}.room-card small{font-size:12px;margin-top:1px}.tone-yellow>ha-icon{color:#f2c400}.tone-orange>ha-icon{color:#fb8c00}.tone-green>ha-icon{color:#2dbd65}.tone-blue>ha-icon{color:#2196f3}.tone-grey>ha-icon{color:#999}.room-view{padding-bottom:4px}.section{margin:0 0 13px}.section h2{display:flex;align-items:center;gap:8px;margin:0 0 7px;font-size:19px}.section h2 ha-icon{--mdc-icon-size:23px}.entity-grid,.sensor-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.entity,.sensor-card{min-height:52px;border:1px solid var(--divider-color,#ddd);border-radius:14px;background:var(--card-background-color,#fff);color:inherit;padding:9px 10px}.entity{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:8px;text-align:left}.entity span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.entity b{white-space:nowrap}.sensor-card>b{display:block;margin-bottom:5px}.sensor-card button,.device button{width:100%;border:0;border-top:1px solid var(--divider-color,#ddd);background:transparent;color:inherit;padding:7px 0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;text-align:left}.sensor-card button span,.device button span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.diagnostics,.back-plaque{width:100%;min-height:52px;border:1px solid var(--divider-color,#ddd);border-radius:16px;background:var(--card-background-color,#fff);font:inherit;font-size:17px;font-weight:800;color:inherit}.diag{padding-bottom:8px}.back-plaque{margin-bottom:10px}.diag-card{background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#ddd);border-radius:18px;padding:13px}.diag-card h2{margin:0;font-size:20px}.diag-card p{margin:3px 0 10px;color:var(--secondary-text-color,#666)}.devices{display:grid;gap:9px}.device{background:var(--secondary-background-color,#eee);border:1px solid var(--divider-color,#ddd);border-radius:14px;padding:10px}.device h3{margin:0 0 7px;font-size:16px}.chips{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:5px}.chips span{padding:3px 6px;border-radius:999px;background:var(--card-background-color,#fff);font-size:10px;color:var(--secondary-text-color,#666)}@media(max-height:780px){main{padding-top:7px}.room-card{min-height:44px}.room-card b{font-size:13px}.floor h2{height:21px;margin-bottom:3px}.overview{gap:4px}}@media(min-width:850px){main{width:min(900px,100%);margin:0 auto}.room-grid,.entity-grid,.sensor-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}`}
}

if(!customElements.get(ELEMENT_NAME))customElements.define(ELEMENT_NAME,NikasRoomsV11);
