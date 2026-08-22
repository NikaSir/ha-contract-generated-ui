# Integration-owned dashboard UI standard v1.2

**Status:** Required  
**Applies to:** all integration-owned specialized dashboards in Home Assistant NikaS  
**Primary target:** iPhone Pro Max, portrait

## 1. Purpose

Integration-owned dashboards must behave and look like mobile applications inside Home Assistant rather than unrelated Lovelace dashboards.

The content and domain workflow remain integration-specific, but the application shell is shared:

1. compact top Header;
2. scrollable domain content;
3. full-width fixed bottom Tab Bar for primary in-app navigation.

The navigation model is app-like:

- Header Back = exit the specialized application to its declared parent surface;
- Bottom Tab Bar = move between the main sections of the current specialized application.

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

## 5. Screen hierarchy

The first screen must prioritize current domain state, not navigation chrome.

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

The user should understand the current operating state within a few seconds of opening the application.

## 6. Mobile-first rules

Acceptance is performed first on **iPhone Pro Max portrait**.

Required:

- no horizontal scroll;
- no clipped primary labels;
- one-handed reachability for frequent navigation/actions;
- Header remains compact;
- Bottom Tab Bar does not hide content;
- page has enough bottom clearance for the final card to scroll above the bar;
- iOS safe areas are respected;
- dark/light themes remain readable;
- desktop/iPad layouts are adaptations of the accepted mobile hierarchy, not the source design.

## 7. Entity/action behavior

The shared shell must not weaken domain safety.

- no raw Tuya DP writes from Lovelace;
- no direct RCI/SNMP write bypasses;
- no fabricated entity IDs or unsupported commands;
- `unknown` / `unavailable` never mean healthy;
- direct controls are exposed only through stable public APIs of the owning integration;
- long press on factual entity-backed domain elements should open normal Home Assistant more-info where appropriate;
- Header and Bottom Tab Bar themselves must never trigger entity/device actions.

## 8. Navigation metadata

Conceptual example:

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

`icon` remains navigation/brand metadata. `show_brand_icon: false` defines the Header presentation.

## 9. Application-specific corrections

### Stark SolarPower

- remove the battery/brand icon from the Header;
- center `Stark SolarPower` geometrically in the viewport;
- keep `UPS · UI v…` as secondary centered text;
- keep Back on the left and Refresh on the right;
- retain the current full-width fixed bottom Tab Bar (`Обзор · Диагностика · История`);
- retain the strong UPS operating-state cards and power-flow visualization.

### S8 OMNI

- Header uses Back, not a hamburger/Menu control as the primary exit;
- center `S8 OMNI` in the viewport;
- no decorative robot/integration icon in the Header;
- keep the full-width fixed bottom navigation (`Обзор · Уборка · Станция · Сервис · Диагн.`);
- keep composite robot + station state as the hero information.

### HO-SC-8W irrigation

- add explicit Back in the Header;
- center `Полив` in the viewport;
- move model/version to secondary text;
- remove the decorative droplet from the Header itself;
- keep droplet/sprinkler iconography inside status/navigation content where useful;
- keep primary navigation in the full-width fixed bottom Tab Bar (`Обзор · Зоны · Программы · Диагн.`).

### Keenetic Hero 4G+

- build directly to this standard;
- Back on the left, centered title, optional Refresh/overflow on the right;
- no router icon beside the Header title;
- full-width fixed bottom navigation;
- first screen prioritizes Internet / active WAN / Ethernet / LTE / recent failover, not system diagnostics.

## 10. Acceptance criteria

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
- `unknown` / `unavailable` remain visibly unreliable;
- no navigation element can accidentally execute a domain action.

## Project rule

> Integration-owned dashboards are mobile applications inside Home Assistant: explicit Back at top, geometrically centered application title, no decorative Header icon, domain content in the middle, and a full-width fixed Bottom Tab Bar for primary internal navigation.
