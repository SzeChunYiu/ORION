#!/usr/bin/env python3
"""Run the single frozen P3 V9 native BERTMap smoke, fail closed.

This runner has interface-conformance authority only.  It never opens a gold
or reference alignment and never computes scientific performance.  An atomic
attempt lock prevents a retry after native process launch.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_V9.json"
RIGHTS_GATE = ROOT / "RUNTIME_RIGHTS_GATE_V9.json"
UNIVERSE_MANIFEST = ROOT / "UNIVERSE_MANIFEST_V9.json"
PARSER = ROOT.parent / "p3-bertmap-execution-binding-v7-2026-08-23" / "bertmap_native_parser_v7.py"
PYTHON = ROOT / "runtime/venv/bin/python"
ENTRYPOINT = ROOT / "runtime/source/scripts/bertmap.py"
SOURCE = ROOT / "runtime/inputs/source.owl"
TARGET = ROOT / "runtime/inputs/target.owl"
CONFIG = ROOT / "runtime/config.yaml"
JAVA_HOME = Path("/opt/homebrew/Cellar/openjdk@17/17.0.19/libexec/openjdk.jdk/Contents/Home")
OUTPUT_ROOT = ROOT / "runtime/results"
OUTPUT_DIR = OUTPUT_ROOT / "bertmap-out/bertmap/match"
ATTEMPT_LOCK = ROOT / "NATIVE_ATTEMPT_LOCK_V9.json"
STDOUT_LOG = ROOT / "NATIVE_STDOUT_V9.log"
STDERR_LOG = ROOT / "NATIVE_STDERR_V9.log"
PARSER_RECEIPT = ROOT / "NATIVE_ARTIFACT_CONTRACT_V9.json"
EXECUTION_RECEIPT = ROOT / "NATIVE_EXECUTION_RECEIPT_V9.json"

PROTOCOL_SHA256 = "7e5eac0b04988cf936a9517043e63f8599866d215e1c5b3537fb47271d87f2e8"
RIGHTS_GATE_SHA256 = "1c92df931ee57e6d743484461c43e8d26c8d2e0773eb834be05a4133264a602a"
PARSER_SHA256 = "d1184dc129082bdcf18b415b551f244a695b4e34417286afc37a3f3a5d788bc5"
UNIVERSE_SHA256 = "4bc0ff4c5c4afd18baff0d5cee3d6566e79fed681157211569d20af0e0d02de2"
CONFIG_SHA256 = "01df313b8bb683f6cfe08f0050f90979ccdcc14454074eaccbcab395bf1096ea"
SOURCE_SHA256 = "c347f32626f6c5b3b782b2f6344bca5ac2282a701161d11f1e02a7422fef4d9e"
TARGET_SHA256 = "16bd34ec22c3d130b94257404fd60a112a3383d16255a67472e0c5e1518c5521"
MODEL_WEIGHT_SHA256 = "a18c4c260fb5c0978b86658615106d5617050b5f14dac6ceb5e0d8beb2f9f719"
REPAIRED_MAPPING_SHA256 = "d0b3b6cfdee45019783707c4bd623cc76f8325142828cf1e10ebb74ad628d70f"
TIMEOUT_SECONDS = 1800
STDIN_BYTES = b"2g\n"
STDIN_DESCRIPTION = r"2g\n"
REQUIRED_ARTIFACTS = (
    "raw_mappings.json",
    "raw_mappings.tsv",
    "extended_mappings.tsv",
    "filtered_mappings.tsv",
    "repaired_mappings.tsv",
)
OFFLINE_GUARDS = {
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


class Refusal(RuntimeError):
    """Pre-launch gate refusal; no native attempt has occurred."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Refusal(f"{path.name} is not a JSON object")
    return value


