from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/paper-12-adaptive-state-reasoning/check_p12_lifecycle_integration_v4.py"


def _module():
    spec = importlib.util.spec_from_file_location("p12_v4_check", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p12_lifecycle_is_bound_and_external_gate_stays_closed():
    report = _module().audit()
    assert report["status"] == "PASS", report["errors"]
    assert report["external_validation"] == "CANNOT_CHECK"
    assert report["top_tier_submission_allowed"] is False


@pytest.mark.parametrize(
    ("mutation", "needle"),
    [
        (lambda d: d.update(schema="mutant"), "wrong schema"),
        (lambda d: d.update(active_claim_leaf={}), "active_claim_leaf"),
        (lambda d: d.update(top_tier_submission_allowed=True), "submission gate"),
        (lambda d: d["robustness_boundary_leaf"].update(price_axis="ROBUST"), "robustness negative"),
        (lambda d: d["price_aware_successor_leaf"].update(forward_time_deployability="SUPPORTED"), "forward-time"),
        (lambda d: d["evidence_bindings"].pop("robustness_result_receipt"), "robustness_result_receipt"),
    ],
)
def test_v4_mutations_fail_closed(tmp_path, mutation, needle):
    module = _module()
    value = json.loads(module.AUTHORITY.read_text(encoding="utf-8"))
    mutation(value)
    mutant = tmp_path / "mutant.json"
    mutant.write_text(json.dumps(value), encoding="utf-8")
    report = module.audit(mutant, check_package=False)
    assert report["status"] == "FAIL"
    assert any(needle in error for error in report["errors"])
