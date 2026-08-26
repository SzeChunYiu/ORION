"""The runner must refuse to hand back a run that skipped a required operator.

`run_problem` already reported `operator_coverage`; reporting is not refusing. The
P1-U R6 campaign scored 48 rows whose runs never reached `DIAGNOSE`, and nothing in
the path it went through said so. These tests pin the guard that does.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from orion_research_harness.operator_coverage import OperatorNotExercised
from orion_research_harness.protocol import CapabilityRequest
from orion_research_harness.runner import run_problem
from orion_research_harness.workspace import ResearchWorkspace

SMOKE_CONTENT = {
    "plan_search": (
        '{"queries":[{"query_id":"q:fixture","text":"fixture query",'
        '"route_id":"route:fixture","route_kind":"PARENT_DISCIPLINE",'
        '"domain_hint":null}]}'
    ),
    "reconstruct": '{"summary":"No verified evidence yet."}',
    "diagnose": '{"responsibilities":["EVIDENCE"],"rationale":"Evidence is missing."}',
    "propose_reframe": '{"add_domain_ids":[],"add_representation_ids":[],"note":"No rewrite."}',
    "compose_answer": '{"answer":"No verified answer."}',
}

PROBLEM = {
    "problem_id": "operator-requirement",
    "question": "What can be concluded?",
    "scope": "No evidence has been acquired.",
    "initial_domain_ids": ["science"],
    "success_criteria": ["Preserve uncertainty."],
}


def _service(workspace: ResearchWorkspace, request: CapabilityRequest) -> None:
    if request.capability == "WEB_SEARCH":
        workspace.ingest_result(
            request.request_id,
            success=True,
            output={"items": []},
            executor="scripted-smoke",
        )
        return
    task = request.payload["task"]
    if task not in SMOKE_CONTENT:
        raise AssertionError(f"unexpected task {task}")
    workspace.ingest_result(
        request.request_id,
        success=True,
        output={"content": SMOKE_CONTENT[task], "model_id": "scripted-smoke"},
        executor="scripted-smoke",
    )


def _run(workspace: ResearchWorkspace, **kwargs) -> dict:
    for _ in range(8):
        outcome = run_problem(workspace, PROBLEM, max_iterations=1, **kwargs)
        if outcome["status"] == "COMPLETE":
            return outcome
        _service(workspace, CapabilityRequest.from_dict(outcome["request"]))
    raise AssertionError("scripted host did not terminate within the replay budget")


def test_required_operator_that_ran_is_returned_with_its_coverage(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    outcome = _run(workspace, require_operators={"DIAGNOSE"})
    assert outcome["status"] == "COMPLETE"
    assert "DIAGNOSE" in outcome["operator_coverage"]["executed"]


def test_required_operator_that_never_ran_raises_and_names_it(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    # Nothing invalidates a claim in this world, so REOPEN cannot fire. An
    # experiment that depended on it must be told, not handed a scoreable row.
    with pytest.raises(OperatorNotExercised) as raised:
        _run(workspace, require_operators={"REOPEN"})
    message = str(raised.value)
    assert "REOPEN" in message
    assert "operator-requirement" in message


def test_omitting_the_requirement_leaves_behaviour_unchanged(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    outcome = _run(workspace)
    assert outcome["status"] == "COMPLETE"
    assert outcome["operator_coverage"]["schema"] == "ORION.HarnessRunOperatorCoverage.v1"
