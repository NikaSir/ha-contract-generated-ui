# NikaS frontend resources

Home Assistant 2026 can construct Lovelace before a late `custom:` element is registered. NikaS central dashboards therefore keep their primary content native Lovelace. Frontend JavaScript is used only where an application shell materially improves navigation.

## Global navigation — Contract Generated UI 0.22.0

The 0.22.0 line keeps the global-navigation cache generation at **b004** because `nikas-ui.js` itself is unchanged.

Contract Generated UI automatically loads the global navigation enhancement through Home Assistant `frontend.add_extra_js_url()`:

```text
/contract_generated_ui/frontend/nikas-ui.js?build=b004
```

It renders the common `Дом · Действия · Инфра` Bottom Tab Bar and Lovelace-embedded tab groups described by the formal navigation contract. No manual `lovelace.resources` entry is required.

## Shared generated application panels

Generated application subpanels such as ZONT and StarLine are **автоматически** registered as Home Assistant custom panels by Contract Generated UI using one shared web component and one self-contained frontend bundle:

```text
/contract_generated_ui/frontend/nikas-generated-subpanel.js?build=b006
```

The shared host receives panel title/subtitle, explicit Back parent, 2–5 tab descriptors and optional read-only runtime source metadata from `PanelManifest + NavigationContract`.

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

This mechanism is generic. StarLine is the first field use: two vehicles can be shown side by side in the overview while `Охрана`, `Двигатель`, `Авто` and `Сервис` operate on the selected vehicle.

## Read-only StarLine profile

StarLine UI `v0.5.0` uses the field-reference hierarchy:

- `Обзор` — up to six priority facts per vehicle, targeting охрана, пробег, топливо, АКБ, двигатель and салон;
- `Охрана` — binary/lock state set for the selected vehicle;
- `Двигатель` — engine, ignition, autostart/heater-related state only;
- `Авто` — sensor and device-tracker telemetry for the selected vehicle;
- `Сервис` — unavailable/unknown entities only.

Commands remain intentionally absent. History graphs and a map are separate read-only presentation layers and are not inferred until the real StarLine entity/device grouping has been field-verified.

## Visual contract

Generated custom panels use the common NikaS application language:

- Back button in the upper-left;
- geometrically centered title/subtitle;
- refresh rail in the upper-right;
- Hero status section;
- rounded application cards;
- fixed edge-attached Bottom Tab Bar;
- safe-area handling on iPhone;
- mobile one-column entity layout.

Architectural invariant:

> One CGUI-owned shared custom-panel host; domain content stays declarative and read-only until explicitly promoted.

## Routing and Back

A generated custom panel has one Home Assistant panel route, for example:

```text
/dashboard-zont
/dashboard-starline
```

Its logical parent remains declarative in `navigation/main.yaml`:

```text
ZONT     → /dashboard-house/heating
StarLine → /dashboard-house/vehicles
```

The shared Header uses this parent path directly and never depends on browser history.

## Lovelace registration

Generated application subpanels are not exported under `lovelace.dashboards:` and require no manual edit of `configuration.yaml`.

During field validation generated ZONT and StarLine panels remain visible in the Home Assistant sidebar. After an integration update, fully restart Home Assistant so the custom-panel module cache key is refreshed.
