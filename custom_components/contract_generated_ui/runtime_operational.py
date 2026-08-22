"""Operational v3 layout for Contract Generated UI runtime rendering."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from . import runtime_renderer as base

RuntimeRenderError = base.RuntimeRenderError
GeneratedArtifact = base.GeneratedArtifact

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


def _role_groups(contract: Mapping[str, Any]) -> dict[str, list[str]]:
    contract_id = contract["metadata"]["id"]
    presentation = contract["spec"]["presentation"]
    groups = presentation.get("role_groups")
    if not isinstance(groups, dict) or set(groups) != set(GROUP_NAMES):
        raise RuntimeRenderError(
            f"contract {contract_id!r} requires explicit status/telemetry/diagnostic role_groups"
        )

    role_order = list(presentation["role_order"])
    flattened: list[str] = []
    normalized: dict[str, list[str]] = {}
    for group_name in GROUP_NAMES:
        group = groups.get(group_name)
        if not isinstance(group, list) or not all(isinstance(role, str) for role in group):
            raise RuntimeRenderError(
                f"contract {contract_id!r} role group {group_name!r} must be a role list"
            )
        normalized[group_name] = list(group)
        flattened.extend(group)

    if len(flattened) != len(set(flattened)):
        raise RuntimeRenderError(f"contract {contract_id!r} operational role groups overlap")
    if set(flattened) != set(role_order):
        raise RuntimeRenderError(
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
        raise RuntimeRenderError(
            "operational v3 requires rendered views and semantic trace views"
        )
    if len(views) != len(semantic_views):
        raise RuntimeRenderError("operational v3 view/trace count mismatch")

    for view, semantic_view in zip(views, semantic_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RuntimeRenderError(
                "operational v3 expects validated tiles_v1 masonry input"
            )
        cards = view.pop("cards", None)
        modules = semantic_view.get("modules")
        if not isinstance(cards, list) or not isinstance(modules, list):
            raise RuntimeRenderError("operational v3 module input missing")
        if len(cards) != len(modules) * 2:
            raise RuntimeRenderError(
                "operational v3 heading/grid pairs do not match modules"
            )

        sections: list[dict[str, Any]] = []
        for module_index, semantic_module in enumerate(modules):
            heading = cards[module_index * 2]
            grid = cards[module_index * 2 + 1]
            if not isinstance(heading, dict) or heading.get("type") != "heading":
                raise RuntimeRenderError(
                    "operational v3 module must begin with a heading"
                )
            if not isinstance(grid, dict) or grid.get("type") != "grid":
                raise RuntimeRenderError(
                    "operational v3 module must contain a tile grid"
                )
            tiles = grid.get("cards")
            semantic_roles = semantic_module.get("roles")
            if not isinstance(tiles, list) or not isinstance(semantic_roles, list):
                raise RuntimeRenderError("operational v3 module roles/tiles missing")
            if len(tiles) != len(semantic_roles):
                raise RuntimeRenderError("operational v3 role/tile count mismatch")

            contract_id = semantic_module.get("contract")
            contract = contracts.get(contract_id)
            if contract is None:
                raise RuntimeRenderError(
                    f"operational v3 missing contract {contract_id!r}"
                )
            groups = _role_groups(contract)

            tile_by_role: dict[str, dict[str, Any]] = {}
            semantic_by_role: dict[str, Mapping[str, Any]] = {}
            for tile, role in zip(tiles, semantic_roles, strict=True):
                role_name = role.get("role")
                if not isinstance(role_name, str) or not isinstance(tile, dict):
                    raise RuntimeRenderError("operational v3 invalid role/tile")
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
                    raise RuntimeRenderError(
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


def render_all_manifests(
    source_root: Path,
    generated_root: Path,
) -> list[GeneratedArtifact]:
    contracts = base._index_contracts(source_root)
    inventory, snapshot_ids = base._index_inventory(source_root)
    artifacts: list[GeneratedArtifact] = []

    manifests = list(base._documents(source_root / "manifests"))
    if not manifests:
        raise RuntimeRenderError("no panel manifests found")

    seen_ids: set[str] = set()
    for manifest_path in manifests:
        manifest = base._load_object(manifest_path)
        if manifest.get("kind") != "PanelManifest":
            raise RuntimeRenderError(f"unexpected manifest kind in {manifest_path}")
        manifest_id = manifest.get("metadata", {}).get("id")
        if not isinstance(manifest_id, str) or not manifest_id:
            raise RuntimeRenderError(f"manifest id missing in {manifest_path}")
        if manifest_id in seen_ids:
            raise RuntimeRenderError(f"duplicate manifest id {manifest_id!r}")
        seen_ids.add(manifest_id)

        dashboard, trace = base._render_manifest(
            manifest,
            contracts,
            inventory,
            snapshot_ids=snapshot_ids,
        )
        dashboard = _operational_dashboard(dashboard, trace, contracts)
        canonical = json.dumps(
            dashboard,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        trace = copy.deepcopy(trace)
        trace["renderer_engine_sha256"] = _layout_engine_sha256(
            trace["renderer_engine_sha256"]
        )
        trace["dashboard_sha256"] = hashlib.sha256(canonical).hexdigest()

        output_path = generated_root / f"{manifest_id}.yaml"
        trace_path = generated_root / f"{manifest_id}.meta.json"
        yaml_text = yaml.safe_dump(dashboard, allow_unicode=True, sort_keys=False)
        trace_text = json.dumps(trace, ensure_ascii=False, indent=2) + "\n"
        output_changed = base._atomic_write(output_path, yaml_text)
        trace_changed = base._atomic_write(trace_path, trace_text)
        artifacts.append(
            GeneratedArtifact(
                manifest_id=manifest_id,
                output_path=output_path,
                trace_path=trace_path,
                dashboard_sha256=trace["dashboard_sha256"],
                changed=output_changed or trace_changed,
            )
        )

    return artifacts


__all__ = [
    "GeneratedArtifact",
    "RuntimeRenderError",
    "render_all_manifests",
]