def require_hash(path: Path, expected: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise Refusal(f"required regular non-symlink file absent: {path}")
    observed = sha256(path)
    if observed != expected:
        raise Refusal(f"hash mismatch for {path.name}: {observed}")


def atomic_json(path: Path, value: dict[str, Any], *, exclusive: bool = False) -> None:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if exclusive:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(payload, encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def preflight() -> None:
    expected = {
        PROTOCOL: PROTOCOL_SHA256,
        RIGHTS_GATE: RIGHTS_GATE_SHA256,
        UNIVERSE_MANIFEST: UNIVERSE_SHA256,
        PARSER: PARSER_SHA256,
        CONFIG: CONFIG_SHA256,
        SOURCE: SOURCE_SHA256,
        TARGET: TARGET_SHA256,
        ROOT / "runtime/model/pytorch_model.bin": MODEL_WEIGHT_SHA256,
        ROOT / "runtime/source/src/deeponto/align/mapping.py": REPAIRED_MAPPING_SHA256,
        ROOT / "runtime/venv/lib/python3.10/site-packages/deeponto/align/mapping.py": REPAIRED_MAPPING_SHA256,
    }
    for path, digest in expected.items():
        require_hash(path, digest)

    protocol = load_object(PROTOCOL)
    gate = load_object(RIGHTS_GATE)
    if protocol.get("protocol_id") != "P3_V9_BERTMAP_COMPLETE_RUNTIME_RIGHTS_AND_NO_GOLD_NATIVE_SMOKE":
        raise Refusal("protocol identity mismatch")
    if protocol.get("required_actual_artifacts") != list(REQUIRED_ARTIFACTS):
        raise Refusal("required artifact list mismatch")
    if protocol.get("unchanged_no_gold_smoke", {}).get("retries") != 0:
        raise Refusal("frozen retry count is not zero")
    if protocol.get("unchanged_no_gold_smoke", {}).get("wall_seconds") != TIMEOUT_SECONDS:
        raise Refusal("frozen timeout mismatch")
    if protocol.get("unchanged_no_gold_smoke", {}).get("stdin_utf8") != STDIN_DESCRIPTION:
        raise Refusal("frozen stdin mismatch")
    if protocol.get("unchanged_no_gold_smoke", {}).get("offline_guards") != OFFLINE_GUARDS:
        raise Refusal("offline guard mismatch")
    if gate.get("terminal") != "PASS__COMPLETE_CONTENT_ADDRESSED_RUNTIME_AND_COMPONENT_RIGHTS_BOUND":
        raise Refusal("rights gate terminal is not PASS")
    if gate.get("native_execution_authorized") is not True:
        raise Refusal("native execution is not authorized")
    if gate.get("checks_passed") != gate.get("checks_total") or gate.get("checks_total") != 30:
        raise Refusal("rights gate check count mismatch")
    if gate.get("gold_or_outcomes_opened") is not False:
        raise Refusal("rights gate outcome-blind flag mismatch")

    if not PYTHON.exists() or not os.access(PYTHON, os.X_OK):
        raise Refusal("frozen Python executable absent")
    if not ENTRYPOINT.is_file() or ENTRYPOINT.is_symlink():
        raise Refusal("native entrypoint absent or symlinked")
    if not (JAVA_HOME / "bin/java").is_file():
        raise Refusal("exact Java executable absent")
    if ATTEMPT_LOCK.exists() or EXECUTION_RECEIPT.exists():
        raise Refusal("native attempt or receipt already exists; retries are forbidden")
    for path in (STDOUT_LOG, STDERR_LOG, PARSER_RECEIPT):
        if path.exists():
            raise Refusal(f"stale execution artifact present: {path.name}")
    if OUTPUT_DIR.exists():
        raise Refusal("native match output directory already exists")
    if OUTPUT_ROOT.exists() and any(OUTPUT_ROOT.iterdir()):
        raise Refusal("runtime results root is not empty")


def build_environment() -> dict[str, str]:
    home = ROOT / "runtime/home"
    cache = ROOT / "runtime/cache/native"
    temp = ROOT / "runtime/tmp"
    for path in (home, cache, temp):
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
    env = {
        "PATH": f"{PYTHON.parent}:{JAVA_HOME / 'bin'}:/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(home),
        "XDG_CACHE_HOME": str(cache / "xdg"),
        "HF_HOME": str(cache / "huggingface"),
        "HF_HUB_CACHE": str(cache / "huggingface/hub"),
        "TRANSFORMERS_CACHE": str(cache / "transformers"),
        "TORCH_HOME": str(cache / "torch"),
        "TMPDIR": str(temp),
        "PYTHONNOUSERSITE": "1",
        "PYTHONUNBUFFERED": "1",
        "JAVA_HOME": str(JAVA_HOME),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        **OFFLINE_GUARDS,
    }
    for key in ("XDG_CACHE_HOME", "HF_HOME", "HF_HUB_CACHE", "TRANSFORMERS_CACHE", "TORCH_HOME"):
        Path(env[key]).mkdir(parents=True, exist_ok=True, mode=0o700)
    return env


def command() -> list[str]:
    return [
        str(PYTHON),
        str(ENTRYPOINT),
        "-s",
        str(SOURCE),
        "-t",
        str(TARGET),
        "-c",
        str(CONFIG),
    ]


def bounded_excerpt(path: Path, head_bytes: int = 4000, tail_bytes: int = 8000) -> dict[str, Any]:
    if not path.is_file():
        return {"present": False}
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(head_bytes)
        if size > tail_bytes:
            handle.seek(max(0, size - tail_bytes))
        tail = handle.read(tail_bytes)
    return {
        "present": True,
        "bytes": size,
        "sha256": sha256(path),
        "head": head.decode("utf-8", errors="replace"),
        "tail": tail.decode("utf-8", errors="replace"),
        "excerpt_truncated": size > head_bytes + tail_bytes,
    }


def artifact_inventory() -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for name in REQUIRED_ARTIFACTS:
        path = OUTPUT_DIR / name
        valid = path.is_file() and not path.is_symlink()
        inventory[name] = {
            "path": str(path),
            "regular_non_symlink": valid,
            "bytes": path.stat().st_size if valid else None,
            "sha256": sha256(path) if valid else None,
        }
    return inventory


def terminate_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def run_parser(env: dict[str, str]) -> tuple[int, dict[str, Any], str, str]:
    parser_command = [
        str(PYTHON),
        str(PARSER),
        "--output-dir",
        str(OUTPUT_DIR),
        "--manifest",
        str(UNIVERSE_MANIFEST),
        "--write-receipt",
        str(PARSER_RECEIPT),
    ]
    completed = subprocess.run(
        parser_command,
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=120,
        check=False,
    )
    parsed = load_object(PARSER_RECEIPT) if PARSER_RECEIPT.is_file() else {}
    return (
        completed.returncode,
        parsed,
        completed.stdout.decode("utf-8", errors="replace")[-8000:],
        completed.stderr.decode("utf-8", errors="replace")[-8000:],
    )


def main() -> int:
    try:
        preflight()
        env = build_environment()
    except Exception as exc:
        refusal = {
            "schema_version": "orion.p3.repaired-native-runtime.prelaunch-refusal.v9",
            "terminal": "CANNOT_CHECK__PRELAUNCH_GATE_REFUSED__NO_NATIVE_ATTEMPT",
            "reason": f"{type(exc).__name__}: {exc}",
            "evaluated_at": now(),
        }
        print(json.dumps(refusal, indent=2, sort_keys=True))
        return 2

    native_command = command()
    started_at = now()
    lock = {
        "schema_version": "orion.p3.repaired-native-runtime.native-attempt-lock.v9",
        "protocol_sha256": PROTOCOL_SHA256,
        "created_before_process_launch": True,
        "started_at": started_at,
        "command": native_command,
        "cwd": str(ROOT),
        "stdin_utf8": STDIN_DESCRIPTION,
        "timeout_seconds": TIMEOUT_SECONDS,
        "retries_permitted": 0,
        "offline_guards": OFFLINE_GUARDS,
    }
    try:
        atomic_json(ATTEMPT_LOCK, lock, exclusive=True)
    except Exception as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK__ATTEMPT_LOCK_FAILED__NO_NATIVE_ATTEMPT", "reason": str(exc)}))
        return 2

    started = time.monotonic()
    process: subprocess.Popen[bytes] | None = None
    exit_code: int | None = None
    timed_out = False
    launch_error: str | None = None
    try:
        with STDOUT_LOG.open("xb") as stdout, STDERR_LOG.open("xb") as stderr:
            process = subprocess.Popen(
                native_command,
                cwd=ROOT,
                env=env,
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                process.communicate(input=STDIN_BYTES, timeout=TIMEOUT_SECONDS)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                terminate_group(process)
                exit_code = process.returncode
    except Exception as exc:
        launch_error = f"{type(exc).__name__}: {exc}"
        if process is not None and process.poll() is None:
            terminate_group(process)
            exit_code = process.returncode
    wall_seconds = time.monotonic() - started
    finished_at = now()

    artifacts = artifact_inventory()
    artifacts_complete = all(item["regular_non_symlink"] for item in artifacts.values())
    parser_exit_code: int | None = None
    parser_result: dict[str, Any] = {}
    parser_stdout = ""
    parser_stderr = ""
    if exit_code == 0 and not timed_out and launch_error is None and artifacts_complete:
        try:
            parser_exit_code, parser_result, parser_stdout, parser_stderr = run_parser(env)
        except Exception as exc:
            parser_stderr = f"{type(exc).__name__}: {exc}"

    parser_pass = (
        parser_exit_code == 0
        and parser_result.get("terminal") == "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS"
    )
    success = exit_code == 0 and not timed_out and launch_error is None and artifacts_complete and parser_pass
    if success:
        terminal = "P3_V9_NATIVE_SMOKE_PASS__FIVE_OF_FIVE_ACTUAL_ARTIFACTS_PASS_FROZEN_V7_PARSER__NATIVE_READINESS_THREE_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE"
        failure_reason = None
    else:
        terminal = "CANNOT_CHECK__P3_V9_SINGLE_NATIVE_ATTEMPT_FAILED__NO_RETRY__SCIENTIFIC_READINESS_ZERO_OF_THREE"
        if launch_error:
            failure_reason = launch_error
        elif timed_out:
            failure_reason = "whole-run timeout"
        elif exit_code != 0:
            failure_reason = f"native exit code {exit_code}"
        elif not artifacts_complete:
            failure_reason = "one or more required actual artifacts absent or symlinked"
        else:
            failure_reason = f"frozen V7 parser failure: {parser_stderr or parser_result}"

    receipt = {
        "schema_version": "orion.p3.repaired-native-runtime.native-execution-receipt.v9",
        "protocol_id": "P3_V9_BERTMAP_COMPLETE_RUNTIME_RIGHTS_AND_NO_GOLD_NATIVE_SMOKE",
        "terminal": terminal,
        "authority": "NATIVE_EXECUTION_AND_ARTIFACT_INTERFACE_CONFORMANCE_ONLY__NO_MAPPING_TRUTH_OR_SCIENTIFIC_PERFORMANCE_AUTHORITY",
        "success": success,
        "failure_reason": failure_reason,
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_seconds": wall_seconds,
        "timeout_seconds": TIMEOUT_SECONDS,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "retries_permitted": 0,
        "retries_used": 0,
        "launch_error": launch_error,
        "command": native_command,
        "cwd": str(ROOT),
        "stdin_utf8": STDIN_DESCRIPTION,
        "environment": {
            key: env[key]
            for key in (
                "HOME", "XDG_CACHE_HOME", "HF_HOME", "HF_HUB_CACHE", "TRANSFORMERS_CACHE",
                "TORCH_HOME", "TMPDIR", "PYTHONNOUSERSITE", "JAVA_HOME", *OFFLINE_GUARDS.keys()
            )
        },
        "frozen_bindings": {
            "protocol_sha256": PROTOCOL_SHA256,
            "rights_gate_sha256": RIGHTS_GATE_SHA256,
            "parser_sha256": PARSER_SHA256,
            "universe_manifest_sha256": UNIVERSE_SHA256,
            "config_sha256": CONFIG_SHA256,
            "source_ontology_sha256": SOURCE_SHA256,
            "target_ontology_sha256": TARGET_SHA256,
            "model_weight_sha256": MODEL_WEIGHT_SHA256,
            "repaired_mapping_source_sha256": REPAIRED_MAPPING_SHA256,
        },
        "artifacts": artifacts,
        "artifacts_complete": artifacts_complete,
        "parser": {
            "exit_code": parser_exit_code,
            "terminal": parser_result.get("terminal"),
            "receipt_path": str(PARSER_RECEIPT),
            "receipt_sha256": sha256(PARSER_RECEIPT) if PARSER_RECEIPT.is_file() else None,
            "result": parser_result,
            "stdout_tail": parser_stdout,
            "stderr_tail": parser_stderr,
        },
        "logs": {
            "stdout": bounded_excerpt(STDOUT_LOG),
            "stderr": bounded_excerpt(STDERR_LOG),
        },
        "outcome_boundary": {
            "gold_or_reference_alignment_opened": False,
            "protected_outcome_opened": False,
            "scientific_scoring_performed": False,
            "correctness_performance_harm_coverage_transport_superiority_authority": False,
        },
        "readiness_after": {
            "native_smoke_ready": "3/3" if success else "2/3",
            "scientific_comparator_ready": "0/3",
        },
    }
    atomic_json(EXECUTION_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if success else 3


if __name__ == "__main__":
    raise SystemExit(main())
