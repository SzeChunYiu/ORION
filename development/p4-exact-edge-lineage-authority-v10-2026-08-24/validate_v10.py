#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V9 = ROOT.parent / "p4-exact-edge-lineage-authority-v9-2026-08-23"
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


json_files = sorted(path for path in ROOT.rglob("*.json") if path.name != "VALIDATION_RECEIPT_V10.json")
for path in json_files:
    json.loads(path.read_text())
check("all_json_machine_readable", len(json_files) >= 85)

check("immutable_v9_result_hash", sha(V9 / "RESULT_V9.json") == "b9507beca0bc653e99e6281a4f47df10d600851be6c8b1750a0beab4b8aa2111")
check("immutable_v9_sha256sums_hash", sha(V9 / "SHA256SUMS") == "caae0bb5fabd064f8c76d33270c97afe2659a45da9a050118bf68fd7bace4cb7")

freeze = load("PROTOCOL_FREEZE_RECEIPT_V10.json")
check("v10_protocol_hash", sha("PROTOCOL_V10.json") == freeze["protocol_sha256"] == "b19145f547b686943ae8c12e9cb63d22557f38f765176cfdb6ce12395df43399")
provider = load("PROVIDER_AUTHORITY_PROBE_RECEIPT_V10.json")
check("v10_provider_probe_protocol_hash", provider["protocol_sha256"] == freeze["protocol_sha256"])
check("v10_provider_probe_five_rows", [row["frozen_index"] for row in provider["rows"]] == [36, 91, 133, 185, 199])
check("v10_provider_probe_65_requests", sum(len(row["requests"]) for row in provider["rows"]) == 65)

freeze_b = load("PROTOCOL_FREEZE_RECEIPT_V10B.json")
check("v10b_protocol_hash", sha("PROTOCOL_V10B.json") == freeze_b["sha256"] == "8eda26f0fef9a9545e7393651601050e9a34e4843af7463f5e5cbd90f7d214f2")
check("v10b_explicitly_outcome_informed", load("PROTOCOL_V10B.json")["successor_status"]["outcome_informed"] is True and freeze_b["outcome_informed_successor"] is True)
probe_b = load("PROBE_RECEIPT_V10B.json")
check("v10b_probe_protocol_hash", probe_b["protocol_sha256"] == freeze_b["sha256"])
freeze_time = dt.datetime.fromisoformat(freeze_b["frozen_at"].replace("Z", "+00:00"))
request_times = [dt.datetime.fromisoformat(item["started_at"]) for item in probe_b["requests"]]
check("v10b_frozen_before_every_request", all(freeze_time <= value for value in request_times))
check("v10b_six_predeclared_requests", probe_b["request_count"] == 6 and len(probe_b["requests"]) == 6)
check("v10b_all_requests_http_200", all(item["status"] == 200 and item["error"] is None for item in probe_b["requests"]))

for item in probe_b["requests"]:
    if item["body_retained"]:
        path = ROOT / item["body_path"]
        check("retained_body_exists_" + path.name, path.is_file())
        check("retained_body_hash_" + path.name, path.stat().st_size == item["body_bytes"] and sha(path) == item["body_sha256"])
    else:
        check("omitted_body_has_no_path_" + item["body_sha256"][:12], item["body_path"] is None)

edge = load("EDGE_199_CONTENT_IDENTITY_V10B.json")
check("index_199_all_eight_gates", edge["all_closure_gates_pass"] is True and len(edge["gates"]) == 8 and all(edge["gates"].values()))
check("index_199_exact_165_paths", edge["comparison"]["exact"] is True and edge["comparison"]["left_entry_count"] == edge["comparison"]["right_entry_count"] == edge["comparison"]["common_entry_count"] == 165)
check("index_199_zero_manifest_residual", edge["comparison"]["only_left_count"] == edge["comparison"]["only_right_count"] == edge["comparison"]["differing_count"] == 0)
check("index_199_full_revision", edge["github_ref"]["resolved_object_sha"] == edge["github_commit"]["sha"] == "a85df681d29a5cf3406d529144a7c0645e543e61")
check("index_199_exact_git_tree", edge["github_commit"]["tree_sha"] == edge["software_heritage"]["revision_directory"] == "178315b57afafc1f20ab9929b4de893430524c62")
check("index_199_swh_independent_ref", edge["software_heritage"]["ref_target_type"] == "revision" and edge["software_heritage"]["ref_target"] == edge["github_commit"]["sha"])
check("index_199_zenodo_md5", edge["zenodo"]["provider_checksum"] == "md5:3409352bdc0926acfafc39bf121f4263" and edge["zenodo"]["downloaded_md5"] == "3409352bdc0926acfafc39bf121f4263")
check("index_199_zenodo_zip_identity", edge["zenodo"]["downloaded_bytes"] == 4237826 and edge["zenodo"]["downloaded_sha256"] == "5eaf4bc23f11cf14d6b1f41510a7b99cf3107cb906a7b7e9aa2945a2a64baeba")
check("index_199_codeload_zip_identity", edge["github_codeload"]["downloaded_bytes"] == 4247426 and edge["github_codeload"]["downloaded_sha256"] == "b468f53c66e751ae242a039ba94c43788ec059363f8d2a2691207b4d4015a0b7")
check("index_199_mit_rights", edge["licenses"]["zenodo_declared"] == "mit-license" and edge["licenses"]["github_raw_license_is_mit"] is True and edge["licenses"]["exact_license_byte_equal"] is True)

