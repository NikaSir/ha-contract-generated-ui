# Specialized Panel Zoom Standard v1.2

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Architecture:** shared specialized-panel shell

## 1. Purpose

Specialized panels must allow the user to enlarge their working content without scaling or disturbing Home Assistant chrome, application context or navigation.

Stark SolarPower UI 0.5.4–0.5.5 proved two additional requirements that are now normative:

- zoom-shell installation must be idempotent and produce exactly one work viewport;
- on-screen controls are a shell presentation option, while focal-point pinch is the mandatory touch interaction.

## 2. Required interaction

On phone/tablet touch clients every specialized panel MUST support:

- **two-finger pinch-to-zoom**;
- focal-point preservation around the midpoint between the fingers;
- pan/scroll to every enlarged region;
- persistent scale.

On-screen `− / percentage / +` controls are optional shell presentation. A panel declares whether they are shown.

This policy allows compact gesture-only mobile compositions while keeping one canonical control behavior when visible controls are useful.

## 3. Zoom scope

Only the work viewport scales.

The following remain at native scale:

- Home Assistant chrome/sidebar;
- specialized Header;
- permanent Home Assistant main-menu button;
- right Header action;
- persistent peer-device selector;
- zoom controls when enabled;
- fixed Bottom Tab Bar;
- safe-area surfaces.

Canonical hierarchy:

```text
HEADER / HA MENU                 native
DEVICE SELECTOR (optional)      native
ZOOM CONTROLS (optional)        native
ONE WORK VIEWPORT               scaled
BOTTOM TAB BAR                  native
```

Browser/page zoom is not a conforming panel implementation.

## 4. Exactly one work viewport

A specialized panel instance must contain exactly one active zoom viewport.

The shell must be idempotent across:

- full renders;
- optimized renders;
- unrelated Home Assistant state changes;
- selected-device changes;
- Bottom Tab changes;
- reconnect/reload cycles.

It must never create:

- nested zoom wrappers;
- duplicate controls;
- abandoned wrappers with blank space;
- progressive shrink/growth caused by scaling an already scaled wrapper.

When migrating a legacy implementation, old wrappers may be normalized/unwrapped before the canonical viewport is installed. That is a migration technique, not the desired steady-state architecture.

## 5. Pinch behavior

When a two-finger gesture begins, capture:

- initial touch distance;
- initial effective scale;
- content coordinate under the gesture midpoint.

While the gesture changes:

```text
new scale = initial scale × current distance / initial distance
```

After applying scale, scroll offsets are adjusted so the same content coordinate remains under the current gesture midpoint as closely as the browser permits.

Required:

- pinch affects only the work viewport;
- normal one-finger scroll remains available;
- enlarged content can pan horizontally and vertically;
- pinch must not accidentally execute domain actions;
- taps/long press/more-info continue to work after scaling.

## 6. Scale limits

Default policy:

- minimum: **75%**;
- maximum: **200%**;
- default: **100%**;
- visible-control step, when controls exist: **10%**.

A narrower range is allowed only for a documented technical reason. The panel may not remove pinch support silently.

## 7. Optional on-screen controls

When enabled, use exactly one native-scale control group:

```text
−   125%   +
```

Behavior:

- `−` decreases by configured step;
- `+` increases by configured step;
- percentage always shows effective scale;
- tapping percentage resets to **100%**;
- controls are outside the zoom viewport;
- controls do not cover Header, selector or Bottom Tab Bar;
- controls are shell-owned, not recreated independently by each domain view.

A gesture-only panel is conforming when metadata explicitly declares controls hidden/disabled and all mandatory pinch/pan/persistence behavior passes field acceptance.

## 8. Persistence scope

Scale is local UI preference, never Home Assistant entity state.

Required stable scope:

### Single-device panel

```text
panel-id + client
```

### Multi-peer-device panel

The panel MAY and generally SHOULD include the selected peer-device identity:

```text
panel-id + peer-device-id + client
```

This follows the proven Stark SolarPower behavior: switching peer UPS can restore that UPS's own preferred scale.

Changing one panel must not change another panel's scale. Changing subordinate sections/tabs of the same selected device should normally preserve scale.

If browser/local storage is unavailable, zoom must continue to work for the current session rather than making the panel unusable.

## 9. Responsive layout interaction

Responsive layout and user zoom are independent stages:

1. actual viewport selects mobile/tablet/desktop composition;
2. application context selects device/domain content;
3. user scale is applied to the work viewport.

Zoom does not change breakpoint selection and must not cause repeated mobile/desktop layout switching.

## 10. Rerender behavior

Home Assistant can update many unrelated entities while a specialized panel is open.

A conforming zoom implementation must preserve scale and viewport topology when:

- unrelated HA state changes arrive;
- the domain renderer skips a full render because relevant state did not change;
- only part of the UI changes;
- selected peer changes;
- a Bottom Tab changes.

Recommended:

- keep shell DOM stable and replace/update domain content inside it;
- or explicitly reconcile one known viewport by stable selector/identity.

Repeated blind post-render wrapping is prohibited.

## 11. Interaction with Device Selector

Persistent peer-device selector remains native scale and outside the work viewport.

When peer selection changes:

- selector geometry does not change;
- current Bottom Tab remains selected;
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

A state cannot become hidden or be reinterpreted because of zoom.

## 13. Accessibility and motion

- touch targets outside the zoom viewport retain their native accessible size;
- zoom controls, when shown, expose meaningful `aria-label` text;
- current percentage is announced accurately;
- pinch should not depend on animation;
- reduced-motion preference must not disable core zoom functionality.

## 14. Acceptance criteria

A specialized panel conforms when:

- two-finger pinch works on phone/tablet;
- focal point remains visually anchored;
- enlarged content pans/scrolls to all regions;
- only one work viewport exists after repeated state updates;
- no nested wrappers or progressive shrinkage occurs;
- Header, HA menu, Device Selector and Bottom Tab Bar remain native scale;
- scale survives reopening on the same client when storage is available;
- persistence is isolated per panel and optionally per peer device;
- responsive composition is preserved;
- normal tap/long-press/more-info behavior remains valid;
- optional controls, when enabled, exist once and perform `− / % / +` behavior correctly;
- gesture-only presentation, when declared, has no hidden dependence on removed controls.

## 15. Default contract

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
    controls: optional
    control_step: 0.10
    reset_on_percentage_tap: true
    persist: per_panel_per_client
    peer_device_scope: allowed
    viewport_count: 1
    install: idempotent
```

## Project rule

> Every specialized panel has exactly one zoomable work viewport. Two-finger focal-point pinch, pan/scroll and persistence are mandatory on touch clients. On-screen `− / % / +` controls are an optional shell presentation and, when enabled, exist exactly once outside the scaled content.
