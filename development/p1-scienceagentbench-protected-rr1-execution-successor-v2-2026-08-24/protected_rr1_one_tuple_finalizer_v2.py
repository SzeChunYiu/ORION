#!/usr/bin/env python3
"""Fail-closed post-job metadata finalizer for one protected RR1 tuple.

The capture entrypoint executes only the frozen read-only scheduler queries;
the finalizer parses their retained bytes and body-free runtime metadata.  No
job submission, generation, evaluation, external API, or network route exists.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
CONTRACT_PATH = ROOT / "FINALIZER_CONTRACT_V2.json"
SCHEMA_PATH = ROOT / "FINALIZER_OUTPUT_SCHEMA_V2.json"
CONTRACT_SHA256 = "a6692154fe3bc308522a377ad1ba57647f07f59f8da5455c56a1fd8f1a037cc3"
SCHEMA_SHA256 = "66a09148fa724cf804146dc2a085e2d1e7a52859d59f94fa0648e6b2c3b71824"
NORMALIZED_MODULE_SHA256 = "a902c977a22da7182cbecb15cd18acc2b47c0038adcd4c7517bc9bde7ffadac4"

ADAPTER_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py"
)
ADAPTER_CONTRACT_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/LUNARC_GENERATION_ADAPTER_CONTRACT_V1.json"
)
ADAPTER_SHA256 = "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9"
ADAPTER_CONTRACT_SHA256 = "ae8fe86e4052b65f12176980fb03a653c1ab4b5b4f99c146d0db401563d93883"
DIRECT_ROUTE_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24/protected_rr1_direct_route_v1.py"
)
DIRECT_ROUTE_CONTRACT_PATH = DIRECT_ROUTE_PATH.parent / "PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V1.json"
DIRECT_ROUTE_FINALIZATION_PATH = DIRECT_ROUTE_PATH.parent / "ONE_TUPLE_FINALIZATION_CONTRACT_V1.json"
DIRECT_ROUTE_SHA256SUMS_PATH = DIRECT_ROUTE_PATH.parent / "SHA256SUMS"
DIRECT_ROUTE_SHA256 = "7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91"
DIRECT_ROUTE_CONTRACT_SHA256 = "a091bf0617d657ee7f8c2bcab08acda96d16246407d791d6a90704efffedc398"
DIRECT_ROUTE_FINALIZATION_SHA256 = "340cc4f8bffac425d5de05a531d20452aacf440fa948de7738f2b5fdfa643a11"
DIRECT_ROUTE_SHA256SUMS_SHA256 = "dac2f45a7b862d789a9e672938dccd1175d611c396f6aff3c1294258416fb4d1"

FIXED_TUPLE = {"task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101}
FIXED_STAGE_TUPLE = {"task_id": "1", "arm_id": "RR", "attempt": 1}
SUCCESS_NAME = "ONE_TUPLE_FINALIZATION_RECEIPT_V1.json"
CANNOT_NAME = "ONE_TUPLE_FINALIZATION_CANNOT_CHECK_V1.json"
SUCCESS_STATUS = "PASS_ONE_TUPLE_POST_JOB_METADATA_FINALIZATION"
CANNOT_STATUS = "CANNOT_CHECK_ONE_TUPLE_FINALIZATION"

SACCT_FIELDS = (
    "JobIDRaw", "Partition", "State", "ExitCode", "DerivedExitCode",
    "Submit", "Eligible", "Start", "End", "TimelimitRaw", "Elapsed",
    "NodeList", "NNodes", "NCPUS", "NTasks", "ReqCPUS", "ReqMem",
    "ReqTRES", "AllocTRES", "Account", "QOS", "Constraints",
    "Reservation", "Reason",
)
TERMINAL_STATES = {
    "BOOT_FAIL", "CANCELLED", "COMPLETED", "DEADLINE", "FAILED",
    "NODE_FAIL", "OUT_OF_MEMORY", "PREEMPTED", "REVOKED", "TIMEOUT",
}
TERMINAL_ACCOUNTING_INCOMPLETE_NORMALIZATION = {
    "Partition": "gpua40i",
    "ExitCode": "0:0",
    "DerivedExitCode": "0:0",
    "Submit": "1970-01-01T00:00:00",
    "Eligible": "1970-01-01T00:00:00",
    "Start": "1970-01-01T00:00:00",
    "End": "1970-01-01T00:00:00",
    "TimelimitRaw": "60",
    "NodeList": "sentinel-node",
    "NNodes": "1",
    "NCPUS": "8",
    "ReqCPUS": "8",
    "ReqMem": "64G",
    "ReqTRES": "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
    "AllocTRES": "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
    "Account": "lu2026-2-51",
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
UINT_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")
JOB_RE = re.compile(r"^[1-9][0-9]*$")
CLUSTER_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
NODE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
GPU_UUID_RE = re.compile(
    r"^GPU-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
SLURM_TIME_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$")
UTC_TIME_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$"
)
EXIT_RE = re.compile(r"^(?:0|[1-9][0-9]*):(?:0|[1-9][0-9]*)$")
FORBIDDEN_JSON_KEYS = {
    "masked_packet", "recovered_packet", "prompt_body", "completion_body",
    "token_ids", "evaluator_material", "credentials",
}
FORBIDDEN_JSON_KEY_ALIASES = {
    "maskedpacket", "recoveredpacket", "promptbody", "completionbody",
    "tokenids", "evaluatormaterial", "credentials",
}
SELF_BINDING_CONSTANT_RE = re.compile(
    rb'(?m)^(CONTRACT_SHA256|SCHEMA_SHA256|NORMALIZED_MODULE_SHA256) = "[0-9a-f]{64}"$'
)

CAPTURE_ROOT_COMMON = (
    "POST_JOB_SACCT_V1.txt",
    "POST_JOB_SACCT_NONOVERLAP_V1.txt",
    "POST_JOB_SCONTROL_V1.txt",
    "SCHEDULER_CONFIG_V1.txt",
    "SCHEDULER_PARTITION_V1.txt",
    "SCHEDULER_NODE_V1.txt",
    "SCHEDULER_CAPTURE_PROVENANCE_V1.json",
)
EVIDENCE_ROOT_COMMON = (
    "GPU_ALLOCATION_IDENTITY_V1.json",
    "SERVER_CLEANUP_V1.json",
    "STAGED_RUNTIME_INPUT_V1.json",
    "PROCESS_ATTESTATION_V1.json",
)
ATTEMPT_COMMON = (
    "SCONTROL_IN_JOB_V1.txt",
    "SLURM_IDENTITY_AND_SNAPSHOT_V1.json",
)
SUCCESS_PAIR = (
    "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json",
    "DIRECT_ROUTE_BRIDGE_BINDING_V1.json",
    "ATTEMPT_CAPTURE_V1.json",
)
FAILURE_PAIR = (
    "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json",
    "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json",
)

EXPORT_FIELDS = {
    "schema_version", "authority", "status", "tuple_identity",
    "slurm_job_identity", "capture_argv", "source_sha256",
    "in_job_snapshot_sha256", "scheduler_record_source",
    "scheduler_job_state", "scheduler_exit_code", "allocation_started_at",
    "allocation_ended_at", "node_name", "allocated_gpu_count",
    "partition", "account", "allocated_cpu_count", "allocated_memory",
    "timelimit_raw_minutes", "constraints",
    "gpu_allocations", "exclusive_gres_status", "attempt_scope_status",
    "nonoverlap_query_status", "nonoverlap_conflict_count",
    "whole_node_exclusivity_claimed", "protected_bodies_retained",
    "official_evaluator_invoked", "official_outcomes_opened",
    "runner_v2_population_ledger_status", "production_admissibility",
    "scientific_authority_delta",
}
DYNAMIC_CORE_FIELDS = {
    "phase_id", "rendered_prompt_sha256", "tokenize_request_sha256",
    "tokenize_repeat_count", "tokenize_raw_response_sha256",
    "token_array_sha256", "prompt_tokens", "phase_output_cap",
    "context_window_tokens", "remaining_context_margin_tokens",
    "completion_prompt_n_equal", "status",
}
DYNAMIC_FIELDS = DYNAMIC_CORE_FIELDS | {
    "schema_version", "authority", "tuple_identity", "protected_bodies_retained",
    "production_admissibility", "scientific_authority_delta",
}
BRIDGE_FIELDS = {
    "schema_version", "authority", "status", "tuple_identity",
    "run_plan_binding_extension", "run_plan_binding_extension_sha256",
    "runtime_stage_sha256", "process_attestation_sha256",
    "attempt_capture_canonical_sha256", "request_bindings",
    "dynamic_rr1_pretokenize_binding",
    "dynamic_rr1_pretokenize_binding_canonical_sha256",
    "dynamic_rr1_pretokenize_file_sha256", "protected_bodies_retained",
    "runner_v2_population_ledger_status", "allocation_status",
    "production_admissibility", "scientific_authority_delta",
}
EXPECTED_STAGE_SOURCE_SHA256 = {
    "plan": "66d54431f6d8ac479b2009759a4cd7b6d5f7d489f4b8f4b6a99d0f591616cc81",
    "owner": "a94fba71c1d51a0b60f4ee2ab44da85ca139373070efc3d13c41e2c63c0e3dce",
    "runtime": "2bf1150adf32239cd7603c3bb92ea0c728e1a9f28388b6d7c89aeb22b2db5019",
    "masked": "405f5836a21192d0a6d21e4b85143865fec8a2fb7cd9a4eb62100862b9d1a3df",
    "recovered": "3fce9e45e3012845d7dec2e343c224b43a4d79dea0c1192e5bf1972652733722",
    "model": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
    "server": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
    "backend": "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb",
    "launcher": "a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219",
}
EXPECTED_STAGE_EXTENSION = {
    "run_plan_sha256": EXPECTED_STAGE_SOURCE_SHA256["plan"],
    "direct_driver_sha256": "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
    "direct_contract_sha256": "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    "direct_prompt_bundle_sha256": "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    "adapter_sha256": ADAPTER_SHA256,
    "upstream_wrapper_sha256": "1d4655350c1a037cd4e51ee11e15e21491c5bfd7cea125948beb2e152c73b582",
    "upstream_wrapper_execution_allowed": False,
    "upstream_wrapper_binding_role": "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
    "preflight_bridge_sha256": DIRECT_ROUTE_SHA256,
    "prompt_binding_mode": "PROSPECTIVE_STATIC_HASH_OR_DYNAMIC_SEALED_RR_STATE_RULE",
    "merged_slurm_bridge_donor_sha256": "93ee3abec947a2b6fe6b9a4d1fb7871bbee56c1e190430c4193431a640c93006",
    "dynamic_rr1_pretokenize": {
        "route": "POST /tokenize", "add_special": True, "parse_special": True,
        "repeat_count": 3, "phase_output_cap": 7168,
        "context_window_tokens": 32768,
        "completion_prompt_n_equality_required": True,
    },
    "tuple_freeze_sha256": "eb06634717a6e7ae5aa69d817fc61c285b961b5d72d128405b891c8dcf0c3a47",
}
STAGE_FIELDS = {
    "schema_version", "authority", "status", "tuple_identity", "source_paths",
    "source_sha256", "runtime_observed_sha256", "run_plan_binding_extension",
    "server_argv", "allocation_status", "production_admissibility",
    "scientific_authority_delta", "prompt_commitments_by_phase",
    "run_plan_binding_extension_sha256", "tuple_seed", "protected_body_retention",
}
PROCESS_FIELDS = {
    "schema_version", "authority", "status", "runtime_stage_sha256",
    "process_identity", "listener", "readiness", "model_sha256",
    "llama_server_sha256", "cuda_backend_sha256", "launcher_sha256",
    "successor_bridge_sha256", "server_stdout_stderr_retained",
    "protected_bodies_retained", "production_admissibility",
    "scientific_authority_delta",
}
PROCESS_IDENTITY_FIELDS = {
    "pid", "executable_path", "executable_sha256", "executable_device",
    "executable_inode", "argv", "cmdline_sha256", "ggml_backend_path",
    "cuda_backend_mapped_path", "cuda_backend_sha256", "model_mapped_path",
    "model_sha256", "proxy_environment_empty",
}
CAPTURE_PROVENANCE_FIELDS = {
    "schema_version", "authority", "status", "slurm_job_id", "partition",
    "node_name", "allocation_started_at", "allocation_ended_at", "capture_argv",
    "raw_file_sha256", "credential_environment_read", "stderr_retained",
    "job_submitted", "scientific_authority_delta",
    "terminal_poll_interval_seconds", "terminal_poll_limit",
    "terminal_poll_count", "terminal_poll_observations",
    "partition_source", "node_source",
    "capture_command_timeout_seconds", "post_terminal_capture_deadline_seconds",
    "post_job_scontrol_start_latency_limit_seconds",
    "terminal_observed_at_utc", "terminal_observed_monotonic_ns",
    "post_job_scontrol_started_at_utc",
    "post_job_scontrol_start_seconds_after_terminal_observation",
    "post_job_scontrol_completed_at_utc",
    "post_job_scontrol_seconds_after_terminal_observation",
    "capture_command_observations",
}

TERMINAL_POLL_INTERVAL_SECONDS = 5
TERMINAL_POLL_LIMIT = 1440
CAPTURE_COMMAND_TIMEOUT_SECONDS = 20
POST_TERMINAL_CAPTURE_DEADLINE_SECONDS = 240
POST_JOB_SCONTROL_START_LATENCY_LIMIT_SECONDS = 2
FROZEN_SBATCH_STDOUT_PATH = Path(
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDOUT_V1.txt"
)


class FinalizationError(ValueError):
    """Evidence cannot support the bounded one-tuple pass receipt."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code


def parse_sbatch_parsable_job_id(payload: bytes) -> str:
    """Parse the exact body-free `sbatch --parsable` response accepted by handoff."""
    if not isinstance(payload, bytes) or not payload:
        raise FinalizationError(
            "SBATCH_JOB_ID_INVALID", "sbatch --parsable stdout is empty or nonbytes"
        )
    if not payload.endswith(b"\n"):
        raise FinalizationError(
            "SBATCH_JOB_ID_INVALID", "sbatch --parsable stdout lacks its exact final LF"
        )
    candidate = payload[:-1]
    if not candidate or b"\n" in candidate or b"\r" in payload:
        raise FinalizationError(
            "SBATCH_JOB_ID_INVALID", "sbatch --parsable stdout is not one exact LF-terminated line"
        )
    try:
        job_id = candidate.decode("ascii")
    except UnicodeDecodeError as exc:
        raise FinalizationError(
            "SBATCH_JOB_ID_INVALID", "sbatch --parsable stdout is not ASCII"
        ) from exc
    if JOB_RE.fullmatch(job_id) is None:
        raise FinalizationError(
            "SBATCH_JOB_ID_INVALID",
            "sbatch --parsable stdout is not one canonical positive decimal job ID",
        )
    return job_id


def _typed_unexpected_failure(
    exc: Exception, code: str, detail: str
) -> FinalizationError:
    if isinstance(exc, FinalizationError):
        return exc
    return FinalizationError(code, f"{detail}; exception_type={type(exc).__name__}")


class DuplicateJsonMemberError(ValueError):
    pass


class CliArgs:
    def __init__(self, evidence_root: Path, capture_root: Path, output_root: Path):
        self.evidence_root = evidence_root
        self.capture_root = capture_root
        self.output_root = output_root


class CaptureArgs:
    def __init__(self, job_id: str, output_root: Path):
        self.job_id = job_id
        self.output_root = output_root


class SbatchJobIdArgs:
    def __init__(self, input_path: Path):
        self.input_path = input_path


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "value is not canonical JSON") from exc


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def normalized_module_bytes(payload: bytes) -> bytes:
    """Zero the three embedded hash constants to break the binding cycle."""
    seen: set[bytes] = set()

    def replace(match: re.Match[bytes]) -> bytes:
        name = match.group(1)
        if name in seen:
            raise FinalizationError("SELF_BINDING_INVALID", "duplicate module binding constant")
        seen.add(name)
        return name + b' = "' + (b"0" * 64) + b'"'

    normalized = SELF_BINDING_CONSTANT_RE.sub(replace, payload)
    expected = {b"CONTRACT_SHA256", b"SCHEMA_SHA256", b"NORMALIZED_MODULE_SHA256"}
    if seen != expected:
        raise FinalizationError("SELF_BINDING_INVALID", "module binding constants are not exact")
    return normalized


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} is not lowercase SHA-256")
    return value


def _require_exact(value: Any, fields: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} fields are not exact")
    return value


