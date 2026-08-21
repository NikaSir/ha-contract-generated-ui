# Contract Generated UI for Home Assistant

Architecture-as-Code toolchain for generating and validating Home Assistant Lovelace dashboards from formal UI contracts.

## Pipeline

`UI contracts → Home Assistant registry snapshot → semantic inventory → panel manifests → Lovelace YAML generation → semantic diff → validation → release`

## Status

Contract core v1 and the first Home Assistant custom-integration shell are under active development. The repository has machine-readable schemas, an executable validator and an installable `custom_components/contract_generated_ui` layer. Production contracts and bindings are still introduced only from verified Home Assistant NikaS project data; placeholder dashboard logic and fabricated production entity IDs are not accepted.

## Repository structure

- `contracts/` — formal subsystem and UI contracts.
- `inventory/` — normalized semantic inventory derived from Home Assistant state/registry snapshots.
- `manifests/` — concise declarations describing panel composition.
- `generator/` — validation and deterministic generator implementation.
- `schemas/` — machine-readable schemas for contracts, inventory and manifests.
- `custom_components/contract_generated_ui/` — Home Assistant custom integration and packaged schemas.
- `tests/` — contract, integration, semantic-diff and generation regression tests.
- `docs/` — architecture, contract-core, release and operating documentation.

## Contract core

The first executable layer enforces a hard separation between semantics and Home Assistant bindings:

- contracts define roles, state classes, actions and safety invariants;
- semantic inventory is the only input layer allowed to contain verified `entity_id` bindings;
- manifests compose dashboards and views by contract reference, not by direct entity binding;
- `unknown` and `unavailable` must remain explicit unreliable states.

See `docs/CONTRACT_CORE_V1.md` for the v1 format and validation commands.

## Home Assistant custom integration

The custom integration is intentionally narrow in its first version. It validates contract sources and exposes their factual state; it does **not** write Lovelace configuration yet.

### Source directory

The integration reads:

```text
/config/contract_generated_ui/
├── contracts/
├── inventory/
└── manifests/
```

Validation runs once per minute outside the Home Assistant event loop. The diagnostic enum sensor reports one of:

- `missing` — `/config/contract_generated_ui` does not exist;
- `empty` — the directory exists but contains no supported contract documents;
- `incomplete` — valid documents exist, but at least one required source kind is missing;
- `valid` — contracts, inventory and manifests are present and pass Contract Core v1 validation;
- `invalid` — parsing, schema or binding-boundary validation failed.

The sensor exposes scrubbed counts and up to ten validation issues as attributes. A validation problem is data, not a healthy state.

### Installation

The integration source lives in `custom_components/contract_generated_ui`. After the first tagged release it is intended for HACS installation as a custom repository. For manual installation, copy that directory to `/config/custom_components/contract_generated_ui`, restart Home Assistant, then go to **Settings → Devices & services → Add integration → Contract Generated UI**.

The integration is single-instance and requires no credentials or cloud service.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

Home Assistant-specific metadata is additionally checked with the official `home-assistant/actions/hassfest` workflow.

## Design principles

1. **Source data is factual.** `unknown` and `unavailable` are not silently converted to normal states.
2. **Contracts are explicit.** UI behavior, entity semantics and navigation are defined before rendering.
3. **Generated output is reproducible.** Manual changes to generated dashboards are treated as drift.
4. **Semantic diff precedes release.** Meaningful UI changes must be reviewable independently of formatting noise.
5. **Home Assistant entity IDs are never invented.** Generation consumes verified inventory.
6. **Secrets stay outside Git.** Registry snapshots and diagnostics must be scrubbed before commit.

## License

MIT.
