#!/usr/bin/env python3
"""Fail-closed checks for the ORION-Q / ORION-QG publication-synthesis branch.

This checker grants no scientific or submission authority. It protects pre-existing frozen
science from publication-owned mutation and enforces final-manuscript / evidence-cut bindings.
Q3 is the one prospectively authorized science extension in the original publication chronology;
only its exact, newly-created QG19/QG20 protocol/analyzer/result paths are allowed through the
science guard. A pull-request merge base scopes branch-owned changes; it does not approve the
base's scientific content or weaken the original-cut chronology checks.

For a repository-side materialization job, ``ORION_PUBLICATION_SCOPE_BASE`` may name the exact
commit at which the materializer started. This changes only the *branch-owned mutation* denominator;
all original-cut chronology, required-artifact, claim-boundary and evidence-binding checks remain
active. Callers using this override must also verify that the protected science roots remain
unchanged from that commit through the final materialized commit.
"""

from __future__ import annotations

import os
import pathlib
import re
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
    "papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    "papers/orion-05-tare-expressivity/CLAIM_LEDGER_V2.md",
    "papers/orion-05-tare-expressivity/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-05-tare-expressivity/MOCK_REVIEW_V2.md",
    "papers/orion-05-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md",
    "papers/orion-05-tare-expressivity/TARE_FULLTEXT_DONOR_BOUNDARY_V3.md",
    "papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md",
    "papers/orion-06-recursive-recovery/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-06-recursive-recovery/MOCK_REVIEW_V2.md",
    "papers/orion-06-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json",
    "papers/orion-06-recursive-recovery/Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json",
    "papers/orion-06-recursive-recovery/check_transition_graph.py",
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
    "papers/orion-08-typed-state/MANUSCRIPT_V3.md",
    "papers/orion-08-typed-state/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-08-typed-state/MOCK_REVIEW_V2.md",
    "papers/orion-08-typed-state/INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md",
    "papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md",
    "papers/orion-09-compilation-regime-geometry/PUBLICATION_FOUNDATION_V3.md",
    "papers/orion-09-compilation-regime-geometry/CROSS_FAMILY_EVIDENCE_MATRIX_V3.md",
    "papers/orion-09-compilation-regime-geometry/FIGURE_CONTRACT_V3.md",
    "papers/orion-09-compilation-regime-geometry/MOCK_REVIEW_V2.md",
    "papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md",
    "papers/orion-10-certified-static-forecasting/PUBLICATION_FOUNDATION_V2.md",
    "papers/orion-10-certified-static-forecasting/MOCK_REVIEW_V2.md",
    "papers/orion-10-certified-static-forecasting/FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md",
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


def _verified_ref(ref: str) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    resolved = proc.stdout.strip()
    if not resolved:
        raise RuntimeError(f"empty commit resolution for {ref}")
    return resolved


def changed_for_publication_branch() -> tuple[str, str, list[str]]:
    target = publication_head()
    explicit_scope_base = os.environ.get("ORION_PUBLICATION_SCOPE_BASE", "").strip()
    base_name = os.environ.get("GITHUB_BASE_REF", "").strip()

    if explicit_scope_base:
        # This override is for a caller that freezes the exact repository commit
        # before publication materialization begins. It does not alter ORIGINAL_CUT
        # chronology checks elsewhere in this program.
        scope_base = _verified_ref(explicit_scope_base)
    elif base_name:
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


R0_DOUBLE_PREFIX = re.compile(rb"ORION[ -]ORION-(\d{2})")


def blob_at(ref: str, rel: str) -> bytes | None:
    proc = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout if proc.returncode == 0 else None


def is_r0_rebind_only(scope_base: str, target: str, rel: str) -> bool:
    base = blob_at(scope_base, rel)
    head = blob_at(target, rel)
    if base is None or head is None:
        return False
    return R0_DOUBLE_PREFIX.sub(rb"ORION-\1", base) == head


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
            if path_exists_at(scope_base, rel):
                errors.append(f"Q3_AUTHORIZED_EXISTING_PATH_MUTATED_OR_DELETED:{rel}")
            elif path_exists_at(ORIGINAL_CUT, rel):
                errors.append(f"Q3_AUTHORIZED_PATH_WAS_NOT_NEW:{rel}")
            elif rel not in authorized_q3_present:
                errors.append(f"Q3_AUTHORIZED_NEW_PATH_MISSING_AT_HEAD:{rel}")
            continue
        if is_r0_rebind_only(scope_base, target, rel):
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

    q1_ledger = text("papers/orion-05-tare-expressivity/CLAIM_LEDGER_V2.md")
    for token in ("PROVEN-ALL-N", "PROSPECTIVE-BOUNDED", "REFUTED",
                  "MAX_R6S_ALL_N_COMPOSITION", "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT"):
        if token not in q1_ledger:
            errors.append(f"Q1_MISSING_SYNCHRONIZED_TOKEN:{token}")
    q1 = text("papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md").lower()
    for token in ("user-selectable", "non-unique tag", "canonical anticommuting", "donor-exposed"):
        if token not in q1:
            errors.append(f"Q1_DONOR_SUBTRACTION_MISSING:{token}")

    q2 = text("papers/orion-06-recursive-recovery/MANUSCRIPT_V3.md").lower()
    for token in ("23 result nodes", "16 are eligible", "7 excluded",
                  "scientistone", "scienceagentbench", "astabench"):
        if token not in q2:
            errors.append(f"Q2_MISSING_METHOD_OR_DONOR_TOKEN:{token}")

    q3 = text("papers/orion-07-dual-instrument/MANUSCRIPT_V3.md").lower()
    for token in ("prospective case series is now complete", "n=3", "not a validation guarantee",
                  "outside-cone sharpness", "objective-scope obstruction", "qet"):
        if token not in q3:
            errors.append(f"Q3_MISSING_COMPLETION_OR_DONOR_TOKEN:{token}")
    q3_completion = text("papers/orion-07-dual-instrument/Q3_COMPLETION_RECEIPT_V3.md")
    if Q3_COMPLETE_TERMINAL not in q3_completion:
        errors.append("Q3_COMPLETION_TERMINAL_MISSING")

    q4 = text("papers/orion-08-typed-state/MANUSCRIPT_V3.md").lower()
    for token in ("stale", "contextnest", "downstream-decision paper", "exact synthetic"):
        if token not in q4:
            errors.append(f"Q4_DONOR_OR_SCOPE_BOUNDARY_MISSING:{token}")

    qg1 = text("papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md").lower()
    for token in ("preprint-specific companion", "cross-family evidence matrix", "proof-derived ceiling",
                  "objective certificate", "representation identifiability", "qet"):
        if token not in qg1:
            errors.append(f"QG1_MISSING_INTEGRATION_OR_DONOR_TOKEN:{token}")

    qg2 = text("papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md").lower()
    for token in ("preprint-specific companion", "qet", "layered authority", "not a generic quantum-cost model"):
        if token not in qg2:
            errors.append(f"QG2_MISSING_SCOPE_OR_DONOR_TOKEN:{token}")

    if errors:
        print("Q_QG_PUBLICATION_CHECK=FAIL")
        print(f"PUBLICATION_DIFF_TARGET={target}")
        print(f"PUBLICATION_DIFF_SCOPE_BASE={scope_base}")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_PUBLICATION_CHECK=PASS")
    print(f"PUBLICATION_DIFF_TARGET={target}")
    print(f"PUBLICATION_DIFF_SCOPE_BASE={scope_base}")
    print(f"PUBLICATION_CHANGED_PATHS={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
