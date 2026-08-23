#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED = [
    ROOT / "TECHNICAL_NOTE.md",
    ROOT / "CLAIM_LEDGER.md",
    ROOT / "JOURNAL_READINESS.md",
    ROOT / "SATURATION_LEDGER_2026-08-18.md",
    ROOT / "P11_CLAIM_LEDGER_V1.md",
    ROOT / "P11_JOURNAL_READINESS.md",
    ROOT / "P11_REPRODUCE.md",
    ROOT / "P11_REOPEN_PROTOCOL_V3.md",
    ROOT / "benchmark" / "CONTENT_BOUND_PROOF_TASK_V3_SCHEMA.json",
    ROOT / "results" / "PARSER_CONTAMINATION_AUDIT_V2.json",
    ROOT / "results" / "INVALIDATION_V2.md",
    ROOT / "results" / "MATHLIB_TRANSFER_V2_1.json",
    ROOT / "results" / "MATHLIB_TRANSFER_V2_1_NULL_DISTRIBUTIONS.json",
    ROOT / "results" / "MATHLIB_NATIVE_RECEIPTS_V1.json",
    ROOT / "submission" / "P11_JAR_MANUSCRIPT.tex",
    ROOT / "submission" / "P11_REFERENCES.bib",
    ROOT / "submission" / "P11_COVER_LETTER.md",
    ROOT / "submission" / "P11_DECLARATIONS.md",
    ROOT / "submission" / "README.md",
]

MUST_APPEAR = [
    "1,289",
    "4,861",
    "26.52",
    "0.1046",
    "0.0863",
    "0.1223",
    "151",
    "518",
    "1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90",
    "does not establish",
]

FORBIDDEN = [
    r"discover(?:s|ed)? reusable tactics",
    r"proves? statement faithfulness",
    r"all 457 files (?:were|are) natively",
    r"cross-revision mechanism transfer (?:is|was) supported",
    r"scientific truth (?:is|was) established",
]

BIB_KEYS = {
    "yang2023leandojo",
    "leandojov2",
    "letson2026sorrydb",
    "firsching2026formalconjectures",
    "xin2026verisoftbench",
    "xin2025tacminer",
    "nawaz2019pvs",
    "wu2026itpeval",
    "ammanamanchi2026faults",
    "lu2026leanrefactor",
}


def fail(msg: str) -> None:
    print(f"P11_PEER_REVIEW_READY: FAIL: {msg}")
    raise SystemExit(1)


def main() -> None:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    manuscript = (ROOT / "submission" / "P11_JAR_MANUSCRIPT.tex").read_text(encoding="utf-8")
    ledger = (ROOT / "P11_CLAIM_LEDGER_V1.md").read_text(encoding="utf-8")
    readiness = (ROOT / "P11_JOURNAL_READINESS.md").read_text(encoding="utf-8")
    bib = (ROOT / "submission" / "P11_REFERENCES.bib").read_text(encoding="utf-8")

    combined = manuscript + "\n" + ledger
    for token in MUST_APPEAR:
        if token not in combined:
            fail(f"required result/boundary token absent: {token}")

    lower = manuscript.lower()
    for pattern in FORBIDDEN:
        if re.search(pattern, lower):
            fail(f"forbidden overclaim matched: {pattern}")

    if "PEER_REVIEW_READY" not in readiness:
        fail("readiness file lacks exact peer-review terminal")
    if "exact PR head" not in readiness:
        fail("readiness file lacks exact-head gate")

    present_keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
    absent = sorted(BIB_KEYS - present_keys)
    if absent:
        fail("missing bibliography keys: " + ", ".join(absent))

    citations = set()
    for match in re.findall(r"\\cite\{([^}]+)\}", manuscript):
        citations.update(k.strip() for k in match.split(","))
    unresolved = sorted(citations - present_keys)
    if unresolved:
        fail("unresolved manuscript citations: " + ", ".join(unresolved))

    future_work_markers = (
        "P11_REOPEN_PROTOCOL_V3.md",
        r"P11\_REOPEN\_PROTOCOL\_V3.md",
    )
    if not any(marker in manuscript for marker in future_work_markers):
        fail("manuscript does not identify prospective V3 as future work")

    print("P11_PEER_REVIEW_READY: PASS")
    print(f"required_files={len(REQUIRED)} citations={len(citations)} bibliography_entries={len(present_keys)}")


if __name__ == "__main__":
    main()
