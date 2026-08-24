#!/usr/bin/env python3
"""Fail-closed, network-free contract runner for verified ScienceAgentBench.

This module validates and seals generation metadata, then emits an inert official
 evaluator argv receipt.  It deliberately has no model, network, shell,
subprocess, Docker, Parquet-reader, evaluator-import, or outcome-analysis path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PRODUCTION_SPLIT = "verified"
PRODUCTION_PARQUET_SHA256 = (
    "c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147"
)
PRODUCTION_MASK_MANIFEST_SHA256 = (
    "442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758"
)
OFFICIAL_SOURCE_COMMIT = "c26e151ed601ba109dc4d35e057ff8e73fec469d"
TASK_IDS = tuple(str(value) for value in range(1, 103))
ARMS = ("RR", "OS", "NR")
ATTEMPTS = (1, 2, 3)
OFFICIAL_EVALUATOR_MODULE = "evaluation.harness.run_evaluation"

RUN_PLAN_SCHEMA = "orion.p1.scienceagentbench.run-plan.v1"
LEDGER_SCHEMA = "orion.p1.scienceagentbench.candidate-ledger.v1"
SEAL_SCHEMA = "orion.p1.scienceagentbench.candidate-seal-receipt.v1"
COMMAND_SCHEMA = "orion.p1.scienceagentbench.evaluator-command-receipt.v1"
INPUT_SCHEMA = "orion.p1.scienceagentbench.input-binding-receipt.v1"

RUN_PLAN_FIELDS = {
    "schema_version",
    "split",
    "task_ids",
    "arms",
    "attempts_per_task_arm",
    "bindings",
    "budget_by_arm",
    "cost_accounting",
}
BINDING_FIELDS = {
    "model_id",
    "provider",
    "tokenizer_revision",
    "prompt_bundle_sha256_by_arm",
    "seed_schedule",
    "provider_seed_capability",
    "model_parameters_sha256",
    "tool_policy_sha256",
    "generation_runtime_manifest_sha256",
    "credential_route_sha256",
    "credential_route_status",
}
BUDGET_FIELDS = {
    "total_input_token_cap",
    "total_output_token_cap",
    "tool_call_cap",
    "wall_time_seconds_cap",
    "local_execution_seconds_cap",
    "final_candidates_per_attempt",
}
LEDGER_FIELDS = {
    "schema_version",
    "split",
    "run_plan_sha256",
    "cost_accounting",
    "records",
}
RECORD_FIELDS = {
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
FAILURE_FIELDS = {"status", "stage", "code", "detail_sha256"}
FAILURE_STAGES = {
    "GENERATION",
    "LOCAL_EXECUTION",
    "USAGE_ACCOUNTING",
    "RAW_OUTPUT_SEALING",
}
INTEGER_USAGE_FIELDS = {"input_tokens", "output_tokens", "tool_calls"}
NUMBER_USAGE_FIELDS = {
    "wall_time_seconds",
    "local_execution_wall_time_seconds",
    "billed_cost_usd",
}
HASH_RECORD_FIELDS = {"raw_output_sha256", "candidate_program_sha256"}
MASK_FIELDS = {
    "task_inst",
    "output_fname",
    "domain_knowledge",
    "dataset_folder_tree",
    "dataset_preview",
}
MASK_DESCRIPTOR_FIELDS = {
    "state",
    "value_type",
    "canonical_json_bytes",
    "canonical_json_sha256",
}
FORBIDDEN_FIELD_FRAGMENTS = {
    "gold",
    "rubric",
    "evaluator_feedback",
    "evaluation_result",
    "official_outcome",
    "official_score",
    "success_rate",
    "solved",
    "judge_response",
    "result_body",
}
FORBIDDEN_PATH_COMPONENTS = {
    "gold_programs",
    "gold_results",
    "eval_programs",
    "evaluation_programs",
    "scoring_rubrics",
    "evaluator_feedback",
    "official_results",
}
PLACEHOLDER_FRAGMENTS = {
    "AUTHOR_INPUT_NEEDED",
    "CANNOT_CHECK",
    "TBD",
    "TODO",
    "UNKNOWN",
    "UNBOUND",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class ContractError(ValueError):
    """Raised when an input fails the frozen runner contract."""


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise ContractError(f"required file does not exist or is unreadable: {path}") from exc


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return _sha256_bytes(payload)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ContractError(f"required {label} does not exist or is unreadable: {path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{label} is not valid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    return value


def _require_exact_fields(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise ContractError(f"{label} fields mismatch: missing={missing} extra={extra}")


def _validate_no_forbidden_fields(value: Any, location: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ContractError(f"non-string field name at {location}")
            lowered = key.lower()
            matched = sorted(
                fragment
                for fragment in FORBIDDEN_FIELD_FRAGMENTS
                if fragment in lowered
            )
            if matched:
                raise ContractError(
                    f"forbidden field {key!r} at {location}: matched {matched[0]}"
                )
            _validate_no_forbidden_fields(nested, f"{location}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_no_forbidden_fields(nested, f"{location}[{index}]")


def _validate_split(split: str | None) -> str:
    if split is None or not isinstance(split, str) or not split:
        raise ContractError("split is required explicitly and must equal verified")
    if split != PRODUCTION_SPLIT:
        raise ContractError(
            f"split must equal verified exactly; received {split!r}"
        )
    return split


def _validate_sha256(value: Any, label: str, *, allow_null: bool = False) -> str | None:
    if value is None and allow_null:
        return None
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ContractError(f"{label} must be a lowercase 64-hex SHA-256 or allowed null")
    return value


def _canonical_task_id(value: Any) -> str:
    if isinstance(value, bool):
        raise ContractError("task IDs cannot be booleans")
    if isinstance(value, int):
        if value < 1:
            raise ContractError(f"task IDs must be positive canonical integers: {value!r}")
        return str(value)
    if isinstance(value, str) and value.isdigit() and value == str(int(value)):
        return value
    raise ContractError(f"task IDs must be canonical decimal strings or integers: {value!r}")


def _canonical_task_ids(values: Any, label: str) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise ContractError(f"{label} task IDs must be a JSON list")
    try:
        return tuple(_canonical_task_id(value) for value in values)
    except ContractError as exc:
        raise ContractError(f"{label} task IDs invalid: {exc}") from exc


def _ensure_expected_task_ids(
    observed: tuple[str, ...], expected: Sequence[str], label: str
) -> None:
    expected_tuple = tuple(expected)
    if observed != expected_tuple or len(set(observed)) != len(observed):
        raise ContractError(
            f"{label} task IDs must equal the exact ordered population {list(expected_tuple)}; "
            f"observed={list(observed)}"
        )


def _validate_absolute_safe_path(path: Path | str, label: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise ContractError(f"{label} must be an absolute path")
    lowered_components = {component.lower() for component in candidate.parts}
    matched = sorted(lowered_components & FORBIDDEN_PATH_COMPONENTS)
    if matched:
        raise ContractError(
            f"forbidden path component {matched[0]!r} in {label}: {candidate}"
        )
    return candidate


def _validate_mask_shape(mask: Mapping[str, Any], expected_task_ids: Sequence[str]) -> None:
    if mask.get("schema_version") != "orion.p1.scienceagentbench.mask-manifest.v1":
        raise ContractError("mask manifest schema_version mismatch")
    source = mask.get("source")
    if not isinstance(source, dict):
        raise ContractError("mask manifest source must be an object")
    if source.get("split") != PRODUCTION_SPLIT:
        raise ContractError("mask manifest split must equal verified")
    if mask.get("outcomes_opened") is not False:
        raise ContractError("mask manifest outcomes_opened must be false")
    if mask.get("scientific_authority_delta") != "NONE":
        raise ContractError("mask manifest scientific_authority_delta must be NONE")
    records = mask.get("records")
    if not isinstance(records, list):
        raise ContractError("mask manifest records must be a list")
    observed_ids = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ContractError(f"mask record {index} must be an object")
        observed_ids.append(_canonical_task_id(record.get("instance_id")))
        fields = record.get("fields")
        if not isinstance(fields, dict) or set(fields) != MASK_FIELDS:
            raise ContractError(f"mask record {index} fields are not hash-only frozen fields")
        for field_name, descriptor in fields.items():
            if not isinstance(descriptor, dict):
                raise ContractError(
                    f"mask record {index} descriptor {field_name} must be an object"
                )
            _require_exact_fields(
                descriptor,
                MASK_DESCRIPTOR_FIELDS,
                f"mask record {index} descriptor {field_name}",
            )
            _validate_sha256(
                descriptor.get("canonical_json_sha256"),
                f"mask record {index} descriptor {field_name} canonical_json_sha256",
            )
            byte_count = descriptor.get("canonical_json_bytes")
            if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count < 0:
                raise ContractError(
                    f"mask record {index} descriptor {field_name} canonical_json_bytes invalid"
                )
    _ensure_expected_task_ids(tuple(observed_ids), expected_task_ids, "mask manifest")


def _validate_input_binding(
    split: str | None,
    parquet_path: Path | str,
    mask_manifest_path: Path | str,
    *,
    expected_parquet_sha256: str,
    expected_mask_sha256: str,
    expected_task_ids: Sequence[str],
) -> dict[str, Any]:
    _validate_split(split)
    parquet = _validate_absolute_safe_path(parquet_path, "Parquet path")
    manifest_path = _validate_absolute_safe_path(
        mask_manifest_path, "mask-manifest path"
    )
    observed_parquet_hash = _sha256_file(parquet)
    if observed_parquet_hash != expected_parquet_sha256:
        raise ContractError(
            "verified Parquet SHA-256 mismatch: "
            f"expected={expected_parquet_sha256} observed={observed_parquet_hash}"
        )
    observed_mask_hash = _sha256_file(manifest_path)
    if observed_mask_hash != expected_mask_sha256:
        raise ContractError(
            "mask-manifest SHA-256 mismatch: "
            f"expected={expected_mask_sha256} observed={observed_mask_hash}"
        )
    mask = _load_json(manifest_path, "mask manifest")
    _validate_mask_shape(mask, expected_task_ids)
    source = mask["source"]
    if source.get("verified_parquet_sha256") != expected_parquet_sha256:
        raise ContractError(
            "mask-manifest verified Parquet binding does not match the required hash"
        )
    return {
        "schema_version": INPUT_SCHEMA,
        "authority": "INPUT_IDENTITY_ONLY__NO_TASK_OR_OUTCOME_AUTHORITY",
        "split": PRODUCTION_SPLIT,
        "verified_parquet_sha256": observed_parquet_hash,
        "mask_manifest_sha256": observed_mask_hash,
        "task_ids": list(expected_task_ids),
        "task_count": len(expected_task_ids),
        "parquet_body_parsed": False,
        "outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }


def validate_input_binding(
    split: str | None, parquet_path: Path | str, mask_manifest_path: Path | str
) -> dict[str, Any]:
    """Validate production input constants; callers cannot override them."""

    return _validate_input_binding(
        split,
        parquet_path,
        mask_manifest_path,
        expected_parquet_sha256=PRODUCTION_PARQUET_SHA256,
        expected_mask_sha256=PRODUCTION_MASK_MANIFEST_SHA256,
        expected_task_ids=TASK_IDS,
    )


def _ensure_bound_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a nonempty immutable binding")
    upper = value.upper()
    matched = sorted(fragment for fragment in PLACEHOLDER_FRAGMENTS if fragment in upper)
    if matched:
        raise ContractError(f"{label} is unbound: contains {matched[0]}")
    return value


def _ensure_nonnegative_number(
    value: Any, label: str, *, integer: bool, allow_null: bool = False
) -> int | float | None:
    if value is None and allow_null:
        return None
    if isinstance(value, bool):
        raise ContractError(f"{label} must be numeric, not boolean")
    if integer:
        if not isinstance(value, int):
            raise ContractError(f"{label} must be a nonnegative integer")
    elif not isinstance(value, (int, float)):
        raise ContractError(f"{label} must be a nonnegative finite number")
    if not math.isfinite(value) or value < 0:
        raise ContractError(f"{label} must be a nonnegative finite number")
    return value


def _validate_run_plan(
    plan: Mapping[str, Any], *, expected_task_ids: Sequence[str]
) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ContractError("run plan must be a JSON object")
    _validate_no_forbidden_fields(plan, "run_plan")
    _require_exact_fields(plan, RUN_PLAN_FIELDS, "run plan")
    if plan["schema_version"] != RUN_PLAN_SCHEMA:
        raise ContractError("run plan schema_version mismatch")
    _validate_split(plan["split"])
    observed_ids = _canonical_task_ids(plan["task_ids"], "run plan")
    _ensure_expected_task_ids(observed_ids, expected_task_ids, "run plan")
    if plan["arms"] != list(ARMS):
        raise ContractError(f"run plan arms must equal {list(ARMS)} in order")
    if plan["attempts_per_task_arm"] != len(ATTEMPTS):
        raise ContractError("run plan attempts_per_task_arm must equal 3")
    if plan["cost_accounting"] != "ALL_ATTEMPTS_NO_SELECTION":
        raise ContractError("run plan cost_accounting must be ALL_ATTEMPTS_NO_SELECTION")

    bindings = plan["bindings"]
    if not isinstance(bindings, dict):
        raise ContractError("run plan bindings must be an object")
    _require_exact_fields(bindings, BINDING_FIELDS, "run plan bindings")
    for name in ("model_id", "provider", "tokenizer_revision"):
        _ensure_bound_string(bindings[name], name)
    prompt_hashes = bindings["prompt_bundle_sha256_by_arm"]
    if not isinstance(prompt_hashes, dict) or set(prompt_hashes) != set(ARMS):
        raise ContractError(f"prompt_bundle_sha256_by_arm must bind exactly {list(ARMS)}")
    for arm in ARMS:
        _validate_sha256(prompt_hashes[arm], f"prompt bundle for {arm}")
    seeds = bindings["seed_schedule"]
    expected_seed_keys = {str(attempt) for attempt in ATTEMPTS}
    if not isinstance(seeds, dict) or set(seeds) != expected_seed_keys:
        raise ContractError("seed_schedule must bind attempts 1, 2, and 3 exactly")
    for attempt in ATTEMPTS:
        _ensure_nonnegative_number(
            seeds[str(attempt)], f"seed_schedule[{attempt}]", integer=True
        )
    if bindings["provider_seed_capability"] != "CONFIRMED":
        raise ContractError("provider_seed_capability must equal CONFIRMED")
    if bindings["credential_route_status"] != "BOUND_OWNER_CONTROLLED":
        raise ContractError("credential_route_status must equal BOUND_OWNER_CONTROLLED")
    for name in (
        "model_parameters_sha256",
        "tool_policy_sha256",
        "generation_runtime_manifest_sha256",
        "credential_route_sha256",
    ):
        _validate_sha256(bindings[name], name)

    budgets = plan["budget_by_arm"]
    if not isinstance(budgets, dict) or set(budgets) != set(ARMS):
        raise ContractError(f"budget_by_arm must bind exactly {list(ARMS)}")
    normalized_budgets = []
    for arm in ARMS:
        budget = budgets[arm]
        if not isinstance(budget, dict):
            raise ContractError(f"budget for {arm} must be an object")
        _require_exact_fields(budget, BUDGET_FIELDS, f"budget for {arm}")
        for name in (
            "total_input_token_cap",
            "total_output_token_cap",
            "tool_call_cap",
            "final_candidates_per_attempt",
        ):
            _ensure_nonnegative_number(budget[name], f"{arm}.{name}", integer=True)
        for name in ("wall_time_seconds_cap", "local_execution_seconds_cap"):
            _ensure_nonnegative_number(budget[name], f"{arm}.{name}", integer=False)
        if budget["total_input_token_cap"] <= 0 or budget["total_output_token_cap"] <= 0:
            raise ContractError(f"{arm} token caps must be positive")
        if budget["wall_time_seconds_cap"] <= 0 or budget["local_execution_seconds_cap"] <= 0:
            raise ContractError(f"{arm} time caps must be positive")
        if budget["final_candidates_per_attempt"] != 1:
            raise ContractError(f"{arm}.final_candidates_per_attempt must equal 1")
        normalized_budgets.append(budget)
    if any(budget != normalized_budgets[0] for budget in normalized_budgets[1:]):
        raise ContractError("RR/OS/NR budget envelopes must be exactly matched")
    return dict(plan)


def validate_run_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a production 102-task run plan."""

    return _validate_run_plan(plan, expected_task_ids=TASK_IDS)


