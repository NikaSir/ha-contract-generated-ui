# Contract Generated UI 0.29.2 — field polish

This patch is based on the first complete iPhone field run of the central `Дом / Действия / Инфраструктура` set.

## Fixed in code

- `Действия`: the swing-gate placeholder now uses the shorter mobile-safe text `Датчика положения нет` while remaining strictly read-only.
- `Действия`: S8 OMNI fault state is presented semantically (`Ошибок нет`, `Код …`, `Нет данных`) instead of exposing the raw zero value as the primary user-facing status.
- `Инфраструктура`: an UPS summary can no longer show `Нет данных` and `Данные актуальны` at the same time. If the required UPS telemetry set is unreliable, freshness is rendered as `Данные недоступны`.

## Private House inventory field correction

The live infrastructure inventory confirms the verified incoming three-phase voltage entities:

- `infrastructure.power.voltage_a` → `sensor.power_monitor_voltage_a`;
- `infrastructure.power.voltage_b` → `sensor.power_monitor_voltage_b`;
- `infrastructure.power.voltage_c` → `sensor.power_monitor_voltage_c`.

The private House RC inventory must therefore rebind `house.home.power_a/b/c` to those same verified entities before regeneration. Private Home Assistant entity bindings remain outside the public repository.

This is deliberately a private-inventory correction rather than a generated-YAML edit. Generated dashboards remain reproducible from contracts, manifests and verified inventory.
