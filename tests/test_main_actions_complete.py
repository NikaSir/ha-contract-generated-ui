from __future__ import annotations

import json

import pytest

from generator.render import RenderError
from generator.render_actions import _vacuum_command, render_actions_dashboard


def _role(role: str, entity_id: str) -> dict:
    return {
        "role": role,
        "entity_id": entity_id,
        "action": {"kind": "more_info"},
    }


def _dashboard() -> dict:
    return {
        "views": [
            {
                "title": "Действия · v11.0",
                "path": "home",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Ворота и доступ"},
                    {
                        "type": "grid",
                        "cards": [
                            {"type": "tile", "entity": "binary_sensor.sectional"},
                        ],
                    },
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


def _trace() -> dict:
    return {
        "semantics": {
            "views": [
                {
                    "id": "home",
                    "modules": [
                        {
                            "instance": "access",
                            "roles": [
                                _role("sectional_gate", "binary_sensor.sectional"),
                            ],
                        },
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


def test_complete_actions_panel_keeps_gate_controls_read_only_and_adds_safe_vacuum_commands() -> None:
    dashboard = render_actions_dashboard(_dashboard(), _trace())
    view = dashboard["views"][0]
    assert view["type"] == "sections"
    assert view["max_columns"] == 2
    assert [section["cards"][0]["heading"] for section in view["sections"]] == [
        "Ворота и доступ",
        "Уборка",
        "Полив",
    ]

    access = view["sections"][0]["cards"]
    assert access[2]["primary"] == "Распашные ворота"
    assert access[2]["secondary"] == "Нет датчика"
    assert access[2]["tap_action"] == {"action": "none"}

    cleaning = view["sections"][1]["cards"]
    assert cleaning[1]["grid_options"] == {"columns": 12, "rows": 1}
    assert cleaning[2]["primary"] == "Ошибки S8 OMNI"
    assert "Ошибок нет" in cleaning[2]["secondary"]
    assert cleaning[2]["entity"] == "sensor.s8_fault"
    assert cleaning[4]["grid_options"] == {"columns": 4, "rows": 1}
    assert cleaning[5]["grid_options"] == {"columns": 4, "rows": 1}
    assert cleaning[6]["grid_options"] == {"columns": 4, "rows": 1}

    start = cleaning[7]
    home = cleaning[8]
    details = cleaning[9]
    assert start["tap_action"] == {
        "action": "perform-action",
        "perform_action": "vacuum.start",
        "target": {"entity_id": "vacuum.s8_omni"},
        "confirmation": {"text": "Начать уборку S8 OMNI?"},
    }
    assert home["tap_action"] == {
        "action": "perform-action",
        "perform_action": "vacuum.return_to_base",
        "target": {"entity_id": "vacuum.s8_omni"},
        "confirmation": {"text": "Отправить S8 OMNI на базу?"},
    }
    assert details["tap_action"]["navigation_path"] == "/dashboard-s8-omni"

    irrigation = view["sections"][2]["cards"][1]
    assert irrigation["tap_action"]["navigation_path"] == "/dashboard-irrigation"

    serialized = json.dumps(dashboard, ensure_ascii=False)
    assert "cover." not in serialized
    assert "cover.open_cover" not in serialized
    assert "cover.close_cover" not in serialized


def test_actions_vacuum_allowlist_fails_closed() -> None:
    with pytest.raises(RenderError, match="unsafe vacuum service"):
        _vacuum_command(
            "vacuum.s8_omni",
            primary="Bad",
            icon="mdi:alert",
            service="vacuum.send_command",
            confirmation="Bad?",
        )
