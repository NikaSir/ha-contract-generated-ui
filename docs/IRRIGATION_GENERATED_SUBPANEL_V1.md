# HO-SC-8W generated subpanel v1

**Status:** staged migration candidate  
**Owner of UI shell:** `ha-contract-generated-ui`  
**Owner of data/actions:** `ha-ho-sc-8w`

## Architecture boundary

The HO-SC-8W integration remains responsible for controller transport, entities, factual states and future verified actions. Contract Generated UI owns the application route, Header/Back behavior, Bottom Tab Bar and Lovelace composition.

The generated panel is intentionally read-only for controller changes in this stage. It contains no raw Tuya DP write path.

## Canonical route

```text
Действия
  ↓
/dashboard-irrigation/overview
```

Generated tabs:

```text
Обзор · Ручной · Настройки · Диагностика
```

Every view is a native Home Assistant subview with deterministic:

```text
back_path: /dashboard-actions
```

The generated dashboard is hidden from the sidebar and entered through the logical parent surface.

## Public contracts

Three public contracts define the UI boundary:

- `house.irrigation.controller` — transport, controller mode, active/queued zones, rain, seasonal adjustment and integration diagnostics;
- `house.irrigation.zone` — repeatable production zone program/runtime contract for zones 1–6;
- `house.irrigation.lab` — diagnostics-only Zone 8 read-only program source.

All actions in v1 are `more_info`. `unknown` and `unavailable` are always unreliable.

## Required private semantic inventory

The public manifest references semantic keys only. The real Home Assistant entity IDs remain in private runtime inventory and must be verified before generation.

Controller keys:

```text
house.irrigation.ho_sc_8w.connection_mode
house.irrigation.ho_sc_8w.operation_mode
house.irrigation.ho_sc_8w.irrigation_mode
house.irrigation.ho_sc_8w.active_zones
house.irrigation.ho_sc_8w.queued_zones
house.irrigation.ho_sc_8w.rain_sensor
house.irrigation.ho_sc_8w.seasonal_adjustment
house.irrigation.ho_sc_8w.schedule_cache
house.irrigation.ho_sc_8w.timer_error_alarm
```

For each production zone `N = 1..6`:

```text
house.irrigation.ho_sc_8w.zone_N.schedule
house.irrigation.ho_sc_8w.zone_N.time_remaining
house.irrigation.ho_sc_8w.zone_N.time_elapsed
```

Laboratory Zone 8:

```text
house.irrigation.ho_sc_8w.zone_8.schedule
```

## Functional mapping

### Overview

Shows factual controller status plus the decoded program state of zones 1–6.

### Manual

Shows current controller execution and per-zone runtime telemetry. No Start/Stop action is exposed until `ha-ho-sc-8w` publishes and validates an integration-owned safe action.

### Settings

Shows controller-wide factual settings in read-only form: irrigation order, rain handling and seasonal adjustment.

### Diagnostics

Shows cache/error diagnostics, laboratory Zone 8 and detailed production-zone program/runtime verification.

## Migration gate

The existing integration-owned `ha-ho-sc-8w` custom panel remains the fallback until the generated candidate passes all of the following in real Home Assistant:

1. every required semantic key is bound to a verified entity in private inventory;
2. generation completes without unresolved bindings;
3. `/dashboard-irrigation/overview` opens locally after a full Home Assistant restart;
4. the same route opens through Home Assistant Cloud / Nabu Casa;
5. Header Back returns deterministically to `/dashboard-actions`;
6. the four Bottom Tab Bar tabs switch correctly;
7. `unknown` / `unavailable` remain visibly unreliable;
8. zones 1–6 match the factual DP38/runtime data from `ha-ho-sc-8w`;
9. Zone 8 appears only in Diagnostics;
10. no controller write is produced by the generated UI.

Only after this PASS may the integration-owned shell registration/frontend in `ha-ho-sc-8w` be retired. Controller/backend code must remain in `ha-ho-sc-8w`.

## Non-goals of v1

- no raw DP38/DP45 write;
- no schedule editing;
- no manual start/stop;
- no duplicated Home Assistant entity IDs in public repository sources;
- no subsystem-specific route constants in `nikas-ui.js`.
