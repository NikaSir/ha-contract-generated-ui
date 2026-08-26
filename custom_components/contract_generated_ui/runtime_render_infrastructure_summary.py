from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any, Mapping

from . import runtime_renderer as base
from .runtime_infrastructure_summary import (
    SUMMARY_RENDERER,
    build_summary_card,
    required_summary_roles,
)

RenderError = base.RuntimeRenderError

MAX_SECTION_COLUMNS = 2


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    helper_sha = hashlib.sha256(
        (Path(__file__).parent / "runtime_infrastructure_summary.py").read_bytes()
    ).hexdigest()
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}:{helper_sha}".encode("utf-8")
    ).hexdigest()


def _role_entities(semantic_module: Mapping[str, Any]) -> dict[str, str]:
    roles = semantic_module.get("roles")
    if not isinstance(roles, list):
        raise RenderError("infrastructure summary roles missing")
    return {
        role["role"]: role["entity_id"]
        for role in roles
        if isinstance(role, Mapping)
        and isinstance(role.get("role"), str)
        and isinstance(role.get("entity_id"), str)
    }


def _power_quality_prefix(entities: Mapping[str, str]) -> str:
    required = (
        "grid_ok",
        "meter_online",
        "phase_loss",
        "phase_a_present",
        "phase_b_present",
        "phase_c_present",
        "voltage_a",
        "voltage_b",
        "voltage_c",
    )
    missing = [name for name in required if name not in entities]
    if missing:
        raise RenderError("infrastructure power quality missing roles: " + ", ".join(missing))

    grid = entities["grid_ok"]
    meter = entities["meter_online"]
    phase_loss = entities["phase_loss"]
    phase_a = entities["phase_a_present"]
    phase_b = entities["phase_b_present"]
    phase_c = entities["phase_c_present"]
    voltage_a = entities["voltage_a"]
    voltage_b = entities["voltage_b"]
    voltage_c = entities["voltage_c"]
    return (
        "{% set reliable = has_value('" + grid + "') and has_value('" + meter + "') and has_value('" + phase_loss + "') and has_value('" + phase_a + "') and has_value('" + phase_b + "') and has_value('" + phase_c + "') and is_number(states('" + voltage_a + "')) and is_number(states('" + voltage_b + "')) and is_number(states('" + voltage_c + "')) %}"
        "{% set event = reliable and (is_state('" + grid + "','off') or is_state('" + meter + "','off') or is_state('" + phase_loss + "','on') or is_state('" + phase_a + "','off') or is_state('" + phase_b + "','off') or is_state('" + phase_c + "','off')) %}"
        "{% if reliable %}{% set volts=[states('" + voltage_a + "')|float,states('" + voltage_b + "')|float,states('" + voltage_c + "')|float] %}{% else %}{% set volts=[] %}{% endif %}"
    )


def _power_quality_short(entities: Mapping[str, str]) -> str:
    return (
        _power_quality_prefix(entities)
        + "{% if not reliable %}⚪ Нет данных"
        + "{% elif event or (volts|min)<125 or (volts|max)>275 %}🔴 Авария"
        + "{% elif (volts|min)<150 or (volts|max)>265 %}🟠 Рабочий предел"
        + "{% else %}🟢 Нормально{% endif %}"
    )


def _power_quality_heading(entities: Mapping[str, str]) -> str:
    return (
        _power_quality_prefix(entities)
        + "## {% if not reliable %}⚪ Данные входящей сети неполные"
        + "{% elif event or (volts|min)<125 or (volts|max)>275 %}🔴 Авария входящей сети"
        + "{% elif (volts|min)<150 or (volts|max)>265 %}🟠 Рабочий предел входящей сети"
        + "{% else %}🟢 Входящая сеть в норме{% endif %}"
    )


