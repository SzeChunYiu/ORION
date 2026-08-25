"""Non-authorizing mechanical checks for DES-HISTORICAL-01."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("des_historical", HERE / "run_des_historical.py")
assert SPEC and SPEC.loader
des_historical = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(des_historical)


def test_post_cutoff_and_unknown_date_are_not_admissible() -> None:
    assert des_historical.chronology_verdict("1855-01-01", "1854-09-07") == (
        "POST_CUTOFF_EVALUATOR_ONLY"
    )
    assert des_historical.chronology_verdict(None, "1854-09-07") == (
        "CANNOT_CHECK_UNKNOWN_DATE"
    )


def test_schedule_is_denominator_complete_even_without_external_custody() -> None:
    freeze = des_historical.load_freeze()
    rows = des_historical.build_schedule(freeze)
    assert len(rows) == 144
    external = [row for row in rows if row["scorer_id"] == "external_model"]
    assert len(external) == 24
    assert all(row["status"] == "NOT_RUN_CANNOT_CHECK" for row in external)


def test_no_admissible_evidence_makes_twins_cannot_check_not_negative() -> None:
    cases = des_historical.construct_cases(
        episode={"episode_id": "e", "registered_actions": ["a", "cannot_check"]},
        admissible_evidence=[],
        seed=20260825,
    )
    assert len(cases) == 6
    assert all(case["construction_status"] == "CANNOT_CHECK_NO_ADMISSIBLE_EVIDENCE" for case in cases)


def test_reconciliation_rejects_a_dropped_cell() -> None:
    with pytest.raises(ValueError, match="scheduled cell denominator"):
        des_historical.require_schedule_denominator([], expected=144)
