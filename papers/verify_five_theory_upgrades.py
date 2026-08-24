#!/usr/bin/env python3
"""Additive publication verifier for the five-paper theory wave.

This script verifies only the new mathematical upgrade obligations and binds the
pre-existing frozen evidence.  It does not grant novelty, venue, external
replication, or physical-resource authority.
"""
from __future__ import annotations

import itertools
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


# ---------------------------------------------------------------------------
# Paper A: arbitrary-block Restore sensitivity
# ---------------------------------------------------------------------------
def restore_b(values: tuple[int, ...]) -> int:
    if values and all(v == values[0] != 0 for v in values):
        return 1
    return sum(v != 0 for v in values)


def verify_a() -> dict:
    rows = []
    for b in range(2, 8):
        histogram = Counter()
        maximum = -10**9
        for position in range(b):
            for old in itertools.product(range(4), repeat=b):
                old_value = restore_b(old)
                for new_letter in range(4):
                    new = list(old)
                    new[position] = new_letter
                    delta = restore_b(tuple(new)) - old_value
                    histogram[delta] += 1
                    maximum = max(maximum, delta)
        rows.append(
            {
                "blocks": b,
                "maximum_increase": maximum,
                "theorem_value": b - 1,
                "matches": maximum == b - 1,
            }
        )
    return {
        "rows": rows,
        "all_checks": all(row["matches"] for row in rows),
        "symbolic_extension": "one-letter increase <= b-1 for every b>=2",
        "certificate_cone": "mu >= (b-1)*t_R",
    }


# ---------------------------------------------------------------------------
# Paper B: exact rank-only terminal length and tight/loose compiler controls
# ---------------------------------------------------------------------------
def verify_b() -> dict:
    exhaustive = []
    for d in range(1, 4):
        checked = failures = 0
        length = d + 1
        for word in itertools.product(range(1 << d), repeat=length):
            if xor(word) == 0:
                continue
            checked += 1
            reducible = False
            for size in range(1, length):
                for subset in itertools.combinations(range(length), size):
                    if xor(tuple(word[i] for i in subset)) == 0:
                        reducible = True
                        break
                if reducible:
                    break
            failures += int(not reducible)
        basis = tuple(1 << i for i in range(d))
        basis_zero_subsets = sum(
            1
            for size in range(1, d + 1)
            for subset in itertools.combinations(basis, size)
            if xor(subset) == 0
        )
        exhaustive.append(
            {
                "dimension": d,
                "words_checked": checked,
                "upper_failures": failures,
                "basis_total_nonzero": xor(basis) != 0,
                "basis_zero_subset_count": basis_zero_subsets,
            }
        )

    b_result = json.loads(
        (ROOT / "research/extensions/orion-qg/PAPER_B_B1_RANK_ONLY_PROOF_GAP_RESULTS_2026-08-24.json").read_text()
    )
    a_result = json.loads(
        (ROOT / "research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json").read_text()
    )
    return {
        "small_dimension_exhaustive": exhaustive,
        "rank_theorem_checks": all(
            row["upper_failures"] == 0
            and row["basis_total_nonzero"]
            and row["basis_zero_subset_count"] == 0
            for row in exhaustive
        ),
        "r6m_rank_only_certificate": 2,
        "r6m_intrinsic_support": a_result["r6m_parent_binding"]["sharp_kappa"],
        "r6i_terminal": b_result["terminal"],
        "r6i_certificate": 5,
        "r6i_intrinsic": 1,
        "tight_control": a_result["r6m_parent_binding"]["sharp_kappa"] == 2,
        "loose_control": "5_VS_INTRINSIC_1" in b_result["terminal"],
    }


# ---------------------------------------------------------------------------
# Paper C: Boolean-lattice proper-marginal kernel
# ---------------------------------------------------------------------------
def upper_marginal(delta: dict[int, int], q: int, target: int) -> int:
    return sum(value for support, value in delta.items() if support & target == target)


def reconstruct_from_marginals(q: int, c: int) -> dict[int, int]:
    """Downward inversion with all proper upper marginals fixed at zero."""
    full = (1 << q) - 1
    delta = {full: c}
    for size in range(q - 1, -1, -1):
        for support in (m for m in range(1 << q) if m.bit_count() == size):
            strict_superset_sum = sum(
                value
                for other, value in delta.items()
                if other != support and other & support == support
            )
            delta[support] = -strict_superset_sum
    return delta


