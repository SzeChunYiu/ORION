"""LOCAL_ENGINEERING_ONLY: #136 structural-transfer substrate.

Not scientific cross-domain transfer evidence for #286.
"""

from __future__ import annotations

import math

import pytest

from orion.transfer import (
    AffineLens,
    AlgorithmCell,
    AuthorityReadiness,
    CandidateArchive,
    CandidateRecord,
    CandidateVerdict,
    ConsistencyStatus,
    ConservativeRouteAllocator,
    Defeater,
    DefeaterPlanner,
    DiagnosticProbe,
    EvidenceAction,
    LensEdge,
    MultiStageCandidateGate,
    ProblemSignature,
    ResponsibilityDiagnoser,
    ResponsibilityHypothesis,
    ScientificLensNetwork,
    Stage,
    StageResult,
    StageVerdict,
    StructuralTransferSolver,
    TransferStatus,
    assess_transfer,
)


def signature(problem_id: str, domain: str, *, risk: float = 0.5) -> ProblemSignature:
    return ProblemSignature(
        problem_id=problem_id,
        source_domain=domain,
        hidden_state="latent-cause",
        observability="partial",
        actions=frozenset({"probe", "abstain"}),
        ground_truth="protected",
        dependence=0.6,
        authority_risk=risk,
        nonstationarity=0.2,
        reversibility=0.8,
    )


def cell(cell_id: str, source: ProblemSignature) -> AlgorithmCell:
    return AlgorithmCell(
        cell_id=cell_id,
        source_signature=source,
        mechanism="active-probe",
        assumptions=("probe-valid",),
        invariants=("no authority from retrieval score",),
        stopping_rule="stop when distinguished",
        failure_modes=("non-diagnosable",),
        falsifiers=("toy-world-separates",),
    )


def test_far_domain_is_a_retrieval_bonus_not_an_authority_grant() -> None:
    target = signature("target", "scientific-research")
    remote = signature("remote", "fault-diagnosis")
    candidate = cell("remote-active-probe", remote)
    assessment = assess_transfer(
        target,
        candidate,
        assumption_truth={"probe-valid": False},
        falsifier_results={"toy-world-separates": True},
    )
    assert target.far_domain_score(remote) > target.structural_similarity(remote)
    assert assessment.status is TransferStatus.BLOCKED_ASSUMPTION
    assert not assessment.admissible


def test_unknown_assumption_fails_closed_as_cannot_check() -> None:
    target = signature("target", "science")
    candidate = cell("c", signature("s", "medicine"))
    assessment = assess_transfer(
        target,
        candidate,
        assumption_truth={"probe-valid": None},
        falsifier_results={"toy-world-separates": True},
    )
    assert assessment.status is TransferStatus.CANNOT_CHECK


def test_failed_falsifier_blocks_even_when_assumptions_hold() -> None:
    target = signature("target", "science")
    candidate = cell("c", signature("s", "medicine"))
    assessment = assess_transfer(
        target,
        candidate,
        assumption_truth={"probe-valid": True},
        falsifier_results={"toy-world-separates": False},
    )
    assert assessment.status is TransferStatus.OBSTRUCTED


def test_solver_skips_highest_scoring_invalid_analogy() -> None:
    target = signature("target", "science")
    highest = cell("highest", signature("near-perfect", "ecology"))
    lower_source = ProblemSignature(
        problem_id="lower",
        source_domain="clinical-trials",
        hidden_state="latent-cause",
        observability="partial",
        actions=frozenset({"probe"}),
        ground_truth="protected",
        dependence=0.5,
        authority_risk=0.5,
        nonstationarity=0.2,
        reversibility=0.7,
    )
    lower = cell("lower", lower_source)
    solver = StructuralTransferSolver()
    assert solver.rank(target, [lower, highest])[0].cell_id == "highest"
    selected = solver.select(
        target,
        [lower, highest],
        {
            "highest": ({"probe-valid": False}, {"toy-world-separates": True}),
            "lower": ({"probe-valid": True}, {"toy-world-separates": True}),
        },
    )
    assert selected is not None
    assert selected.cell.cell_id == "lower"
    assert selected.assessment.status is TransferStatus.ADMISSIBLE


def make_diagnoser() -> ResponsibilityDiagnoser:
    return ResponsibilityDiagnoser(
        [
            ResponsibilityHypothesis("evidence", 1.0),
            ResponsibilityHypothesis("execution", 1.0),
            ResponsibilityHypothesis("formulation", 1.0),
        ],
        cost_weight=0.02,
        risk_weight=0.05,
    )


