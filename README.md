# NikaS House panel for Home Assistant

This repository builds and validates only the new main **Дом** overview for Home Assistant NikaS.

The installed integration domain remains `contract_generated_ui` for upgrade compatibility. Its production scope is now deliberately narrower: one panel, one manifest and one public UI contract.

## Route ownership

| Surface | Route | Owner |
|---|---|---|
| Existing YAML Дом | `/dashboard-house` | Existing Home Assistant YAML configuration |
| New main Дом | `/dashboard-house-v11/home` | This repository |
| Existing YAML Помещения | `/dashboard-rooms/rooms` | Existing Home Assistant YAML configuration |
| Existing YAML Действия | `/dashboard-actions/home` | Existing Home Assistant YAML configuration |
| Existing YAML Инфраструктура | `/dashboard-infrastructure/overview` | Existing Home Assistant YAML configuration |

This integration registers only the new `/dashboard-house-v11` custom panel, and only when that route is unowned. It never removes, replaces or injects UI into the existing YAML dashboards. Unload removes only the House fallback that this integration registered itself.

The House cards may navigate to legacy YAML detail views or to autonomous specialized integrations such as ZONT, StarLine, S8 OMNI, HO-SC-8W, Stark, Keenetic, LIDER and water accounting. Those links do not give this repository ownership of the destination.

## Repository-per-panel rule

Every new detailed control panel is developed in its own repository with its own:

- Home Assistant integration and route owner;
- frontend bundle and assets;
- contracts, manifest and tests;
- release history.

No detailed-panel implementation is added here. The House overview stores only explicit navigation URLs to accepted external panels. Shared UI rules may be copied at development time but never become cross-repository runtime dependencies.

See `docs/REPOSITORY_SCOPE.md` for the migration and preservation rules.

## Preserved baseline

The complete pre-split multi-panel state is preserved at commit `c525b30` on branch:

```text
archive/multipanel-0.37.8
```

Existing Home Assistant YAML files are not generated, rewritten or deleted by this repository. They remain the operational baseline while new panels are built and accepted one at a time.

## Pipeline

```text
scrubbed HA registry snapshot
  + House UI contract
  + private verified semantic inventory
  + House manifest
  → deterministic candidate
  → semantic diff and release gate
  → House custom panel
```

Private runtime inventory containing verified `entity_id` bindings stays under `/config/contract_generated_ui/inventory/` and is never committed here. Production entity IDs are not invented.

## Repository structure

- `contracts/house_home.yaml` — public semantic contract for the main House overview.
- `manifests/house_v11_preview.yaml` — the only production panel manifest.
- `navigation/main.yaml` — links from House to independently owned routes.
- `custom_components/contract_generated_ui/` — House integration, renderer and frontend.
- `generator/` — deterministic House rendering, validation, snapshot and release tools.
- `schemas/` — machine-readable source and release schemas.
- `tests/` — House and core safety regression tests.
- `docs/` — architecture and UI rules retained for House development.

## Home Assistant behavior

The integration:

- synchronizes only the public House contract, manifest and navigation links;
- validates the private source tree once per minute outside the event loop;
- captures and downloads scrubbed registry snapshots;
- generates review artifacts under `/config/contract_generated_ui/generated/`;
- serves the autonomous House frontend bundle;
- preserves every existing Lovelace/YAML route.

The generated Lovelace registration snippet is review-only. Because the House is a specialized custom panel, the snippet contains no dashboard registration and is never applied automatically.

## Installation

Add `NikaSir/ha-contract-generated-ui` to HACS as a custom **Integration**, install it, restart Home Assistant, then add **Contract Generated UI** under **Settings → Devices & services**.

For a manual installation, copy `custom_components/contract_generated_ui` to `/config/custom_components/contract_generated_ui` and restart Home Assistant.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

## Safety rules

1. Existing YAML dashboards remain unchanged and independently owned.
2. This repository owns only the new main House route.
3. Detailed panels live in separate repositories.
4. Unknown and unavailable states remain explicit.
5. Production entity IDs come only from verified private inventory.
6. Navigation uses explicit Home Assistant routes, never browser history.
7. No repository is a runtime dependency of another specialized panel.

## License

MIT.
