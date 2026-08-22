"""Runtime dispatcher for Contract Generated UI layout engines."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from . import runtime_operational as operational
from .runtime_actions import (
    ACTIONS_RENDERER,
    _layout_engine_sha256 as _actions_layout_engine_sha256,
    render_actions_dashboard,
)

base = operational.base
RuntimeRenderError = base.RuntimeRenderError
GeneratedArtifact = base.GeneratedArtifact

SUPPORTED_RENDERERS = frozenset({
    operational.DEFAULT_RENDERER,
    operational.HOUSE_RENDERER,
    ACTIONS_RENDERER,
})


def manifest_renderer(manifest: Mapping[str, Any]) -> str:
    views = manifest.get("spec", {}).get("views")
    if not isinstance(views, list) or not views:
        raise RuntimeRenderError("panel manifest has no views")
    renderers: set[str] = set()
    for view in views:
        if not isinstance(view, dict):
            raise RuntimeRenderError("panel manifest view must be an object")
        renderer = view.get("renderer", operational.DEFAULT_RENDERER)
        if renderer not in SUPPORTED_RENDERERS:
            raise RuntimeRenderError(f"unsupported view renderer {renderer!r}")
        renderers.add(renderer)
    if len(renderers) != 1:
        raise RuntimeRenderError(
            "mixed view renderers are not supported in one manifest"
        )
    return renderers.pop()


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
        renderer = manifest_renderer(manifest)

        if renderer == ACTIONS_RENDERER:
            dashboard = render_actions_dashboard(dashboard, base_trace)
            trace = copy.deepcopy(base_trace)
            trace["renderer_engine_sha256"] = _actions_layout_engine_sha256(
                base_trace["renderer_engine_sha256"]
            )
        elif renderer == operational.HOUSE_RENDERER:
            dashboard = operational.render_house_dashboard(
                dashboard,
                base_trace,
                manifest,
            )
            trace = copy.deepcopy(base_trace)
            trace["renderer_engine_sha256"] = operational._house_layout_engine_sha256(
                base_trace["renderer_engine_sha256"]
            )
        else:
            dashboard = operational._operational_dashboard(
                dashboard,
                base_trace,
                contracts,
                manifest,
            )
            trace = operational._filter_trace(base_trace, contracts, manifest)
            trace["renderer_engine_sha256"] = operational._layout_engine_sha256(
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
    "GeneratedArtifact",
    "RuntimeRenderError",
    "manifest_renderer",
    "render_all_manifests",
]