def _require_false_boundaries(value: Mapping[str, Any], label: str) -> None:
    for field in ("protected_bodies_retained", "official_evaluator_invoked", "official_outcomes_opened"):
        if field in value and value[field] is not False:
            raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", f"{label} authority boundary drift")
    if value.get("production_admissibility", "CANNOT_CHECK") != "CANNOT_CHECK":
        raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", f"{label} production authority drift")
    if value.get("scientific_authority_delta", "NONE") != "NONE":
        raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", f"{label} scientific authority drift")


def _reject_forbidden_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            alias = re.sub(r"[^a-z0-9]", "", key.casefold())
            if key in FORBIDDEN_JSON_KEYS or alias in FORBIDDEN_JSON_KEY_ALIASES:
                raise FinalizationError("FORBIDDEN_BODY_FIELD", f"forbidden metadata key: {key}")
            _reject_forbidden_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_forbidden_keys(child)


def _reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonMemberError(key)
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> Any:
    raise ValueError(value)


def strict_json(payload: bytes, label: str, adapter: ModuleType) -> dict[str, Any]:
    if not payload.endswith(b"\n") or payload.endswith(b"\r\n") or b"\r" in payload:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} must have one LF-only ending")
    try:
        value = adapter.strict_json_object_from_bytes(payload, label, label)
    except Exception as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} strict JSON rejected") from exc
    if payload != canonical_bytes(value) + b"\n":
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} is not canonical JSON plus one LF")
    _reject_forbidden_keys(value)
    return value


def parse_cli(argv: Sequence[str]) -> CliArgs:
    actual = list(argv)
    if (
        len(actual) != 7
        or actual[0] != "finalize"
        or actual[1] != "--evidence-root"
        or actual[3] != "--capture-root"
        or actual[5] != "--output-root"
    ):
        raise FinalizationError("ARGV_INVALID", "argv must equal the frozen finalize form")
    evidence = Path(actual[2])
    capture = Path(actual[4])
    output = Path(actual[6])
    if (
        not evidence.is_absolute()
        or not capture.is_absolute()
        or not output.is_absolute()
        or len({evidence, capture, output}) != 3
    ):
        raise FinalizationError("ARGV_INVALID", "evidence, capture, and output roots must be distinct absolute paths")
    return CliArgs(evidence, capture, output)


def parse_capture_cli(argv: Sequence[str]) -> CaptureArgs:
    actual = list(argv)
    if (
        len(actual) != 5
        or actual[0] != "watch-capture"
        or actual[1] != "--job-id"
        or actual[3] != "--output-root"
    ):
        raise FinalizationError("ARGV_INVALID", "argv must equal the frozen watch-capture form")
    job_id, raw_output = actual[2], actual[4]
    output = Path(raw_output)
    if JOB_RE.fullmatch(job_id) is None:
        raise FinalizationError("ARGV_INVALID", "capture job is outside the freeze")
    if not output.is_absolute():
        raise FinalizationError("ARGV_INVALID", "capture output root must be absolute")
    return CaptureArgs(job_id, output)


def parse_sbatch_job_id_cli(argv: Sequence[str]) -> SbatchJobIdArgs:
    actual = list(argv)
    if (
        len(actual) != 3
        or actual[0] != "parse-sbatch-job-id"
        or actual[1] != "--input-path"
    ):
        raise FinalizationError(
            "ARGV_INVALID",
            "argv must equal the frozen parse-sbatch-job-id input-path form",
        )
    input_path = Path(actual[2])
    if input_path != FROZEN_SBATCH_STDOUT_PATH:
        raise FinalizationError(
            "ARGV_INVALID", "sbatch stdout input path differs from the exact freeze"
        )
    return SbatchJobIdArgs(input_path)


def _open_directory(path: Path, label: str) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
        info = os.fstat(fd)
    except OSError as exc:
        raise FinalizationError("INPUT_SET_INVALID", f"{label} is not a pinned directory") from exc
    if (
        not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o700
        or info.st_uid != os.getuid()
    ):
        os.close(fd)
        raise FinalizationError("INPUT_SET_INVALID", f"{label} is not one private owned directory")
    return fd


def _open_child_directory(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise FinalizationError("INPUT_SET_INVALID", f"required directory is unavailable: {name}") from exc
    info = os.fstat(fd)
    if (
        not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o700
        or info.st_uid != os.getuid()
    ):
        os.close(fd)
        raise FinalizationError("INPUT_SET_INVALID", f"required directory is not regular: {name}")
    return fd


def _entry_exists(parent_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise FinalizationError("INPUT_SET_INVALID", f"cannot inspect evidence entry: {name}") from exc


def _read_held(
    parent_fd: int, name: str, label: str, max_bytes: int = 2_000_000,
    *, allowed_modes: frozenset[int] = frozenset({0o400, 0o600}),
) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
        before = os.fstat(fd)
        evidence_mode = stat.S_IMODE(before.st_mode)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_size <= 0
            or before.st_size > max_bytes
            or before.st_nlink != 1
            or before.st_uid != os.getuid()
            or evidence_mode not in allowed_modes
        ):
            raise FinalizationError("INPUT_SET_INVALID", f"{label} is not one bounded regular file")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(fd, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        after = os.fstat(fd)
        named_after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FinalizationError:
        raise
    except OSError as exc:
        raise FinalizationError("INPUT_SET_INVALID", f"{label} cannot be read by held descriptor") from exc
    finally:
        if "fd" in locals():
            os.close(fd)
    if (
        remaining != 0
        or len(payload) != before.st_size
        or not stat.S_ISREG(after.st_mode)
        or not stat.S_ISREG(named_after.st_mode)
        or after.st_uid != os.getuid()
        or named_after.st_uid != os.getuid()
        or after.st_nlink != 1
        or named_after.st_nlink != 1
        or stat.S_IMODE(after.st_mode) not in allowed_modes
        or stat.S_IMODE(named_after.st_mode) not in allowed_modes
        or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        or (named_after.st_dev, named_after.st_ino, named_after.st_size, named_after.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    ):
        raise FinalizationError("INPUT_SET_INVALID", f"{label} changed or was replaced during held read")
    return payload


def read_sbatch_job_id_file(path: Path) -> str:
    """Descriptor-safely read and parse one private raw sbatch stdout file."""
    if path != FROZEN_SBATCH_STDOUT_PATH:
        raise FinalizationError(
            "ARGV_INVALID", "sbatch stdout input path differs from the exact freeze"
        )
    parent_fd = _open_directory(path.parent, "sbatch stdout parent")
    try:
        payload = _read_held(
            parent_fd,
            path.name,
            "sbatch stdout",
            max_bytes=4096,
            allowed_modes=frozenset({0o600}),
        )
    finally:
        os.close(parent_fd)
    return parse_sbatch_parsable_job_id(payload)


def _create_output_root(path: Path) -> int:
    if not path.is_absolute() or path.name in {"", ".", ".."}:
        raise FinalizationError("OUTPUT_INVALID", "output root must be a new absolute directory")
    parent_fd = _open_directory(path.parent, "output parent")
    created = False
    created_identity: tuple[int, int] | None = None
    fd: int | None = None
    try:
        os.mkdir(path.name, mode=0o700, dir_fd=parent_fd)
        created = True
        initial = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        created_identity = (initial.st_dev, initial.st_ino)
        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path.name, flags, dir_fd=parent_fd)
        os.chmod(path.name, 0o700, dir_fd=parent_fd, follow_symlinks=False)
        held = os.fstat(fd)
        named = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISDIR(held.st_mode)
            or (held.st_dev, held.st_ino) != (named.st_dev, named.st_ino)
            or held.st_uid != os.getuid()
            or stat.S_IMODE(named.st_mode) != 0o700
        ):
            raise OSError("new output directory identity or mode mismatch")
    except OSError as exc:
        if fd is not None:
            os.close(fd)
            fd = None
        if created:
            try:
                current = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                if (
                    stat.S_ISDIR(current.st_mode)
                    and (current.st_dev, current.st_ino) == created_identity
                ):
                    os.rmdir(path.name, dir_fd=parent_fd)
            except OSError:
                pass
        raise FinalizationError("OUTPUT_INVALID", "output root must be exclusively creatable") from exc
    finally:
        os.close(parent_fd)
    if fd is None:
        raise FinalizationError("OUTPUT_INVALID", "output directory descriptor is unavailable")
    return fd


def _write_new_json(
    output_fd: int, name: str, value: Mapping[str, Any]
) -> tuple[str, tuple[int, int]]:
    payload = canonical_bytes(value) + b"\n"
    expected_sha = sha256_bytes(payload)
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = None
    created_identity: tuple[int, int] | None = None
    try:
        fd = os.open(name, flags, 0o600, dir_fd=output_fd)
        os.fchmod(fd, 0o600)
        created = os.fstat(fd)
        created_identity = (created.st_dev, created.st_ino)
        written = 0
        while written < len(payload):
            count = os.write(fd, payload[written:])
            if count <= 0:
                raise OSError("short write")
            written += count
        os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        observed = b""
        while len(observed) < len(payload):
            chunk = os.read(fd, len(payload) - len(observed))
            if not chunk:
                break
            observed += chunk
        final_info = os.fstat(fd)
        parent_info = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
        if (
            observed != payload
            or sha256_bytes(observed) != expected_sha
            or (final_info.st_dev, final_info.st_ino) != created_identity
            or (parent_info.st_dev, parent_info.st_ino) != created_identity
            or not stat.S_ISREG(parent_info.st_mode)
            or parent_info.st_nlink != 1
            or stat.S_IMODE(parent_info.st_mode) != 0o600
        ):
            raise OSError("receipt identity or byte verification failed")
    except OSError as exc:
        if created_identity is not None:
            try:
                current = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == created_identity:
                    os.unlink(name, dir_fd=output_fd)
            except OSError:
                pass
        raise FinalizationError("OUTPUT_INVALID", f"cannot create final receipt: {name}") from exc
    finally:
        if fd is not None:
            os.close(fd)
    if created_identity is None:
        raise FinalizationError("OUTPUT_INVALID", f"receipt identity is unavailable: {name}")
    return expected_sha, created_identity


def _write_new_bytes(
    output_fd: int, name: str, payload: bytes
) -> tuple[str, tuple[int, int]]:
    if not isinstance(payload, bytes) or not payload:
        raise FinalizationError("OUTPUT_INVALID", f"raw capture is empty: {name}")
    expected_sha = sha256_bytes(payload)
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = None
    identity: tuple[int, int] | None = None
    try:
        fd = os.open(name, flags, 0o600, dir_fd=output_fd)
        os.fchmod(fd, 0o600)
        created = os.fstat(fd)
        identity = (created.st_dev, created.st_ino)
        offset = 0
        while offset < len(payload):
            count = os.write(fd, payload[offset:])
            if count <= 0:
                raise OSError("short raw write")
            offset += count
        os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        observed = b""
        while len(observed) < len(payload):
            chunk = os.read(fd, len(payload) - len(observed))
            if not chunk:
                break
            observed += chunk
        final_info = os.fstat(fd)
        parent_info = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
        if (
            observed != payload
            or sha256_bytes(observed) != expected_sha
            or (final_info.st_dev, final_info.st_ino) != identity
            or (parent_info.st_dev, parent_info.st_ino) != identity
            or parent_info.st_nlink != 1
            or stat.S_IMODE(parent_info.st_mode) != 0o600
        ):
            raise OSError("raw capture verification failed")
    except OSError as exc:
        if identity is not None:
            try:
                current = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == identity:
                    os.unlink(name, dir_fd=output_fd)
            except OSError:
                pass
        raise FinalizationError("OUTPUT_INVALID", f"cannot create raw capture: {name}") from exc
    finally:
        if fd is not None:
            os.close(fd)
    if identity is None:
        raise FinalizationError("OUTPUT_INVALID", f"raw capture identity is unavailable: {name}")
    return expected_sha, identity


def _rollback_new_output_root(
    path: Path,
    output_fd: int,
    identities: Mapping[str, tuple[int, int]],
) -> None:
    """Best-effort rollback without unlinking entries whose identity is unsafe."""
    root_identity = os.fstat(output_fd)
    for name, identity in identities.items():
        try:
            info = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
            if (
                stat.S_ISREG(info.st_mode)
                and info.st_uid == os.getuid()
                and info.st_nlink == 1
                and (info.st_dev, info.st_ino) == identity
            ):
                os.unlink(name, dir_fd=output_fd)
        except FileNotFoundError:
            continue
        except OSError:
            return
    try:
        os.fsync(output_fd)
        parent_fd = _open_directory(path.parent, "output parent")
    except (OSError, FinalizationError):
        return
    try:
        named = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            stat.S_ISDIR(named.st_mode)
            and (named.st_dev, named.st_ino)
            == (root_identity.st_dev, root_identity.st_ino)
        ):
            os.rmdir(path.name, dir_fd=parent_fd)
            os.fsync(parent_fd)
    except OSError:
        pass
    finally:
        os.close(parent_fd)


def _seal_capture_files(
    output_fd: int, identities: Mapping[str, tuple[int, int]]
) -> None:
    """Seal every safely-held capture artifact to exact mode 0400."""
    for name, identity in identities.items():
        try:
            before = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_uid != os.getuid()
                or before.st_nlink != 1
                or (before.st_dev, before.st_ino) != identity
            ):
                raise OSError("capture artifact identity drift")
            os.chmod(name, 0o400, dir_fd=output_fd, follow_symlinks=False)
            after = os.stat(name, dir_fd=output_fd, follow_symlinks=False)
            if (
                (after.st_dev, after.st_ino) != identity
                or stat.S_IMODE(after.st_mode) != 0o400
                or after.st_uid != os.getuid()
                or after.st_nlink != 1
            ):
                raise OSError("capture artifact seal drift")
        except OSError as exc:
            raise FinalizationError(
                "OUTPUT_INVALID", "capture artifacts could not be sealed read-only"
            ) from exc
    try:
        os.fsync(output_fd)
    except OSError as exc:
        raise FinalizationError("OUTPUT_INVALID", "capture root fsync failed") from exc


def load_exact_adapter() -> ModuleType:
    frozen: dict[Path, str | None] = {
        ADAPTER_PATH: ADAPTER_SHA256,
        ADAPTER_CONTRACT_PATH: ADAPTER_CONTRACT_SHA256,
        DIRECT_ROUTE_PATH: DIRECT_ROUTE_SHA256,
        DIRECT_ROUTE_CONTRACT_PATH: DIRECT_ROUTE_CONTRACT_SHA256,
        DIRECT_ROUTE_FINALIZATION_PATH: DIRECT_ROUTE_FINALIZATION_SHA256,
        DIRECT_ROUTE_SHA256SUMS_PATH: DIRECT_ROUTE_SHA256SUMS_SHA256,
        CONTRACT_PATH: CONTRACT_SHA256,
        SCHEMA_PATH: SCHEMA_SHA256,
        Path(__file__).resolve(): None,
    }
    held: dict[Path, bytes] = {}
    for path, expected in frozen.items():
        fd = None
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(path, flags)
            info = os.fstat(fd)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            payload = b"".join(chunks)
            after = os.fstat(fd)
        except OSError as exc:
            raise FinalizationError("DONOR_DRIFT", f"frozen source unreadable: {path.name}") from exc
        finally:
            if fd is not None:
                os.close(fd)
        if not stat.S_ISREG(info.st_mode) or (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise FinalizationError("DONOR_DRIFT", f"frozen source identity drift: {path.name}")
        if expected is not None and sha256_bytes(payload) != expected:
            raise FinalizationError("DONOR_DRIFT", f"frozen source hash drift: {path.name}")
        held[path] = payload
    held_adapter = held.get(ADAPTER_PATH)
    if held_adapter is None:
        raise FinalizationError("DONOR_DRIFT", "exact adapter donor bytes are unavailable")
    name = "p1_one_tuple_exact_adapter_donor"
    module = ModuleType(name)
    module.__file__ = os.fspath(ADAPTER_PATH)
    module.__package__ = ""
    sys.modules[name] = module
    try:
        code = compile(held_adapter, os.fspath(ADAPTER_PATH), "exec")
        exec(code, module.__dict__)
    except Exception as exc:
        sys.modules.pop(name, None)
        raise FinalizationError("DONOR_DRIFT", "exact adapter donor import failed") from exc
    if not callable(getattr(module, "strict_json_object_from_bytes", None)):
        raise FinalizationError("DONOR_DRIFT", "exact adapter donor parser is unavailable")
    contract = strict_json(held[CONTRACT_PATH], "finalizer contract", module)
    schema = strict_json(held[SCHEMA_PATH], "finalizer output schema", module)
    self_payload = held[Path(__file__).resolve()]
    normalized_sha = sha256_bytes(normalized_module_bytes(self_payload))
    binding = contract.get("self_binding")
    if (
        not isinstance(binding, dict)
        or set(binding)
        != {"module_normalization", "normalized_module_sha256", "output_schema_sha256"}
        or binding["module_normalization"]
        != "ZERO_EXACT_CONTRACT_SCHEMA_AND_NORMALIZED_MODULE_SHA256_CONSTANT_ASSIGNMENTS"
        or binding["normalized_module_sha256"] != NORMALIZED_MODULE_SHA256
        or binding["output_schema_sha256"] != SCHEMA_SHA256
        or normalized_sha != NORMALIZED_MODULE_SHA256
        or schema.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-one-tuple-finalizer-output-schema.v2"
    ):
        raise FinalizationError("SELF_BINDING_INVALID", "finalizer contract/module/schema binding drift")
    module._finalizer_contract_bytes = held[CONTRACT_PATH]
    module._finalizer_schema_bytes = held[SCHEMA_PATH]
    module._finalizer_module_bytes = self_payload
    module._finalizer_module_raw_sha256 = sha256_bytes(self_payload)
    try:
        module.verify_frozen_dependencies()
    except Exception as exc:
        raise FinalizationError("DONOR_DRIFT", "adapter donor dependency verification failed") from exc
    return module


def _parse_tres(value: str, label: str) -> dict[str, str]:
    if not isinstance(value, str) or not value:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} TRES is empty")
    result: dict[str, str] = {}
    aliases: set[str] = set()
    for item in value.split(","):
        if "=" not in item:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} TRES item is malformed")
        key, count = item.split("=", 1)
        alias = key.casefold()
        if not key or not count or key != alias or alias in aliases:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} TRES item is ambiguous")
        aliases.add(alias)
        result[key] = count
    return result


