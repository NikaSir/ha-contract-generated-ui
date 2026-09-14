from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "deployments" / "repository-contracts"


def load(name: str) -> dict:
    return json.loads((PROFILES / name).read_text(encoding="utf-8"))


def finding(profile: dict, finding_id: str) -> dict:
    return next(item for item in profile["findings"] if item["id"] == finding_id)


def test_hikvision_profile_tracks_fixed_main_findings() -> None:
    profile = load("ha-hikvision-next.json")
    assert profile["source_revision"] == "16f058095019bfbca571dc5e7e13fd1d7ded41d6"
    assert finding(profile, "A02")["status"] == "fixed_pending_verification"
    assert finding(profile, "A13")["status"] == "fixed_pending_verification"
    assert finding(profile, "A14")["status"] == "fixed_pending_verification"
    assert "tests/test_coordinator.py" in profile["evidence"][3]["paths"]


def test_keenetic_profile_tracks_fixed_main_finding() -> None:
    profile = load("ha-keenetic-hero-4g.json")
    assert profile["source_revision"] == "40668e90b71484baba2dd2279aa1281e2be3cd8c"
    assert finding(profile, "A15")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert "tests/test_wan_contract.py" in data_quality["paths"]


def test_house_profile_records_full_hacs_validation_without_device_acceptance() -> None:
    profile = load("ha-nikas-house.json")
    assert profile["source_revision"] == "97f7d137f54c891a6acea69d84aa2da9de2ae453"
    assert "A30" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A30")["requirement"] == "repository_checks"
    assert finding(profile, "A30")["status"] == "fixed_pending_verification"
    assert profile["artifacts"][0]["ui_version"] == "1.0.3"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "tests/test_hacs_validation_contract.py" in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_keenetic_profile_records_required_delivery_without_device_acceptance() -> None:
    profile = load("ha-keenetic-hero-4g.json")
    assert "A28" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A28")["requirement"] == "repository_checks"
    assert finding(profile, "A28")["status"] == "fixed_pending_verification"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    for path in (".github/workflows/repository-checks.yml",
                 "scripts/build_frontend_bundle.py", "scripts/check_nikas_ui_standard.py",
                 "tests/test_required_frontend_delivery.py"):
        assert path in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_water_profile_records_full_hacs_validation_without_device_acceptance() -> None:
    profile = load("ha-water-accounting.json")
    assert profile["source_revision"] == "889c22f44ce56559eede919099340c48ead1c386"
    assert "A27" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A27")["requirement"] == "repository_checks"
    assert finding(profile, "A27")["status"] == "fixed_pending_verification"
    assert profile["artifacts"][0]["ui_version"] == "0.1.6"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "tests/test_hacs_validation_contract.py" in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_hikvision_profile_records_required_regressions_without_device_acceptance() -> None:
    profile = load("ha-hikvision-next.json")
    assert "A26" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A26")["requirement"] == "repository_checks"
    assert finding(profile, "A26")["status"] == "fixed_pending_verification"
    assert profile["observed_workflow_paths"] == [
        ".github/workflows/hacs.yml", ".github/workflows/testing.yml",
    ]
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "tests/test_required_ci_gate.py" in evidence["repository_checks"]["paths"]
    assert ".github/workflows/hassfest.yml" not in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_climate_profile_tracks_fixed_main_findings() -> None:
    profile = load("ha-nikas-climate.json")
    assert profile["source_revision"] == "1c98b256df93a6793708a9462eef392ff1cdf858"
    artifact = profile["artifacts"][0]
    assert artifact["path"] == "custom_components/nikas_climate/frontend/nikas-climate-production.js"
    assert artifact["ui_version"] == "1.4.29"
    assert finding(profile, "A07")["status"] == "fixed_pending_verification"
    assert finding(profile, "A11")["status"] == "fixed_pending_verification"
    assert finding(profile, "A12")["status"] == "fixed_pending_verification"
    assert finding(profile, "A20-CI")["status"] == "fixed_pending_verification"
    assert ".github/workflows/repository-checks.yml" in profile["observed_workflow_paths"]
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "tests/dom_stability.test.cjs" in repository_checks["paths"]


def test_lider_profile_tracks_a03_fix() -> None:
    profile = load("ha-lider-voltage-control.json")
    assert profile["source_revision"] == "03dcc945f22f2d8506d1db857706748198566e88"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.8.10"
    assert finding(profile, "A03")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert "custom_components/lider_voltage_control/frontend/lider-voltage-control-panel-core.js" in data_quality["paths"]


