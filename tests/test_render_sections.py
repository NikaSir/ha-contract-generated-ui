from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from generator.render_sections import render_repository_manifest, write_render_result


def _contract() -> dict:
    return {
        "api_version": "nikas.home-assistant/ui-contract/v1",
        "kind": "UIContract",
        "metadata": {"id": "access", "title": "Access", "version": "1.0"},
        "spec": {
            "roles": {
                "contact": {
                    "label": "Door contact with a deliberately useful label",
                    "description": "Door contact",
                    "required": True,
                    "allowed_domains": ["binary_sensor"],
                },
                "light": {
                    "label": "Local light",
                    "description": "Local light",
                    "required": True,
                    "allowed_domains": ["light"],
                },
            },
            "states": {
                "normal": {"description": "Normal", "rules": []},
                "event": {"description": "Event", "rules": []},
                "unreliable": {"description": "Unreliable", "rules": []},
            },
            "actions": [
                {
                    "id": "contact_info",
                    "kind": "more_info",
                    "description": "Open details",
                    "role": "contact",
                },
                {
                    "id": "light_toggle",
                    "kind": "toggle",
                    "description": "Toggle light",
                    "role": "light",
                },
            ],
            "presentation": {
                "renderer": "tiles_v1",
                "columns": 2,
                "role_order": ["contact", "light"],
            },
            "safety": {
                "unknown_is_unreliable": True,
                "unavailable_is_unreliable": True,
                "invent_entity_ids": False,
            },
        },
    }


def _inventory() -> dict:
    return {
        "api_version": "nikas.home-assistant/semantic-inventory/v1",
        "kind": "SemanticInventory",
        "metadata": {
            "generated_at": "2026-08-22T00:00:00Z",
            "source": "home_assistant",
            "scrubbed": True,
            "snapshot_id": "sha256:test",
        },
        "spec": {
            "bindings": {
                "access.garden.contact": {
                    "entity_id": "binary_sensor.garden_door",
                    "domain": "binary_sensor",
                    "verification": "verified",
                },
                "access.garden.light": {
                    "entity_id": "light.garden",
                    "domain": "light",
                    "verification": "verified",
                },
            }
        },
    }


def _manifest() -> dict:
    return {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {"id": "house", "title": "House", "version": "1.0"},
        "spec": {
            "dashboard_path": "/dashboard-house",
            "views": [
                {
                    "id": "home",
                    "title": "Home",
                    "path": "home",
                    "order": 0,
                    "modules": [
                        {
                            "contract": "access",
                            "instance": "garden",
                            "title": "Garden",
                            "order": 0,
                            "bindings": {
                                "contact": "access.garden.contact",
                                "light": "access.garden.light",
                            },
                        }
                    ],
                }
            ],
        },
    }


def _write_repo(root: Path) -> Path:
    for directory in ("contracts", "inventory", "manifests", "schemas"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    source_root = Path(__file__).parents[1]
    for name in ("contract.schema.json", "inventory.schema.json", "manifest.schema.json"):
        (root / "schemas" / name).write_bytes((source_root / "schemas" / name).read_bytes())
    (root / "contracts" / "access.yaml").write_text(
        yaml.safe_dump(_contract(), sort_keys=False), encoding="utf-8"
    )
    (root / "inventory" / "home.yaml").write_text(
        yaml.safe_dump(_inventory(), sort_keys=False), encoding="utf-8"
    )
    manifest_path = root / "manifests" / "house.yaml"
    manifest_path.write_text(yaml.safe_dump(_manifest(), sort_keys=False), encoding="utf-8")
    return manifest_path


def test_sections_v2_uses_wide_sections_and_explicit_tile_grid(tmp_path: Path) -> None:
    manifest_path = _write_repo(tmp_path)
    result = render_repository_manifest(tmp_path, manifest_path)
    view = result.dashboard["views"][0]

    assert view["type"] == "sections"
    assert view["max_columns"] == 4
    assert view["dense_section_placement"] is False
    assert "cards" not in view
    assert len(view["sections"]) == 1

    section = view["sections"][0]
    assert section["type"] == "grid"
    assert section["column_span"] == 4
    assert section["cards"][0] == {"type": "heading", "heading": "Garden"}
    contact, light = section["cards"][1:]
    assert contact["grid_options"] == {"columns": 6, "rows": 1}
    assert light["grid_options"] == {"columns": 6, "rows": 1}
    assert contact["tap_action"] == {"action": "more-info"}
    assert light["tap_action"] == {"action": "toggle"}


def test_sections_v2_is_deterministic_and_trace_valid(tmp_path: Path) -> None:
    manifest_path = _write_repo(tmp_path)
    first = render_repository_manifest(tmp_path, manifest_path)
    second = render_repository_manifest(tmp_path, manifest_path)
    assert first == second

    output = tmp_path / "generated" / "house.yaml"
    yaml_path, meta_path = write_render_result(output, first)
    yaml_bytes = yaml_path.read_bytes()
    meta_bytes = meta_path.read_bytes()
    write_render_result(output, second)
    assert yaml_path.read_bytes() == yaml_bytes
    assert meta_path.read_bytes() == meta_bytes

    trace_schema = json.loads(
        (Path(__file__).parents[1] / "schemas" / "render-trace.schema.json").read_text(
            encoding="utf-8"
        )
    )
    trace = json.loads(meta_path.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(trace_schema).iter_errors(trace)) == []
    assert trace["dashboard_sha256"] == first.trace["dashboard_sha256"]