def _validate_candidate_ledger(
    ledger: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    expected_task_ids: Sequence[str],
    expected_run_plan_sha256: str,
) -> dict[str, int]:
    if not isinstance(ledger, dict):
        raise ContractError("candidate ledger must be a JSON object")
    _validate_no_forbidden_fields(ledger, "candidate_ledger")
    _require_exact_fields(ledger, LEDGER_FIELDS, "candidate ledger")
    if ledger["schema_version"] != LEDGER_SCHEMA:
        raise ContractError("candidate ledger schema_version mismatch")
    _validate_split(ledger["split"])
    if ledger["run_plan_sha256"] != expected_run_plan_sha256:
        raise ContractError(
            "candidate ledger run-plan SHA-256 does not match the supplied run plan"
        )
    if ledger["cost_accounting"] != "ALL_ATTEMPTS_NO_SELECTION":
        raise ContractError(
            "candidate ledger cost_accounting must be ALL_ATTEMPTS_NO_SELECTION"
        )
    records = ledger["records"]
    if not isinstance(records, list):
        raise ContractError("candidate ledger records must be a list")

    expected_tuples = {
        (task_id, arm, attempt)
        for task_id in expected_task_ids
        for arm in ARMS
        for attempt in ATTEMPTS
    }
    observed_tuples: list[tuple[str, str, int]] = []
    cannot_check_count = 0
    seeds = plan["bindings"]["seed_schedule"]
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ContractError(f"candidate record {index} must be an object")
        _require_exact_fields(record, RECORD_FIELDS, f"candidate record {index}")
        task_id = _canonical_task_id(record["task_id"])
        arm = record["arm_id"]
        if arm not in ARMS:
            raise ContractError(f"candidate record {index} arm_id invalid: {arm!r}")
        attempt = record["attempt"]
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt not in ATTEMPTS:
            raise ContractError(f"candidate record {index} attempt must be 1, 2, or 3")
        if record["seed"] != seeds[str(attempt)] or isinstance(record["seed"], bool):
            raise ContractError(f"candidate record {index} seed does not match run plan")
        observed_tuples.append((task_id, arm, attempt))

        for name in INTEGER_USAGE_FIELDS:
            _ensure_nonnegative_number(
                record[name], f"candidate record {index} {name}", integer=True, allow_null=True
            )
        for name in NUMBER_USAGE_FIELDS:
            _ensure_nonnegative_number(
                record[name], f"candidate record {index} {name}", integer=False, allow_null=True
            )
        budget = plan["budget_by_arm"][arm]
        usage_caps = {
            "input_tokens": "total_input_token_cap",
            "output_tokens": "total_output_token_cap",
            "tool_calls": "tool_call_cap",
            "wall_time_seconds": "wall_time_seconds_cap",
            "local_execution_wall_time_seconds": "local_execution_seconds_cap",
        }
        for usage_name, cap_name in usage_caps.items():
            usage = record[usage_name]
            if usage is not None and usage > budget[cap_name]:
                raise ContractError(
                    f"candidate record {index} {usage_name} exceeds matched cap "
                    f"{cap_name}={budget[cap_name]}"
                )
        for name in HASH_RECORD_FIELDS:
            _validate_sha256(
                record[name], f"candidate record {index} {name}", allow_null=True
            )

        failure = record["failure"]
        if failure is None:
            required_success_fields = (
                INTEGER_USAGE_FIELDS | NUMBER_USAGE_FIELDS | HASH_RECORD_FIELDS
            )
            missing = sorted(name for name in required_success_fields if record[name] is None)
            if missing:
                raise ContractError(
                    f"candidate record {index} successful record has null fields: {missing}"
                )
        else:
            cannot_check_count += 1
            if not isinstance(failure, dict):
                raise ContractError(f"candidate record {index} failure must be null or object")
            _require_exact_fields(failure, FAILURE_FIELDS, f"candidate record {index} failure")
            if failure["status"] != "CANNOT_CHECK":
                raise ContractError(
                    f"candidate record {index} failure status must be CANNOT_CHECK"
                )
            if failure["stage"] not in FAILURE_STAGES:
                raise ContractError(f"candidate record {index} failure stage invalid")
            _ensure_bound_string(failure["code"], f"candidate record {index} failure code")
            _validate_sha256(
                failure["detail_sha256"],
                f"candidate record {index} failure detail_sha256",
                allow_null=True,
            )

    observed_set = set(observed_tuples)
    if (
        len(observed_tuples) != len(expected_tuples)
        or len(observed_set) != len(observed_tuples)
        or observed_set != expected_tuples
    ):
        missing = len(expected_tuples - observed_set)
        extra = len(observed_set - expected_tuples)
        duplicates = len(observed_tuples) - len(observed_set)
        raise ContractError(
            "candidate tuples must equal the complete task x arm x attempt product: "
            f"missing={missing} extra={extra} duplicates={duplicates}"
        )
    return {
        "candidate_record_count": len(records),
        "cannot_check_record_count": cannot_check_count,
    }


