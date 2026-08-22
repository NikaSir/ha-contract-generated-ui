from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ups_contract_hands_detail_ui_to_stark_panel() -> None:
    contract = _load(ROOT / "contracts" / "infrastructure_ups.yaml")
    bundled = _load(
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "contracts"
        / "infrastructure_ups.yaml"
    )

    assert contract == bundled
    assert contract["metadata"]["version"] == "0.4.0"

    actions = {action["role"]: action for action in contract["spec"]["actions"]}
    assert actions["operating_mode"] == {
        "id": "open_stark_solarpower_panel",
        "kind": "navigate",
        "description": "Открыть каноническую специализированную UPS-панель Stark SolarPower.",
        "role": "operating_mode",
        "target": "/dashboard-ups",
    }

    groups = contract["spec"]["presentation"]["role_groups"]
    assert groups["status"] == [
        "operating_mode",
        "battery_capacity",
        "output_load",
        "cloud_telemetry",
        "data_stale",
        "on_battery",
    ]
    assert groups["telemetry"] == []
    assert "input_voltage" in groups["diagnostic"]
    assert "output_voltage" in groups["diagnostic"]


def test_infrastructure_keeps_ups_handoff_outside_central_power_subviews() -> None:
    manifest = _load(ROOT / "manifests" / "infrastructure.yaml")
    bundled = _load(
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "manifests"
        / "infrastructure.yaml"
    )

    assert manifest == bundled
    assert manifest["metadata"]["version"] == "0.12.0"
    assert manifest["spec"]["app_shell"] == {"active": "infrastructure"}

    views = {view["id"]: view for view in manifest["spec"]["views"]}
    assert set(views) == {
        "overview",
        "power-overview",
        "power-before",
        "power-after",
        "power-history",
    }
    assert all(view["renderer"] == "infrastructure_summary_v1" for view in views.values())

    overview_ups = [
        module
        for module in views["overview"]["modules"]
        if module["contract"] == "infrastructure.ups"
    ]
    assert len(overview_ups) == 2
    assert all(module["groups"] == ["status"] for module in overview_ups)

    for view_id in ("power-overview", "power-before", "power-after", "power-history"):
        assert all(
            module["contract"] != "infrastructure.ups"
            for module in views[view_id]["modules"]
        )

    assert any(
        module["contract"] == "infrastructure.keenetic"
        for module in views["overview"]["modules"]
    )
