# Architecture

## CONTRACT_GENERATED_UI

The project treats Home Assistant dashboards as generated artifacts derived from explicit contracts and verified Home Assistant inventory.

### Stages

1. **Registry snapshot** — collect the factual Home Assistant entity/device/area registry state required by UI generation.
2. **Semantic inventory** — normalize source entities into stable semantic roles without changing their factual state.
3. **UI contracts** — define subsystem behavior, status semantics, actions, navigation, visibility and failure handling.
4. **Panel manifests** — declare which contract modules compose each dashboard/view.
5. **Generation** — render deterministic Lovelace YAML from contracts, inventory and manifests.
6. **Semantic diff** — compare meaning (entities, actions, navigation, visibility, safety behavior), not only YAML formatting.
7. **Validation** — reject unknown entity references, contract/schema violations and unsafe state handling.
8. **Release** — publish only validated generated output with traceable inputs.

## Non-negotiable rules

- `unknown` / `unavailable` are distinct from normal/healthy states.
- Entity IDs come only from verified inventory.
- Generated dashboard files are not hand-edited in production workflow.
- Controls must preserve subsystem safety constraints defined by their contracts.
- A panel manifest is concise; reusable behavior belongs in contract modules and generator components.
- Input snapshots committed to Git must be scrubbed of secrets and private data.

## Current stage

Repository bootstrap. The next milestone is to formalize the first real contract and inventory schema from the existing Home Assistant NikaS UI architecture before implementing production generation.
