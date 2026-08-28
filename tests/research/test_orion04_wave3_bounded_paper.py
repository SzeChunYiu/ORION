from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "papers/orion-04-rooted-completion-certificates/wave3_bounded_closeout_v1"


def test_orion04_bounded_closeout_verifies() -> None:
    completed = subprocess.run(
        [sys.executable, str(PACKET / "verify_closeout.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "ORION04_WAVE3_BOUNDED_PAPER=VERIFIED" in completed.stdout


def test_orion04_authority_is_fail_closed() -> None:
    disposition = json.loads((PACKET / "PUBLICATION_DISPOSITION.json").read_text())
    assert disposition["scientific_terminal"] == (
        "ORION04_EXACT_D4_NOT_ESTABLISHED__PAPER_REFRAMED_TO_BOUNDED_STRUCTURAL_RESULT"
    )
    assert disposition["admitted_authority"]["support_at_least_14"] is True
    assert all(value is False for value in disposition["withheld_authority"].values())


def test_orion04_claim_ledger_keeps_exact_d4_open() -> None:
    ledger = json.loads((PACKET / "ATOMIC_CLAIM_LEDGER.json").read_text())
    by_id = {row["id"]: row for row in ledger["claims"]}
    assert by_id["C6"]["status"] == "PROVED_BOUNDED_COMPUTER_ASSISTED"
    assert by_id["C10"]["status"] == "OPEN"
    assert by_id["C11"]["status"] == "OPEN"
    assert by_id["C12"]["status"] == "OPEN"
