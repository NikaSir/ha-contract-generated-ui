# NikaS frontend resource

Home Assistant 2026 can construct Lovelace before a late `custom:` element is registered. NikaS central and generated subpanel content therefore stays usable without frontend custom cards.

The frontend bundle is progressive enhancement for shared navigation and application chrome only.

## Automatic loading — v0.19.0_b003

Contract Generated UI **автоматически** registers the UI bundle through Home Assistant `frontend.add_extra_js_url()` after its static paths are ready.

The b003 URL is build-versioned for cache invalidation:

```text
/contract_generated_ui/frontend/nikas-ui.js?build=b003
```

Manual `lovelace.resources` registration is not required. Existing `lovelace.dashboards:` entries must be preserved.

Because dashboard content is native Lovelace, late frontend loading cannot turn dashboard content into `Configuration error`; at worst Header/Bottom Tab Bar progressive chrome appears a little later.

## Data-driven navigation

Contract Generated UI compiles the formal navigation contract and panel manifests into:

```text
/config/contract_generated_ui/generated/navigation.json
```

The integration serves it at:

```text
/contract_generated_ui/navigation.json
```

`nikas-ui.js` loads that registry with `cache: no-store` and renders:

- global `Дом · Действия · Инфра` navigation;
- local Bottom Tab Bar for generated application subpanels;
- local embedded tab groups such as the electrical subpanel;
- a shared external-panel-like Header for active generated subpanels.

Subsystem names, parent routes, tab labels, icons and tab URLs are **not** hardcoded in `nikas-ui.js`.

## Embedded application subpanels — b003

ZONT and StarLine demonstrate the preferred route model:

```text
/dashboard-house/zont-overview
/dashboard-house/zont-heating
...
/dashboard-house/starline-overview
/dashboard-house/starline-security
...
```

They are composed into the existing parent dashboard YAML rather than registered as separate Lovelace dashboards. Their parent views receive generated launch cards.

The route is embedded, but the visual language is the same as external NikaS specialized panels:

```text
App Header: Back | centered title/subtitle | Refresh
↓
Hero / current state
↓
Native Lovelace content
↓
Fixed Bottom Tab Bar
```

The shared Header uses the same symmetric rail principle as `NikaS Integration Panel Template v1.0`; the lower navigation is fixed, edge-attached and safe-area aware.

Native Home Assistant `subview: true` and explicit `back_path` remain in generated YAML as a reliability fallback. If the progressive shell cannot load, native Lovelace content and native Back remain usable.

## Legacy modules

`nikas-app-shell.js` and `nikas-infrastructure-summary.js` remain loaded through `Promise.allSettled` only as migration fallback for already-generated older dashboards. New generated subpanels do not depend on them.

After a Contract Generated UI update, fully restart Home Assistant and regenerate dashboards so YAML and `navigation.json` are synchronized.
