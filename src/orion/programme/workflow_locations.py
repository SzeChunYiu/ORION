"""Resolve a GitHub Actions workflow file by name, live directory or archive.

The repository once kept every workflow in ``.github/workflows/``. It now keeps
seven live ones there and 391 one-shot ones in ``.github/archived-workflows/``,
where they remain readable but never fire.

A test that reads a workflow as text to pin its behaviour does not care which
directory holds it: the file is the record either way, and moving it changes
nothing the test is asserting about. Eleven such tests nevertheless broke on the
move, because each hard-coded ``.github/workflows`` and raised
``FileNotFoundError`` the moment the file was no longer there.

This module is the one place that knows about both directories. It resolves by
file name, preferring a live workflow over an archived one of the same name, and
it raises rather than returning a missing path -- a workflow that has genuinely
been deleted must still fail loudly.
"""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "ARCHIVED_WORKFLOW_DIR",
    "LIVE_WORKFLOW_DIR",
    "REPO_ROOT",
    "workflow_files",
    "workflow_path",
    "workflow_repo_path",
]

REPO_ROOT = Path(__file__).resolve().parents[3]

#: Workflows that GitHub still runs.
LIVE_WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

#: Workflows kept for the record. Readable, never triggered.
ARCHIVED_WORKFLOW_DIR = REPO_ROOT / ".github" / "archived-workflows"


def _dirs(root: Path | None) -> tuple[Path, Path]:
    base = REPO_ROOT if root is None else Path(root)
    return base / ".github" / "workflows", base / ".github" / "archived-workflows"


def workflow_path(name: str, *, root: Path | None = None) -> Path:
    """Where the workflow called ``name`` lives; live directory wins a tie.

    Raises ``FileNotFoundError`` naming both directories when it is in neither,
    so a deleted workflow is still an error rather than a silently wrong path.
    """

    live, archived = _dirs(root)
    for directory in (live, archived):
        candidate = directory / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"workflow {name!r} is in neither {live} nor {archived}"
    )


def workflow_repo_path(name: str, *, root: Path | None = None) -> str:
    """:func:`workflow_path` as a repository-relative POSIX string.

    This is the form ``git`` wants, for example in ``git rev-parse HEAD:<path>``.
    """

    base = REPO_ROOT if root is None else Path(root)
    return workflow_path(name, root=root).relative_to(base).as_posix()


def workflow_files(*, root: Path | None = None) -> tuple[Path, ...]:
    """Every workflow file, live and archived, sorted by name.

    A scan over workflows is looking for what the repository has ever declared,
    so it must cover the archive too; restricting it to the live directory is
    what silently emptied one such scan when the archive was created.
    """

    live, archived = _dirs(root)
    found: dict[str, Path] = {}
    for directory in (archived, live):  # live overwrites archived on a name clash
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            if path.suffix in (".yml", ".yaml") and path.is_file():
                found[path.name] = path
    return tuple(found[name] for name in sorted(found))
