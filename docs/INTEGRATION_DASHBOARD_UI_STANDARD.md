# Integration-owned dashboard UI standard v1.3

**Status:** Required  
**Applies to:** all integration-owned specialized dashboards in Home Assistant NikaS  
**Primary target:** iPhone Pro Max, portrait  
**Related standards:** `SPECIALIZED_PANEL_SHELL_STANDARD.md`, `SPECIALIZED_PANEL_ZOOM_STANDARD.md`, `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`

## 1. Purpose

Integration-owned dashboards behave as mobile applications inside Home Assistant rather than unrelated Lovelace pages.

The integration keeps ownership of domain data, actions and presentation. The shared NikaS standards define application-shell behavior, visual semantics and release constraints without creating a runtime dependency on `ha-contract-generated-ui`.

Reference field evidence: `STARK_SOLARPOWER_PANEL_LESSONS.md`.

## 2. Application hierarchy

Single-device application:

```text
SAFE AREA
↓
HEADER: ☰ | centered title | global action
↓
ZOOMABLE DOMAIN WORK VIEWPORT
↓
BOTTOM TAB BAR
```

Multi-peer-device application:

```text
SAFE AREA
↓
HEADER: ☰ | centered title | global action
↓
PERSISTENT DEVICE SELECTOR
↓
ZOOMABLE SELECTED-DEVICE WORK VIEWPORT
↓
BOTTOM TAB BAR
```

The user should understand the current operating state within a few seconds of opening the application.

## 3. Header

Every primary view uses the shared shell Header.

```text
┌─────────────────────────────────────┐
│  ☰            Panel title         ⟳ │
│             optional subtitle       │
└─────────────────────────────────────┘
```

### 3.1 Left side — Home Assistant main-system menu

- icon/presentation corresponds to the normal Home Assistant menu control;
- always present in the permanent left rail;
- opens/toggles Home Assistant main navigation/sidebar/drawer;
- is not browser Back;
- is not a hard-coded parent route;
- is not an integration-specific drawer;
- never performs a device/domain action;
- touch target approximately 44×44 pt or larger.

Logical parent/drill-down navigation may exist elsewhere when the domain needs it, but does not replace this permanent system control.

### 3.2 Center — title

The title is **geometrically centered on the mobile viewport**, not merely centered in free space between controls.

Rules:

- one concise application title;
- one primary line on the reference iPhone;
- optional short subtitle for model/context/version;
- no second oversized duplicate title immediately below Header;
- UI/integration version remains secondary information.

Examples:

- `Stark SolarPower` / `UPS · UI v…`;
- `S8 OMNI`;
- `Полив` / `HO-SC-8W`;
- `Keenetic Hero 4G+`.

### 3.3 Decorative icon policy

A decorative brand/device icon is not placed next to the Header title. Brand artwork may appear in content, navigation metadata or contextual hero artwork.

### 3.4 Right side — one global action

At most one primary application-level action appears in the right rail, e.g. Refresh or overflow.

If the action is asynchronous:

- frontend calls an existing Home Assistant integration API/entity, not the vendor API directly;
- busy state blocks repeated activation;
- success/error feedback should be visible when practical;
- right-side feedback must not shift the centered title.

## 4. Safe-area ownership

Safe area is consumed exactly once at the application boundary.

Required:

- Header is below notch/Dynamic Island;
- Bottom Tab Bar clears Home Indicator;
- no duplicate blank top band from adding an inset Home Assistant already supplied;
- no per-view phone-model padding hacks;
- Home Assistant Companion App field capture is part of acceptance.

See `SPECIALIZED_PANEL_SHELL_STANDARD.md` for the normative geometry.

## 5. Primary in-app navigation — Bottom Tab Bar

When the application has 3–5 primary sections, they use one **full-width, edge-attached, fixed Bottom Tab Bar**.

Required:

- fixed to bottom viewport edge;
- full-width on mobile;
- not a floating card/pill;
- safe-area-aware;
- icon + short label;
- active item unambiguous;
- final domain content scrolls above the bar;
- comfortable one-hand touch targets;
- labels stay readable instead of being reduced excessively.

More than five destinations move under secondary hierarchy rather than shrinking the bar.

Current reference tab sets:

- **HO-SC-8W:** `Обзор · Зоны · Программы · Диагн.`
- **S8 OMNI:** `Обзор · Уборка · Станция · Сервис · Диагн.`
- **Stark SolarPower:** `Обзор · ИБП · История · События · Диагн.`
- **Keenetic Hero 4G+:** `Обзор · WAN/LTE · Трафик · Диагн.`; a separate Failover workflow may justify five tabs.

