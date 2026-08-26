#!/usr/bin/env python3
"""Independent finite sanity checker for P11-P13 top-tier theory V1.

This checker does not prove the general mathematics mechanically.  It verifies the
registered finite witnesses, algebraic identities, counterexamples and boundary
conditions so later manuscript edits cannot silently contradict the theorem notes.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[2]


def rational_rank(rows: list[list[int]]) -> int:
    a = [[Fraction(x) for x in row] for row in rows]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        p = a[r][c]
        a[r] = [v / p for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == m:
            break
    return r


def p11_checks() -> dict:
    # T11.1 exact arbitrary finite query-family witness: three independent columns.
    f = [
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 0],
        [1, -1, 1],
    ]
    rank_f = rational_rank(f)
    assert rank_f == 3
    # Any exact Phi W factorization has rank <= d, so d=1,2 are excluded.
    excluded_exact_dimensions = [d for d in (1, 2) if d < rank_f]
    assert excluded_exact_dimensions == [1, 2]

    # T11.1 approximate low-rank witness using known singular-value squares.
    # spectrum sigma^2 = 25,9,1; epsilon^2=1.1 => rank epsilon exactly 2.
    singular_sq = [Fraction(25), Fraction(9), Fraction(1)]
    epsilon_sq = Fraction(11, 10)
    approx_rank = None
    for k in range(len(singular_sq) + 1):
        if sum(singular_sq[k:], Fraction(0)) <= epsilon_sq:
            approx_rank = k
            break
    assert approx_rank == 2
    assert sum(singular_sq[1:]) > epsilon_sq
    assert sum(singular_sq[2:]) <= epsilon_sq

    # T11.2 relative no-answer-laundering concrete parity witness.
    for k in (2, 3, 4):
        states = list(product((-1, 1), repeat=k))
        labels = [math.prod(z) for z in states]
        assert labels.count(1) == labels.count(-1)
        # No constant or single selected coordinate realizes parity for k>=2.
        constant_predictions = ([1] * len(states), [-1] * len(states))
        assert all(list(pred) != labels for pred in constant_predictions)
        for j in range(k):
            coordinate = [z[j] for z in states]
            assert coordinate != labels
            assert [-v for v in coordinate] != labels
        # Registered compositional decoder realizes it exactly.
        assert [math.prod(z) for z in states] == labels

    # T11.3 exact expected-unique/crossover law.
    p = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
    assert sum(p) == 1

    def unique_expectation(h: int) -> Fraction:
        return sum((1 - (1 - pi) ** h for pi in p), Fraction(0))

    c, rc, materialize, ru = map(Fraction, (4, 3, 10, 1))
    deltas = {}
    for h in range(1, 9):
        cache = c * unique_expectation(h) + h * rc
        universal = materialize + h * ru
        deltas[h] = cache - universal
    assert deltas[1] < 0
    first_universal_better = next(h for h in sorted(deltas) if deltas[h] > 0)
    assert first_universal_better >= 2

    # No-cache closed-form threshold sanity.
    denom = c + rc - ru
    threshold = materialize / denom
    assert denom > 0
    for h in range(1, 8):
        compile_cost = h * (c + rc)
        universal_cost = materialize + h * ru
        assert (universal_cost < compile_cost) == (Fraction(h) > threshold)

    return {
        "exact_query_rank": rank_f,
        "approximate_rank_epsilon": approx_rank,
        "parity_non_laundering_k": [2, 3, 4],
        "cache_universal_first_crossover_h": first_universal_better,
        "no_cache_threshold": str(threshold),
        "terminal": "P11_TOP_TIER_THEORY_V1_GREEN",
    }


def p12_checks() -> dict:
    # T12.1 strict value of adaptive resource location.
    signals = ("access", "reason")
    probs = {"access": Fraction(1, 2), "reason": Fraction(1, 2)}
    actions = ("state", "reason")
    values = {
        ("access", "state"): Fraction(1),
        ("access", "reason"): Fraction(0),
        ("reason", "state"): Fraction(0),
        ("reason", "reason"): Fraction(1),
    }
    adaptive = sum(probs[s] * max(values[(s, a)] for a in actions) for s in signals)
    fixed = max(sum(probs[s] * values[(s, a)] for s in signals) for a in actions)
    assert adaptive == 1 and fixed == Fraction(1, 2) and adaptive > fixed

    # T12.2 cross-difference witnesses.
    def cross(q: Callable[[int, int], int], c: int = 0, r: int = 0) -> int:
        return q(c + 1, r + 1) - q(c + 1, r) - q(c, r + 1) + q(c, r)

    assert cross(lambda c, r: c + r + c * r) > 0
    assert cross(lambda c, r: c + r - c * r) < 0
    assert cross(lambda c, r: c + r) == 0

    # Affine per-locus costs do not change the cross-difference.
    base = lambda c, r: c + r + c * r
    charged = lambda c, r: base(c, r) - 7 * c - 11 * r - 3
    assert cross(base) == cross(charged)

    # T12.3 exhaustive finite witness of the 2 epsilon regret bound.
    eps = Fraction(1)
    max_regret = Fraction(0)
    checked = 0
    for true_values in product(range(-2, 3), repeat=3):
        for errors in product((-1, 0, 1), repeat=3):
            hats = [Fraction(v) + Fraction(e) for v, e in zip(true_values, errors)]
            true = list(map(Fraction, true_values))
            a_star = max(range(3), key=lambda i: (true[i], -i))
            a_hat = max(range(3), key=lambda i: (hats[i], -i))
            regret = true[a_star] - true[a_hat]
            assert regret <= 2 * eps
            max_regret = max(max_regret, regret)
            checked += 1
    assert max_regret == 2 * eps

    return {
        "adaptive_value": str(adaptive),
        "best_fixed_value": str(fixed),
        "cross_difference_examples": {"complement": 1, "substitute": -1, "additive": 0},
        "regret_assignments_checked": checked,
        "max_regret": str(max_regret),
        "bound": str(2 * eps),
        "terminal": "P12_TOP_TIER_THEORY_V1_GREEN",
    }


def supports(rep: dict[str, str], gold: dict[str, object]) -> bool:
    xs = sorted(rep)
    for i, x in enumerate(xs):
        for y in xs[i + 1:]:
            if rep[x] == rep[y] and gold[x] != gold[y]:
                return False
    return True


def partition_refines(fine: dict[str, object], coarse: dict[str, object]) -> bool:
    xs = sorted(fine)
    for i, x in enumerate(xs):
        for y in xs[i + 1:]:
            if fine[x] == fine[y] and coarse[x] != coarse[y]:
                return False
    return True


def p13_checks() -> dict:
    xs = ("a", "b", "c", "d")
    compact = {"a": "u", "b": "u", "c": "v", "d": "v"}
    identity = {x: x for x in xs}
    r1 = {"a": 0, "b": 0, "c": 1, "d": 1}
    r2 = {"a": 0, "b": 1, "c": 2, "d": 3}
    incomparable = {"a": 0, "b": 1, "c": 1, "d": 0}

    # T13.1 exact support and responsibility implication.
    assert supports(compact, r1)
    assert not supports(compact, r2)
    assert supports(identity, r2)
    assert partition_refines(r2, r1)  # r2 >= r1
    assert supports(identity, r1)
    assert not partition_refines(r1, r2)
    assert not partition_refines(r1, incomparable)
    assert not partition_refines(incomparable, r1)

    # T13.2 transport: merge identity states according to compact map.
    transported = compact
    assert supports(transported, r1)
    assert not supports(transported, r2)

    # Responsibility upgrade is not automatic.
    assert supports(compact, r1) and not supports(compact, r2)

    # T13.3 Hoeffding calibration examples with prospectively chosen alpha/delta.
    alpha = 0.05
    delta = 0.05

    def upper(errors: int, n: int) -> float:
        p_hat = errors / n
        return min(1.0, p_hat + math.sqrt(math.log(1 / alpha) / (2 * n)))

    high_n = upper(5, 1000)
    low_n = upper(5, 100)
    assert high_n <= delta
    assert low_n > delta

    # Zero observed failures still needs enough samples; no zero-risk self-certification.
    zero_small = upper(0, 20)
    assert zero_small > delta

    return {
        "compact_supports_r1": True,
        "compact_supports_stricter_r2": False,
        "transport_preserves_r1": True,
        "transport_revokes_r2": True,
        "hoeffding": {
            "alpha": alpha,
            "delta": delta,
            "5_of_1000_upper": high_n,
            "5_of_100_upper": low_n,
            "0_of_20_upper": zero_small,
        },
        "terminal": "P13_TOP_TIER_THEORY_V1_GREEN",
    }


def assert_manuscript_markers() -> None:
    required = {
        "papers/orion-21-state-as-computation/TOP_TIER_THEORY_V1.md": ["T11.1", "T11.2", "T11.3"],
        "papers/orion-22-adaptive-state-reasoning/TOP_TIER_THEORY_V1.md": ["T12.1", "T12.2", "T12.3"],
        "papers/orion-23-responsibility-carrying-state/TOP_TIER_THEORY_V1.md": ["T13.1", "T13.2", "T13.3"],
        "papers/candidates/RESOURCE_LOCATION_SEMANTICS_V1.md": ["Resource vector", "P11 ownership", "P12 ownership", "P13 ownership"],
    }
    for path, markers in required.items():
        text = (ROOT / path).read_text()
        for marker in markers:
            assert marker in text, (path, marker)


def main() -> int:
    assert_manuscript_markers()
    payload = {
        "P11": p11_checks(),
        "P12": p12_checks(),
        "P13": p13_checks(),
        "programme_terminal": "P11_P13_TOP_TIER_THEORY_V1_GREEN",
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
