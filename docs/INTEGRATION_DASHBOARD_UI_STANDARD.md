# Integration-owned dashboard UI standard v1.4

**Status:** Required  
**Applies to:** all integration-owned specialized dashboards in Home Assistant NikaS  
**Primary target:** iPhone Pro Max, portrait  
**Related standards:** `SPECIALIZED_PANEL_SHELL_STANDARD.md`, `SPECIALIZED_PANEL_ZOOM_STANDARD.md`, `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`

## 1. Purpose

Integration-owned dashboards behave as mobile applications inside Home Assistant rather than unrelated Lovelace pages.

The integration keeps ownership of domain data, actions and presentation. Shared NikaS standards define application-shell behavior, visual semantics and release constraints without creating a runtime dependency on `ha-contract-generated-ui`.

Stark SolarPower mobile field experience is the reference implementation input.

## 2. Application hierarchy

Single-device application:

```text
SAFE AREA
↓
HEADER: ☰ | centered title | global action
↓
EXACTLY ONE ZOOMABLE DOMAIN WORK VIEWPORT
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
EXACTLY ONE ZOOMABLE SELECTED-DEVICE WORK VIEWPORT
↓
BOTTOM TAB BAR
```

Header, Device Selector and Bottom Tab Bar remain at native scale.

## 3. Header

Every primary view uses the shared shell Header.

### 3.1 Left side — Home Assistant main-system menu

The permanent left control:

- is always the Home Assistant system menu `☰`;
- dispatches the standard `hass-toggle-menu` event;
- remains below notch/Dynamic Island;
- is not browser Back;
- is not a hard-coded parent route;
- is not an integration-specific drawer;
- never performs a device/domain action;
- remains native scale.

Logical parent/drill-down navigation, when needed, belongs inside the work area and never replaces this system control.

### 3.2 Center — title

- geometrically centered on viewport;
- one concise application title;
- optional short subtitle for model/context/version;
- no duplicated oversized title below Header;
- no decorative brand/device icon shifting Header title.

### 3.3 Right side — one global action

At most one primary application-level action appears in right rail, e.g. Refresh/overflow.

Async action rules:

- call existing Home Assistant integration API/entity, not vendor API directly;
- block repeated activation while busy;
- provide success/error feedback when practical;
- feedback must not shift centered title.

## 4. Safe-area ownership

Safe area is consumed exactly once at application boundary.

Required:

- Header below notch/Dynamic Island;
- Bottom Tab Bar above Home Indicator;
- no duplicate blank top band;
- no phone-model padding hacks;
- Companion App field capture is part of acceptance.

## 5. Primary navigation — Bottom Tab Bar

Applications with 3–5 primary sections use one full-width edge-attached fixed Bottom Tab Bar.

Required:

- fixed to bottom viewport edge;
- full-width on mobile;
- not a floating card/pill;
- safe-area-aware;
- icon + short label;
- active item unambiguous;
- final work content scrolls above bar;
- comfortable one-hand targets;
- more than five destinations move under secondary hierarchy.

Bottom Tab Bar remains native scale.

## 6. Multi-peer-device context — Device Selector

If one application serves multiple peer physical devices, Device Selector is a persistent context layer.

It answers **which device?**. Bottom Tab Bar answers **which section?**.

Required:

- directly below Header on every primary section;
- native scale and outside zoom viewport;
- fixed device order;
- selected peer never reorders;
- selection preserved across Bottom Tabs;
- compact health badge allowed for non-selected peers;
- detailed content belongs only to selected peer;
- new peers reuse same template when device discovery permits.

Subordinate channels are not automatically peer devices.

## 7. Zoom interaction — Stark field baseline

The mobile standard is gesture-first.

Required:

- exactly one zoomable work viewport;
- two-finger focal-point pinch;
- pan/scroll enlarged content;
- no permanent `− / % / +` toolbar;
- pinch ending at **97–103%** snaps to exactly **100%**;
- two-finger double tap resets scale and work-area scroll to **100%**;
- reset briefly shows `Масштаб 100%`;
- scale persists locally per panel/client and preferably per peer device where applicable;
- repeated HA renders never nest/re-wrap zoom viewport.

See `SPECIALIZED_PANEL_ZOOM_STANDARD.md` for normative gesture/lifecycle behavior.

## 8. First useful viewport

First mobile viewport prioritizes operating state over chrome or secondary detail:

