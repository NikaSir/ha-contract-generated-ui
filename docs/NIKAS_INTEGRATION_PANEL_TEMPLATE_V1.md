# NikaS Integration Panel Template v1.9

> **SUPERSEDED FOR SHELL GEOMETRY, HEADER NAVIGATION AND GESTURES:** use `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.9 and `NIKAS_PANEL_NAVIGATION_CONTRACT.md`. Domain composition guidance remains valid only when compatible with those documents.

**Status:** Required reference implementation
**Primary target:** iPhone Pro Max, portrait
**Applies to:** all integration-owned specialized panels in Home Assistant NikaS

This document turns the existing UI and frontend-release standards into one reusable implementation template. Domain developers customize content, not the application shell.

Normative sources:

- `INTEGRATION_DASHBOARD_UI_STANDARD.md` — navigation, device context, mobile behavior and semantics;
- `SPECIALIZED_PANEL_FRONTEND_RELEASE_STANDARD.md` — production frontend delivery;
- this document — shared geometry, visual primitives and reference implementation contract.

## 1. Fixed application hierarchy

Every specialized panel uses this order:

```text
AppHeader
↓
DeviceContextSelector (optional, peer devices only)
↓
One scroll/zoom viewport with HeroStatus + ViewContent
↓
BottomTabBar
```

The hierarchy must not change between integrations.

- Header menu answers **how do I open Home Assistant navigation?**
- Device Selector answers **which physical device?**
- Bottom Tab Bar answers **which section of this application?**

## 2. Header contract

Mobile grid:

```text
52px | minmax(0, 1fr) | 52px
```

Narrow fallback:

```text
48px | minmax(0, 1fr) | 48px
```

Rules:

- left control is only `mdi:menu`; it dispatches bubbling/composed `hass-toggle-menu`;
- menu and Refresh use matching 44×44 px, radius 16 px plaques with 25 px `ha-icon` glyphs;
- title is geometrically centered on the viewport;
- first line is the human application name;
- second line contains only `UI vX.Y.Z`; type, model and context text are prohibited there;
- the whole title is the sole standard return button and copies the exact LIDER plaque geometry, surface, pressed and focus-visible states from the v1.9 standard;
- first/second lines are `23/14px`; narrow fallback is `21/13px`;
- decorative brand/device icon is not placed next to the title;
- right zone contains at most one primary global action, normally Refresh, plus overflow only when genuinely needed.

## 3. Parent-section routes inside the work area

| Application | Parent |
| --- | --- |
| ZONT | `/dashboard-house-v11/home` |
| StarLine | `/dashboard-house-v11/home` |
| HO-SC-8W irrigation | `/dashboard-actions/home` |
| S8 OMNI | `/dashboard-actions/home` |
| Keenetic Hero 4G+ | `/dashboard-infrastructure/overview` |
| Stark SolarPower UPS | `/dashboard-infrastructure/overview` |
| LIDER | `/dashboard-infrastructure/overview` |

Future applications may declare a parent route in machine-readable metadata, but its navigation control belongs inside the work area. The permanent Header rail never becomes Back.

## 4. Device Selector

Use only when one application owns several peer physical devices of the same type.

Reference form:

```text
[ ● UPS Интернет ] [ ● UPS Котёл ]
```

Rules:

- immediately below Header on every primary view;
- fixed device order;
- selection changes only active presentation and content;
- selected device is never moved to first position;
- selection persists while switching Bottom Tab Bar sections;
- status dot semantics: green healthy, amber warning, red fault, grey unreliable/unknown;
- all full content below belongs to the selected device only.

## 5. HeroStatus

The first content card answers:

> What is happening now, and is the system healthy?

HeroStatus contains:

1. one large factual status;
2. one concise explanation;
3. optionally one compact badge;
4. only the minimum domain telemetry needed to understand current state.

Do not turn the Hero into a technical sensor registry.

## 6. Shared color semantics

| Meaning | Presentation |
| --- | --- |
| healthy / available / working | green |
| selection / information / active context | Home Assistant primary color |
| warning | amber/orange |
| fault / unavailable source | red |
| unknown / unreliable data | grey |

Color must communicate state, not decorate different subsystems.

## 7. Shared visual primitives

### Card

- radius: 20–24 px;
- padding: 16–20 px;
- gap between cards: 12–16 px;
- 1 px divider/border;
- minimal or no shadow.

### MetricCard

```text
Label
Value unit
```

Label is secondary text. Value is primary, semibold/bold. Unit is always present when the HA entity provides one.

### StateRow

```text
Icon   Label                         Value
```

### ActionCard

```text
Icon   Action
       concise explanation
