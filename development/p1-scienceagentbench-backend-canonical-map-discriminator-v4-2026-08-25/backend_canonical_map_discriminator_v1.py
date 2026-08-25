#!/usr/bin/env python3
"""Body-free live discriminator for logical/canonical ``/proc/maps`` aliases.

The discriminator starts the exact frozen loopback llama-server, performs only
body-free health/slot reads, and proves that the frozen server, CUDA backend,
and model identities are mapped under only their frozen logical or canonical
paths.  It never opens protected packets or sends tokenize/completion requests.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "BACKEND_CANONICAL_MAP_DISCRIMINATOR_CONTRACT_V1.json"
SUCCESS_NAME = "BACKEND_CANONICAL_MAP_DISCRIMINATOR_RESULT_V1.json"
CANNOT_NAME = "BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json"
SUCCESS_TERMINAL = "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_PASS"
CANNOT_TERMINAL = "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK"
SCHEMA = "orion.p1.scienceagentbench.backend-canonical-map-discriminator-result.v1"
CANNOT_SCHEMA = (
    "orion.p1.scienceagentbench.backend-canonical-map-discriminator-cannot-check.v1"
)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
JOB_RE = re.compile(r"^[1-9][0-9]*$")
GPU_UUID_RE = re.compile(
    r"^GPU-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}$"
)
MODE_RE = re.compile(r"^0[0-7]{3}$")
MAP_ADDRESS_RE = re.compile(r"^[0-9a-f]+-[0-9a-f]+$")
MAP_PERMISSION_RE = re.compile(r"^[r-][w-][x-][ps]$")
MAP_OFFSET_RE = re.compile(r"^[0-9a-f]+$")
MAP_DEVICE_RE = re.compile(r"^[0-9a-f]+:[0-9a-f]+$")
MAP_INODE_RE = re.compile(r"^(0|[1-9][0-9]*)$")
BODY_FREE_HTTP_PATHS = ("/health", "/slots")
BODY_FREE_HTTP_REQUEST_TYPES_ALLOWED = ("GET /health", "GET /slots")
HTTP_BODY_LIMIT_BYTES = 4 * 1024 * 1024
PROXY_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


class GateError(RuntimeError):
    """Typed fail-closed discriminator error."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_fd(fd: int) -> str:
    digest = hashlib.sha256()
    offset = 0
    while True:
        try:
            chunk = os.pread(fd, 1024 * 1024, offset)
        except OSError as exc:
            raise GateError("FILE_HASH_UNAVAILABLE", "required descriptor cannot be hashed") from exc
        if not chunk:
            return digest.hexdigest()
        digest.update(chunk)
        offset += len(chunk)


def _read_fd_bytes(fd: int, *, limit: int) -> bytes:
    chunks: list[bytes] = []
    offset = 0
    while True:
        try:
            chunk = os.pread(fd, min(1024 * 1024, limit + 1 - offset), offset)
        except OSError as exc:
            raise GateError("FILE_READ_UNAVAILABLE", "required descriptor cannot be read") from exc
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        offset += len(chunk)
        if offset > limit:
            raise GateError("FILE_READ_UNAVAILABLE", "required descriptor exceeds byte limit")


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
            raw.decode("utf-8"),
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
    return value


def _load_contract_bound() -> Tuple[dict[str, Any], str, Tuple[int, int]]:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        entry_before = CONTRACT_PATH.lstat()
        fd = os.open(CONTRACT_PATH, flags)
    except OSError as exc:
        raise GateError("CONTRACT_INVALID", "contract cannot be opened") from exc
    try:
        opened_before = os.fstat(fd)
        if (
            stat.S_ISLNK(entry_before.st_mode)
            or not stat.S_ISREG(entry_before.st_mode)
            or not stat.S_ISREG(opened_before.st_mode)
            or (entry_before.st_dev, entry_before.st_ino)
            != (opened_before.st_dev, opened_before.st_ino)
        ):
            raise GateError("CONTRACT_INVALID", "contract must be one regular non-symlink file")
        raw = _read_fd_bytes(fd, limit=16 * 1024 * 1024)
        opened_after = os.fstat(fd)
        entry_after = CONTRACT_PATH.lstat()
        if (
            (opened_before.st_dev, opened_before.st_ino, opened_before.st_size)
            != (opened_after.st_dev, opened_after.st_ino, opened_after.st_size)
            or (entry_after.st_dev, entry_after.st_ino)
            != (opened_after.st_dev, opened_after.st_ino)
            or not stat.S_ISREG(entry_after.st_mode)
        ):
            raise GateError("CONTRACT_INVALID", "contract identity changed while read")
    except OSError as exc:
        raise GateError("CONTRACT_INVALID", "contract cannot be inspected") from exc
    finally:
        os.close(fd)
    contract = strict_json_bytes(raw, "canonical-map discriminator contract")
    if raw != canonical_json_bytes(contract) + b"\n":
        raise GateError("CONTRACT_INVALID", "contract is not exact canonical JSON with one LF")
    if contract.get("schema_version") != (
        "orion.p1.scienceagentbench.backend-canonical-map-discriminator-contract.v1"
    ):
        raise GateError("CONTRACT_INVALID", "contract schema mismatch")
    if contract.get("status") != "FROZEN_BODY_FREE_DISCRIMINATOR_NOT_EXECUTED":
        raise GateError("CONTRACT_INVALID", "contract status mismatch")
    if contract.get("submission_authority") is not False:
        raise GateError("CONTRACT_INVALID", "contract cannot grant submission authority")
    if not isinstance(contract.get("base_commit"), str) or COMMIT_RE.fullmatch(
        contract["base_commit"]
    ) is None:
        raise GateError("CONTRACT_INVALID", "base commit is not lowercase Git object identity")
    if contract.get("body_free_http_allowlist") != list(
        BODY_FREE_HTTP_REQUEST_TYPES_ALLOWED
    ):
        raise GateError("CONTRACT_INVALID", "contract body-free HTTP allowlist differs")
    if contract.get("body_free_http_forbidden") != [
        "POST /tokenize",
        "POST /completion",
        "ANY_PROTECTED_OR_TASK_BEARING_REQUEST",
    ]:
        raise GateError("CONTRACT_INVALID", "contract forbidden HTTP boundary differs")
    for field, expected in (
        ("official_evaluator_invoked", False),
        ("official_outcomes_opened", 0),
        ("protected_packet_bodies_opened", 0),
        ("protected_prompt_bodies_opened", 0),
        ("production_admissibility", "CANNOT_CHECK"),
        ("scientific_authority_delta", "NONE"),
    ):
        if contract.get(field) != expected or isinstance(contract.get(field), bool) != isinstance(
            expected, bool
        ):
            raise GateError("CONTRACT_INVALID", f"contract truthful boundary differs at {field}")
    gpu_gate = contract.get("gpu_identity_gate")
    if not isinstance(gpu_gate, Mapping) or gpu_gate.get("nvidia_smi_argv") != [
        "/usr/bin/nvidia-smi",
        "--query-gpu=index,uuid,name",
        "--format=csv,noheader,nounits",
    ]:
        raise GateError("CONTRACT_INVALID", "contract nvidia-smi argv differs")
    return (
        contract,
        sha256_bytes(raw),
        (opened_after.st_dev, opened_after.st_ino),
    )