def _gpu_tres_count(tres: Mapping[str, str], label: str) -> int:
    generic: int | None = None
    typed_total = 0
    for key, value in tres.items():
        if key == "gres/gpu" or key.startswith("gres/gpu:"):
            if UINT_RE.fullmatch(value) is None:
                raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} GPU TRES count is not canonical")
            if key == "gres/gpu":
                generic = int(value)
            else:
                typed_total += int(value)
    if generic is not None and typed_total and generic != typed_total:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} generic and typed GPU TRES disagree")
    return generic if generic is not None else typed_total


def _parse_slurm_time(value: str, label: str, *, allow_unknown: bool = False) -> datetime | None:
    if allow_unknown and value == "Unknown":
        return None
    if not isinstance(value, str) or SLURM_TIME_RE.fullmatch(value) is None:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} timestamp is not exact Slurm seconds")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} timestamp is invalid") from exc


def parse_sacct_snapshot(
    payload: bytes, *, allow_multiple: bool, require_terminal: bool = True
) -> list[dict[str, str]]:
    if not isinstance(payload, bytes) or not payload or not payload.endswith(b"\n") or b"\r" in payload:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct snapshot must be nonempty LF-only bytes")
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct snapshot is not UTF-8") from exc
    if not allow_multiple and len(lines) != 1:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "terminal sacct must contain exactly one allocation row")
    if not lines:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct snapshot is empty")
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in lines:
        parts = line.split("|")
        if len(parts) != len(SACCT_FIELDS):
            raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct row has wrong explicit field count")
        record = dict(zip(SACCT_FIELDS, parts))
        job_id = record["JobIDRaw"]
        if JOB_RE.fullmatch(job_id) is None or job_id in seen:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct steps, arrays, aliases, or duplicates are forbidden")
        seen.add(job_id)
        if re.fullmatch(r"[A-Z][A-Z_]*", record["State"]) is None:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct state must be one exact uppercase token")
        if EXIT_RE.fullmatch(record["ExitCode"]) is None or EXIT_RE.fullmatch(record["DerivedExitCode"]) is None:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct exit code is not canonical")
        for field in ("Submit", "Eligible", "Start"):
            _parse_slurm_time(record[field], f"sacct {field}")
        _parse_slurm_time(record["End"], "sacct End", allow_unknown=allow_multiple)
        for field in ("NNodes", "NCPUS", "ReqCPUS", "TimelimitRaw"):
            if UINT_RE.fullmatch(record[field]) is None:
                raise FinalizationError("EVIDENCE_PARSE_INVALID", f"sacct {field} is not canonical unsigned decimal")
        if record["NTasks"] != "" and UINT_RE.fullmatch(record["NTasks"]) is None:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", "sacct NTasks is neither empty nor canonical unsigned decimal")
        _parse_tres(record["ReqTRES"], "sacct ReqTRES")
        _parse_tres(record["AllocTRES"], "sacct AllocTRES")
        records.append(record)
    if require_terminal and not allow_multiple and records[0]["State"] not in TERMINAL_STATES:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "terminal sacct state is not terminal")
    return records


def parse_sacct_poll_snapshot(payload: bytes) -> dict[str, str]:
    """Parse only identity/state while a job may legitimately have blank fields."""
    if (
        not isinstance(payload, bytes)
        or not payload
        or not payload.endswith(b"\n")
        or b"\r" in payload
    ):
        raise FinalizationError(
            "EVIDENCE_PARSE_INVALID", "polled sacct row must be nonempty LF-only bytes"
        )
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise FinalizationError(
            "EVIDENCE_PARSE_INVALID", "polled sacct row is not UTF-8"
        ) from exc
    if len(lines) != 1:
        raise FinalizationError(
            "EVIDENCE_PARSE_INVALID", "polled sacct must contain exactly one allocation row"
        )
    parts = lines[0].split("|")
    if len(parts) != len(SACCT_FIELDS):
        raise FinalizationError(
            "EVIDENCE_PARSE_INVALID", "polled sacct row has wrong explicit field count"
        )
    record = dict(zip(SACCT_FIELDS, parts))
    if JOB_RE.fullmatch(record["JobIDRaw"]) is None:
        raise FinalizationError(
            "EVIDENCE_PARSE_INVALID", "polled sacct steps, arrays, and aliases are forbidden"
        )
    if re.fullmatch(r"[A-Z][A-Z_]*", record["State"]) is None:
        raise FinalizationError(
            "EVIDENCE_PARSE_INVALID", "polled sacct state must be one exact uppercase token"
        )
    return record


def classify_sacct_poll_snapshot(
    payload: bytes, record: Mapping[str, str]
) -> str:
    """Classify only the frozen Slurm accounting-readiness profiles."""
    state = record["State"]
    partition = record["Partition"]
    if state in TERMINAL_STATES:
        if partition not in {"", "gpua40i"}:
            raise FinalizationError(
                "SCHEDULER_CAPTURE_FAILED",
                "terminal sacct partition is neither blank-incomplete nor gpua40i",
            )
        normalized = dict(record)
        incomplete_fields: list[str] = []
        for field, replacement in TERMINAL_ACCOUNTING_INCOMPLETE_NORMALIZATION.items():
            sentinels = {""} if field == "Partition" else {"", "Unknown"}
            if record[field] in sentinels:
                normalized[field] = replacement
                incomplete_fields.append(field)
        normalized_payload = (
            "|".join(normalized[field] for field in SACCT_FIELDS) + "\n"
        ).encode("utf-8")
        parse_sacct_snapshot(
            normalized_payload, allow_multiple=False, require_terminal=True
        )
        if (
            normalized["NNodes"] != "1"
            or NODE_RE.fullmatch(normalized["NodeList"]) is None
        ):
            raise FinalizationError(
                "SCHEDULER_CAPTURE_FAILED",
                "terminal sacct cannot derive exactly one canonical node",
            )
        if incomplete_fields:
            return "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL"
        return "TERMINAL_COMPLETE_gpua40i"
    if partition == "":
        return "PRETERMINAL_EMPTY_PARTITION"
    if partition == "gpua40i":
        return "PRETERMINAL_PARTITION_READY"
    raise FinalizationError(
        "SCHEDULER_CAPTURE_FAILED",
        "preterminal sacct partition is not the exact allowed readiness profile",
    )


def parse_scontrol_snapshot(payload: bytes, label: str) -> dict[str, str]:
    if not payload or not payload.endswith(b"\n") or b"\r" in payload:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} must be nonempty LF-only bytes")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} is not UTF-8") from exc
    pairs = re.findall(r"(?:^|\s)([A-Za-z][A-Za-z0-9_/]*?)=([^\s]+)", text)
    fields: dict[str, str] = {}
    aliases: set[str] = set()
    for key, value in pairs:
        alias = key.casefold()
        if alias in aliases:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} repeats key {key}")
        aliases.add(alias)
        fields[key] = value
    required = {
        "JobId", "JobState", "ExitCode", "StartTime", "EndTime", "Partition",
        "NodeList", "NumNodes", "NumCPUs", "NumTasks", "ReqTRES", "AllocTRES",
        "Account",
        "TresPerNode", "GresDetail",
    }
    if not required.issubset(fields):
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} lacks required -dd keys")
    if JOB_RE.fullmatch(fields["JobId"]) is None or EXIT_RE.fullmatch(fields["ExitCode"]) is None:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} identity or exit code is invalid")
    _parse_slurm_time(fields["StartTime"], f"{label} StartTime")
    _parse_slurm_time(fields["EndTime"], f"{label} EndTime", allow_unknown=True)
    req = _parse_tres(fields["ReqTRES"], f"{label} ReqTRES")
    alloc = _parse_tres(fields["AllocTRES"], f"{label} AllocTRES")
    if (
        fields["Partition"] != "gpua40i"
        or fields["Account"] != "lu2026-2-51"
        or fields["NumNodes"] != "1"
        or fields["NumCPUs"] != "8"
        or fields["NumTasks"] != "1"
        or req.get("gres/gpu:a40") != "1"
        or _gpu_tres_count(req, label) != 1
        or req.get("mem") != "64G"
        or alloc.get("gres/gpu:a40") != "1"
        or _gpu_tres_count(alloc, label) != 1
        or alloc.get("mem") != "64G"
    ):
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", f"{label} lacks exact gres/gpu:a40=1 allocation")
    if fields["TresPerNode"] != "gres:gpu:a40:1":
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", f"{label} TresPerNode is not exact A40 one-GRES")
    if re.fullmatch(r"gpu:a40:1\(IDX:(0|[1-9][0-9]*)\)", fields["GresDetail"]) is None:
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", f"{label} GresDetail lacks one exact A40 index")
    return fields


def _parse_key_value_lines(
    payload: bytes, label: str, *, configuration_header: bool = False
) -> dict[str, str]:
    if not payload or not payload.endswith(b"\n") or b"\r" in payload:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} must be nonempty LF-only bytes")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} is not UTF-8") from exc
    lines = text.splitlines()
    if configuration_header:
        prefix = "Configuration data as of "
        if not lines or not lines[0].startswith(prefix):
            raise FinalizationError(
                "EVIDENCE_PARSE_INVALID", f"{label} lacks exact first configuration header"
            )
        if lines[0].count(prefix) != 1:
            raise FinalizationError(
                "EVIDENCE_PARSE_INVALID", f"{label} configuration header is ambiguous"
            )
        _parse_slurm_time(lines[0][len(prefix):], f"{label} header")
        lines = lines[1:]
        if not lines:
            raise FinalizationError(
                "EVIDENCE_PARSE_INVALID", f"{label} has no fields after configuration header"
            )
    fields: dict[str, str] = {}
    aliases: set[str] = set()
    for line in lines:
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9]*)\s*=\s*(.+)", line)
        if match is None:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} line is not Key = Value")
        key, value = match.groups()
        alias = key.casefold()
        if alias in aliases:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} repeats key {key}")
        aliases.add(alias)
        fields[key] = value
    return fields


def _parse_one_line_tokens(payload: bytes, label: str) -> dict[str, str]:
    if not payload or not payload.endswith(b"\n") or b"\r" in payload:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} must be one LF-only line")
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} is not UTF-8") from exc
    if len(lines) != 1:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} must be exactly one -o line")
    line = lines[0]
    markers = list(re.finditer(r"(?:^| +)([A-Za-z][A-Za-z0-9_]*)=", line))
    if not markers or markers[0].start() != 0 or markers[0].group(0).startswith(" "):
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} lacks a leading key=value")
    fields: dict[str, str] = {}
    aliases: set[str] = set()
    for index, marker in enumerate(markers):
        key = marker.group(1)
        value_start = marker.end()
        value_end = markers[index + 1].start() if index + 1 < len(markers) else len(line)
        value = line[value_start:value_end].rstrip(" ")
        alias = key.casefold()
        if alias in aliases:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} token is ambiguous")
        aliases.add(alias)
        fields[key] = value
    return fields


def _parse_canonical_csv(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, str) or not value:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} list is empty")
    items = value.split(",")
    aliases: set[str] = set()
    for item in items:
        alias = item.casefold()
        if not item or item.strip() != item or alias in aliases:
            raise FinalizationError("EVIDENCE_PARSE_INVALID", f"{label} list is ambiguous")
        aliases.add(alias)
    return tuple(items)


def parse_config_snapshots(config: bytes, partition: bytes, node: bytes) -> dict[str, dict[str, str]]:
    cfg = _parse_key_value_lines(
        config, "scheduler config", configuration_header=True
    )
    required = {
        "SlurmctldVersion": "23.11.3", "ClusterName": "cosmos",
        "SelectType": "select/cons_tres",
        "ProctrackType": "proctrack/cgroup",
        "AccountingStorageType": "accounting_storage/slurmdbd",
        "JobAcctGatherType": "jobacct_gather/cgroup",
        "PrivateData": "none",
    }
    for key, expected in required.items():
        if cfg.get(key) != expected:
            raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", f"scheduler config {key} mismatch")
    task_plugins = _parse_canonical_csv(cfg.get("TaskPlugin"), "scheduler TaskPlugin")
    if (
        cfg.get("MinJobAge") != "300 sec"
        or "gpu" not in cfg.get("GresTypes", "").split(",")
        or not cfg.get("AccountingStorageEnforce")
        or "gres/gpu" not in cfg.get("AccountingStorageTRES", "").split(",")
        or not {"task/cgroup", "task/affinity"}.issubset(task_plugins)
    ):
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "scheduler retention or GRES config mismatch")
    part = _parse_one_line_tokens(partition, "scheduler partition")
    allow_accounts = _parse_canonical_csv(
        part.get("AllowAccounts"), "scheduler partition AllowAccounts"
    )
    account_allowed = allow_accounts == ("ALL",) or "lu2026-2-51" in allow_accounts
    if (
        part.get("PartitionName") != "gpua40i"
        or not account_allowed
        or part.get("OverSubscribe") != "NO"
        or part.get("State") != "UP"
    ):
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "partition cannot prove non-oversubscribed GPU GRES")
    nd = _parse_one_line_tokens(node, "scheduler node")
    if nd.get("NodeName") is None or NODE_RE.fullmatch(nd["NodeName"]) is None:
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "node snapshot identity is invalid")
    if re.search(r"(?:^|,)gpu:a40:[1-9][0-9]*(?:\(|,|$)", nd.get("Gres", "")) is None:
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "node snapshot lacks configured A40 GRES")
    cfg_tres = _parse_tres(nd.get("CfgTRES", ""), "node CfgTRES")
    if "gres/gpu:a40" not in cfg_tres or UINT_RE.fullmatch(cfg_tres["gres/gpu:a40"]) is None or int(cfg_tres["gres/gpu:a40"]) < 1:
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "node snapshot lacks A40 configured TRES")
    return {"config": cfg, "partition": part, "node": nd}


def parse_scheduler_export(payload: bytes, adapter: ModuleType | None = None) -> dict[str, Any]:
    donor = load_exact_adapter() if adapter is None else adapter
    if payload.count(b"\n") != 1:
        raise FinalizationError("EVIDENCE_PARSE_INVALID", "scheduler export must be exactly one JSONL row")
    value = strict_json(payload, "scheduler export", donor)
    _require_exact(value, EXPORT_FIELDS, "scheduler export")
    return value


def _materialized_argv(job_id: str, partition: str, start: str, end: str, node: str) -> dict[str, list[str]]:
    fields = ",".join(SACCT_FIELDS)
    return {
        "terminal_sacct": ["sacct", "-a", "-X", "-D", "-j", job_id, "--parsable2", "--noheader", f"--format={fields}"],
        "post_job_scontrol": ["scontrol", "show", "job", "-dd", job_id],
        "scheduler_config": ["scontrol", "show", "config"],
        "scheduler_partition": ["scontrol", "show", "partition", partition, "-o"],
        "scheduler_node": ["scontrol", "show", "node", "-dd", "-o", node],
        "nonoverlap_sacct": ["sacct", "-a", "-X", "-D", "-S", start, "-E", end, "-N", node, "--parsable2", "--noheader", f"--format={fields}"],
    }


