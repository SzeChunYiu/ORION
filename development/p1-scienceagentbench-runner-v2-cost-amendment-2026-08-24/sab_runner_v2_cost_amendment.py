#!/usr/bin/env python3
"""Fail-closed Runner V2 allocated-accelerator cost amendment.

This module validates metadata only.  It does not retrieve a benchmark, call a
model, read a candidate body, invoke an evaluator, or open an outcome.  The
unmodified Runner V1 remains the sole BILLED_USD route.  This additive module
admits only the prospectively frozen open-weight LUNARC
ALLOCATED_ACCELERATOR_SECONDS route and emits a deterministic generation-side
cost projection whose metric object and per-attempt cost fields are copied
without conversion into the merged Analysis Freeze V1 outcome ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
AMENDMENT_CONTRACT_PATH = ROOT / "RUNNER_V2_COST_AMENDMENT_CONTRACT.json"
AMENDMENT_CONTRACT_SHA256 = "0226a0c8350803e6e47eea846df3871c02c790ababdf3d4cf290461834e0369d"

V1_ROOT = REPO_ROOT / "development/p1-scienceagentbench-runner-v1-2026-08-24"
V1_CONTRACT_PATH = V1_ROOT / "RUNNER_CONTRACT_V1.json"
V1_MODULE_PATH = V1_ROOT / "sab_verified_runner_v1.py"
V1_CONTRACT_SHA256 = "e191540f131b3e7e33b0c040900bea94336dbd0d704b247b547a5c361b6e242f"
V1_MODULE_SHA256 = "15d6f511be9b3b1dbac408cc41812b0f72e1dd7aa700983035438efb8ed416df"

ANALYSIS_ROOT = REPO_ROOT / "development/p1-scienceagentbench-analysis-freeze-v1-2026-08-24"
ANALYSIS_CONTRACT_PATH = ANALYSIS_ROOT / "ANALYSIS_CONTRACT_V1.json"
ANALYSIS_CONTRACT_SHA256 = "0cae220a5b2f73156eda63a01f769dfdecbf8ad1fa16bd0995e3f906cff391d4"

PRODUCTION_SPLIT = "verified"
TASK_IDS = tuple(str(value) for value in range(1, 103))
ARMS = ("RR", "OS", "NR")
ATTEMPTS = (1, 2, 3)

RUN_PLAN_SCHEMA = "orion.p1.scienceagentbench.run-plan.allocated-accelerator-seconds.v2"
LEDGER_SCHEMA = "orion.p1.scienceagentbench.candidate-ledger.allocated-accelerator-seconds.v2"
PROJECTION_SCHEMA = "orion.p1.scienceagentbench.analysis-generation-cost-projection.v2"
SEAL_SCHEMA = "orion.p1.scienceagentbench.candidate-cost-seal-receipt.v2"
V1_RUN_PLAN_SCHEMA = "orion.p1.scienceagentbench.run-plan.v1"

METRIC_ID = "ALLOCATED_ACCELERATOR_SECONDS"
METRIC_UNIT = "accelerator-second"
ALLOCATION_RULE = (
    "FOR_EACH_ATTEMPT_SUM_EXCLUSIVE_ACCELERATOR_COUNT_TIMES_MONOTONIC_GENERATION_"
    "WALL_SECONDS__NO_OVERLAP_DOUBLE_ALLOCATION__THEN_SUM_ALL_ATTEMPTS"
)
BINDING_PHASE = "BEFORE_CANDIDATE_GENERATION_AND_OUTCOME_OPENING"
COST_ACCOUNTING = "ALL_ATTEMPTS_NO_SELECTION"

ROUTE_PROFILE = {
    "route_id": "OPEN_WEIGHT_LUNARC_SLURM_EXCLUSIVE_GPU_V1",
    "site": "LUNARC",
    "scheduler": "SLURM",
    "model_weight_class": "OPEN_WEIGHT",
    "accelerator_kind": "GPU",
}

TIMING_CONSTANTS = {
    "clock_id": "CLOCK_MONOTONIC_RAW",
    "clock_api": "clock_gettime_ns",
    "clock_unit": "nanosecond",
    "clock_semantics": "MONOTONIC_NOT_WALL_CLOCK__NO_REALTIME_SUBSTITUTION",
    "start_boundary": "IMMEDIATELY_BEFORE_FIRST_MODEL_GENERATION_OPERATION",
    "end_boundary": "IMMEDIATELY_AFTER_FINAL_MODEL_GENERATION_OPERATION",
    "elapsed_rule": "monotonic_end_ns-minus-monotonic_start_ns",
    "allocation_scope": "EXCLUSIVE_SLURM_GPU_ALLOCATION_FOR_ONE_TASK_ARM_ATTEMPT",
    "overlap_rule": "NO_OVERLAP_DOUBLE_ALLOCATION",
    "attempt_identity_scope": "EACH_TASK_ARM_ATTEMPT_EXACTLY_ONCE",
}

BASE_RUN_PLAN_FIELDS = {
    "schema_version",
    "split",
    "task_ids",
    "arms",
    "attempts_per_task_arm",
    "bindings",
    "budget_by_arm",
    "cost_accounting",
}
RUN_PLAN_FIELDS = BASE_RUN_PLAN_FIELDS | {
    "amendment_scope",
    "base_runner_contract_sha256",
    "base_runner_module_sha256",
    "analysis_contract_sha256",
    "route_profile",
    "route_profile_binding_sha256",
    "cost_gate_metric",
    "cost_gate_metric_binding_sha256",
    "cost_measurement_binding",
    "cost_measurement_binding_sha256",
}
METRIC_FIELDS = {"metric_id", "unit", "allocation_rule", "binding_phase"}
MEASUREMENT_FIELDS = set(TIMING_CONSTANTS) | {"exclusive_gpu_count_by_arm"}
LEDGER_FIELDS = {
    "schema_version",
    "split",
    "run_plan_sha256",
    "cost_gate_metric",
    "cost_gate_metric_binding_sha256",
    "cost_measurement_binding_sha256",
    "cost_accounting",
    "records",
}
V1_RECORD_FIELDS = {
    "task_id",
    "arm_id",
    "attempt",
    "seed",
    "input_tokens",
    "output_tokens",
    "tool_calls",
    "wall_time_seconds",
    "local_execution_wall_time_seconds",
    "billed_cost_usd",
    "failure",
    "raw_output_sha256",
    "candidate_program_sha256",
}
RECORD_FIELDS = V1_RECORD_FIELDS | {
    "generation_cost_quantity",
    "generation_billed_cost_usd",
    "generation_billed_cost_status",
    "cost_metric_id",
    "cost_gate_metric_binding_sha256",
    "exclusive_gpu_count",
    "timing_provenance_sha256",
    "monotonic_start_ns",
    "monotonic_end_ns",
    "monotonic_elapsed_ns",
    "accelerator_allocation_status",
}
FAILURE_FIELDS = {"status", "stage", "code", "detail_sha256"}
FAILURE_STAGES = {
    "GENERATION",
    "LOCAL_EXECUTION",
    "USAGE_ACCOUNTING",
    "RAW_OUTPUT_SEALING",
}
V1_PLACEHOLDER_FRAGMENTS = {
    "AUTHOR_INPUT_NEEDED",
    "CANNOT_CHECK",
    "TBD",
    "TODO",
    "UNKNOWN",
    "UNBOUND",
}
INTEGER_USAGE_FIELDS = {"input_tokens", "output_tokens", "tool_calls"}
NUMBER_USAGE_FIELDS = {"wall_time_seconds", "local_execution_wall_time_seconds"}
HASH_RECORD_FIELDS = {"raw_output_sha256", "candidate_program_sha256"}
PROJECTION_TOP_LEVEL_FIELDS = {
    "schema_version",
    "analysis_contract_sha256",
    "split",
    "run_plan_sha256",
    "source_candidate_ledger_sha256",
    "cost_gate_metric",
    "cost_gate_metric_binding_sha256",
    "cost_accounting",
    "records",
}
PROJECTION_TASK_FIELDS = {"task_id", "attempt_records"}
PROJECTION_ATTEMPT_FIELDS = {
    "arm_id",
    "attempt",
    "candidate_program_sha256",
    "generation_cost_quantity",
    "generation_billed_cost_usd",
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CANONICAL_UINT_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")
CANONICAL_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$")
FORBIDDEN_PATH_COMPONENTS = {
    "gold_programs",
    "gold_results",
    "eval_programs",
    "evaluation_programs",
    "scoring_rubrics",
    "evaluator_feedback",
    "official_results",
}


class ContractError(ValueError):
    """An input is not admissible under the frozen amendment."""


class DuplicateJsonMemberError(ValueError):
    """JSON repeated a member and therefore has ambiguous identity."""


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise ContractError(f"required file is unreadable: {path}") from exc


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(value))


def _reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonMemberError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _load_json(path: Path | str, label: str) -> dict[str, Any]:
    candidate = Path(path)
    try:
        value = json.loads(
            candidate.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_members,
            parse_constant=_reject_nonfinite_constant,
        )
    except OSError as exc:
        raise ContractError(f"required {label} is unreadable: {candidate}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonMemberError, ValueError) as exc:
        raise ContractError(f"{label} is not unambiguous strict UTF-8 JSON: {candidate}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    return value


def _require_exact_fields(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    observed = set(value)
    if observed != expected:
        raise ContractError(
            f"{label} fields mismatch: missing={sorted(expected-observed)} "
            f"extra={sorted(observed-expected)}"
        )


def _validate_sha256(value: Any, label: str, *, allow_null: bool = False) -> str | None:
    if value is None and allow_null:
        return None
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ContractError(f"{label} must be lowercase 64-hex SHA-256")
    return value


def _validate_canonical_uint(value: Any, label: str, *, positive: bool = False) -> int:
    if not isinstance(value, str) or CANONICAL_UINT_RE.fullmatch(value) is None:
        raise ContractError(f"{label} must be a canonical unsigned decimal string")
    parsed = int(value)
    if positive and parsed == 0:
        raise ContractError(f"{label} must be strictly positive")
    return parsed


def _validate_canonical_decimal(value: Any, label: str) -> Fraction:
    if not isinstance(value, str) or CANONICAL_DECIMAL_RE.fullmatch(value) is None:
        raise ContractError(
            f"{label} must be canonical nonnegative decimal text without sign, "
            "exponent, leading zero, or redundant trailing zero"
        )
    if "." not in value:
        return Fraction(int(value), 1)
    whole, fractional = value.split(".", 1)
    return Fraction(int(whole + fractional), 10 ** len(fractional))


def _ns_to_accelerator_seconds(allocated_ns: int) -> str:
    if allocated_ns < 0:
        raise ContractError("allocated nanoseconds cannot be negative")
    whole, remainder = divmod(allocated_ns, 1_000_000_000)
    if remainder == 0:
        return str(whole)
    fractional = f"{remainder:09d}".rstrip("0")
    return f"{whole}.{fractional}"


def _validate_nonnegative_number(
    value: Any, label: str, *, integer: bool, allow_null: bool
) -> int | float | None:
    if value is None and allow_null:
        return None
    if isinstance(value, bool):
        raise ContractError(f"{label} must be numeric, not Boolean")
    if integer:
        if not isinstance(value, int):
            raise ContractError(f"{label} must be a nonnegative integer")
    elif not isinstance(value, (int, float)):
        raise ContractError(f"{label} must be a nonnegative finite number")
    if not math.isfinite(value) or value < 0:
        raise ContractError(f"{label} must be a nonnegative finite number")
    return value


def _validate_absolute_path(path: Path | str, label: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise ContractError(f"{label} must be an absolute path")
    matched = {part.lower() for part in candidate.parts} & FORBIDDEN_PATH_COMPONENTS
    if matched:
        raise ContractError(f"{label} contains forbidden path component {sorted(matched)[0]}")
    return candidate


def _metric_object() -> dict[str, str]:
    return {
        "metric_id": METRIC_ID,
        "unit": METRIC_UNIT,
        "allocation_rule": ALLOCATION_RULE,
        "binding_phase": BINDING_PHASE,
    }


def _load_and_verify_upstream_contracts() -> dict[str, Any]:
    bindings = (
        (V1_CONTRACT_PATH, V1_CONTRACT_SHA256, "Runner V1 contract"),
        (V1_MODULE_PATH, V1_MODULE_SHA256, "Runner V1 module"),
        (ANALYSIS_CONTRACT_PATH, ANALYSIS_CONTRACT_SHA256, "Analysis Freeze V1 contract"),
        (AMENDMENT_CONTRACT_PATH, AMENDMENT_CONTRACT_SHA256, "Runner V2 amendment contract"),
    )
    for path, expected, label in bindings:
        observed = _sha256_file(path)
        if observed != expected:
            raise ContractError(f"{label} SHA-256 drift: expected={expected} observed={observed}")

    analysis = _load_json(ANALYSIS_CONTRACT_PATH, "Analysis Freeze V1 contract")
    cost_binding = analysis.get("outcome_ledger_contract", {}).get(
        "cost_gate_metric_binding", {}
    )
    supported = cost_binding.get("supported_metrics", {}).get(METRIC_ID)
    if not isinstance(supported, dict):
        raise ContractError("Analysis Freeze V1 no longer supports the allocated metric")
    if supported.get("unit") != METRIC_UNIT or supported.get("allocation_rule") != ALLOCATION_RULE:
        raise ContractError("allocated metric identity disagrees with Analysis Freeze V1")
    if analysis.get("cost_gate", {}).get("zero_denominator") != (
        "CANNOT_CHECK_COST_DENOMINATOR_ZERO"
    ):
        raise ContractError("Analysis Freeze V1 zero-denominator rule drift")
    return analysis


def _load_v1_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("orion_p1_sab_runner_v1", V1_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ContractError("Runner V1 module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_route_profile(plan: Mapping[str, Any]) -> None:
    route = plan["route_profile"]
    _require_exact_fields(route, set(ROUTE_PROFILE), "route_profile")
    if route != ROUTE_PROFILE:
        raise ContractError("route_profile must equal the frozen open-weight LUNARC route")
    if plan["route_profile_binding_sha256"] != _canonical_sha256(route):
        raise ContractError("route_profile_binding_sha256 mismatch")


def _validate_cost_metric(plan: Mapping[str, Any]) -> None:
    metric = plan["cost_gate_metric"]
    _require_exact_fields(metric, METRIC_FIELDS, "cost_gate_metric")
    if metric != _metric_object():
        if isinstance(metric, dict) and metric.get("metric_id") == "BILLED_USD":
            raise ContractError(
                "BILLED_USD is not reimplemented by this amendment; use unchanged Runner V1"
            )
        raise ContractError("cost_gate_metric drift or unsupported fallback")
    if plan["cost_gate_metric_binding_sha256"] != _canonical_sha256(metric):
        raise ContractError("cost_gate_metric_binding_sha256 mismatch")


def _validate_measurement_binding(plan: Mapping[str, Any]) -> dict[str, int]:
    binding = plan["cost_measurement_binding"]
    _require_exact_fields(binding, MEASUREMENT_FIELDS, "cost_measurement_binding")
    for field, expected in TIMING_CONSTANTS.items():
        if binding[field] != expected:
            raise ContractError(f"cost_measurement_binding {field} drift")
    counts = binding["exclusive_gpu_count_by_arm"]
    _require_exact_fields(counts, set(ARMS), "exclusive_gpu_count_by_arm")
    parsed = {
        arm: _validate_canonical_uint(
            counts[arm], f"exclusive_gpu_count_by_arm.{arm}", positive=True
        )
        for arm in ARMS
    }
    if len(set(parsed.values())) != 1:
        raise ContractError("RR/OS/NR exclusive GPU counts must be exactly identical")
    if plan["cost_measurement_binding_sha256"] != _canonical_sha256(binding):
        raise ContractError("cost_measurement_binding_sha256 mismatch")
    return parsed


def _v1_plan_view(plan: Mapping[str, Any]) -> dict[str, Any]:
    view = {field: plan[field] for field in BASE_RUN_PLAN_FIELDS}
    view["schema_version"] = V1_RUN_PLAN_SCHEMA
    return view


def _validate_run_plan(
    plan: Mapping[str, Any], *, expected_task_ids: Sequence[str] = TASK_IDS
) -> dict[str, Any]:
    _load_and_verify_upstream_contracts()
    _require_exact_fields(plan, RUN_PLAN_FIELDS, "allocated cost run plan")
    if plan["schema_version"] != RUN_PLAN_SCHEMA:
        raise ContractError("allocated cost run plan schema_version mismatch")
    if plan["amendment_scope"] != (
        "ALLOCATED_ACCELERATOR_SECONDS_ONLY__BILLED_USD_REMAINS_UNCHANGED_RUNNER_V1"
    ):
        raise ContractError("amendment_scope mismatch")
    expected_hashes = {
        "base_runner_contract_sha256": V1_CONTRACT_SHA256,
        "base_runner_module_sha256": V1_MODULE_SHA256,
        "analysis_contract_sha256": ANALYSIS_CONTRACT_SHA256,
    }
    for field, expected in expected_hashes.items():
        if plan[field] != expected:
            raise ContractError(f"{field} drift")

    v1 = _load_v1_module()
    try:
        v1._validate_run_plan(_v1_plan_view(plan), expected_task_ids=expected_task_ids)
    except v1.ContractError as exc:
        raise ContractError(f"unchanged Runner V1 run-plan invariant failed: {exc}") from exc
    _validate_route_profile(plan)
    _validate_cost_metric(plan)
    _validate_measurement_binding(plan)
    return dict(plan)


def validate_run_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a production-size prospectively frozen allocated-cost run plan."""

    return _validate_run_plan(plan, expected_task_ids=TASK_IDS)


