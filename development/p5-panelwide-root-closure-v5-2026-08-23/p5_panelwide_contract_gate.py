#!/usr/bin/env python3
"""Fail-closed metadata gate for the P5 V5 panel-wide contract.

This program does not execute an arm or open protected payloads.  It verifies
only content identities and receipt metadata.  Institutional independence,
rights, and factual executor coverage remain external adjudications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = HERE / "P5_PANELWIDE_ROOT_CLOSURE_PROTOCOL_V5.json"
REGISTRY = HERE / "P5_PANELWIDE_BLOCKER_EQUIVALENCE_REGISTRY_V5.json"

REFUSAL = (
    "P5_V5_PANEL_GATE_REFUSES_EXECUTION__COMPLETE_SIGNED_EXTERNAL_CUSTODY_CASE_RIGHTS_"
    "PROVIDER_RESOURCE_RUNTIME_ISOLATION_AND_ARM_ACCEPTANCE_EVIDENCE_REQUIRED"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def no_payload_keys(value: Any, path: str = "$") -> list[str]:
    forbidden = ("outcome", "score_value", "gold", "test_body", "payload_body", "model_output")
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            low = key.lower()
            if any(token in low for token in forbidden):
                hits.append(f"{path}.{key}")
            hits.extend(no_payload_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            hits.extend(no_payload_keys(child, f"{path}[{i}]"))
    return hits


def verify_frozen_inputs(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for arm in registry["arms"]:
        for path_key, hash_key in (
            ("v4_registry_path", "v4_registry_sha256"),
            ("v4_result_path", "v4_result_sha256"),
        ):
            p = ROOT / arm[path_key]
            if not p.is_file() or sha256(p) != arm[hash_key]:
                failures.append(f"{arm['arm_code']}:{path_key}:digest_mismatch")
        parser = arm["parser"]
        p = ROOT / parser["path"]
        if not p.is_file() or sha256(p) != parser["sha256"]:
            failures.append(f"{arm['arm_code']}:parser:digest_mismatch")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--handoff", type=Path, help="metadata-only closing handoff; protected payloads forbidden")
    args = ap.parse_args()
    contract = json.loads(CONTRACT.read_text())
    registry = json.loads(REGISTRY.read_text())
    failures = verify_frozen_inputs(registry)

    if args.handoff is None:
        print(json.dumps({
            "eligible_to_execute": False,
            "frozen_input_failures": failures,
            "reason": "no closing handoff supplied; schema bytes do not bind evidence",
            "terminal": REFUSAL,
        }, indent=2, sort_keys=True))
        return 2

    handoff = json.loads(args.handoff.read_text())
    payload_hits = no_payload_keys(handoff)
    required = {
        "schema_version",
        "contract_sha256",
        "six_arm_field_acceptance",
        "external_custody_bundle",
        "common_case_and_rights_bundle",
        "provider_resource_bundle",
        "arm_runtime_isolation_receipts",
    }
    missing = sorted(required - set(handoff))
    if handoff.get("contract_sha256") != sha256(CONTRACT):
        failures.append("contract_sha256:mismatch")
    if sorted(handoff.get("six_arm_field_acceptance", {})) != ["C1", "C2", "C3", "C4", "C5", "C6"]:
        failures.append("six_arm_field_acceptance:must_name_C1_through_C6")
    for arm, accepted in handoff.get("six_arm_field_acceptance", {}).items():
        if sorted(accepted) != sorted(contract["required_field_paths"]):
            failures.append(f"{arm}:not_all_21_fields_accepted")
    failures.extend(f"missing:{x}" for x in missing)
    failures.extend(f"forbidden_payload_key:{x}" for x in payload_hits)

    # Even a structurally valid handoff is not self-authorizing.  The separate
    # independent-adjudication flag must be signed outside candidate custody.
    custody = handoff.get("external_custody_bundle", {})
    if custody.get("independent_adjudication") != "PASS_SIGNED_EXTERNAL":
        failures.append("external_custody_bundle:independent_adjudication_absent")
    if not custody.get("signed_metadata_receipt_sha256"):
        failures.append("external_custody_bundle:signed_metadata_receipt_sha256_absent")

    eligible = not failures
    print(json.dumps({
        "eligible_to_execute": eligible,
        "warning": "Structural eligibility is not scientific authority; external signatures, rights and executor facts require independent adjudication.",
        "failures": failures,
        "terminal": "P5_V5_PANEL_METADATA_GATE_STRUCTURALLY_COMPLETE__EXTERNAL_ADJUDICATION_STILL_REQUIRED" if eligible else REFUSAL,
    }, indent=2, sort_keys=True))
    return 0 if eligible else 2


if __name__ == "__main__":
    raise SystemExit(main())
