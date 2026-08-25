# Specialized Panel Zoom Standard v1.4

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Architecture:** transform-owned fixed canvas  
**Reference field implementation:** Stark SolarPower 1.8.10 on iOS Home Assistant Companion App

## 1. Purpose

Specialized panels must allow the user to enlarge and move their working content without scaling or disturbing Home Assistant chrome, persistent peer-device context or fixed navigation.

The required mobile architecture is a single fixed canvas whose complete visual state is owned by the panel:

```text
transform = translate3d(x, y, 0) scale(s)
state = { scale: s, x, y }
```

Browser scroll position is not canvas state.

## 2. iOS field finding

The former implementation used CSS `zoom` plus native `overflow` scrolling and tried to preserve `scrollLeft` / `scrollTop`. It is non-conforming.

On iOS WebView that model produced:

- layout recomputation that broke the canvas as one composition;
- nested zoom containers and duplicated controls after rerender;
- elastic/rubber-band displacement visible while the finger was down but not represented by durable scroll coordinates;
- snap-back to a boundary or the upper-left corner after gesture release;
- the same snap-back during ordinary vertical movement at 100%;
- accidental Home Assistant `more-info` / history graph activation during pinch or pan.

The project must not use CSS `zoom`, page/browser zoom, `scrollLeft`, `scrollTop` or native overflow scrolling as the position engine for a scalable panel canvas.

## 3. Layer and scale ownership

The following always remain at native scale:

- Home Assistant chrome/sidebar;
- specialized Header and permanent Home Assistant menu button;
- right Header action;
- persistent peer-device selector;
- fixed Bottom Tab Bar;
- safe-area surfaces;
- transient reset confirmation.

Only the working canvas transforms.

```text
HEADER / HA MENU                         native
DEVICE SELECTOR (optional)              native
ONE FIXED CANVAS VIEWPORT               native clipping window
  └── CANVAS CONTENT                    translate3d(x,y,0) scale(s)
BOTTOM TAB BAR                          native
```

## 4. Exactly one canvas viewport

A specialized-panel instance contains exactly one active canvas viewport and exactly one transform target.

The viewport owns clipping and gesture capture. It may use `overflow: hidden`, but it does not own a browser scroll position. The canvas content uses `transform-origin: 0 0` and one combined transform.

Shell installation/reconciliation is idempotent across full renders, optimized renders, unrelated Home Assistant state changes, peer-device changes, Bottom Tab changes, reconnects and reloads.

It must never create nested wrappers, duplicate gesture handlers, duplicate reset messages, abandoned blank wrappers or progressive shrinking/growth.

## 5. Canvas state

The complete durable presentation state is:

```text
scale
x
y
```

No second state source may compete with this tuple. Native scroll offsets are ignored and normally remain zero.

Persistence scope:

- single device: `panel-id + client`;
- multiple peer devices: `panel-id + peer-device-id + client`.

Changing Bottom Tab for the same peer preserves state. Changing peer restores that peer's state. Zoom/pan state is local UI data, never a Home Assistant entity.

## 6. Transform application

The only canvas transform is:

```css
transform-origin: 0 0;
transform: translate3d(var(--x), var(--y), 0) scale(var(--scale));
will-change: transform;
```

Translation and scale must not be split between unrelated DOM layers. Splitting them makes focal-point calculations, clamping, persistence and rerender recovery ambiguous.

## 7. One-finger pan

One touch moves `x/y` directly.

- movement begins only after a small threshold so an intentional stationary hold remains possible;
- the same transform-owned mechanism provides vertical movement at 100%;
- the canvas does not hand movement to native `overflow` scrolling;
- after finger release, the final transform remains unchanged;
- the final state is persisted.

## 8. Two-finger focal-point pinch

At pinch start capture the initial distance, initial scale, initial `x/y` and the content coordinate below the midpoint.

```text
newScale = startScale * currentDistance / startDistance
contentX = (midX - x) / scale
contentY = (midY - y) / scale
newX = currentMidX - contentX * newScale
newY = currentMidY - contentY * newScale
```

This keeps the content point below the fingers as stable as possible without consulting browser scroll state.

Default scale limits are 75–200%, with 100% as the default.

## 9. Coordinate clamping

After every scale or translation change, constrain `x/y` using the real unscaled canvas size, effective scale and viewport size.

