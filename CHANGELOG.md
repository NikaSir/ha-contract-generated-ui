# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Initial Architecture-as-Code repository bootstrap.
- Formal directories for contracts, inventory, manifests, schemas, generator and tests.
- Repository validation workflow and Dependabot configuration.
- MIT license.
- Contract Core v1 schemas for `UIContract`, `SemanticInventory` and `PanelManifest`.
- Executable `ha-contract-ui validate` / `python -m generator validate` validation path.
- Architectural guard that rejects concrete Home Assistant binding keys from contracts and manifests.
- Verified-only semantic inventory bindings and explicit unreliable-state safety invariants.
- Regression test suite for contract-core validation.
- Python dependency tracking in Dependabot.
- Home Assistant custom integration shell under `custom_components/contract_generated_ui`.
- Single-entry UI config flow and diagnostic contract-source status sensor.
- Runtime validation of `/config/contract_generated_ui` using packaged Contract Core v1 schemas.
- English and Russian translations for setup, sensor states and registry snapshot capture.
- HACS repository metadata and official Home Assistant Hassfest workflow.
- Regression guard ensuring packaged schemas stay aligned with repository schemas.
- Scrubbed Home Assistant entity-registry capture with deterministic content IDs.
- Atomic `current.json` / `previous.json` snapshot rotation only on factual registry change.
- Explicit verified-inventory builder from snapshot entities and semantic bindings.
- Semantic diff for registry snapshots and semantic inventory, including rebinding detection.
- Disabled-entity guard for verified inventory construction.
- Semantic namespace grammar that cannot be confused with Home Assistant `domain.object_id` entity IDs.
- Deterministic Lovelace Renderer v1 using core Heading, Grid and Tile cards.
- Explicit safe Tile card/icon tap, hold and double-tap action generation.
- Fail-closed service actions and restricted v1 toggle-domain allowlist.
- Deterministic `RenderTrace v1` metadata with source versions, resolved bindings and dashboard SHA-256.
- Reviewable RenderTrace semantics for views, modules, roles, domains and primary actions.
- Deterministic renderer-engine SHA-256 fingerprint in every RenderTrace.
- `RenderDiff v1` classification for manifest, source, view, module, binding, action and renderer changes.
- Critical detection of unexplained canonical dashboard drift.
- Fail-closed `ha-contract-ui gate render` release gate.
- Exact `RenderApproval v1` hash matching with automatic stale-approval rejection.
- Renderer safety, namespace-boundary, reproducibility and release-gate regression tests.
- First production infrastructure contracts for electrical grid, Stark SolarPower UPS and Keenetic WAN failover telemetry.
- Public/private runtime policy that keeps real Home Assistant `SemanticInventory` bindings outside the public repository.
- Home Assistant runtime renderer and **Generate dashboards / Сгенерировать панели** button (`0.2.0`).
- Deterministic candidate generation under `/config/contract_generated_ui/generated/` with generated-file and SHA attributes.
- Official Home Assistant YAML-dashboard registration snippet export (`0.3.0`) without automatic configuration or `.storage` mutation.
- Runtime regression tests for deterministic generation, verified-only bindings, registration snippet shape and dashboard slug safety.
- Renderer v2 Sections layout (`0.4.0`) as a deterministic layer over validated tiles_v1 semantics.
- Module-to-section composition with `max_columns: 4`, explicit non-dense placement and stable section spans.
- Explicit Tile card Sections sizing (`grid_options: columns: 6, rows: 1`) to improve label readability.
- CLI and Home Assistant runtime parity for Sections v2 generation.
- Infrastructure panel manifest `0.2.0` / title `Инфраструктура · v0.2` for the new layout baseline.
