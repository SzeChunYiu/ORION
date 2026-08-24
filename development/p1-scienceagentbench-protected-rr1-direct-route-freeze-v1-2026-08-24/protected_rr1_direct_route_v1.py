#!/usr/bin/env python3
"""Exact-bound one-tuple RR successor with dynamic pre-tokenize fail-close.

The module reuses the merged direct-route SLURM bridge as a byte-bound helper
donor but binds this module and its launcher as the executed successor. It never
retains packet, prompt, completion, or token-ID bodies and exposes no submission
entrypoint.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import http.client
import json
import os
import re
import signal
import socket
import stat
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
CONTRACT_PATH = ROOT / "PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V1.json"
TUPLE_PATH = ROOT / "TUPLE_FREEZE_V1.json"
PLAN_PATH = ROOT / "RUN_PLAN_V1.json"
OWNER_PATH = ROOT / "OWNER_SELECTION_V1.json"
RUNTIME_PATH = ROOT / "RUNTIME_BINDING_V1.json"
LAUNCHER_PATH = ROOT / "run_protected_rr1_direct_route_v1.sh"

UPSTREAM_LANE = (
    REPO_ROOT
    / "development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24"
)
UPSTREAM_BRIDGE_PATH = UPSTREAM_LANE / "direct_route_slurm_preflight_v1.py"
UPSTREAM_CONTRACT_PATH = UPSTREAM_LANE / "DIRECT_ROUTE_SLURM_PREFLIGHT_CONTRACT_V1.json"
UPSTREAM_LAUNCHER_PATH = UPSTREAM_LANE / "run_direct_route_slurm_preflight_v1.sh"
TOKENIZER_LANE = (
    REPO_ROOT / "development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24"
)

EXPECTED_UPSTREAM = {
    "development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/direct_route_slurm_preflight_v1.py": "93ee3abec947a2b6fe6b9a4d1fb7871bbee56c1e190430c4193431a640c93006",
    "development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/DIRECT_ROUTE_SLURM_PREFLIGHT_CONTRACT_V1.json": "59bd2fd58a6da6b43acf781de8c86a1ca8b488938fe0249a9e1e905e19319a13",
    "development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/run_direct_route_slurm_preflight_v1.sh": "eec521d77db9324f4c8373bce2b5e9de0214c2c51808bfcf450e41e1707350ee",
    "development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/JOB_RECEIPT_V1.json": "8644d0b02e125e4cdf75ca0ed913a2fbf0e818ebf358a9ace15d7be7fcabfbc4",
    "development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/EXACT_TOKENIZER_RESULT_V1.json": "b04a25c03f6901f45a047a38962ede4c475826efd3816613bc2fa53df5161e76",
    "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/PROTECTED_PROMPT_FIT_RECEIPT_V1.json": "4ff1163b7e405b5881a7d2d4aea10bb634aaf49ada7bfc0c02159a1b5e18fa83",
    "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/SUCCESSOR_RESULT_V2.json": "63f818cbf0558fb53201f7e7b4b2b97cfae03b0687fbaca91d3d64586df70ce9",
    "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/BODY_FREE_EXPORT_MANIFEST_V1.json": "ea2de55a77b0d8131a7f0e1814791363c50bfc54d9043ecb380ac3c0726cbb07",
    "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/SHA256SUMS": "bc894b82b7635db206f72ef1fb82a28132a272e36e25330c249b5d1c0695ea7f",
}

FIXED_TUPLE = {"task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101}
CONTEXT_TOKENS = 32768
RR1_CAP = 7168
TOKENIZE_REPEAT_COUNT = 3
GPU_UUID_RE = re.compile(
    r"^GPU-[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
DIRECT_DRIVER_SHA256 = "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480"
ADAPTER_SHA256 = "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9"


def _load_exact_module(path: Path, name: str, expected_sha256: str) -> ModuleType:
    """Compile and execute only the bytes hashed through one held descriptor."""

    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise RuntimeError(f"cannot open exact-bound helper: {path}") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError(f"exact-bound helper is not regular: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks)
    finally:
        os.close(fd)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise RuntimeError(f"exact-bound helper SHA-256 mismatch: {path}")
    module = ModuleType(name)
    module.__file__ = os.fspath(path)
    module.__package__ = ""
    exec(compile(raw, os.fspath(path), "exec"), module.__dict__)
    return module


UPSTREAM = _load_exact_module(
    UPSTREAM_BRIDGE_PATH,
    "p1_rr1_exact_bound_slurm_donor",
    EXPECTED_UPSTREAM[
        "development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/direct_route_slurm_preflight_v1.py"
    ],
)
PreflightError = UPSTREAM.PreflightError
AttemptDeadlineExceeded = UPSTREAM.AttemptDeadlineExceeded
RawDeadline = UPSTREAM.RawDeadline
AdapterFacade = UPSTREAM.AdapterFacade
sha256_bytes = UPSTREAM.sha256_bytes
sha256_file = UPSTREAM.sha256_file
canonical_json_bytes = UPSTREAM.canonical_json_bytes
canonical_hash = UPSTREAM.canonical_hash
read_json = UPSTREAM.read_json
validate_sha256 = UPSTREAM.validate_sha256


def load_contract() -> dict[str, Any]:
    _, contract = read_json(CONTRACT_PATH, "protected RR1 direct-route contract")
    if (
        contract.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-direct-route.v1"
    ):
        raise PreflightError("protected RR1 contract schema mismatch")
    return contract


def validate_frozen_upstream(contract: Mapping[str, Any]) -> None:
    declared_items = contract.get("upstream_bindings")
    if not isinstance(declared_items, list):
        raise PreflightError("upstream_bindings must be a list")
    declared: dict[str, str] = {}
    for item in declared_items:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise PreflightError("upstream binding must contain exact path and sha256")
        declared[item["path"]] = item["sha256"]
    if declared != EXPECTED_UPSTREAM:
        raise PreflightError("protected RR1 upstream binding mismatch")
    for relative, expected in EXPECTED_UPSTREAM.items():
        if sha256_file(REPO_ROOT / relative) != expected:
            raise PreflightError(f"protected RR1 upstream drift: {relative}")

    _, upstream_contract = read_json(UPSTREAM_CONTRACT_PATH, "merged SLURM contract")
    UPSTREAM.validate_frozen_upstream(upstream_contract)

    lane = contract.get("lane_artifact_bindings")
    if not isinstance(lane, dict):
        raise PreflightError("lane artifact bindings are missing")
    if lane.get("bridge_sha256") != sha256_file(Path(__file__).resolve()):
        raise PreflightError("executed successor module hash differs from contract")
    if lane.get("launcher_sha256") != sha256_file(LAUNCHER_PATH):
        raise PreflightError("executed successor launcher hash differs from contract")
    local_paths = {
        "tuple_freeze_sha256": TUPLE_PATH,
        "run_plan_sha256": PLAN_PATH,
        "owner_selection_sha256": OWNER_PATH,
        "runtime_binding_sha256": RUNTIME_PATH,
    }
    inputs = contract.get("input_artifact_bindings")
    if not isinstance(inputs, dict):
        raise PreflightError("input artifact bindings are missing")
    for field, path in local_paths.items():
        if inputs.get(field) != sha256_file(path):
            raise PreflightError(f"frozen local input drift: {path.name}")


def validate_private_packet(path: Path, kind: str, contract: Mapping[str, Any]) -> Path:
    if kind not in {"masked", "recovered"}:
        raise PreflightError("private packet kind is invalid")
    candidate = UPSTREAM.validate_absolute_regular(path, f"private {kind} packet")
    raw = candidate.read_bytes()
    _, tuple_freeze = read_json(TUPLE_PATH, "tuple freeze")
    binding = tuple_freeze["packet_bindings"][kind]
    if len(raw) != binding["canonical_json_bytes"]:
        raise PreflightError(f"private {kind} packet byte count mismatch")
    if sha256_bytes(raw) != binding["canonical_json_sha256"]:
        raise PreflightError(f"private {kind} packet SHA-256 mismatch")
    value = UPSTREAM.strict_json_bytes(raw, f"private {kind} packet")
    if canonical_json_bytes(value) != raw:
        raise PreflightError(f"private {kind} packet must be exact canonical JSON bytes")
    expected = contract["private_packet_bindings"][kind]
    if expected != binding:
        raise PreflightError(f"contract and tuple {kind} packet binding disagree")
    return candidate


def build_runtime_stage(
    contract: Mapping[str, Any],
    paths: Mapping[str, Path],
    expected_sha256: Mapping[str, str],
) -> dict[str, Any]:
    _, donor_contract = read_json(UPSTREAM_CONTRACT_PATH, "merged SLURM contract")
    stage = UPSTREAM.build_runtime_stage(
        donor_contract,
        paths,
        expected_sha256,
        FIXED_TUPLE["task_id"],
        FIXED_TUPLE["arm_id"],
        FIXED_TUPLE["attempt"],
    )
    successor_sha = sha256_file(Path(__file__).resolve())
    stage["schema_version"] = (
        "orion.p1.scienceagentbench.protected-rr1-direct-route-runtime-stage.v1"
    )
    stage["authority"] = (
        "ONE_TUPLE_RUNTIME_PREFLIGHT_METADATA_ONLY__NO_SUBMISSION_OUTCOME_OR_SCIENTIFIC_AUTHORITY"
    )
    stage["runtime_observed_sha256"]["preflight_bridge"] = successor_sha
    extension = stage["run_plan_binding_extension"]
    extension["preflight_bridge_sha256"] = successor_sha
    extension["merged_slurm_bridge_donor_sha256"] = EXPECTED_UPSTREAM[
        "development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/direct_route_slurm_preflight_v1.py"
    ]
    extension["dynamic_rr1_pretokenize"] = {
        "route": "POST /tokenize",
        "add_special": True,
        "parse_special": True,
        "repeat_count": TOKENIZE_REPEAT_COUNT,
        "phase_output_cap": RR1_CAP,
        "context_window_tokens": CONTEXT_TOKENS,
        "completion_prompt_n_equality_required": True,
    }
    extension["tuple_freeze_sha256"] = sha256_file(TUPLE_PATH)
    stage["run_plan_binding_extension_sha256"] = canonical_hash(extension)
    stage["tuple_seed"] = FIXED_TUPLE["seed"]
    stage["protected_body_retention"] = False
    return stage


RUNTIME_INPUT_NAMES = {
    "plan": "RUN_PLAN.json",
    "owner": "OWNER_SELECTION.json",
    "runtime": "RUNTIME_BINDING.json",
    "masked": "MASKED_PACKET.json",
    "recovered": "RECOVERED_PACKET.json",
}


def open_runtime_inputs_directory(output_root_fd: int) -> int:
    """Pin the staged runtime-input directory relative to pinned output root."""

    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open("runtime-inputs", flags, dir_fd=output_root_fd)
        entry = os.stat(
            "runtime-inputs", dir_fd=output_root_fd, follow_symlinks=False
        )
    except OSError as exc:
        raise PreflightError("staged runtime-input directory cannot be pinned") from exc
    opened = os.fstat(fd)
    if (
        not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(entry.st_mode)
        or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)
    ):
        os.close(fd)
        raise PreflightError("staged runtime-input directory identity changed")
    return fd


def read_staged_inputs(
    stage: Mapping[str, Any], runtime_inputs_fd: int | None = None
) -> dict[str, dict[str, Any]]:
    """Hash and parse each staged JSON from the same held openat bytes."""

    paths = stage.get("source_paths")
    hashes = stage.get("source_sha256")
    if not isinstance(paths, dict) or not isinstance(hashes, dict):
        raise PreflightError("staged runtime input path/hash bindings are missing")
    if not set(RUNTIME_INPUT_NAMES).issubset(paths) or not set(
        RUNTIME_INPUT_NAMES
    ).issubset(hashes):
        raise PreflightError("staged runtime JSON input set is incomplete")
    for key, filename in RUNTIME_INPUT_NAMES.items():
        if Path(paths[key]).name != filename:
            raise PreflightError(f"staged runtime input filename drift: {key}")

    owned_fd = False
    directory_fd = runtime_inputs_fd
    if directory_fd is None:
        parents = {Path(paths[key]).parent for key in RUNTIME_INPUT_NAMES}
        if len(parents) != 1:
            raise PreflightError("staged runtime JSON inputs must share one directory")
        directory_fd = UPSTREAM._open_verified_directory(
            next(iter(parents)), "staged runtime inputs"
        )
        owned_fd = True
    if directory_fd is None or not stat.S_ISDIR(os.fstat(directory_fd).st_mode):
        raise PreflightError("staged runtime input capability is not a directory")

    results: dict[str, dict[str, Any]] = {}
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        for key, filename in RUNTIME_INPUT_NAMES.items():
            try:
                fd = os.open(filename, flags, dir_fd=directory_fd)
            except OSError as exc:
                raise PreflightError(f"staged runtime input cannot be opened: {key}") from exc
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode):
                    raise PreflightError(f"staged runtime input is not regular: {key}")
                chunks: list[bytes] = []
                while True:
                    chunk = os.read(fd, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                raw = b"".join(chunks)
            finally:
                os.close(fd)
            expected = validate_sha256(hashes[key], f"staged {key} sha256")
            if sha256_bytes(raw) != expected:
                raise PreflightError(f"held staged runtime input hash mismatch: {key}")
            results[key] = UPSTREAM.strict_json_bytes(raw, f"held staged {key}")
    finally:
        if owned_fd:
            os.close(directory_fd)
    return results


def add_prompt_commitments(
    stage: dict[str, Any],
    *,
    bound_inputs: Mapping[str, Mapping[str, Any]] | None = None,
    runtime_inputs_fd: int | None = None,
) -> dict[str, Any]:
    direct = _load_exact_module(
        UPSTREAM.DIRECT_DRIVER_PATH,
        "p1_direct_route_for_rr1_stage",
        DIRECT_DRIVER_SHA256,
    )
    adapter = _load_exact_module(
        UPSTREAM.ADAPTER_PATH,
        "p1_adapter_for_rr1_stage",
        ADAPTER_SHA256,
    )
    inputs = (
        read_staged_inputs(stage, runtime_inputs_fd)
        if bound_inputs is None
        else {key: copy.deepcopy(value) for key, value in bound_inputs.items()}
    )
    if set(inputs) != set(RUNTIME_INPUT_NAMES):
        raise PreflightError("bound staged runtime input set is not exact")
    plan = inputs["plan"]
    owner = inputs["owner"]
    runtime = inputs["runtime"]
    masked = inputs["masked"]
    recovered = inputs["recovered"]
    _, frozen = read_json(UPSTREAM.DIRECT_CONTRACT_PATH, "direct-route contract")
    _, prompts = read_json(UPSTREAM.DIRECT_PROMPT_PATH, "direct-route prompt bundle")
    try:
        direct.validate_packet_contract(frozen, prompts)
        direct.validate_runtime_binding(runtime, frozen)
        direct.validate_owner_selection(owner)
        direct.bind_runner_v2_plan(plan, frozen, prompts, owner, adapter)
    except Exception as exc:
        raise PreflightError(f"protected RR1 staged input invariant failed: {exc}") from exc
    rendered = direct._render_phase0(prompts, "RR_PHASE0", 1, masked)
    result = copy.deepcopy(stage)
    result["prompt_commitments_by_phase"] = {
        "RR_PHASE0": {
            "status": "PROSPECTIVE_EXACT",
            "rendered_prompt_sha256": sha256_bytes(rendered.encode("utf-8")),
        },
        "RR_PHASE1": {
            "status": "DYNAMIC_SEALED_RR_STATE_RULE",
            "template_text_sha256": sha256_bytes(
                prompts["templates"]["RR_PHASE1"]["text"].encode("utf-8")
            ),
            "recovered_packet_canonical_sha256": canonical_hash(recovered),
            "state_source": "RR_PHASE0_STRICT_PARSED_CANONICAL_STATE_AND_SHA256",
        },
    }
    _, tuple_freeze = read_json(TUPLE_PATH, "tuple freeze")
    expected_rr0 = tuple_freeze["rr_phase0_static_fit"]["prompt_sha256"]
    observed_rr0 = result["prompt_commitments_by_phase"]["RR_PHASE0"][
        "rendered_prompt_sha256"
    ]
    if observed_rr0 != expected_rr0:
        raise PreflightError("protected RR0 rendered prompt differs from static-fit binding")
    return result


def validate_staged_files_unchanged(stage: Mapping[str, Any]) -> None:
    if (
        stage.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-direct-route-runtime-stage.v1"
    ):
        raise PreflightError("successor runtime stage schema mismatch")
    if stage.get("tuple_identity") != {
        "task_id": FIXED_TUPLE["task_id"],
        "arm_id": FIXED_TUPLE["arm_id"],
        "attempt": FIXED_TUPLE["attempt"],
    } or stage.get("tuple_seed") != FIXED_TUPLE["seed"]:
        raise PreflightError("successor runtime tuple drift")
    paths = stage.get("source_paths")
    hashes = stage.get("source_sha256")
    if not isinstance(paths, dict) or not isinstance(hashes, dict) or set(paths) != set(hashes):
        raise PreflightError("successor stage path/hash map mismatch")
    normalized = {
        name: UPSTREAM.validate_absolute_regular(Path(path), f"staged {name}")
        for name, path in paths.items()
    }
    UPSTREAM.require_unique_files(normalized)
    for name, path in normalized.items():
        if sha256_file(path) != validate_sha256(hashes[name], f"staged {name} sha256"):
            raise PreflightError(f"staged {name} changed after staging")
    if stage.get("server_argv") != UPSTREAM.build_server_argv(
        normalized["server"], normalized["model"]
    ):
        raise PreflightError("successor server argv drift")
    extension = stage.get("run_plan_binding_extension")
    if not isinstance(extension, dict) or stage.get(
        "run_plan_binding_extension_sha256"
    ) != canonical_hash(extension):
        raise PreflightError("successor run-plan extension drift")
    self_sha = sha256_file(Path(__file__).resolve())
    if (
        stage.get("runtime_observed_sha256", {}).get("preflight_bridge") != self_sha
        or extension.get("preflight_bridge_sha256") != self_sha
    ):
        raise PreflightError("executed successor changed after runtime staging")


def build_credential_free_server_environment(
    backend: Path, source: Mapping[str, str] | None = None
) -> dict[str, str]:
    """Build the exact runtime environment from a narrow noncredential allowlist."""

    donor = UPSTREAM.build_server_environment(backend, source)
    allowed = {
        "HOME",
        "PATH",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TMPDIR",
        "CUDA_VISIBLE_DEVICES",
        "LD_LIBRARY_PATH",
        "GGML_BACKEND_PATH",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    }
    result = {key: value for key, value in donor.items() if key in allowed}
    required = {
        "GGML_BACKEND_PATH",
        "LD_LIBRARY_PATH",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    }
    if not required.issubset(result):
        raise PreflightError("credential-free server environment lacks runtime bindings")
    return result


class DynamicRR1PretokenizeClient(UPSTREAM.DeadlineLoopbackClient):
    """Merged dynamic sealing plus mandatory repeated RR1 pre-tokenization."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.stage.get("tuple_identity") != {
            "task_id": "1",
            "arm_id": "RR",
            "attempt": 1,
        }:
            raise PreflightError("dynamic RR1 client accepts only the frozen tuple")
        self.dynamic_tokenize_bindings: list[dict[str, Any]] = []

    def _request(self, path: str, request_bytes: bytes) -> tuple[bytes, int]:
        timeout = self.deadline.remaining_seconds()
        connection = self.connection_factory("127.0.0.1", 8080, timeout=timeout)
        try:
            connection.request(
                "POST",
                path,
                body=request_bytes,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            raw = response.read()
            status = response.status
        except (socket.timeout, TimeoutError) as exc:
            self.deadline.expired = True
            raise AttemptDeadlineExceeded(
                "loopback request exhausted the one cross-phase deadline"
            ) from exc
        finally:
            connection.close()
        self.deadline.require_not_expired()
        return raw, status

    def _pretokenize_rr1(self, prompt: str, n_predict: int) -> dict[str, Any]:
        if n_predict != RR1_CAP:
            raise PreflightError("dynamic RR1 completion cap differs from frozen 7168")
        request = {
            "content": prompt,
            "add_special": True,
            "parse_special": True,
        }
        request_bytes = canonical_json_bytes(request)
        arrays: list[list[int]] = []
        raw_hashes: list[str] = []
        for _ in range(TOKENIZE_REPEAT_COUNT):
            raw, status = self._request("/tokenize", request_bytes)
            if status != 200:
                raise PreflightError(f"loopback tokenize returned HTTP status {status}")
            parsed = self.direct.strict_json_object_from_bytes(
                raw, "dynamic RR1 tokenize response"
            )
            tokens = parsed.get("tokens")
            if (
                not isinstance(tokens, list)
                or not tokens
                or any(
                    isinstance(token, bool)
                    or not isinstance(token, int)
                    or token < 0
                    for token in tokens
                )
            ):
                raise PreflightError("dynamic RR1 tokenize returned invalid token IDs")
            arrays.append(list(tokens))
            raw_hashes.append(sha256_bytes(raw))
        if any(tokens != arrays[0] for tokens in arrays[1:]):
            raise PreflightError("dynamic RR1 tokenize token arrays disagree")
        if any(digest != raw_hashes[0] for digest in raw_hashes[1:]):
            raise PreflightError("dynamic RR1 tokenize raw responses disagree")
        prompt_tokens = len(arrays[0])
        margin = CONTEXT_TOKENS - prompt_tokens - n_predict
        if margin < 0:
            raise PreflightError(
                "dynamic RR1 pretokenize prompt plus phase cap exceeds context window"
            )
        return {
            "phase_id": "RR_PHASE1",
            "rendered_prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
            "tokenize_request_sha256": sha256_bytes(request_bytes),
            "tokenize_repeat_count": TOKENIZE_REPEAT_COUNT,
            "tokenize_raw_response_sha256": raw_hashes[0],
            "token_array_sha256": canonical_hash(arrays[0]),
            "prompt_tokens": prompt_tokens,
            "phase_output_cap": n_predict,
            "context_window_tokens": CONTEXT_TOKENS,
            "remaining_context_margin_tokens": margin,
            "completion_prompt_n_equal": False,
            "status": "PRETOKENIZE_FIT__COMPLETION_COUNT_PENDING",
        }

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        index = len(self.responses)
        if index >= len(self.phases):
            raise PreflightError("extra completion request forbidden")
        phase = self.phases[index]
        self._validate_prompt(phase, body)
        self.request_bindings[-1]["transport_status"] = "VALIDATED_NOT_SENT"
        prompt = body.get("prompt")
        if not isinstance(prompt, str):
            raise PreflightError("completion prompt must be text")

        dynamic: dict[str, Any] | None = None
        if phase == "RR_PHASE1":
            dynamic = self._pretokenize_rr1(prompt, body.get("n_predict"))
        self.request_bindings[-1]["transport_status"] = "SENT_RESPONSE_PENDING"
        raw, status = self._request("/completion", canonical_json_bytes(body))
        self.request_bindings[-1]["completion_raw_response_sha256"] = sha256_bytes(raw)
        if status != 200:
            self.request_bindings[-1]["transport_status"] = "SENT_RESPONSE_REJECTED"
            raise PreflightError(f"loopback completion returned HTTP status {status}")
        try:
            parsed = self.direct.strict_json_object_from_bytes(
                raw, "loopback completion response"
            )
        except BaseException:
            self.request_bindings[-1]["transport_status"] = "SENT_RESPONSE_REJECTED"
            raise
        if dynamic is not None:
            timings = parsed.get("timings")
            if not isinstance(timings, dict) or timings.get("prompt_n") != dynamic[
                "prompt_tokens"
            ]:
                self.request_bindings[-1]["transport_status"] = "SENT_RESPONSE_REJECTED"
                raise PreflightError(
                    "dynamic RR1 completion prompt_n differs from pretokenize count"
                )
            dynamic["completion_prompt_n_equal"] = True
            dynamic["status"] = "PASS_DYNAMIC_RR1_PRETOKENIZE_FIT"
            self.dynamic_tokenize_bindings.append(dynamic)
        self.request_bindings[-1]["transport_status"] = "SENT_RESPONSE_ACCEPTED"
        self.responses.append(parsed)
        return parsed


def _success_binding(
    stage: Mapping[str, Any],
    stage_sha256: str,
    attestation_sha256: str,
    capture: Mapping[str, Any],
    client: DynamicRR1PretokenizeClient,
) -> dict[str, Any]:
    if len(client.dynamic_tokenize_bindings) != 1:
        raise PreflightError("successful RR attempt lacks one dynamic tokenize binding")
    dynamic = client.dynamic_tokenize_bindings[0]
    return {
        "schema_version": "orion.p1.scienceagentbench.protected-rr1-direct-route-bridge-binding.v1",
        "authority": "ONE_TUPLE_ATTEMPT_BINDING_METADATA_ONLY__ALLOCATION_OUTCOMES_AND_918_LEDGER_UNFINALIZED",
        "status": "BOUND_ONE_TUPLE_CAPTURE__POST_JOB_FINALIZATION_PENDING",
        "tuple_identity": copy.deepcopy(FIXED_TUPLE),
        "run_plan_binding_extension": copy.deepcopy(
            stage["run_plan_binding_extension"]
        ),
        "run_plan_binding_extension_sha256": stage[
            "run_plan_binding_extension_sha256"
        ],
        "runtime_stage_sha256": stage_sha256,
        "process_attestation_sha256": attestation_sha256,
        "attempt_capture_canonical_sha256": canonical_hash(capture),
        "request_bindings": copy.deepcopy(client.request_bindings),
        "dynamic_rr1_pretokenize_binding": copy.deepcopy(dynamic),
        "dynamic_rr1_pretokenize_binding_canonical_sha256": canonical_hash(dynamic),
        "protected_bodies_retained": False,
        "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
        "allocation_status": "CANNOT_CHECK_PENDING_ONE_TUPLE_SCHEDULER_FINALIZATION",
        "production_admissibility": "CANNOT_CHECK",
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
    bound_inputs: Mapping[str, Mapping[str, Any]] | None = None,
    runtime_inputs_fd: int | None = None,
) -> dict[str, Any]:
    validate_sha256(stage_sha256, "runtime stage sha256")
    validate_sha256(attestation_sha256, "process attestation sha256")
    validate_staged_files_unchanged(stage)
    if not output_dir.is_absolute() or not stat.S_ISDIR(os.fstat(output_dir_fd).st_mode):
        raise PreflightError("bridge output must be one absolute pinned directory")

    direct = _load_exact_module(
        UPSTREAM.DIRECT_DRIVER_PATH,
        "p1_direct_route_for_protected_rr1_attempt",
        DIRECT_DRIVER_SHA256,
    )
    adapter = _load_exact_module(
        UPSTREAM.ADAPTER_PATH,
        "p1_adapter_for_protected_rr1_attempt",
        ADAPTER_SHA256,
    )
    inputs = (
        read_staged_inputs(stage, runtime_inputs_fd)
        if bound_inputs is None
        else {key: copy.deepcopy(value) for key, value in bound_inputs.items()}
    )
    if set(inputs) != set(RUNTIME_INPUT_NAMES):
        raise PreflightError("bound staged runtime input set is not exact")
    plan = inputs["plan"]
    owner = inputs["owner"]
    runtime = inputs["runtime"]
    masked = inputs["masked"]
    recovered = inputs["recovered"]
    _, frozen = read_json(UPSTREAM.DIRECT_CONTRACT_PATH, "direct-route contract")
    _, prompts = read_json(UPSTREAM.DIRECT_PROMPT_PATH, "direct-route prompt bundle")
    if owner["budget_by_arm"]["RR"]["wall_time_seconds_cap"] != 1800.0:
        raise PreflightError("protected RR bridge requires exact 1800-second wall cap")
    deadline = RawDeadline(
        1_800_000_000_000,
        adapter.raw_monotonic_ns if raw_clock is None else raw_clock,
    )
    facade = AdapterFacade(adapter)
    client = DynamicRR1PretokenizeClient(
        direct,
        deadline,
        stage,
        prompts,
        recovered,
        connection_factory=connection_factory,
    )
    output = output_dir / "ATTEMPT_CAPTURE_V1.json"
    dynamic_output = output_dir / "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"
    binding_output = output_dir / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
    failure_output = output_dir / "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json"
    failure_binding_output = output_dir / "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json"
    UPSTREAM._require_absent_entries(
        output_dir_fd,
        [
            path.name
            for path in (
                output,
                dynamic_output,
                binding_output,
                failure_output,
                failure_binding_output,
            )
        ],
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
            task_id="1",
            arm_id="RR",
            attempt=1,
            masked_packet=masked,
            recovered_packet=recovered,
            run_plan_sha256=stage["source_sha256"]["plan"],
            slurm_job_identity=slurm_identity["slurm_job_identity"],
            slurm_in_job_snapshot_sha256=slurm_identity[
                "slurm_in_job_snapshot_sha256"
            ],
        )
    except BaseException as exc:
        if facade.capture is not None:
            failure = (
                AttemptDeadlineExceeded(str(exc))
                if deadline.expired and not isinstance(exc, AttemptDeadlineExceeded)
                else exc
            )
            sidecar = UPSTREAM.capture_failure_sidecar(facade.capture, failure)
            sidecar_sha, _ = UPSTREAM._write_new_json(
                failure_output, sidecar, parent_fd=output_dir_fd
            )
            UPSTREAM._write_new_json(
                failure_binding_output,
                {
                    "schema_version": "orion.p1.scienceagentbench.protected-rr1-direct-route-failure-binding.v1",
                    "authority": "ONE_TUPLE_FAILURE_BINDING_METADATA_ONLY",
                    "status": "CANNOT_CHECK",
                    "tuple_identity": copy.deepcopy(FIXED_TUPLE),
                    "runtime_stage_sha256": stage_sha256,
                    "process_attestation_sha256": attestation_sha256,
                    "adapter_cannot_check_file_sha256": sidecar_sha,
                    "request_bindings": copy.deepcopy(client.request_bindings),
                    "dynamic_rr1_pretokenize_bindings": copy.deepcopy(
                        client.dynamic_tokenize_bindings
                    ),
                    "protected_bodies_retained": False,
                    "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
                    "production_admissibility": "CANNOT_CHECK",
                    "scientific_authority_delta": "NONE",
                },
                parent_fd=output_dir_fd,
            )
        raise PreflightError(
            "protected RR1 bridge failed; typed sidecar emitted when capture existed"
        ) from exc

    binding = _success_binding(
        stage, stage_sha256, attestation_sha256, receipt, client
    )
    dynamic_record = {
        "schema_version": "orion.p1.scienceagentbench.dynamic-rr1-pretokenize-binding.v1",
        "authority": "DYNAMIC_PROMPT_FIT_METADATA_ONLY__NO_BODY_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "tuple_identity": copy.deepcopy(FIXED_TUPLE),
        **copy.deepcopy(client.dynamic_tokenize_bindings[0]),
        "protected_bodies_retained": False,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }
    dynamic_sha, dynamic_identity = UPSTREAM._write_new_json(
        dynamic_output, dynamic_record, parent_fd=output_dir_fd
    )
    try:
        binding["dynamic_rr1_pretokenize_file_sha256"] = dynamic_sha
        binding_sha, binding_identity = UPSTREAM._write_new_json(
            binding_output, binding, parent_fd=output_dir_fd
        )
    except Exception:
        UPSTREAM._rollback_output(
            dynamic_output,
            dynamic_sha,
            dynamic_identity,
            parent_fd=output_dir_fd,
        )
        raise
    try:
        UPSTREAM._write_new_json(output, receipt, parent_fd=output_dir_fd)
    except Exception:
        UPSTREAM._rollback_output(
            binding_output,
            binding_sha,
            binding_identity,
            parent_fd=output_dir_fd,
        )
        UPSTREAM._rollback_output(
            dynamic_output,
            dynamic_sha,
            dynamic_identity,
            parent_fd=output_dir_fd,
        )
        raise
    return receipt


def capture_gpu_identity(
    output_root: Path,
    output_root_fd: int,
    *,
    environment: Mapping[str, str] | None = None,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    env = dict(os.environ if environment is None else environment)
    job_id = env.get("SLURM_JOB_ID")
    visible = env.get("CUDA_VISIBLE_DEVICES")
    if not isinstance(job_id, str) or re.fullmatch(r"[1-9][0-9]*", job_id) is None:
        raise PreflightError("GPU identity requires one canonical SLURM_JOB_ID")
    if (
        not isinstance(visible, str)
        or not visible
        or "," in visible
        or any(character.isspace() for character in visible)
    ):
        raise PreflightError("GPU identity requires exactly one CUDA-visible device")
    for name in ("SLURM_JOB_GPUS", "SLURM_STEP_GPUS"):
        value = env.get(name)
        if value is not None and (
            not isinstance(value, str)
            or not value
            or "," in value
            or any(character.isspace() for character in value)
        ):
            raise PreflightError(f"GPU identity {name} must name at most one device")
    command = [
        "nvidia-smi",
        "--query-gpu=index,uuid,name",
        "--format=csv,noheader,nounits",
    ]
    try:
        runner_env = {
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
        }
        completed = runner(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=runner_env,
            check=False,
        )
    except OSError as exc:
        raise PreflightError("nvidia-smi allocation identity command failed") from exc
    if completed.returncode != 0:
        raise PreflightError(
            "nvidia-smi allocation identity returned nonzero; "
            f"stderr_sha256={sha256_bytes(completed.stderr)}"
        )
    lines = [line.strip() for line in completed.stdout.decode("utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        raise PreflightError("exactly one visible allocated GPU is required")
    fields = [field.strip() for field in lines[0].split(",", 2)]
    if len(fields) != 3 or not fields[0].isdigit() or GPU_UUID_RE.fullmatch(fields[1]) is None:
        raise PreflightError("allocated GPU identity is not canonical")
    if fields[2] != "NVIDIA A40":
        raise PreflightError("allocated GPU must be exactly NVIDIA A40")
    result = {
        "schema_version": "orion.p1.scienceagentbench.one-a40-allocation-identity.v1",
        "authority": "IN_JOB_VISIBLE_GPU_IDENTITY_METADATA_ONLY",
        "status": "PASS_EXACTLY_ONE_VISIBLE_NVIDIA_A40",
        "slurm_job_id": job_id,
        "cuda_visible_devices": visible,
        "slurm_job_gpus": env.get("SLURM_JOB_GPUS"),
        "slurm_step_gpus": env.get("SLURM_STEP_GPUS"),
        "gpu": {"visible_index": fields[0], "gpu_uuid": fields[1], "name": fields[2]},
        "nvidia_smi_stdout_sha256": sha256_bytes(completed.stdout),
        "scheduler_exclusivity_status": "CANNOT_CHECK_PENDING_POST_JOB_SCHEDULER_FINALIZATION",
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }
    UPSTREAM._write_new_json(
        output_root / "GPU_ALLOCATION_IDENTITY_V1.json",
        result,
        parent_fd=output_root_fd,
    )
    return result


def validate_live_attestation(
    stage: Mapping[str, Any], attestation: Mapping[str, Any]
) -> None:
    validate_staged_files_unchanged(stage)
    if (
        attestation.get("schema_version")
        != "orion.p1.scienceagentbench.protected-rr1-process-attestation.v1"
    ):
        raise PreflightError("successor process attestation schema mismatch")
    pid = attestation.get("process_identity", {}).get("pid")
    if isinstance(pid, bool) or not isinstance(pid, int):
        raise PreflightError("successor process pid is invalid")
    paths = stage["source_paths"]
    observed = UPSTREAM.attest_process_identity(
        pid,
        Path(paths["server"]),
        stage["server_argv"],
        paths["backend"],
    )
    if observed != attestation.get("process_identity"):
        raise PreflightError("successor process identity drift")
    if UPSTREAM.attest_loopback_listener(pid) != attestation.get("listener"):
        raise PreflightError("successor loopback listener drift")


def _supervisor_failure(
    root: Path, exc: BaseException, *, root_fd: int | None = None
) -> None:
    if root_fd is None and not root.is_dir():
        return
    try:
        UPSTREAM._write_new_json(
            root / "PREFLIGHT_CANNOT_CHECK_V1.json",
            {
                "schema_version": "orion.p1.scienceagentbench.protected-rr1-preflight-cannot-check.v1",
                "authority": "ONE_TUPLE_PREFLIGHT_FAILURE_METADATA_ONLY",
                "status": "CANNOT_CHECK",
                "tuple_identity": copy.deepcopy(FIXED_TUPLE),
                "failure_detail_sha256": sha256_bytes(
                    f"{type(exc).__name__}:{exc}".encode(
                        "utf-8", errors="replace"
                    )
                ),
                "protected_bodies_retained": False,
                "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
                "production_admissibility": "CANNOT_CHECK",
                "scientific_authority_delta": "NONE",
            },
            parent_fd=root_fd,
        )
    except Exception:
        pass


def run_supervisor(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run only the frozen protected task 1 / RR / attempt 1 tuple"
    )
    parser.add_argument("--masked-packet", type=Path, required=True)
    parser.add_argument("--recovered-packet", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--llama-server", type=Path, required=True)
    parser.add_argument("--cuda-backend", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)

    contract = load_contract()
    validate_frozen_upstream(contract)
    masked = validate_private_packet(args.masked_packet, "masked", contract)
    recovered = validate_private_packet(args.recovered_packet, "recovered", contract)
    output_root = args.output_root
    if not output_root.is_absolute():
        raise PreflightError("output root must be absolute")
    output_root_fd = UPSTREAM._create_new_directory(output_root, 0o700)
    attempt_fd: int | None = None
    runtime_inputs_fd: int | None = None
    process: subprocess.Popen[Any] | None = None
    caught: BaseException | None = None
    try:
        runtime = contract["runtime_artifacts"]
        inputs = contract["input_artifact_bindings"]
        snapshots = UPSTREAM.stage_runtime_snapshots(
            {
                "plan": PLAN_PATH,
                "owner": OWNER_PATH,
                "runtime": RUNTIME_PATH,
                "masked": masked,
                "recovered": recovered,
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
            "plan": inputs["run_plan_sha256"],
            "owner": inputs["owner_selection_sha256"],
            "runtime": inputs["runtime_binding_sha256"],
            "masked": contract["private_packet_bindings"]["masked"][
                "canonical_json_sha256"
            ],
            "recovered": contract["private_packet_bindings"]["recovered"][
                "canonical_json_sha256"
            ],
            "model": runtime["model_sha256"],
            "server": runtime["llama_server_sha256"],
            "backend": runtime["cuda_backend_sha256"],
            "launcher": contract["lane_artifact_bindings"]["launcher_sha256"],
        }
        if args.model.stat().st_size != runtime["model_bytes"]:
            raise PreflightError("staged model byte count mismatch")
        stage = build_runtime_stage(contract, paths, expected)
        runtime_inputs_fd = open_runtime_inputs_directory(output_root_fd)
        bound_inputs = read_staged_inputs(stage, runtime_inputs_fd)
        stage = add_prompt_commitments(stage, bound_inputs=bound_inputs)
        stage_sha, _ = UPSTREAM._write_new_json(
            output_root / "STAGED_RUNTIME_INPUT_V1.json",
            stage,
            parent_fd=output_root_fd,
        )
        process = subprocess.Popen(
            stage["server_argv"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=build_credential_free_server_environment(args.cuda_backend),
            start_new_session=True,
        )
        ready = UPSTREAM.wait_for_exact_server(process)
        process_identity = UPSTREAM.attest_process_identity(
            process.pid,
            args.llama_server,
            stage["server_argv"],
            os.fspath(args.cuda_backend),
        )
        listener = UPSTREAM.attest_loopback_listener(process.pid)
        attestation = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-process-attestation.v1",
            "authority": "LIVE_RUNTIME_IDENTITY_METADATA_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
            "status": "EXACT_ONE_TUPLE_LOOPBACK_PROCESS_ATTESTED",
            "runtime_stage_sha256": stage_sha,
            "process_identity": process_identity,
            "listener": listener,
            "readiness": ready,
            "model_sha256": stage["runtime_observed_sha256"]["model"],
            "llama_server_sha256": stage["runtime_observed_sha256"]["llama_server"],
            "cuda_backend_sha256": stage["runtime_observed_sha256"]["cuda_backend"],
            "launcher_sha256": stage["runtime_observed_sha256"]["launcher"],
            "successor_bridge_sha256": stage["runtime_observed_sha256"][
                "preflight_bridge"
            ],
            "server_stdout_stderr_retained": False,
            "protected_bodies_retained": False,
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        attestation_sha, _ = UPSTREAM._write_new_json(
            output_root / "PROCESS_ATTESTATION_V1.json",
            attestation,
            parent_fd=output_root_fd,
        )
        capture_gpu_identity(output_root, output_root_fd)
        attempt_dir = output_root / "attempt"
        attempt_fd = UPSTREAM._create_new_directory(
            attempt_dir, 0o700, parent_fd=output_root_fd
        )
        slurm_identity = UPSTREAM.capture_slurm_identity(attempt_dir, attempt_fd)
        validate_live_attestation(stage, attestation)
        execute_bridge_attempt(
            stage=stage,
            stage_sha256=stage_sha,
            attestation_sha256=attestation_sha,
            slurm_identity=slurm_identity,
            output_dir=attempt_dir,
            output_dir_fd=attempt_fd,
            bound_inputs=bound_inputs,
            runtime_inputs_fd=runtime_inputs_fd,
        )
        capture_info = os.stat(
            "ATTEMPT_CAPTURE_V1.json", dir_fd=attempt_fd, follow_symlinks=False
        )
        if not stat.S_ISREG(capture_info.st_mode) or capture_info.st_size <= 0:
            raise PreflightError("one-tuple route completed without attempt capture")
        return 0
    except BaseException as exc:
        caught = exc
        _supervisor_failure(output_root, exc, root_fd=output_root_fd)
        raise
    finally:
        wrapper_record, server_cleanup = UPSTREAM.cleanup_managed_processes(process)
        all_absent = server_cleanup["process_absent_after_cleanup"]
        cleanup = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-server-cleanup.v1",
            "authority": "PROCESS_CLEANUP_METADATA_ONLY",
            "status": "PASS_OWNED_PROCESS_GROUPS_ABSENT" if all_absent else "CANNOT_CHECK",
            "preflight_succeeded": caught is None,
            "managed_processes": [wrapper_record, server_cleanup],
            "protected_bodies_retained": False,
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        cleanup_error: BaseException | None = None
        try:
            UPSTREAM._write_new_json(
                output_root / "SERVER_CLEANUP_V1.json",
                cleanup,
                parent_fd=output_root_fd,
            )
        except BaseException as exc:
            cleanup_error = exc
        finally:
            if attempt_fd is not None:
                os.close(attempt_fd)
            if runtime_inputs_fd is not None:
                os.close(runtime_inputs_fd)
            os.close(output_root_fd)
        if caught is None:
            if cleanup_error is not None:
                raise cleanup_error
            if not all_absent:
                raise PreflightError("owned server process-group absence cannot be verified")


def _install_signal_guards() -> None:
    def handler(signum: int, _frame: Any) -> None:
        raise PreflightError(f"successor supervisor interrupted by signal {signum}")

    for name in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(name, handler)


def main(argv: Sequence[str] | None = None) -> int:
    actual = list(sys.argv[1:] if argv is None else argv)
    try:
        if actual and actual[0] == "supervise":
            _install_signal_guards()
            result = run_supervisor(actual[1:])
            if result != 0:
                raise PreflightError("one-tuple supervisor returned nonzero")
            print("P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING")
            return 0
        raise PreflightError("only the non-submitting one-tuple supervise entrypoint is enabled")
    except PreflightError as exc:
        detail_sha = sha256_bytes(
            f"{type(exc).__name__}:{exc}".encode("utf-8", errors="replace")
        )
        print(
            "P1_SAB_PROTECTED_RR1_DIRECT_ROUTE_CANNOT_CHECK "
            f"detail_sha256={detail_sha}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
