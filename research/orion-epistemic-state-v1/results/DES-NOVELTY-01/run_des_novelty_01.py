#!/usr/bin/env python3
"""Fail-closed external novelty-review preflight for DES-NOVELTY-01."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


JOB_ID = "DES-NOVELTY-01"
CANNOT = "INACCESSIBLE_WORK_MAY_ABSORB_CLAIM"
AUTHORITY = (
    "EXTERNAL_NOVELTY_NOT_ESTABLISHED__NO_INDEPENDENT_FOUR_DIMENSION_REVIEW__"
    "NO_INACCESSIBLE_WORK_CLEARANCE__NO_DOMAIN_EXPERT_ADJUDICATION"
)
DIMENSIONS = ("exact", "function", "history", "implementation")


def canonical(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, payload: Any) -> None:
    path.write_bytes(canonical(payload))


def valid_digest(value: Any) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", str(value or "")))


def validate_transfer(
    directory: Path, freeze: dict[str, Any]
) -> tuple[bool, list[str], dict[str, Any] | None]:
    path = directory / "EXTERNAL_NOVELTY_TRANSFER_V1.json"
    if not path.is_file():
        return False, ["EXTERNAL_NOVELTY_TRANSFER_V1.json absent"], None
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"external novelty transfer unreadable:{exc}"], None

    errors: list[str] = []
    expected = {
        "schema": "orion.des.external-novelty-transfer.v1",
        "job_id": JOB_ID,
        "subject_revision": freeze["subject_revision"],
        "claim_atoms_sha256": freeze["claim_atoms"]["sha256"],
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{key} mismatch")

    reviewers = payload.get("reviewers")
    if not isinstance(reviewers, dict):
        reviewers = {}
        errors.append("reviewer map absent")
    reviewer_ids: list[str] = []
    for dimension in DIMENSIONS:
        row = reviewers.get(dimension)
        if not isinstance(row, dict):
            errors.append(f"{dimension} reviewer absent")
            continue
        reviewer_id = str(row.get("reviewer_id") or "")
        if not reviewer_id:
            errors.append(f"{dimension} reviewer identity absent")
        else:
            reviewer_ids.append(reviewer_id)
        if row.get("lineage_overlaps_orion") is not False:
            errors.append(f"{dimension} reviewer independence not established")
        if not valid_digest(row.get("signed_report_sha256")):
            errors.append(f"{dimension} signed report digest absent or invalid")

    adjudicator = payload.get("domain_expert_adjudicator")
    if not isinstance(adjudicator, dict):
        errors.append("domain expert adjudicator absent")
    else:
        adjudicator_id = str(adjudicator.get("adjudicator_id") or "")
        if not adjudicator_id:
            errors.append("domain expert adjudicator identity absent")
        else:
            reviewer_ids.append(adjudicator_id)
        if adjudicator.get("lineage_overlaps_orion") is not False:
            errors.append("domain expert independence not established")
        if not valid_digest(adjudicator.get("signed_adjudication_sha256")):
            errors.append("domain expert adjudication digest absent or invalid")
    if len(reviewer_ids) != len(set(reviewer_ids)):
        errors.append("reviewer/adjudicator identities are not distinct")

    rounds = payload.get("no_material_change_rounds")
    if not isinstance(rounds, list) or len(rounds) != 2:
        errors.append("exactly two no-material-change rounds absent")
    else:
        for index, row in enumerate(rounds, 1):
            if not isinstance(row, dict):
                errors.append(f"round {index} malformed")
                continue
            if row.get("claim_atoms_sha256") != freeze["claim_atoms"]["sha256"]:
                errors.append(f"round {index} claim digest mismatch")
            if row.get("material_change") is not False:
                errors.append(f"round {index} no-material-change state absent")
            if not valid_digest(row.get("signed_round_receipt_sha256")):
                errors.append(f"round {index} receipt digest absent or invalid")

    clearance = payload.get("inaccessible_work_clearance")
    if not isinstance(clearance, dict) or clearance.get("cleared") is not True:
        errors.append("inaccessible-work clearance absent")
    elif not valid_digest(clearance.get("basis_sha256")):
        errors.append("inaccessible-work clearance basis digest absent or invalid")
    if payload.get("sealed_before_executor_outcome_access") is not True:
        errors.append("prospective seal chronology not established")
    if payload.get("executor_outcome_accessed_before_freeze") is not False:
        errors.append("executor outcome blindness not established")
    return not errors, errors, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--review-dir", type=Path)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("execution head must be a full Git SHA")

    bundle = args.bundle.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    claims_path = bundle / "CLAIM_ATOMS_V1.json"
    runner_path = bundle / "run_des_novelty_01.py"
    freeze = json.loads(freeze_path.read_text())
    claims = json.loads(claims_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    if sha(claims_path) != freeze["claim_atoms"]["sha256"]:
        raise SystemExit("claim atom digest drift")
    if claims.get("atom_denominator") != 75 or len(claims.get("atoms", [])) != 75:
        raise SystemExit("claim atom denominator drift")

    if args.review_dir is None:
        attained, blockers, transfer = False, ["no independent external novelty review transferred"], None
    elif not args.review_dir.is_dir():
        attained, blockers, transfer = False, ["configured external review directory absent"], None
    else:
        attained, blockers, transfer = validate_transfer(args.review_dir.resolve(), freeze)
    if attained:
        blockers = ["validated transfer requires signed receipt-ingestion successor"]

    rows = [
        {
            "atom_id": atom["atom_id"],
            "paper_id": atom["paper_id"],
            "review_state": "CANNOT_CHECK",
            "reason": CANNOT,
            "missing_preconditions": blockers,
        }
        for atom in claims["atoms"]
    ]
    novelty = {
        "schema": "orion.des.p1-p15-external-novelty-receipts.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "claim_atoms_sha256": sha(claims_path),
        "paper_denominator": 15,
        "atom_denominator": 75,
        "externally_reviewed_denominator": 0,
        "cannot_check_denominator": 75,
        "review_dimensions": list(DIMENSIONS),
        "no_material_change_rounds_completed": 0,
        "rows": rows,
        "exact_terminal": CANNOT,
        "authority_ceiling": AUTHORITY,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "exact_terminal": CANNOT,
        "case_denominator": 75,
        "externally_reviewed_denominator": 0,
        "cannot_check_denominator": 75,
        "claim_ceiling": AUTHORITY,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB_ID,
        "state": "NOT_ESTABLISHED",
        "reason": "independent external review and inaccessible-work clearance unavailable",
        "weak_proxy_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": [
            {"id": "NO_INTERNAL_REVIEW_AS_EXTERNAL", "passed": True},
            {"id": "NO_METADATA_SEARCH_AS_NOVELTY_AUTHORITY", "passed": True},
            {"id": "NO_ACCESSIBLE_ONLY_CLEARANCE", "passed": True},
            {"id": "NO_ZERO_REVIEW_PROMOTION", "passed": True},
            {"id": "ALL_ATOMS_RETAINED_AS_CANNOT_CHECK", "passed": len(rows) == 75},
        ],
        "all_pass": len(rows) == 75,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB_ID,
        "resource_vector": {
            "claim_atoms_registered": 75,
            "external_reviews_received": 0,
            "domain_expert_adjudications": 0,
            "no_material_change_rounds": 0,
            "gpu": 0,
            "external_calls": 0,
        },
        "cap_hit": False,
        "censored": False,
    }
    transfer_result = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": JOB_ID,
        "state": "CANNOT_CHECK",
        "reason": CANNOT,
        "authority_delta": "NONE",
    }
    outputs = {
        "P1_P15_EXTERNAL_NOVELTY_RECEIPTS_V1.json": novelty,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer_result,
    }
    for name, payload in outputs.items():
        write(out / name, payload)
    manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB_ID,
        "subject_revision": freeze["subject_revision"],
        "freeze_sha256": sha(freeze_path),
        "claim_atoms_sha256": sha(claims_path),
        "runner_sha256": sha(runner_path),
        "external_review_transfer": transfer,
        "outputs": {
            name: {"bytes": (out / name).stat().st_size, "sha256": sha(out / name)}
            for name in sorted(outputs)
        },
    }
    write(out / "RAW_MANIFEST_V1.json", manifest)
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": JOB_ID,
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": args.execution_head,
        "freeze_sha256": sha(freeze_path),
        "raw_manifest_sha256": sha(out / "RAW_MANIFEST_V1.json"),
        "case_denominator": 75,
        "externally_reviewed_denominator": 0,
        "cannot_check_denominator": 75,
        "hard_preconditions": {
            "exact_review": False,
            "function_review": False,
            "history_review": False,
            "implementation_review": False,
            "domain_expert_adjudication": False,
            "two_no_material_change_rounds": False,
            "inaccessible_work_clearance": False,
            "prospective_external_custody": False,
        },
        "leakage": {"internal_review_relabelled_external": False, "accessible_only_clearance": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer_result,
        "exact_terminal": CANNOT,
        "claim_ceiling": AUTHORITY,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB_ID}={CANNOT} atoms=75 reviewed=0 cannot_check=75")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
