# Specialized Panel Shell Standard v1.4

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Primary acceptance viewport:** iPhone Pro Max, portrait  
**Reference field implementation:** Stark SolarPower 1.8.10

## 1. Purpose and hierarchy

All specialized panels use one application-shell contract while keeping domain UI in the owning integration/project.

```text
HOME ASSISTANT / EFFECTIVE TOP SAFE AREA
↓
SPECIALIZED HEADER                         native scale
  └── ☰ HA menu | centered title | action
↓
PEER DEVICE SELECTOR (when applicable)    native scale
↓
ONE FIXED CANVAS VIEWPORT                 native clipping window
  └── domain canvas                       translate3d(x,y,0) scale(s)
↓
BOTTOM TAB BAR                            native scale
↓
EFFECTIVE BOTTOM SAFE AREA
```

There is no permanent zoom toolbar and no browser-scroll-owned scalable canvas.

## 2. Ownership boundary

The shared shell owns safe areas, Header/menu behavior, peer-selector placement, one canvas topology, transform/gesture lifecycle, reset feedback, Bottom Tab geometry and shell clearances.

The integration owns entities, telemetry, commands, cards, visualizations, peer-device labels/data, contextual artwork and any parent/drill-down navigation inside the work area.

Do not combine a shell migration with an unrelated domain redesign.

## 3. Safe area — consume exactly once

Use effective Home Assistant/browser insets and never phone-model constants.

```css
env(safe-area-inset-top, 0px)
env(safe-area-inset-right, 0px)
env(safe-area-inset-bottom, 0px)
env(safe-area-inset-left, 0px)
```

If registration or Home Assistant already consumes an inset, the panel must not add it again. Header stays below Dynamic Island/notch; Bottom Tab stays above Home Indicator; views/cards do not add independent safe-area padding.

## 4. Header

The permanent left control is the Home Assistant main-system menu only:

```js
new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true })
```

It is never browser Back, a parent-route arrow, an integration drawer or a device action. Parent navigation, when needed, belongs inside the work area.

The title is geometrically centered relative to the viewport. The right rail contains at most one application-global action. Both rails use comparable geometry and approximately 44×44 pt touch targets. Header, menu and right action remain native scale.

## 5. Peer Device Selector

Use it only for multiple peer physical devices.

- directly below Header;
- native scale and outside canvas;
- fixed order;
- selection survives Bottom Tab changes;
- primary detail is selected-peer-only;
- compact health state for non-selected peers is allowed;
- zones/channels/components are not peers merely because they are selectable.

## 6. One transform-owned canvas

The working area is one shell-sized fixed canvas viewport. It captures gestures and clips content but does not use browser `scrollLeft`, `scrollTop` or native `overflow` scrolling to own position.

The only transform target uses:

```text
translate3d(x, y, 0) scale(s)
```

At 100%, one-finger movement still updates `x/y`; no separate scroll model appears.

The canvas viewport, transform target, gesture handlers and reset status element each exist once. Installation/reconciliation is idempotent across all Home Assistant rerenders.

## 7. Transform and gesture lifecycle

Normative behavior is defined by `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.4.

The shell must:

- keep Header, selector and Bottom Tab outside the transform;
- support one-finger pan and two-finger focal-point pinch;
- clamp `x/y` to measured scaled-content bounds;
- preserve the final transform after release;
- persist `{scale,x,y}` per panel/client and peer device where applicable;
- restore the saved transform on replacement DOM before the visible frame;
- never re-wrap an existing canvas;
- avoid CSS `zoom`, page zoom and native overflow scroll as the canvas engine.

## 8. Interaction guard

The shell coordinates custom gestures with Home Assistant interactions.

- second finger immediately cancels/blocks pending `more-info`;
- crossing the pan threshold cancels pending long press through `pointercancel` semantics;
- synthetic clicks after a gesture are briefly suppressed;
- pinch/pan/reset never execute device commands;
- stationary intentional long press still opens native `more-info`.

## 9. Reset UX

- no permanent `− / % / +` controls;
- two-finger double tap resets `{scale:1,x:0,y:0}`;
- pinch ending at 97–103% uses the same exact reset;
- reset/snap briefly shows `Масштаб 100%` at native scale.

## 10. Bottom Tab Bar

Primary navigation with 3–5 destinations uses one full-width fixed edge-attached Bottom Tab Bar.

- safe-area-aware and native scale;
- not a floating card/pill;
- active tab unambiguous;
- icon + short readable label;
- comfortable touch targets;
- canvas bounds/bottom reserve allow the final content to be moved completely above the bar.

## 11. Render stability

Unrelated Home Assistant state churn should not rebuild the complete shell when practical.

Any render path preserves one shell/canvas, selected peer, active Bottom Tab, `{scale,x,y}`, gesture bindings, `more-info` bindings and global-action feedback.

When work DOM must be replaced, transform restoration happens before reveal/paint so users never see an origin flash.

## 12. State and visual semantics

- first useful view prioritizes current operating state;
- normal factual values use neutral typography;
- semantic colors express confirmed health/warning/fault;
- `unknown`, `unavailable`, stale or untrusted data never appear healthy;
- backend semantic states/thresholds remain authoritative;
- decorative artwork contains no live state;
- unsupported values are not invented;
- native `more-info`/history is reused where useful.

## 13. Non-conforming patterns

Prohibited:

- Header under Dynamic Island/notch or double safe-area consumption;
- Back/integration drawer/device action in permanent left Header rail;
- menu icon that does not dispatch `hass-toggle-menu`;
- CSS `zoom` or whole-page/browser zoom as panel zoom;
- native overflow scrolling as scalable-canvas position state;
- reading/writing `scrollLeft` / `scrollTop` as transform state;
- nested canvas/zoom wrappers or repeated handler installation;
- scaling Header, peer selector or Bottom Tab with content;
- permanent on-screen zoom controls;
- origin flash or position reset during telemetry rerender;
- accidental `more-info`, graphs, clicks or commands during gestures;
- floating primary Bottom Tab Bar;
- hard-coded device safe-area constants.

## 14. Field acceptance

Verify on iPhone Companion App first:

1. safe area is consumed once;
2. `☰` opens native HA menu;
3. title/right action geometry is stable;
4. peer selector remains native and fixed;
5. exactly one canvas exists after repeated HA updates;
6. one-finger movement at 100% persists after release;
7. focal-point pinch persists after release;
8. real bounds expose all reachable content without snap-back;
9. no permanent zoom buttons appear;
10. two-finger reset, 97–103% snap and `Масштаб 100%` work;
11. telemetry updates restore transform before paint;
12. gestures do not open `more-info`/graphs or execute actions;
13. stationary long press still opens `more-info`;
14. Bottom Tab remains fixed/native and final content is reachable;
15. no nested wrappers, blank areas or progressive shrink occur.

## Project rule

> The shell owns native application chrome and one transform-owned canvas. Only the canvas content moves/scales through `translate3d(x,y,0) scale(s)`; browser scroll is not canvas state, and every rerender restores transform plus gesture safety before paint.

