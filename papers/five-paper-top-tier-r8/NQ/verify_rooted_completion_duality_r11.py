#!/usr/bin/env python3
"""Finite controls for rooted one-term zero-sum completion duality.

The analytic Markdown proof owns all-size authority.  This verifier works with
occurrence-labelled finite sequences, independently computes exact packing
numbers, enumerates every maximum packing on complete small panels, checks the
rooted packing/factorization bijection and hereditary packing lattice, and
freezes the conditional C5^3 rooted length skeletons.
"""
from __future__ import annotations

import functools
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Sequence

SCHEMA = "ORION.NQ.RootedCompletionDuality.R11.v1"
SEED = 20260826

GroupElement = tuple[int, ...]
Packing = frozenset[int]


@functools.lru_cache(maxsize=None)
def set_partitions(size: int) -> tuple[tuple[int, ...], ...]:
    """All set partitions of occurrence indices, represented by disjoint masks."""
    if size == 0:
        return ((),)
    previous = set_partitions(size - 1)
    bit = 1 << (size - 1)
    out: set[tuple[int, ...]] = set()
    for partition in previous:
        out.add(tuple(sorted((*partition, bit))))
        for index, block in enumerate(partition):
            updated = list(partition)
            updated[index] = block | bit
            out.add(tuple(sorted(updated)))
    return tuple(sorted(out))


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def add(a: GroupElement, b: GroupElement, moduli: tuple[int, ...]) -> GroupElement:
    return tuple((x + y) % modulus for x, y, modulus in zip(a, b, moduli))


def neg(a: GroupElement, moduli: tuple[int, ...]) -> GroupElement:
    return tuple((-x) % modulus for x, modulus in zip(a, moduli))


def sequence_sum(
    sequence: Sequence[GroupElement], moduli: tuple[int, ...]
) -> GroupElement:
    total = tuple(0 for _ in moduli)
    for element in sequence:
        total = add(total, element, moduli)
    return total


def mask_sum(
    sequence: Sequence[GroupElement], mask: int, moduli: tuple[int, ...]
) -> GroupElement:
    total = tuple(0 for _ in moduli)
    index = 0
    while mask:
        if mask & 1:
            total = add(total, sequence[index], moduli)
        index += 1
        mask >>= 1
    return total


def zero_sum_masks(
    sequence: Sequence[GroupElement], moduli: tuple[int, ...]
) -> tuple[int, ...]:
    zero = tuple(0 for _ in moduli)
    return tuple(
        mask
        for mask in range(1, 1 << len(sequence))
        if mask_sum(sequence, mask, moduli) == zero
    )


def packing_solver(sequence: Sequence[GroupElement], moduli: tuple[int, ...]):
    """Return exact packing number and all maximum occurrence-labelled packings."""
    edges = zero_sum_masks(sequence, moduli)
    by_bit: dict[int, tuple[int, ...]] = {}
    for bit_index in range(len(sequence)):
        bit = 1 << bit_index
        by_bit[bit] = tuple(edge for edge in edges if edge & bit)

    @functools.lru_cache(maxsize=None)
    def value(mask: int) -> int:
        if mask == 0:
            return 0
        bit = mask & -mask
        best = value(mask ^ bit)
        for edge in by_bit[bit]:
            if edge & mask == edge:
                best = max(best, 1 + value(mask ^ edge))
        return best

    @functools.lru_cache(maxsize=None)
    def maximum_packings(mask: int) -> tuple[Packing, ...]:
        target = value(mask)
        if target == 0:
            return (frozenset(),)
        bit = mask & -mask
        out: set[Packing] = set()
        if value(mask ^ bit) == target:
            out.update(maximum_packings(mask ^ bit))
        for edge in by_bit[bit]:
            if edge & mask != edge:
                continue
            rest = mask ^ edge
            if 1 + value(rest) != target:
                continue
            for packing in maximum_packings(rest):
                out.add(frozenset((*packing, edge)))
        return tuple(sorted(out, key=lambda row: (len(row), tuple(sorted(row)))))

    full = (1 << len(sequence)) - 1
    return value, maximum_packings, full, set(edges)


