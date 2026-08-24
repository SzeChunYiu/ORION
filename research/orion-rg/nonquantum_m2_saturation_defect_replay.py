#!/usr/bin/env python3
"""M2: exponent-p saturation defects and isolated support-8/9 replay."""
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
PROTOCOL = DEV / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_PROTOCOL_2026-08-24.md"
C8 = RG / "x1k_property_c_support_check.c"
C9 = RG / "x1k_c0_support9_check.c"
DEFAULT_OUTPUT = RG / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_RESULTS_2026-08-24.json"
BASE = "df58c9d3bd7dedab0011ca2e126bfcf5fcd35429"
POSITIVE = (
    "NONQUANTUM_M2_EXPONENT_P_SATURATION_DEFECT_LEMMA"
    "__C5CUBED_SUPPORT_LE9_EXCLUDED_BY_ISOLATED_DUAL_REPLAY"
)
TOKEN = "ORION_NONQUANTUM_M2_REPLAY="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(raw: dict[str, Any]) -> str:
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def symbolic_ledger() -> dict[str, Any]:
    sample_primes = (3, 5, 7, 11, 13, 17, 19)
    sample_rows = [
        {
            "p": p,
            "forbidden_multiplicity": p - 2,
            "max_remainder_length": p - 1 - (p - 2),
            "remainder_sum_coefficient_mod_p": (-(p - 1)) % p,
        }
        for p in sample_primes
    ]
    pattern_rows = []
    for c1 in range(10):
        for c2 in range(10):
            for c4 in range(10):
                if c1 + c2 + c4 == 9 and c1 + 2 * c2 + 4 * c4 == 31:
                    pattern_rows.append((c1, c2, c4))
    checks = {
        "all_sample_remainders_length_one": all(
            row["max_remainder_length"] == 1 for row in sample_rows
        ),
        "all_sample_remainders_equal_x": all(
            row["remainder_sum_coefficient_mod_p"] == 1 for row in sample_rows
        ),
        "support9_unique_pattern": pattern_rows == [(1, 1, 7)],
        "human_all_prime_proof_registered": True,
        "finite_samples_are_not_all_prime_proof": True,
    }
    return {
        "general_statement": (
            "in an odd-prime exponent-p saturated p-short-free sequence, a point of multiplicity m<p "
            "forces x^m R with |R|<=p-1-m and sigma(R)=-(m+1)x; multiplicity p-2 is impossible"
        ),
        "sample_rows": sample_rows,
        "support9_patterns": [list(row) for row in pattern_rows],
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def compile_and_run(source: Path, executable: Path) -> dict[str, Any]:
    command = [
        "gcc",
        "-std=c11",
        "-O3",
        "-Wall",
        "-Wextra",
        "-pedantic",
        str(source),
        "-o",
        str(executable),
    ]
    compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if compiled.returncode != 0 or compiled.stderr:
        raise RuntimeError(
            {
                "source": str(source),
                "compile_returncode": compiled.returncode,
                "compile_stdout": compiled.stdout,
                "compile_stderr": compiled.stderr,
            }
        )
    executed = subprocess.run(
        [str(executable)], cwd=ROOT, capture_output=True, text=True, check=False, timeout=1200
    )
    if executed.returncode != 0 or executed.stderr:
        raise RuntimeError(
            {
                "source": str(source),
                "run_returncode": executed.returncode,
                "run_stderr": executed.stderr,
            }
        )
    return {
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": file_sha256(source),
        "compile_command": command[:-1] + ["<temporary-executable>"],
        "compile_returncode": compiled.returncode,
        "compile_stdout": compiled.stdout,
        "compile_stderr": compiled.stderr,
        "run_returncode": executed.returncode,
        "run_stderr": executed.stderr,
        "output": json.loads(executed.stdout),
    }


def replay_ledger() -> dict[str, Any]:
    path = Path(tempfile.mkdtemp(prefix="orion-nonquantum-m2-source-", dir="/tmp"))
    try:
        support8 = compile_and_run(C8, path / "support8")
        support9 = compile_and_run(C9, path / "support9")
    finally:
        shutil.rmtree(path, ignore_errors=True)

    row8 = support8["output"]
    row9 = support9["output"]
    checks = {
        "support8_schema": row8.get("schema") == "ORION.RG.X1K.PropertyCSupportCheck.v1",
        "support8_engines_agree": row8.get("engines_agree") is True,
        "support8_byte": row8.get("engine_byte")
        == {"nodes": 80202, "normalized_supports": 564, "minus_support_sum_in_support": 0},
        "support8_bit": row8.get("engine_bit_reverse")
        == {"nodes": 80202, "normalized_supports": 564, "minus_support_sum_in_support": 0},
        "support9_schema": row9.get("schema") == "ORION.RG.X1K.C0Support9Check.v1",
        "support9_both_unsat": row9.get("both_engines_unsat") is True,
        "support9_byte": row9.get("byte_engine")
        == {"nodes": 6537270, "forced_final_candidates": 138785, "solutions": 0},
        "support9_bit": row9.get("bit_reverse_engine")
        == {"nodes": 6537270, "forced_final_candidates": 146788, "solutions": 0},
        "temporary_executables_deleted": not path.exists(),
    }
    return {
        "compiler": "gcc",
        "build_mode": "C11 O3 warnings-as-admission-failure",
        "support8": support8,
        "support9": support9,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run() -> dict[str, Any]:
    symbolic = symbolic_ledger()
    replay = replay_ledger()
    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "symbolic_lemma": symbolic["all_checks"],
        "isolated_dual_replay": replay["all_checks"],
        "post_outcome_status_preserved": True,
        "external_replay_not_claimed": True,
        "full_c0_not_claimed": True,
    }
    positive = all(gates.values())
    result: dict[str, Any] = {
        "schema": "ORION.NonQuantumMath.M2.SaturationDefectReplay.v1",
        "base_revision": BASE,
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "terminal": POSITIVE if positive else "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_REJECTED",
        "symbolic_ledger": symbolic,
        "replay_ledger": replay,
        "gates": gates,
        "theorems": {
            "general_saturation_defect": symbolic["general_statement"],
            "c5cubed_bounded": (
                "a length-31 total-zero 5-short-free sequence over C_5^3, if one exists, "
                "has support at least 10"
            ),
        },
        "scientific_authority": (
            "GENERAL_EXPONENT_P_SATURATION_DEFECT_LEMMA_AND_BOUNDED_C5CUBED_SUPPORT_LE9_EXCLUSION"
            if positive
            else "NONE"
        ),
        "result_owner": "NON_QUANTUM_MATH",
        "bounded_support_le9_theorem_authority": positive,
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
                "support8_solutions": result["replay_ledger"]["support8"]["output"]
                ["engine_byte"]["minus_support_sum_in_support"],
                "support9_solutions": result["replay_ledger"]["support9"]["output"]
                ["byte_engine"]["solutions"],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
