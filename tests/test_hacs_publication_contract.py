"""Guard the canonical HACS publication agreement; this is not fleet delivery certification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = "docs/NIKAS_HACS_PUBLICATION_CONTRACT.md"
CASES = [
    "manifest_version",
    "release_exact_match",
    "release_target",
    "idempotent_publish",
    "hacs_validation",
    "no_release_assets_by_default",
    "delivery_acceptance",
]


def config() -> dict:
    return json.loads((ROOT / ".nikas-ui-standard.json").read_text(encoding="utf-8"))


def test_hacs_publication_contract_is_required_and_pinned() -> None:
    policy = config()["hacs_publication"]
    assert policy["version"] == "1.0"
    assert policy["status"] == "required"
    assert policy["applies_when"] == "hacs_distributed_integration"
    assert policy["path"] == PATH
    assert policy["version_source"] == "custom_components/<domain>/manifest.json"
    assert policy["delivery_boundary"] == "hacs_visible_release_when_release_driven"
    assert policy["main_is_delivery"] is False
    assert policy["release_version"] == "exact_manifest_version"
    assert policy["release_target"] == "merged_main_commit_with_manifest_version"
    assert policy["idempotent_publish"] is True
    assert policy["default_custom_assets"] is False
    assert policy["publication_permission"] == "contents_write_publication_workflow_only"
    assert policy["unsupported_branch_install_after_rejection"] is True
    assert policy["required_cases"] == CASES
    assert policy["sha256"] == hashlib.sha256((ROOT / PATH).read_bytes()).hexdigest()


def test_delivery_states_cannot_be_collapsed() -> None:
    states = config()["hacs_publication"]["states"]
    assert states == {
        "merged_main": "code_accepted",
        "matching_release": "published_to_hacs_channel",
        "hacs_installable": "delivered",
        "device_acceptance": "accepted_in_operation",
    }
    assert len(set(states.values())) == 4


@pytest.mark.parametrize("number", range(1, 9))
def test_mandatory_hacs_rules_remain_present(number: int) -> None:
    document = (ROOT / PATH).read_text(encoding="utf-8")
    assert f"### HACS-{number:02d} — " in document


@pytest.mark.parametrize("case", CASES)
def test_each_required_case_remains_in_the_contract(case: str) -> None:
    document = (ROOT / PATH).read_text(encoding="utf-8")
    assert f"| `{case}` |" in document


def test_frontend_delivery_standard_no_longer_forbids_hacs_releases() -> None:
    frontend = (ROOT / "docs/SPECIALIZED_PANEL_FRONTEND_RELEASE_STANDARD.md").read_text(encoding="utf-8")
    assert "Frontend Delivery Standard v1.8" in frontend
    assert "accepted code but not delivered software" in frontend
    assert "GitHub Releases and automatic release tags are not created" not in frontend
    assert "NIKAS_HACS_PUBLICATION_CONTRACT.md" in frontend


def test_contract_records_observed_main_install_rejection() -> None:
    document = (ROOT / PATH).read_text(encoding="utf-8")
    assert "Installing `main` through `update.install` was then rejected by HACS" in document
    assert "do not instruct the user to retry the same path" in document
