#!/usr/bin/env python3
"""Packet-native validation without rerunning the completed V9 microgate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V8 = ROOT / "development" / "p5-c3-native-environment-v8-2026-08-23"
TERMINAL = (
    "P5_C3_V9_OUTCOME_FREE_INITIALIZATION_ADAPTER_STOPPED__"
    "UNCHANGED_NATIVE_PARENT_SELECTION_REQUIRES_PRIOR_OUTCOME_METADATA__"
    "NO_LAWFUL_SEMANTICS_PRESERVING_ADAPTER__RUNTIME_TASK_ENVIRONMENT_REMAINS_BLOCKING"
)
EXPECTED_V8 = {
    "P5_C3_CANDIDATE_SAFE_SEED_V8.tar.gz": "8d7197f581cad11695ae4c867ad8f941d86f7eeec8d0e8e4e7b79895d72b8f2d",
    "P5_C3_NATIVE_TASK_ENVIRONMENT_RECEIPT_V8.json": "fafca0ece9654e7c0b0e738628648fea9b74a917b29440c16513b53a7b21a4d2",
    "P5_C3_INPUT_NATIVE_CERTIFICATE_V8.json": "460402c3925a083017d640872960ec9927dbbfce62e24fbe7f2cd62faf7de341",
    "P5_C3_MUTABLE_IMMUTABLE_SPLIT_V8.json": "f1fead7d0e607ee30132e4c28f5634b0a96abfc17e0f2bb689e9e0a9febf6a4c",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(checks: list[dict[str, Any]], name: str, condition: bool, detail: Any = None) -> None:
    checks.append({"check": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def main() -> int:
    checks: list[dict[str, Any]] = []
    prereg = load(HERE / "P5_C3_V9_SUCCESSOR_ADAPTER_PREREGISTRATION.json")
    receipt = load(HERE / "P5_C3_V9_MICROGATE_RECEIPT.json")
    witness = load(HERE / "P5_C3_V9_INITIALIZATION_IMPOSSIBILITY_WITNESS.json")
    result = load(HERE / "P5_C3_V9_RESULT.json")

    prereg_sha = sha(HERE / "P5_C3_V9_SUCCESSOR_ADAPTER_PREREGISTRATION.json")
    check(checks, "preregistration_exact", prereg_sha == "18946ca0493bb73a3c52f51a0cef5910b11f19e0e89c6da34f272c761076718c", prereg_sha)
    check(checks, "preregistered_before_microgate", prereg["frozen_before_microgate"] is True and receipt["preregistration"]["sha256"] == prereg_sha)
    check(checks, "stop_rule_exact", "stop" in prereg["stop_rule"].lower() and "prior outcome metadata" in prereg["stop_rule"].lower())
    check(checks, "forbids_fabrication", any("zero-fill" in value for value in prereg["forbidden_actions"]))
    check(checks, "forbids_degenerate_evasion", any("zero self-improvement" in value for value in prereg["forbidden_actions"]))

    adapter_sha = sha(HERE / "p5_c3_outcome_free_initializer_v9.py")
    check(checks, "adapter_hash_receipted", adapter_sha == receipt["adapter_implementation"]["sha256"], adapter_sha)
    check(checks, "adapter_fail_closed", receipt["adapter_implementation"]["exit_code"] == 3 and receipt["adapter_implementation"]["fail_closed"] is True)
    check(checks, "one_completed_microgate", receipt["microgates_run"] == 1 and receipt["microgate_type"] == "STATIC_EXACT_BYTE_AND_AST_DATAFLOW_GATE")
    check(checks, "verdict_stop", receipt["verdict"] == "STOP_NO_LAWFUL_SEMANTICS_PRESERVING_OUTCOME_FREE_INITIALIZATION_ADAPTER")
    check(checks, "terminal_exact", receipt["terminal"] == result["terminal"] == TERMINAL)
    check(checks, "terminal_file_exact", (HERE / "TERMINAL_V9.txt").read_text(encoding="utf-8").strip() == TERMINAL)

    adapter = receipt["adapter_result"]
    check(checks, "exact_source_hash", adapter["source_member_sha256"] == "239bc76f0e1b78210b8f7b3757b1082f6ca07db3537d6af50a45bf97709795ed")
    check(checks, "exact_excerpt_hash", adapter["source_excerpt_sha256"] == "5a1d46b8328d7215701fc20959080eddbde029bf2836f97ed9408e8f1ec7edec")
    check(checks, "all_static_gates_true", all(adapter["gates"].values()), adapter["gates"])
    check(checks, "five_required_prior_fields", adapter["required_prior_fields"] == ["accuracy_score", "overall_performance", "total_emptypatch_ids", "total_resolved_ids", "total_unresolved_ids"])
    check(checks, "all_strategies_rejected", len(adapter["strategy_adjudication"]) == 4 and not any(item["admissible"] for item in adapter["strategy_adjudication"]))
    check(checks, "native_semantics_not_preservable", adapter["native_semantics_preservable"] is False)
    check(checks, "no_initializer_materialized", adapter["adapter_materialized"] is False and adapter["initial_directory_materialized"] is False)
    check(checks, "no_performance_fabricated", adapter["prior_performance_fields_created"] is False)
    check(checks, "no_source_or_core_mutation", adapter["dgm_source_mutated"] is False and adapter["lang1_core_mutated"] is False)
    check(checks, "zero_executions", all(value == 0 for value in adapter["executions"].values()), adapter["executions"])

    closure = receipt["field_closure_effect"]
    check(checks, "field_remains_blocking", closure["field"] == "runtime.task_environment" and closure["v8_status"] == closure["v9_status"] == "BLOCKING")
    check(checks, "zero_field_closure", closure["field_instances_closed"] == 0 and closure["c3_blocker_delta"] == 0)
    check(checks, "claims_preserved", receipt["scientific_boundary"]["native_execution_readiness"] == "NOT_ESTABLISHED" and receipt["scientific_boundary"]["performance"] == receipt["scientific_boundary"]["superiority"] == "CANNOT_CHECK")

    for name, expected in EXPECTED_V8.items():
        observed = sha(V8 / name)
        check(checks, f"v8_unchanged_{name}", observed == expected, observed)
    check(checks, "v8_before_after_equal", receipt["predecessor_v8"]["hashes_before"] == receipt["predecessor_v8"]["hashes_after"] and receipt["predecessor_v8"]["mutated"] is False)
    core = receipt["immutable_lang1_core"]
    check(checks, "six_core_members", core["member_count"] == len(core["members"]) == 6)
    check(checks, "lang1_core_preserved", core["mutated"] is False and core["extracted_for_mutation"] is False)
    exclusions = receipt["excluded_prior_outcome_prefixes"]
    check(checks, "excluded_prefixes_absent", exclusions["absent_from_seed"] is True and exclusions["forbidden_members_observed"] == [])
    check(checks, "excluded_payloads_unopened", exclusions["excluded_payload_contents_opened"] is False)

    contradiction = witness["contradiction"]
    check(checks, "witness_no_identity_element", contradiction["identity_element_exposed_by_native_interface"] is False)
    check(checks, "witness_no_solution", contradiction["semantics_preserving_solution_exists"] is False)
    check(checks, "witness_scope_bounded", "exact released source" in witness["scope_boundary"].lower() and "not an impossibility" in witness["scope_boundary"].lower())
    check(checks, "result_no_future_overclaim", result["scientific_boundary"]["future_dgm_design_impossibility_claimed"] is False)

    validation = {
        "schema_version": "orion.p5.c3.outcome-free-successor-validation-receipt.v9",
        "validation_scope": "PACKET_AND_PREDECESSOR_HASHES_ONLY__SCIENTIFIC_MICROGATE_NOT_RERUN",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "json_files_parsed_before_receipt": 4,
        "microgate_rerun": False,
        "dgm_model_benchmark_scorer_outcome_test_executions": "0/0/0/0/0/0",
        "v8_mutated": False,
        "field_instances_closed": 0,
        "c3_blocker_delta": 0,
        "terminal": TERMINAL,
        "checks": checks,
    }
    (HERE / "VALIDATION_RECEIPT_V9.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "checks_passed": len(checks),
        "checks_failed": 0,
        "microgate_rerun": False,
        "field_instances_closed": 0,
        "c3_blocker_delta": 0,
        "terminal": TERMINAL,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