1. current state / trust state;
2. primary visual/status summary;
3. important live metrics/actions;
4. essential subsystem state rows;
5. detail below.

Critical state must not be pushed below fixed navigation by oversized decorative content.

## 9. Visual-state semantics

- normal factual measurements use neutral typography;
- green = confirmed healthy/normal;
- amber/orange = warning/degraded/attention;
- red = fault/critical;
- grey/neutral = unknown/unavailable/not confirmed;
- stale/source failure overrides last-known normal state;
- frontend consumes validated backend semantic entities/thresholds instead of duplicating business logic;
- unsupported runtime/watts/alarms/health are not invented.

## 10. Contextual visual assets

Rich hero scenes are allowed when they improve state recognition.

Required:

- panel-critical images ship locally with integration;
- no external CDN dependency;
- no Base64 images in production JS;
- background art contains no live HA values/status text;
- device artwork, SVG paths, labels, values and state overlays remain separate runtime layers;
- context background may change with selected peer;
- images optimized before shipping;
- asset URL uses version/cache busting.

Stark SolarPower reference: transparent UPS PNG + separate local WebP room backgrounds + dynamic HTML/SVG power-flow/value layers.

## 11. Entity/action behavior

- no raw Tuya DP writes from UI;
- no direct RCI/SNMP/vendor API bypasses;
- no fabricated entity IDs/unsupported commands;
- controls use stable public Home Assistant APIs/entities of owning integration;
- Header/Device Selector/Bottom Tab Bar never execute unrelated domain actions;
- factual entity-backed elements should reuse native more-info/history where useful.

## 12. Render performance and shell stability

Avoid complete Shadow DOM rebuilds for unrelated Home Assistant entity churn.

Relevant-state fingerprints/selective updates are allowed, but must preserve:

- exactly one shell/work viewport;
- selected peer;
- active Bottom Tab;
- current zoom state;
- interaction bindings;
- global action feedback.

Nested wrappers, duplicated handlers or progressive shrinkage are release-blocking defects.

## 13. Frontend delivery

Production delivery follows `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`:

- one deterministic production entry module;
- historical/versioned sources are not runtime dependency chain;
- UI-version cache busting;
- local packaged assets;
- CI validates syntax, registration/manifest parity and reproducibility.

## 14. Mobile-first acceptance

Acceptance order:

1. iPhone Pro Max portrait in Home Assistant Companion App;
2. smaller iPhone portrait;
3. iPad/tablet;
4. desktop.

Required field checks:

- Header below Dynamic Island/notch without duplicate safe-area band;
- left `☰` triggers `hass-toggle-menu`;
- centered title remains centered;
- Device Selector fits/stays stable where applicable;
- first useful state appears at intended density;
- Bottom Tab Bar clears content/Home Indicator;
- pinch/pan works;
- 97–103% snap works;
- two-finger double-tap reset and `Масштаб 100%` feedback work;
- repeated HA updates do not duplicate shell/viewport;
- peer switching preserves context;
- `unknown`/stale/source-loss scenarios remain explicit;
- long press/more-info and global action feedback work where specified.

Desktop render alone is insufficient acceptance evidence.

## 15. Conceptual metadata

```yaml
panel:
  shell:
    version: "1.3"
    safe_area_owner: application_once
  header:
    left_control: home_assistant_menu
    left_event: hass-toggle-menu
    title_alignment: viewport_center
  navigation:
    primary: full_width_fixed_bottom_tab_bar
    floating: false
  zoom:
    viewport_count: 1
    pinch: true
    persistent_controls: false
    snap_to_100_range: [0.97, 1.03]
    reset_gesture: two_finger_double_tap
    reset_scroll: true
    reset_feedback: "Масштаб 100%"
    min: 0.75
    max: 2.0
```

For multi-peer-device panels:

```yaml
  device_context:
    selector: persistent_below_header
    preserve_across_views: true
    reorder_selected: false
    content_scope: selected_device_only
    zoom_persistence_scope: panel_and_device
```

## 16. Project rule

> Integration-owned specialized dashboards are mobile applications inside Home Assistant: permanent `hass-toggle-menu` system menu at top-left, centered title, optional native-scale peer-device selector, exactly one idempotent gesture-zoom work viewport, fixed full-width Bottom Tab Bar, factual state-first content, local layered assets, strict trust semantics and deterministic frontend delivery.