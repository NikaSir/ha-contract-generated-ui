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

            tiles = grid.get("cards")
            roles = semantic_module.get("roles")
            if not isinstance(tiles, list) or not isinstance(roles, list):
                raise RuntimeRenderError("actions_home_v1 roles/tiles missing")
            if len(tiles) != len(roles):
                raise RuntimeRenderError("actions_home_v1 role/tile count mismatch")

            section_cards: list[dict[str, Any]] = [heading]
            for tile, role in zip(tiles, roles, strict=True):
                if not isinstance(tile, dict) or not isinstance(role, dict):
                    raise RuntimeRenderError("actions_home_v1 invalid role/tile")
                action = role.get("action")
                if not isinstance(action, dict):
                    raise RuntimeRenderError("actions_home_v1 role action missing")
                tile["grid_options"] = {
                    "columns": _grid_columns(action),
                    "rows": TILE_ROWS,
                }
                section_cards.append(tile)

            if len(section_cards) <= 1:
                raise RuntimeRenderError("actions_home_v1 module rendered no actions")
            sections.append({"type": "grid", "cards": section_cards})

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