def test_p1_identical_probe_signatures_are_detected_as_non_diagnosable() -> None:
    diagnoser = make_diagnoser()
    blind = DiagnosticProbe(
        "blind", {"evidence": 0.5, "execution": 0.5, "formulation": 0.5}
    )
    assert diagnoser.information_gain(blind) == pytest.approx(0.0)
    assert not diagnoser.diagnosable([blind])
    assert diagnoser.choose_probe([blind]) is None


def test_p1_selects_probe_with_more_information_after_cost_and_risk() -> None:
    diagnoser = make_diagnoser()
    weak = DiagnosticProbe(
        "weak", {"evidence": 0.45, "execution": 0.55, "formulation": 0.50}, cost=0.1
    )
    strong = DiagnosticProbe(
        "strong",
        {"evidence": 0.05, "execution": 0.10, "formulation": 0.95},
        cost=1.0,
        risk=0.1,
    )
    assert diagnoser.choose_probe([weak, strong]) == strong


def test_p1_observation_can_license_formulation_rewrite_only_after_discrimination() -> None:
    diagnoser = make_diagnoser()
    probe = DiagnosticProbe(
        "representation-challenge",
        {"evidence": 0.05, "execution": 0.05, "formulation": 0.98},
    )
    assert not diagnoser.licenses({"formulation"}, threshold=0.8)
    diagnoser.observe(probe, positive=True)
    name, probability = diagnoser.best_hypothesis()
    assert name == "formulation"
    assert probability > 0.9
    assert diagnoser.licenses({"formulation"}, threshold=0.8)
    assert not diagnoser.licenses({"evidence", "execution"}, threshold=0.8)


def test_p1_evidence_diagnosis_does_not_license_formulation_rewrite() -> None:
    diagnoser = make_diagnoser()
    probe = DiagnosticProbe(
        "evidence-probe",
        {"evidence": 0.99, "execution": 0.01, "formulation": 0.01},
    )
    diagnoser.observe(probe, positive=True)
    assert diagnoser.best_hypothesis()[0] == "evidence"
    assert not diagnoser.licenses({"formulation"}, threshold=0.8)


def test_p2_falls_back_to_baseline_until_safety_credit_exists() -> None:
    allocator = ConservativeRouteAllocator(
        baseline_route="bm25", baseline_lower_bound=1.0, alpha=0.2
    )
    allocator.register("semantic")
    assert allocator.select() == "bm25"
    for _ in range(3):
        allocator.record("bm25", reward=1.0)
        assert allocator.safety_credit >= -1e-12
        assert allocator.select() == "bm25"
    allocator.record("bm25", reward=1.0)
    assert allocator.safety_credit == pytest.approx(0.8)
    assert allocator.select() == "semantic"


def test_p2_censored_unavailability_is_not_learned_as_zero_reward() -> None:
    allocator = ConservativeRouteAllocator(
        baseline_route="bm25", baseline_lower_bound=1.0, alpha=0.5
    )
    allocator.register("openalex")
    allocator.record("bm25", reward=1.0)
    assert allocator.select() == "openalex"
    allocator.record("openalex", reward=None, censored=True, lower_bound=0.0)
    route = allocator.routes["openalex"]
    assert route.observed_attempts == 0
    assert route.mean_reward is None
    assert route.censored_attempts == 1


def test_p2_exploration_can_outperform_baseline_in_toy_world_without_breaking_floor() -> None:
    allocator = ConservativeRouteAllocator(
        baseline_route="bm25", baseline_lower_bound=1.0, alpha=0.5
    )
    allocator.register("far-route")
    realized = 0.0
    allocator.record("bm25", reward=1.0)
    realized += 1.0
    assert allocator.select() == "far-route"
    allocator.record("far-route", reward=3.0, lower_bound=0.0)
    realized += 3.0
    assert allocator.safety_credit >= -1e-12
    assert realized > 2.0


def test_p2_allocator_rejects_call_that_would_break_declared_safety_invariant() -> None:
    allocator = ConservativeRouteAllocator(
        baseline_route="bm25", baseline_lower_bound=1.0, alpha=0.2
    )
    allocator.register("unsafe")
    with pytest.raises(AssertionError):
        allocator.record("unsafe", reward=10.0, lower_bound=0.0)


