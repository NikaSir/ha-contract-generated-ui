from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_house_power_rebind_policy_is_documented_without_private_ids_in_public_manifest() -> None:
    doc = (ROOT / "docs" / "FIELD_POLISH_0292.md").read_text(encoding="utf-8")
    manifest = (ROOT / "manifests" / "house_v11_preview.yaml").read_text(encoding="utf-8")

    assert "sensor.power_monitor_voltage_a" in doc
    assert "sensor.power_monitor_voltage_b" in doc
    assert "sensor.power_monitor_voltage_c" in doc
    assert "sensor.power_monitor_voltage_a" not in manifest
    assert "sensor.power_monitor_voltage_b" not in manifest
    assert "sensor.power_monitor_voltage_c" not in manifest
