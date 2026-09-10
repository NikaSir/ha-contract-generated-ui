"""Pin the four reviewed A19 consumer migrations in the central fleet registry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "deployments" / "repository-contracts"

EXPECTED = {
    "ha-ho-sc-8w": {
        "revision": "fee88c1b86a996281b7c684fed2cd041e1b32dfc",
        "ui_version": "1.0.2",
        "entrypoint": "custom_components/nikas_ho_sc_8w/frontend/irrigation-panel.js",
    },
    "ha-nikas-house": {
        "revision": "27c00b6783a7b6b8e325421db3d45c918bb1c57e",
        "ui_version": "1.0.2",
        "entrypoint": "custom_components/nikas_house/frontend/dist/nikas-house-overview.js",
    },
    "ha-stark-solarpower": {
        "revision": "4059a5b67743e3b8f05a441ace61da32e1e4094d",
        "ui_version": "0.9.6",
        "entrypoint": "custom_components/stark_solarpower/frontend/stark-solarpower-panel-bundle.js",
    },
    "ha-water-accounting": {
        "revision": "9f9bffd3db845374e8211baea9dbe843acc7332b",
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
