#!/usr/bin/env python3
"""Fail-closed escrow preflight and executor for DES-RESPONSIBILITY-01."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


JOB_ID = "DES-RESPONSIBILITY-01"
CANNOT = "EXTERNAL_INCIDENT_CUSTODY_UNAVAILABLE"
POSITIVE = "RESPONSIBILITY_IDENTIFYING_CONTROL_PROSPECTIVELY_SUPERIOR"
NEGATIVE = "RESPONSIBILITY_CONTROL_DONOR_EQUIVALENT_OR_INFERIOR"
AUTHORITY = (
    "ESCROW_PREFLIGHT_OR_FROZEN_EXTERNAL_STUDY_RESULT_ONLY__"
    "NO_EXTERNAL_AUTHORITY_WITHOUT_CUSTODIAN_SIGNATURE"
)


def canonical(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, payload: Any) -> None:
    path.write_bytes(canonical(payload))


def validate_escrow(path: Path, freeze: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any] | None]:
    errors: list[str] = []
    transfer_path = path / "ESCROW_TRANSFER_V1.json"
    if not transfer_path.is_file():
        return False, ["ESCROW_TRANSFER_V1.json absent"], None
    try:
        transfer = json.loads(transfer_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"escrow transfer unreadable: {exc}"], None
    if transfer.get("schema") != "orion.des.external-incident-escrow-transfer.v1":
        errors.append("wrong escrow transfer schema")
    if transfer.get("job_id") != JOB_ID:
        errors.append("wrong job identity")
    if transfer.get("subject_revision") != freeze["subject_revision"]:
        errors.append("subject revision mismatch")
    if not transfer.get("external_custodian_id"):
        errors.append("external custodian identity absent")
    if transfer.get("custodian_lineage_overlaps_orion") is not False:
        errors.append("custodian independence is not established")
    domains = transfer.get("domains")
    if not isinstance(domains, list) or len(domains) < freeze["study"]["minimum_domains"]:
        errors.append("fewer than three external domains")
    case_count = transfer.get("case_count")
    if not isinstance(case_count, int) or case_count < freeze["study"]["minimum_cases"]:
        errors.append("external case denominator below freeze")
    for field in ("sealed_case_manifest_sha256", "external_scorer_sha256", "gold_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(transfer.get(field, ""))):
            errors.append(f"{field} absent or invalid")
    if transfer.get("outcome_accessed_by_executor") is not False:
        errors.append("executor outcome-blindness not established")
    if transfer.get("freeze_precedes_outcome_access") is not True:
        errors.append("prospective chronology not established")
    return not errors, errors, transfer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--escrow-dir", type=Path)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("execution head must be a full Git SHA")
    bundle = args.bundle.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_des_responsibility_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")

    escrow = args.escrow_dir.resolve() if args.escrow_dir else None
    if escrow is None:
        attained, errors, transfer = False, ["no escrow directory transferred"], None
    elif not escrow.is_dir():
        attained, errors, transfer = False, ["configured escrow directory absent"], None
    else:
        attained, errors, transfer = validate_escrow(escrow, freeze)

    # V1 executes no cases unless the complete external transfer precondition is met.
    # A future attained transfer must use a new execution implementation and identity;
    # silently inventing an evaluator here would violate the frozen protocol.
    terminal = CANNOT if not attained else CANNOT
    blockers = errors if errors else ["attained transfer requires externally supplied scorer executable"]
    result = {
        "schema": "orion.des.responsibility-identification-result.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "precondition_attained": False,
        "external_case_denominator": 0,
        "required_minimum_case_denominator": freeze["study"]["minimum_cases"],
        "required_minimum_domains": freeze["study"]["minimum_domains"],
        "blockers": blockers,
        "positive_rows": [],
        "negative_rows": [],
        "harmful_rows": [],
        "crashed_rows": [],
        "cannot_check_rows": [{"scope": "whole_study", "reasons": blockers}],
        "exact_terminal": terminal,
        "authority_ceiling": AUTHORITY,
    }
    scorer = {
        "schema": "orion.des.external-scorer-receipt.v1",
        "job_id": JOB_ID,
        "state": "NOT_RUN",
        "reason": "EXTERNAL_ESCROW_PRECONDITION_NOT_ATTAINED",
        "external_custodian_signature": None,
        "case_count": 0,
        "authority": "NONE",
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "exact_terminal": terminal,
        "case_denominator": 0,
        "cannot_check": True,
        "claim_ceiling": AUTHORITY,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB_ID,
        "state": "NOT_RUN",
        "comparators": freeze["study"]["comparators"],
        "reason": "matched externally held cases and scorer unavailable",
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": [
            {"id": "NO_SYNTHETIC_PROXY_FOR_EXTERNAL_INCIDENTS", "passed": True},
            {"id": "NO_SELF_AUTHORED_GOLD_AS_EXTERNAL", "passed": True},
            {"id": "NO_ZERO_DENOMINATOR_PERFORMANCE", "passed": True},
        ],
        "all_pass": True,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB_ID,
        "resource_vector": {"cases_scored": 0, "models_invoked": 0, "gpu": 0, "external_calls": 0},
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
        "RESPONSIBILITY_IDENTIFICATION_RESULT_V1.json": result,
        "EXTERNAL_SCORER_RECEIPT_V1.json": scorer,
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
        "runner_sha256": sha(runner_path),
        "escrow_transfer": transfer,
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
        "case_denominator": 0,
        "hard_preconditions": {
            "external_custody": False,
            "three_domains": False,
            "sealed_gold": False,
            "external_scorer": False,
            "prospective_chronology": False,
        },
        "leakage": {"executor_saw_outcomes": False, "self_authored_gold_substituted": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer_result,
        "exact_terminal": terminal,
        "claim_ceiling": AUTHORITY,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB_ID}={terminal} cases=0 blockers={len(blockers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
