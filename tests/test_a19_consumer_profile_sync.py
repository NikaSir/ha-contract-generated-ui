"""Pin the four reviewed A19 consumer migrations in the central fleet registry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "deployments" / "repository-contracts"

EXPECTED = {'ha-ho-sc-8w': {'revision': '8e4e1bf755105a3bef88ca6bfa04175bc5c5d4c6', 'ui_version': '1.1.1', 'entrypoint': 'custom_components/nikas_ho_sc_8w/frontend/irrigation-panel.js'}, 'ha-nikas-house': {'revision': '97f7d137f54c891a6acea69d84aa2da9de2ae453', 'ui_version': '1.0.3', 'entrypoint': 'custom_components/nikas_house/frontend/dist/nikas-house-overview.js'}, 'ha-stark-solarpower': {'revision': '331a7dcad89cc8e85d9a4c93f200828175c022db', 'ui_version': '0.9.8', 'entrypoint': 'custom_components/stark_solarpower/frontend/stark-solarpower-panel-bundle.js'}, 'ha-water-accounting': {'revision': '889c22f44ce56559eede919099340c48ead1c386', 'ui_version': '0.1.6', 'entrypoint': 'custom_components/water_accounting/frontend/water-accounting-panel.js'}}


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
    assert bindings["ui_version"]["expected"] == "1.1.1"
    assert bindings["cache_key"]["expected"] == "1.1.1"
    evidence = {item["requirement"]: item for item in current["evidence"]}
    assert "scripts/check-zone-schedule-summary-ui.mjs" in evidence["repository_checks"]["paths"]
    assert all(item["status"] == "pending" for item in current["evidence"])
    assert evidence["device_acceptance"]["paths"] == []
