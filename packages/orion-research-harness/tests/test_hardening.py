from __future__ import annotations

import json
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from orion.core.search import RetrievedItem, SearchQuery, SearchRouteKind
from orion.providers.llm.base import LLMRequest
from orion_research_harness.broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from orion_research_harness.cli import main as cli_main
from orion_research_harness.local_tools import execute_local
from orion_research_harness.protocol import CapabilityRequest
from orion_research_harness.runner import run_problem
from orion_research_harness.workspace import ResearchWorkspace


def test_concurrent_workspace_initialization_converges_to_one_session(tmp_path: Path):
    root = tmp_path / "ws"
    workers = 16
    barrier = threading.Barrier(workers)

    def initialize(_: int) -> str:
        barrier.wait()
        return ResearchWorkspace.initialize(root, project_root=tmp_path).session_id

    with ThreadPoolExecutor(max_workers=workers) as pool:
        session_ids = list(pool.map(initialize, range(workers)))

    assert len(set(session_ids)) == 1
    assert ResearchWorkspace.load(root).session_id == session_ids[0]
    json.loads((root / ".orion-harness" / "session.json").read_text())


def test_concurrent_deterministic_request_creation_is_atomic(tmp_path: Path):
    root = tmp_path / "ws"
    ResearchWorkspace.initialize(root, project_root=tmp_path)
    workers = 16
    barrier = threading.Barrier(workers)

    def create(_: int) -> tuple[str, str]:
        workspace = ResearchWorkspace.load(root)
        barrier.wait()
        request = workspace.get_or_create_request(
            capability="WEB_SEARCH",
            payload={"query": "same deterministic payload", "limit": 4},
        )
        return request.request_id, request.request_digest

    with ThreadPoolExecutor(max_workers=workers) as pool:
        identities = list(pool.map(create, range(workers)))

    assert len(set(identities)) == 1
    request_files = list((root / ".orion-harness" / "requests").glob("*.json"))
    assert len(request_files) == 1
    CapabilityRequest.from_dict(json.loads(request_files[0].read_text()))


def test_concurrent_conflicting_results_have_exactly_one_winner(tmp_path: Path):
    root = tmp_path / "ws"
    workspace = ResearchWorkspace.initialize(root, project_root=tmp_path)
    request = workspace.get_or_create_request(capability="CUSTOM", payload={"x": 1})
    workers = 16
    barrier = threading.Barrier(workers)

    def ingest(index: int) -> tuple[str, int]:
        local = ResearchWorkspace.load(root)
        barrier.wait()
        try:
            local.ingest_result(
                request.request_id,
                success=True,
                output={"winner": index},
                executor="race-host",
            )
        except ValueError:
            return "rejected", index
        return "accepted", index

    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(ingest, range(workers)))

    accepted = [index for status, index in outcomes if status == "accepted"]
    assert len(accepted) == 1
    persisted = workspace.load_result(request.request_id)
    assert persisted is not None
    assert persisted.output == {"winner": accepted[0]}
    result_files = list((root / ".orion-harness" / "results").glob("*.json"))
    assert len(result_files) == 1
    json.loads(result_files[0].read_text())


def test_concurrent_identical_result_ingest_is_idempotent(tmp_path: Path):
    root = tmp_path / "ws"
    workspace = ResearchWorkspace.initialize(root, project_root=tmp_path)
    request = workspace.get_or_create_request(capability="CUSTOM", payload={"x": 1})
    workers = 16
    barrier = threading.Barrier(workers)

    def ingest(_: int) -> str:
        local = ResearchWorkspace.load(root)
        barrier.wait()
        result = local.ingest_result(
            request.request_id,
            success=True,
            output={"same": True},
            executor="same-host",
        )
        return result.result_digest

    with ThreadPoolExecutor(max_workers=workers) as pool:
        digests = list(pool.map(ingest, range(workers)))

    assert len(set(digests)) == 1
    assert workspace.load_result(request.request_id).result_digest == digests[0]


