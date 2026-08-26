from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/orion-21-state-as-computation/check_p11_adverse_integration_v2.py"


def _module():
    spec = importlib.util.spec_from_file_location("p11_adverse_integration_v2", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p11_adverse_result_is_integrated_and_bound():
    report = _module().audit()
    assert report["status"] == "PASS", report["errors"]


def test_p11_integration_only_narrows_authority():
    report = _module().audit()
    assert report["scientific_authority_delta"] == "BOUNDARY_NARROWING_ONLY"
    assert report["external_validation"] == "CANNOT_CHECK"


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda d: d.update(schema="mutant"), "wrong V2 schema"),
        (lambda d: d.update(active_terminal="mutant"), "active terminal"),
        (lambda d: d.update(active_claim_leaf={}), "active claim leaf"),
        (lambda d: d.update(historical_boundary_leaf={}), "historical boundary leaf"),
        (lambda d: d.update(promotion_allowed=False), "promotion flag"),
        (
            lambda d: [
                d["evidence_bindings"].pop(key)
                for key in tuple(d["evidence_bindings"])
                if key.startswith("query_family_")
            ],
            "query-family binding key/path/hash set",
        ),
        (
            lambda d: d["adverse_query_family_leaf"].update(retuned=True),
            "negative retune boundary",
        ),
    ],
)
def test_authority_semantic_mutations_fail_closed(tmp_path, mutation, expected_error):
    module = _module()
    authority = json.loads(module.AUTHORITY.read_text(encoding="utf-8"))
    mutation(authority)
    mutant = tmp_path / "mutant.json"
    mutant.write_text(json.dumps(authority), encoding="utf-8")
    report = module.audit(mutant, check_package=False)
    assert report["status"] == "FAIL"
    assert any(expected_error in error for error in report["errors"])
