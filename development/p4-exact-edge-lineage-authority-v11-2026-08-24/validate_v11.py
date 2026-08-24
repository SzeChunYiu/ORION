#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V10 = ROOT.parent / "p4-exact-edge-lineage-authority-v10-2026-08-24"
checks: list[dict] = []


def check(name: str, condition: bool) -> None:
    checks.append({"check": name, "pass": bool(condition)})
    if not condition:
        raise AssertionError(name)


def load(path: Path | str) -> dict:
    if isinstance(path, str):
        path = ROOT / path
    return json.loads(path.read_text())


def sha(path: Path | str) -> str:
    if isinstance(path, str):
        path = ROOT / path
    return hashlib.sha256(path.read_bytes()).hexdigest()


json_files = sorted(path for path in ROOT.rglob("*.json") if path.name != "VALIDATION_RECEIPT_V11.json")
for path in json_files:
    json.loads(path.read_text())
check("all_json_machine_readable", len(json_files) >= 18)
check("v10_result_immutable", sha(V10 / "RESULT_V10.json") == "9cd19c2f2d3129f4789e5976395ce02f6cb08a29287614900c2b3bddbbaa20d1")
check("v10_sha256sums_immutable", sha(V10 / "SHA256SUMS") == "b643beb8a740cc618bacc742f617e87f3eed3e1288afe1af87f6b49aff5d0449")

freeze = load("PROTOCOL_FREEZE_RECEIPT_V11.json")
check("v11_protocol_hash", sha("PROTOCOL_V11.json") == freeze["protocol_sha256"] == "687a29b8d5358723fc16274c11e325431a42f00216b4f400a2d2446c04d55334")
check("v11_outcome_informed", load("PROTOCOL_V11.json")["outcome_informed"] is True and freeze["outcome_informed"] is True)
probe = load("PROBE_RECEIPT_V11.json")
check("probe_protocol_hash", probe["protocol_sha256"] == freeze["protocol_sha256"])
freeze_time = dt.datetime.fromisoformat(freeze["frozen_at"].replace("Z", "+00:00"))
request_times = [dt.datetime.fromisoformat(item["started_at"]) for item in probe["requests"]]
check("protocol_frozen_before_requests", all(freeze_time <= value for value in request_times))
check("ten_predeclared_requests", probe["request_count"] == len(probe["requests"]) == 10)
check("all_requests_http_200", all(item["status"] == 200 and item["error"] is None for item in probe["requests"]))
for item in probe["requests"]:
    if item["body_retained"]:
        path = ROOT / item["body_path"]
        check("retained_exists_" + path.name, path.is_file())
        check("retained_hash_" + path.name, path.stat().st_size == item["body_bytes"] and sha(path) == item["body_sha256"])
    else:
        check("omitted_has_no_path_" + item["body_sha256"][:12], item["body_path"] is None)

e36 = load("EDGE_36_PROVIDER_CORRECTION_V11.json")
check("index36_zenodo_version_null", e36["zenodo"]["version"] is None)
check("index36_datacite_versions_null", e36["datacite"]["concept_version"] is None and e36["datacite"]["child_version"] is None)
check("index36_preserved_adverse_head", e36["preserved_archive"]["embedded_head"] == "3cd108c376faf9832373adfe3ab4688295aa42fa" and e36["preserved_archive"]["embedded_head_tag"] == "0.0.12" and e36["preserved_archive"]["accepted_commit"] == "069ab4f56d100d765d46c594ac1b06add7e49f9e")
check("index36_fail_closed", e36["verdict"] == "REMAINS_CANNOT_CHECK" and not any(e36["gates"].values()))

e91 = load("EDGE_91_EMBEDDED_HEAD_CONTENT_IDENTITY_V11.json")
check("index91_archive_identity", e91["zenodo_archive"] == {"bytes": 17147954, "md5": "506a29c006cbf81161acf21bca60e021", "provider_checksum": "md5:506a29c006cbf81161acf21bca60e021", "sha256": "2a94e0ed7e61e18ea4135aa559d6a06a407adcabd84dbbc52ebface6bba5b407"})
check("index91_github_full_revision", e91["github_commit"]["sha"] == e91["embedded_git"]["head"] == "aa021231cdafb6d74ce9ab5f55f824a3032058a4")
check("index91_exact_tree_authority", e91["github_commit"]["tree_sha"] == e91["embedded_git"]["tree"] == "d5620f3acf4e5a163cfdfdefc2432ebd5709008a")
check("index91_git_fsck", e91["embedded_git"]["fsck_returncode"] == 0)
check("index91_git_index_clean_but_worktree_mode_dirty", e91["embedded_git"]["status_porcelain"] == [] and e91["embedded_git"]["diff_index_clean"] is True and e91["embedded_git"]["diff_files_clean"] is False)
comparison = e91["comparison"]
check("index91_manifest_counts", comparison["left_count"] == 444 and comparison["right_count"] == comparison["common_count"] == 338)
check("index91_106_archive_only", comparison["only_left_count"] == 106 and comparison["only_right_count"] == 0 and all(path.startswith("java/bin/") and path.endswith(".class") for path in comparison["only_left"]))
check("index91_two_mode_differences", comparison["differing_count"] == 2 and [item["normalized_path"] for item in comparison["differing"]] == ["cpp/PAIpp.exe", "run.sh"] and all(item["left"]["sha256"] == item["right"]["sha256"] and item["left"]["unix_executable_bit"] != item["right"]["unix_executable_bit"] for item in comparison["differing"]))
check("index91_exact_gate_fails", comparison["exact"] is False and e91["gates"]["exact_non_git_archive_to_codeload_manifest"] is False and e91["all_closure_gates_pass"] is False and e91["verdict"] == "REMAINS_CANNOT_CHECK")
check("index91_rights_pass_not_compensatory", e91["gates"]["archive_and_revision_mit_rights"] is True and e91["licenses"]["exact_license_byte_equal"] is True)

