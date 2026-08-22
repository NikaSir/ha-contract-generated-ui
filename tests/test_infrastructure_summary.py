from __future__ import annotations

from pathlib import Path

import yaml

from generator.infrastructure_summary import build_summary_card
from generator.render_infrastructure_summary import _filter_trace, _summary_dashboard

ROOT = Path(__file__).parents[1]


def _role(name: str, entity: str, *, target: str | None = None) -> dict:
    action = {"kind": "navigate", "target": target} if target else {"kind": "more_info"}
    return {
        "role": name,
        "label": name,
        "entity_id": entity,
        "domain": entity.split(".", 1)[0],
        "action": action,
    }


def _ups_module() -> dict:
    return {
        "instance": "ups_internet",
        "contract": "infrastructure.ups",
        "title": "UPS Интернет",
        "roles": [
            _role("operating_mode", "sensor.ups_mode", target="/dashboard-ups"),
            _role("battery_capacity", "sensor.ups_battery"),
            _role("output_load", "sensor.ups_load"),
            _role("cloud_telemetry", "binary_sensor.ups_cloud"),
            _role("data_stale", "binary_sensor.ups_stale"),
            _role("on_battery", "binary_sensor.ups_on_battery"),
            _role("data_age", "sensor.ups_age"),
        ],
    }


def _power_module() -> dict:
    return {
        "instance": "power",
        "contract": "infrastructure.power_grid",
        "title": "Электросеть",
        "roles": [
            _role("grid_ok", "binary_sensor.grid_ok", target="/dashboard-infrastructure/power-overview"),
            _role("meter_online", "binary_sensor.meter_online"),
            _role("phase_loss", "binary_sensor.phase_loss"),
            _role("phase_a_present", "binary_sensor.phase_a_present"),
            _role("phase_b_present", "binary_sensor.phase_b_present"),
            _role("phase_c_present", "binary_sensor.phase_c_present"),
            _role("voltage_a", "sensor.voltage_a"),
            _role("voltage_b", "sensor.voltage_b"),
            _role("voltage_c", "sensor.voltage_c"),
            _role("voltage_imbalance", "sensor.voltage_imbalance"),
            _role("total_power", "sensor.total_power"),
            _role("non_interruptible_voltage", "sensor.boiler_input_voltage"),
            _role("non_interruptible_frequency", "sensor.boiler_input_frequency"),
            _role("non_interruptible_mode", "sensor.boiler_mode"),
            _role("non_interruptible_data_stale", "binary_sensor.boiler_stale"),
        ],
    }


def test_summary_card_is_native_markdown_with_contract_navigation() -> None:
    card = build_summary_card(_ups_module(), view_id="overview")
    assert card["type"] == "markdown"
    assert card["tap_action"] == {
        "action": "navigate",
        "navigation_path": "/dashboard-ups",
    }
    assert card["grid_options"] == {"columns": "full"}
    assert set(card["entity_id"]) == {
        "sensor.ups_mode",
        "sensor.ups_battery",
        "sensor.ups_load",
        "binary_sensor.ups_cloud",
        "binary_sensor.ups_stale",
        "binary_sensor.ups_on_battery",
    }
    assert "sensor.ups_age" not in card["entity_id"]
    assert "UPS Интернет" in card["content"]
    assert "Подробнее" in card["content"]
    assert "state_translated" in card["content"]
    assert "custom:" not in str(card)


def test_power_overview_is_native_three_point_subpanel() -> None:
    card = build_summary_card(_power_module(), view_id="power-overview")
    assert card["type"] == "vertical-stack"
    assert "custom:" not in str(card)
    text = str(card)
    assert "1. До стабилизаторов" in text
    assert "2. После стабилизаторов" in text
    assert "3. Неотключаемая линия · UPS Котёл" in text
    assert "sensor.boiler_input_voltage" in text
    assert "sensor.boiler_input_frequency" in text
    assert "sensor.boiler_mode" in text
    assert "210–230 В" in text


def test_power_after_view_fails_closed_without_fake_measurements() -> None:
    card = build_summary_card(_power_module(), view_id="power-after")
    assert card["type"] == "markdown"
    assert "не использует входящие фазы как замену" in card["content"]
    assert "проверенные semantic bindings" in card["content"]
    assert "210–230 В" in card["content"]
    assert "sensor.voltage_a" not in str(card)
    assert "custom:" not in str(card)


