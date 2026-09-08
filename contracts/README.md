# Contracts

This directory is intentionally free of panel-specific contracts.

Shared contract structure is defined by `schemas/contract.schema.json`. Each runtime
panel keeps its concrete public contracts in the repository that owns, tests and
releases that panel. Concrete Home Assistant bindings remain private inventory.
