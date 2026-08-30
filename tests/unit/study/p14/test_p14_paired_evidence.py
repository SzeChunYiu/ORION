"""Regression tests for ORION-24 paired-evidence interpretation."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "papers/orion-24-orion-rse/analyze_p14_paired_evidence_v1.py"
RECEIPT = ROOT / "papers/orion-24-orion-rse/P14_PAIRED_EVIDENCE_INTERPRETATION_V1.json"


def _load():
    spec = importlib.util.spec_from_file_location("p14_paired_evidence", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = _load()


def test_committed_receipt_is_exactly_derived() -> None:
    committed = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert committed == audit.derive()
    assert audit.render() == RECEIPT.read_text(encoding="utf-8")


def test_p14c_exposes_the_four_to_zero_discordance_without_overclaiming() -> None:
    p14c = audit.derive()["p14c"]
    assert p14c["paired_correctness_table"] == {
        "both_correct": 24,
        "subject_only_correct": 4,
        "comparator_only_correct": 0,
        "both_wrong": 0,
    }
    assert p14c["case_level_exact_mcnemar_two_sided_p"] == 0.125
    assert p14c["stratum_outcome_counts"] == {
        "subject_wins": 1,
        "comparator_wins": 0,
        "ties": 6,
    }
    assert p14c["stratum_level_exact_sign_two_sided_p"] == 1.0
    assert p14c["discordant_strata"] == ["RETAIN_NEGATIVE"]


def test_p14c_advantage_disappears_when_the_only_discriminating_stratum_is_removed() -> None:
    leave_one_out = audit.derive()["p14c"]["leave_one_stratum_out"]
    assert leave_one_out["RETAIN_NEGATIVE"]["accuracy_difference"] == 0.0
    assert all(
        row["accuracy_difference"] == 1 / 6
        for stratum, row in leave_one_out.items()
        if stratum != "RETAIN_NEGATIVE"
    )


def test_p14e_family_replication_is_design_fixed_not_population_inference() -> None:
    p14e = audit.derive()["p14e"]
    assert p14e["subject_only_correct_cases"] == 960
    assert p14e["comparator_only_correct_cases"] == 0
    assert p14e["subject_only_correct_cases_per_family"] == 80
    assert len(set(p14e["family_accuracy_differences"])) == 1
    assert p14e["between_family_standard_deviation"] == 0.0
    assert p14e["differing_strata"] == ["RETAIN_NEGATIVE"]
    assert p14e["case_level_exact_test"] == "NOT_APPLICABLE_AS_POPULATION_INFERENCE"


def test_exact_binomial_helper_is_fail_closed_on_invalid_counts() -> None:
    assert audit.exact_two_sided_binomial_p(4, 0) == 0.125
    assert audit.exact_two_sided_binomial_p(1, 0) == 1.0
    assert audit.exact_two_sided_binomial_p(0, 0) == 1.0
    try:
        audit.exact_two_sided_binomial_p(-1, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("negative counts must fail")
