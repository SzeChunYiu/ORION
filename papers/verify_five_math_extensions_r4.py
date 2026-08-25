#!/usr/bin/env python3
"""Executable finite sanity checks for the five R4 mathematical addenda.

The script is not a proof assistant and does not replace the written proofs or
external donor theorems.  It checks the finite algebraic consequences that are
most vulnerable to transcription errors:

* Paper A: small-group zero-sum-free invariants and direct-sum additivity;
* Paper B: fixed-budget enumeration exponents and product arithmetic;
* Paper C: exact fiber radii on representative finite target sets;
* Paper D: the HITTING SET reduction used by the seed-blocker theorem; and
* non-quantum: multiplicity equations on the newly closed 25-diagonal.

Run from the repository root:

    python papers/verify_five_math_extensions_r4.py
"""

from __future__ import annotations

import json
from itertools import combinations, product
from math import comb
from typing import Iterable, Sequence

Vector = tuple[int, ...]


def add(x: Vector, y: Vector, moduli: Sequence[int]) -> Vector:
    return tuple((a + b) % m for a, b, m in zip(x, y, moduli, strict=True))


def scalar_mul(k: int, x: Vector, moduli: Sequence[int]) -> Vector:
    return tuple((k * a) % m for a, m in zip(x, moduli, strict=True))


def zero(moduli: Sequence[int]) -> Vector:
    return tuple(0 for _ in moduli)


def element_order(x: Vector, moduli: Sequence[int]) -> int:
    current = zero(moduli)
    for k in range(1, 1 + 10_000):
        current = add(current, x, moduli)
        if current == zero(moduli):
            return k
    raise RuntimeError("order search exceeded finite safety bound")


def is_zero_sum_free_multiplicity(
    multiplicities: Sequence[int],
    alphabet: Sequence[Vector],
    moduli: Sequence[int],
) -> bool:
    """Return whether the multiset has no nonempty zero-sum submultiset."""

    ranges = [range(u + 1) for u in multiplicities]
    for submultiplicities in product(*ranges):
        if not any(submultiplicities):
            continue
        total = zero(moduli)
        for count, letter in zip(submultiplicities, alphabet, strict=True):
            total = add(total, scalar_mul(count, letter, moduli), moduli)
        if total == zero(moduli):
            return False
    return True


def brute_zsf(alphabet: Sequence[Vector], moduli: Sequence[int]) -> int:
    """Compute zsf for small explicit alphabets by Proposition A4."""

    orders = [element_order(letter, moduli) for letter in alphabet]
    optimum = 0
    for multiplicities in product(*[range(order) for order in orders]):
        if is_zero_sum_free_multiplicity(multiplicities, alphabet, moduli):
            optimum = max(optimum, sum(multiplicities))
    return optimum


def check_paper_a() -> dict[str, object]:
    # H1 = C2^2 with its basis: zsf = 2.
    moduli_1 = (2, 2)
    alphabet_1 = ((1, 0), (0, 1))

    # H2 = C3 with alphabet {1}: two copies are zero-sum-free, three are not.
    moduli_2 = (3,)
    alphabet_2 = ((1,),)

    # Axis-separated direct sum.
    moduli = (2, 2, 3)
    alphabet = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

    z1 = brute_zsf(alphabet_1, moduli_1)
    z2 = brute_zsf(alphabet_2, moduli_2)
    z = brute_zsf(alphabet, moduli)

    assert (z1, z2, z) == (2, 2, 4)
    assert z == z1 + z2

    # Quotient lower-bound example: C6 -> C3 sends 1 to 1.
    source_z = brute_zsf(((1,),), (6,))
    image_z = brute_zsf(((1,),), (3,))
    assert source_z >= image_z

    return {
        "component_zsf": [z1, z2],
        "direct_sum_zsf": z,
        "quotient_example": {"source": source_z, "image": image_z},
    }


def support_volume(n: int, budget: int, labels: int) -> int:
    return sum(comb(n, j) * labels**j for j in range(budget + 1))


def check_paper_b() -> dict[str, object]:
    beta = (2, 5, 1)
    kappa = (1, 1, 1)
    assert sum(beta) == 8
    assert sum(kappa) == 3
    assert sum(b - k for b, k in zip(beta, kappa, strict=True)) == 5

    # A finite leading-degree check for B=5, K=3.  The normalized ratio
    # V_B/V_K divided by n^(B-K) stabilizes away from zero and infinity.
    ratios = []
    for n in (40, 80, 160):
        ratio = support_volume(n, 5, 2) / support_volume(n, 3, 2)
        ratios.append(ratio / n**2)
    assert all(0.001 < value < 10 for value in ratios)

    return {
        "abstract_product_budget": sum(beta),
        "intrinsic_product_budget": sum(kappa),
        "exponent_gap": 5,
        "normalized_ratio_samples": ratios,
    }


