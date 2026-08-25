#!/usr/bin/env python3
"""Finite sanity checks for the five R5 mathematical addenda.

The written proofs carry the general authority. This script checks arithmetic,
small finite-group formulas, license-coordinate behavior, and the complete
C_5^2 length-ten classification used on the non-quantum 26-diagonal.
"""

from __future__ import annotations

import json
from itertools import combinations, permutations, product
from math import comb, factorial
from typing import Sequence

Vector = tuple[int, ...]


def zero(moduli: Sequence[int]) -> Vector:
    return tuple(0 for _ in moduli)


def add(x: Vector, y: Vector, moduli: Sequence[int]) -> Vector:
    return tuple((a + b) % m for a, b, m in zip(x, y, moduli, strict=True))


def scalar_mul(k: int, x: Vector, moduli: Sequence[int]) -> Vector:
    return tuple((k * a) % m for a, m in zip(x, moduli, strict=True))


def element_order(x: Vector, moduli: Sequence[int]) -> int:
    current = zero(moduli)
    for k in range(1, 1 + 10000):
        current = add(current, x, moduli)
        if current == zero(moduli):
            return k
    raise RuntimeError("finite order search exceeded bound")


def is_zero_sum_free_multiplicity(
    multiplicities: Sequence[int],
    alphabet: Sequence[Vector],
    moduli: Sequence[int],
) -> bool:
    for sub in product(*[range(m + 1) for m in multiplicities]):
        if not any(sub):
            continue
        total = zero(moduli)
        for count, letter in zip(sub, alphabet, strict=True):
            total = add(total, scalar_mul(count, letter, moduli), moduli)
        if total == zero(moduli):
            return False
    return True


def brute_zsf(alphabet: Sequence[Vector], moduli: Sequence[int]) -> int:
    orders = [element_order(letter, moduli) for letter in alphabet]
    answer = 0
    for multiplicities in product(*[range(order) for order in orders]):
        if is_zero_sum_free_multiplicity(multiplicities, alphabet, moduli):
            answer = max(answer, sum(multiplicities))
    return answer


def is_minimal_zero_sum(
    multiplicities: Sequence[int],
    alphabet: Sequence[Vector],
    moduli: Sequence[int],
) -> bool:
    if not any(multiplicities):
        return False
    total = zero(moduli)
    for count, letter in zip(multiplicities, alphabet, strict=True):
        total = add(total, scalar_mul(count, letter, moduli), moduli)
    if total != zero(moduli):
        return False
    target = tuple(multiplicities)
    for sub in product(*[range(m + 1) for m in multiplicities]):
        if not any(sub) or sub == target:
            continue
        subtotal = zero(moduli)
        for count, letter in zip(sub, alphabet, strict=True):
            subtotal = add(subtotal, scalar_mul(count, letter, moduli), moduli)
        if subtotal == zero(moduli):
            return False
    return True


def max_atom_length(alphabet: Sequence[Vector], moduli: Sequence[int], cap: int) -> int:
    orders = [element_order(letter, moduli) for letter in alphabet]
    answer = 0
    for multiplicities in product(*[range(order + 1) for order in orders]):
        if sum(multiplicities) <= cap and is_minimal_zero_sum(
            multiplicities, alphabet, moduli
        ):
            answer = max(answer, sum(multiplicities))
    return answer


def check_paper_a() -> dict[str, object]:
    standard_rows = []
    for moduli in ((2, 3, 4), (3, 5), (2, 2, 3)):
        alphabet = tuple(
            tuple(1 if i == j else 0 for i in range(len(moduli)))
            for j in range(len(moduli))
        )
        computed = brute_zsf(alphabet, moduli)
        expected = sum(n - 1 for n in moduli)
        assert computed == expected
        standard_rows.append({"moduli": moduli, "zsf": computed})

    h_moduli = (2, 4)
    source_alphabet = ((1, 0), (0, 1), (1, 1))
    source_zsf = brute_zsf(source_alphabet, h_moduli)
    image_alphabet = ((1,), (0,))
    image_zsf = brute_zsf(image_alphabet, (2,))
    image_atom = max_atom_length(image_alphabet, (2,), cap=2)
    kernel_davenport = 4
    upper = image_zsf + (kernel_davenport - 1) * image_atom
    assert source_zsf <= upper
    return {
        "standard_generator_formula": standard_rows,
        "quotient_example": {
            "source_zsf": source_zsf,
            "image_zsf": image_zsf,
            "max_image_atom": image_atom,
            "upper_bound": upper,
        },
    }


def support_volume(n: int, budget: int, labels: int) -> int:
    return sum(comb(n, size) * labels**size for size in range(budget + 1))


