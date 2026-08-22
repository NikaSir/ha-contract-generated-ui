from __future__ import annotations

from generator.render_operational import _filter_trace, _operational_dashboard


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


def test_overview_and_diagnostics_are_explicitly_separated() -> None:
    contracts = {"infra.test": _contract()}
    manifest = _manifest()
    dashboard = _operational_dashboard(_dashboard(), _trace(), contracts, manifest)

    overview_cards = dashboard["views"][0]["sections"][0]["cards"]
    assert [card["type"] for card in overview_cards] == ["heading", "tile", "tile"]
    assert overview_cards[1]["entity"] == "sensor.status"
    assert overview_cards[2]["entity"] == "sensor.telemetry"

    diagnostic_cards = dashboard["views"][1]["sections"][0]["cards"]
    assert [card["type"] for card in diagnostic_cards] == ["heading", "entities"]
    assert "title" not in diagnostic_cards[1]
    assert diagnostic_cards[1]["entities"] == [
        {"entity": "sensor.diagnostic", "name": "Diagnostic"}
    ]

    filtered = _filter_trace(_trace(), contracts, manifest)
    overview_roles = filtered["semantics"]["views"][0]["modules"][0]["roles"]
    diagnostic_roles = filtered["semantics"]["views"][1]["modules"][0]["roles"]
    assert [role["role"] for role in overview_roles] == ["status", "telemetry"]
    assert [role["role"] for role in diagnostic_roles] == ["diagnostic"]
    assert set(filtered["bindings"]) == {
        "overview.test.status",
        "overview.test.telemetry",
        "diagnostics.test.diagnostic",
    }
