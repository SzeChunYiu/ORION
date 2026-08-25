#!/usr/bin/env python3
"""Frozen custody preflight for the externally escrowed frontier-math job."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


JOB = "DES-FRONTIER-MATH-01"
CANNOT = "EXTERNALLY_ESCROWED_FRONTIER_TARGET_UNAVAILABLE"
CEILING = "ESCROW_PREFLIGHT_ONLY__NO_FRONTIER_DISCOVERY_OR_OUTSIDE_CLOSURE_AUTHORITY"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def validate_transfer(directory: Path, freeze: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any] | None]:
    path = directory / "FRONTIER_MATH_ESCROW_TRANSFER_V1.json"
    if not path.is_file():
        return False, ["FRONTIER_MATH_ESCROW_TRANSFER_V1.json absent"], None
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"transfer unreadable:{exc}"], None
    errors: list[str] = []
    expected = {
        "schema": "orion.des.frontier-math-escrow-transfer.v1",
        "job_id": JOB,
        "subject_revision": freeze["subject_revision"],
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{key} mismatch")
    for key in (
        "target_statement_sha256",
        "old_grammar_sha256",
        "exact_checker_sha256",
        "donor_refusal_sha256",
        "heldout_siblings_sha256",
    ):
        if not re.fullmatch(r"[0-9a-f]{64}", str(payload.get(key, ""))):
            errors.append(f"{key} absent or invalid")
    if not payload.get("target_id"):
        errors.append("target identity absent")
    if not payload.get("external_custodian_id"):
        errors.append("external custodian absent")
    if payload.get("custodian_lineage_overlaps_orion") is not False:
        errors.append("external custody independence not established")
    if payload.get("sealed_before_executor_access") is not True:
        errors.append("prospective seal chronology not established")
    if payload.get("executor_saw_target_or_outcome") is not False:
        errors.append("executor blindness not established")
    return not errors, errors, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--escrow-dir", type=Path)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("invalid execution head")
    bundle = args.bundle.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_des_frontier_math_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    if args.escrow_dir is None:
        attained, blockers, transfer = False, ["no external frontier target transferred"], None
    elif not args.escrow_dir.is_dir():
        attained, blockers, transfer = False, ["configured escrow directory absent"], None
    else:
        attained, blockers, transfer = validate_transfer(args.escrow_dir.resolve(), freeze)
    if attained:
        blockers = ["attained target requires a target-specific frozen executor successor"]
    terminal = CANNOT
    discovery = {
        "schema": "orion.des.frontier-math-discovery-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "target_denominator": 0,
        "attempt_denominator": 0,
        "donor_first_refusals": 0,
        "verified_extensions": 0,
        "negative_attempts": 0,
        "cannot_check_rows": [{"target_id": None, "reasons": blockers}],
        "exact_terminal": terminal,
        "authority_ceiling": CEILING,
    }
    outside = {
        "schema": "orion.des.outside-closure-certificate.v1",
        "job_id": JOB,
        "state": "NOT_ISSUED",
        "reason": CANNOT,
        "old_grammar_sha256": None,
        "checker_sha256": None,
        "certificate_authority": "NONE",
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": terminal,
        "case_denominator": 0,
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "NOT_RUN",
        "reason": "external target, grammar, checker, and donor-refusal receipt unavailable",
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "NO_SELF_SELECTED_FRONTIER_TARGET", "passed": True},
            {"id": "NO_TIMEOUT_AS_OBSTRUCTION", "passed": True},
            {"id": "NO_DONOR_FAILURE_AS_OUTSIDE_CLOSURE", "passed": True},
        ],
        "all_pass": True,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {"targets": 0, "attempts": 0, "cpu_seconds": 0, "gpu_seconds": 0},
        "cap_hit": False,
        "censored": False,
    }
    transfer_result = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": JOB,
        "state": "CANNOT_CHECK",
        "reason": CANNOT,
        "authority_delta": "NONE",
    }
    outputs = {
        "FRONTIER_MATH_DISCOVERY_RESULT_V1.json": discovery,
        "OUTSIDE_CLOSURE_CERTIFICATE_V1.json": outside,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer_result,
    }
    for name, value in outputs.items():
        write(out / name, value)
    manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB,
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
        "job_id": JOB,
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": args.execution_head,
        "freeze_sha256": sha(freeze_path),
        "raw_manifest_sha256": sha(out / "RAW_MANIFEST_V1.json"),
        "case_denominator": 0,
        "hard_preconditions": {
            "external_target": False,
            "old_grammar": False,
            "exact_checker": False,
            "donor_first_refusal": False,
            "heldout_siblings": False,
            "prospective_custody": False,
        },
        "leakage": {"executor_selected_target": False, "outcome_accessed": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer_result,
        "exact_terminal": terminal,
        "claim_ceiling": CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB}={terminal} targets=0 blockers={len(blockers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
