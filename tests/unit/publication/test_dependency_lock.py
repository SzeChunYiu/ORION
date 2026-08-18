"""The dependency lock is committed, current, and covers what the papers import.

Issue #160 Gate 7 records "dependency/environment lock" as `[ ]` for all five
papers, with the reason *"no lockfile beyond pyproject.toml"*. A lock closes that
only while it stays in step with `pyproject.toml`; a stale lock is worse than
none, because it looks like a reproducible environment and is not.

`uv sync --frozen` in `clean-install-reproduction.yml` is the real enforcement --
it refuses to install when the two disagree. These tests fail in the ordinary
suite instead, so a dependency change without a relock is caught by every lane
rather than only by the workflow that watches `uv.lock`.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOCK = ROOT / "uv.lock"
PYPROJECT = ROOT / "pyproject.toml"
GITIGNORE = ROOT / ".gitignore"

#: `name = "x"` at the start of a `[[package]]` block.
PACKAGE_NAME = re.compile(r'^name = "([^"]+)"$', re.MULTILINE)
#: `cryptography>=45` -> `cryptography`; also handles extras and markers.
REQUIREMENT_NAME = re.compile(r"^([A-Za-z0-9._-]+)")


def _declared_dependencies() -> set[str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data["project"]
    requirements = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        requirements.extend(extra)
    names = set()
    for requirement in requirements:
        match = REQUIREMENT_NAME.match(requirement.strip())
        assert match, requirement
        names.add(match.group(1).lower().replace("_", "-"))
    return names


def test_lock_exists_and_is_tracked() -> None:
    assert LOCK.is_file(), "uv.lock is missing; run `uv lock`"
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "uv.lock"],
        capture_output=True,
        text=True,
    )
    assert tracked.returncode == 0, "uv.lock exists but is untracked"


def test_lock_is_not_gitignored() -> None:
    """The line that made Gate 7 unclosable.

    `uv.lock` was ignored in `.gitignore`'s initial commit alongside `.venv/`,
    `__pycache__/` and `.pytest_cache/`. Those are derived artifacts; a lock is
    an input. If it is re-added to the ignore list the gate silently reopens, so
    this asserts the absence rather than trusting the comment to survive.
    """

    ignored = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", "uv.lock"],
        capture_output=True,
        text=True,
    )
    assert ignored.returncode != 0, "uv.lock is gitignored again; see .gitignore"
    assert "uv.lock" not in {
        line.strip() for line in GITIGNORE.read_text(encoding="utf-8").splitlines()
    }


def test_every_declared_dependency_is_locked() -> None:
    locked = {name.lower().replace("_", "-") for name in PACKAGE_NAME.findall(LOCK.read_text(encoding="utf-8"))}
    missing = sorted(_declared_dependencies() - locked)
    assert not missing, f"declared but not in uv.lock (relock needed): {missing}"


def test_lock_pins_the_python_floor_the_project_declares() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    declared = data["project"]["requires-python"]
    assert f'requires-python = "{declared}"' in LOCK.read_text(encoding="utf-8")
