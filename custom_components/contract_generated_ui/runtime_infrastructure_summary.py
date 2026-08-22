from __future__ import annotations

from typing import Any, Mapping

SUMMARY_RENDERER = "infrastructure_summary_v1"
SUMMARY_CARD_TYPE = "markdown"

SUMMARY_VARIANTS = {
    "infrastructure.power_grid": "power_grid",
    "infrastructure.ups": "ups",
    "infrastructure.keenetic": "keenetic",
}

POWER_ROLES = (
    "grid_ok",
    "meter_online",
    "phase_loss",
    "phase_a_present",
    "phase_b_present",
    "phase_c_present",
    "voltage_a",
    "voltage_b",
    "voltage_c",
    "voltage_imbalance",
    "total_power",
    "non_interruptible_voltage",
    "non_interruptible_frequency",
    "non_interruptible_mode",
    "non_interruptible_data_stale",
)

SUMMARY_ROLE_ORDER = {
    "infrastructure.power_grid": POWER_ROLES,
    "infrastructure.ups": (
        "operating_mode",
        "battery_capacity",
        "output_load",
        "cloud_telemetry",
        "data_stale",
        "on_battery",
    ),
    "infrastructure.keenetic": (
        "active_wan",
        "last_wan_switch",
        "last_wan_switch_reason",
        "wan_switches_today",
        "lte_time_today",
        "temperature",
    ),
}

POWER_VIEW_ROLE_ORDER = {
    "power-overview": POWER_ROLES,
    "power-before": (
        "grid_ok",
        "meter_online",
        "phase_loss",
        "phase_a_present",
        "phase_b_present",
        "phase_c_present",
        "voltage_a",
        "voltage_b",
        "voltage_c",
        "voltage_imbalance",
        "total_power",
    ),
    "power-after": ("grid_ok",),
    "power-history": (
        "voltage_a",
        "voltage_b",
        "voltage_c",
        "non_interruptible_voltage",
    ),
}


def required_summary_roles(
    contract_id: str,
    view_id: str | None = None,
) -> tuple[str, ...]:
    if contract_id == "infrastructure.power_grid" and view_id in POWER_VIEW_ROLE_ORDER:
        return POWER_VIEW_ROLE_ORDER[view_id]
    roles = SUMMARY_ROLE_ORDER.get(contract_id)
    if roles is None:
        raise ValueError(
            f"infrastructure summary does not support contract {contract_id!r}"
        )
    return roles


def _translated(entity_id: str) -> str:
    return (
        "{{ state_translated('"
        + entity_id
        + "') if has_value('"
        + entity_id
        + "') else 'Недоступно' }}"
    )


def _tile(entity_id: str, name: str, icon: str) -> dict[str, Any]:
    return {
        "type": "tile",
        "entity": entity_id,
        "name": name,
        "icon": icon,
        "tap_action": {"action": "more-info"},
        "hold_action": {"action": "more-info"},
        "double_tap_action": {"action": "none"},
    }


