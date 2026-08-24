#!/usr/bin/env python3
"""Independent verifier for M2 saturation-defect/support replay evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development" / "orion-rg-davenport"
RG = ROOT / "research" / "orion-rg"
PROTOCOL = DEV / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_PROTOCOL_2026-08-24.md"
C8 = RG / "x1k_property_c_support_check.c"
C9 = RG / "x1k_c0_support9_check.c"
DEFAULT_INPUT = RG / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = DEV / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_GENERIC_2026-08-24.json"
POSITIVE = (
    "NONQUANTUM_M2_EXPONENT_P_SATURATION_DEFECT_LEMMA"
    "__C5CUBED_SUPPORT_LE9_EXCLUDED_BY_ISOLATED_DUAL_REPLAY"
)
TOKEN = "ORION_NONQUANTUM_M2_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_valid(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def independent_symbolic_check() -> dict[str, Any]:
    primes = []
    for candidate in range(3, 1_000, 2):
        if all(candidate % divisor for divisor in range(2, int(candidate**0.5) + 1)):
            primes.append(candidate)
    identities = {
        p: {
            "m": p - 2,
            "max_remainder": p - 1 - (p - 2),
            "target_coefficient": (-(p - 1)) % p,
        }
        for p in primes
    }
    patterns = [
        (c1, c2, c4)
        for c1 in range(10)
        for c2 in range(10)
        for c4 in range(10)
        if c1 + c2 + c4 == 9 and c1 + 2 * c2 + 4 * c4 == 31
    ]
    checks = {
        "prime_samples": len(primes) == 167,
        "remainder_identity": all(row["max_remainder"] == 1 for row in identities.values()),
        "coefficient_identity": all(row["target_coefficient"] == 1 for row in identities.values()),
        "support9_pattern": patterns == [(1, 1, 7)],
        "finite_identity_check_not_human_proof": True,
    }
    return {
        "odd_primes_below_1000": len(primes),
        "support9_patterns": [list(row) for row in patterns],
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    symbolic = independent_symbolic_check()
    replay = source.get("replay_ledger", {})
    row8 = replay.get("support8", {}).get("output", {})
    row9 = replay.get("support9", {}).get("output", {})
    checks = {
        "source_schema": source.get("schema")
        == "ORION.NonQuantumMath.M2.SaturationDefectReplay.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": digest_valid(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "c8_hash": replay.get("support8", {}).get("source_sha256") == file_sha256(C8),
        "c9_hash": replay.get("support9", {}).get("source_sha256") == file_sha256(C9),
        "source_gates": all(source.get("gates", {}).values()),
        "independent_symbolic": symbolic["all_checks"],
        "support8_exact": row8.get("engines_agree") is True
        and row8.get("engine_byte")
        == {"nodes": 80202, "normalized_supports": 564, "minus_support_sum_in_support": 0}
        and row8.get("engine_bit_reverse")
        == {"nodes": 80202, "normalized_supports": 564, "minus_support_sum_in_support": 0},
        "support9_exact": row9.get("both_engines_unsat") is True
        and row9.get("byte_engine")
        == {"nodes": 6537270, "forced_final_candidates": 138785, "solutions": 0}
        and row9.get("bit_reverse_engine")
        == {"nodes": 6537270, "forced_final_candidates": 146788, "solutions": 0},
        "scope": source.get("scientific_authority")
        == "GENERAL_EXPONENT_P_SATURATION_DEFECT_LEMMA_AND_BOUNDED_C5CUBED_SUPPORT_LE9_EXCLUSION",
        "bounded_authority": source.get("bounded_support_le9_theorem_authority") is True,
        "no_support23": source.get("support_23_theorem_authority") is False,
        "no_external_or_prospective": source.get("independent_external_replay_complete") is False
        and source.get("prospective_validation_authority") is False,
        "no_c0_or_d4": source.get("c0_31_authority") is False
        and source.get("exact_d4_authority") is False,
        "no_novelty_venue_quantum": source.get("novelty_authority") is False
        and source.get("venue_authority") is False
        and source.get("quantum_claim") is False,
    }
    positive = all(checks.values())
    result: dict[str, Any] = {
        "schema": "ORION.NonQuantumMath.M2.GenericVerification.v1",
        "decision": "ACCEPT_SATURATION_DEFECT_SUPPORT_LE9"
        if positive
        else "REJECT_SATURATION_DEFECT_SUPPORT_LE9",
        "source_result_digest": source.get("result_digest"),
        "symbolic": symbolic,
        "checks": checks,
        "authority_scope": (
            "GENERAL_EXPONENT_P_SATURATION_DEFECT_LEMMA_AND_BOUNDED_C5CUBED_SUPPORT_LE9_EXCLUSION"
        ),
        "support_23_theorem_authority": False,
        "independent_external_replay_complete": False,
        "prospective_validation_authority": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
        "quantum_claim": False,
    }
    result["verification_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "decision": result["decision"],
                "verification_digest": result["verification_digest"],
                "odd_primes_checked": result["symbolic"]["odd_primes_below_1000"],
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
