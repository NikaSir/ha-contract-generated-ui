from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class SemanticChange:
    """One meaning-level change in a generated input."""

    kind: str
    key: str
    before: Any
    after: Any

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _diff_keyed(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    rebind_field: str | None = None,
) -> list[SemanticChange]:
    changes: list[SemanticChange] = []
    for key in sorted(before.keys() | after.keys()):
        old = before.get(key)
        new = after.get(key)
        if key not in before:
            changes.append(SemanticChange("added", key, None, new))
        elif key not in after:
            changes.append(SemanticChange("removed", key, old, None))
        elif old != new:
            kind = "changed"
            if (
                rebind_field
                and isinstance(old, Mapping)
                and isinstance(new, Mapping)
                and old.get(rebind_field) != new.get(rebind_field)
            ):
                kind = "rebound"
            changes.append(SemanticChange(kind, key, old, new))
    return changes


def diff_inventories(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> list[SemanticChange]:
    """Compare semantic bindings independently of formatting or metadata."""
    return _diff_keyed(
        before["spec"]["bindings"],
        after["spec"]["bindings"],
        rebind_field="entity_id",
    )


def diff_registry_snapshots(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> list[SemanticChange]:
    """Compare scrubbed entity registry facts independently of capture time."""
    old_entities = {
        entity["entity_id"]: entity for entity in before["spec"]["entities"]
    }
    new_entities = {
        entity["entity_id"]: entity for entity in after["spec"]["entities"]
    }
    return _diff_keyed(old_entities, new_entities)


def render_text(changes: list[SemanticChange]) -> str:
    """Render a compact deterministic human review."""
    if not changes:
        return "No semantic changes."
    lines = [f"{len(changes)} semantic change(s):"]
    for change in changes:
        lines.append(f"- {change.kind}: {change.key}")
    return "\n".join(lines)
