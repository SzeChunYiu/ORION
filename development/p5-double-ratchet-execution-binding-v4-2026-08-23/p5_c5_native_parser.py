#!/usr/bin/env python3
"""Outcome-blind parser for the Double Ratchet metric-only C5 arm.

The parser consumes the *development* result envelope emitted by the exact
``scripts/run_metric_evo.py`` entrypoint plus a host-produced evaluator-only
guard receipt.  It never emits development agreement values and it is not a
protected scorer.  A protected panel or score is forbidden input.

``--self-smoke`` uses only in-memory, authored, native-shaped objects.  It does
not load a benchmark, a released result, a task, or a protected outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ARM_ID = "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY"
SCHEMA_VERSION = "orion.p5.c5.double-ratchet-native-terminal.v4"
SOURCE_COMMIT = "0f14e910d361196422d9b938f45280919952d4fd"
SUPPORTED_INPUT_CLASS = "EVALUATOR_REPAIR"
UNRESOLVED = "UNRESOLVED"
EXPECTED_SOLVER_SHA256 = "089707d2a543c2fcf43be661a058647a0326e5402eb360156ed8baaba9de78ed"
EXPECTED_PROMPTS_SHA256 = "08611d2077e44267dbef415e26d514971ee36d268e2938e716d4b12c4eafa8f9"


class NativeParseError(ValueError):
    """Fail-closed malformed native/guard input."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _is_hex64(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(ch in "0123456789abcdef" for ch in value)


def _guard_failure(guard: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "terminal_class": UNRESOLVED,
        "native_terminal": "DOUBLE_RATCHET_GUARD_FAILURE",
        "reason": reason,
        "evaluator_artifact_sha256": None,
        "solver_bytes_preserved": False,
        "performance": "CANNOT_CHECK",
        "protected_outcome_accessed": False,
    }


