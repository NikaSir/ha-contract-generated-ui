import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'ha-nikas-rooms': {'sha': 'ed3f7e50b2c9756fddd9f2a79dc14f82f09e8fdc', 'id': 'A40', 'pr': 7}, 'ha-keenetic-hero-4g': {'sha': '40668e90b71484baba2dd2279aa1281e2be3cd8c', 'id': 'A41', 'pr': 95}, 'ha-s8-omni': {'sha': '0780c62f793f95bd941d4b377dfcf2724168342e', 'id': 'A42', 'pr': 133}, 'ha-starline-telemetry': {'sha': 'ecbe026ba7e785265c3d2a746e97d529998443d8', 'id': 'A43', 'pr': 59}, 'ha-vless-gateway': {'sha': '532d45fecd5cd7622be875437da02ff6060252f8', 'id': 'A44', 'pr': 23}, 'ha-zont': {'sha': '9ca0f4eb6b4a9c8ab7e128ed75560e48c38e19e3', 'id': 'A45', 'pr': 33}, 'ha-lider-voltage-control': {'sha': '03dcc945f22f2d8506d1db857706748198566e88', 'id': 'A46', 'pr': 45}}

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
