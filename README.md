# Contract Generated UI service for Home Assistant

`NikaSir/ha-contract-generated-ui` is the retained NikaS service integration for
scrubbed Home Assistant registry snapshots, reviewed source records and shared static
assets. It no longer owns, generates or registers a runtime dashboard.

The installed domain and integration name remain `contract_generated_ui` and
**Contract Generated UI** for upgrade compatibility.

## Runtime scope

The integration:

- captures a scrubbed entity/device/area/floor/label registry snapshot;
- rotates `current.json` and `previous.json` only when registry facts change;
- exposes the current snapshot through an authenticated download URL;
- validates the preserved source tree once per minute;
- serves the retained local photo/assets directory;
- never registers, replaces, unloads or generates a Home Assistant dashboard.

The former `Дом · новая` routes `/dashboard-house-v11/home` and
`/dashboard-house-v12/home` are no longer registered by this integration. The accepted
main House panel is owned exclusively by `NikaSir/ha-nikas-house`.

## Preserved data

An update or uninstall must not delete private data already stored under
`/config/contract_generated_ui/`, including:

- `inventory/`;
- `snapshots/`;
- `generated/` history;
- reviewed contracts, manifests and navigation sources;
- user-supplied photos or other retained assets.

The complete pre-split multi-panel state remains preserved at commit `c525b30` on
branch `archive/multipanel-0.37.8`.

The final standalone House implementation previously shipped here remains available
in Git history at commit `f5bff81`; its source and tests may remain for audit purposes,
but no House module is loaded by the integration at runtime.

## Repository structure

- `custom_components/contract_generated_ui/registry_snapshot.py` — scrubbed registry capture;
- `custom_components/contract_generated_ui/snapshot_download.py` — authenticated download;
- `custom_components/contract_generated_ui/frontend/assets/` — retained shared assets;
- `custom_components/contract_generated_ui/brand/` — integration icon;
- `templates/shell_v2/` — canonical build-time shell source copied by owning panel repositories;
- `contracts/`, `manifests/`, `navigation/`, `generator/` — preserved reviewed engineering history;
- `schemas/` and `tests/` — validation and regression checks.

## Installation

Add `NikaSir/ha-contract-generated-ui` to HACS as a custom **Integration**, install it,
restart Home Assistant, then add **Contract Generated UI** under
**Settings → Devices & services**.

For a manual installation, copy `custom_components/contract_generated_ui` to
`/config/custom_components/contract_generated_ui` and restart Home Assistant.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## Safety rules

1. No Lovelace or custom-panel route is registered by this integration.
2. Existing YAML dashboards and specialized integration panels remain independently owned.
3. Private snapshots, inventory and generated history are never removed automatically.
4. Snapshots contain only scrubbed facts; raw Home Assistant storage is not exported.
5. The main House panel belongs only to `NikaSir/ha-nikas-house`.

## License

MIT.