def _power_content(title: str, entities: Mapping[str, str]) -> str:
    grid = entities["grid_ok"]
    meter = entities["meter_online"]
    phase_loss = entities["phase_loss"]
    phase_a = entities["phase_a_present"]
    phase_b = entities["phase_b_present"]
    phase_c = entities["phase_c_present"]
    voltage_a = entities["voltage_a"]
    voltage_b = entities["voltage_b"]
    voltage_c = entities["voltage_c"]
    imbalance = entities["voltage_imbalance"]
    power = entities["total_power"]
    line_voltage = entities["non_interruptible_voltage"]
    line_frequency = entities["non_interruptible_frequency"]
    line_mode = entities["non_interruptible_mode"]
    line_stale = entities["non_interruptible_data_stale"]

    return f"""{{% set before_reliable = has_value('{grid}') and has_value('{meter}') and has_value('{phase_loss}') and has_value('{phase_a}') and has_value('{phase_b}') and has_value('{phase_c}') and has_value('{voltage_a}') and has_value('{voltage_b}') and has_value('{voltage_c}') and has_value('{imbalance}') and has_value('{power}') %}}
{{% set before_event = before_reliable and (is_state('{grid}', 'off') or is_state('{meter}', 'off') or is_state('{phase_loss}', 'on') or is_state('{phase_a}', 'off') or is_state('{phase_b}', 'off') or is_state('{phase_c}', 'off')) %}}
{{% set line_reliable = has_value('{line_voltage}') and has_value('{line_frequency}') and has_value('{line_mode}') and has_value('{line_stale}') %}}
<table role="presentation" width="100%">
<tr><td><strong>{title}</strong><br><small>Три точки контроля</small></td><td align="right"><strong>🔵 Контроль</strong></td></tr>
</table>
<table role="presentation" width="100%">
<tr>
<td width="33%" align="center"><small>До стаб.</small><br><strong>{{% if not before_reliable %}}⚪ Нет данных{{% elif before_event %}}🔴 Отклонение{{% else %}}🟢 Нормально{{% endif %}}</strong></td>
<td width="34%" align="center"><small>После стаб.</small><br><strong>⚪ Подготовлено</strong></td>
<td width="33%" align="center"><small>Линия котла</small><br><strong>{{% if not line_reliable %}}⚪ Нет данных{{% elif is_state('{line_stale}', 'on') %}}🟠 Данные устарели{{% else %}}🟢 {_translated(line_voltage)}{{% endif %}}</strong></td>
</tr>
</table>
<table role="presentation" width="100%">
<tr>
<td><ha-icon icon="mdi:sine-wave"></ha-icon> Перекос · <strong>{_translated(imbalance)}</strong></td>
<td><ha-icon icon="mdi:flash"></ha-icon> Мощность · <strong>{_translated(power)}</strong></td>
<td align="right"><ha-icon icon="mdi:sine-wave"></ha-icon> Линия · <strong>{_translated(line_frequency)}</strong></td>
</tr>
<tr><td colspan="3" align="right"><strong>Подробнее ›</strong></td></tr>
</table>"""


def _power_status_content(entities: Mapping[str, str]) -> str:
    grid = entities["grid_ok"]
    meter = entities["meter_online"]
    phase_loss = entities["phase_loss"]
    phase_a = entities["phase_a_present"]
    phase_b = entities["phase_b_present"]
    phase_c = entities["phase_c_present"]
    line_stale = entities["non_interruptible_data_stale"]
    line_mode = entities["non_interruptible_mode"]
    return f"""{{% set reliable = has_value('{grid}') and has_value('{meter}') and has_value('{phase_loss}') and has_value('{phase_a}') and has_value('{phase_b}') and has_value('{phase_c}') %}}
{{% set event = reliable and (is_state('{grid}', 'off') or is_state('{meter}', 'off') or is_state('{phase_loss}', 'on') or is_state('{phase_a}', 'off') or is_state('{phase_b}', 'off') or is_state('{phase_c}', 'off')) %}}
## {{% if not reliable %}}⚪ Данные входящей сети неполные{{% elif event %}}🔴 Есть отклонение входящей сети{{% else %}}🟢 Входящая сеть в норме{{% endif %}}
Три физические точки контроля: **до стабилизаторов**, **после стабилизаторов**, **неотключаемая линия**.

Линия котла: **{_translated(line_mode)}** · {{% if not has_value('{line_stale}') %}}свежесть неизвестна{{% elif is_state('{line_stale}', 'on') %}}данные устарели{{% else %}}данные актуальны{{% endif %}}."""


