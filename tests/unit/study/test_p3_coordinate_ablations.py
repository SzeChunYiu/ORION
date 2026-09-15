"""Hostile tests for P3 coordinate ablations on frozen confirmatory gold.

These tests bind #100 Step 5 / #280 V2 ablations to the public-reference
comparator (`evaluate_case` / `compare_meaning`). They must not treat the
SCOPE/SCION placeholder in `orion.study.ablations` as a study result.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.knowledge.semantics import MeaningRelation
from orion.study.p3_confirmatory_receipt import CONFIRMATORY_GOLD_SHA256, load_confirmatory_gold
from orion.study.p3_coordinate_ablations import (
    CANNOT_CHECK_ABLATIONS,
    CHECKABLE_ABLATIONS,
    RESULTS_PATH,
    ZERO_EFFECT_ABLATIONS,
    apply_ablation,
    archive_results,
    coordinate_coverage,
    evaluate_ablated_case,
    obstruction_false_merge_delta,
    run_coordinate_ablations,
)
from orion.study.p3_public_reference import NONMERGE_RELATIONS, evaluate_case


def test_module_does_not_use_placeholder_full_pipeline() -> None:
    source = Path("src/orion/study/p3_coordinate_ablations.py").read_text(encoding="utf-8")
    assert "SCOPE_SCION_Like" not in source
    assert "orion.study.ablations" not in source


def test_forcing_merge_on_obstruction_cases_increases_false_merges() -> None:
    cases = load_confirmatory_gold()
    delta = obstruction_false_merge_delta(cases)
    assert delta["obstruction_case_count"] > 0
    assert delta["full_orion_false_merges"] == 0
    assert delta["forced_false_merges"] > delta["full_orion_false_merges"]
    assert delta["false_merge_increase"] > 0


def test_confirmatory_ablations_reproduce_known_facts() -> None:
    report = run_coordinate_ablations()
    assert report["case_count"] == 32
    assert report["gold_sha256"] == CONFIRMATORY_GOLD_SHA256
    assert report["resource_match"]["deterministic_cpu"] is True
    assert report["resource_match"]["same_cases"] is True
    assert report["resource_match"]["extra_retrieval"] is False
    assert report["resource_match"]["gpu"] is False
    assert report["resource_match"]["provider_credentials"] is False

    modality = report["ablations"]["remove_modality_polarity_attribution_discourse"]
    assert modality["status"] == "SCORED"
    fm = modality["false_merge_ablation_minus_full"]
    assert fm["candidate_minus_baseline"] == 0.1875
    assert fm["ci95_low"] > 0.0
    assert fm["ci95_high"] > fm["ci95_low"]

    forced = report["ablations"]["force_compatibility_without_obstruction"]
    assert forced["status"] == "SCORED"
    forced_fm = forced["false_merge_ablation_minus_full"]
    assert forced_fm["candidate_minus_baseline"] == 0.1875
    assert forced_fm["ci95_low"] > 0.0

    for name in ZERO_EFFECT_ABLATIONS:
        block = report["ablations"][name]
        assert block["status"] == "SCORED"
        zero = block["false_merge_ablation_minus_full"]
        assert zero["candidate_minus_baseline"] == 0.0
        assert zero["ci95_low"] == 0.0
        assert zero["ci95_high"] == 0.0

    interpretation = report["zero_effect_interpretation"]
    assert interpretation["status"] == "COVERAGE_LIMITED_NOT_REFUTATION"
    assert set(interpretation["ablations"]) == set(ZERO_EFFECT_ABLATIONS)


def test_recoverability_and_w_expansion_remain_cannot_check() -> None:
    report = run_coordinate_ablations()
    for name in CANNOT_CHECK_ABLATIONS:
        block = report["ablations"][name]
        assert block["status"] == "CANNOT_CHECK"
        assert "false_merge_ablation_minus_full" not in block
        assert str(block["reason"]).strip()
    assert report["cannot_check"] == list(CANNOT_CHECK_ABLATIONS)


def test_coordinate_strip_ablations_go_through_evaluate_case() -> None:
    cases = load_confirmatory_gold()
    obstruction = next(
        case
        for case in cases
        if MeaningRelation(str(case["expected"]["meaning_relation"])) in NONMERGE_RELATIONS
    )
    full = evaluate_case(obstruction)
    assert full.predicted == "CONTRADICTORY"
    stripped = apply_ablation(obstruction, "remove_modality_polarity_attribution_discourse")
    ablated = evaluate_case(stripped)
    assert ablated.predicted == "COMPATIBLE"
    wrapped = evaluate_ablated_case(
        obstruction, "remove_modality_polarity_attribution_discourse"
    )
    assert wrapped.predicted == "COMPATIBLE"
    assert wrapped.correct is False


def test_zero_effect_is_coverage_limited_not_a_refutation() -> None:
    coverage = coordinate_coverage(load_confirmatory_gold())
    assert coverage["referent_ids"]["disagreement_count"] == 0
    assert coverage["construct_ids"]["disagreement_count"] == 0
    assert coverage["measurement_ids"]["nonempty_count"] == 0
    assert coverage["temporal_context_ids"]["nonempty_count"] == 0
    assert coverage["polarity"]["disagreement_count"] > 0


def test_archived_results_match_live_run() -> None:
    live = archive_results(write=False)
    committed = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert committed["results_sha256"] == live["results_sha256"]
    assert committed["case_count"] == 32
    assert committed["ablations"]["remove_source_projection_recoverability"]["status"] == (
        "CANNOT_CHECK"
    )
    assert committed["ablations"]["remove_w_expansion_reopen"]["status"] == "CANNOT_CHECK"


def test_checkable_ablation_ids_are_the_step5_set() -> None:
    assert CHECKABLE_ABLATIONS == (
        "remove_referent",
        "remove_construct",
        "remove_measurement",
        "remove_temporal_context",
        "remove_modality_polarity_attribution_discourse",
        "force_compatibility_without_obstruction",
    )
    assert CANNOT_CHECK_ABLATIONS == (
        "remove_source_projection_recoverability",
        "remove_w_expansion_reopen",
    )


def test_unknown_ablation_fails_closed() -> None:
    case = load_confirmatory_gold()[0]
    with pytest.raises(ValueError, match="unknown ablation"):
        evaluate_ablated_case(case, "ORION_no_referent")
