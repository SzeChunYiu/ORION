#!/usr/bin/env python3
"""Independent stdlib-only exact regression for the finite-information theorem spine."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

GREEN = "FINITE_INFORMATION_INTERFACE_V1_THEOREMS_REPRODUCED"
RED = "FINITE_INFORMATION_INTERFACE_V1_COUNTEREXAMPLE_OR_IMPLEMENTATION_DRIFT"


def restricted_growth_partitions(n: int) -> list[tuple[int, ...]]:
    """Canonical set partitions encoded as restricted-growth strings."""
    if n < 1:
        raise ValueError("n must be positive")
    out: list[tuple[int, ...]] = []

    def rec(prefix: list[int], current_max: int) -> None:
        if len(prefix) == n:
            out.append(tuple(prefix))
            return
        for value in range(current_max + 2):
            prefix.append(value)
            rec(prefix, max(current_max, value))
            prefix.pop()

    rec([0], 0)
    return out


def partition_blocks(partition: Sequence[int]) -> list[list[int]]:
    count = max(partition) + 1
    return [[i for i, block in enumerate(partition) if block == b] for b in range(count)]


def refines(fine: Sequence[int], coarse: Sequence[int]) -> bool:
    if len(fine) != len(coarse):
        return False
    for i in range(len(fine)):
        for j in range(i + 1, len(fine)):
            if fine[i] == fine[j] and coarse[i] != coarse[j]:
                return False
    return True


def reshape_losses(flat: Sequence[int], n: int, actions: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(flat[i * actions : (i + 1) * actions]) for i in range(n))


def closed_partition_risk(
    losses: Sequence[Sequence[int]], weights: Sequence[int], partition: Sequence[int]
) -> int:
    total = 0
    actions = len(losses[0])
    for block in partition_blocks(partition):
        total += min(sum(weights[x] * losses[x][a] for x in block) for a in range(actions))
    return total


def brute_policy_risk(
    losses: Sequence[Sequence[int]], weights: Sequence[int], partition: Sequence[int]
) -> int:
    actions = len(losses[0])
    block_count = max(partition) + 1
    best: int | None = None
    for policy in itertools.product(range(actions), repeat=block_count):
        risk = sum(weights[x] * losses[x][policy[partition[x]]] for x in range(len(partition)))
        best = risk if best is None else min(best, risk)
    if best is None:
        raise AssertionError("empty policy class")
    return best


def full_information_risk(losses: Sequence[Sequence[int]], weights: Sequence[int]) -> int:
    return sum(weights[x] * min(losses[x]) for x in range(len(losses)))


def every_fibre_has_common_optimum(losses: Sequence[Sequence[int]], partition: Sequence[int]) -> bool:
    actions = len(losses[0])
    for block in partition_blocks(partition):
        common = set(range(actions))
        for x in block:
            state_min = min(losses[x])
            common.intersection_update(a for a in range(actions) if losses[x][a] == state_min)
        if not common:
            return False
    return True


def check_pair_lower_bounds(
    losses: Sequence[Sequence[int]], weights: Sequence[int], partition: Sequence[int], regret: int
) -> None:
    actions = len(losses[0])
    minima = [min(row) for row in losses]
    for block in partition_blocks(partition):
        for x, y in itertools.combinations(block, 2):
            lower = min(
                weights[x] * (losses[x][a] - minima[x])
                + weights[y] * (losses[y][a] - minima[y])
                for a in range(actions)
            )
            if lower > regret:
                raise AssertionError(
                    f"pair lower bound exceeds regret: lower={lower}, regret={regret}, "
                    f"partition={partition}, pair={(x, y)}"
                )


def simplex_grid_denominator_three(actions: int) -> list[tuple[Fraction, ...]]:
    if actions != 3:
        raise ValueError("registered randomized probe uses three actions")
    out: list[tuple[Fraction, ...]] = []
    for numerators in itertools.product(range(4), repeat=3):
        if sum(numerators) == 3:
            out.append(tuple(Fraction(k, 3) for k in numerators))
    if len(out) != 10:
        raise AssertionError("unexpected simplex-grid size")
    return out


def run_decision_regression() -> tuple[int, int, int]:
    decision_instances = 0
    refinement_pairs = 0
    randomized_probes = 0
    configurations = ((1, 3), (2, 3), (3, 3), (4, 2))
    q_grid = simplex_grid_denominator_three(3)

    for n, actions in configurations:
        partitions = restricted_growth_partitions(n)
        refinement_index = [
            (fine, coarse)
            for fine in partitions
            for coarse in partitions
            if refines(fine, coarse)
        ]
        for flat in itertools.product((0, 1), repeat=n * actions):
            losses = reshape_losses(flat, n, actions)
            for weights in itertools.product((1, 2), repeat=n):
                risks: dict[tuple[int, ...], int] = {}
                full = full_information_risk(losses, weights)
                for partition in partitions:
                    closed = closed_partition_risk(losses, weights, partition)
                    brute = brute_policy_risk(losses, weights, partition)
                    if closed != brute:
                        raise AssertionError(
                            f"partition-risk mismatch: closed={closed}, brute={brute}, "
                            f"losses={losses}, weights={weights}, partition={partition}"
                        )
                    regret = closed - full
                    if regret < 0:
                        raise AssertionError("negative information regret")
                    common = every_fibre_has_common_optimum(losses, partition)
                    if (regret == 0) != common:
                        raise AssertionError(
                            f"zero/common-optimum mismatch: regret={regret}, common={common}, "
                            f"losses={losses}, weights={weights}, partition={partition}"
                        )
                    check_pair_lower_bounds(losses, weights, partition, regret)
                    risks[partition] = closed
                    decision_instances += 1

                    if actions == 3:
                        for block in partition_blocks(partition):
                            action_totals = [
                                sum(weights[x] * losses[x][a] for x in block)
                                for a in range(actions)
                            ]
                            deterministic = min(action_totals)
                            for q in q_grid:
                                randomized = sum(q[a] * action_totals[a] for a in range(actions))
                                if randomized < deterministic:
                                    raise AssertionError(
                                        f"randomization improvement found: randomized={randomized}, "
                                        f"deterministic={deterministic}"
                                    )
                                randomized_probes += 1

                for fine, coarse in refinement_index:
                    if risks[fine] > risks[coarse]:
                        raise AssertionError(
                            f"refinement increased risk: fine={fine}, coarse={coarse}, "
                            f"fine_risk={risks[fine]}, coarse_risk={risks[coarse]}"
                        )
                    refinement_pairs += 1

    return decision_instances, refinement_pairs, randomized_probes


def run_classification_regression() -> int:
    instances = 0
    for n in range(1, 6):
        partitions = restricted_growth_partitions(n)
        for label_count in (2, 3):
            for labels in itertools.product(range(label_count), repeat=n):
                losses = tuple(
                    tuple(0 if labels[x] == action else 1 for action in range(label_count))
                    for x in range(n)
                )
                for weights in itertools.product((1, 2), repeat=n):
                    for partition in partitions:
                        closed = closed_partition_risk(losses, weights, partition)
                        minority_mass = 0
                        for block in partition_blocks(partition):
                            total = sum(weights[x] for x in block)
                            majority = max(
                                sum(weights[x] for x in block if labels[x] == label)
                                for label in range(label_count)
                            )
                            minority_mass += total - majority
                        if closed != minority_mass:
                            raise AssertionError(
                                f"0-1 minority-mass mismatch: closed={closed}, "
                                f"minority={minority_mass}, labels={labels}, weights={weights}, "
                                f"partition={partition}"
                            )
                        instances += 1
    return instances


def run_scalar_regression() -> int:
    instances = 0
    alphabet = (-2, -1, 0, 1, 2)
    for n in range(1, 6):
        partitions = restricted_growth_partitions(n)
        for values in itertools.product(alphabet, repeat=n):
            for partition in partitions:
                for block in partition_blocks(partition):
                    fibre = [values[x] for x in block]
                    lo, hi = min(fibre), max(fibre)
                    diameter = hi - lo
                    claimed_radius = Fraction(diameter, 2)
                    candidates = {
                        Fraction(u + v, 2)
                        for u in fibre
                        for v in fibre
                    }
                    brute_radius = min(
                        max(abs(Fraction(value) - center) for value in fibre)
                        for center in candidates
                    )
                    if brute_radius != claimed_radius:
                        raise AssertionError(
                            f"scalar-radius mismatch: brute={brute_radius}, claimed={claimed_radius}, "
                            f"fibre={fibre}"
                        )
                    covering_width = Fraction(hi - lo)
                    if covering_width != 2 * claimed_radius:
                        raise AssertionError("covering width is not twice minimax radius")
                    instances += 1
    return instances


def generate_result() -> dict[str, object]:
    decision_instances, refinement_pairs, randomized_probes = run_decision_regression()
    classification_instances = run_classification_regression()
    scalar_instances = run_scalar_regression()
    counters = {
        "decision_partition_instances": decision_instances,
        "refinement_pairs": refinement_pairs,
        "randomized_policy_probes": randomized_probes,
        "classification_partition_instances": classification_instances,
        "scalar_fibre_instances": scalar_instances,
        "mismatches": 0,
    }
    expected = {
        "decision_partition_instances": 82448,
        "refinement_pairs": 295696,
        "randomized_policy_probes": 417440,
        "classification_partition_instances": 482394,
        "scalar_fibre_instances": 496330,
        "mismatches": 0,
    }
    if counters != expected:
        raise AssertionError(f"registered counter drift: observed={counters}, expected={expected}")
    return {
        "schema": "ORION.FiniteInformationInterface.Result.v1",
        "terminal": GREEN,
        "status": "EXACT_BOUNDED_REGRESSION_GREEN__UNRESTRICTED_AUTHORITY_FROM_PROOFS",
        "scientific_authority_delta": "NONE",
        "counters": counters,
        "interpretation": (
            "Independent exhaustive finite regression found no counterexample in the registered "
            "universe. Novelty, external validity, and paper promotion are not assessed."
        ),
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check-result", type=Path)
    group.add_argument("--write-result", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = generate_result()
        if args.check_result is not None:
            expected = json.loads(args.check_result.read_text(encoding="utf-8"))
            if result != expected:
                raise AssertionError(
                    "result artifact differs from independent recomputation:\n"
                    + json.dumps({"recomputed": result, "artifact": expected}, indent=2, sort_keys=True)
                )
        if args.write_result is not None:
            args.write_result.parent.mkdir(parents=True, exist_ok=True)
            args.write_result.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        counters = result["counters"]
        print(
            f"{GREEN} decision_partition_instances={counters['decision_partition_instances']} "
            f"refinement_pairs={counters['refinement_pairs']} "
            f"scalar_fibre_instances={counters['scalar_fibre_instances']} "
            f"randomized_policy_probes={counters['randomized_policy_probes']}"
        )
        return 0
    except Exception as exc:  # fail closed with one machine-readable terminal
        print(f"{RED}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