def load_contract() -> dict[str, Any]:
    """Load the exact frozen contract (compatibility surface for validators)."""

    contract, _, _ = _load_contract_bound()
    return contract


def _validate_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise GateError("CONTRACT_INVALID", f"{label} is not lowercase SHA-256")
    return value


def _stable_file_stat(info: os.stat_result) -> Tuple[int, ...]:
    """Return every byte/custody field that must remain stable while hashing."""

    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mode,
        info.st_uid,
        info.st_gid,
        info.st_nlink,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def validate_bound_file(binding: Mapping[str, Any], label: str) -> dict[str, Any]:
    required = {
        "logical_path",
        "canonical_path",
        "bytes",
        "sha256",
        "mode",
        "uid",
        "gid",
        "nlink",
    }
    if not isinstance(binding, Mapping) or set(binding) != required:
        raise GateError("CONTRACT_INVALID", f"{label} binding fields differ")
    logical_text = binding["logical_path"]
    canonical_text = binding["canonical_path"]
    if not isinstance(logical_text, str) or not isinstance(canonical_text, str):
        raise GateError("CONTRACT_INVALID", f"{label} paths must be strings")
    if (
        not logical_text
        or not canonical_text
        or "\x00" in logical_text
        or "\x00" in canonical_text
        or any(character.isspace() for character in logical_text + canonical_text)
    ):
        raise GateError("BOUND_FILE_INVALID", f"{label} paths are not map-safe")
    logical = Path(logical_text)
    canonical = Path(canonical_text)
    if not logical.is_absolute() or not canonical.is_absolute():
        raise GateError("BOUND_FILE_INVALID", f"{label} paths must be absolute")
    if os.path.normpath(logical_text) != logical_text or os.path.normpath(
        canonical_text
    ) != canonical_text:
        raise GateError("BOUND_FILE_INVALID", f"{label} paths are not normalized")
    mode_text = binding["mode"]
    if not isinstance(mode_text, str) or MODE_RE.fullmatch(mode_text) is None:
        raise GateError("CONTRACT_INVALID", f"{label} mode is not exact four-digit octal")
    for field in ("bytes", "uid", "gid", "nlink"):
        value = binding[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GateError("CONTRACT_INVALID", f"{label} {field} is not a nonnegative integer")
    if binding["nlink"] < 1:
        raise GateError("CONTRACT_INVALID", f"{label} nlink must be positive")
    expected_sha = _validate_sha(binding["sha256"], f"{label} sha256")
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    logical_fd: Optional[int] = None
    canonical_fd: Optional[int] = None
    try:
        logical_lstat = logical.lstat()
        canonical_lstat = canonical.lstat()
        resolved_logical = logical.resolve(strict=True)
        resolved_canonical = canonical.resolve(strict=True)
        logical_fd = os.open(logical, flags)
        canonical_fd = os.open(canonical, flags)
        logical_stat = os.fstat(logical_fd)
        canonical_stat = os.fstat(canonical_fd)
        if stat.S_ISLNK(logical_lstat.st_mode) or not stat.S_ISREG(logical_lstat.st_mode):
            raise GateError(
                "BOUND_FILE_INVALID", f"{label} logical leaf must be regular non-symlink"
            )
        if stat.S_ISLNK(canonical_lstat.st_mode) or not stat.S_ISREG(
            canonical_lstat.st_mode
        ):
            raise GateError(
                "BOUND_FILE_INVALID", f"{label} canonical leaf must be regular non-symlink"
            )
        if not stat.S_ISREG(logical_stat.st_mode) or not stat.S_ISREG(
            canonical_stat.st_mode
        ):
            raise GateError("BOUND_FILE_INVALID", f"{label} descriptors must be regular files")
        if resolved_canonical != canonical or resolved_logical != canonical:
            raise GateError(
                "BOUND_FILE_INVALID",
                f"{label} logical path must resolve to the exact self-resolving canonical path",
            )
        identity = (logical_stat.st_dev, logical_stat.st_ino)
        if identity != (canonical_stat.st_dev, canonical_stat.st_ino):
            raise GateError("BOUND_FILE_INVALID", f"{label} logical/canonical identity differs")
        if identity != (logical_lstat.st_dev, logical_lstat.st_ino) or identity != (
            canonical_lstat.st_dev,
            canonical_lstat.st_ino,
        ):
            raise GateError("BOUND_FILE_INVALID", f"{label} named/descriptor identity differs")
        expected = (
            binding["bytes"],
            int(mode_text, 8),
            binding["uid"],
            binding["gid"],
            binding["nlink"],
        )
        observed = (
            logical_stat.st_size,
            stat.S_IMODE(logical_stat.st_mode),
            logical_stat.st_uid,
            logical_stat.st_gid,
            logical_stat.st_nlink,
        )
        if observed != expected:
            raise GateError("BOUND_FILE_INVALID", f"{label} custody differs from freeze")
        # One descriptor hash is sufficient after exact device/inode equality.
        # Hashing the canonical alias again would reread the 18.56 GB GGUF.
        if _sha256_fd(logical_fd) != expected_sha:
            raise GateError("BOUND_FILE_INVALID", f"{label} hash differs from freeze")
        logical_after = logical.lstat()
        canonical_after = canonical.lstat()
        logical_fd_after = os.fstat(logical_fd)
        canonical_fd_after = os.fstat(canonical_fd)
        if (
            _stable_file_stat(logical_after) != _stable_file_stat(logical_lstat)
            or _stable_file_stat(canonical_after) != _stable_file_stat(canonical_lstat)
            or _stable_file_stat(logical_fd_after) != _stable_file_stat(logical_stat)
            or _stable_file_stat(canonical_fd_after) != _stable_file_stat(canonical_stat)
        ):
            raise GateError("BOUND_FILE_INVALID", f"{label} bytes or custody changed while hashed")
    except GateError:
        raise
    except (OSError, RuntimeError) as exc:
        raise GateError("BOUND_FILE_INVALID", f"{label} cannot be inspected") from exc
    finally:
        if canonical_fd is not None:
            os.close(canonical_fd)
        if logical_fd is not None:
            os.close(logical_fd)
    return {
        "logical_path": logical_text,
        "canonical_path": canonical_text,
        "bytes": logical_stat.st_size,
        "sha256": expected_sha,
        "mode": f"{stat.S_IMODE(logical_stat.st_mode):04o}",
        "uid": logical_stat.st_uid,
        "gid": logical_stat.st_gid,
        "nlink": logical_stat.st_nlink,
        "mtime_ns": logical_stat.st_mtime_ns,
        "ctime_ns": logical_stat.st_ctime_ns,
        "device": str(logical_stat.st_dev),
        "inode": str(logical_stat.st_ino),
        "maps_device": f"{os.major(logical_stat.st_dev):02x}:{os.minor(logical_stat.st_dev):02x}",
    }


def _rebind_runtime_files(
    runtime_files: Mapping[str, Mapping[str, Any]],
    frozen_files: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    rebound = {
        label: validate_bound_file(runtime_files[label], label)
        for label in ("server", "backend", "model")
    }
    if rebound != frozen_files:
        raise GateError(
            "RUNTIME_FILE_REATTESTATION_DRIFT",
            "runtime file bytes or custody changed after mapping reattestation",
        )
    return rebound


def expected_server_argv(files: Mapping[str, Mapping[str, Any]]) -> list[str]:
    return [
        str(files["server"]["logical_path"]),
        "--model",
        str(files["model"]["logical_path"]),
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
        "--ctx-size",
        "32768",
        "--parallel",
        "1",
        "--no-cont-batching",
        "--threads",
        "8",
        "--threads-batch",
        "8",
        "--batch-size",
        "512",
        "--ubatch-size",
        "512",
        "--cache-type-k",
        "f16",
        "--cache-type-v",
        "f16",
        "--flash-attn",
        "on",
        "--n-gpu-layers",
        "all",
        "--no-context-shift",
        "--metrics",
        "--slots",
    ]


def build_server_environment(
    contract: Mapping[str, Any], source: Optional[Mapping[str, str]] = None
) -> dict[str, str]:
    incoming = dict(os.environ if source is None else source)
    allowed = {
        key: incoming[key]
        for key in (
            "HOME",
            "PATH",
            "LANG",
            "LC_ALL",
            "LC_CTYPE",
            "TMPDIR",
            "CUDA_VISIBLE_DEVICES",
        )
        if key in incoming
    }
    visible = allowed.get("CUDA_VISIBLE_DEVICES")
    if not isinstance(visible, str) or not visible or "," in visible or any(
        character.isspace() for character in visible
    ):
        raise GateError("GPU_ENVIRONMENT_INVALID", "exactly one CUDA-visible device is required")
    loader = contract.get("loader_environment")
    runtime_files = contract.get("runtime_files")
    if not isinstance(loader, Mapping) or not isinstance(runtime_files, Mapping):
        raise GateError("CONTRACT_INVALID", "loader/runtime contract objects are absent")
    ld_library_path = loader.get("effective_server_ld_library_path")
    backend = runtime_files.get("backend")
    server = runtime_files.get("server")
    if (
        not isinstance(ld_library_path, str)
        or not isinstance(backend, Mapping)
        or not isinstance(server, Mapping)
        or not isinstance(backend.get("logical_path"), str)
        or not isinstance(server.get("logical_path"), str)
    ):
        raise GateError("CONTRACT_INVALID", "loader/runtime environment binding is invalid")
    loader_parts = ld_library_path.split(":")
    expected_prefix = [
        os.fspath(Path(server["logical_path"]).parent),
        os.fspath(Path(backend["logical_path"]).parent),
    ]
    if (
        len(loader_parts) != 3
        or loader_parts[:2] != expected_prefix
        or len(set(loader_parts)) != 3
        or any(
            not part
            or not Path(part).is_absolute()
            or os.path.normpath(part) != part
            or any(character.isspace() for character in part)
            for part in loader_parts
        )
    ):
        raise GateError("CONTRACT_INVALID", "server LD_LIBRARY_PATH is not the exact three-directory freeze")
    allowed["LD_LIBRARY_PATH"] = ld_library_path
    allowed["GGML_BACKEND_PATH"] = backend["logical_path"]
    for key in PROXY_KEYS:
        allowed[key] = ""
    allowed["NO_PROXY"] = "127.0.0.1,localhost"
    allowed["no_proxy"] = "127.0.0.1,localhost"
    if any(not isinstance(value, str) for value in allowed.values()) or any(
        "\x00" in key or "\x00" in value for key, value in allowed.items()
    ):
        raise GateError("GPU_ENVIRONMENT_INVALID", "server environment contains NUL")
    return allowed


def _http_get_json(path: str, timeout: float = 2.0) -> Any:
    if path not in BODY_FREE_HTTP_PATHS:
        raise GateError("BODY_FREE_BOUNDARY_VIOLATION", "HTTP path is outside the body-free allowlist")
    connection = http.client.HTTPConnection("127.0.0.1", 8080, timeout=timeout)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        status_code = response.status
        raw = response.read(HTTP_BODY_LIMIT_BYTES + 1)
    finally:
        connection.close()
    if len(raw) > HTTP_BODY_LIMIT_BYTES:
        raise GateError("SERVER_NOT_READY", f"readiness response is oversized at {path}")
    if status_code != 200:
        raise GateError("SERVER_NOT_READY", f"readiness HTTP status differs at {path}")
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                GateError("SERVER_NOT_READY", f"nonfinite readiness JSON at {path}")
            ),
        )
    except GateError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("SERVER_NOT_READY", f"readiness JSON is invalid at {path}") from exc