def test_power_history_uses_incoming_phases_and_boiler_line_voltage() -> None:
    card = build_summary_card(_power_module(), view_id="power-history")
    assert card == {
        "type": "history-graph",
        "title": "Напряжение · 24 часа",
        "hours_to_show": 24,
        "entities": [
            "sensor.voltage_a",
            "sensor.voltage_b",
            "sensor.voltage_c",
            "sensor.boiler_input_voltage",
        ],
        "grid_options": {"columns": "full"},
    }


def test_power_subview_renderer_marks_home_assistant_subview() -> None:
    module = _power_module()
    dashboard = {
        "views": [
            {
                "title": "Электросеть",
                "path": "power-overview",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Электросеть"},
                    {"type": "grid", "cards": []},
                ],
            }
        ]
    }
    trace = {
        "bindings": {
            f"power-overview.power.{role['role']}": {}
            for role in module["roles"]
        },
        "semantics": {
            "views": [
                {
                    "id": "power-overview",
                    "modules": [module],
                }
            ]
        },
    }

    rendered = _summary_dashboard(dashboard, trace)
    view = rendered["views"][0]
    assert view["type"] == "sections"
    assert view["subview"] is True
    assert view["max_columns"] == 1
    assert view["sections"][0]["cards"][0]["type"] == "vertical-stack"

    filtered = _filter_trace(trace)
    assert "power-overview.power.non_interruptible_voltage" in filtered["bindings"]
    assert "power-overview.power.non_interruptible_frequency" in filtered["bindings"]
    assert "power-overview.power.non_interruptible_mode" in filtered["bindings"]


def test_summary_renderer_filters_trace_to_visible_semantics() -> None:
    module = _ups_module()
    trace = {
        "bindings": {
            "overview.ups_internet.operating_mode": {},
            "overview.ups_internet.battery_capacity": {},
            "overview.ups_internet.output_load": {},
            "overview.ups_internet.cloud_telemetry": {},
            "overview.ups_internet.data_stale": {},
            "overview.ups_internet.on_battery": {},
            "overview.ups_internet.data_age": {},
        },
        "semantics": {
            "views": [
                {
                    "id": "overview",
                    "modules": [module],
                }
            ]
        },
    }
    dashboard = {
        "views": [
            {
                "title": "Infrastructure",
                "path": "overview",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "UPS Интернет"},
                    {"type": "grid", "cards": []},
                ],
            }
        ]
    }

    rendered = _summary_dashboard(dashboard, trace)
    view = rendered["views"][0]
    assert view["type"] == "sections"
    card = view["sections"][0]["cards"][0]
    assert card["type"] == "markdown"
    assert "custom:" not in str(rendered)

    filtered = _filter_trace(trace)
    roles = filtered["semantics"]["views"][0]["modules"][0]["roles"]
    assert [role["role"] for role in roles] == [
        "operating_mode",
        "battery_capacity",
        "output_load",
        "cloud_telemetry",
        "data_stale",
        "on_battery",
    ]
    assert "overview.ups_internet.data_age" not in filtered["bindings"]


def test_infrastructure_v012_uses_native_power_subviews_and_boiler_line() -> None:
    manifest_path = ROOT / "manifests" / "infrastructure.yaml"
    bundled_path = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "manifests"
        / "infrastructure.yaml"
    )
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["metadata"]["version"] == "0.12.0"
    assert [view["id"] for view in manifest["spec"]["views"]] == [
        "overview",
        "power-overview",
        "power-before",
        "power-after",
        "power-history",
    ]
    assert all(
        view["renderer"] == "infrastructure_summary_v1"
        for view in manifest["spec"]["views"]
    )
    power = manifest["spec"]["views"][0]["modules"][0]["bindings"]
    assert power["non_interruptible_voltage"] == "infrastructure.ups.boiler.input_voltage"
    assert power["non_interruptible_frequency"] == "infrastructure.ups.boiler.input_frequency"
    assert power["non_interruptible_mode"] == "infrastructure.ups.boiler.operating_mode"
    assert power["non_interruptible_data_stale"] == "infrastructure.ups.boiler.data_stale"
    assert bundled_path.read_bytes() == manifest_path.read_bytes()


def test_summary_model_runtime_and_generator_sources_are_byte_equivalent() -> None:
    generator_source = (ROOT / "generator" / "infrastructure_summary.py").read_bytes()
    runtime_source = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "runtime_infrastructure_summary.py"
    ).read_bytes()
    assert generator_source == runtime_source


def test_native_summary_uses_supported_markdown_features_only() -> None:
    card = build_summary_card(_ups_module(), view_id="overview")
    content = card["content"]
    assert '<table role="presentation"' in content
    assert '<ha-icon icon="mdi:battery"></ha-icon>' in content
    assert "has_value" in content
    assert "state_translated" in content
    assert "customElements" not in content