def _create_candidate_seal(
    split: str | None,
    parquet_path: Path | str,
    mask_manifest_path: Path | str,
    run_plan_path: Path | str,
    candidate_ledger_path: Path | str,
    *,
    expected_parquet_sha256: str,
    expected_mask_sha256: str,
    expected_task_ids: Sequence[str],
) -> dict[str, Any]:
    input_binding = _validate_input_binding(
        split,
        parquet_path,
        mask_manifest_path,
        expected_parquet_sha256=expected_parquet_sha256,
        expected_mask_sha256=expected_mask_sha256,
        expected_task_ids=expected_task_ids,
    )
    plan_path = _validate_absolute_safe_path(run_plan_path, "run-plan path")
    ledger_path = _validate_absolute_safe_path(
        candidate_ledger_path, "candidate-ledger path"
    )
    run_plan_sha256 = _sha256_file(plan_path)
    plan = _load_json(plan_path, "run plan")
    _validate_run_plan(plan, expected_task_ids=expected_task_ids)
    ledger_sha256 = _sha256_file(ledger_path)
    ledger = _load_json(ledger_path, "candidate ledger")
    counts = _validate_candidate_ledger(
        ledger,
        plan,
        expected_task_ids=expected_task_ids,
        expected_run_plan_sha256=run_plan_sha256,
    )
    canonical_tuples = [
        [task_id, arm, attempt]
        for task_id in expected_task_ids
        for arm in ARMS
        for attempt in ATTEMPTS
    ]
    return {
        "schema_version": SEAL_SCHEMA,
        "authority": "COMPLETE_CANDIDATE_METADATA_SEAL_ONLY__NO_EVALUATOR_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "status": "COMPLETE_CANDIDATE_LEDGER_SEALED__EVALUATOR_NOT_INVOKED",
        "split": PRODUCTION_SPLIT,
        "verified_parquet_sha256": input_binding["verified_parquet_sha256"],
        "mask_manifest_sha256": input_binding["mask_manifest_sha256"],
        "official_source_commit": OFFICIAL_SOURCE_COMMIT,
        "run_plan_sha256": run_plan_sha256,
        "candidate_ledger_sha256": ledger_sha256,
        "canonical_tuple_set_sha256": _canonical_sha256(canonical_tuples),
        "candidate_record_count": counts["candidate_record_count"],
        "cannot_check_record_count": counts["cannot_check_record_count"],
        "candidate_generation_complete": True,
        "cost_accounting": "ALL_ATTEMPTS_NO_SELECTION",
        "missingness_policy": "NULL_AND_CANNOT_CHECK_PRESERVED__NO_SOLVED_COERCION",
        "evaluator_outcomes_opened": False,
        "official_evaluator_invoked": False,
        "scientific_authority_delta": "NONE",
    }


