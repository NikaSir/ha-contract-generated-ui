# Contract Generated UI for Home Assistant

Architecture-as-Code toolchain for generating and validating Home Assistant Lovelace dashboards from formal UI contracts.

## Pipeline

`UI contracts → Home Assistant registry snapshot → semantic inventory → panel manifests → Lovelace YAML generation → semantic diff → validation → release`

## Status

Contract core v1 is under active development. The repository now has machine-readable schemas and an executable validator for UI contracts, semantic inventory and panel manifests. Production contracts and bindings are still introduced only from verified Home Assistant NikaS project data; placeholder dashboard logic and fabricated production entity IDs are not accepted.

## Repository structure

- `contracts/` — formal subsystem and UI contracts.
- `inventory/` — normalized semantic inventory derived from Home Assistant state/registry snapshots.
- `manifests/` — concise declarations describing panel composition.
- `generator/` — validation and deterministic generator implementation.
- `schemas/` — machine-readable schemas for contracts, inventory and manifests.
- `tests/` — contract, semantic-diff and generation regression tests.
- `docs/` — architecture, contract-core, release and operating documentation.

## Contract core

The first executable layer enforces a hard separation between semantics and Home Assistant bindings:

- contracts define roles, state classes, actions and safety invariants;
- semantic inventory is the only input layer allowed to contain verified `entity_id` bindings;
- manifests compose dashboards and views by contract reference, not by direct entity binding;
- `unknown` and `unavailable` must remain explicit unreliable states.

See `docs/CONTRACT_CORE_V1.md` for the v1 format and validation commands.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

## Design principles

1. **Source data is factual.** `unknown` and `unavailable` are not silently converted to normal states.
2. **Contracts are explicit.** UI behavior, entity semantics and navigation are defined before rendering.
3. **Generated output is reproducible.** Manual changes to generated dashboards are treated as drift.
4. **Semantic diff precedes release.** Meaningful UI changes must be reviewable independently of formatting noise.
5. **Home Assistant entity IDs are never invented.** Generation consumes verified inventory.
6. **Secrets stay outside Git.** Registry snapshots and diagnostics must be scrubbed before commit.

## License

MIT.
