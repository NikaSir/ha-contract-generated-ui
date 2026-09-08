from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = "docs/NIKAS_PANEL_LIFECYCLE_CONTRACT.md"
CASES = [
    "registration_before_refresh",
    "initial_failure_preserves_route",
    "offline_bootstrap",
    "retry_recovery",
    "route_collision",
    "unload_ownership",
    "generated_manifest_ownership",
]


def _config() -> dict:
    return json.loads((ROOT / ".nikas-ui-standard.json").read_text(encoding="utf-8"))


def test_panel_lifecycle_contract_is_required_and_pinned() -> None:
    lifecycle = _config()["panel_lifecycle"]
    assert lifecycle["version"] == "1.0"
    assert lifecycle["status"] == "required"
    assert lifecycle["path"] == CONTRACT_PATH
    assert lifecycle["registration_before_device_io"] is True
    assert lifecycle["initial_failure"] == "panel_remains_registered"
    assert lifecycle["unavailable_rendering"] == "fail_closed"
    assert lifecycle["recovery"] == "coordinator_or_config_entry_retry"
    assert lifecycle["required_cases"] == CASES
    assert lifecycle["sha256"] == hashlib.sha256(
        (ROOT / CONTRACT_PATH).read_bytes()
    ).hexdigest()


@pytest.mark.parametrize("number", range(1, 9))
def test_each_normative_lifecycle_rule_is_present(number: int) -> None:
    contract = (ROOT / CONTRACT_PATH).read_text(encoding="utf-8")
    assert f"### LIFECYCLE-{number:02d} — " in contract


@pytest.mark.parametrize("case", CASES)
def test_each_lifecycle_regression_case_is_present(case: str) -> None:
    contract = (ROOT / CONTRACT_PATH).read_text(encoding="utf-8")
    assert f"| `{case}` |" in contract


def test_ui_standard_requires_the_lifecycle_companion() -> None:
    standard = (
        ROOT / "docs" / "NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md"
    ).read_text(encoding="utf-8")
    assert "## 16. Panel lifecycle and availability" in standard
    assert "NIKAS_PANEL_LIFECYCLE_CONTRACT.md" in standard
    assert "configured panel route is application infrastructure" in standard


def test_fleet_baseline_covers_current_panel_owners() -> None:
    audit = (
        ROOT / "docs" / "audits" / "2026-09-08-panel-lifecycle-baseline.md"
    ).read_text(encoding="utf-8")
    for repository in (
        "ha-keenetic-hero-4g",
        "ha-s8-omni",
        "ha-ho-sc-8w",
        "ha-stark-solarpower",
        "ha-starline-telemetry",
        "ha-nikas-house",
        "ha-lider-voltage-control",
        "ha-nikas-access",
        "ha-nikas-climate",
        "ha-nikas-rooms",
        "ha-vless-gateway",
        "ha-water-accounting",
        "ha-zont",
        "ha-hikvision-next",
    ):
        assert f"`{repository}`" in audit
