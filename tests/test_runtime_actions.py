from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "contract_generated_ui"


def _runtime_module():
    package_name = "contract_generated_ui_runtime_actions_test"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        PACKAGE_PATH / "__init__.py",
        submodule_search_locations=[str(PACKAGE_PATH)],
    )
    assert package_spec is not None and package_spec.loader is not None
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package
    package_spec.loader.exec_module(package)

    for module_name in (
        "runtime_renderer",
        "runtime_house",
        "runtime_operational",
        "runtime_actions",
        "runtime_render_dispatch",
    ):
        spec = importlib.util.spec_from_file_location(
            f"{package_name}.{module_name}",
            PACKAGE_PATH / f"{module_name}.py",
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return sys.modules[f"{package_name}.runtime_render_dispatch"]


def _write_sources(root: Path) -> None:
    for directory in ("contracts", "inventory", "manifests"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    roles = {
        "light": {
            "label": "Свет кухни",
            "description": "Safe quick light toggle.",
            "required": True,
            "allowed_domains": ["light"],
        },
        "vacuum": {
            "label": "Пылесос",
            "description": "Open the specialized vacuum dashboard.",
            "required": True,
            "allowed_domains": ["vacuum"],
        },
        "status": {
            "label": "Статус",
            "description": "Open entity details.",
            "required": True,
            "allowed_domains": ["sensor"],
        },
    }
    contract = {
        "api_version": "nikas.home-assistant/ui-contract/v1",
        "kind": "UIContract",
        "metadata": {"id": "actions.test", "title": "Actions", "version": "1.0"},
        "spec": {
            "roles": roles,
            "states": {
                "normal": {"description": "Normal", "rules": []},
                "event": {"description": "Event", "rules": []},
                "unreliable": {"description": "Unreliable", "rules": []},
            },
            "actions": [
                {
                    "id": "toggle_light",
                    "kind": "toggle",
                    "description": "Toggle light.",
                    "role": "light",
                },
                {
                    "id": "open_vacuum",
                    "kind": "navigate",
                    "description": "Open vacuum panel.",
                    "role": "vacuum",
                    "target": "/dashboard-s8-omni",
                },
                {
                    "id": "status_info",
                    "kind": "more_info",
                    "description": "Open details.",
                    "role": "status",
                },
            ],
            "presentation": {
                "renderer": "tiles_v1",
                "columns": 2,
                "role_order": ["light", "vacuum", "status"],
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
            "generated_at": "2026-08-22T07:00:00Z",
            "source": "home_assistant",
            "scrubbed": True,
            "snapshot_id": "sha256:actions-test",
        },
        "spec": {
            "bindings": {
                "actions.test.light": {
                    "entity_id": "light.kitchen",
                    "domain": "light",
                    "verification": "verified",
                },
                "actions.test.vacuum": {
                    "entity_id": "vacuum.robot",
                    "domain": "vacuum",
                    "verification": "verified",
                },
                "actions.test.status": {
                    "entity_id": "sensor.status",
                    "domain": "sensor",
                    "verification": "verified",
                },
            }
        },
    }
    manifest = {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {"id": "actions_test", "title": "Actions", "version": "1.0"},
        "spec": {
            "dashboard_path": "/dashboard-actions-test",
            "views": [
                {
                    "id": "home",
                    "title": "Actions",
                    "path": "home",
                    "order": 0,
                    "renderer": "actions_home_v1",
                    "modules": [
                        {
                            "contract": "actions.test",
                            "instance": "quick",
                            "title": "Быстрые действия",
                            "order": 0,
                            "bindings": {
                                "light": "actions.test.light",
                                "vacuum": "actions.test.vacuum",
                                "status": "actions.test.status",
                            },
                        }
                    ],
                }
            ],
        },
    }

    (root / "contracts" / "actions.yaml").write_text(
        yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
    )
    (root / "inventory" / "home.yaml").write_text(
        yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8"
    )
    (root / "manifests" / "actions.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )


def test_runtime_actions_render_is_deterministic(tmp_path: Path) -> None:
    module = _runtime_module()
    source = tmp_path / "source"
    generated = source / "generated"
    _write_sources(source)

    first = module.render_all_manifests(source, generated)
    assert len(first) == 1
    assert first[0].changed is True

    dashboard = yaml.safe_load(
        (generated / "actions_test.yaml").read_text(encoding="utf-8")
    )
    view = dashboard["views"][0]
    assert view["type"] == "sections"
    assert view["dense_section_placement"] is True
    cards = view["sections"][0]["cards"]
    assert cards[1]["grid_options"] == {"columns": 6, "rows": 1}
    assert cards[2]["grid_options"] == {"columns": 12, "rows": 1}
    assert cards[3]["grid_options"] == {"columns": 6, "rows": 1}
    assert cards[2]["tap_action"] == {
        "action": "navigate",
        "navigation_path": "/dashboard-s8-omni",
    }

    yaml_bytes = (generated / "actions_test.yaml").read_bytes()
    trace_bytes = (generated / "actions_test.meta.json").read_bytes()
    second = module.render_all_manifests(source, generated)
    assert second[0].changed is False
    assert (generated / "actions_test.yaml").read_bytes() == yaml_bytes
    assert (generated / "actions_test.meta.json").read_bytes() == trace_bytes
