# Specialized Panel Zoom Standard v1.1

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Architecture:** CONTRACT_GENERATED_UI / shared panel shell

## 1. Purpose

Specialized panels must allow the user to enlarge their working content without scaling or disturbing the surrounding Home Assistant interface. The mechanism is a shared shell capability, not an application-specific implementation.

## 2. Required interaction modes

Every specialized panel must support both:

1. **pinch-to-zoom** with two fingers on phone and tablet;
2. **on-screen zoom controls**: decrease / current percentage / increase.

The two mechanisms operate on the same zoom state.

## 3. Zoom scope

Only the specialized panel working area is zoomed.

The following remain at native Home Assistant scale:

- Home Assistant header/chrome;
- Home Assistant sidebar/main-system navigation;
- specialized panel Header;
- the permanent left Home Assistant main-menu button;
- zoom controls themselves;
- specialized panel fixed Bottom Tab Bar.

Conceptual shell:

```text
HOME ASSISTANT CHROME                  native scale
└── SPECIALIZED PANEL SHELL
    ├── Header / HA main-menu button   native scale
    ├── Zoom controls                  native scale
    ├── Zoom viewport                  scaled
    │   └── Domain content
    └── Bottom Tab Bar                 native scale
```

Browser/page zoom and viewport scaling of the whole Home Assistant application are not accepted implementations.

## 4. Pinch behavior

- Pinch scaling is relative to the point between the two fingers.
- The content under the gesture focal point should remain visually anchored as scale changes.
- When zoomed above 100%, the viewport must permit scrolling/panning so all enlarged content remains reachable.
- Pinch must not accidentally trigger domain actions.
- Normal taps, navigation and Home Assistant more-info behavior must continue to work after scaling.

## 5. On-screen controls

Canonical control:

```text
−   125%   +
```

Required behavior:

- `−` decreases zoom;
- `+` increases zoom;
- tapping the percentage resets zoom to **100%**;
- the displayed percentage always reflects the effective current scale;
- controls remain unscaled and reachable while content is enlarged.

Default policy:

- minimum: **75%**;
- maximum: **200%**;
- button step: **10%**;
- reset: **100%**.

## 6. Persistence

The selected zoom is remembered for the specific panel on the specific client/device. The persistence key must include a stable panel identifier. Changing one specialized panel must not change the zoom of another panel.

The stored value is local UI preference data and is not part of Home Assistant entity state.

## 7. Responsive layout interaction

Responsive layout and user zoom are separate stages:

1. choose the normal mobile/tablet/desktop composition from the actual viewport;
2. render that composition;
3. apply user zoom to the working content inside the zoom viewport.

Zoom must not cause repeated switching between mobile and desktop layouts.

## 8. Shared-shell ownership

Zoom is owned by the common specialized-panel shell/template. Individual domain modules such as ZONT, StarLine, S8 OMNI, HO-SC-8W, Keenetic, Stark SolarPower, UPS or VLESS Gateway must not create independent pinch implementations, zoom controls or persistence schemes.

Default contract:

```yaml
shell:
  zoom:
    enabled: true
    min: 0.75
    max: 2.00
    step: 0.10
    pinch: true
    focal_point: gesture_center
    pan_when_zoomed: true
    reset_on_percentage_tap: true
    persist: per_panel_per_client
```

## 9. Scope of rollout

Mandatory for new specialized panels and progressively added to existing specialized panels, including ZONT, StarLine, S8 OMNI, HO-SC-8W, Keenetic Hero 4G+, Stark SolarPower / UPS, VLESS Gateway and future specialized subsystems.

The central panels `Дом`, `Действия` and `Инфраструктура` are not automatically required to use this specialized-panel zoom shell.

## 10. Safety and state semantics

Zoom is presentation only. It must not change entity selection, semantic inventory, thresholds, `unknown` / `unavailable` handling, navigation routes, confirmation requirements or domain command behavior.

## 11. Acceptance criteria

A specialized panel conforms only when:

- two-finger pinch works on phone and tablet;
- pinch scales around the gesture focal point;
- `− / percentage / +` controls are present and usable;
- tapping percentage restores 100%;
- enlarged content can be panned/scrolled to all regions;
- Header, Home Assistant main-menu button, Home Assistant chrome and Bottom Tab Bar remain at native scale;
- selected scale survives reopening the panel on the same client;
- zoom preference is isolated per panel;
- mobile/desktop responsive composition is preserved;
- taps, navigation and more-info continue to work;
- no independent domain-specific zoom implementation is required.

## Project rule

> One shared zoom mechanism for all specialized panels: pinch-to-zoom plus on-screen controls, scaling only the working area, focal-point-preserving gestures, pan/scroll when enlarged, 100% reset, per-panel/per-client persistence, while the permanent Home Assistant main-menu button and all shell navigation remain at native scale.
