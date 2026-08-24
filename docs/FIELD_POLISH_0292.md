# Contract Generated UI 0.29.2 — field polish

This patch is based on the first complete iPhone field run of the central `Дом / Действия / Инфраструктура` set.

## Fixed in code

- `Действия`: the swing-gate placeholder now uses the shorter mobile-safe text `Датчика положения нет` while remaining strictly read-only.
- `Действия`: S8 OMNI fault state is presented semantically (`Ошибок нет`, `Код …`, `Нет данных`) instead of exposing the raw zero value as the primary user-facing status.
- `Инфраструктура`: an UPS summary can no longer show `Нет данных` and `Данные актуальны` at the same time. If the required UPS telemetry set is unreliable, freshness is rendered as `Данные недоступны`.

## Private House inventory field correction

The live infrastructure inventory confirms that `infrastructure.power.voltage_a/b/c` are the verified incoming three-phase voltage source. The private House RC inventory must rebind `house.home.power_a/b/c` to the same three verified entities before regeneration.

Concrete Home Assistant entity ids remain exclusively in the private runtime inventory and are intentionally not recorded in this public repository.

This is deliberately a private-inventory correction rather than a generated-YAML edit. Generated dashboards remain reproducible from contracts, manifests and verified inventory.
