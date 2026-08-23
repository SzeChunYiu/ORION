#!/usr/bin/env python3
"""Fail closed on accidental promotion of the audited Q1-Q4 candidate.

This checker validates the audit disposition and prospective-protocol boundary.
It grants no scientific, novelty, causal, model-attribution, or submission
authority.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent
MATRIX = ROOT / "PUBLICATION_GATE_MATRIX.json"
EXPECTED_MATRIX_SHA256 = "62c01cc8d0dc7ebe4982e571e65f6b2324a6ad9125e05491eec07e5fe610673f"
EXPECTED_CANDIDATE_COMMIT = "158fcb08b612ffc82f5a5d2bed4917409084ded8"
PROTOCOLS = {
    "Q2-P1": ROOT / "Q2_PROSPECTIVE_COMPARATIVE_PROTOCOL.md",
    "Q3-P1": ROOT / "Q3_P1_PROSPECTIVE_PROTOCOL.md",
    "Q4-P1": ROOT / "Q4_FACTORIAL_CONFIRMATION_PROTOCOL.md",
}
REPOSITORY_ROOT = ROOT.parents[1]


def git_bound_and_clean(path: pathlib.Path, label: str, errors: list[str]) -> None:
    rel = path.relative_to(REPOSITORY_ROOT)
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(rel)],
        cwd=REPOSITORY_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if tracked.returncode != 0:
        errors.append(f"NOT_GIT_TRACKED:{label}")
    bound = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel}"],
        cwd=REPOSITORY_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if bound.returncode != 0:
        errors.append(f"NOT_BOUND_AT_HEAD:{label}")
    clean = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", str(rel)],
        cwd=REPOSITORY_ROOT,
        check=False,
    )
    if clean.returncode != 0:
        errors.append(f"WORKTREE_DIFFERS_FROM_HEAD:{label}")


def main() -> int:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    errors: list[str] = []

    git_bound_and_clean(MATRIX, "PUBLICATION_GATE_MATRIX", errors)
    git_bound_and_clean(pathlib.Path(__file__).resolve(), "GATE_CHECKER", errors)

    matrix_sha256 = hashlib.sha256(MATRIX.read_bytes()).hexdigest()
    if matrix_sha256 != EXPECTED_MATRIX_SHA256:
        errors.append(f"MATRIX_DIGEST_DRIFT:{matrix_sha256}")
    if data.get("candidate_commit") != EXPECTED_CANDIDATE_COMMIT:
        errors.append("CANDIDATE_COMMIT_DRIFT")
    candidate_exists = subprocess.run(
        ["git", "cat-file", "-e", f"{EXPECTED_CANDIDATE_COMMIT}^{{commit}}"],
        cwd=REPOSITORY_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if candidate_exists.returncode != 0:
        errors.append("CANDIDATE_COMMIT_NOT_AVAILABLE")

    if data.get("portfolio_terminal") != "CURRENT_CLAIMS_NOT_ESTABLISHED_FOR_SUBMISSION_READINESS":
        errors.append("PORTFOLIO_TERMINAL_PROMOTED_WITHOUT_NEW_AUDIT")

    rules = data.get("integrity_rules", {})
    required_true = (
        "negative_results_immutable",
        "harness_repair_requires_new_version",
        "superiority_requires_prospective_strongest_donor_comparison",
    )
    for key in required_true:
        if rules.get(key) is not True:
            errors.append(f"INTEGRITY_RULE_NOT_TRUE:{key}")
    if rules.get("checker_pass_grants_scientific_authority") is not False:
        errors.append("CHECKER_MUST_NOT_GRANT_SCIENTIFIC_AUTHORITY")
    if rules.get("failed_target_pdf_build_can_be_submission_ready") is not False:
        errors.append("FAILED_PDF_BUILD_MUST_BLOCK_READINESS")
    if rules.get("not_started_successor_protocol_can_close_current_p0") is not False:
        errors.append("NOT_STARTED_PROTOCOL_MUST_NOT_CLOSE_CURRENT_P0")

    papers = data.get("papers", {})
    if set(papers) != {"Q1", "Q2", "Q3", "Q4"}:
        errors.append(f"PAPER_SET_DRIFT:{sorted(papers)}")
    for paper, entry in sorted(papers.items()):
        if entry.get("publication_status") != "BLOCKED":
            errors.append(f"UNAUTHORIZED_PUBLICATION_PROMOTION:{paper}")
        if not entry.get("p0_gates"):
            errors.append(f"MISSING_P0_GATES:{paper}")
        if not entry.get("forbidden_promotions"):
            errors.append(f"MISSING_FORBIDDEN_PROMOTIONS:{paper}")
    for paper in ("Q3", "Q4"):
        entry = papers.get(paper, {})
        if entry.get("requires_new_prospective_science_for_current_headline_claim") is not True:
            errors.append(f"CURRENT_HEADLINE_PROSPECTIVE_GATE_NOT_TRUE:{paper}")
        if entry.get("requires_new_prospective_science_for_narrowed_historical_claim") is not False:
            errors.append(f"NARROWED_HISTORICAL_GATE_NOT_FALSE:{paper}")
        if entry.get("requires_new_science_for_narrowed_historical_core") is not False:
            errors.append(f"NARROWED_HISTORICAL_CORE_GATE_NOT_FALSE:{paper}")
        if entry.get("requires_new_science_for_original_comparative_or_general_claim") is not True:
            errors.append(f"ORIGINAL_GENERAL_CLAIM_GATE_NOT_TRUE:{paper}")
    required_donor_gates = {
        "Q2": "CLASSICAL_AND_PRIMARY_SOURCE_DONOR_SUBTRACTION",
        "Q3": "DIRECT_DEFERRED_EVALUATION_AND_DUAL_INSTRUMENT_DONOR_SUBTRACTION",
    }
    for paper, gate in required_donor_gates.items():
        if gate not in papers.get(paper, {}).get("p0_gates", []):
            errors.append(f"MISSING_DONOR_GATE:{paper}:{gate}")

    for protocol_id, path in PROTOCOLS.items():
        if not path.is_file():
            errors.append(f"MISSING_SUCCESSOR_PROTOCOL:{protocol_id}")
            continue
        body = path.read_text(encoding="utf-8")
        if f"Protocol identifier: `{protocol_id}`" not in body:
            errors.append(f"PROTOCOL_ID_MISMATCH:{protocol_id}")
        if body.splitlines().count("`EXECUTION_STATUS=NOT_STARTED`") != 1:
            errors.append(f"PROTOCOL_EXECUTION_NOT_FAIL_CLOSED:{protocol_id}")
        if "strict ancestor" not in body:
            errors.append(f"PROSPECTIVE_ANCESTRY_RULE_MISSING:{protocol_id}")
        git_bound_and_clean(path, f"PROTOCOL:{protocol_id}", errors)

    if errors:
        print("Q1_Q4_PUBLICATION_GATE_MATRIX=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Q1_Q4_PUBLICATION_GATE_MATRIX=PASS")
    print("PAPERS=4")
    print("CURRENT_SUBMISSION_READY=0")
    print("TRACKED_NOT_STARTED_SUCCESSOR_PROTOCOLS=Q2-P1,Q3-P1,Q4-P1")
    print("SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_CHECKER")
    return 0


if __name__ == "__main__":
    sys.exit(main())