def independent_partition_value(
    sequence: Sequence[GroupElement], moduli: tuple[int, ...]
) -> int:
    """Independent Bell-partition oracle for the maximum packing number."""
    zero = tuple(0 for _ in moduli)
    return max(
        (
            sum(mask_sum(sequence, block, moduli) == zero for block in partition)
            for partition in set_partitions(len(sequence))
        ),
        default=0,
    )


def is_atom(mask: int, zero_masks: set[int]) -> bool:
    if mask not in zero_masks:
        return False
    proper = (mask - 1) & mask
    while proper:
        if proper in zero_masks:
            return False
        proper = (proper - 1) & mask
    return True


def check_sequence(
    sequence: tuple[GroupElement, ...],
    moduli: tuple[int, ...],
    *,
    independent_partition_check: bool,
) -> dict[str, int]:
    value_m, packings_m, full_m, zero_m = packing_solver(sequence, moduli)
    k = value_m(full_m)
    maxima_m = packings_m(full_m)
    maxima_m_set = set(maxima_m)

    completion = neg(sequence_sum(sequence, moduli), moduli)
    completed = (*sequence, completion)
    root_bit = 1 << len(sequence)
    value_s, packings_s, full_s, zero_s = packing_solver(completed, moduli)
    maxima_s = packings_s(full_s)

    assert value_s(full_s) == k + 1
    assert all(any(edge & root_bit for edge in packing) for packing in maxima_s)
    independent_checks = 0
    if independent_partition_check:
        assert independent_partition_value(sequence, moduli) == k
        assert independent_partition_value(completed, moduli) == k + 1
        independent_checks = 2

    image: set[Packing] = set()
    hereditary_checks = 0
    atom_checks = 0
    residue_zero_free_checks = 0

    for packing in maxima_m:
        used = 0
        for edge in packing:
            assert used & edge == 0
            used |= edge
            assert is_atom(edge, zero_m)
            atom_checks += 1
        residue = full_m ^ used
        assert value_m(residue) == 0
        residue_zero_free_checks += 1
        rooted_atom = residue | root_bit
        assert is_atom(rooted_atom, zero_s)
        atom_checks += 1
        image.add(frozenset((*packing, rooted_atom)))

        factors = tuple(sorted(packing))
        for subset_mask in range(1 << len(factors)):
            selected = 0
            chosen = 0
            for index, edge in enumerate(factors):
                if subset_mask & (1 << index):
                    selected |= edge
                    chosen += 1
            assert value_m(selected) == chosen
            assert value_m(selected | residue) == chosen
            hereditary_checks += 2

    assert image == set(maxima_s)

    for factorization in maxima_s:
        used = 0
        root_edges = []
        for edge in factorization:
            assert used & edge == 0
            used |= edge
            assert is_atom(edge, zero_s)
            atom_checks += 1
            if edge & root_bit:
                root_edges.append(edge)
        assert used == full_s
        assert len(root_edges) == 1
        rooted_atom = root_edges[0]
        source_packing = frozenset(
            edge for edge in factorization if edge != rooted_atom
        )
        assert source_packing in maxima_m_set
        residue = rooted_atom ^ root_bit
        assert value_m(residue) == 0
        residue_zero_free_checks += 1

        factors = tuple(sorted(factorization))
        for subset_mask in range(1 << len(factors)):
            selected = 0
            chosen = 0
            for index, edge in enumerate(factors):
                if subset_mask & (1 << index):
                    selected |= edge
                    chosen += 1
            # Restrict the completed sequence to the selected occurrence set.
            assert value_s(selected) == chosen
            hereditary_checks += 1

    return {
        "source_maximum_packings": len(maxima_m),
        "rooted_maximum_factorizations": len(maxima_s),
        "hereditary_lattice_checks": hereditary_checks,
        "atom_checks": atom_checks,
        "residue_zero_free_checks": residue_zero_free_checks,
        "independent_partition_oracle_checks": independent_checks,
    }


def group_elements(moduli: tuple[int, ...]) -> tuple[GroupElement, ...]:
    return tuple(itertools.product(*(range(modulus) for modulus in moduli)))