def test_starline_profile_tracks_a04_fix() -> None:
    profile = load("ha-starline-telemetry.json")
    assert profile["source_revision"] == "ecbe026ba7e785265c3d2a746e97d529998443d8"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.6.10"
    assert finding(profile, "A04")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert "tests/test_binary_quality.py" in data_quality["paths"]


def test_lider_profile_records_full_hacs_validation_without_device_acceptance() -> None:
    profile = load("ha-lider-voltage-control.json")
    assert "A29" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A29")["requirement"] == "repository_checks"
    assert finding(profile, "A29")["status"] == "fixed_pending_verification"
    assert profile["artifacts"][0]["ui_version"] == "0.8.10"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "scripts/check-hacs-validation.py" in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_s8_profile_tracks_autonomous_production_main() -> None:
    profile = load("ha-s8-omni.json")
    assert profile["source_revision"] == "0780c62f793f95bd941d4b377dfcf2724168342e"
    artifact = profile["artifacts"][0]
    assert artifact["path"] == "custom_components/s8_omni/frontend/s8-omni-production.js"
    assert artifact["ui_version"] == "v1.0.8"
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
    assert profile["source_revision"] == "29ad98ac191d210f36c75ed2fde24844637efaf4"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.1.10"
    assert profile["standards"]["observed_version"] == "2.2"
    assert finding(profile, "A08")["status"] == "fixed_pending_verification"
    assert finding(profile, "A19")["status"] == "fixed_pending_verification"
    lifecycle = next(item for item in profile["evidence"] if item["requirement"] == "lifecycle")
    assert "tests/test_lifecycle_reconnect.py" in lifecycle["paths"]
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "tests/test_refresh_contract.py" in repository_checks["paths"]


def test_access_profile_records_required_python_syntax_without_device_acceptance() -> None:
    profile = load("ha-nikas-access.json")
    assert "A32" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A32")["requirement"] == "repository_checks"
    assert finding(profile, "A32")["status"] == "fixed_pending_verification"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    for path in (".github/workflows/validate.yml", "scripts/check_repository.py",
                 "tests/test_python_syntax_validation.py"):
        assert path in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_rooms_profile_tracks_merged_a08_a09_a10_and_a19() -> None:
    profile = load("ha-nikas-rooms.json")
    assert profile["source_revision"] == "ed3f7e50b2c9756fddd9f2a79dc14f82f09e8fdc"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "11.0.16"
    assert profile["standards"]["observed_version"] == "2.2"
    assert finding(profile, "A08")["status"] == "fixed_pending_verification"
    assert finding(profile, "A09")["status"] == "fixed_pending_verification"
    assert finding(profile, "A10")["status"] == "fixed_pending_verification"
    assert finding(profile, "A19")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    lifecycle = next(item for item in profile["evidence"] if item["requirement"] == "lifecycle")
    assert "tests/registry_loader_harness.js" in data_quality["paths"]
    assert "tests/test_frontend_contract.py" in lifecycle["paths"]


def test_rooms_registration_version_fix_preserves_pending_acceptance() -> None:
    profile = load("ha-nikas-rooms.json")
    assert "A33" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A33")["status"] == "fixed_pending_verification"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "11.0.16"
    bindings = {item["role"]: item for item in artifact["bindings"]}
    assert bindings["cache_key"]["expected"] == "11.0.16"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert "tests/test_registration_version.py" in evidence["repository_checks"]["paths"]
    assert all(item["status"] == "pending" for item in profile["evidence"])
    assert evidence["device_acceptance"]["paths"] == []


def test_rooms_profile_records_required_python_syntax_without_device_acceptance() -> None:
    profile = load("ha-nikas-rooms.json")
    assert "A31" in {item["id"] for item in profile["findings"]}
    assert finding(profile, "A31")["requirement"] == "repository_checks"
    assert finding(profile, "A31")["status"] == "fixed_pending_verification"
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    for path in (".github/workflows/validate.yml", "scripts/check_repository.py",
                 "tests/test_python_syntax_validation.py"):
        assert path in evidence["repository_checks"]["paths"]
    assert evidence["repository_checks"]["status"] == "pending"
    assert evidence["device_acceptance"]["status"] == "pending"
    assert evidence["device_acceptance"]["paths"] == []


