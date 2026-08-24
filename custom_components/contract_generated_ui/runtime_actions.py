"""Action-center layout for Contract Generated UI runtime rendering."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from . import runtime_renderer as base

RuntimeRenderError = base.RuntimeRenderError

ACTIONS_RENDERER = "actions_home_v1"
MAX_COLUMNS = 2
TOGGLE_COLUMNS = 6
MORE_INFO_COLUMNS = 6
NAVIGATE_COLUMNS = 12
TILE_ROWS = 1

ACCESS_INSTANCE = "access"
CLEANING_INSTANCE = "cleaning"
CLEANING_DETAILS_PATH = "/dashboard-s8-omni"
IRRIGATION_PATH = "/dashboard-irrigation"


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}".encode("utf-8")
    ).hexdigest()


def _grid_columns(action: Mapping[str, Any]) -> int:
    kind = action.get("kind")
    if kind == "navigate":
        return NAVIGATE_COLUMNS
    if kind == "toggle":
        return TOGGLE_COLUMNS
    if kind in {"more_info", "none"}:
        return MORE_INFO_COLUMNS
    raise RuntimeRenderError(f"actions_home_v1 unsupported action kind {kind!r}")


def _role_entity(semantic_module: Mapping[str, Any], role_name: str) -> str:
    roles = semantic_module.get("roles")
    if not isinstance(roles, list):
        raise RuntimeRenderError("actions_home_v1 semantic roles missing")
    for role in roles:
        if not isinstance(role, dict) or role.get("role") != role_name:
            continue
        entity_id = role.get("entity_id")
        if isinstance(entity_id, str) and entity_id:
            return entity_id
    raise RuntimeRenderError(f"actions_home_v1 role {role_name!r} missing")


def _swing_gate_placeholder() -> dict[str, Any]:
    return {
        "type": "custom:mushroom-template-card",
        "primary": "Распашные ворота",
        "secondary": "Физический датчик не установлен",
        "icon": "mdi:gate",
        "icon_color": "grey",
        "tap_action": {"action": "none"},
        "hold_action": {"action": "none"},
        "grid_options": {"columns": 6},
    }


def _vacuum_command(
    entity_id: str,
    *,
    primary: str,
    icon: str,
    service: str,
    confirmation: str,
) -> dict[str, Any]:
    if not entity_id.startswith("vacuum."):
        raise RuntimeRenderError(
            f"actions_home_v1 vacuum command requires vacuum entity, got {entity_id!r}"
        )
    if service not in {"vacuum.start", "vacuum.return_to_base"}:
        raise RuntimeRenderError(f"actions_home_v1 unsafe vacuum service {service!r}")
    return {
        "type": "custom:mushroom-template-card",
        "entity": entity_id,
        "primary": primary,
        "secondary": "S8 OMNI",
        "icon": icon,
        "icon_color": "blue",
        "badge_icon": "mdi:gesture-tap-button",
        "badge_color": "blue",
        "tap_action": {
            "action": "perform-action",
            "perform_action": service,
            "target": {"entity_id": entity_id},
            "confirmation": {"text": confirmation},
        },
        "hold_action": {"action": "more-info"},
        "grid_options": {"columns": 6},
    }


def _navigate_card(
    primary: str,
    secondary: str,
    icon: str,
    path: str,
) -> dict[str, Any]:
    return {
        "type": "custom:mushroom-template-card",
        "primary": primary,
        "secondary": secondary,
        "icon": icon,
        "icon_color": "blue",
        "tap_action": {"action": "navigate", "navigation_path": path},
        "hold_action": {"action": "none"},
        "grid_options": {"columns": 12},
    }


def _irrigation_section() -> dict[str, Any]:
    return {
        "type": "grid",
        "cards": [
            {
                "type": "heading",
                "heading": "Полив",
                "heading_style": "title",
                "icon": "mdi:sprinkler-variant",
            },
            _navigate_card(
                "Полив",
                "Ручной запуск, зоны и программы",
                "mdi:sprinkler-variant",
                IRRIGATION_PATH,
            ),
        ],
    }


def _real_panel_enhancements(
    section_cards: list[dict[str, Any]],
    semantic_module: Mapping[str, Any],
) -> None:
    instance = semantic_module.get("instance")
    if instance == ACCESS_INSTANCE:
        section_cards.append(_swing_gate_placeholder())
        return
    if instance != CLEANING_INSTANCE:
        return

    vacuum_entity = _role_entity(semantic_module, "vacuum_state")
    section_cards.extend(
        [
            _vacuum_command(
                vacuum_entity,
                primary="Начать уборку",
                icon="mdi:play",
                service="vacuum.start",
                confirmation="Начать уборку S8 OMNI?",
            ),
            _vacuum_command(
                vacuum_entity,
                primary="На базу",
                icon="mdi:home-import-outline",
                service="vacuum.return_to_base",
                confirmation="Отправить S8 OMNI на базу?",
            ),
            _navigate_card(
                "Подробнее",
                "S8 OMNI",
                "mdi:arrow-right-circle-outline",
                CLEANING_DETAILS_PATH,
            ),
        ]
    )


def render_actions_dashboard(
    dashboard: dict[str, Any],
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    semantic_views = trace.get("semantics", {}).get("views")
    if not isinstance(views, list) or not isinstance(semantic_views, list):
        raise RuntimeRenderError(
            "actions_home_v1 requires rendered views and semantic trace views"
        )
    if len(views) != len(semantic_views):
        raise RuntimeRenderError("actions_home_v1 view/trace count mismatch")

    for view, semantic_view in zip(views, semantic_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RuntimeRenderError(
                "actions_home_v1 expects validated tiles_v1 masonry input"
            )
        cards = view.pop("cards", None)
        modules = semantic_view.get("modules")
        if not isinstance(cards, list) or not isinstance(modules, list):
            raise RuntimeRenderError("actions_home_v1 module input missing")
        if len(cards) != len(modules) * 2:
            raise RuntimeRenderError(
                "actions_home_v1 heading/grid pairs do not match modules"
            )

        sections: list[dict[str, Any]] = []
        complete_main_panel = False
        for module_index, semantic_module in enumerate(modules):
            heading = cards[module_index * 2]
            grid = cards[module_index * 2 + 1]
            if not isinstance(heading, dict) or heading.get("type") != "heading":
                raise RuntimeRenderError(
                    "actions_home_v1 module must begin with a heading"
                )
            if not isinstance(grid, dict) or grid.get("type") != "grid":
                raise RuntimeRenderError(
                    "actions_home_v1 module must contain a tile grid"
                )
            if not isinstance(semantic_module, dict):
                raise RuntimeRenderError("actions_home_v1 invalid semantic module")

            tiles = grid.get("cards")
            roles = semantic_module.get("roles")
            if not isinstance(tiles, list) or not isinstance(roles, list):
                raise RuntimeRenderError("actions_home_v1 roles/tiles missing")
            if len(tiles) != len(roles):
                raise RuntimeRenderError("actions_home_v1 role/tile count mismatch")

            instance = semantic_module.get("instance")
            if instance in {ACCESS_INSTANCE, CLEANING_INSTANCE}:
                complete_main_panel = True

            section_cards: list[dict[str, Any]] = [heading]
            for tile, role in zip(tiles, roles, strict=True):
                if not isinstance(tile, dict) or not isinstance(role, dict):
                    raise RuntimeRenderError("actions_home_v1 invalid role/tile")
                action = role.get("action")
                if not isinstance(action, dict):
                    raise RuntimeRenderError("actions_home_v1 role action missing")
                columns = _grid_columns(action)
                role_name = role.get("role")
                if instance == CLEANING_INSTANCE:
                    if role_name == "vacuum_state":
                        columns = 12
                    elif role_name in {"station_clean", "station_dust", "station_dry"}:
                        columns = 4
                tile["grid_options"] = {"columns": columns, "rows": TILE_ROWS}
                section_cards.append(tile)

            _real_panel_enhancements(section_cards, semantic_module)

            if len(section_cards) <= 1:
                raise RuntimeRenderError("actions_home_v1 module rendered no actions")
            sections.append({"type": "grid", "cards": section_cards})

        if complete_main_panel:
            sections.append(_irrigation_section())

        if not sections:
            raise RuntimeRenderError("actions_home_v1 rendered no sections")
        view["type"] = "sections"
        view["max_columns"] = min(MAX_COLUMNS, max(1, len(sections)))
        view["dense_section_placement"] = True
        view["sections"] = sections

    return transformed


def dashboard_sha256(dashboard: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        dashboard,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


__all__ = [
    "ACTIONS_RENDERER",
    "RuntimeRenderError",
    "dashboard_sha256",
    "render_actions_dashboard",
]
