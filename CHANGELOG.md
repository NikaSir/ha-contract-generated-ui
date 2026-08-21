# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Initial Architecture-as-Code repository bootstrap.
- Formal directories for contracts, inventory, manifests, schemas, generator and tests.
- Repository validation workflow and Dependabot configuration.
- MIT license.
- Contract core v1 schemas for `UIContract`, `SemanticInventory` and `PanelManifest`.
- Executable `ha-contract-ui validate` / `python -m generator validate` validation path.
- Architectural guard that rejects concrete Home Assistant binding keys from contracts and manifests.
- Verified-only semantic inventory bindings and explicit unreliable-state safety invariants.
- Regression test suite for contract-core validation.
- Python dependency tracking in Dependabot.
- Home Assistant custom integration shell under `custom_components/contract_generated_ui`.
- Single-entry UI config flow and diagnostic contract-source status sensor.
- Runtime validation of `/config/contract_generated_ui` using packaged Contract Core v1 schemas.
- English and Russian translations for setup and sensor states.
- HACS repository metadata and official Home Assistant hassfest workflow.
- Regression guard ensuring packaged schemas stay aligned with repository schemas.
