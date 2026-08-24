from __future__ import annotations

from generator.render_infrastructure_summary import _summary_dashboard


def _role(name: str, entity: str, *, target: str | None = None) -> dict:
    action = {"kind": "navigate", "target": target} if target else {"kind": "more_info"}
    return {
        "role": name,
        "label": name,
        "entity_id": entity,
        "domain": entity.split(".", 1)[0],
        "action": action,
    }


def test_ups_summary_never_calls_unreliable_data_current() -> None:
    module = {
        "instance": "ups_boiler",
        "contract": "infrastructure.ups",
        "title": "UPS Котёл",
        "roles": [
            _role("operating_mode", "sensor.ups_mode", target="/dashboard-ups"),
            _role("battery_capacity", "sensor.ups_battery"),
            _role("output_load", "sensor.ups_load"),
            _role("cloud_telemetry", "binary_sensor.ups_cloud"),
            _role("data_stale", "binary_sensor.ups_stale"),
            _role("on_battery", "binary_sensor.ups_on_battery"),
        ],
    }
    dashboard = {
        "views": [
            {
                "title": "Инфраструктура · v0.12",
                "path": "overview",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "UPS Котёл"},
                    {"type": "grid", "cards": []},
                ],
            }
        ]
    }
    trace = {
        "bindings": {},
        "semantics": {"views": [{"id": "overview", "modules": [module]}]},
    }

    rendered = _summary_dashboard(dashboard, trace)
    content = rendered["views"][0]["sections"][0]["cards"][0]["content"]

    assert "{% if not reliable %}Данные недоступны" in content
    assert (
        "{% if not has_value('binary_sensor.ups_stale') %}Свежесть неизвестна"
        "{% elif is_state('binary_sensor.ups_stale', 'on') %}Данные устарели"
        "{% else %}Данные актуальны{% endif %}"
    ) not in content
