"""Comprehensive tests for all ORION Paper 3 metrics.

Tests cover each metric function defined in src/orion/study/metrics.py:
false_merge_rate, false_contradiction_rate, missed_contradiction_rate,
false_split_rate, valid_integration_rate,
false_integration_rate_with_valid_integration_guard,
mapping_precision_recall_f1, measurement_equivalence_accuracy,
obstruction_precision_recall, source_recoverability_rate,
preservation_condition_accuracy, literature_bridge_validity_precision_recall,
downstream_answer_accuracy, unresolved_abstention_calibration,
annotation_agreement_by_coordinate, cost_metrics, compute_all_metrics.
"""
from __future__ import annotations

import math

import pytest
from orion.study.metrics import (
    ALL_METRIC_FUNCTIONS,
    annotation_agreement_by_coordinate,
    compute_all_metrics,
    cost_metrics,
    downstream_answer_accuracy,
    false_contradiction_rate,
    false_integration_rate_with_valid_integration_guard,
    false_merge_rate,
    false_split_rate,
    literature_bridge_validity_precision_recall,
    mapping_precision_recall_f1,
    measurement_equivalence_accuracy,
    missed_contradiction_rate,
    obstruction_precision_recall,
    preservation_condition_accuracy,
    source_recoverability_rate,
    unresolved_abstention_calibration,
    valid_integration_rate,
)


def _g(verdict: str, **kw) -> dict:
    base = {"integration_verdict": verdict,
            "mapping_relation": "UNRESOLVED",
            "contradiction_verdict": "UNRESOLVED",
            "measurement_relation": "UNRESOLVED",
            "case_family": "same_name_different_referent"}
    base.update(kw)
    return base


def _p(verdict: str, **kw) -> dict:
    return _g(verdict, **kw)


# ── false_merge_rate ──────────────────────────────────────────────────────────

def test_false_merge_rate_basic():
    gold = [_g("OBSTRUCTION"), _g("GLUE_ALLOWED")]
    pred = [_p("GLUE_ALLOWED"), _p("GLUE_ALLOWED")]
    out = false_merge_rate(gold, pred)
    assert out["false_merge_rate"] == 0.5
    assert out["false_merge_n"] == 2


def test_false_merge_rate_abstention_excluded():
    gold = [_g("OBSTRUCTION"), _g("OBSTRUCTION")]
    pred = [_p("UNRESOLVED"), _p("GLUE_ALLOWED")]
    out = false_merge_rate(gold, pred)
    assert out["false_merge_rate"] == 1.0
    assert out["false_merge_n"] == 1


def test_false_merge_rate_plural_view_counts_as_gold_obstruction():
    gold = [_g("PLURAL_VIEW")]
    pred = [_p("GLUE_ALLOWED")]
    assert false_merge_rate(gold, pred)["false_merge_rate"] == 1.0


def test_false_merge_rate_empty_denominator():
    """No measurable case must not report the best attainable harm rate.

    This test previously asserted 0.0, which for a harm rate is a perfect score:
    a metric that measured nothing reported that nothing went wrong, and any
    threshold check on it passed. The rate is now nan, so every comparison
    against it is False and the metric fails closed; the denominator stays
    beside it for a caller that wants to tell the two apart.
    """

    gold = [_g("OBSTRUCTION")]
    pred = [_p("UNRESOLVED")]
    out = false_merge_rate(gold, pred)
    assert math.isnan(out["false_merge_rate"])
    assert out["false_merge_n"] == 0
    # Fails closed: a superiority check on an unmeasured rate does not pass.
    assert not (out["false_merge_rate"] <= 0.05)


# ── false_split_rate ──────────────────────────────────────────────────────────

def test_false_split_rate():
    gold = [_g("GLUE_ALLOWED"), _g("GLUE_ALLOWED")]
    pred = [_p("OBSTRUCTION"), _p("GLUE_ALLOWED")]
    out = false_split_rate(gold, pred)
    assert out["false_split_rate"] == 0.5
    assert out["false_split_n"] == 2


def test_false_split_rate_plural_prediction_is_split():
    gold = [_g("GLUE_ALLOWED")]
    pred = [_p("PLURAL_VIEW")]
    assert false_split_rate(gold, pred)["false_split_rate"] == 1.0


