import importlib.util
import json
from pathlib import Path


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);assert spec.loader is not None;spec.loader.exec_module(mod);return mod


def test_method_space_eval_v2_replays_and_stays_bounded():
    root=Path('research/extensions/p7-method-space')
    checker=load(root/'check_method_space_eval_v2.py','p7check')
    expected=json.loads((root/'METHOD_SPACE_EVAL_V2_SUMMARY.json').read_text())
    actual=checker.derive()
    assert actual == expected
    assert actual['n_worlds'] == 15
    assert actual['target_discovery_rate'] == 1.0
    assert actual['false_analogy_control'] == 1.0
    assert actual['premature_stop_rate'] == 0.0
    assert actual['mutation_detection_rate'] == 1.0
    assert actual['policy_accuracy']['p7_method_chart'] == 1.0
    assert actual['policy_accuracy']['p7_v2_local_navigation'] < 1.0
    assert actual['terminal'] == 'P7_METHOD_SPACE_NAVIGATION_NARROWED'
    assert 'does not establish real-world' in actual['claim_ceiling']
