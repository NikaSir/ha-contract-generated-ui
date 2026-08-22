from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "contract_generated_ui"


def _runtime_module():
    package_name = "contract_generated_ui_operational_test"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        PACKAGE_PATH / "__init__.py",
        submodule_search_locations=[str(PACKAGE_PATH)],
    )
    assert package_spec is not None and package_spec.loader is not None
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package
    package_spec.loader.exec_module(package)

    for module_name in ("runtime_renderer", "runtime_operational"):
        spec = importlib.util.spec_from_file_location(
            f"{package_name}.{module_name}",
            PACKAGE_PATH / f"{module_name}.py",
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return sys.modules[f"{package_name}.runtime_operational"]


def _write_sources(root: Path) -> None:
    for directory in ("contracts", "inventory", "manifests"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    contract = {
        "api_version": "nikas.home-assistant/ui-contract/v1",
        "kind": "UIContract",
        "metadata": {"id": "infra.test", "title": "Test", "version": "1.0"},
        "spec": {
            "roles": {
                role: {
                    "label": role.title(),
                    "description": role,
                    "required": True,
                    "allowed_domains": ["sensor"],
                }
                for role in ("status", "telemetry", "diagnostic")
            },
            "states": {
                "normal": {"description": "Normal", "rules": []},
                "event": {"description": "Event", "rules": []},
                "unreliable": {"description": "Unreliable", "rules": []},
            },
            "actions": [
                {
                    "id": f"info_{role}",
                    "kind": "more_info",
                    "description": "Info",
                    "role": role,
                }
                for role in ("status", "telemetry", "diagnostic")
            ],
            "presentation": {
                "renderer": "tiles_v1",
                "columns": 3,
                "role_order": ["status", "telemetry", "diagnostic"],
                "role_groups": {
                    "status": ["status"],
                    "telemetry": ["telemetry"],
                    "diagnostic": ["diagnostic"],
                },
            },
            "safety": {
                "unknown_is_unreliable": True,
                "unavailable_is_unreliable": True,
                "invent_entity_ids": False,
            },
        },
    }
    inventory = {
        "api_version": "nikas.home-assistant/semantic-inventory/v1",
        "kind": "SemanticInventory",
        "metadata": {
            "generated_at": "2026-08-22T04:00:00Z",
            "source": "home_assistant",
            "scrubbed": True,
            "snapshot_id": "sha256:test",
        },
        "spec": {
            "bindings": {
                f"infrastructure.test.{role}": {
                    "entity_id": f"sensor.test_{role}",
                    "domain": "sensor",
                    "verification": "verified",
                }
                for role in ("status", "telemetry", "diagnostic")
            }
        },
    }
    manifest = {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {"id": "test", "title": "Test", "version": "1.0"},
        "spec": {
            "dashboard_path": "/dashboard-test",
            "views": [
                {
                    "id": "overview",
                    "title": "Test",
                    "path": "overview",
                    "order": 0,
                    "modules": [
                        {
                            "contract": "infra.test",
                            "instance": "test",
                            "title": "Subsystem",
                            "order": 0,
                            "bindings": {
                                role: f"infrastructure.test.{role}"
                                for role in ("status", "telemetry", "diagnostic")
                            },
                        }
                    ],
                }
            ],
        },
    }

    (root / "contracts" / "test.yaml").write_text(
        yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
    )
    (root / "inventory" / "home.yaml").write_text(
        yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8"
    )
    (root / "manifests" / "test.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )


def test_runtime_operational_render_is_deterministic(tmp_path: Path) -> None:
    module = _runtime_module()
    source = tmp_path / "source"
    generated = source / "generated"
    _write_sources(source)

    first = module.render_all_manifests(source, generated)
    assert len(first) == 1
    assert first[0].changed is True

    dashboard = yaml.safe_load((generated / "test.yaml").read_text(encoding="utf-8"))
    view = dashboard["views"][0]
    assert view["type"] == "sections"
    assert view["dense_section_placement"] is True
    cards = view["sections"][0]["cards"]
    assert cards[1]["grid_options"] == {"columns": 6, "rows": 1}
    assert cards[2]["grid_options"] == {"columns": 4, "rows": 1}
    assert cards[3]["type"] == "entities"
    assert cards[3]["entities"] == [
        {"entity": "sensor.test_diagnostic", "name": "Diagnostic"}
    ]

    yaml_bytes = (generated / "test.yaml").read_bytes()
    trace_bytes = (generated / "test.meta.json").read_bytes()
    second = module.render_all_manifests(source, generated)
    assert second[0].changed is False
    assert (generated / "test.yaml").read_bytes() == yaml_bytes
    assert (generated / "test.meta.json").read_bytes() == trace_bytes
