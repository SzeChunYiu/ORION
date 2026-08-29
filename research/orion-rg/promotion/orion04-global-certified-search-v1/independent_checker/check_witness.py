#!/usr/bin/env python3
"""Standalone checker for a claimed length-31 C_5^3 obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

POSITIVE = "ORION04_D4_31_EXPLICIT_EXTREMAL_INDEPENDENTLY_VERIFIED"
NEGATIVE = "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def add(left: tuple[int, ...], right: tuple[int, ...], prime: int) -> tuple[int, ...]:
    return tuple((a + b) % prime for a, b in zip(left, right))


def validate(raw: dict[str, Any]) -> dict[str, Any]:
    prime = raw.get("prime")
    rank = raw.get("rank")
    length = raw.get("length")
    rows = raw.get("multiplicities")
    checks: dict[str, bool] = {
        "schema": raw.get("schema") == "ORION.ORION04.ExtremalWitness.v1",
        "registered_parameters": prime == 5 and rank == 3 and length == 31,
        "rows_are_list": isinstance(rows, list),
    }
    if not all(checks.values()):
        return {"checks": checks, "terminal": NEGATIVE}

    observed: dict[tuple[int, ...], int] = {}
    row_shape = True
    allowed = True
    no_zero = True
    for row in rows:
        if not isinstance(row, dict):
            row_shape = False
            continue
        point_raw = row.get("point")
        multiplicity = row.get("multiplicity")
        if (
            not isinstance(point_raw, list)
            or len(point_raw) != rank
            or not all(isinstance(value, int) and 0 <= value < prime for value in point_raw)
            or not isinstance(multiplicity, int)
        ):
            row_shape = False
            continue
        point = tuple(point_raw)
        if point == (0,) * rank:
            no_zero = False
        if multiplicity not in {1, 2, 4}:
            allowed = False
        if point in observed:
            row_shape = False
        observed[point] = multiplicity

    checks["row_shape_and_unique_points"] = row_shape
    checks["allowed_multiplicities"] = allowed
    checks["zero_not_present"] = no_zero
    if not row_shape:
        return {"checks": checks, "terminal": NEGATIVE}

    total_length = sum(observed.values())
    support = len(observed)
    total_sum = [0] * rank
    occurrences: list[tuple[int, ...]] = []
    for point, multiplicity in observed.items():
        for axis, coordinate in enumerate(point):
            total_sum[axis] = (total_sum[axis] + multiplicity * coordinate) % prime
        occurrences.extend([point] * multiplicity)

    checks["length_31"] = total_length == 31
    checks["support_at_least_14"] = support >= 14
    checks["total_sum_zero"] = total_sum == [0] * rank

    zero = (0,) * rank
    reachable: list[set[tuple[int, ...]]] = [set() for _ in range(6)]
    reachable[0].add(zero)
    first_short_zero: dict[str, Any] | None = None
    for occurrence_index, point in enumerate(occurrences):
        for weight in range(5, 0, -1):
            additions = {add(partial, point, prime) for partial in reachable[weight - 1]}
            reachable[weight].update(additions)
            if zero in additions and first_short_zero is None:
                first_short_zero = {
                    "weight": weight,
                    "occurrence_index": occurrence_index,
                    "point": list(point),
                }

    checks["no_zero_sum_of_length_1_to_5"] = first_short_zero is None
    positive = all(checks.values())
    report: dict[str, Any] = {
        "schema": "ORION.ORION04.ExtremalWitnessVerification.v1",
        "witness_sha256": hashlib.sha256(canonical(raw).encode()).hexdigest(),
        "support": support,
        "total_length": total_length,
        "total_sum": total_sum,
        "reachable_state_counts": {str(weight): len(reachable[weight]) for weight in range(6)},
        "first_short_zero": first_short_zero,
        "checks": checks,
        "terminal": POSITIVE if positive else NEGATIVE,
        "c0_31_authority": False,
        "exact_d4_31_authority": positive,
        "exact_d4_30_authority": False,
    }
    unsigned = dict(report)
    report["verification_digest"] = hashlib.sha256(canonical(unsigned).encode()).hexdigest()
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    raw = json.loads(args.input.read_text())
    report = validate(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        "ORION04_WITNESS_CHECK="
        + canonical(
            {
                "terminal": report["terminal"],
                "all_checks": all(report["checks"].values()),
                "verification_digest": report.get("verification_digest"),
            }
        )
    )
    return 0 if report["terminal"] == POSITIVE else 1


if __name__ == "__main__":
    raise SystemExit(main())
