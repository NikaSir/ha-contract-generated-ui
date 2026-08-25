# Specialized Panel Shell Standard v1.2

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Primary acceptance viewport:** iPhone Pro Max, portrait  
**Architecture:** `CONTRACT_GENERATED_UI` / integration-owned compatible shell

## 1. Purpose

All specialized panels must use one application-shell contract so they behave like parts of the same Home Assistant system without forcing their domain UI into one repository.

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
ZOOM CONTROLS (when enabled)                  native scale
↓
EXACTLY ONE ZOOMABLE WORK VIEWPORT             user scale
  └── selected-device / domain content
↓
BOTTOM TAB BAR                                native scale
↓
DEVICE BOTTOM SAFE AREA / HOME INDICATOR
```

The reference evidence behind v1.2 is recorded in `STARK_SOLARPOWER_PANEL_LESSONS.md`.

## 2. Ownership invariant

A specialized domain module MUST NOT independently define incompatible versions of:

- safe-area ownership;
- Header geometry;
- Home Assistant main-menu button geometry/meaning;
- title centering;
- zoom viewport topology;
- pinch behavior;
- optional zoom-control geometry;
- persistent peer-device selector placement;
- primary Bottom Tab Bar geometry;
- fixed shell clearances.

The domain implementation owns:

- domain status and telemetry;
- domain commands exposed through approved Home Assistant APIs/entities;
- content cards and visualizations;
- secondary drill-down content;
- peer-device data and labels;
- domain-specific context artwork.

**Migration rule:** shell migration must not be combined with an unrelated domain-UI refactor.

## 3. Safe-area contract — consume once

Safe areas have exactly one effective owner at each boundary.

The shell must use Home Assistant/browser safe-area values rather than phone-model constants:

```css
env(safe-area-inset-top, 0px)
env(safe-area-inset-right, 0px)
env(safe-area-inset-bottom, 0px)
env(safe-area-inset-left, 0px)
```

If Home Assistant or `panel_custom` already exposes/consumes the effective safe-area inset, the specialized shell must not blindly add the same inset again.

Required:

- no Header content under a notch/Dynamic Island;
- no bottom navigation under the Home Indicator;
- no duplicate blank band caused by double top-safe-area consumption;
- no device-specific fixes such as `top: 47px`;
- no independent safe-area padding in individual views/cards.

A release must be field-checked in the Home Assistant Companion App, not inferred from desktop browser geometry only.

## 4. Top Header

### 4.1 Canonical geometry

```text
┌─────────────────────────────────────┐
│  ☰           PANEL TITLE          ⟳ │
│              subtitle               │
└─────────────────────────────────────┘
```

Required:

- left rail is always the **Home Assistant main-system menu**;
- left rail is never permanent Back;
- title is geometrically centered relative to the viewport;
- right rail contains at most one primary shell/global action;
- left/right rails use matching geometry whenever practical;
- touch targets are approximately 44×44 pt or larger;
- primary title is concise and remains one line on the reference iPhone;
- optional subtitle carries model/context/version;
- decorative integration/device artwork is not placed beside the Header title;
- the title is not duplicated as another oversized heading below.

### 4.2 Main-system menu behavior

The left control opens/toggles the standard Home Assistant main navigation/sidebar/drawer appropriate to the client.

It MUST NOT open:

- an integration-specific drawer;
- browser Back;
- a hard-coded parent route;
- a device/domain action.

Parent or drill-down navigation may be available elsewhere when needed, but it does not replace the permanent Home Assistant menu rail.

### 4.3 Right action

A global action such as Refresh may occupy the right rail when appropriate.

For async actions:

- call only a stable Home Assistant API/entity belonging to the integration;
- do not call the vendor API directly from frontend code;
- show busy/success/error feedback when practical;
- suppress repeated activation while the action is busy.

The Header remains at native scale.

## 5. Persistent peer-device selector

When one application owns multiple peer physical devices, Device Selector is a first-class application-context layer.

Required placement:

```text
HEADER
↓
DEVICE SELECTOR
↓
WORK VIEWPORT
```

Required behavior:

- remains directly below Header on every primary section;
- remains at **native scale**;
- fixed device order;
- selection never reorders devices;
- selected peer survives Bottom Tab changes;
- compact health dot/badge for non-selected peers is allowed;
- detailed domain content belongs only to the selected peer;
- do not append full cards for all peers below a selector that claims selected-device context;
- a newly discovered peer should reuse the same template where the integration model permits it.

Subordinate channels of one device are not peer devices merely because they are selectable.

## 6. Zoomable work viewport

There is **exactly one** zoomable work viewport per specialized-panel instance.

Native-scale layers outside it:

- Home Assistant chrome;
- Header and HA menu button;
- persistent Device Selector;
- zoom controls when enabled;
- Bottom Tab Bar;
- safe-area surfaces.

Responsive composition is resolved before zoom:

```text
actual viewport
→ mobile/tablet/desktop composition
→ peer-device/domain context
→ user zoom
```

User zoom must not trigger artificial breakpoint changes.

### 6.1 Idempotent lifecycle

Shell installation/reconciliation MUST be idempotent.

Home Assistant may deliver frequent unrelated state updates, partial DOM updates or optimized renders. The shell must never create:

- nested zoom viewports;
- duplicated zoom controls;
- progressive content shrinkage;
- blank space from abandoned wrappers;
- duplicate Header/selector/navigation layers.

Preferred architecture keeps shell topology stable and updates only domain content. A migration shim may normalize old wrappers, but production design should not depend on repeated blind DOM post-processing.

## 7. Zoom controls

Pinch behavior is normative in `SPECIALIZED_PANEL_ZOOM_STANDARD.md`.

On-screen zoom controls are a **shell presentation policy** rather than a mandatory domain feature.

When enabled, canonical controls are:

```text
−   100%   +
```

Rules:

- exactly one control group;
- native scale;
- never inside the zoomable domain viewport;
- does not overlap Header, selector or Bottom Tab Bar;
- percentage shows effective scale and resets to 100% on tap;
- control presence/absence is declared in panel metadata rather than improvised by a domain view.

Gesture-only mobile presentation is conforming when pinch/pan/persistence satisfy the Zoom Standard and the panel declares controls disabled.

## 8. Bottom Tab Bar

Primary in-app navigation with 3–5 destinations uses one full-width fixed Bottom Tab Bar.

Required:

- edge-attached to viewport bottom;
- fixed while work content scrolls;
- full-width on mobile;
- no external left/right/bottom floating-card gap;
- safe-area-aware;
- identical base geometry across specialized applications using the same shell revision;
- icon + short label;
- active tab is unambiguous;
- touch target remains comfortable for one-handed use;
- labels must not be shrunk into illegibility to fit excess destinations.

If more than five primary destinations are needed, reduce hierarchy via `Сервис`, `Диагностика`, `Ещё` or drill-down.

The final work-content item must scroll completely above the Bottom Tab Bar.

Bottom reserve is owned by the shell:

```text
bottom tab bar content height
+ effective bottom safe area
```

Bottom Tab Bar remains at native scale.

## 9. Visual composition inside the work viewport

Shell standard does not prescribe identical cards, but Stark field experience establishes several cross-panel rules:

- the first useful viewport prioritizes current operating state over navigation chrome;
- normal measurements use neutral typography;
- green/amber/red are reserved for confirmed semantic health/warning/fault meaning;
- `unknown`, `unavailable`, stale/source loss never appear healthy;
- decorative/context artwork is separate from live values and state layers;
- do not invent runtime, watts, alarms or reserve estimates when no validated source exists;
- native Home Assistant more-info/history should be reused for factual entity detail when appropriate.

## 10. Render performance

Integration-owned panels should avoid rebuilding the entire Shadow DOM for unrelated Home Assistant entity churn.

Permitted optimizations include a render fingerprint or equivalent relevant-state filter.

Any optimization must preserve:

- exactly one shell;
- exactly one work viewport;
- selected peer context;
- Bottom Tab active state;
- zoom state;
- more-info and global-action bindings.

## 11. Responsive and field acceptance

Acceptance order:

1. iPhone Pro Max portrait in Home Assistant Companion App;
2. smaller iPhone portrait;
3. iPad/tablet;
4. desktop.

Mobile portrait is the source hierarchy. Tablet/desktop are adaptations.

Field acceptance must check at minimum:

- no duplicate or missing safe-area space;
- HA menu is visible and reachable;
- centered title and right action geometry;
- persistent selector fit where applicable;
- first useful domain state enters the expected viewport;
- Bottom Tab Bar does not cover values;
- pinch/pan works;
- shell does not duplicate after repeated HA state updates;
- peer-device switching preserves context;
- `unknown` / stale / source-loss states remain explicit;
- long press / native more-info works where specified.

## 12. Non-conforming patterns

Prohibited:

- Header under notch/Dynamic Island;
- double safe-area consumption;
- integration-specific drawer behind the permanent HA menu icon;
- permanent Back in the left Header rail;
- domain-specific Header/Bottom Bar geometry;
- nested zoom wrappers;
- duplicated zoom controls after rerender;
- whole-page/browser zoom as panel zoom;
- zooming Header/selector/Bottom Bar with content;
- floating primary Bottom Tab card/pill;
- hard-coded iPhone-model safe-area constants;
- simultaneous shell migration plus unrelated domain redesign.

## 13. Acceptance criteria

A specialized panel shell is accepted only when:

1. safe area is consumed exactly once;
2. Header stays below notch/Dynamic Island;
3. left rail is always Home Assistant main-system menu;
4. title remains geometrically centered;
5. persistent peer selector, when present, is native-scale, fixed-order and selected-device-only;
6. exactly one work viewport exists;
7. repeated HA updates do not nest/recreate shell topology incorrectly;
8. pinch zoom affects only work content;
9. on-screen zoom controls, when enabled, exist exactly once and remain native-sized;
10. Bottom Tab Bar is fixed, full-width, safe-area-aware and native-sized;
11. final content clears Bottom Tab Bar;
12. responsive layout is selected before zoom;
13. unrelated HA updates do not require full UI rebuild;
14. domain semantics/commands remain owned by the integration;
15. actual target-device field acceptance passes.

## 14. Project rule

> Specialized panels own domain content, not application chrome. The shared NikaS shell contract owns effective safe areas, the permanent Home Assistant menu Header, peer-device context placement, exactly one zoomable work viewport, optional native zoom controls and the full-width fixed Bottom Tab Bar. Shell installation is idempotent; only the work content scales.
