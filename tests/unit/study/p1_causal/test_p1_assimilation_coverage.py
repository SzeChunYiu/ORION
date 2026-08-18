from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKER = ROOT / "research" / "revival" / "p1" / "check_p1_assimilation_coverage.py"
COVERAGE = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ASSIMILATION_COVERAGE_V1.json"
LEDGER = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ASSIMILATION_LEDGER_V1.json"

_spec = importlib.util.spec_from_file_location("p1_assimilation_coverage", CHECKER)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def _coverage() -> dict:
    return json.loads(COVERAGE.read_text())


def _ledger() -> dict:
    return json.loads(LEDGER.read_text())


def test_committed_coverage_binds_all_36_matrix_rows() -> None:
    coverage = _coverage()
    assert len(coverage["rows"]) == 36
    assert checker.validate_coverage(coverage, _ledger()) == ()


def test_disposition_drift_is_rejected() -> None:
    coverage = _coverage()
    coverage["rows"][0]["disposition"] = "DEFER"
    errors = checker.validate_coverage(coverage, _ledger())
    assert any("row[1]:disposition" in item for item in errors)
    assert any("coverage_disposition_counts" in item for item in errors)


def test_arxiv_source_substitution_is_rejected() -> None:
    coverage = _coverage()
    coverage["rows"][0]["source"] = "unrelated source"
    errors = checker.validate_coverage(coverage, _ledger())
    assert "row[1]:missing_arxiv:2607.21461" in errors


def test_unknown_atomic_receipt_is_rejected() -> None:
    coverage = _coverage()
    coverage["rows"][8]["receipt_id"] = "P1-NOT-A-RECEIPT"
    errors = checker.validate_coverage(coverage, _ledger())
    assert "row[9]:unknown_receipt:P1-NOT-A-RECEIPT" in errors


def test_round_b_requirement_cannot_be_dropped() -> None:
    coverage = copy.deepcopy(_coverage())
    coverage["round_state"] = "ROUND_A_COMPLETE"
    errors = checker.validate_coverage(coverage, _ledger())
    assert "round_b_requirement_missing" in errors