def _power_overview_card(entities: Mapping[str, str]) -> dict[str, Any]:
    status_entities = [
        entities[name]
        for name in (
            "grid_ok",
            "meter_online",
            "phase_loss",
            "phase_a_present",
            "phase_b_present",
            "phase_c_present",
            "non_interruptible_mode",
            "non_interruptible_data_stale",
        )
    ]
    return {
        "type": "vertical-stack",
        "grid_options": {"columns": "full"},
        "cards": [
            {
                "type": "markdown",
                "content": _power_status_content(entities),
                "entity_id": status_entities,
            },
            {"type": "heading", "heading": "1. До стабилизаторов · входящая сеть"},
            {
                "type": "grid",
                "columns": 3,
                "square": False,
                "cards": [
                    _tile(entities["voltage_a"], "Фаза A", "mdi:alpha-a-circle-outline"),
                    _tile(entities["voltage_b"], "Фаза B", "mdi:alpha-b-circle-outline"),
                    _tile(entities["voltage_c"], "Фаза C", "mdi:alpha-c-circle-outline"),
                ],
            },
            {
                "type": "grid",
                "columns": 2,
                "square": False,
                "cards": [
                    _tile(entities["voltage_imbalance"], "Перекос", "mdi:sine-wave"),
                    _tile(entities["total_power"], "Мощность", "mdi:flash"),
                ],
            },
            {
                "type": "markdown",
                "content": """### 2. После стабилизаторов
⚪ **Точка контроля зарезервирована.** В v0.12 структура уже показана в интерфейсе, но значения не подменяются и не вычисляются из входящей сети до появления проверенных semantic bindings.

**Пороги качества после стабилизаторов:** норма 210–230 В; внимание 205–209 / 231–235 В; существенное отклонение 198–204 / 236–242 В; авария ниже 198 В.""",
            },
            {"type": "heading", "heading": "3. Неотключаемая линия · UPS Котёл"},
            {
                "type": "grid",
                "columns": 3,
                "square": False,
                "cards": [
                    _tile(
                        entities["non_interruptible_voltage"],
                        "Напряжение",
                        "mdi:power-plug-outline",
                    ),
                    _tile(
                        entities["non_interruptible_frequency"],
                        "Частота",
                        "mdi:sine-wave",
                    ),
                    _tile(
                        entities["non_interruptible_mode"],
                        "Источник",
                        "mdi:battery-sync-outline",
                    ),
                ],
            },
        ],
    }


def _power_before_card(entities: Mapping[str, str]) -> dict[str, Any]:
    grid = entities["grid_ok"]
    meter = entities["meter_online"]
    phase_loss = entities["phase_loss"]
    phase_a = entities["phase_a_present"]
    phase_b = entities["phase_b_present"]
    phase_c = entities["phase_c_present"]
    status = f"""{{% set reliable = has_value('{grid}') and has_value('{meter}') and has_value('{phase_loss}') and has_value('{phase_a}') and has_value('{phase_b}') and has_value('{phase_c}') %}}
{{% set event = reliable and (is_state('{grid}', 'off') or is_state('{meter}', 'off') or is_state('{phase_loss}', 'on') or is_state('{phase_a}', 'off') or is_state('{phase_b}', 'off') or is_state('{phase_c}', 'off')) %}}
## {{% if not reliable %}}⚪ Данные неполные{{% elif event %}}🟠 Требует внимания{{% else %}}🟢 Нормально{{% endif %}}
Контроль входящей трёхфазной сети **до стабилизаторов**."""
    return {
        "type": "vertical-stack",
        "grid_options": {"columns": "full"},
        "cards": [
            {
                "type": "markdown",
                "content": status,
                "entity_id": [grid, meter, phase_loss, phase_a, phase_b, phase_c],
            },
            {
                "type": "grid",
                "columns": 3,
                "square": False,
                "cards": [
                    _tile(entities["voltage_a"], "Фаза A", "mdi:alpha-a-circle-outline"),
                    _tile(entities["voltage_b"], "Фаза B", "mdi:alpha-b-circle-outline"),
                    _tile(entities["voltage_c"], "Фаза C", "mdi:alpha-c-circle-outline"),
                ],
            },
            {
                "type": "grid",
                "columns": 2,
                "square": False,
                "cards": [
                    _tile(entities["voltage_imbalance"], "Перекос фаз", "mdi:sine-wave"),
                    _tile(entities["total_power"], "Мощность общая", "mdi:flash"),
                ],
            },
        ],
    }


def _power_after_card() -> dict[str, Any]:
    return {
        "type": "markdown",
        "grid_options": {"columns": "full"},
        "content": """## ⚪ После стабилизаторов

Точка контроля предусмотрена отдельным экраном и **не использует входящие фазы как замену выходным измерениям**.

Сейчас проверенные semantic bindings для трёх напряжений после стабилизаторов в Contract Generated UI не заданы. Поэтому v0.12 намеренно показывает структуру без фиктивных значений.

| Уровень | Напряжение |
|---|---:|
| Норма | 210–230 В |
| Внимание | 205–209 / 231–235 В |
| Существенное отклонение | 198–204 / 236–242 В |
| Авария | <198 В |

После привязки трёх фактических источников этот экран заполняется без изменения общей навигации.""",
    }


