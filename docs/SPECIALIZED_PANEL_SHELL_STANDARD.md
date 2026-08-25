# Specialized Panel Shell Standard v1.1

**Status:** Required  
**Applies to:** all specialized Home Assistant panels in Home Assistant NikaS  
**Primary acceptance viewport:** iPhone Pro Max, portrait  
**Architecture:** `CONTRACT_GENERATED_UI`

## 1. Purpose

All specialized panels must use one shared application shell so they behave like parts of the same Home Assistant application.

The shell owns viewport geometry, safe areas, top navigation, zoom controls and bottom in-app navigation. A domain/integration module owns only the content rendered inside the shell work area.

Canonical hierarchy:

```text
HOME ASSISTANT / DEVICE SAFE AREA
↓
SPECIALIZED PANEL HEADER                 native scale
↓
ZOOM CONTROLS                            native scale
↓
ZOOMABLE WORK VIEWPORT                   user scale
  └── domain / integration content
↓
BOTTOM TAB BAR                           native scale
↓
DEVICE BOTTOM SAFE AREA / HOME INDICATOR
```

## 2. Ownership invariant

A specialized domain module MUST NOT independently implement:

- top safe-area offsets;
- Header height or geometry;
- Home Assistant main-menu button geometry;
- title centering rules;
- zoom controls;
- pinch-to-zoom;
- bottom safe-area offsets;
- primary Bottom Tab Bar geometry;
- fixed navigation clearances;
- device-model-specific `top`, `bottom`, `padding-top` or `padding-bottom` constants.

These belong to the shared shell.

The domain module owns only:

- domain status and telemetry;
- domain commands exposed through approved integration APIs;
- content cards, visualizations and secondary drill-down content;
- optional persistent Device Selector when the application represents multiple peer physical devices.

## 3. Safe-area contract

The shell MUST use browser/Home Assistant safe-area environment values rather than hard-coded dimensions for a specific iPhone model.

Required values:

```css
env(safe-area-inset-top, 0px)
env(safe-area-inset-right, 0px)
env(safe-area-inset-bottom, 0px)
env(safe-area-inset-left, 0px)
```

The panel must remain valid on devices with Dynamic Island, display notch, rounded display corners, iOS Home Indicator, no cutout/safe-area requirement, tablet and desktop viewports.

Hard-coded fixes such as `top: 47px` for one phone are non-conforming.

## 4. Top Header

### 4.1 Position

The Header is the first shell-owned visual surface and MUST remain below the effective top safe area.

Conceptually:

```css
padding-top: max(var(--nika-shell-top-padding), env(safe-area-inset-top, 0px));
```

No Header control or title may render underneath the notch or Dynamic Island.

### 4.2 Geometry

Canonical mobile Header:

```text
┌─────────────────────────────────────┐
│  ☰           PANEL TITLE          ⟳ │
│              subtitle               │
└─────────────────────────────────────┘
```

Required:

- **the left rail is always the Home Assistant main-system menu button**;
- the left rail MUST NOT be a panel-specific Back button;
- the menu button must open/toggle the standard Home Assistant main navigation/sidebar/drawer appropriate to the client;
- the title is geometrically centered relative to the viewport;
- at most one primary shell-level action is placed on the right;
- left/right rail geometry should match whenever practical;
- minimum touch target is approximately 44×44 pt;
- primary title stays concise and one-line on the reference iPhone viewport;
- an optional secondary line may show model/context/version;
- no decorative integration/device icon is placed next to the Header title;
- no duplicated oversized title appears immediately below the Header.

### 4.3 Main-system menu behavior

The left Header control belongs to the Home Assistant application shell. It always exposes the main-system navigation rather than performing domain navigation.

A specialized panel MUST NOT replace this control with:

- browser Back;
- a hard-coded parent route;
- an integration-specific menu;
- a device action.

Logical navigation to a parent section, previous domain screen or drill-down level may exist elsewhere in the panel when needed, but it is not the permanent left shell control.

### 4.4 Scroll behavior

The Header may be `sticky` or shell-fixed, but its behavior must be identical across specialized panels using the same shell version. It MUST NOT participate in user zoom.

## 5. Zoom controls

The zoom-control surface is shell-owned and remains at native scale.

Canonical controls:

```text
−   100%   +
```

Required behavior is defined by `SPECIALIZED_PANEL_ZOOM_STANDARD.md`.

Zoom controls MUST NOT cover the Header or Bottom Tab Bar. Their position is derived from shell navigation clearances and safe areas; domain modules do not reserve arbitrary space for them.

