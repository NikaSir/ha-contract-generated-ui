# HO-SC-8W generated subpanel v1

**Status:** dormant staged migration candidate  
**Shell authority:** `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.7.
**Owner of UI shell:** `ha-contract-generated-ui`  
**Owner of data/actions:** `ha-ho-sc-8w`

## Architecture boundary

The HO-SC-8W integration remains responsible for controller transport, entities, factual states and future verified actions. Contract Generated UI owns the application route, Home Assistant menu Header, Bottom Tab Bar and Lovelace composition.

The generated panel is intentionally read-only for controller changes in this stage. It contains no raw Tuya DP write path.

## Dormant staging rule

The candidate manifest is stored at:

```text
staged/irrigation/panel-manifest.yaml
```

It is intentionally **not** placed in active `manifests/` and is not bundled into runtime `bundled_sources/manifests/` yet. This preserves the existing fail-closed generator: installing Contract Generated UI 0.20.0 must not make normal dashboard generation fail merely because the private HO-SC-8W semantic bindings have not been created yet.

Activation occurs only after every required irrigation semantic key exists in verified private inventory. At that point the exact staged manifest is promoted into active `manifests/` and bundled runtime sources in a dedicated activation change.

## Staged route and final cutover

The production integration-owned panel already occupies `/dashboard-irrigation`. Therefore the generated candidate uses a non-conflicting route when activated for field testing.

Staged route:

```text
Действия
  ↓
/dashboard-irrigation-generated/overview
```

The logical candidate route is already reserved in `navigation/main.yaml` as `actions.irrigation_candidate`, but no generated irrigation Tab Bar is published to the runtime navigation registry while the manifest remains dormant.

After field acceptance, one coordinated cutover changes the generated dashboard to the canonical production route:

```text
/dashboard-irrigation/overview
```

and retires only the old integration-owned shell registration/frontend from `ha-ho-sc-8w`. The controller/backend integration remains unchanged.

Generated tabs:

```text
Обзор · Ручной · Настройки · Диагностика
```

Every view is a native Home Assistant subview with deterministic:

```text
back_path: /dashboard-actions
```

## Public contracts

Three public contracts define the UI boundary:

- `house.irrigation.controller` — transport, controller mode, active/queued zones, rain, seasonal adjustment and integration diagnostics;
- `house.irrigation.zone` — repeatable production zone program/runtime contract for zones 1–6;
- `house.irrigation.lab` — diagnostics-only Zone 8 read-only program source.

All actions in v1 are `more_info`. `unknown` and `unavailable` are always unreliable.

## Required private semantic inventory

The staged manifest references semantic keys only. The real Home Assistant entity IDs remain in private runtime inventory and must be verified before activation.

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
2. the staged manifest is promoted into active runtime sources;
3. generation completes without unresolved bindings;
4. `/dashboard-irrigation-generated/overview` opens locally after a full Home Assistant restart;
5. the same staged route opens through Home Assistant Cloud / Nabu Casa;
6. the Header menu opens native Home Assistant navigation and the in-work parent link returns deterministically to `/dashboard-actions`;
7. the four Bottom Tab Bar tabs switch correctly;
8. `unknown` / `unavailable` remain visibly unreliable;
9. zones 1–6 match the factual DP38/runtime data from `ha-ho-sc-8w`;
10. Zone 8 appears only in Diagnostics;
11. no controller write is produced by the generated UI.

Only after this PASS may the coordinated production cutover occur. The cutover must not leave two owners of `/dashboard-irrigation` active at the same time.

## Non-goals of v1

- no raw DP38/DP45 write;
- no schedule editing;
- no manual start/stop;
- no duplicated Home Assistant entity IDs in public repository sources;
- no subsystem-specific route constants in `nikas-ui.js`.
