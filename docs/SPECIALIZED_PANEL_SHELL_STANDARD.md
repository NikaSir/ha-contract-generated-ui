# Specialized Panel Shell Standard v1.3

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Primary acceptance viewport:** iPhone Pro Max, portrait  
**Architecture:** `CONTRACT_GENERATED_UI` / integration-owned compatible shell

## 1. Purpose

All specialized panels use one application-shell contract so they behave like parts of the same Home Assistant system without forcing domain UI into one repository.

The shell owns application chrome and viewport behavior. The integration/domain implementation owns entities, telemetry, commands, cards and domain semantics.

Canonical hierarchy:

```text
HOME ASSISTANT / DEVICE SAFE AREA
↓
SPECIALIZED PANEL HEADER                     native scale
  └── ☰ HA main menu | centered title | action
↓
DEVICE SELECTOR (when peer devices exist)     native scale
↓
EXACTLY ONE ZOOMABLE WORK VIEWPORT             user scale
  └── selected-device / domain content
↓
BOTTOM TAB BAR                                native scale
↓
DEVICE BOTTOM SAFE AREA / HOME INDICATOR
```

The Stark SolarPower mobile field pass is the reference evidence for v1.3.

## 2. Ownership invariant

A specialized domain module MUST NOT independently define incompatible versions of:

- safe-area ownership;
- Header geometry;
- Home Assistant main-menu button meaning;
- title centering;
- zoom viewport topology/gestures;
- persistent peer-device selector placement;
- primary Bottom Tab Bar geometry;
- fixed shell clearances.

The domain implementation owns domain status, telemetry, commands, cards, visualizations, peer-device data/labels and domain-specific context artwork.

**Migration rule:** shell migration must not be combined with unrelated domain-UI refactoring.

## 3. Safe-area contract — consume once

Safe areas have exactly one effective owner at each boundary.

Use Home Assistant/browser safe-area values rather than phone-model constants:

```css
env(safe-area-inset-top, 0px)
env(safe-area-inset-right, 0px)
env(safe-area-inset-bottom, 0px)
env(safe-area-inset-left, 0px)
```

If Home Assistant or `panel_custom` already consumes/exposes the effective inset, the specialized shell must not add the same inset again.

Required:

- no Header content under notch/Dynamic Island;
- no bottom navigation under Home Indicator;
- no duplicate blank band from double safe-area consumption;
- no device-specific fixes such as `top: 47px`;
- no per-view independent safe-area padding.

Field acceptance in Home Assistant Companion App is mandatory.

## 4. Top Header

Canonical geometry:

```text
┌─────────────────────────────────────┐
│  ☰           PANEL TITLE          ⟳ │
│              subtitle               │
└─────────────────────────────────────┘
```

Required:

- left rail is always the **Home Assistant main-system menu**;
- it dispatches the standard Home Assistant event `hass-toggle-menu`;
- it is never permanent Back, integration drawer or device action;
- title is geometrically centered relative to the viewport;
- right rail contains at most one shell/global action;
- left/right rails use matching geometry whenever practical;
- touch targets are approximately 44×44 pt or larger;
- primary title remains concise and one-line on reference iPhone;
- optional subtitle carries model/context/version;
- decorative integration/device artwork is not placed beside Header title;
- title is not duplicated as an oversized heading below.

If parent/drill-down navigation is needed, place it inside the work area. It never replaces the permanent HA menu button.

Header/menu/title/right action remain at native scale and below the effective top safe area.

## 5. Persistent peer-device selector

When one application owns multiple peer physical devices, Device Selector is a first-class application-context layer.

Placement:

```text
HEADER
↓
DEVICE SELECTOR
↓
WORK VIEWPORT
```

Required:

- directly below Header on every primary section;
- native scale and outside zoom viewport;
- fixed device order;
- selection never reorders devices;
- selected peer survives Bottom Tab changes;
- compact health dot/badge for non-selected peers is allowed;
- detailed content belongs only to selected peer;
- do not append full cards for all peers below selected-device context;
- newly discovered peer should reuse same template where integration model permits.

Subordinate channels of one device are not peer devices merely because they are selectable.

## 6. Exactly one zoomable work viewport

There is exactly one zoomable work viewport per specialized-panel instance.

Native-scale layers outside it:

- Home Assistant chrome;
- Header and HA menu button;
- persistent Device Selector;
- Bottom Tab Bar;
- safe-area surfaces;
- transient reset feedback.

Responsive composition is resolved before zoom:

```text
actual viewport
→ mobile/tablet/desktop composition
→ peer-device/domain context
→ user zoom
```

Shell installation/reconciliation MUST be idempotent. Repeated HA renders/partial updates must never create nested wrappers, duplicate gesture handlers, progressive shrinkage, blank abandoned wrapper space or duplicate shell layers.

The implementation must detect/reuse the canonical viewport rather than blindly wrapping the work area again.

## 7. Zoom interaction policy

Normative behavior is defined by `SPECIALIZED_PANEL_ZOOM_STANDARD.md`.

Mobile shell policy:

- primary interaction is two-finger focal-point pinch;
- permanent `− / % / +` controls are not used;
- pinch ending at 97–103% snaps to exactly 100%;
- two-finger double tap resets zoom and work-area scroll to 100%;
- reset briefly shows `Масштаб 100%` at native scale;
- scale persists locally per panel/client and preferably per peer device where applicable.