manifests = load("EDGE_199_NORMALIZED_MANIFESTS_V10B.json")
zm = manifests["zenodo"]
gm = manifests["github_codeload"]
check("index_199_manifest_hash_equal", zm["manifest_sha256"] == gm["manifest_sha256"] == "32decf39f38d4652e184bef077625ce8e22fa44ec37afb98746ddce178f5364e")
check("index_199_manifest_entries_exact", zm["manifest"] == gm["manifest"] and len(zm["manifest"]) == 165)
check("index_199_manifest_no_encryption", zm["encrypted_entry_count"] == gm["encrypted_entry_count"] == 0)
check("index_199_one_root_each", zm["top_level_root"] == "TARGENE-targene-pipeline-0f8b2db" and gm["top_level_root"] == "targene-pipeline-a85df681d29a5cf3406d529144a7c0645e543e61")

provider_rows = {row["frozen_index"]: row for row in provider["rows"]}


def one_request(index: int, fragment: str) -> dict:
    matches = [item for item in provider_rows[index]["requests"] if fragment in item["url"]]
    check(f"index_{index}_one_{fragment.replace('/', '_')[:30]}", len(matches) == 1)
    return matches[0]


check("index_36_current_zenodo_child_unversioned", load("evidence/36_zenodo_record.body")["doi"] == "10.5281/zenodo.21221062" and load("evidence/36_zenodo_record.body")["metadata"].get("version") is None)
v9e91 = load(V9 / "EDGE_91_EMBEDDED_GIT_AUTHORITY_V9.json")
check("index_91_adverse_embedded_git_preserved", v9e91["head"] == "aa021231cdafb6d74ce9ab5f55f824a3032058a4" and not v9e91["accepted_commit_object_present"])
for index in (133, 185):
    check(f"index_{index}_pypi_integrity_absent", one_request(index, "/integrity/")["status"] == 404)
    check(f"index_{index}_github_attestation_absent", one_request(index, "/attestations/")["status"] == 404)

negative = load("NEGATIVE_RESULT_LEDGER_V10.json")
check("four_preserved_negative_rows", negative["remaining_count"] == 4 and negative["remaining_indices"] == [36, 91, 133, 185])
check("no_negative_relabel", all(row["verdict"] == "REMAINS_CANNOT_CHECK" and row["residual"] for row in negative["rows"]))

result = load("RESULT_V10.json")
check("closed_one_index_199", result["v10_closed_count"] == 1 and result["v10_closed_indices"] == [199])
check("remaining_four", result["v10_remaining_count"] == 4 and result["v10_remaining_indices"] == [36, 91, 133, 185])
check("cumulative_76_of_80", result["predecessor_exact_bridge"] == "75/80" and result["cumulative_exact_bridge"] == "76/80" and sum(result["cumulative_exact_by_domain"].values()) == 76)
check("life_only_domain_increment", result["cumulative_exact_by_domain"] == {"EARTH_ENVIRONMENT": 5, "LIFE_BIOMEDICAL": 7, "PHYSICAL_ENGINEERING": 4, "SCIENTIFIC_SOFTWARE": 60})
check("v10_primary_failure_preserved", result["protocol_chronology"]["v10_primary"]["index_199_target_specific_discriminator"] == "FAILED_AS_FROZEN")
check("v10b_chronology_explicit", result["protocol_chronology"]["v10b_successor"]["outcome_informed"] is True and result["protocol_chronology"]["v10b_successor"]["frozen_before_v10b_archive_download_or_comparison"] is True)
check("no_scientific_authority", result["natural_pair_and_scientific_boundary"] == {"author_lineage_adjudications_added": 0, "comparator_outcomes_accessed": False, "eligible_natural_pairs_added": 0, "external_custody_added": False, "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK", "scientific_authority_granted": False})

for name, metadata in result["evidence"].items():
    path = ROOT / name if not name.startswith("development/") else ROOT.parent.parent / name
    check("result_evidence_exists_" + path.name, path.is_file())
    check("result_evidence_hash_" + path.name, path.stat().st_size == metadata["bytes"] and sha(path) == metadata["sha256"])

check("large_zip_bodies_not_retained", not (ROOT / "evidence/199_v10b_zenodo_archive_omitted.body").exists() and not (ROOT / "evidence/199_v10b_github_codeload_omitted.body").exists())

receipt = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10.validation",
    "validation_basis": "deterministic packet-local structural, hash, exact-manifest, chronology and scientific-boundary checks",
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
(ROOT / "VALIDATION_RECEIPT_V10.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps({"checks": len(checks), "passed": receipt["passed"], "json_files": len(json_files)}, sort_keys=True))
