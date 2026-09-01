#!/usr/bin/env python3
"""Skill-driven surface audit for the five R4 mathematical packages.

The audit operationalizes the final editorial guardrails taken from the frozen
academic-paper-skills workflow.  It checks structure, proof visibility,
application boundaries, unresolved-claim visibility, and the canonical finite
verifier.  It does not evaluate mathematical novelty or replace peer review.

Run from the repository root:

    python papers/audit_five_r4_surfaces.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"

ADDENDA = {
    "A": PAPERS / "theory-A-multitag-constraint-rank" / "MATHEMATICAL_EXTENSIONS_R4.md",
    "B": PAPERS / "theory-B-certificate-complexity" / "MATHEMATICAL_EXTENSIONS_R4.md",
    "C": PAPERS / "theory-C-low-order-information" / "MATHEMATICAL_EXTENSIONS_R4.md",
    "D": PAPERS / "theory-D-falsification-authority" / "MATHEMATICAL_EXTENSIONS_R4.md",
    "NQ": PAPERS / "nonquantum-c5cubed-davenport" / "MATHEMATICAL_EXTENSIONS_R4.md",
}

CENTRAL_FILES = [
    PAPERS / "FIVE_PAPER_MATH_ENGINEERING_R3_2026-08-25.md",
    PAPERS / "FIVE_PAPER_APPLICATION_MAP_R3_2026-08-25.md",
    PAPERS / "FIVE_PAPER_REVIEW_SYNTHESIS_R5_2026-08-25.md",
    PAPERS / "FIVE_PAPER_ATOMIC_VERIFICATION_R8_2026-08-25.md",
    PAPERS / "FIVE_PAPER_SKILL_APPLICATION_R3_2026-08-25.md",
    PAPERS / "FIVE_PAPER_POLISHED_TITLES_ABSTRACTS_R3_2026-08-25.md",
]

PLACEHOLDERS = ("TODO", "TBD", "FIXME", "XXX", "lorem ipsum")
HYPE_PATTERNS = (
    r"\brevolutionary\b",
    r"\bgroundbreaking\b",
    r"\bguarantees? top[- ]tier\b",
    r"\bsolves? D_4\(C_5\^3\)\b",
    r"\bproves? C_0\(31\)\b",
)


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def audit_addendum(label: str, path: Path) -> dict[str, object]:
    text = read(path)
    lower = text.lower()

    theorem_count = len(re.findall(r"\*\*(?:Theorem|Proposition|Corollary)\b", text))
    proof_count = len(re.findall(r"\*\*Proof\.\*\*", text))

    assert theorem_count >= 3, f"{label}: too few visible formal statements"
    assert proof_count >= 2, f"{label}: too few visible proof blocks"
    assert "purpose" in lower, f"{label}: missing purpose section"
    assert "application" in lower, f"{label}: missing application discussion"
    assert "atomic claim status" in lower, f"{label}: missing atomic claim status"
    assert "editorial effect" in lower, f"{label}: missing editorial effect"
    assert "not_claimed" in lower or "not claimed" in lower, (
        f"{label}: missing explicit nonclaim"
    )
    assert "unresolved" in lower or "remaining" in lower, (
        f"{label}: missing unresolved/remaining boundary"
    )

    for placeholder in PLACEHOLDERS:
        assert placeholder.lower() not in lower, f"{label}: placeholder {placeholder!r}"
    for pattern in HYPE_PATTERNS:
        assert not re.search(pattern, text, flags=re.IGNORECASE), (
            f"{label}: prohibited hype/overclaim pattern {pattern!r}"
        )

    return {
        "path": str(path.relative_to(ROOT)),
        "formal_statements": theorem_count,
        "proof_blocks": proof_count,
        "application_boundary": True,
        "unresolved_boundary": True,
    }


def audit_central_files() -> dict[str, object]:
    reports: dict[str, object] = {}
    for path in CENTRAL_FILES:
        text = read(path)
        assert len(text.split()) >= 150, f"central file too thin: {path.name}"
        for placeholder in PLACEHOLDERS:
            assert placeholder.lower() not in text.lower(), (
                f"{path.name}: placeholder {placeholder!r}"
            )
        reports[path.name] = {"words": len(text.split())}

    application_text = read(PAPERS / "FIVE_PAPER_APPLICATION_MAP_R3_2026-08-25.md")
    assert application_text.count("**Do not claim:**") >= 15

    review_text = read(PAPERS / "FIVE_PAPER_REVIEW_SYNTHESIS_R5_2026-08-25.md")
    for paper in ("Paper A decision", "Paper B decision", "Paper C decision", "Paper D decision", "Non-quantum decision"):
        assert paper in review_text, f"review synthesis missing {paper}"

    atomic_text = read(PAPERS / "FIVE_PAPER_ATOMIC_VERIFICATION_R8_2026-08-25.md")
    for status in ("VERIFIED", "FINITE_REPLAY", "EXTERNAL_DONOR", "UNRESOLVED", "NOT_CLAIMED"):
        assert status in atomic_text, f"atomic ledger missing status {status}"

    skill_text = read(PAPERS / "FIVE_PAPER_SKILL_APPLICATION_R3_2026-08-25.md")
    assert "fefc3f138e9ad30a56e35f50cc44f06850ccc89d" in skill_text
    assert "natural-scholarly-prose" in skill_text
    assert "atomic-claim-verification" in skill_text

    return reports


def run_finite_verifier() -> dict[str, object]:
    verifier = PAPERS / "verify_five_math_extensions_r4_v2.py"
    completed = subprocess.run(
        [sys.executable, str(verifier)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    report = json.loads(completed.stdout)
    assert report.get("status") == "PASS"
    return report


def main() -> None:
    result = {
        "addenda": {label: audit_addendum(label, path) for label, path in ADDENDA.items()},
        "central_files": audit_central_files(),
        "finite_verifier": run_finite_verifier(),
        "audit_status": "PASS",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
