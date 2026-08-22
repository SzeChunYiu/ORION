from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from orion.programme.q_series_content_binding import load_q_series_content_binding


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "papers/Q-paper-01-tare-expressivity/independent_human_proof_sanity.py"
BOUND_RESULT = (
    ROOT
    / "papers/Q-paper-01-tare-expressivity/"
    "INDEPENDENT_HUMAN_PROOF_SANITY_RESULTS_2026-08-22.json"
)


def test_q1_standalone_proof_sanity_matches_bound_result() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    actual = json.loads(completed.stdout)
    expected = json.loads(BOUND_RESULT.read_text(encoding="utf-8"))

    assert actual == expected
    assert actual["status"] == "PASS"
    assert actual["orion_quantum_imports"] is False
    assert "not external peer review" in actual["authority"]


def test_q1_standalone_proof_sanity_code_and_result_are_content_bound() -> None:
    binding = load_q_series_content_binding(ROOT)
    bound_paths = {row["path"] for row in binding["files"]}

    assert SCRIPT.relative_to(ROOT).as_posix() in bound_paths
    assert BOUND_RESULT.relative_to(ROOT).as_posix() in bound_paths
