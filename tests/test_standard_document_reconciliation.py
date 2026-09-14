import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'ha-nikas-rooms': {'sha': 'aa0d5e211bb38cd95b52263e8391e55f99327090', 'id': 'A40', 'pr': 7}, 'ha-keenetic-hero-4g': {'sha': '40668e90b71484baba2dd2279aa1281e2be3cd8c', 'id': 'A41', 'pr': 95}, 'ha-s8-omni': {'sha': '53b609d23183b86f5d016da80fcbdf6beb4c396b', 'id': 'A42', 'pr': 133}, 'ha-starline-telemetry': {'sha': '1b7e819833d210f95b5f1bb40f29c3d20693344f', 'id': 'A43', 'pr': 59}, 'ha-vless-gateway': {'sha': '5aa7c3b1090cf322c3321ee7446388a25915b229', 'id': 'A44', 'pr': 23}, 'ha-zont': {'sha': '508f4f3db76bc60be42fb644eba23b5737cfd62d', 'id': 'A45', 'pr': 33}, 'ha-lider-voltage-control': {'sha': 'cea8d1c85bb371a5322a5579e6478d4186341b40', 'id': 'A46', 'pr': 45}}

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
