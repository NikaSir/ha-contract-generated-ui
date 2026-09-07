"""The initial reviewed adoption scope must not silently lose a repository."""

import json
from pathlib import Path


def test_initial_scope_contains_all_maintained_repositories():
    registry = Path(__file__).resolve().parents[1] / "deployments/repository-contracts"
    profiles = [json.loads(path.read_text()) for path in registry.glob("*.json")]
    expected = {
        ".github", "ha-contract-generated-ui", "ha-hikvision-next", "ha-ho-sc-8w",
        "ha-keenetic-hero-4g", "ha-lider-voltage-control", "ha-nikas-access",
        "ha-nikas-climate", "ha-nikas-house", "ha-nikas-rooms", "ha-s8-omni",
        "ha-stark-solarpower", "ha-starline-telemetry", "ha-vless-gateway",
        "ha-water-accounting", "ha-zont", "vless-gateway",
    }
    identities = [profile["repository"] for profile in profiles]
    assert len(identities) == len(set(identities)), "Duplicate repository profile"
    assert set(identities) == {f"NikaSir/{name}" for name in expected}
