from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

import orion_research_harness.local_tools as local_tools
from orion_research_harness.workspace import ResearchWorkspace


def test_file_list_fails_closed_when_directory_exceeds_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    project = tmp_path / "project"
    project.mkdir()
    for index in range(4):
        (project / f"f{index}.txt").write_text("x")
    workspace = ResearchWorkspace.initialize(project / "ws", project_root=project)
    monkeypatch.setattr(local_tools, "_MAX_LIST_ENTRIES", 3)
    with pytest.raises(OverflowError, match="narrow the listing scope"):
        local_tools.execute_local(workspace, "FILE_LIST", {"path": "."})


def test_descendant_holding_output_pipe_cannot_hang_completed_process(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    workspace = ResearchWorkspace.initialize(
        project / "ws",
        project_root=project,
        allow_process_tools=True,
    )
    code = (
        "import subprocess,sys; "
        "subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)']); "
        "print('parent-complete')"
    )
    started = time.monotonic()
    result = local_tools.execute_local(
        workspace,
        "PYTHON",
        {"code": code, "timeout": 5},
    )
    elapsed = time.monotonic() - started
    assert result["returncode"] == 0
    assert "parent-complete" in result["stdout"]
    assert elapsed < 5


def test_shell_uses_argv_without_shell_interpolation(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    workspace = ResearchWorkspace.initialize(
        project / "ws",
        project_root=project,
        allow_process_tools=True,
    )
    result = local_tools.execute_local(
        workspace,
        "SHELL",
        {"argv": [sys.executable, "-c", "import sys; print(sys.argv[1])", "$(echo injected)"]},
    )
    assert result["returncode"] == 0
    assert result["stdout"].strip() == "$(echo injected)"


def test_process_timeout_clamp_admits_long_research_runs(tmp_path: Path):
    """The process timeout clamp is a resource guard, not an evidence gate.

    Lanes legitimately request runs far longer than a minute (the QG-3 stage-1
    scan is ~20 minutes). The clamp silently rewrites an over-long request
    rather than refusing it, so a lane that asks for more than the cap gets a
    shorter run than it believes it asked for. Pin the bound so it cannot drift
    back below what real lanes need without a failing test.
    """
    assert local_tools._MAX_PROCESS_TIMEOUT_SECONDS >= 1_500

    project = tmp_path / "project"
    project.mkdir()
    workspace = ResearchWorkspace.initialize(
        project / "ws",
        project_root=project,
        allow_process_tools=True,
    )
    observed: list[float | None] = []
    real_popen = local_tools.subprocess.Popen

    class _Recording(real_popen):  # type: ignore[misc, valid-type]
        def wait(self, timeout=None):  # type: ignore[override]
            observed.append(timeout)
            return super().wait(timeout=timeout)

    local_tools.subprocess.Popen = _Recording
    try:
        result = local_tools.execute_local(
            workspace,
            "PYTHON",
            {"code": "print('ok')", "timeout": 1_500},
        )
    finally:
        local_tools.subprocess.Popen = real_popen

    assert result["returncode"] == 0
    assert observed and observed[0] == 1_500, (
        "a 1500s request must reach process.wait intact; a lower clamp would "
        f"silently truncate long lane runs (saw {observed})"
    )


def test_local_capability_rejects_unsupported_payload_keys(tmp_path: Path):
    """An unread payload key must fail closed, not be silently discarded.

    The request digest covers the whole payload, so a key the executor ignores
    still changes the request identity while changing nothing about what runs.
    Found live: FILE_LIST accepted `limit: 3` and returned the whole directory,
    leaving a receipt that looked valid and replayed exactly while attesting to
    a constraint that was never applied.
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.txt").write_text("a")
    (project / "b.txt").write_text("b")
    workspace = ResearchWorkspace.initialize(project / "ws", project_root=project)

    with pytest.raises(ValueError, match="unsupported key"):
        local_tools.execute_local(
            workspace,
            "FILE_LIST",
            {"path": ".", "limit": 1},
        )

    # The supported vocabulary still works untouched.
    result = local_tools.execute_local(workspace, "FILE_LIST", {"path": "."})
    assert "a.txt" in result["entries"]


def test_payload_vocabulary_matches_what_the_executor_reads(tmp_path: Path):
    """Every declared key must be one the executor actually honors.

    Guards the reverse drift: a key added to the vocabulary but never read
    would re-open exactly the silent-ignore hole this validation closes.
    """
    import inspect
    import re

    source = inspect.getsource(local_tools.execute_local)
    read_keys = set(re.findall(r'payload\[\s*"([a-z_]+)"\s*\]', source))
    read_keys |= set(re.findall(r'payload\.get\(\s*"([a-z_]+)"', source))

    declared: set[str] = set()
    for keys in local_tools._CAPABILITY_PAYLOAD_KEYS.values():
        declared |= set(keys)

    assert declared == read_keys, (
        f"declared-but-unread: {sorted(declared - read_keys)}; "
        f"read-but-undeclared: {sorted(read_keys - declared)}"
    )
