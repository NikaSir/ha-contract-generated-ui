# Main panels v11

This document covers only the three central NikaS surfaces:

- `Дом`;
- `Действия`;
- `Инфраструктура`.

Integration-owned application panels are outside this migration scope.

## Complete-set release candidate — CGUI 0.29.0

The isolated mock-up phase is closed. The next field-test unit is the complete three-panel application shell:

1. `Дом` — `/dashboard-house-v11/home`;
2. `Действия` — `/dashboard-actions/home`;
3. `Инфраструктура` — `/dashboard-infrastructure/overview`.

The global fixed bottom navigation is evaluated only as a complete set: `Дом / Действия / Инфра`.

The accepted live `/dashboard-house` is intentionally left untouched during the release-candidate test. The central `Дом` tab temporarily targets `/dashboard-house-v11/home`. After mobile acceptance, House is promoted to `/dashboard-house` and the route is returned to the production path.

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

## Действия

The formal public contract is `contracts/actions_home.yaml`. The generated main manifest is `manifests/actions.yaml`.

The central Actions surface contains:

1. `Ворота и доступ` — physical sectional-gate status and an explicit no-sensor state for swing gates; no retired ROXIMO cover controls;
2. `Уборка` — S8 OMNI factual status plus two strictly allowlisted, confirmed quick commands: start cleaning and return to base;
3. `Полив` — navigation into the irrigation panel while the central quick-action contract remains deliberately conservative.

The renderer does not introduce a generic service-call mechanism. Unsupported contract service actions still fail closed.

## Инфраструктура

`manifests/infrastructure.yaml` remains the current generated infrastructure main panel. It is tested in the same global shell without a parallel replacement.

The overview remains summary-first. Detailed electricity, UPS, WAN/LTE and other diagnostics stay in their owned detail views/panels.

A future `Здоровье системы` semantic source may be backed by Gatus after the integration is installed and verified; no synthetic Gatus entities are introduced by this release candidate.

## Private semantic inventory

Public contracts/manifests are synchronized from the integration package. Private Home Assistant bindings remain local under:

`/config/contract_generated_ui/inventory/`

The release candidate therefore requires the verified House and Actions private inventory files on the target Home Assistant instance before generation.

## Acceptance gate

Promotion of the complete set requires:

- successful generation with current private semantic inventory;
- no broken global navigation targets;
- correct `unknown` / `unavailable` handling;
- no retired gate-control actions in `Действия`;
- S8 OMNI commands confirmed and working;
- the House protected section order preserved;
- all three main panels reviewed on the real iPhone frontend;
- semantic diff reviewed before House route cut-over.
