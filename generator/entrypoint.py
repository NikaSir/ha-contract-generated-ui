"""CLI entrypoint that keeps legacy commands and dispatches current renderers."""

from __future__ import annotations

from . import render_operational
from .render_dispatch import render_repository_manifest, write_render_result

# `generator.cli` imports these names from render_operational. Patch only the
# render entrypoints before importing the unchanged CLI command implementation.
render_operational.render_repository_manifest = render_repository_manifest
render_operational.write_render_result = write_render_result

from .cli import main  # noqa: E402  (import after renderer compatibility patch)

__all__ = ["main"]