def _validate_failure(value: Any, label: str) -> None:
    _require_exact_fields(value, FAILURE_FIELDS, label)
    if value["status"] != "CANNOT_CHECK":
        raise ContractError(f"{label}.status must equal CANNOT_CHECK")
    if value["stage"] not in FAILURE_STAGES:
        raise ContractError(f"{label}.stage invalid")
    code = value["code"]
    if not isinstance(code, str) or not code.strip():
        raise ContractError(f"{label}.code must be nonempty bound text")
    matched = sorted(
        fragment for fragment in V1_PLACEHOLDER_FRAGMENTS if fragment in code.upper()
    )
    if matched:
        raise ContractError(f"{label}.code is unbound: contains {matched[0]}")
    _validate_sha256(value["detail_sha256"], f"{label}.detail_sha256")


def _validate_billed_usd(record: Mapping[str, Any], label: str) -> None:
    status = record["generation_billed_cost_status"]
    legacy_value = record["billed_cost_usd"]
    analysis_value = record["generation_billed_cost_usd"]
    if status == "AVAILABLE":
        legacy_parsed = _validate_canonical_decimal(legacy_value, f"{label}.billed_cost_usd")
        analysis_parsed = _validate_canonical_decimal(
            analysis_value, f"{label}.generation_billed_cost_usd"
        )
        if legacy_parsed != analysis_parsed or legacy_value != analysis_value:
            raise ContractError(f"{label} billed USD copies must be byte-identical")
    elif status == "CANNOT_CHECK":
        if legacy_value is not None or analysis_value is not None:
            raise ContractError(
                f"{label} unavailable billed USD must remain null; zero imputation forbidden"
            )
    else:
        raise ContractError(
            f"{label}.generation_billed_cost_status must be AVAILABLE or CANNOT_CHECK"
        )


