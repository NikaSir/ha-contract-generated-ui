from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "contract_generated_ui"


def _runtime_module():
    package_name = "contract_generated_ui_runtime_diagnostics_test"
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


def _contract() -> dict:
    return {
        "metadata": {"id": "infra.test"},
        "spec": {
            "presentation": {
                "role_order": ["status", "telemetry", "diagnostic"],
                "role_groups": {
                    "status": ["status"],
                    "telemetry": ["telemetry"],
                    "diagnostic": ["diagnostic"],
                },
            }
        },
    }


def _manifest() -> dict:
    bindings = {
        "status": "infrastructure.test.status",
        "telemetry": "infrastructure.test.telemetry",
        "diagnostic": "infrastructure.test.diagnostic",
    }
    return {
        "spec": {
            "views": [
                {
                    "id": "overview",
                    "modules": [
                        {
                            "contract": "infra.test",
                            "instance": "test",
                            "groups": ["status", "telemetry"],
                            "bindings": bindings,
                        }
                    ],
                },
                {
                    "id": "diagnostics",
                    "modules": [
                        {
                            "contract": "infra.test",
                            "instance": "test",
                            "groups": ["diagnostic"],
                            "bindings": bindings,
                        }
                    ],
                },
            ]
        }
    }


def _cards() -> list[dict]:
    return [
        {"type": "heading", "heading": "Subsystem"},
        {
            "type": "grid",
            "cards": [
                {"type": "tile", "entity": "sensor.status"},
                {"type": "tile", "entity": "sensor.telemetry"},
                {"type": "tile", "entity": "sensor.diagnostic"},
            ],
        },
    ]


def _dashboard() -> dict:
    return {
        "views": [
            {"title": "Overview", "path": "overview", "type": "masonry", "cards": _cards()},
            {
                "title": "Diagnostics",
                "path": "diagnostics",
                "type": "masonry",
                "cards": _cards(),
            },
        ]
    }


def _roles() -> list[dict]:
    return [
        {
            "role": "status",
            "label": "Status",
            "entity_id": "sensor.status",
            "action": {"kind": "more_info"},
        },
        {
            "role": "telemetry",
            "label": "Telemetry",
            "entity_id": "sensor.telemetry",
            "action": {"kind": "more_info"},
        },
        {
            "role": "diagnostic",
            "label": "Diagnostic",
            "entity_id": "sensor.diagnostic",
            "action": {"kind": "more_info"},
        },
    ]


def _trace() -> dict:
    return {
        "bindings": {
            "overview.test.status": {},
            "overview.test.telemetry": {},
            "overview.test.diagnostic": {},
            "diagnostics.test.status": {},
            "diagnostics.test.telemetry": {},
            "diagnostics.test.diagnostic": {},
        },
        "semantics": {
            "views": [
                {
                    "id": "overview",
                    "modules": [
                        {"contract": "infra.test", "instance": "test", "roles": _roles()}
                    ],
                },
                {
                    "id": "diagnostics",
                    "modules": [
                        {"contract": "infra.test", "instance": "test", "roles": _roles()}
                    ],
                },
            ]
        },
    }


def test_runtime_filter_matches_rendered_views() -> None:
    module = _runtime_module()
    contracts = {"infra.test": _contract()}
    manifest = _manifest()

    dashboard = module._operational_dashboard(_dashboard(), _trace(), contracts, manifest)
    assert [card["type"] for card in dashboard["views"][0]["sections"][0]["cards"]] == [
        "heading",
        "tile",
        "tile",
    ]
    diagnostic_cards = dashboard["views"][1]["sections"][0]["cards"]
    assert [card["type"] for card in diagnostic_cards] == [
        "heading",
        "entities",
    ]
    assert "title" not in diagnostic_cards[1]

    trace = module._filter_trace(_trace(), contracts, manifest)
    assert set(trace["bindings"]) == {
        "overview.test.status",
        "overview.test.telemetry",
        "diagnostics.test.diagnostic",
    }
