from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any, Mapping

from .render import RenderError

PLACEHOLDER_RENDERER = "subpanel_placeholder_v1"


def _layout_engine_sha256(base_engine_sha256: str) -> str:
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}".encode("utf-8")
    ).hexdigest()


def render_subpanel_placeholder_dashboard(
    dashboard: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Render entity-free demo content while preserving the generated shell boundary."""
    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    manifest_views = manifest.get("spec", {}).get("views")
    if not isinstance(views, list) or not isinstance(manifest_views, list):
        raise RenderError("subpanel_placeholder_v1 requires dashboard and manifest views")
    if len(views) != len(manifest_views):
        raise RenderError("subpanel_placeholder_v1 view count mismatch")

    for view, view_spec in zip(views, manifest_views, strict=True):
        if not isinstance(view, dict) or view.get("type") != "masonry":
            raise RenderError("subpanel_placeholder_v1 expects validated masonry input")
        if view.get("cards") != []:
            raise RenderError("subpanel_placeholder_v1 must not render entity modules")
        placeholder = view_spec.get("placeholder")
        tab_title = view_spec.get("title")
        if not isinstance(placeholder, str) or not placeholder.strip():
            raise RenderError("subpanel_placeholder_v1 requires non-empty placeholder text")
        if not isinstance(tab_title, str) or not tab_title:
            raise RenderError("subpanel_placeholder_v1 requires view title")

        view.pop("cards", None)
        view["type"] = "sections"
        view["max_columns"] = 1
        view["dense_section_placement"] = True
        view["sections"] = [
            {
                "type": "grid",
                "cards": [
                    {
                        "type": "heading",
                        "heading": tab_title,
                        "heading_style": "title",
                        "grid_options": {"columns": "full"},
                    },
                    {
                        "type": "markdown",
                        "content": (
                            "### Каркас субпанели\n\n"
                            f"{placeholder}\n\n"
                            "_Навигация, заголовок и кнопка «Назад» сформированы "
                            "централизованно Contract Generated UI._"
                        ),
                        "grid_options": {"columns": "full"},
                    },
                ],
            }
        ]
    return transformed


__all__ = [
    "PLACEHOLDER_RENDERER",
    "_layout_engine_sha256",
    "render_subpanel_placeholder_dashboard",
]
