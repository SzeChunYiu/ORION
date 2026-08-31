#!/usr/bin/env python3
"""Standalone finite checks for the low-order-information manuscript."""

from __future__ import annotations

import itertools
import json
import math
from functools import lru_cache
from typing import Iterable, Iterator, Sequence


PauliInstance = tuple[str, ...]
Partition = tuple[tuple[int, ...], ...]


def binary_width(size: int) -> int:
    return 0 if size == 1 else math.ceil(math.log2(size))


@lru_cache(maxsize=None)
def depth_cost(size: int) -> int:
    if size == 1:
        return 0
    return (
        depth_cost(math.ceil(size / 2))
        + depth_cost(math.floor(size / 2))
        + size
        - 2
    )


def term_weight(term: str) -> int:
    return sum(letter != "I" for letter in term)


def common_factor_count(instance: PauliInstance, block: Sequence[int]) -> int:
    return sum(
        len({instance[index][column] for index in block}) == 1
        and instance[block[0]][column] != "I"
        for column in range(len(instance[0]))
    )


def set_partitions(items: Sequence[int]) -> Iterator[Partition]:
    """Yield every set partition once, with canonical block ordering."""

    if not items:
        yield ()
        return
    first, *rest = items
    for partition in set_partitions(rest):
        yield ((first,),) + partition
        for index, block in enumerate(partition):
            yield partition[:index] + ((first,) + block,) + partition[index + 1 :]


def unary_cost(instance: PauliInstance) -> int:
    m = len(instance)
    return 2 * sum(map(term_weight, instance)) + 3 * m - 3


def partition_cost(instance: PauliInstance, partition: Partition) -> int:
    m = len(instance)
    total_weight = sum(map(term_weight, instance))
    if len(partition) == 1:
        width = binary_width(m)
        common = common_factor_count(instance, partition[0])
        return (
            (width + 1) * total_weight
            + m
            - 1
            + depth_cost(m)
            + width
            - (m * (width + 1) - 1) * common
        )

    cost = 2 * m + len(partition) - 3
    cost += sum(depth_cost(len(block)) for block in partition)
    cost += max(binary_width(len(block)) for block in partition)
    for block in partition:
        size = len(block)
        width = binary_width(size)
        common = common_factor_count(instance, block)
        weight = sum(term_weight(instance[index]) for index in block)
        cost += 2 * common + (width + 2) * (weight - size * common)
    return cost


def improvement(instance: PauliInstance, partition: Partition) -> int:
    return unary_cost(instance) - partition_cost(instance, partition)


def exact_optima(instance: PauliInstance) -> tuple[int, list[Partition], int]:
    best = -10**9
    optimizers: list[Partition] = []
    count = 0
    for partition in set_partitions(tuple(range(len(instance)))):
        count += 1
        value = improvement(instance, partition)
        if value > best:
            best = value
            optimizers = [partition]
        elif value == best:
            optimizers.append(partition)
    return best, optimizers, count


def pair_data(instance: PauliInstance) -> tuple[tuple[int, ...], tuple[int, ...]]:
    weights = tuple(map(term_weight, instance))
    common = tuple(
        common_factor_count(instance, pair)
        for pair in itertools.combinations(range(len(instance)), 2)
    )
    return weights, common


def disjoint_product(instance: PauliInstance, copies: int) -> PauliInstance:
    width = len(instance[0])
    output: list[str] = []
    for copy_index in range(copies):
        for term in instance:
            output.append(
                "I" * (copy_index * width)
                + term
                + "I" * ((copies - copy_index - 1) * width)
            )
    return tuple(output)


def four_term_witness_checks() -> dict[str, object]:
    instance = ("XXII", "XYII", "XZII", "XIXX")
    weights, common = pair_data(instance)
    pairs = list(itertools.combinations(range(4), 2))
    gains = {
        pair: 4 * common[index] - weights[pair[0]] - weights[pair[1]]
        for index, pair in enumerate(pairs)
    }
    disjoint_pair_clauses = [
        gains[pair] + gains[other] + 1
        for pair, other in itertools.combinations(pairs, 2)
        if set(pair).isdisjoint(other)
    ]
    one_block = (tuple(range(4)),)
    return {
        "unary_cost": unary_cost(instance),
        "one_block_cost": partition_cost(instance, one_block),
        "pair_clauses_hold": max(gains.values()) <= 0,
        "disjoint_pair_clauses_hold": max(disjoint_pair_clauses) <= 0,
        "expected_costs": unary_cost(instance) == 27
        and partition_cost(instance, one_block) == 23,
    }


