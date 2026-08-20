from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion_research_harness.broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    CapabilityBroker,
    HostCapabilityRequired,
)
from orion_research_harness.local_tools import execute_local
from orion_research_harness.protocol import CapabilityRequest, CapabilityResult
from orion_research_harness.runner import run_problem
from orion_research_harness.workspace import ResearchWorkspace
from orion.core.search import SearchQuery, SearchRouteKind
from orion.providers.llm.base import LLMRequest


def test_request_result_receipts_are_bound_and_tamper_evident(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    request = workspace.get_or_create_request(
        capability="WEB_SEARCH",
        payload={"query": "orion research"},
    )
    same = workspace.get_or_create_request(
        capability="WEB_SEARCH",
        payload={"query": "orion research"},
    )
    assert same.request_id == request.request_id

    result = workspace.ingest_result(
        request.request_id,
        success=True,
        output={"items": []},
        executor="test-host",
    )
    result.validate(request)

    raw = result.as_dict()
    raw["output"] = {"items": [{"content": "tampered"}]}
    with pytest.raises(ValueError, match="digest mismatch"):
        CapabilityResult.from_dict(raw)


def test_workspace_problem_persistence_and_path_confined_local_tools(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    workspace = ResearchWorkspace.initialize(project / ".research", project_root=project)
    workspace.save_problem(
        problem_id="p1",
        question="Test P1",
        initial_domain_ids=("science",),
    )
    assert workspace.load_problem("p1")["question"] == "Test P1"

    write = execute_local(
        workspace,
        "FILE_WRITE",
        {"path": "notes/test.txt", "content": "hello"},
    )
    assert write["bytes_written"] == 5
    read = execute_local(workspace, "FILE_READ", {"path": "notes/test.txt"})
    assert read["content"] == "hello"

    with pytest.raises(PermissionError):
        execute_local(workspace, "FILE_READ", {"path": "../outside.txt"})


def test_broker_llm_and_web_requests_replay_ingested_results(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    broker = CapabilityBroker(workspace)
    llm = BrokerLLMProvider(broker)

    request = LLMRequest(
        task="reconstruct",
        system="system",
        user='{"x":1}',
        response_schema='{"summary":"..."}',
    )
    with pytest.raises(HostCapabilityRequired) as pending:
        llm.complete(request)
    workspace.ingest_result(
        pending.value.request.request_id,
        success=True,
        output={"content": '{"summary":"ok"}', "model_id": "test-model"},
        executor="test",
    )
    response = llm.complete(request)
    assert json.loads(response.content)["summary"] == "ok"
    assert response.model_id == "test-model"

    retrieval = BrokerRetrievalProvider(broker)
    query = SearchQuery(
        query_id="q1",
        text="query",
        route_id="r1",
        route_kind=SearchRouteKind.FRESHNESS,
        domain_hint="science",
    )
    with pytest.raises(HostCapabilityRequired) as web_pending:
        retrieval.search(query, limit=2)
    workspace.ingest_result(
        web_pending.value.request.request_id,
        success=True,
        output={
            "items": [
                {
                    "item_id": "web:1",
                    "content": "grounded",
                    "source_uri": "https://example.org",
                    "domain_ids": ["science"],
                }
            ]
        },
        executor="test-web",
    )
    items = retrieval.search(query, limit=2)
    assert items[0].item_id == "web:1"
    assert items[0].source_uri == "https://example.org"


def _service_smoke_llm(workspace: ResearchWorkspace, request: CapabilityRequest) -> None:
    payload = request.payload
    task = payload["task"]
    if task == "plan_search":
        content = '{"queries":[]}'
    elif task == "reconstruct":
        content = '{"summary":"No verified evidence yet."}'
    elif task == "diagnose":
        content = '{"responsibilities":["EVIDENCE"],"rationale":"Evidence is missing."}'
    elif task == "propose_reframe":
        content = '{"add_domain_ids":[],"add_representation_ids":[],"note":"No rewrite."}'
    elif task == "compose_answer":
        content = '{"answer":"No verified answer."}'
    else:
        raise AssertionError(f"unexpected task {task}")
    workspace.ingest_result(
        request.request_id,
        success=True,
        output={"content": content, "model_id": "scripted-smoke"},
        executor="scripted-smoke",
    )


def test_host_execution_failure_is_not_scientific_failure_evidence(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    problem = {
        "problem_id": "host-failure",
        "question": "What can be concluded?",
        "scope": "Host execution may fail.",
        "initial_domain_ids": ["science"],
        "success_criteria": ["Do not convert orchestration failure into scientific evidence."],
    }

    pending = run_problem(workspace, problem, max_iterations=1)
    assert pending["status"] == "PENDING_CAPABILITY"
    request = CapabilityRequest.from_dict(pending["request"])
    workspace.ingest_result(
        request.request_id,
        success=False,
        error="external host unavailable",
        executor="test-host",
    )

    outcome = run_problem(workspace, problem, max_iterations=1)
    assert outcome["status"] == "HOST_CAPABILITY_FAILED"
    assert outcome["request"]["request_id"] == request.request_id
    assert outcome["result"]["success"] is False
    assert not workspace.run_ids()


def test_canonical_orion_runtime_can_be_replayed_across_pending_host_requests(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    problem = {
        "problem_id": "smoke",
        "question": "What can be concluded?",
        "scope": "No evidence has been acquired.",
        "initial_domain_ids": ["science"],
        "success_criteria": ["Preserve uncertainty."],
    }

    for _ in range(8):
        outcome = run_problem(workspace, problem, max_iterations=1)
        if outcome["status"] == "COMPLETE":
            break
        request = CapabilityRequest.from_dict(outcome["request"])
        assert request.capability == "LLM_COMPLETE"
        _service_smoke_llm(workspace, request)
    else:
        raise AssertionError("canonical ORION did not terminate within smoke replay budget")

    assert outcome["status"] == "COMPLETE"
    assert outcome["solution_status"] in {"BLOCKED", "CANNOT_CHECK"}
    assert "FRAME" in outcome["operator_sequence"]
    assert "SEARCH" in outcome["operator_sequence"]
    assert workspace.run_ids()
