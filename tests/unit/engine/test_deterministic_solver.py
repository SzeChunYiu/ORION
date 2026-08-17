from __future__ import annotations

from dataclasses import replace
from hashlib import sha256

import pytest

import orion.engine.deterministic_solver as solver_module
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search import SearchRouteKind
from orion.core.solution import SolutionStatus
from orion.engine.deterministic_solver import (
    CheckerPolicy,
    CompiledProblem,
    DeterministicProblemSolver,
    DeterministicSolverConfig,
    GoalClause,
    TransitionCertificate,
    TransitionCheckRequest,
    TransitionRule,
    VerificationVerdict,
)
from orion.kernel.support import (
    DependencyStatus,
    DependencyStatusEvent,
    SupportSet,
)
from orion.knowledge.backward_multiseed import SeedFamily, SeedOrigin, WaypointSeed
from orion.knowledge.route_control import (
    FrozenRouteControlPolicy,
    RouteAttempt,
    RouteControlState,
    decide_route,
)
from orion.knowledge.route_family_health import RouteHealthState


def _event(event_id: str, dependency: str, status: DependencyStatus, time: int):
    return DependencyStatusEvent(event_id, dependency, status, time, status.value)


def _rule(
    rule_id: str,
    pre: tuple[str, ...],
    add: tuple[str, ...],
    *,
    cost: int = 1,
    dependency: str = "dep:live",
    route_id: str = "route:default",
    tags: tuple[str, ...] = (),
    signature: tuple[str, ...] = (),
) -> TransitionRule:
    return TransitionRule(
        rule_id=rule_id,
        route_id=route_id,
        route_kind=SearchRouteKind.FUNCTION_ONLY,
        preconditions=frozenset(pre),
        add_effects=frozenset(add),
        delete_effects=frozenset(),
        support_sets=(SupportSet(f"support:{rule_id}", (dependency,)),),
        cost_units=cost,
        checker_policy=CheckerPolicy(
            checker_id=f"checker:{rule_id}",
            checker_lineage_id="lineage:independent",
            checker_binary_digest="1" * 64,
            policy_digest="2" * 64,
            authority_root_digest="3" * 64,
            version=1,
            valid_from=0,
            valid_until=100,
            revocation_epoch=0,
        ),
        checker_registered_before_run=True,
        representation="facts:v1",
        structural_signature=signature,
        semantic_tags=tags,
    )


def _problem(
    *rules: TransitionRule,
    goal: tuple[str, ...] = ("goal",),
    history: tuple[DependencyStatusEvent, ...] | None = None,
    status_time: int = 1,
    residuals: tuple[Residual, ...] = (),
    seeds: tuple[WaypointSeed, ...] = (),
    route_health: tuple[tuple[str, RouteHealthState], ...] = (),
    route_decisions=(),
) -> CompiledProblem:
    return CompiledProblem(
        problem_id="problem:known-world",
        snapshot_id="snapshot:v1",
        initial_facts=frozenset({"start"}),
        goals=(GoalClause("goal:main", frozenset(goal)),),
        rules=rules,
        dependency_history=history
        if history is not None
        else (_event("event:live", "dep:live", DependencyStatus.LIVE, 1),),
        status_time=status_time,
        admissible_checker_lineage_ids=("lineage:independent",),
        residuals=residuals,
        waypoint_seeds=seeds,
        route_health=route_health,
        route_decisions=route_decisions,
    )


def _provider(request: TransitionCheckRequest) -> TransitionCertificate:
    artifact_id = f"artifact:{request.rule_id}:{request.target_state_digest[:12]}"
    return TransitionCertificate(
        problem_snapshot_digest=request.problem_snapshot_digest,
        rule_id=request.rule_id,
        rule_digest=request.rule_digest,
        source_state_digest=request.source_state_digest,
        target_state_digest=request.target_state_digest,
        checker_id=request.checker_id,
        checker_lineage_id=request.checker_lineage_id,
        checker_policy_digest=request.checker_policy_digest,
        artifact_id=artifact_id,
        artifact_digest=sha256(artifact_id.encode()).hexdigest(),
        verdict=VerificationVerdict.PASS,
    )


def _seed(seed_id: str, family: SeedFamily, signature: tuple[str, ...]):
    return WaypointSeed(
        seed_id=seed_id,
        root_goal_id="goal:main",
        atom_ids=("atom",),
        family=family,
        statement_or_object=seed_id,
        representation="facts:v1",
        structural_signature=signature,
        origin=SeedOrigin.OPERATOR_APPLICATION,
        origin_operator_id="fixture",
        expected_useful_connection="connect to goal",
        falsifier_or_cheapest_connection_test="run exact transition checker",
    )