def _validate_candidate_ledger(
    ledger: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    expected_task_ids: Sequence[str],
    expected_run_plan_sha256: str,
) -> tuple[dict[tuple[str, str, int], dict[str, Any]], dict[str, int], dict[str, int]]:
    _require_exact_fields(ledger, LEDGER_FIELDS, "allocated candidate ledger")
    if ledger["schema_version"] != LEDGER_SCHEMA:
        raise ContractError("allocated candidate ledger schema_version mismatch")
    if ledger["split"] != PRODUCTION_SPLIT:
        raise ContractError("allocated candidate ledger split must equal verified")
    if ledger["run_plan_sha256"] != expected_run_plan_sha256:
        raise ContractError("candidate ledger run_plan_sha256 mismatch")
    if ledger["cost_gate_metric"] != plan["cost_gate_metric"]:
        raise ContractError("candidate ledger cost_gate_metric drift")
    if ledger["cost_gate_metric_binding_sha256"] != plan["cost_gate_metric_binding_sha256"]:
        raise ContractError("candidate ledger cost metric binding drift")
    if ledger["cost_measurement_binding_sha256"] != plan["cost_measurement_binding_sha256"]:
        raise ContractError("candidate ledger timing provenance binding drift")
    if ledger["cost_accounting"] != COST_ACCOUNTING:
        raise ContractError("candidate ledger must retain all attempts with no selection")
    records = ledger["records"]
    if not isinstance(records, list):
        raise ContractError("candidate ledger records must be a list")

    expected = {
        (task_id, arm, attempt)
        for task_id in expected_task_ids
        for arm in ARMS
        for attempt in ATTEMPTS
    }
    by_tuple: dict[tuple[str, str, int], dict[str, Any]] = {}
    gpu_counts = _validate_measurement_binding(plan)
    seed_schedule = plan["bindings"]["seed_schedule"]
    timing_hash = plan["cost_measurement_binding_sha256"]
    metric_hash = plan["cost_gate_metric_binding_sha256"]
    cannot_check_candidates = 0
    billed_counts = {arm: 0 for arm in ARMS}
    allocated_ns_totals = {arm: 0 for arm in ARMS}

    for index, record in enumerate(records):
        label = f"candidate record {index}"
        _require_exact_fields(record, RECORD_FIELDS, label)
        task_id = record["task_id"]
        if not isinstance(task_id, str) or task_id not in expected_task_ids:
            raise ContractError(f"{label}.task_id must be a canonical frozen decimal string")
        arm = record["arm_id"]
        if arm not in ARMS:
            raise ContractError(f"{label}.arm_id invalid")
        attempt = record["attempt"]
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt not in ATTEMPTS:
            raise ContractError(f"{label}.attempt must be integer 1, 2, or 3")
        key = (task_id, arm, attempt)
        if key in by_tuple:
            raise ContractError(f"duplicate candidate tuple {key}")
        if record["seed"] != seed_schedule[str(attempt)] or isinstance(record["seed"], bool):
            raise ContractError(f"{label}.seed does not match the paired schedule")

        for field in INTEGER_USAGE_FIELDS:
            _validate_nonnegative_number(record[field], f"{label}.{field}", integer=True, allow_null=True)
        for field in NUMBER_USAGE_FIELDS:
            _validate_nonnegative_number(record[field], f"{label}.{field}", integer=False, allow_null=True)
        budget = plan["budget_by_arm"][arm]
        caps = {
            "input_tokens": "total_input_token_cap",
            "output_tokens": "total_output_token_cap",
            "tool_calls": "tool_call_cap",
            "wall_time_seconds": "wall_time_seconds_cap",
            "local_execution_wall_time_seconds": "local_execution_seconds_cap",
        }
        for usage_field, cap_field in caps.items():
            value = record[usage_field]
            if value is not None and value > budget[cap_field]:
                raise ContractError(f"{label}.{usage_field} exceeds matched cap")
        for field in HASH_RECORD_FIELDS:
            _validate_sha256(record[field], f"{label}.{field}", allow_null=True)

        failure = record["failure"]
        if failure is None:
            required = INTEGER_USAGE_FIELDS | NUMBER_USAGE_FIELDS | HASH_RECORD_FIELDS
            missing = sorted(field for field in required if record[field] is None)
            if missing:
                raise ContractError(f"{label} successful candidate has null fields: {missing}")
        else:
            cannot_check_candidates += 1
            _validate_failure(failure, f"{label}.failure")

        if record["cost_metric_id"] != METRIC_ID:
            raise ContractError(f"{label} metric identity drift/fallback")
        if record["cost_gate_metric_binding_sha256"] != metric_hash:
            raise ContractError(f"{label} cost metric binding drift")
        if record["timing_provenance_sha256"] != timing_hash:
            raise ContractError(f"{label} monotonic timing provenance drift")
        if record["accelerator_allocation_status"] != "EXCLUSIVE_NO_OVERLAP_CONFIRMED":
            raise ContractError(f"{label} lacks exclusive no-overlap allocation confirmation")

        gpu_count = _validate_canonical_uint(
            record["exclusive_gpu_count"], f"{label}.exclusive_gpu_count", positive=True
        )
        if gpu_count != gpu_counts[arm]:
            raise ContractError(f"{label} exclusive GPU count drift")
        start_ns = _validate_canonical_uint(record["monotonic_start_ns"], f"{label}.monotonic_start_ns")
        end_ns = _validate_canonical_uint(record["monotonic_end_ns"], f"{label}.monotonic_end_ns")
        elapsed_ns = _validate_canonical_uint(record["monotonic_elapsed_ns"], f"{label}.monotonic_elapsed_ns")
        if end_ns < start_ns:
            raise ContractError(f"{label} monotonic end precedes start")
        if elapsed_ns != end_ns - start_ns:
            raise ContractError(f"{label} monotonic elapsed is not exact end-minus-start")
        allocated_ns = gpu_count * elapsed_ns
        expected_quantity = _ns_to_accelerator_seconds(allocated_ns)
        _validate_canonical_decimal(
            record["generation_cost_quantity"], f"{label}.generation_cost_quantity"
        )
        if record["generation_cost_quantity"] != expected_quantity:
            raise ContractError(
                f"{label} generation_cost_quantity must equal exact GPU-count times elapsed"
            )
        _validate_billed_usd(record, label)
        if record["generation_billed_cost_status"] == "AVAILABLE":
            billed_counts[arm] += 1
        allocated_ns_totals[arm] += allocated_ns
        by_tuple[key] = dict(record)

    observed = set(by_tuple)
    if observed != expected or len(records) != len(expected):
        raise ContractError(
            "candidate tuples must equal all 918 task x arm x attempt tuples: "
            f"missing={len(expected-observed)} extra={len(observed-expected)}"
        )

    # Analysis selects the stronger comparator only after outcomes.  Requiring
    # both prospective comparator totals to be positive guarantees that the
    # later selected denominator cannot be zero without opening any outcome.
    for arm in ("OS", "NR"):
        if allocated_ns_totals[arm] == 0:
            raise ContractError(
                f"{arm} allocated-cost total is zero; strongest-comparator denominator cannot be certified"
            )
    return by_tuple, billed_counts, allocated_ns_totals


