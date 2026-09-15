#!/usr/bin/env python3
"""Validate the cross-session provenance packet without running repo tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/billy/Desktop/projects/ORION-claude")
OUT = ROOT / "development/cross-session-empirical-provenance-audit-2026-08-23"
TERMINAL = (
    "CROSS_SESSION_EMPIRICAL_PROVENANCE_AUDIT_P1_P3_COMPLETE__"
    "NO_RECORD_PROMOTED__TOP_TIER_EMPIRICAL_CLAIMS_CANNOT_CHECK"
)


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_status_digest() -> tuple[int, str]:
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z"]
    )
    excluded = b"?? development/cross-session-empirical-provenance-audit-2026-08-23/"
    entries = [item for item in raw.split(b"\0") if item and not item.startswith(excluded)]
    canonical = b"\0".join(entries) + (b"\0" if entries else b"")
    return len(entries), hashlib.sha256(canonical).hexdigest()


def main() -> None:
    source = load("SOURCE_CHECKOUT_RECEIPT.json")
    evidence = load("PROVENANCE_AUDIT_EVIDENCE.json")
    admission = load("ADMISSION_MATRIX.json")
    ledger = load("NEGATIVE_RESULT_LEDGER.json")
    result = load("RESULT.json")

    head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    assert head == source["head_at_audit_start"] == source["head_at_audit_end"]
    entry_count, status_digest = source_status_digest()
    recorded_status = source["source_status_at_end_excluding_audit_path"]
    assert entry_count == recorded_status["entry_count"] == 72
    assert status_digest == recorded_status["porcelain_v1_z_sha256"]
    assert source["head_stable_during_audit"] is True
    assert source["source_status_stable_during_audit"] is True
    assert source["commits_after_parent_observed_head"] == 1
    assert source["selected_file_count"] == 121
    assert source["selected_git_tracked_file_count"] == 9
    assert source["selected_tracked_files_identical_parent_observed_to_audit_head"] == 9
    assert source["selected_tracked_files_missing_at_parent_observed_head"] == 0
    assert source["selected_tracked_files_different_parent_observed_to_audit_head"] == 0
    for item in source["selected_files"]:
        path = ROOT / item["path"]
        assert path.is_file()
        assert path.stat().st_size == item["bytes"]
        assert sha(path) == item["sha256"]

    p1 = evidence["p1"]
    assert p1["files"]["pilot_runs.jsonl"]["rows"] == 990
    assert p1["files"]["pilot_runs.jsonl"]["unique_case_system_seed"] == 990
    assert p1["files"]["pilot_runs.jsonl"]["model_token_nonzero_rows"] == 0
    assert p1["files"]["test_runs.jsonl"]["rows"] == 2_880
    assert p1["files"]["test_runs.jsonl"]["unique_case_system_seed"] == 2_880
    assert p1["test_live_provider_rows"] == 240
    assert p1["test_live_provider_model_tokens_sum"] == 289_261
    assert p1["evidence_class"] == "HIDDEN_FORMULATION_HARNESS"
    assert p1["naturalistic_v2_v3_action_evidence_admissible"] is False

    annotations = evidence["p3"]["annotations"]
    assert annotations["files"] == 32
    assert annotations["source_references"] == 64
    assert annotations["document_ids_with_seed_placeholder"] == 64
    assert annotations["text_hash_seed_prefix"] == 64
    assert annotations["valid_64_hex_text_hashes"] == 0
    assert annotations["unique_placeholder_text_hashes"] == 63
    assert annotations["duplicate_placeholder_hash_excess"] == 1
    assert annotations["annotator_a_filename_count"] == 32
    assert annotations["annotator_b_filename_count"] == 0
    assert annotations["tracked_combined_gold_text_hash_matches_text_sha256"] == 0
    assert annotations["freeze_two_annotator_status"]["independent_labels_exist"] is False
    assert annotations["freeze_two_annotator_status"]["coordinate_agreement_computable"] is False

    full = evidence["p3"]["run_full"]
    manifest = full["manifest"]
    results = full["results"]
    checkpoint = full["checkpoint_final"]
    pre = full["checkpoint_pre_retry"]
    code = full["code_evidence"]
    assert manifest["gold_hash_matches_current_combined_gold_bytes"] is False
    assert manifest["source_revision_bound"] is False
    assert results["rows"] == results["unique_system_seed"] == 75
    assert results["status_counts"] == {"PASS": 75}
    assert results["orion_full_pass_rows"] == 5
    assert set(results["zero_cost_field_rows"].values()) == {75}
    assert results["cost_metrics_error_counts"] == {"-1.0": 75}
    assert results["raw_artifact_hash_matches_system_seed_key_rows"] == 75
    assert results["source_revision_bound"] is False
    assert checkpoint["rows"] == 3_340
    assert checkpoint["unique_sid_case_seed"] == 2_400
    assert checkpoint["duplicate_excess"] == 940
    assert checkpoint["keys_with_duplicates"] == 683
    assert checkpoint["duplicate_keys_with_conflicting_payloads"] == 683
    assert checkpoint["exact_duplicate_excess"] == 0
    assert checkpoint["max_key_multiplicity"] == 7
    assert checkpoint["keys_not_in_pre_retry"] == 72
    assert pre["rows"] == 2_720
    assert pre["unique_sid_case_seed"] == 2_328
    assert pre["duplicate_excess"] == 392
    assert code["cost_metric_signature_mismatch_present"] is True
    assert code["checkpoint_analysis_last_write_wins_dict_comprehension_present"] is True
    assert code["full_orion_stub_marker_present"] is True
    assert code["zero_cost_metadata_literal_present"] is True

    analysis = evidence["p3"]["analysis_directory"]
    assert analysis["aggregate_system_count"] == 0
    assert analysis["metric_seed_counts"] == {"ORION_FULL": 1, "VanillaLongContext": 1}
    assert evidence["p3"]["empirical_promotion_allowed"] is False
    assert evidence["overall_terminal"] == TERMINAL

    summary = admission["primary_candidate_file_summary"]
    assert summary == {
        "audit_fact_admissible_files": 46,
        "exact_narrow_empirical_claim_admissible_files": 2,
        "file_count": 46,
        "naturalistic_or_real_source_claim_admissible_files": 0,
        "top_tier_empirical_promotion_rejected_or_cannot_check_files": 46,
    }
    assert admission["non_primary_files"] == {
        "run_full_log_files_hashed_not_semantically_opened": 66,
        "selected_file_inventory_total": 121,
        "tracked_context_or_code_files_used_for_interpretation": 9,
    }
    assert len(ledger["entries"]) == 12
    assert all("next_discriminator" in item for item in ledger["entries"])
    assert result["terminal"] == admission["terminal"] == ledger["terminal"] == TERMINAL
    assert result["file_admission"] == summary
    assert result["p1"]["naturalistic_v2_v3_action_admissible"] is False
    assert result["p3"]["empirical_promotion_allowed"] is False
    assert result["artifacts"]["source_checkout_receipt_sha256"] == sha(
        OUT / "SOURCE_CHECKOUT_RECEIPT.json"
    )
    assert result["artifacts"]["provenance_audit_evidence_sha256"] == sha(
        OUT / "PROVENANCE_AUDIT_EVIDENCE.json"
    )
    assert result["artifacts"]["admission_matrix_sha256"] == sha(OUT / "ADMISSION_MATRIX.json")
    assert result["artifacts"]["negative_result_ledger_sha256"] == sha(
        OUT / "NEGATIVE_RESULT_LEDGER.json"
    )

    forbidden = [
        path.name
        for path in OUT.iterdir()
        if path.is_file() and path.suffix in {".jsonl", ".log", ".csv"}
    ]
    assert forbidden == []

    names = sorted(
        path.name
        for path in OUT.iterdir()
        if path.is_file()
        and path.name not in {"VALIDATION_RECEIPT.json", "SHA256SUMS"}
    )
    receipt = {
        "schema_version": "orion.cross-session-empirical-provenance.validation-receipt.v1",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "assertion_count": 78,
        "terminal": TERMINAL,
        "scientific_checks": {
            "primary_candidate_files": 46,
            "naturalistic_or_real_source_admissible_files": 0,
            "top_tier_rejected_or_cannot_check_files": 46,
            "p1_pilot_rows": 990,
            "p1_test_rows": 2_880,
            "p3_source_references": 64,
            "p3_valid_source_hashes": 0,
            "p3_independent_annotator_b_files": 0,
            "p3_results": 75,
            "p3_zero_cost_and_error_rows": 75,
            "p3_checkpoint_duplicate_excess": 940,
            "p3_conflicting_duplicate_keys": 683,
        },
        "boundary": {
            "pytest_or_repo_ci_run": False,
            "raw_payload_imported": False,
            "record_promoted": False,
            "source_files_mutated": False,
            "manuscript_or_readiness_files_mutated": False,
        },
        "validated_artifact_sha256": {name: sha(OUT / name) for name in names},
    }
    (OUT / "VALIDATION_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"status": "PASS", **receipt["scientific_checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
