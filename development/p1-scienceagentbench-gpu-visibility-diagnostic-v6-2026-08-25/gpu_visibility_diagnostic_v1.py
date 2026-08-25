#!/usr/bin/env python3
"""Bounded, body-free GPU visibility diagnostic for ORION Paper 1 V6.

The program does not load a model, start a server, use the network, open a
protected body, or reach any task-bearing route.  It retains only an allowlist
of scheduler visibility variables, safe metadata/read-only-open results for
``/dev/nvidia*``, bounded cgroup evidence, and three exact ``nvidia-smi`` calls.
Raw diagnostic bodies are nonprotected and are retained as capped base64 with
their exact byte counts and SHA-256 digests.
"""

from __future__ import annotations

import argparse
import base64
import errno
import hashlib
import json
import os
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "GPU_VISIBILITY_DIAGNOSTIC_CONTRACT_V1.json"
PREDECESSOR_PATH = ROOT / "JOB_3537915_PREDECESSOR_BINDING_V1.json"
SUCCESS_NAME = "GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json"
CANNOT_NAME = "GPU_VISIBILITY_DIAGNOSTIC_CANNOT_CHECK_V1.json"
SUCCESS_TERMINAL = "P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_PASS"
CANNOT_TERMINAL = "P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_CANNOT_CHECK"
SCHEMA = "orion.p1.scienceagentbench.gpu-visibility-diagnostic-result.v1"
CANNOT_SCHEMA = "orion.p1.scienceagentbench.gpu-visibility-diagnostic-cannot-check.v1"
BASE_COMMIT = "9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67"

PATH_BASE = (
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824"
)
DEPLOYMENT_ROOT = PATH_BASE + "/repo-gpu-visibility-v6-20260825"
RUN_ROOT = PATH_BASE + "/live-gpu-visibility-v6-20260825"
EXPECTED_OUTPUT_ROOT = RUN_ROOT + "/evidence"
EXCLUDED_PREDECESSOR_NODE = "cg14"
NODE_CHANGE_INTERPRETATION = "NODE_CHANGE_DIAGNOSTIC_ONLY__NO_CAUSAL_PROOF"

ENV_ALLOWLIST = (
    "SLURM_JOB_ID",
    "SLURMD_NODENAME",
    "SLURM_JOB_GPUS",
    "SLURM_STEP_GPUS",
    "CUDA_VISIBLE_DEVICES",
)
COMMAND_ENVIRONMENT = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
NVIDIA_SMI_LIST_ARGV = ("/usr/bin/nvidia-smi", "-L")
NVIDIA_SMI_UNSCOPED_IDENTITY_ARGV = (
    "/usr/bin/nvidia-smi",
    "--query-gpu=index,uuid,name",
    "--format=csv,noheader,nounits",
)
NVIDIA_SMI_SCOPED_IDENTITY_PREFIX = ("/usr/bin/nvidia-smi",)
NVIDIA_SMI_SCOPED_IDENTITY_SUFFIX = (
    "--query-gpu=index,uuid,name",
    "--format=csv,noheader,nounits",
)

ENV_VALUE_BYTE_CAP = 4096
COMMAND_STREAM_BYTE_CAP = 65536
COMMAND_TIMEOUT_SECONDS = 30.0
PROC_CGROUP_BYTE_CAP = 65536
MOUNTINFO_READ_BYTE_CAP = 1048576
MOUNTINFO_SELECTED_BYTE_CAP = 131072
DEVICE_ENTRY_CAP = 64
DEVICE_NAME_BYTE_CAP = 255

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
JOB_RE = re.compile(r"^[1-9][0-9]*$")
NODE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
DECIMAL_DEVICE_RE = re.compile(r"^(0|[1-9][0-9]*)$")
GPU_UUID_RE = re.compile(
    r"^GPU-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
    r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)

VISIBLE_A40_IDENTITY_BOUND = "VISIBLE_A40_IDENTITY_BOUND"
UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND = (
    "UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND"
)
NVIDIA_DEVICE_NODES_ABSENT = "NVIDIA_DEVICE_NODES_ABSENT"
DEVICE_ACCESS_RESTRICTED = "DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK"
NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES = "NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES"
INCONCLUSIVE_DECISION = "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE"
INCOMPLETE_DECISION = "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE"
DECISION_OUTPUTS = (
    VISIBLE_A40_IDENTITY_BOUND,
    UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND,
    NVIDIA_DEVICE_NODES_ABSENT,
    DEVICE_ACCESS_RESTRICTED,
    NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES,
    INCONCLUSIVE_DECISION,
    INCOMPLETE_DECISION,
)


