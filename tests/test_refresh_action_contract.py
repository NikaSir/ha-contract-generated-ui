"""Guard the canonical refresh agreement; this is not panel runtime certification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = "docs/NIKAS_REFRESH_ACTION_CONTRACT.md"
CASES = [
    "activation", "fast_success", "slow_success", "duplicate_activation",
    "failure_cleanup", "unavailable_targets", "render_stability",
    "context_preservation", "reduced_motion", "truthful_freshness",
    "result_presentation", "retry_during_result", "partial_failure", "disconnect_cleanup",
]
EXPECTED = {
    "version": "1.1",
    "status": "required",
    "applies_when": "refresh_action_present",
    "path": PATH,
    "busy_animation": "rotate",
    "minimum_visible_ms": 900,
    "busy_until": "request_settled_and_minimum_elapsed",
    "duplicate_activation": "blocked",
    "aria_busy": True,
    "failure_notification": True,
    "completion_feedback": {
        "visible_ms": 1400,
        "success_icon": "mdi:check",
        "success_color": "#43a047",
        "error_icon": "mdi:alert-circle-outline",
        "error_color": "#e53935",
        "idle_icon": "mdi:refresh",
        "idle_color": "var(--primary-color)",
        "success_semantics": "all_required_requests_explicitly_succeeded",
        "retry_during_result": True,
        "cancel_previous_timer_on_retry": True,
        "preserve_result_deadline_on_render": True,
        "disconnect_cleanup": True,
        "geometry_unchanged": True,
        "accessible_result_name": True,
    },
    "reduced_motion": "static_busy_surface",
    "execution_scope": "read_only_telemetry",
    "freshness": "accepted_sample_only",
    "update_mode": "point-patch",
    "preserve": ["header", "active_tab", "peer", "work_viewport", "scroll", "zoom", "editor_draft"],
    "test_source": "production_entrypoint",
    "required_cases": CASES,
    "browser_acceptance_required": True,
}


def config() -> dict:
    return json.loads((ROOT / ".nikas-ui-standard.json").read_text(encoding="utf-8"))


def test_refresh_contract_is_required_and_exact() -> None:
    data = config()
    assert data["version"] == "2.2"
    actual = dict(data["refresh_action_feedback"])
    digest = actual.pop("sha256")
    assert actual == EXPECTED
    assert len(digest) == 64
    assert digest == hashlib.sha256((ROOT / PATH).read_bytes()).hexdigest()


@pytest.mark.parametrize("case", CASES)
def test_each_production_case_remains_in_the_rule(case: str) -> None:
    document = (ROOT / PATH).read_text(encoding="utf-8")
    assert f"| `{case}` |" in document


@pytest.mark.parametrize("number", range(1, 8))
def test_mandatory_behavior_sections_remain_present(number: int) -> None:
    document = (ROOT / PATH).read_text(encoding="utf-8")
    assert f"### REFRESH-{number:02d} — " in document


def test_rule_is_discoverable_and_does_not_claim_fleet_acceptance() -> None:
    document = (ROOT / PATH).read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"]({PATH})" in readme
    assert "required companion" in readme.lower()
    assert "REQUIRED companion to NikaS Specialized Panel UI Standard v2.2" in document
    assert "Missing evidence is `GAP`, not an assumed pass." in document
    assert "does not execute every panel's runtime" in document
    assert "Browser checks are required" in document
