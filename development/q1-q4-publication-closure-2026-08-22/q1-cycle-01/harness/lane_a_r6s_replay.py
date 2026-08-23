#!/usr/bin/env python3
"""Q1-C1 Lane A historical R6S replay wrapper.

This is a receipt-producing runner, not a theorem checker.  The outer process
uses the ORION ResearchWorkspace only to persist a PYTHON capability request.
That capability is a bootstrap which immediately execs the frozen Python
command, under strace whenever the host permits ptrace, in the protocol's
cleared environment. The isolated child
captures the complete author-program streams outside the harness output cap.

The later coordinator must supply a fresh ``git archive`` extraction of the
candidate commit.  This file never extracts a mutable worktree and never
grants mathematical, novelty, performance, submission, or merge authority.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import runpy
import socket
import subprocess
import sys
import traceback
import types
from pathlib import Path
from typing import Any


CANDIDATE_REF = "158fcb08b612ffc82f5a5d2bed4917409084ded8"
PROTOCOL_ID = "Q1-C1"
PROTOCOL_VERSION = "1.0"
PYTHON = str(Path(sys.executable).resolve())
STRACE = "/usr/bin/strace"
STRACE_SHA256 = "28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001"
TIMEOUT_SECONDS = 120
ENVIRONMENT = {
    "PATH": "/usr/bin:/bin",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONHASHSEED": "0",
    "TZ": "UTC",
}
ENVIRONMENT_NAMES = ["PATH", "LANG", "LC_ALL", "PYTHONHASHSEED", "TZ"]
SEMANTIC_EXCLUSIONS = ["/runtime_seconds"]
R6S_SOURCE = "research/extensions/orion-q/max_r6s_all_n_composition.py"
R6S_RESULT = "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
R6S_STDOUT_PREFIX = "ORIONQ_MAX_R6S_ALL_N_COMPOSITION="

FROZEN_INPUT_SHA256 = {
    R6S_SOURCE: "6fad2d4f8f97b0a1b76428bff4fdd83dda18f9e3a49cdab7732391d4bcf3d41d",
    R6S_RESULT: "b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875",
    "research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py": "1006ab0293727ebb994b1202118bc60e779eb5432f820222c6ffbf22304d5965",
    "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json": "3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190",
    "research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py": "7c6579db5f4afbc1738e8b3d96aa3730023bc3831d1fc4950ab34e071c0e3d90",
    "research/extensions/orion-q/max_r6o_enlarged_tag_donor_closure.py": "37cfd64201312e4c7e670e2beefede0961c7dd6a4cd1e3bb2f1fb74afbdf8c17",
    "research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json": "e40e7a948061b9e4b647ba091c04a73b39cffa619ca829bbf4cef4beacdad352",
    "development/orion-q-max-r0/MAX_R6S_ALL_N_COMPOSITION_PROTOCOL.md": "bb8a9d32176c5e13c4ce270b1f83a091b57ed6e00fe55e851bc6dee10027c602",
    "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md": "b44c8b39363cdde2604c5cba7e8998bc34621623639a78007e78a856659ed171",
    "papers/Q-paper-01-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md": "3e9494a68ded5b482d17fc0738c9b4bbd54df389a29de95bfec341e17b6b5ed1",
    "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V2.md": "94e07f841b58a0274c2503d89b011b117636f2e534c2439bd9f00a6aebd368f3",
    "packages/orion-research-harness/pyproject.toml": "bfe497e0c16cde06431799a5a7f1e260757c9744402f40b16c2cff76643dcec7",
    "uv.lock": "62c5d787f3b411f54def8ec61584a8ec3a182003c0fbc013e1e396f37735a465",
}

# The instantiated bootstrap differs only in the JSON argv literal.  The
# campaign binds this exact template, and each result binds the instantiated
# bytes as well as the final exec argv.
BOOTSTRAP_TEMPLATE = """import json,os
argv=json.loads(__ARGV_JSON_REPR__)
env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8","LC_ALL":"C.UTF-8","PYTHONHASHSEED":"0","TZ":"UTC"}
os.execve(argv[0],argv,env)
"""

_NETWORK_SYSCALL = re.compile(
    r"^(?:(?:\[pid\s+\d+\]|\d+)\s+)?(?:socket|socketpair|bind|listen|accept|accept4|"
    r"connect|getsockname|getpeername|sendto|recvfrom|sendmsg|recvmsg|shutdown|"
    r"setsockopt|getsockopt)\("
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _exclusive_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _normalized_paths(argv: list[str]) -> tuple[Path, Path, Path, Path]:
    if len(argv) != 4:
        raise SystemExit(
            "usage: lane_a_r6s_replay.py ARCHIVE_ROOT STDOUT_PATH "
            "STDERR_PATH RESULT_PATH"
        )
    archive, stdout, stderr, result = (Path(item).expanduser().resolve() for item in argv)
    if not archive.is_dir():
        raise NotADirectoryError(archive)
    if len({stdout, stderr, result}) != 3:
        raise ValueError("STDOUT_PATH, STDERR_PATH, and RESULT_PATH must be distinct")
    for output in (stdout, stderr, result):
        if _inside(output, archive):
            raise ValueError("out-of-band outputs must be outside ARCHIVE_ROOT")
        if output.exists():
            raise FileExistsError(output)
    return archive, stdout, stderr, result


def _verify_frozen_inputs(archive: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    mismatches: list[dict[str, str]] = []
    for relative, expected in FROZEN_INPUT_SHA256.items():
        path = archive / relative
        if not path.is_file():
            actual = "MISSING"
            size = None
        else:
            raw = path.read_bytes()
            actual = _sha256_bytes(raw)
            size = len(raw)
        records[relative] = {"sha256": actual, "bytes": size}
        if actual != expected:
            mismatches.append(
                {"path": relative, "expected_sha256": expected, "actual_sha256": actual}
            )
    if mismatches:
        raise ValueError({"frozen_input_mismatches": mismatches})
    return records


def _project_result(value: Any) -> Any:
    if not isinstance(value, dict) or "runtime_seconds" not in value:
        raise ValueError("R6S result lacks the exact /runtime_seconds projection field")
    projected = copy.deepcopy(value)
    del projected["runtime_seconds"]
    return projected


def _json_diffs(expected: Any, actual: Any, pointer: str = "") -> list[dict[str, Any]]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        rows: list[dict[str, Any]] = []
        for key in sorted(set(expected) | set(actual)):
            token = str(key).replace("~", "~0").replace("/", "~1")
            child = f"{pointer}/{token}"
            if key not in expected:
                rows.append({"json_pointer": child, "expected": "<MISSING>", "actual": actual[key]})
            elif key not in actual:
                rows.append({"json_pointer": child, "expected": expected[key], "actual": "<MISSING>"})
            else:
                rows.extend(_json_diffs(expected[key], actual[key], child))
        return rows
    if isinstance(expected, list) and isinstance(actual, list):
        rows = []
        for index in range(max(len(expected), len(actual))):
            child = f"{pointer}/{index}"
            if index >= len(expected):
                rows.append({"json_pointer": child, "expected": "<MISSING>", "actual": actual[index]})
            elif index >= len(actual):
                rows.append({"json_pointer": child, "expected": expected[index], "actual": "<MISSING>"})
            else:
                rows.extend(_json_diffs(expected[index], actual[index], child))
        return rows
    if type(expected) is not type(actual) or expected != actual:
        return [{"json_pointer": pointer or "/", "expected": expected, "actual": actual}]
    return []


def _parse_stdout_projection(stdout_path: Path) -> Any:
    text = stdout_path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith(R6S_STDOUT_PREFIX)]
    if len(rows) != 1:
        raise ValueError(f"expected one R6S stdout record, observed {len(rows)}")
    return json.loads(rows[0][len(R6S_STDOUT_PREFIX) :])


def _deny_socket_audit(event: str, _args: tuple[Any, ...]) -> None:
    if event.startswith("socket."):
        raise PermissionError(f"Q1-C1 network audit denied {event}")


def _socket_negative_control() -> dict[str, str]:
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except PermissionError as exc:
        return {"status": "PASS", "exception": f"{type(exc).__name__}: {exc}"}
    raise AssertionError("AF_INET negative control was not denied")


def _child_record_path(result_path: Path) -> Path:
    return result_path.with_name(result_path.name + ".child.json")


def _trace_path(result_path: Path) -> Path:
    return result_path.with_name(result_path.name + ".network.strace")


def _child(argv: list[str]) -> int:
    archive, stdout_path, stderr_path, result_path = _normalized_paths(argv)
    child_record_path = _child_record_path(result_path)
    if child_record_path.exists():
        raise FileExistsError(child_record_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_fd = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    stderr_fd = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.dup2(stdout_fd, 1)
    os.dup2(stderr_fd, 2)
    os.close(stdout_fd)
    os.close(stderr_fd)

    record: dict[str, Any] = {
        "schema_version": "q1-c1-lane-a-r6s-child-v1",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_ref": CANDIDATE_REF,
        "role": "HISTORICAL_EXECUTABLE_REPLAY_ONLY",
        "grants_scientific_authority": False,
        "environment_allowlist": {"names": ENVIRONMENT_NAMES, "values": ENVIRONMENT},
        "semantic_projection": {"excluded_json_pointers": SEMANTIC_EXCLUSIONS},
    }
    scientific_exit_code = 0
    frozen_result_path = archive / R6S_RESULT
    frozen_result_bytes: bytes | None = None
    try:
        record["input_digests"] = _verify_frozen_inputs(archive)
        if Path(sys.executable).resolve() != Path(PYTHON).resolve():
            raise ValueError(f"unexpected interpreter: {sys.executable}")
        if sys.version.split()[0] != "3.12.13":
            raise ValueError(f"unexpected Python version: {sys.version.split()[0]}")
        python_sha256 = _sha256_path(Path(sys.executable).resolve())
        import numpy as np

        if np.__version__ != "2.3.5":
            raise ValueError(f"unexpected NumPy version: {np.__version__}")
        record["interpreter"] = {
            "path": str(Path(sys.executable).resolve()),
            "python_version": sys.version.split()[0],
            "python_sha256": python_sha256,
            "numpy_version": np.__version__,
        }
        sys.addaudithook(_deny_socket_audit)
        record["socket_negative_control"] = _socket_negative_control()

        frozen_result_bytes = frozen_result_path.read_bytes()
        expected_raw = json.loads(frozen_result_bytes)
        expected_projection = _project_result(expected_raw)
        os.chdir(archive)
        try:
            runpy.run_path(str(archive / R6S_SOURCE), run_name="__main__")
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            scientific_exit_code = int(code)
            if scientific_exit_code:
                traceback.print_exc()
        except BaseException:
            scientific_exit_code = 1
            traceback.print_exc()

        sys.stdout.flush()
        sys.stderr.flush()

        if scientific_exit_code == 0:
            generated_bytes = frozen_result_path.read_bytes()
            generated_raw = json.loads(generated_bytes)
            actual_projection = _project_result(generated_raw)
            stdout_projection = _parse_stdout_projection(stdout_path)
            diffs = _json_diffs(expected_projection, actual_projection)
            stdout_diffs = _json_diffs(actual_projection, stdout_projection)
            record["scientific_result"] = {
                "expected_raw_sha256": _sha256_bytes(frozen_result_bytes),
                "generated_raw_sha256": _sha256_bytes(generated_bytes),
                "generated_raw_bytes": len(generated_bytes),
                "expected_semantic_sha256": _sha256_bytes(_canonical_bytes(expected_projection)),
                "generated_semantic_sha256": _sha256_bytes(_canonical_bytes(actual_projection)),
                "stdout_semantic_sha256": _sha256_bytes(_canonical_bytes(stdout_projection)),
                "semantic_projection": actual_projection,
                "semantic_diff": diffs,
                "stdout_projection_diff": stdout_diffs,
            }
            record["replay_status"] = "MATCH" if not diffs and not stdout_diffs else "MISMATCH"
        else:
            record["replay_status"] = "EXECUTION_ERROR"
    except BaseException as exc:
        scientific_exit_code = scientific_exit_code or 1
        record["replay_status"] = "INVALID"
        record["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        if frozen_result_bytes is not None:
            frozen_result_path.write_bytes(frozen_result_bytes)
            record["frozen_result_restored"] = (
                _sha256_path(frozen_result_path) == FROZEN_INPUT_SHA256[R6S_RESULT]
            )
        record["scientific_exit_code"] = scientific_exit_code
        record["stdout"] = {
            "path": str(stdout_path),
            "sha256": _sha256_path(stdout_path),
            "bytes": stdout_path.stat().st_size,
        }
        record["stderr"] = {
            "path": str(stderr_path),
            "sha256": _sha256_path(stderr_path),
            "bytes": stderr_path.stat().st_size,
        }
        _exclusive_json(child_record_path, record)
    return scientific_exit_code


def _bootstrap_code(exec_argv: list[str]) -> str:
    encoded = json.dumps(exec_argv, separators=(",", ":"))
    return BOOTSTRAP_TEMPLATE.replace("__ARGV_JSON_REPR__", repr(encoded))


def _network_syscalls(trace_path: Path) -> list[str]:
    return [
        line
        for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if _NETWORK_SYSCALL.match(line)
    ]


def _probe_strace(result_path: Path) -> dict[str, Any]:
    probe_trace = result_path.with_name(result_path.name + ".strace-probe.trace")
    probe_stdout = result_path.with_name(result_path.name + ".strace-probe.stdout")
    probe_stderr = result_path.with_name(result_path.name + ".strace-probe.stderr")
    with probe_stdout.open("xb") as stdout, probe_stderr.open("xb") as stderr:
        completed = subprocess.run(
            [
                STRACE, "-f", "-qq", "-e", "trace=network", "-o", str(probe_trace),
                PYTHON, "-I", "-c", "pass",
            ],
            env=ENVIRONMENT, stdin=subprocess.DEVNULL,
            stdout=stdout, stderr=stderr, check=False,
        )
    available = completed.returncode == 0
    if not available:
        error = probe_stderr.read_text(encoding="utf-8", errors="replace")
        if "PTRACE_TRACEME" not in error or "Operation not permitted" not in error:
            raise RuntimeError("strace probe failed for an unclassified reason")
    if not probe_trace.exists():
        probe_trace.write_text("STRACE_PROBE_DID_NOT_CREATE_TRACE\n", encoding="utf-8")
    return {
        "available": available,
        "returncode": completed.returncode,
        "trace_path": str(probe_trace),
        "trace_sha256": _sha256_path(probe_trace),
        "stdout_path": str(probe_stdout),
        "stdout_sha256": _sha256_path(probe_stdout),
        "stderr_path": str(probe_stderr),
        "stderr_sha256": _sha256_path(probe_stderr),
    }


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "packages/orion-research-harness/src/orion_research_harness").is_dir():
            return parent
    raise RuntimeError("cannot locate orion-research-harness source")


def _outer(argv: list[str]) -> int:
    archive, stdout_path, stderr_path, result_path = _normalized_paths(argv)
    child_record_path = _child_record_path(result_path)
    trace_path = _trace_path(result_path)
    for path in (child_record_path, trace_path):
        if path.exists():
            raise FileExistsError(path)
    _verify_frozen_inputs(archive)
    python_sha256 = _sha256_path(Path(PYTHON))
    if _sha256_path(Path(STRACE)) != STRACE_SHA256:
        raise ValueError("frozen strace executable digest mismatch")
    strace_probe = _probe_strace(result_path)

    repo = _repo_root()
    harness_src = repo / "packages/orion-research-harness/src"
    package_root = harness_src / "orion_research_harness"
    lightweight_package = types.ModuleType("orion_research_harness")
    lightweight_package.__path__ = [str(package_root)]
    lightweight_package.__package__ = "orion_research_harness"
    sys.modules["orion_research_harness"] = lightweight_package
    from orion_research_harness.local_tools import service_local_request
    from orion_research_harness.workspace import ResearchWorkspace

    workspace_root = result_path.parent / ".q1-c1-lane-a-r6s-workspace"
    if workspace_root.exists():
        raise FileExistsError(f"fresh ResearchWorkspace required: {workspace_root}")
    workspace = ResearchWorkspace.initialize(
        workspace_root, project_root=archive, allow_process_tools=True
    )
    child_argv = [
        PYTHON,
        "-I",
        str(Path(__file__).resolve()),
        "--child",
        str(archive),
        str(stdout_path),
        str(stderr_path),
        str(result_path),
    ]
    if strace_probe["available"]:
        exec_argv = [
            STRACE, "-f", "-qq", "-e", "trace=network", "-o", str(trace_path),
        ] + child_argv
    else:
        trace_path.write_text(
            "STRACE_UNAVAILABLE: host denied PTRACE_TRACEME; Python audit hook active\n",
            encoding="utf-8",
        )
        exec_argv = child_argv
    bootstrap = _bootstrap_code(exec_argv)
    request = workspace.get_or_create_request(
        capability="PYTHON",
        payload={"code": bootstrap, "cwd": ".", "timeout": TIMEOUT_SECONDS},
    )
    capability_result = service_local_request(workspace, request.request_id)
    if not child_record_path.is_file():
        raise RuntimeError(
            {"missing_child_record": str(child_record_path), "capability_error": capability_result.error}
        )
    child = json.loads(child_record_path.read_text(encoding="utf-8"))
    if not trace_path.is_file():
        raise RuntimeError("strace did not create its output")
    calls = _network_syscalls(trace_path)
    output = capability_result.output if isinstance(capability_result.output, dict) else {}
    capability_output_truncated = any(
        "...[truncated" in str(output.get(stream, "")) for stream in ("stdout", "stderr")
    )
    result = {
        "schema_version": "q1-c1-lane-a-r6s-replay-v1",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_ref": CANDIDATE_REF,
        "role": "HISTORICAL_EXECUTABLE_REPLAY_ONLY",
        "campaign_path": str(Path(__file__).with_name("lane_a_campaign.json")),
        "research_workspace": {
            "root": str(workspace_root),
            "project_root": str(workspace.project_root),
            "allow_process_tools": workspace.allow_process_tools,
            "request": request.as_dict(),
            "result": capability_result.as_dict(),
        },
        "bootstrap": {
            "template_sha256": _sha256_bytes(BOOTSTRAP_TEMPLATE.encode("utf-8")),
            "instantiated_sha256": _sha256_bytes(bootstrap.encode("utf-8")),
            "exec_argv": exec_argv,
            "python_sha256": python_sha256,
        },
        "network_control": {
            "socket_negative_control": child.get("socket_negative_control", {}).get("status"),
            "network_syscall_count": len(calls),
            "network_syscalls": calls,
            "trace_path": str(trace_path),
            "trace_sha256": _sha256_path(trace_path),
            "trace_bytes": trace_path.stat().st_size,
            "syscall_trace_available": strace_probe["available"],
            "strace_probe": strace_probe,
            "namespace_isolation": "NOT_APPLICABLE",
            "namespace_detail": (
                "No network namespace is claimed; Python audit denial and syscall tracing are recorded."
                if strace_probe["available"]
                else "No network namespace is claimed; ptrace is unavailable, so audit-hook evidence is partial and release-blocking."
            ),
            "sandboxed": bool(output.get("sandboxed", False)),
        },
        "child_record": {
            "path": str(child_record_path),
            "sha256": _sha256_path(child_record_path),
            "bytes": child_record_path.stat().st_size,
            "content": child,
        },
        "output_truncated": capability_output_truncated,
        "replay_status": child.get("replay_status"),
        "authority_limits": {
            "grants_mathematical_authority": False,
            "grants_novelty_authority": False,
            "grants_physical_resource_authority": False,
            "grants_runtime_superiority_authority": False,
            "grants_submission_authority": False,
            "grants_merge_authority": False,
        },
    }
    if (
        len(calls)
        or capability_output_truncated
        or result["network_control"]["socket_negative_control"] != "PASS"
    ):
        result["replay_status"] = "INVALID"
    _exclusive_json(result_path, result)
    return 0 if capability_result.success else 1


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--child":
        return _child(sys.argv[2:])
    return _outer(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
