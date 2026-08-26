from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER = (
    ROOT
    / "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/"
    "check_commutation_contract_binding_v1.py"
)


def _checker():
    spec = importlib.util.spec_from_file_location("p6_commutation_contract_binding", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_commutation_contract_is_bound_across_canonical_artifacts():
    report = _checker().audit(ROOT)
    assert report["status"] == "PASS", report["errors"]
    assert report["contract_id"] == "P6.COMMUTE.RW_NONINTERFERENCE.V1"


def test_commutation_contract_keeps_its_scope_boundary():
    boundary = _checker().audit(ROOT)["authority_boundary"]
    assert "not necessity for every specific mechanic pair" in boundary
    assert "kernel verification" in boundary
    assert "independent formal review" in boundary
    assert "deployed-system validation" in boundary
