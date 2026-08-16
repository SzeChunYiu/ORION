import pytest

from orion.knowledge.backward_multiseed_benchmark import (
    ArmVerdict,
    ContaminationCeilings,
    FrozenBenchmarkSpec,
    HiddenPathCase,
    HiddenPathTaskFamily,
    MatchedBudget,
    SearchArm,
    TaskArmObservation,
    compare_arms,
    evaluate_arm,
)

BUDGET = MatchedBudget(64, 64, 64, 100_000, 600.0)
CEILINGS = ContaminationCeilings(0.10, 0.90, 0.25)


def _case(index: int, family: HiddenPathTaskFamily) -> HiddenPathCase:
    return HiddenPathCase(
        f"case-{index}", family, f"root-{index}", (f"evidence-{index}",), True, True, True
    )


def _spec(*, arms=tuple(SearchArm), ceilings=CEILINGS, n_cases=4, frozen=True):
    families = tuple(HiddenPathTaskFamily)
    cases = tuple(_case(i, families[i % len(families)]) for i in range(n_cases))
    return FrozenBenchmarkSpec("bench-141", cases, arms, BUDGET, ceilings, 1, frozen)


def _observation(
    case_index: int,
    arm: SearchArm,
    *,
    solved=False,
    emitted=0,
    useful=0,
    irrelevant=0,
    claimed=4,
    confirmed=4,
    tests=4,
    claims=2,
    upheld=2,
    retries=0,
    tool_calls=10,
    expansions=10,
    gold_path_exposed=False,
    budget_frozen=True,
):
    return TaskArmObservation(
        benchmark_id="bench-141",
        case_id=f"case-{case_index}",
        arm=arm,
        verified_solved=solved,
        root_obligations_declared=2,
        root_obligations_verified_closed=1,
        waypoints_emitted=emitted,
        waypoints_used_in_verified_connection=useful,
        waypoints_judged_irrelevant_by_evaluator=irrelevant,
        connection_tests_run=tests,
        connection_tests_claimed_verified=claimed,
        connection_tests_confirmed_by_checker=confirmed,
        root_progress_claims=claims,
        root_progress_claims_upheld=upheld,
        repeated_known_failure_retries=retries,
        distinct_representations_used=2,
        forward_frontier_signature=("f1", "f2"),
        backward_frontier_signature=("f2", "b1"),
        expansions_used=expansions,
        tool_calls_used=tool_calls,
        tokens_used=1_000,
        wall_clock_seconds=5.0,
        verification_debt=0.5,
        gold_path_exposed=gold_path_exposed,
        budget_frozen_before_run=budget_frozen,
    )


def test_spec_can_cover_all_six_arms_and_nine_task_families():
    spec = _spec(n_cases=9)
    assert spec.covers_all_arms
    assert spec.covers_all_task_families
    assert len(SearchArm) == 6
    assert len(HiddenPathTaskFamily) == 9


def test_harness_cannot_invent_results_without_observations():
    spec = _spec()
    report = evaluate_arm(spec, (), SearchArm.A_FORWARD_ONLY)
    assert report.verdict is ArmVerdict.INSUFFICIENT_HISTORY
    assert report.metrics is None
    assert "harness_does_not_generate_arm_results" in report.reasons
    comparison = compare_arms(spec, ())
    assert all(item.metrics is None for item in comparison.ranked)
    assert "no_observations_supplied" in comparison.reasons
    assert not comparison.establishes_extension_benefit


def test_waypoint_volume_cannot_buy_rank():
    spec = _spec(arms=(SearchArm.C_FORWARD_BACKWARD, SearchArm.D_FORWARD_SEEDS))
    noisy, quiet = SearchArm.C_FORWARD_BACKWARD, SearchArm.D_FORWARD_SEEDS
    rows = []
    for index in range(4):
        solved = index < 2
        rows.append(_observation(index, noisy, solved=solved, emitted=1_000, useful=2, irrelevant=998))
        rows.append(_observation(index, quiet, solved=solved, emitted=2, useful=2, irrelevant=0))
    comparison = compare_arms(spec, rows)
    noisy_report, quiet_report = evaluate_arm(spec, rows, noisy), evaluate_arm(spec, rows, quiet)
    assert noisy_report.metrics is not None and quiet_report.metrics is not None
    assert noisy_report.metrics.verified_solve_rate == quiet_report.metrics.verified_solve_rate
    assert noisy_report.metrics.irrelevant_waypoint_rate == pytest.approx(0.998)
    assert quiet_report.metrics.irrelevant_waypoint_rate == pytest.approx(0.0)
    assert comparison.rank_of(quiet) < comparison.rank_of(noisy)


