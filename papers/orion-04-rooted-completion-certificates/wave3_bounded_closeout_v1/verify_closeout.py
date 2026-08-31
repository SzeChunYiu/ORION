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
    "we prove D_4(C_5^3)=30",
    "we prove D_4(C_5^3)=31",
    "support at least twenty-three",
    "external independent replay is complete",
)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    disposition = json.loads(DISPOSITION.read_text())
    claims = json.loads(CLAIMS.read_text())
    text = MANUSCRIPT.read_text()

    assert manifest["scientific_terminal"] == (
        "ORION04_EXACT_D4_NOT_ESTABLISHED__PAPER_REFRAMED_TO_BOUNDED_STRUCTURAL_RESULT"
    )
    for row in manifest["files"]:
        path = ROOT / row["path"]
        assert path.is_file(), row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]

    admitted = disposition["admitted_authority"]
    withheld = disposition["withheld_authority"]
    assert admitted["support_at_least_14"] is True
    assert all(value is False for value in withheld.values())
    assert claims["all_reader_facing_claims_resolved"] is True
    assert claims["unresolved_claims_are_explicitly_labelled_open"] is True
    assert "has support at least fourteen" in text
    assert "remains open" in text and "D_4(C_5^3)" in text
    assert "theorem_authority=false" in text
    lowered = text.lower()
    for phrase in PROHIBITED:
        assert phrase.lower() not in lowered, phrase
    print("ORION04_WAVE3_BOUNDED_PAPER=VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