def parse_native(
    result: dict[str, Any],
    metric_db_bytes: bytes,
    guard: dict[str, Any],
) -> dict[str, Any]:
    """Map a native development result to the sole C5 actionable class.

    The function intentionally does not return ``final_locked_agreement``,
    per-round agreement, combined score, development score, or any metric
    fixture value.  Those quantities are neither protected performance nor P5
    performance, and are irrelevant to this terminal adapter.
    """
    if not isinstance(result, dict) or not isinstance(guard, dict):
        raise NativeParseError("native result and guard must be objects")
    if guard.get("schema_version") != "orion.p5.c5.evaluator-only-guard.v4":
        return _guard_failure(guard, "GUARD_SCHEMA_MISMATCH")
    if guard.get("arm_id") != ARM_ID:
        return _guard_failure(guard, "GUARD_ARM_MISMATCH")
    if guard.get("source_commit") != SOURCE_COMMIT:
        return _guard_failure(guard, "SOURCE_COMMIT_MISMATCH")
    if guard.get("protected_panel_used") is not False:
        return _guard_failure(guard, "PROTECTED_PANEL_FORBIDDEN_DURING_EVOLUTION")
    if guard.get("protected_score_visible") is not False:
        return _guard_failure(guard, "PROTECTED_SCORE_VISIBILITY_FORBIDDEN")

    exit_code = guard.get("native_exit_code")
    if exit_code == 124:
        return {
            **_guard_failure(guard, "WALLCLOCK_TIMEOUT"),
            "native_terminal": "TIMEOUT",
        }
    if exit_code != 0:
        return {
            **_guard_failure(guard, "NATIVE_NONZERO_EXIT"),
            "native_terminal": "ERROR",
        }

    if result.get("loop") != "metric_evo":
        return _guard_failure(guard, "NOT_METRIC_EVO")
    params = result.get("params")
    native_result = result.get("result")
    if not isinstance(params, dict) or not isinstance(native_result, dict):
        return _guard_failure(guard, "NATIVE_ENVELOPE_INCOMPLETE")
    if params.get("naive") is not False or params.get("arm") != "anchored":
        return _guard_failure(guard, "ANCHORED_VALIDITY_GUARD_DISABLED")
    if guard.get("golden_diff_selectable") is not False:
        return _guard_failure(guard, "ANCHOR_ONLY_OPERATION_BECAME_SELECTABLE")

    expr = native_result.get("final_metric_expr")
    history = native_result.get("evolution_history")
    if not isinstance(expr, str) or not expr.strip():
        return {
            **_guard_failure(guard, "NO_FINAL_METRIC_EXPRESSION"),
            "native_terminal": "EMPTY",
        }
    if not isinstance(history, list) or not history:
        return {
            **_guard_failure(guard, "NO_EVOLUTION_HISTORY"),
            "native_terminal": "EMPTY",
        }
    if not metric_db_bytes:
        return _guard_failure(guard, "METRIC_DB_EMPTY")

    solver_pre = guard.get("solver_sha256_pre")
    solver_post = guard.get("solver_sha256_post")
    prompts_pre = guard.get("prompts_sha256_pre")
    prompts_post = guard.get("prompts_sha256_post")
    task_pre = guard.get("task_tree_sha256_pre")
    task_post = guard.get("task_tree_sha256_post")
    if (
        solver_pre != EXPECTED_SOLVER_SHA256
        or solver_post != EXPECTED_SOLVER_SHA256
        or prompts_pre != EXPECTED_PROMPTS_SHA256
        or prompts_post != EXPECTED_PROMPTS_SHA256
    ):
        return _guard_failure(guard, "FROZEN_SOLVER_OR_PROMPT_BYTES_CHANGED")
    if not (_is_hex64(task_pre) and task_pre == task_post):
        return _guard_failure(guard, "TASK_BYTES_CHANGED_OR_UNATTESTED")
    if guard.get("skill_bank_empty") is not True:
        return _guard_failure(guard, "SKILL_BANK_NOT_EMPTY")
    if guard.get("evaluator_only_mutation") is not True:
        return _guard_failure(guard, "NON_EVALUATOR_MUTATION")
    writes = guard.get("write_paths")
    if not isinstance(writes, list) or any(
        not isinstance(path, str) or not path.startswith("results/metric_evo/")
        for path in writes
    ):
        return _guard_failure(guard, "WRITE_SURFACE_VIOLATION")
    if guard.get("development_validity_gate") != "PASSED":
        return _guard_failure(guard, "DEVELOPMENT_VALIDITY_NOT_PASSED")
    if guard.get("input_native_class") != SUPPORTED_INPUT_CLASS:
        return _guard_failure(guard, "INPUT_CLASS_NOT_EVALUATOR_REPAIR")

    result_digest = sha256_bytes(canonical_bytes(result))
    db_digest = sha256_bytes(metric_db_bytes)
    artifact_digest = sha256_bytes(
        (SOURCE_COMMIT + "\n" + result_digest + "\n" + db_digest + "\n").encode()
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "terminal_class": SUPPORTED_INPUT_CLASS,
        "native_terminal": "SUCCESS",
        "reason": "EVALUATOR_ONLY_GUARDS_AND_DEVELOPMENT_VALIDITY_PASSED",
        "evaluator_artifact_sha256": artifact_digest,
        "native_result_sha256": result_digest,
        "metric_db_sha256": db_digest,
        "solver_bytes_preserved": True,
        "performance": "CANNOT_CHECK",
        "protected_outcome_accessed": False,
    }


def _synthetic_native() -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    task_hash = "4" * 64
    result = {
        "loop": "metric_evo",
        "dataset": "AUTHORED_NATIVE_SHAPE_ONLY",
        "config": {
            "model_id": "SYNTHETIC_MODEL_ID",
            "fallback_model_id": None,
            "region": "SYNTHETIC_REGION",
            "parallelism": 1,
        },
        "params": {
            "naive": False,
            "arm": "anchored",
            "rounds": 1,
            "rounds_used": 1,
            "stopped_early": False,
            "seed": 0,
        },
        "result": {
            "final_metric_expr": "root_ok AND synthetic_detector",
            "final_locked_agreement": None,
            "elites": [],
            "evolution_history": [
                {
                    "round": 0,
                    "best_expr": "root_ok AND synthetic_detector",
                    "locked_report_agreement": None,
                }
            ],
            "synthesized_ops_total": 0,
            "store": "results/metric_evo/synthetic/metric.db",
            "audit_events": 1,
        },
        "note": "AUTHORED_NATIVE_SHAPE_ONLY; NOT PERFORMANCE",
    }
    guard = {
        "schema_version": "orion.p5.c5.evaluator-only-guard.v4",
        "arm_id": ARM_ID,
        "source_commit": SOURCE_COMMIT,
        "native_exit_code": 0,
        "solver_sha256_pre": EXPECTED_SOLVER_SHA256,
        "solver_sha256_post": EXPECTED_SOLVER_SHA256,
        "prompts_sha256_pre": EXPECTED_PROMPTS_SHA256,
        "prompts_sha256_post": EXPECTED_PROMPTS_SHA256,
        "task_tree_sha256_pre": task_hash,
        "task_tree_sha256_post": task_hash,
        "skill_bank_empty": True,
        "evaluator_only_mutation": True,
        "development_validity_gate": "PASSED",
        "golden_diff_selectable": False,
        "input_native_class": SUPPORTED_INPUT_CLASS,
        "write_paths": [
            "results/metric_evo/synthetic/metric.db",
            "results/metric_evo/synthetic/result.json",
        ],
        "protected_panel_used": False,
        "protected_score_visible": False,
    }
    return result, b"SYNTHETIC SQLITE-SHAPED BYTES; NOT A METRIC OR SCORE", guard


