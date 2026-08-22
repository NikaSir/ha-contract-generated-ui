from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .app_shell import (
    app_shell_engine_sha256,
    append_app_shell,
    manifest_app_shell_active,
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
from .render_operational import (
    DEFAULT_RENDERER,
    _contracts,
    _filter_trace,
    _layout_engine_sha256 as _operational_layout_engine_sha256,
    _operational_dashboard,
)
from .validation import load_document

SUPPORTED_RENDERERS = frozenset({
    DEFAULT_RENDERER,
    HOUSE_RENDERER,
    ACTIONS_RENDERER,
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
    else:
        contracts = _contracts(repo_root)
        dashboard = _operational_dashboard(base.dashboard, base.trace, contracts, manifest)
        trace = _filter_trace(base.trace, contracts, manifest)
        trace["renderer_engine_sha256"] = _operational_layout_engine_sha256(
            base.trace["renderer_engine_sha256"]
        )

    app_shell_active = manifest_app_shell_active(manifest)
    if app_shell_active is not None:
        dashboard = append_app_shell(dashboard, active=app_shell_active)
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
