"""Regression tests for defects D2/D3 found during live dual-harness use.

D2: a successful LLM receipt whose content violates the task schema (e.g. an
invalid enum value in decompose_problem) crashed the recursive CLI with a raw
traceback instead of the documented HOST_CAPABILITY_FAILED exit-3 contract.

D3: such a successful-but-malformed receipt permanently pinned its
deterministic request identity — `retry-failed` refuses successful receipts,
and tamper rejection refuses a corrected re-ingest — leaving the workspace
unrecoverable.
"""

import json
from pathlib import Path

import pytest

from orion_research_harness.cli import main as cli_main
from orion_research_harness.workspace import ResearchWorkspace


def _seed_malformed_decompose(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> tuple[ResearchWorkspace, str]:
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    workspace.save_problem(problem_id="p1", question="Test problem")
    assert cli_main(["solve", str(workspace.root), "p1", "--max-iterations", "1"]) == 2
    capsys.readouterr()
    request = workspace.pending_requests()[0]
    content = json.dumps(
        {"atoms": [], "stop_reason": "NOT_A_VALID_STOP_REASON", "rationale": "x"}
    )
    workspace.ingest_result(
        request.request_id,
        success=True,
        output={"content": content, "model_id": "test"},
        executor="host",
    )
    return workspace, request.request_id


def test_malformed_successful_receipt_maps_to_host_capability_failed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    workspace, _ = _seed_malformed_decompose(tmp_path, capsys)
    exit_code = cli_main(["solve", str(workspace.root), "p1", "--max-iterations", "1"])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 3
    assert output["status"] == "HOST_CAPABILITY_FAILED"
    assert "reasoner content invalid" in output["error"]


def test_invalid_content_archive_frees_identity_for_corrected_receipt(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    workspace, request_id = _seed_malformed_decompose(tmp_path, capsys)

    # Plain retry-failed must keep refusing successful receipts.
    with pytest.raises(ValueError, match="only failed results"):
        workspace.archive_failed_result(request_id)

    # The explicit override requires a reason and preserves the audit trail.
    with pytest.raises(ValueError, match="non-empty reason"):
        workspace.archive_invalid_result(request_id, reason="   ")
    assert (
        cli_main(
            [
                "retry-failed",
                str(workspace.root),
                request_id,
                "--invalid-content",
                "--reason",
                "stop_reason not a valid RecursiveProblemStopReason",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    archived_to = Path(payload["archived"][0]["archived_to"])
    assert archived_to.exists()
    assert archived_to.with_suffix(".reason.txt").read_text().strip()
    assert json.loads(archived_to.read_text())["success"] is True

    # The identity is pending again and accepts a corrected receipt.
    assert [item.request_id for item in workspace.pending_requests()] == [request_id]
    corrected = json.dumps(
        {
            "atoms": [],
            "stop_reason": "NO_DECISION_SEPARATING_DECOMPOSITION",
            "rationale": "corrected",
        }
    )
    workspace.ingest_result(
        request_id,
        success=True,
        output={"content": corrected, "model_id": "test"},
        executor="host",
    )
    exit_code = cli_main(["solve", str(workspace.root), "p1", "--max-iterations", "1"])
    output = json.loads(capsys.readouterr().out)
    assert exit_code != 3 or output["status"] != "HOST_CAPABILITY_FAILED"


def test_invalid_content_requires_explicit_request_id(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    with pytest.raises(SystemExit, match="requires an explicit request_id"):
        cli_main(["retry-failed", str(workspace.root), "--invalid-content"])
