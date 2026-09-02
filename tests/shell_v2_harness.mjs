import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { runInNewContext } from "node:vm";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(join(root, "templates", "shell_v2", "nikas-specialized-shell.js"), "utf8");
const context = {};
runInNewContext(`${source}\n;globalThis.shellApi = {
  shouldBlockNikasShellBoundaryMove,
  createNikasShellScrollBoundaryGuard,
};`, context);

const { shouldBlockNikasShellBoundaryMove, createNikasShellScrollBoundaryGuard } = context.shellApi;
const move = (overrides = {}) => shouldBlockNikasShellBoundaryMove({
  deltaX: 0,
  deltaY: 10,
  inViewport: true,
  scrollTop: 0,
  scrollHeight: 1000,
  clientHeight: 500,
  ...overrides,
});

assert.equal(move(), true, "top-edge downward pull must be consumed");
assert.equal(move({ deltaY: -10 }), false, "top-edge upward move must scroll natively");
assert.equal(move({ scrollTop: 250 }), false, "interior movement must scroll natively");
assert.equal(move({ deltaY: -10, scrollTop: 500 }), true, "bottom-edge upward pull must be consumed");
assert.equal(move({ scrollTop: 500 }), false, "bottom-edge downward move must scroll natively");
assert.equal(move({ scrollHeight: 500 }), true, "short view downward movement must be consumed");
assert.equal(move({ deltaY: -10, scrollHeight: 500 }), true, "short view upward movement must be consumed");
assert.equal(move({ inViewport: false }), true, "fixed chrome must not drag the host page");
assert.equal(move({ deltaX: 20, deltaY: 10 }), false, "horizontal-dominant movement must remain untouched");

const listeners = new Map();
const host = {
  addEventListener(type, listener, options) {
    listeners.set(type, { listener, options });
  },
  removeEventListener(type, listener, capture) {
    const registered = listeners.get(type);
    if (registered?.listener === listener && capture === true) listeners.delete(type);
  },
};
const viewport = {
  scrollTop: 0,
  scrollHeight: 1000,
  clientHeight: 500,
  contains: () => false,
};
const cleanup = createNikasShellScrollBoundaryGuard({ host, viewport });
assert.equal(listeners.get("touchstart").options.passive, false, "touch sequence must be cancelable on iOS");
assert.equal(listeners.get("touchmove").options.passive, false, "touchmove must be non-passive");
assert.equal(listeners.get("touchmove").options.capture, true, "touchmove must run in capture phase");

const target = {};
listeners.get("touchstart").listener({
  target,
  touches: [{ clientX: 40, clientY: 100 }],
  composedPath: () => [target, viewport, host],
});
let prevented = false;
listeners.get("touchmove").listener({
  cancelable: true,
  touches: [{ clientX: 40, clientY: 102 }],
  preventDefault: () => { prevented = true; },
});
assert.equal(prevented, false, "tap-sized touch jitter must not be canceled");
listeners.get("touchmove").listener({
  cancelable: true,
  touches: [{ clientX: 40, clientY: 125 }],
  preventDefault: () => { prevented = true; },
});
assert.equal(prevented, true, "top-edge touchmove must be canceled before Home Assistant");
cleanup();
assert.equal(listeners.size, 0, "cleanup must remove every capture listener");

console.log("Shell v2 scroll-boundary harness passed");