def _polish_power_summary(
    card: dict[str, Any],
    semantic_module: Mapping[str, Any],
    *,
    view_id: str,
) -> None:
    if semantic_module.get("contract") != "infrastructure.power_grid":
        return
    entities = _role_entities(semantic_module)
    voltage_entities = [
        entities.get("voltage_a"),
        entities.get("voltage_b"),
        entities.get("voltage_c"),
    ]
    if not all(isinstance(entity, str) for entity in voltage_entities):
        raise RenderError("infrastructure power voltage roles missing")

    if view_id == "overview":
        content = card.get("content")
        if not isinstance(content, str):
            raise RenderError("infrastructure power overview content missing")
        grid = entities["grid_ok"]
        meter = entities["meter_online"]
        phase_loss = entities["phase_loss"]
        phase_a = entities["phase_a_present"]
        phase_b = entities["phase_b_present"]
        phase_c = entities["phase_c_present"]
        voltage_a = entities["voltage_a"]
        voltage_b = entities["voltage_b"]
        voltage_c = entities["voltage_c"]
        old_prefix = (
            "{% set before_reliable = has_value('" + grid + "') and has_value('" + meter + "') and has_value('" + phase_loss + "') and has_value('" + phase_a + "') and has_value('" + phase_b + "') and has_value('" + phase_c + "') and has_value('" + voltage_a + "') and has_value('" + voltage_b + "') and has_value('" + voltage_c + "') and has_value('" + entities["voltage_imbalance"] + "') and has_value('" + entities["total_power"] + "') %}"
            "\n{% set before_event = before_reliable and (is_state('" + grid + "', 'off') or is_state('" + meter + "', 'off') or is_state('" + phase_loss + "', 'on') or is_state('" + phase_a + "', 'off') or is_state('" + phase_b + "', 'off') or is_state('" + phase_c + "', 'off')) %}"
        )
        old_status = (
            "{% if not before_reliable %}⚪ Нет данных"
            "{% elif before_event %}🔴 Авария"
            "{% else %}🟢 Контроль{% endif %}"
        )
        if old_prefix not in content or old_status not in content:
            raise RenderError("infrastructure power overview template shape changed")
        card["content"] = content.replace(old_prefix, _power_quality_prefix(entities)).replace(
            old_status, _power_quality_short(entities)
        )
        return

    if view_id not in {"power-overview", "power-before"}:
        return
    cards = card.get("cards")
    if not isinstance(cards, list) or not cards or not isinstance(cards[0], dict):
        raise RenderError("infrastructure power detail status card missing")
    status_card = cards[0]
    entity_ids = status_card.get("entity_id")
    if not isinstance(entity_ids, list):
        raise RenderError("infrastructure power detail entity tracking missing")
    for entity in voltage_entities:
        if entity not in entity_ids:
            entity_ids.append(entity)

    if view_id == "power-before":
        status_card["content"] = (
            _power_quality_heading(entities)
            + "\nКонтроль **до стабилизаторов** по паспорту LIDER PS7500W-30: номинальный диапазон **150–265 В**, рабочий диапазон **125–275 В**."
        )
        return

    line_mode = entities.get("non_interruptible_mode")
    line_stale = entities.get("non_interruptible_data_stale")
    if not isinstance(line_mode, str) or not isinstance(line_stale, str):
        raise RenderError("infrastructure boiler-line status roles missing")
    status_card["content"] = (
        _power_quality_heading(entities)
        + "\nТри физические точки контроля: **до стабилизаторов**, **после стабилизаторов**, **неотключаемая линия**."
        + "\n\nДо стабилизаторов применяются паспортные диапазоны LIDER PS7500W-30; после стабилизаторов — диапазон ГОСТ **198–242 В**."
        + "\n\nЛиния котла: **{{ state_translated('" + line_mode + "') if has_value('" + line_mode + "') else 'Недоступно' }}** · "
        + "{% if not has_value('" + line_stale + "') %}свежесть неизвестна"
        + "{% elif is_state('" + line_stale + "', 'on') %}данные устарели"
        + "{% else %}данные актуальны{% endif %}."
    )


def _polish_ups_summary(card: dict[str, Any], semantic_module: Mapping[str, Any]) -> None:
    if semantic_module.get("contract") != "infrastructure.ups":
        return
    roles = semantic_module.get("roles")
    if not isinstance(roles, list):
        raise RenderError("infrastructure UPS summary roles missing")
    role_entities = {
        role.get("role"): role.get("entity_id")
        for role in roles
        if isinstance(role, Mapping)
        and isinstance(role.get("role"), str)
        and isinstance(role.get("entity_id"), str)
    }
    stale = role_entities.get("data_stale")
    content = card.get("content")
    if not isinstance(stale, str) or not isinstance(content, str):
        raise RenderError("infrastructure UPS summary freshness source missing")
    old = (
        "{% if not has_value('" + stale + "') %}Свежесть неизвестна"
        "{% elif is_state('" + stale + "', 'on') %}Данные устарели"
        "{% else %}Данные актуальны{% endif %}"
    )
    new = (
        "{% if not reliable %}Данные недоступны"
        "{% elif not has_value('" + stale + "') %}Свежесть неизвестна"
        "{% elif is_state('" + stale + "', 'on') %}Данные устарели"
        "{% else %}Данные актуальны{% endif %}"
    )
    if old not in content:
        raise RenderError("infrastructure UPS freshness template shape changed")
    card["content"] = content.replace(old, new)


