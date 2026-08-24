from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from generator.render_actions import render_actions_dashboard as render_generator

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "contract_generated_ui"


def _runtime_module():
    package_name = "contract_generated_ui_actions_parity_test"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        PACKAGE_PATH / "__init__.py",
        submodule_search_locations=[str(PACKAGE_PATH)],
    )
    assert package_spec is not None and package_spec.loader is not None
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package
    package_spec.loader.exec_module(package)

    renderer_spec = importlib.util.spec_from_file_location(
        f"{package_name}.runtime_renderer",
        PACKAGE_PATH / "runtime_renderer.py",
    )
    assert renderer_spec is not None and renderer_spec.loader is not None
    renderer = importlib.util.module_from_spec(renderer_spec)
    sys.modules[renderer_spec.name] = renderer
    renderer_spec.loader.exec_module(renderer)

    spec = importlib.util.spec_from_file_location(
        f"{package_name}.runtime_actions",
        PACKAGE_PATH / "runtime_actions.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _dashboard() -> dict:
    return {
        "views": [
            {
                "title": "Действия · v11.0",
                "path": "home",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Ворота и доступ"},
                    {"type": "grid", "cards": [{"type": "tile", "entity": "binary_sensor.sectional"}]},
                    {"type": "heading", "heading": "Уборка"},
                    {
                        "type": "grid",
                        "cards": [
                            {"type": "tile", "entity": "vacuum.s8_omni"},
                            {"type": "tile", "entity": "sensor.s8_fault"},
                            {"type": "tile", "entity": "sensor.s8_battery"},
                            {"type": "tile", "entity": "binary_sensor.s8_clean"},
                            {"type": "tile", "entity": "binary_sensor.s8_dust"},
                            {"type": "tile", "entity": "binary_sensor.s8_dry"},
                        ],
                    },
                ],
            }
        ]
    }


def _role(role: str, entity_id: str) -> dict:
    return {"role": role, "entity_id": entity_id, "action": {"kind": "more_info"}}


def _trace() -> dict:
    return {
        "semantics": {
            "views": [
                {
                    "id": "home",
                    "modules": [
                        {"instance": "access", "roles": [_role("sectional_gate", "binary_sensor.sectional")]},
                        {
                            "instance": "cleaning",
                            "roles": [
                                _role("vacuum_state", "vacuum.s8_omni"),
                                _role("vacuum_fault", "sensor.s8_fault"),
                                _role("vacuum_battery", "sensor.s8_battery"),
                                _role("station_clean", "binary_sensor.s8_clean"),
                                _role("station_dust", "binary_sensor.s8_dust"),
                                _role("station_dry", "binary_sensor.s8_dry"),
                            ],
                        },
                    ],
                }
            ]
        }
    }


def test_complete_actions_generator_runtime_parity() -> None:
    runtime = _runtime_module()
    assert render_generator(_dashboard(), _trace()) == runtime.render_actions_dashboard(
        _dashboard(), _trace()
    )
