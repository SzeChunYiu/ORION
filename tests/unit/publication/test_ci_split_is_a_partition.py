"""The CI split must cover every test exactly once.

The suite is split by measured cost, not by test count. A profiling run recorded
all 3077 tests at 1878s, of which one file -- `test_p2_offline_systems.py`, 14
parametrised cases at ~107s each -- is roughly 80%. So there are three lanes: a
serial job for everything outside `tests/unit/p2`, a six-way matrix over the
heavy file alone, and one job for the rest of p2.

The arrangement is only sound while those three lanes stay disjoint and
exhaustive. If they drift apart the result is not a loud failure -- it is a green
run that quietly stopped testing something, which is the worst way for a test
gate to break.

Verified by collection when this split was introduced: 3096 collected across the
three lanes against 3096 unsplit, no duplicates and none missing. This module
pins the structural invariants that keep that true, cheaply enough to run on
every commit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML is needed to read the workflow")

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
HEAVY_FILE = "tests/unit/p2/test_p2_offline_systems.py"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _pytest_commands(job: dict) -> list[str]:
    return [
        " ".join(step["run"].split())
        for step in job.get("steps", [])
        if isinstance(step.get("run"), str) and "pytest" in step["run"]
    ]


def test_the_three_lanes_are_disjoint_and_exhaustive() -> None:
    """Every test belongs to exactly one lane, by construction of the commands."""

    jobs = _workflow()["jobs"]
    fast = " ".join(_pytest_commands(jobs["fast"]))
    heavy = " ".join(_pytest_commands(jobs["p2-heavy"]))
    rest = " ".join(_pytest_commands(jobs["p2-rest"]))

    # fast excludes all of p2.
    assert "--ignore=tests/unit/p2 " in fast + " ", (
        "the fast job no longer excludes tests/unit/p2, so p2 would run twice"
    )
    # heavy runs only the heavy file.
    assert HEAVY_FILE in heavy, "the heavy matrix no longer targets the heavy file"
    # rest runs p2 minus the heavy file. Both halves matter: drop the target and
    # nothing runs, drop the ignore and the heavy file runs twice.
    assert "tests/unit/p2" in rest, "the p2-rest job no longer targets p2"
    assert f"--ignore={HEAVY_FILE}" in rest, (
        "p2-rest no longer excludes the heavy file, so it would run in two lanes"
    )


def test_every_split_group_is_actually_run() -> None:
    """A group listed but never executed is coverage that silently disappears."""

    jobs = _workflow()["jobs"]
    groups = jobs["p2-heavy"]["strategy"]["matrix"]["group"]
    command = " ".join(_pytest_commands(jobs["p2-heavy"]))

    assert groups == list(range(1, len(groups) + 1)), (
        f"pytest-split groups must be 1..N with no gaps, got {groups}"
    )
    assert f"--splits {len(groups)}" in command, (
        f"the matrix declares {len(groups)} groups but --splits disagrees; a mismatch "
        f"here drops tests rather than failing: {command}"
    )


def test_the_aggregate_gate_fails_on_anything_that_is_not_success() -> None:
    """`cancelled` must not read as a pass, and here that is not hypothetical.

    The concurrency group cancels superseded runs, so `cancelled` is routine. More
    sharply: GitHub reports a job that exceeds `timeout-minutes` as `cancelled`
    too, not as `failure`. A 20-minute bound on the old unbalanced p2 shard fired
    exactly that way, and a gate testing only for `failure` would have called that
    run green.
    """

    jobs = _workflow()["jobs"]
    gate = jobs["test"]
    assert gate["if"] == "always()" or gate["if"] is True, (
        "the gate must run even when a needed job failed, or it is skipped along "
        "with them and the PR shows no failing required check"
    )
    assert set(gate["needs"]) == {"fast", "p2-heavy", "p2-rest"}, (
        f"the gate must depend on every test job, got {gate['needs']}"
    )

    script = " ".join(
        step["run"] for step in gate["steps"] if isinstance(step.get("run"), str)
    )
    assert '!= "success"' in script, (
        "the gate must test for 'not success' rather than for 'failure', so that a "
        "cancelled, timed-out or skipped job cannot pass it"
    )


def test_no_test_directory_is_excluded_without_a_job_that_runs_it() -> None:
    """Catch a new --ignore added without a lane to cover it."""

    jobs = _workflow()["jobs"]
    ignored: set[str] = set()
    for job in jobs.values():
        for command in _pytest_commands(job):
            for token in command.split():
                if token.startswith("--ignore="):
                    ignored.add(token.split("=", 1)[1])

    assert ignored == {"tests/unit/p2", HEAVY_FILE}, (
        f"exclusions changed to {sorted(ignored)}. Every excluded path needs a job "
        f"that runs it, and this test updated to say so."
    )


def test_every_job_is_bounded_in_time() -> None:
    """A job with no timeout sits at GitHub's six-hour default when it hangs."""

    for name, job in _workflow()["jobs"].items():
        if name == "test":
            continue  # the gate is a shell echo; it cannot hang on tests
        assert "timeout-minutes" in job, f"{name} has no timeout-minutes"
        # Measured, not guessed.  Twelve completed `fast` jobs on ci.yml run
        # 18.9-28.6 minutes (median 27.3), and that already includes the poppler
        # install this lane now performs.  The bound exists to catch a *hang* --
        # a job with no timeout sits at GitHub's six-hour default -- and 40
        # catches a hang just as surely as 30 while leaving the measured maximum
        # ~11 minutes of headroom on a slow hosted runner.
        #
        # 30 was never reconciled with the workflow: ci.yml has given `fast`
        # timeout-minutes 40 since run 32915463499 exhausted a 25-minute budget
        # mid-suite, so main was red on this contradiction rather than on any
        # real regression.  A timeout is reported as `cancelled`, which the
        # aggregate gate reads as failure, so a bound set below the measured
        # maximum converts slow runners into spurious red.
        assert job["timeout-minutes"] <= 40, (
            f"{name} allows {job['timeout-minutes']}m; measured `fast` runs peak "
            f"at 28.6m, so a lane past 40 is wrong rather than slow"
        )