manifests = load("EDGE_91_NORMALIZED_MANIFESTS_V11.json")
am = manifests["archive_non_git_payload"]
gm = manifests["github_codeload"]
check("index91_manifest_artifact_counts", am["entry_count"] == 444 and gm["entry_count"] == 338)
check("index91_git_envelope_separated_exactly", am["git_envelope_separated"] is True and am["git_envelope_member_count"] == 103 and gm["git_envelope_separated"] is False)

pypi = load("PYPI_SIMPLE_PROVENANCE_V11.json")
rows = {row["frozen_index"]: row for row in pypi["rows"]}
check("pypi_exact_indices", sorted(rows) == [133, 185])
check("index133_exact_hash", rows[133]["simple_api_sha256"] == rows[133]["expected_sha256"] == "b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3")
check("index185_exact_hash", rows[185]["simple_api_sha256"] == rows[185]["expected_sha256"] == "775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19")
check("pypi_provenance_null", all(row["provenance_field_present"] is False and row["provenance_value"] is None and row["provenance_url"] is None for row in rows.values()))
check("pypi_fail_closed", all(row["verdict"] == "REMAINS_CANNOT_CHECK" and row["provider_native_signed_artifact_to_commit_binding"] is False for row in rows.values()))

negative = load("NEGATIVE_RESULT_LEDGER_V11.json")
check("four_negative_rows", negative["remaining_count"] == 4 and negative["remaining_indices"] == [36, 91, 133, 185] and all(row["verdict"] == "REMAINS_CANNOT_CHECK" for row in negative["rows"]))
result = load("RESULT_V11.json")
check("zero_closures", result["v11_closed_count"] == 0 and result["v11_closed_indices"] == [])
check("remaining_four", result["v11_remaining_count"] == 4 and result["v11_remaining_indices"] == [36, 91, 133, 185])
check("cumulative_stays_76", result["cumulative_exact_bridge"] == "76/80" and sum(result["cumulative_exact_by_domain"].values()) == 76)
check("domain_counts_unchanged", result["cumulative_exact_by_domain"] == {"EARTH_ENVIRONMENT": 5, "LIFE_BIOMEDICAL": 7, "PHYSICAL_ENGINEERING": 4, "SCIENTIFIC_SOFTWARE": 60})
check("v10_v10b_chronology_preserved", "V10 index-199 target-specific discriminator failed" in result["preserved_v10_v10b_chronology"] and "V10B" in result["preserved_v10_v10b_chronology"])
check("no_scientific_authority", result["natural_pair_and_scientific_boundary"] == {"author_lineage_adjudications_added": 0, "comparator_outcomes_accessed": False, "eligible_natural_pairs_added": 0, "external_custody_added": False, "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK", "scientific_authority_granted": False})
for name, metadata in result["evidence"].items():
    path = ROOT / name if not name.startswith("development/") else ROOT.parent.parent / name
    check("result_evidence_exists_" + path.name, path.is_file())
    check("result_evidence_hash_" + path.name, path.stat().st_size == metadata["bytes"] and sha(path) == metadata["sha256"])

check("large_bodies_not_retained", not (ROOT / "evidence/91_zenodo_archive_omitted.body").exists() and not (ROOT / "evidence/91_github_embedded_head_codeload_omitted.body").exists())

receipt = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v11.validation",
    "validation_basis": "deterministic packet-local structural, hash, exact-manifest, provider-provenance, chronology and scientific-boundary checks",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "json_file_count_excluding_receipt": len(json_files),
    "check_count": len(checks),
    "passed": sum(item["pass"] for item in checks),
    "failed": sum(not item["pass"] for item in checks),
    "checks": checks,
    "pytest_run": False,
    "repository_ci_run": False,
    "git_operation_run": False,
}
(ROOT / "VALIDATION_RECEIPT_V11.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps({"checks": len(checks), "passed": receipt["passed"], "json_files": len(json_files)}, sort_keys=True))
