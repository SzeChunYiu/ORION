#!/usr/bin/env python3
"""Outcome-blind LUNARC generation timing and allocation-evidence adapter.

The module instruments injected model-operation callables and finalizes existing
candidate metadata. It has no benchmark, credential, provider, candidate-body,
evaluator or outcome reader and does not itself execute SLURM commands.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping, Sequence, TypeVar


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
CONTRACT_PATH = ROOT / "LUNARC_GENERATION_ADAPTER_CONTRACT_V1.json"
CONTRACT_SHA256 = "ae8fe86e4052b65f12176980fb03a653c1ab4b5b4f99c146d0db401563d93883"

RUNNER_V2_ROOT = REPO_ROOT / "development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24"
RUNNER_V2_MODULE_PATH = RUNNER_V2_ROOT / "sab_runner_v2_cost_amendment.py"
RUNNER_V2_CONTRACT_PATH = RUNNER_V2_ROOT / "RUNNER_V2_COST_AMENDMENT_CONTRACT.json"
RUNNER_V2_MODULE_SHA256 = "14c7d42b0b5add7c9bc4ae8608f74b422c638d0e795ef26996dcef4a87afe8ae"
RUNNER_V2_CONTRACT_SHA256 = "806a497798ed162af06130ec9bc12a1edf6153dc4adb690886c1c1d87f67dc0e"

RUNNER_V1_MODULE_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-runner-v1-2026-08-24/sab_verified_runner_v1.py"
)
RUNNER_V1_MODULE_SHA256 = "15d6f511be9b3b1dbac408cc41812b0f72e1dd7aa700983035438efb8ed416df"

CAPTURE_SCHEMA = "orion.p1.scienceagentbench.lunarc-generation-attempt-capture.v1"
CANNOT_CHECK_SCHEMA = (
    "orion.p1.scienceagentbench.lunarc-generation-attempt-cannot-check.v1"
)
SCHEDULER_EVIDENCE_SCHEMA = (
    "orion.p1.scienceagentbench.lunarc-scheduler-allocation-evidence.v1"
)
ALLOCATION_INDEX_SCHEMA = "orion.p1.scienceagentbench.lunarc-allocation-index.v1"
ADAPTER_SEAL_SCHEMA = "orion.p1.scienceagentbench.lunarc-generation-adapter-seal.v1"

CAPTURE_STATUS = "TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING"
PENDING_ALLOCATION_STATUS = "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION"
FINAL_ALLOCATION_STATUS = "EXCLUSIVE_NO_OVERLAP_CONFIRMED"
SCHEDULER_EXCLUSIVITY_STATUS = "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES"
ATTEMPT_SCOPE_STATUS = "ONE_TASK_ARM_ATTEMPT_ONLY_CONFIRMED"
TERMINAL_SLURM_STATES = {
    "BOOT_FAIL",
    "CANCELLED",
    "COMPLETED",
    "DEADLINE",
    "FAILED",
    "NODE_FAIL",
    "OUT_OF_MEMORY",
    "PREEMPTED",
    "REVOKED",
    "TIMEOUT",
}

PHASE_SEQUENCE_BY_ARM = {
    "RR": ("RR_PHASE0", "RR_PHASE1"),
    "OS": ("OS_PHASE1",),
    "NR": ("NR_PHASE0", "NR_PHASE1"),
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CANONICAL_UINT_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")
CANONICAL_POSITIVE_UINT_RE = re.compile(r"^[1-9][0-9]*$")
CANONICAL_CLUSTER_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CANONICAL_NODE_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CANONICAL_GRES_TYPE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
CANONICAL_GPU_UUID_RE = re.compile(
    r"^GPU-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
UTC_SECONDS_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")

BASE_RECORD_FIELDS = {
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

CAPTURE_FIELDS = {
    "schema_version",
    "authority",
    "status",
    "run_plan_sha256",
    "task_id",
    "arm_id",
    "attempt",
    "seed",
    "phase_sequence",
    "base_candidate_record",
    "base_candidate_record_canonical_sha256",
    "cost_measurement_binding_sha256",
    "exclusive_gpu_count",
    "clock_id",
    "clock_api",
    "monotonic_start_ns",
    "monotonic_end_ns",
    "monotonic_elapsed_ns",
    "allocation_status",
    "slurm_job_identity",
    "slurm_in_job_snapshot_sha256",
    "candidate_bodies_opened",
    "official_evaluator_invoked",
    "official_outcomes_opened",
    "scientific_authority_delta",
}

JOB_IDENTITY_FIELDS = {"cluster", "job_id", "array_job_id", "array_task_id"}
SCHEDULER_TOP_FIELDS = {
    "schema_version",
    "site",
    "scheduler",
    "scheduler_config_snapshot_sha256",
    "scheduler_export_sha256",
    "records",
}
SCHEDULER_RECORD_FIELDS = {
    "task_id",
    "arm_id",
    "attempt",
    "slurm_job_identity",
    "in_job_snapshot_sha256",
    "scheduler_record_sha256",
    "scheduler_record_source",
    "scheduler_job_state",
    "allocation_started_at_utc",
    "allocation_ended_at_utc",
    "node_name",
    "allocated_gpu_count",
    "gpu_allocations",
    "exclusive_gres_status",
    "attempt_scope_status",
}
SCHEDULER_RAW_RECORD_FIELDS = SCHEDULER_RECORD_FIELDS - {"scheduler_record_sha256"}
GPU_ALLOCATION_FIELDS = {
    "node_name",
    "gres_name",
    "gres_type",
    "gres_index",
    "gpu_uuid",
}

T = TypeVar("T")


class ContractError(ValueError):
    """Input or runtime evidence cannot satisfy the frozen adapter contract."""


class DuplicateJsonMemberError(ValueError):
    """Strict JSON input repeated a member."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path | str) -> str:
    candidate = Path(path)
    try:
        return sha256_bytes(candidate.read_bytes())
    except OSError as exc:
        raise ContractError(f"required file is unreadable: {candidate}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonMemberError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def strict_json_object_from_bytes(payload: bytes, label: str, source: Path | str) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_members,
            parse_constant=_reject_nonfinite_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonMemberError, ValueError) as exc:
        raise ContractError(f"{label} is not unambiguous strict UTF-8 JSON: {source}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    return value


def read_json_snapshot(path: Path | str, label: str) -> tuple[bytes, str, dict[str, Any]]:
    candidate = Path(path)
    try:
        payload = candidate.read_bytes()
    except OSError as exc:
        raise ContractError(f"required {label} is unreadable: {candidate}") from exc
    return payload, sha256_bytes(payload), strict_json_object_from_bytes(payload, label, candidate)


def _require_exact_fields(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    observed = set(value)
    if observed != expected:
        raise ContractError(
            f"{label} fields mismatch: missing={sorted(expected-observed)} "
            f"extra={sorted(observed-expected)}"
        )


def _validate_sha256(value: Any, label: str) -> str:
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


def _validate_runtime_clock_value(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError("raw clock value must be a nonnegative integer, not Boolean or float")
    return value


def _allocated_ns_to_seconds(allocated_ns: int) -> str:
    if isinstance(allocated_ns, bool) or not isinstance(allocated_ns, int) or allocated_ns < 0:
        raise ContractError("allocated nanoseconds must be a nonnegative integer")
    whole, remainder = divmod(allocated_ns, 1_000_000_000)
    if remainder == 0:
        return str(whole)
    return f"{whole}.{remainder:09d}".rstrip("0")


def _validate_job_identity(value: Any, label: str) -> dict[str, Any]:
    _require_exact_fields(value, JOB_IDENTITY_FIELDS, label)
    cluster = value["cluster"]
    job_id = value["job_id"]
    if (
        not isinstance(cluster, str)
        or CANONICAL_CLUSTER_NAME_RE.fullmatch(cluster) is None
    ):
        raise ContractError(
            f"{label}.cluster must be one canonical lowercase scheduler ClusterName"
        )
    if not isinstance(job_id, str):
        raise ContractError(f"{label}.job_id must be canonical text")
    array_job_id = value["array_job_id"]
    array_task_id = value["array_task_id"]
    if (array_job_id is None) != (array_task_id is None):
        raise ContractError(
            f"{label} canonical array_job_id and array_task_id must both be null or bound"
        )
    if array_job_id is None:
        if CANONICAL_POSITIVE_UINT_RE.fullmatch(job_id) is None:
            raise ContractError(
                f"{label}.job_id must be one canonical positive base allocation ID; array and step aliases forbidden"
            )
    else:
        if (
            not isinstance(array_job_id, str)
            or CANONICAL_POSITIVE_UINT_RE.fullmatch(array_job_id) is None
            or not isinstance(array_task_id, str)
            or CANONICAL_UINT_RE.fullmatch(array_task_id) is None
            or job_id != f"{array_job_id}_{array_task_id}"
        ):
            raise ContractError(
                f"{label} must use exactly one canonical array allocation identity"
            )
    return dict(value)


def _canonical_job_allocation_key(identity: Mapping[str, Any], label: str) -> str:
    canonical = _validate_job_identity(identity, label)
    return f"{canonical['cluster']}:{canonical['job_id']}"


def _validate_node_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or CANONICAL_NODE_NAME_RE.fullmatch(value) is None:
        raise ContractError(
            f"{label} must be one canonical lowercase scheduler NodeName without aliases"
        )
    return value


def _validate_gpu_allocations(
    value: Any, node_name: str, expected_count: int, label: str
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != expected_count:
        raise ContractError(
            f"{label} must contain exactly the scheduler allocated GPU count"
        )
    validated: list[dict[str, Any]] = []
    for index, allocation in enumerate(value):
        item_label = f"{label} item {index}"
        _require_exact_fields(allocation, GPU_ALLOCATION_FIELDS, item_label)
        if allocation["node_name"] != node_name:
            raise ContractError(f"{item_label} node alias or mismatch")
        if allocation["gres_name"] != "gpu":
            raise ContractError(f"{item_label}.gres_name must equal canonical gpu")
        gres_type = allocation["gres_type"]
        if (
            not isinstance(gres_type, str)
            or CANONICAL_GRES_TYPE_RE.fullmatch(gres_type) is None
        ):
            raise ContractError(f"{item_label}.gres_type must be canonical lowercase text")
        _validate_canonical_uint(allocation["gres_index"], f"{item_label}.gres_index")
        gpu_uuid = allocation["gpu_uuid"]
        if not isinstance(gpu_uuid, str) or CANONICAL_GPU_UUID_RE.fullmatch(gpu_uuid) is None:
            raise ContractError(f"{item_label}.gpu_uuid must be one canonical GPU UUID")
        validated.append(dict(allocation))
    if validated != sorted(
        validated, key=lambda item: (int(item["gres_index"]), item["gpu_uuid"])
    ):
        raise ContractError(f"{label} must use canonical GRES-index/GPU-UUID order")
    uuid_keys = [item["gpu_uuid"] for item in validated]
    gres_keys = [
        (item["node_name"], item["gres_name"], item["gres_type"], item["gres_index"])
        for item in validated
    ]
    if len(set(uuid_keys)) != len(uuid_keys) or len(set(gres_keys)) != len(gres_keys):
        raise ContractError(f"{label} contains duplicate physical GPU or GRES identity")
    return validated


_V2_MODULE: ModuleType | None = None
_VALIDATED_PLAN_HASHES: set[str] = set()


def load_v2_module() -> ModuleType:
    global _V2_MODULE
    observed = sha256_file(RUNNER_V2_MODULE_PATH)
    if observed != RUNNER_V2_MODULE_SHA256:
        raise ContractError(
            f"Runner V2 module SHA-256 drift: expected={RUNNER_V2_MODULE_SHA256} observed={observed}"
        )
    if _V2_MODULE is None:
        spec = importlib.util.spec_from_file_location(
            "orion_p1_sab_runner_v2_for_lunarc_adapter", RUNNER_V2_MODULE_PATH
        )
        if spec is None or spec.loader is None:
            raise ContractError("Runner V2 module cannot be loaded")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _V2_MODULE = module
    return _V2_MODULE


def verify_frozen_dependencies() -> None:
    bindings = (
        (CONTRACT_PATH, CONTRACT_SHA256, "adapter contract"),
        (RUNNER_V2_MODULE_PATH, RUNNER_V2_MODULE_SHA256, "Runner V2 module"),
        (RUNNER_V2_CONTRACT_PATH, RUNNER_V2_CONTRACT_SHA256, "Runner V2 contract"),
        (RUNNER_V1_MODULE_PATH, RUNNER_V1_MODULE_SHA256, "Runner V1 module"),
    )
    for path, expected, label in bindings:
        observed = sha256_file(path)
        if observed != expected:
            raise ContractError(
                f"{label} SHA-256 drift: expected={expected} observed={observed}"
            )
    v2 = load_v2_module()
    try:
        v2._load_and_verify_upstream_contracts()
    except Exception as exc:
        raise ContractError(f"Runner V2 upstream dependency failed: {exc}") from exc


def validate_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ContractError("run plan must be an object")
    plan_hash = canonical_hash(plan)
    if plan_hash not in _VALIDATED_PLAN_HASHES:
        v2 = load_v2_module()
        try:
            validated = v2.validate_run_plan(plan)
        except Exception as exc:
            raise ContractError(f"Runner V2 run-plan invariant failed: {exc}") from exc
        _VALIDATED_PLAN_HASHES.add(plan_hash)
        return validated
    return dict(plan)


def raw_monotonic_ns() -> int:
    clock_id = getattr(time, "CLOCK_MONOTONIC_RAW", None)
    reader = getattr(time, "clock_gettime_ns", None)
    if clock_id is None or reader is None or not callable(reader):
        raise ContractError("CLOCK_MONOTONIC_RAW via clock_gettime_ns is unavailable; fallback forbidden")
    try:
        return _validate_runtime_clock_value(reader(clock_id))
    except ContractError:
        raise
    except Exception as exc:
        raise ContractError("CLOCK_MONOTONIC_RAW clock_gettime_ns read failed") from exc


class GenerationAttemptCapture:
    """Capture exact first-to-final injected model-operation timing for one tuple."""

    def __init__(
        self,
        *,
        plan: Mapping[str, Any],
        run_plan_sha256: str,
        task_id: str,
        arm_id: str,
        attempt: int,
        slurm_job_identity: Mapping[str, Any],
        slurm_in_job_snapshot_sha256: str,
        raw_clock: Callable[[], int] = raw_monotonic_ns,
    ) -> None:
        self._plan = validate_plan(plan)
        self._run_plan_sha256 = _validate_sha256(run_plan_sha256, "run_plan_sha256")
        v2 = load_v2_module()
        if not isinstance(task_id, str) or task_id not in v2.TASK_IDS:
            raise ContractError("task_id must be one of the 102 frozen task IDs")
        if arm_id not in PHASE_SEQUENCE_BY_ARM:
            raise ContractError("arm_id must be RR, OS, or NR")
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt not in v2.ATTEMPTS:
            raise ContractError("attempt must be integer 1, 2, or 3")
        if not callable(raw_clock):
            raise ContractError("raw_clock must be callable")
        self.task_id = task_id
        self.arm_id = arm_id
        self.attempt = attempt
        self.seed = self._plan["bindings"]["seed_schedule"][str(attempt)]
        self.expected_phases = PHASE_SEQUENCE_BY_ARM[arm_id]
        self.slurm_job_identity = _validate_job_identity(
            slurm_job_identity, "slurm_job_identity"
        )
        self.slurm_in_job_snapshot_sha256 = _validate_sha256(
            slurm_in_job_snapshot_sha256, "slurm_in_job_snapshot_sha256"
        )
        self.exclusive_gpu_count = self._plan["cost_measurement_binding"][
            "exclusive_gpu_count_by_arm"
        ][arm_id]
        _validate_canonical_uint(
            self.exclusive_gpu_count, "exclusive_gpu_count", positive=True
        )
        self._clock = raw_clock
        self._next_phase_index = 0
        self._attempted_phases: list[str] = []
        self._start_ns: int | None = None
        self._end_ns: int | None = None
        self._failed = False
        self._failure_detail_sha256: str | None = None
        self._finalized = False

    def _read_clock(self) -> int:
        try:
            return _validate_runtime_clock_value(self._clock())
        except ContractError:
            self._failed = True
            raise
        except Exception as exc:
            self._failed = True
            raise ContractError("raw clock read failed") from exc

    def call_model(self, phase_id: str, operation: Callable[[], T]) -> T:
        if self._finalized:
            raise ContractError("capture is finalized and cannot accept another model operation")
        if self._failed:
            raise ContractError("capture failed and cannot accept another model operation")
        if self._next_phase_index >= len(self.expected_phases):
            self._failed = True
            raise ContractError("all frozen phases are complete; extra model operation forbidden")
        expected = self.expected_phases[self._next_phase_index]
        if phase_id != expected:
            self._failed = True
            raise ContractError(f"phase order mismatch: expected={expected} observed={phase_id}")
        if not callable(operation):
            self._failed = True
            raise ContractError("model operation must be callable")

        is_first = self._next_phase_index == 0
        is_final = self._next_phase_index == len(self.expected_phases) - 1
        if is_first:
            self._start_ns = self._read_clock()
        self._attempted_phases.append(phase_id)
        try:
            result = operation()
        except BaseException as exc:
            try:
                self._end_ns = self._read_clock()
            finally:
                self._failed = True
                self._failure_detail_sha256 = sha256_bytes(
                    f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
                )
            if self._start_ns is not None and self._end_ns < self._start_ns:
                raise ContractError("raw clock end precedes start after failed model operation") from exc
            raise
        if is_final:
            self._end_ns = self._read_clock()
            if self._start_ns is None or self._end_ns < self._start_ns:
                self._failed = True
                raise ContractError("raw clock end precedes start")
        self._next_phase_index += 1
        return result

    def finish(self, base_candidate_record: Mapping[str, Any]) -> dict[str, Any]:
        if self._finalized:
            raise ContractError("capture is already finalized")
        if self._failed:
            raise ContractError("capture failed; only a CANNOT_CHECK sidecar is admissible")
        if self._next_phase_index != len(self.expected_phases):
            self._failed = True
            raise ContractError("capture phase sequence is incomplete")
        if self._start_ns is None or self._end_ns is None:
            self._failed = True
            raise ContractError("capture lacks exact start or end clock value")
        try:
            _require_exact_fields(
                base_candidate_record, BASE_RECORD_FIELDS, "base candidate record"
            )
            identity = (
                base_candidate_record["task_id"],
                base_candidate_record["arm_id"],
                base_candidate_record["attempt"],
            )
            if identity != (self.task_id, self.arm_id, self.attempt):
                raise ContractError(
                    "base candidate record identity does not match capture identity"
                )
            if (
                base_candidate_record["seed"] != self.seed
                or isinstance(base_candidate_record["seed"], bool)
            ):
                raise ContractError(
                    "base candidate record seed does not match paired run plan"
                )
            base_copy = dict(base_candidate_record)
            base_record_hash = canonical_hash(base_copy)
        except ContractError:
            self._failed = True
            raise
        except (TypeError, ValueError) as exc:
            self._failed = True
            raise ContractError(
                "base candidate record must be strict canonical-JSON serializable"
            ) from exc
        elapsed_ns = self._end_ns - self._start_ns
        receipt = {
            "schema_version": CAPTURE_SCHEMA,
            "authority": "GENERATION_TIMING_METADATA_ONLY__ALLOCATION_AND_OUTCOMES_UNFINALIZED",
            "status": CAPTURE_STATUS,
            "run_plan_sha256": self._run_plan_sha256,
            "task_id": self.task_id,
            "arm_id": self.arm_id,
            "attempt": self.attempt,
            "seed": self.seed,
            "phase_sequence": list(self.expected_phases),
            "base_candidate_record": base_copy,
            "base_candidate_record_canonical_sha256": base_record_hash,
            "cost_measurement_binding_sha256": self._plan[
                "cost_measurement_binding_sha256"
            ],
            "exclusive_gpu_count": self.exclusive_gpu_count,
            "clock_id": "CLOCK_MONOTONIC_RAW",
            "clock_api": "clock_gettime_ns",
            "monotonic_start_ns": str(self._start_ns),
            "monotonic_end_ns": str(self._end_ns),
            "monotonic_elapsed_ns": str(elapsed_ns),
            "allocation_status": PENDING_ALLOCATION_STATUS,
            "slurm_job_identity": dict(self.slurm_job_identity),
            "slurm_in_job_snapshot_sha256": self.slurm_in_job_snapshot_sha256,
            "candidate_bodies_opened": False,
            "official_evaluator_invoked": False,
            "official_outcomes_opened": False,
            "scientific_authority_delta": "NONE",
        }
        self._finalized = True
        return receipt

    def cannot_check_sidecar(self, code: str, detail: bytes) -> dict[str, Any]:
        if self._finalized:
            raise ContractError("capture is finalized and cannot emit another receipt")
        if not isinstance(code, str) or not code.strip():
            raise ContractError("CANNOT_CHECK sidecar code must be nonempty bound text")
        if not isinstance(detail, bytes):
            raise ContractError("CANNOT_CHECK sidecar detail must be bytes for hash-only retention")
        sidecar = {
            "schema_version": CANNOT_CHECK_SCHEMA,
            "authority": "GENERATION_CAPTURE_FAILURE_METADATA_ONLY",
            "status": "CANNOT_CHECK",
            "run_plan_sha256": self._run_plan_sha256,
            "task_id": self.task_id,
            "arm_id": self.arm_id,
            "attempt": self.attempt,
            "seed": self.seed,
            "expected_phase_sequence": list(self.expected_phases),
            "attempted_phase_sequence": list(self._attempted_phases),
            "monotonic_start_ns": None if self._start_ns is None else str(self._start_ns),
            "monotonic_end_ns": None if self._end_ns is None else str(self._end_ns),
            "failure_code": code,
            "failure_detail_sha256": sha256_bytes(detail),
            "captured_exception_detail_sha256": self._failure_detail_sha256,
            "allocation_status": PENDING_ALLOCATION_STATUS,
            "slurm_job_identity": dict(self.slurm_job_identity),
            "slurm_in_job_snapshot_sha256": self.slurm_in_job_snapshot_sha256,
            "runner_v2_record_emitted": False,
            "official_evaluator_invoked": False,
            "official_outcomes_opened": False,
            "scientific_authority_delta": "NONE",
        }
        self._finalized = True
        return sidecar


def _validate_capture(
    capture: Any,
    plan: Mapping[str, Any],
    run_plan_sha256: str,
) -> tuple[tuple[str, str, int], dict[str, Any], int, int, int]:
    _require_exact_fields(capture, CAPTURE_FIELDS, "attempt capture")
    if capture["schema_version"] != CAPTURE_SCHEMA or capture["status"] != CAPTURE_STATUS:
        raise ContractError("attempt capture schema or status mismatch")
    if capture["run_plan_sha256"] != run_plan_sha256:
        raise ContractError("attempt capture run-plan SHA-256 mismatch")
    v2 = load_v2_module()
    task_id = capture["task_id"]
    arm = capture["arm_id"]
    attempt = capture["attempt"]
    if not isinstance(task_id, str) or task_id not in v2.TASK_IDS:
        raise ContractError("attempt capture task tuple is outside frozen population")
    if arm not in v2.ARMS or isinstance(attempt, bool) or attempt not in v2.ATTEMPTS:
        raise ContractError("attempt capture tuple arm or attempt invalid")
    key = (task_id, arm, attempt)
    expected_seed = plan["bindings"]["seed_schedule"][str(attempt)]
    if capture["seed"] != expected_seed or isinstance(capture["seed"], bool):
        raise ContractError("attempt capture seed mismatch")
    if capture["phase_sequence"] != list(PHASE_SEQUENCE_BY_ARM[arm]):
        raise ContractError("attempt capture phase sequence drift")
    if capture["allocation_status"] != PENDING_ALLOCATION_STATUS:
        raise ContractError("attempt capture must remain allocation pending")
    if capture["clock_id"] != "CLOCK_MONOTONIC_RAW" or capture["clock_api"] != "clock_gettime_ns":
        raise ContractError("attempt capture raw clock provenance drift")
    if capture["cost_measurement_binding_sha256"] != plan["cost_measurement_binding_sha256"]:
        raise ContractError("attempt capture measurement binding drift")
    gpu_count = _validate_canonical_uint(
        capture["exclusive_gpu_count"], "attempt capture exclusive_gpu_count", positive=True
    )
    expected_count = _validate_canonical_uint(
        plan["cost_measurement_binding"]["exclusive_gpu_count_by_arm"][arm],
        "plan exclusive_gpu_count",
        positive=True,
    )
    if gpu_count != expected_count:
        raise ContractError("attempt capture GPU count drift")
    start_ns = _validate_canonical_uint(capture["monotonic_start_ns"], "monotonic_start_ns")
    end_ns = _validate_canonical_uint(capture["monotonic_end_ns"], "monotonic_end_ns")
    elapsed_ns = _validate_canonical_uint(capture["monotonic_elapsed_ns"], "monotonic_elapsed_ns")
    if end_ns < start_ns:
        raise ContractError("attempt capture monotonic end precedes start")
    if elapsed_ns != end_ns - start_ns:
        raise ContractError("attempt capture elapsed is not exact end-minus-start")
    _require_exact_fields(capture["base_candidate_record"], BASE_RECORD_FIELDS, "base candidate record")
    if canonical_hash(capture["base_candidate_record"]) != capture[
        "base_candidate_record_canonical_sha256"
    ]:
        raise ContractError("base candidate record canonical SHA-256 mismatch")
    base = capture["base_candidate_record"]
    if (base["task_id"], base["arm_id"], base["attempt"]) != key:
        raise ContractError("base candidate record identity drift")
    if base["seed"] != expected_seed or isinstance(base["seed"], bool):
        raise ContractError("base candidate record seed drift")
    _validate_job_identity(capture["slurm_job_identity"], "capture slurm_job_identity")
    _validate_sha256(capture["slurm_in_job_snapshot_sha256"], "capture snapshot")
    if any(
        capture[field] is not expected
        for field, expected in (
            ("candidate_bodies_opened", False),
            ("official_evaluator_invoked", False),
            ("official_outcomes_opened", False),
        )
    ) or capture["scientific_authority_delta"] != "NONE":
        raise ContractError("attempt capture authority boundary drift")
    return key, dict(capture), gpu_count, start_ns, elapsed_ns


def _parse_utc_seconds(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or UTC_SECONDS_RE.fullmatch(value) is None:
        raise ContractError(f"{label} scheduler interval timestamp invalid")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ContractError(f"{label} scheduler interval timestamp invalid") from exc
    return parsed


def validate_scheduler_snapshot_bindings(
    evidence: Mapping[str, Any],
    observed_config_snapshot_sha256: str,
    observed_export_snapshot_sha256: str,
) -> None:
    _validate_sha256(observed_config_snapshot_sha256, "observed scheduler config snapshot")
    _validate_sha256(observed_export_snapshot_sha256, "observed scheduler export snapshot")
    if not isinstance(evidence, dict):
        raise ContractError("scheduler evidence must be an object")
    if evidence.get("scheduler_config_snapshot_sha256") != observed_config_snapshot_sha256:
        raise ContractError("scheduler config snapshot SHA-256 mismatch")
    if evidence.get("scheduler_export_sha256") != observed_export_snapshot_sha256:
        raise ContractError("scheduler export snapshot SHA-256 mismatch")


def parse_scheduler_export_snapshot(
    payload: bytes,
) -> dict[str, dict[str, Any]]:
    """Parse exact LF-terminated JSONL scheduler records keyed by raw-line hash."""

    if not isinstance(payload, bytes) or not payload or not payload.endswith(b"\n"):
        raise ContractError(
            "scheduler export snapshot must be nonempty bytes with a final LF"
        )
    records_by_raw_sha256: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(payload.splitlines(keepends=True), start=1):
        if not line.endswith(b"\n") or line.endswith(b"\r\n") or line == b"\n":
            raise ContractError(
                f"scheduler export raw record {line_number} must be one nonempty LF-only line"
            )
        record_bytes = line[:-1]
        record = strict_json_object_from_bytes(
            record_bytes,
            f"scheduler export raw record {line_number}",
            f"scheduler-export-jsonl:{line_number}",
        )
        _require_exact_fields(
            record,
            SCHEDULER_RAW_RECORD_FIELDS,
            f"scheduler export raw record {line_number}",
        )
        raw_record_sha256 = sha256_bytes(line)
        if raw_record_sha256 in records_by_raw_sha256:
            raise ContractError(
                "scheduler export reuses one exact raw record line/hash"
            )
        records_by_raw_sha256[raw_record_sha256] = record
    return records_by_raw_sha256


def validate_scheduler_allocation_evidence(
    captures: Sequence[Mapping[str, Any]],
    evidence: Mapping[str, Any],
    plan: Mapping[str, Any],
    run_plan_sha256: str,
    scheduler_export_snapshot: bytes,
) -> dict[str, Any]:
    validated_plan = validate_plan(plan)
    expected_plan_sha = _validate_sha256(run_plan_sha256, "run_plan_sha256")
    if not isinstance(captures, list):
        raise ContractError("capture ledger records must be a list")
    v2 = load_v2_module()
    expected_tuples = {
        (task_id, arm, attempt)
        for task_id in v2.TASK_IDS
        for arm in v2.ARMS
        for attempt in v2.ATTEMPTS
    }
    captures_by_tuple: dict[tuple[str, str, int], dict[str, Any]] = {}
    for capture in captures:
        key, validated, _, _, _ = _validate_capture(
            capture, validated_plan, expected_plan_sha
        )
        if key in captures_by_tuple:
            raise ContractError(f"duplicate capture tuple {key}")
        captures_by_tuple[key] = validated
    if set(captures_by_tuple) != expected_tuples or len(captures) != len(expected_tuples):
        raise ContractError(
            "capture tuple set must equal all 918 tuples: "
            f"missing={len(expected_tuples-set(captures_by_tuple))} "
            f"extra={len(set(captures_by_tuple)-expected_tuples)}"
        )

    _require_exact_fields(evidence, SCHEDULER_TOP_FIELDS, "scheduler evidence")
    if evidence["schema_version"] != SCHEDULER_EVIDENCE_SCHEMA:
        raise ContractError("scheduler evidence schema mismatch")
    if evidence["site"] != "LUNARC" or evidence["scheduler"] != "SLURM":
        raise ContractError("scheduler evidence route must equal LUNARC/SLURM")
    _validate_sha256(evidence["scheduler_config_snapshot_sha256"], "scheduler config snapshot")
    _validate_sha256(evidence["scheduler_export_sha256"], "scheduler export")
    observed_export_sha256 = sha256_bytes(scheduler_export_snapshot)
    if evidence["scheduler_export_sha256"] != observed_export_sha256:
        raise ContractError("scheduler export snapshot SHA-256 mismatch")
    raw_records_by_sha256 = parse_scheduler_export_snapshot(
        scheduler_export_snapshot
    )
    records = evidence["records"]
    if not isinstance(records, list):
        raise ContractError("scheduler evidence records must be a list")

    scheduler_by_tuple: dict[tuple[str, str, int], dict[str, Any]] = {}
    job_bindings: dict[str, tuple[str, str, int]] = {}
    used_raw_record_hashes: set[str] = set()
    for index, record in enumerate(records):
        _require_exact_fields(record, SCHEDULER_RECORD_FIELDS, f"scheduler record {index}")
        raw_record_sha256 = _validate_sha256(
            record["scheduler_record_sha256"], "scheduler raw record SHA-256"
        )
        if raw_record_sha256 in used_raw_record_hashes:
            raise ContractError(
                "scheduler evidence reuses one exact raw scheduler record/hash"
            )
        raw_record = raw_records_by_sha256.get(raw_record_sha256)
        if raw_record is None:
            raise ContractError(
                "scheduler evidence record hash is absent from exact retained raw export bytes"
            )
        parsed_record = {
            field: record[field] for field in SCHEDULER_RAW_RECORD_FIELDS
        }
        if parsed_record != raw_record:
            raise ContractError(
                "scheduler evidence parsed fields do not equal the exact retained raw record"
            )
        used_raw_record_hashes.add(raw_record_sha256)
        task_id = record["task_id"]
        arm_id = record["arm_id"]
        attempt = record["attempt"]
        if (
            not isinstance(task_id, str)
            or task_id not in v2.TASK_IDS
            or not isinstance(arm_id, str)
            or arm_id not in v2.ARMS
            or isinstance(attempt, bool)
            or not isinstance(attempt, int)
            or attempt not in v2.ATTEMPTS
        ):
            raise ContractError(f"scheduler record {index} tuple is outside frozen population")
        key = (task_id, arm_id, attempt)
        if key in scheduler_by_tuple:
            raise ContractError(f"duplicate scheduler tuple {key}")
        scheduler_by_tuple[key] = dict(record)
        identity_key = _canonical_job_allocation_key(
            record["slurm_job_identity"], f"scheduler record {index} job identity"
        )
        if identity_key in job_bindings:
            raise ContractError(
                "one SLURM job/allocation identity cannot bind two task/arm/attempt tuples"
            )
        job_bindings[identity_key] = key
    if set(scheduler_by_tuple) != expected_tuples or len(records) != len(expected_tuples):
        raise ContractError(
            "scheduler tuple set must equal all 918 tuples: "
            f"missing={len(expected_tuples-set(scheduler_by_tuple))} "
            f"extra={len(set(scheduler_by_tuple)-expected_tuples)}"
        )
    if (
        used_raw_record_hashes != set(raw_records_by_sha256)
        or len(raw_records_by_sha256) != len(expected_tuples)
    ):
        raise ContractError(
            "exact retained scheduler export record set must equal all 918 evidence records"
        )

    intervals_by_gpu: dict[str, list[tuple[datetime, datetime, tuple[str, str, int]]]] = {}
    gpu_uuid_to_node: dict[str, str] = {}
    gres_device_to_uuid: dict[tuple[str, str, str, str], str] = {}
    index_records: list[dict[str, Any]] = []
    for task_id in v2.TASK_IDS:
        for arm in v2.ARMS:
            for attempt in v2.ATTEMPTS:
                key = (task_id, arm, attempt)
                capture = captures_by_tuple[key]
                record = scheduler_by_tuple[key]
                if record["slurm_job_identity"] != capture["slurm_job_identity"]:
                    raise ContractError(f"scheduler/capture SLURM job identity mismatch for {key}")
                if record["in_job_snapshot_sha256"] != capture[
                    "slurm_in_job_snapshot_sha256"
                ]:
                    raise ContractError(f"scheduler/capture in-job snapshot mismatch for {key}")
                if record["scheduler_record_source"] != "SCONTROL_AND_SACCT":
                    raise ContractError("scheduler record must bind both scontrol and sacct evidence")
                scheduler_state = record["scheduler_job_state"]
                if (
                    not isinstance(scheduler_state, str)
                    or scheduler_state not in TERMINAL_SLURM_STATES
                ):
                    raise ContractError(
                        "scheduler job state must be one normalized terminal SLURM state"
                    )
                if record["exclusive_gres_status"] != SCHEDULER_EXCLUSIVITY_STATUS:
                    raise ContractError(
                        "scheduler-confirmed consumable exclusive GRES evidence is required; environment-only claim rejected"
                    )
                if record["attempt_scope_status"] != ATTEMPT_SCOPE_STATUS:
                    raise ContractError("scheduler allocation must be scoped to one task/arm/attempt")
                count = _validate_canonical_uint(
                    record["allocated_gpu_count"], "scheduler allocated GPU count", positive=True
                )
                expected_count = _validate_canonical_uint(
                    capture["exclusive_gpu_count"], "capture exclusive GPU count", positive=True
                )
                if count != expected_count:
                    raise ContractError("scheduler allocated GPU count does not match frozen plan/capture")
                node = _validate_node_name(record["node_name"], "scheduler node_name")
                gpu_allocations = _validate_gpu_allocations(
                    record["gpu_allocations"],
                    node,
                    count,
                    "scheduler GPU allocations",
                )
                gpu_keys: list[str] = []
                for allocation in gpu_allocations:
                    gpu_uuid = allocation["gpu_uuid"]
                    prior_node = gpu_uuid_to_node.setdefault(gpu_uuid, node)
                    if prior_node != node:
                        raise ContractError(
                            "one physical GPU UUID cannot use multiple scheduler NodeName aliases"
                        )
                    gres_key = (
                        node,
                        allocation["gres_name"],
                        allocation["gres_type"],
                        allocation["gres_index"],
                    )
                    prior_uuid = gres_device_to_uuid.setdefault(gres_key, gpu_uuid)
                    if prior_uuid != gpu_uuid:
                        raise ContractError(
                            "one scheduler node/GRES identity cannot alias multiple GPU UUIDs"
                        )
                    gpu_keys.append(f"{node}/{gpu_uuid}")
                started = _parse_utc_seconds(
                    record["allocation_started_at_utc"], "allocation start"
                )
                ended = _parse_utc_seconds(
                    record["allocation_ended_at_utc"], "allocation end"
                )
                if ended <= started:
                    raise ContractError("scheduler allocation interval must have end strictly after start")
                for allocation in gpu_allocations:
                    intervals_by_gpu.setdefault(allocation["gpu_uuid"], []).append(
                        (started, ended, key)
                    )
                index_records.append(
                    {
                        "task_id": task_id,
                        "arm_id": arm,
                        "attempt": attempt,
                        "capture_receipt_canonical_sha256": canonical_hash(capture),
                        "scheduler_record_canonical_sha256": canonical_hash(record),
                        "slurm_job_identity": dict(record["slurm_job_identity"]),
                        "allocation_started_at_utc": record["allocation_started_at_utc"],
                        "allocation_ended_at_utc": record["allocation_ended_at_utc"],
                        "allocated_gpu_count": record["allocated_gpu_count"],
                        "gpu_allocations": [dict(item) for item in gpu_allocations],
                        "gpu_allocation_keys": list(gpu_keys),
                    }
                )

    for gpu_key, intervals in intervals_by_gpu.items():
        ordered = sorted(intervals, key=lambda item: (item[0], item[1], item[2]))
        previous_start, previous_end, previous_key = ordered[0]
        for current_start, current_end, current_key in ordered[1:]:
            if current_start < previous_end:
                raise ContractError(
                    f"scheduler allocation overlap for {gpu_key}: {previous_key} and {current_key}"
                )
            previous_start, previous_end, previous_key = (
                current_start,
                current_end,
                current_key,
            )

    return {
        "schema_version": ALLOCATION_INDEX_SCHEMA,
        "authority": "SCHEDULER_ALLOCATION_METADATA_CONFORMANCE_ONLY__NO_OUTCOME_AUTHORITY",
        "status": FINAL_ALLOCATION_STATUS,
        "run_plan_sha256": expected_plan_sha,
        "capture_ledger_canonical_sha256": canonical_hash(captures),
        "scheduler_evidence_canonical_sha256": canonical_hash(evidence),
        "scheduler_config_snapshot_sha256": evidence["scheduler_config_snapshot_sha256"],
        "scheduler_export_sha256": evidence["scheduler_export_sha256"],
        "scheduler_raw_record_count": len(raw_records_by_sha256),
        "scheduler_raw_record_hash_set_sha256": canonical_hash(
            sorted(raw_records_by_sha256)
        ),
        "tuple_count": len(expected_tuples),
        "unique_slurm_job_count": len(job_bindings),
        "allocation_count_by_arm": {
            arm: sum(1 for row in index_records if row["arm_id"] == arm) for arm in v2.ARMS
        },
        "overlap_interval_semantics": "HALF_OPEN_SCHEDULER_UTC_INTERVALS",
        "cross_job_raw_monotonic_comparison_used": False,
        "overlap_conflict_count": 0,
        "records": index_records,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }


def finalize_v2_candidate_ledger(
    plan: Mapping[str, Any],
    run_plan_sha256: str,
    captures: Sequence[Mapping[str, Any]],
    scheduler_evidence: Mapping[str, Any],
    scheduler_config_snapshot: bytes,
    scheduler_export_snapshot: bytes,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    verify_frozen_dependencies()
    validated_plan = validate_plan(plan)
    expected_plan_sha = _validate_sha256(run_plan_sha256, "run_plan_sha256")
    if not isinstance(scheduler_config_snapshot, bytes):
        raise ContractError("scheduler config snapshot must be exact bytes")
    if not isinstance(scheduler_export_snapshot, bytes):
        raise ContractError("scheduler export snapshot must be exact bytes")
    validate_scheduler_snapshot_bindings(
        scheduler_evidence,
        sha256_bytes(scheduler_config_snapshot),
        sha256_bytes(scheduler_export_snapshot),
    )
    allocation_index = validate_scheduler_allocation_evidence(
        captures,
        scheduler_evidence,
        validated_plan,
        expected_plan_sha,
        scheduler_export_snapshot,
    )
    captures_by_tuple = {
        (capture["task_id"], capture["arm_id"], capture["attempt"]): capture
        for capture in captures
    }
    v2 = load_v2_module()
    records: list[dict[str, Any]] = []
    for task_id in v2.TASK_IDS:
        for arm in v2.ARMS:
            for attempt in v2.ATTEMPTS:
                capture = captures_by_tuple[(task_id, arm, attempt)]
                base = dict(capture["base_candidate_record"])
                billed = base["billed_cost_usd"]
                if billed is None:
                    billed_status = "CANNOT_CHECK"
                    generation_billed = None
                else:
                    try:
                        v2._validate_canonical_decimal(billed, "billed_cost_usd")
                    except Exception as exc:
                        raise ContractError(
                            "available billed_cost_usd must already be one canonical decimal string"
                        ) from exc
                    billed_status = "AVAILABLE"
                    generation_billed = billed
                gpu_count = _validate_canonical_uint(
                    capture["exclusive_gpu_count"], "exclusive_gpu_count", positive=True
                )
                elapsed_ns = _validate_canonical_uint(
                    capture["monotonic_elapsed_ns"], "monotonic_elapsed_ns"
                )
                record = {
                    **base,
                    "generation_cost_quantity": _allocated_ns_to_seconds(
                        gpu_count * elapsed_ns
                    ),
                    "generation_billed_cost_usd": generation_billed,
                    "generation_billed_cost_status": billed_status,
                    "cost_metric_id": v2.METRIC_ID,
                    "cost_gate_metric_binding_sha256": validated_plan[
                        "cost_gate_metric_binding_sha256"
                    ],
                    "exclusive_gpu_count": capture["exclusive_gpu_count"],
                    "timing_provenance_sha256": validated_plan[
                        "cost_measurement_binding_sha256"
                    ],
                    "monotonic_start_ns": capture["monotonic_start_ns"],
                    "monotonic_end_ns": capture["monotonic_end_ns"],
                    "monotonic_elapsed_ns": capture["monotonic_elapsed_ns"],
                    "accelerator_allocation_status": FINAL_ALLOCATION_STATUS,
                }
                records.append(record)
    ledger = {
        "schema_version": v2.LEDGER_SCHEMA,
        "split": v2.PRODUCTION_SPLIT,
        "run_plan_sha256": expected_plan_sha,
        "cost_gate_metric": dict(validated_plan["cost_gate_metric"]),
        "cost_gate_metric_binding_sha256": validated_plan[
            "cost_gate_metric_binding_sha256"
        ],
        "cost_measurement_binding_sha256": validated_plan[
            "cost_measurement_binding_sha256"
        ],
        "cost_accounting": v2.COST_ACCOUNTING,
        "records": records,
    }
    try:
        v2._validate_candidate_ledger(
            ledger,
            validated_plan,
            expected_task_ids=v2.TASK_IDS,
            expected_run_plan_sha256=expected_plan_sha,
        )
    except Exception as exc:
        raise ContractError(f"final Runner V2 candidate ledger rejected: {exc}") from exc

    seal = {
        "schema_version": ADAPTER_SEAL_SCHEMA,
        "authority": "GENERATION_ADAPTER_EVIDENCE_BINDING_ONLY__NO_EVALUATOR_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "status": "ADAPTER_CONFORMANCE_PASS__V2_CANDIDATE_LEDGER_EMITTED__OUTCOMES_NOT_OPENED",
        "adapter_contract_sha256": CONTRACT_SHA256,
        "adapter_module_sha256": sha256_file(Path(__file__).resolve()),
        "runner_v2_contract_sha256": RUNNER_V2_CONTRACT_SHA256,
        "runner_v2_module_sha256": RUNNER_V2_MODULE_SHA256,
        "runner_v1_module_sha256": RUNNER_V1_MODULE_SHA256,
        "run_plan_sha256": expected_plan_sha,
        "capture_ledger_canonical_sha256": canonical_hash(captures),
        "scheduler_evidence_canonical_sha256": canonical_hash(scheduler_evidence),
        "scheduler_config_snapshot_sha256": sha256_bytes(scheduler_config_snapshot),
        "scheduler_export_snapshot_sha256": sha256_bytes(scheduler_export_snapshot),
        "scheduler_raw_record_hash_set_sha256": allocation_index[
            "scheduler_raw_record_hash_set_sha256"
        ],
        "allocation_index_canonical_sha256": canonical_hash(allocation_index),
        "candidate_ledger_canonical_sha256": canonical_hash(ledger),
        "candidate_record_count": len(records),
        "allocation_status_written_only_after_scheduler_finalization": True,
        "cross_job_raw_monotonic_comparison_used": False,
        "missing_billed_usd_imputed_as_zero": False,
        "candidate_bodies_opened": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }
    return ledger, allocation_index, seal


def _write_new_canonical_json_with_identity(
    path: Path | str, value: Any
) -> tuple[str, tuple[int, int]]:
    candidate = Path(path)
    payload = canonical_json_bytes(value) + b"\n"
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(candidate, flags, 0o600)
    except FileExistsError as exc:
        raise ContractError(f"output destination already exists: {candidate}") from exc
    except OSError as exc:
        raise ContractError(f"output destination cannot be created: {candidate}") from exc
    try:
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise ContractError(f"short write to output destination: {candidate}")
            view = view[written:]
        os.fsync(fd)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ContractError(f"output destination is not a regular file: {candidate}")
        os.lseek(fd, 0, os.SEEK_SET)
        observed_parts = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            observed_parts.append(chunk)
        observed = b"".join(observed_parts)
        if observed != payload:
            raise ContractError(f"output byte/hash verification failed: {candidate}")
        path_info = candidate.stat()
        if (path_info.st_dev, path_info.st_ino) != (info.st_dev, info.st_ino):
            raise ContractError(f"output destination identity changed: {candidate}")
        return sha256_bytes(observed), (info.st_dev, info.st_ino)
    except Exception:
        try:
            info = os.fstat(fd)
            path_info = candidate.stat()
            if (path_info.st_dev, path_info.st_ino) == (info.st_dev, info.st_ino):
                candidate.unlink()
        except OSError:
            pass
        raise
    finally:
        os.close(fd)


def write_new_canonical_json(path: Path | str, value: Any) -> str:
    observed_sha256, _ = _write_new_canonical_json_with_identity(path, value)
    return observed_sha256


def _rollback_unchanged_output(
    path: Path | str, expected_sha256: str, expected_identity: tuple[int, int]
) -> bool:
    """Remove only an output this process created and which remains unchanged."""

    candidate = Path(path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(candidate, flags)
    except OSError:
        return False
    try:
        info = os.fstat(fd)
        if (
            not stat.S_ISREG(info.st_mode)
            or (info.st_dev, info.st_ino) != expected_identity
        ):
            return False
        observed_parts = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            observed_parts.append(chunk)
        if sha256_bytes(b"".join(observed_parts)) != expected_sha256:
            return False
        path_info = candidate.lstat()
        if (
            not stat.S_ISREG(path_info.st_mode)
            or (path_info.st_dev, path_info.st_ino) != expected_identity
        ):
            return False
        candidate.unlink()
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def _validate_cli_paths(inputs: Mapping[str, Path], outputs: Mapping[str, Path]) -> None:
    all_paths = {**inputs, **outputs}
    resolved: dict[str, Path] = {}
    identities: dict[str, tuple[int, int]] = {}
    for label, path in all_paths.items():
        if not path.is_absolute():
            raise ContractError(f"{label} must be absolute")
        resolved[label] = path.resolve(strict=False)
        try:
            info = path.stat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ContractError(f"{label} cannot be inspected: {path}") from exc
        identities[label] = (info.st_dev, info.st_ino)
    labels = list(all_paths)
    for left_index, left in enumerate(labels):
        for right in labels[left_index + 1 :]:
            if resolved[left] == resolved[right]:
                raise ContractError(f"CLI paths alias: {left} and {right}")
            if left in identities and right in identities and identities[left] == identities[right]:
                raise ContractError(f"CLI paths alias by device/inode: {left} and {right}")
    for label, path in outputs.items():
        if path.exists() or path.is_symlink():
            raise ContractError(f"output destination already exists: {label}: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Finalize outcome-blind LUNARC generation timing/allocation evidence"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--run-plan", required=True, type=Path)
    finalize.add_argument("--capture-ledger", required=True, type=Path)
    finalize.add_argument("--scheduler-evidence", required=True, type=Path)
    finalize.add_argument("--scheduler-config-snapshot", required=True, type=Path)
    finalize.add_argument("--scheduler-export-snapshot", required=True, type=Path)
    finalize.add_argument("--output-ledger", required=True, type=Path)
    finalize.add_argument("--output-allocation-index", required=True, type=Path)
    finalize.add_argument("--output-adapter-seal", required=True, type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    created_outputs: list[tuple[Path, str, tuple[int, int]]] = []
    try:
        _validate_cli_paths(
            {
                "run plan": args.run_plan,
                "capture ledger": args.capture_ledger,
                "scheduler evidence": args.scheduler_evidence,
                "scheduler config snapshot": args.scheduler_config_snapshot,
                "scheduler export snapshot": args.scheduler_export_snapshot,
            },
            {
                "output ledger": args.output_ledger,
                "output allocation index": args.output_allocation_index,
                "output adapter seal": args.output_adapter_seal,
            },
        )
        _, run_plan_sha256, plan = read_json_snapshot(args.run_plan, "run plan")
        _, _, capture_ledger = read_json_snapshot(args.capture_ledger, "capture ledger")
        _require_exact_fields(capture_ledger, {"records"}, "capture ledger")
        _, _, evidence = read_json_snapshot(args.scheduler_evidence, "scheduler evidence")
        try:
            scheduler_config_snapshot = args.scheduler_config_snapshot.read_bytes()
            scheduler_export_snapshot = args.scheduler_export_snapshot.read_bytes()
        except OSError as exc:
            raise ContractError("scheduler snapshot input is unreadable") from exc
        ledger, allocation_index, seal = finalize_v2_candidate_ledger(
            plan,
            run_plan_sha256,
            capture_ledger["records"],
            evidence,
            scheduler_config_snapshot,
            scheduler_export_snapshot,
        )
        ledger_file_sha, ledger_identity = _write_new_canonical_json_with_identity(
            args.output_ledger, ledger
        )
        created_outputs.append((args.output_ledger, ledger_file_sha, ledger_identity))
        index_file_sha, index_identity = _write_new_canonical_json_with_identity(
            args.output_allocation_index, allocation_index
        )
        created_outputs.append(
            (args.output_allocation_index, index_file_sha, index_identity)
        )
        seal["candidate_ledger_file_sha256"] = ledger_file_sha
        seal["allocation_index_file_sha256"] = index_file_sha
        seal["output_policy"] = "NEW_O_EXCL_MODE_0600__FSYNC_REREAD_HASH_AND_IDENTITY_VERIFIED"
        seal_file_sha, seal_identity = _write_new_canonical_json_with_identity(
            args.output_adapter_seal, seal
        )
        created_outputs.append((args.output_adapter_seal, seal_file_sha, seal_identity))
    except ContractError as exc:
        for path, expected_sha256, expected_identity in reversed(created_outputs):
            _rollback_unchanged_output(path, expected_sha256, expected_identity)
        parser.error(str(exc))
    print(
        "P1_SAB_LUNARC_GENERATION_ADAPTER_CONFORMANCE_PASS "
        "records=918 official_tasks=0 official_outcomes=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
