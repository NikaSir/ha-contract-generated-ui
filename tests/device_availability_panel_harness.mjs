import fs from "node:fs";

class FakeShadowRoot {
  constructor() {
    this.writes = 0;
    this._html = "";
  }
  set innerHTML(value) {
    this.writes += 1;
    this._html = value;
  }
  get innerHTML() { return this._html; }
  getElementById() { return null; }
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
  constructor(type, options = {}) { this.type = type; this.detail = options.detail; }
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

if (request.operation === "shell") {
  const panel = new module.NikasDeviceAvailabilityPanel();
  panel.connectedCallback();
  panel.panel = { config: { parent_route: "/home/overview" } };
  panel.hass = { states: request.states || {} };
  panel.hass = { states: request.states || {} };
  process.stdout.write(JSON.stringify({ writes: panel.shadowRoot.writes }));
} else if (request.operation === "version") {
  process.stdout.write(JSON.stringify({ version: module.UI_VERSION }));
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