def _build_projection(
    by_tuple: Mapping[tuple[str, str, int], Mapping[str, Any]],
    plan: Mapping[str, Any],
    *,
    expected_task_ids: Sequence[str],
    candidate_ledger_sha256: str,
    run_plan_sha256: str,
) -> dict[str, Any]:
    records = []
    for task_id in expected_task_ids:
        attempt_records = []
        for arm in ARMS:
            for attempt in ATTEMPTS:
                source = by_tuple[(task_id, arm, attempt)]
                attempt_records.append(
                    {
                        "arm_id": arm,
                        "attempt": attempt,
                        "candidate_program_sha256": source["candidate_program_sha256"],
                        "generation_cost_quantity": source["generation_cost_quantity"],
                        "generation_billed_cost_usd": source["generation_billed_cost_usd"],
                    }
                )
        records.append({"task_id": task_id, "attempt_records": attempt_records})
    return {
        "schema_version": PROJECTION_SCHEMA,
        "analysis_contract_sha256": ANALYSIS_CONTRACT_SHA256,
        "split": PRODUCTION_SPLIT,
        "run_plan_sha256": run_plan_sha256,
        "source_candidate_ledger_sha256": candidate_ledger_sha256,
        "cost_gate_metric": dict(plan["cost_gate_metric"]),
        "cost_gate_metric_binding_sha256": plan["cost_gate_metric_binding_sha256"],
        "cost_accounting": COST_ACCOUNTING,
        "records": records,
    }


