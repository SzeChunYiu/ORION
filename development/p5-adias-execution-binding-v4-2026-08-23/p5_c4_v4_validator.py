#!/usr/bin/env python3
"""Outcome-blind validator for the frozen P5 C4 ADIAS V4 packet."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parents[2] / "upstream" / "adias-fbcf0c73"
COMMIT = "fbcf0c73d12d30a4ee0d13c2e64b4c40d00b2993"
TREE = "98fc19e691c31b635ec432b6240db775a9527fd0"
TERMINAL = "P5_C4_V4_ADIAS_SOURCE_TREE_NATIVE_PARSER_EMPTY_FALLBACK_AND_WALLCLOCK_BOUND__FIFTEEN_C4_FIELDS_BLOCKING__DEPENDENCY_LOCK_TASK_RIGHTS_ISOLATION_AND_CUSTODY_UNBOUND__ZERO_OF_SIX_PANEL_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
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


def validate_native_output(value: dict[str, Any]) -> None:
    required = {
        "schema_version", "arm_id", "adapter_terminal", "native_terminal",
        "generation_id", "metadata_sha256", "report_count", "nonempty_report_count",
        "reports", "native_exit_status_is_sufficient", "performance_inference",
        "raw_native_singleton_licences", "source_native_caveat",
    }
    if set(value) != required:
        raise AssertionError(f"native output keys mismatch: {sorted(set(value) ^ required)}")
    if value["schema_version"] != "orion.p5.c4.adias-native-terminal.v4":
        raise AssertionError("native schema_version mismatch")
    if value["adapter_terminal"] != "UNRESOLVED":
        raise AssertionError("adapter terminal must remain UNRESOLVED")
    if value["performance_inference"] != "FORBIDDEN":
        raise AssertionError("performance inference must be forbidden")
    if value["native_exit_status_is_sufficient"] is not False:
        raise AssertionError("native exit status sufficiency drift")
    if value["raw_native_singleton_licences"] != 0:
        raise AssertionError("raw singleton licence drift")
    if value["report_count"] != len(value["reports"]):
        raise AssertionError("report count mismatch")
    forbidden_retained = {"score", "success_rate", "reward", "average_reward", "cost_usd", "test_scores"}
    serialized = json.dumps(value)
    for key in forbidden_retained:
        if f'"{key}"' in serialized:
            raise AssertionError(f"outcome value key retained: {key}")


def main() -> int:
    checks: list[dict[str, Any]] = []
    registry = load(HERE / "P5_C4_V4_FIELD_REGISTRY.json")
    fields = registry["fields"]
    bound = sorted(key for key, value in fields.items() if value["status"] == "BOUND")
    blocking = sorted(key for key, value in fields.items() if value["status"] != "BOUND")
    check("registry_21_fields", len(fields) == 21, checks, len(fields))
    check("registry_6_bound", len(bound) == registry["bound_field_count"] == 6, checks, bound)
    check("registry_15_blocking", len(blocking) == registry["blocking_field_count"] == 15, checks, blocking)
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

    manifest = load(HERE / "ADIAS_SOURCE_TREE_MANIFEST_V4.json")
    check("tree_manifest_file_count", manifest["file_count"] == len(manifest["entries"]) == 1578, checks)
    hash_checks = 0
    total_bytes = 0
    for entry in manifest["entries"]:
        path = UPSTREAM / entry["path"]
        if not path.is_file() or path.is_symlink():
            raise AssertionError(f"missing/unsafe source entry: {entry['path']}")
        if path.stat().st_size != entry["size_bytes"] or sha(path) != entry["sha256"]:
            raise AssertionError(f"source manifest mismatch: {entry['path']}")
        total_bytes += entry["size_bytes"]
        hash_checks += 1
    check("tree_manifest_sha256_entries", hash_checks == 1578, checks, hash_checks)
    check("tree_manifest_total_bytes", total_bytes == manifest["total_file_bytes"], checks, total_bytes)
    check("tree_manifest_commit_tree", manifest["commit_sha"] == COMMIT and manifest["tree_sha"] == TREE, checks)
    check("archive_identity", manifest["deterministic_git_archive"]["sha256"] == "472e2ef2258c764b563b07be725a82de80df15bd617259fd839f894b8c602216", checks)

    declarations = load(HERE / "ADIAS_DEPENDENCY_DECLARATIONS_V4.json")
    check("declarations_not_lock", declarations["classification"] == "SOURCE_DECLARATIONS_NOT_A_TRANSITIVE_LOCK" and declarations["lock_present_in_authoritative_tree"] is False, checks)
    check("four_unpinned_vcs", declarations["unpinned_vcs_declaration_count"] == 4, checks, declarations["unpinned_vcs_declarations"])
    rights = load(HERE / "P5_C4_V4_SOURCE_RIGHTS_MANIFEST.json")
    check("source_license_hash", rights["root_licence"]["sha256"] == sha(UPSTREAM / "LICENSE.md"), checks)
    check("component_data_licenses_zero", rights["component_licence_files_under_data"] == 0, checks)
    check("commercial_not_authorized", rights["commercial_execution_authorized"] is False, checks)

    parser_path = HERE / "p5_c4_native_parser.py"
    runner_path = HERE / "p5_c4_fail_closed_runner.py"
    check("parser_hash_bound", fields["adapter.native_parser_binding"]["binding"]["sha256"] == sha(parser_path), checks)
    check("runner_hash_bound", fields["resources.wallclock"]["binding"]["enforcer_sha256"] == sha(runner_path), checks)

    with tempfile.TemporaryDirectory(prefix="p5-c4-v4-smoke-") as temp_text:
        temp = Path(temp_text)
        generation = temp / "gen_0"
        report_dir = generation / "alfworld_eval"
        report_dir.mkdir(parents=True)
        metadata = {
            "gen_output_dir": str(generation),
            "current_genid": 0,
            "parent_genid": None,
            "run_baseline": None,
            "prev_patch_files": [],
            "curr_patch_files": [],
            "parent_agent_success": True,
            "optimize_option": "agent_and_meta",
            "agent_archive_path": None,
            "run_eval": True,
            "valid_parent": True,
        }
        report = {
            "score": 0.0,
            "success_rate": 0.0,
            "average_reward": 0.0,
            "total": 0,
            "steps": {"total": 0, "average": 0.0},
            "task_type": "household",
            "task_agent_usage": {},
        }
        write_json(generation / "metadata.json", metadata)
        write_json(report_dir / "report.json", report)
        parsed_path = temp / "parsed.json"
        parsed = subprocess.run(
            [sys.executable, str(parser_path), "--generation-dir", str(generation), "--expected-domain", "alfworld", "--output", str(parsed_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        check("zero_task_parser_exit_zero", parsed.returncode == 0, checks, parsed.stderr)
        parsed_value = load(parsed_path)
        validate_native_output(parsed_value)
        check("zero_task_terminal_empty", parsed_value["native_terminal"] == "NATIVE_EMPTY_EVALUATION", checks, parsed_value)
        check("zero_task_not_performance", parsed_value["performance_inference"] == "FORBIDDEN" and parsed_value["adapter_terminal"] == "UNRESOLVED", checks)
        check("native_output_schema_validation", True, checks, "1 output validated")

        protected = temp / "gen_1"
        protected_report = protected / "alfworld_eval"
        protected_report.mkdir(parents=True)
        write_json(protected / "metadata.json", {**metadata, "current_genid": 1, "protected_score": 1.0})
        write_json(protected_report / "report.json", report)
        refused = subprocess.run(
            [sys.executable, str(parser_path), "--generation-dir", str(protected), "--expected-domain", "alfworld"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        check("protected_key_refused", refused.returncode == 2 and "protected/final-test key refused" in refused.stdout, checks, refused.stdout)

        runner_terminal = temp / "runner_terminal.json"
        runner = subprocess.run(
            [sys.executable, str(runner_path), "--registry", str(HERE / "P5_C4_V4_FIELD_REGISTRY.json"), "--terminal-output", str(runner_terminal), "--preflight-only"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        runner_value = load(runner_terminal)
        check("runner_refuses_current_registry", runner.returncode == 3, checks, runner.stderr)
        check("runner_refusal_exact_count", runner_value["terminal"] == "EXECUTION_REFUSED_NONBOUND_FIELDS" and runner_value["blocking_field_count"] == 15, checks, runner_value)

    result = load(HERE / "P5_C4_V4_RESULT.json")
    check("native_execution_false", result["execution"]["c4_executed"] is False, checks)
    check("performance_cannot_check", result["preserved_claims"]["performance"] == "CANNOT_CHECK", checks)
    check("superiority_cannot_check", result["preserved_claims"]["superiority"] == "CANNOT_CHECK", checks)
    check("raw_singletons_zero", result["preserved_boundaries"]["raw_native_singleton_licences"] == 0, checks)
    check(
        "v3_unsupported_fibres_preserved",
        result["preserved_boundaries"]["v3_synthetic_cases"] == 231
        and result["preserved_boundaries"]["v3_supported_singleton_case_records"] == 40
        and result["preserved_boundaries"]["v3_supported_singleton_fibres"] == 20
        and result["preserved_boundaries"]["v3_unresolved_case_records"] == 191
        and result["preserved_boundaries"]["scienceclaw_supported_singletons"] == 0,
        checks,
    )
    check("smoke_not_substantive", result["preserved_boundaries"]["smoke_fixture_is_substantive_p5_case"] is False, checks)

    smoke_receipt = {
        "schema_version": "orion.p5.c4.outcome-blind-smoke-receipt.v4",
        "arm_id": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
        "fixture": "authored zero-task native-shaped ADIAS gen_0 metadata/report; not retained",
        "fixture_is_substantive_p5_case": False,
        "fixture_is_performance": False,
        "native_or_model_job_executed": False,
        "parser": {
            "zero_task_exit_code": 0,
            "zero_task_native_terminal": "NATIVE_EMPTY_EVALUATION",
            "adapter_terminal": "UNRESOLVED",
            "protected_key_exit_code": 2,
            "protected_key_refused": True,
            "native_output_schema_validations": 1,
        },
        "runner": {
            "preflight_exit_code": 3,
            "terminal": "EXECUTION_REFUSED_NONBOUND_FIELDS",
            "blocking_field_count": 15,
        },
        "outcomes_accessed": 0,
        "performance_inference": "FORBIDDEN",
    }
    write_json(HERE / "P5_C4_V4_SMOKE_RECEIPT.json", smoke_receipt)

    audit = {
        "schema_version": "orion.p5.c4.audit-receipt.v4",
        "arm_id": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
        "frozen_at_utc": "2026-08-23T18:34:25Z",
        "source": {"commit_sha": COMMIT, "tree_sha": TREE, "worktree_clean": True},
        "field_census": {"required": 21, "bound": 6, "blocking": 15, "execution_ready": False},
        "validation": {
            "checks_passed": len(checks),
            "checks_failed": 0,
            "source_file_sha256_validations": hash_checks,
            "native_output_schema_validations": 1,
            "json_files_parsed": EXPECTED_JSON_FILES,
            "json_parse_failures": 0,
        },
        "smoke": smoke_receipt,
        "scientific_claims": {
            "native_execution": False,
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "raw_native_singleton_licences": 0,
        },
        "terminal": TERMINAL,
        "checks": checks,
    }
    write_json(HERE / "AUDIT_RECEIPT_V4.json", audit)

    json_paths = sorted(HERE.glob("*.json"))
    if len(json_paths) != EXPECTED_JSON_FILES:
        raise AssertionError(f"expected {EXPECTED_JSON_FILES} JSON files, found {len(json_paths)}")
    for path in json_paths:
        load(path)

    print(
        json.dumps(
            {
                "terminal": TERMINAL,
                "checks_passed": len(checks),
                "json_files_parsed": len(json_paths),
                "source_file_sha256_validations": hash_checks,
                "native_output_schema_validations": 1,
                "bound_fields": 6,
                "blocking_fields": 15,
                "native_execution": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
