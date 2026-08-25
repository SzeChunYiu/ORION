#!/usr/bin/env python3
"""Fail-closed acquisition audit for the frozen P11-DES-01 programme."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import time
from typing import Any

JOB = "P11-DES-01"
TERMINAL = "P11_DATASETS_MODELS_TRANSCRIPTS_NOT_CONTENT_BOUND"
CEILING = (
    "ACQUISITION_AUDIT_ONLY__ZERO_SCIENTIFIC_CASES_EXECUTED__NO_REAL_SYSTEM_"
    "REPLICATION_OR_RESOURCE_FRONTIER_AUTHORITY"
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def audit_requirement(root: Path, req: dict[str, Any]) -> dict[str, Any]:
    manifest = root / req["manifest"]
    row: dict[str, Any] = {
        "id": req["id"],
        "manifest": req["manifest"],
        "status": "CANNOT_CHECK",
        "reason": "MANIFEST_ABSENT",
        "verified_objects": 0,
    }
    if not manifest.is_file():
        return row
    try:
        payload = json.loads(manifest.read_text())
    except Exception as exc:
        row["reason"] = f"MANIFEST_INVALID_JSON:{type(exc).__name__}"
        return row
    if payload.get("requirement_id") != req["id"]:
        row["reason"] = "REQUIREMENT_ID_MISMATCH"
        return row
    objects = payload.get("objects")
    if not isinstance(objects, list) or not objects:
        row["reason"] = "CONTENT_OBJECTS_ABSENT"
        return row
    family_ids: set[str] = set()
    for obj in objects:
        if not isinstance(obj, dict):
            row["reason"] = "OBJECT_RECORD_INVALID"
            return row
        rel = obj.get("path")
        expected_sha = obj.get("sha256")
        expected_bytes = obj.get("bytes")
        if (
            not isinstance(rel, str)
            or Path(rel).is_absolute()
            or ".." in Path(rel).parts
            or not isinstance(expected_bytes, int)
            or expected_bytes < 0
            or not isinstance(expected_sha, str)
            or re.fullmatch(r"[0-9a-f]{64}", expected_sha) is None
        ):
            row["reason"] = "OBJECT_BINDING_INVALID"
            return row
        path = root / rel
        if not path.is_file():
            row["reason"] = f"OBJECT_ABSENT:{rel}"
            return row
        if path.stat().st_size != expected_bytes or digest(path) != expected_sha:
            row["reason"] = f"OBJECT_IDENTITY_DRIFT:{rel}"
            return row
        if isinstance(obj.get("family_id"), str):
            family_ids.add(obj["family_id"])
        row["verified_objects"] += 1
    if len(family_ids) < req.get("minimum_distinct_families", 0):
        row["reason"] = "MODEL_FAMILY_DENOMINATOR_NOT_MET"
        row["distinct_model_families"] = len(family_ids)
        return row
    row.update(
        {
            "status": "BOUND",
            "reason": None,
            "manifest_sha256": digest(manifest),
            "distinct_model_families": len(family_ids),
        }
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--custody-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.execution_head) is None:
        raise SystemExit("invalid execution head")
    start_wall = time.monotonic_ns()
    start_cpu = time.process_time_ns()
    repo = args.repo.resolve()
    bundle = args.bundle.resolve()
    custody = args.custody_root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_p11_des_01.py"
    freeze = json.loads(freeze_path.read_text())
    if digest(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    for item in freeze["frozen_inputs"]:
        path = repo / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise SystemExit(f"frozen input drift:{item['path']}")

    rows = [audit_requirement(custody, req) for req in freeze["acquisition_requirements"]]
    bound = sum(row["status"] == "BOUND" for row in rows)
    primary_three = {"LONGMEMEVAL_DATASET_OBJECTS", "OPEN_WEIGHT_OR_API_MODEL_IDENTITIES", "RAW_SESSION_TRANSCRIPTS"}
    missing_primary = [row["id"] for row in rows if row["id"] in primary_three and row["status"] != "BOUND"]
    # This runner is an acquisition gate, never an implicit scientific campaign.
    scientific_execution_allowed = bound == len(rows) and not missing_primary
    exact_terminal = "P11_ACQUISITION_READY_REQUIRES_SEPARATELY_FROZEN_SUCCESSOR" if scientific_execution_allowed else TERMINAL
    audit = {
        "schema": "orion.p11.acquisition-audit.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "custody_root": str(custody),
        "requirement_denominator": len(rows),
        "bound_requirements": bound,
        "cannot_check_requirements": len(rows) - bound,
        "missing_primary_content_classes": missing_primary,
        "requirements": rows,
        "scientific_case_denominator": 0,
        "scientific_cases_executed": 0,
        "scientific_execution_allowed": scientific_execution_allowed,
        "exact_terminal": exact_terminal,
        "claim_ceiling": CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": exact_terminal,
        "acquisition_requirement_denominator": len(rows),
        "bound_requirements": bound,
        "case_denominator": 0,
        "executed_case_denominator": 0,
        "dropped_case_denominator": 0,
        "cannot_check_case_denominator": 0,
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "MATERIAL_DONOR_INPUTS_UNAVAILABLE" if not scientific_execution_allowed else "ACQUISITION_BOUND_NOT_EXECUTED",
        "comparators": freeze["comparators"],
        "runnable_comparator_arms": 0,
        "weak_proxy_substituted": False,
        "existing_same_programme_receipts_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "NO_SKLEARN_THREE_DATASET_PROXY_SUBSTITUTION", "passed": True},
            {"id": "NO_EXISTING_CONTROLLED_RECEIPT_AS_REAL_SYSTEM_REPLICATION", "passed": True},
            {"id": "NO_UNBOUND_MODEL_NAME_AS_MODEL_IDENTITY", "passed": True},
            {"id": "NO_UNBOUND_TRANSCRIPT_AS_EVALUATION_CASE", "passed": True},
            {"id": "NO_COMPILATION_COST_OMISSION", "passed": True},
            {"id": "NO_ZERO_CASE_POSITIVE_TERMINAL", "passed": exact_terminal == TERMINAL},
        ],
        "all_pass": exact_terminal == TERMINAL,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {
            "acquisition_requirements_checked": len(rows),
            "filesystem_objects_verified": sum(row["verified_objects"] for row in rows),
            "scientific_cases": 0,
            "model_calls": 0,
            "gpu": 0,
            "network_calls": 0,
            "cpu_nanoseconds": time.process_time_ns() - start_cpu,
            "wall_nanoseconds": time.monotonic_ns() - start_wall,
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "cap_hit": False,
        "censored": False,
    }
    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": JOB,
        "state": "CANNOT_CHECK",
        "reason": exact_terminal,
        "authority_delta": "NONE",
    }
    outputs = {
        "P11_ACQUISITION_AUDIT_V1.json": audit,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
    }
    for name, payload in outputs.items():
        write(out / name, payload)
    manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB,
        "subject_revision": freeze["subject_revision"],
        "freeze_sha256": digest(freeze_path),
        "runner_sha256": digest(runner_path),
        "outputs": {name: {"bytes": (out / name).stat().st_size, "sha256": digest(out / name)} for name in sorted(outputs)},
    }
    write(out / "RAW_MANIFEST_V1.json", manifest)
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": JOB,
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": args.execution_head,
        "freeze_sha256": digest(freeze_path),
        "raw_manifest_sha256": digest(out / "RAW_MANIFEST_V1.json"),
        "acquisition_requirement_denominator": len(rows),
        "bound_requirements": bound,
        "case_denominator": 0,
        "executed_case_denominator": 0,
        "dropped_case_denominator": 0,
        "hard_preconditions": {row["id"]: row["status"] == "BOUND" for row in rows},
        "leakage": {
            "existing_receipts_substituted": False,
            "unbound_assets_substituted": False,
            "scientific_campaign_run_before_full_binding": False,
        },
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": exact_terminal,
        "claim_ceiling": CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB}={exact_terminal} requirements={len(rows)} bound={bound} scientific_cases=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
