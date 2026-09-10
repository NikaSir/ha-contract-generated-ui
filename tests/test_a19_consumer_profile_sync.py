"""Pin the four reviewed A19 consumer migrations in the central fleet registry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "deployments" / "repository-contracts"

EXPECTED = {
    "ha-ho-sc-8w": {
        "revision": "4cacd889a9d981d34f6e025135f81467baf01617",
        "ui_version": "1.0.3",
        "entrypoint": "custom_components/nikas_ho_sc_8w/frontend/irrigation-panel.js",
    },
    "ha-nikas-house": {
        "revision": "dc34ea6007c42ea19b4b5aa210ee97fd7d9551d7",
        "ui_version": "1.0.2",
        "entrypoint": "custom_components/nikas_house/frontend/dist/nikas-house-overview.js",
    },
    "ha-stark-solarpower": {
        "revision": "4e931954e39a6bd5c61e0c1b52571b67d68233bd",
        "ui_version": "0.9.6",
        "entrypoint": "custom_components/stark_solarpower/frontend/stark-solarpower-panel-bundle.js",
    },
    "ha-water-accounting": {
        "revision": "7251a44aceeda16bc23c41ff111c241a643c0961",
        "ui_version": "0.1.5",
        "entrypoint": "custom_components/water_accounting/frontend/water-accounting-panel.js",
    },
}


def profile(name: str) -> dict:
    return json.loads((REGISTRY / f"{name}.json").read_text(encoding="utf-8"))


def test_a19_profiles_pin_reviewed_main_revisions_and_production_versions() -> None:
    for name, expected in EXPECTED.items():
        current = profile(name)
        panel = next(item for item in current["artifacts"] if item["id"] == "panel")
        assert current["source_revision"] == expected["revision"]
        assert current["standards"]["observed_version"] == "2.2"
        assert current["standards"]["required_version"] == "2.2"
        assert panel["path"] == expected["entrypoint"]
        assert panel["ui_version"] == expected["ui_version"]
        assert all(
            finding["status"] == "fixed_pending_verification"
            for finding in current["findings"]
        )


def test_ho_profile_records_owner_approved_release_driven_hacs_policy() -> None:
    current = profile("ha-ho-sc-8w")
    assert current["publication"] == {
        "default_branch": "main",
        "github_releases": True,
        "automatic_tags": True,
    }
    assert ".github/workflows/publish-hacs-release.yml" in current["observed_workflow_paths"]


def test_ho_schedule_summary_reconciliation_keeps_acceptance_pending() -> None:
    current = profile("ha-ho-sc-8w")
    panel = current["artifacts"][0]
    bindings = {item["role"]: item for item in panel["bindings"]}
    assert bindings["ui_version"]["expected"] == "1.0.3"
    assert bindings["cache_key"]["expected"] == "1.0.3"
    evidence = {item["requirement"]: item for item in current["evidence"]}
    assert "scripts/check-zone-schedule-summary-ui.mjs" in evidence["repository_checks"]["paths"]
    assert all(item["status"] == "pending" for item in current["evidence"])
    assert evidence["device_acceptance"]["paths"] == []
