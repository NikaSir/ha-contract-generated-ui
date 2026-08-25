# Specialized Panel Frontend Delivery Standard v1.2

**Status:** Required for integration-owned specialized panels with custom frontend  
**Canonical owner:** `NikaSir/ha-contract-generated-ui`  
**Reference implementation:** Stark SolarPower 1.8.10

## 1. Purpose

A specialized panel can be visually correct yet fail because of stale modules, broken runtime imports, missing assets, duplicated shell installation or render timing that exposes an untransformed frame. This standard defines packaging, registration, cache identity, manifest parity and release gating.

## 2. One stable production entry

Each integration exposes exactly one self-contained production frontend module. Historical/versioned modules may remain build-time history but are not a runtime import chain.

## 3. Deterministic build and cache identity

- source-to-bundle rebuild is deterministic where applicable;
- UI/build version participates in production module URL cache busting;
- changed local assets receive predictable cache invalidation;
- release notes identify frontend behavior changes.

## 4. Home Assistant registration

Registration and manifest agree on stable route, web-component name, module URL, UI version, asset paths, safe-area owner, `hass-toggle-menu` and canvas policy.

Custom-panel registration must not cause safe-area insets to be consumed twice.

## 5. Local assets

Panel-critical art ships with the integration, is reachable through local static routes, is included in HACS packaging and has validated dimensions/existence. No critical CDN dependency and no Base64 image payload where a normal asset is suitable.

## 6. Machine-readable manifest

Reference fields:

```yaml
api_version: nikas.home-assistant/integration-panel/v1
id: subsystem
path: /dashboard-subsystem
owner: integration_domain
ui_version: 1.2.3
shell:
  standard_version: "1.4"
  safe_area_owner: application_once
header:
  left_control:
    type: home_assistant_system_menu
    event: hass-toggle-menu
  title_alignment: viewport_center
zoom:
  standard_version: "1.4"
  engine: transform_owned_canvas
  viewport_count: 1
  transform_target_count: 1
  transform: translate3d_xy_scale
  state: [scale, x, y]
  css_zoom: false
  native_overflow_pan: false
  one_finger_pan: true
  pan_at_100_percent: true
  pinch: true
  controls: []
  reset_gesture: two_finger_double_tap
  snap_to_100_percent_range: [97, 103]
  persistence: local_per_panel_and_device
  restore_before_paint: true
  cancel_hold_on_pan: pointercancel
  suppress_post_gesture_click: true
frontend_delivery:
  mode: self_contained_bundle
  module: panel-bundle.js
  assets: []
  cache_busting: query_ui_version
  runtime_previous_version_imports: false
targets:
  primary: iPhone Pro Max portrait
```

## 7. Manifest / runtime parity

CI or release validation checks:

- registration route/component/module;
- UI version and cache-busting value;
- declared asset existence;
- permanent HA menu event;
- exactly one transform-owned canvas policy;
- no CSS zoom/native overflow pan policy;
- reset/snap/persistence/pre-paint restore policy;
- gesture interaction guard policy.

## 8. JavaScript validation

- production and source JS pass syntax check;
- self-contained bundle rejects prohibited runtime historical imports;
- deterministic rebuild parity passes where applicable;
- HACS/Hassfest/repository checks remain required.

## 9. Runtime shell regression guard

Static syntax is insufficient. Test where practical:

- one viewport and transform target after repeated renders;
- no nested wrappers/duplicate handlers/reset messages;
- no permanent zoom toolbar;
- `hass-toggle-menu` works;
- one-finger pan at 100% and pinch persist after release;
- CSS `zoom`, `scrollLeft` and `scrollTop` are not transform state;
- real bounds clamp the canvas;
- replacement DOM restores `{scale,x,y}` before visible frame;
- second finger/pan threshold/post-gesture guard suppress accidental detail/actions;
- stationary long press still opens `more-info`.

## 10. Cold-start and target-client gate

Verify empty-cache start, full HA restart, repeated panel opens, local and Nabu Casa access, correct asset version, no stale prior UI and correct Companion App behavior.

## 11. Acceptance

Delivery is complete only when:

1. one stable production entry exists;
2. cache identity changes with frontend release;
3. build and syntax validation pass;
4. manifest/registration/runtime agree;
5. critical local assets exist;
6. safe area is consumed once;
7. HA menu contract works;
8. manifest encodes transform-owned canvas and gesture guards;
9. lifecycle regression passes;
10. target iPhone field check confirms movement/pinch persistence, pre-paint restore and no accidental details/actions.

## Project rule

> A specialized panel release includes deterministic frontend identity plus machine-verifiable transform-canvas, menu, safe-area, rerender and interaction-safety invariants.

