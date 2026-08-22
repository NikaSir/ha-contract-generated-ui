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


def test_summary_card_uses_selected_roles_and_contract_navigation() -> None:
    card = build_summary_card(_ups_module())
    assert card["type"] == "custom:nikas-infrastructure-summary"
    assert card["variant"] == "ups"
    assert card["title"] == "UPS Интернет"
    assert card["details_path"] == "/dashboard-ups"
    assert set(card["roles"]) == {
        "operating_mode",
        "battery_capacity",
        "output_load",
        "cloud_telemetry",
        "data_stale",
        "on_battery",
    }
    assert "data_age" not in card["roles"]
    assert card["grid_options"] == {"columns": "full", "rows": "auto"}


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
    assert card["type"] == "custom:nikas-infrastructure-summary"

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


def test_infrastructure_v08_uses_summary_renderer_and_bundled_source_matches() -> None:
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
    assert manifest["metadata"]["version"] == "0.8.0"
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


def test_frontend_asset_registers_infrastructure_summary_card() -> None:
    asset = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "frontend"
        / "nikas-app-shell.js"
    ).read_text(encoding="utf-8")
    assert 'customElements.define("nikas-infrastructure-summary"' in asset
    assert 'type: "nikas-infrastructure-summary"' in asset
    assert "Данные неполные" in asset
    assert "WAN неизвестен" in asset
