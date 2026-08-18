"""The P9/P10 lane arrives as scripts; these tests are what make it a package.

Three things are pinned. The delivered source is bound by its own manifest and that
binding is checked rather than trusted. Phase 2A is re-derived live and compared against
the committed result, because it is fast, deterministic, and the only real-source evidence
in the lane. And the phase 2A **null** is asserted as a null.

That last one matters most. `p = 0.83` at bigram order against a 1000-rep shuffle is the
lane's most informative result, and a negative is exactly the kind of finding that quietly
becomes a positive when someone widens a corpus or changes a threshold without saying so.
If this test starts failing, that is a claim change and it needs a receipt, not a re-run.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "papers" / "candidates" / "orion-learning-machine"
MANIFEST = LANE / "SCRIPT_MANIFEST_SHA256.txt"
RESULTS = LANE / "results"
PHASE2A = RESULTS / "PHASE2A_RESULTS.json"
PHASE1_V2 = RESULTS / "PHASE1_MECHANIC_COMPOSITION_V2.txt"

MANIFEST_ROW = re.compile(r"([0-9a-f]{64})\s+\*?(.+)")


def _manifest_rows() -> list[tuple[str, str]]:
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        match = MANIFEST_ROW.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2)))
    return rows


def test_every_delivered_file_matches_its_manifest_digest() -> None:
    rows = _manifest_rows()
    assert len(rows) == 36, f"manifest declares {len(rows)} files, expected 36"
    for digest, relative in rows:
        path = LANE / relative
        assert path.is_file(), f"manifest names a file that is not in the tree: {relative}"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == digest, f"{relative} does not match its manifest digest"


def test_results_are_present_and_not_covered_by_the_source_manifest() -> None:
    """The manifest predates the results, and saying so beats implying coverage."""

    named = {relative for _, relative in _manifest_rows()}
    for name in (
        "PHASE0_SOLVER_ECOLOGY.txt",
        "PHASE1_MECHANIC_COMPOSITION.txt",
        "PHASE2A_RESULTS.json",
        "FRAMEWORK_TESTS.txt",
    ):
        assert (RESULTS / name).is_file(), f"missing committed result: {name}"
        assert f"results/{name}" not in named


def test_phase1_false_commit_is_explicitly_not_measured() -> None:
    """A hard-coded zero must never re-enter the result as an observation."""

    delivered = (
        LANE / "experiments" / "phase1_mechanic_composition" / "run_v1.py"
    ).read_text(encoding="utf-8")
    corrected = (
        LANE / "experiments" / "phase1_mechanic_composition" / "run_v2.py"
    ).read_text(encoding="utf-8")
    result = PHASE1_V2.read_text(encoding="utf-8")
    readme = (
        ROOT / "papers" / "candidates" / "paper-09-executable-research-core" / "README.md"
    ).read_text(encoding="utf-8")

    assert "'false_commit':0.0" in delivered, "delivered defect identity changed"
    assert 'metrics.pop("false_commit")' in corrected
    assert "false_commit_status=NOT_MEASURED" in result
    assert "false_commit=0.000" not in result
    assert "false_commit_status=NOT_MEASURED" in readme
    assert "hard-coded `false_commit=0.000`" in readme


def test_phase2a_re_derives_byte_identically(tmp_path: Path) -> None:
    """The only real-source evidence in the lane, checked by re-running it."""

    script = LANE / "experiments" / "phase2_real_source" / "run_phase2a.py"
    written = script.parent / "RESULTS_PHASE2A.json"
    restore = written.read_bytes() if written.exists() else None
    try:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=LANE,
            env={"PYTHONPATH": str(LANE / "framework"), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert completed.returncode == 0, completed.stderr[-2000:]
        assert written.exists(), "phase 2A produced no result file"
        assert json.loads(written.read_text()) == json.loads(PHASE2A.read_text()), (
            "phase 2A no longer re-derives the committed result"
        )
    finally:
        if restore is None:
            written.unlink(missing_ok=True)
        else:
            written.write_bytes(restore)


def test_the_phase2a_macro_result_is_still_a_null() -> None:
    """Guard the negative.

    Mined macros are not distinguishable from shuffled tactic order on this corpus. If a
    later change makes this pass by making the result positive, that is a new claim about
    real Lean source and must be reported as one.
    """

    shuffle = json.loads(PHASE2A.read_text(encoding="utf-8"))["shuffle"]
    bigram = shuffle["bigram"]
    assert bigram["reps"] == 1000
    assert bigram["observed"] <= bigram["shuffle_mean"], (
        "observed bigram macros now exceed the shuffle mean; the null has moved"
    )
    assert bigram["empirical_p_ge"] > 0.05, (
        f"bigram p={bigram['empirical_p_ge']} is now significant; this is a claim change"
    )
    assert shuffle["trigram"]["empirical_p_ge"] > 0.05


def test_phase2b_input_is_absent_and_that_is_recorded() -> None:
    """`CANNOT_CHECK`, not a silent gap.

    The goal-effect script is delivered; its input is not. Both READMEs say so, and this
    fails if the input appears without the documentation catching up.
    """

    script_dir = LANE / "experiments" / "phase2_real_source"
    present = (script_dir / "HF_MATHLIB_TACTICS_SAMPLE.json").is_file()
    documented = "HF_MATHLIB_TACTICS_SAMPLE.json" in (LANE / "REPRODUCE.md").read_text(encoding="utf-8")
    assert documented, "the missing phase 2B input must stay documented"
    if present:
        pytest.fail("phase 2B input has appeared; REPRODUCE.md still calls it absent")


def test_the_closure_verify_script_cannot_be_run_and_the_lane_says_so() -> None:
    """The bundle asserts an authority it does not ship the evidence for.

    `VERIFY_LOCAL_CLOSURE.sh` checks `LOCAL_CORE_COMPLETE` against files that were never
    delivered. Recording that is the honest state; quietly writing the missing files would
    manufacture the authority instead of earning it.
    """

    assert not (LANE / "CLOSURE_MANIFEST.json").exists()
    assert not (LANE / "closure_logs" / "FROZEN_SHA256SUMS.txt").exists()
    reproduce = (LANE / "REPRODUCE.md").read_text(encoding="utf-8")
    assert "not verifiable from what was delivered" in reproduce


@pytest.mark.parametrize(
    ("paper", "must_contain"),
    (
        ("paper-09-executable-research-core", "does not claim novelty"),
        ("paper-10-content-bound-math-evaluation", "does not claim novelty"),
        ("paper-09-executable-research-core", "CANNOT_CHECK"),
        ("paper-10-content-bound-math-evaluation", "CANNOT_CHECK"),
    ),
)
def test_both_candidates_state_their_limits(paper: str, must_contain: str) -> None:
    readme = ROOT / "papers" / "candidates" / paper / "README.md"
    assert must_contain in readme.read_text(encoding="utf-8")
