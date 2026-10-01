#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SUBMISSION_MANIFEST.json"
DISPOSITION = ROOT / "PUBLICATION_DISPOSITION.json"
CLAIMS = ROOT / "ATOMIC_CLAIM_LEDGER.json"
MANUSCRIPT = ROOT / "MANUSCRIPT.md"

PROHIBITED = (
    "we establish autonomous self-improvement",
    "we prove protected longitudinal transfer",
    "all six comparators were executed",
    "external independent reproduction is complete",
)

def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    disposition = json.loads(DISPOSITION.read_text())
    claims = json.loads(CLAIMS.read_text())
    text = MANUSCRIPT.read_text()

    assert manifest["scientific_terminal"] == (
        "SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED"
    )
    for row in manifest["files"]:
        path = ROOT / row["path"]
        assert path.is_file(), row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]

    assert claims["all_reader_facing_claims_resolved"] is True
    admitted = disposition["admitted_authority"]
    withheld = disposition["withheld_authority"]
    assert admitted["adaptive_false_promotion_bound"] is True
    assert all(value is False for value in withheld.values())
    assert "zero of six comparator arms is confirmatory-ready" in text
    assert "protected longitudinal transfer" in text
    assert "CANNOT_CHECK" in text
    assert "SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED" in text
    lowered = text.lower()
    for phrase in PROHIBITED:
        assert phrase.lower() not in lowered, phrase
    print("ORION15_WAVE3_GOVERNANCE_PAPER=VERIFIED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
