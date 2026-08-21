#!/usr/bin/env python3
"""Fail-closed checks for the ORION-Q / ORION-QG publication-synthesis branch.

This checker grants no scientific or submission authority. It protects publication-owned
changes from mutating frozen science and enforces final-manuscript / evidence-cut bindings.
On pull_request events GitHub checks out a synthetic merge commit, so branch-owned changes
are measured against the PR head ref rather than the merge ref.
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
    "papers/Q2_Q3_VERIFIED_BENCHMARK_REFERENCES_V1.bib",
    "papers/Q_QG_FIGURE_CONTRACTS_V1.md",
    "papers/Q_QG_STATISTICS_AND_EVIDENCE_REPORTING_V1.md",
    "papers/Q_QG_POSTCUT_FRESHNESS_ADJUDICATION_V1.md",
    "papers/Q_QG_CONSISTENCY_SWEEP_V1.md",
    # Q1 final publication draft + evidence contracts
    "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md",
    "papers/Q-paper-01-tare-expressivity/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-01-tare-expressivity/MOCK_REVIEW_V2.md",
    "papers/Q-paper-01-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md",
    "papers/Q-paper-01-tare-expressivity/TARE_FULLTEXT_DONOR_BOUNDARY_V3.md",
    # Q2 final V3
    "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V3.md",
    "papers/Q-paper-02-recursive-recovery/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-02-recursive-recovery/MOCK_REVIEW_V2.md",
    "papers/Q-paper-02-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json",
    "papers/Q-paper-02-recursive-recovery/check_transition_graph.py",
    # Q3 intentionally blocked
    "papers/Q-paper-03-dual-instrument/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-03-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md",
    # Q4 final V3
    "papers/Q-paper-04-typed-state/MANUSCRIPT_V3.md",
    "papers/Q-paper-04-typed-state/PUBLICATION_FOUNDATION_V2.md",
    "papers/Q-paper-04-typed-state/MOCK_REVIEW_V2.md",
    "papers/Q-paper-04-typed-state/INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md",
    # QG1 final refreshed V3
    "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md",
    "papers/QG-paper-01-compilation-regime-geometry/PUBLICATION_FOUNDATION_V3.md",
    "papers/QG-paper-01-compilation-regime-geometry/CROSS_FAMILY_EVIDENCE_MATRIX_V3.md",
    "papers/QG-paper-01-compilation-regime-geometry/MOCK_REVIEW_V2.md",
    # QG2 final V3
    "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V3.md",
    "papers/QG-paper-02-certified-static-forecasting/PUBLICATION_FOUNDATION_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/MOCK_REVIEW_V2.md",
    "papers/QG-paper-02-certified-static-forecasting/FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md",
    # nearest-donor cards
    "papers/literature_cards/TARE_2601.05740_PAPER_CARD_V1.md",
    "papers/literature_cards/ISA_3572895_PAPER_CARD_V1.md",
    "papers/literature_cards/ScientistOne_2605.26340_PAPER_CARD_V1.md",
    "papers/literature_cards/ScienceAgentBench_2410.05080_PAPER_CARD_V1.md",
    "papers/literature_cards/AstaBench_2510.21652_PAPER_CARD_V1.md",
    "papers/literature_cards/STALE_2605.06527_PAPER_CARD_V1.md",
    "papers/literature_cards/ContextNest_2607.02116_PAPER_CARD_V1.md",
    "papers/literature_cards/Qet_2604.03971_PAPER_CARD_V1.md",
]

FINAL_MANUSCRIPTS = [
    ("Q1", "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("Q2", "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("Q4", "papers/Q-paper-04-typed-state/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("QG1", "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md", QG1_REFRESH_CUT),
    ("QG2", "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V3.md", ORIGINAL_CUT),
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


def changed_from_original_cut() -> tuple[str, list[str]]:
    target = publication_head()
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{ORIGINAL_CUT}..{target}"],
        cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return target, [x.strip() for x in proc.stdout.splitlines() if x.strip()]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"MISSING_REQUIRED_FILE:{rel}")
    if errors:
        print("Q_QG_PUBLICATION_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    try:
        target, changed = changed_from_original_cut()
    except Exception as exc:  # pragma: no cover
        errors.append(f"CANNOT_CHECK_GIT_DIFF:{exc}")
        target, changed = "UNRESOLVED", []
    for rel in changed:
        if rel.startswith(SCIENCE_PREFIXES):
            errors.append(f"SCIENCE_MUTATED_BY_PUBLICATION_BRANCH:{rel}")

    for paper_id, rel, cut in FINAL_MANUSCRIPTS:
        body = text(rel)
        if cut not in body:
            errors.append(f"MISSING_PAPER_SPECIFIC_CUT:{paper_id}:{cut}")
        if "Limitation" not in body and "limitation" not in body:
            errors.append(f"MISSING_LIMITATIONS_BOUNDARY:{paper_id}")
        if "Reproduc" not in body and "reproduc" not in body:
            errors.append(f"MISSING_REPRODUCIBILITY_SECTION:{paper_id}")

    # Q1: synchronized science + full donor subtraction.
    q1_ledger = text("papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md")
    for token in (
        "PROVEN-ALL-N", "PROSPECTIVE-BOUNDED", "REFUTED",
        "MAX_R6S_ALL_N_COMPOSITION", "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT",
    ):
        if token not in q1_ledger:
            errors.append(f"Q1_MISSING_SYNCHRONIZED_TOKEN:{token}")
    q1 = text("papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md").lower()
    for token in ("user-selectable", "non-unique tag", "canonical anticommuting", "donor-exposed"):
        if token not in q1:
            errors.append(f"Q1_DONOR_SUBTRACTION_MISSING:{token}")

    # Q2: machine-readable denominator/audit must be load-bearing.
    q2 = text("papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V3.md").lower()
    for token in ("23 result nodes", "13 asserted successor edges", "scienceagentbench", "declared publication graph"):
        if token not in q2:
            errors.append(f"Q2_V3_GRAPH_OR_DONOR_MISSING:{token}")

    # Q4: stale memory/context governance/P13 are distinct from bounded Q4 result.
    q4 = text("papers/Q-paper-04-typed-state/MANUSCRIPT_V3.md").lower()
    for token in ("stale", "contextnest", "scope invalidation", "p13", "matched visible information"):
        if token not in q4:
            errors.append(f"Q4_V3_BOUNDARY_MISSING:{token}")

    # QG1: current-main refresh really entered final manuscript.
    qg1 = text("papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md").lower()
    for token in ("kappa_r6i = 1", "qg16", "syndrome", "proof-derived ceiling", "outside the cone"):
        if token not in qg1:
            errors.append(f"QG1_V3_FRESHNESS_RESULT_MISSING:{token}")

    # QG2: current static-analysis donors and anti-accuracy framing visible.
    qg2 = text("papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V3.md").lower()
    for token in ("qet", "qualtran", "10<11", "99.99", "forecastcertificate", "timing is secondary"):
        if token not in qg2:
            errors.append(f"QG2_V3_BOUNDARY_MISSING:{token}")

    # Q3 remains intentionally blocked.
    readiness = text("papers/Q_QG_PUBLICATION_READINESS_V2.md")
    q3p = text("papers/Q-paper-03-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md")
    if Q3_BLOCKED_TERMINAL not in readiness:
        errors.append("Q3_FAIL_CLOSED_TERMINAL_NOT_VISIBLE")
    if "QG-7d" not in q3p or "QG-15c" not in q3p:
        errors.append("Q3_PROSPECTIVE_INSTANCE_FREEZE_INCOMPLETE")

    # No root reuse licence existed at the original cut; do not grant rights via prose.
    for rel in [p for p in changed if p.startswith("papers/")]:
        path = ROOT / rel
        if not path.is_file() or path.suffix.lower() not in {".md", ".tex", ".bib", ".json"}:
            continue
        body = path.read_text(encoding="utf-8", errors="replace").lower()
        for forbidden in ("orion is open-source", "orion is open source", "open-source orion"):
            if forbidden in body:
                errors.append(f"UNLICENSED_OPEN_SOURCE_WORDING:{rel}:{forbidden}")

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
    print("FINAL_MANUSCRIPTS=Q1V3,Q2V3,Q4V3,QG1V3,QG2V3")
    print("SCIENTIFIC_RECEIPT_MUTATIONS_BY_PUBLICATION_BRANCH=0")
    print(f"Q3_PUBLICATION_AUTHORITY={Q3_BLOCKED_TERMINAL}")
    print("SUBMISSION_AUTHORITY=NOT_GRANTED_BY_THIS_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
