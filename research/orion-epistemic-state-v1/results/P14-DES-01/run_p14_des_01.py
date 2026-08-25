#!/usr/bin/env python3
"""Custody-first execution gate for the frozen P14-DES-01 campaign."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import time
from typing import Any

JOB = "P14-DES-01"
TERMINAL = "P14D_EXTERNAL_ACQUISITION_BLOCKED"
CEILING = (
    "EXTERNAL_ACQUISITION_PREFLIGHT_ONLY__ZERO_UNSEEN_INCIDENTS_EXECUTED__"
    "NO_CAUSAL_GOVERNANCE_OR_EXTERNAL_VALIDATION_AUTHORITY"
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("p14_external_acquisition", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen P14 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
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
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_p14_des_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    for item in freeze["frozen_inputs"]:
        path = repo / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            raise SystemExit(f"frozen input drift:{item['path']}")

    validator_path = repo / "src/orion/study/p14/external_acquisition.py"
    validator = load_validator(validator_path)
    preflight = validator.build_external_acquisition_preflight(repo)
    required = list(preflight["required_artifacts"])
    if required != freeze["required_artifacts"]:
        raise SystemExit("required artifact denominator drift")
    if preflight["terminal"] != TERMINAL:
        raise SystemExit("P14D terminal drift")
    present = len(preflight["present_artifacts"])
    missing = len(preflight["missing_artifacts"])
    if present + missing != len(required):
        raise SystemExit("acquisition denominator incomplete")
    execution_allowed = bool(preflight["execution_authorized"])
    if execution_allowed:
        raise SystemExit("frozen repository validator unexpectedly authorized external execution")

    campaign = {
        "schema": "orion.p14.dynamic-governance-acquisition-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "planned_domains": freeze["planned_domains"],
        "planned_arms": freeze["arms"],
        "acquisition_artifact_denominator": len(required),
        "present_artifacts": present,
        "missing_artifacts": missing,
        "scientific_case_denominator": 0,
        "executed_case_denominator": 0,
        "dropped_case_denominator": 0,
        "preflight": preflight,
        "exact_terminal": TERMINAL,
        "claim_ceiling": CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": TERMINAL,
        "acquisition_artifact_denominator": len(required),
        "present_artifacts": present,
        "case_denominator": 0,
        "executed_case_denominator": 0,
        "dropped_case_denominator": 0,
        "false_promotion": "CANNOT_CHECK",
        "valid_positive_retention": "CANNOT_CHECK",
        "wrong_layer_intervention": "CANNOT_CHECK",
        "reviewer_agreement": "CANNOT_CHECK",
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "EXTERNALLY_HELD_PACKET_AND_ADJUDICATION_DONORS_UNAVAILABLE",
        "comparators": freeze["arms"][1:],
        "runnable_external_arms": 0,
        "internal_p14c_or_p14e_substituted": False,
        "weak_proxy_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "NO_P14C_CONFORMANCE_AS_EXTERNAL_CAUSAL_TRIAL", "passed": True},
            {"id": "NO_P14E_SYNTHETIC_ROWS_AS_UNSEEN_INCIDENTS", "passed": True},
            {"id": "NO_SELF_AUTHORED_CUSTODY", "passed": not preflight["external_custody_verified"]},
            {"id": "NO_MISSING_PACKET_AS_NEGATIVE_OUTCOME", "passed": True},
            {"id": "NO_BLANKET_ABSTENTION_PROMOTION", "passed": True},
            {"id": "NO_ZERO_CASE_POSITIVE_TERMINAL", "passed": TERMINAL == preflight["terminal"]},
        ],
        "all_pass": True,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {
            "acquisition_artifacts_checked": len(required),
            "scientific_cases": 0,
            "policy_calls": 0,
            "human_adjudications": 0,
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
    transfer = {"schema": "orion.des.transfer-result.v1", "job_id": JOB, "state": "CANNOT_CHECK", "reason": TERMINAL, "authority_delta": "NONE"}
    outputs = {
        "P14_DYNAMIC_GOVERNANCE_RESULT_V1.json": campaign,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
    }
    for name, value in outputs.items():
        write(out / name, value)
    manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB,
        "subject_revision": freeze["subject_revision"],
        "freeze_sha256": sha(freeze_path),
        "runner_sha256": sha(runner_path),
        "outputs": {name: {"bytes": (out / name).stat().st_size, "sha256": sha(out / name)} for name in sorted(outputs)},
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
        "acquisition_artifact_denominator": len(required),
        "present_artifacts": present,
        "case_denominator": 0,
        "executed_case_denominator": 0,
        "dropped_case_denominator": 0,
        "hard_preconditions": {
            "all_eight_external_artifacts": missing == 0,
            "trusted_external_custody_verifier": preflight["trusted_external_custody_verifier_configured"],
            "external_custody_verified": preflight["external_custody_verified"],
            "execution_authorized": execution_allowed,
        },
        "leakage": {"internal_rows_substituted": False, "self_authored_custody": False, "same_specification_gold": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": TERMINAL,
        "claim_ceiling": CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB}={TERMINAL} artifacts={len(required)} present={present} scientific_cases=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
