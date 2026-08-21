#!/usr/bin/env python3
"""Fail-closed checks for the ORION-Q / ORION-QG publication-synthesis branch.

This checker grants no scientific or submission authority. It protects publication-owned
changes from mutating the frozen science and enforces final-manuscript / evidence-cut
bindings. On pull_request events GitHub checks out a synthetic merge commit, so branch-owned
changes are measured against the PR head ref rather than that merge ref.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGINAL_CUT = "ca7df1055a43f97eaf8d142a62011c4c261af368"
QG1_REFRESH_CUT = "c5ba39fef4f25c46de5fb69bf07f50530f4693ca"
Q3_BLOCKED_TERMINAL = "SCIENTIFIC_SERIES_INCOMPLETE__CANNOT_CHECK_PEER_REVIEW_READY"

REQUIRED = [
    "papers/Q_QG_NATURE_SKILLS_PUBLICATION_CLOSURE_V1.md",
    "papers/Q_QG_PUBLICATION_READINESS_V2.md",
    "papers/Q_QG_VENUE_TARGET_MATRIX_V1.md",
    "papers/Q_QG_DATA_CODE_AVAILABILITY_V1.md",
    "papers/Q_QG_REFERENCE_CANON_V1.md",
    "papers/Q_QG_VERIFIED_CORE_REFERENCES_V1.bib",
    "papers/Q_QG_FIGURE_CONTRACTS_V1.md",
    "papers/Q_QG_STATISTICS_AND_EVIDENCE_REPORTING_V1.md",
    "papers/Q_QG_POSTCUT_FRESHNESS_ADJUDICATION_V1.md",
    # Q1 final publication draft + evidence contracts
    "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md",
    "papers/Q-paper-01-tare-expressivity/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-01-tare-expressivity/MOCK_REVIEW_V2.md",
    "papers/Q-paper-01-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md",
    "papers/Q-paper-01-tare-expressivity/TARE_FULLTEXT_DONOR_BOUNDARY_V3.md",
    # Q2
    "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V2.md",
    "papers/Q-paper-02-recursive-recovery/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-02-recursive-recovery/MOCK_REVIEW_V2.md",
    "papers/Q-paper-02-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json",
    "papers/Q-paper-02-recursive-recovery/check_transition_graph.py",
    # Q3 (intentionally scientifically blocked)
    "papers/Q-paper-03-dual-instrument/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-03-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md",
    # Q4
    "papers/Q-paper-04-typed-state/MANUSCRIPT_V2.md",
    "papers/Q-paper-04-typed-state/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-04-typed-state/MOCK_REVIEW_V2.md",
    "papers/Q-paper-04-typed-state/INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md",
    # QG1 final refreshed draft
    "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md",
    "papers/QG-paper-01-compilation-regime-geometry/PUBLICATION_FOUNDATION_V3.md",
    "papers/QG-paper-01-compilation-regime-geometry/CROSS_FAMILY_EVIDENCE_MATRIX_V3.md",
    "papers/QG-paper-01-compilation-regime-geometry/MOCK_REVIEW_V2.md",
    # QG2
    "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/PUBLICATION_FOUNDATION_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/MOCK_REVIEW_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md",
    # nearest-donor cards that changed publication boundaries
    "papers/literature_cards/TARE_2601.05740_PAPER_CARD_V1.md",
    "papers/literature_cards/ISA_3572895_PAPER_CARD_V1.md",
    "papers/literature_cards/ScientistOne_2605.26340_PAPER_CARD_V1.md",
    "papers/literature_cards/AstaBench_2510.21652_PAPER_CARD_V1.md",
    "papers/literature_cards/STALE_2605.06527_PAPER_CARD_V1.md",
    "papers/literature_cards/ContextNest_2607.02116_PAPER_CARD_V1.md",
    "papers/literature_cards/Qet_2604.03971_PAPER_CARD_V1.md",
]

FINAL_MANUSCRIPTS = [
    ("Q1", "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("Q2", "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V2.md", ORIGINAL_CUT),
    ("Q4", "papers/Q-paper-04-typed-state/MANUSCRIPT_V2.md", ORIGINAL_CUT),
    ("QG1", "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md", QG1_REFRESH_CUT),
    ("QG2", "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V2.md", ORIGINAL_CUT),
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


def publication_head() -> str:
    head_ref = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if head_ref:
        candidate = f"origin/{head_ref}"
        subprocess.run(
            ["git", "rev-parse", "--verify", candidate], cwd=ROOT, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        return candidate
    return "HEAD"


def git_changed_from_original_cut() -> tuple[str, list[str]]:
    target = publication_head()
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{ORIGINAL_CUT}..{target}"],
        cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return target, [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"MISSING_REQUIRED_FILE:{rel}", errors)
    if errors:
        print("Q_QG_PUBLICATION_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    # Publication branch may synthesize paper artifacts only; it must not mutate any
    # scientific receipt/protocol from the original branch base.
    try:
        target, changed = git_changed_from_original_cut()
    except Exception as exc:  # pragma: no cover
        fail(f"CANNOT_CHECK_GIT_DIFF:{exc}", errors)
        target, changed = "UNRESOLVED", []
    for rel in changed:
        if rel.startswith(SCIENCE_PREFIXES):
            fail(f"SCIENCE_MUTATED_BY_PUBLICATION_BRANCH:{rel}", errors)

    # Paper-specific scientific cuts. QG1 was explicitly reopened after a freshness
    # adjudication; the other completed papers intentionally retain the earlier cut.
    for paper_id, rel, cut in FINAL_MANUSCRIPTS:
        body = text(rel)
        if cut not in body:
            fail(f"MISSING_PAPER_SPECIFIC_CUT:{paper_id}:{rel}:{cut}", errors)
        if "Limitation" not in body and "limitation" not in body:
            fail(f"MISSING_LIMITATIONS_BOUNDARY:{paper_id}:{rel}", errors)
        if "Reproduc" not in body and "reproduc" not in body:
            fail(f"MISSING_REPRODUCIBILITY_SECTION:{paper_id}:{rel}", errors)

    # Q1 synchronized theorem/prospective/refutation state.
    q1_ledger = text("papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md")
    for token in (
        "PROVEN-ALL-N", "PROSPECTIVE-BOUNDED", "REFUTED",
        "MAX_R6S_ALL_N_COMPOSITION", "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT",
    ):
        if token not in q1_ledger:
            fail(f"Q1_V2_MISSING_SYNCHRONIZED_TOKEN:{token}", errors)
    for phrase in (
        "support-two sufficiency and the two-trade completeness identity for every n",
        "support-3 necessity: existence",
        "forward slot: MAX_R6S receipt, not present",
        "forward slot: MAX_R6R receipt, not present",
    ):
        if phrase.lower() in q1_ledger.lower():
            fail(f"Q1_STALE_CLAIM:{phrase}", errors)

    # Full-text donor subtraction must be visible in final Q1, not only a side audit.
    q1_final = text("papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md")
    for token in ("user-selectable", "non-unique Tag", "canonical anticommuting", "donor-exposed"):
        if token.lower() not in q1_final.lower():
            fail(f"Q1_FULLTEXT_DONOR_SUBTRACTION_NOT_IN_FINAL:{token}", errors)

    # QG1 freshness reopen must be real: V3 includes exact support1, objective cone and
    # proof-ceiling-versus-intrinsic distinction.
    qg1 = text("papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md")
    for token in ("kappa_R6I = 1", "QG16", "syndrome", "proof-derived ceiling", "outside the cone"):
        if token.lower() not in qg1.lower():
            fail(f"QG1_V3_FRESHNESS_RESULT_MISSING:{token}", errors)

    # Q3 remains intentionally blocked.
    readiness = text("papers/Q_QG_PUBLICATION_READINESS_V2.md")
    q3_protocol = text("papers/Q-paper-03-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md")
    if Q3_BLOCKED_TERMINAL not in readiness:
        fail("Q3_FAIL_CLOSED_TERMINAL_NOT_VISIBLE", errors)
    if "QG-7d" not in q3_protocol or "QG-15c" not in q3_protocol:
        fail("Q3_PROSPECTIVE_INSTANCE_FREEZE_INCOMPLETE", errors)

    # No root reuse licence existed at the original publication cut; do not grant
    # open-source rights through manuscript wording.
    publication_files = [p for p in changed if p.startswith("papers/")]
    for rel in publication_files:
        path = ROOT / rel
        if not path.is_file() or path.suffix.lower() not in {".md", ".tex", ".bib", ".json"}:
            continue
        body = path.read_text(encoding="utf-8", errors="replace").lower()
        for forbidden in ("orion is open-source", "orion is open source", "open-source orion"):
            if forbidden in body:
                fail(f"UNLICENSED_OPEN_SOURCE_WORDING:{rel}:{forbidden}", errors)

    # Portfolio ownership and audit artifacts.
    closure = text("papers/Q_QG_NATURE_SKILLS_PUBLICATION_CLOSURE_V1.md")
    for token in ("Q1", "Q2", "Q3", "Q4", "QG1", "QG2", "authority"):
        if token.lower() not in closure.lower():
            fail(f"PORTFOLIO_CONTRACT_MISSING:{token}", errors)
    for rel in (
        "papers/Q_QG_DATA_CODE_AVAILABILITY_V1.md",
        "papers/Q_QG_REFERENCE_CANON_V1.md",
        "papers/Q_QG_FIGURE_CONTRACTS_V1.md",
        "papers/Q_QG_STATISTICS_AND_EVIDENCE_REPORTING_V1.md",
        "papers/Q_QG_POSTCUT_FRESHNESS_ADJUDICATION_V1.md",
    ):
        body = text(rel)
        if "Q1" not in body or "QG2" not in body:
            fail(f"PORTFOLIO_AUDIT_INCOMPLETE:{rel}", errors)

    if errors:
        print("Q_QG_PUBLICATION_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_PUBLICATION_CHECK=PASS")
    print(f"ORIGINAL_CUT={ORIGINAL_CUT}")
    print(f"QG1_REFRESH_CUT={QG1_REFRESH_CUT}")
    print(f"PUBLICATION_HEAD={target}")
    print(f"PUBLICATION_BRANCH_CHANGED_FILES={len(changed)}")
    print("SCIENTIFIC_RECEIPT_MUTATIONS_BY_PUBLICATION_BRANCH=0")
    print(f"Q3_PUBLICATION_AUTHORITY={Q3_BLOCKED_TERMINAL}")
    print("SUBMISSION_AUTHORITY=NOT_GRANTED_BY_THIS_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
