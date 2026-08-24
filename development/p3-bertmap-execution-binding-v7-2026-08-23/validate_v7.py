#!/usr/bin/env python3
"""Independent stdlib validator for the P3 BERTMap V7 packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V6 = REPO / "development/p3-comparator-native-preflight-v6-2026-08-23"
TERMINAL = (
    "P3_V7_BERTMAP_PAPER_SOURCE_AND_DEPENDENCY_CONSTRUCTOR_COMPATIBILITY_BOUND__"
    "CLOSED_FIVE_ARTIFACT_PARSER_BOUND__NONEMPTY_SOURCE_TABLE_READER_DEFECT_AND_"
    "FULL_NATIVE_SMOKE_CANNOT_CHECK__NATIVE_READINESS_TWO_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str):
    return json.loads((ROOT / name).read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    checks: list[dict] = []

    def check(name: str, condition: bool, evidence=None) -> None:
        checks.append({"check": name, "pass": bool(condition), "evidence": evidence})

    json_paths = sorted(p for p in ROOT.glob("*.json") if p.name != "VALIDATION_RECEIPT_V7.json")
    for path in json_paths:
        try:
            json.loads(path.read_text())
            check(f"json_parse:{path.name}", True)
        except Exception as exc:
            check(f"json_parse:{path.name}", False, f"{type(exc).__name__}: {exc}")

    protocol = load("PROTOCOL_V7.json")
    freeze = load("PROTOCOL_FREEZE_RECEIPT_V7.json")
    check("protocol_freeze_hash", freeze["protocol_sha256"] == sha(ROOT / "PROTOCOL_V7.json"), freeze["protocol_sha256"])
    check("protocol_parser_hash", protocol["parser_binding"]["parser_sha256"] == sha(ROOT / "bertmap_native_parser_v7.py"))
    for name, binding in protocol["predecessor"].items():
        if isinstance(binding, dict) and "path" in binding:
            path = Path(binding["path"])
            check(f"predecessor_exists:{name}", path.is_file(), str(path))
            check(f"predecessor_hash:{name}", path.is_file() and sha(path) == binding["sha256"], binding["sha256"])
    check("protocol_forbidden_operations_false", all(value is False for key, value in protocol["preserved_invariants"].items() if isinstance(value, bool)))

    runtime = load("RUNTIME_COMPATIBILITY_RECEIPT_V7.json")
    expected_versions = {"accelerate": "1.0.1", "tokenizers": "0.20.3", "torch": "2.5.1", "transformers": "4.46.3"}
    check("runtime_constructor_pass", runtime["terminal"] == "DEPENDENCY_API_CONSTRUCTOR_PASS")
    check("runtime_exact_versions", runtime["compatibility"]["observed_versions"] == expected_versions and runtime["compatibility"]["exact_versions_match"])
    check("runtime_keyword_and_constructor", runtime["compatibility"]["training_arguments_signature_has_evaluation_strategy"] and runtime["compatibility"]["training_arguments_constructor_pass"])
    check("runtime_keyword_deprecated_retained", runtime["compatibility"]["training_arguments_source_marks_evaluation_strategy_deprecated"])
    check("runtime_training_args_source_hash", runtime["compatibility"]["training_arguments_source_sha256"] == "6c594e97c4dd930612ccba8fe763650ef91ae9d7e20b20d326017bf7cd06f237")
    check("runtime_26_distributions", runtime["distribution_count"] == len(runtime["distributions"]) == 26)
    check("runtime_license_metadata_present", all(x["license"] or x["license_expression"] or x["license_classifiers"] for x in runtime["distributions"]))
    check("runtime_no_forbidden_operations", all(value is False for value in runtime["forbidden_operations"].values()))
    reader = runtime["source_native_reader_audit"]
    check("source_reader_defect_ast", reader["dp_string_subscript_found"] and reader["function_line_span"] == [119, 151])
    check("source_reader_defect_reproduced", reader["synthetic_nonempty_row_error"] == "TypeError: tuple indices must be integers or slices, not str")

    island = load("COMPATIBILITY_ISLAND_MANIFEST_V7.json")
    lock = (ROOT / "V7_COMPATIBILITY_REQUIREMENTS.txt").read_text()
    check("island_lock_hash", island["requirements_lock_sha256"] == sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.txt"))
    check("island_input_hash", island["requirements_input_sha256"] == sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.in"))
    check("island_all_primary_hashes", all(island["primary_expected_wheel_hashes_present_in_lock"].values()))
    check("island_hash_mode", island["hashes_required_at_install"] and "--hash=sha256:" in lock)
    check("island_constructor_only_boundary", "complete BERTMap lock" in island["boundary"] and "constructor_only" in island["authority"].lower())

    parser_receipt = load("PARSER_SELF_TEST_RECEIPT_V7.json")
    check("parser_self_test", parser_receipt["terminal"] == "PASS" and parser_receipt["passed"] == parser_receipt["check_count"] == 7 and parser_receipt["failed"] == 0)
    check("parser_empty_absence_pass", next(x for x in parser_receipt["checks"] if x["check"] == "complete_empty_fixture_absence_not_obstruction")["observed_pass"])
    check("parser_partial_refusal", not next(x for x in parser_receipt["checks"] if x["check"] == "partial_raw_json_refused")["observed_pass"])
    contract = load("NATIVE_ARTIFACT_CONTRACT_V7.json")
    check("contract_five_artifacts", len(contract["required_artifacts"]) == 5)
    check("contract_parser_hash", contract["parser"]["sha256"] == sha(ROOT / "bertmap_native_parser_v7.py"))
    check("contract_reader_defect_bound", contract["source_anchors"]["nonempty_table_reader_defect"]["dp_string_subscript_found"])

    rights = load("SOURCE_RIGHTS_MANIFEST_V7.json")
    check("rights_exact_source_commits", rights["canonical_original"]["commit"] == "ce848402b40e2f9513bf2d004894d3f82635022c" and rights["maintained_implementation"]["commit"] == "74ca8d47f01bad0b8739f19ee2c392bdf6d9c090")
    check("rights_exact_source_trees", rights["canonical_original"]["tree"] == "6659aca8db43a74921ff5f5176b0dd9a80eb8554" and rights["maintained_implementation"]["tree"] == "b499cb5780bbe749f7db44d0bc872d275a2737ea")
    check("rights_root_licenses", rights["canonical_original"]["root_license"]["spdx"] == rights["maintained_implementation"]["root_license"]["spdx"] == "Apache-2.0")
    check("rights_paper_identity", rights["paper"]["doi"] == "10.1609/aaai.v36i5.20510" and rights["paper"]["title"] == "BERTMap: A BERT-Based Ontology Alignment System")
    check("rights_data_payload_unopened", not rights["canonical_original"]["paper_data_payload"]["content_opened"] and rights["canonical_original"]["paper_data_payload"]["bytes"] == 2017453)
    check("rights_submodule_unopened", not rights["maintained_implementation"]["unopened_submodule"]["content_opened"])
    check("rights_jar_census", rights["maintained_implementation"]["metadata_census"]["jar_files"] == 208 and rights["canonical_original"]["metadata_census"]["jar_files"] == 106)
    check("rights_full_runtime_not_closed", len(rights["rights_not_closed"]) >= 6)

    result = load("RESULT_V7.json")
    check("result_terminal", result["terminal"] == TERMINAL)
    check("result_zero_native_artifacts", result["required_native_artifacts"] == {"present": 0, "required": 5})
    check("result_readiness_unchanged", result["readiness_delta"]["native_smoke_ready_before"] == result["readiness_delta"]["native_smoke_ready_after"] == "2/3" and result["readiness_delta"]["scientific_comparator_ready_before"] == result["readiness_delta"]["scientific_comparator_ready_after"] == "0/3" and result["readiness_delta"]["net_comparator_readiness_change"] == 0)
    check("result_no_forbidden_outcomes", all(value is False for value in result["outcome_boundary"].values()))
    check("result_evidence_hashes", result["evidence"]["runtime_receipt_sha256"] == sha(ROOT / "RUNTIME_COMPATIBILITY_RECEIPT_V7.json") and result["evidence"]["source_rights_manifest_sha256"] == sha(ROOT / "SOURCE_RIGHTS_MANIFEST_V7.json") and result["evidence"]["native_artifact_contract_sha256"] == sha(ROOT / "NATIVE_ARTIFACT_CONTRACT_V7.json") and result["evidence"]["compatibility_island_manifest_sha256"] == sha(ROOT / "COMPATIBILITY_ISLAND_MANIFEST_V7.json"))

    ledger = load("NEGATIVE_RESULT_LEDGER_V7.json")
    check("negative_ledger_count", len(ledger["entries"]) == 10)
    check("negative_ledger_complete", all(all(item.get(key) for key in ["id", "negative_result", "cause", "positive_progress", "residual", "next_discriminator"]) for item in ledger["entries"]))
    check("probe_amendment_retained", load("PROBE_ASSERTION_AMENDMENT_V7.json")["observed"]["training_arguments_constructor_returned"])
    check("audit_boundary", load("AUDIT_RECEIPT_V7.json")["terminal"] == "PASS_OUTCOME_BLIND_BINDING__FULL_NATIVE_AND_SCIENTIFIC_CANNOT_CHECK")
    cleanup_path = ROOT / "CLEANUP_AUDIT_V7.json"
    if cleanup_path.exists():
        cleanup = load("CLEANUP_AUDIT_V7.json")
        check("cleanup_runtime_removed", cleanup["post_cleanup"]["temporary_runtime_exists"] is False and not (ROOT / "_runtime").exists())
        check("cleanup_no_model_ontology_payload_opened", cleanup["pre_cleanup"]["model_payloads_opened_or_run"] is False and cleanup["pre_cleanup"]["ontology_benchmark_or_reference_payloads_opened_or_run"] is False)

    sums_path = ROOT / "SHA256SUMS"
    if sums_path.exists():
        entries = []
        for line in sums_path.read_text().splitlines():
            expected, name = line.split("  ", 1)
            path = ROOT / name
            entries.append((expected, path))
        check("sha256_manifest_all_exist", all(path.is_file() for _, path in entries), len(entries))
        check("sha256_manifest_all_match", all(sha(path) == expected for expected, path in entries), len(entries))

    failed = [item for item in checks if not item["pass"]]
    receipt = {
        "schema_version": "orion.p3.bertmap-execution-binding.validation-receipt.v7",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "validator": "validate_v7.py stdlib assertions; no pytest or repository CI",
        "json_file_count_excluding_receipt": len(json_paths),
        "check_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "checks": checks,
        "terminal": "PASS" if not failed else "FAIL",
    }
    if args.write:
        (ROOT / "VALIDATION_RECEIPT_V7.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: receipt[key] for key in ["check_count", "passed", "failed", "terminal"]}, sort_keys=True))
    for item in failed:
        print(json.dumps(item, sort_keys=True))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
