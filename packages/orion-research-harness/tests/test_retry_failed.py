import json
from pathlib import Path

import pytest

from orion_research_harness.cli import main as cli_main
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace


def _failed_read_request(workspace: ResearchWorkspace):
    request = workspace.get_or_create_request(
        capability="FILE_READ",
        payload={"path": "missing/probe.txt"},
    )
    result = service_local_request(workspace, request.request_id)
    assert result.success is False
    return request


def test_archive_failed_result_frees_identity_for_retry(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    request = _failed_read_request(workspace)
    assert workspace.pending_requests() == ()

    archived_to = workspace.archive_failed_result(request.request_id)
    assert archived_to.exists()
    archived = json.loads(archived_to.read_text())
    assert archived["success"] is False
    assert archived["request_id"] == request.request_id

    # The identity is pending again; after the environment is repaired the
    # same deterministic request can be serviced successfully.
    assert [item.request_id for item in workspace.pending_requests()] == [
        request.request_id
    ]
    (tmp_path / "missing").mkdir()
    (tmp_path / "missing" / "probe.txt").write_text("recovered")
    retried = service_local_request(workspace, request.request_id)
    assert retried.success is True
    assert workspace.load_result(request.request_id).success is True


def test_archive_failed_result_rejects_successful_receipts(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    (tmp_path / "ok.txt").write_text("fine")
    request = workspace.get_or_create_request(
        capability="FILE_READ",
        payload={"path": "ok.txt"},
    )
    result = service_local_request(workspace, request.request_id)
    assert result.success is True
    with pytest.raises(ValueError, match="only failed results"):
        workspace.archive_failed_result(request.request_id)
    with pytest.raises(FileNotFoundError):
        workspace.archive_failed_result(
            workspace.get_or_create_request(
                capability="FILE_READ", payload={"path": "never-serviced.txt"}
            ).request_id
        )


def test_archive_failed_result_keeps_every_failed_attempt(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    request = _failed_read_request(workspace)
    first = workspace.archive_failed_result(request.request_id)
    second_result = service_local_request(workspace, request.request_id)
    assert second_result.success is False
    second = workspace.archive_failed_result(request.request_id)
    assert first != second
    assert first.exists() and second.exists()


def test_cli_retry_failed_archives_all_failed_results(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    request = _failed_read_request(workspace)
    assert cli_main(["retry-failed", str(workspace.root)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "ORION.ResearchHarnessRetryFailed.v1"
    assert [item["request_id"] for item in payload["archived"]] == [request.request_id]
    assert workspace.load_result(request.request_id) is None
