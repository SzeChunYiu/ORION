#!/usr/bin/env python3
"""Fail-closed checks for the ORION-Q / ORION-QG publication-synthesis branch.

This checker grants no scientific or submission authority.  It protects the publication
cut from accidental science mutation and checks a small set of publication invariants.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_CUT = "ca7df1055a43f97eaf8d142a62011c4c261af368"

REQUIRED = [
    "papers/Q_QG_NATURE_SKILLS_PUBLICATION_CLOSURE_V1.md",
    "papers/Q_QG_PUBLICATION_READINESS_V2.md",
    "papers/Q_QG_VENUE_TARGET_MATRIX_V1.md",
    "papers/Q_QG_DATA_CODE_AVAILABILITY_V1.md",
    "papers/Q_QG_REFERENCE_CANON_V1.md",
    "papers/Q_QG_VERIFIED_CORE_REFERENCES_V1.bib",
    "papers/Q_QG_FIGURE_CONTRACTS_V1.md",
    "papers/Q_QG_STATISTICS_AND_EVIDENCE_REPORTING_V1.md",
    "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V2.md",
    "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md",
    "papers/Q-paper-01-tare-expressivity/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-01-tare-expressivity/MOCK_REVIEW_V2.md",
    "papers/Q-paper-01-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md",
    "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V2.md",
    "papers/Q-paper-02-recursive-recovery/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-02-recursive-recovery/MOCK_REVIEW_V2.md",
    "papers/Q-paper-02-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json",
    "papers/Q-paper-03-dual-instrument/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-03-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md",
    "papers/Q-paper-04-typed-state/MANUSCRIPT_V2.md",
    "papers/Q-paper-04-typed-state/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-04-typed-state/MOCK_REVIEW_V2.md",
    "papers/Q-paper-04-typed-state/INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md",
    "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V2.md",
    "papers/QG-paper-01-compilation-regime-geometry/PUBLICATION_FOUNDATION_V2.md",
    "papers/QG-paper-01-compilation-regime-geometry/MOCK_REVIEW_V2.md",
    "papers/QG-paper-01-compilation-regime-geometry/CROSS_FAMILY_EVIDENCE_MATRIX_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/PUBLICATION_FOUNDATION_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/MOCK_REVIEW_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md",
]

PAPER_V2 = [
    "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V2.md",
    "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V2.md",
    "papers/Q-paper-04-typed-state/MANUSCRIPT_V2.md",
    "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V2.md",
]

SCIENCE_PREFIXES = (
    "research/extensions/orion-q/",
    "research/extensions/orion-qg/",
    "development/orion-q-max-r0/",
    "development/orion-qg-regime-geometry/",
    "development/orion-q-nlane-closure/",
)


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def git_changed_from_cut() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{EVIDENCE_CUT}..HEAD"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []

    # Existence gates.
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"MISSING_REQUIRED_FILE: {rel}", errors)

    if errors:
        for err in errors:
            print(err)
        return 1

    # Publication branch may add publication artifacts, but it may not rewrite the
    # frozen science whose outcomes it is synthesizing.
    try:
        changed = git_changed_from_cut()
    except Exception as exc:  # pragma: no cover - fail closed in CI
        fail(f"CANNOT_CHECK_GIT_DIFF: {exc}", errors)
        changed = []
    for rel in changed:
        if rel.startswith(SCIENCE_PREFIXES):
            fail(f"SCIENCE_MUTATED_AFTER_PUBLICATION_CUT: {rel}", errors)

    # Every V2 manuscript must visibly carry limitations/reproducibility and the cut.
    for rel in PAPER_V2:
        body = text(rel)
        if EVIDENCE_CUT not in body:
            fail(f"MISSING_EVIDENCE_CUT_BINDING: {rel}", errors)
        if "Limitation" not in body and "limitation" not in body:
            fail(f"MISSING_LIMITATIONS_BOUNDARY: {rel}", errors)
        if "Reproduc" not in body and "reproduc" not in body:
            fail(f"MISSING_REPRODUCIBILITY_SECTION: {rel}", errors)

    # Q1 stale-state guard: the old ledger called R6S/R6R open.  V2 must not.
    q1_ledger = text("papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md")
    required_q1_tokens = [
        "PROVEN-ALL-N",
        "PROSPECTIVE-BOUNDED",
        "REFUTED",
        "MAX_R6S_ALL_N_COMPOSITION",
        "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT",
    ]
    for token in required_q1_tokens:
        if token not in q1_ledger:
            fail(f"Q1_V2_MISSING_SYNCHRONIZED_TOKEN: {token}", errors)

    stale_q1_phrases = [
        "support-two sufficiency and the two-trade completeness identity for every n",
        "support-3 necessity: existence",
        "forward slot: MAX_R6S receipt, not present",
        "forward slot: MAX_R6R receipt, not present",
    ]
    lower_q1 = q1_ledger.lower()
    for phrase in stale_q1_phrases:
        if phrase.lower() in lower_q1:
            fail(f"Q1_V2_STALE_CLAIM: {phrase}", errors)

    # Q3 is intentionally not publication-ready before additional prospective outcomes.
    readiness = text("papers/Q_QG_PUBLICATION_READINESS_V2.md")
    q3_protocol = text(
        "papers/Q-paper-03-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md"
    )
    if "Q3" not in readiness or "BLOCK" not in readiness.upper():
        fail("Q3_FAIL_CLOSED_STATUS_NOT_VISIBLE", errors)
    if "QG-7d" not in q3_protocol or "QG-15c" not in q3_protocol:
        fail("Q3_PROSPECTIVE_INSTANCE_FREEZE_INCOMPLETE", errors)

    # Licence wording guard. A root licence did not exist at the publication cut, so
    # publication artifacts must not call ORION open-source until that changes through
    # an explicit owner decision and this checker is deliberately updated.
    publication_files = [p for p in changed if p.startswith("papers/")]
    for rel in publication_files:
        path = ROOT / rel
        if not path.is_file() or path.suffix.lower() not in {".md", ".tex", ".bib", ".json"}:
            continue
        body = path.read_text(encoding="utf-8", errors="replace").lower()
        for forbidden in ("orion is open-source", "orion is open source", "open-source orion"):
            if forbidden in body:
                fail(f"UNLICENSED_OPEN_SOURCE_WORDING: {rel}: {forbidden}", errors)

    # Cross-paper ownership markers must remain in the programme contracts.
    closure = text("papers/Q_QG_NATURE_SKILLS_PUBLICATION_CLOSURE_V1.md")
    for token in ("Q1", "Q2", "Q3", "Q4", "QG1", "QG2", "authority"):
        if token.lower() not in closure.lower():
            fail(f"PORTFOLIO_CONTRACT_MISSING: {token}", errors)

    # Reference/data/figure/statistics contracts are mandatory once added.
    for rel in (
        "papers/Q_QG_DATA_CODE_AVAILABILITY_V1.md",
        "papers/Q_QG_REFERENCE_CANON_V1.md",
        "papers/Q_QG_FIGURE_CONTRACTS_V1.md",
        "papers/Q_QG_STATISTICS_AND_EVIDENCE_REPORTING_V1.md",
    ):
        body = text(rel)
        if "Q1" not in body or "QG2" not in body:
            fail(f"PORTFOLIO_AUDIT_INCOMPLETE: {rel}", errors)

    if errors:
        print("Q_QG_PUBLICATION_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_PUBLICATION_CHECK=PASS")
    print(f"EVIDENCE_CUT={EVIDENCE_CUT}")
    print(f"CHANGED_FILES_FROM_CUT={len(changed)}")
    print("SCIENTIFIC_RECEIPT_MUTATIONS=0")
    print("Q3_PUBLICATION_AUTHORITY=BLOCKED_PENDING_PROSPECTIVE_OUTCOMES")
    print("SUBMISSION_AUTHORITY=NOT_GRANTED_BY_THIS_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
