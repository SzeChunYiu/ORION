from orion.benchmarks.discovery import external_discovery_gate, run_discovery_known_world
from orion.benchmarks.result import BenchmarkStatus


def test_open_world_known_world_exercises_recall_and_coverage_refusals():
    report = run_discovery_known_world()
    assert report.passed
    assert report.metric_dict["system_recall_at_2"] == 1.0
    assert report.metric_dict["recall_margin_at_2"] > 0.0
    assert report.metric_dict["content_union_after_reencounter"] == 1.0


def test_external_discovery_claim_remains_cannot_check_without_live_frozen_trial():
    report = external_discovery_gate(
        benchmark_name="AutoResearchBench-wide",
        complete_gold=True,
        matched_baseline=False,
        frozen_provider_trace=False,
        system_beats_baseline=None,
    )
    assert report.status is BenchmarkStatus.CANNOT_CHECK
    assert len(report.blockers) == 3


def test_external_discovery_gate_requires_beating_the_baseline():
    report = external_discovery_gate(
        benchmark_name="frozen-local-complete-gold",
        complete_gold=True,
        matched_baseline=True,
        frozen_provider_trace=True,
        system_beats_baseline=False,
    )
    assert report.status is BenchmarkStatus.FAIL
