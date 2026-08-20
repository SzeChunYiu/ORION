from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion_research_harness.workspace import ResearchWorkspace


def test_new_session_is_digest_bound_and_tamper_evident(tmp_path: Path):
    root = tmp_path / "ws"
    workspace = ResearchWorkspace.initialize(root, project_root=tmp_path)
    session_path = root / ".orion-harness" / "session.json"
    raw = json.loads(session_path.read_text())
    assert raw["schema"] == "ORION.ResearchHarnessSession.v2"
    assert isinstance(raw["session_digest"], str)
    assert len(raw["session_digest"]) == 64
    assert workspace.allow_process_tools is False

    raw["allow_process_tools"] = True
    session_path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="session digest mismatch"):
        ResearchWorkspace.load(root)


def test_session_boolean_is_never_truthy_string_coerced(tmp_path: Path):
    root = tmp_path / "ws"
    ResearchWorkspace.initialize(root, project_root=tmp_path)
    session_path = root / ".orion-harness" / "session.json"
    raw = json.loads(session_path.read_text())
    raw["allow_process_tools"] = "false"
    session_path.write_text(json.dumps(raw))
    with pytest.raises(TypeError, match="allow_process_tools must be a boolean"):
        ResearchWorkspace.load(root)


def test_valid_legacy_v1_session_remains_readable(tmp_path: Path):
    root = tmp_path / "legacy"
    meta = root / ".orion-harness"
    for child in ("requests", "results", "problems", "runs", "notes"):
        (meta / child).mkdir(parents=True, exist_ok=True)
    (meta / "session.json").write_text(
        json.dumps(
            {
                "schema": "ORION.ResearchHarnessSession.v1",
                "session_id": "session:legacy",
                "project_root": str(tmp_path),
                "created_at": "2026-08-20T00:00:00+00:00",
                "allow_process_tools": False,
            }
        )
    )
    workspace = ResearchWorkspace.load(root)
    assert workspace.session_id == "session:legacy"
    assert workspace.allow_process_tools is False


def test_initialize_rejects_non_boolean_process_opt_in(tmp_path: Path):
    with pytest.raises(TypeError, match="allow_process_tools must be a boolean"):
        ResearchWorkspace.initialize(
            tmp_path / "ws",
            project_root=tmp_path,
            allow_process_tools="false",  # type: ignore[arg-type]
        )
