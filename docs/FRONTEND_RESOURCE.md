# NikaS frontend resources

> Shell, Header, source-aware return, zoom/scroll, stable rendering, optional indicators, typography and Bottom Tab Bar requirements are governed by `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.7. Older explicit-Back configuration notes are historical.

Home Assistant 2026 can construct Lovelace before a late `custom:` element is registered. NikaS central dashboards therefore keep their primary content native Lovelace. Frontend JavaScript is used only where an application shell materially improves navigation.

## Global navigation — Contract Generated UI 0.22.0

The 0.22.0 line keeps the global-navigation cache generation at **b004** because `nikas-ui.js` itself is unchanged.

Contract Generated UI automatically loads the global navigation enhancement through Home Assistant `frontend.add_extra_js_url()`:

```text
/contract_generated_ui/frontend/nikas-ui.js?build=b004
```

It renders the common `Дом · Действия · Инфра` Bottom Tab Bar and Lovelace-embedded tab groups described by the formal navigation contract. No manual `lovelace.resources` entry is required.

## Generic generated application panels

Non-specialized manifest-defined subpanels use one shared web component and one self-contained frontend bundle only when their declared route is not already registered:

```text
/contract_generated_ui/frontend/nikas-generated-subpanel.js?build=b006
```

The shared host receives panel title/subtitle, an optional parent route for an in-work link, 2–5 tab descriptors and optional read-only runtime source metadata from `PanelManifest + NavigationContract`.

An existing Home Assistant/Lovelace panel always wins a route collision. Contract Generated UI does not remove or replace it. The integration records only routes it registered as missing-route fallbacks, and unload removes only those recorded fallbacks.

For runtime read-only panels the host reads both Home Assistant **Entity Registry** and **Device Registry**. Current values are resolved only from `hass.states`. It does not call Home Assistant services, does not invoke `call_service`, and does not expose toggle/control handlers.

Concrete Home Assistant entity IDs and private semantic inventory remain outside public manifests.

### Multi-device grouping

Starting with `0.22.0`, a read-only integration that exposes entities under several `device_id` values is rendered as a multi-device application:

- the `Обзор` view shows one compact block per Home Assistant device;
- device names come from Device Registry (`name_by_user` → `name` → `model`);
- detailed tabs show a compact device selector when more than one device exists;
- the selected device persists while switching among internal tabs;
- non-service views do not expose raw `entity_id` text;
- the `Сервис` view may show raw entity IDs only for `unknown` / `unavailable` diagnostics.

This mechanism remains generic and is not a host for integration-owned applications.

## Visual contract

Generated custom panels use the common NikaS application language:

- Home Assistant menu button `☰` in the upper-left, dispatching `hass-toggle-menu`;
- geometrically centered title/subtitle;
- refresh rail in the upper-right;
- Hero status section;
- rounded application cards;
- fixed edge-attached Bottom Tab Bar;
- safe-area handling on iPhone;
- mobile one-column entity layout.

Architectural invariant:

> One CGUI-owned generic custom-panel host; integration-owned applications register and serve themselves.

## Routing and parent navigation

A generated generic custom panel has one Home Assistant panel route, for example:

```text
/dashboard-example
```

Its logical parent remains declarative in `navigation/main.yaml`:

The permanent Header control remains the Home Assistant system menu. When a parent transition is required, the explicit parent path is presented inside the work area and never depends on browser history.

`/dashboard-zont` is explicitly outside this mechanism. It is registered and served only by the dedicated `ha-zont` integration. A central navigation link to that URL does not transfer panel ownership back to Contract Generated UI.

## House overview specialized panel

The `nikas-house-overview` runtime remains available as a missing-route fallback. If `/dashboard-house-v11` already exists, Contract Generated UI preserves the existing Home Assistant/Lovelace panel and does not register the fallback over it. The shared shell can still provide the fixed Header and global Bottom Tab Bar without taking ownership of the panel content.

The same rule applies to `nikas-infrastructure-overview`: it may register only when `/dashboard-infrastructure` is unowned. Its verified operational model—grid, two UPS devices and Keenetic—remains available for that fallback and for generated review, but it cannot displace an existing panel.

## Lovelace registration

Generated application subpanels may be exported for reviewed Lovelace registration. Runtime fallback registration never overwrites an existing dashboard and requires no automatic edit of `configuration.yaml`.

After an integration update, fully restart Home Assistant so custom-panel module cache keys are refreshed. ZONT lifecycle and cache invalidation are handled entirely by `ha-zont`.