def test_false_split_rate_no_split_when_abstain():
    gold = [_g("GLUE_ALLOWED")]
    pred = [_p("UNRESOLVED")]
    assert false_split_rate(gold, pred)["false_split_n"] == 0


# ── contradiction metrics ─────────────────────────────────────────────────────

def test_false_contradiction_rate():
    gold = [_g("GLUE_ALLOWED", contradiction_verdict="NO_CONTRADICTION")]
    pred = [_p("GLUE_ALLOWED", contradiction_verdict="CONTRADICTION")]
    out = false_contradiction_rate(gold, pred)
    assert out["false_contradiction_rate"] == 1.0
    assert out["false_contradiction_n"] == 1


def test_false_contradiction_ignores_unresolved():
    gold = [_g("GLUE_ALLOWED", contradiction_verdict="NO_CONTRADICTION")]
    pred = [_p("GLUE_ALLOWED", contradiction_verdict="UNRESOLVED")]
    assert false_contradiction_rate(gold, pred)["false_contradiction_n"] == 0


def test_missed_contradiction_rate():
    gold = [_g("OBSTRUCTION", contradiction_verdict="CONTRADICTION")]
    pred = [_p("OBSTRUCTION", contradiction_verdict="NO_CONTRADICTION")]
    out = missed_contradiction_rate(gold, pred)
    assert out["missed_contradiction_rate"] == 1.0
    assert out["missed_contradiction_n"] == 1


def test_missed_contradiction_context_dependent_not_counted():
    # CONTEXT_DEPENDENT is not CONTRADICTION — the helper only flags
    # gold=CONTRADICTION vs pred!=CONTRADICTION as a miss. CONTEXT_DEPENDENT
    # is handled separately by the annotator; it's not a missed contradiction.
    gold = [_g("OBSTRUCTION", contradiction_verdict="CONTEXT_DEPENDENT")]
    pred = [_p("OBSTRUCTION", contradiction_verdict="NO_CONTRADICTION")]
    assert missed_contradiction_rate(gold, pred)["missed_contradiction_rate"] == 0.0


# ── valid_integration_rate ────────────────────────────────────────────────────

def test_valid_integration_rate():
    gold = [_g("GLUE_ALLOWED"), _g("OBSTRUCTION"), _g("GLUE_ALLOWED")]
    pred = [_p("GLUE_ALLOWED"), _p("OBSTRUCTION"), _p("OBSTRUCTION")]
    out = valid_integration_rate(gold, pred)
    assert out["valid_integration_rate"] == 2 / 3


def test_valid_integration_abstention_excluded():
    gold = [_g("GLUE_ALLOWED")]
    pred = [_p("UNRESOLVED")]
    assert valid_integration_rate(gold, pred)["valid_integration_n"] == 0


def test_valid_integration_plural_matches_plural():
    gold = [_g("PLURAL_VIEW")]
    pred = [_p("PLURAL_VIEW")]
    assert valid_integration_rate(gold, pred)["valid_integration_rate"] == 1.0


# ── guard composite ───────────────────────────────────────────────────────────

def test_guard_composite_includes_both_headline_metrics():
    gold = [_g("OBSTRUCTION"), _g("GLUE_ALLOWED")]
    pred = [_p("GLUE_ALLOWED"), _p("GLUE_ALLOWED")]
    out = false_integration_rate_with_valid_integration_guard(gold, pred)
    assert out["false_merge_rate"] == 0.5
    assert out["valid_integration_rate"] == 0.5


# ── mapping_precision_recall_f1 ───────────────────────────────────────────────

def test_mapping_f1_perfect():
    gold = [_g("GLUE_ALLOWED", mapping_relation="IDENTITY"),
            _g("GLUE_ALLOWED", mapping_relation="EQUIVALENCE")]
    pred = [_p("GLUE_ALLOWED", mapping_relation="IDENTITY"),
            _p("GLUE_ALLOWED", mapping_relation="EQUIVALENCE")]
    out = mapping_precision_recall_f1(gold, pred)
    assert out["mapping_f1_macro"] == 1.0
    assert out["mapping_precision_macro"] == 1.0
    assert out["mapping_recall_macro"] == 1.0


