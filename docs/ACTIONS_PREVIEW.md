# Actions preview

`actions_home_v1` is the staged renderer for the Home Assistant NikaS **Действия** surface.

## Role

The central Actions dashboard is intentionally shallow. It is responsible for:

- safe, frequent quick operations;
- navigation into canonical integration-owned dashboards;
- keeping high-risk or domain-specific workflows out of the house-wide UI.

It follows ADR-001: irrigation, S8 OMNI, Keenetic and UPS deep interaction models belong to their owning integrations.

## Mobile target

Primary target: **iPhone Pro Max, portrait**.

Layout rules:

- maximum two Sections columns;
- direct `toggle` actions: half-width (`6/12`);
- `more_info`: half-width (`6/12`);
- deep `navigate`: full-width (`12/12`);
- unsupported/service-style actions: fail closed.

## Safety

The renderer does not create new action semantics. It consumes the already validated `UIContract` action for each resolved semantic role.

Therefore:

- `entity_id` still comes only from verified `SemanticInventory`;
- toggle-domain safety remains enforced by the base renderer (`light`, `switch`, `input_boolean` only);
- navigation targets must be absolute paths;
- raw Tuya/RCI/SNMP writes are not an Actions-panel feature;
- gates/covers or other consequential controls are not enabled merely because a UI card could be drawn.

## Staged rollout

`0.10.0` adds renderer capability only. It does not replace the current `/dashboard-actions` automatically.

A private preview manifest/inventory is generated separately from the current Home Assistant registry and first reviewed on iPhone. Production replacement requires explicit acceptance.
