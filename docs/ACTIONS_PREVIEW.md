# Actions main-panel release candidate

`actions_home_v1` is the renderer for the Home Assistant NikaS **Действия** central surface.

## Role

The central Actions dashboard is intentionally shallow. It is responsible for:

- safe, frequent quick operations;
- factual status immediately before a consequential action;
- navigation into canonical integration-owned subsystem panels;
- keeping high-risk or domain-specific workflows out of the house-wide UI.

Deep interaction models remain owned by their dedicated integrations and repositories.

## Mobile target

Primary target: **iPhone Pro Max, portrait**.

Layout rules:

- maximum two Sections columns;
- generic `toggle` actions: half-width (`6/12`);
- generic `more_info`: half-width (`6/12`);
- generic deep `navigate`: full-width (`12/12`);
- unsupported contract action kinds, including generic service actions: fail closed.

The complete v11 main Actions manifest uses three top-level sections:

1. `Ворота и доступ`;
2. `Уборка`;
3. `Полив`.

## Safety

The base renderer consumes only validated `UIContract` action semantics. The main-panel specialization adds exactly two fixed S8 OMNI quick operations after the semantic layer has resolved the verified `vacuum.*` entity:

- `vacuum.start` — `Начать уборку`;
- `vacuum.return_to_base` — `На базу`.

Both commands require an explicit confirmation dialog. The renderer contains a strict allowlist and rejects any other vacuum service name. This is not a generic service-action mechanism.

Additional safety rules:

- `entity_id` for factual data still comes only from verified `SemanticInventory`;
- sectional-gate position is displayed only from the physical contact sensor;
- cover state is never treated as physical position confirmation;
- swing-gate position is explicitly shown as `Физический датчик не установлен`;
- ROXIMO cover controls are absent from the working main Actions panel because the controller devices are retired from active operation;
- raw Tuya/RCI/SNMP writes are not an Actions-panel feature;
- irrigation is a navigation entry to `/dashboard-irrigation` until a current verified central quick-action contract is accepted;
- S8 OMNI details open the integration-owned `/dashboard-s8-omni` application.

## v11 complete-set RC

Contract Generated UI `0.29.0` moves Actions from renderer-only staging to the generated main-panel set at `/dashboard-actions`.

The release-candidate set is evaluated together:

- `Дом` — `/dashboard-house-v11/home`;
- `Действия` — `/dashboard-actions/home`;
- `Инфраструктура` — `/dashboard-infrastructure/overview`.

Production cut-over of the House route remains a separate acceptance gate after the three-panel mobile test.
