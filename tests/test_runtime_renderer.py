from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
RUNTIME_RENDERER_PATH = (
    ROOT
    / "custom_components"
    / "contract_generated_ui"
    / "runtime_sections.py"
)


def _runtime_renderer():
    package_name = "contract_generated_ui_runtime_test"
    package_path = ROOT / "custom_components" / "contract_generated_ui"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        package_path / "__init__.py",
        submodule_search_locations=[str(package_path)],
    )
    assert package_spec is not None and package_spec.loader is not None
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package
    package_spec.loader.exec_module(package)

    spec = importlib.util.spec_from_file_location(
        f"{package_name}.runtime_sections",
        RUNTIME_RENDERER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _contract() -> dict:
    return {
        "api_version": "nikas.home-assistant/ui-contract/v1",
        "kind": "UIContract",
        "metadata": {"id": "infra", "title": "Infrastructure", "version": "1.0"},
        "spec": {
            "roles": {
                "status": {
                    "label": "Status",
                    "description": "Synthetic status",
                    "required": True,
                    "allowed_domains": ["sensor"],
                }
            },
            "states": {
                "normal": {"description": "Normal", "rules": []},
                "event": {"description": "Event", "rules": []},
                "unreliable": {"description": "Unreliable", "rules": []},
            },
            "actions": [
                {
                    "id": "status_info",
                    "kind": "more_info",
                    "description": "Open details",
                    "role": "status",
                }
            ],
            "presentation": {
                "renderer": "tiles_v1",
                "columns": 1,
                "role_order": ["status"],
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
            "generated_at": "2026-08-21T19:45:22Z",
            "source": "home_assistant",
            "scrubbed": True,
            "snapshot_id": "sha256:test",
        },
        "spec": {
            "bindings": {
                "infrastructure.router.status": {
                    "entity_id": "sensor.router_status",
                    "domain": "sensor",
                    "verification": "verified",
                }
            }
        },
    }


def _manifest() -> dict:
    return {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {"id": "infrastructure", "title": "Infrastructure", "version": "1.0"},
        "spec": {
            "dashboard_path": "/dashboard-infrastructure",
            "views": [
                {
                    "id": "overview",
                    "title": "Infrastructure",
                    "path": "overview",
                    "order": 0,
                    "modules": [
                        {
                            "contract": "infra",
                            "instance": "router",
                            "order": 0,
                            "bindings": {
                                "status": "infrastructure.router.status"
                            },
                        }
                    ],
                }
            ],
        },
    }


def _write_sources(root: Path) -> None:
    for directory in ("contracts", "inventory", "manifests"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / "contracts" / "infra.yaml").write_text(
        yaml.safe_dump(_contract(), sort_keys=False),
        encoding="utf-8",
    )
    (root / "inventory" / "home.yaml").write_text(
        yaml.safe_dump(_inventory(), sort_keys=False),
        encoding="utf-8",
    )
    (root / "manifests" / "infrastructure.yaml").write_text(
        yaml.safe_dump(_manifest(), sort_keys=False),
        encoding="utf-8",
    )


def test_runtime_renderer_writes_deterministic_sections_yaml_and_trace(tmp_path: Path) -> None:
    renderer = _runtime_renderer()
    source_root = tmp_path / "source"
    generated_root = source_root / "generated"
    _write_sources(source_root)

    first = renderer.render_all_manifests(source_root, generated_root)
    assert len(first) == 1
    assert first[0].changed is True

    yaml_path = generated_root / "infrastructure.yaml"
    trace_path = generated_root / "infrastructure.meta.json"
    dashboard = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    view = dashboard["views"][0]
    assert view["type"] == "sections"
    assert view["max_columns"] == 4
    assert view["dense_section_placement"] is False
    assert len(view["sections"]) == 1
    assert view["sections"][0]["column_span"] == 4

    tile = view["sections"][0]["cards"][1]
    assert tile["entity"] == "sensor.router_status"
    assert tile["grid_options"] == {"columns": 6, "rows": 1}
    assert tile["tap_action"] == {"action": "more-info"}
    assert tile["icon_tap_action"] == {"action": "more-info"}
    assert tile["hold_action"] == {"action": "more-info"}
    assert tile["double_tap_action"] == {"action": "none"}

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["manifest"]["dashboard_path"] == "/dashboard-infrastructure"
    assert trace["inventory_snapshot_ids"] == ["sha256:test"]
    assert len(trace["dashboard_sha256"]) == 64
    assert len(trace["renderer_engine_sha256"]) == 64

    yaml_bytes = yaml_path.read_bytes()
    trace_bytes = trace_path.read_bytes()
    second = renderer.render_all_manifests(source_root, generated_root)
    assert second[0].changed is False
    assert yaml_path.read_bytes() == yaml_bytes
    assert trace_path.read_bytes() == trace_bytes


def test_runtime_renderer_rejects_unverified_inventory(tmp_path: Path) -> None:
    renderer = _runtime_renderer()
    source_root = tmp_path / "source"
    _write_sources(source_root)
    inventory = _inventory()
    inventory["spec"]["bindings"]["infrastructure.router.status"]["verification"] = "unverified"
    (source_root / "inventory" / "home.yaml").write_text(
        yaml.safe_dump(inventory, sort_keys=False),
        encoding="utf-8",
    )

    try:
        renderer.render_all_manifests(source_root, source_root / "generated")
    except renderer.RuntimeRenderError as exc:
        assert "is not verified" in str(exc)
    else:
        raise AssertionError("unverified runtime binding must fail closed")
