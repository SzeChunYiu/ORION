#!/usr/bin/env python3
"""Native fail-closed verifier for the P1 V10 construct-validity packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "VALIDATION_RECEIPT_V10.json"

EXPECTED_TERMINAL = (
    "P1_V10_FOUR_AUTHORITY_ACTS_REMAIN_NECESSARY__"
    "ADAPTER_BLIND_PRECOMMITMENT_OR_HISTORICAL_PRECEDENCE_CANNOT_CHECK__"
    "720_MAPS_UNCHANGED"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_local(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def main() -> int:
    errors: list[str] = []
    protocol = load_local("ADAPTER_BLIND_RATIFICATION_PROTOCOL_V10.json")
    allowlist = load_local("OWNER_INPUT_ALLOWLIST_V10.json")
    result = load_local("CURRENT_RESULT_V10.json")

    upstream_expected = {
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json": "eedb25a2dc084aaac34377bc9942647c3eea80bffa7b6a099d3de10b6bb11f55",
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_V8_REQUIRED_FIELD_CUSTODIAN_REGISTRY.json": "42fd386b113802b5b269dada6ab2965503fa5afa020a06e52a25ce667d03dae4",
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_V8_TARGET_SEMANTIC_REGISTRY.json": "fc3ff7435d291e8581eeefaab30b16a119bb005fd99f720090ef147c6b2944ba",
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_V8_PUBLIC_TARGET_SOURCE_REGISTRY.json": "7f16c0c6b036b1d257b917744fe63b562ff693cf9f41992dd1c93424e248c17d",
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_V8_720_ADAPTER_REGISTRY.json": "f2507273c49a30cceddfd745476aeab373a5c11d14dc56108ab16493cbd4dd23",
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_V8_ADAPTER_ADJUDICATION_RESULT.json": "0364e95997323192594c1c7491e65ef26969a707fca47a7e5c021a531f2ad5ac",
        "development/p1-source-native-target-semantics-v8-2026-08-23/P1_RESULT_V8.json": "47d1d6b38c96b7046500188c84b3b3cdb6afb1260a9acf87e4731dadd2ed76ed",
        "development/p1-owner-algebra-construct-validity-v4-2026-08-23/OWNER_GROUP_FEASIBILITY_V4.json": "9675a577a54b6175d01907af16145a9f010744e7b66c7d004e742320e6c2f394",
        "development/p1-owner-algebra-construct-validity-v4-2026-08-23/STANDARD_NATIVE_ACTION_ENVELOPE_V4.json": "d6dd6bab21ef971e966b081e357691581f7106bf029059d0854144ae72a7dc97",
        "development/p1-owner-algebra-construct-validity-v4-2026-08-23/RESULT_V4.json": "cb09da0c5299b7f34837d8bef63cc4bd1348e38e202fb85840549fdcdfd91f12",
        "development/p1-scientific-blocker-compression-2026-08-23/OWNER_ALGEBRA_V9_COMPLETION_CONTRACT.json": "32a4af7b6adb9dd8250e072470605e574ed695145818da3b87cdeec3feef92b1",
        "../lane-handoffs/p1-source-native-action-adapter-v2/ADAPTER_COMPATIBILITY_MATRIX_V2.json": "64d44ae85dc54411ae083c35f53090ac6776ec81e57a2425113c437f3fd746d5",
    }
    upstream_receipts: list[dict[str, object]] = []
    for relative, expected in upstream_expected.items():
        path = (REPO / relative).resolve()
        exists = path.is_file()
        actual = sha256(path) if exists else None
        matches = actual == expected
        upstream_receipts.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "exists": exists,
                "matches": matches,
            }
        )
        if not matches:
            errors.append(f"upstream_binding_failed:{relative}")

    v8 = json.loads(
        (
            REPO
            / "development/p1-source-native-target-semantics-v8-2026-08-23/P1_RESULT_V8.json"
        ).read_text()
    )
    v4 = json.loads(
        (
            REPO
            / "development/p1-owner-algebra-construct-validity-v4-2026-08-23/RESULT_V4.json"
        ).read_text()
    )
    v9 = json.loads(
        (
            REPO
            / "development/p1-scientific-blocker-compression-2026-08-23/OWNER_ALGEBRA_V9_COMPLETION_CONTRACT.json"
        ).read_text()
    )

    frozen = protocol.get("frozen_counts", {})
    expected_counts = {
        "owner_requirement_groups": 12,
        "current_sufficient_groups": 0,
        "unchanged_map_space": 117649,
        "currently_rejected_maps": 116929,
        "currently_cannot_check_maps": 720,
        "currently_certified_maps": 0,
        "scientific_action_gold_cells": 0,
    }
    for key, value in expected_counts.items():
        if frozen.get(key) != value:
            errors.append(f"protocol_count_mismatch:{key}")

    if (
        frozen.get("currently_rejected_maps", 0)
        + frozen.get("currently_cannot_check_maps", 0)
        + frozen.get("currently_certified_maps", 0)
        != frozen.get("unchanged_map_space")
    ):
        errors.append("map_partition_invalid")

    if v8["adapter_result"].get("remain_cannot_check") != 720:
        errors.append("v8_cannot_check_count_drift")
    if v4["owner_algebra"].get("sufficient_groups") != 0:
        errors.append("v4_sufficient_group_count_drift")
    if v4.get("scientific_action_gold_cells") != 0:
        errors.append("v4_gold_count_drift")
    if len(v9.get("required_owner_deliverables", [])) != 4:
        errors.append("v9_four_authority_acts_drift")
    if any(v9.get("current_bindings", {}).values()):
        errors.append("v9_current_binding_must_remain_false")

    repair = protocol.get("minimal_repair", {})
    if repair.get("new_authority_roles") != 0:
        errors.append("v10_must_not_invent_fifth_authority_role")
    if repair.get("retained_non_substitutable_authority_acts") != 4:
        errors.append("v10_must_retain_four_authority_acts")
    if repair.get("added_predicate_count") != 1:
        errors.append("v10_must_add_exactly_one_ordering_predicate")

    orders = [gate.get("order") for gate in protocol.get("ordered_gates", [])]
    if orders != list(range(1, 8)):
        errors.append("ordered_gate_sequence_invalid")
    if protocol.get("current_execution_authorized") is not False:
        errors.append("protocol_must_not_authorize_execution")
    if protocol.get("map_audit_authorized") is not False:
        errors.append("protocol_must_not_authorize_map_audit")
    if protocol.get("case_or_outcome_access_authorized") is not False:
        errors.append("protocol_must_not_authorize_case_or_outcome_access")

    allowed = allowlist.get("allowlisted_local_artifacts", [])
    if len(allowed) != 3:
        errors.append("owner_allowlist_must_have_exactly_three_local_artifacts")
    allowed_paths = {entry.get("path") for entry in allowed}
    forbidden_fragments = (
        "720_ADAPTER",
        "ADAPTER_ADJUDICATION",
        "COMPATIBILITY_MATRIX",
        "OWNER_GROUP_FEASIBILITY",
        "STANDARD_NATIVE_ACTION_ENVELOPE",
        "RESULT_V",
    )
    for path in allowed_paths:
        if not isinstance(path, str) or any(x in path for x in forbidden_fragments):
            errors.append(f"forbidden_artifact_in_owner_allowlist:{path}")
    if allowlist.get("current_delivery_executed") is not False:
        errors.append("allowlist_must_not_claim_delivery")
    if allowlist.get("current_custody_receipt_bound") is not False:
        errors.append("allowlist_must_not_claim_custody_receipt")

    bindings = result.get("current_bindings", {})
    if any(bindings.values()):
        errors.append("result_current_bindings_must_all_be_false")
    if result.get("case_or_outcome_accessed") is not False:
        errors.append("result_case_or_outcome_boundary_broken")
    if result.get("map_audit_rerun") is not False:
        errors.append("result_must_not_claim_map_audit_rerun")
    if result.get("terminal") != EXPECTED_TERMINAL:
        errors.append("result_terminal_drift")
    if protocol.get("cannot_check_terminal") != EXPECTED_TERMINAL:
        errors.append("protocol_terminal_drift")

    local_files = [
        "README.md",
        "POST_SELECTION_NONIDENTIFICATION_THEOREM_V10.md",
        "OWNER_INPUT_ALLOWLIST_V10.json",
        "ADAPTER_BLIND_RATIFICATION_PROTOCOL_V10.json",
        "CURRENT_RESULT_V10.json",
        "SCIENTIFIC_REPORT_V10.md",
        "verify_v10.py",
    ]
    local_hashes = {name: sha256(HERE / name) for name in local_files}
    receipt = {
        "schema_version": "orion.p1.adapter-blind-owner-ratification.validation.v10",
        "validated_at": "2026-08-23T00:00:00+00:00",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "validated_counts": expected_counts,
        "allowlisted_local_artifacts": len(allowed),
        "retained_authority_acts": repair.get(
            "retained_non_substitutable_authority_acts"
        ),
        "new_authority_roles": repair.get("new_authority_roles"),
        "new_ordering_predicates": repair.get("added_predicate_count"),
        "upstream_bindings": upstream_receipts,
        "local_artifact_sha256": local_hashes,
        "boundary": {
            "network_used": False,
            "pytest_or_repository_ci_run": False,
            "git_operation_run": False,
            "manuscript_or_shared_ledger_edited": False,
            "case_or_outcome_accessed": False,
            "map_audit_rerun": False,
        },
        "terminal": EXPECTED_TERMINAL,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"status={receipt['status']}")
    print(f"errors={len(errors)}")
    print(f"upstream_bindings={len(upstream_receipts)}")
    print(f"allowlisted_local_artifacts={len(allowed)}")
    print("map_audit_rerun=false")
    return 0 if not errors else 3


if __name__ == "__main__":
    raise SystemExit(main())
