# Device Availability Technical Panel Design

**Date:** 2026-09-14  
**Status:** Approved for implementation  
**Owner:** `NikaSir/ha-contract-generated-ui`

## Purpose

Add a NikaS technical panel named **Доступность устройств**. The panel gives a
single operational view of monitored Home Assistant devices and uses the installed
Entity Availability integration as its monitoring engine and history store.

The panel is diagnostic. Entity selection, cooldowns, staleness thresholds, battery
mapping, signal mapping and suppression policy remain configured in Entity
Availability.

## Repository boundary

`ha-contract-generated-ui` currently declares that it owns no runtime dashboard.
This decision is revised narrowly: the repository may own and register one technical
route for availability diagnostics. It still must not own or register House, Rooms,
Actions, Infrastructure or device-specific control panels.

The route is registered for the lifetime of this integration's config entry and is
removed only when this integration unloads a route that it registered itself.

## Dependency model

Entity Availability is an optional runtime dependency. The integration must load and
the route must remain available when Entity Availability is missing, starting or
temporarily unavailable. In that state, the panel displays a clear setup state with a
link to Home Assistant integrations.

The panel discovers Entity Availability groups from their summary entities rather
than from private `.storage` files. It reads public Home Assistant state objects and
attributes exposed by the integration. The implementation does not import or copy
Entity Availability code.

Compatibility is based on the entities exposed by version 0.5.3 currently installed
by the user. Missing optional sensors must reduce detail without breaking the page.

## Route and navigation

- Route: `/dashboard-device-availability`
- Title: `Доступность устройств`
- Header title: `Доступность устройств`
- Header subtitle: UI version
- Header click: safe return to the built-in Home Assistant overview at
  `/home/overview`
- Canonical navigation registry: add a specialized route entry owned by this
  integration with `parent_route` and `safe_return_route` set to
  `/home/overview`.

The panel follows NikaS UI Standard v2.2: fixed header and footer, safe-area insets,
one scrollable work area, no horizontal scrolling at 100%, work-area zoom only,
pinch-to-zoom and two-finger double-tap reset. Telemetry updates patch existing DOM
nodes and must not rebuild the panel shell.

## Information architecture

### Summary

The first view answers whether attention is required. It contains:

- total monitored entities;
- online, offline, stale, low-battery and poor-signal counts;
- group cards sorted with affected groups first;
- recently offline and recently recovered lists when available;
- a black `Обновить` button with progress, success and failure feedback.

The aggregate status is `Есть проблемы` when any essential entity is offline, stale,
low on battery or has poor signal. Otherwise it is `Всё доступно`. Non-essential and
suppressed entities remain visible in detail but do not raise the aggregate problem
status.

### Devices

The second view contains one searchable table/list of monitored items with filters
for group and condition. Rows show the display name, group, current condition,
duration or last activity when available, battery and signal. A row opens the normal
Home Assistant more-info dialog for its representative entity.

When Entity Availability exposes multiple entities for the same physical device, the
panel respects the source group's collapse setting and the representative entity list
provided in sensor attributes. It does not attempt a second independent collapse.

### Diagnostics

The third view shows integration presence, detected groups, source entity IDs,
missing optional sensors, last successful refresh and current compatibility status.
This view makes source-data problems distinguishable from actual device outages.

## Status semantics

The panel renders Entity Availability's conclusions and does not infer connectivity
from a value that has not changed. Source states have these meanings:

1. `offline` — confirmed by Entity Availability after its configured cooldown;
2. `stale` — source group reports staleness using its configured activity rule;
3. `low battery` and `poor signal` — degraded but still reachable;
4. `online` — no reported problem;
5. `suppressed` or `non-essential` — informational and excluded from the aggregate
   alert;
6. missing/unavailable Entity Availability source entities — `Нет данных`, never
   silently treated as healthy.

`unknown` is displayed as the source integration classifies it. The panel does not
override each group's configured bad-state list.

## Data flow

The backend registers the panel and serves a versioned JavaScript module. The frontend
receives the existing Home Assistant state collection, discovers
`entity_availability_*_group_summary` and combined-summary entities, and binds their
companion sensors by group slug. Home Assistant state-change notifications trigger
targeted recalculation of affected counts and rows.

The refresh action asks Home Assistant to update the discovered Entity Availability
entities through `homeassistant.update_entity`. It reports success only after the
service call completes and a current state snapshot has been reapplied.

## Failure handling

- Missing Entity Availability: show setup state and keep the route usable.
- No configured groups: show an empty state with instructions to add a service/group.
- Missing optional sensors: show available data and list gaps under Diagnostics.
- Entity state `unavailable` or malformed attributes: show `Нет данных` for that
  field and retain the rest of the group.
- Refresh failure: preserve current data and show the error beside the refresh action.
- Frontend resource failure: backend and Home Assistant setup continue to load.

## Testing and acceptance

Automated tests cover route lifecycle ownership, frontend asset serving, group
discovery, aggregation, missing dependency/empty states, malformed optional data,
refresh semantics and absence of full-shell re-render on state updates.

Manual acceptance covers desktop and phone layouts, light and dark themes, fixed
header/footer, scrolling, pinch zoom/reset, more-info opening, problem-first sorting,
refresh feedback and live transition through offline and recovery states.

## First release scope

The first release reads and displays Entity Availability data, provides search and
filters, opens more-info and performs a source refresh. Editing groups, suppressing
entities and changing monitoring thresholds remain in Entity Availability settings.
