"""Operational layout for Contract Generated UI runtime rendering."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from . import runtime_renderer as base
from .runtime_house import (
    HOUSE_RENDERER,
    _layout_engine_sha256 as _house_layout_engine_sha256,
    render_house_dashboard,
)

RuntimeRenderError = base.RuntimeRenderError
GeneratedArtifact = base.GeneratedArtifact

GROUP_NAMES = ("status", "telemetry", "diagnostic")
DEFAULT_RENDERER = "operational_v1"
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


def _module_group_selection(manifest: Mapping[str, Any]) -> dict[tuple[str, str], tuple[str, ...]]:
    selections: dict[tuple[str, str], tuple[str, ...]] = {}
    views = manifest.get("spec", {}).get("views")
    if not isinstance(views, list):
        raise RuntimeRenderError("operational renderer requires manifest views")

    for view in views:
        if not isinstance(view, dict):
            raise RuntimeRenderError("operational renderer manifest view must be an object")
        view_id = view.get("id")
        modules = view.get("modules")
        if not isinstance(view_id, str) or not isinstance(modules, list):
            raise RuntimeRenderError("operational renderer manifest view id/modules missing")
        for module in modules:
            if not isinstance(module, dict):
                raise RuntimeRenderError("operational renderer manifest module must be an object")
            contract_id = module.get("contract")
            instance = module.get("instance") or contract_id
            if not isinstance(instance, str):
                raise RuntimeRenderError("operational renderer module instance missing")
            raw_groups = module.get("groups", list(GROUP_NAMES))
            if (
                not isinstance(raw_groups, list)
                or not raw_groups
                or not all(group in GROUP_NAMES for group in raw_groups)
                or len(raw_groups) != len(set(raw_groups))
            ):
                raise RuntimeRenderError(
                    f"module {view_id!r}.{instance!r} has invalid operational groups"
                )
            key = (view_id, instance)
            if key in selections:
                raise RuntimeRenderError(
                    f"duplicate operational module selector {view_id}.{instance}"
                )
            selections[key] = tuple(raw_groups)
    return selections


def _selected_role_names(
    groups: Mapping[str, list[str]],
    selected_groups: tuple[str, ...],
) -> set[str]:
    return {
        role
        for group_name in selected_groups
        for role in groups[group_name]
    }


def _diagnostic_entities_card(
    entities: list[dict[str, str]],
    selected_groups: tuple[str, ...],
) -> dict[str, Any]:
    card: dict[str, Any] = {
        "type": "entities",
        "show_header_toggle": False,
        "entities": entities,
    }
    if selected_groups != ("diagnostic",):
        card["title"] = "Диагностика"
    return card


def _manifest_renderer(manifest: Mapping[str, Any]) -> str:
    views = manifest.get("spec", {}).get("views")
    if not isinstance(views, list) or not views:
        raise RuntimeRenderError("panel manifest has no views")
    renderers: set[str] = set()
    for view in views:
        if not isinstance(view, dict):
            raise RuntimeRenderError("panel manifest view must be an object")
        renderer = view.get("renderer", DEFAULT_RENDERER)
        if renderer not in {DEFAULT_RENDERER, HOUSE_RENDERER}:
            raise RuntimeRenderError(f"unsupported view renderer {renderer!r}")
        renderers.add(renderer)
    if len(renderers) != 1:
        raise RuntimeRenderError("mixed view renderers are not supported in one manifest")
    return renderers.pop()


def _operational_dashboard(
    dashboard: dict[str, Any],
    trace: Mapping[str, Any],
    contracts: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    semantic_views = trace.get("semantics", {}).get("views")
    if not isinstance(views, list) or not isinstance(semantic_views, list):
        raise RuntimeRenderError(
            "operational renderer requires rendered views and semantic trace views"
        )
    if len(views) != len(semantic_views):
        raise RuntimeRenderError("operational renderer view/trace count mismatch")

    selections = _module_group_selection(manifest)

    for view, semantic_view in zip(views, semantic_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RuntimeRenderError(
                "operational renderer expects validated tiles_v1 masonry input"
            )
        cards = view.pop("cards", None)
        modules = semantic_view.get("modules")
        view_id = semantic_view.get("id")
        if not isinstance(cards, list) or not isinstance(modules, list) or not isinstance(view_id, str):
            raise RuntimeRenderError("operational renderer module/view input missing")
        if len(cards) != len(modules) * 2:
            raise RuntimeRenderError(
                "operational renderer heading/grid pairs do not match modules"
            )

        sections: list[dict[str, Any]] = []
        for module_index, semantic_module in enumerate(modules):
            heading = cards[module_index * 2]
            grid = cards[module_index * 2 + 1]
            if not isinstance(heading, dict) or heading.get("type") != "heading":
                raise RuntimeRenderError(
                    "operational renderer module must begin with a heading"
                )
            if not isinstance(grid, dict) or grid.get("type") != "grid":
                raise RuntimeRenderError(
                    "operational renderer module must contain a tile grid"
                )
            tiles = grid.get("cards")
            semantic_roles = semantic_module.get("roles")
            if not isinstance(tiles, list) or not isinstance(semantic_roles, list):
                raise RuntimeRenderError("operational renderer module roles/tiles missing")
            if len(tiles) != len(semantic_roles):
                raise RuntimeRenderError("operational renderer role/tile count mismatch")

            contract_id = semantic_module.get("contract")
            instance = semantic_module.get("instance")
            contract = contracts.get(contract_id)
            if contract is None or not isinstance(instance, str):
                raise RuntimeRenderError(
                    f"operational renderer missing contract/instance {contract_id!r}"
                )
            groups = _role_groups(contract)
            selected_groups = selections.get((view_id, instance), GROUP_NAMES)

            tile_by_role: dict[str, dict[str, Any]] = {}
            semantic_by_role: dict[str, Mapping[str, Any]] = {}
            for tile, role in zip(tiles, semantic_roles, strict=True):
                role_name = role.get("role")
                if not isinstance(role_name, str) or not isinstance(tile, dict):
                    raise RuntimeRenderError("operational renderer invalid role/tile")
                tile_by_role[role_name] = tile
                semantic_by_role[role_name] = role

            section_cards: list[dict[str, Any]] = [heading]
            if "status" in selected_groups:
                for role_name in groups["status"]:
                    tile = tile_by_role.get(role_name)
                    if tile is None:
                        continue
                    tile["grid_options"] = {
                        "columns": STATUS_GRID_COLUMNS,
                        "rows": TILE_GRID_ROWS,
                    }
                    section_cards.append(tile)

            if "telemetry" in selected_groups:
                for role_name in groups["telemetry"]:
                    tile = tile_by_role.get(role_name)
                    if tile is None:
                        continue
                    tile["grid_options"] = {
                        "columns": TELEMETRY_GRID_COLUMNS,
                        "rows": TILE_GRID_ROWS,
                    }
                    section_cards.append(tile)

            if "diagnostic" in selected_groups:
                diagnostic_entities: list[dict[str, str]] = []
                for role_name in groups["diagnostic"]:
                    role = semantic_by_role.get(role_name)
                    if role is None:
                        continue
                    if role.get("action") != {"kind": "more_info"}:
                        raise RuntimeRenderError(
                            f"operational diagnostic role {role_name!r} must use more_info"
                        )
                    diagnostic_entities.append(
                        {
                            "entity": role["entity_id"],
                            "name": role["label"],
                        }
                    )
                if diagnostic_entities:
                    section_cards.append(
                        _diagnostic_entities_card(diagnostic_entities, selected_groups)
                    )

            if len(section_cards) > 1:
                sections.append({"type": "grid", "cards": section_cards})

        if not sections:
            raise RuntimeRenderError(f"operational view {view_id!r} rendered no sections")
        view["type"] = "sections"
        view["max_columns"] = min(MAX_SECTION_COLUMNS, max(1, len(sections)))
        view["dense_section_placement"] = True
        view["sections"] = sections

    return transformed


def _filter_trace(
    trace: Mapping[str, Any],
    contracts: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    filtered = copy.deepcopy(trace)
    selections = _module_group_selection(manifest)
    semantic_views = filtered.get("semantics", {}).get("views")
    if not isinstance(semantic_views, list):
        raise RuntimeRenderError("operational trace has no semantic views")

    keep_binding_keys: set[str] = set()
    for view in semantic_views:
        view_id = view.get("id")
        modules = view.get("modules")
        if not isinstance(view_id, str) or not isinstance(modules, list):
            raise RuntimeRenderError("operational trace view is incomplete")
        for module in modules:
            contract_id = module.get("contract")
            instance = module.get("instance")
            roles = module.get("roles")
            contract = contracts.get(contract_id)
            if contract is None or not isinstance(instance, str) or not isinstance(roles, list):
                raise RuntimeRenderError("operational trace module is incomplete")
            groups = _role_groups(contract)
            selected_groups = selections.get((view_id, instance), GROUP_NAMES)
            selected_roles = _selected_role_names(groups, selected_groups)
            module["roles"] = [role for role in roles if role.get("role") in selected_roles]
            for role in module["roles"]:
                role_name = role.get("role")
                if isinstance(role_name, str):
                    keep_binding_keys.add(f"{view_id}.{instance}.{role_name}")

    bindings = filtered.get("bindings")
    if not isinstance(bindings, dict):
        raise RuntimeRenderError("operational trace bindings missing")
    filtered["bindings"] = {
        key: value for key, value in bindings.items() if key in keep_binding_keys
    }
    return filtered


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

        dashboard, base_trace = base._render_manifest(
            manifest,
            contracts,
            inventory,
            snapshot_ids=snapshot_ids,
        )
        renderer = _manifest_renderer(manifest)
        if renderer == HOUSE_RENDERER:
            dashboard = render_house_dashboard(dashboard, base_trace, manifest)
            trace = copy.deepcopy(base_trace)
            trace["renderer_engine_sha256"] = _house_layout_engine_sha256(
                base_trace["renderer_engine_sha256"]
            )
        else:
            dashboard = _operational_dashboard(dashboard, base_trace, contracts, manifest)
            trace = _filter_trace(base_trace, contracts, manifest)
            trace["renderer_engine_sha256"] = _layout_engine_sha256(
                base_trace["renderer_engine_sha256"]
            )

        canonical = json.dumps(
            dashboard,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
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
    "DEFAULT_RENDERER",
    "GeneratedArtifact",
    "RuntimeRenderError",
    "render_all_manifests",
]