CAPTURE_ENVIRONMENT = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "LANG": "C",
    "LC_ALL": "C",
}
CAPTURE_FILE_BY_KEY = {
    "terminal_sacct": "POST_JOB_SACCT_V1.txt",
    "post_job_scontrol": "POST_JOB_SCONTROL_V1.txt",
    "scheduler_config": "SCHEDULER_CONFIG_V1.txt",
    "scheduler_partition": "SCHEDULER_PARTITION_V1.txt",
    "scheduler_node": "SCHEDULER_NODE_V1.txt",
    "nonoverlap_sacct": "POST_JOB_SACCT_NONOVERLAP_V1.txt",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_utc(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", "capture UTC clock returned a naive value"
        )
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _format_ns_seconds(value: int) -> str:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", "capture elapsed nanoseconds are invalid"
        )
    return f"{value // 1_000_000_000}.{value % 1_000_000_000:09d}"


def _parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or UTC_TIME_RE.fullmatch(value) is None:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", f"{label} is not exact UTC microseconds"
        )
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", f"{label} is not a real UTC time"
        ) from exc


def _capture_command(
    argv: Sequence[str],
    runner: Any,
    *,
    allow_empty: bool = False,
) -> bytes:
    try:
        completed = runner(
            list(argv),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(CAPTURE_ENVIRONMENT),
            check=False,
            timeout=CAPTURE_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_TIMEOUT", "scheduler capture command exceeded frozen timeout"
        ) from exc
    except OSError as exc:
        raise FinalizationError("SCHEDULER_CAPTURE_FAILED", "scheduler capture command could not execute") from exc
    stderr = completed.stderr if isinstance(completed.stderr, bytes) else b""
    stdout = completed.stdout if isinstance(completed.stdout, bytes) else b""
    if completed.returncode != 0:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED",
            f"scheduler capture returned nonzero; stderr_sha256={sha256_bytes(stderr)}",
        )
    if not stdout and not allow_empty:
        raise FinalizationError("SCHEDULER_CAPTURE_FAILED", "scheduler capture returned empty stdout")
    return stdout


def watch_capture_scheduler(
    job_id: str,
    output_root: Path,
    *,
    runner: Any = subprocess.run,
    sleeper: Any = time.sleep,
    monotonic_ns: Any = time.monotonic_ns,
    utc_now: Any = _utc_now,
) -> dict[str, Any]:
    """Poll one frozen job to terminal state, derive its node, and retain raw evidence."""
    if JOB_RE.fullmatch(job_id) is None:
        raise FinalizationError("ARGV_INVALID", "watch-capture job is outside the exact freeze")
    if not output_root.is_absolute():
        raise FinalizationError("ARGV_INVALID", "capture output root must be absolute")
    output_fd = _create_output_root(output_root)
    raw_hashes: dict[str, str] = {}
    identities: dict[str, tuple[int, int]] = {}
    observations: list[dict[str, Any]] = []
    command_observations: list[dict[str, Any]] = []
    completed_argv: dict[str, list[str]] = {}
    terminal: dict[str, str] | None = None
    terminal_raw: bytes | None = None
    node: str | None = None
    terminal_observed_monotonic_ns: int | None = None
    terminal_observed_at_utc: str | None = None
    post_job_scontrol_started_at_utc: str | None = None
    post_job_scontrol_start_seconds_after_terminal: str | None = None
    post_job_scontrol_completed_at_utc: str | None = None
    post_job_scontrol_seconds_after_terminal: str | None = None
    fields = ",".join(SACCT_FIELDS)
    terminal_argv = [
        "sacct", "-a", "-X", "-D", "-j", job_id,
        "--parsable2", "--noheader", f"--format={fields}",
    ]
    try:
        try:
            for poll_index in range(1, TERMINAL_POLL_LIMIT + 1):
                observed = monotonic_ns()
                if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
                    raise FinalizationError(
                        "SCHEDULER_CAPTURE_FAILED", "monotonic poll timestamp is invalid"
                    )
                if observations:
                    previous_poll = int(
                        observations[-1]["observed_at_monotonic_ns"]
                    )
                    if (
                        observed - previous_poll
                        < TERMINAL_POLL_INTERVAL_SECONDS * 1_000_000_000
                    ):
                        raise FinalizationError(
                            "SCHEDULER_CAPTURE_FAILED",
                            "terminal poll cadence is shorter than the frozen interval",
                        )
                raw = _capture_command(
                    terminal_argv, runner, allow_empty=True
                )
                row_count = 0 if raw == b"" else len(raw.splitlines())
                observation = {
                    "poll_index": poll_index,
                    "observed_at_monotonic_ns": str(observed),
                    "argv": list(terminal_argv),
                    "row_count": row_count,
                    "raw_sha256": sha256_bytes(raw),
                    "state": None,
                    "partition": None,
                    "classification": "NO_ROW",
                    "terminal": False,
                }
                if raw:
                    try:
                        row = parse_sacct_poll_snapshot(raw)
                    except FinalizationError:
                        observation["classification"] = "REJECTED_PARSE"
                        observations.append(observation)
                        raise
                    observation["state"] = row["State"]
                    observation["partition"] = row["Partition"]
                    if row["JobIDRaw"] != job_id:
                        observation["classification"] = "REJECTED_IDENTITY"
                        observations.append(observation)
                        raise FinalizationError(
                            "SCHEDULER_CAPTURE_FAILED",
                            "polled sacct identity differs from the frozen job",
                        )
                    try:
                        classification = classify_sacct_poll_snapshot(raw, row)
                    except FinalizationError:
                        observation["classification"] = "REJECTED_PROFILE"
                        observations.append(observation)
                        raise
                    observation["classification"] = classification
                observations.append(observation)
                if raw and observation["classification"] == "TERMINAL_COMPLETE_gpua40i":
                    row = parse_sacct_snapshot(raw, allow_multiple=False)[0]
                    if row["NNodes"] != "1" or NODE_RE.fullmatch(row["NodeList"]) is None:
                        raise FinalizationError(
                            "SCHEDULER_CAPTURE_FAILED",
                            "terminal sacct does not derive exactly one canonical node",
                        )
                    observation["terminal"] = True
                    terminal = row
                    terminal_raw = raw
                    node = row["NodeList"]
                    terminal_observed_monotonic_ns = monotonic_ns()
                    if (
                        isinstance(terminal_observed_monotonic_ns, bool)
                        or not isinstance(terminal_observed_monotonic_ns, int)
                        or terminal_observed_monotonic_ns < observed
                    ):
                        raise FinalizationError(
                            "SCHEDULER_CAPTURE_FAILED",
                            "terminal observation monotonic time is invalid",
                        )
                    terminal_observed_at_utc = _format_utc(utc_now())
                    break
                if poll_index < TERMINAL_POLL_LIMIT:
                    sleeper(TERMINAL_POLL_INTERVAL_SECONDS)
            if (
                terminal is None
                or node is None
                or terminal_observed_monotonic_ns is None
                or terminal_observed_at_utc is None
            ):
                raise FinalizationError(
                    "SCHEDULER_TERMINAL_TIMEOUT",
                    "terminal sacct poll limit was exhausted",
                )

            argv_by_key = _materialized_argv(
                job_id, "gpua40i", terminal["Start"], terminal["End"], node
            )
            for key in (
                "post_job_scontrol", "scheduler_config", "scheduler_partition",
                "scheduler_node", "nonoverlap_sacct",
            ):
                started_ns = monotonic_ns()
                if (
                    isinstance(started_ns, bool)
                    or not isinstance(started_ns, int)
                    or started_ns < terminal_observed_monotonic_ns
                    or started_ns - terminal_observed_monotonic_ns
                    > POST_TERMINAL_CAPTURE_DEADLINE_SECONDS * 1_000_000_000
                ):
                    raise FinalizationError(
                        "SCHEDULER_CAPTURE_DEADLINE_EXCEEDED",
                        "post-terminal capture deadline expired before command start",
                    )
                start_elapsed_ns = started_ns - terminal_observed_monotonic_ns
                if (
                    key == "post_job_scontrol"
                    and start_elapsed_ns
                    > POST_JOB_SCONTROL_START_LATENCY_LIMIT_SECONDS
                    * 1_000_000_000
                ):
                    raise FinalizationError(
                        "SCHEDULER_CAPTURE_START_LATENCY_EXCEEDED",
                        "first post-job scontrol did not start within the frozen latency limit",
                    )
                started_utc = _format_utc(utc_now())
                if key == "post_job_scontrol":
                    post_job_scontrol_started_at_utc = started_utc
                    post_job_scontrol_start_seconds_after_terminal = (
                        _format_ns_seconds(start_elapsed_ns)
                    )
                raw = _capture_command(argv_by_key[key], runner)
                completed_ns = monotonic_ns()
                if (
                    isinstance(completed_ns, bool)
                    or not isinstance(completed_ns, int)
                    or completed_ns < started_ns
                ):
                    raise FinalizationError(
                        "SCHEDULER_CAPTURE_FAILED",
                        "capture command monotonic completion time is invalid",
                    )
                duration_ns = completed_ns - started_ns
                if duration_ns > CAPTURE_COMMAND_TIMEOUT_SECONDS * 1_000_000_000:
                    raise FinalizationError(
                        "SCHEDULER_CAPTURE_TIMEOUT",
                        "scheduler capture command exceeded frozen monotonic duration",
                    )
                completed_utc = _format_utc(utc_now())
                if key == "post_job_scontrol":
                    if terminal_raw is None:
                        raise FinalizationError(
                            "SCHEDULER_CAPTURE_FAILED", "terminal raw bytes are unavailable"
                        )
                    terminal_name = CAPTURE_FILE_BY_KEY["terminal_sacct"]
                    digest, identity = _write_new_bytes(
                        output_fd, terminal_name, terminal_raw
                    )
                    raw_hashes[terminal_name] = digest
                    identities[terminal_name] = identity
                    completed_argv["terminal_sacct"] = list(terminal_argv)
                name = CAPTURE_FILE_BY_KEY[key]
                digest, identity = _write_new_bytes(output_fd, name, raw)
                raw_hashes[name] = digest
                identities[name] = identity
                completed_argv[key] = list(argv_by_key[key])
                elapsed_ns = completed_ns - terminal_observed_monotonic_ns
                before_deadline = (
                    elapsed_ns
                    <= POST_TERMINAL_CAPTURE_DEADLINE_SECONDS * 1_000_000_000
                )
                command_observations.append({
                    "key": key,
                    "argv": list(argv_by_key[key]),
                    "started_at_monotonic_ns": str(started_ns),
                    "started_at_utc": started_utc,
                    "completed_at_monotonic_ns": str(completed_ns),
                    "completed_at_utc": completed_utc,
                    "duration_seconds": _format_ns_seconds(duration_ns),
                    "seconds_after_terminal_observation": _format_ns_seconds(elapsed_ns),
                    "post_terminal_deadline_remaining_seconds": _format_ns_seconds(
                        max(
                            0,
                            POST_TERMINAL_CAPTURE_DEADLINE_SECONDS * 1_000_000_000
                            - elapsed_ns,
                        )
                    ),
                    "completed_before_post_terminal_deadline": before_deadline,
                })
                if key == "post_job_scontrol":
                    post_job_scontrol_completed_at_utc = completed_utc
                    post_job_scontrol_seconds_after_terminal = _format_ns_seconds(
                        elapsed_ns
                    )
                if not before_deadline:
                    raise FinalizationError(
                        "SCHEDULER_CAPTURE_DEADLINE_EXCEEDED",
                        "post-terminal capture command completed after frozen deadline",
                    )

            post = parse_scontrol_snapshot(
                _read_held(output_fd, CAPTURE_FILE_BY_KEY["post_job_scontrol"], "captured post-job scontrol"),
                "captured post-job scontrol -dd",
            )
            if post["JobId"] != job_id or post["NodeList"] != node:
                raise FinalizationError(
                    "SCHEDULER_CAPTURE_FAILED", "post-job scontrol identity drift"
                )
            parse_config_snapshots(
                _read_held(output_fd, CAPTURE_FILE_BY_KEY["scheduler_config"], "captured scheduler config"),
                _read_held(output_fd, CAPTURE_FILE_BY_KEY["scheduler_partition"], "captured scheduler partition"),
                _read_held(output_fd, CAPTURE_FILE_BY_KEY["scheduler_node"], "captured scheduler node"),
            )
            overlap_rows = parse_sacct_snapshot(
                _read_held(output_fd, CAPTURE_FILE_BY_KEY["nonoverlap_sacct"], "captured non-overlap sacct"),
                allow_multiple=True,
            )
            _validate_nonoverlap(overlap_rows, terminal)

            provenance = {
                "schema_version": "orion.p1.scienceagentbench.protected-rr1-scheduler-capture-provenance.v2",
                "authority": "EXACT_SCHEDULER_CAPTURE_COMMAND_AND_RAW_BYTE_BINDING_ONLY",
                "status": "PASS_EXACT_POST_JOB_SCHEDULER_CAPTURE",
                "slurm_job_id": job_id,
                "partition": "gpua40i",
                "node_name": node,
                "allocation_started_at": terminal["Start"],
                "allocation_ended_at": terminal["End"],
                "capture_argv": argv_by_key,
                "capture_command_timeout_seconds": CAPTURE_COMMAND_TIMEOUT_SECONDS,
                "post_terminal_capture_deadline_seconds": POST_TERMINAL_CAPTURE_DEADLINE_SECONDS,
                "post_job_scontrol_start_latency_limit_seconds": POST_JOB_SCONTROL_START_LATENCY_LIMIT_SECONDS,
                "terminal_observed_at_utc": terminal_observed_at_utc,
                "terminal_observed_monotonic_ns": str(terminal_observed_monotonic_ns),
                "post_job_scontrol_started_at_utc": post_job_scontrol_started_at_utc,
                "post_job_scontrol_start_seconds_after_terminal_observation": post_job_scontrol_start_seconds_after_terminal,
                "post_job_scontrol_completed_at_utc": post_job_scontrol_completed_at_utc,
                "post_job_scontrol_seconds_after_terminal_observation": post_job_scontrol_seconds_after_terminal,
                "capture_command_observations": command_observations,
                "terminal_poll_interval_seconds": TERMINAL_POLL_INTERVAL_SECONDS,
                "terminal_poll_limit": TERMINAL_POLL_LIMIT,
                "terminal_poll_count": len(observations),
                "terminal_poll_observations": observations,
                "partition_source": "INTERNAL_FROZEN_gpua40i",
                "node_source": "DERIVED_FROM_UNIQUE_TERMINAL_SACCT_NODELIST",
                "raw_file_sha256": raw_hashes,
                "credential_environment_read": False,
                "stderr_retained": False,
                "job_submitted": False,
                "scientific_authority_delta": "NONE",
            }
            _, identity = _write_new_json(
                output_fd, "SCHEDULER_CAPTURE_PROVENANCE_V1.json", provenance
            )
            identities["SCHEDULER_CAPTURE_PROVENANCE_V1.json"] = identity
            _seal_capture_files(output_fd, identities)
            return provenance
        except Exception as caught:
            exc = _typed_unexpected_failure(
                caught,
                "SCHEDULER_CAPTURE_RUNTIME_FAILED",
                "unexpected scheduler capture runtime failure",
            )
            if (
                terminal_raw is not None
                and CAPTURE_FILE_BY_KEY["terminal_sacct"] not in raw_hashes
            ):
                terminal_name = CAPTURE_FILE_BY_KEY["terminal_sacct"]
                digest, identity = _write_new_bytes(
                    output_fd, terminal_name, terminal_raw
                )
                raw_hashes[terminal_name] = digest
                identities[terminal_name] = identity
                completed_argv["terminal_sacct"] = list(terminal_argv)
            failure = {
                "schema_version": "orion.p1.scienceagentbench.protected-rr1-scheduler-capture-cannot-check.v2",
                "authority": "BODY_FREE_PARTIAL_READ_ONLY_SCHEDULER_CAPTURE_FAILURE_ONLY",
                "status": "CANNOT_CHECK_POST_JOB_SCHEDULER_CAPTURE",
                "slurm_job_id": job_id,
                "partition": "gpua40i",
                "node_name": node,
                "capture_command_timeout_seconds": CAPTURE_COMMAND_TIMEOUT_SECONDS,
                "post_terminal_capture_deadline_seconds": POST_TERMINAL_CAPTURE_DEADLINE_SECONDS,
                "post_job_scontrol_start_latency_limit_seconds": POST_JOB_SCONTROL_START_LATENCY_LIMIT_SECONDS,
                "terminal_observed_at_utc": terminal_observed_at_utc,
                "terminal_observed_monotonic_ns": (
                    None if terminal_observed_monotonic_ns is None
                    else str(terminal_observed_monotonic_ns)
                ),
                "post_job_scontrol_started_at_utc": post_job_scontrol_started_at_utc,
                "post_job_scontrol_start_seconds_after_terminal_observation": post_job_scontrol_start_seconds_after_terminal,
                "post_job_scontrol_completed_at_utc": post_job_scontrol_completed_at_utc,
                "post_job_scontrol_seconds_after_terminal_observation": post_job_scontrol_seconds_after_terminal,
                "capture_command_observations": command_observations,
                "terminal_poll_interval_seconds": TERMINAL_POLL_INTERVAL_SECONDS,
                "terminal_poll_limit": TERMINAL_POLL_LIMIT,
                "terminal_poll_count": len(observations),
                "terminal_poll_observations": observations,
                "completed_capture_argv": completed_argv,
                "raw_file_sha256": raw_hashes,
                "failure_code": exc.code,
                "failure_detail_sha256": sha256_bytes(
                    f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
                ),
                "stderr_retained": False,
                "credential_environment_read": False,
                "job_submitted": False,
                "scientific_authority_delta": "NONE",
            }
            _, identity = _write_new_json(
                output_fd, "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json", failure
            )
            identities["SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"] = identity
            _seal_capture_files(output_fd, identities)
            raise exc from (None if exc is caught else caught)
    finally:
        os.close(output_fd)