def test_result_executor_identity_is_immutable(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    request = workspace.get_or_create_request(capability="CUSTOM", payload={"x": 1})
    workspace.ingest_result(
        request.request_id,
        success=True,
        output={"ok": True},
        executor="host-a",
    )
    with pytest.raises(ValueError, match="different content or executor"):
        workspace.ingest_result(
            request.request_id,
            success=True,
            output={"ok": True},
            executor="host-b",
        )


def test_malformed_successful_llm_receipt_is_host_failure_not_scientific_evidence(
    tmp_path: Path,
):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    problem = {
        "problem_id": "malformed-host",
        "question": "What can be concluded?",
        "scope": "Do not learn from malformed orchestration data.",
        "initial_domain_ids": ["science"],
        "success_criteria": ["Fail outside scientific evidence."],
    }
    pending = run_problem(workspace, problem, max_iterations=1)
    request = CapabilityRequest.from_dict(pending["request"])
    assert request.capability == "LLM_COMPLETE"
    workspace.ingest_result(
        request.request_id,
        success=True,
        output={},
        executor="malformed-host",
    )

    outcome = run_problem(workspace, problem, max_iterations=1)
    assert outcome["status"] == "HOST_CAPABILITY_FAILED"
    assert outcome["result"]["success"] is True
    assert "invalid host result" in outcome["error"]
    assert not workspace.run_ids()


def test_malformed_web_receipt_escapes_as_host_failure(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    broker = CapabilityBroker(workspace)
    retrieval = BrokerRetrievalProvider(broker)
    query = SearchQuery(
        query_id="q1",
        text="query",
        route_id="r1",
        route_kind=SearchRouteKind.FRESHNESS,
        domain_hint="science",
    )
    with pytest.raises(HostCapabilityRequired) as pending:
        retrieval.search(query, limit=1)
    workspace.ingest_result(
        pending.value.request.request_id,
        success=True,
        output={"items": [{"content": "grounded", "source_uri": ""}]},
        executor="bad-web",
    )
    with pytest.raises(HostCapabilityFailed, match="invalid host result"):
        retrieval.search(query, limit=1)


def test_verification_pass_requires_real_certificate_and_boolean(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    broker = CapabilityBroker(workspace)
    verification = BrokerVerificationProvider(broker)
    item = RetrievedItem(
        item_id="e1",
        content="source text",
        source_uri="https://example.org/source",
        domain_ids=("science",),
    )

    with pytest.raises(HostCapabilityRequired) as pending:
        verification.verify({"contribution_id": "c1"}, item)
    workspace.ingest_result(
        pending.value.request.request_id,
        success=True,
        output={"passed": True, "certificate_ids": [], "reason": "claimed pass"},
        executor="bad-verifier",
    )
    with pytest.raises(HostCapabilityFailed, match="requires a certificate_id"):
        verification.verify({"contribution_id": "c1"}, item)


def test_llm_contract_rejects_non_string_content(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    llm = BrokerLLMProvider(CapabilityBroker(workspace))
    request = LLMRequest(
        task="compose_answer",
        system="system",
        user="{}",
        response_schema='{"answer":"..."}',
    )
    with pytest.raises(HostCapabilityRequired) as pending:
        llm.complete(request)
    workspace.ingest_result(
        pending.value.request.request_id,
        success=True,
        output={"content": {"answer": "not serialized"}},
        executor="bad-llm",
    )
    with pytest.raises(HostCapabilityFailed, match="content must be a string"):
        llm.complete(request)


def test_file_reads_and_process_output_are_bounded_before_return(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    workspace = ResearchWorkspace.initialize(project / "ws", project_root=project)
    (project / "large.txt").write_text("x" * 5000)

    read = execute_local(
        workspace,
        "FILE_READ",
        {"path": "large.txt", "max_chars": 50},
    )
    assert read["content"].startswith("x" * 50)
    assert "truncated" in read["content"]
    with pytest.raises(ValueError, match="max_chars"):
        execute_local(workspace, "FILE_READ", {"path": "large.txt", "max_chars": 0})

    with pytest.raises(PermissionError):
        execute_local(workspace, "PYTHON", {"code": "print('no opt in')"})

    process_workspace = ResearchWorkspace.initialize(
        project / "proc-ws",
        project_root=project,
        allow_process_tools=True,
    )
    result = execute_local(
        process_workspace,
        "PYTHON",
        {"code": "import sys; sys.stdout.write('z' * 150000)"},
    )
    assert result["returncode"] == 0
    assert result["sandboxed"] is False
    assert len(result["stdout"]) < 101000
    assert "truncated 50000 bytes" in result["stdout"]


def test_local_process_timeout_is_fail_closed(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    workspace = ResearchWorkspace.initialize(
        project / "ws",
        project_root=project,
        allow_process_tools=True,
    )
    with pytest.raises(subprocess.TimeoutExpired):
        execute_local(
            workspace,
            "PYTHON",
            {"code": "import time; time.sleep(2)", "timeout": 1},
        )


def test_cli_returns_nonzero_for_host_and_local_capability_failures(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    workspace.save_problem(problem_id="p1", question="Test problem")

    # Legacy single-pass flow: seed via run_problem, whose request identity the
    # --single-pass CLI path replays.
    pending = run_problem(workspace, workspace.load_problem("p1"), max_iterations=1)
    request = CapabilityRequest.from_dict(pending["request"])
    workspace.ingest_result(
        request.request_id,
        success=False,
        error="host unavailable",
        executor="host",
    )
    assert (
        cli_main(
            [
                "solve",
                str(workspace.root),
                "p1",
                "--max-iterations",
                "1",
                "--single-pass",
            ]
        )
        == 3
    )
    capsys.readouterr()

    # Default recursive flow: its first request identity differs from the
    # single-pass one, so seed the failure through the CLI's own pending request.
    assert cli_main(["solve", str(workspace.root), "p1", "--max-iterations", "1"]) == 2
    capsys.readouterr()
    recursive_request = next(
        item
        for item in workspace.pending_requests()
        if item.request_id != request.request_id
    )
    workspace.ingest_result(
        recursive_request.request_id,
        success=False,
        error="host unavailable",
        executor="host",
    )
    assert cli_main(["solve", str(workspace.root), "p1", "--max-iterations", "1"]) == 3
    capsys.readouterr()

    local_request = workspace.get_or_create_request(
        capability="FILE_READ",
        payload={"path": "../outside.txt"},
    )
    assert cli_main(["service-local", str(workspace.root), local_request.request_id]) == 3
    output = json.loads(capsys.readouterr().out)
    assert output["serviced"][0]["success"] is False
