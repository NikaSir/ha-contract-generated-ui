# Architecture

## Common contract layer

The repository provides shared Architecture-as-Code primitives for NikaS Home
Assistant interfaces:

1. **Registry snapshot** — scrubbed entity, device, area, floor and label facts.
2. **Semantic inventory** — explicit private bindings from facts to stable roles.
3. **UI contracts** — subsystem behavior, states, actions and safety semantics.
4. **Panel manifests** — panel composition declared by an owning repository.
5. **Deterministic rendering** — a panel-neutral offline reference renderer.
6. **Semantic diff and release gates** — meaning-level review of generated output.
7. **Shared standards** — navigation, shell, UI and publication contracts.
8. **Route registry** — canonical cross-repository destinations and safe returns.

## Runtime ownership boundary

The installed integration provides registry capture/download, diagnostics, generic
source validation and common route-registry synchronization. It does not register a
dashboard, inject frontend code, serve panel assets or render Lovelace at runtime.

Every panel implementation is built, tested and released by its dedicated repository.
The House runtime belongs to `NikaSir/ha-nikas-house`; the common repository only
records its public route.

The historical ownership transition is recorded in
[ADR-001](ADR-001-INTEGRATION-OWNED-DASHBOARDS.md). Superseded implementations remain
recoverable from Git history and the `archive/multipanel-0.37.8` branch.

## Non-negotiable rules

- `unknown` and `unavailable` remain distinct from healthy states.
- Concrete Home Assistant IDs come only from verified private inventory.
- Common contracts and navigation must not contain concrete bindings.
- Generated dashboard files are reviewed and released by their owning repository.
- A panel's controls preserve the safety constraints in its contracts.
- Input snapshots committed to Git are scrubbed of secrets and private data.
- A detailed device/domain experience has one canonical owner.
- Cross-dashboard links use stable routes from `navigation/main.yaml`.
- The common integration never creates a runtime dependency between panel owners.

## Current stage

Runtime version 0.40.0 enforces the common-only boundary. Historical House contracts,
manifests, renderers, frontend files, assets and tests are no longer shipped.