def _validate_plan(plan: Mapping[str, Any], adapter: ModuleType) -> None:
    try:
        validated = adapter.validate_plan(plan)
    except Exception as exc:
        raise FinalizationError("FULL_PLAN_INVALID", "exact adapter donor rejected full Runner V2 plan") from exc
    if validated != plan:
        raise FinalizationError("FULL_PLAN_INVALID", "adapter donor plan normalization drift")
    if plan.get("schema_version") != "orion.p1.scienceagentbench.run-plan.allocated-accelerator-seconds.v2":
        raise FinalizationError("FULL_PLAN_INVALID", "full Runner V2 plan schema mismatch")
    if plan.get("split") != "verified" or plan.get("task_ids") != [str(i) for i in range(1, 103)]:
        raise FinalizationError("FULL_PLAN_INVALID", "full Runner V2 plan must retain all 102 ordered tasks")
    if plan.get("arms") != ["RR", "OS", "NR"] or plan.get("attempts_per_task_arm") != 3:
        raise FinalizationError("FULL_PLAN_INVALID", "full Runner V2 arms or attempts drift")
    bindings = plan.get("bindings")
    if not isinstance(bindings, dict) or bindings.get("seed_schedule") != {"1": 101, "2": 202, "3": 303}:
        raise FinalizationError("FULL_PLAN_INVALID", "full Runner V2 seed schedule drift")
    if len(plan["task_ids"]) * len(plan["arms"]) * plan["attempts_per_task_arm"] != 918:
        raise FinalizationError("FULL_PLAN_INVALID", "full Runner V2 population is not 918 tuples")


def _validate_stage_process(
    stage: Mapping[str, Any], process: Mapping[str, Any], plan_payload: bytes,
    stage_file_sha: str, process_file_sha: str,
) -> None:
    _require_exact(stage, STAGE_FIELDS, "runtime stage")
    if (
        stage.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-direct-route-runtime-stage.v1"
        or stage.get("authority")
        != "ONE_TUPLE_RUNTIME_PREFLIGHT_METADATA_ONLY__NO_SUBMISSION_OUTCOME_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime stage schema mismatch")
    if stage.get("tuple_identity") != FIXED_STAGE_TUPLE or stage.get("tuple_seed") != 101:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime stage tuple/seed mismatch")
    source_sha = stage.get("source_sha256")
    source_paths = stage.get("source_paths")
    if (
        source_sha != EXPECTED_STAGE_SOURCE_SHA256
        or not isinstance(source_paths, dict)
        or set(source_paths) != set(EXPECTED_STAGE_SOURCE_SHA256)
        or source_sha.get("plan") != sha256_bytes(plan_payload)
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime stage does not bind held full plan bytes")
    if any(
        not isinstance(source_paths[name], str) or not Path(source_paths[name]).is_absolute()
        for name in EXPECTED_STAGE_SOURCE_SHA256
    ) or len(set(source_paths.values())) != len(source_paths):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime stage source paths are not exact distinct absolutes")
    extension = stage.get("run_plan_binding_extension")
    if (
        extension != EXPECTED_STAGE_EXTENSION
        or stage.get("run_plan_binding_extension_sha256") != canonical_hash(extension)
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime stage extension hash mismatch")
    runtime_observed = stage.get("runtime_observed_sha256")
    if runtime_observed != {
        "model": source_sha["model"], "llama_server": source_sha["server"],
        "cuda_backend": source_sha["backend"], "launcher": source_sha["launcher"],
        "preflight_bridge": DIRECT_ROUTE_SHA256,
    }:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime observed source hashes drift")
    expected_server_argv = [
        source_paths["server"], "--model", source_paths["model"],
        "--host", "127.0.0.1", "--port", "8080", "--ctx-size", "32768",
        "--parallel", "1", "--no-cont-batching", "--threads", "8",
        "--threads-batch", "8", "--batch-size", "512", "--ubatch-size", "512",
        "--cache-type-k", "f16", "--cache-type-v", "f16", "--flash-attn", "on",
        "--n-gpu-layers", "all", "--no-context-shift", "--metrics", "--slots",
    ]
    if stage.get("server_argv") != expected_server_argv:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime server argv drift")
    commitments = stage.get("prompt_commitments_by_phase")
    if not isinstance(commitments, dict) or set(commitments) != {"RR_PHASE0", "RR_PHASE1"}:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "runtime prompt commitment set is not exact RR0/RR1")
    rr0, rr1 = commitments["RR_PHASE0"], commitments["RR_PHASE1"]
    if not isinstance(rr0, dict) or set(rr0) != {"status", "rendered_prompt_sha256"} or rr0["status"] != "PROSPECTIVE_EXACT":
        raise FinalizationError("CROSS_BINDING_MISMATCH", "RR0 prompt commitment drift")
    _require_sha(rr0["rendered_prompt_sha256"], "RR0 prompt commitment")
    if (
        not isinstance(rr1, dict)
        or set(rr1) != {"status", "template_text_sha256", "recovered_packet_canonical_sha256", "state_source"}
        or rr1["status"] != "DYNAMIC_SEALED_RR_STATE_RULE"
        or rr1["recovered_packet_canonical_sha256"] != source_sha["recovered"]
        or rr1["state_source"] != "RR_PHASE0_STRICT_PARSED_CANONICAL_STATE_AND_SHA256"
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "RR1 prompt commitment drift")
    _require_sha(rr1["template_text_sha256"], "RR1 template commitment")
    if (
        stage.get("status") != "HASHED_RUNTIME_INPUT_STAGED__PROCESS_ATTESTATION_PENDING"
        or stage.get("allocation_status") != "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION"
        or stage.get("protected_body_retention") is not False
        or stage.get("production_admissibility") != "CANNOT_CHECK"
        or stage.get("scientific_authority_delta") != "NONE"
    ):
        raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", "runtime stage retains protected bodies")
    _require_exact(process, PROCESS_FIELDS, "process attestation")
    if (
        process.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-process-attestation.v1"
        or process.get("authority")
        != "LIVE_RUNTIME_IDENTITY_METADATA_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY"
        or process.get("status") != "EXACT_ONE_TUPLE_LOOPBACK_PROCESS_ATTESTED"
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "process attestation schema/status mismatch")
    if process.get("runtime_stage_sha256") != stage_file_sha:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "process attestation runtime-stage file hash mismatch")
    if process.get("server_stdout_stderr_retained") is not False or process.get("protected_bodies_retained") is not False:
        raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", "process attestation retention boundary drift")
    if {
        "model": process["model_sha256"],
        "llama_server": process["llama_server_sha256"],
        "cuda_backend": process["cuda_backend_sha256"],
        "launcher": process["launcher_sha256"],
        "preflight_bridge": process["successor_bridge_sha256"],
    } != runtime_observed:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "process attestation runtime hash binding drift")
    process_identity = process["process_identity"]
    _require_exact(process_identity, PROCESS_IDENTITY_FIELDS, "live process identity")
    pid = process_identity["pid"]
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "live process PID is invalid")
    for field in ("executable_sha256", "cmdline_sha256", "cuda_backend_sha256", "model_sha256"):
        _require_sha(process_identity[field], f"process identity {field}")
    if (
        process_identity["executable_path"] != source_paths["server"]
        or process_identity["executable_sha256"] != source_sha["server"]
        or process_identity["argv"] != expected_server_argv
        or process_identity["ggml_backend_path"] != source_paths["backend"]
        or process_identity["cuda_backend_mapped_path"] != source_paths["backend"]
        or process_identity["cuda_backend_sha256"] != source_sha["backend"]
        or process_identity["model_mapped_path"] != source_paths["model"]
        or process_identity["model_sha256"] != source_sha["model"]
        or process_identity["proxy_environment_empty"] is not True
        or not isinstance(process_identity["executable_device"], str)
        or UINT_RE.fullmatch(process_identity["executable_device"]) is None
        or not isinstance(process_identity["executable_inode"], str)
        or UINT_RE.fullmatch(process_identity["executable_inode"]) is None
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "live process identity does not bind staged runtime")
    listener = process["listener"]
    _require_exact(listener, {"listen_host", "listen_port", "socket_inode"}, "loopback listener")
    if (
        listener["listen_host"] != "127.0.0.1"
        or listener["listen_port"] != 8080
        or not isinstance(listener["socket_inode"], str)
        or UINT_RE.fullmatch(listener["socket_inode"]) is None
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "loopback listener identity drift")
    readiness = process["readiness"]
    _require_exact(readiness, {"health_sha256", "slots_sha256", "slot_count"}, "server readiness")
    _require_sha(readiness["health_sha256"], "server health receipt")
    _require_sha(readiness["slots_sha256"], "server slots receipt")
    if readiness["slot_count"] != 1:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "server readiness slot count drift")
    _require_sha(process_file_sha, "process attestation file")
    _require_false_boundaries(process, "process attestation")


def _validate_job_identity(identity: Any) -> dict[str, Any]:
    fields = {"cluster", "job_id", "array_job_id", "array_task_id"}
    _require_exact(identity, fields, "SLURM job identity")
    if identity["cluster"] != "cosmos" or CLUSTER_RE.fullmatch(identity["cluster"]) is None:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "SLURM cluster identity mismatch")
    if JOB_RE.fullmatch(identity["job_id"]) is None:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "SLURM job ID is not one non-array allocation")
    if identity["array_job_id"] is not None or identity["array_task_id"] is not None:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "one-tuple finalizer rejects array aliases")
    return dict(identity)


def _validate_gpu(gpu: Mapping[str, Any], job_id: str) -> dict[str, Any]:
    _require_exact(
        gpu,
        {
            "schema_version", "authority", "status", "slurm_job_id",
            "cuda_visible_devices", "slurm_job_gpus", "slurm_step_gpus",
            "gpu", "nvidia_smi_stdout_sha256", "scheduler_exclusivity_status",
            "production_admissibility", "scientific_authority_delta",
        },
        "GPU identity",
    )
    if (
        gpu.get("schema_version")
        != "orion.p1.scienceagentbench.one-a40-allocation-identity.v1"
        or gpu.get("authority") != "IN_JOB_VISIBLE_GPU_IDENTITY_METADATA_ONLY"
        or gpu.get("status") != "PASS_EXACTLY_ONE_VISIBLE_NVIDIA_A40"
    ):
        raise FinalizationError("GPU_IDENTITY_CANNOT_CHECK", "one-A40 identity schema/status mismatch")
    if gpu.get("slurm_job_id") != job_id:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "GPU identity job mismatch")
    value = gpu.get("gpu")
    if not isinstance(value, dict) or set(value) != {"visible_index", "gpu_uuid", "name"}:
        raise FinalizationError("GPU_IDENTITY_CANNOT_CHECK", "GPU identity fields are not exact")
    if (
        value["name"] != "NVIDIA A40"
        or value["visible_index"] != "0"
        or gpu["cuda_visible_devices"] != "0"
        or GPU_UUID_RE.fullmatch(value["gpu_uuid"]) is None
    ):
        raise FinalizationError("GPU_IDENTITY_CANNOT_CHECK", "exact one NVIDIA A40 UUID is required")
    job_gpus = gpu.get("slurm_job_gpus")
    step_gpus = gpu.get("slurm_step_gpus")
    if (
        not isinstance(job_gpus, str)
        or not isinstance(step_gpus, str)
        or UINT_RE.fullmatch(job_gpus) is None
        or UINT_RE.fullmatch(step_gpus) is None
        or job_gpus != step_gpus
    ):
        raise FinalizationError("GPU_IDENTITY_CANNOT_CHECK", "SLURM job/step GPU index receipts do not bind one device")
    _require_sha(gpu.get("nvidia_smi_stdout_sha256"), "nvidia-smi stdout")
    if gpu.get("scheduler_exclusivity_status") != "CANNOT_CHECK_PENDING_POST_JOB_SCHEDULER_FINALIZATION":
        raise FinalizationError("CROSS_BINDING_MISMATCH", "GPU identity must remain scheduler-finalization pending")
    _require_false_boundaries(gpu, "GPU identity")
    return {**dict(value), "slurm_job_gpus": job_gpus, "slurm_step_gpus": step_gpus}


def _validate_dynamic(dynamic: Mapping[str, Any]) -> dict[str, Any]:
    _require_exact(dynamic, DYNAMIC_FIELDS, "dynamic RR1 binding")
    if (
        dynamic["schema_version"]
        != "orion.p1.scienceagentbench.dynamic-rr1-pretokenize-binding.v1"
        or dynamic["authority"]
        != "DYNAMIC_PROMPT_FIT_METADATA_ONLY__NO_BODY_OUTCOME_OR_SCIENTIFIC_AUTHORITY"
        or dynamic["tuple_identity"] != FIXED_TUPLE
    ):
        raise FinalizationError("DYNAMIC_TOKENIZE_CANNOT_CHECK", "dynamic RR1 schema/tuple mismatch")
    if dynamic["phase_id"] != "RR_PHASE1" or dynamic["tokenize_repeat_count"] != 3:
        raise FinalizationError("DYNAMIC_TOKENIZE_CANNOT_CHECK", "dynamic RR1 phase/repeat mismatch")
    for field in (
        "rendered_prompt_sha256", "tokenize_request_sha256",
        "tokenize_raw_response_sha256", "token_array_sha256",
    ):
        _require_sha(dynamic[field], f"dynamic {field}")
    integers = (
        "prompt_tokens", "phase_output_cap", "context_window_tokens",
        "remaining_context_margin_tokens",
    )
    if any(isinstance(dynamic[field], bool) or not isinstance(dynamic[field], int) or dynamic[field] < 0 for field in integers):
        raise FinalizationError("DYNAMIC_TOKENIZE_CANNOT_CHECK", "dynamic token counts are invalid")
    if (
        dynamic["phase_output_cap"] != 7168
        or dynamic["context_window_tokens"] != 32768
        or dynamic["remaining_context_margin_tokens"]
        != dynamic["context_window_tokens"] - dynamic["prompt_tokens"] - dynamic["phase_output_cap"]
        or dynamic["remaining_context_margin_tokens"] < 0
        or dynamic["completion_prompt_n_equal"] is not True
        or dynamic["status"] != "PASS_DYNAMIC_RR1_PRETOKENIZE_FIT"
    ):
        raise FinalizationError("DYNAMIC_TOKENIZE_CANNOT_CHECK", "dynamic RR1 fit/count gate is incomplete")
    _require_false_boundaries(dynamic, "dynamic RR1 binding")
    return {field: dynamic[field] for field in DYNAMIC_CORE_FIELDS}


