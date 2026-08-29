#!/usr/bin/env python3
"""Generate an independent DIMACS encoding of the ORION-04 obstruction."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence


class CnfWriter:
    def __init__(self, body: Path) -> None:
        self.handle = body.open("w", encoding="ascii", newline="\n")
        self.names: dict[str, int] = {}
        self.clause_count = 0

    def var(self, name: str) -> int:
        if name not in self.names:
            self.names[name] = len(self.names) + 1
        return self.names[name]

    def clause(self, literals: Iterable[int]) -> None:
        values = list(dict.fromkeys(literals))
        if any(-literal in values for literal in values):
            return
        if not values:
            raise ValueError("empty clause requested")
        self.handle.write(" ".join(str(value) for value in values) + " 0\n")
        self.clause_count += 1

    def exactly_one(self, variables: Sequence[int]) -> None:
        self.clause(variables)
        for left, right in itertools.combinations(variables, 2):
            self.clause((-left, -right))

    def close(self) -> None:
        self.handle.close()


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    return all(value % divisor for divisor in range(2, math.isqrt(value) + 1))


def coords(code: int, prime: int, rank: int) -> tuple[int, ...]:
    result = []
    for _ in range(rank):
        result.append(code % prime)
        code //= prime
    return tuple(result)


def encode(values: Sequence[int], prime: int) -> int:
    code = 0
    place = 1
    for value in values:
        code += (value % prime) * place
        place *= prime
    return code


def negated_prefix_sum(
    prefix: Sequence[int],
    points: Sequence[tuple[int, ...]],
    prime: int,
    rank: int,
) -> int:
    totals = [0] * rank
    for code in prefix:
        point = points[code]
        for axis, value in enumerate(point):
            totals[axis] = (totals[axis] + value) % prime
    return encode(tuple((-value) % prime for value in totals), prime)


def zero_sum_multisets(
    size: int,
    nonzero: range,
    points: Sequence[tuple[int, ...]],
    prime: int,
    rank: int,
) -> Iterator[tuple[int, ...]]:
    for prefix in itertools.combinations_with_replacement(nonzero, size - 1):
        final = negated_prefix_sum(prefix, points, prime, rank)
        if final != 0 and final >= prefix[-1]:
            yield (*prefix, final)


def x_name(code: int, multiplicity: int) -> str:
    return f"x_g{code}_m{multiplicity}"


def t_name(code: int, threshold: int) -> str:
    return f"t_g{code}_ge{threshold}"


def state_name(label: str, layer: int, state: int) -> str:
    return f"s_{label}_i{layer}_v{state}"


def encode_automaton(
    writer: CnfWriter,
    *,
    label: str,
    inputs: Sequence[tuple[int, int]],
    state_count: int,
    start_state: int,
    final_state: int,
    transition: Callable[[int, int], int],
) -> None:
    layers: list[list[int]] = []
    for layer in range(len(inputs) + 1):
        states = [writer.var(state_name(label, layer, state)) for state in range(state_count)]
        writer.exactly_one(states)
        layers.append(states)
    writer.clause((layers[0][start_state],))
    for layer, (input_variable, coefficient) in enumerate(inputs, start=1):
        previous = layers[layer - 1]
        current = layers[layer]
        for state, previous_variable in enumerate(previous):
            false_target = transition(state, 0)
            true_target = transition(state, coefficient)
            writer.clause((-previous_variable, input_variable, current[false_target]))
            writer.clause((-previous_variable, -input_variable, current[true_target]))
    writer.clause((layers[-1][final_state],))


def materialize(
    *,
    output: Path,
    manifest_path: Path,
    prime: int,
    rank: int,
    length: int,
    support_lower_bound: int,
    max_short_length: int,
    multiplicities: tuple[int, ...],
) -> dict[str, object]:
    if not is_prime(prime):
        raise ValueError("prime must be prime")
    if multiplicities != tuple(sorted(set(multiplicities))):
        raise ValueError("multiplicities must be strictly increasing")
    if not multiplicities or multiplicities[0] < 1 or multiplicities[-1] >= prime:
        raise ValueError("multiplicities must lie between one and prime-1")
    if not 1 <= max_short_length <= prime:
        raise ValueError("invalid short-zero length")

    group_size = prime**rank
    nonzero = range(1, group_size)
    points = [coords(code, prime, rank) for code in range(group_size)]
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="orion04-cnf-") as temporary:
        body = Path(temporary) / "body.cnf"
        writer = CnfWriter(body)
        try:
            x: dict[tuple[int, int], int] = {}
            threshold: dict[tuple[int, int], int] = {}
            for code in nonzero:
                row = []
                for multiplicity in multiplicities:
                    variable = writer.var(x_name(code, multiplicity))
                    x[(code, multiplicity)] = variable
                    row.append(variable)
                for left, right in itertools.combinations(row, 2):
                    writer.clause((-left, -right))

                for required in range(1, multiplicities[-1] + 1):
                    t_variable = writer.var(t_name(code, required))
                    threshold[(code, required)] = t_variable
                    supporting = [
                        x[(code, multiplicity)]
                        for multiplicity in multiplicities
                        if multiplicity >= required
                    ]
                    if not supporting:
                        writer.clause((-t_variable,))
                    else:
                        for source in supporting:
                            writer.clause((-source, t_variable))
                        writer.clause((-t_variable, *supporting))

            basis = [prime**axis for axis in range(rank)]
            for code in basis:
                writer.clause((threshold[(code, 1)],))
            for left, right in zip(basis, basis[1:]):
                for required in range(1, multiplicities[-1] + 1):
                    writer.clause((-threshold[(right, required)], threshold[(left, required)]))

            length_inputs = [
                (x[(code, multiplicity)], multiplicity)
                for code in nonzero
                for multiplicity in multiplicities
            ]
            overflow = length + 1
            encode_automaton(
                writer,
                label="length",
                inputs=length_inputs,
                state_count=overflow + 1,
                start_state=0,
                final_state=length,
                transition=lambda state, coefficient: min(overflow, state + coefficient),
            )

            support_inputs = [(threshold[(code, 1)], 1) for code in nonzero]
            encode_automaton(
                writer,
                label="support",
                inputs=support_inputs,
                state_count=support_lower_bound + 1,
                start_state=0,
                final_state=support_lower_bound,
                transition=lambda state, coefficient: min(
                    support_lower_bound, state + coefficient
                ),
            )

            for axis in range(rank):
                coordinate_inputs = [
                    (
                        x[(code, multiplicity)],
                        (points[code][axis] * multiplicity) % prime,
                    )
                    for code in nonzero
                    for multiplicity in multiplicities
                ]
                encode_automaton(
                    writer,
                    label=f"sum{axis}",
                    inputs=coordinate_inputs,
                    state_count=prime,
                    start_state=0,
                    final_state=0,
                    transition=lambda state, coefficient, p=prime: (state + coefficient) % p,
                )

            short_counts: dict[str, int] = {}
            skipped_counts: dict[str, int] = {}
            for size in range(2, max_short_length + 1):
                emitted = 0
                skipped = 0
                for multiset in zero_sum_multisets(size, nonzero, points, prime, rank):
                    counts = Counter(multiset)
                    if max(counts.values()) > multiplicities[-1]:
                        skipped += 1
                        continue
                    literals = []
                    possible = True
                    for code, required in sorted(counts.items()):
                        variable = threshold.get((code, required))
                        if variable is None:
                            possible = False
                            break
                        literals.append(-variable)
                    if not possible:
                        skipped += 1
                        continue
                    writer.clause(literals)
                    emitted += 1
                short_counts[str(size)] = emitted
                skipped_counts[str(size)] = skipped
        finally:
            writer.close()

        header = f"p cnf {len(writer.names)} {writer.clause_count}\n"
        with output.open("w", encoding="ascii", newline="\n") as destination:
            destination.write(header)
            with body.open("r", encoding="ascii") as source:
                shutil.copyfileobj(source, destination)

    hasher = hashlib.sha256()
    with output.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    manifest: dict[str, object] = {
        "schema": "ORION.ORION04.GlobalCertifiedSearchCnfManifest.v1",
        "protocol_id": "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1",
        "parameters": {
            "prime": prime,
            "rank": rank,
            "length": length,
            "support_lower_bound": support_lower_bound,
            "max_short_length": max_short_length,
            "positive_multiplicities": list(multiplicities),
        },
        "cnf_path": str(output),
        "cnf_sha256": hasher.hexdigest(),
        "variable_count": len(writer.names),
        "clause_count": writer.clause_count,
        "basis_codes": basis,
        "short_zero_clauses_by_length": short_counts,
        "short_zero_multisets_impossible_from_multiplicity_cap": skipped_counts,
        "encoding_components": [
            "one-hot multiplicity choices",
            "exact multiplicity-threshold equivalences",
            "finite-state exact length automaton",
            "capped support-lower-bound automaton",
            "three independent modulo-five sum automata",
            "complete short-zero no-good clauses",
            "rank-three basis normalization and basis multiplicity order"
        ],
        "solver_outcome_accessed": False,
        "proof_checked": False,
        "witness_checked": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime", type=int, default=5)
    parser.add_argument("--rank", type=int, default=3)
    parser.add_argument("--length", type=int, default=31)
    parser.add_argument("--support-lower-bound", type=int, default=14)
    parser.add_argument("--max-short-length", type=int)
    parser.add_argument("--multiplicities", type=int, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    multiplicities = tuple(args.multiplicities or sorted({1, 2, args.prime - 1}))
    manifest = materialize(
        output=args.output,
        manifest_path=args.manifest,
        prime=args.prime,
        rank=args.rank,
        length=args.length,
        support_lower_bound=args.support_lower_bound,
        max_short_length=args.max_short_length or args.prime,
        multiplicities=multiplicities,
    )
    print(
        "ORION04_GLOBAL_CNF="
        + json.dumps(
            {
                "sha256": manifest["cnf_sha256"],
                "variables": manifest["variable_count"],
                "clauses": manifest["clause_count"],
                "terminal": "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