def check_paper_b() -> dict[str, object]:
    moduli_by_component = ((2, 3), (5,), (2, 2, 2))
    beta = tuple(sum(n - 1 for n in component) for component in moduli_by_component)
    kappa = (1, 1, 2)
    waste = tuple(b - k for b, k in zip(beta, kappa, strict=True))
    assert beta == (3, 4, 3)
    assert waste == (2, 3, 1)
    labels = (2, 3, 2)
    normalized = []
    asymptotic_constant = 1.0
    for b, k, q in zip(beta, kappa, labels, strict=True):
        asymptotic_constant *= q ** (b - k) * factorial(k) / factorial(b)
    for n in (40, 80, 160):
        certificate = 1
        intrinsic = 1
        for b, k, q in zip(beta, kappa, labels, strict=True):
            certificate *= support_volume(n, b, q)
            intrinsic *= support_volume(n, k, q)
        normalized.append((certificate / intrinsic) / n ** sum(waste))
    assert all(value > 0 for value in normalized)
    assert normalized[-1] > normalized[0]
    return {
        "component_budgets": beta,
        "intrinsic_budgets": kappa,
        "certificate_waste": waste,
        "common_scale_exponent": sum(waste),
        "leading_constant": asymptotic_constant,
        "normalized_ratio_samples": normalized,
    }


def radius(values: Sequence[float]) -> float:
    return (max(values) - min(values)) / 2


def check_paper_c() -> dict[str, object]:
    fibers = {"a": (2.0, 6.0, 5.0), "b": (-1.0, 1.0), "c": (8.0,)}
    global_radius = max(radius(values) for values in fibers.values())
    merged_radius = max(radius(fibers["a"] + fibers["b"]), radius(fibers["c"]))
    assert global_radius == 2.0
    assert merged_radius == 3.5
    assert merged_radius >= global_radius

    target_gap = 9.0
    feature_distance = 2.0
    lipschitz = 1.5
    lower = max(0.0, target_gap - lipschitz * feature_distance) / 2
    assert lower == 3.0
    predictions = (3.0, 6.0)
    targets = (0.0, 9.0)
    assert max(abs(p - t) for p, t in zip(predictions, targets, strict=True)) == lower
    return {
        "fiber_radii": {key: radius(value) for key, value in fibers.items()},
        "global_radius": global_radius,
        "coarsened_radius": merged_radius,
        "near_collision_lower_bound": lower,
    }


def horn_closure(
    seeds: set[str], rules: Sequence[tuple[frozenset[str], str]], refuted: set[str]
) -> frozenset[str]:
    reached = set(seeds) - refuted
    changed = True
    while changed:
        changed = False
        for body, head in rules:
            if head in refuted or body & refuted:
                continue
            if body <= reached and head not in reached:
                reached.add(head)
                changed = True
    return frozenset(reached)


def check_paper_d() -> dict[str, object]:
    rule_shapes = {
        "r_theorem": (frozenset({"theorem_seed"}), "bridge"),
        "r_bounded": (frozenset({"bounded_seed"}), "bridge"),
        "r_bridge": (frozenset({"bridge"}), "claim"),
    }
    caps = {
        "r_theorem": {"THEOREM"},
        "r_bounded": {"BOUNDED"},
        "r_bridge": {"THEOREM", "BOUNDED", "PROSPECTIVE"},
    }
    seed_labels = {
        "theorem_seed": {"THEOREM"},
        "bounded_seed": {"BOUNDED"},
        "bridge": set(),
        "claim": set(),
    }

    def projection(license_name: str) -> frozenset[str]:
        seeds = {q for q, labels in seed_labels.items() if license_name in labels}
        rules = [rule_shapes[r] for r, cap in caps.items() if license_name in cap]
        return horn_closure(seeds, rules, set())

    theorem_before = projection("THEOREM")
    seed_labels["bounded_seed"].add("UNRELATED")
    caps["r_bounded"].add("UNRELATED")
    theorem_after = projection("THEOREM")
    bounded = projection("BOUNDED")
    prospective = projection("PROSPECTIVE")
    assert theorem_before == theorem_after == frozenset(
        {"theorem_seed", "bridge", "claim"}
    )
    assert bounded == frozenset({"bounded_seed", "bridge", "claim"})
    assert prospective == frozenset()
    return {
        "theorem_projection": sorted(theorem_before),
        "bounded_projection": sorted(bounded),
        "unseeded_prospective_projection": sorted(prospective),
        "license_locality": "PASS",
    }


P = 5
VECTORS_2 = tuple((a, b) for a in range(P) for b in range(P) if (a, b) != (0, 0))


