from __future__ import annotations

from orion.core.method import MethodState
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.trace import SolveTrace
from orion.runtime import RuntimeResult
from orion_research_harness.recursive_runner import _RecursiveSession, run_problem_recursive
from orion_research_harness.research_director import (
    ResearchDirectiveKind,
    direct_research,
)
from orion_research_harness.workspace import ResearchWorkspace


def _residual(residual_id: str, responsibility: Responsibility | None, *, ambiguous: bool = False) -> Residual:
    if ambiguous:
        responsibilities = (Responsibility.SEARCH, Responsibility.METHOD)
    elif responsibility is None:
        responsibilities = ()
    else:
        responsibilities = (responsibility,)
    return Residual(
        residual_id=residual_id,
        kind=ResidualKind.METHOD_GAP if responsibility is Responsibility.METHOD else ResidualKind.UNCLASSIFIED,
        description=f"open residual {residual_id}",
        candidate_responsibilities=responsibilities,
    )


def test_verified_no_residual_routes_to_saturation_never_task_stop():
    directive = direct_research(
        solution_status=SolutionStatus.SOLVED_VERIFIED,
        material_residuals=(),
    )
    assert directive.kind is ResearchDirectiveKind.ASSESS_SATURATION
    assert directive.grants_global_task_stop_authority is False
    assert directive.paper_ids == ("P2", "P5", "P7")


def test_method_residual_routes_to_ocme_not_direct_method_jump():
    directive = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(_residual("r:method", Responsibility.METHOD),),
    )
    assert directive.kind is ResearchDirectiveKind.ASSESS_OCME
    assert directive.paper_ids == ("P10",)
    assert "jump" not in directive.kind.value.casefold()
    assert directive.grants_scientific_authority is False


def test_noncompensatory_execution_evidence_evaluator_precedence():
    directive = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(
            _residual("r:method", Responsibility.METHOD),
            _residual("r:evidence", Responsibility.EVIDENCE),
            _residual("r:execution", Responsibility.EXECUTION),
            _residual("r:evaluator", Responsibility.EVALUATOR),
        ),
    )
    assert directive.kind is ResearchDirectiveKind.RESTORE_CAPABILITY
    assert directive.trigger_residual_ids == ("r:execution",)
    assert directive.paper_ids == ("P15",)


def test_ambiguous_or_missing_responsibility_requires_diagnosis():
    ambiguous = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(_residual("r:a", Responsibility.METHOD, ambiguous=True),),
    )
    assert ambiguous.kind is ResearchDirectiveKind.DIAGNOSE_RESPONSIBILITY
    missing = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(_residual("r:b", None),),
    )
    assert missing.kind is ResearchDirectiveKind.DIAGNOSE_RESPONSIBILITY


def test_resource_and_identity_ambiguity_fail_closed_before_other_actions():
    residual = _residual("r:method", Responsibility.METHOD)
    resource = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(residual,),
        resource_bound_hit=True,
    )
    assert resource.kind is ResearchDirectiveKind.CANNOT_CHECK
    identity = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(residual,),
        identity_ambiguity_hit=True,
    )
    assert identity.kind is ResearchDirectiveKind.CANNOT_CHECK


def test_search_family_responsibilities_route_to_navigation_or_reframe():
    for responsibility in (
        Responsibility.QUESTION,
        Responsibility.REPRESENTATION,
        Responsibility.SEARCH,
        Responsibility.ROUTING,
        Responsibility.DECOMPOSITION,
        Responsibility.INTERFACE,
        Responsibility.MEASUREMENT,
    ):
        directive = direct_research(
            solution_status=SolutionStatus.CANNOT_CHECK,
            material_residuals=(_residual(f"r:{responsibility.value}", responsibility),),
        )
        assert directive.kind is ResearchDirectiveKind.NAVIGATE_OR_REFRAME
        assert directive.paper_ids == ("P1", "P2", "P7")


def test_recursive_complete_outcome_exposes_director_result(monkeypatch, tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    final_state = OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="fixture"),
    )
    fake = RuntimeResult(
        solution=Solution(
            problem_id="problem:director",
            status=SolutionStatus.SOLVED_VERIFIED,
            answer="verified bounded answer",
            evidence_ids=("e:verified",),
            trace_id="trace:director",
        ),
        final_state=final_state,
        trace=SolveTrace(trace_id="trace:director", events=()),
    )

    def fake_solve_root(self, *, problem, state):
        return fake, final_state

    monkeypatch.setattr(_RecursiveSession, "solve_root", fake_solve_root)
    outcome = run_problem_recursive(
        workspace,
        {
            "problem_id": "problem:director",
            "question": "What next control action is required?",
        },
    )
    assert outcome["status"] == "COMPLETE"
    assert outcome["research_directive"]["kind"] == "ASSESS_SATURATION"
    assert outcome["research_directive"]["grants_global_task_stop_authority"] is False