def test_false_root_progress_contaminates_even_high_solve_arm():
    spec = _spec(arms=(SearchArm.A_FORWARD_ONLY, SearchArm.B_BACKWARD_ONLY))
    rows = []
    for index in range(4):
        rows.append(_observation(index, SearchArm.A_FORWARD_ONLY, solved=index < 1))
        rows.append(_observation(index, SearchArm.B_BACKWARD_ONLY, solved=True, claims=4, upheld=1))
    honest = evaluate_arm(spec, rows, SearchArm.A_FORWARD_ONLY)
    contaminated = evaluate_arm(spec, rows, SearchArm.B_BACKWARD_ONLY)
    assert honest.verdict is ArmVerdict.ARM_ADMISSIBLE
    assert contaminated.verdict is ArmVerdict.ARM_CONTAMINATED
    assert contaminated.metrics is not None and honest.metrics is not None
    assert contaminated.metrics.verified_solve_rate > honest.metrics.verified_solve_rate
    assert comparison_rank(spec, rows, SearchArm.A_FORWARD_ONLY) < comparison_rank(spec, rows, SearchArm.B_BACKWARD_ONLY)


def comparison_rank(spec, rows, arm):
    rank = compare_arms(spec, rows).rank_of(arm)
    assert rank is not None
    return rank


def test_low_connection_precision_contaminates_arm():
    spec = _spec(arms=(SearchArm.A_FORWARD_ONLY, SearchArm.B_BACKWARD_ONLY))
    rows = [_observation(i, SearchArm.B_BACKWARD_ONLY, solved=True, claimed=8, confirmed=2, tests=8) for i in range(4)]
    report = evaluate_arm(spec, rows, SearchArm.B_BACKWARD_ONLY)
    assert report.verdict is ArmVerdict.ARM_CONTAMINATED
    assert any("UNVERIFIED_CONNECTION_AS_ROAD" in reason for reason in report.reasons)


def test_gold_path_exposure_budget_violation_and_posthoc_freeze_invalidate():
    spec = _spec()
    exposed = evaluate_arm(spec, [_observation(0, SearchArm.A_FORWARD_ONLY, solved=True, gold_path_exposed=True)], SearchArm.A_FORWARD_ONLY)
    assert exposed.verdict is ArmVerdict.TRIAL_INVALID
    over = evaluate_arm(spec, [_observation(0, SearchArm.E_FORWARD_BACKWARD_SEEDS, solved=True, expansions=BUDGET.max_expansions + 1)], SearchArm.E_FORWARD_BACKWARD_SEEDS)
    assert over.verdict is ArmVerdict.TRIAL_INVALID
    late_spec = _spec(frozen=False)
    late = evaluate_arm(late_spec, [_observation(0, SearchArm.A_FORWARD_ONLY, solved=True)], SearchArm.A_FORWARD_ONLY)
    assert late.verdict is ArmVerdict.TRIAL_INVALID


def test_unknown_integrity_state_is_cannot_check():
    spec = _spec()
    base = _observation(0, SearchArm.A_FORWARD_ONLY, solved=True)
    row = TaskArmObservation(**{**base.__dict__, "gold_path_exposed": None})
    report = evaluate_arm(spec, [row], SearchArm.A_FORWARD_ONLY)
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert report.metrics is None


def test_spec_hash_changes_when_contamination_threshold_is_retuned():
    original = _spec()
    retuned = _spec(ceilings=ContaminationCeilings(0.90, 0.10, 0.90))
    assert original.spec_hash != retuned.spec_hash


def test_metrics_and_comparison_grant_no_authority_or_capability_claim():
    spec = _spec()
    rows = [_observation(0, SearchArm.A_FORWARD_ONLY, solved=True)]
    report = evaluate_arm(spec, rows, SearchArm.A_FORWARD_ONLY)
    assert report.metrics is not None
    assert not report.grants_scientific_authority
    assert not report.metrics.grants_capability_claim
    comparison = compare_arms(spec, rows)
    assert not comparison.grants_scientific_authority
    assert not comparison.establishes_extension_benefit


def test_observation_rejects_impossible_counts_and_bad_budget_contracts():
    with pytest.raises(ValueError):
        _observation(0, SearchArm.A_FORWARD_ONLY, claimed=1, confirmed=5)
    with pytest.raises(ValueError):
        _observation(0, SearchArm.A_FORWARD_ONLY, emitted=2, useful=2, irrelevant=2)
    with pytest.raises(ValueError):
        MatchedBudget(0, 1, 1, 1, 1.0)
    with pytest.raises(ValueError):
        ContaminationCeilings(1.1, 0.9, 0.2)
