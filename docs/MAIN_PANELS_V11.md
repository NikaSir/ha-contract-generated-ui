# Main panels v11

This document covers the four central NikaS surfaces:

- `Дом`;
- `Помещения`;
- `Действия`;
- `Инфраструктура`.

Integration-owned application panels are outside this migration scope.

## Current complete set

The canonical four-panel application shell is:

1. `Дом` — `/dashboard-house-v11/home`;
2. `Помещения` — `/dashboard-rooms/rooms`;
3. `Действия` — `/dashboard-actions/home`;
4. `Инфраструктура` — `/dashboard-infrastructure/overview`.

The global fixed bottom navigation is evaluated only as a complete set: `Дом / Помещения / Действия / Инфра`.

Navigation contract `1.3.0` owns the four canonical entry routes. `/dashboard-house` may remain only as a temporary legacy detail/redirect surface; it is not a base-panel source route, return fallback or global-tab target.

Canonical deep routes used by the House/Actions manifests and renderers point to integration-owned applications rather than recreating them inside Contract Generated UI:

- heating — `/dashboard-zont`;
- vehicles — `/starline`;
- cleaning — `/dashboard-s8-omni`;
- irrigation — `/dashboard-irrigation`;
- UPS — `/dashboard-ups`;
- electricity — `/dashboard-lider`;
- internet/router — `/dashboard-keenetic`;
- rooms — `/dashboard-rooms/rooms`.

## Помещения

Rooms v11 is an integration-owned base-panel renderer registered directly at `/dashboard-rooms` through `panel_custom`. Legacy Lovelace room cards are no longer the runtime owner.

The shared NikaS base shell continues to own the fixed Header and Bottom Tab Bar. The Rooms renderer owns exactly one work viewport between them and does not create a second Header, Bottom Tab Bar or safe-area layer.

The Rooms data model is discovered from Home Assistant registries:

`Area → Device → Entity → Labels`.

Admission policy:

- the physical device belongs to the current Area;
- the device has `В эксплуатации` (`v_ekspluatatsii`);
- devices labelled `Резерв`, `На обслуживании`, `Требует замены` or `Выведено из эксплуатации` are excluded from the operational model;
- additional labels classify devices but do not replace Area ownership;
- room entity IDs are not manually hard-coded in the renderer.

The three internal views are:

1. **Overview** — compact navigation for floors and technical rooms; the reference iPhone portrait view is designed to fit between the fixed Header and Bottom Tab Bar without relying on hidden Lovelace spacing.
2. **Room** — operational climate, additional climate sensors, activity, security, cameras and a full-width `Диагностика` plaque.
3. **Diagnostics** — full device/entity listing for the selected room, including service/diagnostic entities; long scrolling is allowed here.

Routine Home Assistant state updates patch stable DOM values and classes. They do not remount the work viewport or rebuild the shared shell. Structural route changes replace only the active Rooms work-view subtree.

The previous `nikas-rooms-equipment.js`, `nikas-rooms-live-sections.js` and `nikas-rooms-diagnostics.js` source files may remain temporarily for rollback history, but they are not registered runtime modules after the Rooms v11 cut-over.

## Дом

The formal public contract is `contracts/house_home.yaml`. It contains semantic roles only and no private Home Assistant entity ids. The matching private semantic inventory remains local to the Home Assistant installation and is not tracked in Git.

The `house_home_v1` renderer preserves the approved top-level order:

1. Дом сейчас
2. Активные события
3. Ресурсы
4. Отопление и ГВС
5. Автомобили
6. Ключевые точки доступа

Main-panel resources remain intentionally compact. Detailed subsystem telemetry belongs to the owning subsystem panel.

The accepted `Дом сейчас` composition is fixed as three information rows above the visual scene:

1. `Окна / Двери / Свет / Движение / Климат`;
2. `Погода | Защита`;
3. `Дата и время | Камеры`.

The lower resource plaques delegate directly to their owners: `Электросеть` opens LIDER at `/dashboard-lider`, `Отопление` opens ZONT at `/dashboard-zont`, and `Интернет` opens Keenetic at `/dashboard-keenetic`.

Approved specialized-panel labels used by the main navigation are `Электросеть`, `Отопление`, `Пылесос`, `StarLine`, `Автополив` and `ИБП Stark`.

## Действия

The formal public contract is `contracts/actions_home.yaml`. The generated main manifest is `manifests/actions.yaml`.

The central Actions surface contains:

1. `Ворота и доступ` — physical sectional-gate status and an explicit no-sensor state for swing gates; no retired ROXIMO cover controls;
2. `Уборка` — S8 OMNI factual status plus two strictly allowlisted, confirmed quick commands: start cleaning and return to base; details go to `/dashboard-s8-omni`;
3. `Полив` — navigation into `/dashboard-irrigation` while the central quick-action contract remains deliberately conservative.

The renderer does not introduce a generic service-call mechanism. Unsupported contract service actions still fail closed.

## Инфраструктура

`manifests/infrastructure.yaml` remains the current generated infrastructure main panel. It is tested in the same global shell without a parallel replacement.

The overview remains summary-first. Detailed electricity, UPS, WAN/LTE and other diagnostics stay in their owned detail views/panels.

A future `Здоровье системы` semantic source may be backed by Gatus after the integration is installed and verified; no synthetic Gatus entities are introduced by this release candidate.

## Ownership boundary

Contract Generated UI owns the central shell, contracts, generation and navigation. It does not reclaim specialized application ownership that has already moved out:

- ZONT application/UI is owned by the dedicated ZONT project;
- StarLine application/UI is owned by `ha-starline-telemetry`;
- S8 OMNI, irrigation and UPS keep their dedicated panels.

## Private semantic inventory

Public contracts/manifests are synchronized from the integration package. Private Home Assistant bindings remain local under:

`/config/contract_generated_ui/inventory/`

The current set therefore requires the verified House and Actions private inventory files on the target Home Assistant instance before generation.

## Acceptance gate

Acceptance of the complete set requires:

- successful generation with current private semantic inventory;
- no broken global or integration-owned navigation targets;
- correct `unknown` / `unavailable` handling;
- no retired gate-control actions in `Действия`;
- S8 OMNI commands confirmed and working;
- the House protected section order preserved;
- Rooms overview/detail/diagnostics reviewed on the real iPhone frontend;
- all four main panels reviewed on the real iPhone frontend;
- semantic diff reviewed for every route-contract change.