def test_mapping_f1_unresolved_skipped():
    gold = [_g("GLUE_ALLOWED", mapping_relation="IDENTITY"),
            _g("GLUE_ALLOWED", mapping_relation="EQUIVALENCE")]
    pred = [_p("GLUE_ALLOWED", mapping_relation="IDENTITY"),
            _p("GLUE_ALLOWED", mapping_relation="UNRESOLVED")]
    out = mapping_precision_recall_f1(gold, pred)
    assert out["mapping_f1_macro"] == 1.0


def test_mapping_f1_zero_when_empty():
    out = mapping_precision_recall_f1([], [])
    assert out.get("mapping_f1_macro", 0.0) == 0.0


def test_mapping_f1_type_specific_keys():
    gold = [_g("GLUE_ALLOWED", mapping_relation="SUBSUMPTION")]
    pred = [_p("GLUE_ALLOWED", mapping_relation="SUBSUMPTION")]
    out = mapping_precision_recall_f1(gold, pred)
    assert out["mapping_f1_SUBSUMPTION"] == 1.0


# ── measurement_equivalence_accuracy ──────────────────────────────────────────

def test_measurement_equivalence():
    gold = [_g("GLUE_ALLOWED", measurement_relation="SAME")]
    pred = [_p("GLUE_ALLOWED", measurement_relation="SAME")]
    assert measurement_equivalence_accuracy(gold, pred)["measurement_equivalence_accuracy"] == 1.0


def test_measurement_equivalence_wrong_and_abstain():
    gold = [_g("GLUE_ALLOWED", measurement_relation="SAME"),
            _g("GLUE_ALLOWED", measurement_relation="DIFFERENT")]
    pred = [_p("GLUE_ALLOWED", measurement_relation="DIFFERENT"),
            _p("GLUE_ALLOWED", measurement_relation="UNRESOLVED")]
    out = measurement_equivalence_accuracy(gold, pred)
    assert out["measurement_equivalence_accuracy"] == 0.0
    assert out["measurement_equivalence_n"] == 1


# ── obstruction_precision_recall ──────────────────────────────────────────────

def test_obstruction_prf_perfect():
    gold = [_g("OBSTRUCTION"), _g("PLURAL_VIEW"), _g("GLUE_ALLOWED")]
    pred = [_p("OBSTRUCTION"), _p("PLURAL_VIEW"), _p("GLUE_ALLOWED")]
    out = obstruction_precision_recall(gold, pred)
    assert out["obstruction_precision"] == 1.0
    assert out["obstruction_recall"] == 1.0
    assert out["obstruction_f1"] == 1.0


def test_obstruction_prf_false_positive():
    gold = [_g("GLUE_ALLOWED")]
    pred = [_p("OBSTRUCTION")]
    out = obstruction_precision_recall(gold, pred)
    assert out["obstruction_precision"] == 0.0
    assert out["obstruction_false_pos"] == 1


def test_obstruction_prf_missed():
    gold = [_g("OBSTRUCTION")]
    pred = [_p("GLUE_ALLOWED")]
    out = obstruction_precision_recall(gold, pred)
    assert out["obstruction_recall"] == 0.0
    assert out["obstruction_false_neg"] == 1


def test_obstruction_prf_abstention_ignored():
    gold = [_g("OBSTRUCTION")]
    pred = [_p("UNRESOLVED")]
    assert obstruction_precision_recall(gold, pred)["obstruction_false_neg"] == 0


# ── source_recoverability_rate ────────────────────────────────────────────────

def test_source_recoverability_all_targets():
    gold = [_g("GLUE_ALLOWED", recoverability_target=["referent_relation", "construct_relation"])]
    pred = [_p("GLUE_ALLOWED", recoverability_target=["referent_relation", "construct_relation"])]
    out = source_recoverability_rate(gold, pred)
    assert out["source_recoverability_rate"] == 1.0


def test_source_recoverability_missing_target():
    gold = [_g("GLUE_ALLOWED", recoverability_target=["referent_relation", "construct_relation"])]
    pred = [_p("GLUE_ALLOWED", recoverability_target=["referent_relation"])]
    assert source_recoverability_rate(gold, pred)["source_recoverability_rate"] == 0.0


def test_source_recoverability_no_requirement_skipped():
    gold = [_g("GLUE_ALLOWED", recoverability_target=[])]
    pred = [_p("GLUE_ALLOWED", recoverability_target=[])]
    out = source_recoverability_rate(gold, pred)
    assert out["source_recoverability_n"] == 0


