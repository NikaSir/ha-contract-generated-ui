from __future__ import annotations

from typing import Any, Mapping

SUMMARY_RENDERER = "infrastructure_summary_v1"
SUMMARY_CARD_TYPE = "custom:nikas-infrastructure-summary-v2"

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

    role_config: dict[str, dict[str, str]] = {}
    navigate_targets: set[str] = set()
    for role_name in required:
        role = role_by_name[role_name]
        entity_id = role.get("entity_id")
        label = role.get("label")
        if not isinstance(entity_id, str) or not isinstance(label, str):
            raise ValueError(
                f"infrastructure summary role {role_name!r} entity/label missing"
            )
        role_config[role_name] = {"entity": entity_id, "label": label}
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

    card: dict[str, Any] = {
        "type": SUMMARY_CARD_TYPE,
        "variant": variant,
        "title": title,
        "roles": role_config,
        "grid_options": {"columns": "full", "rows": "auto"},
    }
    if navigate_targets:
        card["details_path"] = next(iter(navigate_targets))
    return card


__all__ = [
    "SUMMARY_CARD_TYPE",
    "SUMMARY_RENDERER",
    "SUMMARY_ROLE_ORDER",
    "SUMMARY_VARIANTS",
    "build_summary_card",
    "required_summary_roles",
]