class GateError(RuntimeError):
    """A typed, fail-closed diagnostic error."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise GateError("JSON_INVALID", "value is not strict canonical JSON") from exc


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GateError("JSON_INVALID", f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                GateError("JSON_INVALID", f"nonfinite JSON member: {token}")
            ),
        )
    except GateError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("JSON_INVALID", f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise GateError("JSON_INVALID", f"{label} must be a JSON object")
    if raw != canonical_json_bytes(value) + b"\n":
        raise GateError("JSON_INVALID", f"{label} is not canonical JSON plus one LF")
    return value


def _read_bound_regular(path: Path, *, cap: int, label: str) -> Tuple[bytes, Tuple[int, int]]:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        before = path.lstat()
        fd = os.open(path, flags)
    except OSError as exc:
        raise GateError("SOURCE_INVALID", f"{label} cannot be opened") from exc
    try:
        opened_before = os.fstat(fd)
        if (
            stat.S_ISLNK(before.st_mode)
            or not stat.S_ISREG(before.st_mode)
            or not stat.S_ISREG(opened_before.st_mode)
            or (before.st_dev, before.st_ino) != (opened_before.st_dev, opened_before.st_ino)
        ):
            raise GateError("SOURCE_INVALID", f"{label} is not one regular non-symlink file")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, cap + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise GateError("SOURCE_INVALID", f"{label} exceeds its byte cap")
        opened_after = os.fstat(fd)
        after = path.lstat()
        if (
            (opened_before.st_dev, opened_before.st_ino, opened_before.st_size)
            != (opened_after.st_dev, opened_after.st_ino, opened_after.st_size)
            or (after.st_dev, after.st_ino) != (opened_after.st_dev, opened_after.st_ino)
            or not stat.S_ISREG(after.st_mode)
        ):
            raise GateError("SOURCE_INVALID", f"{label} changed while read")
        return b"".join(chunks), (opened_after.st_dev, opened_after.st_ino)
    except OSError as exc:
        raise GateError("SOURCE_INVALID", f"{label} cannot be inspected") from exc
    finally:
        os.close(fd)


def load_contract() -> Tuple[dict[str, Any], str, Tuple[int, int]]:
    raw, identity = _read_bound_regular(CONTRACT_PATH, cap=1024 * 1024, label="contract")
    contract = strict_json_bytes(raw, "GPU visibility diagnostic contract")
    if contract.get("schema_version") != (
        "orion.p1.scienceagentbench.gpu-visibility-diagnostic-contract.v1"
    ):
        raise GateError("CONTRACT_INVALID", "contract schema differs")
    if contract.get("status") != "FROZEN_NOT_EXECUTED":
        raise GateError("CONTRACT_INVALID", "contract status differs")
    if contract.get("base_commit") != BASE_COMMIT:
        raise GateError("CONTRACT_INVALID", "contract base commit differs")
    if contract.get("submission_authority") is not False:
        raise GateError("CONTRACT_INVALID", "contract cannot grant submission authority")
    if contract.get("paths") != {
        "deployment_root": DEPLOYMENT_ROOT,
        "output_root": EXPECTED_OUTPUT_ROOT,
        "run_root": RUN_ROOT,
    }:
        raise GateError("CONTRACT_INVALID", "contract roots differ")
    policy = contract.get("diagnostic_policy")
    if not isinstance(policy, Mapping):
        raise GateError("CONTRACT_INVALID", "diagnostic policy is absent")
    exact_policy_members = {
        "command_stream_byte_cap": COMMAND_STREAM_BYTE_CAP,
        "command_timeout_seconds": int(COMMAND_TIMEOUT_SECONDS),
        "device_entry_cap": DEVICE_ENTRY_CAP,
        "device_name_byte_cap": DEVICE_NAME_BYTE_CAP,
        "environment_allowlist": list(ENV_ALLOWLIST),
        "environment_value_byte_cap": ENV_VALUE_BYTE_CAP,
        "mountinfo_read_byte_cap": MOUNTINFO_READ_BYTE_CAP,
        "mountinfo_selected_byte_cap": MOUNTINFO_SELECTED_BYTE_CAP,
        "proc_cgroup_byte_cap": PROC_CGROUP_BYTE_CAP,
    }
    for key, expected in exact_policy_members.items():
        if policy.get(key) != expected:
            raise GateError("CONTRACT_INVALID", f"contract diagnostic policy differs at {key}")
    if policy.get("commands") != {
        "nvidia_smi_list": list(NVIDIA_SMI_LIST_ARGV),
        "scoped_identity_template": [
            "/usr/bin/nvidia-smi",
            "--id=<VALIDATED_CUDA_VISIBLE_DEVICES_TOKEN>",
            *NVIDIA_SMI_SCOPED_IDENTITY_SUFFIX,
        ],
        "unscoped_identity": list(NVIDIA_SMI_UNSCOPED_IDENTITY_ARGV),
    }:
        raise GateError("CONTRACT_INVALID", "contract command argv freeze differs")
    scheduler_node = policy.get("scheduler_node")
    if not isinstance(scheduler_node, Mapping) or scheduler_node.get(
        "excluded_predecessor_node"
    ) != EXCLUDED_PREDECESSOR_NODE:
        raise GateError("CONTRACT_INVALID", "excluded scheduler node differs")
    if contract.get("decision_policy", {}).get("outputs") != list(DECISION_OUTPUTS):
        raise GateError("CONTRACT_INVALID", "contract decision outputs differ")
    if contract.get("output_policy", {}).get("success_file") != SUCCESS_NAME or contract.get(
        "output_policy", {}
    ).get("cannot_check_file") != CANNOT_NAME:
        raise GateError("CONTRACT_INVALID", "contract output names differ")
    return contract, sha256_bytes(raw), identity


def load_predecessor(contract: Mapping[str, Any]) -> Tuple[dict[str, Any], dict[str, Any], Tuple[int, int]]:
    binding = contract.get("predecessor", {}).get("binding")
    if not isinstance(binding, Mapping) or binding.get("file") != PREDECESSOR_PATH.name:
        raise GateError("PREDECESSOR_INVALID", "predecessor binding path differs")
    expected_bytes = binding.get("bytes")
    expected_sha = binding.get("sha256")
    if (
        not isinstance(expected_bytes, int)
        or isinstance(expected_bytes, bool)
        or expected_bytes <= 0
        or not isinstance(expected_sha, str)
        or SHA_RE.fullmatch(expected_sha) is None
    ):
        raise GateError("PREDECESSOR_INVALID", "predecessor binding metadata differs")
    raw, identity = _read_bound_regular(
        PREDECESSOR_PATH, cap=1024 * 1024, label="job-3537915 predecessor"
    )
    if len(raw) != expected_bytes or sha256_bytes(raw) != expected_sha:
        raise GateError("PREDECESSOR_INVALID", "predecessor byte binding differs")
    predecessor = strict_json_bytes(raw, "job-3537915 predecessor")
    if predecessor.get("status") != "PASS_BOUND_JOB_3537915_ADVERSE_PREDECESSOR":
        raise GateError("PREDECESSOR_INVALID", "predecessor status differs")
    if predecessor.get("bound_at_merged_result_commit") != BASE_COMMIT:
        raise GateError("PREDECESSOR_INVALID", "predecessor result commit differs")
    if predecessor.get("job", {}).get("job_id") != "3537915":
        raise GateError("PREDECESSOR_INVALID", "predecessor job differs")
    if predecessor.get("job", {}).get("node") != EXCLUDED_PREDECESSOR_NODE:
        raise GateError("PREDECESSOR_INVALID", "predecessor node differs")
    accounting = predecessor.get("accounting_after_job_3537915", {})
    if accounting != {
        "body_free_discriminator_scheduler_gpu_seconds": 170,
        "body_free_discriminator_submissions_completed": 2,
        "combined_scheduler_gpu_seconds": 260,
        "protected_generation_attempts_consumed": 0,
        "protected_infrastructure_scheduler_gpu_seconds": 90,
        "protected_infrastructure_submissions_completed": 3,
    }:
        raise GateError("PREDECESSOR_INVALID", "predecessor cost differs")
    if predecessor.get("result", {}).get("nvidia_smi_return_code") != 6:
        raise GateError("PREDECESSOR_INVALID", "predecessor return code differs")
    if predecessor.get("result", {}).get("failure_subcode") != "NVIDIA_SMI_NONZERO_RETURN":
        raise GateError("PREDECESSOR_INVALID", "predecessor failure branch differs")
    if predecessor.get("no_promotion") != {
        "job_3537893_promoted": False,
        "job_3537910_promoted": False,
        "job_3537915_promoted": False,
        "node_change_is_causal_proof": False,
        "protected_retry_authorized": False,
    }:
        raise GateError("PREDECESSOR_INVALID", "predecessor no-promotion boundary differs")
    return (
        predecessor,
        {
            "bytes": expected_bytes,
            "file": PREDECESSOR_PATH.name,
            "job_id": "3537915",
            "result_commit": BASE_COMMIT,
            "sha256": expected_sha,
            "status": "PASS_BOUND_JOB_3537915_ADVERSE_PREDECESSOR",
        },
        identity,
    )


def raw_binding(payload: bytes, *, complete: bool = True) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(payload).decode("ascii"),
        "bytes": len(payload),
        "complete": complete,
        "encoding": "base64",
        "sha256": sha256_bytes(payload),
    }


def _decode_raw_binding(binding: Mapping[str, Any], label: str) -> bytes:
    if binding.get("encoding") != "base64" or binding.get("complete") is not True:
        raise GateError("EVIDENCE_INVALID", f"{label} is not a complete base64 body")
    encoded = binding.get("base64")
    byte_count = binding.get("bytes")
    if (
        not isinstance(encoded, str)
        or not isinstance(byte_count, int)
        or isinstance(byte_count, bool)
        or byte_count < 0
    ):
        raise GateError("EVIDENCE_INVALID", f"{label} base64 or byte count is absent")
    try:
        payload = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError) as exc:
        raise GateError("EVIDENCE_INVALID", f"{label} base64 is invalid") from exc
    if (
        encoded != base64.b64encode(payload).decode("ascii")
        or byte_count != len(payload)
        or binding.get("sha256") != sha256_bytes(payload)
    ):
        raise GateError("EVIDENCE_INVALID", f"{label} byte binding differs")
    return payload


def _environment_bytes(environmentb: Optional[Mapping[Any, Any]]) -> Mapping[bytes, bytes]:
    if environmentb is None:
        if not hasattr(os, "environb"):
            raise GateError("ENVIRONMENT_INVALID", "byte environment access is unavailable")
        return os.environb
    normalized: dict[bytes, bytes] = {}
    for key, value in environmentb.items():
        raw_key = key if isinstance(key, bytes) else str(key).encode("utf-8")
        raw_value = value if isinstance(value, bytes) else str(value).encode("utf-8")
        normalized[raw_key] = raw_value
    return normalized


def _decode_strict_optional(payload: bytes, complete: bool) -> Tuple[Optional[str], bool]:
    if not complete:
        return None, False
    try:
        return payload.decode("utf-8", errors="strict"), True
    except UnicodeDecodeError:
        return None, False


def _valid_cuda_token(value: Optional[str]) -> bool:
    if value is None or not value or "," in value or "\x00" in value:
        return False
    if any(character.isspace() for character in value):
        return False
    return DECIMAL_DEVICE_RE.fullmatch(value) is not None or GPU_UUID_RE.fullmatch(value) is not None


def capture_environment(environmentb: Optional[Mapping[Any, Any]] = None) -> dict[str, Any]:
    env = _environment_bytes(environmentb)
    variables: dict[str, Any] = {}
    capture_complete = True
    decoded: dict[str, Optional[str]] = {}
    for name in ENV_ALLOWLIST:
        key = name.encode("ascii")
        present = key in env
        original = env.get(key, b"")
        if not isinstance(original, bytes):
            raise GateError("ENVIRONMENT_INVALID", "byte environment mapping returned nonbytes")
        complete = len(original) <= ENV_VALUE_BYTE_CAP
        retained = original if complete else original[:ENV_VALUE_BYTE_CAP]
        value, utf8_valid = _decode_strict_optional(retained, complete)
        variables[name] = {
            "present": present,
            "raw": raw_binding(retained, complete=complete),
            "utf8": value,
            "utf8_valid": utf8_valid,
        }
        decoded[name] = value if present and utf8_valid else None
        capture_complete = capture_complete and complete

    job_id = decoded["SLURM_JOB_ID"]
    node = decoded["SLURMD_NODENAME"]
    token = decoded["CUDA_VISIBLE_DEVICES"]
    job_valid = isinstance(job_id, str) and JOB_RE.fullmatch(job_id) is not None
    node_valid = (
        isinstance(node, str)
        and NODE_RE.fullmatch(node) is not None
        and node != EXCLUDED_PREDECESSOR_NODE
    )
    token_valid = _valid_cuda_token(token)
    return {
        "allowlist": list(ENV_ALLOWLIST),
        "capture_complete": capture_complete,
        "cuda_visible_devices_token": token if token_valid else None,
        "cuda_visible_devices_token_valid": token_valid,
        "slurm_job_id": job_id if job_valid else None,
        "slurm_job_id_valid": job_valid,
        "scheduler_node": node if isinstance(node, str) else None,
        "scheduler_node_valid_and_changed": node_valid,
        "validation_complete": bool(capture_complete and job_valid and node_valid and token_valid),
        "variables": variables,
    }


def _file_type(mode: int) -> str:
    if stat.S_ISCHR(mode):
        return "CHARACTER_DEVICE"
    if stat.S_ISBLK(mode):
        return "BLOCK_DEVICE"
    if stat.S_ISREG(mode):
        return "REGULAR_FILE"
    if stat.S_ISDIR(mode):
        return "DIRECTORY"
    if stat.S_ISLNK(mode):
        return "SYMLINK"
    if stat.S_ISFIFO(mode):
        return "FIFO"
    if stat.S_ISSOCK(mode):
        return "SOCKET"
    return "OTHER"


def _errno_record(exc: OSError) -> dict[str, Any]:
    number = exc.errno if isinstance(exc.errno, int) else errno.EIO
    return {"name": errno.errorcode.get(number, "UNKNOWN"), "number": number}


def capture_device_inventory(dev_root: Path = Path("/dev")) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    scan_complete = True
    directory_error: Optional[dict[str, Any]] = None
    try:
        candidates = [entry for entry in os.scandir(dev_root) if entry.name.startswith("nvidia")]
    except OSError as exc:
        candidates = []
        scan_complete = False
        directory_error = _errno_record(exc)
    candidates.sort(key=lambda entry: os.fsencode(entry.name))
    discovered_count = len(candidates)
    if discovered_count > DEVICE_ENTRY_CAP:
        candidates = candidates[:DEVICE_ENTRY_CAP]
        scan_complete = False

    char_device_count = 0
    denied_count = 0
    for directory_entry in candidates:
        name_bytes = os.fsencode(directory_entry.name)
        try:
            display_name = name_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            display_name = None
        entry_complete = len(name_bytes) <= DEVICE_NAME_BYTE_CAP and display_name is not None
        if not entry_complete:
            scan_complete = False
        record: dict[str, Any] = {
            "name_raw": raw_binding(name_bytes[:DEVICE_NAME_BYTE_CAP], complete=entry_complete),
            "path": os.fspath(Path(dev_root) / display_name) if display_name is not None else None,
        }
        try:
            info = directory_entry.stat(follow_symlinks=False)
            type_name = _file_type(info.st_mode)
            if type_name == "CHARACTER_DEVICE":
                char_device_count += 1
            record["lstat"] = {
                "device": info.st_dev,
                "gid": info.st_gid,
                "inode": info.st_ino,
                "mode": f"{stat.S_IMODE(info.st_mode):04o}",
                "nlink": info.st_nlink,
                "rdev_major": os.major(info.st_rdev) if stat.S_ISCHR(info.st_mode) or stat.S_ISBLK(info.st_mode) else None,
                "rdev_minor": os.minor(info.st_rdev) if stat.S_ISCHR(info.st_mode) or stat.S_ISBLK(info.st_mode) else None,
                "status": "BOUND",
                "type": type_name,
                "uid": info.st_uid,
            }
        except OSError as exc:
            record["lstat"] = {"error": _errno_record(exc), "status": "CANNOT_CHECK"}
            scan_complete = False

        flags = os.O_RDONLY
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(directory_entry.path, flags)
        except OSError as exc:
            error = _errno_record(exc)
            if error["number"] in (errno.EACCES, errno.EPERM):
                denied_count += 1
            record["read_only_open"] = {
                "attempted": True,
                "error": error,
                "ioctl_invoked": False,
                "opened": False,
                "read_invoked": False,
            }
        else:
            try:
                record["read_only_open"] = {
                    "attempted": True,
                    "error": None,
                    "ioctl_invoked": False,
                    "opened": True,
                    "read_invoked": False,
                }
            finally:
                os.close(fd)
        entries.append(record)

    return {
        "character_device_count": char_device_count,
        "device_root": os.fspath(dev_root),
        "directory_error": directory_error,
        "discovered_entry_count": discovered_count,
        "entries": entries,
        "entry_cap": DEVICE_ENTRY_CAP,
        "read_only_open_denied_count": denied_count,
        "scan_complete": scan_complete,
    }


def _read_bounded_path(path: Path, cap: int) -> dict[str, Any]:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        return {
            "error": _errno_record(exc),
            "path": os.fspath(path),
            "raw": raw_binding(b"", complete=False),
            "status": "READ_ERROR",
        }
    try:
        chunks: list[bytes] = []
        total = 0
        while total <= cap:
            try:
                chunk = os.read(fd, min(65536, cap + 1 - total))
            except OSError as exc:
                return {
                    "error": _errno_record(exc),
                    "path": os.fspath(path),
                    "raw": raw_binding(b"".join(chunks), complete=False),
                    "status": "READ_ERROR",
                }
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        payload = b"".join(chunks)
        if len(payload) > cap:
            return {
                "error": None,
                "path": os.fspath(path),
                "raw": raw_binding(payload[:cap], complete=False),
                "status": "OUTPUT_LIMIT",
            }
        return {
            "error": None,
            "path": os.fspath(path),
            "raw": raw_binding(payload),
            "status": "COMPLETE",
        }
    finally:
        os.close(fd)


def capture_cgroup_evidence(
    cgroup_path: Path = Path("/proc/self/cgroup"),
    mountinfo_path: Path = Path("/proc/self/mountinfo"),
) -> dict[str, Any]:
    cgroup = _read_bounded_path(cgroup_path, PROC_CGROUP_BYTE_CAP)
    mountinfo = _read_bounded_path(mountinfo_path, MOUNTINFO_READ_BYTE_CAP)
    selected_record: dict[str, Any]
    if mountinfo["status"] == "COMPLETE":
        raw_mountinfo = _decode_raw_binding(mountinfo["raw"], "mountinfo")
        selected_lines = []
        for line in raw_mountinfo.splitlines(keepends=True):
            if b" - cgroup " in line or b" - cgroup2 " in line:
                selected_lines.append(line)
        selected = b"".join(selected_lines)
        complete = len(selected) <= MOUNTINFO_SELECTED_BYTE_CAP
        selected_record = {
            "filter_rule": "LINES_WITH_POST_SEPARATOR_FILESYSTEM_TYPE_CGROUP_OR_CGROUP2",
            "raw": raw_binding(selected[:MOUNTINFO_SELECTED_BYTE_CAP], complete=complete),
            "status": "COMPLETE" if complete else "OUTPUT_LIMIT",
        }
    else:
        selected_record = {
            "filter_rule": "LINES_WITH_POST_SEPARATOR_FILESYSTEM_TYPE_CGROUP_OR_CGROUP2",
            "raw": raw_binding(b"", complete=False),
            "status": "SOURCE_INCOMPLETE",
        }
    return {
        "capture_complete": bool(
            cgroup["status"] == "COMPLETE"
            and mountinfo["status"] == "COMPLETE"
            and selected_record["status"] == "COMPLETE"
        ),
        "proc_self_cgroup": cgroup,
        "proc_self_mountinfo": {
            "full_source_binding": {
                "bytes": mountinfo["raw"]["bytes"],
                "complete": mountinfo["raw"]["complete"],
                "sha256": mountinfo["raw"]["sha256"],
            },
            "path": os.fspath(mountinfo_path),
            "selected_cgroup_lines": selected_record,
            "status": mountinfo["status"],
        },
    }


def _empty_command_capture(argv: Optional[Sequence[str]], status_name: str) -> dict[str, Any]:
    return {
        "argv": list(argv) if argv is not None else None,
        "return_code": None,
        "status": status_name,
        "stderr": raw_binding(b"", complete=False),
        "stdout": raw_binding(b"", complete=False),
        "stdout_parse_attempted": False,
    }


def bounded_command(
    argv: Sequence[str],
    *,
    timeout_seconds: float = COMMAND_TIMEOUT_SECONDS,
    stream_byte_cap: int = COMMAND_STREAM_BYTE_CAP,
    environment: Optional[Mapping[str, str]] = None,
    popen_factory: Optional[Callable[..., Any]] = None,
) -> dict[str, Any]:
    exact_argv = list(argv)
    if not exact_argv or any(not isinstance(item, str) or "\x00" in item for item in exact_argv):
        raise GateError("COMMAND_INVALID", "command argv is not exact text")
    if stream_byte_cap <= 0 or timeout_seconds <= 0:
        raise GateError("COMMAND_INVALID", "command bounds are not positive")
    factory = subprocess.Popen if popen_factory is None else popen_factory
    try:
        process = factory(
            exact_argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(COMMAND_ENVIRONMENT if environment is None else environment),
            start_new_session=True,
        )
    except OSError as exc:
        capture = _empty_command_capture(exact_argv, "EXECUTION_ERROR")
        capture["execution_error"] = _errno_record(exc)
        return capture
    if process.stdout is None or process.stderr is None:
        try:
            process.kill()
            process.wait(timeout=5)
        except BaseException:
            pass
        return _empty_command_capture(exact_argv, "EXECUTION_ERROR")

    selector = selectors.DefaultSelector()
    buffers: dict[str, bytearray] = {"stdout": bytearray(), "stderr": bytearray()}
    overflow = False
    timed_out = False
    caught: Optional[BaseException] = None
    try:
        for label, handle in (("stdout", process.stdout), ("stderr", process.stderr)):
            os.set_blocking(handle.fileno(), False)
            selector.register(handle, selectors.EVENT_READ, data=label)
        deadline = time.monotonic() + timeout_seconds
        killed = False
        while selector.get_map():
            if not killed and time.monotonic() >= deadline:
                timed_out = True
                killed = True
                process.kill()
            events = selector.select(0.05)
            for key, _mask in events:
                label = key.data
                try:
                    chunk = os.read(key.fileobj.fileno(), 8192)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                available = stream_byte_cap - len(buffers[label])
                if available > 0:
                    buffers[label].extend(chunk[:available])
                if len(chunk) > available:
                    overflow = True
                    if not killed:
                        killed = True
                        process.kill()
            if process.poll() is not None and not events:
                # Pipes remain registered until EOF, binding every byte under the cap.
                continue
        try:
            return_code = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            return_code = process.wait(timeout=5)
            timed_out = True
    except BaseException as exc:
        caught = exc
        try:
            process.kill()
            process.wait(timeout=5)
        except BaseException:
            pass
        raise
    finally:
        try:
            selector.close()
        finally:
            process.stdout.close()
            process.stderr.close()
        del caught

    status_name = "OUTPUT_LIMIT" if overflow else ("TIMEOUT" if timed_out else "COMPLETED")
    streams_complete = not overflow and not timed_out
    return {
        "argv": exact_argv,
        "return_code": return_code,
        "status": status_name,
        "stderr": raw_binding(bytes(buffers["stderr"]), complete=streams_complete),
        "stdout": raw_binding(bytes(buffers["stdout"]), complete=streams_complete),
        "stdout_parse_attempted": False,
    }


def scoped_identity_argv(token: str) -> list[str]:
    if not _valid_cuda_token(token):
        raise GateError("ENVIRONMENT_INVALID", "CUDA_VISIBLE_DEVICES token is invalid")
    return [
        *NVIDIA_SMI_SCOPED_IDENTITY_PREFIX,
        f"--id={token}",
        *NVIDIA_SMI_SCOPED_IDENTITY_SUFFIX,
    ]


def _parse_eligible(capture: Mapping[str, Any]) -> bool:
    if not (
        capture.get("status") == "COMPLETED"
        and type(capture.get("return_code")) is int
        and capture.get("return_code") == 0
        and capture.get("stderr", {}).get("complete") is True
        and capture.get("stdout", {}).get("complete") is True
    ):
        return False
    stderr = _decode_raw_binding(capture["stderr"], "command stderr")
    _decode_raw_binding(capture["stdout"], "command stdout")
    return stderr == b""


def parse_identity_capture(capture: MutableMapping[str, Any]) -> dict[str, Any]:
    if not _parse_eligible(capture):
        return {"identity": None, "status": "NOT_PARSE_ELIGIBLE"}
    capture["stdout_parse_attempted"] = True
    raw = _decode_raw_binding(capture["stdout"], "identity stdout")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {"identity": None, "status": "STDOUT_UTF8_INVALID"}
    if "\r" in text or (text and not text.endswith("\n")):
        return {"identity": None, "status": "STDOUT_FRAMING_INVALID"}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return {"identity": None, "status": "VISIBLE_ROW_COUNT_INVALID"}
    fields = [field.strip() for field in lines[0].split(",", 2)]
    if (
        len(fields) != 3
        or DECIMAL_DEVICE_RE.fullmatch(fields[0]) is None
        or GPU_UUID_RE.fullmatch(fields[1]) is None
    ):
        return {"identity": None, "status": "VISIBLE_ROW_INVALID"}
    identity = {"gpu_uuid": fields[1], "index": fields[0], "name": fields[2]}
    if fields[2] != "NVIDIA A40":
        return {"identity": identity, "status": "VISIBLE_GPU_MODEL_NOT_A40"}
    return {"identity": identity, "status": "PARSED_ONE_A40"}


def parse_list_capture(capture: MutableMapping[str, Any]) -> dict[str, Any]:
    if not _parse_eligible(capture):
        return {"identity": None, "status": "NOT_PARSE_ELIGIBLE"}
    capture["stdout_parse_attempted"] = True
    raw = _decode_raw_binding(capture["stdout"], "nvidia-smi -L stdout")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {"identity": None, "status": "STDOUT_UTF8_INVALID"}
    if "\r" in text or (text and not text.endswith("\n")):
        return {"identity": None, "status": "STDOUT_FRAMING_INVALID"}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return {"identity": None, "status": "VISIBLE_ROW_COUNT_INVALID"}
    match = re.fullmatch(
        r"GPU (0|[1-9][0-9]*): (.+) \(UUID: "
        r"(GPU-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\)",
        lines[0],
    )
    if match is None:
        return {"identity": None, "status": "VISIBLE_ROW_INVALID"}
    identity = {"gpu_uuid": match.group(3), "index": match.group(1), "name": match.group(2)}
    if identity["name"] != "NVIDIA A40":
        return {"identity": identity, "status": "VISIBLE_GPU_MODEL_NOT_A40"}
    return {"identity": identity, "status": "PARSED_ONE_A40"}


def _identity_matches(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return bool(
        left.get("status") == "PARSED_ONE_A40"
        and right.get("status") == "PARSED_ONE_A40"
        and left.get("identity") == right.get("identity")
    )


def _scope_token_matches_identity(token: Optional[str], parsed: Mapping[str, Any]) -> bool:
    identity = parsed.get("identity")
    if not isinstance(token, str) or not isinstance(identity, Mapping):
        return False
    if DECIMAL_DEVICE_RE.fullmatch(token) is not None:
        return identity.get("index") == token
    if GPU_UUID_RE.fullmatch(token) is not None:
        uuid = identity.get("gpu_uuid")
        return isinstance(uuid, str) and uuid.casefold() == token.casefold()
    return False


def classify_diagnostic(context: Mapping[str, Any]) -> str:
    if context.get("evidence_complete") is not True:
        return INCOMPLETE_DECISION
    devices = context.get("device_inventory", {})
    commands = context.get("commands", {})
    if not isinstance(commands, Mapping) or not _commands_complete(commands):
        return INCOMPLETE_DECISION
    parsed = context.get("parsed_identities", {})
    list_parsed = parsed.get("nvidia_smi_list", {})
    unscoped = parsed.get("unscoped_identity", {})
    scoped = parsed.get("scoped_identity", {})
    char_count = devices.get("character_device_count", 0)
    entries = devices.get("entries", [])
    denied_count = devices.get("read_only_open_denied_count", 0)

    if (
        char_count > 0
        and _identity_matches(list_parsed, unscoped)
        and _identity_matches(unscoped, scoped)
        and scoped.get("scope_token_matches_identity") is True
        and denied_count == 0
    ):
        return VISIBLE_A40_IDENTITY_BOUND
    if (
        char_count > 0
        and scoped.get("status") == "PARSED_ONE_A40"
        and scoped.get("scope_token_matches_identity") is True
        and commands.get("unscoped_identity", {}).get("status") == "COMPLETED"
        and commands.get("unscoped_identity", {}).get("return_code") not in (None, 0)
    ):
        return UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND
    any_identity = any(
        parsed.get(name, {}).get("status") == "PARSED_ONE_A40"
        for name in ("nvidia_smi_list", "unscoped_identity", "scoped_identity")
    )
    if entries == [] and not any_identity:
        return NVIDIA_DEVICE_NODES_ABSENT
    if denied_count > 0 and not any_identity:
        return DEVICE_ACCESS_RESTRICTED
    if all(
        commands.get(name, {}).get("status") == "COMPLETED"
        and type(commands.get(name, {}).get("return_code")) is int
        and commands.get(name, {}).get("return_code") == 6
        and commands.get(name, {}).get("stdout_parse_attempted") is False
        and parsed.get(name, {}).get("status") == "NOT_PARSE_ELIGIBLE"
        and parsed.get(name, {}).get("identity") is None
        for name in ("nvidia_smi_list", "unscoped_identity", "scoped_identity")
    ):
        return NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES
    return INCONCLUSIVE_DECISION


def _command_argv_frozen(name: str, argv: Any) -> bool:
    if not isinstance(argv, list) or any(not isinstance(item, str) for item in argv):
        return False
    if name == "nvidia_smi_list":
        return argv == list(NVIDIA_SMI_LIST_ARGV)
    if name == "unscoped_identity":
        return argv == list(NVIDIA_SMI_UNSCOPED_IDENTITY_ARGV)
    if name != "scoped_identity" or len(argv) != 4 or not argv[1].startswith("--id="):
        return False
    token = argv[1][len("--id=") :]
    try:
        return argv == scoped_identity_argv(token)
    except GateError:
        return False


def _commands_complete(commands: Mapping[str, Any]) -> bool:
    names = ("nvidia_smi_list", "unscoped_identity", "scoped_identity")
    if set(commands) != set(names):
        return False
    for name in names:
        capture = commands.get(name)
        if (
            not isinstance(capture, Mapping)
            or capture.get("status") != "COMPLETED"
            or not _command_argv_frozen(name, capture.get("argv"))
            or type(capture.get("stdout_parse_attempted")) is not bool
        ):
            return False
        for stream in ("stdout", "stderr"):
            binding = capture.get(stream)
            if not isinstance(binding, Mapping) or binding.get("complete") is not True:
                return False
            try:
                _decode_raw_binding(binding, f"{name} {stream}")
            except GateError:
                return False
        if not isinstance(capture.get("return_code"), int) or isinstance(
            capture.get("return_code"), bool
        ):
            return False
    return True


def _directory_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _create_output_root(output_root: Path) -> int:
    if os.fspath(output_root) != EXPECTED_OUTPUT_ROOT or not output_root.is_absolute():
        raise GateError("OUTPUT_ROOT_INVALID", "output root differs from the exact fresh V6 freeze")
    parent_fd: Optional[int] = None
    root_fd: Optional[int] = None
    created = False
    succeeded = False
    try:
        parent_fd = os.open(output_root.parent, _directory_flags())
        os.mkdir(output_root.name, 0o700, dir_fd=parent_fd)
        created = True
        root_fd = os.open(output_root.name, _directory_flags(), dir_fd=parent_fd)
        entry = os.stat(output_root.name, dir_fd=parent_fd, follow_symlinks=False)
        opened = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(entry.st_mode)
            or not stat.S_ISDIR(opened.st_mode)
            or opened.st_uid != os.geteuid()
            or (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise GateError("OUTPUT_ROOT_INVALID", "output root custody differs")
        os.fchmod(root_fd, 0o700)
        os.fsync(root_fd)
        os.fsync(parent_fd)
        result = root_fd
        root_fd = None
        succeeded = True
        return result
    except GateError:
        raise
    except OSError as exc:
        raise GateError("OUTPUT_ROOT_INVALID", "output root is not exclusively creatable") from exc
    finally:
        if root_fd is not None:
            os.close(root_fd)
        if created and not succeeded and parent_fd is not None:
            try:
                os.rmdir(output_root.name, dir_fd=parent_fd)
            except OSError:
                pass
        if parent_fd is not None:
            os.close(parent_fd)


def _write_receipt(root_fd: int, name: str, receipt: Mapping[str, Any]) -> None:
    if name not in (SUCCESS_NAME, CANNOT_NAME) or Path(name).name != name:
        raise GateError("OUTPUT_WRITE_FAILED", "receipt name is outside the exact allowlist")
    payload = canonical_json_bytes(receipt) + b"\n"
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd: Optional[int] = None
    succeeded = False
    try:
        fd = os.open(name, flags, 0o600, dir_fd=root_fd)
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise GateError("OUTPUT_WRITE_FAILED", "receipt write made no progress")
            view = view[written:]
        os.fsync(fd)
        opened = os.fstat(fd)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_uid != os.geteuid()
            or opened.st_nlink != 1
            or opened.st_size != len(payload)
        ):
            raise GateError("OUTPUT_WRITE_FAILED", "receipt descriptor custody differs")
        os.lseek(fd, 0, os.SEEK_SET)
        reread = bytearray()
        while len(reread) < len(payload):
            chunk = os.read(fd, len(payload) - len(reread))
            if not chunk:
                break
            reread.extend(chunk)
        if bytes(reread) != payload:
            raise GateError("OUTPUT_WRITE_FAILED", "receipt reread differs")
        entry = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
        if (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
            raise GateError("OUTPUT_WRITE_FAILED", "receipt named identity differs")
        os.fchmod(fd, 0o400)
        os.fsync(fd)
        final = os.fstat(fd)
        final_entry = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
        if (
            stat.S_IMODE(final.st_mode) != 0o400
            or stat.S_IMODE(final_entry.st_mode) != 0o400
            or (final.st_dev, final.st_ino) != (final_entry.st_dev, final_entry.st_ino)
            or final.st_size != len(payload)
            or final_entry.st_size != len(payload)
        ):
            raise GateError("OUTPUT_WRITE_FAILED", "receipt final custody differs")
        os.fsync(root_fd)
        succeeded = True
    except GateError:
        raise
    except OSError as exc:
        raise GateError("OUTPUT_WRITE_FAILED", "receipt cannot be persisted") from exc
    finally:
        if fd is not None:
            if not succeeded:
                try:
                    os.unlink(name, dir_fd=root_fd)
                except OSError:
                    pass
            os.close(fd)


def _persist_receipt(output_root: Path, root_fd: int, name: str, receipt: Mapping[str, Any]) -> None:
    _write_receipt(root_fd, name, receipt)
    try:
        os.fchmod(root_fd, 0o500)
        os.fsync(root_fd)
        opened = os.fstat(root_fd)
        entry = output_root.lstat()
        if (
            not stat.S_ISDIR(opened.st_mode)
            or not stat.S_ISDIR(entry.st_mode)
            or stat.S_IMODE(opened.st_mode) != 0o500
            or stat.S_IMODE(entry.st_mode) != 0o500
            or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)
        ):
            raise GateError("OUTPUT_WRITE_FAILED", "output root final custody differs")
    except BaseException as exc:
        # Never leave a success-shaped receipt under an unsealed output root.
        try:
            os.fchmod(root_fd, 0o700)
            candidate = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
            if (
                stat.S_ISREG(candidate.st_mode)
                and candidate.st_uid == os.geteuid()
                and candidate.st_nlink == 1
                and stat.S_IMODE(candidate.st_mode) == 0o400
            ):
                os.unlink(name, dir_fd=root_fd)
                os.fsync(root_fd)
            os.fchmod(root_fd, 0o500)
            os.fsync(root_fd)
        except OSError:
            pass
        if isinstance(exc, GateError):
            raise
        raise GateError("OUTPUT_WRITE_FAILED", "output root cannot be sealed") from exc


def _common_receipt(
    *,
    contract_sha256: str,
    predecessor_binding: Mapping[str, Any],
    completed_stages: Sequence[str],
    environment: Mapping[str, Any],
    device_inventory: Mapping[str, Any],
    cgroup_evidence: Mapping[str, Any],
    commands: Mapping[str, Any],
    parsed_outputs: Mapping[str, Any],
) -> dict[str, Any]:
    node = environment.get("scheduler_node")
    changed = (
        node != EXCLUDED_PREDECESSOR_NODE
        if environment.get("scheduler_node_valid_and_changed") is True and isinstance(node, str)
        else None
    )
    return {
        "base_commit": BASE_COMMIT,
        "cgroup_evidence": cgroup_evidence,
        "commands": commands,
        "completed_stages": list(completed_stages),
        "completion_requests": 0,
        "contract_sha256": contract_sha256,
        "device_inventory": device_inventory,
        "environment": environment,
        "generation_invocations": 0,
        "model_started": False,
        "network_accessed": False,
        "no_promotion": {
            "job_3537893_promoted": False,
            "job_3537910_promoted": False,
            "job_3537915_promoted": False,
            "node_change_is_causal_proof": False,
            "protected_retry_authorized": False,
        },
        "node_change_diagnostic": {
            "different_from_predecessor_node": changed,
            "excluded_predecessor_node": EXCLUDED_PREDECESSOR_NODE,
            "interpretation": NODE_CHANGE_INTERPRETATION,
            "observed_scheduler_node": node,
        },
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "parsed_outputs": parsed_outputs,
        "predecessor_binding": dict(predecessor_binding),
        "prior_accounting": {
            "body_free_discriminator_scheduler_gpu_seconds": 170,
            "body_free_discriminator_submissions_completed": 2,
            "combined_scheduler_gpu_seconds": 260,
            "protected_generation_attempts_consumed": 0,
            "protected_infrastructure_scheduler_gpu_seconds": 90,
            "protected_infrastructure_submissions_completed": 3,
        },
        "production_admissibility": "CANNOT_CHECK",
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scheduler_node": node,
        "scientific_authority_delta": "NONE",
        "task_bearing_requests": 0,
        "tokenize_requests": 0,
    }


def _failure_code(
    environment: Mapping[str, Any],
    devices: Mapping[str, Any],
    cgroup: Mapping[str, Any],
    commands: Mapping[str, Any],
) -> str:
    if environment.get("validation_complete") is not True:
        return "ENVIRONMENT_INVALID"
    if devices.get("scan_complete") is not True:
        return "DEVICE_INVENTORY_INCOMPLETE"
    if cgroup.get("capture_complete") is not True:
        return "CGROUP_EVIDENCE_INCOMPLETE"
    for name in ("nvidia_smi_list", "unscoped_identity", "scoped_identity"):
        if commands.get(name, {}).get("status") != "COMPLETED":
            return "COMMAND_CAPTURE_INCOMPLETE"
    return "DIAGNOSTIC_INCOMPLETE"


def run(
    output_root: Path,
    *,
    environmentb: Optional[Mapping[Any, Any]] = None,
    dev_root: Path = Path("/dev"),
    cgroup_path: Path = Path("/proc/self/cgroup"),
    mountinfo_path: Path = Path("/proc/self/mountinfo"),
    command_runner: Callable[..., dict[str, Any]] = bounded_command,
) -> Tuple[int, dict[str, Any]]:
    contract, contract_sha256, contract_identity = load_contract()
    predecessor, predecessor_binding, predecessor_identity = load_predecessor(contract)
    del predecessor
    root_fd = _create_output_root(output_root)
    completed_stages = ["CONTRACT_BOUND", "PREDECESSOR_BOUND"]
    environment: dict[str, Any] = {}
    devices: dict[str, Any] = {}
    cgroup: dict[str, Any] = {}
    commands: dict[str, Any] = {}
    parsed: dict[str, Any] = {}
    caught: Optional[BaseException] = None
    try:
        try:
            environment = capture_environment(environmentb)
            completed_stages.append("VISIBILITY_ENVIRONMENT_CAPTURED")
            devices = capture_device_inventory(dev_root)
            completed_stages.append("DEVICE_INVENTORY_CAPTURED")
            cgroup = capture_cgroup_evidence(cgroup_path, mountinfo_path)
            completed_stages.append("CGROUP_EVIDENCE_CAPTURED")
            commands["nvidia_smi_list"] = command_runner(
                list(NVIDIA_SMI_LIST_ARGV),
                timeout_seconds=COMMAND_TIMEOUT_SECONDS,
                stream_byte_cap=COMMAND_STREAM_BYTE_CAP,
                environment=COMMAND_ENVIRONMENT,
            )
            completed_stages.append("NVIDIA_SMI_LIST_CAPTURED")
            commands["unscoped_identity"] = command_runner(
                list(NVIDIA_SMI_UNSCOPED_IDENTITY_ARGV),
                timeout_seconds=COMMAND_TIMEOUT_SECONDS,
                stream_byte_cap=COMMAND_STREAM_BYTE_CAP,
                environment=COMMAND_ENVIRONMENT,
            )
            completed_stages.append("UNSCOPED_IDENTITY_CAPTURED")
            token = environment.get("cuda_visible_devices_token")
            if isinstance(token, str):
                commands["scoped_identity"] = command_runner(
                    scoped_identity_argv(token),
                    timeout_seconds=COMMAND_TIMEOUT_SECONDS,
                    stream_byte_cap=COMMAND_STREAM_BYTE_CAP,
                    environment=COMMAND_ENVIRONMENT,
                )
                completed_stages.append("SCOPED_IDENTITY_CAPTURED")
            else:
                commands["scoped_identity"] = _empty_command_capture(
                    None, "NOT_RUN_INVALID_SCOPED_TOKEN"
                )
                completed_stages.append("SCOPED_IDENTITY_NOT_RUN")

            parsed["nvidia_smi_list"] = parse_list_capture(commands["nvidia_smi_list"])
            parsed["unscoped_identity"] = parse_identity_capture(commands["unscoped_identity"])
            parsed["scoped_identity"] = parse_identity_capture(commands["scoped_identity"])
            parsed["scoped_identity"]["scope_token"] = token if isinstance(token, str) else None
            parsed["scoped_identity"]["scope_token_matches_identity"] = (
                _scope_token_matches_identity(
                    token if isinstance(token, str) else None,
                    parsed["scoped_identity"],
                )
            )
            completed_stages.append("PARSE_POLICY_APPLIED")
        except BaseException as exc:
            caught = exc

        evidence_complete = bool(
            caught is None
            and environment.get("validation_complete") is True
            and devices.get("scan_complete") is True
            and cgroup.get("capture_complete") is True
            and _commands_complete(commands)
        )
        decision = classify_diagnostic(
            {
                "commands": commands,
                "device_inventory": devices,
                "evidence_complete": evidence_complete,
                "parsed_identities": parsed,
            }
        )
        if evidence_complete:
            completed_stages.append("DIAGNOSTIC_DECISION_BOUND")

        try:
            final_contract, final_contract_sha256, final_contract_identity = load_contract()
            final_predecessor, final_binding, final_predecessor_identity = load_predecessor(
                final_contract
            )
            del final_predecessor
            if (
                final_contract != contract
                or final_contract_sha256 != contract_sha256
                or final_contract_identity != contract_identity
                or final_binding != predecessor_binding
                or final_predecessor_identity != predecessor_identity
            ):
                raise GateError("SOURCE_DRIFT", "contract or predecessor changed during execution")
        except BaseException as exc:
            caught = exc
            evidence_complete = False
            decision = INCOMPLETE_DECISION

        common = _common_receipt(
            contract_sha256=contract_sha256,
            predecessor_binding=predecessor_binding,
            completed_stages=completed_stages,
            environment=environment,
            device_inventory=devices,
            cgroup_evidence=cgroup,
            commands=commands,
            parsed_outputs=parsed,
        )
        if evidence_complete and caught is None:
            receipt = {
                "schema_version": SCHEMA,
                "authority": (
                    "BODY_FREE_GPU_VISIBILITY_DIAGNOSTIC_RESULT_ONLY__"
                    "NO_CAUSAL_PROOF_PROTECTED_EXECUTION_TASK_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY"
                ),
                "status": "PASS_GPU_VISIBILITY_DIAGNOSTIC",
                **common,
                "decision": decision,
            }
            _persist_receipt(output_root, root_fd, SUCCESS_NAME, receipt)
            return 0, receipt

        error = caught if isinstance(caught, GateError) else None
        code = error.code if error is not None else _failure_code(environment, devices, cgroup, commands)
        detail_text = str(error) if error is not None else code
        detail = f"{code}:{detail_text}".encode("utf-8", errors="replace")
        receipt = {
            "schema_version": CANNOT_SCHEMA,
            "authority": (
                "BODY_FREE_GPU_VISIBILITY_DIAGNOSTIC_INCOMPLETE_ONLY__"
                "NO_CAUSAL_PROOF_PROTECTED_EXECUTION_TASK_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY"
            ),
            "status": "CANNOT_CHECK_GPU_VISIBILITY_DIAGNOSTIC",
            **common,
            "decision": INCOMPLETE_DECISION,
            "failure_code": code,
            "failure_detail_sha256": sha256_bytes(detail),
        }
        _persist_receipt(output_root, root_fd, CANNOT_NAME, receipt)
        return 1, receipt
    finally:
        os.close(root_fd)


def parse_cli(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the body-free V6 GPU visibility diagnostic")
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    if len(argv) != 2 or argv[0] != "--output-root":
        raise GateError("ARGV_INVALID", "only exact --output-root argv is accepted")
    if os.fspath(args.output_root) != EXPECTED_OUTPUT_ROOT:
        raise GateError("ARGV_INVALID", "output root differs from the exact V6 freeze")
    return args


def _raise_termination(signum: int, frame: Any) -> None:
    del frame
    raise GateError("TERMINATION_REQUESTED", f"received signal {signum}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    previous_sigterm = signal.signal(signal.SIGTERM, _raise_termination)
    try:
        actual = list(sys.argv[1:] if argv is None else argv)
        try:
            args = parse_cli(actual)
            code, receipt = run(args.output_root)
        except BaseException as caught:
            error = caught if isinstance(caught, GateError) else GateError(
                "UNEXPECTED_FAILURE", f"{type(caught).__name__}:{caught}"
            )
            detail = f"{type(error).__name__}:{error}".encode("utf-8", errors="replace")
            print(
                f"{CANNOT_TERMINAL} failure_code={error.code} "
                f"detail_sha256={sha256_bytes(detail)}",
                file=sys.stderr,
            )
            return 2
        if code == 0:
            print(f"{SUCCESS_TERMINAL} decision={receipt['decision']}")
        else:
            print(
                f"{CANNOT_TERMINAL} failure_code={receipt['failure_code']} "
                f"detail_sha256={receipt['failure_detail_sha256']}",
                file=sys.stderr,
            )
        return code
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)


if __name__ == "__main__":
    raise SystemExit(main())
