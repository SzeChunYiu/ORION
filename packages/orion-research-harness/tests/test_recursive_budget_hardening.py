from __future__ import annotations

from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.problem_tree import (
    DiscriminatorKind,
    DiscriminatorSpec,
    ProblemAtom,
    ProblemDecomposition,
)
from orion.core.residuals import Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.trace import SolveTrace
from orion.runtime import RuntimeResult
from orion_research_harness.recursive_runner import RecursiveRunLimits, _RecursiveSession


class _ProblemPlanner:
    def __init__(self, atoms):
        self._decomposition = ProblemDecomposition(
            parent_problem_id="root",
            atoms=tuple(atoms),
            rationale="force the hard root node-budget boundary",
        )

    def decompose(self, **_kwargs):
        return self._decomposition

    @staticmethod
    def order_atoms(atoms):
        return tuple(sorted(atoms, key=lambda item: item.discriminator.expected_cost_units))


class _Runtime:
    def solve(self, problem: Problem, **_kwargs) -> RuntimeResult:
        state = OrionState(
            knowledge=KnowledgeState(),
            search_universe=SearchUniverseState(),
            method=MethodState(method_version="test"),
            metadata=(("checkpoint", "preserved"),),
        )
        trace = SolveTrace(trace_id=f"trace:{problem.problem_id}", events=())
        return RuntimeResult(
            solution=Solution(
                problem_id=problem.problem_id,
                status=SolutionStatus.PROVISIONAL,
                answer="child completed without closing root",
                trace_id=trace.trace_id,
            ),
            final_state=state,
            trace=trace,
        )


def _atom(atom_id: str, cost: float) -> ProblemAtom:
    return ProblemAtom(
        atom_id=atom_id,
        question=f"Can {atom_id} settle one root coordinate?",
        responsibility=Responsibility.QUESTION,
        discriminator=DiscriminatorSpec(
            discriminator_id=f"disc:{atom_id}",
            kind=DiscriminatorKind.EXACT_COMPUTATION,
            question=f"Evaluate {atom_id}.",
            success_criterion=f"Return a bounded result for {atom_id}.",
            expected_cost_units=cost,
        ),
    )


def test_hard_root_node_budget_returns_root_cannot_check_with_checkpoint() -> None:
    assert getattr(_RecursiveSession, "_recursive_budget_hardening_installed", False)
    session = _RecursiveSession(
        runtime=_Runtime(),  # type: ignore[arg-type]
        residual_planner=object(),  # unused in this boundary test
        problem_planner=_ProblemPlanner((_atom("first", 1.0), _atom("second", 2.0))),  # type: ignore[arg-type]
        limits=RecursiveRunLimits(max_depth=3, max_nodes=1),
        evaluation_epoch_id="test",
    )
    initial = OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
    )
    result, working = session.solve_root(
        problem=Problem("root", "root question"),
        state=initial,
    )
    assert session.resource_bound_hit is True
    assert result.solution.problem_id == "root"
    assert result.solution.status is SolutionStatus.CANNOT_CHECK
    assert "resource bound" in result.solution.answer.lower()
    assert dict(result.final_state.metadata)["checkpoint"] == "preserved"
    assert dict(working.metadata)["checkpoint"] == "preserved"
    assert result.trace.trace_id.startswith("recursive-resource-bound:")
    assert any(
        row.get("stop_reason") == "CANNOT_CHECK_RESOURCE_BOUND"
        for row in session.stop_records
    )
