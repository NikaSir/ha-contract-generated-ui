# Snapshot pipeline

`CONTRACT_GENERATED_UI` now supports a factual registry-snapshot stage before semantic inventory.

## Home Assistant capture

Press **Capture registry snapshot** in the integration. Home Assistant writes `contract_generated_ui/snapshots/current.json` and rotates the prior changed snapshot to `previous.json`.

The snapshot excludes Home Assistant unique IDs and device identifiers. Its `snapshot_id` is derived from canonical scrubbed entity facts, so capture time alone does not create drift.

## CLI

Validate a snapshot:

`ha-contract-ui snapshot validate snapshots/current.json`

Build inventory only from explicit verified bindings:

`ha-contract-ui inventory build snapshots/current.json inventory/home.yaml --bind access.garden_door=binary_sensor.example_door`

Compare registry facts:

`ha-contract-ui diff snapshot snapshots/previous.json snapshots/current.json`

Compare semantic bindings:

`ha-contract-ui diff inventory inventory/before.yaml inventory/after.yaml`

`--json` emits machine-readable changes. `--check` returns exit code 2 when valid inputs contain semantic changes.
