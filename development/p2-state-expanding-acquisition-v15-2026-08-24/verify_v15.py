#!/usr/bin/env python3
"""Read-only deterministic validator for the P2 V15 packet."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V14 = ROOT.parent / "p2-state-expanding-acquisition-v14-2026-08-24"
PROTOCOL_SHA256 = "a492bf47620651b35542b64ac9bc1da115ef793d0998e14a3fa43ab98f64c29c"
checks: list[dict] = []


def check(name: str, condition: bool) -> None:
    checks.append({"check": name, "pass": bool(condition)})
    if not condition:
        raise AssertionError(name)


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


json_files = sorted(path for path in ROOT.rglob("*.json") if path.name != "VALIDATION_RECEIPT_V15.json")
for path in json_files:
    json.loads(path.read_text())
check("all_json_machine_readable", len(json_files) >= 15)
check("v14_result_immutable", sha(V14 / "RESULT_V14.json") == "95496f053d762173285b9fbb436ff19bad08f47a82e278bb44715b565a0cd333")
check("v14_sums_immutable", sha(V14 / "SHA256SUMS") == "8bb23e1c91d59328b64c70fc04af39840c78830f4d4cea1d588f2698495234e6")
check("v14_discriminator_immutable", sha(V14 / "NEXT_DISCRIMINATOR_V15.json") == "a4b56974558bf93692ca13aa90ccb9839466636b352a1eab90e67774e989e0b6")

protocol = load("PROTOCOL_V15.json")
freeze = load("PROTOCOL_FREEZE_RECEIPT_V15.json")
check("protocol_hash_frozen", sha(ROOT / "PROTOCOL_V15.json") == freeze["protocol_sha256"] == PROTOCOL_SHA256)
check("protocol_no_pre_access", freeze["network_requests_before_freeze"] == freeze["index_json_parses_before_freeze"] == freeze["review_csv_requests_before_freeze"] == 0)
check("coherent_tuple_frozen", protocol["coherent_single_snapshot_repair"] == {"candidate_dataset_template": "https://raw.githubusercontent.com/asreview/synergy-dataset/38b35218e4d0f99621cec5a8a25a0147bb88c654/datasets/{review_id}.csv", "commit": "38b35218e4d0f99621cec5a8a25a0147bb88c654", "index_bytes": 22135, "index_git_blob_sha1": "f4f5007156cb71e7d54e99057037fb75d44f87c4", "index_path": "index_v1.json", "index_sha256": "f34c17b3dca9d609585e5fcc9d24c5433d4ad240ef91e5c2e9a48edee1e0959a", "repair_boundary": protocol["coherent_single_snapshot_repair"]["repair_boundary"], "repository": "asreview/synergy-dataset", "root_tree_sha1": "49f437c367cc45a90867418fcef77c9ff3614456"})
check("later_route_disallowed", protocol["preserved_adverse_lineage"]["later_owner_commit"] == "dc2dadfdbb98eb1b4259604789abd640aa3b693e" and protocol["preserved_adverse_lineage"]["substitution_allowed"] is False)

probe = load("PROBE_RECEIPT_V15.json")
check("probe_protocol_hash", probe["protocol_sha256"] == PROTOCOL_SHA256)
freeze_time = dt.datetime.fromisoformat(freeze["frozen_at_utc"].replace("Z", "+00:00"))
request_times = [dt.datetime.fromisoformat(item["started_at"]) for item in probe["requests"]]
check("seven_requests_after_freeze", probe["request_count"] == len(probe["requests"]) == 7 and all(freeze_time <= value for value in request_times))
for item in probe["requests"]:
    body = ROOT / item["body_path"]
    receipt = ROOT / "evidence" / f"{item['name']}.receipt.json"
    check(f"body_exists_{item['name']}", body.is_file())
    check(f"body_hash_{item['name']}", body.stat().st_size == item["body_bytes"] and sha(body) == item["body_sha256"])
    check(f"receipt_exists_{item['name']}", receipt.is_file())

qualification = load("PROVIDER_QUALIFICATION_V15.json")
check("qualification_protocol_hash", qualification["protocol_sha256"] == PROTOCOL_SHA256)
check("signed_commit_exact", qualification["commit"]["sha"] == "38b35218e4d0f99621cec5a8a25a0147bb88c654" and qualification["commit"]["tree_sha1"] == "49f437c367cc45a90867418fcef77c9ff3614456" and qualification["commit"]["verification"]["verified"] is True and qualification["commit"]["verification"]["reason"] == "valid")
check("recursive_tree_complete", qualification["recursive_tree"] == {"blob_count": 140, "entry_count": 169, "pass": True, "sha": "49f437c367cc45a90867418fcef77c9ff3614456", "status": 200, "truncated": False})
check("index_tree_entry_exact", qualification["index_entry"]["pass"] is True and qualification["index_entry"]["matching_entry_count"] == 1 and qualification["index_entry"]["entry"]["sha"] == "f4f5007156cb71e7d54e99057037fb75d44f87c4" and qualification["index_entry"]["entry"]["size"] == 22135 and qualification["index_entry"]["body_requested"] is False and qualification["index_entry"]["json_parsed"] is False)
manifest = qualification["same_snapshot_dataset_path_manifest"]["manifest"]
check("dataset_manifest_61", qualification["same_snapshot_dataset_path_manifest"]["count"] == len(manifest) == 61 and all(item["path"].startswith("datasets/") and item["path"].endswith(".csv") and item["mode"] == "100644" for item in manifest))
check("dataset_bodies_not_requested", qualification["same_snapshot_dataset_path_manifest"]["bodies_requested"] is False and qualification["same_snapshot_dataset_path_manifest"]["labels_or_class_counts_inspected"] is False)
check("exact_snapshot_root_mit", qualification["rights_witness"]["status"] == 200 and qualification["rights_witness"]["api_path"] == "LICENSE" and qualification["rights_witness"]["git_blob_sha1"] == "72f8c206ed3b5e333f94f3dffde2b525fb449954" and qualification["rights_witness"]["decoded_bytes"] == 1064 and qualification["rights_witness"]["decoded_sha256"] == "f1e934ccb74b86e49caa93146e16d342c86885d06a4b8d087679c3ac5689bbad" and qualification["rights_witness"]["license"]["spdx_id"] == "MIT")
check("current_cc0_not_blended", qualification["rights_witness"]["repository_api_license"]["spdx_id"] == "CC0-1.0" and "per-review" in qualification["rights_witness"]["boundary"])
tag_rows = {item["ref"]: item["object"] for item in qualification["provider_relations"]["tag_refs"]}
check("metadata_v1_final_tag_exact", tag_rows["refs/tags/metadata-v1-final"]["sha"] == "38b35218e4d0f99621cec5a8a25a0147bb88c654" and tag_rows["refs/tags/metadata-v1-final"]["type"] == "commit")
check("attestation_absent", qualification["provider_relations"]["index_attestation_status"] == 404 and qualification["provider_relations"]["v15_contract_predicate_present"] is False)
check("provider_positive_custody_negative", all(qualification["gates"][name] is True for name in ["coherent_commit_tree", "coherent_index_tree_entry", "provider_signature_valid", "recursive_tree_complete", "repository_rights_witness", "same_snapshot_dataset_path_manifest_nonempty"]) and qualification["gates"]["provider_native_v15_contract_predicate"] is False and qualification["gates"]["independent_source_custody"] is False)

actions = probe["actions"]
check("zero_protected_data_actions", actions["index_json_requests"] == actions["index_json_parses"] == actions["review_csv_requests"] == actions["review_population_censuses"] == actions["learner_or_model_runs"] == actions["ranking_or_metric_runs"] == 0 and actions["label_values_inspected_or_retained"] is False and actions["class_counts_inspected_or_retained"] is False)
check("no_pytest_or_ci", actions["pytest_or_repository_ci_runs"] == 0)

correction = load("IMPLEMENTATION_CORRECTION_V15B.json")
check("template_error_preserved", correction["error"] == "FROZEN_V15_CANDIDATE_TEMPLATE_DIVERGES_FROM_IMMUTABLE_V14_TEMPLATE" and correction["v15_frozen_template"] == protocol["coherent_single_snapshot_repair"]["candidate_dataset_template"] and correction["immutable_v14_template"] == "https://raw.githubusercontent.com/asreview/synergy-dataset/38b35218e4d0f99621cec5a8a25a0147bb88c654/datasets/{review}/output/{review}.csv")
check("correction_no_authority", correction["authorization"] == {"candidate_request": False, "census": False, "index_parse": False, "performance": False, "reuse_provider_metadata_as_descriptive_witness": True})

custody = load("INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.json")
check("custody_manifest_hash", custody["provider_witness"]["same_snapshot_dataset_csv_count"] == 61 and custody["provider_witness"]["same_snapshot_dataset_manifest_sha256"] == canonical_sha(manifest))
check("candidate_author_cannot_sign", custody["candidate_author_session_must_not_sign"] is True and "Generic commit" in custody["acceptance_gate"])

negative = load("NEGATIVE_RESULT_LEDGER_V15.json")
check("three_residuals_have_discriminators", len(negative["rows"]) == 3 and all("next_discriminator" in item for item in negative["rows"]))
result = load("RESULT_V15.json")
check("result_provider_positive", result["positive_result"]["commit_tree_index_coherent"] is True and result["positive_result"]["provider_commit_signature_valid"] is True and result["positive_result"]["same_snapshot_dataset_csv_count"] == 61 and result["positive_result"]["same_snapshot_dataset_manifest_sha256"] == canonical_sha(manifest))
check("result_boundaries", result["custody"]["provider_snapshot_authentication"] is True and result["custody"]["independent_source_population_custody"] is False and result["gates"] == {"coherent_provider_snapshot": True, "independent_source_custody": False, "label_blind_census_authorized": False, "matched_performance_authorized": False})
check("result_rights_boundary", result["rights"] == {"current_metadata_substituted_as_historical_rights": False, "current_repository_metadata_license_spdx": "CC0-1.0", "exact_snapshot_root_license_sha256": "f1e934ccb74b86e49caa93146e16d342c86885d06a4b8d087679c3ac5689bbad", "exact_snapshot_root_license_spdx": "MIT", "per_review_exact_rights_closed": False})
check("result_zero_science_actions", result["actions"]["index_json_parses"] == result["actions"]["review_csv_requests"] == result["actions"]["review_population_censuses"] == result["actions"]["learner_or_model_runs"] == result["actions"]["ranking_or_metric_runs"] == result["actions"]["performance_arms"] == 0 and result["actions"]["manuscript_updated"] is False and result["actions"]["shared_ledger_updated"] is False)
check("result_verdict_bounded", result["verdict"] == "POSITIVE_COHERENT_PROVIDER_SNAPSHOT__CENSUS_AND_PERFORMANCE_WITHHELD" and "not an eligible population or performance result" in result["claim_boundary"])
check("v14_adverse_preserved", result["preserved_v14"]["result_sha256"] == "95496f053d762173285b9fbb436ff19bad08f47a82e278bb44715b565a0cd333" and result["preserved_v14"]["historical_owner_substituted"] is False)
for name, metadata in result["evidence"].items():
    path = ROOT / name if not name.startswith("development/") else ROOT.parent.parent / name
    check(f"evidence_exists_{path.name}", path.is_file())
    check(f"evidence_hash_{path.name}", path.stat().st_size == metadata["bytes"] and sha(path) == metadata["sha256"])

sums_path = ROOT / "SHA256SUMS"
if sums_path.exists():
    rows = []
    for line in sums_path.read_text().splitlines():
        digest, rel = line.split("  ", 1)
        rows.append((digest, rel))
    actual_files = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file() and path.name != "SHA256SUMS")
    check("sha256sums_complete_file_set", [rel for _, rel in rows] == actual_files)
    check("sha256sums_all_match", all(sha(ROOT / rel) == digest for digest, rel in rows))

receipt = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.validation",
    "validation_basis": "read-only deterministic packet-local chronology, hash, provider snapshot, custody, protected-data stop and bounded-claim checks",
    "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "json_file_count_excluding_receipt": len(json_files),
    "check_count": len(checks),
    "passed": sum(item["pass"] for item in checks),
    "failed": sum(not item["pass"] for item in checks),
    "checks": checks,
    "validator_read_only": True,
    "pytest_or_repository_ci_runs": 0,
    "git_operation_run": False,
}
print(json.dumps(receipt, indent=2, sort_keys=True))
