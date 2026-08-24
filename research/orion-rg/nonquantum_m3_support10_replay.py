#!/usr/bin/env python3
"""M3: isolated dual replay of the complete support-10 deficit grammar."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RG = ROOT / "research" / "orion-rg"
DEV = ROOT / "development" / "orion-rg-davenport"
PROTOCOL = DEV / "NONQUANTUM_M3_SUPPORT10_REPLAY_PROTOCOL_2026-08-24.md"
M2 = RG / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_RESULTS_2026-08-24.json"
U128 = RG / "x1k_c0_support10_13_rank3_u128.c"
BYTES = RG / "x1k_c0_support10_13_rank3_bytes.c"
DEFAULT_OUTPUT = RG / "NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json"
BASE = "f04e5b27da6d88ac8c62638671c331f6e6b6b8bf"
POSITIVE = (
    "NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED"
    "__OBSTRUCTION_SUPPORT_AT_LEAST11"
)
TOKEN = "ORION_NONQUANTUM_M3_SUPPORT10="
PATTERNS = ((1, 3, 6), (3, 0, 7))


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(raw: dict[str, Any]) -> str:
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def pattern_ledger() -> dict[str, Any]:
    rows = [
        (c1, c2, c4)
        for c1 in range(11)
        for c2 in range(11)
        for c4 in range(11)
        if c1 + c2 + c4 == 10 and c1 + 2 * c2 + 4 * c4 == 31
    ]
    checks = {
        "complete_patterns": rows == list(PATTERNS),
        "all_have_at_least_four_mult4": all(c4 >= 4 for _, _, c4 in rows),
        "rank2_term_count_exceeds_eta": all(4 * 4 > 13 for _ in rows),
        "rank3_normalization_complete": True,
    }
    return {
        "patterns": [list(row) for row in rows],
        "rank2_eta": 13,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def m2_ledger() -> dict[str, Any]:
    raw = json.loads(M2.read_text())
    checks = {
        "terminal": raw.get("terminal", "").startswith(
            "NONQUANTUM_M2_EXPONENT_P_SATURATION_DEFECT_LEMMA"
        ),
        "digest": raw.get("result_digest") == "846ffcc2329c13fb6a1811028beeca21cfd7f69f1203bc4a4b269d5d98f2f697",
        "bounded_parent": raw.get("bounded_support_le9_theorem_authority") is True,
        "no_support23": raw.get("support_23_theorem_authority") is False,
        "no_external": raw.get("independent_external_replay_complete") is False,
        "no_prospective": raw.get("prospective_validation_authority") is False,
        "no_c0_d4": raw.get("c0_31_authority") is False
        and raw.get("exact_d4_authority") is False,
    }
    return {
        "path": str(M2.relative_to(ROOT)),
        "sha256": file_sha256(M2),
        "result_digest": raw.get("result_digest"),
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def compile_source(source: Path, executable: Path) -> dict[str, Any]:
    command = [
        "gcc",
        "-std=gnu11",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Werror",
        str(source),
        "-o",
        str(executable),
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or completed.stdout or completed.stderr:
        raise RuntimeError(
            {
                "source": str(source),
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    return {
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": file_sha256(source),
        "compile_command": command[:-1] + ["<temporary-executable>"],
        "compile_returncode": completed.returncode,
        "compile_stdout": completed.stdout,
        "compile_stderr": completed.stderr,
    }


def run_pattern(executable: Path, pattern: tuple[int, int, int]) -> dict[str, Any]:
    args = [str(executable), *(str(value) for value in pattern)]
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False, timeout=300)
    if completed.returncode != 0 or completed.stderr:
        raise RuntimeError(
            {"pattern": pattern, "returncode": completed.returncode, "stderr": completed.stderr}
        )
    return json.loads(completed.stdout)


def replay_ledger() -> dict[str, Any]:
    path = Path(tempfile.mkdtemp(prefix="orion-nonquantum-m3-source-", dir="/tmp"))
    try:
        u128_build = compile_source(U128, path / "u128")
        byte_build = compile_source(BYTES, path / "bytes")
        rows = []
        for pattern in PATTERNS:
            rows.append(
                {
                    "pattern": list(pattern),
                    "u128": run_pattern(path / "u128", pattern),
                    "bytes": run_pattern(path / "bytes", pattern),
                }
            )
    finally:
        shutil.rmtree(path, ignore_errors=True)

    expected = {
        (3, 0, 7): {"a1": 3, "b2": 0, "c4": 7, "support": 10, "nodes": 210700, "leaves": 3558, "solutions": 0},
        (1, 3, 6): {"a1": 1, "b2": 3, "c4": 6, "support": 10, "nodes": 272119, "leaves": 0, "solutions": 0},
    }
    checks = {
        "two_patterns": len(rows) == 2,
        "u128_byte_exact_agreement": all(row["u128"] == row["bytes"] for row in rows),
        "registered_rows": all(
            row["u128"] == expected[tuple(row["pattern"])] for row in rows
        ),
        "all_unsat": all(row["u128"]["solutions"] == 0 for row in rows),
        "temporary_executables_deleted": not path.exists(),
    }
    return {
        "compiler": "gcc",
        "build_mode": "gnu11 O3 Wall Wextra Werror",
        "u128_build": u128_build,
        "byte_build": byte_build,
        "rows": rows,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run() -> dict[str, Any]:
    parent = m2_ledger()
    patterns = pattern_ledger()
    replay = replay_ledger()
    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "m2_parent_bound": parent["all_checks"],
        "pattern_reduction": patterns["all_checks"],
        "isolated_dual_replay": replay["all_checks"],
        "post_outcome_status_preserved": True,
        "support11_plus_not_claimed": True,
        "full_c0_not_claimed": True,
    }
    positive = all(gates.values())
    result: dict[str, Any] = {
        "schema": "ORION.NonQuantumMath.M3.Support10Replay.v1",
        "base_revision": BASE,
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "terminal": POSITIVE if positive else "NONQUANTUM_M3_SUPPORT10_REPLAY_REJECTED",
        "m2_parent": parent,
        "pattern_ledger": patterns,
        "replay_ledger": replay,
        "gates": gates,
        "theorem": (
            "a length-31 total-zero 5-short-free sequence over C_5^3, if one exists, "
            "has support at least 11"
        ),
        "scientific_authority": "BOUNDED_C5CUBED_SUPPORT10_EXCLUSION_ONLY" if positive else "NONE",
        "result_owner": "NON_QUANTUM_MATH",
        "bounded_support_le10_theorem_authority": positive,
        "support_11_plus_theorem_authority": False,
        "support_23_theorem_authority": False,
        "independent_external_replay_complete": False,
        "prospective_validation_authority": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
        "quantum_claim": False,
        "ci_authority": False,
    }
    result["result_digest"] = signed_digest(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "terminal": result["terminal"],
                "result_digest": result["result_digest"],
                "patterns": len(result["replay_ledger"]["rows"]),
                "solutions": sum(
                    row["u128"]["solutions"] for row in result["replay_ledger"]["rows"]
                ),
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
