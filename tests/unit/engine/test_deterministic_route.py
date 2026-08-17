from __future__ import annotations



from orion.core.problem import Problem
from orion.core.solution import SolutionStatus
from orion.engine.deterministic_route import (
    RouteDecision,
    attempt_deterministic_route,
)


class ExplodingReasoner:
    """Any attribute access is a reasoner invocation, and fails the test.

    The claim under test is negative — that a verified answer was produced
    without a language model. A negative claim needs a witness, so this stands
    in for one: if the deterministic route touches the reasoner at all, the
    test fails rather than passing quietly.
    """

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"reasoner was invoked ({name}) on the deterministic route")


def test_an_uncompiled_problem_is_not_compiled_not_a_failure() -> None:
    """No typed model is an honest NOT_COMPILED, never a solved or failed verdict."""

    problem = Problem(problem_id="p1", question="anything")
    outcome = attempt_deterministic_route(problem, None, None)
    assert outcome.decision is RouteDecision.NOT_COMPILED
    assert outcome.solution is None
    assert not outcome.reasoner_invoked


def test_a_blocked_mechanical_result_yields_a_residual_not_a_solution() -> None:
    """The route translates a mechanical status; it never upgrades one."""

    problem = Problem(problem_id="p2", question="anything")

    class BlockedSolver:
        def solve(self, compiled: object) -> object:
            class Result:
                status = SolutionStatus.BLOCKED
                answer = "resource bound reached"
                evidence_ids: tuple[str, ...] = ()
                receipt = type("R", (), {"residuals": ("resource_bound",), "steps": ()})()

            return Result()

    outcome = attempt_deterministic_route(problem, object(), BlockedSolver())
    assert outcome.decision is RouteDecision.DETERMINISTIC_RESIDUAL
    assert outcome.solution is None
    assert outcome.result is not None
    assert "resource_bound" in outcome.result.receipt.residuals


def test_a_verified_result_without_evidence_degrades_rather_than_fabricating_one() -> None:
    """Solution refuses a verified status with no evidence. The honest response
    is to lower the status, never to mint an evidence id to satisfy the check."""

    problem = Problem(problem_id="p3", question="anything")

    class EvidencelessSolver:
        def solve(self, compiled: object) -> object:
            class Result:
                status = SolutionStatus.SOLVED_VERIFIED
                answer = "chain closes"
                evidence_ids: tuple[str, ...] = ()
                receipt = type("R", (), {"residuals": (), "steps": ()})()

            return Result()

    outcome = attempt_deterministic_route(problem, object(), EvidencelessSolver())
    assert outcome.solution is not None
    assert outcome.solution.status is SolutionStatus.PROVISIONAL
    assert outcome.solution.evidence_ids == ()


def test_a_verified_chain_closes_the_problem_without_any_reasoner() -> None:
    problem = Problem(problem_id="p4", question="anything")

    class VerifiedSolver:
        def solve(self, compiled: object) -> object:
            class Result:
                status = SolutionStatus.SOLVED_VERIFIED
                answer = "verified transition chain satisfies the goal"
                evidence_ids = ("cert:a1",)
                receipt = type("R", (), {"residuals": (), "steps": ("s1", "s2")})()

            return Result()

    outcome = attempt_deterministic_route(problem, object(), VerifiedSolver())
    assert outcome.decision is RouteDecision.SOLVED_DETERMINISTICALLY
    assert outcome.solution is not None
    assert outcome.solution.status is SolutionStatus.SOLVED_VERIFIED
    assert outcome.solution.iterations == 2
    assert not outcome.reasoner_invoked


def test_the_solver_never_touches_the_reasoner_when_the_route_closes() -> None:
    """End-to-end through OrionSolver: the wiring, not just the bridge."""

    from orion.engine.solver import OrionSolver

    problem = Problem(problem_id="p5", question="anything")

    class VerifiedSolver:
        def solve(self, compiled: object) -> object:
            class Result:
                status = SolutionStatus.SOLVED_VERIFIED
                answer = "verified transition chain satisfies the goal"
                evidence_ids = ("cert:a1",)
                receipt = type("R", (), {"residuals": (), "steps": ("s1",)})()

            return Result()

    solver = OrionSolver(
        reasoner=ExplodingReasoner(),
        retrieval=ExplodingReasoner(),
        verification=ExplodingReasoner(),
        deterministic=VerifiedSolver(),
        compiled_problems={"p5": object()},
    )
    solution, _state, _trace = solver.solve(problem)
    assert solution.status is SolutionStatus.SOLVED_VERIFIED
    assert solution.problem_id == "p5"


