"""Keep the merged P6-P8 hostile and assumption-review suites live in CI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def _run(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *parts],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_assumption_and_contract_regressions_execute() -> None:
    completed = _run("papers/candidates/run_assumption_regressions_v2.py")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    receipt = json.loads(completed.stdout)
    assert receipt["all_passed"] is True
    assert receipt["totals"]["unit_tests"] >= 28
    assert receipt["totals"]["machine_readable_cases"] == 37


def test_hostile_review_executes_and_can_report_failures(tmp_path: Path) -> None:
    unit = _run(
        "-m",
        "unittest",
        "papers.candidates.hostile_review_v1.tests.test_hostile_review",
    )
    assert unit.returncode == 0, unit.stdout + unit.stderr

    output = tmp_path / "hostile-review.json"
    completed = _run(
        "papers/candidates/hostile_review_v1/run_all.py",
        "--output",
        str(output),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS" in completed.stdout
    assert json.loads(output.read_text(encoding="utf-8"))["schema"] == (
        "orion.p6_p8.hostile_formal_review.v1"
    )