def _power_history_card(entities: Mapping[str, str]) -> dict[str, Any]:
    return {
        "type": "history-graph",
        "title": "Напряжение · 24 часа",
        "hours_to_show": 24,
        "entities": [
            entities["voltage_a"],
            entities["voltage_b"],
            entities["voltage_c"],
            entities["non_interruptible_voltage"],
        ],
        "grid_options": {"columns": "full"},
    }


def _ups_content(title: str, entities: Mapping[str, str], *, details: bool) -> str:
    mode = entities["operating_mode"]
    battery = entities["battery_capacity"]
    load = entities["output_load"]
    cloud = entities["cloud_telemetry"]
    stale = entities["data_stale"]
    on_battery = entities["on_battery"]
    details_text = "<strong>Подробнее ›</strong>" if details else ""

    return f"""{{% set reliable = has_value('{mode}') and has_value('{battery}') and has_value('{load}') and has_value('{stale}') and has_value('{on_battery}') %}}
<table role="presentation" width="100%">
<tr><td><strong>{title}</strong><br><small>{_translated(mode)}</small></td><td align="right"><strong>{{% if not reliable %}}⚪ Нет данных{{% elif is_state('{on_battery}', 'on') %}}🔴 От батареи{{% elif is_state('{stale}', 'on') %}}🟠 Данные устарели{{% elif not has_value('{cloud}') %}}⚪ Облако неизвестно{{% elif is_state('{cloud}', 'off') %}}🟠 Облако отключено{{% else %}}🟢 Нормально{{% endif %}}</strong></td></tr>
</table>
<table role="presentation" width="100%">
<tr>
<td width="50%"><ha-icon icon="mdi:battery"></ha-icon> АКБ · <strong>{_translated(battery)}</strong></td>
<td width="50%"><ha-icon icon="mdi:gauge"></ha-icon> Нагрузка · <strong>{_translated(load)}</strong></td>
</tr>
<tr>
<td><small>Облако: {{% if not has_value('{cloud}') %}}неизвестно{{% elif is_state('{cloud}', 'on') %}}подключено{{% else %}}отключено{{% endif %}} · {{% if not has_value('{stale}') %}}Свежесть неизвестна{{% elif is_state('{stale}', 'on') %}}Данные устарели{{% else %}}Данные актуальны{{% endif %}}</small></td>
<td align="right">{details_text}</td>
</tr>
</table>"""


def _keenetic_content(title: str, entities: Mapping[str, str]) -> str:
    wan = entities["active_wan"]
    switch = entities["last_wan_switch"]
    reason = entities["last_wan_switch_reason"]
    switches = entities["wan_switches_today"]
    lte = entities["lte_time_today"]
    temperature = entities["temperature"]

    return f"""{{% set raw_switch = states('{switch}') %}}
{{% if raw_switch not in ['unknown', 'unavailable'] %}}
  {{% set switch_seconds = (as_timestamp(now()) - as_timestamp(as_datetime(raw_switch))) | int %}}
  {{% if switch_seconds < 60 %}}{{% set switch_text = 'только что' %}}
  {{% elif switch_seconds < 3600 %}}{{% set switch_text = (switch_seconds // 60) ~ ' мин назад' %}}
  {{% elif switch_seconds < 172800 %}}{{% set switch_text = (switch_seconds // 3600) ~ ' ч назад' %}}
  {{% else %}}{{% set switch_text = (switch_seconds // 86400) ~ ' дн назад' %}}{{% endif %}}
{{% else %}}{{% set switch_text = 'Недоступно' %}}{{% endif %}}
<table role="presentation" width="100%">
<tr><td><strong>{title}</strong><br><small>WAN / LTE</small></td><td align="right"><strong>{{% if has_value('{wan}') %}}🔵 WAN · {_translated(wan)}{{% else %}}⚪ WAN неизвестен{{% endif %}}</strong></td></tr>
</table>
<table role="presentation" width="100%">
<tr>
<td width="50%">Активный WAN · <strong>{_translated(wan)}</strong></td>
<td width="50%">Последняя смена · <strong>{{{{ switch_text }}}}</strong></td>
</tr>
<tr><td colspan="2"><small><strong>Причина ·</strong> {_translated(reason)}</small></td></tr>
<tr>
<td><ha-icon icon="mdi:swap-horizontal"></ha-icon> Смен сегодня · <strong>{_translated(switches)}</strong></td>
<td><ha-icon icon="mdi:timer-outline"></ha-icon> LTE · <strong>{_translated(lte)}</strong> &nbsp; <ha-icon icon="mdi:thermometer"></ha-icon> <strong>{_translated(temperature)}</strong></td>
</tr>
</table>"""