## 6. Zoomable work viewport

Only the work viewport is scaled.

The following stay at native scale:

- Home Assistant chrome;
- specialized Header;
- Home Assistant main-menu button;
- Refresh/overflow shell controls;
- zoom controls;
- Bottom Tab Bar;
- device safe areas.

Responsive composition is selected first and user zoom is applied second:

```text
viewport size
→ mobile/tablet/desktop layout
→ domain content layout
→ user zoom
```

User zoom must not trigger an artificial switch between mobile and desktop layouts. When enlarged, content may pan/scroll without moving shell navigation surfaces.

## 7. Bottom Tab Bar

Primary in-app navigation for 3–5 sections MUST use one shared full-width Bottom Tab Bar.

Required:

- edge-attached to the viewport bottom;
- fixed while domain content scrolls;
- full-width on the mobile reference viewport;
- no external left/right/bottom card gap;
- not a floating pill/card;
- respects `env(safe-area-inset-bottom)`;
- identical base height and item geometry across specialized panels;
- active section is unambiguous;
- icon plus short text label;
- touch targets suitable for one-handed mobile use;
- no shrink-to-unreadable behavior when there are too many destinations.

More than five primary destinations must be reduced through `Сервис`, `Диагностика`, `Ещё` or drill-down hierarchy.

Bottom shell reserve is:

```text
bottom tab bar content height
+ safe-area-inset-bottom
```

The final work-content element MUST scroll fully above the Bottom Tab Bar. Domain content MUST NOT hard-code a second competing bottom safe-area reserve. Bottom Tab Bar is never scaled; zoom controls sit above its occupied region.

## 8. Device Selector placement

When required for multiple peer physical devices, canonical placement is:

```text
HEADER
↓
DEVICE SELECTOR
↓
ZOOMABLE DOMAIN CONTENT
↓
BOTTOM TAB BAR
```

The selector remains directly below the Header and is not moved by Bottom Tab changes. For shell v1 it SHOULD remain at native scale when used as persistent application context.

## 9. Responsive policy

Reference acceptance order:

1. iPhone Pro Max portrait;
2. smaller iPhone portrait;
3. iPad/tablet;
4. desktop.

Mobile portrait is the source hierarchy. Tablet/desktop are adaptations of the accepted shell, not independently designed applications.

Required at every breakpoint:

- safe areas remain correct;
- Header remains usable and title centered;
- Home Assistant main-menu button remains available on the left;
- Bottom Tab Bar does not cover content;
- zoom controls remain reachable;
- no shell-induced horizontal clipping;
- domain responsive layout is evaluated before user zoom.

## 10. Non-conforming patterns

The following are prohibited in new specialized panels:

- Header under Dynamic Island/notch;
- application-specific `padding-top` hacks for one phone;
- permanent Back button in the left Header rail instead of the Home Assistant main-system menu;
- floating bottom navigation card with side/bottom gaps;
- bottom controls covered by the iOS Home Indicator;
- zooming the Header or Bottom Tab Bar together with content;
- browser/page zoom as panel zoom;
- separate pinch implementations in individual integrations;
- separate bottom-navigation geometry per integration;
- separate main-menu button geometry per integration;
- hard-coded viewport-height calculations that ignore safe-area values.

## 11. Acceptance criteria

A specialized panel shell is accepted only when all are true:

1. Header content stays below the top safe area on a notched/Dynamic-Island iPhone;
2. the left Header rail is always the Home Assistant main-system menu button;
3. the centered title and right rail follow standard geometry;
4. Header does not scale with domain content;
5. zoom controls remain native-sized and usable;
6. only the work viewport changes scale;
7. Bottom Tab Bar remains fixed, full-width and native-sized;
8. Bottom Tab Bar respects the Home Indicator safe area;
9. the last domain item scrolls completely above the bar;
10. zoom controls do not overlap bottom navigation;
11. no device-model-specific safe-area constants are required;
12. switching mobile/tablet/desktop layout is independent of user zoom;
13. a new specialized panel can use these shell behaviors without implementing its own Header, safe area, menu button, zoom or Bottom Tab Bar logic.

## 12. Project rule

> Specialized panels own domain content, not application chrome. The shared CGUI shell owns safe areas, the top Header with the Home Assistant main-system menu button permanently on the left, zoom controls, zoomable viewport and the full-width fixed Bottom Tab Bar. Only the work area scales; all navigation and device-safe-area surfaces remain at native scale.
