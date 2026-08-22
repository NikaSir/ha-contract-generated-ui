# Integration-owned dashboard UI standard v1.2

**Status:** Required  
**Applies to:** all integration-owned specialized dashboards in Home Assistant NikaS  
**Primary target:** iPhone Pro Max, portrait

## 1. Purpose

Integration-owned dashboards must behave and look like mobile applications inside Home Assistant rather than unrelated Lovelace dashboards.

The content and domain workflow remain integration-specific, but the application shell is shared:

1. compact top Header;
2. optional persistent Device Selector when one application owns multiple peer physical devices of the same type;
3. scrollable domain content;
4. full-width fixed bottom Tab Bar for primary in-app navigation.

The navigation model is app-like and separates three different questions:

- Header Back = **where do I exit?** — leave the specialized application for its declared parent surface;
- Device Selector = **which physical device am I looking at?**;
- Bottom Tab Bar = **what aspect of that device am I looking at?** — move between the main sections of the current specialized application.

These navigation levels must not be mixed.

## 2. Required top Header

Every top-level view must start with the same compact Header.

```text
┌─────────────────────────────────────┐
│  ←            Panel title         ⟳ │
│             optional subtitle       │
└─────────────────────────────────────┘
```

### 2.1 Left side — Back

- icon: `mdi:arrow-left`;
- the arrow button is always present;
- visible text `Назад` is optional when it would compromise the centered title;
- touch target approximately 44×44 pt or larger;
- tap performs explicit Home Assistant `navigate`;
- long press and double tap do not trigger domain actions;
- browser history is not the canonical navigation contract.

### 2.2 Center — title

The title must be **geometrically centered on the mobile viewport**, not merely centered in the free space between the left and right controls.

Rules:

- one concise application title;
- one line on the primary iPhone viewport;
- optional short secondary line for model/context/version;
- no second oversized duplicate title immediately below the Header;
- UI/integration version is secondary information and must not compete with the application title.

Examples:

- `Stark SolarPower` / `UPS · UI v0.3.1`;
- `S8 OMNI` / optional model or connection context;
- `Полив` / `HO-SC-8W`;
- `Keenetic Hero 4G+` / optional WAN context.

### 2.3 Header icon policy

A decorative integration/device icon **must not be placed next to the title in the Header**.

Reason: it shifts the visual center, competes with Back and makes otherwise different applications look inconsistent.

The integration icon may still exist in navigation metadata, sidebar metadata, launcher cards, status cards or brand assets. It is simply not part of the standard top Header.

### 2.4 Right side — contextual global action

The right side may contain at most one primary global control, with an optional overflow menu when genuinely needed.

Examples:

- refresh;
- overflow (`⋮`);
- another application-level action that is not a device-domain command.

Left and right control zones should use matching geometry whenever practical so the centered title remains visually balanced.

## 3. Back navigation contract

A specialized dashboard can be entered from a central panel, sidebar, notification or direct URL. Therefore browser history is not deterministic enough.

Each specialized dashboard declares a canonical parent route.

| Specialized dashboard | Canonical parent |
| --- | --- |
| HO-SC-8W irrigation | `/dashboard-actions` |
| S8 OMNI vacuum | `/dashboard-actions` |
| Keenetic Hero 4G+ | `/dashboard-infrastructure/overview` |
| Stark SolarPower UPS | `/dashboard-infrastructure/overview` |

Back always exits to this declared parent route. Internal views/tabs do not redefine Back.

## 4. Primary in-app navigation — Bottom Tab Bar

When the specialized application has 3–5 primary sections, they must be exposed through a **full-width, edge-attached, fixed bottom Tab Bar**.

Required behavior:

- fixed to the bottom edge of the viewport;
- full-width on the primary mobile viewport;
- no external left/right/bottom gaps;
- not a floating card or pill;
- remains available while the content scrolls;
- respects iOS bottom safe area;
- active tab is highlighted inside the shared bar;
- each item uses an icon plus short label;
- touch targets are comfortable for one-handed iPhone use;
- the final content can scroll fully above the bar.

### 4.1 Non-conforming pattern

A floating navigation card with visible side/bottom margins is not accepted as primary navigation.

### 4.2 Number of tabs

Preferred: 3–5 primary tabs.

If more than five destinations exist, secondary functions move under `Сервис`, `Диагностика`, `Ещё` or drill-down screens rather than shrinking touch targets.

### 4.3 Current application tab sets

**HO-SC-8W**

`Обзор · Зоны · Программы · Диагн.`

**S8 OMNI**

`Обзор · Уборка · Станция · Сервис · Диагн.`

**Stark SolarPower**