```text
scaledWidth  = contentWidth  * scale
scaledHeight = contentHeight * scale
minX = min(0, viewportWidth  - scaledWidth)
minY = min(0, viewportHeight - scaledHeight)
maxX = 0
maxY = 0
```

Clamp to these limits or to an explicitly documented centering policy when scaled content is smaller than its viewport. Bounds must be recalculated after responsive recomposition, peer change, content-size change and viewport resize.

## 10. Rerender and telemetry updates

Before replacing work-content DOM, remember the current `{scale,x,y}` for its panel/peer key.

When new DOM is produced:

1. create or reconcile one known canvas viewport;
2. restore the saved state on the new transform target synchronously;
3. clamp against the new measured geometry;
4. reveal/commit the visual frame only after the transform is attached.

Users must not see an intermediate untransformed frame, and telemetry updates must not reset or move the canvas.

## 11. Interaction protection

Gesture ownership must not break deliberate Home Assistant detail access.

Required:

- the appearance of a second finger immediately blocks pending `more-info` and domain activation;
- when one-finger movement crosses the pan threshold, dispatch/cause `pointercancel` for the pending hold target;
- click events synthesized after a completed gesture are suppressed for a short guard interval;
- pinch/pan/reset never execute device actions;
- an intentional stationary long press still opens standard Home Assistant `more-info`;
- ordinary intentional taps remain available when no gesture was recognized.

## 12. Reset and snap-to-100

Permanent `− / % / +` controls are not used.

Two quick two-finger taps reset:

```text
scale = 1
x = 0
y = 0
```

When pinch ends within 97–103%, the same reset path fixes scale and position to exact 100%/origin.

After explicit reset or snap, briefly show the non-interactive native-scale confirmation:

```text
Масштаб 100%
```

Use polite accessibility status where practical.

## 13. Responsive layout

Order is fixed:

```text
actual viewport
→ mobile/tablet/desktop composition
→ selected peer/domain content
→ restored transform state
```

User scale must not choose breakpoints or trigger repeated responsive switching.

## 14. Safety and semantics

Transform state must not change entity selection, semantic inventory, trust/stale thresholds, `unknown` / `unavailable` behavior, routes, confirmations or domain commands.

## 15. Acceptance criteria

A panel conforms only when:

1. exactly one canvas viewport and transform target exist after repeated HA updates;
2. CSS `zoom` and native overflow scroll are not the canvas position engine;
3. one-finger movement persists after release, including vertical movement at 100%;
4. focal-point pinch uses the combined transform;
5. all regions are reachable within real clamped bounds;
6. Header, HA menu, selector and Bottom Tab Bar remain native scale;
7. no permanent zoom buttons are rendered;
8. two-finger double tap resets `{scale,x,y}`;
9. 97–103% snaps to exact 100%;
10. `Масштаб 100%` appears briefly;
11. state persists per panel/client and peer device where applicable;
12. telemetry rerender restores transform before the visible frame;
13. pinch/pan suppress accidental `more-info`, graphs, clicks and commands;
14. stationary long press still opens `more-info`;
15. no nested wrappers, blank space or progressive shrink occurs.

## 16. Default contract

```yaml
shell:
  zoom:
    engine: transform_owned_canvas
    viewport_count: 1
    transform_target_count: 1
    transform: translate3d_xy_scale
    native_overflow_pan: false
    css_zoom: false
    min: 0.75
    max: 2.00
    default: 1.00
    one_finger_pan: true
    pan_at_100_percent: true
    pinch: true
    focal_point: gesture_midpoint
    coordinates: clamped_to_scaled_content
    controls: none
    reset_gesture: two_finger_double_tap
    reset_state: {scale: 1.0, x: 0, y: 0}
    snap_to_100_percent_range: [97, 103]
    reset_feedback: "Масштаб 100%"
    persist: per_panel_per_client
    peer_device_scope: per_device_when_present
    restore_before_paint: true
    cancel_hold_on_pan: pointercancel
    suppress_post_gesture_click: true
    install: idempotent
```

## Project rule

> A specialized panel uses one fixed transform-owned canvas. `translate3d(x,y,0) scale(s)` is the complete zoom/pan state. Browser scrolling is not canvas state; rerenders restore `{scale,x,y}` before paint, and gesture guards prevent accidental Home Assistant actions.

