from __future__ import annotations

from typing import Any, Mapping

SUMMARY_RENDERER = "infrastructure_summary_v1"
SUMMARY_CARD_TYPE = "markdown"

SUMMARY_VARIANTS = {
    "infrastructure.power_grid": "power_grid",
    "infrastructure.ups": "ups",
    "infrastructure.keenetic": "keenetic",
}

SUMMARY_ROLE_ORDER = {
    "infrastructure.power_grid": (
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


def required_summary_roles(contract_id: str) -> tuple[str, ...]:
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

    return f"""{{% set reliable = has_value('{grid}') and has_value('{meter}') and has_value('{phase_loss}') and has_value('{phase_a}') and has_value('{phase_b}') and has_value('{phase_c}') and has_value('{voltage_a}') and has_value('{voltage_b}') and has_value('{voltage_c}') and has_value('{imbalance}') and has_value('{power}') %}}
{{% set event = reliable and (is_state('{grid}', 'off') or is_state('{meter}', 'off') or is_state('{phase_loss}', 'on') or is_state('{phase_a}', 'off') or is_state('{phase_b}', 'off') or is_state('{phase_c}', 'off')) %}}
<table role="presentation" width="100%">
<tr><td><strong>{title}</strong><br><small>Трёхфазная сеть</small></td><td align="right"><strong>{{% if not reliable %}}⚪ Данные неполные{{% elif event %}}🔴 Отклонение{{% else %}}🟢 Нормально{{% endif %}}</strong></td></tr>
</table>
<table role="presentation" width="100%">
<tr>
<td width="33%" align="center">A<br><strong>{_translated(voltage_a)}</strong></td>
<td width="34%" align="center">B<br><strong>{_translated(voltage_b)}</strong></td>
<td width="33%" align="center">C<br><strong>{_translated(voltage_c)}</strong></td>
</tr>
<tr>
<td colspan="2"><ha-icon icon="mdi:sine-wave"></ha-icon> Перекос · <strong>{_translated(imbalance)}</strong></td>
<td><ha-icon icon="mdi:flash"></ha-icon> <strong>{_translated(power)}</strong></td>
</tr>
</table>"""


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


def build_summary_card(semantic_module: Mapping[str, Any]) -> dict[str, Any]:
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

    required = required_summary_roles(contract_id)
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
    if navigate_targets:
        card["tap_action"] = {
            "action": "navigate",
            "navigation_path": next(iter(navigate_targets)),
        }
    return card


__all__ = [
    "SUMMARY_CARD_TYPE",
    "SUMMARY_RENDERER",
    "SUMMARY_ROLE_ORDER",
    "SUMMARY_VARIANTS",
    "build_summary_card",
    "required_summary_roles",
]
