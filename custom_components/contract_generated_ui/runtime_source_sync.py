"""Synchronize bundled public contracts/manifests/navigation into the runtime source tree."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PUBLIC_SOURCE_DIRECTORIES = ("contracts", "manifests", "navigation")

# Public Architecture-as-Code files that were previously shipped by this integration
# but are not part of the House overview. They are managed public runtime sources,
# not legacy Lovelace YAML dashboards, private inventory, or user data.
RETIRED_PUBLIC_SOURCE_FILES = (
    Path("contracts") / "actions_home.yaml",
    Path("contracts") / "house_irrigation_controller.yaml",
    Path("contracts") / "house_irrigation_lab.yaml",
    Path("contracts") / "house_irrigation_zone.yaml",
    Path("contracts") / "infrastructure_keenetic.yaml",
    Path("contracts") / "infrastructure_power_grid.yaml",
    Path("contracts") / "infrastructure_ups.yaml",
    Path("manifests") / "actions.yaml",
    Path("manifests") / "infrastructure.yaml",
    Path("manifests") / "irrigation.yaml",
    Path("manifests") / "starline.yaml",
    Path("manifests") / "zont.yaml",
)


@dataclass(frozen=True, slots=True)
class SourceSyncResult:
    """Result of synchronizing packaged public sources."""

    changed_files: int
    checked_files: int


def _atomic_sync(source: Path, target: Path) -> bool:
    payload = source.read_bytes()
    if target.exists() and target.read_bytes() == payload:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.tmp")
    temp.write_bytes(payload)
    os.replace(temp, target)
    return True


def _remove_retired_public_sources(source_root: Path) -> int:
    """Remove only explicitly retired integration-managed public source files."""
    changed = 0
    for relative in RETIRED_PUBLIC_SOURCE_FILES:
        target = source_root / relative
        if not target.exists():
            continue
        target.unlink()
        changed += 1
    return changed


def sync_bundled_public_sources(source_root: Path) -> SourceSyncResult:
    """Sync bundled public Architecture-as-Code sources and retire managed legacy files."""
    bundled_root = Path(__file__).with_name("bundled_sources")
    changed = _remove_retired_public_sources(source_root)
    checked = 0
    for directory in PUBLIC_SOURCE_DIRECTORIES:
        packaged = bundled_root / directory
        if not packaged.exists():
            continue
        for source in sorted(packaged.rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(packaged)
            target = source_root / directory / relative
            checked += 1
            changed += int(_atomic_sync(source, target))
    return SourceSyncResult(changed_files=changed, checked_files=checked)
