#!/usr/bin/env python3
"""Frozen, standard-library ScienceAgentBench outcome analysis contract V1.

This module does not retrieve or run the benchmark.  It accepts a future
externally retained, task-level outcome ledger and either evaluates the exact
frozen gate or emits a typed CANNOT_CHECK result without imputing outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import sys
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "ANALYSIS_CONTRACT_V1.json"
CONTRACT_SHA256 = "143ce29af997257f3cccea19dc1ae97521889472fb3981ca1ad6d0fbafbdec81"

OUTCOME_SCHEMA = "orion.p1.scienceagentbench.outcome-ledger.v1"
RESULT_SCHEMA = "orion.p1.scienceagentbench.analysis-result.v1"
DATASET = "osunlp/ScienceAgentBench"
DATASET_REVISION = "9c6e96c9e74572e979b0930ee735041cef528cb7"
VERIFIED_PARQUET_SHA256 = "c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147"
OFFICIAL_SOURCE_COMMIT = "c26e151ed601ba109dc4d35e057ff8e73fec469d"
SPLIT = "verified"
ARMS = ("RR", "OS", "NR")
ATTEMPTS = (1, 2, 3)
BOOTSTRAP_REPLICATES = 100_000
BOOTSTRAP_SEED = 20_260_824
GAIN_THRESHOLD = Fraction(8, 100)
DISCIPLINE_NI_THRESHOLD = Fraction(-5, 100)
COST_RATIO_THRESHOLD = Decimal("1.5")

TOP_LEVEL_FIELDS = {
    "schema_version",
    "dataset",
    "dataset_revision",
    "split",
    "verified_parquet_sha256",
    "official_source_commit",
    "candidate_seal_sha256",
    "run_plan_sha256",
    "generation_ledger_sha256",
    "evaluator_runtime_manifest_sha256",
    "official_evaluator_identity_sha256",
    "cost_gate_metric",
    "cost_gate_metric_binding_sha256",
    "cost_accounting",
    "records",
}
ARTIFACT_HASH_FIELDS = {
    "candidate_seal_sha256",
    "run_plan_sha256",
    "generation_ledger_sha256",
    "evaluator_runtime_manifest_sha256",
    "official_evaluator_identity_sha256",
}
TASK_FIELDS = {
    "task_id",
    "discipline",
    "official_task_record_sha256",
    "attempt_records",
}
ATTEMPT_FIELDS = {
    "arm_id",
    "attempt",
    "candidate_program_sha256",
    "official_evaluator_record_sha256",
    "official_evaluator_status",
    "valid_program",
    "success_rate",
    "generation_cost_quantity",
    "generation_billed_cost_usd",
    "official_evaluator_billed_cost_usd",
    "failure",
}
FAILURE_FIELDS = {"status", "stage", "code", "detail_sha256"}
COST_METRIC_FIELDS = {"metric_id", "unit", "allocation_rule", "binding_phase"}
COST_METRICS = {
    "BILLED_USD": {
        "unit": "USD",
        "allocation_rule": "SUM_PROVIDER_BILLED_USD_FOR_ALL_ATTEMPTS_NO_SELECTION",
    },
    "ALLOCATED_ACCELERATOR_SECONDS": {
        "unit": "accelerator-second",
        "allocation_rule": "FOR_EACH_ATTEMPT_SUM_EXCLUSIVE_ACCELERATOR_COUNT_TIMES_MONOTONIC_GENERATION_WALL_SECONDS__NO_OVERLAP_DOUBLE_ALLOCATION__THEN_SUM_ALL_ATTEMPTS",
    },
}
COST_BINDING_PHASE = "BEFORE_CANDIDATE_GENERATION_AND_OUTCOME_OPENING"
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
TASK_ID_RE = re.compile(r"^(?:[1-9][0-9]*)$")


class ContractError(RuntimeError):
    """The committed analysis contract is absent, changed, or malformed."""


class MT19937Reference:
    """Minimal reference MT19937 using uint32 outputs only.

    The implementation and its unbiased ``randbelow`` construction are frozen
    in ANALYSIS_CONTRACT_V1.json.  It intentionally does not use Python's
    version-dependent high-level ``random`` sampling helpers.
    """

    N = 624
    M = 397
    MATRIX_A = 0x9908B0DF
    UPPER_MASK = 0x80000000
    LOWER_MASK = 0x7FFFFFFF

    def __init__(self, seed: int) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("MT19937 seed must be an integer")
        self._state = [0] * self.N
        self._state[0] = seed & 0xFFFFFFFF
        for index in range(1, self.N):
            prior = self._state[index - 1]
            self._state[index] = (
                1_812_433_253 * (prior ^ (prior >> 30)) + index
            ) & 0xFFFFFFFF
        self._index = self.N

    def _twist(self) -> None:
        for index in range(self.N):
            value = (self._state[index] & self.UPPER_MASK) | (
                self._state[(index + 1) % self.N] & self.LOWER_MASK
            )
            twisted = value >> 1
            if value & 1:
                twisted ^= self.MATRIX_A
            self._state[index] = self._state[(index + self.M) % self.N] ^ twisted
        self._index = 0

    def uint32(self) -> int:
        if self._index >= self.N:
            self._twist()
        value = self._state[self._index]
        self._index += 1
        value ^= value >> 11
        value ^= (value << 7) & 0x9D2C5680
        value ^= (value << 15) & 0xEFC60000
        value ^= value >> 18
        return value & 0xFFFFFFFF

    def randbelow(self, stop: int) -> int:
        if isinstance(stop, bool) or not isinstance(stop, int) or stop <= 0:
            raise ValueError("randbelow stop must be a positive integer")
        if stop > 2**32:
            raise ValueError("frozen randbelow supports stop <= 2^32")
        limit = (2**32 // stop) * stop
        while True:
            value = self.uint32()
            if value < limit:
                return value % stop


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _json_no_constants(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r} is forbidden")


def _load_json_bytes(payload: bytes) -> Any:
    return json.loads(
        payload.decode("utf-8"),
        parse_float=Decimal,
        parse_constant=_json_no_constants,
    )


def _load_frozen_contract() -> dict[str, Any]:
    try:
        payload = CONTRACT_PATH.read_bytes()
    except OSError as exc:
        raise ContractError(f"cannot read frozen contract: {exc}") from exc
    actual = sha256_bytes(payload)
    if actual != CONTRACT_SHA256:
        raise ContractError(
            f"analysis contract SHA-256 mismatch: expected {CONTRACT_SHA256}, got {actual}"
        )
    try:
        value = _load_json_bytes(payload)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot parse frozen contract: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("frozen contract must be a JSON object")
    return value


def _production_bindings() -> tuple[tuple[str, ...], dict[str, str], tuple[str, ...]]:
    contract = _load_frozen_contract()
    try:
        population = contract["production_population"]
        task_ids = tuple(population["task_ids"])
        discipline_order = tuple(population["discipline_order"])
        grouped = population["task_ids_by_discipline"]
    except (KeyError, TypeError) as exc:
        raise ContractError(f"frozen population is malformed: {exc}") from exc
    if task_ids != tuple(str(index) for index in range(1, 103)):
        raise ContractError("frozen task population is not canonical 1..102")
    task_to_discipline: dict[str, str] = {}
    for discipline in discipline_order:
        ids = grouped.get(discipline)
        if not isinstance(ids, list) or not ids:
            raise ContractError(f"malformed frozen discipline {discipline!r}")
        for task_id in ids:
            if task_id in task_to_discipline:
                raise ContractError(f"duplicate frozen task {task_id}")
            task_to_discipline[task_id] = discipline
    if set(task_to_discipline) != set(task_ids):
        raise ContractError("frozen task-to-discipline map is incomplete")
    return task_ids, task_to_discipline, discipline_order


def _reason(code: str, path: str, detail: str) -> dict[str, str]:
    return {"code": code, "path": path, "detail": detail}


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and HEX_RE.fullmatch(value) is not None


def _decimal_string(value: Any) -> Decimal | None:
    if not isinstance(value, str) or DECIMAL_RE.fullmatch(value) is None:
        return None
    parsed = Decimal(value)
    if not parsed.is_finite() or parsed < 0:
        return None
    return parsed


def _nullable_sha(value: Any) -> bool:
    return value is None or _is_sha256(value)


def _nullable_decimal(value: Any) -> bool:
    return value is None or _decimal_string(value) is not None


def _canonical_object_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def _exact_fields(value: Any, expected: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == expected


def _cannot_check_result(
    input_ledger_sha256: str | None,
    reasons: list[dict[str, str]],
    *,
    observed_task_records: int | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": RESULT_SCHEMA,
        "analysis_contract_sha256": CONTRACT_SHA256,
        "input_ledger_sha256": input_ledger_sha256,
        "status": "CANNOT_CHECK",
        "terminal": "P1_SAB_FROZEN_GATE_CANNOT_CHECK",
        "gate_evaluable": False,
        "population": {
            "expected_task_records": 102,
            "observed_task_records": observed_task_records,
            "expected_nested_attempt_records": 918,
        },
        "cannot_check_reasons": reasons,
        "estimands": None,
        "gate_components": None,
        "official_outcomes_opened_by_this_packet": False,
        "scientific_authority_delta": "NONE",
    }


def _validate_ledger(
    ledger: Any,
    task_ids: tuple[str, ...],
    task_to_discipline: dict[str, str],
) -> tuple[
    list[dict[str, str]],
    dict[str, dict[str, dict[int, dict[str, Any]]]],
    int | None,
    dict[str, str] | None,
]:
    reasons: list[dict[str, str]] = []
    parsed: dict[str, dict[str, dict[int, dict[str, Any]]]] = {}

    if not isinstance(ledger, dict):
        return [_reason("LEDGER_NOT_OBJECT", "$", "outcome ledger must be an object")], parsed, None, None
    if set(ledger) != TOP_LEVEL_FIELDS:
        missing = sorted(TOP_LEVEL_FIELDS - set(ledger))
        extra = sorted(set(ledger) - TOP_LEVEL_FIELDS)
        reasons.append(
            _reason(
                "TOP_LEVEL_SCHEMA_MISMATCH",
                "$",
                f"missing={missing}; extra={extra}",
            )
        )

    fixed = {
        "schema_version": OUTCOME_SCHEMA,
        "dataset": DATASET,
        "dataset_revision": DATASET_REVISION,
        "split": SPLIT,
        "verified_parquet_sha256": VERIFIED_PARQUET_SHA256,
        "official_source_commit": OFFICIAL_SOURCE_COMMIT,
        "cost_accounting": "ALL_ATTEMPTS_NO_SELECTION",
    }
    for field, expected in fixed.items():
        if ledger.get(field) != expected:
            reasons.append(
                _reason(
                    "FIXED_BINDING_MISMATCH",
                    f"$.{field}",
                    f"required frozen value {expected!r}",
                )
            )
    for field in ARTIFACT_HASH_FIELDS:
        if not _is_sha256(ledger.get(field)):
            reasons.append(
                _reason("INVALID_ARTIFACT_SHA256", f"$.{field}", "lowercase 64-hex required")
            )

    cost_metric = ledger.get("cost_gate_metric")
    parsed_cost_metric: dict[str, str] | None = None
    if not _exact_fields(cost_metric, COST_METRIC_FIELDS):
        reasons.append(
            _reason(
                "COST_METRIC_SCHEMA_MISMATCH",
                "$.cost_gate_metric",
                "exact prospectively frozen metric fields required",
            )
        )
    else:
        metric_values_are_strings = all(
            isinstance(cost_metric[field], str) for field in COST_METRIC_FIELDS
        )
        if not metric_values_are_strings:
            reasons.append(
                _reason(
                    "COST_METRIC_TYPE_MISMATCH",
                    "$.cost_gate_metric",
                    "all metric binding fields must be strings",
                )
            )
        metric_id = cost_metric["metric_id"]
        if not isinstance(metric_id, str) or metric_id not in COST_METRICS:
            expected_metric = None
            reasons.append(
                _reason(
                    "UNSUPPORTED_COST_METRIC",
                    "$.cost_gate_metric.metric_id",
                    "BILLED_USD or ALLOCATED_ACCELERATOR_SECONDS required",
                )
            )
        else:
            expected_metric = COST_METRICS[metric_id]
            if cost_metric["unit"] != expected_metric["unit"]:
                reasons.append(
                    _reason(
                        "COST_METRIC_UNIT_MISMATCH",
                        "$.cost_gate_metric.unit",
                        f"{expected_metric['unit']!r} required for {metric_id}",
                    )
                )
            if cost_metric["allocation_rule"] != expected_metric["allocation_rule"]:
                reasons.append(
                    _reason(
                        "COST_ALLOCATION_RULE_MISMATCH",
                        "$.cost_gate_metric.allocation_rule",
                        "exact frozen allocation rule required",
                    )
                )
            if cost_metric["binding_phase"] != COST_BINDING_PHASE:
                reasons.append(
                    _reason(
                        "COST_BINDING_PHASE_MISMATCH",
                        "$.cost_gate_metric.binding_phase",
                        COST_BINDING_PHASE,
                    )
                )
            parsed_cost_metric = dict(cost_metric)
        binding_hash = ledger.get("cost_gate_metric_binding_sha256")
        if not _is_sha256(binding_hash):
            reasons.append(
                _reason(
                    "INVALID_COST_METRIC_BINDING_SHA256",
                    "$.cost_gate_metric_binding_sha256",
                    "lowercase 64-hex required",
                )
            )
        elif metric_values_are_strings and binding_hash != _canonical_object_sha256(cost_metric):
            reasons.append(
                _reason(
                    "COST_METRIC_BINDING_SHA256_MISMATCH",
                    "$.cost_gate_metric_binding_sha256",
                    "must bind the canonical cost_gate_metric object",
                )
            )

    records = ledger.get("records")
    if not isinstance(records, list):
        reasons.append(_reason("RECORDS_NOT_LIST", "$.records", "records must be a list"))
        return reasons, parsed, None, parsed_cost_metric
    observed = len(records)
    if observed != len(task_ids):
        reasons.append(
            _reason(
                "OFFICIAL_TASK_RECORD_COUNT_MISMATCH",
                "$.records",
                f"expected {len(task_ids)}, observed {observed}",
            )
        )

    seen_tasks: set[str] = set()
    for record_index, task_record in enumerate(records):
        task_path = f"$.records[{record_index}]"
        if not _exact_fields(task_record, TASK_FIELDS):
            reasons.append(
                _reason("TASK_RECORD_SCHEMA_MISMATCH", task_path, "exact task fields required")
            )
            continue
        task_id = task_record["task_id"]
        if not isinstance(task_id, str) or TASK_ID_RE.fullmatch(task_id) is None:
            reasons.append(
                _reason("NONCANONICAL_TASK_ID", f"{task_path}.task_id", "canonical decimal string required")
            )
            continue
        if task_id in seen_tasks:
            reasons.append(_reason("DUPLICATE_TASK_ID", f"{task_path}.task_id", task_id))
            continue
        seen_tasks.add(task_id)
        if task_id not in task_to_discipline:
            reasons.append(_reason("EXTRA_TASK_ID", f"{task_path}.task_id", task_id))
            continue
        expected_discipline = task_to_discipline[task_id]
        if task_record["discipline"] != expected_discipline:
            reasons.append(
                _reason(
                    "DISCIPLINE_MISMATCH",
                    f"{task_path}.discipline",
                    f"task {task_id} requires {expected_discipline!r}",
                )
            )
        if not _is_sha256(task_record["official_task_record_sha256"]):
            reasons.append(
                _reason(
                    "INVALID_OFFICIAL_TASK_RECORD_SHA256",
                    f"{task_path}.official_task_record_sha256",
                    "lowercase 64-hex required",
                )
            )

        attempt_records = task_record["attempt_records"]
        if not isinstance(attempt_records, list):
            reasons.append(
                _reason("ATTEMPT_RECORDS_NOT_LIST", f"{task_path}.attempt_records", "list required")
            )
            continue
        if len(attempt_records) != len(ARMS) * len(ATTEMPTS):
            reasons.append(
                _reason(
                    "ATTEMPT_RECORD_COUNT_MISMATCH",
                    f"{task_path}.attempt_records",
                    f"expected 9, observed {len(attempt_records)}",
                )
            )
        parsed_task = {arm: {} for arm in ARMS}
        seen_attempts: set[tuple[str, int]] = set()
        for attempt_index, attempt_record in enumerate(attempt_records):
            attempt_path = f"{task_path}.attempt_records[{attempt_index}]"
            if not _exact_fields(attempt_record, ATTEMPT_FIELDS):
                reasons.append(
                    _reason("ATTEMPT_RECORD_SCHEMA_MISMATCH", attempt_path, "exact attempt fields required")
                )
                continue
            arm = attempt_record["arm_id"]
            attempt = attempt_record["attempt"]
            if arm not in ARMS:
                reasons.append(_reason("INVALID_ARM", f"{attempt_path}.arm_id", repr(arm)))
                continue
            if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt not in ATTEMPTS:
                reasons.append(_reason("INVALID_ATTEMPT", f"{attempt_path}.attempt", repr(attempt)))
                continue
            key = (arm, attempt)
            if key in seen_attempts:
                reasons.append(_reason("DUPLICATE_ATTEMPT_TUPLE", attempt_path, f"{arm}/{attempt}"))
                continue
            seen_attempts.add(key)

            status = attempt_record["official_evaluator_status"]
            if status == "OK":
                if not _is_sha256(attempt_record["candidate_program_sha256"]):
                    reasons.append(_reason("INVALID_CANDIDATE_SHA256", f"{attempt_path}.candidate_program_sha256", "required for OK record"))
                if not _is_sha256(attempt_record["official_evaluator_record_sha256"]):
                    reasons.append(_reason("INVALID_EVALUATOR_RECORD_SHA256", f"{attempt_path}.official_evaluator_record_sha256", "required for OK record"))
                valid_program = attempt_record["valid_program"]
                if isinstance(valid_program, bool) or not isinstance(valid_program, int) or valid_program not in (0, 1):
                    reasons.append(_reason("INVALID_VALID_PROGRAM", f"{attempt_path}.valid_program", "integer 0 or 1 required"))
                success_rate = _decimal_string(attempt_record["success_rate"])
                if success_rate is None or success_rate > 1:
                    reasons.append(_reason("INVALID_SUCCESS_RATE", f"{attempt_path}.success_rate", "exact decimal string in [0,1] required"))
                primary_cost = _decimal_string(attempt_record["generation_cost_quantity"])
                generation_billed_cost = (
                    None
                    if attempt_record["generation_billed_cost_usd"] is None
                    else _decimal_string(attempt_record["generation_billed_cost_usd"])
                )
                evaluator_cost = (
                    None
                    if attempt_record["official_evaluator_billed_cost_usd"] is None
                    else _decimal_string(attempt_record["official_evaluator_billed_cost_usd"])
                )
                if primary_cost is None:
                    reasons.append(_reason("INVALID_PRIMARY_GENERATION_COST", f"{attempt_path}.generation_cost_quantity", "exact nonnegative decimal string required"))
                if not _nullable_decimal(attempt_record["generation_billed_cost_usd"]):
                    reasons.append(_reason("INVALID_GENERATION_BILLED_USD", f"{attempt_path}.generation_billed_cost_usd", "null or exact nonnegative decimal string required"))
                if not _nullable_decimal(attempt_record["official_evaluator_billed_cost_usd"]):
                    reasons.append(_reason("INVALID_EVALUATOR_COST", f"{attempt_path}.official_evaluator_billed_cost_usd", "null or exact nonnegative decimal string required"))
                if (
                    parsed_cost_metric is not None
                    and parsed_cost_metric["metric_id"] == "BILLED_USD"
                    and (
                        generation_billed_cost is None
                        or primary_cost is None
                        or generation_billed_cost != primary_cost
                    )
                ):
                    reasons.append(
                        _reason(
                            "BILLED_USD_PRIMARY_QUANTITY_MISMATCH",
                            attempt_path,
                            "authoritative billed USD must be present and equal generation_cost_quantity",
                        )
                    )
                if attempt_record["failure"] is not None:
                    reasons.append(_reason("UNEXPECTED_FAILURE_OBJECT", f"{attempt_path}.failure", "OK record requires null"))
                attempt_record = dict(attempt_record)
                attempt_record["_success_rate_decimal"] = success_rate
                attempt_record["_generation_primary_cost_decimal"] = primary_cost
                attempt_record["_generation_billed_cost_decimal"] = generation_billed_cost
                attempt_record["_evaluator_cost_decimal"] = evaluator_cost
            elif status == "CANNOT_CHECK":
                if not _nullable_sha(attempt_record["candidate_program_sha256"]):
                    reasons.append(_reason("INVALID_CANDIDATE_SHA256", f"{attempt_path}.candidate_program_sha256", "null or lowercase 64-hex required"))
                if not _nullable_sha(attempt_record["official_evaluator_record_sha256"]):
                    reasons.append(_reason("INVALID_EVALUATOR_RECORD_SHA256", f"{attempt_path}.official_evaluator_record_sha256", "null or lowercase 64-hex required"))
                if attempt_record["valid_program"] is not None or attempt_record["success_rate"] is not None:
                    reasons.append(_reason("CANNOT_CHECK_OUTCOME_NOT_NULL", attempt_path, "outcome fields must remain null"))
                if not _nullable_decimal(attempt_record["generation_cost_quantity"]):
                    reasons.append(_reason("INVALID_PRIMARY_GENERATION_COST", f"{attempt_path}.generation_cost_quantity", "null or exact nonnegative decimal string required"))
                if not _nullable_decimal(attempt_record["generation_billed_cost_usd"]):
                    reasons.append(_reason("INVALID_GENERATION_COST", f"{attempt_path}.generation_billed_cost_usd", "null or exact nonnegative decimal string required"))
                if not _nullable_decimal(attempt_record["official_evaluator_billed_cost_usd"]):
                    reasons.append(_reason("INVALID_EVALUATOR_COST", f"{attempt_path}.official_evaluator_billed_cost_usd", "null or exact nonnegative decimal string required"))
                failure = attempt_record["failure"]
                if not _exact_fields(failure, FAILURE_FIELDS):
                    reasons.append(_reason("FAILURE_SCHEMA_MISMATCH", f"{attempt_path}.failure", "exact typed CANNOT_CHECK failure required"))
                else:
                    if failure["status"] != "CANNOT_CHECK":
                        reasons.append(_reason("FAILURE_STATUS_MISMATCH", f"{attempt_path}.failure.status", "CANNOT_CHECK required"))
                    if not isinstance(failure["stage"], str) or not failure["stage"]:
                        reasons.append(_reason("INVALID_FAILURE_STAGE", f"{attempt_path}.failure.stage", "nonempty string required"))
                    if not isinstance(failure["code"], str) or not failure["code"]:
                        reasons.append(_reason("INVALID_FAILURE_CODE", f"{attempt_path}.failure.code", "nonempty string required"))
                    if not _is_sha256(failure["detail_sha256"]):
                        reasons.append(_reason("INVALID_FAILURE_DETAIL_SHA256", f"{attempt_path}.failure.detail_sha256", "lowercase 64-hex required"))
                reasons.append(
                    _reason(
                        "OFFICIAL_EVALUATOR_CANNOT_CHECK",
                        attempt_path,
                        "evaluator/runtime/missingness failure is not solved=0",
                    )
                )
            else:
                reasons.append(_reason("INVALID_EVALUATOR_STATUS", f"{attempt_path}.official_evaluator_status", "OK or CANNOT_CHECK required"))
            parsed_task[arm][attempt] = attempt_record

        expected_attempts = {(arm, attempt) for arm in ARMS for attempt in ATTEMPTS}
        missing_attempts = sorted(expected_attempts - seen_attempts)
        extra_attempts = sorted(seen_attempts - expected_attempts)
        if missing_attempts or extra_attempts:
            reasons.append(
                _reason(
                    "ATTEMPT_TUPLE_SET_MISMATCH",
                    f"{task_path}.attempt_records",
                    f"missing={missing_attempts}; extra={extra_attempts}",
                )
            )
        parsed[task_id] = parsed_task

    missing_tasks = sorted(set(task_ids) - seen_tasks, key=lambda value: int(value))
    extra_tasks = sorted(seen_tasks - set(task_ids), key=lambda value: int(value))
    if missing_tasks or extra_tasks:
        reasons.append(
            _reason(
                "OFFICIAL_TASK_SET_MISMATCH",
                "$.records",
                f"missing={missing_tasks}; extra={extra_tasks}",
            )
        )
    return reasons, parsed, observed, parsed_cost_metric


def _fraction_text(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 50
        decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal_value.quantize(Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN), "f")


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _ratio_text(numerator: Decimal, denominator: Decimal) -> str:
    with localcontext() as context:
        context.prec = 50
        value = numerator / denominator
        return format(value.quantize(Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN), "f")


def _paired_stratified_bootstrap(
    solved: dict[str, dict[str, int]],
    task_ids: tuple[str, ...],
    task_to_discipline: dict[str, str],
    discipline_order: tuple[str, ...],
) -> dict[str, Any]:
    strata: dict[str, list[tuple[int, int, int]]] = {name: [] for name in discipline_order}
    for task_id in sorted(task_ids, key=lambda value: int(value)):
        strata[task_to_discipline[task_id]].append(
            (solved[task_id]["RR"], solved[task_id]["OS"], solved[task_id]["NR"])
        )

    rng = MT19937Reference(BOOTSTRAP_SEED)
    rr_os_numerators: list[int] = []
    rr_nr_numerators: list[int] = []
    trace = hashlib.sha256()
    for _ in range(BOOTSTRAP_REPLICATES):
        rr_os = 0
        rr_nr = 0
        for discipline in discipline_order:
            rows = strata[discipline]
            for _ in range(len(rows)):
                rr, os_value, nr_value = rows[rng.randbelow(len(rows))]
                rr_os += rr - os_value
                rr_nr += rr - nr_value
        rr_os_numerators.append(rr_os)
        rr_nr_numerators.append(rr_nr)
        trace.update(struct.pack(">hh", rr_os, rr_nr))

    rr_os_numerators.sort()
    rr_nr_numerators.sort()
    lower_index = math.ceil(Decimal("0.025") * BOOTSTRAP_REPLICATES) - 1
    upper_index = math.ceil(Decimal("0.975") * BOOTSTRAP_REPLICATES) - 1
    denominator = len(task_ids)

    def interval(values: list[int]) -> dict[str, Any]:
        lower = Fraction(values[lower_index], denominator)
        upper = Fraction(values[upper_index], denominator)
        return {
            "lower": _fraction_text(lower),
            "upper": _fraction_text(upper),
            "lower_numerator": lower.numerator,
            "lower_denominator": lower.denominator,
            "upper_numerator": upper.numerator,
            "upper_denominator": upper.denominator,
            "lower_strictly_greater_than_zero": lower > 0,
        }

    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "rng_algorithm": "MT19937_REFERENCE_UINT32_V1",
        "rng_seed_decimal": BOOTSTRAP_SEED,
        "stratum_order": list(discipline_order),
        "quantile_rule": "NEAREST_RANK_CEIL_Q_TIMES_B",
        "lower_zero_index": lower_index,
        "upper_zero_index": upper_index,
        "replicate_contrast_numerators_sha256": trace.hexdigest(),
        "RR_minus_OS": interval(rr_os_numerators),
        "RR_minus_NR": interval(rr_nr_numerators),
    }


def _evaluate_complete_gate(
    parsed: dict[str, dict[str, dict[int, dict[str, Any]]]],
    cost_metric: dict[str, str],
    task_ids: tuple[str, ...],
    task_to_discipline: dict[str, str],
    discipline_order: tuple[str, ...],
    input_ledger_sha256: str | None,
) -> dict[str, Any]:
    solved: dict[str, dict[str, int]] = {}
    primary_generation_costs = {arm: Decimal(0) for arm in ARMS}
    generation_billed_costs = {arm: Decimal(0) for arm in ARMS}
    generation_billed_missing = {arm: 0 for arm in ARMS}
    evaluator_costs = {arm: Decimal(0) for arm in ARMS}
    evaluator_cost_missing = {arm: 0 for arm in ARMS}
    for task_id in task_ids:
        solved[task_id] = {}
        for arm in ARMS:
            arm_records = parsed[task_id][arm]
            solved[task_id][arm] = int(
                any(
                    arm_records[attempt]["valid_program"] == 1
                    and arm_records[attempt]["_success_rate_decimal"] == 1
                    for attempt in ATTEMPTS
                )
            )
            for attempt in ATTEMPTS:
                primary_generation_costs[arm] += arm_records[attempt][
                    "_generation_primary_cost_decimal"
                ]
                billed = arm_records[attempt]["_generation_billed_cost_decimal"]
                if billed is None:
                    generation_billed_missing[arm] += 1
                else:
                    generation_billed_costs[arm] += billed
                evaluator_billed = arm_records[attempt]["_evaluator_cost_decimal"]
                if evaluator_billed is None:
                    evaluator_cost_missing[arm] += 1
                else:
                    evaluator_costs[arm] += evaluator_billed

    solved_counts = {
        arm: sum(solved[task_id][arm] for task_id in task_ids) for arm in ARMS
    }
    rates = {arm: Fraction(solved_counts[arm], len(task_ids)) for arm in ARMS}
    strongest = "OS" if rates["OS"] >= rates["NR"] else "NR"
    strongest_cost = primary_generation_costs[strongest]
    if strongest_cost == 0:
        return _cannot_check_result(
            input_ledger_sha256,
            [
                _reason(
                    "CANNOT_CHECK_COST_DENOMINATOR_ZERO",
                    "$.records[*].attempt_records[*].generation_cost_quantity",
                    f"strongest comparator {strongest} has zero total primary generation cost",
                )
            ],
            observed_task_records=len(task_ids),
        )

    bootstrap = _paired_stratified_bootstrap(
        solved, task_ids, task_to_discipline, discipline_order
    )
    point_contrasts = {
        "RR_minus_OS": rates["RR"] - rates["OS"],
        "RR_minus_NR": rates["RR"] - rates["NR"],
    }
    strongest_gain = rates["RR"] - rates[strongest]

    discipline_report: dict[str, Any] = {}
    discipline_pass = True
    for discipline in discipline_order:
        ids = [task_id for task_id in task_ids if task_to_discipline[task_id] == discipline]
        counts = {
            arm: sum(solved[task_id][arm] for task_id in ids) for arm in ARMS
        }
        discipline_rates = {arm: Fraction(counts[arm], len(ids)) for arm in ARMS}
        contrasts = {
            "RR_minus_OS": discipline_rates["RR"] - discipline_rates["OS"],
            "RR_minus_NR": discipline_rates["RR"] - discipline_rates["NR"],
        }
        contrast_pass = {
            name: value >= DISCIPLINE_NI_THRESHOLD for name, value in contrasts.items()
        }
        discipline_pass = discipline_pass and all(contrast_pass.values())
        discipline_report[discipline] = {
            "task_count": len(ids),
            "solved_counts": counts,
            "solve_rates": {arm: _fraction_text(value) for arm, value in discipline_rates.items()},
            "contrasts": {name: _fraction_text(value) for name, value in contrasts.items()},
            "contrast_pass": contrast_pass,
        }

    paired_ci_pass = all(
        bootstrap[name]["lower_strictly_greater_than_zero"]
        for name in ("RR_minus_OS", "RR_minus_NR")
    )
    gain_pass = strongest_gain >= GAIN_THRESHOLD
    cost_pass = primary_generation_costs["RR"] <= COST_RATIO_THRESHOLD * strongest_cost
    overall_pass = paired_ci_pass and gain_pass and discipline_pass and cost_pass

    return {
        "schema_version": RESULT_SCHEMA,
        "analysis_contract_sha256": CONTRACT_SHA256,
        "input_ledger_sha256": input_ledger_sha256,
        "status": "PASS" if overall_pass else "FAIL",
        "terminal": "P1_SAB_FROZEN_GATE_PASS" if overall_pass else "P1_SAB_FROZEN_GATE_FAIL",
        "gate_evaluable": True,
        "population": {
            "expected_task_records": 102,
            "observed_task_records": 102,
            "expected_nested_attempt_records": 918,
            "observed_nested_attempt_records": 918,
            "arms": list(ARMS),
            "attempts_per_task_arm": 3,
        },
        "cannot_check_reasons": [],
        "estimands": {
            "solved_counts": solved_counts,
            "solve_rates": {arm: _fraction_text(value) for arm, value in rates.items()},
            "point_contrasts": {name: _fraction_text(value) for name, value in point_contrasts.items()},
            "strongest_comparator": strongest,
            "strongest_comparator_tie_break": "OS_BY_FROZEN_ARM_ORDER",
            "RR_gain_over_strongest_comparator": _fraction_text(strongest_gain),
        },
        "gate_components": {
            "official_record_guard": {
                "required_task_records": 102,
                "required_nested_attempt_records": 918,
                "pass": True,
            },
            "paired_stratified_bootstrap": {
                **bootstrap,
                "required_lower_bound_operator": ">",
                "required_lower_bound": "0",
                "pass": paired_ci_pass,
            },
            "point_gain": {
                "strongest_comparator": strongest,
                "observed": _fraction_text(strongest_gain),
                "operator": ">=",
                "threshold": "0.08",
                "pass": gain_pass,
            },
            "discipline_noninferiority": {
                "operator": ">=",
                "threshold": "-0.05",
                "disciplines": discipline_report,
                "pass": discipline_pass,
            },
            "generation_cost": {
                "accounting": "ALL_ATTEMPTS_NO_SELECTION",
                "metric": cost_metric,
                "cost_gate_metric_binding_sha256": _canonical_object_sha256(cost_metric),
                "total_quantity_by_arm": {
                    arm: _decimal_text(value)
                    for arm, value in primary_generation_costs.items()
                },
                "strongest_comparator": strongest,
                "RR_to_strongest_comparator_ratio": _ratio_text(
                    primary_generation_costs["RR"], strongest_cost
                ),
                "operator": "<=",
                "threshold": "1.5",
                "pass": cost_pass,
            },
            "generation_billed_usd_separate": {
                "total_available_usd_by_arm": {
                    arm: _decimal_text(value)
                    for arm, value in generation_billed_costs.items()
                },
                "missing_attempts_by_arm": generation_billed_missing,
                "complete_by_arm": {
                    arm: generation_billed_missing[arm] == 0 for arm in ARMS
                },
                "missing_is_zero": False,
                "gate_primary": cost_metric["metric_id"] == "BILLED_USD",
            },
            "official_evaluator_cost_separate": {
                "total_available_usd_by_arm": {
                    arm: _decimal_text(value) for arm, value in evaluator_costs.items()
                },
                "missing_attempts_by_arm": evaluator_cost_missing,
                "complete_by_arm": {
                    arm: evaluator_cost_missing[arm] == 0 for arm in ARMS
                },
                "total_available_usd_all_arms": _decimal_text(
                    sum(evaluator_costs.values(), Decimal(0))
                ),
                "included_in_generation_ratio": False,
                "missing_is_zero": False,
            },
            "overall_pass": overall_pass,
        },
        "official_outcomes_opened_by_this_packet": False,
        "scientific_authority_delta": "NONE",
    }


def analyze_ledger(ledger: Any, input_ledger_sha256: str | None) -> dict[str, Any]:
    """Validate a parsed ledger and evaluate the frozen gate if it is complete."""

    task_ids, task_to_discipline, discipline_order = _production_bindings()
    reasons, parsed, observed, cost_metric = _validate_ledger(
        ledger, task_ids, task_to_discipline
    )
    if reasons:
        return _cannot_check_result(
            input_ledger_sha256,
            reasons,
            observed_task_records=observed,
        )
    return _evaluate_complete_gate(
        parsed,
        cost_metric,
        task_ids,
        task_to_discipline,
        discipline_order,
        input_ledger_sha256,
    )


def analyze_path(path: Path) -> dict[str, Any]:
    """Read one supplied ledger path and always fail closed on input defects."""

    try:
        payload = path.read_bytes()
    except OSError as exc:
        return _cannot_check_result(
            None,
            [_reason("LEDGER_READ_FAILURE", "$", type(exc).__name__)],
        )
    digest = sha256_bytes(payload)
    try:
        ledger = _load_json_bytes(payload)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        return _cannot_check_result(
            digest,
            [_reason("LEDGER_PARSE_FAILURE", "$", type(exc).__name__)],
        )
    return analyze_ledger(ledger, digest)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcome-ledger", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = analyze_path(args.outcome_ledger)
        write_json(args.output, result)
    except ContractError as exc:
        print(f"contract error: {exc}", file=sys.stderr)
        return 2
    print(result["terminal"])
    return 0 if result["status"] != "CANNOT_CHECK" else 3


if __name__ == "__main__":
    raise SystemExit(main())
