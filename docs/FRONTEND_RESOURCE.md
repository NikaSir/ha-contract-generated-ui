# NikaS frontend resource

Home Assistant 2026 can construct Lovelace before a late `custom:` element is registered. NikaS central and generated subpanel content therefore stays usable without frontend custom cards.

The frontend bundle is progressive enhancement for fixed navigation only.

## Resource

Add once under the existing `lovelace:` block:

```yaml
lovelace:
  resources:
    - url: /contract_generated_ui/frontend/nikas-ui.js
      type: module
```

Keep existing `lovelace.dashboards:` entries alongside `resources:`.

## Data-driven navigation

Contract Generated UI `0.19+` compiles the formal navigation contract and panel manifests into:

```text
/config/contract_generated_ui/generated/navigation.json
```

The integration serves it at:

```text
/contract_generated_ui/navigation.json
```

`nikas-ui.js` loads that registry with `cache: no-store` and renders:

- global `Дом · Действия · Инфра` navigation;
- generated standalone subpanel tabs such as ZONT and StarLine;
- embedded local tab groups such as the current electricity subpanel.

Subsystem names, parent routes, tab labels, icons and tab URLs are **not** hardcoded in `nikas-ui.js`.

If the registry loads late or cannot be read, native Lovelace content and native subview Back remain usable. Only local progressive-enhancement navigation may appear later; a minimal global fallback is retained.

## Native subpanel header

Generated subpanel views use Home Assistant `subview: true` plus explicit `back_path`. The frontend bundle does not draw a competing Header or implement browser-history Back.

## Legacy modules

`nikas-app-shell.js` and `nikas-infrastructure-summary.js` remain loaded through `Promise.allSettled` only as migration fallback for already-generated older dashboards. New generated subpanels do not depend on them.

After adding the resource initially, validate configuration and fully restart Home Assistant. After a Contract Generated UI update, regenerate dashboards so YAML and `navigation.json` are synchronized.