## 6. Multi-peer-device context — Device Selector

If one integration application serves multiple peer physical devices, Device Selector is a distinct persistent context layer.

It answers **which device?**. Bottom Tab Bar answers **which section?**. These must not be mixed.

Required:

- located immediately below Header on every primary section;
- remains at native scale;
- fixed device order;
- selected peer never moves to the first position because it was selected;
- selection shown only through active-state presentation;
- selected peer survives section changes;
- compact health dot/badge is allowed for non-selected peers;
- the selector is not a second telemetry panel;
- detailed primary content belongs only to selected peer;
- new peers should reuse the same template when device discovery permits it.

Subordinate channels are not automatically peer devices. Irrigation zones, S8 robot/station parts and Keenetic WAN channels remain subordinate parts of one application context unless there are multiple peer physical systems.

### 6.1 Stark SolarPower reference model

```text
HEADER
↓
[ UPS Интернет ] [ UPS Котёл ]
↓
SELECTED UPS CONTENT
↓
Обзор | ИБП | История | События | Диагн.
```

Reference behavior:

- fixed selector order;
- selected UPS context preserved across all five views;
- selected-device-only content;
- no second full UPS block appended below;
- optional per-peer zoom persistence.

## 7. First useful viewport

The first mobile viewport prioritizes operating state over chrome or secondary detail.

Preferred hierarchy:

1. current state / trust state;
2. primary visual or status summary;
3. most important live metrics/actions;
4. explicit essential subsystem state rows;
5. detail below.

Field review should verify that critical state is not pushed below fixed navigation simply because decorative content or selector/header geometry is oversized.

## 8. Visual-state semantics

### 8.1 Semantic color, neutral data

Normal factual measurements use neutral typography.

Reserve semantic colors for confirmed meaning:

- green — healthy/normal confirmed state;
- amber/orange — warning/degraded/attention;
- red — fault/critical;
- grey/neutral — unknown/unavailable/not confirmed.

A normal numeric value is not colored green merely because it is present.

### 8.2 Trust before last known operating mode

If the integration exposes source/trust/freshness state, source failure or stale state overrides a last reported normal operating value in the overview status.

`unknown`, `unavailable`, stale or untrusted source never mean healthy.

### 8.3 Backend owns validated thresholds

When the integration exposes a semantic entity such as `data_stale`, the frontend consumes that entity instead of duplicating the backend threshold constant.

Frontend explanatory text may show observed age/value, but must not silently reimplement backend business logic that can drift.

### 8.4 No invented runtime

Do not derive or display unsupported values only to make a panel appear complete.

Examples of prohibited invention without a validated source/algorithm:

- battery runtime minutes;
- watts from unrelated measurements;
- alarms not exposed by the integration;
- inferred health from unavailable source data.

Use `—`, `Неизвестно`, `Недоступно` or equivalent factual presentation.

## 9. Contextual visual assets

Integration-owned panels may use rich visual hero scenes when they improve state recognition.

Required asset model:

```text
frontend/
└── assets/
    ├── device.png        # transparent product/object layer when useful
    └── context.webp      # decorative/context plate
```

Rules:

- panel-critical images ship locally with the integration;
- no external CDN dependency;
- no Base64 image embedding in production JS;
- decorative/background art contains no live HA measurements/status text;
- device artwork, SVG paths, labels, values and state overlays remain separate runtime layers;
- contextual background may change with selected peer/device context;
- background contrast may use a lightweight overlay/gradient for readability;
- images are optimized before shipping.

Stark SolarPower is the reference pattern: transparent UPS artwork + separate network/boiler WebP plates + dynamic HTML/SVG power-flow layers.

## 10. Entity and action behavior

The shared UI rules must not weaken domain safety.

- no raw Tuya DP writes from Lovelace;
- no direct RCI/SNMP/vendor API bypasses;
- no fabricated entity IDs or unsupported commands;
- direct controls use stable public Home Assistant APIs/entities of the owning integration;
- Header, Device Selector and Bottom Tab Bar never execute unrelated domain actions;
- long press on factual entity-backed elements should open native Home Assistant more-info where useful;
- native Home Assistant history/more-info is preferred over duplicating a full history subsystem unless custom history adds material domain value.

## 11. Render performance and shell stability

Home Assistant may update hundreds of unrelated entities while a specialized panel is open.

A production panel should avoid complete Shadow DOM rebuilds when neither its relevant entities nor UI context changed.

Permitted mechanisms include relevant-state fingerprints or equivalent selective updates.

Optimization must preserve:

- exactly one shell/work viewport;
- selected peer;
- active Bottom Tab;
- current zoom state;
- entity interaction bindings;
- global action feedback.

