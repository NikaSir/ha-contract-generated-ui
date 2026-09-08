# NikaS Contract Generated UI

`NikaSir/ha-contract-generated-ui` is the shared NikaS contract and registry
repository. It provides scrubbed Home Assistant registry snapshots, the canonical
route registry, common schemas, UI standards and offline validation tooling. It owns
no runtime dashboard and ships no panel frontend.

The installed domain and integration name remain `contract_generated_ui` and
**NikaS Contract Generated UI** for upgrade compatibility.

## Runtime scope

The integration:

- captures scrubbed entity, device, area, floor and label registry snapshots;
- rotates `current.json` and `previous.json` only when registry facts change;
- exposes the current snapshot through an authenticated download URL;
- validates user-provided contract sources under
  `/config/contract_generated_ui/`;
- synchronizes the canonical common navigation registry;
- never registers, replaces, unloads or generates a Home Assistant dashboard;
- serves no panel JavaScript, artwork or other panel-owned asset.

The accepted main House panel is owned exclusively by
`NikaSir/ha-nikas-house`. Every other panel remains in its dedicated repository.

## Data preservation

Updates and uninstall must not delete user-owned data under
`/config/contract_generated_ui/`, including:

- `inventory/`;
- `snapshots/`;
- `generated/` history;
- user-supplied contracts, manifests, navigation files and assets.

Version 0.40 stops bundling and synchronizing the historical House contract and
manifest. Existing copies in a user's configuration are left untouched.

The complete pre-split multi-panel state remains preserved at commit `c525b30` on
branch `archive/multipanel-0.37.8`. The final standalone House implementation
previously shipped here remains available in Git history at commit `f5bff81`.

## Repository structure

- `custom_components/contract_generated_ui/registry_snapshot.py` — scrubbed registry capture;
- `custom_components/contract_generated_ui/snapshot_download.py` — authenticated download;
- `navigation/main.yaml` — canonical cross-repository route registry;
- `templates/shell_v2/` — canonical build-time shell source copied by panel owners;
- `schemas/` — common Architecture-as-Code schemas;
- `generator/` — panel-neutral offline validation, rendering and semantic-diff tools;
- `docs/` — shared NikaS UI and delivery standards;
- `deployments/repository-contracts/` — factual repository inspection profiles;
- `tests/` — common service and contract-toolkit regression checks.

The `contracts/` and `manifests/` directories intentionally contain guidance
only. Production panel definitions belong to their owning repositories.

## Installation

Add `NikaSir/ha-contract-generated-ui` to HACS as a custom **Integration**,
install it, restart Home Assistant, then add **NikaS Contract Generated UI** under
**Settings → Devices & services**.

For a manual installation, copy `custom_components/contract_generated_ui` to
`/config/custom_components/contract_generated_ui` and restart Home Assistant.

## Canonical NikaS standards

[NikaS UI Standard v2.2](docs/NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md) defines the
mandatory shell and data-truth baseline. The
[Engineering Knowledge Base](docs/NIKAS_ENGINEERING_KNOWLEDGE_BASE.md) records the
associated experience and failure modes.

The [Refresh Action Contract v1.0](docs/NIKAS_REFRESH_ACTION_CONTRACT.md) is a
required companion for panels with a refresh action. Each owning repository must
provide its own production tests and browser/device acceptance evidence.

The [Panel Lifecycle Contract v1.0](docs/NIKAS_PANEL_LIFECYCLE_CONTRACT.md) is
required for every owned panel route. Device or cloud availability may change panel
content, but never determines whether the route exists.

The [NikaS Repository Contract v1.0](docs/NIKAS_REPOSITORY_CONTRACT.md) defines
factual delivery, data-quality, command-confirmation, lifecycle and publication
evidence across the repository fleet. Its schema, inspector and pinned profiles are
development tooling; a valid profile is not product certification.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

The aggregate `validate` job requires repository checks, HACS, Hassfest and the
contract-toolkit checks to pass. Manual fleet inspection reports product compliance
separately.

## Safety rules

1. This integration owns no Lovelace or custom-panel route.
2. Panel implementations, assets, manifests and runtime tests live with their owners.
3. User-owned snapshots, inventory and generated history are never removed automatically.
4. Snapshots contain scrubbed facts only; raw Home Assistant storage is not exported.
5. Cross-repository navigation uses only routes declared in `navigation/main.yaml`.

## License

MIT.
