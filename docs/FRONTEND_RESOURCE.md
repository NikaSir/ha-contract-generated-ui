# Deterministic frontend resource

Home Assistant 2026 can race `add_extra_js_url()` module loading against Lovelace custom-card construction. Production NikaS dashboards therefore load the frontend bundle as a Lovelace module resource.

Add this once under the existing `lovelace:` block in `configuration.yaml`:

```yaml
lovelace:
  resources:
    - url: /contract_generated_ui/frontend/nikas-ui.js
      type: module
```

Keep existing `lovelace.dashboards:` entries alongside `resources:`. The URL is intentionally stable; the integration serves the file with cache headers disabled, so releases do not require changing this resource entry.

The bundle imports:

- `nikas-app-shell.js`
- `nikas-infrastructure-summary.js`

After adding the resource, validate configuration and fully restart Home Assistant. Then fully reload/reopen the mobile frontend once.