def create_candidate_seal(
    split: str | None,
    parquet_path: Path | str,
    mask_manifest_path: Path | str,
    run_plan_path: Path | str,
    candidate_ledger_path: Path | str,
) -> dict[str, Any]:
    """Validate and seal the complete production ledger; constants are fixed."""

    return _create_candidate_seal(
        split,
        parquet_path,
        mask_manifest_path,
        run_plan_path,
        candidate_ledger_path,
        expected_parquet_sha256=PRODUCTION_PARQUET_SHA256,
        expected_mask_sha256=PRODUCTION_MASK_MANIFEST_SHA256,
        expected_task_ids=TASK_IDS,
    )


def validate_evaluator_argv(argv: Sequence[str]) -> None:
    """Validate one inert official evaluator argv vector."""

    if not isinstance(argv, (list, tuple)) or not all(
        isinstance(token, str) for token in argv
    ):
        raise ContractError("evaluator argv must be a sequence of strings")
    expected_prefix = ["python", "-m", OFFICIAL_EVALUATOR_MODULE]
    if list(argv[:3]) != expected_prefix:
        raise ContractError(f"evaluator argv must start with {expected_prefix}")
    if any(token.startswith("--split=") for token in argv):
        raise ContractError("evaluator split must not use --split= form")
    if argv.count("--split") != 1:
        raise ContractError("evaluator argv must contain exactly one --split token")
    split_index = argv.index("--split")
    if split_index + 1 >= len(argv) or argv[split_index + 1] != PRODUCTION_SPLIT:
        raise ContractError("evaluator split must be exactly --split verified")
    for flag in (
        "--benchmark_path",
        "--pred_program_path",
        "--log_fname",
        "--run_id",
    ):
        if argv.count(flag) != 1:
            raise ContractError(f"evaluator argv must contain exactly one {flag}")
        index = argv.index(flag)
        if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
            raise ContractError(f"evaluator argv {flag} must have one value")


