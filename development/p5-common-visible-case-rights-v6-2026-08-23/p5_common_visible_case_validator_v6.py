#!/usr/bin/env python3
"""Narrow, outcome-blind validator for the P5 V6 shared case/rights packet."""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = "396afc3e4693cfee182efe582455f2d97058c068"
FIX_COMMIT = "d1a45e9738de5b3e299bb51e987565dcce55fee6"
FIX_PATCH_SHA = "2bacab48cc56c962cc906a3e95878735cacb2f231d4a64717a8798f1eb41090f"
TERMINAL = (
    "P5_V6_SUBSTANTIVE_PUBLIC_LANG1_CASE_AND_RIGHTS_CORE_BOUND__"
    "TWELVE_SHARED_INPUT_AND_CONTENT_RIGHTS_FIELDS_CLOSED__"
    "SIX_NATIVE_TASK_ENVIRONMENTS_BLOCKING__"
    "FIFTY_FOUR_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__"
    "SEVENTY_TWO_BLOCKING__ZERO_OF_SIX_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load(name: str) -> dict[str, Any]:
    return json.loads((HERE / name).read_text())


def keys(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.append(str(key))
            found.extend(keys(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(keys(child))
    return found


def main() -> int:
    checks = 0
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(label)

    case = load("candidate_visible/CASE_BODY_V6.json")
    tree = load("P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json")
    provenance = load("P5_PUBLIC_CASE_PROVENANCE_V6.json")
    rights = load("P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json")
    index = load("P5_SHARED_CASE_CORE_INDEX_V6.json")
    acceptance = load("P5_SIX_ARM_SHARED_CORE_ACCEPTANCE_V6.json")
    protocol = load("P5_COMMON_VISIBLE_CASE_RIGHTS_PROTOCOL_V6.json")
    result = load("P5_COMMON_VISIBLE_CASE_RIGHTS_RESULT_V6.json")
    negative = load("P5_COMMON_VISIBLE_CASE_RIGHTS_NEGATIVE_LEDGER_V6.json")

    check(case["case_id"] == "P5-PUBLIC-LANG1-COMMON-001", "case:id")
    check(case["campaign_role"] == "PUBLIC_DEVELOPMENT_ONLY", "case:public_development_only")
    check(case["source"]["commit"] == BASE_COMMIT, "case:base_commit")
    check(case["source"]["tree"] == "34e33cca607f33ffcf8661e3a6c4b7fc5aca9701", "case:base_tree")
    check(case["candidate_interface"]["arm_neutral"] is True, "case:arm_neutral")
    check(case["selection"]["copied_issue_prose_or_attachments"] is False, "case:no_copied_issue_payload")

    forbidden_exact = {
        "FAIL_TO_PASS",
        "PASS_TO_PASS",
        "accuracy_score",
        "archive_admitted",
        "benchmark_outcome",
        "gold_patch",
        "patch",
        "protected_outcome",
        "protected_score",
        "resolved",
        "reward",
        "score",
        "scorer_response",
        "test_output",
        "test_patch",
    }
    forbidden_prefixes = ("gold_", "heldout_", "protected_", "scorer_")
    case_keys = keys(case)
    check(not sorted(set(case_keys) & forbidden_exact), "case:no_forbidden_exact_keys")
    check(not [key for key in case_keys if key.startswith(forbidden_prefixes)], "case:no_forbidden_prefix_keys")

    expected_visible = {
        "candidate_visible/APACHE-2.0-LICENSE.txt",
        "candidate_visible/APACHE-NOTICE.txt",
        "candidate_visible/CASE_BODY_V6.json",
        "candidate_visible/PACKET-CONTENT-CC0-1.0.txt",
        "candidate_visible/TASK_SPECIFICATION_V6.md",
        f"candidate_visible/source/commons-lang-{BASE_COMMIT}.tar.gz",
    }
    actual_visible = {
        path.relative_to(HERE).as_posix()
        for path in (HERE / "candidate_visible").rglob("*")
        if path.is_file()
    }
    check(actual_visible == expected_visible, "core:exact_visible_file_set")
    for path in actual_visible:
        raw = (HERE / path).read_bytes()
        check(FIX_COMMIT.encode() not in raw, f"core:{path}:fixed_commit_absent")
        check(FIX_PATCH_SHA.encode() not in raw, f"core:{path}:fix_patch_digest_absent")

    archive = HERE / tree["source_archive_path"]
    check(archive.is_file(), "source:archive_present")
    check(sha256(archive) == "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08", "source:archive_hash")
    check(sha256(archive) == tree["source_archive_sha256"], "source:manifest_archive_hash")
    root_prefix = f"commons-lang-{BASE_COMMIT}/"
    rows: list[dict[str, Any]] = []
    source_by_path: dict[str, bytes] = {}
    link_count = 0
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf.getmembers():
            if member.name == root_prefix.rstrip("/") or member.isdir():
                continue
            check(member.name.startswith(root_prefix), f"source:member_root:{member.name}")
            if member.issym() or member.islnk():
                link_count += 1
                continue
            check(member.isfile(), f"source:regular_member:{member.name}")
            stream = tf.extractfile(member)
            data = b"" if stream is None else stream.read()
            subpath = member.name[len(root_prefix) :]
            source_by_path[subpath] = data
            rows.append({"path": subpath, "mode": oct(member.mode), "size_bytes": len(data), "sha256": sha256_bytes(data)})
    rows.sort(key=lambda row: row["path"])
    canonical = b"".join(
        row["path"].encode()
        + b"\0"
        + row["mode"].encode()
        + b"\0"
        + str(row["size_bytes"]).encode()
        + b"\0"
        + row["sha256"].encode()
        + b"\n"
        for row in rows
    )
    check(link_count == 0 == tree["link_member_count"], "source:no_links")
    check(len(rows) == 302 == tree["regular_file_count"], "source:302_files")
    check(sum(row["size_bytes"] for row in rows) == tree["regular_file_bytes"], "source:byte_count")
    check(rows == tree["members"], "source:exact_member_manifest")
    check(sha256_bytes(canonical) == tree["canonical_member_manifest_sha256"], "source:canonical_tree_digest")
    check(sha256_bytes(source_by_path["LICENSE.txt"]) == sha256(HERE / "candidate_visible/APACHE-2.0-LICENSE.txt"), "source:license_bytes_retained")
    check(sha256_bytes(source_by_path["NOTICE.txt"]) == sha256(HERE / "candidate_visible/APACHE-NOTICE.txt"), "source:notice_bytes_retained")
    number_utils = source_by_path["src/main/java/org/apache/commons/lang3/math/NumberUtils.java"]
    number_utils_test = source_by_path["src/test/java/org/apache/commons/lang3/math/NumberUtilsTest.java"]
    check(b"firstSigDigit" not in number_utils, "source:known_fix_implementation_absent")
    check(b"TestLang747" not in number_utils_test, "source:known_fix_test_absent")

    expected_component_paths = sorted(expected_visible)
    actual_component_paths = sorted(row["path"] for row in index["components"])
    check(index["candidate_visible_component_count"] == 6, "index:6_components")
    check(actual_component_paths == expected_component_paths, "index:all_visible_components")
    check(sum(row["size_bytes"] for row in index["components"]) == index["candidate_visible_bytes"], "index:byte_sum")
    for row in index["components"]:
        path = HERE / row["path"]
        check(path.stat().st_size == row["size_bytes"], f"index:{row['path']}:size")
        check(sha256(path) == row["sha256"], f"index:{row['path']}:hash")
    component_canonical = b"".join(
        row["path"].encode() + b"\0" + row["sha256"].encode() + b"\0" + str(row["size_bytes"]).encode() + b"\n"
        for row in sorted(index["components"], key=lambda item: item["path"])
    )
    check(sha256_bytes(component_canonical) == index["candidate_visible_core_sha256"], "index:core_digest")
    check(index["source_tree_content_manifest"]["sha256"] == sha256(HERE / "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json"), "index:tree_manifest_hash")
    check(index["rights_manifest"]["sha256"] == sha256(HERE / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"), "index:rights_manifest_hash")

    check(rights["rights_status"] == "BOUND_FOR_LISTED_SHARED_CASE_COMPONENTS", "rights:bound_listed_components")
    ids = {row["component_id"] for row in rights["components"]}
    check(ids == {"APACHE_COMMONS_LANG_BUGGY_SOURCE_ARCHIVE", "DEFECTS4J_LANG1_SOURCE_IDENTITY_MAPPING", "V6_AUTHORED_CASE_BODY_AND_TASK_SPECIFICATION"}, "rights:component_ids")
    by_id = {row["component_id"]: row for row in rights["components"]}
    apache = by_id["APACHE_COMMONS_LANG_BUGGY_SOURCE_ARCHIVE"]
    check(apache["license_spdx_id"] == "Apache-2.0", "rights:apache_id")
    check(sha256(HERE / apache["license_path"]) == apache["license_sha256"], "rights:apache_license_hash")
    check(sha256(HERE / apache["notice_path"]) == apache["notice_sha256"], "rights:apache_notice_hash")
    mapping = by_id["DEFECTS4J_LANG1_SOURCE_IDENTITY_MAPPING"]
    check(mapping["license_spdx_id"] == "MIT", "rights:mapping_mit")
    check(sha256(HERE / mapping["path"]) == mapping["sha256"], "rights:mapping_hash")
    check(sha256(HERE / mapping["license_path"]) == mapping["license_sha256"], "rights:mapping_license_hash")
    authored = by_id["V6_AUTHORED_CASE_BODY_AND_TASK_SPECIFICATION"]
    check(authored["license_spdx_id"] == "CC0-1.0", "rights:authored_cc0")
    check(sha256(HERE / authored["license_path"]) == authored["license_sha256"], "rights:cc0_hash")
    check(authored["authorship_assertion_is_local_not_independent"] is True, "rights:authorship_boundary")

    mapping_row = (HERE / mapping["path"]).read_text().splitlines()
    check(len(mapping_row) == 2, "provenance:mapping_one_row")
    check(mapping_row[1].split(",")[:3] == ["1", BASE_COMMIT, FIX_COMMIT], "provenance:mapping_exact_identity")
    check(provenance["source_identity"]["known_public_fix_bytes_in_candidate_core"] is False, "provenance:fix_excluded")
    check(provenance["predecessor_public_development_evidence"]["selection_is_post_outcome"] is True, "provenance:post_outcome_retained")
    for row in provenance["predecessor_public_development_evidence"].values():
        if isinstance(row, dict) and "path" in row and "sha256" in row:
            check(sha256(ROOT / row["path"]) == row["sha256"], f"provenance:{row['path']}:hash")

    receipts = acceptance["receipts"]
    check(len(receipts) == 6, "acceptance:6_receipts")
    check(sorted(row["arm_code"] for row in receipts) == ["C1", "C2", "C3", "C4", "C5", "C6"], "acceptance:C1_C6")
    check(acceptance["same_core_for_all_six"] is True, "acceptance:same_core")
    check(acceptance["shared_field_instances_closed"] == 12, "acceptance:12_shared_closed")
    check(acceptance["native_task_environment_instances_closed"] == 0, "acceptance:0_environment_closed")
    for row in receipts:
        fields = row["field_bindings"]
        check(fields["inputs.candidate_visible_case_bytes"]["status"] == "BOUND", f"{row['arm_code']}:case_bound")
        check(fields["rights.task_and_benchmark_content"]["status"] == "BOUND", f"{row['arm_code']}:rights_bound")
        check(fields["runtime.task_environment"]["status"] == "BLOCKING", f"{row['arm_code']}:environment_blocking")
        check(row["same_candidate_visible_core_sha256"] == index["candidate_visible_core_sha256"], f"{row['arm_code']}:same_core")
        check(row["core_index_sha256"] == sha256(HERE / "P5_SHARED_CASE_CORE_INDEX_V6.json"), f"{row['arm_code']}:index_hash")
        check(row["after_shared_core_only"]["bound"] == row["before"]["bound"] + 2, f"{row['arm_code']}:bound_delta")
        check(row["after_shared_core_only"]["blocking"] == row["before"]["blocking"] - 2, f"{row['arm_code']}:blocking_delta")
        check(row["arm_or_model_executed"] is False, f"{row['arm_code']}:no_execution")

    delta = result["field_delta"]
    check(delta == {
        "before_bound": 42,
        "before_blocking": 84,
        "new_bindings": 12,
        "after_bound": 54,
        "after_blocking": 72,
        "per_arm": {row["arm_code"]: row["after_shared_core_only"] for row in receipts},
        "ready_arms": 0,
    }, "result:exact_field_delta")
    check(result["root_r2"]["after_blocking_instances"] == 6, "result:R2_6_residual")
    check(all(value == 0 for value in result["executions"].values()), "result:no_executions_or_outcomes")
    check(result["preserved_claims"]["performance"] == "CANNOT_CHECK", "result:performance_boundary")
    check(result["preserved_claims"]["superiority"] == "CANNOT_CHECK", "result:superiority_boundary")
    check(result["terminal"] == TERMINAL == negative["terminal"], "result:terminal")
    check((HERE / "TERMINAL_V6.txt").read_text().strip() == TERMINAL, "terminal:file")

    v5 = protocol["predecessor_v5_registry"]
    check(sha256(ROOT / v5["path"]) == v5["sha256"], "protocol:v5_registry_hash")
    check(protocol["target"]["targeted_field_instances"] == 12, "protocol:12_targeted")
    check(all(value == 0 for value in protocol["execution_prohibitions"].values()), "protocol:no_execution")
    check(len(negative["records"]) == 5, "negative:5_records")

    manifest_path = HERE / "SHA256SUMS"
    check(manifest_path.is_file(), "manifest:present")
    if manifest_path.is_file():
        entries = []
        for line in manifest_path.read_text().splitlines():
            digest, name = line.split("  ", 1)
            entries.append((digest, name))
        actual_files = sorted(path.relative_to(HERE).as_posix() for path in HERE.rglob("*") if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts)
        check(sorted(name for _, name in entries) == actual_files, "manifest:exact_file_set")
        check(all((HERE / name).is_file() and sha256(HERE / name) == digest for digest, name in entries), "manifest:all_hashes")

    if failures:
        print(json.dumps({"checks": checks, "failures": failures, "status": "FAIL"}, indent=2))
        return 1
    print(json.dumps({"checks": checks, "failures": 0, "status": "PASS", "terminal": TERMINAL}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