```

### AlertCard

```text
! Problem
  concise explanation
```

### Diagram

Allowed only when topology/flow materially improves understanding.

## 8. Typography baseline

Primary mobile screen must remain readable at arm/hand distance.

Meaningful user-facing typography stays within `12–25px`. Header is the explicit `23/14px` pair (`21/13px` narrow); the optional connection/freshness indicator uses `16/13px`; Bottom Tab Bar labels use `12px/700`. Only redundant non-interactive schematic annotations may use `9–10px`. If meaningful copy does not fit at 12px, recompose the layout instead of shrinking it.

## 9. Bottom Tab Bar

Primary navigation is always:

- fixed;
- edge-attached;
- full-width on the mobile viewport;
- safe-area aware;
- outside the content scroll region;
- 3–5 primary destinations;
- icon + short label;
- `ha-icon` MDI glyph at 28 px and label at 12 px/700;
- active state highlighted inside its shared cell.

Floating/pill navigation with side or bottom gaps is non-conforming.

## 10. Loading contract

Loading must preserve the application shell:

```text
Header
↓
Device Selector placeholder if applicable
↓
Skeleton / Loading state
↓
Bottom Tab Bar
```

A blank white application while waiting for bootstrap/telemetry is non-conforming.

The shell is mounted once. Telemetry, clock and freshness updates point-patch existing text/classes/attributes and never replace Header, selector, viewport, canvas, background or Bottom Tab Bar. Tabs and peer-device views use lazy DOM caching so switching them cannot create a full-screen flash.

## 11. unavailable / unknown

`unknown` and `unavailable` are never rendered as normal/green/zero by default.

Use explicit semantics such as:

- `Нет данных`;
- `Состояние неизвестно`;
- `Нет достоверной телеметрии`.

A domain may distinguish source-down from stale data, but neither is healthy.

## 12. Long press

Factual entity-backed content should preserve:

```text
hold → native Home Assistant more-info
```

Header, Device Selector and Bottom Tab Bar are navigation chrome and never execute entity-specific commands on hold/double tap.

## 13. Production frontend rule

The copied reference implementation is a development source pattern, not a shared runtime library.

Every integration produces its own autonomous production artifact:

```text
<integration-panel-bundle.js>?v=<ui-version>
```

No specialized panel may import this repository or another integration at runtime. Historical versions and shared source helpers may participate only at build time.

## 14. Reference implementation

The code template lives under:

```text
templates/integration-panel-v1/
```

It provides:

- `panel-shell-reference.js` — stable shell/reference component designed to be concatenated with the copied v1.9 zoom controller into one autonomous bundle;
- `zoom-controller-reference.js` — the copy/adapt v1.9 gesture controller; concatenate it into the integration-owned production bundle;
- `panel-contract.example.json` — machine-readable metadata example;
- `README.md` — adoption checklist.

The reference intentionally contains no integration API calls and no device commands. A developer copies/adapts it into the integration repository, replaces placeholders and domain ViewContent, then ships an autonomous production bundle.

## 15. What each integration is allowed to customize

Only these application-specific choices belong to the integration:

1. title and numeric UI version; the rendered second line remains exactly `UI vX.Y.Z`;
2. optional parent route shown only through an in-work navigation control;
3. optional peer-device selector;
4. HeroStatus content;
5. primary tab set (3–5);
6. domain ViewContent;
7. validated actions exposed through the integration API/entities;
8. domain-specific diagrams.

The integration should not redesign Header geometry, navigation mechanics, state-color semantics, basic card language, mobile safe-area behavior or production loading architecture.

## 16. Acceptance

A specialized panel is template-conforming when, on iPhone Pro Max portrait:

- Header geometry matches the common shell;
- `mdi:menu` opens the native Home Assistant menu and both Header actions use matching plaques;
- optional Device Selector remains stable across primary sections;
- first visible content is current domain status rather than another navigation row;
- Bottom Tab Bar is fixed, edge-attached and safe-area aware;
- last content scrolls fully above the Tab Bar;
- native vertical scroll at 100%, focal 75–200% pinch, bounded enlarged pan, 97–103% snap and stationary two-finger reset work;
- no horizontal scrolling occurs;
- no important label is clipped into ambiguity;
- unknown/unavailable is visibly non-normal;
- factual entity long press opens native more-info where supported;
- cold-cache loading shows shell rather than a blank page;
- telemetry, scroll and tab/device switches produce no whole-panel flash or DOM duplication;
- production frontend is one self-contained bundle.

The intended result is one NikaS application ecosystem with different domain content, not a collection of unrelated frontend designs.
