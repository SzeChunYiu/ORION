#!/usr/bin/env python3
"""Fail-closed validation for the P1 blocker-compression packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "VALIDATION_RECEIPT_V1.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def main() -> int:
    errors: list[str] = []
    compression = load("BLOCKER_COMPRESSION_V1.json")
    owner = load("OWNER_ALGEBRA_V9_COMPLETION_CONTRACT.json")
    bridge = load("RW_CC0_NATURALISTIC_BRIDGE_V1.json")
    alignment = load("MANUSCRIPT_ALIGNMENT_CHECK_V1.json")

    if compression.get("scientific_root_count") != 2:
        errors.append("scientific_root_count_must_equal_2")
    roots = compression.get("roots", [])
    if len(roots) != 2 or len({r.get("root_id") for r in roots}) != 2:
        errors.append("exactly_two_distinct_roots_required")
    if compression.get("execution_authorized") is not False:
        errors.append("compression_must_not_authorize_execution")
    if compression.get("case_or_outcome_accessed") is not False:
        errors.append("compression_case_or_outcome_boundary_broken")

    r1 = roots[0].get("exact_facts", {}) if roots else {}
    expected_r1 = {
        "owner_algebra_requirement_groups": 12,
        "named_custodian_or_delegation_groups": 0,
        "sufficient_owner_groups": 0,
        "scientific_action_gold_cells": 0,
        "adapter_maps_total": 117649,
        "adapter_maps_rejected": 116929,
        "adapter_maps_cannot_check": 720,
        "adapter_maps_certified": 0,
    }
    for key, value in expected_r1.items():
        if r1.get(key) != value:
            errors.append(f"r1_count_mismatch:{key}")
    if r1.get("adapter_maps_rejected", 0) + r1.get(
        "adapter_maps_cannot_check", 0
    ) + r1.get("adapter_maps_certified", 0) != r1.get("adapter_maps_total"):
        errors.append("r1_map_partition_invalid")

    r2 = roots[1].get("exact_facts", {}) if len(roots) > 1 else {}
    expected_r2 = {
        "retraction_watch_pinned_rows_counted_without_field_display": 71944,
        "rw_structurally_admitted_metadata_relations": 49878,
        "rights_valid_metadata_relations": 12038,
        "rights_valid_metadata_source_families": 11602,
        "structured_action_records_retraction": 11251,
        "structured_action_records_correction_or_erratum": 256,
        "structured_action_records_expression_of_concern": 469,
        "structured_action_records_other_or_cannot_check": 15,
        "structured_action_records_ambiguous": 0,
        "europe_pmc_frozen_metadata_queries": 5,
        "europe_pmc_notice_class_hits_not_deduplicated": 218014,
        "europe_pmc_retracted_original_hits": 18056,
        "complete_source_clusters": 0,
        "rights_admissible_case_dossier_pairs": 0,
        "case_eligibility_decisions": 0,
        "primary_comparator_arms_ready": 0,
        "required_primary_comparator_arms": 9,
        "external_custody_roles_bound": 0,
        "registered_external_binding_rows": 14,
        "source_clusters_required_both_waves": 896,
        "system_outcomes_accessed": 0,
    }
    for key, value in expected_r2.items():
        if r2.get(key) != value:
            errors.append(f"r2_count_mismatch:{key}")

    if owner.get("identity") != (
        "P1_R7_LICENSED_OWNER_RATIFIED_TARGET_ALGEBRA_AND_INDEPENDENT_REVIEW_V9"
    ):
        errors.append("owner_successor_identity_drift")
    if owner.get("case_or_outcome_access_authorized") is not False:
        errors.append("owner_contract_must_fail_closed")
    if any(owner.get("current_bindings", {}).values()):
        errors.append("owner_contract_cannot_claim_current_bindings")
    if owner.get("frozen_counts", {}).get("currently_certified_maps") != 0:
        errors.append("owner_contract_certified_map_drift")

    if bridge.get("execution_authorized") is not False:
        errors.append("bridge_must_not_authorize_execution")
    if bridge.get("source_bindings", {}).get("development_backbone", {}).get(
        "metadata_licence"
    ) != "CC0":
        errors.append("rw_rights_binding_missing")
    current = bridge.get("current_counts", {})
    zero_scientific_keys = (
        "eligible_source_clusters",
        "scientific_action_gold_cells",
        "ready_comparator_arms",
        "external_custody_roles_bound",
        "system_outcomes",
    )
    if any(current.get(k) != 0 for k in zero_scientific_keys):
        errors.append("bridge_current_scientific_counts_must_remain_zero")
    if current.get("rights_valid_metadata_relations") != 12038:
        errors.append("bridge_rights_valid_metadata_relation_drift")
    if current.get("rights_valid_metadata_families") != 11602:
        errors.append("bridge_rights_valid_metadata_family_drift")
    if bridge.get("registered_scale_preserved", {}).get("total_source_clusters") != 896:
        errors.append("registered_scale_drift")

    if alignment.get("claim_alignment_state") != "INTEGRATED_IN_CURRENT_SHARED_WORKTREE":
        errors.append("manuscript_alignment_not_integrated")
    if alignment.get("legacy_patch", {}).get("dry_run_exit") != 1:
        errors.append("legacy_patch_drift_check_must_record_exit_1")
    alignment_sources = alignment.get("source_snapshot", [])
    marker_corpus_parts: list[str] = []
    for item in alignment_sources:
        source_path = REPO / item["path"]
        if not source_path.is_file():
            errors.append(f"manuscript_alignment_source_missing:{item['path']}")
            continue
        if digest(source_path) != item["sha256"]:
            errors.append(f"manuscript_alignment_source_drift:{item['path']}")
        marker_corpus_parts.append(source_path.read_text(errors="replace"))
    marker_corpus = "\n".join(marker_corpus_parts)
    for marker in alignment.get("required_markers_present", []):
        if marker not in marker_corpus:
            errors.append(f"manuscript_alignment_marker_missing:{marker}")

    upstream_results: list[dict[str, object]] = []
    for binding in compression.get("upstream_bindings", []):
        path = (REPO / binding["path"]).resolve()
        exists = path.is_file()
        actual = digest(path) if exists else None
        matches = exists and actual == binding["sha256"]
        upstream_results.append(
            {
                "path": binding["path"],
                "expected_sha256": binding["sha256"],
                "actual_sha256": actual,
                "exists": exists,
                "matches": matches,
            }
        )
        if not matches:
            errors.append(f"upstream_binding_failed:{binding['path']}")

    local_files = [
        "BLOCKER_COMPRESSION_V1.json",
        "BLOCKER_COMPRESSION_V1.md",
        "OWNER_ALGEBRA_V9_COMPLETION_CONTRACT.json",
        "RW_CC0_NATURALISTIC_BRIDGE_V1.json",
        "MANUSCRIPT_ALIGNMENT_CHECK_V1.json",
        "README.md",
        "validate_packet.py",
    ]
    local_digests = {name: digest(HERE / name) for name in local_files}
    receipt = {
        "schema_version": "orion.p1.scientific-blocker-compression.validation.v1",
        # Bind validation to the packet date so a verification rerun is
        # byte-stable and does not invalidate the packet manifest.
        "validated_at": f"{compression['date']}T00:00:00+00:00",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "validated_counts": {
            "scientific_roots": len(roots),
            "owner_requirement_groups": r1.get("owner_algebra_requirement_groups"),
            "owner_sufficient_groups": r1.get("sufficient_owner_groups"),
            "adapter_maps_total": r1.get("adapter_maps_total"),
            "adapter_maps_cannot_check": r1.get("adapter_maps_cannot_check"),
            "rw_rows_counted_without_field_display": r2.get(
                "retraction_watch_pinned_rows_counted_without_field_display"
            ),
            "rw_structurally_admitted_metadata_relations": r2.get(
                "rw_structurally_admitted_metadata_relations"
            ),
            "rights_valid_metadata_relations": r2.get(
                "rights_valid_metadata_relations"
            ),
            "rights_valid_metadata_source_families": r2.get(
                "rights_valid_metadata_source_families"
            ),
            "structured_action_records_retraction": r2.get(
                "structured_action_records_retraction"
            ),
            "structured_action_records_correction_or_erratum": r2.get(
                "structured_action_records_correction_or_erratum"
            ),
            "structured_action_records_expression_of_concern": r2.get(
                "structured_action_records_expression_of_concern"
            ),
            "structured_action_records_other_or_cannot_check": r2.get(
                "structured_action_records_other_or_cannot_check"
            ),
            "structured_action_records_ambiguous": r2.get(
                "structured_action_records_ambiguous"
            ),
            "europe_pmc_frozen_queries": r2.get("europe_pmc_frozen_metadata_queries"),
            "complete_source_clusters": r2.get("complete_source_clusters"),
            "ready_comparator_arms": r2.get("primary_comparator_arms_ready"),
            "external_custody_roles_bound": r2.get("external_custody_roles_bound"),
            "system_outcomes_accessed": r2.get("system_outcomes_accessed"),
        },
        "upstream_bindings": upstream_results,
        "local_artifact_sha256": local_digests,
        "boundary": {
            "network_used": False,
            "pytest_or_repository_ci_run": False,
            "manuscript_or_shared_matrix_edited": False,
            "case_or_outcome_accessed": False,
            "execution_authorized": False,
        },
        "terminal": compression.get("current_terminal"),
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"status={receipt['status']}")
    print(f"errors={len(errors)}")
    print(f"upstream_bindings={len(upstream_results)}")
    print(f"scientific_roots={len(roots)}")
    return 0 if not errors else 3


if __name__ == "__main__":
    raise SystemExit(main())