def test_an_uncompiled_problem_still_reaches_the_reasoner_path() -> None:
    """The deterministic route must not silently swallow problems it cannot
    model — an uncompiled problem falls through to the existing route."""

    from orion.engine.solver import OrionSolver

    problem = Problem(problem_id="unmodelled", question="anything")
    solver = OrionSolver(
        reasoner=ExplodingReasoner(),
        retrieval=ExplodingReasoner(),
        verification=ExplodingReasoner(),
        deterministic=None,
        compiled_problems={},
    )
    # The solver catches operator exceptions and fails closed with a typed
    # residual rather than propagating, so the witness that the reasoner was
    # reached is the residual naming the operator that touched it.
    solution, _state, _trace = solver.solve(problem)
    assert solution.status is SolutionStatus.BLOCKED
    assert any(
        residual.startswith("operator-exception:SEARCH")
        for residual in solution.residual_ids
    ), solution.residual_ids


def test_a_verified_exact_receipt_records_that_its_exactness_was_declared() -> None:
    """Exactness is asserted by whoever compiled the problem, not derived from
    the checkers that ran. It is auditable after the fact — every checker binary,
    policy and authority root is content-bound — but unchecked during the solve.
    The caveat therefore has to ride on the SOLVED_VERIFIED receipt, which is the
    only case where it changes what a reader should conclude. A first version of
    this test used a rule-less problem, which can only exit via graph exhaustion:
    it proved the caveat appears on a failed solve, where nobody is misled.
    """

    from hashlib import sha256

    from orion.core.solution import SolutionStatus as _Status
    from orion.kernel.support import DependencyStatus, DependencyStatusEvent
    from orion.engine.deterministic_solver import (
        AssuranceBasis,
        AssuranceMode,
        CheckerPolicy,
        CompiledProblem,
        DeterministicProblemSolver,
        GoalClause,
        SearchRouteKind,
        SupportSet,
        TransitionCertificate,
        TransitionRule,
        VerificationVerdict,
    )

    policy = CheckerPolicy(
        checker_id="checker:1",
        checker_lineage_id="lineage:independent",
        checker_binary_digest="c" * 64,
        policy_digest="d" * 64,
        authority_root_digest="e" * 64,
        version=1,
        valid_from=0,
        valid_until=10,
        revocation_epoch=0,
    )
    rule = TransitionRule(
        rule_id="rule:1",
        route_id="route:1",
        route_kind=SearchRouteKind.CURRENT_VOCABULARY,
        preconditions=frozenset({"a"}),
        add_effects=frozenset({"z"}),
        delete_effects=frozenset(),
        support_sets=(SupportSet("support:1", ("dep:live",)),),
        cost_units=1,
        checker_policy=policy,
        checker_registered_before_run=True,
        representation="facts:v1",
        structural_signature=(),
        semantic_tags=(),
    )
    problem = CompiledProblem(
        problem_id="exactness",
        snapshot_id="snap:1",
        initial_facts=frozenset({"a"}),
        goals=(GoalClause(clause_id="g1", required_facts=frozenset({"z"})),),
        rules=(rule,),
        dependency_history=(
            DependencyStatusEvent(
                "event:live", "dep:live", DependencyStatus.LIVE, 1, DependencyStatus.LIVE.value
            ),
        ),
        status_time=1,
        admissible_checker_lineage_ids=("lineage:independent",),
        assurance_mode=AssuranceMode.EXACT,
    )

    def provider(request):
        return TransitionCertificate(
            problem_snapshot_digest=request.problem_snapshot_digest,
            rule_id=request.rule_id,
            rule_digest=request.rule_digest,
            source_state_digest=request.source_state_digest,
            target_state_digest=request.target_state_digest,
            checker_id=request.checker_id,
            checker_lineage_id=request.checker_lineage_id,
            checker_policy_digest=request.checker_policy_digest,
            artifact_id="artifact:1",
            artifact_digest=sha256(b"artifact:1").hexdigest(),
            verdict=VerificationVerdict.PASS,
        )

    result = DeterministicProblemSolver(provider).solve(problem)
    assert result.status is _Status.SOLVED_VERIFIED, result.receipt.residuals
    assert result.receipt.assurance_mode is AssuranceMode.EXACT
    assert result.receipt.assurance_basis is AssuranceBasis.DECLARED