A renderer optimization that causes nested wrappers or duplicated controls is a release-blocking defect.

## 12. Frontend delivery

Production delivery follows `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`.

Key principles:

- one deterministic production entry module;
- historical/versioned source modules are build-time history, not runtime dependency chain;
- UI-version cache busting;
- local packaged assets;
- panel metadata describes shell/device/zoom/delivery behavior;
- CI validates syntax, registration/manifest parity and reproducibility.

## 13. Mobile-first acceptance

Acceptance order:

1. iPhone Pro Max portrait in Home Assistant Companion App;
2. smaller iPhone portrait;
3. iPad/tablet;
4. desktop.

Required field checks:

- Header below Dynamic Island/notch with no duplicated safe-area band;
- HA main-system menu works from left rail;
- centered title remains centered with right action feedback;
- Device Selector fits and stays stable;
- first useful state content is visible at intended density;
- Bottom Tab Bar clears content/Home Indicator;
- pinch/pan behaves correctly;
- repeated HA updates do not duplicate shell/controls;
- peer switching preserves expected context;
- `unknown`/stale/source-loss scenarios are visible;
- long press/more-info works;
- global action feedback works.

A desktop render alone is not sufficient acceptance evidence for a mobile-first panel.

## 14. Navigation metadata

Conceptual single-device example:

```yaml
panel:
  id: irrigation
  title: Полив
  path: /dashboard-irrigation
  owner: ha-ho-sc-8w
  expose_in_generated_ui: true
  preferred_view: overview
  shell:
    version: "1.2"
    safe_area_owner: application_once
  header:
    left_control: home_assistant_menu
    title_alignment: viewport_center
    show_brand_icon: false
    right_action: refresh
  navigation:
    primary: full_width_fixed_bottom_tab_bar
    floating: false
  zoom:
    pinch: true
    controls: optional
    min: 0.75
    max: 2.0
```

Conceptual multi-peer-device addition:

```yaml
  device_context:
    selector: persistent_below_header
    preserve_across_views: true
    reorder_selected: false
    content_scope: selected_device_only
    zoom_persistence_scope: panel_and_device
```

## 15. Application-specific guidance

### Stark SolarPower

- HA system menu remains permanent left Header control;
- centered `Stark SolarPower`, optional short UI subtitle;
- one right global Refresh action with feedback;
- persistent fixed-order `UPS Интернет / UPS Котёл` selector;
- selected-UPS-only content across five views;
- contextual local network/boiler hero art with separate dynamic UPS/power-flow/value layers;
- semantic colors for state, neutral measurements;
- backend `data_stale` owns freshness threshold;
- gesture-only zoom is allowed if declared; exactly one work viewport;
- native more-info/history for factual entity detail.

### S8 OMNI

- HA system menu on left;
- composite robot + station state may be hero information;
- no Device Selector while the application represents one peer system;
- keep five primary sections in fixed Bottom Tab Bar.

### HO-SC-8W irrigation

- HA system menu on left;
- zones are subordinate channels, not peer-device selector entries;
- keep `Обзор · Зоны · Программы · Диагн.` in Bottom Tab Bar;
- domain write safety remains owned by integration APIs.

### Keenetic Hero 4G+

- HA system menu on left;
- first viewport prioritizes Internet / active WAN / Ethernet / LTE / failover state;
- Ethernet/LTE are channels of one router, not peer devices;
- detailed diagnostics stay below operational status.

## 16. Acceptance criteria

An integration-owned specialized dashboard is UI-complete only when:

- permanent HA system menu is present on the left;
- title is geometrically centered;
- safe area is consumed once;
- no decorative Header icon shifts title;
- async right action, if present, provides safe feedback;
- Bottom Tab Bar is fixed, full-width, edge-attached and safe-area-aware;
- persistent peer selector, if applicable, is native-scale, fixed-order and selected-device-only;
- exactly one zoom work viewport exists;
- repeated HA updates do not nest shell topology;
- factual data is neutral while semantic state uses semantic color;
- stale/source failure/unknown never become healthy;
- no unsupported derived values are invented;
- local visual assets remain separate from live state layers;
- long press/native more-info remains available where specified;
- production frontend passes deterministic delivery checks;
- actual target-device field acceptance passes.

## Project rule

> Integration-owned specialized dashboards are mobile applications inside Home Assistant: permanent Home Assistant system menu at top-left, centered title, optional persistent peer-device context, exactly one zoomable work viewport, fixed full-width Bottom Tab Bar, factual state-first content, local layered assets, strict trust semantics and deterministic frontend delivery.
