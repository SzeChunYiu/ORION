#!/usr/bin/env python3
"""Read-only deterministic validator for the P4 V12 packet."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V11 = ROOT.parent / "p4-exact-edge-lineage-authority-v11-2026-08-24"
PROTOCOL_SHA256 = "9bc43bfae807d3d69ac01696786987e0e7e583421dc0e77d1af3f22ef7bec1dd"
checks: list[dict] = []


def check(name: str, condition: bool) -> None:
    checks.append({"check": name, "pass": bool(condition)})
    if not condition:
        raise AssertionError(name)


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


json_files = sorted(
    path for path in ROOT.rglob("*.json") if path.name != "VALIDATION_RECEIPT_V12.json"
)
for path in json_files:
    json.loads(path.read_text())
check("all_json_machine_readable", len(json_files) >= 21)
check(
    "v11_result_immutable",
    sha(V11 / "RESULT_V11.json")
    == "dee86c33a0347df5da2425ebc606c12020cfffdff6ac21cea6b23b570ad8fef4",
)
check(
    "v11_sha256sums_immutable",
    sha(V11 / "SHA256SUMS")
    == "72cb2fd2a3e0830fe113a69e8db2311416dab67b5cab59a1c732a20ea0048eed",
)

freeze = load("PROTOCOL_FREEZE_RECEIPT_V12.json")
protocol = load("PROTOCOL_V12.json")
check("protocol_hash_frozen", sha(ROOT / "PROTOCOL_V12.json") == freeze["protocol_sha256"] == PROTOCOL_SHA256)
check("protocol_outcome_boundary", protocol["outcome_informed"] is True and protocol["new_outcome_access_before_freeze"] is True)
check("protocol_frozen_expected_counts", freeze["source_count"] == freeze["expected_output_count"] == 106)
check("protocol_source_manifest_count", protocol["source_freeze"]["source_count"] == len(protocol["source_freeze"]["source_manifest"]) == 106)
check("protocol_output_manifest_count", protocol["expected_archive_only_outputs"]["count"] == len(protocol["expected_archive_only_outputs"]["manifest"]) == 106)

probe = load("PROBE_RECEIPT_V12.json")
check("probe_protocol_hash", probe["protocol_sha256"] == PROTOCOL_SHA256)
freeze_time = dt.datetime.fromisoformat(freeze["frozen_at"].replace("Z", "+00:00"))
request_times = [dt.datetime.fromisoformat(item["started_at"]) for item in probe["requests"]]
check("protocol_frozen_before_all_requests", len(request_times) == probe["network_request_count"] == 10 and all(freeze_time <= value for value in request_times))
for item in probe["requests"]:
    body_path = ROOT / item["body_path"]
    receipt_path = ROOT / "evidence" / f"{item['name']}.receipt.json"
    check(f"body_exists_{item['name']}", body_path.is_file())
    check(f"body_hash_{item['name']}", body_path.stat().st_size == item["body_bytes"] and sha(body_path) == item["body_sha256"])
    check(f"receipt_exists_{item['name']}", receipt_path.is_file())

projection = load("JAR_PROJECTION_V12.json")
check("projection_protocol_hash", projection["protocol_sha256"] == PROTOCOL_SHA256)
check("tracked_jar_identity", projection["tracked_jar"] == {"bytes": 164121, "git_blob": "3cfbeb5d147a3c37ab0f4e5b4a4caa8c0c09b882", "path": "java/jPAI.jar", "sha256": "ff49482838e3a761913df327a48e819d4f9e552bfeab29655a82675c60c47162"})
check("projection_exact_counts", projection["expected_count"] == projection["observed_class_member_count"] == 106 and projection["missing_count"] == projection["extra_count"] == projection["different_byte_count"] == 0)
check("projection_no_duplicate_members", projection["duplicate_member_names"] == [])
check("projection_full_manifest_exact", projection["observed_manifest"] == protocol["expected_archive_only_outputs"]["manifest"])
check("projection_java17_major", projection["class_major_version_counts"] == {"61": 106} and len(projection["zip_member_metadata"]) == 106 and all(row["class_major_version"] == 61 for row in projection["zip_member_metadata"]))
check("projection_boundary_preserved", "not source compilation" in projection["boundary"] and "signed attestation" in projection["boundary"])

mode = load("MODE_AUTHORITY_V12.json")
check("mode_protocol_hash", mode["protocol_sha256"] == PROTOCOL_SHA256)
check("provider_release_observed", mode["github_releases_status"] == 200 and mode["github_release_count"] == 1)
release_body = json.loads((ROOT / "evidence/github_releases.body").read_text())
check("release_has_no_assets_or_predicate", len(release_body) == 1 and release_body[0]["tag_name"] == "v1.0.0" and release_body[0]["assets"] == [])
check("archive_attestation_404", mode["archive_attestation_status"] == 404)
for path, expected_blob in {
    "cpp/PAIpp.exe": "2488a6769086da39198b471d1e58110b5ad6cbd6",
    "run.sh": "11aa0299f89abd31a430dcc41a33df903ab018bf",
}.items():
    row = mode["paths"][path]
    check(f"history_one_introducer_{path}", row["github_history_status"] == 200 and row["history_commit_count"] == 1 and row["history_returned_shas"] == ["6e7f7b5c8e4502cb3e6f6ee20d30b72ebbe697f5"])
    revisions = {item["commit_sha"]: item for item in row["inspected_revisions"]}
    check(f"history_expected_revisions_{path}", sorted(revisions) == ["6e7f7b5c8e4502cb3e6f6ee20d30b72ebbe697f5", "aa021231cdafb6d74ce9ab5f55f824a3032058a4"])
    check(f"introducer_unsigned_{path}", revisions["6e7f7b5c8e4502cb3e6f6ee20d30b72ebbe697f5"]["commit_verification"]["verified"] is False and revisions["6e7f7b5c8e4502cb3e6f6ee20d30b72ebbe697f5"]["commit_verification"]["reason"] == "unsigned")
    check(f"current_revision_signed_{path}", revisions["aa021231cdafb6d74ce9ab5f55f824a3032058a4"]["commit_verification"]["verified"] is True and revisions["aa021231cdafb6d74ce9ab5f55f824a3032058a4"]["commit_verification"]["reason"] == "valid")
    check(f"all_provider_modes_100644_{path}", all(item["path_entries"] == [{"mode": "100644", "path": path, "sha": expected_blob, "size": 409071 if path == "cpp/PAIpp.exe" else 352, "type": "blob", "url": item["path_entries"][0]["url"]}] for item in revisions.values()))
    check(f"file_attestation_404_{path}", row["exact_file_attestation_status"] == 404)
    check(f"mode_authority_fails_{path}", row["provider_native_signed_mode_authority"] is False)
check("both_modes_fail_authority", mode["both_paths_authoritative"] is False and mode["matching_bytes_do_not_establish_authority"] is True)

compiler = load("COMPILER_PROBE_V12.json")
check("compiler_protocol_hash", compiler["protocol_sha256"] == PROTOCOL_SHA256)
check("compiler_exact_blocker", compiler["compiler_executed"] is False and compiler["fresh_class_outputs_observed"] is False and compiler["source_compilation_exact"] is None and compiler["verdict"] == "CANNOT_CHECK" and compiler["exact_terminal"] == "PINNED_COMPILER_RUNTIME_UNAVAILABLE_NO_BUILD_EXECUTED")
check("no_substitute_compiler", compiler["substitute_compiler_used"] is False)
check("runtime_blocker_preserved", len(compiler["attempts"]) == 5 and compiler["attempts"][-1]["exact_terminal"].endswith("no space left on device"))

sbom = load("SBOM_V12.json")
tool = load("TOOL_PROVENANCE_V12.json")
check("sbom_complete_counts", len(sbom["source_files"]) == len(sbom["expected_archive_only_outputs"]) == len(sbom["observed_jar_projection_outputs"]) == 106)
check("sbom_boundary", "not provider-native signed" in sbom["boundary"])
check("tool_provenance_pinned", tool["compiler_image"]["manifest_digest"] == protocol["pinned_lawful_tooling"]["compiler_container"]["manifest_digest"] and tool["compiler_probe"]["exact_terminal"] == compiler["exact_terminal"])

contract = load("AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json")
check("signing_contract_complete_classes", contract["required_subjects"]["archive_only_class_count"] == 106 and contract["required_subjects"]["archive_only_class_manifest_sha256"] == protocol["expected_archive_only_outputs"]["manifest_sha256"])
check("signing_contract_both_modes", contract["required_subjects"]["cpp_PAIpp_exe"]["required_archive_mode"] == contract["required_subjects"]["run_sh"]["required_archive_mode"] == "0755" and contract["required_subjects"]["cpp_PAIpp_exe"]["signed_revision_mode_to_explain"] == contract["required_subjects"]["run_sh"]["signed_revision_mode_to_explain"] == "100644")

negative = load("NEGATIVE_RESULT_LEDGER_V12.json")
check("three_causal_residuals", len(negative["rows"]) == 3 and all("next_discriminator" in row for row in negative["rows"]))
result = load("RESULT_V12.json")
check("zero_closures", result["v12_closed_count"] == 0 and result["v12_closed_indices"] == [] and result["v12_remaining_indices"] == [91])
check("cumulative_stays_76", result["cumulative_exact_bridge"] == "76/80" and sum(result["cumulative_exact_by_domain"].values()) == 76)
check("result_class_boundary", result["class_findings"]["tracked_jar_projection_exact"] is True and result["class_findings"]["fresh_source_compilation_exact"] is None and result["class_findings"]["provider_native_signed_build_provenance"] is False)
check("result_mode_contradiction", result["mode_findings"]["archive_modes"] == {"cpp/PAIpp.exe": "0755", "run.sh": "0755"} and result["mode_findings"]["signed_current_revision_modes"] == {"cpp/PAIpp.exe": "100644", "run.sh": "100644"} and result["mode_findings"]["current_revision_signature_valid"] is True)
check("result_gates_fail_closed", result["gates"]["complete_tracked_jar_projection_exact"] is True and result["gates"]["all_index_91_closure_gates"] is False and result["verdict"] == "REMAINS_CANNOT_CHECK")
check("result_scientific_boundary", result["natural_pair_and_scientific_boundary"] == {"author_lineage_adjudications_added": 0, "comparator_outcomes_accessed": False, "eligible_natural_pairs_added": 0, "external_custody_added": False, "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK", "scientific_authority_granted": False})
check("no_tests_or_manuscript_edits", result["pytest_run"] is False and result["repository_ci_run"] is False and result["manuscript_or_claim_ledger_modified"] is False)
for name, metadata in result["evidence"].items():
    path = ROOT / name if not name.startswith("development/") else ROOT.parent.parent / name
    check(f"result_evidence_exists_{path.name}", path.is_file())
    check(f"result_evidence_hash_{path.name}", path.stat().st_size == metadata["bytes"] and sha(path) == metadata["sha256"])

check("transient_payloads_removed", not (ROOT / "transient").exists())

sums_path = ROOT / "SHA256SUMS"
if sums_path.exists():
    rows = []
    for line in sums_path.read_text().splitlines():
        digest, rel = line.split("  ", 1)
        rows.append((digest, rel))
    actual_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    )
    check("sha256sums_complete_file_set", [rel for _, rel in rows] == actual_files)
    check("sha256sums_all_match", all(sha(ROOT / rel) == digest for digest, rel in rows))

receipt = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.validation",
    "validation_basis": "read-only deterministic packet-local structural, hash, exact-multiset, provider-mode, blocker, provenance and scientific-boundary checks",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "json_file_count_excluding_receipt": len(json_files),
    "check_count": len(checks),
    "passed": sum(item["pass"] for item in checks),
    "failed": sum(not item["pass"] for item in checks),
    "checks": checks,
    "validator_read_only": True,
    "pytest_run": False,
    "repository_ci_run": False,
    "git_operation_run": False,
}
print(json.dumps(receipt, indent=2, sort_keys=True))
