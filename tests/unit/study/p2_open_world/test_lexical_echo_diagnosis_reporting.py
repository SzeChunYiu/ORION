from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "papers/paper-02-open-world-scientific-discovery/diagnose_lexical_echo_reproduction.py"


def _module():
    spec = importlib.util.spec_from_file_location("diagnose_lexical_echo_reproduction", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_finding_is_derived_from_measured_count_fields_and_ulps() -> None:
    module = _module()
    checks = {
        "two_fresh_runs_are_bit_identical": True,
        "frozen_parameter_digest_still_matches": True,
        "verdict_unchanged": True,
        "world_content_hash_unchanged": True,
        "gate_results_unchanged": True,
        "no_non_float_difference": True,
        "no_gate_read_field_differs": True,
        "every_float_difference_is_within_four_ulps": True,
    }
    finding = module.build_finding(
        float_diffs=[{"field": "mrr_at_50"}, {"field": "ndcg_at_10"}],
        max_ulps=4,
        deterministic=True,
        checks=checks,
    )
    assert "2 reported float values differ" in finding
    assert "mrr_at_50" in finding
    assert "ndcg_at_10" in finding
    assert "maximum distance is 4 ulps" in finding
    assert "bit-identical" in finding


def test_finding_does_not_claim_diagnosis_when_a_check_fails() -> None:
    module = _module()
    checks = {"no_gate_read_field_differs": False, "no_non_float_difference": True}
    finding = module.build_finding(
        float_diffs=[{"field": "hit_at_10"}],
        max_ulps=1,
        deterministic=True,
        checks=checks,
    )
    assert finding.startswith("Diagnosis not established:")
    assert "no_gate_read_field_differs" in finding
    assert "hit_at_10" in finding
