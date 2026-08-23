from __future__ import annotations

import json

import pytest

from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.providers.llm import CallableLLMProvider
from orion.providers.reasoner.recursive_llm import RecursiveLLMResearchReasoner
from orion_research_harness.execution_coverage import execution_coverage
from orion_research_harness.governance_runtime import (
    ContextCandidate,
    request_benchmark,
    request_independent_review,
    select_context,
)
from orion_research_harness.mechanics_bridge import canonical_mechanic_cells
from orion_research_harness.workspace import ResearchWorkspace


def test_all_59_mechanics_have_resolvable_execution_owners() -> None:
    coverage = execution_coverage(canonical_mechanic_cells())
    assert coverage["mechanic_count"] == 59
    assert coverage["specification_only_ids"] == []
    assert coverage["owner_resolution_failures"] == []
    assert coverage["automatic_missing_ids"] == []
    assert coverage["automatic_not_ready_ids"] == []
    assert coverage["direct_runtime_missing_ids"] == []
    assert coverage["executable_owner_coverage_ready"] is True

    by_id = {row["mechanic_id"]: row for row in coverage["rows"]}
    assert by_id["FRAME.DECOMPOSE.v0"]["execution_mode"] == "RECURSIVE_RUNTIME"
    assert by_id["DIAGNOSE.DISCRIMINATOR.v0"]["execution_mode"] == "RECURSIVE_RUNTIME"
    assert by_id["REOPEN.FIBRE.v0"]["execution_mode"] == "RECURSIVE_RUNTIME"
    assert by_id["REFRAME.METHOD.v0"]["execution_mode"] == "DEVELOPMENT_GATED"
    assert by_id["CROSS.REVIEW.v0"]["execution_mode"] == "EXTERNAL_GATED"
    assert by_id["CROSS.BENCHMARK.v0"]["execution_mode"] == "EXTERNAL_GATED"


def test_context_policy_never_drops_mandatory_material() -> None:
    selection = select_context(
        (
            ContextCandidate("mandatory:evidence", priority=0.0, cost_units=2, mandatory=True),
            ContextCandidate("optional:high", priority=10.0, cost_units=1),
            ContextCandidate("optional:low", priority=1.0, cost_units=1),
        ),
        budget_units=3,
    )
    assert selection.mandatory_preserved is True
    assert selection.selected_ids == ("mandatory:evidence", "optional:high")
    assert selection.omitted_ids == ("optional:low",)

    with pytest.raises(ValueError, match="mandatory context exceeds budget"):
        select_context(
            (ContextCandidate("must-keep", priority=1.0, cost_units=2, mandatory=True),),
            budget_units=1,
        )


def test_review_and_benchmark_are_replayable_non_authorizing_capabilities(tmp_path) -> None:
    workspace = ResearchWorkspace.initialize(tmp_path / "workspace")

    review = request_independent_review(
        workspace,
        review_id="review:1",
        claim_ids=("claim:1",),
        evidence_ids=("evidence:1",),
        review_question="Does the evidence independently support the claim?",
    )
    assert review["status"] == "PENDING_CAPABILITY"
    request = workspace.load_request(review["request_id"])
    assert request.capability == "INDEPENDENT_REVIEW"

    workspace.ingest_result(
        request.request_id,
        success=True,
        output={
            "terminal": "PASS",
            "evidence_ids": ["review-certificate:1"],
            "residual_ids": [],
            "detail": "independent review passed",
            "grants_scientific_authority": False,
        },
        executor="independent-reviewer",
    )
    replay = request_independent_review(
        workspace,
        review_id="review:1",
        claim_ids=("claim:1",),
        evidence_ids=("evidence:1",),
        review_question="Does the evidence independently support the claim?",
    )
    assert replay["status"] == "COMPLETE"
    assert replay["terminal"] == "PASS"
    assert replay["grants_scientific_authority"] is False

    benchmark = request_benchmark(
        workspace,
        benchmark_id="bench:1",
        subject_ids=("subject:a",),
        evaluator_id="eval:v1",
        acceptance_rule="PASS only if the frozen evaluator threshold is met",
    )
    assert benchmark["status"] == "PENDING_CAPABILITY"
    benchmark_request = workspace.load_request(benchmark["request_id"])
    assert benchmark_request.capability == "BENCHMARK_RUN"


def test_external_governance_rejects_authority_escalation(tmp_path) -> None:
    workspace = ResearchWorkspace.initialize(tmp_path / "workspace")
    pending = request_independent_review(
        workspace,
        review_id="review:authority-hostile",
        claim_ids=("claim:1",),
        evidence_ids=("evidence:1",),
        review_question="hostile authority test",
    )
    workspace.ingest_result(
        pending["request_id"],
        success=True,
        output={
            "terminal": "PASS",
            "evidence_ids": ["forged:certificate"],
            "residual_ids": [],
            "detail": "forged authority",
            "grants_scientific_authority": True,
        },
        executor="hostile-reviewer",
    )
    with pytest.raises(
        ValueError,
        match="authority escalation|authority fields, when present, must be literal false",
    ):
        request_independent_review(
            workspace,
            review_id="review:authority-hostile",
            claim_ids=("claim:1",),
            evidence_ids=("evidence:1",),
            review_question="hostile authority test",
        )


def test_recursive_decomposition_receives_mechanical_and_fibre_context() -> None:
    captured = []

    def provider(request):
        captured.append(request)
        return json.dumps(
            {
                "atoms": [],
                "stop_reason": "IRREDUCIBLE_AT_CURRENT_RESOLUTION",
                "rationale": "bounded test stop",
            }
        )

    reasoner = RecursiveLLMResearchReasoner(
        CallableLLMProvider(provider, model_id="recursive-context-test")
    )
    residual = Residual(
        residual_id="residual:method",
        kind=ResidualKind.METHOD_GAP,
        description="The current method language cannot separate the surviving alternatives.",
        candidate_responsibilities=(Responsibility.METHOD,),
    )
    state = OrionState(
        knowledge=KnowledgeState(residuals=(residual,)),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
    )
    decomposition = reasoner.decompose_residual(
        residual,
        Problem("problem:1", "Resolve the method residual"),
        state,
    )
    assert decomposition.stop_reason is not None
    assert len(captured) == 1
    payload = json.loads(captured[0].user)
    assert payload["mechanical_questions"]
    fibre_ids = {
        row["mechanic_id"] for row in payload["development_fibre_context"]
    }
    assert "DIAGNOSE.EXPERIENCE_RETRIEVAL.v0" in fibre_ids
    assert "DIAGNOSE.DISCRIMINATOR.v0" in fibre_ids
    assert "REOPEN.FIBRE.v0" in fibre_ids
    assert "REFRAME.METHOD.v0" in fibre_ids