def _validate_cleanup(cleanup: Mapping[str, Any]) -> None:
    _require_exact(
        cleanup,
        {
            "schema_version", "authority", "status", "preflight_succeeded",
            "managed_processes", "protected_bodies_retained",
            "production_admissibility", "scientific_authority_delta",
        },
        "server cleanup",
    )
    if (
        cleanup.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-server-cleanup.v1"
        or cleanup.get("authority") != "PROCESS_CLEANUP_METADATA_ONLY"
        or cleanup.get("status") != "PASS_OWNED_PROCESS_GROUPS_ABSENT"
        or cleanup.get("preflight_succeeded") is not True
    ):
        raise FinalizationError("CLEANUP_CANNOT_CHECK", "cleanup schema/status is not a success")
    managed = cleanup.get("managed_processes")
    if not isinstance(managed, list) or len(managed) != 2:
        raise FinalizationError("CLEANUP_CANNOT_CHECK", "cleanup must bind wrapper and server records")
    labels = {record.get("label") for record in managed if isinstance(record, dict)}
    if labels != {"unchanged-wrapper", "llama-server"}:
        raise FinalizationError("CLEANUP_CANNOT_CHECK", "cleanup process labels are not exact")
    for record in managed:
        if record.get("process_group_absent_after_cleanup") is not True or record.get("process_absent_after_cleanup") is not True:
            raise FinalizationError("CLEANUP_CANNOT_CHECK", "cleanup lacks leader and whole-group absence")
    wrapper = next(record for record in managed if record["label"] == "unchanged-wrapper")
    server = next(record for record in managed if record["label"] == "llama-server")
    _require_exact(
        wrapper,
        {
            "label", "status", "binding_role", "process_started",
            "process_group_id", "termination_signal",
            "process_group_absent_after_cleanup", "process_absent_after_cleanup",
        },
        "wrapper cleanup",
    )
    _require_exact(
        server,
        {
            "label", "process_started", "process_group_id", "termination_signal",
            "return_code", "process_group_absent_after_cleanup",
            "process_absent_after_cleanup",
        },
        "server cleanup",
    )
    if (
        wrapper["status"] != "NONINVOKED"
        or wrapper["binding_role"] != "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED"
        or wrapper["process_started"] is not False
        or wrapper["process_group_id"] is not None
        or wrapper["termination_signal"] is not None
        or server["process_started"] is not True
        or isinstance(server["process_group_id"], bool)
        or not isinstance(server["process_group_id"], int)
        or server["process_group_id"] <= 0
        or server["termination_signal"] not in {None, "SIGTERM", "SIGKILL"}
        or isinstance(server["return_code"], bool)
        or not isinstance(server["return_code"], int)
    ):
        raise FinalizationError("CLEANUP_CANNOT_CHECK", "cleanup exact producer semantics drift")
    _require_false_boundaries(cleanup, "cleanup")


def _validate_capture(
    capture: Mapping[str, Any], adapter: ModuleType, plan: Mapping[str, Any],
    identity: Mapping[str, Any], in_job_sha: str,
) -> None:
    expected_fields = set(adapter.CAPTURE_FIELDS)
    _require_exact(capture, expected_fields, "attempt capture")
    try:
        adapter._validate_capture(
            capture, plan, EXPECTED_STAGE_SOURCE_SHA256["plan"]
        )
    except Exception as exc:
        raise FinalizationError(
            "CAPTURE_CANNOT_CHECK", "exact adapter donor rejected attempt capture"
        ) from exc
    if (
        capture["schema_version"] != adapter.CAPTURE_SCHEMA
        or capture["authority"]
        != "GENERATION_TIMING_METADATA_ONLY__ALLOCATION_AND_OUTCOMES_UNFINALIZED"
        or capture["status"] != adapter.CAPTURE_STATUS
    ):
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt capture schema/status mismatch")
    if {key: capture[key] for key in ("task_id", "arm_id", "attempt", "seed")} != FIXED_TUPLE:
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt capture tuple/seed mismatch")
    if capture["phase_sequence"] != ["RR_PHASE0", "RR_PHASE1"] or capture["exclusive_gpu_count"] != "1":
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt capture phase/GPU count mismatch")
    if (
        capture["run_plan_sha256"] != EXPECTED_STAGE_SOURCE_SHA256["plan"]
        or capture["cost_measurement_binding_sha256"]
        != "779204ac91ba4b11a4982d2b89d09f3e0788dfa035236f6fa1324a7b4bef3411"
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "attempt capture full-plan/cost binding mismatch")
    if capture["allocation_status"] != adapter.PENDING_ALLOCATION_STATUS:
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt capture must remain allocation pending")
    if capture["slurm_job_identity"] != identity or capture["slurm_in_job_snapshot_sha256"] != in_job_sha:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "attempt capture in-job identity binding mismatch")
    base = capture["base_candidate_record"]
    _require_exact(base, set(adapter.BASE_RECORD_FIELDS), "base candidate record")
    if capture["base_candidate_record_canonical_sha256"] != canonical_hash(base):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "base candidate canonical hash mismatch")
    for field in ("monotonic_start_ns", "monotonic_end_ns", "monotonic_elapsed_ns"):
        if not isinstance(capture[field], str) or UINT_RE.fullmatch(capture[field]) is None:
            raise FinalizationError("CAPTURE_CANNOT_CHECK", "capture raw clock field is invalid")
    if int(capture["monotonic_end_ns"]) - int(capture["monotonic_start_ns"]) != int(capture["monotonic_elapsed_ns"]):
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "capture elapsed raw clock mismatch")
    if capture["candidate_bodies_opened"] is not False or capture["official_evaluator_invoked"] is not False or capture["official_outcomes_opened"] is not False or capture["scientific_authority_delta"] != "NONE":
        raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", "attempt capture authority boundary drift")


def _validate_bridge(
    bridge: Mapping[str, Any], capture: Mapping[str, Any], dynamic: Mapping[str, Any],
    stage_sha: str, process_sha: str, dynamic_file_sha: str,
    stage_extension: Mapping[str, Any], rr0_rendered_prompt_sha256: str,
) -> None:
    _require_exact(bridge, BRIDGE_FIELDS, "direct-route bridge binding")
    if (
        bridge["schema_version"]
        != "orion.p1.scienceagentbench.protected-rr1-direct-route-bridge-binding.v1"
        or bridge["authority"]
        != "ONE_TUPLE_ATTEMPT_BINDING_METADATA_ONLY__ALLOCATION_OUTCOMES_AND_918_LEDGER_UNFINALIZED"
        or bridge["status"] != "BOUND_ONE_TUPLE_CAPTURE__POST_JOB_FINALIZATION_PENDING"
        or bridge["tuple_identity"] != FIXED_TUPLE
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "bridge schema/status/tuple mismatch")
    if bridge["runtime_stage_sha256"] != stage_sha or bridge["process_attestation_sha256"] != process_sha:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "bridge stage/process file hash mismatch")
    if bridge["attempt_capture_canonical_sha256"] != canonical_hash(capture):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "success capture canonical hash mismatch")
    extension = bridge["run_plan_binding_extension"]
    if extension != stage_extension or bridge["run_plan_binding_extension_sha256"] != canonical_hash(extension):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "bridge run-plan extension hash mismatch")
    core = {field: dynamic[field] for field in DYNAMIC_CORE_FIELDS}
    if bridge["dynamic_rr1_pretokenize_binding"] != core or bridge["dynamic_rr1_pretokenize_binding_canonical_sha256"] != canonical_hash(core) or bridge["dynamic_rr1_pretokenize_file_sha256"] != dynamic_file_sha:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "bridge dynamic file/canonical hash chain mismatch")
    if bridge["runner_v2_population_ledger_status"] != "NOT_FINALIZED_918_TUPLES" or bridge["allocation_status"] != "CANNOT_CHECK_PENDING_ONE_TUPLE_SCHEDULER_FINALIZATION":
        raise FinalizationError("AUTHORITY_BOUNDARY_DRIFT", "bridge finalization boundary drift")
    requests = bridge["request_bindings"]
    if not isinstance(requests, list) or len(requests) != 2:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "bridge must bind exact RR0/RR1 completion request order")
    request_fields = {
        "phase_id", "rendered_prompt_sha256", "canonical_request_sha256",
        "cache_prompt", "transport_status", "completion_raw_response_sha256",
    }
    for request, phase in zip(requests, ("RR_PHASE0", "RR_PHASE1")):
        _require_exact(request, request_fields, f"bridge {phase} request")
        if request["phase_id"] != phase or request["cache_prompt"] is not False or request["transport_status"] != "SENT_RESPONSE_ACCEPTED":
            raise FinalizationError("CROSS_BINDING_MISMATCH", f"bridge {phase} request status/order drift")
        for field in ("rendered_prompt_sha256", "canonical_request_sha256", "completion_raw_response_sha256"):
            _require_sha(request[field], f"bridge {phase} {field}")
    if (
        requests[0]["rendered_prompt_sha256"] != rr0_rendered_prompt_sha256
        or requests[1]["rendered_prompt_sha256"] != dynamic["rendered_prompt_sha256"]
    ):
        raise FinalizationError(
            "CROSS_BINDING_MISMATCH", "bridge request prompt hashes are not cross-bound"
        )
    _reject_forbidden_keys(requests)
    _require_false_boundaries(bridge, "bridge")


def _validate_failure_pair(
    sidecar: Mapping[str, Any], failure_bridge: Mapping[str, Any],
    stage_sha: str, process_sha: str, sidecar_file_sha: str,
    identity: Mapping[str, Any], in_job_sha: str,
) -> None:
    sidecar_fields = {
        "schema_version", "authority", "status", "run_plan_sha256", "task_id",
        "arm_id", "attempt", "seed", "expected_phase_sequence",
        "attempted_phase_sequence", "monotonic_start_ns", "monotonic_end_ns",
        "failure_code", "failure_detail_sha256", "captured_exception_detail_sha256",
        "allocation_status", "slurm_job_identity", "slurm_in_job_snapshot_sha256",
        "runner_v2_record_emitted", "official_evaluator_invoked",
        "official_outcomes_opened", "scientific_authority_delta",
    }
    failure_bridge_fields = {
        "schema_version", "authority", "status", "tuple_identity",
        "runtime_stage_sha256", "process_attestation_sha256",
        "adapter_cannot_check_file_sha256", "request_bindings",
        "dynamic_rr1_pretokenize_bindings", "protected_bodies_retained",
        "runner_v2_population_ledger_status", "production_admissibility",
        "scientific_authority_delta",
    }
    _require_exact(sidecar, sidecar_fields, "attempt failure sidecar")
    _require_exact(failure_bridge, failure_bridge_fields, "failure bridge")
    if sidecar.get("schema_version") != "orion.p1.scienceagentbench.lunarc-generation-attempt-cannot-check.v1" or sidecar.get("status") != "CANNOT_CHECK":
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt failure sidecar schema/status mismatch")
    if {key: sidecar.get(key) for key in ("task_id", "arm_id", "attempt", "seed")} != FIXED_TUPLE:
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt failure sidecar tuple mismatch")
    if (
        sidecar["run_plan_sha256"] != EXPECTED_STAGE_SOURCE_SHA256["plan"]
        or sidecar["expected_phase_sequence"] != ["RR_PHASE0", "RR_PHASE1"]
        or sidecar["attempted_phase_sequence"]
        not in ([], ["RR_PHASE0"], ["RR_PHASE0", "RR_PHASE1"])
        or sidecar["allocation_status"] != "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION"
        or sidecar["failure_code"]
        not in {"ATTEMPT_DEADLINE_EXCEEDED", "DIRECT_ROUTE_EXECUTION_FAILED"}
        or sidecar["slurm_job_identity"] != identity
        or sidecar["slurm_in_job_snapshot_sha256"] != in_job_sha
        or sidecar["runner_v2_record_emitted"] is not False
        or sidecar["official_evaluator_invoked"] is not False
        or sidecar["official_outcomes_opened"] is not False
        or sidecar["scientific_authority_delta"] != "NONE"
    ):
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt failure sidecar producer shape mismatch")
    _require_sha(sidecar["failure_detail_sha256"], "failure sidecar detail")
    if sidecar["captured_exception_detail_sha256"] is not None:
        _require_sha(sidecar["captured_exception_detail_sha256"], "captured exception detail")
    for field in ("monotonic_start_ns", "monotonic_end_ns"):
        value = sidecar[field]
        if value is not None and (not isinstance(value, str) or UINT_RE.fullmatch(value) is None):
            raise FinalizationError("CAPTURE_CANNOT_CHECK", f"attempt failure {field} is invalid")
    start_ns, end_ns = sidecar["monotonic_start_ns"], sidecar["monotonic_end_ns"]
    if end_ns is not None and (start_ns is None or int(end_ns) < int(start_ns)):
        raise FinalizationError("CAPTURE_CANNOT_CHECK", "attempt failure monotonic interval is invalid")
    if failure_bridge.get("schema_version") != "orion.p1.scienceagentbench.protected-rr1-direct-route-failure-binding.v1" or failure_bridge.get("status") != "CANNOT_CHECK" or failure_bridge.get("tuple_identity") != FIXED_TUPLE:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "failure bridge schema/status/tuple mismatch")
    if failure_bridge.get("runtime_stage_sha256") != stage_sha or failure_bridge.get("process_attestation_sha256") != process_sha or failure_bridge.get("adapter_cannot_check_file_sha256") != sidecar_file_sha:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "failure bridge file hash chain mismatch")
    requests = failure_bridge["request_bindings"]
    dynamics = failure_bridge["dynamic_rr1_pretokenize_bindings"]
    if not isinstance(requests, list) or len(requests) > 2 or not isinstance(dynamics, list) or len(dynamics) > 1:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "failure bridge partial binding counts are invalid")
    request_required = {
        "phase_id", "rendered_prompt_sha256", "canonical_request_sha256", "cache_prompt",
    }
    request_allowed = request_required | {"transport_status", "completion_raw_response_sha256"}
    for index, request in enumerate(requests):
        if not isinstance(request, dict) or not request_required.issubset(request) or not set(request).issubset(request_allowed):
            raise FinalizationError("CROSS_BINDING_MISMATCH", "failure bridge request binding shape is invalid")
        if request["phase_id"] != ("RR_PHASE0", "RR_PHASE1")[index] or request["cache_prompt"] is not False:
            raise FinalizationError("CROSS_BINDING_MISMATCH", "failure bridge request order/cache binding drift")
        _require_sha(request["rendered_prompt_sha256"], "failure request rendered prompt")
        _require_sha(request["canonical_request_sha256"], "failure request canonical request")
        if "completion_raw_response_sha256" in request:
            _require_sha(request["completion_raw_response_sha256"], "failure request response")
        if "transport_status" in request and request["transport_status"] not in {
            "VALIDATED_NOT_SENT", "SENT_RESPONSE_PENDING", "SENT_RESPONSE_REJECTED",
            "SENT_RESPONSE_ACCEPTED",
        }:
            raise FinalizationError("CROSS_BINDING_MISMATCH", "failure request transport status drift")
    for dynamic in dynamics:
        _require_exact(dynamic, DYNAMIC_CORE_FIELDS, "failure bridge dynamic RR1 binding")
        if dynamic["phase_id"] != "RR_PHASE1":
            raise FinalizationError("CROSS_BINDING_MISMATCH", "failure dynamic binding phase drift")
        for field in (
            "rendered_prompt_sha256", "tokenize_request_sha256",
            "tokenize_raw_response_sha256", "token_array_sha256",
        ):
            _require_sha(dynamic[field], f"failure dynamic {field}")
    _reject_forbidden_keys(requests)
    _reject_forbidden_keys(dynamics)
    _require_false_boundaries(sidecar, "attempt failure sidecar")
    _require_false_boundaries(failure_bridge, "failure bridge")
    raise FinalizationError("ATTEMPT_CAPTURE_CANNOT_CHECK", "attempt emitted the mutually exclusive typed failure pair")


def _same_target_record(left: Mapping[str, str], right: Mapping[str, str]) -> bool:
    return all(left[field] == right[field] for field in SACCT_FIELDS)


def _validate_nonoverlap(rows: list[dict[str, str]], target: Mapping[str, str]) -> None:
    matching = [row for row in rows if row["JobIDRaw"] == target["JobIDRaw"]]
    if len(matching) != 1 or not _same_target_record(matching[0], target):
        raise FinalizationError("NONOVERLAP_CANNOT_CHECK", "non-overlap query lacks the exact target allocation row")
    target_start = _parse_slurm_time(target["Start"], "target start")
    target_end = _parse_slurm_time(target["End"], "target end")
    if target_start is None or target_end is None:
        raise FinalizationError("NONOVERLAP_CANNOT_CHECK", "target interval is unknown")
    for row in rows:
        if row["JobIDRaw"] == target["JobIDRaw"]:
            continue
        alloc = _parse_tres(row["AllocTRES"], "non-overlap AllocTRES")
        if _gpu_tres_count(alloc, "non-overlap") == 0:
            continue
        other_start = _parse_slurm_time(row["Start"], "non-overlap start")
        other_end = _parse_slurm_time(row["End"], "non-overlap end", allow_unknown=True)
        if other_start is None:
            raise FinalizationError("NONOVERLAP_CANNOT_CHECK", "other allocation start is unknown")
        overlaps = other_start < target_end and (other_end is None or target_start < other_end)
        if overlaps:
            raise FinalizationError("NONOVERLAP_CANNOT_CHECK", "another same-node GPU allocation overlaps conservatively")


