#!/usr/bin/env python3
"""Decode the registered CNF's Kissat model into a mathematical witness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


def coordinates(code: int, prime: int, rank: int) -> list[int]:
    result = []
    for _ in range(rank):
        result.append(code % prime)
        code //= prime
    return result


def registered_x_map() -> dict[int, tuple[int, int]]:
    """Reconstruct x-variable IDs without importing the CNF generator."""
    next_variable = 1
    result: dict[int, tuple[int, int]] = {}
    for code in range(1, 5**3):
        for multiplicity in (1, 2, 4):
            result[next_variable] = (code, multiplicity)
            next_variable += 1
        # The generator next allocates four exact threshold variables.
        next_variable += 4
    return result


def parse_model(path: Path) -> tuple[bool, set[int]]:
    satisfiable = False
    positive: set[int] = set()
    for line in path.read_text(errors="strict").splitlines():
        stripped = line.strip()
        if stripped in {"s SATISFIABLE", "SATISFIABLE"}:
            satisfiable = True
        if stripped.startswith("v "):
            for token in stripped[2:].split():
                literal = int(token)
                if literal > 0:
                    positive.add(literal)
    return satisfiable, positive


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    satisfiable, positive = parse_model(args.solver_output)
    if not satisfiable:
        raise SystemExit("solver output does not contain a SATISFIABLE terminal")
    x_map = registered_x_map()
    by_point: dict[int, int] = {}
    for variable, (code, multiplicity) in x_map.items():
        if variable not in positive:
            continue
        if code in by_point:
            raise SystemExit(f"multiple multiplicity variables selected for point {code}")
        by_point[code] = multiplicity

    witness = {
        "schema": "ORION.ORION04.ExtremalWitness.v1",
        "prime": 5,
        "rank": 3,
        "length": 31,
        "source": {
            "encoding": "ORION.ORION04.GlobalCertifiedSearchCnfManifest.v1",
            "solver_output": str(args.solver_output),
            "decoder": "independent_checker/decode_kissat_model.py",
        },
        "multiplicities": [
            {"point": coordinates(code, 5, 3), "multiplicity": multiplicity}
            for code, multiplicity in sorted(by_point.items())
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n")
    print(
        "ORION04_DECODED_WITNESS="
        + json.dumps(
            {
                "support": len(by_point),
                "total_length": sum(by_point.values()),
                "output": str(args.output),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
