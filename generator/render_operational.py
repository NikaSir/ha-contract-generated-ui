from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .render import (
    RenderError,
    RenderResult,
    render_repository_manifest as render_tiles_repository_manifest,
    write_render_result,
)
from .validation import load_document

GROUP_NAMES = ("status", "telemetry", "diagnostic")
MAX_SECTION_COLUMNS = 2
STATUS_GRID_COLUMNS = 6
TELEMETRY_GRID_COLUMNS = 4
TILE_GRID_ROWS = 1


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}".encode("utf-8")
    ).hexdigest()


def _contracts(repo_root: Path) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for path in sorted((repo_root / "contracts").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        document = load_document(path)
        if not isinstance(document, dict) or document.get("kind") != "UIContract":
            continue
        contract_id = document.get("metadata", {}).get("id")
        if not isinstance(contract_id, str) or not contract_id:
            raise RenderError(f"contract id missing in {path}")
        result[contract_id] = document
    return result


def _role_groups(contract: Mapping[str, Any]) -> dict[str, list[str]]:
    contract_id = contract["metadata"]["id"]
    presentation = contract["spec"]["presentation"]
    groups = presentation.get("role_groups")
    if not isinstance(groups, dict) or set(groups) != set(GROUP_NAMES):
        raise RenderError(
            f"contract {contract_id!r} requires explicit status/telemetry/diagnostic role_groups"
        )

    role_order = list(presentation["role_order"])
    flattened: list[str] = []
    normalized: dict[str, list[str]] = {}
    for group_name in GROUP_NAMES:
        group = groups.get(group_name)
        if not isinstance(group, list) or not all(isinstance(role, str) for role in group):
            raise RenderError(
                f"contract {contract_id!r} role group {group_name!r} must be a role list"
            )
        normalized[group_name] = list(group)
        flattened.extend(group)

    if len(flattened) != len(set(flattened)):
        raise RenderError(f"contract {contract_id!r} operational role groups overlap")
    if set(flattened) != set(role_order):
        raise RenderError(
            f"contract {contract_id!r} operational role groups must cover every role exactly once"
        )
    return normalized


def _operational_dashboard(
    dashboard: dict[str, Any],
    trace: Mapping[str, Any],
    contracts: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    semantic_views = trace.get("semantics", {}).get("views")
    if not isinstance(views, list) or not isinstance(semantic_views, list):
        raise RenderError("operational v3 requires rendered views and semantic trace views")
    if len(views) != len(semantic_views):
        raise RenderError("operational v3 view/trace count mismatch")

    for view, semantic_view in zip(views, semantic_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RenderError("operational v3 expects validated tiles_v1 masonry input")
        cards = view.pop("cards", None)
        modules = semantic_view.get("modules")
        if not isinstance(cards, list) or not isinstance(modules, list):
            raise RenderError("operational v3 module input missing")
        if len(cards) != len(modules) * 2:
            raise RenderError("operational v3 heading/grid pairs do not match modules")

        sections: list[dict[str, Any]] = []
        for module_index, semantic_module in enumerate(modules):
            heading = cards[module_index * 2]
            grid = cards[module_index * 2 + 1]
            if not isinstance(heading, dict) or heading.get("type") != "heading":
                raise RenderError("operational v3 module must begin with a heading")
            if not isinstance(grid, dict) or grid.get("type") != "grid":
                raise RenderError("operational v3 module must contain a tile grid")
            tiles = grid.get("cards")
            semantic_roles = semantic_module.get("roles")
            if not isinstance(tiles, list) or not isinstance(semantic_roles, list):
                raise RenderError("operational v3 module roles/tiles missing")
            if len(tiles) != len(semantic_roles):
                raise RenderError("operational v3 role/tile count mismatch")

            contract_id = semantic_module.get("contract")
            contract = contracts.get(contract_id)
            if contract is None:
                raise RenderError(f"operational v3 missing contract {contract_id!r}")
            groups = _role_groups(contract)

            tile_by_role: dict[str, dict[str, Any]] = {}
            semantic_by_role: dict[str, Mapping[str, Any]] = {}
            for tile, role in zip(tiles, semantic_roles, strict=True):
                role_name = role.get("role")
                if not isinstance(role_name, str) or not isinstance(tile, dict):
                    raise RenderError("operational v3 invalid role/tile")
                tile_by_role[role_name] = tile
                semantic_by_role[role_name] = role

            section_cards: list[dict[str, Any]] = [heading]
            for role_name in groups["status"]:
                tile = tile_by_role.get(role_name)
                if tile is None:
                    continue
                tile["grid_options"] = {
                    "columns": STATUS_GRID_COLUMNS,
                    "rows": TILE_GRID_ROWS,
                }
                section_cards.append(tile)

            for role_name in groups["telemetry"]:
                tile = tile_by_role.get(role_name)
                if tile is None:
                    continue
                tile["grid_options"] = {
                    "columns": TELEMETRY_GRID_COLUMNS,
                    "rows": TILE_GRID_ROWS,
                }
                section_cards.append(tile)

            diagnostic_entities: list[dict[str, str]] = []
            for role_name in groups["diagnostic"]:
                role = semantic_by_role.get(role_name)
                if role is None:
                    continue
                if role.get("action") != {"kind": "more_info"}:
                    raise RenderError(
                        f"operational v3 diagnostic role {role_name!r} must use more_info"
                    )
                diagnostic_entities.append(
                    {
                        "entity": role["entity_id"],
                        "name": role["label"],
                    }
                )
            if diagnostic_entities:
                section_cards.append(
                    {
                        "type": "entities",
                        "title": "Диагностика",
                        "show_header_toggle": False,
                        "entities": diagnostic_entities,
                    }
                )

            sections.append({"type": "grid", "cards": section_cards})

        view["type"] = "sections"
        view["max_columns"] = min(MAX_SECTION_COLUMNS, max(1, len(sections)))
        view["dense_section_placement"] = True
        view["sections"] = sections

    return transformed


def render_repository_manifest(repo_root: Path, manifest_path: Path) -> RenderResult:
    base = render_tiles_repository_manifest(repo_root, manifest_path)
    dashboard = _operational_dashboard(base.dashboard, base.trace, _contracts(repo_root))
    canonical = json.dumps(
        dashboard,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    trace = copy.deepcopy(base.trace)
    trace["renderer_engine_sha256"] = _layout_engine_sha256(
        base.trace["renderer_engine_sha256"]
    )
    trace["dashboard_sha256"] = hashlib.sha256(canonical).hexdigest()
    return RenderResult(dashboard=dashboard, trace=trace)


__all__ = [
    "RenderError",
    "RenderResult",
    "render_repository_manifest",
    "write_render_result",
]
