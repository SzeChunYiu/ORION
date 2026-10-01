from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "papers/orion-15-self-orion/wave3_governance_closeout_v1"

def test_orion15_governance_closeout_verifies() -> None:
    completed = subprocess.run(
        [sys.executable, str(PACKET / "verify_closeout.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "ORION15_WAVE3_GOVERNANCE_PAPER=VERIFIED" in completed.stdout

def test_orion15_empirical_authority_is_withheld() -> None:
    disposition = json.loads((PACKET / "PUBLICATION_DISPOSITION.json").read_text())
    assert disposition["scientific_terminal"] == (
        "SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED"
    )
    assert all(value is False for value in disposition["withheld_authority"].values())

def test_orion15_claims_separate_theory_from_evidence() -> None:
    ledger = json.loads((PACKET / "ATOMIC_CLAIM_LEDGER.json").read_text())
    by_id = {row["id"]: row for row in ledger["claims"]}
    assert by_id["T8"]["status"] == "PROVED"
    assert by_id["E2"]["status"] == "BOUNDED_DESCRIPTIVE_DIRECTION_ONLY"
    assert by_id["E3"]["status"] == "CANNOT_CHECK"
    assert by_id["E4"]["status"] == "CANNOT_CHECK_WITHDRAWN"
