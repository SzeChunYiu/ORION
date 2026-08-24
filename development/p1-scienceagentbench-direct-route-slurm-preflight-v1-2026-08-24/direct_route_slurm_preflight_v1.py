#!/usr/bin/env python3
"""Additive SLURM preflight/supervisor for the frozen P1 direct route.

The ``supervise`` entrypoint starts and attests one exact local llama-server,
captures the wrapper-donated scheduler semantics directly, and calls the
unchanged adapter API.  The byte-bound upstream wrapper is never invoked.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import http.client
import importlib.util
import json
import os
import re
import signal
import socket
import stat
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
CONTRACT_PATH = ROOT / "DIRECT_ROUTE_SLURM_PREFLIGHT_CONTRACT_V1.json"
LAUNCHER_PATH = ROOT / "run_direct_route_slurm_preflight_v1.sh"
DIRECT_LANE = REPO_ROOT / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24"
ADAPTER_LANE = REPO_ROOT / "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24"
DIRECT_DRIVER_PATH = DIRECT_LANE / "direct_route_generation_driver_v1.py"
DIRECT_CONTRACT_PATH = DIRECT_LANE / "DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
DIRECT_PROMPT_PATH = DIRECT_LANE / "DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
ADAPTER_PATH = ADAPTER_LANE / "sab_lunarc_generation_adapter_v1.py"

EXPECTED_UPSTREAM = {
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py": "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json": "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json": "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py": "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/run_lunarc_attempt_v1.sh": "1d4655350c1a037cd4e51ee11e15e21491c5bfd7cea125948beb2e152c73b582",
}

SHA256_CHARS = frozenset("0123456789abcdef")
PROXY_KEYS = (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"
)
WRAPPER_BINDING_ROLE = "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED"


class PreflightError(RuntimeError):
    """A preflight or bridge invariant failed closed."""


class AttemptDeadlineExceeded(PreflightError):
    """The one first-to-final monotonic-raw attempt deadline expired."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path | str) -> str:
    candidate = Path(path)
    try:
        with candidate.open("rb") as handle:
            digest = hashlib.sha256()
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    return digest.hexdigest()
                digest.update(chunk)
    except OSError as exc:
        raise PreflightError(f"required file cannot be hashed: {candidate}") from exc


def _read_fd_bytes(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, allow_nan=False, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PreflightError("value is not strict canonical JSON") from exc


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PreflightError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_reject_duplicates, parse_constant=lambda x: (_ for _ in ()).throw(PreflightError(f"nonfinite JSON member: {x}")))
    except PreflightError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PreflightError(f"{label} must be a JSON object")
    return value


def read_json(path: Path | str, label: str) -> tuple[bytes, dict[str, Any]]:
    candidate = validate_absolute_regular(path, label)
    try:
        raw = candidate.read_bytes()
    except OSError as exc:
        raise PreflightError(f"{label} cannot be read") from exc
    return raw, strict_json_bytes(raw, label)


def validate_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in SHA256_CHARS for c in value):
        raise PreflightError(f"{label} must be lowercase SHA-256")
    return value