def _validate_projection_against_analysis_contract(
    projection: Mapping[str, Any], analysis_contract: Mapping[str, Any]
) -> None:
    _require_exact_fields(projection, PROJECTION_TOP_LEVEL_FIELDS, "emitted cost projection")
    outcome_contract = analysis_contract["outcome_ledger_contract"]
    outcome_top = set(outcome_contract["required_top_level_fields"])
    for required in (
        "cost_gate_metric",
        "cost_gate_metric_binding_sha256",
        "cost_accounting",
        "records",
    ):
        if required not in outcome_top:
            raise ContractError(f"Analysis Freeze V1 lost required generation field {required}")
    analysis_attempt_fields = set(
        outcome_contract["official_task_record"]["attempt_records"]["required_fields"]
    )
    if not PROJECTION_ATTEMPT_FIELDS.issubset(analysis_attempt_fields):
        raise ContractError("emitted attempt projection fields drift from Analysis Freeze V1")
    if projection["cost_gate_metric"] != _metric_object():
        raise ContractError("emitted metric object drift")
    if projection["cost_gate_metric_binding_sha256"] != _canonical_sha256(
        projection["cost_gate_metric"]
    ):
        raise ContractError("emitted metric binding mismatch")
    records = projection["records"]
    if not isinstance(records, list) or len(records) != len(TASK_IDS):
        raise ContractError("emitted projection must contain exactly 102 task records")
    for task_index, task in enumerate(records):
        _require_exact_fields(task, PROJECTION_TASK_FIELDS, f"emitted task {task_index}")
        attempts = task["attempt_records"]
        if not isinstance(attempts, list) or len(attempts) != 9:
            raise ContractError(f"emitted task {task_index} must contain exactly 9 attempts")
        for attempt_index, attempt in enumerate(attempts):
            _require_exact_fields(
                attempt,
                PROJECTION_ATTEMPT_FIELDS,
                f"emitted task {task_index} attempt {attempt_index}",
            )


