"""The workflow resolver must find archived workflows and still fail on absent ones.

Commit `401df9d9b` moved 391 one-shot workflows into `.github/archived-workflows/`
and broke 29 tests that read a workflow as text from the live directory. The
resolver exists so that move is invisible to a test that only wants the file's
contents. These tests pin the two things that would make it worse than the
hard-coded paths it replaces: silently returning a path for a workflow that has
actually been deleted, and a scan that quietly covers only one of the two
directories.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from orion.programme.workflow_locations import (
    ARCHIVED_WORKFLOW_DIR,
    LIVE_WORKFLOW_DIR,
    workflow_files,
    workflow_path,
    workflow_repo_path,
)


def _tree(root: Path, live: tuple[str, ...], archived: tuple[str, ...]) -> Path:
    for directory, names in ((root / ".github" / "workflows", live),
                             (root / ".github" / "archived-workflows", archived)):
        directory.mkdir(parents=True, exist_ok=True)
        for name in names:
            (directory / name).write_text(f"name: {name}\n")
    return root


def test_a_live_workflow_resolves(tmp_path: Path) -> None:
    root = _tree(tmp_path, ("ci.yml",), ())
    assert workflow_path("ci.yml", root=root) == root / ".github/workflows/ci.yml"


def test_an_archived_workflow_resolves(tmp_path: Path) -> None:
    """The regression the resolver exists for."""
    root = _tree(tmp_path, (), ("orion-foundations-v3.yml",))
    resolved = workflow_path("orion-foundations-v3.yml", root=root)
    assert resolved == root / ".github/archived-workflows/orion-foundations-v3.yml"
    assert resolved.is_file()


def test_live_wins_a_name_clash(tmp_path: Path) -> None:
    root = _tree(tmp_path, ("ci.yml",), ("ci.yml",))
    assert workflow_path("ci.yml", root=root).parent.name == "workflows"


def test_an_absent_workflow_still_raises(tmp_path: Path) -> None:
    """Fail loudly: a deleted workflow must not resolve to anything."""
    root = _tree(tmp_path, ("ci.yml",), ("old.yml",))
    with pytest.raises(FileNotFoundError) as excinfo:
        workflow_path("never-existed.yml", root=root)
    message = str(excinfo.value)
    assert "workflows" in message and "archived-workflows" in message, (
        "the error must name both directories, or it does not say where it looked"
    )


def test_repo_path_is_relative_and_posix(tmp_path: Path) -> None:
    """This is the form `git rev-parse HEAD:<path>` needs."""
    root = _tree(tmp_path, (), ("p5_phase2_live_execution.yml",))
    assert workflow_repo_path("p5_phase2_live_execution.yml", root=root) == (
        ".github/archived-workflows/p5_phase2_live_execution.yml"
    )


def test_the_scan_covers_both_directories(tmp_path: Path) -> None:
    """A scan restricted to the live directory is what silently emptied one guard."""
    root = _tree(tmp_path, ("ci.yml",), ("a.yml", "b.yaml", "notes.md"))
    names = [p.name for p in workflow_files(root=root)]
    assert names == ["a.yml", "b.yaml", "ci.yml"], names


def test_the_live_tree_is_findable_through_the_resolver() -> None:
    """Control: against the real repository, not a fixture.

    If these lookups return nothing the guards above are testing a toy tree
    only, and the resolver could be wrong about this repository's real layout.
    """
    assert LIVE_WORKFLOW_DIR.is_dir(), LIVE_WORKFLOW_DIR
    found = workflow_files()
    assert len(found) > len(list(LIVE_WORKFLOW_DIR.glob("*.y*ml"))), (
        "the scan must see more than the live directory; if it does not, either "
        "the archive is gone or the resolver is only reading one directory"
    )
    if ARCHIVED_WORKFLOW_DIR.is_dir():
        assert any(p.parent == ARCHIVED_WORKFLOW_DIR for p in found)
