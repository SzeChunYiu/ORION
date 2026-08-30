#!/usr/bin/env python3
"""Generate the complete ORION-04 length-31 obstruction as an OPB instance."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


@dataclass(frozen=True)
class Parameters:
    prime: int
    rank: int
    length: int
    support_lower_bound: int
    max_short_length: int
    positive_multiplicities: tuple[int, ...]


class OpbWriter:
    def __init__(self, body_path: Path) -> None:
        self.body_path = body_path
        self.handle = body_path.open("w", encoding="utf-8", newline="\n")
        self.variables: set[str] = set()
        self.constraint_count = 0

    def close(self) -> None:
        self.handle.close()

    def comment(self, text: str) -> None:
        self.handle.write(f"* {text}\n")

    def inequality(self, terms: Iterable[tuple[int, str]], rhs: int) -> None:
        merged: dict[str, int] = {}
        for coefficient, variable in terms:
            if coefficient == 0:
                continue
            merged[variable] = merged.get(variable, 0) + coefficient
        merged = {name: coefficient for name, coefficient in merged.items() if coefficient}
        if not merged:
            if 0 < rhs:
                raise ValueError(f"attempted to emit impossible constant inequality 0 >= {rhs}")
            return
        self.variables.update(merged)
        rendered = " ".join(
            f"{coefficient:+d} {name}" for name, coefficient in sorted(merged.items())
        )
        self.handle.write(f"{rendered} >= {rhs} ;\n")
        self.constraint_count += 1

    def equality(self, terms: Sequence[tuple[int, str]], rhs: int) -> None:
        self.inequality(terms, rhs)
        self.inequality(((-coefficient, variable) for coefficient, variable in terms), -rhs)


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def coordinates(code: int, prime: int, rank: int) -> tuple[int, ...]:
    result = []
    for _ in range(rank):
        result.append(code % prime)
        code //= prime
    return tuple(result)


def encode(coords: Sequence[int], prime: int) -> int:
    code = 0
    factor = 1
    for coordinate in coords:
        code += (coordinate % prime) * factor
        factor *= prime
    return code


def negate_sum(codes: Sequence[int], point_coords: Sequence[tuple[int, ...]], params: Parameters) -> int:
    totals = [0] * params.rank
    for code in codes:
        coords = point_coords[code]
        for axis, coordinate in enumerate(coords):
            totals[axis] = (totals[axis] + coordinate) % params.prime
    return encode(((-value) % params.prime for value in totals), params.prime)


def multiplicity_variable(code: int, multiplicity: int) -> str:
    return f"x_g{code}_m{multiplicity}"


def quotient_variable(axis: int, bit: int) -> str:
    return f"q_a{axis}_b{bit}"


def support_terms(code: int, params: Parameters) -> list[tuple[int, str]]:
    return [(1, multiplicity_variable(code, value)) for value in params.positive_multiplicities]


def threshold_terms(code: int, threshold: int, params: Parameters) -> list[tuple[int, str]]:
    return [
        (1, multiplicity_variable(code, value))
        for value in params.positive_multiplicities
        if value >= threshold
    ]


def basis_codes(params: Parameters) -> list[int]:
    codes = []
    for axis in range(params.rank):
        coords = [0] * params.rank
        coords[axis] = 1
        codes.append(encode(coords, params.prime))
    return codes


def sorted_zero_sum_multisets(
    size: int,
    nonzero_points: range,
    point_coords: Sequence[tuple[int, ...]],
    params: Parameters,
) -> Iterator[tuple[int, ...]]:
    """Enumerate each sorted nonzero zero-sum multiset exactly once."""
    if size < 2:
        return
    for prefix in itertools.combinations_with_replacement(nonzero_points, size - 1):
        final = negate_sum(prefix, point_coords, params)
        if final == 0 or final < prefix[-1]:
            continue
        yield (*prefix, final)


def validate_parameters(params: Parameters) -> None:
    if not is_prime(params.prime):
        raise ValueError("--prime must be prime")
    if params.rank < 1:
        raise ValueError("--rank must be positive")
    if params.length < 1:
        raise ValueError("--length must be positive")
    if not 1 <= params.support_lower_bound <= params.length:
        raise ValueError("support lower bound must be between one and the sequence length")
    if not 1 <= params.max_short_length <= params.prime:
        raise ValueError("max short length must be between one and the exponent")
    if not params.positive_multiplicities:
        raise ValueError("at least one positive multiplicity is required")
    if tuple(sorted(set(params.positive_multiplicities))) != params.positive_multiplicities:
        raise ValueError("positive multiplicities must be strictly increasing")
    if params.positive_multiplicities[-1] >= params.prime:
        raise ValueError("positive multiplicities must be smaller than the exponent")


def build_body(writer: OpbWriter, params: Parameters) -> dict[str, object]:
    group_size = params.prime**params.rank
    nonzero_points = range(1, group_size)
    point_coords = [coordinates(code, params.prime, params.rank) for code in range(group_size)]

    writer.comment("protocol ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1")
    writer.comment(
        "parameters "
        + json.dumps(
            {
                "prime": params.prime,
                "rank": params.rank,
                "length": params.length,
                "support_lower_bound": params.support_lower_bound,
                "max_short_length": params.max_short_length,
                "positive_multiplicities": params.positive_multiplicities,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    for code in nonzero_points:
        writer.inequality(
            [(-1, multiplicity_variable(code, value)) for value in params.positive_multiplicities],
            -1,
        )

    length_terms = [
        (value, multiplicity_variable(code, value))
        for code in nonzero_points
        for value in params.positive_multiplicities
    ]
    writer.equality(length_terms, params.length)

    writer.inequality(
        (
            (1, multiplicity_variable(code, value))
            for code in nonzero_points
            for value in params.positive_multiplicities
        ),
        params.support_lower_bound,
    )

    quotient_max = ((params.prime - 1) * params.length) // params.prime
    quotient_bits = max(1, quotient_max.bit_length())
    for axis in range(params.rank):
        terms: list[tuple[int, str]] = []
        for code in nonzero_points:
            coordinate = point_coords[code][axis]
            for value in params.positive_multiplicities:
                terms.append((coordinate * value, multiplicity_variable(code, value)))
        for bit in range(quotient_bits):
            terms.append((-params.prime * (1 << bit), quotient_variable(axis, bit)))
        writer.equality(terms, 0)

    normalized_basis = basis_codes(params)
    for code in normalized_basis:
        writer.inequality(support_terms(code, params), 1)
    for left, right in zip(normalized_basis, normalized_basis[1:]):
        for threshold in range(1, params.positive_multiplicities[-1] + 1):
            terms = threshold_terms(left, threshold, params)
            terms.extend((-coefficient, variable) for coefficient, variable in threshold_terms(right, threshold, params))
            writer.inequality(terms, 0)

    short_counts: dict[str, int] = {}
    skipped_over_multiplicity: dict[str, int] = {}
    max_multiplicity = params.positive_multiplicities[-1]
    for size in range(2, params.max_short_length + 1):
        emitted = 0
        skipped = 0
        for multiset in sorted_zero_sum_multisets(size, nonzero_points, point_coords, params):
            counts = Counter(multiset)
            if max(counts.values()) > max_multiplicity:
                skipped += 1
                continue
            terms: list[tuple[int, str]] = []
            possible = True
            for code, required in sorted(counts.items()):
                threshold = threshold_terms(code, required, params)
                if not threshold:
                    possible = False
                    break
                terms.extend((-coefficient, variable) for coefficient, variable in threshold)
            if not possible:
                skipped += 1
                continue
            writer.inequality(terms, -(len(counts) - 1))
            emitted += 1
        short_counts[str(size)] = emitted
        skipped_over_multiplicity[str(size)] = skipped

    return {
        "group_size": group_size,
        "nonzero_points": group_size - 1,
        "basis_codes": normalized_basis,
        "quotient_bits_per_coordinate": quotient_bits,
        "short_zero_constraints_by_length": short_counts,
        "short_zero_multisets_impossible_from_multiplicity_cap": skipped_over_multiplicity,
    }


def materialize_instance(output: Path, params: Parameters) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="orion04-opb-") as temporary_directory:
        body_path = Path(temporary_directory) / "body.opb"
        writer = OpbWriter(body_path)
        try:
            details = build_body(writer, params)
        finally:
            writer.close()

        header = f"* #variable= {len(writer.variables)} #constraint= {writer.constraint_count}\n"
        with output.open("w", encoding="utf-8", newline="\n") as destination:
            destination.write(header)
            with body_path.open("r", encoding="utf-8") as source:
                shutil.copyfileobj(source, destination)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {
        "schema": "ORION.ORION04.GlobalCertifiedSearchInstanceManifest.v1",
        "protocol_id": "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1",
        "parameters": {
            "prime": params.prime,
            "rank": params.rank,
            "length": params.length,
            "support_lower_bound": params.support_lower_bound,
            "max_short_length": params.max_short_length,
            "positive_multiplicities": list(params.positive_multiplicities),
        },
        "opb_path": str(output),
        "opb_sha256": digest,
        "variable_count": len(writer.variables),
        "constraint_count": writer.constraint_count,
        "details": details,
        "scientific_terminal": "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK",
        "solver_outcome_accessed": False,
        "proof_checked": False,
        "witness_checked": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
    }


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime", type=int, default=5)
    parser.add_argument("--rank", type=int, default=3)
    parser.add_argument("--length", type=int, default=31)
    parser.add_argument("--support-lower-bound", type=int, default=14)
    parser.add_argument("--max-short-length", type=int)
    parser.add_argument("--multiplicities", type=int, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(argv)
    multiplicities = args.multiplicities
    if multiplicities is None:
        multiplicities = sorted({1, 2, args.prime - 1})
    params = Parameters(
        prime=args.prime,
        rank=args.rank,
        length=args.length,
        support_lower_bound=args.support_lower_bound,
        max_short_length=args.max_short_length or args.prime,
        positive_multiplicities=tuple(multiplicities),
    )
    validate_parameters(params)
    manifest = materialize_instance(args.output, params)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        "ORION04_GLOBAL_OPB="
        + json.dumps(
            {
                "sha256": manifest["opb_sha256"],
                "variables": manifest["variable_count"],
                "constraints": manifest["constraint_count"],
                "terminal": manifest["scientific_terminal"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