def gadget_checks() -> dict[str, object]:
    gadget_a = ("XXXXII", "XXXIXI", "XXXIIX", "XXIIII", "XXIIII")
    gadget_b = ("XXXXII", "XXXIXI", "XXIXXI", "XXIIII", "XXIIII")
    a1, a1_optimizers, a1_count = exact_optima(gadget_a)
    b1, b1_optimizers, b1_count = exact_optima(gadget_b)
    a2, _a2_optimizers, a2_count = exact_optima(disjoint_product(gadget_a, 2))
    b2, _b2_optimizers, b2_count = exact_optima(disjoint_product(gadget_b, 2))

    b1_only_pairs_singletons = all(
        all(len(block) <= 2 for block in partition) for partition in b1_optimizers
    )
    a1_has_triple = all(
        any(len(block) == 3 for block in partition) for partition in a1_optimizers
    )
    return {
        "pair_data_equal": pair_data(gadget_a) == pair_data(gadget_b),
        "ordered_weights": list(pair_data(gadget_a)[0]),
        "partition_counts": {
            "five_terms_a": a1_count,
            "five_terms_b": b1_count,
            "ten_terms_a": a2_count,
            "ten_terms_b": b2_count,
        },
        "improvements": {"a1": a1, "b1": b1, "a2": a2, "b2": b2},
        "expected_improvements": (a1, b1, a2, b2) == (10, 9, 22, 19),
        "a1_optimizers_have_triple": a1_has_triple,
        "b1_optimizers_only_pairs_singletons": b1_only_pairs_singletons,
        "product_formula_finite_checks": all(
            (12 * t - 2) - (10 * t - 1) == 2 * t - 1
            for t in range(1, 101)
        ),
        "minimax_formula_checks": all(
            math.ceil((2 * t - 1) / 2) == t
            and (12 * t - 2) / (10 * t - 1) < 6 / 5
            for t in range(1, 101)
        ),
    }


def supersets(universe_size: int, subset: frozenset[int]) -> Iterable[frozenset[int]]:
    remainder = [index for index in range(universe_size) if index not in subset]
    for size in range(len(remainder) + 1):
        for extension in itertools.combinations(remainder, size):
            yield subset.union(extension)


def parity_kernel_checks() -> dict[str, object]:
    checked: dict[str, object] = {}
    all_checks = True
    for m in range(5, 10):
        q = m - 1
        delta = {
            frozenset(subset): (-1) ** (q - len(subset))
            for size in range(q + 1)
            for subset in itertools.combinations(range(q), size)
        }
        marginals_zero = all(
            sum(delta[superset] for superset in supersets(q, subset)) == 0
            for size in range(q)
            for subset in map(frozenset, itertools.combinations(range(q), size))
        )
        positive_mass = sum(value for value in delta.values() if value > 0)
        negative_mass = -sum(value for value in delta.values() if value < 0)
        mass_minimal = positive_mass == negative_mass == 2 ** (m - 2)
        all_checks = all_checks and marginals_zero and mass_minimal
        checked[str(m)] = {
            "proper_upper_marginals_zero": marginals_zero,
            "positive_mass": positive_mass,
            "negative_mass": negative_mass,
            "expected_primitive_mass": 2 ** (m - 2),
        }
    return {"all_checks": all_checks, "instances": checked}


def nested_booleans(value: object) -> Iterable[bool]:
    if isinstance(value, bool):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from nested_booleans(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            yield from nested_booleans(nested)


def main() -> int:
    result: dict[str, object] = {
        "schema": "low-order-information.public-verification.v1",
        "four_term_witness": four_term_witness_checks(),
        "gadgets": gadget_checks(),
        "parity_kernel": parity_kernel_checks(),
        "scope": (
            "Finite corroboration only; the manuscript proofs carry all-parameter claims."
        ),
    }
    result["all_checks"] = all(nested_booleans(result))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

