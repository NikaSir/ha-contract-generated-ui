from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from . import house_base as _base

HOUSE_RENDERER = _base.HOUSE_RENDERER
MAX_COLUMNS = _base.MAX_COLUMNS
RenderError = _base.RenderError


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    """Fingerprint the accepted House renderer plus the mobile-polish layer."""
    base_sha = _base._layout_engine_sha256(base_engine_sha256)
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(f"{base_sha}:{layer_sha}".encode("utf-8")).hexdigest()


def _trace_entities(trace: Mapping[str, Any]) -> dict[str, str]:
    views = trace.get("semantics", {}).get("views")
    if not isinstance(views, list) or len(views) != 1:
        raise RenderError("house_home_v1 polish requires exactly one semantic view")
    modules = views[0].get("modules")
    if not isinstance(modules, list) or len(modules) != 1:
        raise RenderError("house_home_v1 polish requires exactly one semantic module")
    roles = modules[0].get("roles")
    if not isinstance(roles, list):
        raise RenderError("house_home_v1 polish semantic roles missing")

    result: dict[str, str] = {}
    for role in roles:
        if not isinstance(role, dict):
            continue
        name = role.get("role")
        entity_id = role.get("entity_id")
        if isinstance(name, str) and isinstance(entity_id, str):
            result[name] = entity_id
    return result


def _drop_duplicate_title(view: dict[str, Any]) -> None:
    sections = view.get("sections")
    if not isinstance(sections, list) or not sections:
        raise RenderError("house_home_v1 polish sections missing")
    first = sections[0]
    cards = first.get("cards") if isinstance(first, dict) else None
    title = view.get("title")
    if (
        not isinstance(cards, list)
        or len(cards) != 1
        or not isinstance(cards[0], dict)
        or cards[0].get("type") != "heading"
        or cards[0].get("heading") != title
    ):
        raise RenderError("house_home_v1 duplicate title section shape changed")
    sections.pop(0)


def _temperature_suffix(entity_id: str | None) -> str:
    if not entity_id:
        return ""
    return (
        "{% if is_number(states('" + entity_id + "')) %} · "
        "{{ states('" + entity_id + "')|float|round(1) }} °C{% endif %}"
    )


def _replace_heating_summary(view: dict[str, Any], entities: Mapping[str, str]) -> None:
    required = (
        "heating_main",
        "heating_reserve",
        "heating_radiators",
        "heating_floor",
        "heating_circulation",
    )
    missing = [name for name in required if name not in entities]
    if missing:
        raise RenderError("house_home_v1 heating summary missing roles: " + ", ".join(missing))

    main = entities["heating_main"]
    reserve = entities["heating_reserve"]
    circuits = [
        entities["heating_radiators"],
        entities["heating_floor"],
        entities["heating_circulation"],
    ]
    main_text = "Основной" + _temperature_suffix(entities.get("heating_main_temp"))
    reserve_text = "Резервный" + _temperature_suffix(entities.get("heating_reserve_temp"))
    prefix = (
        "{% set main=states('" + main + "') %}"
        "{% set reserve=states('" + reserve + "') %}"
        "{% set circuits=" + repr(circuits) + " %}"
        "{% set ns=namespace(active=0,bad=0) %}"
        "{% for e in circuits %}"
        "{% if is_state(e,'on') %}{% set ns.active=ns.active+1 %}"
        "{% elif states(e) in ['unknown','unavailable'] %}{% set ns.bad=ns.bad+1 %}{% endif %}"
        "{% endfor %}"
    )
    secondary = (
        prefix
        + "{% if main=='on' %}" + main_text
        + "{% elif reserve=='on' %}" + reserve_text
        + "{% elif ns.active>0 %}Контуры активны"
        + "{% elif main in ['unknown','unavailable'] or reserve in ['unknown','unavailable'] or ns.bad>0 %}Нет данных"
        + "{% else %}Система в ожидании{% endif %}"
    )
    icon_color = (
        prefix
        + "{% if main=='on' or reserve=='on' or ns.active>0 %}orange"
        + "{% elif main in ['unknown','unavailable'] or reserve in ['unknown','unavailable'] or ns.bad>0 %}grey"
        + "{% else %}green{% endif %}"
    )

    sections = view.get("sections")
    if not isinstance(sections, list):
        raise RenderError("house_home_v1 polish sections missing")
    for section in sections:
        cards = section.get("cards") if isinstance(section, dict) else None
        if not isinstance(cards, list) or not cards:
            continue
        heading = cards[0]
        if not isinstance(heading, dict) or heading.get("heading") != "Дом сейчас":
            continue
        for card in cards[1:]:
            if (
                isinstance(card, dict)
                and card.get("type") == "custom:mushroom-template-card"
                and card.get("primary") == "Отопление"
            ):
                card["secondary"] = secondary
                card["icon_color"] = icon_color
                return
    raise RenderError("house_home_v1 heating summary card not found")


def render_house_dashboard(
    dashboard: dict[str, Any],
    trace: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Render House and apply the accepted iPhone field-test polish."""
    rendered = _base.render_house_dashboard(dashboard, trace, manifest)
    views = rendered.get("views")
    if not isinstance(views, list) or len(views) != 1 or not isinstance(views[0], dict):
        raise RenderError("house_home_v1 polish requires exactly one rendered view")
    view = views[0]
    _drop_duplicate_title(view)
    _replace_heating_summary(view, _trace_entities(trace))
    return rendered


__all__ = ["HOUSE_RENDERER", "MAX_COLUMNS", "_layout_engine_sha256", "render_house_dashboard"]
