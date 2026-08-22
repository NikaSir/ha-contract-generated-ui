"""Runtime dispatch for the current Contract Generated UI renderer."""

from __future__ import annotations

from pathlib import Path

from .runtime_render_dispatch import (
    GeneratedArtifact,
    RuntimeRenderError,
    render_all_manifests as render_current,
)
from .runtime_source_sync import sync_bundled_public_sources


def render_all_manifests(source_root: Path, generated_root: Path) -> list[GeneratedArtifact]:
    """Sync public source templates and render current dashboard layouts."""
    if source_root.name == "contract_generated_ui":
        sync_bundled_public_sources(source_root)
    return render_current(source_root, generated_root)


__all__ = ["GeneratedArtifact", "RuntimeRenderError", "render_all_manifests"]
