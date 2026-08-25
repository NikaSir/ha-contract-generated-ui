# Contract Generated UI for Home Assistant

Architecture-as-Code toolchain for generating and validating Home Assistant Lovelace dashboards from formal UI contracts and verified Home Assistant inventory.

## Pipeline

`Home Assistant registry snapshot + UI contracts → semantic inventory → panel manifests → deterministic Lovelace YAML → semantic diff → release gate → validation → release`

## Status

The current release line contains Contract Core v1, an installable Home Assistant custom integration, scrubbed entity-registry capture, verified semantic-inventory construction, semantic diff, deterministic Lovelace Renderer v1, a fail-closed semantic release gate, in-Home-Assistant candidate rendering, and safe export of Home Assistant YAML-dashboard registration configuration.

Production contracts and bindings are introduced only from verified Home Assistant project data; fabricated production entity IDs and placeholder dashboard facts are not accepted. Real runtime inventory files containing private Home Assistant bindings stay under `/config/contract_generated_ui/inventory/` and are not committed to the public repository.

## Repository structure

- `contracts/` — formal subsystem and UI contracts.
- `inventory/` — public examples/policy only; real runtime inventory stays private in Home Assistant.
- `manifests/` — concise panel composition and role-to-semantic-key bindings.
- `snapshots/` — scrubbed reviewed Home Assistant registry snapshots only when intentionally committed.
- `generator/` — validation, inventory construction, semantic diff, deterministic renderer and release gate.
- `schemas/` — machine-readable schemas for contracts, inventory, manifests, snapshots, render traces, diffs and approvals.
- `approvals/` — intentionally reviewed exact semantic-change approvals.
- `custom_components/contract_generated_ui/` — Home Assistant custom integration, runtime renderer and packaged schemas.
- `templates/integration-panel-v1/` — copy/adapt reference implementation for integration-owned specialized panels; never a shared runtime dependency.
- `tests/` — contract, integration, snapshot, semantic-diff, rendering and release-gate regression tests.
- `docs/` — architecture, operating, specialized-panel UI and release documentation.

## Contract boundary

The toolchain keeps semantics separate from Home Assistant registry identifiers:

- contracts define roles, state classes, actions, presentation and safety invariants;
- semantic inventory is the only input layer that contains verified `entity_id` bindings;
- manifests bind contract roles to semantic inventory keys, not to entity IDs;
- semantic keys use at least three dot-separated segments such as `infrastructure.router.status`, so they cannot be confused with Home Assistant `domain.object_id` entity IDs;
- `unknown` and `unavailable` remain explicit unreliable states.

See `docs/CONTRACT_CORE_V1.md`.

## Home Assistant custom integration

The integration monitors `/config/contract_generated_ui` and exposes its factual validation state. Validation runs once per minute outside the Home Assistant event loop.

The diagnostic source-status sensor reports:

- `missing` — source directory does not exist;
- `empty` — no supported source documents exist;
- `incomplete` — at least one required source kind is absent;
- `valid` — contracts, inventory and manifests pass validation;
- `invalid` — parsing, schema or binding-boundary validation failed.

### Capture registry snapshot

**Capture registry snapshot / Снять снимок реестра** writes scrubbed registry facts to:

```text
/config/contract_generated_ui/snapshots/current.json
/config/contract_generated_ui/snapshots/previous.json
```

`previous.json` is rotated only when canonical registry facts change. Snapshots exclude unique IDs, device identifiers, config-entry IDs, credentials and device names.

See `docs/SNAPSHOT_PIPELINE.md`.

### Generate dashboards

**Generate dashboards / Сгенерировать панели** is available only when source status is `valid`. It runs file parsing and rendering in the Home Assistant executor and writes candidate artifacts under:

```text
/config/contract_generated_ui/generated/
```

For each manifest it writes deterministic Lovelace YAML plus a sibling RenderTrace JSON. Repeated generation with identical source meaning is byte-stable and reports no change.

The integration does **not** overwrite Home Assistant dashboards or `.storage` files.

Starting with `0.3.0`, generation also exports:

```text
/config/contract_generated_ui/generated/lovelace_configuration_snippet.yaml
```

This is a reviewable snippet using Home Assistant's supported `lovelace: dashboards:` YAML configuration. It must be merged with existing `configuration.yaml`; it is never applied automatically.

Integration-owned specialized panels are intentionally omitted from that snippet. Starting with `0.35.0`, `Дом · v11.0` is registered automatically at `/dashboard-house-v11/home`; it does not require a `lovelace.dashboards` entry.

