"""The CI split must cover every test exactly once.

The suite is split across jobs for speed: one job runs everything except
``tests/unit/p2``, and a four-way matrix runs ``tests/unit/p2`` alone, because that
one directory is ~400s of a ~405s suite. The arrangement is only sound while the
excluded path and the split path stay the same path. If they drift apart, the
result is not a loud failure -- it is a green run that quietly stopped testing a
directory, which is the worst way for a test gate to break.

Verified by collection when the split was introduced: 2490 tests in the fast job,
501 across the four p2 groups, 2991 in the unsplit suite, no duplicates and none
missing. This module pins the structural invariant that keeps that true, cheaply
enough to run on every commit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML is needed to read the workflow")

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _pytest_commands(job: dict) -> list[str]:
    return [
        step["run"].strip()
        for step in job.get("steps", [])
        if isinstance(step.get("run"), str) and "pytest" in step["run"]
    ]


def test_the_excluded_directory_is_exactly_the_one_the_matrix_runs() -> None:
    """The single invariant the whole split rests on."""

    jobs = _workflow()["jobs"]
    fast = " ".join(_pytest_commands(jobs["fast"]))
    p2 = " ".join(_pytest_commands(jobs["p2"]))

    assert "--ignore=tests/unit/p2" in fast, (
        "the fast job no longer excludes tests/unit/p2; it would now run the slow "
        "directory as well as the matrix, or the matrix path has moved"
    )
    assert "tests/unit/p2" in p2, "the p2 matrix job no longer targets tests/unit/p2"


def test_every_split_group_is_actually_run() -> None:
    """A group listed but never executed is coverage that silently disappears."""

    jobs = _workflow()["jobs"]
    groups = jobs["p2"]["strategy"]["matrix"]["group"]
    command = " ".join(_pytest_commands(jobs["p2"]))

    assert groups == sorted(groups), "matrix groups should be listed in order"
    assert groups[0] == 1 and groups == list(range(1, len(groups) + 1)), (
        f"pytest-split groups must be 1..N with no gaps, got {groups}"
    )
    assert f"--splits {len(groups)}" in command, (
        f"the matrix declares {len(groups)} groups but --splits disagrees; a mismatch "
        f"here drops tests rather than failing: {command}"
    )


def test_the_aggregate_gate_fails_on_anything_that_is_not_success() -> None:
    """`cancelled` and `skipped` must not read as a pass.

    The concurrency group cancels superseded runs, so `cancelled` is a routine
    outcome here rather than an exotic one. A gate that only checks for `failure`
    reports a cancelled run as green.
    """

    jobs = _workflow()["jobs"]
    gate = jobs["test"]
    assert gate["if"] == "always()" or gate["if"] is True, (
        "the aggregate gate must run even when a needed job failed, or it is skipped "
        "along with them and the PR shows no failing required check"
    )
    assert set(gate["needs"]) == {"fast", "p2"}, (
        f"the gate must depend on every test job, got {gate['needs']}"
    )

    script = " ".join(
        step["run"] for step in gate["steps"] if isinstance(step.get("run"), str)
    )
    assert '!= "success"' in script, (
        "the gate must test for 'not success' rather than for 'failure', so that a "
        "cancelled or skipped job cannot pass it"
    )


def test_no_test_directory_is_excluded_without_a_job_that_runs_it() -> None:
    """Catch a second --ignore being added without a matching job.

    One exclusion is accounted for. A future edit that excludes another directory
    to make CI faster, without adding a job to run it, would silently drop it.
    """

    jobs = _workflow()["jobs"]
    ignored: set[str] = set()
    for job in jobs.values():
        for command in _pytest_commands(job):
            for token in command.split():
                if token.startswith("--ignore="):
                    ignored.add(token.split("=", 1)[1])

    assert ignored == {"tests/unit/p2"}, (
        f"exclusions changed to {sorted(ignored)}. Every excluded path needs a job "
        f"that runs it, and this test updated to say so."
    )
