# NikaS frontend resource

Home Assistant 2026 has open frontend races around `custom:` Lovelace elements: both `add_extra_js_url()` modules and ordinary Lovelace resources can be loaded after the dashboard has already started constructing custom cards. A late element can therefore leave a permanent `Configuration error` until the view happens to rebuild.

NikaS central dashboards no longer rely on custom Lovelace cards for their primary content. Infrastructure summaries are rendered with the native Home Assistant Markdown card and the dashboard reserves bottom clearance with a native borderless Markdown spacer.

The frontend bundle is retained only as progressive enhancement for the fixed NikaS bottom navigation. If the bundle loads late, the native dashboard remains fully usable; only the bottom bar can appear a little later. No Lovelace `custom:` card depends on the bundle in the v0.11+ Infrastructure dashboard.

Add this once under the existing `lovelace:` block in `configuration.yaml`:

```yaml
lovelace:
  resources:
    - url: /contract_generated_ui/frontend/nikas-ui.js
      type: module
```

Keep existing `lovelace.dashboards:` entries alongside `resources:`. The URL is intentionally stable and does not need to change for later releases.

`nikas-ui.js`:

- injects the fixed `Дом · Действия · Инфра` navigation as a global overlay outside Lovelace card construction;
- listens for Home Assistant route changes and updates the active central surface;
- keeps legacy custom-card modules available only as a migration fallback for already-generated older dashboards.

After initially adding the resource, validate configuration and fully restart Home Assistant. For v0.17.0 and later, regenerate the dashboards once so old `custom:nikas-*` cards are replaced by native cards.
