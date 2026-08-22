# NikaS Integration Panel Template v1.0 — reference implementation

This directory is the **canonical copy/adapt reference** for integration-owned specialized panels in Home Assistant NikaS.

It is **not** a shared runtime dependency. Every integration copies/adapts the source into its own repository and ships one autonomous production frontend bundle.

Applies to Stark SolarPower, HO-SC-8W, S8 OMNI, Keenetic Hero 4G+, VLESS Gateway and future specialized panels.

## Canonical shell

Every panel keeps this order:

```text
Header
Optional Device Context Selector
Hero Status
Current View Content
Bottom Tab Bar
```

Developers change domain content, tabs and optional device context. Header geometry, card rhythm, state tones, safe-area behavior, loading shell and Bottom Tab Bar mechanics are common infrastructure.

## Header contract

Mobile header grid:

```text
52 px | minmax(0,1fr) | 52 px
```

Narrow mobile may use:

```text
48 px | minmax(0,1fr) | 48 px
```

Rules:

- left control is icon-only `mdi:arrow-left`;
- no `Назад` text in Header;
- Back uses explicit `navigate` to the declared parent route, never browser history;
- center contains human title plus `<type/model> · UI vX.Y.Z`;
- right side contains at most one global action, preferably Refresh;
- left/right touch targets are >=44 × 44 px;
- equal side rails keep the title geometrically centered.

## Bottom Tab Bar contract

- 3–5 primary tabs only;
- full-width, edge-attached, safe-area aware;
- outside the vertical scroll region;
- never a floating pill;
- dynamic equal-width columns from actual tab count;
- active cell uses primary icon/text plus light primary surface;
- short labels; `Диагн.` is allowed only when `Диагностика` does not physically fit.

## Mobile / desktop contract

Primary target: **iPhone Pro Max portrait**.

- mobile primary content is one column;
- no horizontal scrolling;
- primary content uses 100% available width with system side padding;
- card radius 20–24 px, target 22 px;
- card padding 16–20 px, target 18 px in the reference;
- vertical gap 12–16 px, target 14 px;
- desktop is an adaptation of the same hierarchy, capped at 1280 px;
- desktop is not a separate design.

## Shared primitives

`panel-shell-reference.js` includes reference implementations for:

- `PanelShell`;
- `AppHeader`;
- optional Device Context Selector;
- Hero Status;
- Metric Card;
- State Row;
- Action Card;
- Alert;
- Diagram placeholder;
- Loading skeleton;
- dynamic 3–5 item Bottom Tab Bar;
- long-press -> native Home Assistant more-info for entity-backed elements.

## Adoption sequence

1. Copy `panel-shell-reference.js` into the integration frontend source tree.
2. Rename the custom element and constants for the integration.
3. Set title, subtitle, UI version and canonical `parentPath`.
4. Define 3–5 primary tabs.
5. Enable Device Selector only for multiple peer physical devices.
6. Replace `_renderHeroStatus()` and `_renderViewContent()` with domain content.
7. Preserve Header, safe-area geometry, common primitives and Bottom Tab Bar semantics.
8. Bind factual entity-backed blocks to native HA more-info on hold where practical.
9. Add only verified integration actions; never bypass the integration API from the frontend.
10. Build one autonomous production JS bundle and register it through `module_url` with query-string UI-version cache busting.
11. CI must reject runtime imports of previous frontend versions and validate JavaScript syntax.
12. Validate iPhone Pro Max portrait, cold cache, full HA restart and Home Assistant Cloud/Nabu Casa before acceptance.

## Multi-device rule

Use Device Context Selector only for peer physical devices owned by one panel, for example two UPS units.

```text
Header
Device Selector
Hero / selected-device content
Bottom Tab Bar
```

Device order is fixed. Selection persists across views. The selected device never moves to the first slot.

Ethernet/LTE, modes, zones or workflow steps are domain context, not automatically Device Selector items.

## Production frontend rule

```text
Specialized Panel = self-contained production frontend bundle
```

Do not create runtime chains such as `v033 -> v032 -> v031 -> base`. Historical versions belong in Git, not in the browser loading path.

## Non-goals

The reference does not provide:

- direct device API calls;
- raw Tuya/RCI/SNMP writes;
- fake Home Assistant entities;
- shared CDN/runtime module dependencies;
- domain-specific business logic.
