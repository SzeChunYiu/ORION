from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.problem import Problem
from orion.core.solution import Solution, SolutionStatus

from .deterministic_solver import (
    CompiledProblem,
    DeterministicProblemSolver,
    MechanicalSolveResult,
)


class RouteDecision(str, Enum):
    """Why the deterministic route did or did not carry the problem.

    NOT_COMPILED is not a failure of the solver — it is the honest statement
    that no typed problem model exists for this question yet, which is where
    the text-to-model interpretation gap lives.
    """

    SOLVED_DETERMINISTICALLY = "SOLVED_DETERMINISTICALLY"
    NOT_COMPILED = "NOT_COMPILED"
    DETERMINISTIC_RESIDUAL = "DETERMINISTIC_RESIDUAL"


@dataclass(frozen=True)
class RouteOutcome:
    """The deterministic attempt, with the receipt that justifies its verdict.

    `reasoner_invoked` is recorded because the claim this route exists to make
    is that a verified answer was produced without one. A claim about what did
    not happen needs a witness as much as a claim about what did.
    """

    decision: RouteDecision
    solution: Solution | None
    result: MechanicalSolveResult | None
    reasoner_invoked: bool


def attempt_deterministic_route(
    problem: Problem,
    compiled: CompiledProblem | None,
    solver: DeterministicProblemSolver | None,
) -> RouteOutcome:
    """Try to close `problem` by verified transition search, with no reasoner.

    The route yields a `Solution` only when the mechanical result is a verified
    or provisional terminal. Every other status — BLOCKED, CANNOT_CHECK, a
    resource bound, an unavailable certificate — is returned as a residual so
    the caller decides what to do next. The route never upgrades a mechanical
    status; it only translates one.
    """

    if compiled is None or solver is None:
        return RouteOutcome(RouteDecision.NOT_COMPILED, None, None, reasoner_invoked=False)

    result = solver.solve(compiled)
    if result.status not in {SolutionStatus.SOLVED_VERIFIED, SolutionStatus.PROVISIONAL}:
        return RouteOutcome(
            RouteDecision.DETERMINISTIC_RESIDUAL, None, result, reasoner_invoked=False
        )

    # A verified terminal without evidence would fail Solution's own invariant.
    # Rather than fabricate an evidence id, degrade the status honestly.
    status = result.status
    if status is SolutionStatus.SOLVED_VERIFIED and not result.evidence_ids:
        status = SolutionStatus.PROVISIONAL

    solution = Solution(
        problem_id=problem.problem_id,
        status=status,
        answer=result.answer,
        evidence_ids=result.evidence_ids,
        residual_ids=result.receipt.residuals,
        iterations=len(result.receipt.steps),
    )
    return RouteOutcome(
        RouteDecision.SOLVED_DETERMINISTICALLY, solution, result, reasoner_invoked=False
    )


__all__ = ["RouteDecision", "RouteOutcome", "attempt_deterministic_route"]