def complete_small_panels() -> dict[str, object]:
    specifications = (
        ("C2", (2,), 8),
        ("C3", (3,), 7),
        ("C4", (4,), 6),
        ("C2xC2", (2, 2), 6),
    )
    rows = []
    totals = {
        "sequences": 0,
        "source_maximum_packings": 0,
        "rooted_maximum_factorizations": 0,
        "hereditary_lattice_checks": 0,
        "atom_checks": 0,
        "residue_zero_free_checks": 0,
        "independent_partition_oracle_checks": 0,
    }
    for name, moduli, maximum_length in specifications:
        elements = group_elements(moduli)
        group_counts = {key: 0 for key in totals}
        for length in range(maximum_length + 1):
            for sequence in itertools.combinations_with_replacement(elements, length):
                counts = check_sequence(
                    sequence, moduli, independent_partition_check=True
                )
                group_counts["sequences"] += 1
                for key, value in counts.items():
                    group_counts[key] += value
        rows.append(
            {
                "group": name,
                "moduli": list(moduli),
                "maximum_length": maximum_length,
                **group_counts,
            }
        )
        for key, value in group_counts.items():
            totals[key] += value
    return {"groups": rows, "totals": totals}


def generated_rank_three_controls() -> dict[str, int]:
    rng = random.Random(SEED)
    moduli = (5, 5, 5)
    elements = group_elements(moduli)
    cases = 0
    source_packings = 0
    rooted_factorizations = 0
    hereditary_checks = 0
    for length in range(0, 10):
        for _ in range(30):
            sequence = tuple(sorted(rng.choice(elements) for _ in range(length)))
            counts = check_sequence(
                sequence, moduli, independent_partition_check=False
            )
            cases += 1
            source_packings += counts["source_maximum_packings"]
            rooted_factorizations += counts["rooted_maximum_factorizations"]
            hereditary_checks += counts["hereditary_lattice_checks"]
    return {
        "generated_cases": cases,
        "maximum_length": 9,
        "source_maximum_packings": source_packings,
        "rooted_maximum_factorizations": rooted_factorizations,
        "hereditary_lattice_checks": hereditary_checks,
    }


def rooted_c5_cubed_skeletons() -> dict[str, object]:
    rows = []
    for root_atom_length in range(6, 14):
        residue_length = root_atom_length - 1
        triples = []
        for a in range(6, 14):
            for b in range(a, 14):
                for c in range(b, 14):
                    if root_atom_length + a + b + c == 31:
                        triples.append([a, b, c])
        if triples:
            rows.append(
                {
                    "residue_length": residue_length,
                    "root_atom_length": root_atom_length,
                    "avoiding_atom_length_triples": triples,
                    "triple_count": len(triples),
                }
            )
    unrooted = {
        tuple(sorted((row["root_atom_length"], *triple)))
        for row in rows
        for triple in row["avoiding_atom_length_triples"]
    }
    assert len(rows) == 8
    assert sum(row["triple_count"] for row in rows) == 31
    assert len(unrooted) == 11
    assert all(5 <= row["residue_length"] <= 12 for row in rows)
    return {
        "conditional_on": {
            "D3_C5_cubed": 25,
            "ordinary_D_C5_cubed": 13,
            "source_length": 30,
            "completion_length": 31,
            "short_free_threshold": 5,
        },
        "rooted_residue_classes": rows,
        "rooted_skeleton_count": 31,
        "unrooted_skeleton_count": 11,
    }


def run() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "NQ_ROOTED_COMPLETION_DUALITY_R11_PASS",
        "complete_small_panels": complete_small_panels(),
        "generated_rank_three_controls": generated_rank_three_controls(),
        "rooted_c5_cubed_skeletons": rooted_c5_cubed_skeletons(),
        "authority": {
            "universal_theorem_from_computation": False,
            "finite_controls_exact": True,
            "D3_C5_cubed_independently_replayed": False,
            "D4_C5_cubed_closed": False,
            "generic_block_monoid_novelty_claimed": False,
            "generic_hypergraph_matching_novelty_claimed": False,
            "external_novelty_review_complete": False,
            "journal_authority": False,
        },
    }
    payload = canonical_json(result).encode()
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    Path(__file__).with_name("ROOTED_COMPLETION_DUALITY_R11_RESULTS.json").write_text(
        text, encoding="utf-8"
    )
    print("NQ_ROOTED_COMPLETION_DUALITY_R11_PASS")
    print(text, end="")


if __name__ == "__main__":
    main()
