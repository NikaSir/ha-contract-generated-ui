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


def test_summary_card_is_native_markdown_with_contract_navigation() -> None:
    card = build_summary_card(_ups_module())
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


def test_infrastructure_v011_uses_summary_renderer_and_bundled_source_matches() -> None:
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
    assert manifest["metadata"]["version"] == "0.11.0"
    assert manifest["spec"]["views"][0]["renderer"] == "infrastructure_summary_v1"
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
    card = build_summary_card(_ups_module())
    content = card["content"]
    assert '<table role="presentation"' in content
    assert '<ha-icon icon="mdi:battery"></ha-icon>' in content
    assert "has_value" in content
    assert "state_translated" in content
    assert "customElements" not in content
