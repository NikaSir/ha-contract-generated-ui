import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'ha-nikas-rooms': {'sha': '03ee44f56459e2356f7680e5498858d0973000c5', 'id': 'A40', 'pr': 7}, 'ha-keenetic-hero-4g': {'sha': 'f5c2cb7a74d58559004c5056b51974eb2c5a1c2d', 'id': 'A41', 'pr': 95}, 'ha-s8-omni': {'sha': '32ca842494fc467e71e6bb613e423f2188bfc5f2', 'id': 'A42', 'pr': 133}, 'ha-starline-telemetry': {'sha': '5f4496280d8a23b8761972ddc60ffb08cd056062', 'id': 'A43', 'pr': 59}, 'ha-vless-gateway': {'sha': '4b78e29157da9f89cc6f3a816fb9f69a9aee757e', 'id': 'A44', 'pr': 23}, 'ha-zont': {'sha': '012d1841b7aeee0c6bf40079e61dddabd5840e12', 'id': 'A45', 'pr': 33}, 'ha-lider-voltage-control': {'sha': '81ac8734ca55c5aaea29cd513b8da7e15ac8d3b9', 'id': 'A46', 'pr': 45}}

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
        assert artifact['ui_version'] == 'v1.0.6'
        assert all(b['expected'] == 'v1.0.6' for b in artifact['bindings'] if b['role'] in ('ui_version', 'cache_key'))
