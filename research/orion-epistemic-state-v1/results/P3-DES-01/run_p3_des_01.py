#!/usr/bin/env python3
"""Execute the frozen lawful-universe preflight for P3-DES-01."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


JOB = "P3-DES-01"
CANNOT = "P3_MULTI_CASE_LAWFUL_EVALUATION_UNAVAILABLE"
CEILING = (
    "RIGHTS_AND_CASE_UNIVERSE_PREFLIGHT_ONLY__PREEXISTING_ONE_CASE_DEVELOPMENT_"
    "OUTCOMES_NOT_REUSED_AS_PROSPECTIVE_MULTI_CASE_EVIDENCE"
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def classify_strata(license_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    primary = license_manifest["primary_sources"][0]
    natural = license_manifest["natural_pair_candidates"]
    fallback = license_manifest["licensed_fallback"]
    return [
        {
            "stratum_id": "OAEI_BENCH23_GENERATED",
            "rights_state": primary["selection_status"],
            "payload_state": primary["download_status"],
            "admissible": False,
            "reason": "generated single-seed suite cannot satisfy the frozen natural-pair requirement alone",
        },
        {
            "stratum_id": "OAEI_NATURAL_ONTOLOGY_PAIR",
            "rights_state": "CANNOT_CHECK",
            "payload_state": "NOT_DOWNLOADED",
            "admissible": False,
            "reason": "; ".join(row["selection_status"] for row in natural),
        },
        {
            "stratum_id": "SEMTAB_2025",
            "rights_state": fallback["license"]["verification"],
            "payload_state": fallback["activation_status"],
            "admissible": False,
            "reason": fallback["license"]["reason"],
        },
        {
            "stratum_id": "NATURAL_SCIENTIFIC_IDENTITY",
            "rights_state": "NO_FROZEN_SOURCE_TRANSFER",
            "payload_state": "ABSENT",
            "admissible": False,
            "reason": "no independently selected natural scientific measurement identity panel was transferred",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("invalid execution head")
    repo = args.repo.resolve()
    bundle = args.bundle.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_p3_des_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    for item in freeze["frozen_inputs"]:
        path = repo / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            raise SystemExit(f"frozen input drift:{item['path']}")

    license_path = repo / freeze["frozen_inputs"][0]["path"]
    license_manifest = json.loads(license_path.read_text())
    strata = classify_strata(license_manifest)
    admissible = [row for row in strata if row["admissible"]]
    arms = ["ORION_DYNAMIC_GLUING", "LOGMAP", "AML", "PROVENANCE_ONLY", "IDEAL_TYPED_PRODUCT"]
    scheduled = [
        {
            "stratum_id": row["stratum_id"],
            "arm_id": arm,
            "state": "NOT_RUN_CANNOT_CHECK",
            "reason": row["reason"],
        }
        for row in strata
        for arm in arms
    ]
    result = {
        "schema": "orion.p3.dynamic-gluing-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "stratum_denominator": 4,
        "arm_denominator": 5,
        "scheduled_cell_denominator": 20,
        "executed_cell_denominator": 0,
        "cannot_check_cell_denominator": 20,
        "strata": strata,
        "cells": scheduled,
        "preexisting_development_receipts": {
            "counted_as_new_outcomes": False,
            "v20_terminal": "P3_V20_BERTMAP_NATIVE_PASS__TYPED_DECODER_OR_STRUCTURAL_CONTRACT_FAIL__COMMON_SCORING_NOT_AUTHORIZED",
            "reason": "outcome predated the P3-DES-01 freeze and covered one historical public case only",
        },
        "exact_terminal": CANNOT,
        "authority_ceiling": CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": CANNOT,
        "case_denominator": 4,
        "scheduled_cell_denominator": 20,
        "executed_cell_denominator": 0,
        "cannot_check_cell_denominator": 20,
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "NOT_RUN_CANNOT_CHECK",
        "comparators": arms[1:],
        "reason": "no common lawful multi-case universe; no comparator may be replaced by an authored fixture",
        "weak_proxy_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "NO_BENCH23_ALONE_GENERALIZATION", "passed": not admissible},
            {"id": "NO_LICENSE_CANNOT_CHECK_BYPASS", "passed": True},
            {"id": "NO_AUTHORED_FIXTURE_AS_NATURAL_CASE", "passed": True},
            {"id": "NO_PREEXISTING_OUTCOME_AS_PROSPECTIVE", "passed": True},
            {"id": "NO_WEAK_PROXY_FOR_IDEAL_PRODUCT", "passed": True},
            {"id": "ALL_SCHEDULED_CELLS_RETAINED", "passed": len(scheduled) == 20},
        ],
        "all_pass": not admissible and len(scheduled) == 20,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {"registered_strata": 4, "registered_arms": 5, "executed_cells": 0, "gpu": 0, "network_calls": 0},
        "cap_hit": False,
        "censored": False,
    }
    transfer = {"schema": "orion.des.transfer-result.v1", "job_id": JOB, "state": "CANNOT_CHECK", "reason": CANNOT, "authority_delta": "NONE"}
    outputs = {
        "P3_DYNAMIC_GLUING_RESULT_V1.json": result,
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
        "case_denominator": 4,
        "scheduled_cell_denominator": 20,
        "executed_cell_denominator": 0,
        "cannot_check_cell_denominator": 20,
        "hard_preconditions": {
            "lawful_natural_pair": False,
            "lawful_semtab": False,
            "natural_scientific_identity_panel": False,
            "common_official_gold": False,
            "all_five_arms_runnable": False,
            "multi_case_inference_unit": False,
        },
        "leakage": {"authored_fixture_substituted": False, "preexisting_outcome_relabelled_prospective": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": CANNOT,
        "claim_ceiling": CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB}={CANNOT} strata=4 cells=20 executed=0 cannot_check=20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
