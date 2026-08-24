#!/usr/bin/env python3
"""Packet-native scientific validator; no pytest or repository CI."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
V7 = ROOT.parent / "p3-bertmap-execution-binding-v7-2026-08-23"
EXPECTED_TERMINAL = (
    "P3_V8_BERTMAP_TABLE_READER_MINIMAL_REPAIR_SOURCE_HASH_AND_SYNTHETIC_EMPTY_NONEMPTY_EXECUTION_BOUND__"
    "MALFORMED_STALE_AND_PROHIBITED_CASES_FAIL_CLOSED__V7_PARSER_SYNTHETIC_COMPATIBILITY_BOUND__"
    "NATIVE_SMOKE_AND_SCIENTIFIC_READINESS_UNCHANGED"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(name: str):
    return json.loads((ROOT / name).read_text())


def load_execute():
    path = ROOT / "execute_v8.py"
    spec = importlib.util.spec_from_file_location("p3_v8_execute_for_validation", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    protocol = load_json("PROTOCOL_V8.json")
    freeze = load_json("PROTOCOL_FREEZE_RECEIPT_V8.json")
    receipt = load_json("LANGUAGE_LEVEL_EXECUTION_RECEIPT_V8.json")
    result = load_json("RESULT_V8.json")
    ledger = load_json("NEGATIVE_RESULT_LEDGER_V8.json")

    check("protocol_schema", protocol["schema_version"] == "orion.p3.bertmap-table-reader-repair.protocol.v8")
    check("protocol_identity", protocol["protocol_id"] == "P3_V8_BERTMAP_PROSPECTIVE_MINIMAL_TABLE_READER_REPAIR")
    check("freeze_precedes_execution", datetime.fromisoformat(freeze["frozen_at"]) < datetime.fromisoformat(receipt["executed_at"]))
    check("freeze_flags", not any([freeze["repair_executed_before_freeze"], freeze["synthetic_cases_executed_before_freeze"], freeze["outcomes_opened_before_freeze"]]))
    check("protocol_hash", freeze["protocol_sha256"] == sha(ROOT / "PROTOCOL_V8.json"))
    check("pinned_source_hash", sha(ROOT / "PINNED_MAPPING_V7.py") == "9cf0dce1c5bd142e4175f628f8f3267f54ed6deac9f31e165a25b4a073eedff0")
    check("upstream_license_hash", sha(ROOT / "UPSTREAM_LICENSE.txt") == "340ebaff716578e1b620521eeb740febbdcb24b8bd0c1de12c37b916aadf4d36")
    check("v7_result_hash", sha(V7 / "RESULT_V7.json") == protocol["predecessor"]["v7_result_sha256"])
    check("v7_compatibility_manifest_hash", sha(V7 / "COMPATIBILITY_ISLAND_MANIFEST_V7.json") == protocol["predecessor"]["compatibility_manifest_sha256"])
    check("v7_lock_hash", sha(V7 / "V7_COMPATIBILITY_REQUIREMENTS.txt") == protocol["predecessor"]["compatibility_lock_sha256"])
    check("v7_parser_hash", sha(V7 / "bertmap_native_parser_v7.py") == protocol["parser_compatibility_gate"]["parser_sha256"])

    execute = load_execute()
    observed_patch, observed = execute.run()
    check("strict_patch_exact", observed_patch == (ROOT / "mapping_dp_score_v8.patch").read_text())
    check("patch_hash", sha(ROOT / "mapping_dp_score_v8.patch") == receipt["source_identity"]["patch_sha256"])
    check("repaired_source_hash", observed["source_identity"]["repaired_sha256"] == protocol["single_intended_change"]["expected_repaired_mapping_sha256"])
    check("single_changed_expression", observed["source_identity"]["changed_expression_count"] == 1 and observed["source_identity"]["changed_source_lines_removed"] == 1 and observed["source_identity"]["changed_source_lines_added"] == 1)
    check("ast_equivalence_boundary", observed["semantic_equivalence_boundary"]["ast_equivalent_after_normalizing_only_frozen_access"] is True)
    check("synthetic_case_count", observed["synthetic_execution"]["case_count"] == 8)
    check("synthetic_all_pass", observed["synthetic_execution"]["pass_count"] == 8 and all(row["pass"] for row in observed["synthetic_execution"]["cases"]))
    check("synthetic_case_ids", [row["id"] for row in observed["synthetic_execution"]["cases"]] == [row["id"] for row in receipt["synthetic_execution"]["cases"]])
    check("truthy_threshold_before_error", next(row for row in observed["synthetic_execution"]["cases"] if row["id"] == "SYN_NONEMPTY_THRESHOLD")["original_error"].startswith("TypeError:"))
    check("truthy_threshold_after_one_row", len(next(row for row in observed["synthetic_execution"]["cases"] if row["id"] == "SYN_NONEMPTY_THRESHOLD")["repaired"]) == 1)
    check("falsey_threshold_scope_correction", len(next(row for row in observed["synthetic_execution"]["cases"] if row["id"] == "SYN_NONEMPTY_THRESHOLD_NONE")["original"]) == 2)
    check("malformed_fail_closed", all(next(row for row in observed["synthetic_execution"]["cases"] if row["id"] == case)["pass"] for case in ["MALFORMED_MISSING_SCORE", "MALFORMED_NONNUMERIC_SCORE"]))
    check("stale_fail_closed", next(row for row in observed["synthetic_execution"]["cases"] if row["id"] == "STALE_SOURCE_HASH")["pass"])
    check("prohibited_fail_before_access", all(next(row for row in observed["synthetic_execution"]["cases"] if row["id"] == case)["table_access_delta"] == 0 for case in ["PROHIBITED_REFERENCE_MODE", "PROHIBITED_EXTERNAL_FIXTURE"]))
    check("parser_synthetic_pass", observed["parser_compatibility"]["terminal"] == "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS")
    check("parser_authority_bounded", observed["parser_compatibility"]["authority"] == "SYNTHETIC_INTERFACE_COMPATIBILITY_ONLY__NOT_NATIVE_BERTMAP_ARTIFACTS_OR_SMOKE")
    check("synthetic_parser_work_deleted", not (ROOT / "_synthetic_parser_work_v8").exists())
    required = set(protocol["parser_compatibility_gate"]["required_files"])
    final_native_named = [str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file() and path.name in required]
    check("actual_native_artifacts_absent", final_native_named == [], final_native_named)
    check("native_smoke_not_claimed", receipt["parser_compatibility"]["native_smoke_claimed"] is False and receipt["readiness_delta"]["actual_native_artifacts_present"] == 0)
    check("forbidden_operations_false", not any(receipt["forbidden_operations"].values()))
    check("receipt_terminal", receipt["terminal"] == EXPECTED_TERMINAL)
    check("result_terminal", result["terminal"] == EXPECTED_TERMINAL)
    check("ledger_terminal", ledger["terminal"] == EXPECTED_TERMINAL)
    check("readiness_native_unchanged", result["readiness_delta"]["native_smoke_ready_before"] == result["readiness_delta"]["native_smoke_ready_after"] == "2/3")
    check("readiness_scientific_unchanged", result["readiness_delta"]["scientific_comparator_ready_before"] == result["readiness_delta"]["scientific_comparator_ready_after"] == "0/3")
    check("top_tier_not_claimed", result["claim_boundary"]["top_tier_submission_ready"] is False)
    check("scientific_claims_cannot_check", all(result["claim_boundary"][key] == "CANNOT_CHECK" for key in ["correctness", "coverage", "harm", "transport", "performance", "superiority"]))
    check("negative_ledger_ids", [row["id"] for row in ledger["entries"]] == [f"P3V8-N0{i}" for i in range(1, 6)])
    check("negative_ledger_discriminators", all(row["negative_result"] and row["cause"] and row["positive_progress"] and row["residual"] and row["next_discriminator"] for row in ledger["entries"]))
    check("no_bytecode", not any(ROOT.rglob("*.pyc")) and not any(path.name == "__pycache__" for path in ROOT.rglob("*")))

    checksum_path = ROOT / "SHA256SUMS"
    manifest_ok = checksum_path.is_file()
    manifest_rows = {}
    if manifest_ok:
        for line in checksum_path.read_text().splitlines():
            digest, name = line.split("  ", 1)
            manifest_rows[name] = digest
        expected_files = {str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file() and path.name != "SHA256SUMS"}
        manifest_ok = set(manifest_rows) == expected_files and all(sha(ROOT / name) == digest for name, digest in manifest_rows.items())
    check("sha256_manifest", manifest_ok, {"entries": len(manifest_rows)})

    passed = sum(bool(row["pass"]) for row in checks)
    output = {
        "schema_version": "orion.p3.bertmap-table-reader-repair.validation.v8",
        "terminal": "P3_V8_PACKET_VALIDATION_PASS" if passed == len(checks) else "P3_V8_PACKET_VALIDATION_FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