def _validate_capture_provenance(
    provenance: Mapping[str, Any], hashes: Mapping[str, str],
    expected_argv: Mapping[str, list[str]], terminal: Mapping[str, str],
) -> None:
    _require_exact(provenance, CAPTURE_PROVENANCE_FIELDS, "scheduler capture provenance")
    observations = provenance["terminal_poll_observations"]
    if (
        not isinstance(observations, list)
        or not observations
        or len(observations) != provenance["terminal_poll_count"]
        or len(observations) > TERMINAL_POLL_LIMIT
    ):
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", "terminal poll provenance count is invalid"
        )
    previous_time = -1
    for index, observation in enumerate(observations, 1):
        _require_exact(
            observation,
            {
                "poll_index", "observed_at_monotonic_ns", "argv",
                "row_count", "raw_sha256", "state", "partition",
                "classification", "terminal",
            },
            "terminal poll observation",
        )
        timestamp = observation["observed_at_monotonic_ns"]
        row_count = observation["row_count"]
        state = observation["state"]
        partition = observation["partition"]
        classification = observation["classification"]
        valid_profile = (
            (
                row_count == 0
                and state is None
                and partition is None
                and classification == "NO_ROW"
            )
            or (
                row_count == 1
                and isinstance(state, str)
                and re.fullmatch(r"[A-Z][A-Z_]*", state) is not None
                and state not in TERMINAL_STATES
                and partition == ""
                and classification == "PRETERMINAL_EMPTY_PARTITION"
            )
            or (
                row_count == 1
                and isinstance(state, str)
                and re.fullmatch(r"[A-Z][A-Z_]*", state) is not None
                and state not in TERMINAL_STATES
                and partition == "gpua40i"
                and classification == "PRETERMINAL_PARTITION_READY"
            )
            or (
                row_count == 1
                and state in TERMINAL_STATES
                and partition in {"", "gpua40i"}
                and classification
                == "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL"
            )
            or (
                row_count == 1
                and state in TERMINAL_STATES
                and partition == "gpua40i"
                and classification == "TERMINAL_COMPLETE_gpua40i"
            )
        )
        if (
            observation["poll_index"] != index
            or not isinstance(timestamp, str)
            or UINT_RE.fullmatch(timestamp) is None
            or int(timestamp) < previous_time
            or (
                previous_time >= 0
                and int(timestamp) - previous_time
                < TERMINAL_POLL_INTERVAL_SECONDS * 1_000_000_000
            )
            or observation["argv"] != expected_argv["terminal_sacct"]
            or isinstance(row_count, bool)
            or row_count not in {0, 1}
            or not isinstance(observation["raw_sha256"], str)
            or SHA_RE.fullmatch(observation["raw_sha256"]) is None
            or not valid_profile
            or not isinstance(observation["terminal"], bool)
            or (observation["terminal"] is True) != (index == len(observations))
            or (observation["terminal"] is True)
            != (classification == "TERMINAL_COMPLETE_gpua40i")
            or (index == len(observations) and row_count != 1)
        ):
            raise FinalizationError(
                "SCHEDULER_CAPTURE_FAILED", "terminal poll observation drift"
            )
        previous_time = int(timestamp)
    terminal_monotonic = provenance["terminal_observed_monotonic_ns"]
    if (
        not isinstance(terminal_monotonic, str)
        or UINT_RE.fullmatch(terminal_monotonic) is None
        or int(terminal_monotonic) < previous_time
    ):
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", "terminal observation monotonic time drift"
        )
    terminal_utc = _parse_utc(
        provenance["terminal_observed_at_utc"], "terminal observation UTC"
    )
    post_started_utc = _parse_utc(
        provenance["post_job_scontrol_started_at_utc"],
        "post-job scontrol start UTC",
    )
    post_utc = _parse_utc(
        provenance["post_job_scontrol_completed_at_utc"],
        "post-job scontrol completion UTC",
    )
    command_observations = provenance["capture_command_observations"]
    expected_keys = [
        "post_job_scontrol", "scheduler_config", "scheduler_partition",
        "scheduler_node", "nonoverlap_sacct",
    ]
    if not isinstance(command_observations, list) or len(command_observations) != 5:
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", "capture command timing count is invalid"
        )
    previous_completion = int(terminal_monotonic)
    previous_utc = terminal_utc
    for command, key in zip(command_observations, expected_keys):
        _require_exact(
            command,
            {
                "key", "argv", "started_at_monotonic_ns",
                "started_at_utc", "completed_at_monotonic_ns",
                "completed_at_utc", "duration_seconds",
                "seconds_after_terminal_observation",
                "post_terminal_deadline_remaining_seconds",
                "completed_before_post_terminal_deadline",
            },
            "capture command observation",
        )
        started_raw = command["started_at_monotonic_ns"]
        completed_raw = command["completed_at_monotonic_ns"]
        if (
            not isinstance(started_raw, str)
            or UINT_RE.fullmatch(started_raw) is None
            or not isinstance(completed_raw, str)
            or UINT_RE.fullmatch(completed_raw) is None
        ):
            raise FinalizationError(
                "SCHEDULER_CAPTURE_FAILED", "capture command monotonic time is invalid"
            )
        started_ns = int(started_raw)
        completed_ns = int(completed_raw)
        duration_ns = completed_ns - started_ns
        elapsed_ns = completed_ns - int(terminal_monotonic)
        remaining_ns = (
            POST_TERMINAL_CAPTURE_DEADLINE_SECONDS * 1_000_000_000 - elapsed_ns
        )
        started_utc = _parse_utc(
            command["started_at_utc"], f"{key} start UTC"
        )
        completed_utc = _parse_utc(
            command["completed_at_utc"], f"{key} completion UTC"
        )
        if (
            command["key"] != key
            or command["argv"] != expected_argv[key]
            or started_ns < previous_completion
            or completed_ns < started_ns
            or duration_ns > CAPTURE_COMMAND_TIMEOUT_SECONDS * 1_000_000_000
            or elapsed_ns < 0
            or remaining_ns < 0
            or command["duration_seconds"] != _format_ns_seconds(duration_ns)
            or command["seconds_after_terminal_observation"]
            != _format_ns_seconds(elapsed_ns)
            or command["post_terminal_deadline_remaining_seconds"]
            != _format_ns_seconds(remaining_ns)
            or command["completed_before_post_terminal_deadline"] is not True
            or started_utc < previous_utc
            or completed_utc < started_utc
        ):
            raise FinalizationError(
                "SCHEDULER_CAPTURE_FAILED", "capture command timing/deadline drift"
            )
        previous_completion = completed_ns
        previous_utc = completed_utc
    first_command = command_observations[0]
    first_start_latency_ns = (
        int(first_command["started_at_monotonic_ns"]) - int(terminal_monotonic)
    )
    if (
        first_start_latency_ns < 0
        or first_start_latency_ns
        > POST_JOB_SCONTROL_START_LATENCY_LIMIT_SECONDS * 1_000_000_000
        or post_started_utc < terminal_utc
        or post_utc < terminal_utc
        or provenance["post_job_scontrol_started_at_utc"]
        != first_command["started_at_utc"]
        or provenance["post_job_scontrol_start_seconds_after_terminal_observation"]
        != _format_ns_seconds(first_start_latency_ns)
        or provenance["post_job_scontrol_completed_at_utc"]
        != first_command["completed_at_utc"]
        or provenance["post_job_scontrol_seconds_after_terminal_observation"]
        != first_command["seconds_after_terminal_observation"]
    ):
        raise FinalizationError(
            "SCHEDULER_CAPTURE_FAILED", "post-job scontrol timing is not first and bound"
        )
    if (
        provenance["schema_version"]
        != "orion.p1.scienceagentbench.protected-rr1-scheduler-capture-provenance.v2"
        or provenance["authority"]
        != "EXACT_SCHEDULER_CAPTURE_COMMAND_AND_RAW_BYTE_BINDING_ONLY"
        or provenance["status"] != "PASS_EXACT_POST_JOB_SCHEDULER_CAPTURE"
        or provenance["slurm_job_id"] != terminal["JobIDRaw"]
        or provenance["partition"] != terminal["Partition"]
        or provenance["node_name"] != terminal["NodeList"]
        or provenance["allocation_started_at"] != terminal["Start"]
        or provenance["allocation_ended_at"] != terminal["End"]
        or provenance["capture_argv"] != expected_argv
        or provenance["terminal_poll_interval_seconds"] != TERMINAL_POLL_INTERVAL_SECONDS
        or provenance["terminal_poll_limit"] != TERMINAL_POLL_LIMIT
        or provenance["capture_command_timeout_seconds"] != CAPTURE_COMMAND_TIMEOUT_SECONDS
        or provenance["post_terminal_capture_deadline_seconds"]
        != POST_TERMINAL_CAPTURE_DEADLINE_SECONDS
        or provenance["post_job_scontrol_start_latency_limit_seconds"]
        != POST_JOB_SCONTROL_START_LATENCY_LIMIT_SECONDS
        or provenance["partition_source"] != "INTERNAL_FROZEN_gpua40i"
        or provenance["node_source"] != "DERIVED_FROM_UNIQUE_TERMINAL_SACCT_NODELIST"
        or provenance["credential_environment_read"] is not False
        or provenance["stderr_retained"] is not False
        or provenance["job_submitted"] is not False
        or provenance["scientific_authority_delta"] != "NONE"
    ):
        raise FinalizationError("SCHEDULER_CAPTURE_FAILED", "scheduler capture provenance field drift")
    expected_raw = {
        name: hashes[name]
        for name in CAPTURE_FILE_BY_KEY.values()
    }
    if provenance["raw_file_sha256"] != expected_raw:
        raise FinalizationError("SCHEDULER_CAPTURE_FAILED", "scheduler capture raw hash set mismatch")


def _load_evidence(
    evidence_root: Path, capture_root: Path, adapter: ModuleType
) -> tuple[dict[str, bytes], bool]:
    del adapter
    root_fd = _open_directory(evidence_root, "evidence root")
    capture_fd = attempt_fd = runtime_fd = None
    try:
        capture_fd = _open_directory(capture_root, "capture root")
        evidence_identity = os.fstat(root_fd)
        capture_identity = os.fstat(capture_fd)
        if (evidence_identity.st_dev, evidence_identity.st_ino) == (
            capture_identity.st_dev, capture_identity.st_ino
        ):
            raise FinalizationError(
                "INPUT_SET_INVALID",
                "evidence and capture roots resolve to the same held directory",
            )
        if _entry_exists(capture_fd, "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"):
            raise FinalizationError(
                "SCHEDULER_CAPTURE_FAILED",
                "capture root contains only a typed partial-capture failure",
            )
        attempt_fd = _open_child_directory(root_fd, "attempt")
        runtime_fd = _open_child_directory(root_fd, "runtime-inputs")
        present_success = [_entry_exists(attempt_fd, name) for name in SUCCESS_PAIR]
        present_failure = [_entry_exists(attempt_fd, name) for name in FAILURE_PAIR]
        success_pair = all(present_success) and not any(present_failure)
        failure_pair = all(present_failure) and not any(present_success)
        if not (success_pair ^ failure_pair):
            raise FinalizationError("INPUT_SET_INVALID", "success and failure attempt pairs must be mutually exclusive and complete")
        payloads: dict[str, bytes] = {}
        for name in EVIDENCE_ROOT_COMMON:
            payloads[name] = _read_held(root_fd, name, name)
        for name in CAPTURE_ROOT_COMMON:
            payloads[name] = _read_held(
                capture_fd, name, name, allowed_modes=frozenset({0o400})
            )
        if _entry_exists(root_fd, "SCHEDULER_EXPORT_V1.jsonl"):
            payloads["SCHEDULER_EXPORT_V1.jsonl"] = _read_held(
                root_fd, "SCHEDULER_EXPORT_V1.jsonl", "optional scheduler export assertion"
            )
        for name in ATTEMPT_COMMON:
            payloads[f"attempt/{name}"] = _read_held(attempt_fd, name, name)
        for name in SUCCESS_PAIR if success_pair else FAILURE_PAIR:
            payloads[f"attempt/{name}"] = _read_held(attempt_fd, name, name)
        payloads["runtime-inputs/RUN_PLAN.json"] = _read_held(runtime_fd, "RUN_PLAN.json", "full Runner V2 plan")
        return payloads, success_pair
    finally:
        if runtime_fd is not None:
            os.close(runtime_fd)
        if attempt_fd is not None:
            os.close(attempt_fd)
        if capture_fd is not None:
            os.close(capture_fd)
        os.close(root_fd)