def test_p3_affine_lens_round_trip_is_exact_up_to_float_precision() -> None:
    c_to_f = AffineLens(scale=9 / 5, offset=32)
    for value in (-40.0, 0.0, 37.0, 100.0):
        assert c_to_f.round_trip_error(value) < 1e-12


def test_p3_consistent_cycle_is_globalizable() -> None:
    a_to_b = AffineLens(2.0, 1.0)
    b_to_c = AffineLens(3.0, -4.0)
    a_to_c = a_to_b.then(b_to_c)
    network = ScientificLensNetwork(
        [
            LensEdge("A", "B", a_to_b),
            LensEdge("B", "C", b_to_c),
            LensEdge("A", "C", a_to_c),
        ]
    )
    assert network.assess_cycle(["A", "B", "C", "A"], [-2.0, 0.0, 5.0]) is (
        ConsistencyStatus.GLOBALIZABLE
    )


def test_p3_corrupted_mapping_yields_obstruction_instead_of_forced_merge() -> None:
    network = ScientificLensNetwork(
        [
            LensEdge("A", "B", AffineLens(2.0, 1.0)),
            LensEdge("B", "C", AffineLens(3.0, -4.0)),
            LensEdge("A", "C", AffineLens(6.0, 2.0)),
        ]
    )
    assert network.assess_cycle(["A", "B", "C", "A"], [0.0, 1.0, 10.0]) is (
        ConsistencyStatus.OBSTRUCTION
    )


def test_p3_empty_anchor_set_refuses_consistency_claim() -> None:
    network = ScientificLensNetwork([LensEdge("A", "B", AffineLens(2.0))])
    assert network.assess_cycle(["A", "B", "A"], []) is ConsistencyStatus.CANNOT_CHECK


def test_p4_planner_selects_best_protected_risk_reduction_per_cost() -> None:
    planner = DefeaterPlanner(critical_threshold=0.7)
    defeaters = [Defeater("wrong-source", 0.9), Defeater("contamination", 0.8)]
    cheap_weak = EvidenceAction(
        "cheap-weak", frozenset({"wrong-source"}), success_probability=0.2, cost=1.0
    )
    strong = EvidenceAction(
        "strong",
        frozenset({"wrong-source", "contamination"}),
        success_probability=0.9,
        cost=2.0,
    )
    assert planner.choose_action(defeaters, [cheap_weak, strong]) == strong


def test_p4_unprotected_evidence_action_cannot_clear_critical_defeater_path() -> None:
    planner = DefeaterPlanner()
    defeaters = [Defeater("evaluator-integrity", 1.0)]
    self_check = EvidenceAction(
        "self-check",
        frozenset({"evaluator-integrity"}),
        success_probability=1.0,
        cost=0.1,
        protected=False,
    )
    assert planner.choose_action(defeaters, [self_check]) is None
    assert planner.readiness(defeaters, [self_check]) is AuthorityReadiness.CANNOT_CHECK


def test_p4_evidence_planning_never_directly_grants_authority() -> None:
    planner = DefeaterPlanner()
    defeaters = [Defeater("support-gap", 0.8)]
    action = EvidenceAction(
        "retrieve-independent-source",
        frozenset({"support-gap"}),
        success_probability=1.0,
        cost=1.0,
    )
    assert planner.choose_action(defeaters, [action]) == action
    assert planner.readiness(defeaters, [action]) is AuthorityReadiness.BLOCKED


def test_p4_no_unresolved_defeaters_only_reaches_external_check_boundary() -> None:
    planner = DefeaterPlanner()
    assert planner.readiness([], []) is AuthorityReadiness.READY_FOR_EXTERNAL_CHECK


def passing(stage: Stage, score: float = 0.0, cost: float = 1.0) -> StageResult:
    return StageResult(stage, StageVerdict.PASS, score_delta=score, cost=cost)


def test_p5_large_replay_gain_cannot_compensate_fresh_harm() -> None:
    gate = MultiStageCandidateGate()
    record = CandidateRecord("candidate")
    record.record(passing(Stage.STATIC))
    record.record(passing(Stage.REPLAY, score=100.0))
    record.record(StageResult(Stage.FRESH, StageVerdict.FAIL, score_delta=-0.1, harmful=True))
    assert gate.evaluate(record) is CandidateVerdict.REJECT
    assert gate.next_stage(record) is None