The shell must not reserve permanent layout space for zoom controls.

## 8. Bottom Tab Bar

Primary in-app navigation with 3–5 destinations uses one full-width fixed Bottom Tab Bar.

Required:

- edge-attached to viewport bottom;
- fixed while work content scrolls;
- full-width on mobile;
- no external left/right/bottom floating-card gap;
- safe-area-aware;
- identical base geometry across specialized applications using same shell revision;
- icon + short label;
- active tab unambiguous;
- comfortable one-hand touch targets;
- no unreadable label shrinking to fit excess destinations.

More than five primary destinations move under secondary hierarchy (`Сервис`, `Диагностика`, `Ещё` or drill-down).

Final work-content item must scroll completely above Bottom Tab Bar. Bottom reserve is shell-owned and includes the effective bottom safe area. Bottom Tab Bar remains native scale.

## 9. Visual composition inside work viewport

Shell standard does not prescribe identical cards, but field experience establishes:

- first useful viewport prioritizes current operating state;
- normal measurements use neutral typography;
- green/amber/red are reserved for confirmed semantic health/warning/fault;
- `unknown`, `unavailable`, stale/source loss never appear healthy;
- decorative/context artwork is separate from live values/state layers;
- no invented runtime, watts, alarms or reserve estimates without validated source;
- native Home Assistant more-info/history is reused for factual entity detail where appropriate.

## 10. Local visual assets

Panel-critical artwork should ship locally with the owning integration.

Required pattern:

- no external CDN dependency for critical artwork;
- no Base64 image payload in production JS;
- optimized PNG/WebP/SVG assets under integration frontend assets;
- context/background art contains no live HA values or status text;
- live device/status/flow/value layers remain separate runtime HTML/SVG/UI;
- device/context-specific backgrounds may follow selected peer context;
- asset URLs use release/UI-version cache busting.

Stark SolarPower is the reference implementation: transparent UPS artwork + local room WebP backgrounds + separate dynamic power-flow/value layers.

## 11. Render performance

Integration-owned panels should avoid rebuilding entire Shadow DOM for unrelated Home Assistant entity churn.

Relevant-state fingerprints/selective updates are allowed, but must preserve:

- exactly one shell/work viewport;
- selected peer context;
- active Bottom Tab;
- zoom state;
- more-info/global-action bindings.

## 12. Production frontend delivery

Production frontend must be deterministic:

- one production entry module;
- historical/versioned sources are not runtime dependency chain;
- version-based cache busting;
- local packaged assets;
- CI checks JS syntax, registration/manifest parity and declared asset existence.

See `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`.

## 13. Responsive and field acceptance

Acceptance order:

1. iPhone Pro Max portrait in Home Assistant Companion App;
2. smaller iPhone portrait;
3. iPad/tablet;
4. desktop.

Field acceptance checks at minimum:

- safe area consumed exactly once;
- HA menu visible/reachable and emits `hass-toggle-menu`;
- centered title/right action geometry;
- persistent selector fit where applicable;
- first useful domain state enters expected viewport;
- Bottom Tab Bar clears values/Home Indicator;
- pinch/pan works;
- 97–103% snap works;
- two-finger double-tap reset and `Масштаб 100%` feedback work;
- shell does not duplicate after repeated HA updates;
- peer switching preserves context;
- `unknown`/stale/source-loss remain explicit;
- long press/native more-info works where specified.

## 14. Non-conforming patterns

Prohibited:

- Header under notch/Dynamic Island;
- double safe-area consumption;
- integration-specific drawer behind permanent HA menu icon;
- permanent Back in left Header rail;
- left menu control that does not use standard `hass-toggle-menu` behavior;
- domain-specific Header/Bottom Bar geometry;
- permanent zoom toolbar consuming mobile work area;
- nested/repeated zoom wrappers;
- duplicate gesture handlers after rerender;
- whole-page/browser zoom as panel zoom;
- zooming Header/selector/Bottom Bar with content;
- floating primary Bottom Tab card/pill;
- hard-coded iPhone safe-area constants;
- simultaneous shell migration plus unrelated domain redesign.

## 15. Acceptance criteria

A specialized panel shell is accepted only when:

1. safe area is consumed exactly once;
2. Header stays below notch/Dynamic Island;
3. left rail is always HA main-system menu and uses `hass-toggle-menu`;
4. title remains geometrically centered;
5. persistent peer selector, when present, is native-scale/fixed-order/selected-device-only;
6. exactly one work viewport exists;
7. repeated HA updates do not recreate/nest shell topology;
8. pinch affects only work content;
9. no permanent zoom toolbar is present;
10. 97–103% pinch end snaps to exactly 100%;
11. two-finger double tap resets zoom + scroll and shows brief `Масштаб 100%`;
12. Bottom Tab Bar is fixed/full-width/safe-area-aware/native-sized;
13. final content clears Bottom Tab Bar;
14. responsive layout is selected before zoom;
15. domain semantics/commands remain owned by integration;
16. actual target-device field acceptance passes.

## Project rule

> Specialized panels own domain content, not application chrome. The shared NikaS shell owns effective safe areas, the permanent `hass-toggle-menu` Home Assistant menu Header, peer-device context placement, exactly one idempotent zoomable work viewport and the full-width fixed Bottom Tab Bar. Only work content scales; gesture reset returns scale and scroll to 100%.