def _summary_dashboard(
    dashboard: Mapping[str, Any],
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    semantic_views = trace.get("semantics", {}).get("views")
    if not isinstance(views, list) or not isinstance(semantic_views, list):
        raise RenderError("infrastructure summary requires dashboard and semantic views")
    if len(views) != len(semantic_views):
        raise RenderError("infrastructure summary view/trace count mismatch")

    for view, semantic_view in zip(views, semantic_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RenderError("infrastructure summary expects validated masonry input")
        view_id = semantic_view.get("id")
        if not isinstance(view_id, str):
            raise RenderError("infrastructure summary view id missing")
        cards = view.pop("cards", None)
        modules = semantic_view.get("modules")
        if not isinstance(cards, list) or not isinstance(modules, list):
            raise RenderError("infrastructure summary module input missing")
        if len(cards) != len(modules) * 2:
            raise RenderError("infrastructure summary heading/grid pairs do not match modules")

        sections: list[dict[str, Any]] = []
        for semantic_module in modules:
            if not isinstance(semantic_module, Mapping):
                raise RenderError("infrastructure summary module must be an object")
            try:
                card = build_summary_card(semantic_module, view_id=view_id)
            except ValueError as err:
                raise RenderError(str(err)) from err
            _polish_power_summary(card, semantic_module, view_id=view_id)
            _polish_ups_summary(card, semantic_module)
            sections.append({"type": "grid", "cards": [card]})

        if not sections:
            raise RenderError("infrastructure summary rendered no sections")
        view["type"] = "sections"
        view["max_columns"] = min(MAX_SECTION_COLUMNS, max(1, len(sections)))
        view["dense_section_placement"] = True
        if view_id.startswith("power-"):
            view["subview"] = True
            view["max_columns"] = 1
        view["sections"] = sections

    return transformed


def _filter_trace(trace: Mapping[str, Any]) -> dict[str, Any]:
    filtered = copy.deepcopy(trace)
    semantic_views = filtered.get("semantics", {}).get("views")
    if not isinstance(semantic_views, list):
        raise RenderError("infrastructure summary trace has no semantic views")

    keep_binding_keys: set[str] = set()
    for view in semantic_views:
        view_id = view.get("id")
        modules = view.get("modules")
        if not isinstance(view_id, str) or not isinstance(modules, list):
            raise RenderError("infrastructure summary trace view is incomplete")
        for module in modules:
            contract_id = module.get("contract")
            instance = module.get("instance")
            roles = module.get("roles")
            if (
                not isinstance(contract_id, str)
                or not isinstance(instance, str)
                or not isinstance(roles, list)
            ):
                raise RenderError("infrastructure summary trace module is incomplete")
            try:
                required = required_summary_roles(contract_id, view_id)
            except ValueError as err:
                raise RenderError(str(err)) from err
            role_by_name = {
                role.get("role"): role
                for role in roles
                if isinstance(role, Mapping) and isinstance(role.get("role"), str)
            }
            missing = [role_name for role_name in required if role_name not in role_by_name]
            if missing:
                raise RenderError(
                    f"infrastructure summary trace {contract_id!r} missing roles: {', '.join(missing)}"
                )
            module["roles"] = [role_by_name[role_name] for role_name in required]
            for role_name in required:
                keep_binding_keys.add(f"{view_id}.{instance}.{role_name}")

    bindings = filtered.get("bindings")
    if not isinstance(bindings, dict):
        raise RenderError("infrastructure summary trace bindings missing")
    filtered["bindings"] = {
        key: value for key, value in bindings.items() if key in keep_binding_keys
    }
    return filtered


__all__ = [
    "SUMMARY_RENDERER",
    "_filter_trace",
    "_layout_engine_sha256",
    "_summary_dashboard",
]