# ── preservation_condition_accuracy ───────────────────────────────────────────

def test_preservation_conditions_match():
    gold = [_g("GLUE_ALLOWED", preservation_conditions=["unit_consistency"])]
    pred = [_p("GLUE_ALLOWED", preservation_conditions=["unit_consistency"])]
    assert preservation_condition_accuracy(gold, pred)["preservation_condition_accuracy"] == 1.0


def test_preservation_conditions_mismatch():
    gold = [_g("GLUE_ALLOWED", preservation_conditions=["unit_consistency"])]
    pred = [_p("GLUE_ALLOWED", preservation_conditions=["temperature_normalized"])]
    assert preservation_condition_accuracy(gold, pred)["preservation_condition_accuracy"] == 0.0


def test_preservation_conditions_both_empty_ok():
    gold = [_g("GLUE_ALLOWED", preservation_conditions=[])]
    pred = [_p("GLUE_ALLOWED", preservation_conditions=[])]
    assert preservation_condition_accuracy(gold, pred)["preservation_condition_accuracy"] == 1.0


# ── literature_bridge_validity_precision_recall ───────────────────────────────

def test_bridge_validity_skip_non_bridge_cases():
    gold = [_g("GLUE_ALLOWED", mapping_relation="IDENTITY")]  # non-bridge case_family
    pred = [_p("GLUE_ALLOWED", mapping_relation="IDENTITY")]
    out = literature_bridge_validity_precision_recall(gold, pred)
    assert out["literature_bridge_f1"] == 0.0


def test_bridge_validity_tp_fp():
    gold = [_g("GLUE_ALLOWED", case_family="valid_invalid_literature_bridge",
               mapping_relation="IDENTITY"),
            _g("GLUE_ALLOWED", case_family="valid_invalid_literature_bridge",
               mapping_relation="NO_LICENSED_MAPPING")]
    pred = [_p("GLUE_ALLOWED", case_family="valid_invalid_literature_bridge",
               mapping_relation="IDENTITY"),
            _p("GLUE_ALLOWED", case_family="valid_invalid_literature_bridge",
               mapping_relation="IDENTITY")]
    out = literature_bridge_validity_precision_recall(gold, pred)
    assert out["literature_bridge_precision"] == 0.5
    assert out["literature_bridge_recall"] == 1.0


# ── downstream_answer_accuracy ────────────────────────────────────────────────

def test_downstream_accuracy():
    gold = [_g("GLUE_ALLOWED", downstream_correct=True),
            _g("GLUE_ALLOWED", downstream_correct=False)]
    pred = [_p("GLUE_ALLOWED", downstream_correct=True),
            _p("GLUE_ALLOWED", downstream_correct=True)]
    assert downstream_answer_accuracy(gold, pred)["downstream_answer_accuracy"] == 0.5


def test_downstream_skips_missing():
    gold = [_g("GLUE_ALLOWED")]
    pred = [_p("GLUE_ALLOWED")]
    assert downstream_answer_accuracy(gold, pred)["downstream_answer_n"] == 0


# ── unresolved_abstention_calibration ─────────────────────────────────────────

def test_calibration_perfect():
    gold = [_g("UNRESOLVED"), _g("GLUE_ALLOWED")]
    pred = [_p("UNRESOLVED"), _p("GLUE_ALLOWED")]
    out = unresolved_abstention_calibration(gold, pred)
    assert out["unresolved_rate"] == 0.5
    assert out["unresolved_calibration"] == 1.0


def test_calibration_zero_when_no_abstention():
    gold = [_g("GLUE_ALLOWED")]
    pred = [_p("GLUE_ALLOWED")]
    out = unresolved_abstention_calibration(gold, pred)
    assert out["unresolved_rate"] == 0.0
    assert out["unresolved_calibration"] == 0.0


def test_calibration_partial():
    gold = [_g("UNRESOLVED"), _g("GLUE_ALLOWED"), _g("GLUE_ALLOWED")]
    pred = [_p("UNRESOLVED"), _p("UNRESOLVED"), _p("GLUE_ALLOWED")]
    out = unresolved_abstention_calibration(gold, pred)
    assert out["unresolved_rate"] == 2 / 3
    assert out["unresolved_calibration"] == 0.5