def test_zont_profile_tracks_merged_a16_but_keeps_field_acceptance_pending() -> None:
    profile = load("ha-zont.json")
    assert profile["source_revision"] == "9ca0f4eb6b4a9c8ab7e128ed75560e48c38e19e3"
    artifact = profile["artifacts"][0]
    assert artifact["ui_version"] == "0.9.7"
    assert finding(profile, "A16")["status"] == "fixed_pending_verification"
    data_quality = next(item for item in profile["evidence"] if item["requirement"] == "data_quality")
    assert data_quality["status"] == "pending"
    assert "tests/test_zont_dhw_truth.cjs" in data_quality["paths"]


def test_stark_profile_tracks_required_frontend_delivery_gate() -> None:
    profile = load("ha-stark-solarpower.json")
    assert profile["source_revision"] == "331a7dcad89cc8e85d9a4c93f200828175c022db"
    assert finding(profile, "A17")["status"] == "fixed_pending_verification"
    assert finding(profile, "A19")["status"] == "fixed_pending_verification"
    assert finding(profile, "A23")["status"] == "fixed_pending_verification"
    repository_checks = next(item for item in profile["evidence"] if item["requirement"] == "repository_checks")
    assert "scripts/check_frontend_delivery.py" in repository_checks["paths"]
    assert "tests/test_required_frontend_delivery_gate.py" in repository_checks["paths"]


def test_stark_ui_binding_selects_current_header_in_a_bundle_with_historical_constants() -> None:
    profile = load("ha-stark-solarpower.json")
    binding = next(item for item in profile["artifacts"][0]["bindings"] if item["role"] == "ui_version")
    source = '''const UI_VERSION = "0.9.7";
const SAFE_RETURN_ROUTE = "/home/overview";
// BEGIN custom_components/stark_solarpower/frontend/stark-solarpower-panel-v098.js
(() => {
const Panel = customElements.get("stark-solarpower-panel");
const UI_VERSION = "0.9.8";

if (Panel && !Panel.prototype.__starkUiV098) {
'''
    values = [match.group("value") for match in re.finditer(binding["pattern"], source)]
    assert values == ["0.9.8"]


def test_canonical_profile_tracks_completed_a21_main() -> None:
    profile = load("ha-contract-generated-ui.json")
    assert profile["source_revision"] == "759d13f714380972e3b3219dff7cfa3a49f14a2a"
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
    assert profile["source_revision"] == "974b606a524cfbfc4eddd4df649821d112e7c425"
    assert profile["findings"] == []
    assert profile["standards"]["observed_version"] == "2.2"


def test_ha_vless_profile_tracks_document_governance_fix() -> None:
    profile = load("ha-vless-gateway.json")
    assert profile["source_revision"] == "532d45fecd5cd7622be875437da02ff6060252f8"
    assert {item["id"] for item in profile["findings"]} == {"A44", "NAV-1"}
    assert profile["artifacts"][0]["ui_version"] == "0.1.2"


def test_vless_service_profile_tracks_dependency_only_main_drift_without_inventing_findings() -> None:
    profile = load("vless-gateway.json")
    assert profile["source_revision"] == "aa4a0a9f04d084043cabe7b5d0aef3157ca39940"
    assert profile["findings"] == []
    assert profile["standards"]["applicable"] is False


def test_dyson_profile_records_merged_specialized_panel_without_live_acceptance():
    profile = load("ha-nikas-dyson.json")
    assert profile["repository"] == "NikaSir/ha-nikas-dyson"
    assert profile["source_revision"] == "2a246b263ad3fb0398a4ee662e0c1e7a0ffeaae9"
    assert profile["existing_required_checks"] == ["validate"]
    artifact = profile["artifacts"][0]
    assert artifact["path"] == "custom_components/nikas_dyson/frontend/nikas-dyson-panel.js"
    assert artifact["ui_version"] == "1.0.3"
    assert {b["role"] for b in artifact["bindings"]} >= {"entrypoint", "ui_version", "cache_key", "integration_version"}
    assert {item["id"] for item in profile["findings"]} == {"A34", "A35", "A36", "A37", "A38", "A39", "NAV-1"}
    assert all(item["status"] == "fixed_pending_verification" for item in profile["findings"])
    evidence = {item["requirement"]: item for item in profile["evidence"]}
    assert all(item["status"] == "pending" for item in evidence.values())
    assert evidence["device_acceptance"]["paths"] == []
    assert "tests/frontend.cjs" in evidence["data_quality"]["paths"]
    assert "tests/test_options.py" in evidence["data_quality"]["paths"]
    assert "tests/test_ci_gate.py" in evidence["repository_checks"]["paths"]
    assert "topics" in evidence["repository_checks"]["note"]