def _validate_seal_for_emission(
    seal: Mapping[str, Any],
    *,
    expected_task_ids: Sequence[str],
    expected_parquet_sha256: str,
    expected_mask_sha256: str,
) -> None:
    required = {
        "status": "COMPLETE_CANDIDATE_LEDGER_SEALED__EVALUATOR_NOT_INVOKED",
        "split": PRODUCTION_SPLIT,
        "verified_parquet_sha256": expected_parquet_sha256,
        "mask_manifest_sha256": expected_mask_sha256,
        "official_source_commit": OFFICIAL_SOURCE_COMMIT,
        "candidate_record_count": len(expected_task_ids) * len(ARMS) * len(ATTEMPTS),
        "candidate_generation_complete": True,
        "cost_accounting": "ALL_ATTEMPTS_NO_SELECTION",
        "evaluator_outcomes_opened": False,
        "official_evaluator_invoked": False,
        "scientific_authority_delta": "NONE",
    }
    for key, expected in required.items():
        if seal.get(key) != expected:
            raise ContractError(
                f"seal receipt {key} mismatch: expected={expected!r} observed={seal.get(key)!r}"
            )
    for key in (
        "run_plan_sha256",
        "candidate_ledger_sha256",
        "canonical_tuple_set_sha256",
    ):
        _validate_sha256(seal.get(key), f"seal receipt {key}")


