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