def test_model_validation_and_snapshot_digest_are_deterministic() -> None:
    direct = _rule("rule:direct", ("start",), ("goal",))
    first = _problem(direct)
    second = _problem(direct)

    assert first.digest == second.digest
    assert len(first.digest) == 64

    with pytest.raises(ValueError, match="strictly positive"):
        replace(direct, cost_units=-1)
    with pytest.raises(ValueError, match="unique"):
        _problem(direct, direct)


def test_zero_cost_transition_is_rejected_without_a_rank_witness() -> None:
    with pytest.raises(ValueError, match="strictly positive"):
        _rule("rule:zero", ("start",), ("goal",), cost=0)


def test_support_environments_must_be_subset_minimal() -> None:
    base = _rule("rule:nonminimal", ("start",), ("goal",))
    with pytest.raises(ValueError, match="subset-minimal"):
        replace(
            base,
            support_sets=(
                SupportSet("support:minimal", ("dep:a",)),
                SupportSet("support:subsumed", ("dep:a", "dep:b")),
            ),
        )


def test_checker_policy_has_content_bound_identity_and_validity_window() -> None:
    assert hasattr(solver_module, "CheckerPolicy")
    policy = solver_module.CheckerPolicy(
        checker_id="checker:exact",
        checker_lineage_id="lineage:independent",
        checker_binary_digest="1" * 64,
        policy_digest="2" * 64,
        authority_root_digest="3" * 64,
        version=4,
        valid_from=2,
        valid_until=8,
        revocation_epoch=1,
    )

    assert len(policy.digest) == 64
    assert policy.is_valid_at(2)
    assert policy.is_valid_at(8)
    assert not policy.is_valid_at(1)
    assert not policy.is_valid_at(9)


def test_transition_rule_binds_the_full_checker_policy() -> None:
    rule = _rule("rule:policy-bound", ("start",), ("goal",))

    assert hasattr(rule, "checker_policy")
    assert rule.checker_policy.checker_binary_digest == "1" * 64
    assert rule.checker_policy.policy_digest == "2" * 64
    assert rule.checker_policy.authority_root_digest == "3" * 64


def test_expired_checker_policy_fails_closed() -> None:
    base = _rule("rule:expired", ("start",), ("goal",))
    expired = replace(
        base,
        checker_policy=replace(base.checker_policy, valid_until=0),
    )

    result = DeterministicProblemSolver(_provider).solve(_problem(expired))

    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any("checker_policy_not_valid" in item for item in result.receipt.residuals)


def test_transition_check_request_explicitly_binds_checker_policy_digest() -> None:
    seen: list[TransitionCheckRequest] = []

    def capturing_provider(request: TransitionCheckRequest) -> TransitionCertificate:
        seen.append(request)
        return _provider(request)

    result = DeterministicProblemSolver(capturing_provider).solve(
        _problem(_rule("rule:captured", ("start",), ("goal",)))
    )

    assert result.status is SolutionStatus.SOLVED_VERIFIED
    assert seen
    assert hasattr(seen[0], "checker_policy_digest")
    assert len(seen[0].checker_policy_digest) == 64


def test_transition_certificate_explicitly_binds_checker_policy_digest() -> None:
    result = DeterministicProblemSolver(_provider).solve(
        _problem(_rule("rule:certificate-policy", ("start",), ("goal",)))
    )

    assert result.status is SolutionStatus.SOLVED_VERIFIED
    certificate = result.receipt.steps[0].certificate
    assert hasattr(certificate, "checker_policy_digest")
    assert len(certificate.checker_policy_digest) == 64


def test_rule_input_order_is_not_part_of_problem_identity_or_result() -> None:
    first_rule = _rule("rule:first", ("start",), ("middle",))
    second_rule = _rule("rule:second", ("middle",), ("goal",))
    left = _problem(first_rule, second_rule)
    right = _problem(second_rule, first_rule)
    solver = DeterministicProblemSolver(_provider)

    assert left.digest == right.digest
    assert solver.solve(left).receipt.hash == solver.solve(right).receipt.hash


def test_checker_lineage_must_be_frozen_as_admissible() -> None:
    base = _rule("rule:self", ("start",), ("goal",))
    self_checked = replace(
        base,
        checker_policy=replace(
            base.checker_policy,
            checker_lineage_id="lineage:candidate-owned",
        ),
    )

    result = DeterministicProblemSolver(_provider).solve(_problem(self_checked))

    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any(
        "checker_lineage_not_admissible" in item for item in result.receipt.residuals
    )


def test_uniform_cost_search_selects_cheapest_fully_verified_path() -> None:
    expensive = _rule("rule:expensive", ("start",), ("goal",), cost=8)
    first = _rule("rule:first", ("start",), ("middle",), cost=2)
    second = _rule("rule:second", ("middle",), ("goal",), cost=2)

    result = DeterministicProblemSolver(_provider).solve(
        _problem(expensive, first, second)
    )

    assert result.status is SolutionStatus.SOLVED_VERIFIED
    assert tuple(step.rule_id for step in result.receipt.steps) == (
        "rule:first",
        "rule:second",
    )
    assert result.receipt.total_cost_units == 4
    assert result.receipt.goal_clause_id == "goal:main"
    assert result.evidence_ids