def _build_evaluator_command_receipt(
    seal_receipt: Mapping[str, Any],
    *,
    official_repo_root: Path | str,
    benchmark_path: Path | str,
    pred_program_path: Path | str,
    log_fname: Path | str,
    arm_id: str,
    attempt: int,
    run_id: str,
    split: str | None,
    expected_task_ids: Sequence[str],
    expected_parquet_sha256: str,
    expected_mask_sha256: str,
) -> dict[str, Any]:
    _validate_split(split)
    if not isinstance(seal_receipt, dict):
        raise ContractError("seal receipt must be a JSON object")
    _validate_no_forbidden_fields(seal_receipt, "seal_receipt")
    _validate_seal_for_emission(
        seal_receipt,
        expected_task_ids=expected_task_ids,
        expected_parquet_sha256=expected_parquet_sha256,
        expected_mask_sha256=expected_mask_sha256,
    )
    if arm_id not in ARMS:
        raise ContractError(f"arm_id must be one of {list(ARMS)}")
    if isinstance(attempt, bool) or attempt not in ATTEMPTS:
        raise ContractError("attempt must be 1, 2, or 3")
    if not isinstance(run_id, str) or SAFE_RUN_ID_RE.fullmatch(run_id) is None:
        raise ContractError("run_id must contain only letters, digits, dot, underscore, or hyphen")

    repo_root = _validate_absolute_safe_path(official_repo_root, "official repo root")
    benchmark = _validate_absolute_safe_path(benchmark_path, "benchmark path")
    predictions = _validate_absolute_safe_path(
        pred_program_path, "pred-program path"
    )
    log_path = _validate_absolute_safe_path(log_fname, "log-fname path")
    if log_path.suffix != ".jsonl":
        raise ContractError("log_fname must end in .jsonl")

    argv = [
        "python",
        "-m",
        OFFICIAL_EVALUATOR_MODULE,
        "--benchmark_path",
        str(benchmark),
        "--pred_program_path",
        str(predictions),
        "--log_fname",
        str(log_path),
        "--run_id",
        run_id,
        "--split",
        PRODUCTION_SPLIT,
    ]
    validate_evaluator_argv(argv)
    return {
        "schema_version": COMMAND_SCHEMA,
        "authority": "INERT_OFFICIAL_EVALUATOR_COMMAND_PLAN_ONLY__NO_EXECUTION_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "status": "VERIFIED_SPLIT_COMMAND_EMITTED__NOT_EXECUTED",
        "official_source_commit": OFFICIAL_SOURCE_COMMIT,
        "source_checkout_cwd": str(repo_root),
        "source_checkout_identity_status": "CALLER_MUST_VERIFY_PINNED_COMMIT_BEFORE_EXECUTION",
        "candidate_seal_sha256": _canonical_sha256(seal_receipt),
        "arm_id": arm_id,
        "attempt": attempt,
        "run_id": run_id,
        "split": PRODUCTION_SPLIT,
        "argv": argv,
        "argv_sha256": _canonical_sha256(argv),
        "execution_allowed": False,
        "official_evaluator_invoked": False,
        "evaluator_outcomes_opened": False,
        "runtime_status": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }


