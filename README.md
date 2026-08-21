# Contract Generated UI for Home Assistant

Architecture-as-Code toolchain for generating and validating Home Assistant Lovelace dashboards from formal UI contracts.

## Pipeline

`UI contracts → Home Assistant registry snapshot → semantic inventory → panel manifests → Lovelace YAML generation → semantic diff → validation → release`

## Status

Infrastructure/bootstrap stage. The repository intentionally does not contain placeholder dashboard logic or fabricated Home Assistant entities. Production contracts and generator behavior will be imported only from verified project data.

## Repository structure

- `contracts/` — formal subsystem and UI contracts.
- `inventory/` — normalized semantic inventory derived from Home Assistant state/registry snapshots.
- `manifests/` — concise declarations describing panel composition.
- `generator/` — generator implementation and rendering rules.
- `schemas/` — machine-readable schemas for contracts, inventory and manifests.
- `tests/` — contract, semantic-diff and generation regression tests.
- `docs/` — architecture, release and operating documentation.

## Design principles

1. **Source data is factual.** `unknown` and `unavailable` are not silently converted to normal states.
2. **Contracts are explicit.** UI behavior, entity semantics and navigation are defined before rendering.
3. **Generated output is reproducible.** Manual changes to generated dashboards are treated as drift.
4. **Semantic diff precedes release.** Meaningful UI changes must be reviewable independently of formatting noise.
5. **Home Assistant entity IDs are never invented.** Generation consumes verified inventory.
6. **Secrets stay outside Git.** Registry snapshots and diagnostics must be scrubbed before commit.

## License

MIT.
