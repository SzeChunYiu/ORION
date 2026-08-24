#!/usr/bin/env python3
"""Outcome-blind validator for the frozen P5 C6 ScienceClaw V4 packet."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
UPSTREAM = Path(os.environ.get("P5_C6_UPSTREAM", str(HERE / ".source-audit"))).resolve()
COMMIT = "38b2f681e87272cd505c9b2671760fc3729756c2"
TREE = "8b483159e46da54675ee904841f2e8667b2348bc"
ARCHIVE_SHA256 = "2020d5dd69e5118bebccb2e82cf47807c6be6a0eeb75952e910f0bbac98f82be"
ARCHIVE_BYTES = 109_045_760
TERMINAL = (
    "P5_C6_V4_SCIENCECLAW_SOURCE_TREE_DRAFT_PARSER_AND_OUTER_WALLCLOCK_BOUND__"
    "NATIVE_SELECTOR_UNSUPPORTED_AND_FALLBACKS_OPEN__SIXTEEN_C6_FIELDS_BLOCKING__"
    "PRIOR_OUTCOME_PREFIXES_HASHED_NOT_DECODED__ZERO_OF_SIX_PANEL_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)
EXPECTED_JSON_FILES = 15


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(name: str, predicate: bool, checks: list[dict[str, Any]], detail: Any = None) -> None:
    checks.append({"check": name, "passed": bool(predicate), "detail": detail})
    if not predicate:
        raise AssertionError(f"failed: {name}: {detail}")


def archive_identity() -> tuple[str, int]:
    proc = subprocess.Popen(
        ["git", "-C", str(UPSTREAM), "archive", "--format=tar", "HEAD"],
        stdout=subprocess.PIPE,
    )
    if proc.stdout is None:
        raise AssertionError("archive stdout missing")
    h = hashlib.sha256()
    total = 0
    for chunk in iter(lambda: proc.stdout.read(1024 * 1024), b""):
        h.update(chunk)
        total += len(chunk)
    code = proc.wait()
    if code != 0:
        raise AssertionError(f"git archive failed: {code}")
    return h.hexdigest(), total


def validate_native_output(value: dict[str, Any]) -> None:
    required = {
        "schema_version", "arm_id", "adapter_terminal", "native_terminal",
        "draft_sha256", "draft_size_bytes", "top_level_keys",
        "investigation_result_key_count", "structural_list_counts",
        "scientific_payload_values_retained", "native_exit_status_is_sufficient",
        "raw_native_singleton_licences", "performance_inference",
        "source_native_caveat",
    }
    if set(value) != required:
        raise AssertionError(f"native output keys mismatch: {sorted(set(value) ^ required)}")
    if value["schema_version"] != "orion.p5.c6.scienceclaw-native-terminal.v4":
        raise AssertionError("native schema mismatch")
    if value["arm_id"] != "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW":
        raise AssertionError("arm mismatch")
    if value["adapter_terminal"] != "UNRESOLVED":
        raise AssertionError("adapter terminal must remain UNRESOLVED")
    if value["native_terminal"] != "NATIVE_DRY_RUN_DRAFT_RECORDED":
        raise AssertionError("native terminal mismatch")
    if value["scientific_payload_values_retained"] is not False:
        raise AssertionError("scientific payload retention drift")
    if value["native_exit_status_is_sufficient"] is not False:
        raise AssertionError("exit-status sufficiency drift")
    if value["raw_native_singleton_licences"] != 0:
        raise AssertionError("raw singleton licence drift")
    if value["performance_inference"] != "FORBIDDEN":
        raise AssertionError("performance inference drift")
    serialized = json.dumps(value)
    for forbidden_value in ("fixture hypothesis", "fixture findings", "fixture content", "fixture paper title"):
        if forbidden_value in serialized:
            raise AssertionError(f"scientific fixture payload leaked: {forbidden_value}")


def main() -> int:
    checks: list[dict[str, Any]] = []
    registry = load(HERE / "P5_C6_V4_FIELD_REGISTRY.json")
    fields = registry["fields"]
    bound = sorted(k for k, v in fields.items() if v["status"] == "BOUND")
    blocking = sorted(k for k, v in fields.items() if v["status"] != "BOUND")
    check("registry_21_fields", len(fields) == registry["required_field_count"] == 21, checks, len(fields))
    check("registry_5_bound", len(bound) == registry["bound_field_count"] == 5, checks, bound)
    check("registry_16_blocking", len(blocking) == registry["blocking_field_count"] == 16, checks, blocking)
    check("native_selector_unsupported", registry["native_selector_supported"] is False, checks)
    check("registry_not_ready", registry["execution_ready"] is False, checks)
    check("panel_zero_of_six", registry["panel_confirmatory_ready_arms"] == 0, checks)
    check("terminal_exact", registry["terminal"] == TERMINAL, checks)
    check("terminal_file_exact", (HERE / "TERMINAL_V4.txt").read_text().strip() == TERMINAL, checks)

    head = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD^{tree}"], text=True).strip()
    status = subprocess.check_output(["git", "-C", str(UPSTREAM), "status", "--porcelain"], text=True)
    check("source_commit_exact", head == COMMIT, checks, head)
    check("source_tree_exact", tree == TREE, checks, tree)
    check("source_worktree_clean", status == "", checks, status)

    manifest = load(HERE / "SCIENCECLAW_SOURCE_TREE_MANIFEST_V4.json")
    check("tree_manifest_file_count", manifest["file_count"] == len(manifest["entries"]) == 2122, checks)
    total = 0
    file_hash_checks = 0
    for entry in manifest["entries"]:
        path = UPSTREAM / entry["path"]
        if not path.is_file() or path.is_symlink():
            raise AssertionError(f"missing or unsafe source entry: {entry['path']}")
        if path.stat().st_size != entry["size_bytes"] or sha(path) != entry["sha256"]:
            raise AssertionError(f"source manifest mismatch: {entry['path']}")
        total += entry["size_bytes"]
        file_hash_checks += 1
    check("source_file_sha256_validations", file_hash_checks == 2122, checks, file_hash_checks)
    check("source_total_bytes", total == manifest["total_file_bytes"] == 106_818_041, checks, total)
    check("manifest_commit_tree", manifest["commit_sha"] == COMMIT and manifest["tree_sha"] == TREE, checks)
    exclusion = manifest["outcome_blind_exclusion_census"]
    check("prior_outcome_prefix_census", exclusion["file_count"] == 13 and exclusion["total_bytes"] == 106_755, checks, exclusion)
    check("prior_outcome_payloads_not_decoded", exclusion["payload_values_decoded_or_displayed"] is False and exclusion["cryptographic_hashing_only"] is True, checks)
    pycache = manifest["tracked_pycache_census"]
    check("tracked_pycache_census", pycache["file_count"] == 374 and pycache["total_bytes"] == 3_400_553, checks, pycache)
    archive_hash, archive_bytes = archive_identity()
    check("archive_sha256_exact", archive_hash == ARCHIVE_SHA256, checks, archive_hash)
    check("archive_size_exact", archive_bytes == ARCHIVE_BYTES, checks, archive_bytes)

    deps = load(HERE / "SCIENCECLAW_DEPENDENCY_DECLARATIONS_V4.json")
    check("no_resolved_lock", deps["lock_present_in_authoritative_tree"] is False and deps["common_lock_paths"] == [], checks)
    check("core_9_zero_exact", deps["top_level_core_declaration_count"] == 9 and deps["top_level_core_exact_pin_count"] == 0, checks)
    check("full_112_zero_exact", deps["top_level_full_declaration_count"] == 112 and deps["top_level_full_exact_pin_count"] == 0, checks)
    dynamic = deps["skill_dependency_map"]
    check("dynamic_dependency_map", dynamic["skill_keys"] == 60 and dynamic["unique_unversioned_package_names"] == 96 and dynamic["package_references"] == 106, checks, dynamic)
    check("dynamic_install_continues_after_failure", "continues" in dynamic["failure_behavior"], checks, dynamic["failure_behavior"])

    rights = load(HERE / "P5_C6_V4_SOURCE_RIGHTS_MANIFEST.json")
    check("source_license_hash", rights["root_licence"]["sha256"] == sha(UPSTREAM / "LICENSE"), checks)
    check("license_metadata_inconsistent", rights["root_licence"]["spdx"] == "Apache-2.0" and rights["package_json_declared_license"] == "MIT" and rights["source_metadata_consistent"] is False, checks)
    check("skill_rights_census", rights["direct_skill_directories"] == 334 and rights["files_under_skills"] == 1930 and rights["nested_component_licence_files"] == 4, checks)
    check("rights_roots_open", not rights["task_content_rights_closed"] and not rights["service_rights_closed"] and not rights["generated_artifact_rights_closed"], checks)

    parser_path = HERE / "p5_c6_native_parser.py"
    runner_path = HERE / "p5_c6_fail_closed_runner.py"
    check("parser_hash_bound", fields["adapter.native_parser_binding"]["binding"]["sha256"] == sha(parser_path), checks)
    check("runner_hash_bound", fields["resources.wallclock"]["binding"]["enforcer_sha256"] == sha(runner_path), checks)
    check("native_fallbacks_blocking", fields["model_provider.fallbacks"]["status"] == "BLOCKING" and fields["model_provider.fallbacks"]["binding"] is None, checks)

    with tempfile.TemporaryDirectory(prefix="p5-c6-v4-smoke-") as temp_text:
        temp = Path(temp_text)
        draft = {
            "agent": "fixture-agent",
            "topic": "fixture topic",
            "community": "fixture-community",
            "title": "fixture title",
            "hypothesis": "fixture hypothesis",
            "method": "fixture method",
            "findings": "fixture findings",
            "content": "fixture content",
            "investigation_results": {
                "productive_tools": ["fixture-tool"],
                "papers": [{"title": "fixture paper title"}],
                "proteins": [],
                "compounds": [],
                "insights": [],
                "artifacts": [],
            },
        }
        draft_path = temp / "draft.json"
        write_json(draft_path, draft)
        parsed_path = temp / "parsed.json"
        parsed = subprocess.run(
            [sys.executable, str(parser_path), "--draft", str(draft_path), "--output", str(parsed_path)],
            capture_output=True, text=True, timeout=30,
        )
        check("native_shape_parser_exit_zero", parsed.returncode == 0, checks, parsed.stderr)
        parsed_value = load(parsed_path)
        validate_native_output(parsed_value)
        check("native_output_schema_validation", True, checks, "1 output validated")
        check("native_shape_unresolved", parsed_value["adapter_terminal"] == "UNRESOLVED" and parsed_value["raw_native_singleton_licences"] == 0, checks)
        check("scientific_payload_not_retained", parsed_value["scientific_payload_values_retained"] is False, checks)

        protected_path = temp / "protected.json"
        protected = dict(draft)
        protected["investigation_results"] = {"protected_score": {"payload": "synthetic-do-not-decode"}}
        write_json(protected_path, protected)
        refused = subprocess.run(
            [sys.executable, str(parser_path), "--draft", str(protected_path)],
            capture_output=True, text=True, timeout=30,
        )
        check("protected_key_refused_before_decode", refused.returncode == 2 and "before JSON decoding" in refused.stdout, checks, refused.stdout)

        terminal_path = temp / "runner-terminal.json"
        runner = subprocess.run(
            [sys.executable, str(runner_path), "--registry", str(HERE / "P5_C6_V4_FIELD_REGISTRY.json"), "--terminal-output", str(terminal_path), "--preflight-only"],
            capture_output=True, text=True, timeout=30,
        )
        runner_value = load(terminal_path)
        check("runner_refuses_current_registry", runner.returncode == 3, checks, runner.stderr)
        check("runner_refusal_exact_count", runner_value["terminal"] == "EXECUTION_REFUSED_NONBOUND_FIELDS" and runner_value["blocking_field_count"] == 16 and runner_value["native_execution"] is False, checks, runner_value)

    result = load(HERE / "P5_C6_V4_RESULT.json")
    check("native_execution_false", result["execution"]["c6_executed"] is False, checks)
    check("full_native_smoke_cannot_check", result["execution"]["native_scienceclaw_smoke"] == "CANNOT_CHECK", checks)
    check("readiness_delta_exact", result["v4_repairs"]["c6_bound_fields"] == 5 and result["v4_repairs"]["c6_blocking_fields"] == 16 and result["v4_repairs"]["v3_to_v4_blocker_delta"] == -2, checks)
    check("performance_superiority_cannot_check", result["preserved_claims"]["performance"] == "CANNOT_CHECK" and result["preserved_claims"]["superiority"] == "CANNOT_CHECK", checks)
    preserved = result["preserved_boundaries"]
    check(
        "v3_and_scienceclaw_boundaries_preserved",
        preserved["raw_native_singleton_licences"] == 0
        and preserved["scienceclaw_supported_singletons"] == 0
        and preserved["all_native_scienceclaw_fibres"] == "UNRESOLVED"
        and preserved["v3_synthetic_cases"] == 231
        and preserved["v3_supported_singleton_case_records"] == 40
        and preserved["v3_supported_singleton_fibres"] == 20
        and preserved["v3_unresolved_case_records"] == 191,
        checks,
    )
    material = result["material_discoveries"]
    check("material_census_exact", material["excluded_prior_outcome_prefix_files"] == 13 and material["excluded_prior_outcome_prefix_bytes"] == 106755 and material["tracked_pycache_files"] == 374 and material["tracked_pycache_bytes"] == 3400553, checks, material)
    check("dry_run_not_outcome_free", material["native_dry_run_is_outcome_free"] is False, checks)
    check("native_selector_false", material["native_selector_supported"] is False, checks)

    smoke_receipt = {
        "schema_version": "orion.p5.c6.outcome-blind-smoke-receipt.v4",
        "arm_id": "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW",
        "fixture": "authored native-shaped scienceclaw-post dry-run draft; not retained",
        "fixture_is_substantive_p5_case": False,
        "fixture_is_performance": False,
        "native_or_model_or_tool_job_executed": False,
        "parser": {
            "native_shape_exit_code": 0,
            "native_terminal": "NATIVE_DRY_RUN_DRAFT_RECORDED",
            "adapter_terminal": "UNRESOLVED",
            "protected_key_exit_code": 2,
            "protected_key_refused_before_json_decoding": True,
            "native_output_schema_validations": 1,
            "scientific_payload_values_retained": False,
        },
        "runner": {"preflight_exit_code": 3, "terminal": "EXECUTION_REFUSED_NONBOUND_FIELDS", "blocking_field_count": 16},
        "prior_outcome_payload_values_decoded_or_displayed": False,
        "protected_outcomes_accessed": 0,
        "performance_inference": "FORBIDDEN",
    }
    write_json(HERE / "P5_C6_V4_SMOKE_RECEIPT.json", smoke_receipt)

    audit = {
        "schema_version": "orion.p5.c6.audit-receipt.v4",
        "arm_id": "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW",
        "frozen_at_utc": "2026-08-23T18:49:49Z",
        "source": {"commit_sha": COMMIT, "tree_sha": TREE, "archive_sha256": ARCHIVE_SHA256, "archive_size_bytes": ARCHIVE_BYTES, "worktree_clean": True},
        "field_census": {"required": 21, "bound": 5, "blocking": 16, "execution_ready": False, "native_selector_supported": False},
        "validation": {"checks_passed": len(checks), "checks_failed": 0, "source_file_sha256_validations": file_hash_checks, "archive_sha256_validations": 1, "native_output_schema_validations": 1, "json_files_parsed": EXPECTED_JSON_FILES, "json_parse_failures": 0},
        "smoke": smoke_receipt,
        "scientific_claims": {"native_execution": False, "performance": "CANNOT_CHECK", "superiority": "CANNOT_CHECK", "raw_native_singleton_licences": 0, "prior_outcome_payload_values_decoded_or_displayed": False},
        "terminal": TERMINAL,
        "checks": checks,
    }
    write_json(HERE / "AUDIT_RECEIPT_V4.json", audit)

    json_paths = sorted(HERE.glob("*.json"))
    if len(json_paths) != EXPECTED_JSON_FILES:
        raise AssertionError(f"expected {EXPECTED_JSON_FILES} JSON files, found {len(json_paths)}")
    for path in json_paths:
        load(path)

    print(json.dumps({
        "terminal": TERMINAL,
        "checks_passed": len(checks),
        "json_files_parsed": len(json_paths),
        "source_file_sha256_validations": file_hash_checks,
        "archive_sha256_validations": 1,
        "native_output_schema_validations": 1,
        "bound_fields": 5,
        "blocking_fields": 16,
        "native_execution": False,
        "native_selector_supported": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
