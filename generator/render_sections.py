from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from .render import (
    RenderError,
    RenderResult,
    render_repository_manifest as render_tiles_repository_manifest,
    write_render_result,
)

MAX_SECTION_COLUMNS = 4
SECTION_COLUMN_SPAN = 2
TILE_GRID_COLUMNS = 6
TILE_GRID_ROWS = 1


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    """Fingerprint both the validated base renderer and this layout layer."""
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}".encode("utf-8")
    ).hexdigest()


def _sections_dashboard(dashboard: dict[str, Any]) -> dict[str, Any]:
    """Convert the deterministic tiles_v1 masonry shape to Sections view."""
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    if not isinstance(views, list):
        raise RenderError("rendered dashboard has no views list")

    for view in views:
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RenderError("Sections v2 expects the validated masonry tiles_v1 shape")
        cards = view.pop("cards", None)
        if not isinstance(cards, list) or not cards or len(cards) % 2:
            raise RenderError("Sections v2 expects heading/grid card pairs per module")

        sections: list[dict[str, Any]] = []
        for index in range(0, len(cards), 2):
            heading = cards[index]
            grid = cards[index + 1]
            if not isinstance(heading, dict) or heading.get("type") != "heading":
                raise RenderError("Sections v2 module must begin with a heading card")
            if not isinstance(grid, dict) or grid.get("type") != "grid":
                raise RenderError("Sections v2 module must contain a tiles grid")
            tiles = grid.get("cards")
            if not isinstance(tiles, list) or not tiles:
                raise RenderError("Sections v2 module tiles grid cannot be empty")

            section_cards: list[dict[str, Any]] = [heading]
            for tile in tiles:
                if not isinstance(tile, dict) or tile.get("type") != "tile":
                    raise RenderError("Sections v2 accepts only core tile cards")
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


def render_repository_manifest(repo_root: Path, manifest_path: Path) -> RenderResult:
    """Render one manifest through tiles_v1 safety and Sections v2 layout."""
    base = render_tiles_repository_manifest(repo_root, manifest_path)
    dashboard = _sections_dashboard(base.dashboard)
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
