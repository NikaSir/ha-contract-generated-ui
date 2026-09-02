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

## Runtime ownership boundary

The installed integration is a registry and shared-asset service. It does not register
the main House overview or any other dashboard. The accepted House runtime belongs to
`ha-nikas-house`; every other specialized panel belongs to its dedicated repository.

The contract/generator pipeline remains in this repository as reviewed engineering
history and as an offline validation toolkit. It is not invoked by a Home Assistant
entity and cannot apply or register generated Lovelace content.

This rule is formally recorded in [ADR-001: Integration-owned specialized dashboards](ADR-001-INTEGRATION-OWNED-DASHBOARDS.md).

## Non-negotiable rules

- `unknown` / `unavailable` are distinct from normal/healthy states.
- Entity IDs come only from verified inventory.
- Generated dashboard files are not hand-edited in production workflow.
- Controls must preserve subsystem safety constraints defined by their contracts.
- A panel manifest is concise; reusable behavior belongs in contract modules and generator components.
- Input snapshots committed to Git must be scrubbed of secrets and private data.
- Detailed device/domain UX has one canonical owner; the central generator must not silently duplicate a specialized integration's full interaction model.
- Cross-dashboard links must target stable declared routes rather than invented paths.

## Current stage

Runtime version 0.39.0 retains registry capture/download, diagnostics, source
validation and shared static assets. Historical contracts, manifests, renderers and
frontend files remain available for audit, while runtime tests ensure no panel module
is registered or injected.