def self_smoke() -> dict[str, Any]:
    result, metric_bytes, guard = _synthetic_native()
    cases: list[dict[str, Any]] = []

    positive = parse_native(result, metric_bytes, guard)
    cases.append({"id": "S1_SYNTHETIC_GUARDED_SUCCESS", "terminal": positive["terminal_class"]})

    timeout_guard = dict(guard, native_exit_code=124)
    timeout = parse_native(result, metric_bytes, timeout_guard)
    cases.append({"id": "S2_TIMEOUT", "terminal": timeout["terminal_class"]})

    solver_guard = dict(guard, solver_sha256_post="0" * 64)
    solver = parse_native(result, metric_bytes, solver_guard)
    cases.append({"id": "S3_SOLVER_MUTATION", "terminal": solver["terminal_class"]})

    wrong_class_guard = dict(guard, input_native_class="MODEL_REPAIR")
    wrong = parse_native(result, metric_bytes, wrong_class_guard)
    cases.append({"id": "S4_UNSUPPORTED_INPUT_CLASS", "terminal": wrong["terminal_class"]})

    protected_guard = dict(guard, protected_panel_used=True)
    protected = parse_native(result, metric_bytes, protected_guard)
    cases.append({"id": "S5_PROTECTED_PANEL_REFUSAL", "terminal": protected["terminal_class"]})

    naive_result = json.loads(json.dumps(result))
    naive_result["params"]["naive"] = True
    naive_result["params"]["arm"] = "naive"
    naive = parse_native(naive_result, metric_bytes, guard)
    cases.append({"id": "S6_NAIVE_ARM_REFUSAL", "terminal": naive["terminal_class"]})

    expected = [SUPPORTED_INPUT_CLASS, UNRESOLVED, UNRESOLVED, UNRESOLVED, UNRESOLVED, UNRESOLVED]
    passed = [case["terminal"] for case in cases] == expected
    return {
        "schema_version": "orion.p5.c5.double-ratchet-parser-smoke.v4",
        "arm_id": ARM_ID,
        "synthetic_cases": len(cases),
        "synthetic_cases_passed": len(cases) if passed else 0,
        "cases": cases,
        "raw_native_singleton_licences": 0,
        "substantive_p5_cases": 0,
        "performance": "CANNOT_CHECK",
        "protected_outcome_accessed": False,
        "terminal": "SYNTHETIC_CONFORMANCE_ONLY" if passed else "SYNTHETIC_CONFORMANCE_FAILURE",
    }


def _load_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeParseError(f"{label} is unreadable or invalid JSON") from exc
    if not isinstance(value, dict):
        raise NativeParseError(f"{label} must be an object")
    return value, raw


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-smoke", action="store_true")
    ap.add_argument("--result-json", type=Path)
    ap.add_argument("--metric-db", type=Path)
    ap.add_argument("--guard-json", type=Path)
    args = ap.parse_args(argv)

    if args.self_smoke:
        receipt = self_smoke()
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if receipt["terminal"] == "SYNTHETIC_CONFORMANCE_ONLY" else 2

    if args.result_json is None or args.metric_db is None or args.guard_json is None:
        ap.error("--result-json, --metric-db and --guard-json are required outside --self-smoke")
    try:
        result, _ = _load_object(args.result_json, "result_json")
        guard, _ = _load_object(args.guard_json, "guard_json")
        metric_bytes = args.metric_db.read_bytes()
        parsed = parse_native(result, metric_bytes, guard)
        print(json.dumps(parsed, indent=2, sort_keys=True))
        return 0 if parsed["terminal_class"] in {SUPPORTED_INPUT_CLASS, UNRESOLVED} else 2
    except (OSError, NativeParseError) as exc:
        print(f"P5_C5_NATIVE_PARSE_REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
