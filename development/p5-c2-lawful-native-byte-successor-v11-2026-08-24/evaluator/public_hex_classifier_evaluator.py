#!/usr/bin/env python3
"""Frozen public-development evaluator for the P5 C2 V11 successor.

This evaluator is deliberately separate from the route gate.  The V11 route
gate proves that the evaluator bytes are mounted outside candidate write
authority but does not invoke this file.  A later public-development run may
invoke it explicitly; such a run is not confirmatory or protected evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


TARGET = Path("src/main/java/org/apache/commons/lang3/math/NumberUtils.java")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def java_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def build_probe(cases: list[dict]) -> str:
    values = ", ".join(java_string(row["input"]) for row in cases)
    return f"""import org.apache.commons.lang3.math.NumberUtils;

public final class P5C2V11Probe {{
  public static void main(String[] args) {{
    String[] values = new String[] {{{values}}};
    for (String value : values) {{
      Number observed = NumberUtils.createNumber(value);
      System.out.println(value + "\\t" + observed.getClass().getSimpleName());
    }}
  }}
}}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--runtime-lock", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_root = args.source_root.resolve(strict=True)
    cases_path = args.cases.resolve(strict=True)
    runtime_path = args.runtime_lock.resolve(strict=True)
    output = args.output.resolve()
    target = source_root / TARGET
    if not target.is_file():
        raise RuntimeError(f"mutable target missing: {target}")

    runtime = load_json(runtime_path)
    javac = Path(runtime["executables"]["javac"]["path"])
    java = Path(runtime["executables"]["java"]["path"])
    for name, binary in (("javac", javac), ("java", java)):
        expected = runtime["executables"][name]["sha256"]
        if not binary.is_file() or sha256(binary) != expected:
            raise RuntimeError(f"pinned {name} identity mismatch")

    case_doc = load_json(cases_path)
    cases = case_doc["cases"]
    if case_doc["authority"] != "PUBLIC_DEVELOPMENT_ONLY":
        raise RuntimeError("case authority widened")
    if not cases or len({row["input"] for row in cases}) != len(cases):
        raise RuntimeError("public cases must be nonempty and input-unique")

    with tempfile.TemporaryDirectory(prefix="p5-c2-v11-evaluator-") as raw_tmp:
        tmp = Path(raw_tmp)
        classes = tmp / "classes"
        classes.mkdir()
        probe = tmp / "P5C2V11Probe.java"
        probe.write_text(build_probe(cases), encoding="utf-8")
        env = {
            "HOME": str(tmp),
            "JAVA_HOME": runtime["java_home"],
            "LANG": "C",
            "LC_ALL": "C",
            "PATH": "",
            "TMPDIR": str(tmp),
        }
        compile_run = subprocess.run(
            [
                str(javac),
                "-encoding",
                "UTF-8",
                "-d",
                str(classes),
                "-sourcepath",
                str(source_root / "src/main/java"),
                str(target),
                str(probe),
            ],
            cwd=tmp,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if compile_run.returncode != 0:
            raise RuntimeError("pinned javac failed: " + compile_run.stderr[-4000:])
        execute_run = subprocess.run(
            [str(java), "-cp", str(classes), "P5C2V11Probe"],
            cwd=tmp,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if execute_run.returncode != 0:
            raise RuntimeError("pinned java failed: " + execute_run.stderr[-4000:])

    observed = {}
    for line in execute_run.stdout.splitlines():
        value, class_name = line.split("\t", 1)
        observed[value] = class_name
    rows = []
    for case in cases:
        actual = observed.get(case["input"])
        rows.append(
            {
                "case_id": case["case_id"],
                "input": case["input"],
                "expected_class": case["expected_class"],
                "observed_class": actual,
                "passed": actual == case["expected_class"],
            }
        )
    result = {
        "schema_version": "orion.p5.c2.public-hex-evaluator-result.v11",
        "authority": "PUBLIC_DEVELOPMENT_ONLY__NOT_PROTECTED_OR_CONFIRMATORY",
        "source_target_sha256": sha256(target),
        "cases_sha256": sha256(cases_path),
        "runtime_lock_sha256": sha256(runtime_path),
        "case_count": len(rows),
        "passed_count": sum(row["passed"] for row in rows),
        "all_passed": all(row["passed"] for row in rows),
        "cases": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
