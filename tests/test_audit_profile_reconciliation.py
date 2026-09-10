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


def test_lider_profile_tracks_a03_fix() -> None:
    profile = load("ha-lider-voltage-control.json")
    assert profile["source_revision"] == "7e62320cf08daa53dd8d890e5bef4b7586ad19e5"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.8.7"
    assert finding(profile, "A03")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert "custom_components/lider_voltage_control/frontend/lider-voltage-control-panel-core.js" in data_quality["paths"]


def test_starline_profile_tracks_a04_fix() -> None:
    profile = load("ha-starline-telemetry.json")
    assert profile["source_revision"] == "d079f0843a083b94d13e6dd1552fd2d1b7464ba9"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.6.9"
    assert finding(profile, "A04")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert "tests/test_binary_quality.py" in data_quality["paths"]


def test_s8_profile_tracks_autonomous_production_main() -> None:
    profile = load("ha-s8-omni.json")
    assert profile["source_revision"] == "1cfa4f58d7977e9bc99ced2442a5690b02691ff9"
    artifact = profile["artifacts"][0]
    assert artifact["path"] == "custom_components/s8_omni/frontend/s8-omni-production.js"
    assert artifact["ui_version"] == "v1.0.5"
    assert finding(profile, "A05")["status"] == "fixed_pending_verification"
    assert finding(profile, "REG-S8-IMPORTS")["status"] == "fixed_pending_verification"
    assert artifact["binding_limitations"] == []
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "tests/test_autonomous_production_bundle.py" in repository_checks["paths"]


def test_starline_profile_records_full_hacs_validation_without_field_acceptance() -> None:
    profile = load("ha-starline-telemetry.json")
    assert "A25" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A25")["requirement"] == "repository_checks"
    assert finding(profile, "A25")["status"] == "fixed_pending_verification"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "tests/test_hacs_validation_contract.py" in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_starline_profile_references_current_workflow_evidence() -> None:
    profile = load("ha-starline-telemetry.json")
    assert profile["observed_workflow_paths"] == [".github/workflows/repository-checks.yml"]
    checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert {path for path in checks["paths"] if path.startswith(".github/workflows/")} == {
        ".github/workflows/repository-checks.yml"
    }


def test_s8_governance_reconciliation_keeps_acceptance_pending() -> None:
    profile = load("ha-s8-omni.json")
    assert "A24" in {item["id"] for item in profile["findings"]}
    governance = finding(profile, "A24")
    assert governance["requirement"] == "repository_checks"
    assert governance["status"] == "fixed_pending_verification"
    assert profile["observed_workflow_paths"] == [".github/workflows/repository-checks.yml"]
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "tests/test_required_hacs_gate.py" in evidence["repository_checks"]["paths"]
    assert ".github/workflows/repository-checks.yml" in evidence["repository_checks"]["paths"]
    for requirement in ("repository_checks", "device_acceptance", "data_quality",
                        "command_safety", "lifecycle"):
        assert evidence[requirement]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_access_profile_tracks_merged_a08_and_a19() -> None:
    profile = load("ha-nikas-access.json")
    assert profile["source_revision"] == "afdb7d2999d06a96540c4700c116546f43994855"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.1.9"
    assert profile["standards"]["observed_version"] == "2.2"
    assert finding(profile, "A08")["status"] == "fixed_pending_verification"
    assert finding(profile, "A19")["status"] == "fixed_pending_verification"
    lifecycle = next(item for item in profile["evidence"] if item["requirement"] == "lifecycle")
    assert "tests/test_lifecycle_reconnect.py" in lifecycle["paths"]
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "tests/test_refresh_contract.py" in repository_checks["paths"]


def test_rooms_profile_tracks_merged_a08_a09_a10_and_a19() -> None:
    profile = load("ha-nikas-rooms.json")
    assert profile["source_revision"] == "80f2e34c392198ed1efff9ea29b20f262af9efda"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "11.0.15"
    assert profile["standards"]["observed_version"] == "2.2"
    assert finding(profile, "A08")["status"] == "fixed_pending_verification"
    assert finding(profile, "A09")["status"] == "fixed_pending_verification"
    assert finding(profile, "A10")["status"] == "fixed_pending_verification"
    assert finding(profile, "A19")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    lifecycle = next(item for item in profile["evidence"] if item["requirement"] == "lifecycle")
    assert "tests/registry_loader_harness.js" in data_quality["paths"]
    assert "tests/test_frontend_contract.py" in lifecycle["paths"]


def test_zont_profile_tracks_merged_a16_but_keeps_field_acceptance_pending() -> None:
    profile = load("ha-zont.json")
    assert profile["source_revision"] == "a96d8169d9be9a96617f186cfabd1fe2abad0efb"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.9.6"
    assert finding(profile, "A16")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert data_quality["status"] == "pending"
    assert "tests/test_zont_dhw_truth.cjs" in data_quality["paths"]


def test_stark_profile_tracks_required_frontend_delivery_gate() -> None:
    profile = load("ha-stark-solarpower.json")
    assert profile["source_revision"] == "4e931954e39a6bd5c61e0c1b52571b67d68233bd"
    assert finding(profile, "A17")["status"] == "fixed_pending_verification"
    assert finding(profile, "A19")["status"] == "fixed_pending_verification"
    assert finding(profile, "A23")["status"] == "fixed_pending_verification"
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "scripts/check_frontend_delivery.py" in repository_checks["paths"]
    assert "tests/test_required_frontend_delivery_gate.py" in repository_checks["paths"]


def test_canonical_profile_tracks_completed_a21_main() -> None:
    profile = load("ha-contract-generated-ui.json")
    assert profile["source_revision"] == "ade2d1197e9b795d435ac1b57f8393d5fde4b40c"
    assert profile["observed_workflow_paths"] == [
        ".github/workflows/nikas-fleet-inspection.yml",
        ".github/workflows/repository-checks.yml",
    ]
    assert finding(profile, "A21")["status"] == "fixed_pending_verification"
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "tests/test_ci_gate.py" in repository_checks["paths"]
    assert "nikas-required-gate" in repository_checks["note"]
    assert "validate" not in finding(profile, "A21")["note"]


def test_organization_mirror_profile_tracks_current_main_without_inventing_findings() -> None:
    profile = load("nikasir-github.json")
    assert profile["source_revision"] == "4c3fe20c2ee2aaa2ce82e3255930656be4a22ea7"
    assert profile["findings"] == []
    assert profile["standards"]["observed_version"] == "2.2"


def test_ha_vless_profile_tracks_dependency_only_main_drift_without_inventing_findings() -> None:
    profile = load("ha-vless-gateway.json")
    assert profile["source_revision"] == "06eb754c06997c3181c2a94c9fdcb5966cb26f14"
    assert profile["findings"] == []
    assert profile["artifacts"][0]["ui_version"] == "0.1.1"


def test_vless_service_profile_tracks_dependency_only_main_drift_without_inventing_findings() -> None:
    profile = load("vless-gateway.json")
    assert profile["source_revision"] == "aa4a0a9f04d084043cabe7b5d0aef3157ca39940"
    assert profile["findings"] == []
    assert profile["standards"]["applicable"] is False
