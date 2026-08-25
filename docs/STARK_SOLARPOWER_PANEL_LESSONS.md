# Stark SolarPower panel lessons for the NikaS UI standards

**Field line:** Stark SolarPower mobile UI through 1.8.10  
**Client:** Home Assistant Companion App / iOS WebView  
**Purpose:** evidence record for Shell v1.4, Zoom v1.4, Integration UI v1.5 and Frontend Delivery v1.2

## 1. Integration-owned application boundary works

Domain entities/actions stay in the owning integration while a shared shell contract governs safe areas, Header, peer context, canvas behavior and Bottom Tab navigation.

## 2. Safe area has one owner

The field pass exposed doubled top padding. Effective notch/Dynamic Island and Home Indicator insets must be consumed exactly once; cards/views do not add independent copies.

## 3. The permanent left Header rail is native HA menu

The accepted control dispatches:

```js
new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true })
```

Back, parent-route arrows, integration drawers and device commands do not occupy this rail. Parent navigation belongs inside work content.

## 4. Peer-device context is a shell layer

`UPS Интернет` / `UPS Котёл` remain in fixed order directly below Header. Selection persists between tabs; detailed content belongs only to the selected UPS; selector remains native scale.

## 5. Repeated wrapping is a lifecycle defect

Early rerenders produced nested zoom wrappers, duplicate controls/handlers, blank areas and progressive shrink. Shell reconciliation must find or build exactly one known canvas topology.

## 6. CSS zoom plus native overflow failed on iOS

The original scalable work area combined CSS `zoom` with native `overflow` scrolling. On iOS WebView it was unstable:

- layout could be recomputed instead of remaining one composition;
- after release, enlarged content returned to an edge or the upper-left corner;
- ordinary vertical movement at 100% also snapped back;
- `scrollLeft` / `scrollTop` did not reflect temporary rubber-band displacement;
- saving/restoring those offsets therefore could not preserve the visible position.

Adopted rule: CSS `zoom` and browser scroll coordinates are not the canvas state model.

## 7. One combined transform is stable

Stark 1.8.10 uses one state and one transform:

```text
state = { scale, x, y }
transform = translate3d(x, y, 0) scale(scale)
```

Translation and scale belong to the same transform target. One finger updates `x/y`; two fingers update scale around their midpoint. Final transform remains after release.

## 8. Transform-owned pan is required even at 100%

Using a separate native vertical scroller at 100% recreated the same iOS snap-back. The accepted engine uses the canvas transform for vertical movement at all scales.

## 9. Bounds come from real scaled geometry

Coordinates are clamped from viewport size, unscaled content size and effective scale. This prevents unreachable content, unbounded blank space and browser-dependent edge behavior.

## 10. Rerenders restore before paint

Telemetry updates may replace content DOM. The current panel/UPS `{scale,x,y}` is remembered, attached to new DOM before reveal and then clamped against new geometry. No origin flash or position jump is acceptable.

## 11. Gesture ownership must protect more-info

During early pinch/pan, long-press handlers could open Home Assistant cards and graphs.

Accepted guard:

- second finger immediately blocks pending detail activation;
- pan threshold cancels pending hold using `pointercancel` semantics;
- post-gesture synthetic clicks are briefly suppressed;
- stationary deliberate long press still opens native `more-info`.

## 12. Gesture-only reset remains the standard

Permanent `− / % / +` controls consumed space and participated in rerender defects. They remain prohibited.

- two-finger double tap resets `{scale:1,x:0,y:0}`;
- 97–103% pinch completion uses the same exact reset;
- reset/snap briefly shows `Масштаб 100%`.

## 13. Canvas preference includes peer context

Stark persists canvas state per panel/client and selected UPS. Switching peer restores that peer's state; Bottom Tab changes preserve it.

## 14. Responsive layout precedes transform

Order is:

```text
actual viewport → responsive composition → selected peer content → restored transform
```

User scale never selects breakpoints.

## 15. Visual assets remain separate from data

Local transparent device art and context backgrounds work well when live SVG paths, labels, measurements and semantic overlays remain runtime layers. No live state is baked into decorative pixels.

## 16. Normal data is visually neutral

Green/amber/red belong to confirmed semantics, not ordinary numeric decoration. `unknown`, `unavailable`, stale and untrusted data remain explicit.

## 17. Backend owns factual thresholds

Frontend consumes validated semantic entities such as `data_stale` rather than silently duplicating backend thresholds or inventing unsupported runtime/watts/alarm values.

## 18. Native HA surfaces reduce duplication

Custom UI provides domain overview/context; native `more-info` and history remain preferable for generic factual detail when useful.

## 19. Global actions need ownership and feedback

Refresh uses the integration's stable Home Assistant entity/API, suppresses duplicate activation while busy and reports progress/result where practical.

## 20. Unrelated HA churn should not rebuild shell topology

Performance optimization and shell idempotency are tested together. Any render path preserves peer, tab, one canvas, `{scale,x,y}`, gesture guards and detail bindings.

## 21. Production delivery must be deterministic

One stable production entry, version cache identity, local asset validation, manifest/registration parity and no runtime historical-module chain are release requirements.

## 22. Real iPhone acceptance is part of design

Desktop render did not expose rubber-band scroll state, snap-back, notch padding, accidental `more-info` or rerender timing. Target-device acceptance must include movement at 100%, pinch release, clamped bounds, pre-paint restore and interaction guards.

## 23. Standards promoted from this field result

- `SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.4;
- `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.4;
- `INTEGRATION_DASHBOARD_UI_STANDARD.md` v1.5;
- `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md` v1.2.

Stark SolarPower 1.8.10 is the field reference for the transform-owned canvas revision.

