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
from orion.core.solution import SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.residual_recursion import ProblemRecursionPlanner, ResidualRecursionPlanner
from orion.providers.reasoner.scripted import ScriptedReasoner
from orion_research_harness.recursive_runner import RecursiveRunLimits, _RecursiveSession


def _state() -> OrionState:
    return OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
        metadata=(("marker", "preserve-me"),),
    )


class _NeverCalledRuntime:
    def solve(self, problem: Problem, **_kwargs):
        raise AssertionError(
            f"root resource-bound snapshot must not consume another runtime node: {problem.problem_id}"
        )


def test_root_node_budget_returns_snapshot_without_consuming_another_node() -> None:
    atom = ProblemAtom(
        atom_id="would-be-next-root-atom",
        question="Would another bounded discriminator help?",
        responsibility=Responsibility.QUESTION,
        discriminator=DiscriminatorSpec(
            discriminator_id="disc:next-root",
            kind=DiscriminatorKind.FORMAL_PROOF,
            question="Check one more root discriminator.",
            success_criterion="Return a bounded discriminator result.",
            expected_cost_units=0.1,
        ),
    )
    decomposition = ProblemDecomposition(
        parent_problem_id="root",
        atoms=(atom,),
        rationale="one root atom remains but the node budget is already exhausted",
    )
    reasoner = ScriptedReasoner(
        search_plans=[],
        contributions_by_item_id={},
        diagnoses_by_kind={},
        reframes_by_kind={},
        problem_decompositions_by_id={"root": decomposition},
    )
    session = _RecursiveSession(
        runtime=_NeverCalledRuntime(),  # type: ignore[arg-type]
        residual_planner=ResidualRecursionPlanner(reasoner),
        problem_planner=ProblemRecursionPlanner(reasoner),
        limits=RecursiveRunLimits(max_depth=3, max_nodes=1),
        evaluation_epoch_id="test",
    )
    # Model an already-spent node. The next root atom must fail closed without
    # calling runtime.solve again merely to manufacture a snapshot.
    session.nodes.append({"node_index": 0, "role": "already-spent"})
    initial = _state()

    result, final_state = session.solve_root(
        problem=Problem("root", "broad root question"),
        state=initial,
    )

    assert session.resource_bound_hit is True
    assert len(session.nodes) == 1
    assert any(
        row["stop_reason"] == "CANNOT_CHECK_RESOURCE_BOUND"
        for row in session.stop_records
    )
    assert result.solution.problem_id == "root"
    assert result.solution.status is SolutionStatus.CANNOT_CHECK
    assert result.final_state == initial
    assert final_state == initial
    assert result.trace.events == ()
