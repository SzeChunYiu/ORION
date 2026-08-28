from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/wave3/orion04-support11-13-v1"
CHECKER = PACKET / "independent_checker/check_result.py"
RESULT = PACKET / "RESULT.json"
POSITIVE = "ORION04_M4_C5CUBED_SUPPORT11_13_ALL_BRANCHES_EXCLUDED__OBSTRUCTION_SUPPORT_AT_LEAST14"


def test_committed_result_is_fail_closed_and_checker_accepts(tmp_path: Path) -> None:
    raw = json.loads(RESULT.read_text())
    assert raw["terminal"] == POSITIVE
    assert raw["bounded_support_le13_theorem_authority"] is True
    assert raw["support_14_plus_theorem_authority"] is False
    assert raw["support_23_theorem_authority"] is False
    assert raw["c0_31_authority"] is False
    assert raw["exact_d4_authority"] is False

    output = tmp_path / "generic.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), "--input", str(RESULT), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    generic = json.loads(output.read_text())
    assert generic["decision"] == "ACCEPT_ORION04_SUPPORT_LE13_EXCLUSION"
    assert all(generic["checks"].values())
