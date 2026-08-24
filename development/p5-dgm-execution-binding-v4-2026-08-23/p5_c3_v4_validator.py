#!/usr/bin/env python3
"""Deterministic non-pytest validator for the outcome-blind P5 C3 V4 freeze."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ARM_ID = "C3_ARCHIVE_BASED_SELF_EDIT__DGM"
COMMIT = "a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2"
TREE = "dc58ea5c481124afdb97468c1bed4e0debb425c4"
ARCHIVE_SHA = "bb92fc4c9f1a2a930059a9fa92db32f0d2ee81e030dd6925a9afbb4b2f3f1ee4"
ARCHIVE_FORMAT = "git archive --format=tar <commit>"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> Any:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def import_parser() -> Any:
    path = HERE / "p5_c3_native_parser.py"
    spec = importlib.util.spec_from_file_location("p5_c3_native_parser_v4", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load parser spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture(
    code: str,
    stage: str,
    *,
    exit_code: int | None = None,
    patch_sha: str | None = None,
    patch_bytes: int = 0,
) -> bytes:
    return (
        json.dumps(
            {
                "schema_version": "orion.p5.c3.dgm-patch-capture.v4",
                "arm_id": ARM_ID,
                "run_id": "validator-synthetic-run",
                "parent_commit": "initial",
                "native_code": code,
                "stage": stage,
                "exit_code": exit_code,
                "patch_sha256": patch_sha,
                "patch_bytes": patch_bytes,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, observed: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "observed": observed})

    json_files = [
        "AUDIT_RECEIPT_V4.json",
        "CLEANUP_AUDIT_V4.json",
        "P5_C3_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json",
        "P5_C3_V4_CUSTODY_HANDOFF_SCHEMA.json",
        "P5_C3_V4_EXECUTION_BINDING_PROTOCOL.json",
        "P5_C3_V4_FIELD_REGISTRY.json",
        "P5_C3_V4_NATIVE_OUTPUT_SCHEMA.json",
        "P5_C3_V4_NATIVE_TERMINAL_RULES.json",
        "P5_C3_V4_NEGATIVE_LEDGER.json",
        "P5_C3_V4_PATCH_CAPTURE_SCHEMA.json",
        "P5_C3_V4_RESOURCE_REGISTRY.json",
        "P5_C3_V4_RESULT.json",
        "P5_C3_V4_SMOKE_RECEIPT.json",
        "P5_C3_V4_SOURCE_RIGHTS_MANIFEST.json",
        "P5_C3_V4_WRITE_SURFACE_SCHEMA.json",
    ]
    loaded: dict[str, Any] = {}
    for name in json_files:
        try:
            loaded[name] = load(name)
            check(f"json_valid::{name}", True)
        except Exception as exc:  # fail receipt should remain readable
            check(f"json_valid::{name}", False, type(exc).__name__)
    if any(not item["passed"] for item in checks):
        print(
            json.dumps(
                {
                    "schema_version": "orion.p5.c3.validator-receipt.v4",
                    "passed": False,
                    "checks_total": len(checks),
                    "checks_passed": sum(x["passed"] for x in checks),
                    "checks_failed": sum(not x["passed"] for x in checks),
                    "checks": checks,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    registry = loaded["P5_C3_V4_FIELD_REGISTRY.json"]
    protocol = loaded["P5_C3_V4_EXECUTION_BINDING_PROTOCOL.json"]
    result = loaded["P5_C3_V4_RESULT.json"]
    rights = loaded["P5_C3_V4_SOURCE_RIGHTS_MANIFEST.json"]
    resources = loaded["P5_C3_V4_RESOURCE_REGISTRY.json"]
    smoke = loaded["P5_C3_V4_SMOKE_RECEIPT.json"]
    negative = loaded["P5_C3_V4_NEGATIVE_LEDGER.json"]
    audit = loaded["AUDIT_RECEIPT_V4.json"]
    cleanup = loaded["CLEANUP_AUDIT_V4.json"]
    fields = registry["fields"]
    required = registry["required_field_paths"]
    expected_bound = [
        "adapter.native_parser_binding",
        "identity.native_entrypoint_bytes",
        "identity.source_license_bytes",
        "identity.source_repository_commit",
        "model_provider.fallbacks",
        "resources.wallclock",
    ]
    expected_blocking = [path for path in required if path not in expected_bound]

    check("arm_id_exact", registry["arm_id"] == ARM_ID)
    check("required_fields_21", len(required) == 21, len(required))
    check("required_fields_unique", len(set(required)) == 21, len(set(required)))
    check("all_required_fields_present", set(required) == set(fields), sorted(set(required) ^ set(fields)))
    check("all_fields_have_state", all(fields[path].get("state") in {"BOUND", "UNBOUND", "CANNOT_CHECK"} for path in required))
    check("all_fields_have_recursive_discriminator", all(all(key in fields[path] for key in ("cause", "residual", "next_discriminator", "binding")) for path in required))
    check("bound_fields_6", registry["bound_field_count"] == 6, registry["bound_field_count"])
    check("bound_fields_exact", registry["bound_fields"] == expected_bound, registry["bound_fields"])
    check("blocking_fields_15", registry["blocking_field_count"] == 15, registry["blocking_field_count"])
    check("blocking_fields_exact", registry["blocking_fields"] == expected_blocking, registry["blocking_fields"])
    check("states_recompute_bound", [p for p in required if fields[p]["state"] == "BOUND"] == expected_bound)
    check("states_recompute_blocking", [p for p in required if fields[p]["state"] != "BOUND"] == expected_blocking)
    check("execution_not_ready", registry["execution_ready"] is False)
    check("panel_zero_of_six_registry", registry["panel_confirmatory_ready_arms"] == 0)
    check("empty_fallback_exact", fields["model_provider.fallbacks"]["binding"]["fallbacks"] == [])
    check("wallclock_bound", registry["bound_execution_envelope"]["wallclock_seconds"] == {"per_case": 21600, "whole_c3_run": 21600, "termination_grace": 120})
    check("runtime_launcher_absent", registry["bound_execution_envelope"]["runtime_launcher"] is None)
    check("dependency_lock_unbound", fields["runtime.dependency_lock"]["state"] == "UNBOUND")
    check("dependency_exact_pins_zero", fields["runtime.dependency_lock"]["binding"]["requirements"]["exact_pins"] == 0 and fields["runtime.dependency_lock"]["binding"]["requirements_dev"]["exact_pins"] == 0)
    check("dependency_declarations_23", fields["runtime.dependency_lock"]["binding"]["requirements"]["declaration_entries"] + fields["runtime.dependency_lock"]["binding"]["requirements_dev"]["declaration_entries"] == 23)
    check("lockfiles_zero", fields["runtime.dependency_lock"]["binding"]["lockfile_paths_in_authoritative_root"] == 0)
    check("parser_hash_bound", sha(HERE / "p5_c3_native_parser.py") == fields["adapter.native_parser_binding"]["binding"]["sha256"], sha(HERE / "p5_c3_native_parser.py"))
    check("runner_hash_bound", sha(HERE / "p5_c3_fail_closed_runner.py") == fields["resources.wallclock"]["binding"]["enforcer_sha256"], sha(HERE / "p5_c3_fail_closed_runner.py"))
    check("output_schema_hash_bound", sha(HERE / "P5_C3_V4_NATIVE_OUTPUT_SCHEMA.json") == fields["adapter.native_parser_binding"]["binding"]["output_schema_sha256"], sha(HERE / "P5_C3_V4_NATIVE_OUTPUT_SCHEMA.json"))

    check("source_commit_exact", protocol["source_identity"]["commit_sha"] == COMMIT)
    check("source_tree_exact", protocol["source_identity"]["tree_sha"] == TREE)
    check("source_archive_format_exact", protocol["source_identity"]["archive_format"] == ARCHIVE_FORMAT)
    check("source_archive_exact", protocol["source_identity"]["archive_sha256"] == ARCHIVE_SHA)
    check("rights_source_identity_exact", [rights["source"][k] for k in ("commit_sha", "tree_sha", "archive_format", "archive_sha256")] == [COMMIT, TREE, ARCHIVE_FORMAT, ARCHIVE_SHA])
    census = rights["authoritative_tree_metadata_census"]
    check("tree_files_1650", census["tracked_files"] == 1650, census["tracked_files"])
    check("tree_bytes_53195497", census["tracked_blob_bytes"] == 53195497, census["tracked_blob_bytes"])
    check("outcome_union_files_1595", census["outcome_or_initial_union"]["files"] == 1595, census["outcome_or_initial_union"]["files"])
    check("outcome_union_bytes_49707333", census["outcome_or_initial_union"]["blob_bytes"] == 49707333, census["outcome_or_initial_union"]["blob_bytes"])
    check("nonoutcome_union_files_55", census["non_outcome_union"]["files"] == 55, census["non_outcome_union"]["files"])
    check("nonoutcome_union_bytes_3488164", census["non_outcome_union"]["blob_bytes"] == 3488164, census["non_outcome_union"]["blob_bytes"])
    check("census_file_sum", census["outcome_or_initial_union"]["files"] + census["non_outcome_union"]["files"] == census["tracked_files"])
    check("census_byte_sum", census["outcome_or_initial_union"]["blob_bytes"] + census["non_outcome_union"]["blob_bytes"] == census["tracked_blob_bytes"])
    check("outcome_contents_not_opened", census["payload_contents_opened"] is False and result["material_discoveries"]["payload_contents_opened"] is False)
    check("outcome_prefixes_three", [x["prefix"] for x in census["outcome_or_initial_prefixes"]] == ["initial/", "initial_polyglot/", "swe_bench/ref_agent_results/"])
    check("reference_outcome_metadata_two", len(census["reference_outcome_entries"]) == 2)
    check("licence_hash_exact", fields["identity.source_license_bytes"]["binding"]["license_sha256"] == "84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17")
    check("source_rights_layers_separate", rights["licence_layers"][0]["spdx"] == "Apache-2.0" and rights["licence_layers"][1]["status"] == "SEPARATE_RIGHTS_NOT_CLOSED")

    check("result_bound_fields_6", result["v4_repairs"]["v4_bound_fields"] == 6)
    check("result_blocking_fields_15", result["v4_repairs"]["v4_blocking_fields"] == 15)
    check("result_delta_minus_three", result["v4_repairs"]["v3_to_v4_blocker_delta"] == -3)
    check("result_new_bindings_exact", result["v4_repairs"]["newly_bound_v3_fields"] == ["adapter.native_parser_binding", "model_provider.fallbacks", "resources.wallclock"])
    check("result_dependency_adjudication", result["v4_repairs"]["dependency_lock_adjudication"] == "UNBOUND__23_DECLARATIONS__0_EXACT_PINS__NO_LOCKFILE")
    check("result_not_executed", result["execution"]["c3_executed"] is False and result["execution"]["c3_execution_ready"] is False)
    check("panel_zero_of_six_result", result["execution"]["panel_confirmatory_ready_arms"] == 0 and result["execution"]["panel_required_arms"] == 6)
    check("raw_singletons_zero", result["preserved_boundaries"]["raw_native_singleton_licences"] == 0)
    check("raw_patch_unresolved", result["preserved_boundaries"]["raw_patch_disposition"] == "UNRESOLVED")
    check("v3_counts_preserved", [result["preserved_boundaries"][k] for k in ("v3_synthetic_cases", "v3_supported_singleton_case_records", "v3_unresolved_case_records")] == [231, 40, 191])
    check("conditional_support_set_four", result["preserved_boundaries"]["conditional_support_set"] == ["WITHIN_CLASS_MODEL_REPAIR", "MODEL_CLASS_EXPANSION", "REPRESENTATION_REGIME_REPAIR", "EXECUTION_REPAIR"])
    check("claims_cannot_check", all(value == "CANNOT_CHECK" for key, value in result["preserved_claims"].items() if key != "top_tier_publication_readiness"))
    check("publication_not_established", result["preserved_claims"]["top_tier_publication_readiness"] == "NOT_ESTABLISHED")
    check("resource_dependency_not_bound", resources["proposed_but_unbound"]["dependency_resolution"] is None)
    check("released_future_timeout_marked_ineffective", resources["source_defaults_not_adopted_as_matched_p5_values"]["future_result_timeout_effective"] is False)

    parser = import_parser()
    valid = parser.parse_capture_bytes(capture("PATCH_CAPTURED", "capture_patch", exit_code=0, patch_sha="a" * 64, patch_bytes=321))
    check("parser_patch_captured_success", valid["native_terminal"]["status"] == "COMPLETE_SUCCESS", valid["native_terminal"]["status"])
    check("parser_patch_captured_unresolved", valid["adapter_disposition"]["output"] == "UNRESOLVED")
    check("parser_raw_singleton_false", valid["adapter_disposition"]["raw_native_singleton_licensed"] is False)
    check("parser_no_outcome_mapping", valid["source"]["benchmark_or_archive_values_used_for_mapping"] is False)
    expected = [
        ("INITIALIZED", "initialize", "PARTIAL"),
        ("DIAGNOSIS_READY", "diagnose", "PARTIAL"),
        ("SELF_EDIT_STARTED", "self_edit", "PARTIAL"),
        ("NO_PROBLEM_STATEMENT", "diagnose", "PARTIAL"),
        ("NO_ENTRY", "initialize", "EMPTY"),
        ("MISSING_PATCH", "capture_patch", "EMPTY"),
        ("EMPTY_PATCH", "capture_patch", "EMPTY"),
        ("ARGPARSE_INTEGRITY_ERROR", "initialize", "ERROR"),
        ("PROVIDER_ERROR", "diagnose", "ERROR"),
        ("RUNTIME_ERROR", "self_edit", "ERROR"),
        ("TIMEOUT", "self_edit", "TIMEOUT"),
    ]
    for code, stage, status in expected:
        output = parser.parse_capture_bytes(capture(code, stage))
        check(f"parser_status::{code}", output["native_terminal"]["status"] == status, output["native_terminal"]["status"])
        check(f"parser_unresolved::{code}", output["adapter_disposition"]["output"] == "UNRESOLVED")
    invalid_patch = parser.parse_capture_bytes(capture("PATCH_CAPTURED", "capture_patch", exit_code=1, patch_sha="a" * 64, patch_bytes=321))
    check("parser_incoherent_patch_invalid", invalid_patch["native_terminal"]["status"] == "INVALID")

    def refused(raw: bytes) -> bool:
        try:
            parser.parse_capture_bytes(raw)
            return False
        except parser.NativeParseError:
            return True

    base_value = json.loads(capture("INITIALIZED", "initialize"))
    for key in ("gold_future", "heldout_future", "protected_future", "scorer_future", "benchmark_outcome", "test_output"):
        value = dict(base_value)
        value[key] = "synthetic"
        check(f"parser_refuses_prohibited::{key}", refused(json.dumps(value).encode()))
    unknown = dict(base_value)
    unknown["innocuous_but_unregistered"] = "synthetic"
    check("parser_refuses_unknown_key", refused(json.dumps(unknown).encode()))
    wrong_arm = dict(base_value)
    wrong_arm["arm_id"] = "WRONG"
    check("parser_refuses_wrong_arm", refused(json.dumps(wrong_arm).encode()))
    check("parser_refuses_patch_stage_mismatch", refused(capture("PATCH_CAPTURED", "self_edit", exit_code=0, patch_sha="a" * 64, patch_bytes=321)))
    check("parser_refuses_nonpatch_with_patch", refused(capture("INITIALIZED", "initialize", patch_sha="a" * 64, patch_bytes=321)))

    runner = subprocess.run(
        [
            sys.executable,
            str(HERE / "p5_c3_fail_closed_runner.py"),
            "--registry",
            str(HERE / "P5_C3_V4_FIELD_REGISTRY.json"),
            "--preflight",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    runner_value = json.loads(runner.stdout)
    check("runner_preflight_refuses", runner.returncode == 3, runner.returncode)
    check("runner_preflight_count_15", runner_value["blocking_field_count"] == 15, runner_value["blocking_field_count"])
    check("runner_preflight_not_ready", runner_value["execution_ready"] is False)

    parser_smoke = smoke["parser_conformance"]
    check("smoke_valid_exit_zero", parser_smoke["exit_code"] == 0)
    check("smoke_native_complete", parser_smoke["native_status"] == "COMPLETE_SUCCESS")
    check("smoke_adapter_unresolved", parser_smoke["adapter_output"] == "UNRESOLVED")
    check("smoke_raw_singleton_false", parser_smoke["raw_native_singleton_licensed"] is False)
    check("smoke_prohibited_exit_two", parser_smoke["prohibited_exit_code"] == 2)
    check("smoke_preflight_exit_three", smoke["fail_closed_preflight"]["exit_code"] == 3)
    check("smoke_preflight_count_15", smoke["fail_closed_preflight"]["blocking_field_count"] == 15)
    check("smoke_full_native_cannot_check", smoke["full_native_smoke"]["state"] == "CANNOT_CHECK")
    check("smoke_no_raw_retention", smoke["raw_or_large_payloads_retained"] is False and parser_smoke["valid_fixture_retained"] is False and parser_smoke["prohibited_fixture_retained"] is False)

    required_negative_ids = {
        "P5.C3.V4.ARGPARSE.CHOICE.CONCATENATION",
        "P5.C3.V4.INEFFECTIVE.FUTURE.TIMEOUT",
        "P5.C3.V4.MUTABLE.ENVIRONMENT",
        "P5.C3.V4.UNTRUSTED.GENERATED.CODE",
    }
    entries = negative["entries"]
    check("negative_ledger_entries_nine", len(entries) == 9, len(entries))
    check("negative_ledger_recursive_fields", all(all(key in item and item[key] for key in ("id", "cause", "positive_progress", "residual", "next_discriminator")) for item in entries))
    check("required_source_defects_retained", required_negative_ids <= {item["id"] for item in entries}, sorted({item["id"] for item in entries}))
    check("negative_markdown_present", (HERE / "P5_C3_V4_NEGATIVE_LEDGER.md").is_file())
    check("report_terminal_exact", result["terminal"] in (HERE / "SCIENTIFIC_REPORT_V4.md").read_text(encoding="utf-8"))
    report_text = (HERE / "SCIENTIFIC_REPORT_V4.md").read_text(encoding="utf-8")
    check("report_counts_explicit", "6/21 BOUND" in report_text and "15/21 blocking" in report_text and "0/6" in report_text)
    check("report_dependency_honesty", "not forced" in report_text and "zero exact pins" in report_text)
    check("audit_no_forbidden_execution", all(value is False for value in audit["execution"].values()))
    check("audit_readiness_exact", [audit["readiness"][key] for key in ("v4_bound_fields", "v4_blocking_fields", "panel_ready_arms", "panel_required_arms")] == [6, 15, 0, 6])
    check("cleanup_no_payloads", cleanup["no_raw_or_large_payload_retained"] is True and cleanup["outcome_payloads_retained"] is False)

    forbidden_suffixes = {".tar", ".gz", ".zip", ".pdf", ".jsonl", ".sqlite", ".db", ".pt", ".bin"}
    retained_forbidden = [p.name for p in HERE.iterdir() if p.is_file() and any(p.name.endswith(s) for s in forbidden_suffixes)]
    check("no_raw_or_large_artifact_types", retained_forbidden == [], retained_forbidden)
    large_files = [p.name for p in HERE.iterdir() if p.is_file() and p.stat().st_size > 1024 * 1024]
    check("no_file_over_one_mib", large_files == [], large_files)
    cache_paths = [str(p.relative_to(HERE)) for p in HERE.rglob("__pycache__")]
    check("no_python_cache", cache_paths == [], cache_paths)

    failures = [item for item in checks if not item["passed"]]
    receipt = {
        "schema_version": "orion.p5.c3.validator-receipt.v4",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failures),
        "checks_failed": len(failures),
        "passed": not failures,
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
