from __future__ import annotations

from orion.core.method import MethodState
from orion.core.research_resolution import (
    AssimilationDisposition,
    ResearchOutcomeKind,
    ResolutionAction,
    ResolutionState,
    UnresolvedClass,
)
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.trace import SolveTrace
from orion.runtime import RuntimeResult
from orion_research_harness.recursive_director_integration import _dedupe_reason_codes
from orion_research_harness.recursive_runner import _RecursiveSession, run_problem_recursive
from orion_research_harness.research_resolution import (
    assimilate_negative_result,
    build_resolution_obligation,
)
from orion_research_harness.workspace import ResearchWorkspace


def test_resource_cannot_check_is_active_resolution_obligation_not_task_stop():
    obligation = build_resolution_obligation(
        subject_id="problem:resource",
        unresolved_class=UnresolvedClass.RESOURCE,
        reason_codes=("RECURSIVE_NODE_BUDGET_EXHAUSTED",),
        attempt_ids=("run:1",),
    )
    assert obligation.outcome_kind is ResearchOutcomeKind.UNRESOLVED
    assert obligation.state is ResolutionState.ACTIVE
    assert ResolutionAction.REQUEST_RESOURCE_WIDENING in obligation.next_actions
    assert ResolutionAction.REFRAME in obligation.next_actions
    assert ResolutionAction.TASK_STOP not in obligation.next_actions
    assert obligation.grants_scientific_authority is False
    assert obligation.grants_global_task_stop_authority is False


def test_duplicate_recursive_stop_reasons_are_deduplicated_before_obligation_construction():
    assert _dedupe_reason_codes(
        (
            "CANNOT_CHECK_RESOURCE_BOUND",
            "CANNOT_CHECK_RESOURCE_BOUND",
            "CANNOT_CHECK_AMBIGUOUS_RESIDUAL_IDENTITY",
            "CANNOT_CHECK_RESOURCE_BOUND",
        )
    ) == (
        "CANNOT_CHECK_RESOURCE_BOUND",
        "CANNOT_CHECK_AMBIGUOUS_RESIDUAL_IDENTITY",
    )


def test_protected_external_cannot_check_remains_explicitly_blocked_not_local_retry():
    obligation = build_resolution_obligation(
        subject_id="claim:protected",
        unresolved_class=UnresolvedClass.PROTECTED_EXTERNAL,
        reason_codes=("PROTECTED_EVALUATOR_NOT_RELEASED",),
        blocker_ids=("protected:evaluator:v1",),
    )
    assert obligation.state is ResolutionState.BLOCKED_EXTERNAL
    assert obligation.next_actions == (ResolutionAction.REQUEST_PROTECTED_EVIDENCE,)
    assert ResolutionAction.RETRY_CAPABILITY not in obligation.next_actions
    assert obligation.bounded_stop_condition


def test_donor_subsumption_is_negative_scientific_result_not_cannot_check():
    result = assimilate_negative_result(
        result_id="negative:donor",
        subject_id="method:candidate",
        negative_kind="DONOR_SUBSUMED",
        evidence_ids=("e:donor",),
        reason_codes=("STRONG_DONOR_SAME_REACH",),
    )
    assert result.outcome_kind is ResearchOutcomeKind.NEGATIVE
    assert AssimilationDisposition.REGISTER_DONOR_SUBSUMPTION in result.dispositions
    assert AssimilationDisposition.CLOSE_HYPOTHESIS_BRANCH in result.dispositions
    assert result.grants_novelty_authority is False
    assert result.grants_scientific_authority is False


def test_verified_obstruction_is_negative_and_reframes_instead_of_becoming_unknown():
    result = assimilate_negative_result(
        result_id="negative:obstruction",
        subject_id="method:old-language",
        negative_kind="VERIFIED_OBSTRUCTION",
        evidence_ids=("e:obstruction",),
        reason_codes=("EXACT_FINITE_NONREACHABILITY",),
    )
    assert result.outcome_kind is ResearchOutcomeKind.NEGATIVE
    assert AssimilationDisposition.ASSIMILATE_OBSTRUCTION in result.dispositions
    assert AssimilationDisposition.REFRAME in result.dispositions
    assert result.grants_global_task_stop_authority is False


def test_unknown_unresolved_class_fails_closed_with_diagnosis_only():
    obligation = build_resolution_obligation(
        subject_id="problem:unknown",
        unresolved_class=UnresolvedClass.UNKNOWN,
        reason_codes=("UNMAPPED_REASON",),
    )
    assert obligation.state is ResolutionState.ACTIVE
    assert obligation.next_actions == (ResolutionAction.DIAGNOSE_RESPONSIBILITY,)


def test_recursive_cannot_check_outcome_is_not_bare(monkeypatch, tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    final_state = OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="fixture"),
    )
    fake = RuntimeResult(
        solution=Solution(
            problem_id="problem:v4",
            status=SolutionStatus.CANNOT_CHECK,
            answer="evidence is still insufficient",
            trace_id="trace:v4",
        ),
        final_state=final_state,
        trace=SolveTrace(trace_id="trace:v4", events=()),
    )

    def fake_solve_root(self, *, problem, state):
        return fake, final_state

    monkeypatch.setattr(_RecursiveSession, "solve_root", fake_solve_root)
    outcome = run_problem_recursive(
        workspace,
        {"problem_id": "problem:v4", "question": "Can this be decided?"},
    )
    assert outcome["status"] == "COMPLETE"
    assert outcome["solution_status"] == "CANNOT_CHECK"
    resolution = outcome["resolution_obligation"]
    assert resolution["schema"] == "ORION.ResearchResolutionObligation.v1"
    assert resolution["outcome_kind"] == "UNRESOLVED"
    assert resolution["grants_global_task_stop_authority"] is False
