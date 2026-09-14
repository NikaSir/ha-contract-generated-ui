import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'ha-nikas-rooms': {'sha': 'fc668b80790973a57f9f701f2bb1aab6b5c99161', 'id': 'A40', 'pr': 7}, 'ha-keenetic-hero-4g': {'sha': '40668e90b71484baba2dd2279aa1281e2be3cd8c', 'id': 'A41', 'pr': 95}, 'ha-s8-omni': {'sha': '0780c62f793f95bd941d4b377dfcf2724168342e', 'id': 'A42', 'pr': 133}, 'ha-starline-telemetry': {'sha': '6fe4277404447e476f7ed7a95e376de0a8f5e26e', 'id': 'A43', 'pr': 59}, 'ha-vless-gateway': {'sha': '532d45fecd5cd7622be875437da02ff6060252f8', 'id': 'A44', 'pr': 23}, 'ha-zont': {'sha': 'c1cf209562850ccb9b42fec7fb2fafb6a7940016', 'id': 'A45', 'pr': 33}, 'ha-lider-voltage-control': {'sha': 'd7144749882cd008537b633a74b3e3eaeea8c871', 'id': 'A46', 'pr': 45}}

@pytest.mark.parametrize('repo', EXPECTED)
def test_standard_governance_reconciliation_preserves_acceptance_boundary(repo):
    expected = EXPECTED[repo]
    profile = json.loads((ROOT / 'deployments/repository-contracts' / (repo + '.json')).read_text())
    assert profile['source_revision'] == expected['sha']
    finding = next((f for f in profile['findings'] if f['id'] == expected['id']), None)
    assert finding is not None
    assert finding['requirement'] == 'repository_checks'
    assert finding['status'] == 'fixed_pending_verification'
    assert 'PR #' + str(expected['pr']) in finding['note']
    evidence = {e['requirement']: e for e in profile['evidence']}
    assert {'scripts/check_standard_documents.py', 'tests/test_standard_document_sync.py'} <= set(evidence['repository_checks']['paths'])
    assert all(e['status'] == 'pending' for e in evidence.values())
    assert evidence['device_acceptance']['paths'] == []
    if repo == 'ha-s8-omni':
        artifact = profile['artifacts'][0]
        assert artifact['ui_version'] == 'v1.0.8'
        assert all(b['expected'] == 'v1.0.8' for b in artifact['bindings'] if b['role'] in ('ui_version', 'cache_key'))
