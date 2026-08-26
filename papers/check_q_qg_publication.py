#!/usr/bin/env python3
"""Fail-closed checks for the ORION-Q / ORION-QG publication-synthesis branch.

This checker grants no scientific or submission authority. It protects pre-existing frozen
science from publication-owned mutation and enforces final-manuscript / evidence-cut bindings.
Q3 is the one prospectively authorized science extension in the original publication chronology;
only its exact, newly-created QG19/QG20 protocol/analyzer/result paths are allowed through the
science guard. A pull-request merge base scopes branch-owned changes; it does not approve the
base's scientific content or weaken the original-cut chronology checks.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGINAL_CUT = "ca7df1055a43f97eaf8d142a62011c4c261af368"
QG1_REFRESH_CUT = "c5ba39fef4f25c46de5fb69bf07f50530f4693ca"
Q3_RESULT_CUT = "ca561ada07301ee7e45fc10e195dce8f077ea50c"
Q3_COMPLETE_TERMINAL = "Q3_PROSPECTIVE_CASE_SERIES_COMPLETE__N3_VALID__AGREEMENT_NOT_VALIDATION_COUNTEREXAMPLE_OBSERVED__NO_RELIABILITY_GENERALIZATION"

REQUIRED = [
    "papers/Q_QG_NATURE_SKILLS_PUBLICATION_CLOSURE_V1.md",
    "papers/Q_QG_PUBLICATION_READINESS_V3.md",
    "papers/archive/2026-08-pre-unification/Q_QG_VENUE_TARGET_MATRIX_V1.md",
    "papers/Q_QG_DATA_CODE_AVAILABILITY_V1.md",
    "papers/Q_QG_REFERENCE_CANON_V1.md",
    "papers/Q_QG_VERIFIED_CORE_REFERENCES_V1.bib",
    "papers/Q2_Q3_VERIFIED_BENCHMARK_REFERENCES_V1.bib",
    "papers/Q_QG_FIGURE_CONTRACTS_V1.md",
    "papers/Q_QG_STATISTICS_AND_EVIDENCE_REPORTING_V1.md",
    "papers/Q_QG_POSTCUT_FRESHNESS_ADJUDICATION_V1.md",
    "papers/Q_QG_CONSISTENCY_SWEEP_V1.md",
    "papers/Q_QG_SECOND_REVIEW_SYNTHESIS_V1.md",
    # Q1 final publication draft + evidence contracts
    "papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    "papers/orion-05-tare-expressivity/CLAIM_LEDGER_V2.md",
    "papers/orion-05-tare-expressivity/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-05-tare-expressivity/MOCK_REVIEW_V2.md",
    "papers/orion-05-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md",
    "papers/orion-05-tare-expressivity/TARE_FULLTEXT_DONOR_BOUNDARY_V3.md",
    # Q2 final V3
    "papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md",
    "papers/orion-06-recursive-recovery/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-06-recursive-recovery/MOCK_REVIEW_V2.md",
    "papers/orion-06-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json",
    "papers/orion-06-recursive-recovery/Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json",
    "papers/orion-06-recursive-recovery/check_transition_graph.py",
    # Q3 final V3 + prospective custody/completion
    "papers/orion-07-dual-instrument/MANUSCRIPT_V3.md",
    "papers/orion-07-dual-instrument/CLAIM_LEDGER_V2.md",
    "papers/orion-07-dual-instrument/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-07-dual-instrument/Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md",
    "papers/orion-07-dual-instrument/Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md",
    "papers/orion-07-dual-instrument/Q3_CONTAMINATION_DISPOSITION_2026-08-22.md",
    "papers/orion-07-dual-instrument/Q3_D2_D3_DISPOSITION_V2.md",
    "papers/orion-07-dual-instrument/Q3_NOVELTY_REFRESH_2026-08-22.md",
    "papers/orion-07-dual-instrument/Q3_COMPLETION_RECEIPT_V3.md",
    "papers/orion-07-dual-instrument/check_q3_completion.py",
    "papers/orion-07-dual-instrument/check_q3_result_bindings.py",
    "papers/orion-07-dual-instrument/replay_q3_v0.py",
    "research/extensions/orion-qg/QG19_OUTSIDE_CONE_SHARPNESS_RESULTS.json",
    "research/extensions/orion-qg/QG20_SIXLCU_OBJECTIVE_SCOPE_RESULTS.json",
    # Q4 final V3
    "papers/orion-08-typed-state/MANUSCRIPT_V3.md",
    "papers/orion-08-typed-state/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-08-typed-state/MOCK_REVIEW_V2.md",
    "papers/orion-08-typed-state/INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md",
    # QG1 final refreshed V3
    "papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md",
    "papers/orion-09-compilation-regime-geometry/PUBLICATION_FOUNDATION_V3.md",
    "papers/orion-09-compilation-regime-geometry/CROSS_FAMILY_EVIDENCE_MATRIX_V3.md",
    "papers/orion-09-compilation-regime-geometry/FIGURE_CONTRACT_V3.md",
    "papers/orion-09-compilation-regime-geometry/MOCK_REVIEW_V2.md",
    # QG2 final V3
    "papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md",
    "papers/orion-10-certified-static-forecasting/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-10-certified-static-forecasting/MOCK_REVIEW_V2.md",
    "papers/orion-10-certified-static-forecasting/FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md",
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
    ("Q1", "papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("Q2", "papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("Q3", "papers/orion-07-dual-instrument/MANUSCRIPT_V3.md", Q3_RESULT_CUT),
    ("Q4", "papers/orion-08-typed-state/MANUSCRIPT_V3.md", ORIGINAL_CUT),
    ("QG1", "papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md", QG1_REFRESH_CUT),
    ("QG2", "papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md", ORIGINAL_CUT),
]

SCIENCE_PREFIXES = (
    "research/extensions/orion-q/",
    "research/extensions/orion-qg/",
    "development/orion-q-max-r0/",
    "development/orion-qg-regime-geometry/",
    "development/orion-q-nlane-closure/",
)

# These are the only newly-created scientific paths authorized by Q3's prospective protocol.
Q3_AUTHORIZED_NEW_SCIENCE = {
    "development/orion-qg-regime-geometry/QG19_OUTSIDE_CONE_SHARPNESS_PROTOCOL_V1.md",
    "development/orion-qg-regime-geometry/QG20_SIXLCU_OBJECTIVE_SCOPE_PROTOCOL_V1.md",
    "research/extensions/orion-qg/qg19_outside_cone_sharpness.py",
    "research/extensions/orion-qg/qg20_sixlcu_objective_scope.py",
    "research/extensions/orion-qg/QG19_OUTSIDE_CONE_SHARPNESS_RESULTS.json",
    "research/extensions/orion-qg/QG20_SIXLCU_OBJECTIVE_SCOPE_RESULTS.json",
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def publication_head() -> str:
    head_ref = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if head_ref:
        candidate = f"origin/{head_ref}"
        subprocess.run(["git", "rev-parse", "--verify", candidate], cwd=ROOT, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return candidate
    return "HEAD"


def changed_for_publication_branch() -> tuple[str, str, list[str]]:
    target = publication_head()
    base_name = os.environ.get("GITHUB_BASE_REF", "").strip()
    if base_name:
        base_ref = f"origin/{base_name}"
        subprocess.run(
            ["git", "rev-parse", "--verify", base_ref],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        merge_base_proc = subprocess.run(
            ["git", "merge-base", base_ref, target],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        scope_base = merge_base_proc.stdout.strip()
        if not scope_base:
            raise RuntimeError(f"empty merge base for {base_ref} and {target}")
    elif os.environ.get("GITHUB_HEAD_REF", "").strip():
        raise RuntimeError("GITHUB_HEAD_REF is set but GITHUB_BASE_REF is missing")
    else:
        scope_base = ORIGINAL_CUT

    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{scope_base}..{target}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return target, scope_base, [x.strip() for x in proc.stdout.splitlines() if x.strip()]


def path_exists_at(ref: str, rel: str) -> bool:
    proc = subprocess.run(["git", "cat-file", "-e", f"{ref}:{rel}"], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode == 0


def science_change_errors(
    scope_base: str, target: str, changed: list[str]
) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    authorized_q3_present = {
        rel for rel in Q3_AUTHORIZED_NEW_SCIENCE if path_exists_at(target, rel)
    }
    for rel in changed:
        if not rel.startswith(SCIENCE_PREFIXES):
            continue
        if rel in Q3_AUTHORIZED_NEW_SCIENCE:
            # An authorized path already present at the PR scope boundary is frozen for this PR.
            # The scope boundary is not an approval or a replacement for ORIGINAL_CUT chronology.
            if path_exists_at(scope_base, rel):
                errors.append(f"Q3_AUTHORIZED_EXISTING_PATH_MUTATED_OR_DELETED:{rel}")
            elif path_exists_at(ORIGINAL_CUT, rel):
                errors.append(f"Q3_AUTHORIZED_PATH_WAS_NOT_NEW:{rel}")
            elif rel not in authorized_q3_present:
                errors.append(f"Q3_AUTHORIZED_NEW_PATH_MISSING_AT_HEAD:{rel}")
            continue
        errors.append(f"PREEXISTING_OR_UNAUTHORIZED_SCIENCE_MUTATED_BY_PUBLICATION_BRANCH:{rel}")
    return errors, authorized_q3_present


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
        target, scope_base, changed = changed_for_publication_branch()
    except Exception as exc:  # pragma: no cover
        errors.append(f"CANNOT_CHECK_GIT_DIFF:{exc}")
        target, scope_base, changed = "UNRESOLVED", "UNRESOLVED", []

    science_errors, authorized_q3_present = science_change_errors(scope_base, target, changed)
    errors.extend(science_errors)
    for rel in authorized_q3_present:
        # ORIGINAL_CUT remains the chronology authority even when a PR scope base is newer.
        if path_exists_at(ORIGINAL_CUT, rel):
            errors.append(f"Q3_AUTHORIZED_PATH_WAS_NOT_NEW:{rel}")
    if authorized_q3_present != Q3_AUTHORIZED_NEW_SCIENCE:
        errors.append(
            "Q3_AUTHORIZED_SCIENCE_SET_INCOMPLETE:"
            f"{sorted(Q3_AUTHORIZED_NEW_SCIENCE - authorized_q3_present)}"
        )

    for paper_id, rel, cut in FINAL_MANUSCRIPTS:
        body = text(rel)
        if cut not in body:
            errors.append(f"MISSING_PAPER_SPECIFIC_CUT:{paper_id}:{cut}")
        if "Limitation" not in body and "limitation" not in body:
            errors.append(f"MISSING_LIMITATIONS_BOUNDARY:{paper_id}")
        if "Reproduc" not in body and "reproduc" not in body:
            errors.append(f"MISSING_REPRODUCIBILITY_SECTION:{paper_id}")

    # Q1: synchronized science + full donor subtraction.
    q1_ledger = text("papers/orion-05-tare-expressivity/CLAIM_LEDGER_V2.md")
    for token in ("PROVEN-ALL-N", "PROSPECTIVE-BOUNDED", "REFUTED",
                  "MAX_R6S_ALL_N_COMPOSITION", "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT"):
        if token not in q1_ledger:
            errors.append(f"Q1_MISSING_SYNCHRONIZED_TOKEN:{token}")
    q1 = text("papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md").lower()
    for token in ("user-selectable", "non-unique tag", "canonical anticommuting", "donor-exposed"):
        if token not in q1:
            errors.append(f"Q1_DONOR_SUBTRACTION_MISSING:{token}")

    # Q2: graph denominator/audit + scientific-agent donors must be load-bearing.
    q2 = text("papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md").lower()
    for token in ("23 result nodes", "13 asserted successor edges", "51-receipt", "scienceagentbench"):
        if token not in q2:
            errors.append(f"Q2_V3_GRAPH_OR_DONOR_MISSING:{token}")
    if "declared publication graph" not in q2 and "declared bounded graph" not in q2 and "publication graph" not in q2:
        errors.append("Q2_V3_GRAPH_SCOPE_WORDING_MISSING")

    # Q3: completion, negative result and anti-reliability framing must be visible.
    readiness = text("papers/Q_QG_PUBLICATION_READINESS_V3.md")
    q3 = text("papers/orion-07-dual-instrument/MANUSCRIPT_V3.md").lower()
    q3_ledger = text("papers/orion-07-dual-instrument/CLAIM_LEDGER_V2.md")
    if Q3_COMPLETE_TERMINAL not in readiness or Q3_COMPLETE_TERMINAL not in q3_ledger:
        errors.append("Q3_COMPLETE_TERMINAL_NOT_BOUND")
    for token in ("39,489", "zero p0/label mismatches", "agreement did not imply", "contaminated", "three valid units"):
        if token not in q3:
            errors.append(f"Q3_V3_DECISIVE_RESULT_OR_BOUNDARY_MISSING:{token}")
    for forbidden in ("100% agreement", "two-thirds diagnostic accuracy", "100% move accuracy"):
        # Those phrases may occur only in an explicit prohibition context; require the manuscript's
        # anti-summary sentence if present rather than banning the literal text.
        if forbidden in q3 and "we do **not** summarize this as" not in q3:
            errors.append(f"Q3_ILLEGAL_AGGREGATE_REPORTING:{forbidden}")

    # Q4: stale memory/context governance/P13 are distinct from bounded Q4 result.
    q4 = text("papers/orion-08-typed-state/MANUSCRIPT_V3.md").lower()
    for token in ("stale", "contextnest", "scope invalidation", "p13", "matched visible information"):
        if token not in q4:
            errors.append(f"Q4_V3_BOUNDARY_MISSING:{token}")

    # QG1: current-main refresh really entered final manuscript.
    qg1 = text("papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md").lower()
    for token in ("kappa_r6i = 1", "qg16", "syndrome", "proof-derived ceiling", "outside the cone"):
        if token not in qg1:
            errors.append(f"QG1_V3_FRESHNESS_RESULT_MISSING:{token}")

    # QG2: current static-analysis donors and anti-accuracy framing visible.
    qg2 = text("papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md").lower()
    for token in ("qet", "qualtran", "99.99", "forecastcertificate", "timing is secondary"):
        if token not in qg2:
            errors.append(f"QG2_V3_BOUNDARY_MISSING:{token}")
    if "true optimum is 10" not in qg2 or "return 11" not in qg2:
        errors.append("QG2_V3_DECISIVE_COUNTEREXAMPLE_NOT_VISIBLE")

    # No root reuse licence existed at the original cut. Enforce on actual final manuscripts.
    for _paper_id, rel, _cut in FINAL_MANUSCRIPTS:
        body = text(rel).lower()
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
    print(f"Q3_RESULT_CUT={Q3_RESULT_CUT}")
    print(f"PUBLICATION_HEAD={target}")
    print(f"PUBLICATION_CHANGE_SCOPE_BASE={scope_base}")
    print(f"PUBLICATION_BRANCH_CHANGED_FILES={len(changed)}")
    print("FINAL_MANUSCRIPTS=Q1V3,Q2V3,Q3V3,Q4V3,QG1V3,QG2V3")
    print("PREEXISTING_SCIENTIFIC_RECEIPT_MUTATIONS_BY_PUBLICATION_BRANCH=0")
    print(f"Q3_AUTHORIZED_NEW_SCIENCE_FILES={len(authorized_q3_present)}")
    print(f"Q3_PUBLICATION_AUTHORITY={Q3_COMPLETE_TERMINAL}")
    print("SUBMISSION_AUTHORITY=NOT_GRANTED_BY_THIS_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