def test_p5_protected_cannot_check_blocks_promotion() -> None:
    gate = MultiStageCandidateGate()
    record = CandidateRecord("candidate")
    for stage in (Stage.STATIC, Stage.REPLAY, Stage.FRESH):
        record.record(passing(stage))
    record.record(StageResult(Stage.PROTECTED, StageVerdict.CANNOT_CHECK))
    assert gate.evaluate(record) is CandidateVerdict.CANNOT_CHECK


def test_p5_all_required_noncompensatory_stages_end_only_in_host_recommendation() -> None:
    gate = MultiStageCandidateGate()
    record = CandidateRecord("candidate")
    for stage in gate.required_stages:
        record.record(passing(stage))
    assert gate.evaluate(record) is CandidateVerdict.RECOMMEND_HOST_PROMOTION
    assert gate.next_stage(record) is None


def test_p5_early_failure_avoids_later_expensive_stages() -> None:
    gate = MultiStageCandidateGate()
    record = CandidateRecord("bad")
    record.record(StageResult(Stage.STATIC, StageVerdict.FAIL, cost=0.1))
    assert gate.evaluate(record) is CandidateVerdict.REJECT
    assert gate.next_stage(record) is None
    assert record.total_cost == pytest.approx(0.1)


def test_p5_archive_retains_failed_and_harmful_candidate() -> None:
    archive = CandidateArchive()
    bad = CandidateRecord("harmful")
    bad.record(StageResult(Stage.STATIC, StageVerdict.FAIL, harmful=True))
    archive.retain(bad)
    assert len(archive) == 1
    assert archive.get("harmful").results[Stage.STATIC].harmful


def test_problem_similarity_is_finite_and_bounded_with_domain_bonus() -> None:
    a = signature("a", "domain-a")
    b = signature("b", "domain-b")
    score = a.far_domain_score(b)
    assert math.isfinite(score)
    assert 0.0 <= a.structural_similarity(b) <= 1.0
    assert score <= 1.15 + 1e-12


def test_p2_rejected_unsafe_record_is_transactional() -> None:
    allocator = ConservativeRouteAllocator(
        baseline_route="bm25", baseline_lower_bound=1.0, alpha=0.2
    )
    allocator.register("unsafe")
    with pytest.raises(AssertionError):
        allocator.record("unsafe", reward=10.0, lower_bound=0.0)
    assert allocator.steps == 0
    assert allocator.cumulative_lower_bound == 0.0
    assert allocator.routes["unsafe"].observed_attempts == 0
    assert allocator.routes["unsafe"].observed_reward == 0.0


def test_p5_out_of_order_recorded_failure_still_blocks() -> None:
    gate = MultiStageCandidateGate()
    record = CandidateRecord("bad-order")
    record.record(StageResult(Stage.FRESH, StageVerdict.FAIL, harmful=True))
    assert gate.evaluate(record) is CandidateVerdict.REJECT


def test_all_paper_specific_toy_falsifiers_show_the_intended_local_advantage() -> None:
    from orion.transfer.toy_benchmarks import run_all_toys

    results = run_all_toys()
    assert [result.paper for result in results] == ["P1", "P2", "P3", "P4", "P5"]
    assert all(result.passed for result in results)
    assert all(result.improvement > 0 for result in results)


def test_cross_confirmation_requires_distinct_source_domains() -> None:
    target = signature("target", "science")
    source_a = signature("a", "fault-diagnosis")
    source_a2 = signature("a2", "fault-diagnosis")
    c1 = cell("c1", source_a)
    c2 = cell("c2", source_a2)
    solver = StructuralTransferSolver()
    evidence = {
        "c1": ({"probe-valid": True}, {"toy-world-separates": True}),
        "c2": ({"probe-valid": True}, {"toy-world-separates": True}),
    }
    assert solver.cross_confirm(target, [c1, c2], evidence, mechanism="active-probe") is None


def test_cross_confirmation_accepts_two_admissible_independent_domains() -> None:
    target = signature("target", "science")
    c1 = cell("c1", signature("a", "fault-diagnosis"))
    c2 = cell("c2", signature("b", "clinical-diagnosis"))
    solver = StructuralTransferSolver()
    evidence = {
        "c1": ({"probe-valid": True}, {"toy-world-separates": True}),
        "c2": ({"probe-valid": True}, {"toy-world-separates": True}),
    }
    confirmed = solver.cross_confirm(target, [c1, c2], evidence, mechanism="active-probe")
    assert confirmed is not None
    assert confirmed.source_domains == frozenset({"fault-diagnosis", "clinical-diagnosis"})
