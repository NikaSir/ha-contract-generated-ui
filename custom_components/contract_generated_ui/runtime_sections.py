"""Sections v2 layout for the validated Contract Generated UI runtime renderer."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from . import runtime_renderer as base

RuntimeRenderError = base.RuntimeRenderError
GeneratedArtifact = base.GeneratedArtifact

MAX_SECTION_COLUMNS = 4
SECTION_COLUMN_SPAN = 2
TILE_GRID_COLUMNS = 6
TILE_GRID_ROWS = 1


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    """Fingerprint both the base renderer and this Sections layout layer."""
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}".encode("utf-8")
    ).hexdigest()


def _sections_dashboard(dashboard: dict[str, Any]) -> dict[str, Any]:
    """Convert validated tiles_v1 masonry output to Home Assistant Sections."""
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    if not isinstance(views, list):
        raise RuntimeRenderError("rendered dashboard has no views list")

    for view in views:
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RuntimeRenderError(
                "Sections v2 expects the validated masonry tiles_v1 shape"
            )
        cards = view.pop("cards", None)
        if not isinstance(cards, list) or not cards or len(cards) % 2:
            raise RuntimeRenderError(
                "Sections v2 expects heading/grid card pairs per module"
            )

        sections: list[dict[str, Any]] = []
        for index in range(0, len(cards), 2):
            heading = cards[index]
            grid = cards[index + 1]
            if not isinstance(heading, dict) or heading.get("type") != "heading":
                raise RuntimeRenderError(
                    "Sections v2 module must begin with a heading card"
                )
            if not isinstance(grid, dict) or grid.get("type") != "grid":
                raise RuntimeRenderError(
                    "Sections v2 module must contain a tiles grid"
                )
            tiles = grid.get("cards")
            if not isinstance(tiles, list) or not tiles:
                raise RuntimeRenderError(
                    "Sections v2 module tiles grid cannot be empty"
                )

            section_cards: list[dict[str, Any]] = [heading]
            for tile in tiles:
                if not isinstance(tile, dict) or tile.get("type") != "tile":
                    raise RuntimeRenderError(
                        "Sections v2 accepts only core tile cards"
                    )
                tile["grid_options"] = {
                    "columns": TILE_GRID_COLUMNS,
                    "rows": TILE_GRID_ROWS,
                }
                section_cards.append(tile)

            sections.append(
                {
                    "type": "grid",
                    "cards": section_cards,
                }
            )

        column_span = MAX_SECTION_COLUMNS if len(sections) == 1 else SECTION_COLUMN_SPAN
        for section in sections:
            section["column_span"] = column_span

        view["type"] = "sections"
        view["max_columns"] = MAX_SECTION_COLUMNS
        view["dense_section_placement"] = False
        view["sections"] = sections

    return transformed


def render_all_manifests(
    source_root: Path,
    generated_root: Path,
) -> list[GeneratedArtifact]:
    """Render all manifests with validated bindings and Sections v2 layout."""
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
        dashboard = _sections_dashboard(dashboard)
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