def deterministic_absolute_radius(values: Sequence[float]) -> tuple[float, float]:
    low = min(values)
    high = max(values)
    midpoint = (low + high) / 2
    radius = max(abs(midpoint - value) for value in values)
    return midpoint, radius


def check_paper_c() -> dict[str, object]:
    values = (7.0, 10.0, 12.0)
    midpoint, radius = deterministic_absolute_radius(values)
    diameter = max(values) - min(values)
    assert midpoint == 9.5
    assert radius == diameter / 2 == 2.5

    # Pair family at t=4: Delta_A=46, Delta_B=39, gap=7.
    t = 4
    delta_a = 12 * t - 2
    delta_b = 10 * t - 1
    gap = delta_a - delta_b
    assert gap == 2 * t - 1
    assert deterministic_absolute_radius((delta_a, delta_b))[1] == gap / 2
    assert gap**2 / 4 == 12.25

    # Boolean fiber with opposite labels has randomized minimax error 1/2.
    for q in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert max(q, 1 - q) >= 0.5

    return {
        "finite_fiber": {"values": values, "midpoint": midpoint, "radius": radius},
        "pair_family_t4": {
            "Delta_A": delta_a,
            "Delta_B": delta_b,
            "diameter": gap,
            "absolute_radius": gap / 2,
            "squared_radius": gap**2 / 4,
        },
    }


def is_hitting_set(edges: Sequence[frozenset[int]], refuted: frozenset[int]) -> bool:
    return all(edge & refuted for edge in edges)


def reduced_target_reachable(
    edges: Sequence[frozenset[int]], refuted: frozenset[int]
) -> bool:
    """Reachability in the depth-two graph from Theorem D4.

    Intermediate p_j survives exactly when all seeds in E_j survive; q survives
    when at least one p_j survives.
    """

    return any(edge.isdisjoint(refuted) for edge in edges)


def check_paper_d() -> dict[str, object]:
    universe = frozenset(range(5))
    edges = (
        frozenset({0, 1}),
        frozenset({1, 2, 3}),
        frozenset({3, 4}),
    )

    checked = 0
    minimum = None
    for size in range(len(universe) + 1):
        for choice in combinations(universe, size):
            refuted = frozenset(choice)
            hitting = is_hitting_set(edges, refuted)
            blocked = not reduced_target_reachable(edges, refuted)
            assert hitting == blocked
            checked += 1
            if hitting and minimum is None:
                minimum = size

    assert minimum == 2
    return {"subsets_checked": checked, "minimum_seed_blocker": minimum}


def admissible_multiplicity_rows() -> list[tuple[int, int, int, int]]:
    rows: list[tuple[int, int, int, int]] = []
    for support in range(1, 32):
        for c4 in range(0, 32):
            c2 = 31 - support - 3 * c4
            c1 = 2 * support - 31 + 2 * c4
            if min(c1, c2, c4) < 0:
                continue
            if c1 + c2 + c4 != support:
                continue
            if c1 + 2 * c2 + 4 * c4 != 31:
                continue
            rows.append((support, c1, c2, c4))
    return rows


def check_nonquantum() -> dict[str, object]:
    rows = admissible_multiplicity_rows()
    diagonal = [
        row for row in rows if row[0] >= 23 and row[0] + row[3] == 25
    ]
    expected = [
        (23, 19, 2, 2),
        (24, 17, 4, 1),
        (25, 15, 6, 0),
    ]
    assert diagonal == expected

    for support, _c1, _c2, c4 in diagonal:
        high_length = 62 - 2 * (support + c4)
        assert high_length == 12

    # Algebraic consequence of the Property-C low-rank shape: c4=3 and c2=0.
    c4 = 3
    c2 = 0
    support = 31 - 3 * c4 - c2
    c1 = support - c4
    assert (support, c1, c2, c4) == (22, 19, 0, 3)

    return {
        "new_full_rank_diagonal": diagonal,
        "unique_low_rank_boundary_profile": (22, 19, 0, 3),
    }


def main() -> None:
    report = {
        "paper_A": check_paper_a(),
        "paper_B": check_paper_b(),
        "paper_C": check_paper_c(),
        "paper_D": check_paper_d(),
        "nonquantum": check_nonquantum(),
        "status": "PASS",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
