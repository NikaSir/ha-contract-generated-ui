# Specialized Panel Shell Standard v1.0

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
- Back-button geometry;
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

The panel must remain valid on devices with:

- Dynamic Island;
- display notch;
- rounded display corners;
- iOS Home Indicator;
- no cutout/safe-area requirement;
- tablet or desktop viewport.

Hard-coded fixes such as `top: 47px` for one phone are non-conforming.

## 4. Top Header

### 4.1 Position

The Header is the first shell-owned visual surface and MUST remain below the effective top safe area.

The shell must compute its top padding from the safe area, for example conceptually:

```css
padding-top: max(var(--nika-shell-top-padding), env(safe-area-inset-top, 0px));
```

No Header control or title may render underneath the notch or Dynamic Island.

### 4.2 Geometry

Canonical mobile Header:

```text
┌─────────────────────────────────────┐
│  ←           PANEL TITLE          ⟳ │
│              subtitle               │
└─────────────────────────────────────┘
```

Required:

- Back control on the left;
- geometrically viewport-centered title;
- at most one primary shell-level action on the right;
- matching left/right rail geometry whenever practical;
- minimum touch target approximately 44×44 pt;
- concise one-line primary title on the reference iPhone viewport;
- optional secondary line for model/context/version;
- no decorative integration/device icon next to the Header title;
- no duplicated oversized title immediately below the Header.

### 4.3 Back behavior

Back MUST navigate to the declaratively defined canonical parent route.

Browser history is not the canonical contract because the specialized panel may be entered from the sidebar, notification, launcher card or direct URL.

### 4.4 Scroll behavior

The Header may be `sticky` or shell-fixed, but its behavior must be identical across specialized panels using the same shell version.

It MUST NOT participate in user zoom.

## 5. Zoom controls

The zoom-control surface is shell-owned and remains at native scale.

Canonical controls:

```text
−   100%   +
```

Required behavior is defined by `SPECIALIZED_PANEL_ZOOM_STANDARD.md`.

Additional shell invariant:

- zoom controls MUST NOT cover the Header;
- zoom controls MUST NOT cover the Bottom Tab Bar;
- their fixed position must be derived from shell navigation clearances and safe areas;
- domain modules must not reserve their own arbitrary space for these controls.

## 6. Zoomable work viewport

Only the work viewport is scaled.

The following stay at native scale:

- Home Assistant chrome;
- specialized Header;
- Back/Refresh/overflow controls;
- zoom controls;
- Bottom Tab Bar;
- device safe areas.

The viewport is selected/responsive first and scaled second:

```text
viewport size
→ mobile/tablet/desktop layout
→ domain content layout
→ user zoom
```

User zoom must not trigger an artificial switch between mobile and desktop layouts.

When enlarged, content may pan/scroll without moving the shell navigation surfaces.

## 7. Bottom Tab Bar

### 7.1 Position and geometry

Primary in-app navigation for 3–5 sections MUST use one shared full-width Bottom Tab Bar.

Required:

- edge-attached to the viewport bottom;
- fixed while domain content scrolls;
- full-width on the mobile reference viewport;
- no external left/right/bottom card gap;
- not a floating pill/card;
- respects `env(safe-area-inset-bottom)`;
- identical base height and item geometry for all specialized applications;
- active section is unambiguous;
- icon plus short text label;
- touch targets suitable for one-handed mobile use;
- no shrink-to-unreadable behavior when there are too many destinations.

More than five primary destinations must be reduced through a secondary `Сервис`, `Диагностика`, `Ещё` or drill-down hierarchy.

### 7.2 Bottom safe area

The bar owns the bottom device clearance:

```text
bottom shell reserve =
  bottom tab bar content height
+ safe-area-inset-bottom
```

The final work-content element MUST be able to scroll fully above the Bottom Tab Bar.

Domain content MUST NOT hard-code a second competing bottom safe-area reserve.

### 7.3 Zoom interaction

Bottom Tab Bar is never scaled.

Zoom-controls sit above its occupied region and remain accessible at all zoom levels.

## 8. Device Selector placement

When required for multiple peer physical devices, the Device Selector is domain context but its canonical placement is shell-defined:

```text
HEADER
↓
DEVICE SELECTOR
↓
ZOOMABLE DOMAIN CONTENT
↓
BOTTOM TAB BAR
```

The selector remains directly below the Header and is not moved by Bottom Tab changes.

Whether the selector itself is zoomed is a shell policy. For the v1 shell it SHOULD remain at native scale when implemented as persistent application context; the selected device's detailed content is zoomable.

## 9. Responsive policy

Reference acceptance order:

1. iPhone Pro Max portrait;
2. smaller iPhone portrait;
3. iPad/tablet;
4. desktop.

Mobile portrait is the source hierarchy. Tablet/desktop are adaptations of the accepted shell, not separate independently designed applications.

Required at every breakpoint:

- safe areas remain correct;
- Header remains usable and title remains centered;
- Bottom Tab Bar does not cover content;
- zoom controls remain reachable;
- no shell-induced horizontal clipping;
- domain responsive layout is evaluated before user zoom.

## 10. Non-conforming patterns

The following are prohibited in new specialized panels:

- Header under Dynamic Island/notch;
- application-specific `padding-top` hacks for one phone;
- floating bottom navigation card with side/bottom gaps;
- bottom controls covered by the iOS Home Indicator;
- zooming the Header or Bottom Tab Bar together with content;
- browser/page zoom as panel zoom;
- separate pinch implementations in individual integrations;
- separate bottom navigation geometry per integration;
- separate Back-button geometry per integration;
- hard-coded viewport height calculations that ignore safe-area values.

## 11. Acceptance criteria

A specialized panel shell is accepted only when all are true:

1. Header content stays below the top safe area on a notched/Dynamic-Island iPhone;
2. Back, centered title and right rail share the standard geometry;
3. Header does not scale with domain content;
4. zoom controls remain native-sized and usable;
5. only the work viewport changes scale;
6. Bottom Tab Bar remains fixed, full-width and native-sized;
7. Bottom Tab Bar respects the Home Indicator safe area;
8. the last domain item scrolls completely above the bar;
9. zoom controls do not overlap the bottom navigation;
10. no device-model-specific safe-area constants are required;
11. switching mobile/tablet/desktop layout is independent of user zoom;
12. a new specialized panel can use these shell behaviors without implementing its own Header, safe area, zoom or Bottom Tab Bar logic.

## 12. Project rule

> Specialized panels own domain content, not application chrome. The shared CGUI shell owns safe areas, top Header, Back navigation, zoom controls, zoomable viewport and the full-width fixed Bottom Tab Bar. Only the work area scales; all navigation and device-safe-area surfaces remain at native scale.