See `docs/YAML_DASHBOARD_REGISTRATION.md`.

## Integration-owned specialized panels

Specialized applications such as UPS, irrigation, vacuum and network control use a common NikaS mobile shell rather than inventing independent navigation and geometry.

Normative documents:

- `docs/INTEGRATION_DASHBOARD_UI_STANDARD.md` — required app navigation, Header, Device Selector, Bottom Tab Bar and state semantics;
- `docs/NIKAS_INTEGRATION_PANEL_TEMPLATE_V1.md` — shared visual primitives, typography and copy/adapt implementation contract;
- `docs/SPECIALIZED_PANEL_FRONTEND_RELEASE_STANDARD.md` — one self-contained production frontend bundle per integration.

The runnable reference is under `templates/integration-panel-v1/`. It is copied/adapted into an integration repository and must **not** become a runtime dependency on `ha-contract-generated-ui`.

ZONT is a completed handoff: `ha-zont` alone registers and serves `/dashboard-zont`. This repository contains no ZONT panel manifest, frontend bundle or equipment assets. The House heating route may still link to `/dashboard-zont`; that URL is navigation to an external integration-owned panel, not shared ownership.

## Deterministic Lovelace renderer

Renderer v1 resolves explicit manifest role bindings through verified semantic inventory and produces Home Assistant core Heading, Grid and Tile cards.

```bash
ha-contract-ui render manifests/example.yaml .generated/example.yaml
```

The command writes deterministic Lovelace YAML plus a sibling `.meta.json` RenderTrace with source versions, snapshot IDs, resolved bindings, reviewable view/module/role/action semantics, renderer-engine SHA-256 and the SHA-256 of canonical dashboard content.

Interaction safety is explicit: card and icon actions are always written, long-press opens `more-info`, double-tap is disabled, service actions fail closed, and `toggle` is restricted to the v1 allowlist.

See `docs/RENDERER_V1.md`.

## Semantic release gate

A syntactically valid generated dashboard is not automatically releasable.

```bash
ha-contract-ui diff render release/baseline.meta.json .generated/candidate.meta.json
ha-contract-ui gate render release/baseline.meta.json .generated/candidate.meta.json
```

The semantic diff classifies binding reassignments, actions, navigation, layout, source revisions and renderer-engine changes. Any semantic change blocks the gate by default.

A reviewed `RenderApproval v1` is accepted only when its baseline dashboard SHA-256, candidate dashboard SHA-256 and semantic-diff SHA-256 exactly match the candidate under review. Any subsequent change makes the approval stale. Unexplained canonical dashboard drift is classified as critical and blocks release.

See `docs/SEMANTIC_RELEASE_GATE.md` and `docs/RELEASES.md`.

## Installation

Add `NikaSir/ha-contract-generated-ui` to HACS as a custom repository of type **Integration**, install **Contract Generated UI**, restart Home Assistant, then add it through **Settings → Devices & services → Add integration → Contract Generated UI**.

For manual installation, copy `custom_components/contract_generated_ui` to `/config/custom_components/contract_generated_ui` and restart Home Assistant.

The integration is single-instance and requires no credentials or cloud service.

## Development validation

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

Home Assistant metadata and translation structure are additionally checked by the official Hassfest workflow. Repository CI also syntax-checks the shared integration-panel reference and rejects browser-history Back or runtime ES-module dependencies in that reference.

## Design principles

1. **Source data is factual.** `unknown` and `unavailable` are not silently converted to normal states.
2. **Contracts are explicit.** UI behavior, entity semantics, interaction and navigation are defined before rendering.
3. **Generated output is reproducible.** Manual changes to generated dashboards are treated as drift.
4. **Semantic diff precedes release.** Meaningful changes are reviewable independently of formatting noise.
5. **Release is fail-closed.** Unreviewed semantic changes and unexplained renderer drift block the candidate.
6. **Home Assistant entity IDs are never invented.** Generation consumes verified inventory.
7. **Private runtime bindings stay private.** Public contracts/manifests do not reveal the Home Assistant entity catalog.
8. **Deployment uses supported Home Assistant mechanisms.** The integration does not mutate Lovelace `.storage` through private APIs.
9. **Specialized applications share one shell language.** Domain panels customize content, not global mobile navigation mechanics.
10. **Specialized production frontends are autonomous.** Shared source patterns never become cross-repository runtime dependencies.

## License

MIT.
