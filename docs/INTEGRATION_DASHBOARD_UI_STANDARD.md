# Integration-owned dashboard UI standard v1.5

**Status:** Required  
**Applies to:** all integration-owned specialized dashboards in Home Assistant NikaS  
**Primary target:** iPhone Pro Max, portrait  
**Related standards:** Shell v1.4 · Zoom v1.4 · Frontend Delivery v1.2  
**Reference field implementation:** Stark SolarPower 1.8.10

## 1. Application model

Integration-owned dashboards behave as mobile applications inside Home Assistant. The integration owns domain data/actions/presentation; shared NikaS standards own the application shell and release invariants.

Single device:

```text
Header → Transform-owned canvas → Bottom Tab Bar
```

Multiple peer devices:

```text
Header → Device Selector → Transform-owned selected-device canvas → Bottom Tab Bar
```

## 2. Header and system menu

The left Header rail is always Home Assistant `☰` and dispatches `hass-toggle-menu` with bubbling/composed semantics.

It is never Back, browser history, an integration-specific drawer or a device action. If parent/drill-down navigation is required, place it inside the work canvas.

Title is geometrically viewport-centered, concise and free from decorative brand/device artwork. The right rail contains at most one global action such as Refresh, with busy/success/error feedback when practical. Header stays below Dynamic Island/notch and remains native scale.

## 3. Safe areas

Effective top/bottom/side insets have exactly one owner. No phone-model constants and no duplicated inset layers. Bottom Tab stays above Home Indicator.

## 4. Peer Device Selector

Use only for peer physical devices, not zones/channels/components. It remains directly below Header, native scale, fixed-order and persistent across Bottom Tabs. Primary content belongs only to the selected peer.

Stark reference: `UPS Интернет` / `UPS Котёл` remain in fixed order and restore their own canvas state.

## 5. Bottom Tab Bar

Applications with 3–5 primary destinations use one full-width fixed edge-attached native-scale Bottom Tab Bar. It is never a floating pill. Canvas bounds and bottom reserve must make final content reachable above the bar.

## 6. Transform-owned working canvas

Only domain work content moves or scales.

```text
translate3d(x, y, 0) scale(s)
```

The panel stores `{scale,x,y}` and does not use CSS `zoom`, browser/page zoom, `scrollLeft`, `scrollTop` or native overflow scrolling as canvas state.

- one finger pans at any scale, including vertical movement at 100%;
- two fingers pinch around their midpoint;
- real scaled-content dimensions clamp coordinates;
- the final transform remains after release;
- state persists per panel/client and peer device where applicable;
- replacement DOM receives the saved transform before the visible frame;
- exactly one viewport/target/handler set exists after every rerender.

## 7. Gesture safety and Home Assistant detail

- a second finger immediately blocks pending `more-info`;
- crossing the pan threshold cancels pending hold through `pointercancel` semantics;
- post-gesture synthetic clicks are briefly suppressed;
- gestures never execute domain commands;
- stationary intentional long press continues to open native `more-info`.

## 8. Zoom controls and reset

Permanent `− / % / +` controls are not used.

- two-finger double tap resets scale and coordinates to 100%/origin;
- pinch ending at 97–103% snaps to exact 100%/origin;
- reset/snap briefly shows `Масштаб 100%` at native scale.

## 9. First useful viewport

Within a few seconds the user must understand current state, reliability and whether action is required. Navigation chrome must not push the primary factual state out of the useful iPhone viewport without reason.

## 10. State semantics

- normal factual measurements use neutral typography;
- green/amber/red are reserved for confirmed semantic state;
- `unknown`, `unavailable`, stale and untrusted source never look healthy;
- backend validated thresholds and semantic entities remain authoritative;
- unsupported values are not invented;
- factual entity-backed elements reuse native HA more-info/history where useful.

## 11. Visual assets

Critical art ships locally and is cache-busted. Background/context art contains no live HA values/status text. Device art, SVG paths, labels, measurements and semantic overlays remain separate runtime layers.

## 12. Render and delivery stability

Unrelated HA churn should not rebuild complete shell topology when practical. Any render path preserves selected peer, active tab and `{scale,x,y}`. If content DOM is replaced, the transform is restored before reveal/paint.

Each integration ships one deterministic self-contained frontend entry with manifest/registration parity, local assets and release cache identity.

## 13. Application guidance

### Stark SolarPower

Reference multi-peer implementation. Keep fixed UPS order, selected-device-only detail and per-UPS canvas state.

### S8 OMNI

Robot + station form one system, not peer devices. Preserve composite state and primary cleaning/station workflows.

### HO-SC-8W / irrigation

Zones are channels of one controller, not peer devices. Preserve verified read/write safety boundaries.

### Keenetic Hero 4G+

Ethernet/LTE are channels of one router, not peer devices. First state prioritizes Internet, active WAN/LTE and failover.

### ZONT, StarLine and VLESS Gateway

Use the same shell/canvas contract while keeping domain semantics in the owning repository.

## 14. Acceptance

A panel is compliant only when:

- `☰` dispatches `hass-toggle-menu`; no permanent Back occupies that rail;
- safe area is consumed once;
- Header, selector and Bottom Tab remain native scale;
- exactly one transform-owned canvas exists;
- CSS `zoom` and native overflow scrolling are not canvas position engines;
- one-finger movement at 100% and focal-point pinch persist after release;
- bounds reflect real scaled content;
- no permanent zoom controls appear;
- double-tap reset, 97–103% snap and `Масштаб 100%` work;
- per-panel/peer state survives telemetry rerender without an origin flash;
- gestures suppress accidental details/actions while stationary hold still works;
- unavailable/stale states remain explicit;
- production bundle/manifest/assets/release identity validate;
- target-device field acceptance passes.

## Conceptual metadata

```yaml
shell:
  standard: specialized-panel-shell/v1.4
  safe_area_owner: application_once
header:
  left_event: hass-toggle-menu
  title_alignment: viewport_center
zoom:
  standard: specialized-panel-zoom/v1.4
  engine: transform_owned_canvas
  transform: translate3d_xy_scale
  state: [scale, x, y]
  native_overflow_pan: false
  css_zoom: false
  controls: []
  reset_gesture: two_finger_double_tap
  snap_to_100_percent_range: [97, 103]
  restore_before_paint: true
  viewport_count: 1
```

## Project rule

> Integration-owned panels are native-chrome Home Assistant applications with a permanent HA menu, optional peer context, one transform-owned canvas and fixed Bottom Tab navigation. Browser scroll is never the canvas state model.

