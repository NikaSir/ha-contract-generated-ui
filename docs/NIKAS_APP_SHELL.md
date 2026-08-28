# NikaS App Shell v1

> Specialized-panel Header references are superseded by `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.9 and `NIKAS_PANEL_NAVIGATION_CONTRACT.md`. All specialized panels use the permanent Home Assistant system menu and a centered source-return title plaque.

**Status:** staged for production rollout  
**Primary target:** iPhone Pro Max, portrait

## Purpose

`Дом`, `Действия` and `Инфраструктура` are the three house-wide surfaces of Home Assistant NikaS. They share the same fixed Home Assistant-menu Header and do not use Header Back as primary navigation.

Instead they share one central application shell with a persistent bottom Tab Bar:

- `Дом`
- `Действия`
- `Инфра`

The central shell is the parent navigation layer for integration-owned applications such as irrigation, S8 OMNI, Keenetic and Stark SolarPower UPS.

## Required mobile pattern

The Tab Bar is:

- fixed to the bottom edge of the viewport;
- full-width on the primary mobile viewport;
- part of the application shell, not a floating/pill card;
- safe-area aware on iOS;
- always available while the page scrolls;
- represented by icon + short label;
- visually consistent across all three central panels.

The active tab is highlighted inside the common bar and does not navigate when tapped again.

## Canonical routes

| Surface | Route | Tab label |
| --- | --- | --- |
| Дом | `/dashboard-house-v11/home` | `Дом` |
| Действия | `/dashboard-actions/home` | `Действия` |
| Инфраструктура | `/dashboard-infrastructure/overview` | `Инфра` |

These are application routes, not browser-history targets.

## Manifest contract

A generated central dashboard opts in explicitly:

```yaml
spec:
  app_shell:
    active: infrastructure
```

Allowed active values:

- `home`
- `actions`
- `infrastructure`

Optional staging route overrides may be declared under `app_shell.routes`; omitted routes keep their canonical production targets.

The renderer injects the shell only when this metadata is present.

## Frontend ownership

The shell frontend is owned by `ha-contract-generated-ui` and shipped with the integration as:

```text
custom_components/contract_generated_ui/frontend/nikas-app-shell.js
```

Home Assistant runtime setup:

1. serves the exact packaged asset at the public static path `/contract_generated_ui/frontend/nikas-app-shell.js` through `hass.http.async_register_static_paths`;
2. registers the cache-busted module URL `/contract_generated_ui/frontend/nikas-app-shell.js?v=<integration-version>` through `frontend.add_extra_js_url()`;
3. deliberately does not place the frontend module below `/api`, so the browser can load it as a frontend static asset;
4. does not require Card Mod, Browser Mod, an external CDN or a separate HACS frontend package.

The generated dashboard uses:

```yaml
type: custom:nikas-app-shell
```

## RenderTrace

The shell is part of generated output and therefore its transformer source contributes to `renderer_engine_sha256`.

This is intentional: a visual/navigation change to the shared shell must be explainable by the same release-gate machinery as any other renderer change.

## Infrastructure v0.7 boundary

`Инфраструктура v0.7` is the first production surface using the shell.

It contains one central operational `overview` only. The old top-level `Диагностика` view is removed because detailed diagnostics are increasingly owned by the corresponding specialized integrations.

The first shell release deliberately does **not** simultaneously redesign every infrastructure summary card. After live iPhone validation of the shell geometry, the next pass can compact Electrical Grid / UPS / Keenetic summaries independently.

## Acceptance criteria

NikaS App Shell v1 is accepted when, on iPhone Pro Max portrait:

- the custom element loads without a Lovelace configuration-error card;
- the Tab Bar is visually attached to the bottom edge;
- there are no floating side/bottom gaps;
- the final content can scroll completely above the Tab Bar;
- the iOS bottom safe area is respected;
- the active surface is unambiguous;
- switching `Дом ↔ Действия ↔ Инфраструктура` takes one tap;
- no Home Assistant entity action can be triggered from the shell itself;
- the shell remains usable in light and dark themes.