def test_unknown_or_stale_support_fails_closed_as_cannot_check() -> None:
    rule = _rule("rule:unknown", ("start",), ("goal",), dependency="dep:unknown")
    problem = _problem(rule, history=())

    result = DeterministicProblemSolver(_provider).solve(problem)

    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any("support_cannot_check" in item for item in result.receipt.residuals)
    assert result.receipt.steps == ()


def test_one_live_dnf_alternative_survives_another_alternative_revocation() -> None:
    base = _rule("rule:alternatives", ("start",), ("goal",))
    alternatives = replace(
        base,
        support_sets=(
            SupportSet("support:live-alternative", ("dep:live",)),
            SupportSet("support:revoked-alternative", ("dep:revoked",)),
        ),
    )
    history = (
        _event("event:live", "dep:live", DependencyStatus.LIVE, 1),
        _event("event:revoked", "dep:revoked", DependencyStatus.REVOKED, 1),
    )

    result = DeterministicProblemSolver(_provider).solve(
        _problem(alternatives, history=history)
    )

    assert result.status is SolutionStatus.SOLVED_VERIFIED
    assert result.receipt.steps[0].live_support_set_ids == ("support:live-alternative",)


def test_all_revoked_support_is_retained_as_negative_history() -> None:
    rule = _rule("rule:revoked", ("start",), ("goal",), dependency="dep:revoked")
    result = DeterministicProblemSolver(_provider).solve(
        _problem(
            rule,
            history=(
                _event("event:revoked", "dep:revoked", DependencyStatus.REVOKED, 1),
            ),
        )
    )

    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any(
        "support_fail:rule:revoked" in item for item in result.receipt.negative_history
    )


def test_certificate_substitution_is_rejected() -> None:
    rule = _rule("rule:target", ("start",), ("goal",))

    def substituted(request: TransitionCheckRequest) -> TransitionCertificate:
        return replace(_provider(request), target_state_digest="0" * 64)

    result = DeterministicProblemSolver(substituted).solve(_problem(rule))

    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any("certificate_mismatch" in item for item in result.receipt.residuals)
    assert result.receipt.steps == ()


def test_checker_policy_substitution_is_rejected() -> None:
    rule = _rule("rule:policy-target", ("start",), ("goal",))

    def substituted(request: TransitionCheckRequest) -> TransitionCertificate:
        return replace(_provider(request), checker_policy_digest="0" * 64)

    result = DeterministicProblemSolver(substituted).solve(_problem(rule))

    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any("checker_policy_digest" in item for item in result.receipt.residuals)
    assert result.receipt.steps == ()


def test_approximate_assurance_cannot_emit_verified_terminal() -> None:
    assert hasattr(solver_module, "AssuranceMode")
    problem = replace(
        _problem(_rule("rule:approximate", ("start",), ("goal",))),
        assurance_mode=solver_module.AssuranceMode.APPROXIMATE,
    )

    result = DeterministicProblemSolver(_provider).solve(problem)

    assert result.status is SolutionStatus.PROVISIONAL
    assert any(
        "approximate_assurance_no_closure" in item for item in result.receipt.residuals
    )


def test_shortcut_miss_falls_back_to_full_scan() -> None:
    residual = Residual(
        "residual:representation",
        ResidualKind.REPRESENTATION_FAILURE,
        "need another coordinate system",
        candidate_responsibilities=(Responsibility.REPRESENTATION,),
    )
    unrelated = _rule(
        "rule:only-road",
        ("start",),
        ("goal",),
        tags=("completely-unrelated",),
    )

    result = DeterministicProblemSolver(_provider).solve(
        _problem(unrelated, residuals=(residual,))
    )

    assert result.status is SolutionStatus.SOLVED_VERIFIED
    assert result.receipt.shortcut_misses >= 1
    assert tuple(step.rule_id for step in result.receipt.steps) == ("rule:only-road",)


def test_backward_seed_is_tie_break_only_and_never_mints_solution() -> None:
    seeds = (
        _seed("seed:a", SeedFamily.CANDIDATE_LEMMA, ("bridge",)),
        _seed("seed:b", SeedFamily.NORMAL_FORM, ("bridge",)),
        _seed("seed:c", SeedFamily.REDUCTION_TARGET, ("bridge",)),
    )

    no_rules = DeterministicProblemSolver(_provider).solve(_problem(seeds=seeds))

    assert no_rules.status is SolutionStatus.CANNOT_CHECK
    assert no_rules.receipt.steps == ()
    assert no_rules.receipt.seed_diversity_count == 3