def verify_c() -> dict:
    rows = []
    for q in range(1, 9):
        delta = reconstruct_from_marginals(q, 1)
        full = (1 << q) - 1
        proper_zero = all(
            upper_marginal(delta, q, target) == 0
            for target in range(1 << q)
            if target != full
        )
        parity = all(
            value == (-1) ** (q - support.bit_count())
            for support, value in delta.items()
        )
        positive = sum(max(value, 0) for value in delta.values())
        negative = sum(max(-value, 0) for value in delta.values())
        rows.append(
            {
                "q": q,
                "cells": 1 << q,
                "proper_marginals_zero": proper_zero,
                "parity_formula": parity,
                "positive_mass": positive,
                "negative_mass": negative,
                "minimum_each_side": 1 << (q - 1),
            }
        )
    return {
        "rows": rows,
        "all_checks": all(
            row["proper_marginals_zero"]
            and row["parity_formula"]
            and row["positive_mass"] == row["minimum_each_side"]
            and row["negative_mass"] == row["minimum_each_side"]
            for row in rows
        ),
        "symbolic_statement": "delta(S)=(-1)^(q-|S|)c by Boolean-lattice Mobius inversion",
    }


# ---------------------------------------------------------------------------
# Paper D: cyclic positive authority calculus
# ---------------------------------------------------------------------------
def least_authority(n: int, seeds: set[int], rules, refuted: set[int]):
    authority = set(seeds) - refuted
    rounds = 0
    while True:
        rounds += 1
        before = len(authority)
        for antecedents, head in rules:
            if head not in refuted and set(antecedents) <= authority:
                authority.add(head)
        if len(authority) == before:
            return frozenset(authority), rounds


def verify_d() -> dict:
    unsupported_cycle = [((0,), 1), ((1,), 0)]
    seeded_cycle = unsupported_cycle
    controls = {
        "unsupported_cycle_empty": least_authority(2, set(), unsupported_cycle, set())[0] == frozenset(),
        "seeded_cycle_closes": least_authority(2, {0}, seeded_cycle, set())[0] == frozenset({0, 1}),
    }

    rng = random.Random(20260824)
    nodes = tuple(range(4))
    universe = []
    for head in nodes:
        others = [node for node in nodes if node != head]
        for size in (1, 2):
            for antecedents in itertools.combinations(others, size):
                universe.append((antecedents, head))

    monotonic_failures = 0
    excessive_rounds = 0
    for _ in range(5000):
        rules = rng.sample(universe, rng.randint(0, 8))
        seeds = set(rng.sample(nodes, rng.randint(0, 2)))
        r1 = set(rng.sample(nodes, rng.randint(0, 2)))
        r2 = r1 | set(rng.sample(nodes, rng.randint(0, 2)))
        a1, rounds1 = least_authority(4, seeds, rules, r1)
        a2, rounds2 = least_authority(4, seeds, rules, r2)
        monotonic_failures += int(not a2 <= a1)
        excessive_rounds += int(rounds1 > 5 or rounds2 > 5)

    return {
        "controls": controls,
        "random_systems": 5000,
        "refutation_monotonicity_failures": monotonic_failures,
        "finite_convergence_failures": excessive_rounds,
        "all_checks": all(controls.values()) and monotonic_failures == 0 and excessive_rounds == 0,
    }


# ---------------------------------------------------------------------------
# Non-quantum: bind only authority actually present on main
# ---------------------------------------------------------------------------
def verify_nonquantum() -> dict:
    m1 = json.loads((ROOT / "research/orion-rg/NONQUANTUM_M1_DK_TAIL_CORRIDOR_RESULTS_2026-08-24.json").read_text())
    m2 = json.loads((ROOT / "research/orion-rg/NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_RESULTS_2026-08-24.json").read_text())
    m3 = json.loads((ROOT / "research/orion-rg/NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json").read_text())
    frontier = json.loads((ROOT / "research/orion-rg/X1K_C0_SUPPORT_BOUND_RESULTS_V1.json").read_text())
    checks = {
        "corridor_terminal": m1["terminal"].startswith("NONQUANTUM_M1_C5CUBED_ALL_K_GE4"),
        "d4_open": m1["exact_d4_authority"] is False and m1["c0_31_authority"] is False,
        "saturation_parent": m2["terminal"].startswith("NONQUANTUM_M2_EXPONENT_P_SATURATION_DEFECT_LEMMA"),
        "support10_terminal": m3["terminal"].startswith("NONQUANTUM_M3_C5CUBED_SUPPORT10"),
        "frontier_23": frontier["bounded_conclusion"].endswith("support size at least 23."),
        "frontier_not_theorem": frontier["authority"]["theorem_authority"] is False,
        "external_replay_open": frontier["authority"]["external_replay_required"] is True,
    }
    return {"checks": checks, "all_checks": all(checks.values())}


def main() -> int:
    result = {
        "paper_a": verify_a(),
        "paper_b": verify_b(),
        "paper_c": verify_c(),
        "paper_d": verify_d(),
        "nonquantum": verify_nonquantum(),
    }
    result["all_checks"] = (
        result["paper_a"]["all_checks"]
        and result["paper_b"]["rank_theorem_checks"]
        and result["paper_b"]["tight_control"]
        and result["paper_b"]["loose_control"]
        and result["paper_c"]["all_checks"]
        and result["paper_d"]["all_checks"]
        and result["nonquantum"]["all_checks"]
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
