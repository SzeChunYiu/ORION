#!/usr/bin/env python3
"""Validate the P1 R7A preflight without reading scientific outcomes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preflight",
        type=Path,
        default=HERE / "R7A_EXECUTION_PREFLIGHT_V1.json",
    )
    parser.add_argument(
        "--sources",
        type=Path,
        default=HERE / "PUBLIC_SOURCE_RIGHTS_LEDGER_V1.json",
    )
    parser.add_argument(
        "--comparators",
        type=Path,
        default=HERE / "COMPARATOR_INTERFACE_CONTRACT_V1.json",
    )
    parser.add_argument(
        "--external-bindings",
        type=Path,
        default=HERE / "EXTERNAL_BINDINGS_TEMPLATE_V1.json",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    preflight = load(args.preflight)
    sources = load(args.sources)
    comparators = load(args.comparators)
    external = load(args.external_bindings)

    integrity_errors: list[str] = []
    missing_scientific_bindings: list[str] = []

    for row in preflight.get("artifact_bindings", []):
        path = ROOT / row["path"]
        if not path.is_file():
            integrity_errors.append(f"missing bound artifact: {row['path']}")
            continue
        observed = digest(path)
        if observed != row["sha256"]:
            integrity_errors.append(
                f"digest mismatch: {row['path']} expected {row['sha256']} observed {observed}"
            )

    source_summary = sources.get("summary", {})
    if source_summary.get("candidate_metadata_roots") != 28:
        integrity_errors.append("public source ledger must preserve exactly 28 metadata roots")
    if source_summary.get("case_content_rights_bound") != 0:
        integrity_errors.append("current source ledger unexpectedly claims bound case-content rights")
    if source_summary.get("case_eligibility_assessed") != 0:
        integrity_errors.append("current source ledger unexpectedly claims assessed eligibility")
    if any(row.get("r7a_case_content_admissible") for row in sources.get("sources", [])):
        integrity_errors.append("a metadata-only source was promoted to R7A case admissibility")

    arms = comparators.get("primary_comparators", [])
    if len(arms) != 9 or len({row.get("arm_id") for row in arms}) != 9:
        integrity_errors.append("comparator registry must contain nine unique primary arms")
    if comparators.get("execution_authorized") is not False:
        integrity_errors.append("current comparator contract must not authorize execution")

    for row in arms:
        if row.get("current_status") != "R7A_ARM_READY":
            missing_scientific_bindings.append(
                f"COMPARATOR::{row.get('arm_id')}::{row.get('current_status')}"
            )
    candidate = comparators.get("candidate", {})
    if candidate.get("current_status") != "R7A_ARM_READY":
        missing_scientific_bindings.append(
            f"CANDIDATE::{candidate.get('arm_id')}::{candidate.get('current_status')}"
        )

    external_rows = external.get("bindings", [])
    if not external_rows:
        integrity_errors.append("external binding receipt has no required rows")
    for row in external_rows:
        if row.get("status") != "BOUND_VERIFIED":
            missing_scientific_bindings.append(
                f"EXTERNAL::{row.get('binding_id')}::{row.get('status')}"
            )
            continue
        for field in external.get("required_identity_fields_when_bound", []):
            if not row.get(field):
                integrity_errors.append(
                    f"bound external row {row.get('binding_id')} lacks {field}"
                )

    for gate, fact in (
        ("SOURCE_RIGHTS_COMPLETE", source_summary.get("case_content_rights_bound") == 896),
        ("SOURCE_ELIGIBILITY_COMPLETE", source_summary.get("case_eligibility_assessed") == 896),
        ("SOURCE_FRAME_COMPLETE", source_summary.get("r7a_case_content_admissible") == 896),
    ):
        if not fact:
            missing_scientific_bindings.append(gate)

    if integrity_errors:
        terminal = "P1_R7A_PREFLIGHT_INVALID"
        execution_authorized = False
        exit_code = 2
    elif missing_scientific_bindings:
        terminal = "P1_R7A_CANNOT_CHECK_EXTERNAL_BINDINGS"
        execution_authorized = False
        exit_code = 3
    else:
        terminal = "P1_R7A_EXECUTION_AUTHORIZED"
        execution_authorized = True
        exit_code = 0

    receipt = {
        "schema_version": "orion.p1.r7a.public-naturalistic-preflight-receipt.v1",
        "authority": "OUTCOME_BLIND_PREFLIGHT_CONFORMANCE_ONLY",
        "outcomes_accessed": False,
        "terminal": terminal,
        "execution_authorized": execution_authorized,
        "integrity_errors": integrity_errors,
        "missing_scientific_bindings": sorted(set(missing_scientific_bindings)),
        "observed_counts": {
            "candidate_metadata_roots": source_summary.get("candidate_metadata_roots"),
            "case_content_rights_bound": source_summary.get("case_content_rights_bound"),
            "case_eligibility_assessed": source_summary.get("case_eligibility_assessed"),
            "r7a_case_content_admissible": source_summary.get("r7a_case_content_admissible"),
            "primary_comparator_rows": len(arms),
            "external_binding_rows": len(external_rows),
            "external_binding_rows_ready": sum(
                row.get("status") == "BOUND_VERIFIED" for row in external_rows
            ),
        },
        "historical_results_immutable": True,
        "grants_scientific_authority": False,
    }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
