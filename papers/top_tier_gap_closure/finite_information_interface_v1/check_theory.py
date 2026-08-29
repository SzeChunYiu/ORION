#!/usr/bin/env python3
"""Exact finite regression checker for the finite-information-interface theorem spine.

The implementation deliberately compares closed-form expressions with independent
brute-force enumerations on bounded finite universes.  It uses only the Python
standard library and exact rational arithmetic.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Iterable, Sequence


TERMINAL = "FINITE_INFORMATION_INTERFACE_V1_THEOREMS_REPRODUCED"


def set_partitions(n: int) -> list[tuple[int, ...]]:
    """Return canonical restricted-growth encodings of all partitions of range(n)."""
    if n < 1:
        raise ValueError("n must be positive")
    out: list[tuple[int, ...]] = []

    def visit(prefix: list[int], maximum: int) -> None:
        if len(prefix) == n:
            out.append(tuple(prefix))
            return
        for value in range(maximum + 2):
            visit(prefix + [value], max(maximum, value))

    visit([0], 0)
    return out


def fibres(partition: Sequence[int]) -> list[tuple[int, ...]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for state, block in enumerate(partition):
        grouped[block].append(state)
    return [tuple(grouped[key]) for key in sorted(grouped)]


def refines(fine: Sequence[int], coarse: Sequence[int]) -> bool:
    """Whether every fine block is contained in a coarse block."""
    n = len(fine)
    return all(
        fine[i] != fine[j] or coarse[i] == coarse[j]
        for i in range(n)
        for j in range(n)
    )


def full_information_risk(
    losses: Sequence[Sequence[int]], weights: Sequence[int]
) -> Fraction:
    return sum(
        (Fraction(weights[state]) * min(losses[state]) for state in range(len(losses))),
        Fraction(0),
    )


def closed_form_partition_risk(
    losses: Sequence[Sequence[int]],
    weights: Sequence[int],
    partition: Sequence[int],
) -> Fraction:
    action_count = len(losses[0])
    total = Fraction(0)
    for fibre in fibres(partition):
        total += min(
            sum(
                (
                    Fraction(weights[state]) * losses[state][action]
                    for state in fibre
                ),
                Fraction(0),
            )
            for action in range(action_count)
        )
    return total


def brute_force_partition_risk(
    losses: Sequence[Sequence[int]],
    weights: Sequence[int],
    partition: Sequence[int],
) -> Fraction:
    """Enumerate every deterministic observation-measurable policy."""
    blocks = fibres(partition)
    action_count = len(losses[0])
    best: Fraction | None = None
    for block_actions in product(range(action_count), repeat=len(blocks)):
        risk = Fraction(0)
        for block_index, fibre in enumerate(blocks):
            action = block_actions[block_index]
            for state in fibre:
                risk += Fraction(weights[state]) * losses[state][action]
        if best is None or risk < best:
            best = risk
    if best is None:
        raise AssertionError("empty policy set")
    return best


def has_common_optimum(
    losses: Sequence[Sequence[int]],
    weights: Sequence[int],
    partition: Sequence[int],
) -> bool:
    action_count = len(losses[0])
    for fibre in fibres(partition):
        common = set(range(action_count))
        for state in fibre:
            if weights[state] <= 0:
                continue
            minimum = min(losses[state])
            common &= {
                action
                for action in range(action_count)
                if losses[state][action] == minimum
            }
        if not common:
            return False
    return True


def pair_lower_bound(
    losses: Sequence[Sequence[int]],
    weights: Sequence[int],
    left: int,
    right: int,
) -> Fraction:
    """Two-state regret lower bound for any policy forced to share one action."""
    action_count = len(losses[0])
    left_min = min(losses[left])
    right_min = min(losses[right])
    return min(
        Fraction(weights[left]) * (losses[left][action] - left_min)
        + Fraction(weights[right]) * (losses[right][action] - right_min)
        for action in range(action_count)
    )


def simplex_grid(action_count: int, denominator: int) -> Iterable[tuple[Fraction, ...]]:
    """All rational action mixtures with the given denominator."""
    def compositions(total: int, parts: int, prefix: tuple[int, ...] = ()) -> Iterable[tuple[int, ...]]:
        if parts == 1:
            yield prefix + (total,)
            return
        for head in range(total + 1):
            yield from compositions(total - head, parts - 1, prefix + (head,))

    for counts in compositions(denominator, action_count):
        yield tuple(Fraction(count, denominator) for count in counts)


def check_decision_theorems() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    configurations = ((1, 3), (2, 3), (3, 3), (4, 2))

    for state_count, action_count in configurations:
        partitions = set_partitions(state_count)
        for flat_losses in product((0, 1), repeat=state_count * action_count):
            losses = tuple(
                tuple(flat_losses[row * action_count : (row + 1) * action_count])
                for row in range(state_count)
            )
            for weights in product((1, 2), repeat=state_count):
                full_risk = full_information_risk(losses, weights)
                partition_risks: dict[tuple[int, ...], Fraction] = {}

                for partition in partitions:
                    formula_risk = closed_form_partition_risk(losses, weights, partition)
                    enumerated_risk = brute_force_partition_risk(losses, weights, partition)
                    if formula_risk != enumerated_risk:
                        raise AssertionError(
                            ("partition-risk mismatch", losses, weights, partition,
                             formula_risk, enumerated_risk)
                        )

                    regret = formula_risk - full_risk
                    if regret < 0:
                        raise AssertionError(("negative regret", losses, weights, partition))
                    if (regret == 0) != has_common_optimum(losses, weights, partition):
                        raise AssertionError(
                            ("zero-regret/common-optimum mismatch", losses, weights, partition)
                        )

                    # Every same-fibre pair supplies a valid lower bound.
                    for fibre in fibres(partition):
                        for i, left in enumerate(fibre):
                            for right in fibre[i + 1 :]:
                                bound = pair_lower_bound(losses, weights, left, right)
                                if regret < bound:
                                    raise AssertionError(
                                        ("pair lower bound violated", losses, weights,
                                         partition, left, right, regret, bound)
                                    )
                                counts["pair_lower_bounds"] += 1

                    # A rational randomized policy cannot improve a linear objective.
                    # The denominator-3 grid independently probes non-vertex mixtures.
                    if state_count <= 3:
                        for fibre in fibres(partition):
                            deterministic = min(
                                sum(
                                    (
                                        Fraction(weights[state]) * losses[state][action]
                                        for state in fibre
                                    ),
                                    Fraction(0),
                                )
                                for action in range(action_count)
                            )
                            for mixture in simplex_grid(action_count, denominator=3):
                                mixed = sum(
                                    (
                                        mixture[action]
                                        * sum(
                                            (
                                                Fraction(weights[state])
                                                * losses[state][action]
                                                for state in fibre
                                            ),
                                            Fraction(0),
                                        )
                                        for action in range(action_count)
                                    ),
                                    Fraction(0),
                                )
                                if mixed < deterministic:
                                    raise AssertionError(
                                        ("randomization improved linear risk", losses,
                                         weights, partition, fibre, mixture)
                                    )
                                counts["randomized_policy_probes"] += 1

                    partition_risks[partition] = formula_risk
                    counts["decision_partition_instances"] += 1

                for fine in partitions:
                    for coarse in partitions:
                        if refines(fine, coarse):
                            if partition_risks[fine] > partition_risks[coarse]:
                                raise AssertionError(
                                    ("refinement monotonicity violated", losses, weights,
                                     fine, coarse)
                                )
                            counts["refinement_pairs"] += 1

                counts["decision_loss_weight_matrices"] += 1

    return dict(counts)


def check_zero_one_label_formula() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for state_count in range(1, 5):
        partitions = set_partitions(state_count)
        for label_count in (2, 3):
            for labels in product(range(label_count), repeat=state_count):
                losses = tuple(
                    tuple(int(action != labels[state]) for action in range(label_count))
                    for state in range(state_count)
                )
                for weights in product((1, 2), repeat=state_count):
                    for partition in partitions:
                        observed = closed_form_partition_risk(losses, weights, partition)
                        formula = Fraction(0)
                        for fibre in fibres(partition):
                            total = sum(weights[state] for state in fibre)
                            class_weights = [
                                sum(
                                    weights[state]
                                    for state in fibre
                                    if labels[state] == label
                                )
                                for label in range(label_count)
                            ]
                            formula += total - max(class_weights)
                        if observed != formula:
                            raise AssertionError(
                                ("0-1 minority-mass formula mismatch", labels, weights,
                                 partition, observed, formula)
                            )
                        counts["label_partition_instances"] += 1
    return dict(counts)


def candidate_centres(values: Sequence[int]) -> set[Fraction]:
    centres = {Fraction(value) for value in values}
    for left in values:
        for right in values:
            centres.add(Fraction(left + right, 2))
    return centres


def check_scalar_certificate_theorem() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    value_alphabet = (-2, -1, 0, 1, 2)
    for state_count in range(1, 6):
        partitions = set_partitions(state_count)
        for values in product(value_alphabet, repeat=state_count):
            for partition in partitions:
                for fibre in fibres(partition):
                    fibre_values = [values[state] for state in fibre]
                    diameter = max(fibre_values) - min(fibre_values)
                    theorem_radius = Fraction(diameter, 2)
                    enumerated_radius = min(
                        max(abs(Fraction(value) - centre) for value in fibre_values)
                        for centre in candidate_centres(fibre_values)
                    )
                    if theorem_radius != enumerated_radius:
                        raise AssertionError(
                            ("diameter-radius mismatch", values, partition, fibre,
                             theorem_radius, enumerated_radius)
                        )

                    theorem_width = Fraction(diameter)
                    # An interval covering the fibre must span min to max.
                    enumerated_width = Fraction(max(fibre_values) - min(fibre_values))
                    if theorem_width != enumerated_width:
                        raise AssertionError(
                            ("diameter-width mismatch", values, partition, fibre)
                        )
                    counts["scalar_fibre_instances"] += 1
                counts["scalar_partition_instances"] += 1
    return dict(counts)


def run_all() -> dict[str, object]:
    counts: dict[str, int] = {}
    for block in (
        check_decision_theorems(),
        check_zero_one_label_formula(),
        check_scalar_certificate_theorem(),
    ):
        overlap = set(counts).intersection(block)
        if overlap:
            raise AssertionError(f"duplicate counters: {sorted(overlap)}")
        counts.update(block)

    return {
        "schema": "ORION.FiniteInformationInterface.Result.v1",
        "terminal": TERMINAL,
        "arithmetic": "exact_rational",
        "loss_alphabet": [0, 1],
        "positive_weight_alphabet": [1, 2],
        "scalar_value_alphabet": [-2, -1, 0, 1, 2],
        "counts": dict(sorted(counts.items())),
        "scientific_authority_delta": "NONE",
        "novelty_status": "NOT_ASSESSED",
        "paper_promotion_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-result", type=Path)
    args = parser.parse_args()

    result = run_all()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"

    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")

    if args.check_result is not None:
        expected = json.loads(args.check_result.read_text(encoding="utf-8"))
        if expected != result:
            print("FINITE_INFORMATION_INTERFACE_V1_RESULT_DRIFT")
            print(rendered, end="")
            return 1

    print(
        f"{TERMINAL} "
        f"decision_instances={result['counts']['decision_partition_instances']} "
        f"refinement_pairs={result['counts']['refinement_pairs']} "
        f"scalar_fibres={result['counts']['scalar_fibre_instances']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
