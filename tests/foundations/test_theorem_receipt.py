import json

from orion.foundations.cli import (
    build_assumption_ledger,
    build_countermodel_atlas,
    build_receipt,
    canonical_json,
)
from orion.foundations.ledger import build_theorem_ledger
from orion.foundations.theorems import run_local_theorems


def test_all_local_theorems_discharge() -> None:
    results = run_local_theorems()
    assert len(results) >= 20
    assert all(result.passed for result in results), [
        result for result in results if not result.passed
    ]
    assert len({result.theorem_id for result in results}) == len(results)


def test_receipt_is_deterministic_and_has_no_authority_delta() -> None:
    first = build_receipt()
    second = build_receipt()
    assert first == second
    assert first["authority_delta"] == "NONE"
    assert first["p1_rr1_coordination"] == "UNTOUCHED"
    assert json.loads(canonical_json(first)) == first


def test_assumption_and_countermodel_outputs_are_bound() -> None:
    assumptions = build_assumption_ledger()
    countermodels = build_countermodel_atlas()
    assert len(assumptions["entries"]) == 25
    assert countermodels["named_minimal_families"]
    assert any(
        item["target"] == "OSTC-T20"
        for item in countermodels["named_minimal_families"]
    )


def test_theorem_ledger_binds_receipt_and_ownership() -> None:
    results = run_local_theorems()
    receipt = build_receipt(results)
    ledger = build_theorem_ledger(results, receipt["canonical_core_sha256"])
    assert ledger["receipt_core_sha256"] == receipt["canonical_core_sha256"]
    assert len(ledger["entries"]) == len(results)
    assert all(entry["paper_authority_delta"] == "NONE" for entry in ledger["entries"])
