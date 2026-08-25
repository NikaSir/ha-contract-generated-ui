# Specialized Panel Zoom Standard v1.3

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Architecture:** shared specialized-panel shell  
**Field reference:** Stark SolarPower mobile panel

## 1. Purpose

Specialized panels must allow the user to enlarge the working content without scaling or disturbing Home Assistant chrome, application context or navigation.

The Stark SolarPower mobile field pass is the reference for v1.3. It established that the stable mobile pattern is gesture-first: one zoom viewport, no permanent zoom toolbar, explicit gesture reset and idempotent shell lifecycle.

## 2. Zoom scope

Only the work viewport scales.

The following always remain at native scale:

- Home Assistant chrome/sidebar;
- specialized Header;
- permanent Home Assistant main-menu button;
- right Header action;
- persistent peer-device selector;
- fixed Bottom Tab Bar;
- device safe-area surfaces.

Canonical hierarchy:

```text
HEADER / HA MENU                 native
DEVICE SELECTOR (optional)      native
ONE WORK VIEWPORT               scaled
BOTTOM TAB BAR                  native
```

Browser/page zoom is not a conforming panel implementation.

## 3. Required touch interaction

On phone/tablet touch clients every specialized panel MUST support:

- two-finger pinch-to-zoom;
- focal-point preservation around the midpoint between the fingers;
- pan/scroll to every enlarged region;
- two-finger double tap to reset zoom and work-area scroll to 100%;
- persistent scale for the current panel/device context.

Permanent on-screen `− / % / +` zoom controls are **not used** in the standard mobile shell. They consume useful viewport space and, in field experience, increased rerender/lifecycle risk.

## 4. Exactly one work viewport

A specialized panel instance MUST contain exactly one active zoom viewport.

Shell installation/reconciliation must be idempotent across:

- full renders;
- optimized/partial renders;
- unrelated Home Assistant state changes;
- selected-device changes;
- Bottom Tab changes;
- reconnect/reload cycles.

It must never create:

- nested zoom wrappers;
- duplicate gesture handlers;
- abandoned wrappers with blank space;
- progressive shrink/growth caused by scaling an already scaled wrapper;
- duplicate shell layers.

Before creating a viewport, implementation must detect/reuse the existing canonical viewport. Repeated blind post-render wrapping is prohibited.

## 5. Pinch behavior

When a two-finger pinch begins, capture:

- initial touch distance;
- initial effective scale;
- content coordinate under the gesture midpoint.

During the gesture:

```text
new scale = initial scale × current distance / initial distance
```

After applying scale, adjust scroll offsets so the same content coordinate remains under the gesture midpoint as closely as the browser permits.

Required:

- pinch affects only the work viewport;
- normal one-finger scroll remains available;
- enlarged content can pan horizontally and vertically;
- pinch must not execute domain actions;
- taps/long press/more-info continue to work after scaling.

## 6. Scale limits and 100% snap

Default policy:

- minimum: **75%**;
- maximum: **200%**;
- default: **100%**.

When pinch ends, any effective scale in the inclusive range **97–103%** is automatically normalized to exactly **100%**.

The snap is part of the interaction contract, not merely display rounding. Persisted value after the snap must be `1.00` / 100%.

## 7. Two-finger double-tap reset

A two-finger double tap on the work viewport resets:

- scale to exactly **100%**;
- horizontal work-area scroll/pan to its 100% origin;
- vertical work-area scroll/pan to its 100% origin.

After reset, show a brief non-blocking confirmation:

```text
Масштаб 100%
```

The confirmation:

- is transient;
- remains at native scale;
- does not become part of domain content;
- does not reserve permanent layout space;
- must not intercept normal panel interaction after it disappears.

## 8. Persistence scope

Scale is local UI preference, never Home Assistant entity state.

Required isolation:

### Single-device panel

```text
panel-id + client
```

### Multi-peer-device panel

Prefer:

```text
panel-id + peer-device-id + client
```

This follows the proven Stark SolarPower behavior: each peer UPS may restore its own preferred scale.

Changing a Bottom Tab of the same selected device normally preserves scale. If local storage is unavailable, zoom must continue to work for the current session.

## 9. Responsive layout interaction

Responsive layout and user zoom are separate stages:

1. actual viewport selects mobile/tablet/desktop composition;
2. application context selects peer device/domain content;
3. user scale is applied to the single work viewport.

Zoom must not change breakpoint selection or cause repeated mobile/desktop switching.

## 10. Rerender behavior

Home Assistant can update many unrelated entities while a specialized panel is open.

A conforming implementation preserves zoom state and viewport topology when:

- unrelated HA state changes arrive;
- domain renderer skips a full render;
- only part of the UI changes;
- selected peer changes;
- Bottom Tab changes.

Preferred architecture keeps shell DOM stable and updates/replaces only domain content inside the known work viewport.

## 11. Interaction with Device Selector

Persistent peer-device selector remains outside the zoom viewport at native scale.

When peer selection changes:

- selector geometry/order does not change;
- current Bottom Tab remains selected unless domain rules say otherwise;
- work content switches in place;
- device-scoped scale is restored when that persistence mode is used.

## 12. Safety and state semantics

Zoom is presentation only. It must not change:

- entity selection;
- semantic inventory;
- health/stale thresholds;
- `unknown` / `unavailable` behavior;
- navigation routes;
- confirmations;
- domain commands;
- source-trust semantics.

## 13. Acceptance criteria

A specialized panel conforms when:

1. two-finger pinch works on phone/tablet;
2. focal point remains visually anchored;
3. enlarged content pans/scrolls to all regions;
4. Header, HA menu, Device Selector and Bottom Tab Bar remain native scale;
5. no permanent zoom toolbar occupies the mobile viewport;
6. pinch end in 97–103% snaps to exactly 100%;
7. two-finger double tap resets zoom and work-area scroll to 100%;
8. reset briefly confirms `Масштаб 100%`;
9. scale persists per panel/client and, where applicable, per peer device;
10. exactly one zoom viewport exists after repeated HA state updates;
11. no nested wrappers, duplicate handlers, blank wrapper space or progressive shrinkage occurs;
12. responsive composition remains independent of zoom;
13. normal tap/long-press/more-info behavior remains valid.

## 14. Default contract

```yaml
shell:
  zoom:
    enabled: true
    min: 0.75
    max: 2.00
    default: 1.00
    pinch: true
    focal_point: gesture_center
    pan_when_zoomed: true
    persistent_controls: false
    snap_to_100_range: [0.97, 1.03]
    reset_gesture: two_finger_double_tap
    reset_scroll: true
    reset_feedback: "Масштаб 100%"
    persist: per_panel_per_client
    peer_device_scope: preferred_when_applicable
    viewport_count: 1
    install: idempotent
```

## Project rule

> Every specialized panel has exactly one zoomable work viewport. Two-finger focal-point pinch, pan/scroll and persistence are mandatory. Permanent zoom buttons are not used. Pinch ending at 97–103% snaps to 100%, and a two-finger double tap resets scale and scroll with brief `Масштаб 100%` feedback.