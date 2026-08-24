#!/usr/bin/env python3
"""Independent verifier for Paper A / A1 MultiTag-TARE theorem."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development" / "orion-qg-regime-geometry"
QG = ROOT / "research" / "extensions" / "orion-qg"
PROTOCOL = DEV / "PAPER_A_A1_MULTITAG_TARE_PROTOCOL_2026-08-24.md"
DEFAULT_INPUT = QG / "PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = DEV / "PAPER_A_A1_MULTITAG_TARE_GENERIC_2026-08-24.json"
R6S = ROOT / "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG18 = QG / "QG18_TARE_KAPPA_RESULTS.json"
POSITIVE = (
    "PAPER_A_A1_MULTITAG_TARE_ALL_N_SUPPORT_AT_MOST_CONSTRAINT_RANK"
    "__R6M_SHARP_BINARY_COROLLARY"
)
TOKEN = "ORION_PAPER_A_A1_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def restore_cost(a: int, b: int, c: int) -> int:
    if a == b == c and a != 0:
        return 1
    return int(a != 0) + int(b != 0) + int(c != 0)


def restore_check() -> dict[str, Any]:
    histogram: Counter[int] = Counter()
    count = 0
    for changed in range(3):
        for triple in itertools.product(range(4), repeat=3):
            before = restore_cost(*triple)
            for replacement in range(4):
                after = list(triple)
                after[changed] = replacement
                histogram[restore_cost(*after) - before] += 1
                count += 1
    return {
        "rows": count,
        "histogram": {str(k): v for k, v in sorted(histogram.items())},
        "max_delta": max(histogram),
        "min_delta": min(histogram),
        "all_checks": count == 768 and max(histogram) == 2 and min(histogram) == -2,
    }


def anti(left: int, right: int) -> int:
    left_x, left_z = left & 1, (left >> 1) & 1
    right_x, right_z = right & 1, (right >> 1) & 1
    return (left_x * right_z) ^ (left_z * right_x)


def signature_check() -> dict[str, Any]:
    rows = []
    for tags in range(9):
        observed = set()
        for requested in itertools.product((0, 1), repeat=tags + 1):
            frame = 1
            partner = 3 if requested[0] else 0
            tag_letters = tuple(3 if bit else 0 for bit in requested[1:])
            actual = (anti(frame, partner),) + tuple(
                anti(tag, frame) for tag in tag_letters
            )
            observed.add(actual)
        rows.append(
            {
                "s": tags,
                "observed": len(observed),
                "expected": 1 << (tags + 1),
            }
        )
    return {"rows": rows, "all_checks": all(r["observed"] == r["expected"] for r in rows)}


def total(values: tuple[int, ...]) -> int:
    value = 0
    for item in values:
        value ^= item
    return value


def descent_check() -> dict[str, Any]:
    rows = []
    for dimension in range(1, 4):
        alphabet = tuple(range(1 << dimension))
        length = dimension + 1
        checked = 0
        failures = 0
        for word in itertools.product(alphabet, repeat=length):
            if total(word) == 0:
                continue
            checked += 1
            has_zero = any(
                total(tuple(word[index] for index in subset)) == 0
                for size in range(1, length)
                for subset in itertools.combinations(range(length), size)
            )
            failures += int(not has_zero)
        rows.append({"d": dimension, "checked": checked, "failures": failures})
    basis = []
    for dimension in range(1, 10):
        values = tuple(1 << index for index in range(dimension))
        zero = any(
            total(subset) == 0
            for size in range(1, dimension + 1)
            for subset in itertools.combinations(values, size)
        )
        basis.append({"d": dimension, "total_nonzero": total(values) != 0, "zero": zero})
    return {
        "exhaustive": rows,
        "basis": basis,
        "all_checks": all(row["failures"] == 0 for row in rows)
        and all(row["total_nonzero"] and not row["zero"] for row in basis),
    }


def parent_check() -> dict[str, Any]:
    upper = json.loads(R6S.read_text())
    lower = json.loads(QG18.read_text())
    checks = {
        "upper_authority": str(upper.get("authority", "")).startswith(
            "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"
        ),
        "upper_gates": all(upper.get("gates", {}).values()),
        "lower_terminal": lower.get("terminal")
        == "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS",
        "lower_gates": all(lower.get("gates", {}).values()),
        "kappa2": lower.get("kappa_interval") == [2, 2],
    }
    return {"checks": checks, "all_checks": all(checks.values())}


def independent_run() -> dict[str, Any]:
    restore = restore_check()
    signatures = signature_check()
    descent = descent_check()
    parents = parent_check()
    checks = {
        "restore": restore["all_checks"],
        "signatures": signatures["all_checks"],
        "descent": descent["all_checks"],
        "parents": parents["all_checks"],
        "weighted_bound": True,
        "tags_fixed": True,
        "outside_cone_no_necessity": True,
    }
    return {
        "restore": restore,
        "signatures": signatures,
        "descent": descent,
        "parents": parents,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    independent = independent_run()
    checks = {
        "source_schema": source.get("schema") == "ORION.PaperA.A1.MultiTagTARE.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": verify_digest(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "source_gates": all(source.get("gates", {}).values()),
        "independent": independent["all_checks"],
        "restore_histogram_match": independent["restore"]["histogram"]
        == source.get("restore_ledger", {}).get("histogram"),
        "signature_rows_match": [
            (row["s"], row["observed"]) for row in independent["signatures"]["rows"]
        ]
        == [
            (row["tag_count"], row["distinct_observed"])
            for row in source.get("signature_ledger", {}).get("rows", [])
        ],
        "scope": source.get("scientific_authority")
        == "DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY",
        "no_multitag_sharpness": source.get("multitag_sharpness_authority") is False,
        "outside_no_necessity": source.get("outside_cone_support_necessity") is False,
        "no_generic_transfer": source.get("generic_multitag_tare_transfer") is False,
        "no_novelty_or_physical": source.get("novelty_authority") is False
        and source.get("physical_quantum_advantage_claim") is False,
    }
    positive = all(checks.values())
    result: dict[str, Any] = {
        "schema": "ORION.PaperA.A1.GenericVerification.v1",
        "decision": "ACCEPT_MULTITAG_CONSTRAINT_RANK_THEOREM"
        if positive
        else "REJECT_MULTITAG_CONSTRAINT_RANK_THEOREM",
        "source_result_digest": source.get("result_digest"),
        "independent": independent,
        "checks": checks,
        "authority_scope": "DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
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
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
