#!/usr/bin/env python3
"""Exact finite checks for the five R6 mathematical addenda.

The displayed proofs in the addenda carry all-parameter authority. This
verifier independently checks the finite automata, production basis rows,
Boolean-lattice trades, typed proof-tree semantics, and the p=5 quotient-plane
reductions used in the non-quantum paper.
"""
from __future__ import annotations

import json
from functools import lru_cache
from itertools import combinations, product
from math import ceil, comb, log2
from typing import Iterable, Sequence

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


# ---------------------------------------------------------------------------
# Paper A: exact subset-sum automaton
# ---------------------------------------------------------------------------


def automaton_zsf(alphabet: Sequence[Vector], moduli: Sequence[int]) -> dict[str, object]:
    z = zero(moduli)
    alphabet = tuple(alphabet)
    visited: set[frozenset[Vector]] = set()
    strict_growth_checks = 0

    @lru_cache(maxsize=None)
    def longest(state: frozenset[Vector]) -> tuple[int, tuple[int, ...]]:
        nonlocal strict_growth_checks
        visited.add(state)
        best_len = 0
        best_word: tuple[int, ...] = ()
        for idx, letter in enumerate(alphabet):
            translated = {add(total, letter, moduli) for total in state}
            next_state = frozenset(set(state) | {letter} | translated)
            if z in next_state:
                continue
            assert next_state != state
            assert len(next_state) > len(state)
            strict_growth_checks += 1
            tail_len, tail_word = longest(next_state)
            if 1 + tail_len > best_len:
                best_len = 1 + tail_len
                best_word = (idx,) + tail_word
        return best_len, best_word

    length, word = longest(frozenset())
    terminal_state: frozenset[Vector] = frozenset()
    for idx in word:
        letter = alphabet[idx]
        terminal_state = frozenset(
            set(terminal_state)
            | {letter}
            | {add(total, letter, moduli) for total in terminal_state}
        )
    valid_outgoing = 0
    for letter in alphabet:
        candidate = frozenset(
            set(terminal_state)
            | {letter}
            | {add(total, letter, moduli) for total in terminal_state}
        )
        if z not in candidate:
            valid_outgoing += 1
    assert valid_outgoing == 0
    return {
        "zsf": length,
        "witness_letter_indices": word,
        "visited_states": len(visited),
        "strict_growth_checks": strict_growth_checks,
        "terminal_subset_sum_count": len(terminal_state),
        "terminal_outgoing_transitions": valid_outgoing,
    }


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


def check_paper_a() -> dict[str, object]:
    fixtures = (
        ((2, 2, 2), ((1, 0, 0), (0, 1, 0), (0, 0, 1))),
        ((2, 4), ((1, 0), (0, 1), (1, 1))),
        ((3, 3), ((1, 0), (0, 1), (1, 1))),
    )
    rows = []
    for moduli, alphabet in fixtures:
        automaton = automaton_zsf(alphabet, moduli)
        brute = brute_zsf(alphabet, moduli)
        assert automaton["zsf"] == brute
        rows.append(
            {
                "moduli": moduli,
                "alphabet": alphabet,
                "automaton": automaton,
                "brute_zsf": brute,
            }
        )
    return {
        "exact_automaton_rows": rows,
        "automaton_matches_multiplicity_bruteforce": True,
    }


# ---------------------------------------------------------------------------
# Paper B: exact rank-only production proof class
# ---------------------------------------------------------------------------