`Обзор · Диагностика · История`

**Keenetic Hero 4G+**

`Обзор · WAN/LTE · Трафик · Диагн.`

If Failover becomes a full independent workflow, Keenetic may use five tabs:

`Обзор · WAN/LTE · Failover · Трафик · Диагн.`

## 5. Multi-device context — Device Selector

If one integration-owned application serves **multiple peer physical devices of the same type**, device selection becomes a separate persistent navigation level.

Required hierarchy:

```text
HEADER
↓
DEVICE SELECTOR
↓
CONTENT OF SELECTED DEVICE
↓
BOTTOM TAB BAR
```

The Device Selector answers **which device?**. The Bottom Tab Bar answers **which section?**. They must remain independent.

### 5.1 Placement and persistence

The Device Selector:

- is located immediately below the Header on every primary section;
- remains in the same geometric position when the Bottom Tab Bar section changes;
- keeps a fixed device order;
- never moves the selected device to the first position;
- marks selection only through active-state presentation;
- preserves the selected device when moving between Bottom Tab Bar sections during the application session;
- does not disappear on one section and reappear on another.

### 5.2 Device status in selector

Compact status of non-selected devices may be shown directly in the selector, for example with a small status dot or badge.

This may communicate concise states such as:

- healthy;
- warning;
- fault;
- unreliable/unavailable.

The selector must not turn into a second telemetry panel. Detailed information belongs to the Content area of the selected device.

### 5.3 Content ownership

All primary Content below the Device Selector belongs to **only the selected device**.

Do not render a full operational card for every peer device one after another on each section. That pattern:

- duplicates information;
- makes mobile pages unnecessarily long;
- makes the selector semantically meaningless;
- breaks the mobile-application context model.

Changing the selected device must update the Content in place while preserving the current Bottom Tab Bar section.

### 5.4 Scope

Device Selector is for multiple **peer physical devices** represented by one specialized application.

It is not automatically used for subordinate parts of one device/domain. For example:

- irrigation zones are not peer controller devices;
- S8 OMNI robot/station parts are one application domain, not two peer vacuums;
- Ethernet/LTE are WAN channels of one Keenetic, not two peer routers.

If only one physical device exists, no Device Selector is required.

### 5.5 Stark SolarPower reference model

Stark SolarPower is the reference multi-device implementation.

The invariant layout on all three primary sections is:

```text
┌─────────────────────────────────┐
│ ←       Stark SolarPower      ⟳ │
│        UPS · UI vX.X.X          │
├─────────────────────────────────┤
│ [ UPS Интернет ] [ UPS Котёл ] │
├─────────────────────────────────┤
│                                 │
│   CONTENT OF SELECTED UPS        │
│                                 │
├─────────────────────────────────┤
│ Обзор │ Диагностика │ История  │
└─────────────────────────────────┘
```

Rules:

- `UPS Интернет` and `UPS Котёл` remain in a fixed order;
- the chosen UPS remains selected when switching `Обзор ↔ Диагностика ↔ История`;
- status dots may expose the health of both UPS without expanding both devices;
- `Обзор` renders one complete card for the selected UPS only;
- `Диагностика` renders technical data for the selected UPS only;
- `История` renders graphs/events for the selected UPS only;
- no second full UPS block is appended below the selected one.

## 6. Screen hierarchy

The first screen must prioritize current domain state, not navigation chrome.

Single-device application:

```text
HEADER
↓
PRIMARY STATUS
↓
FREQUENT ACTIONS / KEY TELEMETRY
↓
DOMAIN CONTENT
↓
BOTTOM TAB BAR
```

Multi-device application:

```text
HEADER
↓
DEVICE SELECTOR
↓
PRIMARY STATUS OF SELECTED DEVICE
↓
FREQUENT ACTIONS / KEY TELEMETRY
↓
DOMAIN CONTENT OF SELECTED DEVICE
↓
BOTTOM TAB BAR
```

The user should understand the current operating state within a few seconds of opening the application.

## 7. Mobile-first rules

Acceptance is performed first on **iPhone Pro Max portrait**.

Required:

- no horizontal scroll;
- no clipped primary labels;
- one-handed reachability for frequent navigation/actions;
- Header remains compact;
- Device Selector remains compact and does not displace primary status below the first useful viewport without justification;
- Bottom Tab Bar does not hide content;
- page has enough bottom clearance for the final card to scroll above the bar;
- iOS safe areas are respected;
- dark/light themes remain readable;
- desktop/iPad layouts are adaptations of the accepted mobile hierarchy, not the source design.

## 8. Entity/action behavior

The shared shell must not weaken domain safety.