def test_route_stop_never_certifies_task_saturation() -> None:
    policy = FrozenRouteControlPolicy("flat", 1, 2)
    state = RouteControlState(
        "route:stopped",
        SearchRouteKind.FUNCTION_ONLY,
        (RouteAttempt("attempt", "query", (), (), 1.0, backend_exhausted=True),),
        5.0,
    )
    decision = decide_route(state, policy)
    rule = _rule(
        "rule:stopped",
        ("start",),
        ("goal",),
        route_id="route:stopped",
    )

    result = DeterministicProblemSolver(_provider).solve(
        _problem(rule, route_decisions=(decision,))
    )

    assert not decision.certifies_task_saturation
    assert result.status is SolutionStatus.CANNOT_CHECK
    assert any("route_locally_stopped" in item for item in result.receipt.residuals)


def test_health_and_seed_signals_only_order_equal_cost_verified_paths() -> None:
    slow_hint = _rule(
        "rule:a-stagnant",
        ("start",),
        ("goal",),
        route_id="route:stagnant",
        signature=("other",),
    )
    good_hint = _rule(
        "rule:z-progressive",
        ("start",),
        ("goal",),
        route_id="route:progressive",
        signature=("bridge",),
    )
    seeds = (
        _seed("seed:a", SeedFamily.CANDIDATE_LEMMA, ("bridge",)),
        _seed("seed:b", SeedFamily.NORMAL_FORM, ("bridge",)),
        _seed("seed:c", SeedFamily.REDUCTION_TARGET, ("bridge",)),
    )
    result = DeterministicProblemSolver(_provider).solve(
        _problem(
            slow_hint,
            good_hint,
            seeds=seeds,
            route_health=(
                ("route:stagnant", RouteHealthState.STAGNANT_SIGNAL),
                ("route:progressive", RouteHealthState.PROGRESSIVE_SIGNAL),
            ),
        )
    )

    assert result.status is SolutionStatus.SOLVED_VERIFIED
    assert result.receipt.steps[0].rule_id == "rule:z-progressive"


def test_receipt_hash_replays_deterministically() -> None:
    problem = _problem(_rule("rule:direct", ("start",), ("goal",)))
    solver = DeterministicProblemSolver(_provider)

    first = solver.solve(problem)
    second = solver.solve(problem)

    assert first.receipt.hash == second.receipt.hash
    assert first.receipt == second.receipt


def test_dependency_revocation_reopens_earliest_affected_step_and_preserves_old_receipt() -> (
    None
):
    prefix = _rule("rule:prefix", ("start",), ("middle",), dependency="dep:prefix")
    old_suffix = _rule("rule:old", ("middle",), ("goal",), dependency="dep:old")
    new_suffix = _rule("rule:new", ("middle",), ("goal",), dependency="dep:new")
    at_one = (
        _event("event:prefix:live", "dep:prefix", DependencyStatus.LIVE, 1),
        _event("event:old:live", "dep:old", DependencyStatus.LIVE, 1),
        _event("event:new:unknown", "dep:new", DependencyStatus.UNKNOWN, 1),
    )
    original_problem = _problem(prefix, old_suffix, new_suffix, history=at_one)
    solver = DeterministicProblemSolver(_provider)
    original = solver.solve(original_problem)
    assert tuple(step.rule_id for step in original.receipt.steps) == (
        "rule:prefix",
        "rule:old",
    )

    at_two = at_one + (
        _event("event:old:revoked", "dep:old", DependencyStatus.REVOKED, 2),
        _event("event:new:live", "dep:new", DependencyStatus.LIVE, 2),
    )
    changed = replace(original_problem, dependency_history=at_two, status_time=2)
    reopened = solver.solve(
        changed,
        prior_receipt=original.receipt,
        changed_dependency_ids=("dep:old", "dep:new"),
    )

    assert reopened.status is SolutionStatus.SOLVED_VERIFIED
    assert reopened.receipt.previous_receipt_hash == original.receipt.hash
    assert reopened.receipt.reopened_from_step == 1
    assert hasattr(reopened.receipt, "matched_prefix_rule_ids")
    assert reopened.receipt.matched_prefix_rule_ids == ("rule:prefix",)
    assert tuple(step.rule_id for step in reopened.receipt.steps) == (
        "rule:prefix",
        "rule:new",
    )


def test_resource_bound_returns_blocked_without_false_impossibility() -> None:
    rule = _rule("rule:direct", ("start",), ("goal",))
    solver = DeterministicProblemSolver(
        _provider, config=DeterministicSolverConfig(max_expansions=0)
    )

    result = solver.solve(_problem(rule))

    assert result.status is SolutionStatus.BLOCKED
    assert "resource_bound" in result.receipt.residuals
    assert "impossible" not in result.answer.casefold()
