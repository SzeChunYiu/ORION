from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/wave3/orion04-support11-13-v1"
RUNNER = PACKET / "run_replay.py"
CHECKER = PACKET / "independent_checker/check_result.py"
RESULT = PACKET / "RESULT.json"
POSITIVE = "ORION04_M4_C5CUBED_SUPPORT11_13_ALL_BRANCHES_EXCLUDED__OBSTRUCTION_SUPPORT_AT_LEAST14"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_committed_result_is_fail_closed_and_checker_accepts(tmp_path: Path) -> None:
    raw = json.loads(RESULT.read_text())
    assert raw["terminal"] == POSITIVE
    assert raw["bounded_support_le13_theorem_authority"] is True
    assert raw["support_14_plus_theorem_authority"] is False
    assert raw["support_23_theorem_authority"] is False
    assert raw["c0_31_authority"] is False
    assert raw["exact_d4_authority"] is False

    output = tmp_path / "generic.json"
    completed = _run(
        [sys.executable, str(CHECKER), "--input", str(RESULT), "--output", str(output)]
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    generic = json.loads(output.read_text())
    assert generic["decision"] == "ACCEPT_ORION04_SUPPORT_LE13_EXCLUSION"
    assert all(generic["checks"].values())


def test_current_checkout_replays_exact_committed_receipt(tmp_path: Path) -> None:
    generated = tmp_path / "result.json"
    replay = _run([sys.executable, str(RUNNER), "--output", str(generated)])
    assert replay.returncode == 0, replay.stderr + replay.stdout

    committed = json.loads(RESULT.read_text())
    observed = json.loads(generated.read_text())
    assert observed == committed
    assert observed["terminal"] == POSITIVE
    assert all(observed["gates"].values())

    checked = tmp_path / "checked.json"
    verify = _run(
        [sys.executable, str(CHECKER), "--input", str(generated), "--output", str(checked)]
    )
    assert verify.returncode == 0, verify.stderr + verify.stdout
    generic = json.loads(checked.read_text())
    assert generic["decision"] == "ACCEPT_ORION04_SUPPORT_LE13_EXCLUSION"
    assert all(generic["checks"].values())
