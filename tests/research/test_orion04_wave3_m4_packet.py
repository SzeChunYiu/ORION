from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/wave3/orion04-support11-13-v1"
CHECKER = PACKET / "independent_checker/check_result.py"
RESULT = PACKET / "RESULT.json"
POSITIVE = "ORION04_M4_C5CUBED_SUPPORT11_13_ALL_BRANCHES_EXCLUDED__OBSTRUCTION_SUPPORT_AT_LEAST14"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _resign(raw: dict[str, Any]) -> None:
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    raw["result_digest"] = hashlib.sha256(_canonical(unsigned).encode()).hexdigest()


def _run_checker(input_path: Path, output_path: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(output_path.read_text())


def _write_tampered(tmp_path: Path, name: str, raw: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    return path


def test_committed_result_is_fail_closed_and_checker_accepts(tmp_path: Path) -> None:
    raw = json.loads(RESULT.read_text())
    assert raw["terminal"] == POSITIVE
    assert raw["bounded_support_le13_theorem_authority"] is True
    assert raw["support_14_plus_theorem_authority"] is False
    assert raw["support_23_theorem_authority"] is False
    assert raw["c0_31_authority"] is False
    assert raw["exact_d4_authority"] is False

    completed, generic = _run_checker(RESULT, tmp_path / "generic.json")
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert generic["decision"] == "ACCEPT_ORION04_SUPPORT_LE13_EXCLUSION"
    assert all(generic["checks"].values())


def test_checker_rejects_resigned_rank3_fingerprint_tamper(tmp_path: Path) -> None:
    raw = copy.deepcopy(json.loads(RESULT.read_text()))
    raw["replay_ledger"]["rank3_rows"][0]["u128"]["nodes"] += 1
    raw["replay_ledger"]["rank3_rows"][0]["bytes"]["nodes"] += 1
    _resign(raw)
    path = _write_tampered(tmp_path, "rank3-tamper.json", raw)

    completed, generic = _run_checker(path, tmp_path / "rank3-generic.json")
    assert completed.returncode == 1
    assert generic["decision"] == "REJECT_ORION04_SUPPORT_LE13_EXCLUSION"
    assert generic["checks"]["source_digest"] is True
    assert generic["checks"]["nine_rank3_rows"] is False


def test_checker_rejects_resigned_authority_escalation(tmp_path: Path) -> None:
    raw = copy.deepcopy(json.loads(RESULT.read_text()))
    raw["support_23_theorem_authority"] = True
    _resign(raw)
    path = _write_tampered(tmp_path, "authority-tamper.json", raw)

    completed, generic = _run_checker(path, tmp_path / "authority-generic.json")
    assert completed.returncode == 1
    assert generic["checks"]["source_digest"] is True
    assert generic["checks"]["no_support14_or_23"] is False


def test_checker_rejects_resigned_rank2_coverage_tamper(tmp_path: Path) -> None:
    raw = copy.deepcopy(json.loads(RESULT.read_text()))
    for engine in ("u128", "bytes"):
        branch = raw["replay_ledger"]["rank2_branch"][engine]
        branch["seed_rows"] = branch["seed_rows"][:-1]
        branch["seed_rows_executed"] = 8
        branch["seed_rows_rejected_before_dfs"] = 8
    _resign(raw)
    path = _write_tampered(tmp_path, "rank2-tamper.json", raw)

    completed, generic = _run_checker(path, tmp_path / "rank2-generic.json")
    assert completed.returncode == 1
    assert generic["checks"]["source_digest"] is True
    assert generic["checks"]["rank2_branch"] is False
