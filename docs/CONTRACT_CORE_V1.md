# Contract core v1

The first executable layer of `CONTRACT_GENERATED_UI` separates UI semantics from concrete Home Assistant registry bindings.

## Data flow

`UIContract → SemanticInventory → PanelManifest → generator`

The three document kinds are independently schema-validated before generation.

## UIContract

API version: `nikas.home-assistant/ui-contract/v1`

A contract defines semantic roles, normal/event/unreliable state classes, permitted actions, renderer-facing requirements and safety invariants. It must not contain concrete Home Assistant registry identifiers.

Required safety invariants:

- `unknown_is_unreliable: true`
- `unavailable_is_unreliable: true`
- `invent_entity_ids: false`

Concrete `entity_id`, `device_id` and `area_id` keys are rejected recursively in contracts.

## SemanticInventory

API version: `nikas.home-assistant/semantic-inventory/v1`

The inventory is the only v1 input layer allowed to bind semantic roles to concrete Home Assistant entity IDs. Every binding must be marked `verification: verified`, and inventory metadata must state that the source was scrubbed before being committed.

The inventory is factual input. It does not convert `unknown` or `unavailable` into healthy states.

## PanelManifest

API version: `nikas.home-assistant/panel-manifest/v1`

A manifest declares dashboard paths, views, ordering and references to contract modules. It stays intentionally short and contains no concrete Home Assistant registry bindings.

Concrete `entity_id`, `device_id` and `area_id` keys are rejected recursively in manifests.

## Validation

From the repository root:

```bash
python -m pip install -e '.[test]'
python -m generator validate .
python -m pytest -q
```

The installed console entry point is equivalent:

```bash
ha-contract-ui validate .
```

## Scope of v1

Contract core v1 validates document structure and architectural boundaries. It does not yet implement Lovelace rendering, Home Assistant registry snapshot collection or semantic diff. Those layers must consume these validated inputs rather than bypassing them.