def validate_absolute_regular(path: Path | str, label: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise PreflightError(f"{label} must be absolute")
    try:
        link_info = candidate.lstat()
        target_info = candidate.stat()
    except OSError as exc:
        raise PreflightError(f"{label} is missing or unreadable: {candidate}") from exc
    if stat.S_ISLNK(link_info.st_mode):
        raise PreflightError(f"{label} cannot be a symlink")
    if not stat.S_ISREG(target_info.st_mode):
        raise PreflightError(f"{label} must be a regular file")
    return candidate


def require_unique_files(paths: Mapping[str, Path]) -> None:
    identities: dict[tuple[int, int], str] = {}
    lexical: dict[str, str] = {}
    resolved: dict[str, str] = {}
    for label, path in paths.items():
        candidate = validate_absolute_regular(path, label)
        lexical_key = os.path.normpath(os.fspath(candidate)).casefold()
        resolved_key = os.fspath(candidate.resolve(strict=True)).casefold()
        info = candidate.stat()
        identity = (info.st_dev, info.st_ino)
        for table, key, kind in (
            (lexical, lexical_key, "lexical/case-fold"),
            (resolved, resolved_key, "resolved/case-fold"),
        ):
            if key in table:
                raise PreflightError(f"runtime inputs alias by {kind}: {table[key]} and {label}")
            table[key] = label
        if identity in identities:
            raise PreflightError(f"runtime inputs alias by device/inode: {identities[identity]} and {label}")
        identities[identity] = label


def _directory_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _open_verified_directory(path: Path, label: str) -> int:
    """Open an absolute directory one component at a time without symlinks.

    Every descendant lookup is relative to the previously verified descriptor,
    so renaming or replacing a pathname component cannot redirect a later
    operation.  /dev/fd/N is accepted only as an explicit inherited directory
    capability and all components beneath it still use no-follow openat calls.
    """
    candidate = Path(path)
    if not candidate.is_absolute():
        raise PreflightError(f"{label} must be absolute")
    parts = candidate.parts
    if any(part in {".", "..", ""} for part in parts[1:]):
        raise PreflightError(f"{label} contains a noncanonical path component")
    flags = _directory_open_flags()
    current_fd: int | None = None
    remaining = parts[1:]
    try:
        if len(parts) >= 4 and parts[1:3] == ("dev", "fd") and parts[3].isdigit():
            current_fd = os.dup(int(parts[3]))
            info = os.fstat(current_fd)
            if not stat.S_ISDIR(info.st_mode):
                raise PreflightError(f"{label} /dev/fd capability is not a directory")
            remaining = parts[4:]
        else:
            current_fd = os.open("/", flags)
        for component in remaining:
            next_fd = os.open(component, flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
            if not stat.S_ISDIR(os.fstat(current_fd).st_mode):
                raise PreflightError(f"{label} component is not a directory: {component}")
        return current_fd
    except PreflightError:
        if current_fd is not None:
            os.close(current_fd)
        raise
    except OSError as exc:
        if current_fd is not None:
            os.close(current_fd)
        raise PreflightError(f"{label} cannot be opened without symlink traversal: {candidate}") from exc


def _create_new_directory(path: Path, mode: int = 0o700, *, parent_fd: int | None = None) -> int:
    """Create and return a pinned new directory using mkdirat/openat semantics."""
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.name in {"", ".", ".."}:
        raise PreflightError("new directory path must be absolute and canonical")
    owned_parent_fd = os.dup(parent_fd) if parent_fd is not None else _open_verified_directory(
        candidate.parent, "new directory parent"
    )
    created = False
    try:
        os.mkdir(candidate.name, mode, dir_fd=owned_parent_fd)
        created = True
        directory_fd = os.open(candidate.name, _directory_open_flags(), dir_fd=owned_parent_fd)
        entry = os.stat(candidate.name, dir_fd=owned_parent_fd, follow_symlinks=False)
        opened = os.fstat(directory_fd)
        if not stat.S_ISDIR(entry.st_mode) or (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
            os.close(directory_fd)
            raise PreflightError("new directory entry identity changed during creation")
        return directory_fd
    except PreflightError:
        if created:
            try:
                os.rmdir(candidate.name, dir_fd=owned_parent_fd)
            except OSError:
                pass
        raise
    except OSError as exc:
        if created:
            try:
                os.rmdir(candidate.name, dir_fd=owned_parent_fd)
            except OSError:
                pass
        raise PreflightError(f"directory must be new and exclusively creatable: {candidate}") from exc
    finally:
        os.close(owned_parent_fd)


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PreflightError(f"cannot load frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise PreflightError(f"frozen module import failed: {path}") from exc
    return module


def load_contract() -> dict[str, Any]:
    _, contract = read_json(CONTRACT_PATH, "SLURM preflight contract")
    if contract.get("schema_version") != "orion.p1.scienceagentbench.direct-route-slurm-preflight.v1":
        raise PreflightError("SLURM preflight contract schema mismatch")
    return contract


def validate_frozen_upstream(contract: Mapping[str, Any]) -> None:
    if contract.get("wrapper_execution_allowed") is not False:
        raise PreflightError("unchanged wrapper execution must be forbidden")
    if contract.get("wrapper_binding_role") != WRAPPER_BINDING_ROLE:
        raise PreflightError("unchanged wrapper must be bound only as a non-invoked semantics donor")
    bindings = contract.get("upstream_bindings")
    if not isinstance(bindings, list):
        raise PreflightError("upstream_bindings must be a list")
    declared: dict[str, str] = {}
    for item in bindings:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise PreflightError("upstream binding must contain exact path and sha256")
        declared[item["path"]] = item["sha256"]
    if declared != EXPECTED_UPSTREAM:
        raise PreflightError("merged PR #1168 or unchanged adapter/wrapper binding mismatch")
    for relative, expected in EXPECTED_UPSTREAM.items():
        if sha256_file(REPO_ROOT / relative) != expected:
            raise PreflightError(f"frozen upstream SHA-256 drift: {relative}")


def build_server_argv(server: Path, model: Path) -> list[str]:
    return [
        os.fspath(server),
        "--model", os.fspath(model),
        "--host", "127.0.0.1",
        "--port", "8080",
        "--ctx-size", "32768",
        "--parallel", "1",
        "--no-cont-batching",
        "--threads", "8",
        "--threads-batch", "8",
        "--batch-size", "512",
        "--ubatch-size", "512",
        "--cache-type-k", "f16",
        "--cache-type-v", "f16",
        "--flash-attn", "on",
        "--n-gpu-layers", "all",
        "--no-context-shift",
        "--metrics",
        "--slots",
    ]


def build_server_environment(backend: Path, source: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if source is None else source)
    for key in PROXY_KEYS:
        env[key] = ""
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["no_proxy"] = "127.0.0.1,localhost"
    env["GGML_BACKEND_PATH"] = os.fspath(backend)
    library_root = os.fspath(backend.parent)
    parent_root = os.fspath(backend.parent.parent)
    previous = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = ":".join(x for x in (parent_root, library_root, previous) if x)
    return env


def stage_runtime_snapshots(
    sources: Mapping[str, Path], destination: Path, *, destination_parent_fd: int | None = None
) -> dict[str, Path]:
    required = {"plan", "owner", "runtime", "masked", "recovered"}
    if set(sources) != required or not destination.is_absolute():
        raise PreflightError("runtime snapshots require exact sources and an absolute destination")
    normalized = {name: validate_absolute_regular(path, f"snapshot source {name}") for name, path in sources.items()}
    require_unique_files(normalized)
    destination_fd = _create_new_directory(destination, 0o700, parent_fd=destination_parent_fd)
    names = {
        "plan": "RUN_PLAN.json",
        "owner": "OWNER_SELECTION.json",
        "runtime": "RUNTIME_BINDING.json",
        "masked": "MASKED_PACKET.json",
        "recovered": "RECOVERED_PACKET.json",
    }
    snapshots: dict[str, Path] = {}
    try:
        for name in ("plan", "owner", "runtime", "masked", "recovered"):
            source = normalized[name]
            target_name = names[name]
            target = destination / target_name
            source_flags = os.O_RDONLY
            target_flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                source_flags |= os.O_NOFOLLOW
                target_flags |= os.O_NOFOLLOW
            source_fd = os.open(source, source_flags)
            try:
                target_fd = os.open(target_name, target_flags, 0o600, dir_fd=destination_fd)
                try:
                    while True:
                        chunk = os.read(source_fd, 1024 * 1024)
                        if not chunk:
                            break
                        view = memoryview(chunk)
                        while view:
                            count = os.write(target_fd, view)
                            if count <= 0:
                                raise PreflightError("runtime snapshot write made no progress")
                            view = view[count:]
                    os.fsync(target_fd)
                    target_info = os.fstat(target_fd)
                    target_payload = _read_fd_bytes(target_fd)
                    entry_info = os.stat(target_name, dir_fd=destination_fd, follow_symlinks=False)
                    if (entry_info.st_dev, entry_info.st_ino) != (target_info.st_dev, target_info.st_ino):
                        raise PreflightError(f"runtime snapshot entry identity changed: {name}")
                finally:
                    os.close(target_fd)
            finally:
                os.close(source_fd)
            if sha256_bytes(target_payload) != sha256_file(source):
                raise PreflightError(f"runtime snapshot differs from source: {name}")
            snapshots[name] = target
    except Exception:
        for name in snapshots:
            try:
                os.unlink(names[name], dir_fd=destination_fd)
            except OSError:
                pass
        raise
    finally:
        os.close(destination_fd)
    return snapshots


def build_runtime_stage(
    contract: Mapping[str, Any],
    paths: Mapping[str, Path],
    expected_sha256: Mapping[str, str],
    task_id: str,
    arm_id: str,
    attempt: int,
) -> dict[str, Any]:
    required = {"plan", "owner", "runtime", "masked", "recovered", "model", "server", "backend", "launcher"}
    if set(paths) != required or set(expected_sha256) != required:
        raise PreflightError("runtime stage requires exact path and hash fields")
    if not isinstance(task_id, str) or not task_id:
        raise PreflightError("task_id must be nonempty text")
    if arm_id not in {"RR", "OS", "NR"}:
        raise PreflightError("arm_id must be RR, OS, or NR")
    if isinstance(attempt, bool) or attempt not in (1, 2, 3):
        raise PreflightError("attempt must be 1, 2, or 3")
    normalized = {name: validate_absolute_regular(path, f"runtime {name}") for name, path in paths.items()}
    require_unique_files(normalized)
    observed: dict[str, str] = {}
    for name, path in normalized.items():
        expected = validate_sha256(expected_sha256[name], f"expected {name} sha256")
        actual = sha256_file(path)
        if actual != expected:
            raise PreflightError(f"runtime {name} SHA-256 mismatch")
        observed[name] = actual
    direct_driver_sha = EXPECTED_UPSTREAM[
        "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py"
    ]
    preflight_bridge_sha = sha256_file(Path(__file__).resolve())
    return {
        "schema_version": "orion.p1.scienceagentbench.direct-route-slurm-runtime-stage.v1",
        "authority": "RUNTIME_PREFLIGHT_METADATA_ONLY__NO_EXECUTION_OR_SCIENTIFIC_AUTHORITY",
        "status": "HASHED_RUNTIME_INPUT_STAGED__PROCESS_ATTESTATION_PENDING",
        "tuple_identity": {"task_id": task_id, "arm_id": arm_id, "attempt": attempt},
        "source_paths": {name: os.fspath(path) for name, path in normalized.items()},
        "source_sha256": observed,
        "runtime_observed_sha256": {
            "model": observed["model"],
            "llama_server": observed["server"],
            "cuda_backend": observed["backend"],
            "launcher": observed["launcher"],
            "preflight_bridge": preflight_bridge_sha,
        },
        "run_plan_binding_extension": {
            "run_plan_sha256": observed["plan"],
            "direct_driver_sha256": direct_driver_sha,
            "direct_contract_sha256": EXPECTED_UPSTREAM[
                "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
            ],
            "direct_prompt_bundle_sha256": EXPECTED_UPSTREAM[
                "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
            ],
            "adapter_sha256": EXPECTED_UPSTREAM[
                "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py"
            ],
            "upstream_wrapper_sha256": EXPECTED_UPSTREAM[
                "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/run_lunarc_attempt_v1.sh"
            ],
            "upstream_wrapper_execution_allowed": False,
            "upstream_wrapper_binding_role": WRAPPER_BINDING_ROLE,
            "preflight_bridge_sha256": preflight_bridge_sha,
            "prompt_binding_mode": "PROSPECTIVE_STATIC_HASH_OR_DYNAMIC_SEALED_RR_STATE_RULE",
        },
        "server_argv": build_server_argv(normalized["server"], normalized["model"]),
        "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }


# Kept as a positional convenience for the hostile validator and external auditors.
def build_runtime_stage_for_test(
    contract: Mapping[str, Any],
    paths: Mapping[str, Path],
    expected_sha256: Mapping[str, str],
    task_id: str,
    arm_id: str,
    attempt: int,
) -> dict[str, Any]:
    return build_runtime_stage(contract, paths, expected_sha256, task_id, arm_id, attempt)


def add_prompt_commitments(stage: dict[str, Any]) -> dict[str, Any]:
    direct = load_module(DIRECT_DRIVER_PATH, "p1_direct_route_for_preflight_stage")
    adapter = load_module(ADAPTER_PATH, "p1_generation_adapter_for_preflight_stage")
    _, plan = read_json(stage["source_paths"]["plan"], "run plan")
    _, owner = read_json(stage["source_paths"]["owner"], "owner selection")
    _, runtime = read_json(stage["source_paths"]["runtime"], "runtime binding")
    _, masked = read_json(stage["source_paths"]["masked"], "masked packet")
    _, recovered = read_json(stage["source_paths"]["recovered"], "recovered packet")
    _, frozen = read_json(DIRECT_CONTRACT_PATH, "direct-route contract")
    _, prompts = read_json(DIRECT_PROMPT_PATH, "direct-route prompt bundle")
    try:
        direct.validate_packet_contract(frozen, prompts)
        direct.validate_runtime_binding(runtime, frozen)
        direct.validate_owner_selection(owner)
        direct.bind_runner_v2_plan(plan, frozen, prompts, owner, adapter)
    except Exception as exc:
        raise PreflightError(f"direct-route staged input invariant failed: {exc}") from exc
    identity = stage["tuple_identity"]
    arm = identity["arm_id"]
    attempt = identity["attempt"]
    by_phase: dict[str, dict[str, Any]] = {}
    if arm == "RR":
        rendered = direct._render_phase0(prompts, "RR_PHASE0", attempt, masked)
        by_phase["RR_PHASE0"] = {
            "status": "PROSPECTIVE_EXACT",
            "rendered_prompt_sha256": sha256_bytes(rendered.encode("utf-8")),
        }
        by_phase["RR_PHASE1"] = {
            "status": "DYNAMIC_SEALED_RR_STATE_RULE",
            "template_text_sha256": sha256_bytes(prompts["templates"]["RR_PHASE1"]["text"].encode("utf-8")),
            "recovered_packet_canonical_sha256": canonical_hash(recovered),
            "state_source": "RR_PHASE0_STRICT_PARSED_CANONICAL_STATE_AND_SHA256",
        }
    elif arm == "OS":
        rendered = direct._render_phase1_without_state(prompts, "OS_PHASE1", attempt, recovered)
        by_phase["OS_PHASE1"] = {
            "status": "PROSPECTIVE_EXACT",
            "rendered_prompt_sha256": sha256_bytes(rendered.encode("utf-8")),
        }
    else:
        first = direct._render_phase0(prompts, "NR_PHASE0", attempt, masked)
        final = direct._render_phase1_without_state(prompts, "NR_PHASE1", attempt, recovered)
        by_phase["NR_PHASE0"] = {"status": "PROSPECTIVE_EXACT", "rendered_prompt_sha256": sha256_bytes(first.encode("utf-8"))}
        by_phase["NR_PHASE1"] = {"status": "PROSPECTIVE_EXACT", "rendered_prompt_sha256": sha256_bytes(final.encode("utf-8"))}
    result = copy.deepcopy(stage)
    result["prompt_commitments_by_phase"] = by_phase
    result["run_plan_binding_extension_sha256"] = canonical_hash(result["run_plan_binding_extension"])
    return result


def validate_staged_files_unchanged(stage: Mapping[str, Any]) -> None:
    if stage.get("schema_version") != "orion.p1.scienceagentbench.direct-route-slurm-runtime-stage.v1":
        raise PreflightError("runtime stage schema mismatch")
    paths = stage.get("source_paths")
    hashes = stage.get("source_sha256")
    if not isinstance(paths, dict) or not isinstance(hashes, dict) or set(paths) != set(hashes):
        raise PreflightError("runtime stage source path/hash map mismatch")
    normalized = {name: validate_absolute_regular(Path(path), f"staged {name}") for name, path in paths.items()}
    require_unique_files(normalized)
    for name, path in normalized.items():
        expected = validate_sha256(hashes[name], f"staged {name} sha256")
        if sha256_file(path) != expected:
            raise PreflightError(f"staged {name} changed after runtime staging")
    if stage.get("server_argv") != build_server_argv(normalized["server"], normalized["model"]):
        raise PreflightError("runtime stage server argv drift")
    extension = stage.get("run_plan_binding_extension")
    if not isinstance(extension, dict) or stage.get("run_plan_binding_extension_sha256") != canonical_hash(extension):
        raise PreflightError("runtime stage run-plan binding extension drift")
    current_bridge_sha = sha256_file(Path(__file__).resolve())
    if (
        stage.get("runtime_observed_sha256", {}).get("preflight_bridge") != current_bridge_sha
        or extension.get("preflight_bridge_sha256") != current_bridge_sha
    ):
        raise PreflightError("preflight bridge source changed after runtime staging")


class RawDeadline:
    """One raw-clock deadline shared by every phase in an attempt."""

    def __init__(self, cap_ns: int, raw_clock: Callable[[], int]) -> None:
        if isinstance(cap_ns, bool) or not isinstance(cap_ns, int) or cap_ns <= 0:
            raise PreflightError("deadline cap_ns must be a positive integer")
        if not callable(raw_clock):
            raise PreflightError("raw deadline clock must be callable")
        self.cap_ns = cap_ns
        self.raw_clock = raw_clock
        self.start_ns: int | None = None
        self.deadline_ns: int | None = None
        self.expired = False

    def _read(self) -> int:
        value = self.raw_clock()
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PreflightError("raw deadline clock returned an invalid value")
        return value

    def capture_clock(self) -> int:
        value = self._read()
        if self.start_ns is None:
            self.start_ns = value
            self.deadline_ns = value + self.cap_ns
        return value

    def remaining_seconds(self) -> float:
        if self.deadline_ns is None:
            raise PreflightError("attempt deadline is not initialized by the adapter start boundary")
        now = self._read()
        remaining_ns = self.deadline_ns - now
        if remaining_ns <= 0:
            self.expired = True
            raise AttemptDeadlineExceeded("one cross-phase CLOCK_MONOTONIC_RAW deadline expired")
        return remaining_ns / 1_000_000_000

    def require_not_expired(self) -> None:
        self.remaining_seconds()


def capture_failure_sidecar(capture: Any, exc: BaseException) -> dict[str, Any]:
    code = "ATTEMPT_DEADLINE_EXCEEDED" if isinstance(exc, AttemptDeadlineExceeded) else "DIRECT_ROUTE_EXECUTION_FAILED"
    detail = f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
    try:
        sidecar = capture.cannot_check_sidecar(code, detail)
    except Exception as sidecar_exc:
        raise PreflightError("adapter capture could not emit its typed CANNOT_CHECK sidecar") from sidecar_exc
    if sidecar.get("status") != "CANNOT_CHECK" or sidecar.get("failure_code") != code:
        raise PreflightError("adapter capture returned an invalid CANNOT_CHECK sidecar")
    return sidecar


def attest_process_identity(
    pid: int,
    server: Path,
    expected_argv: Sequence[str],
    backend: str,
    *,
    proc_root: Path = Path("/proc"),
) -> dict[str, Any]:
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise PreflightError("server pid must be positive")
    server = validate_absolute_regular(server, "llama-server executable")
    backend_path = validate_absolute_regular(Path(backend), "CUDA backend")
    try:
        model_index = list(expected_argv).index("--model") + 1
        model_path = validate_absolute_regular(Path(expected_argv[model_index]), "model GGUF")
    except (ValueError, IndexError) as exc:
        raise PreflightError("live server argv lacks exactly bound model path") from exc
    root = proc_root / str(pid)
    try:
        exe_link = root / "exe"
        exe_target = exe_link.resolve(strict=True)
        expected_target = server.resolve(strict=True)
        exe_info = exe_link.stat()
        server_info = server.stat()
        cmdline_raw = (root / "cmdline").read_bytes()
        environ_raw = (root / "environ").read_bytes()
        maps_text = (root / "maps").read_text()
    except OSError as exc:
        raise PreflightError("live server process cannot be inspected") from exc
    if exe_target != expected_target or (exe_info.st_dev, exe_info.st_ino) != (server_info.st_dev, server_info.st_ino):
        raise PreflightError("live server executable identity differs from staged llama-server")
    observed_argv = [item.decode("utf-8") for item in cmdline_raw.rstrip(b"\0").split(b"\0") if item]
    if observed_argv != list(expected_argv):
        raise PreflightError("live server command line differs from exact frozen argv")
    environ: dict[str, str] = {}
    for item in environ_raw.rstrip(b"\0").split(b"\0"):
        if not item or b"=" not in item:
            continue
        key, value = item.split(b"=", 1)
        environ[key.decode("utf-8", errors="strict")] = value.decode("utf-8", errors="strict")
    if environ.get("GGML_BACKEND_PATH") != backend:
        raise PreflightError("live server GGML_BACKEND_PATH differs from staged CUDA backend")
    for key in PROXY_KEYS:
        if environ.get(key, "") != "":
            raise PreflightError("live server proxy environment must be empty")
    map_fields = [line.split(maxsplit=5) for line in maps_text.splitlines()]

    def require_mapped(candidate: Path, label: str) -> None:
        info = candidate.stat()
        device = f"{os.major(info.st_dev):02x}:{os.minor(info.st_dev):02x}"
        if not any(
            len(fields) == 6
            and fields[5] == os.fspath(candidate)
            and fields[3].casefold() == device.casefold()
            and fields[4] == str(info.st_ino)
            for fields in map_fields
        ):
            raise PreflightError(f"staged {label} is not mapped into the live server process")

    require_mapped(backend_path, "CUDA backend")
    require_mapped(model_path, "model GGUF")
    return {
        "pid": pid,
        "executable_path": os.fspath(expected_target),
        "executable_sha256": sha256_file(exe_link),
        "executable_device": str(exe_info.st_dev),
        "executable_inode": str(exe_info.st_ino),
        "argv": list(expected_argv),
        "cmdline_sha256": sha256_bytes(cmdline_raw),
        "ggml_backend_path": backend,
        "cuda_backend_mapped_path": os.fspath(backend_path),
        "cuda_backend_sha256": sha256_file(backend_path),
        "model_mapped_path": os.fspath(model_path),
        "model_sha256": sha256_file(model_path),
        "proxy_environment_empty": True,
    }


def attest_loopback_listener(pid: int, proc_root: Path = Path("/proc")) -> dict[str, Any]:
    socket_inodes: set[str] = set()
    try:
        for fd in (proc_root / str(pid) / "fd").iterdir():
            try:
                target = os.readlink(fd)
            except OSError:
                continue
            if target.startswith("socket:[") and target.endswith("]"):
                socket_inodes.add(target[8:-1])
        lines = (proc_root / "net/tcp").read_text().splitlines()[1:]
    except OSError as exc:
        raise PreflightError("live server listener cannot be inspected") from exc
    matches: list[str] = []
    for line in lines:
        fields = line.split()
        if len(fields) < 10:
            continue
        local, state_code, inode = fields[1], fields[3], fields[9]
        if local == "0100007F:1F90" and state_code == "0A" and inode in socket_inodes:
            matches.append(inode)
    if len(matches) != 1:
        raise PreflightError("exactly one server-owned 127.0.0.1:8080 listener is required")
    return {"listen_host": "127.0.0.1", "listen_port": 8080, "socket_inode": matches[0]}


def _http_get_json(path: str, timeout: float = 2.0) -> Any:
    connection = http.client.HTTPConnection("127.0.0.1", 8080, timeout=timeout)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        raw = response.read()
    finally:
        connection.close()
    if response.status != 200:
        raise PreflightError(f"loopback readiness endpoint returned HTTP {response.status}: {path}")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicates)
    except Exception as exc:
        raise PreflightError(f"loopback readiness endpoint returned invalid JSON: {path}") from exc


def wait_for_exact_server(process: subprocess.Popen[Any], timeout_seconds: float = 600.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error: BaseException | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise PreflightError("llama-server exited before readiness")
        try:
            health = _http_get_json("/health")
            slots = _http_get_json("/slots")
            if not isinstance(slots, list) or len(slots) != 1:
                raise PreflightError("live /slots response does not expose exactly one slot")
            return {"health_sha256": canonical_hash(health), "slots_sha256": canonical_hash(slots), "slot_count": 1}
        except (OSError, PreflightError) as exc:
            last_error = exc
            time.sleep(0.25)
    raise PreflightError("llama-server readiness deadline expired") from last_error


def _write_new_bytes(
    path: Path, payload: bytes, *, parent_fd: int | None = None
) -> tuple[str, tuple[int, int]]:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.name in {"", ".", ".."}:
        raise PreflightError("output path must be absolute")
    if not isinstance(payload, bytes):
        raise PreflightError("output payload must be bytes")
    payload_sha256 = sha256_bytes(payload)
    owned_parent_fd = os.dup(parent_fd) if parent_fd is not None else _open_verified_directory(
        candidate.parent, "output parent"
    )
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd: int | None = None
    identity: tuple[int, int] | None = None
    try:
        fd = os.open(candidate.name, flags, 0o600, dir_fd=owned_parent_fd)
        view = memoryview(payload)
        while view:
            count = os.write(fd, view)
            if count <= 0:
                raise PreflightError("output write made no progress")
            view = view[count:]
        os.fsync(fd)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise PreflightError("output descriptor is not a regular file")
        identity = (info.st_dev, info.st_ino)
        if _read_fd_bytes(fd) != payload:
            raise PreflightError("output descriptor reread differs from written bytes")
        entry = os.stat(candidate.name, dir_fd=owned_parent_fd, follow_symlinks=False)
        if not stat.S_ISREG(entry.st_mode) or (entry.st_dev, entry.st_ino) != identity:
            raise PreflightError("output directory entry identity changed during write")
        return payload_sha256, identity
    except OSError as exc:
        if fd is not None:
            try:
                entry = os.stat(candidate.name, dir_fd=owned_parent_fd, follow_symlinks=False)
                opened = os.fstat(fd)
                if (entry.st_dev, entry.st_ino) == (opened.st_dev, opened.st_ino):
                    os.unlink(candidate.name, dir_fd=owned_parent_fd)
            except OSError:
                pass
        raise PreflightError(f"output must be new and exclusively creatable: {candidate}") from exc
    except Exception:
        if fd is not None:
            try:
                entry = os.stat(candidate.name, dir_fd=owned_parent_fd, follow_symlinks=False)
                opened = os.fstat(fd)
                if (entry.st_dev, entry.st_ino) == (opened.st_dev, opened.st_ino):
                    os.unlink(candidate.name, dir_fd=owned_parent_fd)
            except OSError:
                pass
        raise
    finally:
        if fd is not None:
            os.close(fd)
        os.close(owned_parent_fd)


def _write_new_json(
    path: Path, value: Any, *, parent_fd: int | None = None
) -> tuple[str, tuple[int, int]]:
    return _write_new_bytes(
        path,
        canonical_json_bytes(value) + b"\n",
        parent_fd=parent_fd,
    )


def _rollback_output(
    path: Path,
    expected_sha256: str,
    identity: tuple[int, int],
    *,
    parent_fd: int | None = None,
) -> bool:
    candidate = Path(path)
    owned_parent_fd: int | None = None
    fd: int | None = None
    try:
        owned_parent_fd = os.dup(parent_fd) if parent_fd is not None else _open_verified_directory(
            candidate.parent, "rollback parent"
        )
        flags = os.O_RDONLY | (os.O_NOFOLLOW if hasattr(os, "O_NOFOLLOW") else 0)
        fd = os.open(candidate.name, flags, dir_fd=owned_parent_fd)
        info = os.fstat(fd)
        entry = os.stat(candidate.name, dir_fd=owned_parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(info.st_mode)
            or (info.st_dev, info.st_ino) != identity
            or (entry.st_dev, entry.st_ino) != identity
        ):
            return False
        if sha256_bytes(_read_fd_bytes(fd)) != expected_sha256:
            return False
        os.unlink(candidate.name, dir_fd=owned_parent_fd)
        return True
    except (OSError, PreflightError):
        return False
    finally:
        if fd is not None:
            os.close(fd)
        if owned_parent_fd is not None:
            os.close(owned_parent_fd)


def _require_absent_entries(parent_fd: int, names: Sequence[str]) -> None:
    info = os.fstat(parent_fd)
    if not stat.S_ISDIR(info.st_mode):
        raise PreflightError("output directory capability is not a directory")
    for name in names:
        if Path(name).name != name or name in {"", ".", ".."}:
            raise PreflightError("output entry name must be one canonical component")
        try:
            os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise PreflightError(f"output entry cannot be checked through pinned directory: {name}") from exc
        raise PreflightError(f"bridge output already exists: {name}")


def capture_slurm_identity(
    output_dir: Path,
    output_dir_fd: int,
    *,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Capture the byte-bound wrapper scheduler semantics without invoking it."""

    if not output_dir.is_absolute():
        raise PreflightError("SLURM capture output directory must be absolute")
    if not stat.S_ISDIR(os.fstat(output_dir_fd).st_mode):
        raise PreflightError("SLURM capture output capability is not a directory")
    env = dict(os.environ if environment is None else environment)
    job_id = env.get("SLURM_JOB_ID")
    cluster = env.get("SLURM_CLUSTER_NAME")
    if not isinstance(job_id, str) or re.fullmatch(r"[1-9][0-9]*", job_id) is None:
        raise PreflightError("SLURM_JOB_ID must match the unchanged wrapper grammar")
    if not isinstance(cluster, str) or re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)*", cluster) is None:
        raise PreflightError("SLURM_CLUSTER_NAME must match the unchanged wrapper grammar")
    array_job = env.get("SLURM_ARRAY_JOB_ID", "")
    array_task = env.get("SLURM_ARRAY_TASK_ID", "")
    if not isinstance(array_job, str) or not isinstance(array_task, str):
        raise PreflightError("SLURM array identity must be textual")
    if bool(array_job) != bool(array_task):
        raise PreflightError("SLURM array job/task identity must be jointly present or absent")
    if array_job:
        if re.fullmatch(r"[1-9][0-9]*", array_job) is None:
            raise PreflightError("SLURM_ARRAY_JOB_ID must match the unchanged wrapper grammar")
        if re.fullmatch(r"0|[1-9][0-9]*", array_task) is None:
            raise PreflightError("SLURM_ARRAY_TASK_ID must match the unchanged wrapper grammar")
        canonical_job_id = f"{array_job}_{array_task}"
    else:
        canonical_job_id = job_id
        array_job = None
        array_task = None

    command = ["scontrol", "show", "job", "-dd", job_id]
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
    except OSError as exc:
        raise PreflightError("exact scontrol capture command could not be executed") from exc
    if completed.returncode != 0:
        detail_sha = sha256_bytes(completed.stderr)
        raise PreflightError(
            f"exact scontrol capture command returned nonzero; stderr_sha256={detail_sha}"
        )
    if not completed.stdout:
        raise PreflightError("exact scontrol capture command returned an empty snapshot")

    snapshot_path = output_dir / "SCONTROL_IN_JOB_V1.txt"
    identity_path = output_dir / "SLURM_IDENTITY_AND_SNAPSHOT_V1.json"
    snapshot_sha, snapshot_identity = _write_new_bytes(
        snapshot_path,
        completed.stdout,
        parent_fd=output_dir_fd,
    )
    identity = {
        "slurm_job_identity": {
            "cluster": cluster,
            "job_id": canonical_job_id,
            "array_job_id": array_job,
            "array_task_id": array_task,
        },
        "slurm_in_job_snapshot_sha256": snapshot_sha,
        "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
        "environment_only_exclusivity_claimed": False,
    }
    try:
        _write_new_json(identity_path, identity, parent_fd=output_dir_fd)
    except Exception:
        _rollback_output(
            snapshot_path,
            snapshot_sha,
            snapshot_identity,
            parent_fd=output_dir_fd,
        )
        raise
    return identity


def probe_descendant_directory_capability(directory_fd: int, relative_path: str) -> dict[str, Any]:
    """Audit-only portability probe; production execution never depends on it."""

    relative = Path(relative_path)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise PreflightError("descendant capability probe path must be canonical and relative")
    if not stat.S_ISDIR(os.fstat(directory_fd).st_mode):
        raise PreflightError("descendant capability probe requires a directory descriptor")
    unsupported = {
        "status": "CANNOT_CHECK_PROC_SELF_FD_DESCENDANT_TRAVERSAL_UNSUPPORTED",
        "subprocess_traversal_proved": False,
        "production_dependency": False,
    }
    proc_fd_root = Path("/proc/self/fd")
    if not proc_fd_root.is_dir():
        return unsupported
    capability_path = proc_fd_root / str(directory_fd) / relative
    probe_code = (
        "import pathlib,sys\n"
        "payload=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8').strip()\n"
        "print(payload)\n"
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-c", probe_code, os.fspath(capability_path)],
            pass_fds=(directory_fd,),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except (OSError, ValueError):
        return unsupported
    if completed.returncode != 0 or not completed.stdout.strip():
        return unsupported
    return {
        "status": "PASS_PROC_SELF_FD_DESCENDANT_TRAVERSAL",
        "subprocess_traversal_proved": True,
        "observed_marker": completed.stdout.strip(),
        "production_dependency": False,
    }


class AdapterFacade:
    def __init__(self, module: ModuleType) -> None:
        self.module = module
        self.capture: Any | None = None

    def GenerationAttemptCapture(self, **kwargs: Any) -> Any:  # noqa: N802 - upstream API
        if self.capture is not None:
            raise PreflightError("bridge permits exactly one adapter capture")
        self.capture = self.module.GenerationAttemptCapture(**kwargs)
        return self.capture

    def __getattr__(self, name: str) -> Any:
        return getattr(self.module, name)


class DeadlineLoopbackClient:
    def __init__(
        self,
        direct: ModuleType,
        deadline: RawDeadline,
        stage: Mapping[str, Any],
        prompt_bundle: Mapping[str, Any],
        recovered_packet: Mapping[str, Any],
        *,
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.direct = direct
        self.deadline = deadline
        self.stage = stage
        self.prompt_bundle = prompt_bundle
        self.recovered_packet = recovered_packet
        self.connection_factory = connection_factory or http.client.HTTPConnection
        self.phases = list(direct.PHASE_SEQUENCE_BY_ARM[stage["tuple_identity"]["arm_id"]])
        self.responses: list[dict[str, Any]] = []
        self.request_bindings: list[dict[str, Any]] = []

    def _validate_prompt(self, phase: str, body: Mapping[str, Any]) -> None:
        prompt = body.get("prompt")
        if not isinstance(prompt, str):
            raise PreflightError("completion body prompt must be text")
        observed = sha256_bytes(prompt.encode("utf-8"))
        commitment = self.stage["prompt_commitments_by_phase"][phase]
        if commitment["status"] == "PROSPECTIVE_EXACT":
            if observed != commitment["rendered_prompt_sha256"]:
                raise PreflightError(f"rendered prompt differs from prospective binding: {phase}")
        elif phase == "RR_PHASE1" and commitment["status"] == "DYNAMIC_SEALED_RR_STATE_RULE":
            if len(self.responses) != 1:
                raise PreflightError("RR phase 1 lacks one prior response")
            schema = self.prompt_bundle["output_schemas"]["phase0_state"]
            state = self.direct.parse_phase_content(self.responses[0]["content"], schema)
            state_bytes = self.direct.canonical_json_bytes(state)
            expected = self.direct._render_rr_phase1(
                self.prompt_bundle,
                self.stage["tuple_identity"]["attempt"],
                self.recovered_packet,
                state_bytes.decode("utf-8"),
                self.direct.sha256_bytes(state_bytes),
            )
            if prompt != expected:
                raise PreflightError("RR phase 1 prompt differs from sealed-state rendering rule")
        else:
            raise PreflightError("unsupported prompt commitment mode")
        self.request_bindings.append(
            {
                "phase_id": phase,
                "rendered_prompt_sha256": observed,
                "canonical_request_sha256": canonical_hash(body),
                "cache_prompt": body.get("cache_prompt"),
            }
        )

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        index = len(self.responses)
        if index >= len(self.phases):
            raise PreflightError("extra completion request forbidden")
        phase = self.phases[index]
        self._validate_prompt(phase, body)
        timeout = self.deadline.remaining_seconds()
        connection = self.connection_factory("127.0.0.1", 8080, timeout=timeout)
        try:
            connection.request(
                "POST", "/completion", body=canonical_json_bytes(body), headers={"Content-Type": "application/json"}
            )
            response = connection.getresponse()
            raw = response.read()
        except (socket.timeout, TimeoutError) as exc:
            self.deadline.expired = True
            raise AttemptDeadlineExceeded("loopback completion exhausted the one cross-phase deadline") from exc
        finally:
            connection.close()
        self.deadline.require_not_expired()
        if response.status != 200:
            raise PreflightError(f"loopback completion returned HTTP status {response.status}")
        parsed = self.direct.strict_json_object_from_bytes(raw, "loopback completion response")
        self.responses.append(parsed)
        return parsed


def validate_live_attestation(stage: Mapping[str, Any], attestation: Mapping[str, Any]) -> None:
    if attestation.get("schema_version") != "orion.p1.scienceagentbench.direct-route-process-attestation.v1":
        raise PreflightError("process attestation schema mismatch")
    pid_text = attestation.get("process_identity", {}).get("pid")
    if isinstance(pid_text, bool) or not isinstance(pid_text, int):
        raise PreflightError("process attestation pid is invalid")
    paths = stage["source_paths"]
    observed = attest_process_identity(
        pid_text,
        Path(paths["server"]),
        stage["server_argv"],
        paths["backend"],
    )
    if observed != attestation.get("process_identity"):
        raise PreflightError("live process identity drifted after attestation")
    listener = attest_loopback_listener(pid_text)
    if listener != attestation.get("listener"):
        raise PreflightError("live loopback listener drifted after attestation")


def _bridge_binding_receipt(
    stage: Mapping[str, Any],
    stage_sha: str,
    attestation_sha: str,
    capture: Mapping[str, Any],
    client: DeadlineLoopbackClient,
) -> dict[str, Any]:
    return {
        "schema_version": "orion.p1.scienceagentbench.direct-route-bridge-binding.v1",
        "authority": "ATTEMPT_BINDING_METADATA_ONLY__ALLOCATION_AND_OUTCOMES_UNFINALIZED",
        "status": "BOUND_ATTEMPT_CAPTURE__ALLOCATION_FINALIZATION_PENDING",
        "tuple_identity": copy.deepcopy(stage["tuple_identity"]),
        "run_plan_binding_extension": copy.deepcopy(stage["run_plan_binding_extension"]),
        "run_plan_binding_extension_sha256": stage["run_plan_binding_extension_sha256"],
        "runtime_stage_sha256": stage_sha,
        "process_attestation_sha256": attestation_sha,
        "attempt_capture_canonical_sha256": canonical_hash(capture),
        "request_bindings": copy.deepcopy(client.request_bindings),
        "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
        "production_admissibility": "CANNOT_CHECK",
        "semantic_choice_sensitivity": "NOT_ESTABLISHED",
        "scientific_authority_delta": "NONE",
    }


def execute_bridge_attempt(
    *,
    stage: Mapping[str, Any],
    stage_sha256: str,
    attestation_sha256: str,
    slurm_identity: Mapping[str, Any],
    output_dir: Path,
    output_dir_fd: int,
    raw_clock: Callable[[], int] | None = None,
    connection_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Execute one translated tuple and persist success or adapter failure evidence."""

    validate_sha256(stage_sha256, "runtime stage sha256")
    validate_sha256(attestation_sha256, "process attestation sha256")
    validate_staged_files_unchanged(stage)
    if not output_dir.is_absolute():
        raise PreflightError("bridge output directory must be absolute")
    if not stat.S_ISDIR(os.fstat(output_dir_fd).st_mode):
        raise PreflightError("bridge output directory capability is not a directory")
    direct = load_module(DIRECT_DRIVER_PATH, "p1_direct_route_for_slurm_bridge_attempt")
    adapter = load_module(ADAPTER_PATH, "p1_adapter_for_slurm_bridge_attempt")
    _, plan = read_json(stage["source_paths"]["plan"], "run plan")
    _, owner = read_json(stage["source_paths"]["owner"], "owner selection")
    _, runtime = read_json(stage["source_paths"]["runtime"], "runtime binding")
    _, masked = read_json(stage["source_paths"]["masked"], "masked packet")
    _, recovered = read_json(stage["source_paths"]["recovered"], "recovered packet")
    _, frozen = read_json(DIRECT_CONTRACT_PATH, "direct-route contract")
    _, prompts = read_json(DIRECT_PROMPT_PATH, "direct-route prompt bundle")
    identity = stage["tuple_identity"]
    arm_id = identity["arm_id"]
    cap_seconds = owner["budget_by_arm"][arm_id]["wall_time_seconds_cap"]
    if cap_seconds != 1800.0:
        raise PreflightError("bridge requires the exact 1800-second matched wall cap")
    clock = adapter.raw_monotonic_ns if raw_clock is None else raw_clock
    deadline = RawDeadline(1_800_000_000_000, clock)
    facade = AdapterFacade(adapter)
    client = DeadlineLoopbackClient(
        direct,
        deadline,
        stage,
        prompts,
        recovered,
        connection_factory=connection_factory,
    )
    output = output_dir / "ATTEMPT_CAPTURE_V1.json"
    binding_output = output_dir / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
    failure_output = output_dir / "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json"
    failure_binding_output = output_dir / "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json"
    _require_absent_entries(
        output_dir_fd,
        [candidate.name for candidate in (output, binding_output, failure_output, failure_binding_output)],
    )
    try:
        receipt = direct.execute_attempt(
            plan=plan,
            contract=frozen,
            prompt_bundle=prompts,
            owner_selection=owner,
            runtime_binding=runtime,
            adapter_module=facade,
            client=client,
            raw_clock=deadline.capture_clock,
            task_id=identity["task_id"],
            arm_id=arm_id,
            attempt=identity["attempt"],
            masked_packet=masked,
            recovered_packet=recovered,
            run_plan_sha256=stage["source_sha256"]["plan"],
            slurm_job_identity=slurm_identity["slurm_job_identity"],
            slurm_in_job_snapshot_sha256=slurm_identity["slurm_in_job_snapshot_sha256"],
        )
    except BaseException as exc:
        if facade.capture is not None:
            failure = (
                AttemptDeadlineExceeded(str(exc))
                if deadline.expired and not isinstance(exc, AttemptDeadlineExceeded)
                else exc
            )
            sidecar = capture_failure_sidecar(facade.capture, failure)
            sidecar_sha, _ = _write_new_json(
                failure_output,
                sidecar,
                parent_fd=output_dir_fd,
            )
            _write_new_json(
                failure_binding_output,
                {
                    "schema_version": "orion.p1.scienceagentbench.direct-route-bridge-failure-binding.v1",
                    "authority": "FAILURE_BINDING_METADATA_ONLY",
                    "status": "CANNOT_CHECK",
                    "tuple_identity": copy.deepcopy(identity),
                    "runtime_stage_sha256": stage_sha256,
                    "process_attestation_sha256": attestation_sha256,
                    "adapter_cannot_check_file_sha256": sidecar_sha,
                    "request_bindings": copy.deepcopy(client.request_bindings),
                    "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
                    "production_admissibility": "CANNOT_CHECK",
                    "scientific_authority_delta": "NONE",
                },
                parent_fd=output_dir_fd,
            )
        raise PreflightError("direct-route bridge execution failed; typed sidecar emitted when capture existed") from exc
    binding = _bridge_binding_receipt(stage, stage_sha256, attestation_sha256, receipt, client)
    binding_sha, binding_identity = _write_new_json(
        binding_output,
        binding,
        parent_fd=output_dir_fd,
    )
    try:
        _write_new_json(output, receipt, parent_fd=output_dir_fd)
    except Exception:
        _rollback_output(
            binding_output,
            binding_sha,
            binding_identity,
            parent_fd=output_dir_fd,
        )
        raise
    return receipt


def run_wrapper_driver(argv: Sequence[str] | None = None) -> int:
    del argv
    raise PreflightError(
        "unchanged wrapper driver mode is disabled; wrapper is byte-bound but NONINVOKED"
    )


def _supervisor_failure(root: Path, exc: BaseException, *, root_fd: int | None = None) -> None:
    if root_fd is None and not root.is_dir():
        return
    path = root / "PREFLIGHT_CANNOT_CHECK_V1.json"
    if root_fd is None and (path.exists() or path.is_symlink()):
        return
    try:
        _write_new_json(
            path,
            {
                "schema_version": "orion.p1.scienceagentbench.direct-route-slurm-preflight-cannot-check.v1",
                "authority": "PREFLIGHT_FAILURE_METADATA_ONLY",
                "status": "CANNOT_CHECK",
                "failure_detail_sha256": sha256_bytes(f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")),
                "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
                "production_admissibility": "CANNOT_CHECK",
                "scientific_authority_delta": "NONE",
            },
            parent_fd=root_fd,
        )
    except Exception:
        pass


def _process_group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for_process_group_absence(
    process: subprocess.Popen[Any], pgid: int, timeout_seconds: float
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while True:
        process.poll()  # Reap the leader so a zombie cannot keep the PGID observable.
        if not _process_group_exists(pgid):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def stop_managed_process(
    process: subprocess.Popen[Any] | None,
    label: str,
    *,
    term_timeout_seconds: float = 15.0,
    kill_timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    if process is None:
        return {
            "label": label,
            "process_started": False,
            "process_group_id": None,
            "termination_signal": None,
            "process_group_absent_after_cleanup": True,
            "process_absent_after_cleanup": True,
        }
    if term_timeout_seconds < 0 or kill_timeout_seconds < 0:
        raise PreflightError("process cleanup timeouts must be nonnegative")
    pgid = process.pid
    signal_name: str | None = None
    if _process_group_exists(pgid):
        signal_name = "SIGTERM"
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        if not _wait_for_process_group_absence(process, pgid, term_timeout_seconds):
            signal_name = "SIGKILL"
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _wait_for_process_group_absence(process, pgid, kill_timeout_seconds)
    process.poll()
    group_absent = not _process_group_exists(pgid)
    leader_absent = process.poll() is not None
    return {
        "label": label,
        "process_started": True,
        "process_group_id": pgid,
        "termination_signal": signal_name,
        "return_code": process.returncode,
        "process_group_absent_after_cleanup": group_absent,
        "process_absent_after_cleanup": leader_absent and group_absent,
    }


def cleanup_managed_processes(
    server_process: subprocess.Popen[Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    wrapper_record = {
        "label": "unchanged-wrapper",
        "status": "NONINVOKED",
        "binding_role": WRAPPER_BINDING_ROLE,
        "process_started": False,
        "process_group_id": None,
        "termination_signal": None,
        "process_group_absent_after_cleanup": True,
        "process_absent_after_cleanup": True,
    }
    try:
        server_cleanup = stop_managed_process(server_process, "llama-server")
    except BaseException as exc:
        server_cleanup = {
            "label": "llama-server",
            "status": "CANNOT_CHECK",
            "process_started": server_process is not None,
            "process_group_id": None if server_process is None else server_process.pid,
            "termination_signal": None,
            "return_code": None if server_process is None else server_process.poll(),
            "cleanup_failure_detail_sha256": sha256_bytes(
                f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
            ),
            "process_group_absent_after_cleanup": False,
            "process_absent_after_cleanup": False,
        }
    return wrapper_record, server_cleanup


def run_supervisor(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage and run one exact direct-route SLURM tuple")
    parser.add_argument("--run-plan", type=Path, required=True)
    parser.add_argument("--run-plan-sha256", required=True)
    parser.add_argument("--owner-selection", type=Path, required=True)
    parser.add_argument("--owner-selection-sha256", required=True)
    parser.add_argument("--runtime-binding", type=Path, required=True)
    parser.add_argument("--runtime-binding-sha256", required=True)
    parser.add_argument("--masked-packet", type=Path, required=True)
    parser.add_argument("--masked-packet-sha256", required=True)
    parser.add_argument("--recovered-packet", type=Path, required=True)
    parser.add_argument("--recovered-packet-sha256", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--arm", choices=("RR", "OS", "NR"), required=True)
    parser.add_argument("--attempt", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--llama-server", type=Path, required=True)
    parser.add_argument("--cuda-backend", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)

    output_root = args.output_root
    if not output_root.is_absolute():
        raise PreflightError("output root must be absolute")
    output_root_fd = _create_new_directory(output_root, 0o700)
    attempt_fd: int | None = None
    process: subprocess.Popen[Any] | None = None
    log_handle: Any | None = None
    caught: BaseException | None = None
    try:
        contract = load_contract()
        validate_frozen_upstream(contract)
        lane = contract.get("lane_artifact_bindings", {})
        if lane.get("bridge_sha256") != sha256_file(Path(__file__).resolve()):
            raise PreflightError("preflight bridge source hash differs from frozen contract")
        if lane.get("launcher_sha256") != sha256_file(LAUNCHER_PATH):
            raise PreflightError("SLURM launcher source hash differs from frozen contract")
        runtime = contract["runtime_artifacts"]
        snapshots = stage_runtime_snapshots(
            {
                "plan": args.run_plan,
                "owner": args.owner_selection,
                "runtime": args.runtime_binding,
                "masked": args.masked_packet,
                "recovered": args.recovered_packet,
            },
            output_root / "runtime-inputs",
            destination_parent_fd=output_root_fd,
        )
        paths = {
            "plan": snapshots["plan"],
            "owner": snapshots["owner"],
            "runtime": snapshots["runtime"],
            "masked": snapshots["masked"],
            "recovered": snapshots["recovered"],
            "model": args.model,
            "server": args.llama_server,
            "backend": args.cuda_backend,
            "launcher": LAUNCHER_PATH,
        }
        expected = {
            "plan": args.run_plan_sha256,
            "owner": args.owner_selection_sha256,
            "runtime": args.runtime_binding_sha256,
            "masked": args.masked_packet_sha256,
            "recovered": args.recovered_packet_sha256,
            "model": runtime["model_sha256"],
            "server": runtime["llama_server_sha256"],
            "backend": runtime["cuda_backend_sha256"],
            "launcher": lane["launcher_sha256"],
        }
        if args.model.stat().st_size != runtime["model_bytes"]:
            raise PreflightError("staged model byte count mismatch")
        stage = build_runtime_stage(contract, paths, expected, args.task_id, args.arm, args.attempt)
        stage = add_prompt_commitments(stage)
        stage_path = output_root / "STAGED_RUNTIME_INPUT_V1.json"
        stage_sha, _ = _write_new_json(stage_path, stage, parent_fd=output_root_fd)
        server_env = build_server_environment(args.cuda_backend)
        argv_exact = stage["server_argv"]
        log_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            log_flags |= os.O_NOFOLLOW
        log_fd = os.open("llama-server.log", log_flags, 0o600, dir_fd=output_root_fd)
        log_handle = os.fdopen(log_fd, "wb")
        process = subprocess.Popen(
            argv_exact,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=server_env,
            start_new_session=True,
        )
        ready = wait_for_exact_server(process)
        process_identity = attest_process_identity(
            process.pid, args.llama_server, argv_exact, os.fspath(args.cuda_backend)
        )
        listener = attest_loopback_listener(process.pid)
        attestation = {
            "schema_version": "orion.p1.scienceagentbench.direct-route-process-attestation.v1",
            "authority": "LIVE_RUNTIME_IDENTITY_METADATA_ONLY__NO_TASK_OR_OUTCOME_AUTHORITY",
            "status": "EXACT_LOOPBACK_PROCESS_ATTESTED",
            "runtime_stage_sha256": stage_sha,
            "process_identity": process_identity,
            "listener": listener,
            "readiness": ready,
            "model_sha256": stage["runtime_observed_sha256"]["model"],
            "llama_server_sha256": stage["runtime_observed_sha256"]["llama_server"],
            "cuda_backend_sha256": stage["runtime_observed_sha256"]["cuda_backend"],
            "launcher_sha256": stage["runtime_observed_sha256"]["launcher"],
            "server_cache_reuse_authority": "REQUEST_CACHE_PROMPT_FALSE_ONLY",
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        attestation_path = output_root / "PROCESS_ATTESTATION_V1.json"
        attestation_sha, _ = _write_new_json(attestation_path, attestation, parent_fd=output_root_fd)
        attempt_dir = output_root / "attempt"
        attempt_fd = _create_new_directory(
            attempt_dir,
            0o700,
            parent_fd=output_root_fd,
        )
        slurm_identity = capture_slurm_identity(attempt_dir, attempt_fd)
        validate_live_attestation(stage, attestation)
        execute_bridge_attempt(
            stage=stage,
            stage_sha256=stage_sha,
            attestation_sha256=attestation_sha,
            slurm_identity=slurm_identity,
            output_dir=attempt_dir,
            output_dir_fd=attempt_fd,
        )
        capture_info = os.stat(
            "ATTEMPT_CAPTURE_V1.json",
            dir_fd=attempt_fd,
            follow_symlinks=False,
        )
        if not stat.S_ISREG(capture_info.st_mode) or capture_info.st_size <= 0:
            raise PreflightError("direct adapter path completed without exact attempt capture")
        return 0
    except BaseException as exc:
        caught = exc
        _supervisor_failure(output_root, exc, root_fd=output_root_fd)
        raise
    finally:
        wrapper_record, server_cleanup = cleanup_managed_processes(process)
        if log_handle is not None:
            log_handle.close()
        all_absent = server_cleanup["process_absent_after_cleanup"]
        cleanup = {
            "schema_version": "orion.p1.scienceagentbench.direct-route-server-cleanup.v1",
            "authority": "PROCESS_CLEANUP_METADATA_ONLY",
            "status": "PASS_OWNED_PROCESS_GROUPS_ABSENT" if all_absent else "CANNOT_CHECK",
            "preflight_succeeded": caught is None,
            "managed_processes": [wrapper_record, server_cleanup],
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        cleanup_write_error: BaseException | None = None
        try:
            _write_new_json(
                output_root / "SERVER_CLEANUP_V1.json", cleanup, parent_fd=output_root_fd
            )
        except BaseException as exc:
            cleanup_write_error = exc
        finally:
            if attempt_fd is not None:
                os.close(attempt_fd)
            os.close(output_root_fd)
        if caught is None:
            if cleanup_write_error is not None:
                raise cleanup_write_error
            if not all_absent:
                raise PreflightError("owned process-group absence could not be verified")


def _install_signal_guards() -> None:
    def handler(signum: int, _frame: Any) -> None:
        raise PreflightError(f"supervisor interrupted by signal {signum}")

    for name in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(name, handler)


def main(argv: Sequence[str] | None = None) -> int:
    actual = list(sys.argv[1:] if argv is None else argv)
    try:
        if actual and actual[0] == "supervise":
            _install_signal_guards()
            return run_supervisor(actual[1:])
        raise PreflightError("only the direct non-wrapper supervise entrypoint is enabled")
    except PreflightError as exc:
        detail_sha = sha256_bytes(f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace"))
        print(f"P1_SAB_DIRECT_ROUTE_SLURM_PREFLIGHT_CANNOT_CHECK detail_sha256={detail_sha}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