def wait_for_server(process: subprocess.Popen[Any], timeout_seconds: float = 600.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_code = "CONNECTION_PENDING"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise GateError("SERVER_EXITED", "llama-server exited before readiness")
        try:
            health = _http_get_json("/health")
            slots = _http_get_json("/slots")
            if not isinstance(health, Mapping):
                raise GateError("SERVER_NOT_READY", "live health response is not an object")
            if not isinstance(slots, list) or len(slots) != 1:
                raise GateError("SERVER_NOT_READY", "live slots response is not exactly one slot")
            return {
                "health_sha256": sha256_bytes(canonical_json_bytes(health)),
                "slots_sha256": sha256_bytes(canonical_json_bytes(slots)),
                "slot_count": 1,
                "successful_response_request_types": list(
                    BODY_FREE_HTTP_REQUEST_TYPES_ALLOWED
                ),
            }
        except (OSError, GateError) as exc:
            last_code = exc.code if isinstance(exc, GateError) else type(exc).__name__
            time.sleep(0.25)
    raise GateError("SERVER_READINESS_TIMEOUT", f"readiness deadline expired after {last_code}")


def _parse_maps(maps_text: str) -> list[dict[str, str]]:
    if not isinstance(maps_text, str) or "\x00" in maps_text or "\r" in maps_text:
        raise GateError("PROCESS_INSPECTION_FAILED", "proc maps text is not canonical")
    rows: list[dict[str, str]] = []
    for line in maps_text.splitlines():
        if not line:
            raise GateError("PROCESS_INSPECTION_FAILED", "proc maps contains an empty row")
        fields = line.split(maxsplit=5)
        if len(fields) not in (5, 6):
            raise GateError("PROCESS_INSPECTION_FAILED", "proc maps row field count differs")
        address, permissions, offset, device, inode = fields[:5]
        device = device.casefold()
        offset = offset.casefold()
        if (
            MAP_ADDRESS_RE.fullmatch(address.casefold()) is None
            or MAP_PERMISSION_RE.fullmatch(permissions) is None
            or MAP_OFFSET_RE.fullmatch(offset) is None
            or MAP_DEVICE_RE.fullmatch(device) is None
            or MAP_INODE_RE.fullmatch(inode) is None
        ):
            raise GateError("PROCESS_INSPECTION_FAILED", "proc maps row grammar differs")
        start_text, end_text = address.split("-", 1)
        if int(start_text, 16) >= int(end_text, 16):
            raise GateError("PROCESS_INSPECTION_FAILED", "proc maps address range is invalid")
        rows.append(
            {
                "address": address.casefold(),
                "permissions": permissions,
                "offset": offset,
                "device": device,
                "inode": inode,
                "path": fields[5] if len(fields) == 6 else "",
            }
        )
    return rows


def require_mapped_identity(
    rows: Sequence[Mapping[str, str]], binding: Mapping[str, Any], label: str
) -> dict[str, Any]:
    logical = binding["logical_path"]
    canonical = binding["canonical_path"]
    allowed_paths = {logical, canonical}
    device = str(binding["maps_device"]).casefold()
    inode = str(binding["inode"])
    path_rows = [row for row in rows if row["path"] in allowed_paths]
    identity_rows = [
        row for row in rows if row["device"] == device and row["inode"] == inode
    ]
    if not path_rows or not identity_rows:
        raise GateError("MAPPING_ABSENT", f"{label} mapping identity is absent")
    if any(row["device"] != device or row["inode"] != inode for row in path_rows):
        raise GateError("MAPPING_IDENTITY_DRIFT", f"{label} allowed path has wrong identity")
    if any(row["path"] not in allowed_paths for row in identity_rows):
        raise GateError("MAPPING_ALIAS_DRIFT", f"{label} identity is mapped under an unbound alias")
    observed_paths = sorted({row["path"] for row in identity_rows})
    segments = sorted(
        (
            {
                "address": row["address"],
                "permissions": row["permissions"],
                "offset": row["offset"],
                "device": row["device"],
                "inode": row["inode"],
                "path": row["path"],
            }
            for row in identity_rows
        ),
        key=lambda row: (
            row["address"],
            row["permissions"],
            row["offset"],
            row["device"],
            row["inode"],
            row["path"],
        ),
    )
    return {
        "logical_path": logical,
        "canonical_path": canonical,
        "allowed_mapped_paths": sorted(allowed_paths),
        "observed_mapped_paths": observed_paths,
        "device": str(binding["device"]),
        "maps_device": device,
        "inode": inode,
        "sha256": binding["sha256"],
        "segment_count": len(identity_rows),
        "segment_permissions": sorted({row["permissions"] for row in identity_rows}),
        "segments": segments,
    }


def _parse_nul_records(raw: bytes, label: str) -> list[bytes]:
    if not raw or not raw.endswith(b"\0"):
        raise GateError(label, "proc NUL record stream lacks its exact terminator")
    records = raw[:-1].split(b"\0")
    if not records or any(not record for record in records):
        raise GateError(label, "proc NUL record stream contains an empty record")
    return records


def attest_process_identity(
    pid: int,
    server_binding: Mapping[str, Any],
    backend_binding: Mapping[str, Any],
    model_binding: Mapping[str, Any],
    expected_argv: Sequence[str],
    *,
    proc_root: Path = Path("/proc"),
    expected_environment: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise GateError("PROCESS_INSPECTION_FAILED", "live server pid is not positive")
    root = proc_root / str(pid)
    try:
        exe_link = root / "exe"
        exe_target = exe_link.resolve(strict=True)
        exe_info = exe_link.stat()
        cmdline_raw = (root / "cmdline").read_bytes()
        environ_raw = (root / "environ").read_bytes()
        maps_text = (root / "maps").read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise GateError("PROCESS_INSPECTION_FAILED", "live server process cannot be inspected") from exc
    if exe_target != Path(server_binding["canonical_path"]):
        raise GateError("EXECUTABLE_DRIFT", "server executable canonical path differs")
    if (str(exe_info.st_dev), str(exe_info.st_ino)) != (
        str(server_binding["device"]),
        str(server_binding["inode"]),
    ):
        raise GateError("EXECUTABLE_DRIFT", "server executable identity differs")
    try:
        observed_argv = [
            item.decode("utf-8") for item in _parse_nul_records(cmdline_raw, "ARGV_DRIFT")
        ]
    except UnicodeDecodeError as exc:
        raise GateError("ARGV_DRIFT", "server command line is not UTF-8") from exc
    if observed_argv != list(expected_argv):
        raise GateError("ARGV_DRIFT", "server command line differs from exact logical argv")
    environ: dict[str, str] = {}
    try:
        for item in _parse_nul_records(environ_raw, "ENVIRONMENT_DRIFT"):
            if b"=" not in item:
                raise GateError("ENVIRONMENT_DRIFT", "server environment record lacks equals")
            key, value = item.split(b"=", 1)
            decoded_key = key.decode("utf-8")
            if not decoded_key or decoded_key in environ:
                raise GateError("ENVIRONMENT_DRIFT", "server environment key is empty or duplicate")
            environ[decoded_key] = value.decode("utf-8")
    except GateError:
        raise
    except UnicodeDecodeError as exc:
        raise GateError("ENVIRONMENT_DRIFT", "server environment is not UTF-8") from exc
    if expected_environment is not None:
        normalized_expected = dict(expected_environment)
        if any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in normalized_expected.items()
        ):
            raise GateError("CONTRACT_INVALID", "expected server environment is not string-valued")
        if environ != normalized_expected:
            raise GateError("ENVIRONMENT_DRIFT", "server environment differs from the exact allowlist")
    if environ.get("GGML_BACKEND_PATH") != backend_binding["logical_path"]:
        raise GateError("ENVIRONMENT_DRIFT", "GGML_BACKEND_PATH is not the frozen logical path")
    for key in PROXY_KEYS:
        if environ.get(key, "") != "":
            raise GateError("ENVIRONMENT_DRIFT", "server proxy environment is nonempty")
    if environ.get("NO_PROXY") != "127.0.0.1,localhost" or environ.get(
        "no_proxy"
    ) != "127.0.0.1,localhost":
        raise GateError("ENVIRONMENT_DRIFT", "server loopback proxy bypass differs")
    rows = _parse_maps(maps_text)
    server_map = require_mapped_identity(rows, server_binding, "llama-server")
    backend_map = require_mapped_identity(rows, backend_binding, "CUDA backend")
    model_map = require_mapped_identity(rows, model_binding, "model GGUF")
    return {
        "pid": pid,
        "executable": {
            "logical_path": server_binding["logical_path"],
            "canonical_path": server_binding["canonical_path"],
            "device": server_binding["device"],
            "inode": server_binding["inode"],
            "sha256": server_binding["sha256"],
        },
        "argv": list(expected_argv),
        "cmdline_sha256": sha256_bytes(cmdline_raw),
        "environment_sha256": sha256_bytes(canonical_json_bytes(environ)),
        "ggml_backend_path": backend_binding["logical_path"],
        "ld_library_path": environ.get("LD_LIBRARY_PATH"),
        "proxy_environment_empty": True,
        "loopback_proxy_bypass_exact": True,
        "server_mapping": server_map,
        "cuda_backend_mapping": backend_map,
        "model_mapping": model_map,
    }


def _snapshot_socket_inodes(fd_root: Path) -> set[str]:
    socket_inodes: set[str] = set()
    try:
        entries = sorted(fd_root.iterdir(), key=lambda entry: entry.name)
        for fd in entries:
            try:
                target = os.readlink(fd)
            except OSError as exc:
                raise GateError(
                    "LISTENER_DRIFT", "live server file descriptors changed while inspected"
                ) from exc
            if target.startswith("socket:[") and target.endswith("]"):
                inode = target[8:-1]
                if MAP_INODE_RE.fullmatch(inode) is not None and inode != "0":
                    socket_inodes.add(inode)
    except GateError:
        raise
    except OSError as exc:
        raise GateError("LISTENER_DRIFT", "live server file descriptors cannot be listed") from exc
    return socket_inodes


def attest_listener(pid: int, proc_root: Path = Path("/proc")) -> dict[str, Any]:
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise GateError("LISTENER_DRIFT", "live server pid is not positive")
    root = proc_root / str(pid)
    try:
        fd_root = root / "fd"
        socket_inodes_before = _snapshot_socket_inodes(fd_root)
        network_tables = {
            "tcp": (root / "net/tcp").read_text(encoding="ascii", errors="strict"),
            "tcp6": (root / "net/tcp6").read_text(encoding="ascii", errors="strict"),
        }
        socket_inodes_after = _snapshot_socket_inodes(fd_root)
    except GateError:
        raise
    except (OSError, UnicodeError) as exc:
        raise GateError("LISTENER_DRIFT", "live server listener cannot be inspected") from exc
    if socket_inodes_after != socket_inodes_before:
        raise GateError(
            "LISTENER_DRIFT", "live server socket descriptors changed across network-table read"
        )
    socket_inodes = socket_inodes_before
    owned_listeners: list[Tuple[str, str, str]] = []
    local_grammar = {
        "tcp": re.compile(r"^[0-9A-Fa-f]{8}:[0-9A-Fa-f]{4}$"),
        "tcp6": re.compile(r"^[0-9A-Fa-f]{32}:[0-9A-Fa-f]{4}$"),
    }
    for protocol, table in network_tables.items():
        if "\r" in table or "\x00" in table:
            raise GateError("LISTENER_DRIFT", f"proc {protocol} text is not canonical")
        lines = table.splitlines()
        if not lines:
            raise GateError("LISTENER_DRIFT", f"proc {protocol} table is empty")
        for line in lines[1:]:
            fields = line.split()
            if len(fields) < 10:
                raise GateError("LISTENER_DRIFT", f"proc {protocol} row field count differs")
            local, state_code, inode = fields[1], fields[3], fields[9]
            if (
                local_grammar[protocol].fullmatch(local) is None
                or re.fullmatch(r"^[0-9A-Fa-f]{2}$", state_code) is None
                or MAP_INODE_RE.fullmatch(inode) is None
            ):
                raise GateError("LISTENER_DRIFT", f"proc {protocol} row grammar differs")
            if state_code.casefold() == "0a" and inode in socket_inodes:
                owned_listeners.append((protocol, local.upper(), inode))
    if len(owned_listeners) != 1 or owned_listeners[0][:2] != ("tcp", "0100007F:1F90"):
        raise GateError(
            "LISTENER_DRIFT",
            "server must own only one TCP/TCP6 listener at exact 127.0.0.1:8080",
        )
    return {
        "listen_host": "127.0.0.1",
        "listen_port": 8080,
        "socket_inode": owned_listeners[0][2],
    }


def capture_gpu_identity(environment: Optional[Mapping[str, str]] = None) -> dict[str, Any]:
    env = dict(os.environ if environment is None else environment)
    job_id = env.get("SLURM_JOB_ID")
    visible = env.get("CUDA_VISIBLE_DEVICES")
    if not isinstance(job_id, str) or JOB_RE.fullmatch(job_id) is None:
        raise GateError("GPU_IDENTITY_INVALID", "SLURM_JOB_ID is not canonical")
    if (
        not isinstance(visible, str)
        or not visible
        or "," in visible
        or any(character.isspace() for character in visible)
    ):
        raise GateError("GPU_IDENTITY_INVALID", "CUDA_VISIBLE_DEVICES is not singular")
    try:
        completed = subprocess.run(
            [
                "/usr/bin/nvidia-smi",
                "--query-gpu=index,uuid,name",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                key: env[key]
                for key in (
                    "HOME",
                    "PATH",
                    "LANG",
                    "LC_ALL",
                    "LC_CTYPE",
                    "CUDA_VISIBLE_DEVICES",
                )
                if key in env
            },
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError("GPU_IDENTITY_INVALID", "nvidia-smi could not be executed exactly") from exc
    if completed.returncode != 0:
        raise GateError(
            "GPU_IDENTITY_INVALID",
            f"nvidia-smi failed stderr_sha256={sha256_bytes(completed.stderr)}",
        )
    if completed.stderr:
        raise GateError(
            "GPU_IDENTITY_INVALID",
            f"nvidia-smi emitted stderr_sha256={sha256_bytes(completed.stderr)}",
        )
    try:
        stdout_text = completed.stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise GateError("GPU_IDENTITY_INVALID", "nvidia-smi stdout is not UTF-8") from exc
    if "\r" in stdout_text or (stdout_text and not stdout_text.endswith("\n")):
        raise GateError("GPU_IDENTITY_INVALID", "nvidia-smi stdout line framing differs")
    lines = [line.strip() for line in stdout_text.splitlines() if line.strip()]
    if len(lines) != 1:
        raise GateError("GPU_IDENTITY_INVALID", "visible GPU row count differs from one")
    fields = [field.strip() for field in lines[0].split(",", 2)]
    if (
        len(fields) != 3
        or re.fullmatch(r"0|[1-9][0-9]*", fields[0]) is None
        or GPU_UUID_RE.fullmatch(fields[1]) is None
    ):
        raise GateError("GPU_IDENTITY_INVALID", "visible GPU row is not canonical")
    if fields[2] != "NVIDIA A40":
        raise GateError("GPU_IDENTITY_INVALID", "visible GPU is not exactly NVIDIA A40")
    return {
        "slurm_job_id": job_id,
        "cuda_visible_devices": visible,
        "slurm_job_gpus": env.get("SLURM_JOB_GPUS"),
        "slurm_step_gpus": env.get("SLURM_STEP_GPUS"),
        "visible_index": fields[0],
        "gpu_uuid": fields[1],
        "name": fields[2],
        "nvidia_smi_stdout_sha256": sha256_bytes(completed.stdout),
    }


def _stream_binding(handle: Any) -> dict[str, Any]:
    handle.flush()
    handle.seek(0)
    digest = hashlib.sha256()
    total = 0
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            return {"bytes": total, "sha256": digest.hexdigest()}
        total += len(chunk)
        digest.update(chunk)


def _process_group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for_group_absence(
    process: subprocess.Popen[Any], pgid: int, timeout_seconds: float
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while True:
        process.poll()  # Reap the leader so its zombie cannot retain observable state.
        if not _process_group_exists(pgid):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def cleanup_process(process: Optional[subprocess.Popen[Any]]) -> dict[str, Any]:
    if process is None:
        return {
            "process_started": False,
            "process_absent_after_cleanup": True,
            "process_group_absent_after_cleanup": True,
            "return_code": None,
        }
    try:
        pid = process.pid
        # start_new_session=True makes the child's PID the owned process-group ID.
        pgid = pid
        termination_signal: Optional[str] = None
        if _process_group_exists(pgid):
            termination_signal = "SIGTERM"
            try:
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            if not _wait_for_group_absence(process, pgid, 30.0):
                termination_signal = "SIGKILL"
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _wait_for_group_absence(process, pgid, 30.0)
        process.poll()
        group_absent = not _process_group_exists(pgid)
        leader_reaped = process.returncode is not None
        return {
            "process_started": True,
            "pid": pid,
            "process_group_id": pgid,
            "termination_signal": termination_signal,
            "return_code": process.returncode,
            "process_absent_after_cleanup": leader_reaped and group_absent,
            "process_group_absent_after_cleanup": group_absent,
        }
    except BaseException as exc:
        return {
            "process_started": True,
            "pid": getattr(process, "pid", None),
            "process_group_id": getattr(process, "pid", None),
            "termination_signal": None,
            "return_code": None,
            "cleanup_failure_detail_sha256": sha256_bytes(
                f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
            ),
            "process_absent_after_cleanup": False,
            "process_group_absent_after_cleanup": False,
        }


def _directory_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _create_new_output_root(output_root: Path) -> int:
    if (
        not output_root.is_absolute()
        or output_root.name in {"", ".", ".."}
        or os.path.normpath(os.fspath(output_root)) != os.fspath(output_root)
    ):
        raise GateError("OUTPUT_ROOT_INVALID", "output root must be an absolute normalized leaf")
    parent_fd: Optional[int] = None
    root_fd: Optional[int] = None
    created = False
    succeeded = False
    try:
        parent_fd = os.open(output_root.parent, _directory_open_flags())
        os.mkdir(output_root.name, 0o700, dir_fd=parent_fd)
        created = True
        root_fd = os.open(output_root.name, _directory_open_flags(), dir_fd=parent_fd)
        entry = os.stat(output_root.name, dir_fd=parent_fd, follow_symlinks=False)
        opened = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(entry.st_mode)
            or not stat.S_ISDIR(opened.st_mode)
            or opened.st_uid != os.geteuid()
            or (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise GateError("OUTPUT_ROOT_INVALID", "output root identity changed during creation")
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
        raise GateError("OUTPUT_ROOT_INVALID", "output root must be new and exclusively creatable") from exc
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


def _write_new_receipt(
    output_root: Path,
    name: str,
    receipt: Mapping[str, Any],
    *,
    root_fd: Optional[int] = None,
) -> None:
    payload = canonical_json_bytes(receipt) + b"\n"
    if name not in (SUCCESS_NAME, CANNOT_NAME) or Path(name).name != name:
        raise GateError("OUTPUT_WRITE_FAILED", "receipt name is outside the exact allowlist")
    owned_root_fd = os.dup(root_fd) if root_fd is not None else os.open(
        output_root, _directory_open_flags()
    )
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd: Optional[int] = None
    identity: Optional[Tuple[int, int]] = None
    succeeded = False
    try:
        fd = os.open(name, flags, 0o600, dir_fd=owned_root_fd)
        os.fchmod(fd, 0o600)
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise GateError("OUTPUT_WRITE_FAILED", "receipt write made no progress")
            view = view[written:]
        os.fsync(fd)
        opened = os.fstat(fd)
        identity = (opened.st_dev, opened.st_ino)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_uid != os.geteuid()
            or opened.st_nlink != 1
            or stat.S_IMODE(opened.st_mode) != 0o600
            or opened.st_size != len(payload)
        ):
            raise GateError("OUTPUT_WRITE_FAILED", "receipt descriptor custody differs")
        if _read_fd_bytes(fd, limit=len(payload)) != payload:
            raise GateError("OUTPUT_WRITE_FAILED", "receipt reread differs")
        entry = os.stat(name, dir_fd=owned_root_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != identity
            or entry.st_nlink != 1
        ):
            raise GateError("OUTPUT_WRITE_FAILED", "receipt named identity differs")
        os.fchmod(fd, 0o400)
        os.fsync(fd)
        final_opened = os.fstat(fd)
        final_entry = os.stat(name, dir_fd=owned_root_fd, follow_symlinks=False)
        if (
            (final_opened.st_dev, final_opened.st_ino) != identity
            or (final_entry.st_dev, final_entry.st_ino) != identity
            or stat.S_IMODE(final_opened.st_mode) != 0o400
            or stat.S_IMODE(final_entry.st_mode) != 0o400
            or final_opened.st_size != len(payload)
            or final_entry.st_size != len(payload)
        ):
            raise GateError("OUTPUT_WRITE_FAILED", "receipt final custody differs")
        os.fsync(owned_root_fd)
        succeeded = True
    except GateError:
        raise
    except OSError as exc:
        raise GateError("OUTPUT_WRITE_FAILED", "receipt cannot be exclusively persisted") from exc
    finally:
        if fd is not None:
            try:
                if not succeeded:
                    entry = os.stat(name, dir_fd=owned_root_fd, follow_symlinks=False)
                    opened = os.fstat(fd)
                    if (entry.st_dev, entry.st_ino) == (
                        opened.st_dev,
                        opened.st_ino,
                    ):
                        os.unlink(name, dir_fd=owned_root_fd)
            except OSError:
                pass
            os.close(fd)
        os.close(owned_root_fd)


def _as_gate_error(caught: BaseException) -> GateError:
    if isinstance(caught, GateError):
        return caught
    return GateError("UNEXPECTED_FAILURE", f"{type(caught).__name__}:{caught}")


def _safe_stream_binding(handle: Optional[Any], label: str) -> Tuple[dict[str, Any], Optional[GateError]]:
    if handle is None:
        error = GateError("LOG_CAPTURE_FAILED", f"{label} temporary capture was not created")
        return (
            {
                "status": "CANNOT_CHECK_LOG_STREAM_UNAVAILABLE",
                "failure_detail_sha256": sha256_bytes(
                    f"{type(error).__name__}:{error}".encode("utf-8", errors="replace")
                ),
            },
            error,
        )
    try:
        return _stream_binding(handle), None
    except BaseException as caught:
        error = GateError("LOG_CAPTURE_FAILED", f"{label} temporary capture could not be bound")
        return (
            {
                "status": "CANNOT_CHECK_LOG_STREAM_UNAVAILABLE",
                "failure_detail_sha256": sha256_bytes(
                    f"{type(caught).__name__}:{caught}".encode("utf-8", errors="replace")
                ),
            },
            error,
        )


def _seal_output_root(root_fd: int, output_root: Path) -> None:
    try:
        os.fchmod(root_fd, 0o500)
        os.fsync(root_fd)
        opened = os.fstat(root_fd)
        entry = output_root.lstat()
    except OSError as exc:
        raise GateError("OUTPUT_WRITE_FAILED", "output root cannot be sealed") from exc
    if (
        not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(entry.st_mode)
        or stat.S_IMODE(opened.st_mode) != 0o500
        or stat.S_IMODE(entry.st_mode) != 0o500
        or opened.st_uid != os.geteuid()
        or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)
    ):
        raise GateError("OUTPUT_WRITE_FAILED", "output root final mode differs")


def _persist_final_receipt(
    output_root: Path,
    root_fd: int,
    name: str,
    receipt: Mapping[str, Any],
) -> None:
    _write_new_receipt(output_root, name, receipt, root_fd=root_fd)
    try:
        _seal_output_root(root_fd, output_root)
    except BaseException:
        # Do not leave a mode-0400 success-shaped file in an unsealed output root.
        try:
            os.fchmod(root_fd, 0o700)
            entry = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
            if (
                stat.S_ISREG(entry.st_mode)
                and entry.st_uid == os.geteuid()
                and entry.st_nlink == 1
                and stat.S_IMODE(entry.st_mode) == 0o400
            ):
                os.unlink(name, dir_fd=root_fd)
                os.fsync(root_fd)
            os.fchmod(root_fd, 0o500)
            os.fsync(root_fd)
        except OSError:
            pass
        raise


def run(output_root: Path) -> Tuple[int, dict[str, Any]]:
    contract, contract_sha256, contract_identity = _load_contract_bound()
    root_fd = _create_new_output_root(output_root)
    completed_stages = ["CONTRACT_BOUND"]
    process: Optional[subprocess.Popen[Any]] = None
    caught: Optional[BaseException] = None
    live: dict[str, Any] = {}
    server_stdout: Optional[Any] = None
    server_stderr: Optional[Any] = None
    stdout_binding: dict[str, Any]
    stderr_binding: dict[str, Any]
    try:
        try:
            server_stdout = tempfile.TemporaryFile(mode="w+b")
            server_stderr = tempfile.TemporaryFile(mode="w+b")
            runtime_files = contract.get("runtime_files")
            if not isinstance(runtime_files, Mapping) or set(runtime_files) != {
                "server",
                "backend",
                "model",
            }:
                raise GateError("CONTRACT_INVALID", "runtime_files must bind exactly three files")
            files = {
                label: validate_bound_file(runtime_files[label], label)
                for label in ("server", "backend", "model")
            }
            completed_stages.append("RUNTIME_FILES_BOUND")
            argv = contract.get("server_argv")
            frozen_argv = expected_server_argv(files)
            if (
                not isinstance(argv, list)
                or any(not isinstance(item, str) or "\x00" in item for item in argv)
                or argv != frozen_argv
            ):
                raise GateError(
                    "CONTRACT_INVALID",
                    "server argv differs from the exact body-free logical-path freeze",
                )
            server_environment = build_server_environment(contract)
            process = subprocess.Popen(
                argv,
                stdout=server_stdout,
                stderr=server_stderr,
                env=server_environment,
                start_new_session=True,
            )
            completed_stages.append("SERVER_STARTED")
            readiness = wait_for_server(process)
            completed_stages.append("SERVER_READY_BODY_FREE")
            first = attest_process_identity(
                process.pid,
                files["server"],
                files["backend"],
                files["model"],
                argv,
                expected_environment=server_environment,
            )
            listener = attest_listener(process.pid)
            if process.poll() is not None:
                raise GateError("SERVER_EXITED", "llama-server exited during first attestation")
            completed_stages.append("CANONICAL_MAP_ATTESTATION_1")
            gpu = capture_gpu_identity()
            completed_stages.append("GPU_IDENTITY_BOUND")
            second = attest_process_identity(
                process.pid,
                files["server"],
                files["backend"],
                files["model"],
                argv,
                expected_environment=server_environment,
            )
            first_bytes = canonical_json_bytes(first)
            second_bytes = canonical_json_bytes(second)
            if second_bytes != first_bytes:
                raise GateError("MAPPING_REATTESTATION_DRIFT", "second process attestation differs")
            if process.poll() is not None:
                raise GateError("SERVER_EXITED", "llama-server exited during second attestation")
            completed_stages.append("CANONICAL_MAP_ATTESTATION_2")
            rebound_files = _rebind_runtime_files(runtime_files, files)
            rebound_listener = attest_listener(process.pid)
            if rebound_listener != listener:
                raise GateError(
                    "LISTENER_DRIFT", "server listener changed across attestations"
                )
            if process.poll() is not None:
                raise GateError("SERVER_EXITED", "llama-server exited during final rebind")
            completed_stages.append("RUNTIME_FILES_AND_LISTENER_REBOUND_FINAL")
            live = {
                "runtime_files": rebound_files,
                "readiness": readiness,
                "process_identity": first,
                "process_reattestation": {
                    "attestation_count": 2,
                    "attestation_1_sha256": sha256_bytes(first_bytes),
                    "attestation_2_sha256": sha256_bytes(second_bytes),
                    "byte_identical": True,
                    "attestation_2": second,
                },
                "listener": listener,
                "gpu": gpu,
            }
        except BaseException as exc:
            caught = exc
        cleanup = cleanup_process(process)
        stdout_binding, stdout_error = _safe_stream_binding(server_stdout, "stdout")
        stderr_binding, stderr_error = _safe_stream_binding(server_stderr, "stderr")
        if caught is None and stdout_error is not None:
            caught = stdout_error
        if caught is None and stderr_error is not None:
            caught = stderr_error
        for handle in (server_stdout, server_stderr):
            if handle is not None:
                try:
                    handle.close()
                except BaseException as exc:
                    if caught is None:
                        caught = GateError("LOG_CAPTURE_FAILED", f"temporary log close failed:{type(exc).__name__}")
        cleanup_pass = bool(
            cleanup.get("process_absent_after_cleanup")
            and cleanup.get("process_group_absent_after_cleanup")
        )
        if not cleanup_pass:
            caught = GateError("CLEANUP_FAILED", "server process or group remains after cleanup")
        if cleanup_pass:
            completed_stages.append("SERVER_CLEANUP_PASS")
        try:
            final_contract, final_contract_sha256, final_contract_identity = _load_contract_bound()
            if (
                final_contract != contract
                or final_contract_sha256 != contract_sha256
                or final_contract_identity != contract_identity
            ):
                raise GateError("CONTRACT_DRIFT", "contract identity or bytes changed during execution")
        except BaseException as exc:
            caught = GateError(
                "CONTRACT_DRIFT",
                f"contract could not be re-bound after execution:{type(exc).__name__}",
            )
        common = {
            "base_commit": contract["base_commit"],
            "contract_sha256": contract_sha256,
            "completed_stages": completed_stages,
            "server_log_bindings": {"stdout": stdout_binding, "stderr": stderr_binding},
            "cleanup": cleanup,
            "body_free_http_request_types_allowed": list(
                BODY_FREE_HTTP_REQUEST_TYPES_ALLOWED
            ),
            "protected_packet_bodies_opened": 0,
            "protected_prompt_bodies_opened": 0,
            "tokenize_requests": 0,
            "completion_requests": 0,
            "generation_invocations": 0,
            "official_evaluator_invoked": False,
            "official_outcomes_opened": 0,
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        if caught is None:
            receipt = {
                "schema_version": SCHEMA,
                "authority": "BODY_FREE_CANONICAL_MAP_DISCRIMINATOR_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
                "status": "PASS_BACKEND_CANONICAL_MAP_DISCRIMINATOR",
                **common,
                **live,
            }
            _persist_final_receipt(output_root, root_fd, SUCCESS_NAME, receipt)
            return 0, receipt
        error = _as_gate_error(caught)
        detail = f"{type(error).__name__}:{error}".encode("utf-8", errors="replace")
        receipt = {
            "schema_version": CANNOT_SCHEMA,
            "authority": "BODY_FREE_CANONICAL_MAP_DISCRIMINATOR_FAILURE_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
            "status": "CANNOT_CHECK_BACKEND_CANONICAL_MAP_DISCRIMINATOR",
            **common,
            "failure_code": error.code,
            "failure_detail_sha256": sha256_bytes(detail),
        }
        _persist_final_receipt(output_root, root_fd, CANNOT_NAME, receipt)
        return 1, receipt
    finally:
        os.close(root_fd)


def parse_cli(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the body-free canonical-map discriminator")
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    if len(argv) != 2 or argv[0] != "--output-root":
        raise GateError("ARGV_INVALID", "only exact --output-root argv is accepted")
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
            print(SUCCESS_TERMINAL)
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
