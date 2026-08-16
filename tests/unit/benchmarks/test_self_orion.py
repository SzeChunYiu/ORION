from orion.benchmarks.result import BenchmarkStatus
from orion.benchmarks.self_orion import (
    external_self_orion_gate,
    run_self_orion_known_world,
)


def test_self_orion_issue_cause_transfer_and_reward_hacking_suite_passes():
    report = run_self_orion_known_world()
    assert report.passed
    assert report.metric_dict["false_method_change"] == 0.0
    assert report.metric_dict["reward_hack_promotion_rate"] == 0.0
    assert report.metric_dict["negative_interventions_retained"] == 1.0


def test_external_self_orion_claim_remains_cannot_check_without_prospective_trial():
    report = external_self_orion_gate(
        matched_self_edit_baseline_run=False,
        matched_agent_design_baseline_run=False,
        failure_causes_hidden_from_candidate=False,
        fresh_transfer_split=False,
        evaluator_frozen_before_candidate=False,
        negative_history_complete=False,
        protected_path_access_logged=False,
        root_improvement_over_baselines=None,
    )
    assert report.status is BenchmarkStatus.CANNOT_CHECK
    assert len(report.blockers) == 8


def test_external_self_orion_gate_fails_if_baselines_are_not_beaten():
    report = external_self_orion_gate(
        matched_self_edit_baseline_run=True,
        matched_agent_design_baseline_run=True,
        failure_causes_hidden_from_candidate=True,
        fresh_transfer_split=True,
        evaluator_frozen_before_candidate=True,
        negative_history_complete=True,
        protected_path_access_logged=True,
        root_improvement_over_baselines=False,
    )
    assert report.status is BenchmarkStatus.FAIL
