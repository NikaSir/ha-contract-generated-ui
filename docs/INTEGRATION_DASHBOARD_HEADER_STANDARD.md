# Integration dashboard unified header standard

**Status:** Required  
**Applies to:** integration-owned specialized dashboards in Home Assistant NikaS

## Purpose

Every integration-owned dashboard must use the same top-level header pattern so that irrigation, robot vacuum, router and UPS panels feel like parts of one Home Assistant application rather than unrelated dashboards.

Primary target: **iPhone Pro Max, portrait**.

## Required header

The first visual element of every specialized dashboard view must be a compact unified header containing:

1. a left-side **Back / Назад** control;
2. the dashboard title;
3. the integration/domain icon when it improves recognition.

The header must remain visually compact and must not consume the first mobile screen with decorative content.

### Back control

Required behavior:

- icon: `mdi:arrow-left`;
- visible label: `Назад` when the layout permits it; the arrow alone is acceptable only where the mobile layout cannot fit the label without truncating the title;
- touch target must be comfortable for one-handed iPhone use (approximately 44×44 pt or larger);
- tap performs an explicit Home Assistant `navigate` action;
- long press and double tap must not trigger domain actions;
- the back route is a declared stable route, not an inferred entity/action target.

### Do not use browser history as the navigation contract

The header must **not rely on browser history** as its canonical back behavior.

A specialized dashboard may be opened from:

- `Дом`;
- `Действия`;
- `Инфраструктура`;
- a notification;
- a deep link;
- the Home Assistant sidebar.

Therefore browser history is not deterministic enough to define application navigation. Each specialized dashboard declares a canonical `parent_path`, and the Back control navigates to that route.

## Canonical parent routes

Initial Home Assistant NikaS convention:

| Specialized dashboard | Canonical parent |
| --- | --- |
| HO-SC-8W irrigation | `/dashboard-actions` |
| S8 OMNI vacuum | `/dashboard-actions` |
| Keenetic Hero 4G+ | `/dashboard-infrastructure/overview` |
| Stark SolarPower UPS | `/dashboard-infrastructure/overview` |

If the house-wide navigation architecture changes, the parent route is updated as declared metadata rather than hard-coded independently into multiple cards.

## Header metadata contract

Conceptual metadata:

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
    back:
      label: Назад
      icon: mdi:arrow-left
      parent_path: /dashboard-actions
```

For infrastructure-owned domains:

```yaml
panel:
  id: keenetic
  title: Keenetic
  path: /dashboard-keenetic
  icon: mdi:router-network
  owner: ha-keenetic-hero-4g
  expose_in_generated_ui: true
  preferred_view: overview
  header:
    back:
      label: Назад
      icon: mdi:arrow-left
      parent_path: /dashboard-infrastructure/overview
```

This is navigation metadata. It does not transfer ownership of the specialized dashboard to `ha-contract-generated-ui`.

## Visual rules

- Header title is concise and remains on one line on the primary iPhone viewport.
- The Back control is always in the same left-side position across specialized dashboards.
- Avoid oversized title cards and duplicate page titles immediately below the header.
- Use the same spacing and touch geometry across all integration panels.
- Respect Home Assistant/iOS safe areas and the native application header.
- Do not introduce a custom sticky-header dependency solely for this pattern; prefer stable Home Assistant/Lovelace primitives unless a shared project component is later adopted.
- Dark and light themes must remain readable.

## View behavior

The unified header is present on every top-level view of a specialized dashboard (`Обзор`, `Диагностика`, `Станция`, `Зоны`, `Программы`, etc.).

The Back control always exits to the dashboard's canonical parent. Internal tabs/views are used for navigation inside the specialized dashboard; they must not redefine the meaning of Back independently.

## Acceptance criteria

A specialized integration dashboard is not considered UI-complete unless:

- the unified header is present on every view;
- Back is visible and usable on iPhone Pro Max portrait;
- Back navigates to the declared canonical parent route;
- Back does not depend on browser history;
- the title is not duplicated immediately below the header;
- no domain action can be triggered accidentally from the header.

## Project rule

> Every integration-owned specialized dashboard has the same compact header with an explicit Back control. Back navigation is a declared stable application route, not browser history.
