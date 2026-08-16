from orion.benchmarks.result import BenchmarkStatus
from orion.benchmarks.verified_discovery import (
    external_authority_gate,
    run_authority_laundering_suite,
)


def test_authority_laundering_local_suite_passes():
    report = run_authority_laundering_suite()
    assert report.passed
    assert report.metric_dict["evidence_substitution_detection"] == 1.0
    assert report.metric_dict["same_lane_promotion_rate"] == 0.0


def test_external_authority_claim_fails_closed_without_protected_live_evaluation():
    report = external_authority_gate(
        source_attribution_benchmark_run=False,
        search_time_contamination_audited=False,
        evaluator_locked=False,
        heldout_access_logged=False,
        matched_nearest_work_baseline_run=False,
        false_promotion_better_than_baseline=None,
    )
    assert report.status is BenchmarkStatus.CANNOT_CHECK
    assert len(report.blockers) == 6


def test_external_authority_claim_fails_if_safety_tradeoff_is_not_better():
    report = external_authority_gate(
        source_attribution_benchmark_run=True,
        search_time_contamination_audited=True,
        evaluator_locked=True,
        heldout_access_logged=True,
        matched_nearest_work_baseline_run=True,
        false_promotion_better_than_baseline=False,
    )
    assert report.status is BenchmarkStatus.FAIL
