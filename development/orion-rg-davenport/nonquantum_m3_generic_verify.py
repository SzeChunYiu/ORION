#!/usr/bin/env python3
"""Independent verifier for M3 exact support-10 replay evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development" / "orion-rg-davenport"
RG = ROOT / "research" / "orion-rg"
PROTOCOL = DEV / "NONQUANTUM_M3_SUPPORT10_REPLAY_PROTOCOL_2026-08-24.md"
M2 = RG / "NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_RESULTS_2026-08-24.json"
U128 = RG / "x1k_c0_support10_13_rank3_u128.c"
BYTES = RG / "x1k_c0_support10_13_rank3_bytes.c"
DEFAULT_INPUT = RG / "NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = DEV / "NONQUANTUM_M3_SUPPORT10_REPLAY_GENERIC_2026-08-24.json"
POSITIVE = (
    "NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED"
    "__OBSTRUCTION_SUPPORT_AT_LEAST11"
)
TOKEN = "ORION_NONQUANTUM_M3_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_valid(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def independent_patterns() -> list[list[int]]:
    return [
        [c1, c2, c4]
        for c4 in range(11)
        for c2 in range(11)
        for c1 in range(11)
        if c1 + c2 + c4 == 10 and c1 + 2 * c2 + 4 * c4 == 31
    ]


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    parent = json.loads(M2.read_text())
    replay = source.get("replay_ledger", {})
    rows = replay.get("rows", [])
    by_pattern = {tuple(row.get("pattern", [])): row for row in rows}
    expected = {
        (1, 3, 6): {"a1": 1, "b2": 3, "c4": 6, "support": 10, "nodes": 272119, "leaves": 0, "solutions": 0},
        (3, 0, 7): {"a1": 3, "b2": 0, "c4": 7, "support": 10, "nodes": 210700, "leaves": 3558, "solutions": 0},
    }
    patterns = independent_patterns()
    checks = {
        "source_schema": source.get("schema") == "ORION.NonQuantumMath.M3.Support10Replay.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": digest_valid(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "m2_hash": source.get("m2_parent", {}).get("sha256") == file_sha256(M2),
        "m2_digest": source.get("m2_parent", {}).get("result_digest")
        == parent.get("result_digest")
        == "846ffcc2329c13fb6a1811028beeca21cfd7f69f1203bc4a4b269d5d98f2f697",
        "u128_hash": replay.get("u128_build", {}).get("source_sha256") == file_sha256(U128),
        "byte_hash": replay.get("byte_build", {}).get("source_sha256") == file_sha256(BYTES),
        "patterns": sorted(patterns) == [[1, 3, 6], [3, 0, 7]]
        and source.get("pattern_ledger", {}).get("patterns") == [[1, 3, 6], [3, 0, 7]],
        "rank3_forced": all(4 * c4 >= 16 > 13 for _, _, c4 in patterns),
        "exact_rows": set(by_pattern) == set(expected)
        and all(
            by_pattern[pattern].get("u128") == row
            and by_pattern[pattern].get("bytes") == row
            for pattern, row in expected.items()
        ),
        "source_gates": all(source.get("gates", {}).values()),
        "scope": source.get("scientific_authority")
        == "BOUNDED_C5CUBED_SUPPORT10_EXCLUSION_ONLY",
        "bounded_authority": source.get("bounded_support_le10_theorem_authority") is True,
        "no_support11_or_23": source.get("support_11_plus_theorem_authority") is False
        and source.get("support_23_theorem_authority") is False,
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
        "schema": "ORION.NonQuantumMath.M3.GenericVerification.v1",
        "decision": "ACCEPT_SUPPORT10_EXCLUSION" if positive else "REJECT_SUPPORT10_EXCLUSION",
        "source_result_digest": source.get("result_digest"),
        "independent_patterns": patterns,
        "checks": checks,
        "authority_scope": "BOUNDED_C5CUBED_SUPPORT10_EXCLUSION_ONLY",
        "support_11_plus_theorem_authority": False,
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
                "patterns": result["independent_patterns"],
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
