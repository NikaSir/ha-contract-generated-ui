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

RuntimeRenderError = base.RuntimeRenderError
MAX_SECTION_COLUMNS = 2


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    helper_sha = hashlib.sha256(
        (Path(__file__).parent / "runtime_infrastructure_summary.py").read_bytes()
    ).hexdigest()
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}:{helper_sha}".encode("utf-8")
    ).hexdigest()


def _summary_dashboard(
    dashboard: Mapping[str, Any],
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    semantic_views = trace.get("semantics", {}).get("views")
    if not isinstance(views, list) or not isinstance(semantic_views, list):
        raise RuntimeRenderError("infrastructure summary requires dashboard and semantic views")
    if len(views) != len(semantic_views):
        raise RuntimeRenderError("infrastructure summary view/trace count mismatch")

    for view, semantic_view in zip(views, semantic_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RuntimeRenderError("infrastructure summary expects validated masonry input")
        cards = view.pop("cards", None)
        modules = semantic_view.get("modules")
        if not isinstance(cards, list) or not isinstance(modules, list):
            raise RuntimeRenderError("infrastructure summary module input missing")
        if len(cards) != len(modules) * 2:
            raise RuntimeRenderError(
                "infrastructure summary heading/grid pairs do not match modules"
            )

        sections: list[dict[str, Any]] = []
        for semantic_module in modules:
            if not isinstance(semantic_module, Mapping):
                raise RuntimeRenderError("infrastructure summary module must be an object")
            try:
                card = build_summary_card(semantic_module)
            except ValueError as err:
                raise RuntimeRenderError(str(err)) from err
            sections.append({"type": "grid", "cards": [card]})

        if not sections:
            raise RuntimeRenderError("infrastructure summary rendered no sections")
        view["type"] = "sections"
        view["max_columns"] = min(MAX_SECTION_COLUMNS, max(1, len(sections)))
        view["dense_section_placement"] = True
        view["sections"] = sections

    return transformed


def _filter_trace(trace: Mapping[str, Any]) -> dict[str, Any]:
    filtered = copy.deepcopy(trace)
    semantic_views = filtered.get("semantics", {}).get("views")
    if not isinstance(semantic_views, list):
        raise RuntimeRenderError("infrastructure summary trace has no semantic views")

    keep_binding_keys: set[str] = set()
    for view in semantic_views:
        view_id = view.get("id")
        modules = view.get("modules")
        if not isinstance(view_id, str) or not isinstance(modules, list):
            raise RuntimeRenderError("infrastructure summary trace view is incomplete")
        for module in modules:
            contract_id = module.get("contract")
            instance = module.get("instance")
            roles = module.get("roles")
            if (
                not isinstance(contract_id, str)
                or not isinstance(instance, str)
                or not isinstance(roles, list)
            ):
                raise RuntimeRenderError("infrastructure summary trace module is incomplete")
            try:
                required = required_summary_roles(contract_id)
            except ValueError as err:
                raise RuntimeRenderError(str(err)) from err
            role_by_name = {
                role.get("role"): role
                for role in roles
                if isinstance(role, Mapping) and isinstance(role.get("role"), str)
            }
            missing = [role_name for role_name in required if role_name not in role_by_name]
            if missing:
                raise RuntimeRenderError(
                    f"infrastructure summary trace {contract_id!r} missing roles: {', '.join(missing)}"
                )
            module["roles"] = [role_by_name[role_name] for role_name in required]
            for role_name in required:
                keep_binding_keys.add(f"{view_id}.{instance}.{role_name}")

    bindings = filtered.get("bindings")
    if not isinstance(bindings, dict):
        raise RuntimeRenderError("infrastructure summary trace bindings missing")
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
