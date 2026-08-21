"""Scrubbed Home Assistant registry snapshot support."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Mapping

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

CURRENT_SNAPSHOT = "current.json"
PREVIOUS_SNAPSHOT = "previous.json"


@dataclass(frozen=True, slots=True)
class SnapshotWriteResult:
    """Result of atomically writing a registry snapshot."""

    current_path: Path
    previous_path: Path | None
    changed: bool


def canonical_snapshot_id(entities: Iterable[Mapping[str, Any]]) -> str:
    """Return a stable content ID for scrubbed entity facts."""
    payload = json.dumps(
        list(entities),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()[:20]}"


def build_snapshot_document(
    entities: Iterable[Mapping[str, Any]],
    *,
    captured_at: str,
    home_assistant_version: str,
) -> dict[str, Any]:
    """Create a deterministic, scrubbed snapshot document."""
    ordered = sorted(
        (dict(entity) for entity in entities),
        key=lambda item: item["entity_id"],
    )
    return {
        "api_version": "nikas.home-assistant/registry-snapshot/v1",
        "kind": "RegistrySnapshot",
        "metadata": {
            "captured_at": captured_at,
            "source": "home_assistant",
            "scrubbed": True,
            "snapshot_id": canonical_snapshot_id(ordered),
            "home_assistant_version": home_assistant_version,
        },
        "spec": {"entities": ordered},
    }


def capture_registry_snapshot(hass: HomeAssistant) -> dict[str, Any]:
    """Capture only registry fields needed for contract binding and drift review."""
    from homeassistant.const import __version__
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    entities: list[dict[str, Any]] = []
    for entry in registry.entities.values():
        entity: dict[str, Any] = {
            "entity_id": entry.entity_id,
            "domain": entry.domain,
            "platform": entry.platform,
            "disabled": entry.disabled_by is not None,
            "hidden": entry.hidden_by is not None,
        }
        device_class = entry.device_class or entry.original_device_class
        if device_class is not None:
            entity["device_class"] = device_class
        if entry.unit_of_measurement is not None:
            entity["unit_of_measurement"] = entry.unit_of_measurement
        entities.append(entity)

    captured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return build_snapshot_document(
        entities,
        captured_at=captured_at,
        home_assistant_version=__version__,
    )


def write_registry_snapshot(
    snapshot_root: Path,
    document: Mapping[str, Any],
) -> SnapshotWriteResult:
    """Atomically rotate current to previous only when registry facts changed."""
    snapshot_root.mkdir(parents=True, exist_ok=True)
    current_path = snapshot_root / CURRENT_SNAPSHOT
    previous_path = snapshot_root / PREVIOUS_SNAPSHOT
    new_snapshot_id = document["metadata"]["snapshot_id"]
    changed = True

    if current_path.exists():
        try:
            existing = json.loads(current_path.read_text(encoding="utf-8"))
            old_snapshot_id = existing.get("metadata", {}).get("snapshot_id")
        except (json.JSONDecodeError, OSError):
            old_snapshot_id = None
        if old_snapshot_id == new_snapshot_id:
            changed = False
        elif old_snapshot_id is not None:
            os.replace(current_path, previous_path)

    temp_path = snapshot_root / f".{CURRENT_SNAPSHOT}.tmp"
    temp_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temp_path, current_path)

    return SnapshotWriteResult(
        current_path=current_path,
        previous_path=previous_path if previous_path.exists() else None,
        changed=changed,
    )