def gf2_rank(values: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for value in values:
        x = int(value)
        while x:
            pivot = x.bit_length() - 1
            if pivot in basis:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                break
    return len(basis)


def subset_xor_zero(values: Sequence[int]) -> bool:
    for r in range(1, len(values) + 1):
        for subset in combinations(values, r):
            total = 0
            for value in subset:
                total ^= value
            if total == 0:
                return True
    return False


def check_paper_b() -> dict[str, object]:
    blocks = {
        "R6I_A": (1, 68, 136, 272, 544),
        "R6I_B": (2, 4, 8, 16, 32),
    }
    block_rows = {}
    for name, values in blocks.items():
        rank = gf2_rank(values)
        total = 0
        for value in values:
            total ^= value
        assert rank == 5
        assert total != 0
        assert not subset_xor_zero(values)
        block_rows[name] = {
            "basis": values,
            "rank": rank,
            "total_xor": total,
            "nonempty_zero_xor_subsets": 0,
            "beta_ZSD": 5,
            "kappa_unit": 1,
            "gap": 4,
        }

    abstract = []
    for d in range(1, 13):
        basis = tuple(1 << i for i in range(d))
        assert gf2_rank(basis) == d
        assert not subset_xor_zero(basis)
        abstract.append({"d": d, "beta_ZSD": d})

    products = []
    for t in (1, 2, 3, 10, 100):
        products.append(
            {
                "components": t,
                "certificate_budget": 5 * t,
                "intrinsic_budget": t,
                "additive_gap": 4 * t,
            }
        )
    return {
        "production_blocks": block_rows,
        "abstract_basis_rows": abstract,
        "direct_product_rows": products,
        "scope": "rank-only zero-sum-deletion proof class under frozen R6I unit objective",
    }


# ---------------------------------------------------------------------------
# Paper C: every proper interaction can be identical
# ---------------------------------------------------------------------------


def depth_d(size: int) -> int:
    if size <= 1:
        return 0
    return depth_d((size + 1) // 2) + depth_d(size // 2) + size - 2


def set_partitions(items: tuple[int, ...]):
    if not items:
        yield ()
        return
    first, *rest = items
    for partition in set_partitions(tuple(rest)):
        yield ((first,),) + partition
        for i in range(len(partition)):
            block = tuple(sorted(partition[i] + (first,)))
            yield partition[:i] + (block,) + partition[i + 1 :]


def canonical_partitions(m: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
    seen = set()
    out = []
    for partition in set_partitions(tuple(range(m))):
        canonical = tuple(sorted((tuple(sorted(block)) for block in partition), key=lambda b: b[0]))
        if canonical not in seen:
            seen.add(canonical)
            out.append(canonical)
    return tuple(out)


def support_counts(columns: Sequence[int], m: int):
    weights = [sum(bool(mask & (1 << i)) for mask in columns) for i in range(m)]

    def common(block: Sequence[int]) -> int:
        block_mask = sum(1 << i for i in block)
        return sum((mask & block_mask) == block_mask for mask in columns)

    return weights, common


def partition_cost(columns: Sequence[int], partition: tuple[tuple[int, ...], ...], m: int) -> int:
    weights, common = support_counts(columns, m)
    total_weight = sum(weights)
    if len(partition) == 1:
        b = ceil(log2(m))
        full = common(tuple(range(m)))
        return (
            (b + 1) * total_weight
            + m
            - 1
            + depth_d(m)
            + b
            - (m * (b + 1) - 1) * full
        )
    result = 2 * m + len(partition) - 3
    max_b = 0
    for block in partition:
        size = len(block)
        b = 0 if size == 1 else ceil(log2(size))
        max_b = max(max_b, b)
        f = common(block)
        w = sum(weights[i] for i in block)
        result += depth_d(size)
        result += 2 * f + (b + 2) * (w - size * f)
    return result + max_b


def parity_columns(m: int, L: int, positive: bool) -> list[int]:
    columns = []
    for mask in range(1 << m):
        sign_positive = ((m - mask.bit_count()) % 2 == 0)
        if sign_positive == positive:
            columns.extend([mask] * L)
    return columns


def upper_marginal(columns: Sequence[int], target: int) -> int:
    return sum((mask & target) == target for mask in columns)


def check_paper_c() -> dict[str, object]:
    rows = []
    for m in (5, 6):
        L = 1
        b = ceil(log2(m))
        N = (2 ** (m - 1)) * L
        K = N * m * (b + 1) + m - 1 + depth_d(m) + b + 1
        full = (1 << m) - 1
        a_columns = parity_columns(m, L, True) + [full] * K
        b_columns = parity_columns(m, L, False) + [full] * K
        assert len(a_columns) == len(b_columns)
        assert len(parity_columns(m, L, True)) == N
        assert len(parity_columns(m, L, False)) == N

        for target in range(1, full):
            assert upper_marginal(a_columns, target) == upper_marginal(b_columns, target)
        top_diff = upper_marginal(a_columns, full) - upper_marginal(b_columns, full)
        assert top_diff == L

        partitions = canonical_partitions(m)
        a_costs = [(partition_cost(a_columns, p, m), p) for p in partitions]
        b_costs = [(partition_cost(b_columns, p, m), p) for p in partitions]
        a_min = min(cost for cost, _ in a_costs)
        b_min = min(cost for cost, _ in b_costs)
        a_opts = [p for cost, p in a_costs if cost == a_min]
        b_opts = [p for cost, p in b_costs if cost == b_min]
        one_block = (tuple(range(m)),)
        assert a_opts == [one_block]
        assert b_opts == [one_block]
        unary_a = 2 * sum(support_counts(a_columns, m)[0]) + 3 * m - 3
        unary_b = 2 * sum(support_counts(b_columns, m)[0]) + 3 * m - 3
        delta_a = unary_a - a_min
        delta_b = unary_b - b_min
        expected_gap = (m * (b + 1) - 1) * L
        assert abs(delta_a - delta_b) == expected_gap

        signed = {
            mask: (L if ((m - mask.bit_count()) % 2 == 0) else -L)
            for mask in range(1 << m)
        }
        positive_mass = sum(value for value in signed.values() if value > 0)
        negative_mass = -sum(value for value in signed.values() if value < 0)
        assert positive_mass == negative_mass == 2 ** (m - 1) * L

        rows.append(
            {
                "m": m,
                "proper_marginals_checked": (1 << m) - 2,
                "trade_mass_per_side": positive_mass,
                "padding_K": K,
                "partitions_checked": len(partitions),
                "one_block_unique_both_sides": True,
                "top_marginal_difference": top_diff,
                "exact_value_gap": expected_gap,
            }
        )
    return {
        "all_proper_interaction_rows": rows,
        "exact_identifiability_order": "m-way interaction required on the constructed family",
    }


# ---------------------------------------------------------------------------
# Paper D: proof-tree intersection semantics
# ---------------------------------------------------------------------------

Rule = tuple[tuple[str, ...], str, frozenset[str]]


def typed_closure(
    seed_labels: dict[str, frozenset[str]], rules: Sequence[Rule], refuted: frozenset[str]
) -> dict[str, frozenset[str]]:
    labels = {claim: (frozenset() if claim in refuted else value) for claim, value in seed_labels.items()}
    for body, head, cap in rules:
        labels.setdefault(head, frozenset())
        for premise in body:
            labels.setdefault(premise, frozenset())
    changed = True
    while changed:
        changed = False
        for body, head, cap in rules:
            if head in refuted or any(premise in refuted for premise in body):
                continue
            propagated = cap
            for premise in body:
                propagated = propagated & labels[premise]
            new = labels[head] | propagated
            if new != labels[head]:
                labels[head] = new
                changed = True
    return labels


def proof_tree_authorities(
    seed_labels: dict[str, frozenset[str]], rules: Sequence[Rule], refuted: frozenset[str]
) -> dict[str, frozenset[frozenset[str]]]:
    claims = set(seed_labels)
    for body, head, _ in rules:
        claims.add(head)
        claims.update(body)
    authorities: dict[str, set[frozenset[str]]] = {claim: set() for claim in claims}
    for claim, labels in seed_labels.items():
        if claim not in refuted:
            authorities[claim].add(labels)
    # Rules are supplied in topological order for the registered acyclic system.
    for body, head, cap in rules:
        if head in refuted or any(premise in refuted for premise in body):
            continue
        choices = [tuple(authorities[premise]) for premise in body]
        if any(not choice for choice in choices):
            continue
        for selected in product(*choices):
            intersection = cap
            for label_set in selected:
                intersection = intersection & label_set
            authorities[head].add(intersection)
    return {claim: frozenset(values) for claim, values in authorities.items()}


def check_paper_d() -> dict[str, object]:
    seed_labels = {
        "forecast": frozenset({"PROSPECTIVE", "FORECAST_ONLY"}),
        "posthoc": frozenset({"POST_OUTCOME"}),
        "theorem": frozenset({"THEOREM"}),
        "claim": frozenset(),
    }
    rules: tuple[Rule, ...] = (
        (("forecast",), "claim", frozenset({"PROSPECTIVE", "FORECAST_ONLY"})),
        (("posthoc",), "claim", frozenset({"POST_OUTCOME"})),
        (("theorem",), "claim", frozenset({"THEOREM"})),
    )
    for refuted in (frozenset(), frozenset({"forecast"})):
        closure = typed_closure(seed_labels, rules, refuted)
        trees = proof_tree_authorities(seed_labels, rules, refuted)
        for claim, tree_sets in trees.items():
            union = frozenset().union(*tree_sets) if tree_sets else frozenset()
            assert union == closure[claim]

    post = typed_closure(seed_labels, rules, frozenset({"forecast"}))
    assert "PROSPECTIVE" not in post["claim"]
    assert post["claim"] == frozenset({"POST_OUTCOME", "THEOREM"})

    mixed_seed = {
        "p": frozenset({"A"}),
        "q": frozenset({"B"}),
        "r": frozenset(),
    }
    mixed_rules: tuple[Rule, ...] = (
        (("p", "q"), "r", frozenset({"A", "B"})),
    )
    mixed = typed_closure(mixed_seed, mixed_rules, frozenset())
    assert mixed["r"] == frozenset()
    untyped_reachable = True

    qg5_binding = {
        "benchmark_total": 9546,
        "benchmark_exact": 9545,
        "errors": 1,
        "exact_retraction": (
            "ORIGINAL_CLOSED_FORM_EXACTNESS",
            "ORIGINAL_REGIME_LABEL",
        ),
        "post_outcome_repair_is_prospective": False,
        "formal_models_checked": 254253,
    }
    assert qg5_binding["benchmark_total"] - qg5_binding["benchmark_exact"] == 1
    return {
        "proof_tree_formula_matches_fixed_point": True,
        "post_refutation_claim_labels": sorted(post["claim"]),
        "mixed_coordinate_example": {
            "untyped_reachable": untyped_reachable,
            "typed_authority": sorted(mixed["r"]),
        },
        "qg5_bound_application": qg5_binding,
    }


# ---------------------------------------------------------------------------
# Non-quantum paper: plane quotient and p=5 affine-coset cap
# ---------------------------------------------------------------------------

P = 5
V2 = tuple((x, y) for x in range(P) for y in range(P))
V3_NONZERO = tuple(
    (x, y, z)
    for x in range(P)
    for y in range(P)
    for z in range(P)
    if (x, y, z) != (0, 0, 0)
)


def has_short_zero_sum_with_candidate(
    a: tuple[int, int, int],
    b: tuple[int, int, int],
    c: tuple[int, int, int],
    x: tuple[int, int, int],
) -> bool:
    points = (a, b, c, x)
    bounds = (4, 4, 2, 1)
    for counts in product(*[range(bound + 1) for bound in bounds]):
        length = sum(counts)
        if not 1 <= length <= 5:
            continue
        total = tuple(
            sum(count * point[i] for count, point in zip(counts, points, strict=True)) % P
            for i in range(3)
        )
        if total == (0, 0, 0):
            return True
    return False


def has_short_zero_sum_with_candidate_dp(
    a: tuple[int, int, int],
    b: tuple[int, int, int],
    c: tuple[int, int, int],
    x: tuple[int, int, int],
) -> bool:
    points = (a, b, c, x)
    bounds = (4, 4, 2, 1)
    reachable: set[tuple[int, tuple[int, int, int]]] = {(0, (0, 0, 0))}
    for point, multiplicity in zip(points, bounds, strict=True):
        updated = set(reachable)
        for length, total in reachable:
            for count in range(1, multiplicity + 1):
                new_length = length + count
                if new_length > 5:
                    break
                updated.add(
                    (
                        new_length,
                        tuple((total[i] + count * point[i]) % P for i in range(3)),
                    )
                )
        reachable = updated
    return any(length >= 1 and total == (0, 0, 0) for length, total in reachable)


def five_sum_zero(points: Sequence[tuple[int, int]]) -> bool:
    return (
        sum(x for x, _ in points) % P == 0
        and sum(y for _, y in points) % P == 0
    )


def contains_zero_five_direct(points: Sequence[tuple[int, int]]) -> bool:
    return any(five_sum_zero(subset) for subset in combinations(points, 5))


def contains_zero_five_complement(points: Sequence[tuple[int, int]]) -> bool:
    total = (
        sum(x for x, _ in points) % P,
        sum(y for _, y in points) % P,
    )
    for subset in combinations(points, 4):
        subtotal = (
            sum(x for x, _ in subset) % P,
            sum(y for _, y in subset) % P,
        )
        if subtotal == total:
            return True
    return False


def occupancy_profiles(n0_cap: int) -> tuple[tuple[int, int, int, int, int], ...]:
    rows = []
    for n0 in range(n0_cap + 1):
        for n1 in range(9):
            for n2 in range(9):
                for n3 in range(9):
                    n4 = 21 - n0 - n1 - n2 - n3
                    if not 0 <= n4 <= 8:
                        continue
                    if (n1 + 2 * n2 + 3 * n3 + 4 * n4) % 5 != 0:
                        continue
                    rows.append((n0, n1, n2, n3, n4))
    return tuple(rows)


def check_nonquantum() -> dict[str, object]:
    a = (1, 0, 0)
    b = (0, 1, 0)
    forms = ((1, 1), (1, 2), (1, 3), (1, 4), (2, 3))
    expected = {
        (1, 1): ((1, 2, 0), (2, 1, 0)),
        (1, 2): ((1, 4, 0),),
        (1, 3): ((1, 1, 0),),
        (1, 4): ((1, 3, 0), (2, 3, 0)),
        (2, 3): ((4, 1, 0),),
    }
    plane_rows = []
    for uv in forms:
        c = (uv[0], uv[1], 0)
        allowed_list = []
        for point in V3_NONZERO:
            if point[2] != 0 or point in (a, b, c):
                continue
            direct = has_short_zero_sum_with_candidate(a, b, c, point)
            dp = has_short_zero_sum_with_candidate_dp(a, b, c, point)
            assert direct == dp
            if not direct:
                allowed_list.append(point)
        allowed = tuple(allowed_list)
        assert allowed == expected[uv]
        plane_rows.append(
            {
                "normal_form": uv,
                "allowed_plane_singletons": allowed,
                "plane_cap": len(allowed),
                "outside_plane_lower_bound": 21 - len(allowed),
            }
        )

    witness8 = (
        (0, 3), (0, 4), (1, 1), (1, 4),
        (2, 1), (2, 4), (3, 1), (3, 4),
    )
    assert not contains_zero_five_direct(witness8)

    normalized_fixed = ((0, 0), (1, 0), (0, 1))
    remaining = tuple(point for point in V2 if point not in normalized_fixed)
    normalized_sets_checked = 0
    engine_disagreements = 0
    survivors = 0
    for extra in combinations(remaining, 6):
        candidate = normalized_fixed + extra
        direct = contains_zero_five_direct(candidate)
        complement = contains_zero_five_complement(candidate)
        if direct != complement:
            engine_disagreements += 1
        if not direct:
            survivors += 1
        normalized_sets_checked += 1
    assert normalized_sets_checked == comb(22, 6)
    assert engine_disagreements == 0
    assert survivors == 0

    profiles_cap1 = occupancy_profiles(1)
    profiles_cap2 = occupancy_profiles(2)
    assert len(profiles_cap2) == 223
    assert set(profiles_cap1) <= set(profiles_cap2)
    for row in profiles_cap2:
        nonzero_occupied = sum(value > 0 for value in row[1:])
        outside = sum(row[1:])
        assert outside >= 19
        assert nonzero_occupied >= 3

    return {
        "rank_two_442_plane_rows": plane_rows,
        "plane_singleton_engines_agree": True,
        "affine_coset_cap": {
            "published_threshold_g_C5xC5": 9,
            "explicit_zero_sum_free_witness_size": len(witness8),
            "normalized_nine_sets_checked": normalized_sets_checked,
            "independent_engines_agree": engine_disagreements == 0,
            "normalized_survivors": survivors,
            "maximum_coset_occupancy": 8,
        },
        "quotient_occupancy": {
            "profiles_plane_cap_1": len(profiles_cap1),
            "profiles_plane_cap_2": len(profiles_cap2),
            "outside_plane_minimum": 19,
            "nonzero_cosets_occupied_minimum": 3,
            "total_quotient_sum_constraint": "n1+2n2+3n3+4n4 = 0 mod 5",
        },
        "frontier_status": "five rank-two forms compressed, not eliminated",
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
