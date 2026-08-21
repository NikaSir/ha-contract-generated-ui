# Private runtime inventory

Production Home Assistant bindings are intentionally separated from the public repository.

## Public repository

The public repository may contain:

- UI contracts;
- panel manifests;
- schemas;
- generator and validation code;
- synthetic examples and tests.

Contracts and manifests must not contain concrete `entity_id`, `device_id` or `area_id` values.

## Home Assistant runtime

Real bindings live under:

`/config/contract_generated_ui/inventory/`

A production `SemanticInventory` is generated only from a captured `RegistrySnapshot` and explicit verified bindings. It may contain real Home Assistant `entity_id` values and therefore is treated as private runtime configuration.

Do not publish production inventory files to the public GitHub repository.

The public manifest references semantic keys only, for example:

`infrastructure.ups.internet.output_voltage`

The private inventory resolves that semantic key to the actual Home Assistant entity.

## First production slice

The first runtime slice targets `/dashboard-infrastructure` and covers:

- electrical grid;
- UPS Internet;
- UPS Boiler;
- Keenetic Hero 4G+ WAN telemetry.

The associated contracts and manifest are public. The matching `inventory/home.yaml` remains private in Home Assistant.
