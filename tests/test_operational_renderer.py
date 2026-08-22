from __future__ import annotations

import copy

import pytest

from generator.render import RenderError
from generator.render_operational import _operational_dashboard, _role_groups


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


def _dashboard() -> dict:
    return {
        "views": [
            {
                "title": "Infrastructure",
                "path": "overview",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Subsystem"},
                    {
                        "type": "grid",
                        "cards": [
                            {"type": "tile", "entity": "sensor.status"},
                            {"type": "tile", "entity": "sensor.telemetry"},
                            {"type": "tile", "entity": "sensor.diagnostic"},
                        ],
                    },
                ],
            }
        ]
    }


def _trace() -> dict:
    return {
        "semantics": {
            "views": [
                {
                    "id": "overview",
                    "modules": [
                        {
                            "instance": "test",
                            "contract": "infra.test",
                            "roles": [
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
                            ],
                        }
                    ],
                }
            ]
        }
    }


def test_operational_layout_is_compact_and_deterministic() -> None:
    first = _operational_dashboard(
        _dashboard(),
        _trace(),
        {"infra.test": _contract()},
    )
    second = _operational_dashboard(
        _dashboard(),
        _trace(),
        {"infra.test": _contract()},
    )
    assert first == second

    view = first["views"][0]
    assert view["type"] == "sections"
    assert view["max_columns"] == 1
    assert view["dense_section_placement"] is True

    cards = view["sections"][0]["cards"]
    assert cards[1]["grid_options"] == {"columns": 6, "rows": 1}
    assert cards[2]["grid_options"] == {"columns": 4, "rows": 1}
    assert cards[3] == {
        "type": "entities",
        "title": "Диагностика",
        "show_header_toggle": False,
        "entities": [{"entity": "sensor.diagnostic", "name": "Diagnostic"}],
    }


def test_operational_role_groups_must_cover_roles_exactly_once() -> None:
    contract = copy.deepcopy(_contract())
    contract["spec"]["presentation"]["role_groups"]["telemetry"] = [
        "status",
        "telemetry",
    ]
    with pytest.raises(RenderError, match="overlap"):
        _role_groups(contract)

    contract = copy.deepcopy(_contract())
    contract["spec"]["presentation"]["role_groups"]["diagnostic"] = []
    with pytest.raises(RenderError, match="cover every role exactly once"):
        _role_groups(contract)
