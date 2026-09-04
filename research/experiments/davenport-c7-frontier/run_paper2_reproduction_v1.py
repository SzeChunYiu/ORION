#!/usr/bin/env python3
"""One-command clean-checkout reproduction for the reconciled Paper 2 stack."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "research/experiments/davenport-c7-frontier/PAPER2_REPRODUCIBILITY_MANIFEST_V1.json"
SAFE_CXX_FLAGS = ["-std=c++17", "-O3", "-Wall", "-Wextra"]
DEFAULT_TIMEOUT_SECONDS = 3600


class ReproductionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nested_get(value: Any, dotted: str) -> Any:
    current = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ReproductionError(f"missing expected field {dotted!r}")
        current = current[part]
    return current


def parse_last_json(stdout: str, label: str) -> dict[str, Any]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise ReproductionError(f"{label} produced no stdout")
    try:
        result = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise ReproductionError(f"{label} last line is not JSON: {lines[-1]!r}") from exc
    if not isinstance(result, dict):
        raise ReproductionError(f"{label} JSON result must be an object")
    return result


def run_command(command: list[str], label: str, timeout: int) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0:
        raise ReproductionError(
            f"{label} failed with rc={completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    result = parse_last_json(completed.stdout, label)
    return result, completed.stderr


def check_result(entry: dict[str, Any], result: dict[str, Any]) -> None:
    status = result.get("status")
    if "expected_status" in entry:
        if status != entry["expected_status"]:
            raise ReproductionError(
                f"{entry['id']} status mismatch: {status!r} != {entry['expected_status']!r}"
            )
    else:
        suffix = entry.get("status_suffix")
        if not isinstance(status, str) or not isinstance(suffix, str) or not status.endswith(suffix):
            raise ReproductionError(f"{entry['id']} status {status!r} does not end with {suffix!r}")

    expected = entry.get("expected", {})
    if not isinstance(expected, dict):
        raise ReproductionError(f"{entry['id']} expected block must be an object")
    for dotted, wanted in expected.items():
        actual = nested_get(result, dotted)
        if actual != wanted:
            raise ReproductionError(
                f"{entry['id']} field {dotted!r} mismatch: {actual!r} != {wanted!r}"
            )


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "ORION.PAPER2_REPRODUCIBILITY_MANIFEST_V1":
        raise ReproductionError("wrong manifest schema")
    if manifest.get("as_of_date") != "2026-09-04":
        raise ReproductionError("wrong manifest date")

    seen: set[str] = set()
    for group, path_key in (("python_executables", "path"), ("cpp_executables", "source")):
        entries = manifest.get(group)
        if not isinstance(entries, list) or not entries:
            raise ReproductionError(f"{group} must be a nonempty list")
        for entry in entries:
            if not isinstance(entry, dict):
                raise ReproductionError(f"{group} entry must be an object")
            entry_id = entry.get("id")
            if not isinstance(entry_id, str) or not entry_id or entry_id in seen:
                raise ReproductionError(f"invalid or duplicate executable id: {entry_id!r}")
            seen.add(entry_id)
            relative = entry.get(path_key)
            if not isinstance(relative, str) or relative.startswith("/") or ".." in Path(relative).parts:
                raise ReproductionError(f"unsafe executable path for {entry_id}")
            if not (ROOT / relative).is_file():
                raise ReproductionError(f"missing executable source for {entry_id}: {relative}")
            if "expected_status" not in entry and "status_suffix" not in entry:
                raise ReproductionError(f"missing status contract for {entry_id}")

    authority_files = manifest.get("authority_files")
    if not isinstance(authority_files, list) or len(authority_files) != 4:
        raise ReproductionError("authority_files must contain the four frozen surfaces")
    for relative in authority_files:
        if not isinstance(relative, str) or not (ROOT / relative).is_file():
            raise ReproductionError(f"missing authority file: {relative!r}")

    boundary = manifest.get("claim_boundary")
    if boundary != {
        "exact_D3_C7": "OPEN",
        "all_prime_first_corridor_support7": "OPEN",
        "novelty_priority": "CANNOT_CHECK",
        "top_specialist_state": "DEVELOPMENT_READY",
    }:
        raise ReproductionError("claim boundary drift")

    if any("NDEBUG" in flag for flag in SAFE_CXX_FLAGS):
        raise ReproductionError("assertion-suppressing C++ flag is forbidden")


def canonical_result_record(
    entry: dict[str, Any], result: dict[str, Any], source_path: Path
) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "source": str(source_path.relative_to(ROOT)),
        "source_sha256": sha256_file(source_path),
        "result": result,
    }


def reproduce(manifest: dict[str, Any], timeout: int) -> dict[str, Any]:
    validate_manifest(manifest)
    records: list[dict[str, Any]] = []

    for entry in manifest["python_executables"]:
        source = ROOT / entry["path"]
        result, _ = run_command([sys.executable, str(source)], entry["id"], timeout)
        check_result(entry, result)
        records.append(canonical_result_record(entry, result, source))
        print(f"GREEN {entry['id']}", file=sys.stderr, flush=True)

    compiler = shutil.which("g++")
    if compiler is None:
        raise ReproductionError("g++ is required for the independent C++ verifiers")
    compiler_version = subprocess.run(
        [compiler, "--version"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.splitlines()[0]

    with tempfile.TemporaryDirectory(prefix="orion-paper2-") as temp:
        tempdir = Path(temp)
        for entry in manifest["cpp_executables"]:
            source = ROOT / entry["source"]
            binary = tempdir / entry["id"]
            compile_command = [compiler, *SAFE_CXX_FLAGS, str(source), "-o", str(binary)]
            compiled = subprocess.run(
                compile_command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
            )
            if compiled.returncode != 0:
                raise ReproductionError(
                    f"compile failed for {entry['id']} rc={compiled.returncode}\n"
                    f"stdout:\n{compiled.stdout}\nstderr:\n{compiled.stderr}"
                )
            result, _ = run_command([str(binary)], entry["id"], timeout)
            check_result(entry, result)
            record = canonical_result_record(entry, result, source)
            record["compile_flags"] = SAFE_CXX_FLAGS
            records.append(record)
            print(f"GREEN {entry['id']}", file=sys.stderr, flush=True)

    authority_hashes = {
        relative: sha256_file(ROOT / relative)
        for relative in manifest["authority_files"]
    }
    canonical_records = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return {
        "status": "PAPER2_FULL_REPRODUCTION_GREEN",
        "schema": manifest["schema"],
        "executables_green": len(records),
        "python_executables_green": len(manifest["python_executables"]),
        "cpp_executables_green": len(manifest["cpp_executables"]),
        "python_version": platform.python_version(),
        "compiler_version": compiler_version,
        "cpp_assertions_enabled": True,
        "authority_file_sha256": authority_hashes,
        "records_sha256": hashlib.sha256(canonical_records).hexdigest(),
        "records": records,
        "authority": "reproduction receipt only; theorem and claim authority remain in the bound analytic, finite-certificate, and claim-ledger files",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-receipt",
        type=Path,
        help="optional path, relative to the repository root or absolute, for the full JSON receipt",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="per compile or executable timeout",
    )
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds must be positive")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise SystemExit("manifest root must be an object")

    try:
        receipt = reproduce(manifest, args.timeout_seconds)
    except (ReproductionError, subprocess.TimeoutExpired) as exc:
        print(f"PAPER2_REPRODUCTION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    serialized = json.dumps(receipt, sort_keys=True)
    if args.write_receipt is not None:
        target = args.write_receipt
        if not target.is_absolute():
            target = ROOT / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
