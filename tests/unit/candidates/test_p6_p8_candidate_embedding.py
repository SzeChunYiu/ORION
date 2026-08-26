from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]


def _run(relative_path: str) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [sys.executable, str(ROOT / relative_path)],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    return completed.stdout


def test_candidate_schema_embedding_matches_live_orion() -> None:
    output = _run("papers/candidates/checkers/check_orion_schema_embedding_v1.py")
    assert "ORION P6-P8 schema embedding V1: PASS" in output
    assert "exact P1-P5 decision embedding: NOT CHECKED BY THIS SCRIPT" in output


def test_candidate_native_embedding_preserves_p1_p5_fixture_decisions() -> None:
    output = _run("papers/candidates/checkers/check_p1_p5_native_embedding_v1.py")
    assert "PASS P1 responsibility/reframe/reopen native decisions" in output
    assert "PASS P2 route-stop/task-stop native decisions" in output
    assert "PASS P3 semantic merge/obstruction native decisions" in output
    assert "PASS P4 non-compensatory hard-gate native decisions" in output
    assert "PASS P5 protected readiness/no-self-promotion native decisions" in output
    assert "P1-P5 NATIVE EMBEDDING V1: PASS" in output


@pytest.mark.parametrize(
    ("relative_path", "sentinel"),
    (
        (
            "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py",
            "P6 finite-model checks: PASS",
        ),
        (
            "papers/orion-17-epistemic-navigation-open-worlds/formal/check_countermodels.py",
            "P7 deterministic countermodels: PASS",
        ),
        (
            "papers/orion-18-epistemic-authority-autonomous-science/formal/check_authority_calculus.py",
            "P8 authority-calculus checks: PASS",
        ),
        (
            "papers/candidates/checkers/check_preservation_ladder_v1.py",
            "P6-P8 preservation ladder V1: PASS",
        ),
        (
            "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2.py",
            "P6 THEORY CLOSURE V2: PASS",
        ),
        (
            "papers/orion-17-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py",
            "P7 THEORY CLOSURE V2: PASS",
        ),
        (
            "papers/orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2.py",
            "P8 THEORY CLOSURE V2: PASS",
        ),
        (
            "papers/candidates/checkers/check_donor_complete_envelope_v1.py",
            "DONOR-COMPLETE ORION ENVELOPE V1: PASS",
        ),
    ),
)
def test_candidate_theory_and_embedding_support(relative_path: str, sentinel: str) -> None:
    output = _run(relative_path)
    assert sentinel in output
