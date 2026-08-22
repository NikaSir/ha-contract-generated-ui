from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .app_shell import (
    app_shell_engine_sha256,
    append_app_shell,
    manifest_app_shell_config,
)
from .render import (
    RenderError,
    RenderResult,
    render_repository_manifest as render_tiles_repository_manifest,
    write_render_result,
)
from .render_actions import (
    ACTIONS_RENDERER,
    _layout_engine_sha256 as _actions_layout_engine_sha256,
    render_actions_dashboard,
)
from .render_house import (
    HOUSE_RENDERER,
    _layout_engine_sha256 as _house_layout_engine_sha256,
    render_house_dashboard,
)
from .render_infrastructure_summary import (
    SUMMARY_RENDERER,
    _filter_trace as _infrastructure_summary_filter_trace,
    _layout_engine_sha256 as _infrastructure_summary_layout_engine_sha256,
    _summary_dashboard as _infrastructure_summary_dashboard,
)
from .render_operational import (
    DEFAULT_RENDERER,
    _contracts,
    _filter_trace,
    _layout_engine_sha256 as _operational_layout_engine_sha256,
    _operational_dashboard,
)
from .render_subpanel_placeholder import (
    PLACEHOLDER_RENDERER,
    _layout_engine_sha256 as _placeholder_layout_engine_sha256,
    render_subpanel_placeholder_dashboard,
)
from .subpanel_shell import (
    apply_navigation_shell,
    navigation_shell_engine_sha256,
)
from .validation import load_document

SUPPORTED_RENDERERS = frozenset({
    DEFAULT_RENDERER,
    HOUSE_RENDERER,
    ACTIONS_RENDERER,
    SUMMARY_RENDERER,
    PLACEHOLDER_RENDERER,
})


def manifest_renderer(manifest: Mapping[str, Any]) -> str:
    views = manifest.get("spec", {}).get("views")
    if not isinstance(views, list) or not views:
        raise RenderError("panel manifest has no views")
    renderers: set[str] = set()
    for view in views:
        if not isinstance(view, dict):
            raise RenderError("panel manifest view must be an object")
        renderer = view.get("renderer", DEFAULT_RENDERER)
        if renderer not in SUPPORTED_RENDERERS:
            raise RenderError(f"unsupported view renderer {renderer!r}")
        modules = view.get("modules")
        if not isinstance(modules, list):
            raise RenderError("panel manifest view modules must be an array")
        if renderer == PLACEHOLDER_RENDERER:
            if modules:
                raise RenderError("subpanel_placeholder_v1 views must not bind entity modules")
            if not isinstance(view.get("placeholder"), str) or not view["placeholder"].strip():
                raise RenderError("subpanel_placeholder_v1 requires placeholder text")
        elif not modules:
            raise RenderError(f"renderer {renderer!r} requires at least one entity module")
        renderers.add(renderer)
    if len(renderers) != 1:
        raise RenderError("mixed view renderers are not supported in one manifest")
    return renderers.pop()


def render_repository_manifest(repo_root: Path, manifest_path: Path) -> RenderResult:
    manifest = load_document(manifest_path)
    if not isinstance(manifest, dict):
        raise RenderError("panel manifest root must be an object")

    base = render_tiles_repository_manifest(repo_root, manifest_path)
    renderer = manifest_renderer(manifest)

    if renderer == HOUSE_RENDERER:
        dashboard = render_house_dashboard(base.dashboard, base.trace, manifest)
        trace = copy.deepcopy(base.trace)
        trace["renderer_engine_sha256"] = _house_layout_engine_sha256(
            base.trace["renderer_engine_sha256"]
        )
    elif renderer == ACTIONS_RENDERER:
        dashboard = render_actions_dashboard(base.dashboard, base.trace)
        trace = copy.deepcopy(base.trace)
        trace["renderer_engine_sha256"] = _actions_layout_engine_sha256(
            base.trace["renderer_engine_sha256"]
        )
    elif renderer == SUMMARY_RENDERER:
        dashboard = _infrastructure_summary_dashboard(base.dashboard, base.trace)
        trace = _infrastructure_summary_filter_trace(base.trace)
        trace["renderer_engine_sha256"] = _infrastructure_summary_layout_engine_sha256(
            base.trace["renderer_engine_sha256"]
        )
    elif renderer == PLACEHOLDER_RENDERER:
        dashboard = render_subpanel_placeholder_dashboard(base.dashboard, manifest)
        trace = copy.deepcopy(base.trace)
        trace["renderer_engine_sha256"] = _placeholder_layout_engine_sha256(
            base.trace["renderer_engine_sha256"]
        )
    else:
        contracts = _contracts(repo_root)
        dashboard = _operational_dashboard(base.dashboard, base.trace, contracts, manifest)
        trace = _filter_trace(base.trace, contracts, manifest)
        trace["renderer_engine_sha256"] = _operational_layout_engine_sha256(
            base.trace["renderer_engine_sha256"]
        )

    dashboard, navigation_groups = apply_navigation_shell(
        dashboard,
        manifest,
        repo_root,
    )
    trace["renderer_engine_sha256"] = navigation_shell_engine_sha256(
        trace["renderer_engine_sha256"],
        navigation_groups,
    )

    app_shell_config = manifest_app_shell_config(manifest)
    if app_shell_config is not None:
        app_shell_active, app_shell_routes = app_shell_config
        dashboard = append_app_shell(
            dashboard,
            active=app_shell_active,
            routes=app_shell_routes,
        )
        trace["renderer_engine_sha256"] = app_shell_engine_sha256(
            trace["renderer_engine_sha256"]
        )

    canonical = json.dumps(
        dashboard,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    trace["dashboard_sha256"] = hashlib.sha256(canonical).hexdigest()
    return RenderResult(dashboard=dashboard, trace=trace)


__all__ = [
    "RenderError",
    "RenderResult",
    "manifest_renderer",
    "render_repository_manifest",
    "write_render_result",
]
