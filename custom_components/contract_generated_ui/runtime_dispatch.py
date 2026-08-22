"""Runtime dispatch for the current Contract Generated UI renderer."""

from __future__ import annotations

from pathlib import Path

from .runtime_render_dispatch import (
    GeneratedArtifact,
    RuntimeRenderError,
    render_all_manifests as render_current,
)
from .runtime_source_sync import sync_bundled_public_sources
from .runtime_subpanel_shell import (
    NAVIGATION_REGISTRY_FILENAME,
    write_navigation_registry,
)


def render_all_manifests(
    source_root: Path,
    generated_root: Path,
) -> list[GeneratedArtifact]:
    """Sync public sources, render dashboards and refresh the frontend navigation registry."""
    if source_root.name == "contract_generated_ui":
        sync_bundled_public_sources(source_root)
    artifacts = render_current(source_root, generated_root)
    write_navigation_registry(
        source_root,
        generated_root / NAVIGATION_REGISTRY_FILENAME,
    )
    return artifacts


__all__ = ["GeneratedArtifact", "RuntimeRenderError", "render_all_manifests"]