def determinant(x: tuple[int, int], y: tuple[int, int]) -> int:
    return (x[0] * y[1] - x[1] * y[0]) % P


def spans_rank_two(points: Sequence[tuple[int, int]]) -> bool:
    return any(determinant(x, y) != 0 for x, y in combinations(points, 2))


def has_short_zero_sum_bruteforce(
    points: Sequence[tuple[int, int]], multiplicities: Sequence[int], max_length: int = 5
) -> bool:
    for counts in product(*[range(m + 1) for m in multiplicities]):
        length = sum(counts)
        if not 1 <= length <= max_length:
            continue
        sx = sum(c * point[0] for c, point in zip(counts, points, strict=True)) % P
        sy = sum(c * point[1] for c, point in zip(counts, points, strict=True)) % P
        if sx == 0 and sy == 0:
            return True
    return False


def has_short_zero_sum_dp(
    points: Sequence[tuple[int, int]], multiplicities: Sequence[int], max_length: int = 5
) -> bool:
    reachable: set[tuple[int, tuple[int, int]]] = {(0, (0, 0))}
    for point, multiplicity in zip(points, multiplicities, strict=True):
        updated = set(reachable)
        for length, total in reachable:
            for count in range(1, multiplicity + 1):
                new_length = length + count
                if new_length > max_length:
                    break
                updated.add(
                    (
                        new_length,
                        (
                            (total[0] + count * point[0]) % P,
                            (total[1] + count * point[1]) % P,
                        ),
                    )
                )
        reachable = updated
    return any(length >= 1 and total == (0, 0) for length, total in reachable)


def unique_permutations(profile: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(set(permutations(profile))))


def classify_profile(profile: Sequence[int]) -> tuple[int, int]:
    tested = 0
    survivors = 0
    for points in combinations(VECTORS_2, len(profile)):
        if not spans_rank_two(points):
            continue
        for multiplicities in unique_permutations(profile):
            tested += 1
            brute = has_short_zero_sum_bruteforce(points, multiplicities)
            dp = has_short_zero_sum_dp(points, multiplicities)
            assert brute == dp
            if not brute:
                survivors += 1
    return tested, survivors


def check_nonquantum() -> dict[str, object]:
    profiles = ((4, 4, 2), (4, 2, 2, 2), (2, 2, 2, 2, 2))
    rows = []
    for profile in profiles:
        tested, survivors = classify_profile(profile)
        rows.append({"profile": profile, "tested": tested, "survivors": survivors})
    assert [row["tested"] for row in rows] == [6000, 42480, 42504]
    assert [row["survivors"] for row in rows] == [2160, 0, 0]

    basis = ((1, 0), (0, 1))
    remaining = tuple(vector for vector in VECTORS_2 if vector not in basis)
    allowed = tuple(
        candidate
        for candidate in remaining
        if not has_short_zero_sum_dp(basis + (candidate,), (4, 4, 2))
    )
    expected = (
        (1, 1), (1, 2), (1, 3), (1, 4), (2, 1),
        (2, 3), (3, 1), (3, 2), (4, 1),
    )
    assert allowed == expected
    swap_classes = {min((u, v), (v, u)) for u, v in allowed}
    assert swap_classes == {(1, 1), (1, 2), (1, 3), (1, 4), (2, 3)}

    normalized_4222 = sum(
        1
        for pair in combinations(remaining, 2)
        if not has_short_zero_sum_dp(basis + pair, (4, 2, 2, 2))
    )
    normalized_22222 = sum(
        1
        for triple in combinations(remaining, 3)
        if not has_short_zero_sum_dp(basis + triple, (2, 2, 2, 2, 2))
    )
    assert normalized_4222 == 0
    assert normalized_22222 == 0

    diagonal = []
    for c4 in range(3):
        support = 26 - c4
        c2 = 31 - support - 3 * c4
        c1 = 2 * support - 31 + 2 * c4
        diagonal.append((support, c1, c2, c4))
    assert diagonal == [(26, 21, 5, 0), (25, 21, 3, 1), (24, 21, 1, 2)]

    return {
        "raw_exact_classification": rows,
        "allowed_normalized_442_coordinates": allowed,
        "swap_classes": sorted(swap_classes),
        "normalized_excluded_profile_checks": {
            "4,2,2,2_states": comb(len(remaining), 2),
            "4,2,2,2_survivors": normalized_4222,
            "2,2,2,2,2_states": comb(len(remaining), 3),
            "2,2,2,2,2_survivors": normalized_22222,
        },
        "diagonal_26": diagonal,
        "independent_engines_agree": True,
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
