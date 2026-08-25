# NikaS Integration Panel Template v1.2

**Status:** Required development-time template  
**Canonical standards:** Shell v1.4 · Zoom v1.4 · Integration UI v1.5 · Frontend Delivery v1.2  
**Primary target:** iPhone Pro Max portrait

## 1. Fixed hierarchy

```text
AppHeader (native)
  └── HA MenuButton | centered title | global action
DeviceContextSelector (optional, native)
CanvasViewport (one, fixed)
  └── CanvasContent: translate3d(x,y,0) scale(s)
BottomTabBar (native)
```

## 2. Header

The left button is Home Assistant `☰` and dispatches `hass-toggle-menu`. It is never Back, browser history, integration menu or device action. Parent/drill-down navigation belongs inside CanvasContent.

Title is viewport-centered; right rail contains at most one global action; Header consumes effective top safe area once and remains native scale.

## 3. Device context

Use only for peer physical devices. Keep fixed order, persistent selection, selected-peer-only detail and native scale outside CanvasViewport.

## 4. Transform-owned canvas

The reference implementation must provide exactly one CanvasViewport/CanvasContent pair.

- `overflow: hidden` clips the viewport but is not a native scrolling engine;
- canvas position never comes from `scrollLeft` / `scrollTop`;
- transform is `translate3d(x,y,0) scale(s)`;
- one finger pans, including vertical movement at 100%;
- two fingers pinch around their midpoint;
- bounds use actual scaled canvas geometry;
- `{scale,x,y}` persists per panel/client and peer device;
- rerender applies saved transform before revealing the new frame;
- lifecycle is idempotent.

## 5. Gesture/detail arbitration

- second finger cancels pending detail activation;
- pan threshold emits `pointercancel` semantics;
- post-gesture click is temporarily suppressed;
- stationary intentional long press still dispatches `hass-more-info`.

## 6. Reset

No permanent zoom buttons. Two-finger double tap resets `{scale:1,x:0,y:0}`; 97–103% snaps to the same state; briefly show `Масштаб 100%`.

## 7. Shared content primitives

Use HeroStatus, StatusCard, MetricCard, StateRow, ActionCard, AlertCard and Diagram only when the diagram improves understanding. Normal facts are neutral; semantic colors express confirmed state; unreliable data remains explicit.

## 8. Bottom Tab Bar

Use 3–5 fixed full-width safe-area-aware destinations. It remains native scale. Canvas bounds/bottom reserve make final content reachable above it.

## 9. Loading and rerender

Loading preserves the same Header/selector/canvas/Bottom Tab topology. Telemetry updates patch content where practical; replacement DOM is transformed before reveal.

## 10. Production rule

Copy/adapt the development-time reference into the integration and build one self-contained production entry. Never import the template or another repository at runtime. Validate manifest/registration/assets/cache identity and target iPhone behavior.

## 11. Developer variability

Developers choose title/subtitle, peer-device data, tabs, domain content/actions/diagrams and optional work-area parent navigation. They do not redesign Header/menu, safe areas, canvas engine, gesture guards, Bottom Tab geometry, state semantics or delivery rules.

## 12. Acceptance

The template is accepted only when it contains no arrow-Back Header, no CSS zoom/native overflow pan, exactly one transform target, persistent release position, pre-paint restoration, reset/snap feedback, interaction guards and native long-press detail behavior.

