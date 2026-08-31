#!/usr/bin/env python3
"""Compile and replay the public support-eight through support-ten engines."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent

SOURCES = {
    "support_eight": "support_eight_search.c",
    "support_nine": "support_nine_search.c",
    "support_ten_bytes": "support_ten_search_bytes.c",
    "support_ten_u128": "support_ten_search_u128.c",
}

EXPECTED_FILE = HERE / "bounded_search_expected.json"


def run(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def contains(expected: object, actual: object) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and contains(value, actual[key])
            for key, value in expected.items()
        )
    return expected == actual


def compile_engines(compiler: str, destination: Path) -> tuple[dict[str, Path], dict[str, object]]:
    executables: dict[str, Path] = {}
    receipts: dict[str, object] = {}
    for name, source_name in SOURCES.items():
        source = HERE / source_name
        executable = destination / name
        command = [compiler, "-O3", "-std=c11", "-Wall", "-Wextra", str(source), "-o", str(executable)]
        completed = run(command, timeout=60)
        receipts[name] = {
            "returncode": completed.returncode,
            "stderr": completed.stderr.strip(),
        }
        if completed.returncode == 0:
            executables[name] = executable
    return executables, receipts


def parse_json_run(command: list[str], *, timeout: int) -> tuple[dict[str, object], dict[str, object]]:
    completed = run(command, timeout=timeout)
    receipt: dict[str, object] = {
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        return {}, receipt
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        receipt["json_error"] = str(error)
        return {}, receipt
    receipt["json_parsed"] = True
    return payload, receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default=os.environ.get("CC", "cc"))
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args(argv)

    compiler = shutil.which(args.compiler)
    if compiler is None:
        print(json.dumps({"all_checks": False, "error": f"compiler not found: {args.compiler}"}, indent=2))
        return 2

    missing = [name for name in SOURCES.values() if not (HERE / name).is_file()]
    if not EXPECTED_FILE.is_file():
        missing.append(EXPECTED_FILE.name)
    if missing:
        print(json.dumps({"all_checks": False, "missing_sources": missing}, indent=2))
        return 2

    expected = json.loads(EXPECTED_FILE.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="bounded-search-replay-") as temporary:
        executables, compile_receipts = compile_engines(compiler, Path(temporary))
        runs: dict[str, object] = {}
        checks: dict[str, bool] = {
            "all_four_engines_compile": len(executables) == len(SOURCES),
        }

        if "support_eight" in executables:
            payload, receipt = parse_json_run([str(executables["support_eight"])], timeout=args.timeout)
            runs["support_eight"] = receipt
            checks["support_eight_matches"] = contains(expected["support_eight"], payload)

        if "support_nine" in executables:
            payload, receipt = parse_json_run([str(executables["support_nine"])], timeout=args.timeout)
            runs["support_nine"] = receipt
            checks["support_nine_matches"] = contains(expected["support_nine"], payload)

        for pattern_key, expected_row in expected["support_ten"].items():
            pattern = tuple(map(int, pattern_key.split("_")))
            outputs: dict[str, dict[str, object]] = {}
            for engine_name in ("support_ten_bytes", "support_ten_u128"):
                if engine_name not in executables:
                    continue
                payload, receipt = parse_json_run(
                    [str(executables[engine_name]), *map(str, pattern)],
                    timeout=args.timeout,
                )
                runs[f"{engine_name}_{pattern}"] = receipt
                outputs[engine_name] = payload
            check_name = "support_ten_" + "_".join(map(str, pattern)) + "_matches"
            checks[check_name] = (
                len(outputs) == 2
                and all(contains(expected_row, payload) for payload in outputs.values())
                and outputs["support_ten_bytes"] == outputs["support_ten_u128"]
            )

    result = {
        "schema": "conditional-width-one-bounds.same-package-replay.v1",
        "scope": (
            "Same-package bounded-search reproducibility only; not independent replication "
            "and not authority for support above ten or the unresolved exact constant."
        ),
        "compiler": compiler,
        "compile": compile_receipts,
        "runs": runs,
        "checks": checks,
        "all_checks": all(checks.values()),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