def build_evaluator_command_receipt(
    seal_receipt: Mapping[str, Any],
    official_repo_root: Path | str,
    benchmark_path: Path | str,
    pred_program_path: Path | str,
    log_fname: Path | str,
    arm_id: str,
    attempt: int,
    run_id: str,
    split: str | None,
) -> dict[str, Any]:
    """Emit an inert production evaluator argv receipt; never execute it."""

    return _build_evaluator_command_receipt(
        seal_receipt,
        official_repo_root=official_repo_root,
        benchmark_path=benchmark_path,
        pred_program_path=pred_program_path,
        log_fname=log_fname,
        arm_id=arm_id,
        attempt=attempt,
        run_id=run_id,
        split=split,
        expected_task_ids=TASK_IDS,
        expected_parquet_sha256=PRODUCTION_PARQUET_SHA256,
        expected_mask_sha256=PRODUCTION_MASK_MANIFEST_SHA256,
    )


def _write_json(path: Path | str, value: Mapping[str, Any]) -> None:
    destination = _validate_absolute_safe_path(path, "output path")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _add_explicit_split(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--split", required=True, choices=[PRODUCTION_SPLIT])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and seal verified ScienceAgentBench candidate metadata, or "
            "emit an inert official evaluator command receipt. No evaluator is run."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate-bindings")
    _add_explicit_split(validate)
    validate.add_argument("--parquet", required=True, type=Path)
    validate.add_argument("--mask-manifest", required=True, type=Path)
    validate.add_argument("--run-plan", required=True, type=Path)
    validate.add_argument("--output", required=True, type=Path)

    seal = commands.add_parser("seal-candidates")
    _add_explicit_split(seal)
    seal.add_argument("--parquet", required=True, type=Path)
    seal.add_argument("--mask-manifest", required=True, type=Path)
    seal.add_argument("--run-plan", required=True, type=Path)
    seal.add_argument("--candidate-ledger", required=True, type=Path)
    seal.add_argument("--output", required=True, type=Path)

    emit = commands.add_parser("emit-evaluator-command")
    _add_explicit_split(emit)
    emit.add_argument("--seal-receipt", required=True, type=Path)
    emit.add_argument("--official-repo-root", required=True, type=Path)
    emit.add_argument("--benchmark-path", required=True, type=Path)
    emit.add_argument("--pred-program-path", required=True, type=Path)
    emit.add_argument("--log-fname", required=True, type=Path)
    emit.add_argument("--arm", required=True, choices=list(ARMS))
    emit.add_argument("--attempt", required=True, type=int, choices=list(ATTEMPTS))
    emit.add_argument("--run-id", required=True)
    emit.add_argument("--output", required=True, type=Path)
    return parser


def _binding_receipt(
    split: str | None,
    parquet_path: Path,
    mask_manifest_path: Path,
    run_plan_path: Path,
) -> dict[str, Any]:
    input_binding = validate_input_binding(split, parquet_path, mask_manifest_path)
    plan_path = _validate_absolute_safe_path(run_plan_path, "run-plan path")
    plan = _load_json(plan_path, "run plan")
    validate_run_plan(plan)
    return {
        "schema_version": "orion.p1.scienceagentbench.binding-validation-receipt.v1",
        "authority": "INPUT_AND_MATCHING_CONTRACT_VALIDATION_ONLY__NO_RUN_OR_SCIENTIFIC_AUTHORITY",
        "status": "VERIFIED_INPUT_AND_MATCHED_RUN_PLAN_BOUND__CANDIDATES_NOT_GENERATED",
        "input_binding": input_binding,
        "run_plan_sha256": _sha256_file(plan_path),
        "official_source_commit": OFFICIAL_SOURCE_COMMIT,
        "candidate_generation_started": False,
        "official_evaluator_invoked": False,
        "evaluator_outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "validate-bindings":
            receipt = _binding_receipt(
                args.split, args.parquet, args.mask_manifest, args.run_plan
            )
        elif args.command == "seal-candidates":
            receipt = create_candidate_seal(
                args.split,
                args.parquet,
                args.mask_manifest,
                args.run_plan,
                args.candidate_ledger,
            )
        elif args.command == "emit-evaluator-command":
            seal = _load_json(
                _validate_absolute_safe_path(args.seal_receipt, "seal-receipt path"),
                "seal receipt",
            )
            receipt = build_evaluator_command_receipt(
                seal,
                args.official_repo_root,
                args.benchmark_path,
                args.pred_program_path,
                args.log_fname,
                args.arm,
                args.attempt,
                args.run_id,
                args.split,
            )
        else:  # pragma: no cover - argparse makes this unreachable.
            raise ContractError(f"unsupported command: {args.command}")
        _write_json(args.output, receipt)
    except ContractError as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
