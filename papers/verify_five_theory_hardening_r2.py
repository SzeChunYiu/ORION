#!/usr/bin/env python3
"""Independent finite corroboration for the five-paper hardening round R2.

The all-size statements are proved in the accompanying manuscripts.  This
program checks finite obligations, exact formulas, and non-promotion boundaries.
It grants no novelty, venue, external-replication, or physical-resource authority.
"""
from __future__ import annotations

import itertools
import json
import math
import random
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


def add_mod(x: tuple[int, ...], y: tuple[int, ...], moduli: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((a + b) % m for a, b, m in zip(x, y, moduli, strict=True))


def zero(moduli: tuple[int, ...]) -> tuple[int, ...]:
    return (0,) * len(moduli)


def has_zero_sum_subsequence(word: Sequence[tuple[int, ...]], moduli: tuple[int, ...]) -> bool:
    reachable = {zero(moduli)}
    # Track nonempty sums separately so the empty subsequence does not count.
    nonempty: set[tuple[int, ...]] = set()
    for item in word:
        shifted = {add_mod(s, item, moduli) for s in reachable}
        if zero(moduli) in shifted:
            return True
        nonempty |= shifted
        reachable |= shifted
    return False


def zsf_max_bruteforce(moduli: tuple[int, ...], alphabet: tuple[tuple[int, ...], ...], cap: int) -> int:
    """Maximum zero-sum-free word length, brute force for tiny registered controls."""
    best = 0
    for length in range(1, cap + 1):
        found = False
        for word in itertools.product(alphabet, repeat=length):
            if not has_zero_sum_subsequence(word, moduli):
                found = True
                best = length
                break
        if not found:
            break
    return best


def verify_alphabet_davenport() -> dict:
    controls = []
    examples = [
        ((3,), ((1,),), 2),
        ((4,), ((1,), (2,), (3,)), 3),
        ((2, 2), ((1, 0), (0, 1), (1, 1)), 2),
        ((2, 2, 2), tuple(x for x in itertools.product((0, 1), repeat=3) if any(x)), 3),
    ]
    for moduli, alphabet, expected in examples:
        observed = zsf_max_bruteforce(moduli, alphabet, cap=expected + 1)
        controls.append(
            {
                "group": "x".join(map(str, moduli)),
                "alphabet_size": len(alphabet),
                "observed_zsf": observed,
                "expected_zsf": expected,
                "matches": observed == expected,
            }
        )

    binary_rows = []
    for d in range(1, 5):
        basis = tuple(tuple(int(i == j) for i in range(d)) for j in range(d))
        moduli = (2,) * d
        basis_zsf = not has_zero_sum_subsequence(basis, moduli)
        every_d_plus_one_reducible = True
        # Exhaust d<=3.  At d=4 use every multiset of the complete nonzero alphabet,
        # which is enough as finite corroboration of the linear-dependence proof.
        alphabet = tuple(x for x in itertools.product((0, 1), repeat=d) if any(x))
        if d <= 3:
            iterator: Iterable[Sequence[tuple[int, ...]]] = itertools.product(alphabet, repeat=d + 1)
        else:
            iterator = itertools.combinations_with_replacement(alphabet, d + 1)
        checked = 0
        for word in iterator:
            checked += 1
            if not has_zero_sum_subsequence(word, moduli):
                every_d_plus_one_reducible = False
                break
        binary_rows.append(
            {
                "dimension": d,
                "basis_zero_sum_free": basis_zsf,
                "d_plus_one_words_checked": checked,
                "all_reducible": every_d_plus_one_reducible,
            }
        )

    return {
        "controls": controls,
        "binary_rows": binary_rows,
        "theorem": "support <= zsf(H;A); for F_2^d with a basis, zsf=d",
        "all_checks": all(row["matches"] for row in controls)
        and all(row["basis_zero_sum_free"] and row["all_reducible"] for row in binary_rows),
    }


def verify_pair_information_minimax() -> dict:
    rows = []
    for t in list(range(1, 21)) + [100, 1000, 10000]:
        a = 12 * t - 2
        b = 10 * t - 1
        gap = a - b
        real_radius = gap / 2
        integer_radius = math.ceil(gap / 2)
        symmetric_factor = math.sqrt(a / b)
        one_sided_factor = a / b
        midpoint = (a + b) / 2
        geometric = math.sqrt(a * b)
        rows.append(
            {
                "t": t,
                "A": a,
                "B": b,
                "gap": gap,
                "real_minimax_radius": real_radius,
                "integer_minimax_radius": integer_radius,
                "midpoint_attains": max(abs(midpoint - a), abs(midpoint - b)) == real_radius,
                "symmetric_factor": symmetric_factor,
                "geometric_attains": max(a / geometric, geometric / b) <= symmetric_factor + 1e-12,
                "one_sided_factor": one_sided_factor,
            }
        )

    increasing = all(rows[i]["symmetric_factor"] < rows[i + 1]["symmetric_factor"] for i in range(len(rows) - 1))
    limit = math.sqrt(6 / 5)
    return {
        "rows": rows,
        "uniform_symmetric_lower_bound_limit": limit,
        "uniform_one_sided_lower_bound_limit": 6 / 5,
        "all_checks": all(
            row["gap"] == 2 * row["t"] - 1
            and row["integer_minimax_radius"] == row["t"]
            and row["midpoint_attains"]
            and row["geometric_attains"]
            for row in rows
        )
        and increasing
        and rows[-1]["symmetric_factor"] < limit
        and limit - rows[-1]["symmetric_factor"] < 1e-5,
    }


@dataclass(frozen=True)
class TypedRule:
    antecedents: tuple[int, ...]
    head: int
    cap: int


def transfer(args: Sequence[int], cap: int, full_mask: int) -> int:
    if not args:
        return cap & full_mask
    value = full_mask
    for arg in args:
        value &= arg
    return value & cap


def typed_lfp(n: int, seeds: Sequence[int], rules: Sequence[TypedRule], refuted: set[int], full_mask: int) -> tuple[int, ...]:
    labels = [0 if q in refuted else seeds[q] for q in range(n)]
    while True:
        nxt = labels.copy()
        for rule in rules:
            if rule.head in refuted:
                continue
            candidate = transfer([labels[q] for q in rule.antecedents], rule.cap, full_mask)
            nxt[rule.head] |= candidate
        for q in refuted:
            nxt[q] = 0
        if nxt == labels:
            return tuple(labels)
        labels = nxt


def brute_least_fixed_point(n: int, seeds: Sequence[int], rules: Sequence[TypedRule], refuted: set[int], license_bits: int) -> tuple[int, ...]:
    full_mask = (1 << license_bits) - 1
    fixed = []
    for labels in itertools.product(range(1 << license_bits), repeat=n):
        expected = list(labels)
        for q in range(n):
            expected[q] = 0 if q in refuted else seeds[q]
        for rule in rules:
            if rule.head in refuted:
                continue
            expected[rule.head] |= transfer([labels[q] for q in rule.antecedents], rule.cap, full_mask)
        if tuple(expected) == labels:
            fixed.append(labels)
    if not fixed:
        raise AssertionError("finite monotone operator must have a fixed point")
    # Least point under componentwise subset inclusion.
    least_candidates = [
        x
        for x in fixed
        if all(all((xq & ~yq) == 0 for xq, yq in zip(x, y, strict=True)) for y in fixed)
    ]
    if len(least_candidates) != 1:
        raise AssertionError(f"expected unique least fixed point, got {least_candidates}")
    return tuple(least_candidates[0])


def verify_typed_authority() -> dict:
    # Licenses: theorem, finite_exact, bounded, prospective, post_outcome.
    THEOREM, FINITE, BOUNDED, PROSPECTIVE, POST = (1 << i for i in range(5))
    FULL = (1 << 5) - 1

    controls = {}
    unsupported = [TypedRule((0,), 1, FULL), TypedRule((1,), 0, FULL)]
    controls["unsupported_cycle_bottom"] = typed_lfp(2, [0, 0], unsupported, set(), FULL) == (0, 0)
    controls["seeded_cycle_propagates"] = typed_lfp(2, [THEOREM, 0], unsupported, set(), FULL) == (THEOREM, THEOREM)

    # A post-outcome repair can transmit theorem/finite/post-outcome licenses but
    # its cap cannot manufacture PROSPECTIVE authority.
    repair_cap = THEOREM | FINITE | POST
    labels = typed_lfp(2, [THEOREM | FINITE | PROSPECTIVE | POST, 0], [TypedRule((0,), 1, repair_cap)], set(), FULL)
    controls["post_outcome_cap_blocks_prospective"] = bool(labels[1] & POST) and not bool(labels[1] & PROSPECTIVE)

    # Bounded computation plus a rule capped below theorem cannot prove an exact theorem.
    nq_labels = typed_lfp(2, [BOUNDED, 0], [TypedRule((0,), 1, BOUNDED)], set(), FULL)
    controls["bounded_frontier_cannot_promote_theorem"] = nq_labels[1] == BOUNDED and not bool(nq_labels[1] & THEOREM)

    rng = random.Random(20260825)
    exact_failures = monotonic_failures = 0
    checked = 0
    for _ in range(300):
        n = 3
        bits = 2
        full = (1 << bits) - 1
        seeds = [rng.randrange(1 << bits) for _ in range(n)]
        rules = []
        for _ in range(rng.randrange(0, 5)):
            head = rng.randrange(n)
            size = rng.randrange(1, 3)
            ants = tuple(sorted(rng.sample(range(n), size)))
            cap = rng.randrange(1 << bits)
            rules.append(TypedRule(ants, head, cap))
        r1 = set(rng.sample(range(n), rng.randrange(0, 2)))
        remaining = [q for q in range(n) if q not in r1]
        r2 = r1 | set(rng.sample(remaining, rng.randrange(0, min(2, len(remaining)) + 1)))
        lfp1 = typed_lfp(n, seeds, rules, r1, full)
        brute1 = brute_least_fixed_point(n, seeds, rules, r1, bits)
        lfp2 = typed_lfp(n, seeds, rules, r2, full)
        exact_failures += int(lfp1 != brute1)
        monotonic_failures += int(any(b & ~a for a, b in zip(lfp1, lfp2, strict=True)))
        checked += 1

    return {
        "controls": controls,
        "random_systems_checked": checked,
        "least_fixed_point_disagreements": exact_failures,
        "refutation_monotonicity_failures": monotonic_failures,
        "all_checks": all(controls.values()) and exact_failures == 0 and monotonic_failures == 0,
    }


def multiplicity_patterns(support: int) -> list[tuple[int, int, int]]:
    out = []
    for c4 in range(0, 9):
        c2 = 31 - support - 3 * c4
        c1 = 2 * support - 31 + 2 * c4
        if c1 >= 0 and c2 >= 0 and c1 + c2 + c4 == support and c1 + 2 * c2 + 4 * c4 == 31:
            out.append((c1, c2, c4))
    return out


def verify_nonquantum_phase() -> dict:
    rows = []
    all_patterns = []
    for support in range(8, 32):
        patterns = multiplicity_patterns(support)
        for c1, c2, c4 in patterns:
            high_length = 2 * c2 + 4 * c4
            rank3_forced = high_length > 13  # donor eta(C_5^2)=13
            phase_formula = support + c4 <= 24
            all_patterns.append((support, c1, c2, c4, high_length, rank3_forced, phase_formula))
        rows.append(
            {
                "support": support,
                "patterns": [list(x) for x in patterns],
                "rank3_forced_c4": [c4 for _c1, _c2, c4 in patterns if support + c4 <= 24],
            }
        )

    phase_exact = all(rank3 == phase for *_prefix, rank3, phase in all_patterns)
    parity = all(c1 % 2 == 1 for _s, c1, _c2, _c4, _hl, _r, _p in all_patterns)
    support23 = multiplicity_patterns(23)
    support24 = multiplicity_patterns(24)

    # Atom-overlap budget identity: sum internal deficits plus cross-support
    # overlap equals total length minus global support. Exhaust tiny synthetic
    # atom support/multiplicity tables to corroborate the double count.
    atom_identity_checks = 0
    atom_identity_failures = 0
    rng = random.Random(31)
    for _ in range(1000):
        atoms = []
        for _atom in range(4):
            mults = {g: rng.randrange(0, 4) for g in range(8)}
            mults = {g: m for g, m in mults.items() if m}
            atoms.append(mults)
        total_length = sum(sum(atom.values()) for atom in atoms)
        global_support = {g for atom in atoms for g in atom}
        internal = sum(sum(atom.values()) - len(atom) for atom in atoms)
        cross = sum(sum(g in atom for atom in atoms) - 1 for g in global_support)
        atom_identity_checks += 1
        atom_identity_failures += int(internal + cross != total_length - len(global_support))

    return {
        "rows": rows,
        "support23_patterns": [list(x) for x in support23],
        "support24_patterns": [list(x) for x in support24],
        "phase_statement": "high-multiplicity stratum is forced rank three iff support+c4<=24 by eta(C_5^2)=13",
        "atom_overlap_budget": "sum_i(|U_i|-|supp U_i|)+sum_g(r_g-1)=31-|supp S|",
        "atom_identity_checks": atom_identity_checks,
        "atom_identity_failures": atom_identity_failures,
        "exact_d4_authority": False,
        "c0_31_authority": False,
        "support23_theorem_authority": False,
        "all_checks": phase_exact
        and parity
        and support23 == [(15, 8, 0), (17, 5, 1), (19, 2, 2)]
        and support24 == [(17, 7, 0), (19, 4, 1), (21, 1, 2)]
        and atom_identity_failures == 0,
    }


def main() -> int:
    result = {
        "paper_a_b": verify_alphabet_davenport(),
        "paper_c": verify_pair_information_minimax(),
        "paper_d": verify_typed_authority(),
        "nonquantum": verify_nonquantum_phase(),
    }
    result["all_checks"] = all(section["all_checks"] for section in result.values())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
