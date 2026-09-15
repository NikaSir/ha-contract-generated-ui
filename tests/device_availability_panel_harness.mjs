import fs from "node:fs";

class FakeHeaderElement {
  constructor() { this.listeners = new Map(); this.attributes = new Map(); }
  addEventListener(type, handler) { this.listeners.set(type, handler); }
  click() { this.listeners.get("click")?.(); }
  getAttribute(name) { return this.attributes.get(name) ?? null; }
  setAttribute(name, value) { this.attributes.set(name, value); }
  querySelector() { return null; }
}

class FakeShadowRoot {
  constructor() {
    this.writes = 0;
    this._html = "";
  }
  set innerHTML(value) {
    this.writes += 1;
    this._html = value;
    this.headerElements = new Map();
    for (const id of ["title", "menu", "refresh", "refresh-status", "refresh-error"]) {
      if (value.includes(`id="${id}"`)) this.headerElements.set(id, new FakeHeaderElement());
    }
  }
  get innerHTML() { return this._html; }
  getElementById(id) { return this.headerElements?.get(id) ?? null; }
  querySelector() { return null; }
  querySelectorAll() { return []; }
}

globalThis.HTMLElement = class {
  constructor() { this.events = []; }
  attachShadow() { this.shadowRoot = new FakeShadowRoot(); return this.shadowRoot; }
  dispatchEvent(event) { this.events.push(event); return true; }
  addEventListener() {}
  removeEventListener() {}
};
globalThis.CustomEvent = class {
  constructor(type, options = {}) {
    this.type = type; this.detail = options.detail;
    Object.defineProperty(this, "bubbles", { value: Boolean(options.bubbles) });
    Object.defineProperty(this, "composed", { value: Boolean(options.composed) });
  }
};
globalThis.customElements = {
  registry: new Map(),
  get(name) { return this.registry.get(name); },
  define(name, value) { this.registry.set(name, value); },
};
globalThis.window = {
  location: { origin: "https://ha.local", pathname: "/dashboard-device-availability" },
  history: { paths: [], pushState(_state, _title, path) { this.paths.push(path); } },
  events: [],
  dispatchEvent(event) { this.events.push(event.type); },
  localStorage: { getItem() { return null; }, setItem() {} },
};
globalThis.Event = class { constructor(type) { this.type = type; } };

const module = await import(
  "../custom_components/contract_generated_ui/frontend/device-availability-panel.js"
);
const request = JSON.parse(fs.readFileSync(0, "utf8"));

if (request.operation === "header_actions") {
  const panel = new module.NikasDeviceAvailabilityPanel();
  panel.panel = { config: { parent_route: request.parent } };
  panel.connectedCallback();
  panel.shadowRoot.getElementById("menu")?.click();
  panel.shadowRoot.getElementById("title")?.click();
  process.stdout.write(JSON.stringify({
    menu: panel.events.map(event => ({ type: event.type, bubbles: event.bubbles, composed: event.composed })),
    paths: window.history.paths, events: window.events,
  }));
} else if (request.operation === "refresh_failure") {
  const sleeps = [];
  let release, settled = false, rejected = false;
  const task = module.refreshAvailabilitySources(
    { callService: async () => { if (request.mode === "failure") throw Error("Rejected"); return false; } },
    { updateEntityIds: request.mode === "no_entities" ? [] : ["sensor.one"] },
    milliseconds => { sleeps.push(milliseconds); return new Promise(resolve => { release = resolve; }); },
  ).then(() => { settled = true; }, () => { settled = true; rejected = true; });
  await new Promise(resolve => setImmediate(resolve));
  const settledBeforeMinimum = settled;
  release?.();
  await task;
  process.stdout.write(JSON.stringify({ sleeps, rejected, settledBeforeMinimum }));
} else if (request.operation === "shell") {
  const panel = new module.NikasDeviceAvailabilityPanel();
  panel.connectedCallback();
  panel.panel = { config: { parent_route: "/home/overview" } };
  panel.hass = { states: request.states || {} };
  panel.hass = { states: request.states || {} };
  process.stdout.write(JSON.stringify({ writes: panel.shadowRoot.writes }));
} else if (request.operation === "version") {
  process.stdout.write(JSON.stringify({ version: module.UI_VERSION }));
} else if (request.operation === "summary") {
  const panel = new module.NikasDeviceAvailabilityPanel();
  panel.hass = { states: request.states || {} };
  const content = { innerHTML: "", querySelector() { return null; } };
  panel._renderSummary(content);
  const text = content.innerHTML.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
  process.stdout.write(JSON.stringify({ html: content.innerHTML, text }));
} else if (request.operation === "more_info") {
  const target = new globalThis.HTMLElement();
  module.dispatchMoreInfo(target, "light.kitchen");
  process.stdout.write(JSON.stringify(target.events[0]));
} else if (request.operation === "navigate") {
  module.navigatePanel("/home/overview", window);
  process.stdout.write(JSON.stringify({ paths: window.history.paths, events: window.events }));
} else if (request.operation === "refresh") {
  const calls = [];
  const sleeps = [];
  await module.refreshAvailabilitySources(
    { callService: async (...args) => calls.push(args) },
    { updateEntityIds: ["sensor.one", "sensor.two"] },
    async (milliseconds) => sleeps.push(milliseconds),
  );
  process.stdout.write(JSON.stringify({ calls, sleeps }));
}
