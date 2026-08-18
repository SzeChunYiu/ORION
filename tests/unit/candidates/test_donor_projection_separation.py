from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_donor_projection_separation() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "papers/candidates/checkers/check_donor_projection_separation_v1.py")],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "DONOR PROJECTION SEPARATION V1: PASS" in completed.stdout
    assert "ideal donor product with joint semantics may tie" in completed.stdout
