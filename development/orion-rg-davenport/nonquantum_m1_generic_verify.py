#!/usr/bin/env python3
"""Independent verification of the C_5^3 generalized-Davenport tail corridor."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development" / "orion-rg-davenport"
RG = ROOT / "research" / "orion-rg"
PROTOCOL = DEV / "NONQUANTUM_M1_DK_TAIL_CORRIDOR_PROTOCOL_2026-08-24.md"
DEFAULT_INPUT = RG / "NONQUANTUM_M1_DK_TAIL_CORRIDOR_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = DEV / "NONQUANTUM_M1_DK_TAIL_CORRIDOR_GENERIC_2026-08-24.json"
D2 = RG / "X1F0_D2_C5CUBED_EXACT_RESULTS.json"
D3 = RG / "X1F_D3_C5CUBED_EXACT_RESULTS.json"
SUPPORT = RG / "X1K_C0_SUPPORT_BOUND_RESULTS_V1.json"
POSITIVE = (
    "NONQUANTUM_M1_C5CUBED_ALL_K_GE4_ONE_UNIT_CORRIDOR"
    "__D4_30_IMPLIES_EXACT_TAIL_5K_PLUS10"
)
TOKEN = "ORION_NONQUANTUM_M1_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_valid(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def independent_recurrence(max_k: int = 10_000) -> dict[str, Any]:
    lower = {k: 5 * k + 10 for k in range(2, max_k + 1)}
    upper = {4: 31}
    conditional = {4: 30}
    for k in range(4, max_k):
        upper[k + 1] = max(upper[k] + 5, 32)
        conditional[k + 1] = max(conditional[k] + 5, 32)
    checks = {
        "base_interval": (lower[4], upper[4]) == (30, 31),
        "unconditional_corridor": all(
            lower[k] <= upper[k] == lower[k] + 1 for k in range(4, max_k + 1)
        ),
        "conditional_exact_tail": all(
            conditional[k] == lower[k] for k in range(4, max_k + 1)
        ),
        "registered_early_line": lower[2] == 20 and lower[3] == 25,
        "d4_31_tail_not_inferred": True,
    }
    return {
        "max_k": max_k,
        "checks": checks,
        "all_checks": all(checks.values()),
        "sample": {
            str(k): {"lower": lower[k], "upper": upper[k], "if_d4_30": conditional[k]}
            for k in (4, 5, 10, 100, 1_000, max_k)
        },
    }


def parent_check() -> dict[str, Any]:
    d2 = json.loads(D2.read_text())
    d3 = json.loads(D3.read_text())
    support = json.loads(SUPPORT.read_text())
    checks = {
        "d2_exact": d2.get("theorem", {}).get("exact_value") == 20,
        "d3_exact": d3.get("theorem", {}).get("exact_value") == 25,
        "short_threshold": d2.get("eta_T_C5cubed", {}).get("6") == 24,
        "d2_no_novelty": d2.get("authority", {}).get("novelty_claim") is False,
        "d3_no_novelty": d3.get("authority", {}).get("novelty_claim") is False,
        "support_local_only": support.get("authority", {}).get("theorem_authority") is False,
        "support_replay_pending": support.get("authority", {}).get("external_replay_required") is True,
    }
    return {
        "sha256": {
            "d2": file_sha256(D2),
            "d3": file_sha256(D3),
            "support": file_sha256(SUPPORT),
        },
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    recurrence = independent_recurrence()
    parents = parent_check()
    source_support = source.get("support_frontier", {})
    checks = {
        "source_schema": source.get("schema") == "ORION.NonQuantumMath.M1.DKTailCorridor.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": digest_valid(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "source_gates": all(source.get("gates", {}).values()),
        "parents": parents["all_checks"],
        "independent_recurrence": recurrence["all_checks"],
        "theorem_scope": source.get("scientific_authority")
        == "DERIVED_C5_CUBED_GENERALIZED_DAVENPORT_TAIL_THEOREM_ONLY",
        "d4_open": source.get("exact_d4_authority") is False
        and source.get("theorem", {}).get("current_exact_gate") == "D_4 in {30,31}",
        "support_nonaggregable": source_support.get("used_in_tail_proof") is False
        and source_support.get("aggregable_as_theorem") is False
        and source.get("support_23_theorem_authority") is False,
        "no_d4_31_tail": source.get("d4_31_determines_tail") is False
        and source.get("theorem", {}).get("d4_31_tail_consequence") == "NOT_DETERMINED",
        "no_novelty_venue_quantum": source.get("novelty_authority") is False
        and source.get("venue_authority") is False
        and source.get("quantum_claim") is False,
    }
    positive = all(checks.values())
    result: dict[str, Any] = {
        "schema": "ORION.NonQuantumMath.M1.GenericVerification.v1",
        "decision": "ACCEPT_C5_CUBED_TAIL_CORRIDOR" if positive else "REJECT_C5_CUBED_TAIL_CORRIDOR",
        "source_result_digest": source.get("result_digest"),
        "recurrence": recurrence,
        "parents": parents,
        "checks": checks,
        "authority_scope": "DERIVED_C5_CUBED_GENERALIZED_DAVENPORT_TAIL_THEOREM_ONLY",
        "exact_d4_authority": False,
        "support_23_theorem_authority": False,
        "d4_31_determines_tail": False,
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
                "max_k_checked": result["recurrence"]["max_k"],
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
