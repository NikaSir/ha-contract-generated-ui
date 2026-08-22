from __future__ import annotations

import copy

import pytest

from generator.render import RenderError
from generator.render_actions import render_actions_dashboard


def _dashboard() -> dict:
    return {
        "views": [
            {
                "title": "Actions",
                "path": "home",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Quick"},
                    {
                        "type": "grid",
                        "cards": [
                            {"type": "tile", "entity": "light.kitchen"},
                            {"type": "tile", "entity": "vacuum.robot"},
                            {"type": "tile", "entity": "sensor.status"},
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
                    "id": "home",
                    "modules": [
                        {
                            "roles": [
                                {
                                    "role": "light",
                                    "action": {"kind": "toggle"},
                                },
                                {
                                    "role": "vacuum",
                                    "action": {
                                        "kind": "navigate",
                                        "target": "/dashboard-s8-omni",
                                    },
                                },
                                {
                                    "role": "status",
                                    "action": {"kind": "more_info"},
                                },
                            ]
                        }
                    ],
                }
            ]
        }
    }


def test_actions_layout_is_mobile_first_and_deterministic() -> None:
    first = render_actions_dashboard(_dashboard(), _trace())
    second = render_actions_dashboard(_dashboard(), _trace())
    assert first == second

    view = first["views"][0]
    assert view["type"] == "sections"
    assert view["max_columns"] == 1
    assert view["dense_section_placement"] is True

    cards = view["sections"][0]["cards"]
    assert cards[1]["grid_options"] == {"columns": 6, "rows": 1}
    assert cards[2]["grid_options"] == {"columns": 12, "rows": 1}
    assert cards[3]["grid_options"] == {"columns": 6, "rows": 1}


def test_actions_renderer_rejects_unsupported_action_kind() -> None:
    trace = copy.deepcopy(_trace())
    trace["semantics"]["views"][0]["modules"][0]["roles"][0]["action"] = {
        "kind": "service"
    }
    with pytest.raises(RenderError, match="unsupported action kind"):
        render_actions_dashboard(_dashboard(), trace)