def _validate_evidence(
    payloads: dict[str, bytes], success_pair: bool, adapter: ModuleType
) -> tuple[dict[str, Any], bytes]:
    provided_export_payload = payloads.get("SCHEDULER_EXPORT_V1.jsonl")
    source_hashes = {
        name: sha256_bytes(payload)
        for name, payload in payloads.items()
        if name != "SCHEDULER_EXPORT_V1.jsonl"
    }
    hashes = dict(source_hashes)
    plan = strict_json(payloads["runtime-inputs/RUN_PLAN.json"], "full Runner V2 plan", adapter)
    _validate_plan(plan, adapter)
    stage = strict_json(payloads["STAGED_RUNTIME_INPUT_V1.json"], "runtime stage", adapter)
    process = strict_json(payloads["PROCESS_ATTESTATION_V1.json"], "process attestation", adapter)
    _validate_stage_process(
        stage, process, payloads["runtime-inputs/RUN_PLAN.json"],
        hashes["STAGED_RUNTIME_INPUT_V1.json"], hashes["PROCESS_ATTESTATION_V1.json"],
    )
    identity_record = strict_json(
        payloads["attempt/SLURM_IDENTITY_AND_SNAPSHOT_V1.json"], "in-job SLURM identity", adapter
    )
    _require_exact(
        identity_record,
        {"slurm_job_identity", "slurm_in_job_snapshot_sha256", "allocation_status", "environment_only_exclusivity_claimed"},
        "in-job SLURM identity",
    )
    identity = _validate_job_identity(identity_record["slurm_job_identity"])
    in_job_sha = hashes["attempt/SCONTROL_IN_JOB_V1.txt"]
    if identity_record["slurm_in_job_snapshot_sha256"] != in_job_sha or identity_record["allocation_status"] != "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION" or identity_record["environment_only_exclusivity_claimed"] is not False:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "in-job scontrol hash/identity boundary mismatch")
    in_job = parse_scontrol_snapshot(payloads["attempt/SCONTROL_IN_JOB_V1.txt"], "in-job scontrol -dd")
    if in_job["JobId"] != identity["job_id"] or in_job["JobState"] != "RUNNING":
        raise FinalizationError("CROSS_BINDING_MISMATCH", "in-job scontrol job identity/state mismatch")

    capture_provenance = strict_json(
        payloads["SCHEDULER_CAPTURE_PROVENANCE_V1.json"],
        "scheduler capture provenance", adapter,
    )

    if not success_pair:
        sidecar = strict_json(payloads["attempt/ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json"], "attempt failure sidecar", adapter)
        failure_bridge = strict_json(payloads["attempt/DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json"], "failure bridge", adapter)
        _validate_failure_pair(
            sidecar, failure_bridge,
            hashes["STAGED_RUNTIME_INPUT_V1.json"],
            hashes["PROCESS_ATTESTATION_V1.json"],
            hashes["attempt/ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json"],
            identity,
            in_job_sha,
        )

    capture = strict_json(payloads["attempt/ATTEMPT_CAPTURE_V1.json"], "attempt capture", adapter)
    dynamic = strict_json(payloads["attempt/DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"], "dynamic RR1 binding", adapter)
    bridge = strict_json(payloads["attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"], "direct-route bridge", adapter)
    cleanup = strict_json(payloads["SERVER_CLEANUP_V1.json"], "server cleanup", adapter)
    gpu_record = strict_json(payloads["GPU_ALLOCATION_IDENTITY_V1.json"], "one-A40 identity", adapter)
    _validate_capture(capture, adapter, plan, identity, in_job_sha)
    dynamic_core = _validate_dynamic(dynamic)
    del dynamic_core
    _validate_bridge(
        bridge, capture, dynamic,
        hashes["STAGED_RUNTIME_INPUT_V1.json"],
        hashes["PROCESS_ATTESTATION_V1.json"],
        hashes["attempt/DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"],
        stage["run_plan_binding_extension"],
        stage["prompt_commitments_by_phase"]["RR_PHASE0"]["rendered_prompt_sha256"],
    )
    _validate_cleanup(cleanup)
    gpu = _validate_gpu(gpu_record, identity["job_id"])

    terminal_rows = parse_sacct_snapshot(payloads["POST_JOB_SACCT_V1.txt"], allow_multiple=False)
    terminal = terminal_rows[0]
    overlap_rows = parse_sacct_snapshot(payloads["POST_JOB_SACCT_NONOVERLAP_V1.txt"], allow_multiple=True)
    post = parse_scontrol_snapshot(payloads["POST_JOB_SCONTROL_V1.txt"], "post-job scontrol -dd")
    config = parse_config_snapshots(
        payloads["SCHEDULER_CONFIG_V1.txt"],
        payloads["SCHEDULER_PARTITION_V1.txt"],
        payloads["SCHEDULER_NODE_V1.txt"],
    )
    if config["node"]["NodeName"] != terminal["NodeList"]:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "node snapshot and allocation node mismatch")
    if (
        terminal["JobIDRaw"] != identity["job_id"]
        or post["JobId"] != identity["job_id"]
        or in_job["NodeList"] != terminal["NodeList"]
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "terminal scheduler identity mismatch")
    if (
        terminal["State"] != post["JobState"]
        or terminal["ExitCode"] != post["ExitCode"]
        or terminal["Start"] != post["StartTime"]
        or terminal["End"] != post["EndTime"]
        or terminal["NodeList"] != post["NodeList"]
    ):
        raise FinalizationError("CROSS_BINDING_MISMATCH", "sacct and post-job scontrol fields disagree")
    terminal_alloc = _parse_tres(terminal["AllocTRES"], "terminal AllocTRES")
    terminal_req = _parse_tres(terminal["ReqTRES"], "terminal ReqTRES")
    if (
        terminal["Partition"] != "gpua40i"
        or terminal["Account"] != "lu2026-2-51"
        or terminal["NNodes"] != "1"
        or terminal["NCPUS"] != "8"
        or terminal["NTasks"] not in {"", "1"}
        or terminal["ReqCPUS"] != "8"
        or terminal["ReqMem"] != "64G"
        or terminal["TimelimitRaw"] != "60"
        or terminal["Constraints"] != ""
        or terminal_req.get("gres/gpu:a40") != "1"
        or _gpu_tres_count(terminal_req, "terminal ReqTRES") != 1
        or terminal_req.get("mem") != "64G"
        or terminal_alloc.get("gres/gpu:a40") != "1"
        or _gpu_tres_count(terminal_alloc, "terminal AllocTRES") != 1
        or terminal_alloc.get("mem") != "64G"
    ):
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "terminal sacct lacks exact one A40 GRES")
    started = _parse_slurm_time(terminal["Start"], "terminal start")
    ended = _parse_slurm_time(terminal["End"], "terminal end")
    if started is None or ended is None or ended <= started:
        raise FinalizationError("TERMINAL_JOB_NOT_SUCCESSFUL", "terminal interval is not strictly positive")
    if terminal["State"] != "COMPLETED" or terminal["ExitCode"] != "0:0" or terminal["DerivedExitCode"] != "0:0":
        raise FinalizationError("TERMINAL_JOB_NOT_SUCCESSFUL", "terminal job was not COMPLETED with 0:0")
    _validate_nonoverlap(overlap_rows, terminal)

    gres_match = re.fullmatch(r"gpu:a40:1\(IDX:(0|[1-9][0-9]*)\)", post["GresDetail"])
    if gres_match is None:
        raise FinalizationError("EXCLUSIVITY_CANNOT_CHECK", "post-job GresDetail is not exact A40 one-GRES")
    gres_index = gres_match.group(1)
    if gpu["slurm_job_gpus"] != gres_index or gpu["slurm_step_gpus"] != gres_index:
        raise FinalizationError("CROSS_BINDING_MISMATCH", "SLURM job/step GPU index and scontrol GresDetail disagree")
    expected_allocation = {
        "node_name": terminal["NodeList"], "gres_name": "gpu", "gres_type": "a40",
        "gres_index": gres_index, "gpu_uuid": gpu["gpu_uuid"],
    }
    expected_argv = _materialized_argv(
        identity["job_id"], terminal["Partition"], terminal["Start"], terminal["End"], terminal["NodeList"]
    )
    _validate_capture_provenance(capture_provenance, hashes, expected_argv, terminal)
    export = {
        "schema_version": "orion.p1.scienceagentbench.protected-rr1-one-tuple-scheduler-export.v2",
        "authority": "CANONICAL_SCHEDULER_AND_IN_JOB_METADATA_BINDING_ONLY",
        "status": "SCHEDULER_CONFIRMED_ONE_TUPLE_TERMINAL_EXCLUSIVE_GRES",
        "tuple_identity": dict(FIXED_TUPLE),
        "slurm_job_identity": identity,
        "capture_argv": expected_argv,
        "source_sha256": source_hashes,
        "in_job_snapshot_sha256": in_job_sha,
        "scheduler_record_source": "TERMINAL_SACCT__POST_JOB_SCONTROL_DD__CONFIG_PARTITION_NODE__NONOVERLAP_SACCT__IN_JOB_GPU_IDENTITY",
        "scheduler_job_state": "COMPLETED",
        "scheduler_exit_code": "0:0",
        "allocation_started_at": terminal["Start"],
        "allocation_ended_at": terminal["End"],
        "node_name": terminal["NodeList"],
        "partition": "gpua40i",
        "account": "lu2026-2-51",
        "allocated_cpu_count": "8",
        "allocated_memory": "64G",
        "timelimit_raw_minutes": "60",
        "constraints": "",
        "allocated_gpu_count": "1",
        "gpu_allocations": [expected_allocation],
        "exclusive_gres_status": "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES",
        "attempt_scope_status": "ONE_TASK_ARM_ATTEMPT_ONLY_CONFIRMED",
        "nonoverlap_query_status": "NODE_WIDE_BOUNDED_A40_GRES_QUERY_NO_OVERLAP_CONFIRMED",
        "nonoverlap_conflict_count": 0,
        "whole_node_exclusivity_claimed": False,
        "protected_bodies_retained": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }
    export_payload = canonical_bytes(export) + b"\n"
    if provided_export_payload is not None:
        provided_export = parse_scheduler_export(provided_export_payload, adapter)
        if provided_export != export or provided_export_payload != export_payload:
            raise FinalizationError(
                "CROSS_BINDING_MISMATCH",
                "optional scheduler export assertion differs from deterministic export",
            )
    hashes["SCHEDULER_EXPORT_V1.jsonl"] = sha256_bytes(export_payload)
    exact_export = {
        "schema_version": "orion.p1.scienceagentbench.protected-rr1-one-tuple-scheduler-export.v2",
        "authority": "CANONICAL_SCHEDULER_AND_IN_JOB_METADATA_BINDING_ONLY",
        "status": "SCHEDULER_CONFIRMED_ONE_TUPLE_TERMINAL_EXCLUSIVE_GRES",
        "scheduler_record_source": "TERMINAL_SACCT__POST_JOB_SCONTROL_DD__CONFIG_PARTITION_NODE__NONOVERLAP_SACCT__IN_JOB_GPU_IDENTITY",
        "scheduler_job_state": "COMPLETED", "scheduler_exit_code": "0:0",
        "allocation_started_at": terminal["Start"], "allocation_ended_at": terminal["End"],
        "node_name": terminal["NodeList"], "allocated_gpu_count": "1",
        "partition": "gpua40i", "account": "lu2026-2-51",
        "allocated_cpu_count": "8", "allocated_memory": "64G",
        "timelimit_raw_minutes": "60", "constraints": "",
        "exclusive_gres_status": "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES",
        "attempt_scope_status": "ONE_TASK_ARM_ATTEMPT_ONLY_CONFIRMED",
        "nonoverlap_query_status": "NODE_WIDE_BOUNDED_A40_GRES_QUERY_NO_OVERLAP_CONFIRMED",
        "nonoverlap_conflict_count": 0, "whole_node_exclusivity_claimed": False,
        "protected_bodies_retained": False, "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
        "production_admissibility": "CANNOT_CHECK", "scientific_authority_delta": "NONE",
    }
    for key, expected in exact_export.items():
        if export.get(key) != expected:
            code = "NONOVERLAP_CANNOT_CHECK" if key.startswith("nonoverlap") else "EXCLUSIVITY_CANNOT_CHECK"
            raise FinalizationError(code, f"scheduler export field mismatch: {key}")

    receipt = {
        "schema_version": "orion.p1.scienceagentbench.protected-rr1-one-tuple-finalization-receipt.v2",
        "authority": "ONE_TUPLE_SCHEDULER_AND_CAPTURE_METADATA_CONFORMANCE_ONLY__NO_918_LEDGER_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "status": SUCCESS_STATUS,
        "tuple_identity": dict(FIXED_TUPLE),
        "slurm_job_identity": identity,
        "input_artifact_sha256": source_hashes,
        "finalizer_contract_sha256": CONTRACT_SHA256,
        "finalizer_schema_sha256": SCHEMA_SHA256,
        "finalizer_module_sha256": adapter._finalizer_module_raw_sha256,
        "adapter_donor_sha256": ADAPTER_SHA256,
        "scheduler_export_raw_record_sha256": hashes["SCHEDULER_EXPORT_V1.jsonl"],
        "post_job_sacct_sha256": hashes["POST_JOB_SACCT_V1.txt"],
        "post_job_scontrol_sha256": hashes["POST_JOB_SCONTROL_V1.txt"],
        "attempt_capture_file_sha256": hashes["attempt/ATTEMPT_CAPTURE_V1.json"],
        "attempt_capture_canonical_sha256": canonical_hash(capture),
        "runtime_stage_file_sha256": hashes["STAGED_RUNTIME_INPUT_V1.json"],
        "process_attestation_file_sha256": hashes["PROCESS_ATTESTATION_V1.json"],
        "bridge_file_sha256": hashes["attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"],
        "dynamic_file_sha256": hashes["attempt/DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"],
        "terminal_job_state": terminal["State"],
        "terminal_exit_code": terminal["ExitCode"],
        "allocation_interval": {
            "started_at": terminal["Start"], "ended_at": terminal["End"],
            "semantics": "HALF_OPEN_SLURM_CONTROLLER_LOCAL_SECONDS",
        },
        "allocation": {
            "node_name": terminal["NodeList"], "allocated_gpu_count": "1",
            "partition": "gpua40i", "account": "lu2026-2-51",
            "allocated_cpu_count": "8", "allocated_memory": "64G",
            "timelimit_raw_minutes": "60", "constraints": "",
            "gpu_allocations": [expected_allocation],
            "whole_node_exclusivity_claimed": False,
        },
        "exclusive_gres_status": "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES",
        "nonoverlap_status": "NODE_WIDE_BOUNDED_A40_GRES_QUERY_NO_OVERLAP_CONFIRMED",
        "overlap_conflict_count": 0,
        "capture_argv": expected_argv,
        "attempt_capture_status": capture["status"],
        "dynamic_rr1_pretokenize_status": dynamic["status"],
        "server_cleanup_status": cleanup["status"],
        "protected_bodies_opened_by_finalizer": False,
        "protected_bodies_retained": False,
        "generation_invoked_by_finalizer": False,
        "network_invoked_by_finalizer": False,
        "external_api_invoked_by_finalizer": False,
        "credential_environment_read_by_finalizer": False,
        "one_tuple_generation_observed": True,
        "model_completion_calls": 2,
        "task_execution_invoked": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
        "runner_v2_population_finalizer_invoked": False,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }
    schema = strict_json(adapter._finalizer_schema_bytes, "finalizer output schema", adapter)
    if set(receipt) != set(schema["success"]["required_fields"]):
        raise FinalizationError("OUTPUT_INVALID", "success receipt fields drift from frozen schema")
    return receipt, export_payload


def _cannot_receipt(exc: FinalizationError) -> dict[str, Any]:
    receipt = {
        "schema_version": "orion.p1.scienceagentbench.protected-rr1-one-tuple-finalization-cannot-check.v2",
        "authority": "ONE_TUPLE_FINALIZATION_FAILURE_METADATA_ONLY__NO_918_LEDGER_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "status": CANNOT_STATUS,
        "tuple_identity": dict(FIXED_TUPLE),
        "failure_code": exc.code,
        "failure_detail_sha256": sha256_bytes(f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")),
        "success_receipt_emitted": False,
        "protected_bodies_opened_by_finalizer": False,
        "protected_bodies_retained": False,
        "generation_invoked_by_finalizer": False,
        "network_invoked_by_finalizer": False,
        "external_api_invoked_by_finalizer": False,
        "credential_environment_read_by_finalizer": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": False,
        "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
        "runner_v2_population_finalizer_invoked": False,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }
    expected = {
        "schema_version", "authority", "status", "tuple_identity", "failure_code",
        "failure_detail_sha256", "success_receipt_emitted",
        "protected_bodies_opened_by_finalizer", "protected_bodies_retained",
        "generation_invoked_by_finalizer", "network_invoked_by_finalizer",
        "external_api_invoked_by_finalizer", "credential_environment_read_by_finalizer",
        "official_evaluator_invoked", "official_outcomes_opened",
        "runner_v2_population_ledger_status", "runner_v2_population_finalizer_invoked",
        "production_admissibility", "scientific_authority_delta",
    }
    if set(receipt) != expected:
        raise FinalizationError("OUTPUT_INVALID", "CANNOT_CHECK receipt fields drift from frozen schema")
    return receipt


def finalize(
    evidence_root: Path, capture_root: Path, output_root: Path
) -> tuple[int, dict[str, Any]]:
    if (
        not evidence_root.is_absolute()
        or not capture_root.is_absolute()
        or not output_root.is_absolute()
        or len({evidence_root, capture_root, output_root}) != 3
    ):
        raise FinalizationError(
            "ARGV_INVALID", "finalize roots must be three distinct absolute paths"
        )
    output_fd = _create_output_root(output_root)
    try:
        try:
            adapter = load_exact_adapter()
            payloads, success_pair = _load_evidence(
                evidence_root, capture_root, adapter
            )
            receipt, export_payload = _validate_evidence(
                payloads, success_pair, adapter
            )
        except Exception as caught:
            exc = _typed_unexpected_failure(
                caught,
                "FINALIZER_RUNTIME_FAILED",
                "unexpected finalizer validation runtime failure",
            )
            receipt = _cannot_receipt(exc)
            _write_new_json(output_fd, CANNOT_NAME, receipt)
            return 1, receipt
        _, export_identity = _write_new_bytes(
            output_fd, "SCHEDULER_EXPORT_V1.jsonl", export_payload
        )
        try:
            _write_new_json(output_fd, SUCCESS_NAME, receipt)
        except FinalizationError:
            _rollback_new_output_root(
                output_root,
                output_fd,
                {"SCHEDULER_EXPORT_V1.jsonl": export_identity},
            )
            raise
        return 0, receipt
    finally:
        os.close(output_fd)


def main(argv: Sequence[str] | None = None) -> int:
    actual = list(sys.argv[1:] if argv is None else argv)
    if actual and actual[0] == "parse-sbatch-job-id":
        try:
            parse_args = parse_sbatch_job_id_cli(actual)
            job_id = read_sbatch_job_id_file(parse_args.input_path)
        except Exception as caught:
            exc = _typed_unexpected_failure(
                caught,
                "SBATCH_JOB_ID_RUNTIME_FAILED",
                "unexpected sbatch job ID parser entrypoint failure",
            )
            digest = sha256_bytes(
                f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
            )
            print(
                "P1_SAB_PROTECTED_RR1_SBATCH_JOB_ID_CANNOT_CHECK "
                f"failure_code={exc.code} detail_sha256={digest}",
                file=sys.stderr,
            )
            return 2
        print(job_id)
        return 0
    if actual and actual[0] == "watch-capture":
        try:
            capture_args = parse_capture_cli(actual)
            watch_capture_scheduler(
                capture_args.job_id, capture_args.output_root,
            )
        except Exception as caught:
            exc = _typed_unexpected_failure(
                caught,
                "SCHEDULER_CAPTURE_RUNTIME_FAILED",
                "unexpected scheduler capture entrypoint failure",
            )
            digest = sha256_bytes(f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace"))
            print(
                "P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_CANNOT_CHECK "
                f"failure_code={exc.code} detail_sha256={digest}",
                file=sys.stderr,
            )
            return 1
        print("P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_PASS")
        return 0
    try:
        args = parse_cli(actual)
    except Exception as caught:
        exc = _typed_unexpected_failure(
            caught,
            "FINALIZER_RUNTIME_FAILED",
            "unexpected finalizer entrypoint failure",
        )
        digest = sha256_bytes(f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace"))
        print(
            "P1_SAB_PROTECTED_RR1_ONE_TUPLE_FINALIZER_ARGV_CANNOT_CHECK "
            f"failure_code={exc.code} detail_sha256={digest}",
            file=sys.stderr,
        )
        return 2
    try:
        code, receipt = finalize(
            args.evidence_root, args.capture_root, args.output_root
        )
    except Exception as caught:
        exc = _typed_unexpected_failure(
            caught,
            "FINALIZER_RUNTIME_FAILED",
            "unexpected finalizer entrypoint failure",
        )
        digest = sha256_bytes(
            f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
        )
        print(
            "P1_SAB_PROTECTED_RR1_ONE_TUPLE_FINALIZER_ARGV_CANNOT_CHECK "
            f"failure_code={exc.code} detail_sha256={digest}",
            file=sys.stderr,
        )
        return 2
    if code == 0:
        print("P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS")
    else:
        print(
            "P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_CANNOT_CHECK "
            f"failure_code={receipt['failure_code']} detail_sha256={receipt['failure_detail_sha256']}",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
