# Private runtime inventory

Production Home Assistant bindings are intentionally separated from public
repositories.

## Public repositories

Public repositories may contain UI contracts, panel manifests, schemas, generator and
validation code, and synthetic examples. Contracts, manifests and navigation sources
must not contain concrete `entity_id`, `device_id` or `area_id` values.

Panel-specific public sources belong to the repository that owns the panel. The
central `ha-contract-generated-ui` repository contains common schemas, standards,
tools and the route registry only.

## Home Assistant runtime

Real bindings may live under:

`/config/contract_generated_ui/inventory/`

A production `SemanticInventory` is generated only from a captured
`RegistrySnapshot` and explicit verified bindings. It may contain real Home
Assistant entity IDs and is therefore private runtime configuration.

Do not publish production inventory files. Do not copy another panel owner's private
bindings into the central repository or into unrelated panel repositories.

## Ownership and migration

Semantic keys are resolved only within the owning panel's reviewed workflow. Shared
navigation records routes, not entity bindings. Moving a panel between repositories
must not create a runtime import or inventory dependency on the previous owner.

The common integration preserves existing user-owned inventory, snapshots and
generated history during upgrades.