def _prepare_seal(
    run_plan_path: Path | str,
    candidate_ledger_path: Path | str,
    *,
    expected_task_ids: Sequence[str] = TASK_IDS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    analysis_contract = _load_and_verify_upstream_contracts()
    plan_path = _validate_absolute_path(run_plan_path, "run-plan path")
    ledger_path = _validate_absolute_path(candidate_ledger_path, "candidate-ledger path")
    run_plan_sha256 = _sha256_file(plan_path)
    candidate_ledger_sha256 = _sha256_file(ledger_path)
    plan = _load_json(plan_path, "allocated cost run plan")
    _validate_run_plan(plan, expected_task_ids=expected_task_ids)
    ledger = _load_json(ledger_path, "allocated candidate ledger")
    by_tuple, billed_counts, allocated_ns_totals = _validate_candidate_ledger(
        ledger,
        plan,
        expected_task_ids=expected_task_ids,
        expected_run_plan_sha256=run_plan_sha256,
    )
    projection = _build_projection(
        by_tuple,
        plan,
        expected_task_ids=expected_task_ids,
        candidate_ledger_sha256=candidate_ledger_sha256,
        run_plan_sha256=run_plan_sha256,
    )
    # Production projection shape is fixed at 102/918.  Synthetic reduced task
    # sets are admitted only to private helper tests and do not receive a seal.
    if tuple(expected_task_ids) == TASK_IDS:
        _validate_projection_against_analysis_contract(projection, analysis_contract)
    receipt = {
        "schema_version": SEAL_SCHEMA,
        "authority": "GENERATION_COST_METADATA_SEAL_ONLY__NO_OUTCOME_EVALUATOR_OR_SCIENTIFIC_AUTHORITY",
        "status": "ALLOCATED_ACCELERATOR_COST_LEDGER_SEALED__OUTCOMES_NOT_OPENED",
        "base_runner_contract_sha256": V1_CONTRACT_SHA256,
        "base_runner_module_sha256": V1_MODULE_SHA256,
        "analysis_contract_sha256": ANALYSIS_CONTRACT_SHA256,
        "run_plan_sha256": run_plan_sha256,
        "candidate_ledger_sha256": candidate_ledger_sha256,
        "emitted_cost_projection_canonical_sha256": _canonical_sha256(projection),
        "cost_gate_metric": dict(plan["cost_gate_metric"]),
        "cost_gate_metric_binding_sha256": plan["cost_gate_metric_binding_sha256"],
        "cost_measurement_binding_sha256": plan["cost_measurement_binding_sha256"],
        "candidate_record_count": len(by_tuple),
        "task_record_count": len(expected_task_ids),
        "attempt_records_per_task": len(ARMS) * len(ATTEMPTS),
        "cost_accounting": COST_ACCOUNTING,
        "arm_generation_cost_totals": {
            arm: _ns_to_accelerator_seconds(allocated_ns_totals[arm]) for arm in ARMS
        },
        "generation_billed_usd_availability_count_by_arm": billed_counts,
        "generation_billed_usd_unavailable_status": "CANNOT_CHECK__NULL_PRESERVED__ZERO_NOT_IMPUTED",
        "comparator_denominator_precondition": "OS_AND_NR_TOTALS_BOTH_STRICTLY_POSITIVE_BEFORE_OUTCOME_SELECTION",
        "billed_usd_route": "UNCHANGED_RUNNER_V1__NOT_REIMPLEMENTED",
        "candidate_bodies_opened": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }
    return projection, receipt


def prepare_production_seal(
    run_plan_path: Path | str, candidate_ledger_path: Path | str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate all 918 receipts and return an analysis-side cost projection and seal."""

    return _prepare_seal(
        run_plan_path, candidate_ledger_path, expected_task_ids=TASK_IDS
    )


def _write_canonical_json(path: Path | str, value: Mapping[str, Any]) -> str:
    destination = _validate_absolute_path(path, "output path")
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = _canonical_json_bytes(value) + b"\n"
    destination.write_bytes(payload)
    return _sha256_bytes(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the allocated-accelerator Runner V2 amendment and emit a "
            "generation-side Analysis Freeze V1 cost projection. No task is run."
        )
    )
    parser.add_argument("--run-plan", required=True, type=Path)
    parser.add_argument("--candidate-ledger", required=True, type=Path)
    parser.add_argument("--output-ledger", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        projection, receipt = prepare_production_seal(
            args.run_plan, args.candidate_ledger
        )
        emitted_file_sha256 = _write_canonical_json(args.output_ledger, projection)
        receipt["emitted_cost_projection_file_sha256"] = emitted_file_sha256
        _write_canonical_json(args.output_receipt, receipt)
    except ContractError as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
