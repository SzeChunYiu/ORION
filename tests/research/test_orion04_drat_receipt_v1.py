from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/orion-rg/promotion/orion04-global-certified-search-v1"
CHECKER = PACKET / "independent_checker/check_drat_proof.py"


def test_drat_receipt_rejects_unpinned_checker_before_execution(tmp_path: Path) -> None:
    cnf = tmp_path / "registered.cnf"
    proof = tmp_path / "proof.drat"
    fake_checker = tmp_path / "fake-checker"
    manifest = tmp_path / "manifest.json"
    receipt = tmp_path / "receipt.json"

    cnf.write_text("p cnf 1 2\n1 0\n-1 0\n")
    proof.write_text("0\n")
    fake_checker.write_text("#!/bin/sh\nexit 0\n")
    fake_checker.chmod(fake_checker.stat().st_mode | os.stat_result((0o100, 0, 0, 0, 0, 0, 0, 0, 0, 0)).st_mode)
    manifest.write_text(
        json.dumps(
            {
                "schema": "ORION.ORION04.GlobalCertifiedSearchCnfManifest.v1",
                "protocol_id": "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1",
                "parameters": {
                    "prime": 5,
                    "rank": 3,
                    "length": 31,
                    "support_lower_bound": 14,
                    "max_short_length": 5,
                    "positive_multiplicities": [1, 2, 4],
                },
                "cnf_sha256": hashlib.sha256(cnf.read_bytes()).hexdigest(),
                "solver_outcome_accessed": False,
                "proof_checked": False,
                "c0_31_authority": False,
                "exact_d4_authority": False,
            }
        )
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--cnf",
            str(cnf),
            "--manifest",
            str(manifest),
            "--proof",
            str(proof),
            "--checker",
            str(fake_checker),
            "--expected-checker-sha256",
            "0" * 64,
            "--output",
            str(receipt),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    raw = json.loads(receipt.read_text())
    assert raw["terminal"] == "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK"
    assert raw["checks"]["checker_digest"] is False
    assert raw["checks"]["drat_checker_exit_zero"] is False
    assert raw["c0_31_authority"] is False
    assert raw["exact_d4_30_authority"] is False


def test_drat_receipt_rejects_instance_digest_drift(tmp_path: Path) -> None:
    cnf = tmp_path / "registered.cnf"
    proof = tmp_path / "proof.drat"
    fake_checker = tmp_path / "fake-checker"
    manifest = tmp_path / "manifest.json"
    receipt = tmp_path / "receipt.json"

    cnf.write_text("p cnf 1 2\n1 0\n-1 0\n")
    proof.write_text("0\n")
    fake_checker.write_text("#!/bin/sh\nexit 0\n")
    fake_checker.chmod(0o755)
    checker_digest = hashlib.sha256(fake_checker.read_bytes()).hexdigest()
    manifest.write_text(
        json.dumps(
            {
                "schema": "ORION.ORION04.GlobalCertifiedSearchCnfManifest.v1",
                "protocol_id": "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1",
                "parameters": {
                    "prime": 5,
                    "rank": 3,
                    "length": 31,
                    "support_lower_bound": 14,
                    "max_short_length": 5,
                    "positive_multiplicities": [1, 2, 4],
                },
                "cnf_sha256": "f" * 64,
                "solver_outcome_accessed": False,
                "proof_checked": False,
                "c0_31_authority": False,
                "exact_d4_authority": False,
            }
        )
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--cnf",
            str(cnf),
            "--manifest",
            str(manifest),
            "--proof",
            str(proof),
            "--checker",
            str(fake_checker),
            "--expected-checker-sha256",
            checker_digest,
            "--output",
            str(receipt),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    raw = json.loads(receipt.read_text())
    assert raw["checks"]["cnf_digest"] is False
    assert raw["checks"]["drat_checker_exit_zero"] is False
    assert raw["terminal"] == "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK"
