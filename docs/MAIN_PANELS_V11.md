# Main panels v11

This document covers only the three central NikaS surfaces:

- `Дом` (`/dashboard-house`)
- `Действия` (`/dashboard-actions`)
- `Инфраструктура` (`/dashboard-infrastructure`)

Integration-owned application panels are outside this migration scope.

## House phase 1 — safe preview

The first v11 main-panel candidate is staged at:

`staged/main_panels/house/panel-manifest.yaml`

It deliberately uses `/dashboard-house-v11` so the accepted live `/dashboard-house` remains untouched while mobile layout is reviewed.

The formal public contract is `contracts/house_home.yaml`. It contains semantic roles only and no private Home Assistant entity ids. The matching private semantic inventory remains local to the Home Assistant installation and is not tracked in Git.

The `house_home_v1` renderer preserves the approved top-level order:

1. Дом сейчас
2. Активные события
3. Ресурсы
4. Отопление и ГВС
5. Автомобили
6. Ключевые точки доступа

Main-panel resources remain intentionally compact: electrical supply after stabilizers, drinking water and internet. Detailed subsystem telemetry belongs to the owning application panel.

## Preview activation

For a field preview only:

1. install/update Contract Generated UI so the `house.home` contract is synchronized;
2. place the private `house.home.*` inventory bindings in `/config/contract_generated_ui/inventory/`;
3. copy the staged House manifest to `/config/contract_generated_ui/manifests/house_v11_preview.yaml`;
4. run `Сгенерировать панели`;
5. add the generated `/dashboard-house-v11` YAML dashboard using the emitted Lovelace registration snippet;
6. test `/dashboard-house-v11/home` on iPhone;
7. do not replace `/dashboard-house` until field acceptance is complete.

## Promotion gate

Promotion from preview to `/dashboard-house` requires:

- current-registry verification of every private semantic binding;
- no broken navigation targets;
- correct `unknown` / `unavailable` handling;
- protected section order preserved;
- mobile acceptance on the real Home Assistant frontend;
- semantic diff reviewed before route cut-over.

## Next central surfaces

After House acceptance the same process is used for `Действия`. `Инфраструктура` already has a production manifest and is refined in place only after House/Actions central-shell acceptance.
