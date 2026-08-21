from __future__ import annotations

import pytest

from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.problem_tree import (
    DiscriminatorKind,
    DiscriminatorSpec,
    RecursiveProblemStopReason,
    ResidualAtom,
    ResidualDecomposition,
)
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.residual_recursion import (
    ResidualRecursionPlanner,
    ResidualRecursionPolicy,
)
from orion.engine.trace import SolveTrace
from orion.providers.reasoner.base import Diagnosis, ReframeProposal
from orion.providers.reasoner.scripted import ScriptedReasoner
from orion.runtime import RuntimeResult
from orion_research_harness.recursive_runner import RecursiveRunLimits, _RecursiveSession


def _reasoner(*, decomposition: ResidualDecomposition | None = None) -> ScriptedReasoner:
    return ScriptedReasoner(
        search_plans=[],
        contributions_by_item_id={},
        diagnoses_by_kind={
            ResidualKind.METHOD_GAP: Diagnosis(
                (Responsibility.METHOD,), "method responsibility"
            )
        },
        reframes_by_kind={ResidualKind.METHOD_GAP: ReframeProposal()},
        decompositions_by_kind=(
            {} if decomposition is None else {ResidualKind.METHOD_GAP: decomposition}
        ),
    )


def _state(*, residuals=(), marker: str = "") -> OrionState:
    metadata = () if not marker else (("marker", marker),)
    return OrionState(
        knowledge=KnowledgeState(residuals=tuple(residuals)),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
        metadata=metadata,
    )


def _runtime_result(
    problem: Problem, state: OrionState, *, residual_ids: tuple[str, ...] = ()
) -> RuntimeResult:
    status = SolutionStatus.CANNOT_CHECK if residual_ids else SolutionStatus.PROVISIONAL
    return RuntimeResult(
        solution=Solution(
            problem_id=problem.problem_id,
            status=status,
            answer="bounded test result",
            residual_ids=residual_ids,
            trace_id=f"trace:{problem.problem_id}",
        ),
        final_state=state,
        trace=SolveTrace(trace_id=f"trace:{problem.problem_id}", events=()),
    )


def test_problem_lineage_makes_residual_child_a_real_problem() -> None:
    root = Problem("root", "root question")
    child = Problem(
        "child",
        "child question",
        parent_problem_id="root",
        parent_residual_id="residual:1",
        recursion_depth=1,
    )
    assert root.recursion_depth == 0
    assert child.parent_problem_id == "root"
    assert child.parent_residual_id == "residual:1"
    with pytest.raises(ValueError):
        Problem("bad", "question", parent_problem_id="root")
    with pytest.raises(ValueError):
        Problem("bad-depth", "question", recursion_depth=1)


def test_planner_orders_proof_shortcuts_before_expensive_experiments() -> None:
    residual = Residual(
        "residual:method",
        ResidualKind.METHOD_GAP,
        "The current method language is too coarse to separate the remaining alternatives.",
        candidate_responsibilities=(Responsibility.METHOD,),
    )
    expensive = ResidualAtom(
        atom_id="expensive-experiment",
        question="Does a fresh protected experiment separate the remaining method alternatives?",
        responsibility=Responsibility.METHOD,
        discriminator=DiscriminatorSpec(
            discriminator_id="disc:experiment",
            kind=DiscriminatorKind.EXPERIMENT,
            question="Run the expensive experiment.",
            success_criterion="Separate the alternatives under the frozen evaluator.",
            expected_cost_units=50.0,
        ),
    )
    cheap = ResidualAtom(
        atom_id="cheap-dominance",
        question="Does an incumbent lower envelope dominate every candidate point already on open evidence?",
        responsibility=Responsibility.METHOD,
        discriminator=DiscriminatorSpec(
            discriminator_id="disc:dominance",
            kind=DiscriminatorKind.DOMINANCE_PROOF,
            question="Prove or refute candidate dominance using the open evidence envelope.",
            success_criterion="Return an exact dominance witness or a surviving candidate.",
            expected_cost_units=0.25,
        ),
    )
    decomposition = ResidualDecomposition(
        parent_residual_id=residual.residual_id,
        atoms=(expensive, cheap),
        rationale="two valid discriminators",
    )
    planner = ResidualRecursionPlanner(_reasoner(decomposition=decomposition))
    plan = planner.plan(
        residual=residual,
        problem=Problem("root", "root question"),
        state=_state(residuals=(residual,)),
    )
    assert plan.ordered_atom_ids == ("cheap-dominance", "expensive-experiment")


