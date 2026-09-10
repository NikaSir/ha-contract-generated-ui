from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "deployments" / "repository-contracts"


def load(name: str) -> dict:
    return json.loads((PROFILES / name).read_text(encoding="utf-8"))


def finding(profile: dict, finding_id: str) -> dict:
    return next(item for item in profile["findings"] if item["id"] == finding_id)


def test_hikvision_profile_tracks_fixed_main_findings() -> None:
    profile = load("ha-hikvision-next.json")
    assert profile["source_revision"] == "1af73fcc4e715542d7dc78f1e86b96b22c1bb6ea"
    assert finding(profile, "A02")["status"] == "fixed_pending_verification"
    assert finding(profile, "A13")["status"] == "fixed_pending_verification"
    assert finding(profile, "A14")["status"] == "fixed_pending_verification"
    assert "tests/test_coordinator.py" in profile["evidence"][3]["paths"]


def test_keenetic_profile_tracks_fixed_main_finding() -> None:
    profile = load("ha-keenetic-hero-4g.json")
    assert profile["source_revision"] == "b47abe85e7c1ecd9c26219f39f897c1493a6d048"
    assert finding(profile, "A15")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert "tests/test_wan_contract.py" in data_quality["paths"]


def test_climate_profile_tracks_fixed_main_findings() -> None:
    profile = load("ha-nikas-climate.json")
    assert profile["source_revision"] == "8ed775d4cf9bd8a90fcecbeea63ea018f419fa7d"
    artifact = profile["artifacts"][0]
    assert artifact["path"] == "custom_components/nikas_climate/frontend/nikas-climate-production.js"
    assert artifact["ui_version"] == "1.4.26"
    assert finding(profile, "A07")["status"] == "fixed_pending_verification"
    assert finding(profile, "A11")["status"] == "fixed_pending_verification"
    assert finding(profile, "A12")["status"] == "fixed_pending_verification"
    assert finding(profile, "A20-CI")["status"] == "fixed_pending_verification"
    assert ".github/workflows/repository-checks.yml" in profile["observed_workflow_paths"]
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "tests/dom_stability.test.cjs" in repository_checks["paths"]
