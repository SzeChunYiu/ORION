from __future__ import annotations

from pathlib import Path

import pytest

from orion.study.p3_confirmatory_receipt import GoldUnavailableError
from orion.study.p3_phase_a_verification import (
    construction_report,
    exact_conservative_control,
    executable_schema_contract_baseline,
    fail_closed_load_confirmatory,
    flat_canonicalization_baseline,
    scion_like_baseline,
    score_secondary_baselines,
    scorer_agreement,
    source_registry_terminal_leakage,
)


def test_independent_evaluator_agrees_with_incumbent_on_frozen_cases() -> None:
    report = scorer_agreement()
    assert report["n"] == 32
    assert report["unanimous"] is True
    assert report["disagreements"] == []


def test_secondary_baselines_on_frozen_cases_keep_unimplemented_cannot_check() -> None:
    cases = fail_closed_load_confirmatory()
    scored = score_secondary_baselines(cases)
    exact = scored["systems"]["exact_coordinate_conservative"]
    flat = scored["systems"]["flat_predicate_canonicalization"]
    assert exact["n_scored"] == 32
    assert flat["n_scored"] == 32
    assert scored["systems"]["scion_like_conservative_schema_fusion"]["n_cannot_check"] == 32
    assert scored["systems"]["executable_schema_contracts_like"]["n_cannot_check"] == 32
    assert "cannot rewrite the frozen confirmatory claim" in scored["note"]
    assert scion_like_baseline(cases[0]).status == "CANNOT_CHECK"
    assert executable_schema_contract_baseline(cases[0]).status == "CANNOT_CHECK"
    assert exact_conservative_control(cases[0]).status == "SCORED"
    assert flat_canonicalization_baseline(cases[0]).status == "SCORED"


def test_construction_tests_on_frozen_gold() -> None:
    report = construction_report()
    assert report["source_registry"]["clean"] is True
    assert report["overlap_with_primary"]["case_id_overlap_count"] == 0
    assert report["source_hash_and_locator_complete"] is True
    assert report["permutation"]["case_order_invariant_rates"] is True
    assert report["permutation"]["label_permutation_changes_orion_rates"] is True
    predictor = report["metadata_predictor"]
    assert predictor["n"] == 32
    assert 0.0 <= float(predictor["leave_one_out_accuracy"]) <= 1.0


def test_source_registry_rejects_terminal_field(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text('{"sources": [{"id": "X", "expected_terminal": "GLUE"}]}', encoding="utf-8")
    leaked = source_registry_terminal_leakage(path)
    assert leaked["clean"] is False
    assert leaked["leaked_fields"]


def test_fail_closed_without_gold(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import orion.study.p3_confirmatory_receipt as receipt

    monkeypatch.setattr(receipt, "CONFIRMATORY_GOLD", tmp_path / "missing.jsonl")
    with pytest.raises(GoldUnavailableError, match="CANNOT_CHECK"):
        fail_closed_load_confirmatory()
