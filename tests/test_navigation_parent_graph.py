import copy
import importlib.util
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def test_registered_parents_are_known_and_acyclic():
    spec = importlib.util.spec_from_file_location('parent_graph', ROOT / 'scripts/check_navigation_parents.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    registry = yaml.safe_load((ROOT / 'navigation/main.yaml').read_text())
    assert module.validate(registry) == []
    for change in ('cycle', 'unknown', 'wrong_main_parent'):
        broken = copy.deepcopy(registry)
        if change == 'cycle':
            broken['spec']['routes']['overview']['parent'] = 'home'
        elif change == 'unknown':
            broken['spec']['specialized_routes']['s8_omni']['parent_route'] = '/missing'
        else:
            broken['spec']['specialized_routes']['s8_omni']['parent_route'] = '/dashboard-actions/home'
        assert module.validate(broken), change
