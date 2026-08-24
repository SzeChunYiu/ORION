#!/usr/bin/env python3
"""Execute the once-frozen P3 V17 BERTMap and common-scoring contract."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import importlib.metadata as metadata
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_V17.json"
PREFLIGHT = ROOT / "RUNTIME_PREFLIGHT_V17.json"
LOCK = ROOT / "ATTEMPT_LOCK_V17.json"
STDOUT = ROOT / "BERTMAP_STDOUT_V17.log"
STDERR = ROOT / "BERTMAP_STDERR_V17.log"
PARSER_STDOUT = ROOT / "PARSER_STDOUT_V17.log"
PARSER_STDERR = ROOT / "PARSER_STDERR_V17.log"
PARSER_RECEIPT = ROOT / "PARSER_RECEIPT_V17.json"
RESULT = ROOT / "BERTMAP_RESULT_V17.json"
TERMINAL = ROOT / "TERMINAL_V17.txt"
ORIGINAL = ROOT / "runtime-interface/ORIGINAL_WRAPPED_REPAIRED_MAPPINGS_V17.tsv"
RUNTIME_ROOT = Path("/Volumes/P3V17_RUNTIME")
PYTHON = RUNTIME_ROOT / "venv/bin/python"
SOURCE_SCRIPT = RUNTIME_ROOT / "source/scripts/bertmap.py"
OUTPUT_ROOT = RUNTIME_ROOT / "output/bertmap-out"
MATCH = OUTPUT_ROOT / "bertmap/match"
REQUIRED = (
    "raw_mappings.json",
    "raw_mappings.tsv",
    "extended_mappings.tsv",
    "filtered_mappings.tsv",
    "repaired_mappings.tsv",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def regular(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return False
    return stat.S_ISREG(mode) and not path.is_symlink()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def terminate(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def inventory(directory: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for name in REQUIRED:
        path = directory / name
        ok = regular(path)
        result[name] = {
            "path": str(path),
            "regular_non_symlink": ok,
            "bytes": path.stat().st_size if ok else None,
            "sha256": sha256(path) if ok else None,
        }
    return result


def decode_repaired(protocol: dict[str, object]) -> dict[str, object]:
    universe = json.loads((ROOT / "UNIVERSE_MANIFEST_V17.json").read_text())
    sets = {
        "source": set(universe["expected_source_iris"]),
        "target": set(universe["expected_target_iris"]),
    }
    grammar = re.compile(protocol["typed_decoder"]["anchored_regex"])

    def decode(text: str, role: str) -> str:
        match = grammar.fullmatch(text)
        if match is None:
            raise ValueError(f"{role} surface string violates frozen typed grammar")
        decoded = match.group("ontology_iri") + match.group("fragment")
        if decoded not in sets[role]:
            raise ValueError(f"{role} decoded IRI is outside frozen role universe")
        return decoded

    wrapped = MATCH / "repaired_mappings.tsv"
    shutil.copyfile(wrapped, ORIGINAL)
    with wrapped.open(newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t", strict=True))
    if not rows or rows[0] != ["SrcEntity", "TgtEntity", "Score"] or any(len(row) != 3 for row in rows[1:]):
        raise ValueError("wrapped repaired table shape mismatch")
    decoded_rows: list[tuple[str, str, str]] = []
    source_map: dict[str, str] = {}
    target_map: dict[str, str] = {}
    for source, target, score in rows[1:]:
        decoded_source = decode(source, "source")
        decoded_target = decode(target, "target")
        source_map[source] = decoded_source
        target_map[target] = decoded_target
        decoded_rows.append((decoded_source, decoded_target, score))
    source_injective = len(set(source_map)) == len(set(source_map.values()))
    target_injective = len(set(target_map)) == len(set(target_map.values()))
    if not source_injective or not target_injective:
        raise ValueError("typed decoder is not injective on observed strings")

    decoded_dir = ROOT / "decoded-interface"
    for name in REQUIRED[:-1]:
        shutil.copyfile(MATCH / name, decoded_dir / name)
    decoded_path = decoded_dir / "repaired_mappings.tsv"
    with decoded_path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["SrcEntity", "TgtEntity", "Score"])
        writer.writerows(decoded_rows)

    parser_command = [
        str(PYTHON),
        str(ROOT / "bertmap_native_parser_v7.py"),
        "--output-dir",
        str(decoded_dir),
        "--manifest",
        str(ROOT / "UNIVERSE_MANIFEST_V17.json"),
        "--write-receipt",
        str(PARSER_RECEIPT),
    ]
    completed = subprocess.run(parser_command, cwd=ROOT, capture_output=True, timeout=120, check=False)
    PARSER_STDOUT.write_bytes(completed.stdout)
    PARSER_STDERR.write_bytes(completed.stderr)
    parser_result = json.loads(PARSER_RECEIPT.read_text()) if PARSER_RECEIPT.is_file() else {}
    artifacts = inventory(decoded_dir)
    passed = (
        completed.returncode == 0
        and parser_result.get("terminal") == "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS"
        and all(item["regular_non_symlink"] for item in artifacts.values())
    )
    return {
        "pass": passed,
        "input_rows": len(rows) - 1,
        "decoded_rows": len(decoded_rows),
        "exact_source_members": sum(source in sets["source"] for source, _target, _score in decoded_rows),
        "exact_target_members": sum(target in sets["target"] for _source, target, _score in decoded_rows),
        "source_injective": source_injective,
        "target_injective": target_injective,
        "original_wrapped": {"path": str(ORIGINAL), "bytes": ORIGINAL.stat().st_size, "sha256": sha256(ORIGINAL)},
        "decoded_repaired": {"path": str(decoded_path), "bytes": decoded_path.stat().st_size, "sha256": sha256(decoded_path)},
        "parser": {"command": parser_command, "exit_code": completed.returncode, "receipt": parser_result},
        "five_artifact_interface": artifacts,
    }


def main() -> int:
    stale = [PREFLIGHT, LOCK, STDOUT, STDERR, PARSER_STDOUT, PARSER_STDERR, PARSER_RECEIPT, RESULT, TERMINAL, ORIGINAL]
    if any(path.exists() for path in stale) or any((ROOT / "decoded-interface").iterdir()):
        raise SystemExit("REFUSE_RERUN_OR_STALE_V17_ARTIFACT")
    protocol = json.loads(PROTOCOL.read_text())
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    check("runner_identity", sha256(Path(__file__)) == protocol["frozen_code"]["run_bertmap_v17.py"])
    for name, expected in protocol["frozen_code"].items():
        if name == "run_bertmap_v17.py":
            continue
        check(f"code_{name}", sha256(ROOT / name) == expected)
    for name, spec in protocol["frozen_inputs"].items():
        path = Path(spec["path"])
        check(f"input_{name}", regular(path) and sha256(path) == spec["sha256"], str(path))
    for name, spec in protocol["runtime"]["critical_files"].items():
        path = Path(spec["path"])
        check(f"runtime_{name}", regular(path) and sha256(path) == spec["sha256"], str(path))
    expected_sbom = json.loads(Path(protocol["runtime"]["expected_distribution_sbom"]["path"]).read_text())
    expected_versions = {row["name"].lower(): row["version"] for row in expected_sbom["distributions"]}
    observed_versions = {
        dist.metadata["Name"].lower(): dist.version
        for dist in metadata.distributions(path=[str(RUNTIME_ROOT / "venv/lib/python3.10/site-packages")])
        if dist.metadata["Name"]
    }
    check("distribution_count", len(observed_versions) == 126, len(observed_versions))
    check("distribution_versions", observed_versions == expected_versions)
    check("output_absent", not OUTPUT_ROOT.exists() or not any(OUTPUT_ROOT.iterdir()))
    check("reference_not_semantically_opened", True, "hash-only binding before both outputs")
    authorized = all(item["pass"] for item in checks)
    preflight = {
        "schema_version": "orion.p3.oaei-bertmap.runtime-preflight.v17",
        "evaluated_at_utc": now(),
        "protocol_sha256": sha256(PROTOCOL),
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "native_execution_authorized": authorized,
        "terminal": "P3_V17_RUNTIME_AND_OUTCOME_BLIND_IDENTITY_PREFLIGHT_PASS" if authorized else "P3_V17_RUNTIME_OR_IDENTITY_PREFLIGHT_FAIL",
    }
    PREFLIGHT.write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n")
    if not authorized:
        raise SystemExit(preflight["terminal"])

    OUTPUT_ROOT.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(PYTHON),
        str(SOURCE_SCRIPT),
        "-s",
        str(ROOT / "inputs/SOURCE_BASE_BOUND_V17.rdf"),
        "-t",
        str(ROOT / "inputs/TARGET_BASE_BOUND_V17.rdf"),
        "-c",
        str(ROOT / "BERTMAP_CONFIG_V17.yaml"),
    ]
    started = now()
    LOCK.write_text(
        json.dumps(
            {
                "schema_version": "orion.p3.oaei-bertmap.attempt-lock.v17",
                "protocol_sha256": sha256(PROTOCOL),
                "preflight_sha256": sha256(PREFLIGHT),
                "started_at_utc": started,
                "native_attempts": 1,
                "retries": 0,
                "command": command,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    java_home = Path(protocol["runtime"]["java_home"])
    cache = RUNTIME_ROOT / "cache"
    temp = RUNTIME_ROOT / "tmp"
    for path in (cache, temp, cache / "hf", cache / "transformers", cache / "torch", RUNTIME_ROOT / "home"):
        path.mkdir(parents=True, exist_ok=True)
    environment = {
        "PATH": f"{PYTHON.parent}:{java_home / 'bin'}:/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(RUNTIME_ROOT / "home"),
        "TMPDIR": str(temp),
        "JAVA_HOME": str(java_home),
        "PYTHONNOUSERSITE": "1",
        "PYTHONUNBUFFERED": "1",
        "HF_HOME": str(cache / "hf"),
        "TRANSFORMERS_CACHE": str(cache / "transformers"),
        "TORCH_HOME": str(cache / "torch"),
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "TOKENIZERS_PARALLELISM": "false",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
    }
    start_ns = time.monotonic_ns()
    timed_out = False
    launch_error = None
    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=environment,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(b"2g\n", timeout=protocol["attempt"]["timeout_seconds"])
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate(process)
            stdout, stderr = process.communicate()
        exit_code = process.returncode
    except Exception as exc:  # retained verbatim in result
        stdout = b""
        stderr = b""
        exit_code = None
        launch_error = f"{type(exc).__name__}: {exc}"
    wall_ns = time.monotonic_ns() - start_ns
    STDOUT.write_bytes(stdout)
    STDERR.write_bytes(stderr)
    stdout_text = stdout.decode("utf-8", errors="replace")
    direct_codes = [int(value) for value in re.findall(r"^ORION_LOGMAP_DIRECT_CHILD_EXIT_CODE=(-?\d+)$", stdout_text, re.M)]
    effective_commands = [line for line in stdout_text.splitlines() if line.startswith("ORION_LOGMAP_EFFECTIVE_COMMAND=")]
    artifacts = inventory(MATCH)
    five = all(item["regular_non_symlink"] for item in artifacts.values())
    direct_ok = direct_codes == [0] and len(effective_commands) == 1
    native_success = exit_code == 0 and not timed_out and launch_error is None and five and direct_ok

    decoder: dict[str, object]
    if native_success:
        try:
            decoder = decode_repaired(protocol)
        except Exception as exc:
            decoder = {"pass": False, "error": f"{type(exc).__name__}: {exc}"}
    else:
        decoder = {"pass": False, "error": "native success gate not satisfied"}
    typed_pass = bool(decoder.get("pass"))
    if native_success and typed_pass:
        terminal = "P3_V17_BERTMAP_NATIVE_AND_TYPED_DECODER_PASS__SAME_UNIVERSE_OUTPUT_FROZEN__COMMON_REFERENCE_SCORING_AUTHORIZED"
    elif native_success:
        terminal = "P3_V17_BERTMAP_NATIVE_PASS__TYPED_DECODER_OR_STRUCTURAL_CONTRACT_FAIL__COMMON_SCORING_NOT_AUTHORIZED"
    else:
        terminal = "P3_V17_BERTMAP_NATIVE_ATTEMPT_FAIL__NO_RETRY__COMMON_SCORING_NOT_AUTHORIZED"
    result = {
        "schema_version": "orion.p3.oaei-bertmap.execution-result.v17",
        "protocol_id": protocol["protocol_id"],
        "authority": "ONE_PUBLIC_PROVIDER_NATIVE_CASE_MATCHER_OUTPUT_AND_INTERFACE_CONFORMANCE_ONLY_BEFORE_COMMON_SCORING",
        "started_at_utc": started,
        "finished_at_utc": now(),
        "command": command,
        "environment": environment,
        "stdin_utf8": "2g\\n",
        "attempts": 1,
        "retries": 0,
        "timeout_seconds": protocol["attempt"]["timeout_seconds"],
        "timed_out": timed_out,
        "launch_error": launch_error,
        "native_exit_code": exit_code,
        "wall_nanoseconds": wall_ns,
        "wall_seconds": wall_ns / 1e9,
        "stdout": {"path": str(STDOUT), "bytes": len(stdout), "sha256": sha256(STDOUT)},
        "stderr": {"path": str(STDERR), "bytes": len(stderr), "sha256": sha256(STDERR)},
        "direct_logmap_child_exit_codes": direct_codes,
        "effective_logmap_commands": effective_commands,
        "native_artifacts": artifacts,
        "five_regular_non_symlink_artifacts": five,
        "native_success": native_success,
        "typed_decoder": decoder,
        "typed_decoder_pass": typed_pass,
        "decoded_repaired_artifact": decoder.get("decoded_repaired"),
        "reference_semantically_opened": False,
        "common_scoring_authorized": native_success and typed_pass,
        "terminal": terminal,
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    TERMINAL.write_text(terminal + "\n")
    print(terminal)
    if not (native_success and typed_pass):
        return 1

    evaluator = subprocess.run(
        [str(PYTHON), str(ROOT / "common_pair_evaluator_v17.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    (ROOT / "COMMON_SCORING_STDOUT_V17.log").write_text(evaluator.stdout)
    (ROOT / "COMMON_SCORING_STDERR_V17.log").write_text(evaluator.stderr)
    if evaluator.returncode != 0:
        print(evaluator.stderr, end="")
        return evaluator.returncode
    print(evaluator.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