# ── annotation_agreement_by_coordinate ────────────────────────────────────────

def test_agreement_all_coords_present():
    a = [_g("GLUE_ALLOWED", referent_relation="SAME", construct_relation="SAME")]
    b = [_g("GLUE_ALLOWED", referent_relation="SAME", construct_relation="SAME")]
    out = annotation_agreement_by_coordinate(a, b)
    assert out["agreement_referent_relation"] == 1.0
    assert out["agreement_construct_relation"] == 1.0
    assert out["agreement_integration_verdict"] == 1.0
    assert len(out) == 11


def test_agreement_skips_unresolved():
    """"Nothing was comparable" must not equal "they disagreed on everything".

    Together with `test_agreement_zero_when_disagree` below, this pair used to
    assert 0.0 for both --- so the suite pinned the two states as
    indistinguishable, which is the whole defect written down as intended
    behaviour. Total disagreement is still 0.0; nothing comparable is now nan.
    """

    a = [_g("GLUE_ALLOWED", referent_relation="SAME")]
    b = [_g("GLUE_ALLOWED", referent_relation="UNRESOLVED")]
    out = annotation_agreement_by_coordinate(a, b)
    assert math.isnan(out["agreement_referent_relation"])

    disagreeing_a = [_g("GLUE_ALLOWED", referent_relation="SAME")]
    disagreeing_b = [_g("GLUE_ALLOWED", referent_relation="DIFFERENT")]
    disagreed = annotation_agreement_by_coordinate(disagreeing_a, disagreeing_b)
    assert disagreed["agreement_referent_relation"] == 0.0
    assert not math.isnan(disagreed["agreement_referent_relation"])


def test_agreement_zero_when_disagree():
    a = [_g("GLUE_ALLOWED", referent_relation="SAME")]
    b = [_g("GLUE_ALLOWED", referent_relation="DIFFERENT")]
    assert annotation_agreement_by_coordinate(a, b)["agreement_referent_relation"] == 0.0


# ── cost_metrics ──────────────────────────────────────────────────────────────

def test_cost_metrics_empty():
    out = cost_metrics([])
    assert out["wallclock_seconds_total"] == 0.0
    assert out["model_tokens_mean"] == 0.0


def test_cost_metrics_aggregates():
    recs = [
        {"cost": {"wallclock_seconds": 10, "model_tokens": 100, "storage_overhead": 5}},
        {"cost": {"wallclock_seconds": 20, "model_tokens": 300, "storage_overhead": 15}},
    ]
    out = cost_metrics(recs)
    assert out["wallclock_seconds_total"] == 30.0
    assert out["wallclock_seconds_mean"] == 15.0
    assert out["model_tokens_total"] == 400.0
    assert out["model_tokens_mean"] == 200.0
    assert out["storage_overhead_total"] == 20.0


# ── compute_all_metrics ───────────────────────────────────────────────────────

def test_compute_all_metrics_flat_dict():
    gold = [_g("OBSTRUCTION"), _g("GLUE_ALLOWED")]
    pred = [_p("GLUE_ALLOWED"), _p("GLUE_ALLOWED")]
    out = compute_all_metrics(gold, pred)
    assert isinstance(out, dict)
    assert out["false_merge_rate"] == 0.5
    assert out["valid_integration_rate"] == 0.5


def test_all_metric_functions_registered():
    expected = {
        "false_integration_rate_with_valid_integration_guard",
        "false_merge_rate", "false_split_rate", "false_contradiction_rate",
        "missed_contradiction_rate", "valid_integration_rate",
        "mapping_precision_recall_f1", "measurement_equivalence_accuracy",
        "obstruction_precision_recall", "source_recoverability_rate",
        "preservation_condition_accuracy",
        "literature_bridge_validity_precision_recall",
        "downstream_answer_accuracy", "unresolved_abstention_calibration",
        "annotation_agreement_by_coordinate", "cost_metrics",
    }
    assert expected == set(ALL_METRIC_FUNCTIONS)


def test_compute_all_metrics_does_not_crash_on_mismatched_lengths():
    # zip(strict=True) would raise; compute_all_metrics must not propagate.
    gold = [_g("GLUE_ALLOWED")]
    pred = []
    out = compute_all_metrics(gold, pred)
    assert isinstance(out, dict)
