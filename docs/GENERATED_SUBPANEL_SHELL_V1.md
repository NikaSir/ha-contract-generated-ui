# Generated Subpanel Shell v1

**Status:** governed by canonical specialized-panel standards  
**Owner:** `ha-contract-generated-ui`  
**Canonical shell:** `SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.4  
**Canonical zoom:** `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.4

## Decision

Generated specialized subpanels use the same native shell and transform-owned canvas contract as integration-owned panels.

```text
Header / hass-toggle-menu                  native
Peer Device Selector (optional)           native
One fixed canvas viewport                 native clip
  └── generated domain content            translate3d(x,y,0) scale(s)
Bottom Tab Bar                            native
```

## Header

The left control dispatches `hass-toggle-menu` and is never Back, an integration drawer or device action. Logical parent navigation may be metadata or work-area content but never replaces the permanent HA menu rail.

## Canvas contract

- exactly one viewport and one transform target;
- one combined `translate3d(x,y,0) scale(s)` transform;
- state `{scale,x,y}`;
- no CSS `zoom`, browser/page zoom or native overflow scrolling as canvas position;
- one-finger pan at every scale, including 100%;
- two-finger focal-point pinch;
- real geometry clamps coordinates;
- transform persists after release;
- no permanent zoom controls;
- two-finger double-tap reset;
- 97–103% snap to exact 100%;
- brief `Масштаб 100%` feedback;
- local panel/peer persistence;
- restored before visible frame after generated DOM replacement.

## Interaction guard

Second finger blocks pending detail activation; pan threshold cancels hold through `pointercancel` semantics; post-gesture clicks are briefly suppressed; stationary intentional long press remains available.

## Renderer lifecycle

Generated renderers reconcile one stable shell/canvas identity. They must not repeatedly wrap generated content or reinstall handlers. Any replacement preserves selected peer, active tab and canvas state before reveal.

## Semantic safety

Generated UI uses verified semantic bindings and never fabricates domain data. Zoom/canvas state cannot change routes, thresholds, `unknown` / `unavailable`, confirmations or commands.

## Adding a subsystem

1. confirm route/parent metadata;
2. add manifest and primary views;
3. define verified domain bindings;
4. adopt Shell v1.4 / Zoom v1.4;
5. encode canvas and gesture-guard metadata;
6. regenerate and pass semantic, lifecycle and target-device acceptance.

## Acceptance

- native HA menu/safe areas/Header/selector/Bottom Tab;
- one transform-owned canvas after repeated HA updates;
- persistent pan at 100% and focal-point pinch;
- no browser-scroll canvas state;
- clamped real bounds;
- reset/snap/feedback/persistence;
- pre-paint restore;
- accidental detail/action suppression plus valid stationary long press;
- no fabricated data;
- CI/Hassfest/HACS and target-device review pass.

## Architectural invariant

> Generated subpanels join declaratively. The shared shell owns native chrome and one transform-owned canvas; domain renderers own verified content only.