def build_summary_card(
    semantic_module: Mapping[str, Any],
    *,
    view_id: str | None = None,
) -> dict[str, Any]:
    contract_id = semantic_module.get("contract")
    if not isinstance(contract_id, str):
        raise ValueError("infrastructure summary module contract missing")
    variant = SUMMARY_VARIANTS.get(contract_id)
    if variant is None:
        raise ValueError(
            f"infrastructure summary does not support contract {contract_id!r}"
        )

    title = semantic_module.get("title")
    roles = semantic_module.get("roles")
    if not isinstance(title, str) or not title or not isinstance(roles, list):
        raise ValueError("infrastructure summary module title/roles missing")

    role_by_name: dict[str, Mapping[str, Any]] = {}
    for role in roles:
        if not isinstance(role, Mapping):
            raise ValueError("infrastructure summary role must be an object")
        role_name = role.get("role")
        if not isinstance(role_name, str):
            raise ValueError("infrastructure summary role name missing")
        role_by_name[role_name] = role

    required = required_summary_roles(contract_id, view_id)
    missing = [role_name for role_name in required if role_name not in role_by_name]
    if missing:
        raise ValueError(
            f"infrastructure summary {contract_id!r} missing roles: {', '.join(missing)}"
        )

    entities: dict[str, str] = {}
    navigate_targets: set[str] = set()
    for role_name in required:
        role = role_by_name[role_name]
        entity_id = role.get("entity_id")
        label = role.get("label")
        if not isinstance(entity_id, str) or not isinstance(label, str):
            raise ValueError(
                f"infrastructure summary role {role_name!r} entity/label missing"
            )
        entities[role_name] = entity_id
        action = role.get("action")
        if isinstance(action, Mapping) and action.get("kind") == "navigate":
            target = action.get("target")
            if not isinstance(target, str) or not target.startswith("/"):
                raise ValueError(
                    f"infrastructure summary role {role_name!r} has invalid navigate target"
                )
            navigate_targets.add(target)

    if len(navigate_targets) > 1:
        raise ValueError(
            f"infrastructure summary {contract_id!r} has conflicting navigate targets"
        )

    if variant == "power_grid":
        if view_id == "power-overview":
            return _power_overview_card(entities)
        if view_id == "power-before":
            return _power_before_card(entities)
        if view_id == "power-after":
            return _power_after_card()
        if view_id == "power-history":
            return _power_history_card(entities)
        content = _power_content(title, entities)
    elif variant == "ups":
        content = _ups_content(title, entities, details=bool(navigate_targets))
    else:
        content = _keenetic_content(title, entities)

    card: dict[str, Any] = {
        "type": SUMMARY_CARD_TYPE,
        "content": content,
        "entity_id": [entities[role_name] for role_name in required],
        "grid_options": {"columns": "full"},
    }
    if navigate_targets and view_id in (None, "overview"):
        card["tap_action"] = {
            "action": "navigate",
            "navigation_path": next(iter(navigate_targets)),
        }
    return card


__all__ = [
    "POWER_VIEW_ROLE_ORDER",
    "SUMMARY_CARD_TYPE",
    "SUMMARY_RENDERER",
    "SUMMARY_ROLE_ORDER",
    "SUMMARY_VARIANTS",
    "build_summary_card",
    "required_summary_roles",
]
