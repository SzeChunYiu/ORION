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


@pytest.mark.parametrize(
    ("relative_path", "sentinel"),
    (
        (
            "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2_1.py",
            "P6 THEORY CLOSURE V2.1: PASS",
        ),
        (
            "papers/orion-17-epistemic-navigation-open-worlds/formal/check_contract_manifest_v2.py",
            "P7 CONTRACT MANIFEST V2: PASS",
        ),
        (
            "papers/orion-18-epistemic-authority-autonomous-science/formal/check_contract_manifest_v2.py",
            "P8 CONTRACT MANIFEST V2: PASS",
        ),
        (
            "papers/orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2_1.py",
            "P8 THEORY CLOSURE V2.1: PASS",
        ),
    ),
)
def test_parallel_completion_findings_are_absorbed(relative_path: str, sentinel: str) -> None:
    output = _run(relative_path)
    assert sentinel in output