- no raw Tuya DP writes from Lovelace;
- no direct RCI/SNMP write bypasses;
- no fabricated entity IDs or unsupported commands;
- `unknown` / `unavailable` never mean healthy;
- direct controls are exposed only through stable public APIs of the owning integration;
- long press on factual entity-backed domain elements should open normal Home Assistant more-info where appropriate;
- Header, Device Selector and Bottom Tab Bar themselves must never trigger unrelated entity/device actions.

## 9. Navigation metadata

Conceptual single-device example:

```yaml
panel:
  id: irrigation
  title: Полив
  path: /dashboard-irrigation
  icon: mdi:sprinkler
  owner: ha-ho-sc-8w
  expose_in_generated_ui: true
  preferred_view: overview
  header:
    title_alignment: viewport_center
    show_brand_icon: false
    back:
      icon: mdi:arrow-left
      parent_path: /dashboard-actions
  navigation:
    primary: full_width_fixed_bottom_tab_bar
    floating: false
```

Conceptual multi-device addition:

```yaml
  device_context:
    selector: persistent_below_header
    preserve_across_views: true
    reorder_selected: false
    content_scope: selected_device_only
```

`icon` remains navigation/brand metadata. `show_brand_icon: false` defines the Header presentation.

## 10. Application-specific corrections

### Stark SolarPower

- remove the battery/brand icon from the Header;
- center `Stark SolarPower` geometrically in the viewport;
- keep `UPS · UI v…` as secondary centered text;
- keep Back on the left and Refresh on the right;
- keep `UPS Интернет / UPS Котёл` as a persistent Device Selector directly below Header on **Обзор**, **Диагностика** and **История**;
- preserve the selected UPS when switching bottom tabs;
- keep the selector device order fixed and use only active-state to indicate selection;
- status dots/badges may expose health of the non-selected UPS;
- `Обзор` shows one full operating-state/power-flow card for the selected UPS only;
- `Диагностика` continues its current selected-UPS information architecture;
- `История` shows graphs/events for the selected UPS only;
- do not append a second full UPS card/history block below the selected device;
- retain the full-width fixed bottom Tab Bar (`Обзор · Диагностика · История`).

### S8 OMNI

- Header uses Back, not a hamburger/Menu control as the primary exit;
- center `S8 OMNI` in the viewport;
- no decorative robot/integration icon in the Header;
- keep the full-width fixed bottom navigation (`Обзор · Уборка · Станция · Сервис · Диагн.`);
- keep composite robot + station state as the hero information;
- no Device Selector is required while the application owns one S8 OMNI system.

### HO-SC-8W irrigation

- add explicit Back in the Header;
- center `Полив` in the viewport;
- move model/version to secondary text;
- remove the decorative droplet from the Header itself;
- keep droplet/sprinkler iconography inside status/navigation content where useful;
- keep primary navigation in the full-width fixed bottom Tab Bar (`Обзор · Зоны · Программы · Диагн.`);
- zones are subordinate channels of one controller and must not be treated as peer devices by the Device Selector rule.

### Keenetic Hero 4G+

- build directly to this standard;
- Back on the left, centered title, optional Refresh/overflow on the right;
- no router icon beside the Header title;
- full-width fixed bottom navigation;
- first screen prioritizes Internet / active WAN / Ethernet / LTE / recent failover, not system diagnostics;
- Ethernet/LTE are channels of one router and do not constitute a Device Selector.

## 11. Acceptance criteria

An integration-owned dashboard is UI-complete only when:

- Header is present on every primary view;
- Back is explicit and navigates to the declared parent;
- title is geometrically centered on iPhone Pro Max portrait;
- no decorative brand/device icon shifts the Header title;
- right-side global action does not distort title centering;
- the title is not redundantly repeated as another oversized heading below;
- primary tabs are in a full-width fixed bottom bar when the application has 3–5 primary sections;
- the bottom bar is edge-attached, not floating;
- the active tab is unambiguous;
- the final content scrolls above the bottom bar;
- if multiple peer devices exist, Device Selector is persistent directly below Header on all primary sections;
- selected device is preserved across section changes;
- device order never changes because of selection;
- primary Content belongs only to the selected peer device rather than duplicating full blocks for every device;
- `unknown` / `unavailable` remain visibly unreliable;
- no navigation element can accidentally execute an unrelated domain action.

## Project rule

> Integration-owned dashboards are mobile applications inside Home Assistant: explicit Back at top, geometrically centered application title, no decorative Header icon, optional persistent Device Selector for peer physical devices, domain content scoped to the selected device, and a full-width fixed Bottom Tab Bar for primary internal navigation.