def test_depth_exhaustion_is_cannot_check_not_false_closure() -> None:
    residual = Residual(
        "residual:deep",
        ResidualKind.METHOD_GAP,
        "A material child residual remains open.",
        candidate_responsibilities=(Responsibility.METHOD,),
    )
    planner = ResidualRecursionPlanner(
        _reasoner(), policy=ResidualRecursionPolicy(max_depth=1)
    )
    child_problem = Problem(
        "child",
        "child question",
        parent_problem_id="root",
        parent_residual_id="residual:parent",
        recursion_depth=1,
    )
    decomposition = planner.decompose(
        residual=residual,
        problem=child_problem,
        state=_state(residuals=(residual,)),
    )
    assert decomposition.atoms == ()
    assert (
        decomposition.stop_reason
        is RecursiveProblemStopReason.CANNOT_CHECK_RESOURCE_BOUND
    )


def test_decomposition_cannot_merely_rename_parent() -> None:
    residual = Residual(
        "residual:rename",
        ResidualKind.METHOD_GAP,
        "Broad method residual",
        candidate_responsibilities=(Responsibility.METHOD,),
    )
    atom = ResidualAtom(
        atom_id="same",
        question="Broad method residual",
        responsibility=Responsibility.METHOD,
        discriminator=DiscriminatorSpec(
            discriminator_id="disc:same",
            kind=DiscriminatorKind.EXACT_COMPUTATION,
            question="Compute something narrower.",
            success_criterion="Produce a discriminating result.",
            expected_cost_units=1.0,
        ),
    )
    decomposition = ResidualDecomposition(
        parent_residual_id=residual.residual_id,
        atoms=(atom,),
    )
    with pytest.raises(ValueError, match="narrower"):
        decomposition.verify(residual)


class _FakeRuntime:
    def __init__(self, parent_residual: Residual) -> None:
        self.parent_residual = parent_residual
        self.calls: list[str] = []
        self.root_calls = 0

    def solve(self, problem: Problem, **_kwargs) -> RuntimeResult:
        self.calls.append(problem.problem_id)
        if problem.recursion_depth == 0:
            self.root_calls += 1
            if self.root_calls == 1:
                return _runtime_result(
                    problem,
                    _state(residuals=(self.parent_residual,)),
                    residual_ids=(self.parent_residual.residual_id,),
                )
            return _runtime_result(problem, _state(marker="dominance-witness"))
        if "cheap-dominance" in problem.problem_id:
            return _runtime_result(problem, _state(marker="dominance-witness"))
        raise AssertionError(
            f"expensive sibling should have been pruned: {problem.problem_id}"
        )


def test_cheaper_child_closing_parent_prunes_expensive_sibling() -> None:
    residual = Residual(
        "residual:r6-like",
        ResidualKind.METHOD_GAP,
        "A compound method candidate may be dominated or may require a fresh experiment.",
        candidate_responsibilities=(Responsibility.METHOD,),
    )
    cheap = ResidualAtom(
        atom_id="cheap-dominance",
        question="Can an open-evidence incumbent envelope already dominate the compound candidate?",
        responsibility=Responsibility.METHOD,
        discriminator=DiscriminatorSpec(
            discriminator_id="disc:cheap",
            kind=DiscriminatorKind.DOMINANCE_PROOF,
            question="Compute the exact incumbent lower envelope.",
            success_criterion="Produce a dominance witness or a surviving point.",
            expected_cost_units=0.1,
        ),
    )
    expensive = ResidualAtom(
        atom_id="fresh-experiment",
        question="If the candidate survives open-evidence dominance, does it transfer prospectively?",
        responsibility=Responsibility.METHOD,
        discriminator=DiscriminatorSpec(
            discriminator_id="disc:expensive",
            kind=DiscriminatorKind.EXPERIMENT,
            question="Run the fresh experiment.",
            success_criterion="Evaluate the frozen prospective transfer gate.",
            expected_cost_units=100.0,
        ),
    )
    decomposition = ResidualDecomposition(
        parent_residual_id=residual.residual_id,
        atoms=(expensive, cheap),
        rationale="cheap dominance can settle the same parent before protected work",
    )
    planner = ResidualRecursionPlanner(_reasoner(decomposition=decomposition))
    runtime = _FakeRuntime(residual)
    session = _RecursiveSession(
        runtime=runtime,  # type: ignore[arg-type]
        planner=planner,
        limits=RecursiveRunLimits(max_depth=3, max_nodes=8),
        evaluation_epoch_id="test",
    )
    root = Problem("root", "root question")
    result, _state_after = session.solve_problem(
        problem=root,
        state=_state(),
        role="root",
    )
    assert result.solution.residual_ids == ()
    assert any("cheap-dominance" in call for call in runtime.calls)
    assert not any("fresh-experiment" in call for call in runtime.calls)
    assert session.pruned_atoms == [
        {
            "parent_problem_id": "root",
            "parent_residual_id": residual.residual_id,
            "atom_id": "fresh-experiment",
            "reason": "PARENT_RESIDUAL_CLOSED_AFTER_CHEAPER_DISCRIMINATOR",
        }
    ]
