# Contract Generated UI for Home Assistant

Architecture-as-Code toolchain for generating and validating Home Assistant Lovelace dashboards from formal UI contracts and verified Home Assistant inventory.

## Pipeline

`Home Assistant registry snapshot + UI contracts → semantic inventory → panel manifests → deterministic Lovelace YAML → semantic diff → validation → release`

## Status

The current development stack contains Contract Core v1, an installable Home Assistant custom-integration shell, scrubbed entity-registry capture, verified semantic-inventory construction, semantic diff and deterministic Lovelace Renderer v1. Production contracts and bindings are introduced only from verified Home Assistant NikaS project data; fabricated production entity IDs and placeholder dashboard facts are not accepted.

All functional changes are developed through stacked draft pull requests. `main` remains the release baseline until the stack is reviewed.

## Repository structure

- `contracts/` — formal subsystem and UI contracts.
- `inventory/` — normalized semantic inventory derived from verified snapshots.
- `manifests/` — concise panel composition and role-to-semantic-key bindings.
- `snapshots/` — scrubbed reviewed Home Assistant registry snapshots when intentionally committed.
- `generator/` — validation, inventory construction, semantic diff and deterministic renderer.
- `schemas/` — machine-readable schemas for contracts, inventory, manifests, snapshots and render traces.
- `custom_components/contract_generated_ui/` — Home Assistant custom integration and packaged schemas.
- `tests/` — contract, integration, snapshot, semantic-diff and rendering regression tests.
- `docs/` — architecture, operating and release documentation.

## Contract boundary

The toolchain keeps semantics separate from Home Assistant registry identifiers:

- contracts define roles, state classes, actions, presentation and safety invariants;
- semantic inventory is the only input layer that contains verified `entity_id` bindings;
- manifests bind contract roles to semantic inventory keys, not to entity IDs;
- semantic keys use at least three dot-separated segments such as `infrastructure.router.status`, so they cannot be confused with Home Assistant `domain.object_id` entity IDs;
- `unknown` and `unavailable` remain explicit unreliable states.

See `docs/CONTRACT_CORE_V1.md`.

## Home Assistant custom integration

The custom integration monitors `/config/contract_generated_ui` and exposes its factual validation state. Validation runs once per minute outside the Home Assistant event loop.

The diagnostic source-status sensor reports:

- `missing` — source directory does not exist;
- `empty` — no supported source documents exist;
- `incomplete` — at least one required source kind is absent;
- `valid` — contracts, inventory and manifests pass validation;
- `invalid` — parsing, schema or binding-boundary validation failed.

The integration also provides **Capture registry snapshot**. It writes scrubbed registry facts to:

```text
/config/contract_generated_ui/snapshots/current.json
/config/contract_generated_ui/snapshots/previous.json
```

`previous.json` is rotated only when canonical registry facts change. Snapshots exclude unique IDs, device identifiers, config-entry IDs, credentials and device names.

See `docs/SNAPSHOT_PIPELINE.md`.

## Deterministic Lovelace renderer

Renderer v1 resolves explicit manifest role bindings through verified semantic inventory and produces Home Assistant core Heading, Grid and Tile cards.

```bash
ha-contract-ui render manifests/example.yaml .generated/example.yaml
```

The command writes deterministic Lovelace YAML plus a sibling `.meta.json` RenderTrace with source versions, snapshot IDs, resolved bindings and the SHA-256 of canonical dashboard content.

Interaction safety is explicit: card and icon actions are always written, long-press opens `more-info`, double-tap is disabled, service actions fail closed, and `toggle` is restricted to the v1 allowlist.

See `docs/RENDERER_V1.md`.

## Installation

The integration source lives in `custom_components/contract_generated_ui`. After the first tagged release it is intended for HACS installation as a custom repository. For manual installation, copy that directory to `/config/custom_components/contract_generated_ui`, restart Home Assistant, then go to **Settings → Devices & services → Add integration → Contract Generated UI**.

The integration is single-instance and requires no credentials or cloud service.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

Home Assistant metadata and translation structure are additionally checked by the official Hassfest workflow.

## Design principles

1. **Source data is factual.** `unknown` and `unavailable` are not silently converted to normal states.
2. **Contracts are explicit.** UI behavior, entity semantics, interaction and navigation are defined before rendering.
3. **Generated output is reproducible.** Manual changes to generated dashboards are treated as drift.
4. **Semantic diff precedes release.** Meaningful changes are reviewable independently of formatting noise.
5. **Home Assistant entity IDs are never invented.** Generation consumes verified inventory.
6. **Secrets stay outside Git.** Snapshots and diagnostics are scrubbed before intentional commit.

## License

MIT.
