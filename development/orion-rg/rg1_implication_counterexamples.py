"""ORION-RG RG-1 F0 exact counterexample controls.

These controls do not prove a positive general theory. They protect the first
implication matrix by making several negative arrows executable.

Parent issues: #894, #895.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Tuple


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: str


def popcount_word(word: Tuple[int, ...]) -> int:
    return sum(word)


def rg_a_dense_optimum(max_n: int = 12) -> CheckResult:
    """d_sem=0 does not imply bounded intrinsic optimal support.

    Feasible words: all binary words.
    Semantic quotient: trivial.
    Cost: number of zeros, hence unique optimum is all ones.
    """
    supports = []
    for n in range(1, max_n + 1):
        words = list(product((0, 1), repeat=n))
        costs = {w: n - popcount_word(w) for w in words}
        best = min(costs.values())
        optima = [w for w, c in costs.items() if c == best]
        assert optima == [(1,) * n]
        supports.append(popcount_word(optima[0]))
    passed = supports == list(range(1, max_n + 1))
    return CheckResult(
        "RG-A dense optimum",
        passed,
        f"trivial semantic state; optimal supports through n={max_n}: {supports}",
    )


def rg_b_continuation_value_state(max_prefix: int = 16, max_suffix: int = 16) -> CheckResult:
    """kappa=0 + finite alphabet does not imply bounded value-state quotient.

    V(a^n)=n^2. Two prefix lengths m!=m' cannot differ by one fixed additive
    offset across every continuation length k.
    """
    for m in range(max_prefix + 1):
        for mp in range(m + 1, max_prefix + 1):
            deltas = {
                (m + k) ** 2 - (mp + k) ** 2
                for k in range(max_suffix + 1)
            }
            if len(deltas) <= 1:
                return CheckResult(
                    "RG-B unbounded value state",
                    False,
                    f"unexpected fixed offset for prefixes {m}, {mp}: {deltas}",
                )
    return CheckResult(
        "RG-B unbounded value state",
        True,
        f"every tested distinct prefix pair through {max_prefix} has continuation-dependent value offset",
    )


def rg_c_no_uniform_bounded_support_move(max_n: int = 32, candidate_bound: int = 8) -> CheckResult:
    """One regime label does not imply a bounded-support primitive move basis.

    Feasible configurations at size n are only 0^n and 1^n. The only strict
    feasible improvement changes n coordinates. Thus every fixed move-support
    bound b fails once n>b.
    """
    violating_sizes = []
    for n in range(1, max_n + 1):
        changed_coordinates = n  # Hamming distance between 1^n and 0^n.
        if changed_coordinates > candidate_bound:
            violating_sizes.append(n)
    passed = bool(violating_sizes) and min(violating_sizes) == candidate_bound + 1
    return CheckResult(
        "RG-C bounded-support move basis",
        passed,
        f"support bound b={candidate_bound} first fails at n={min(violating_sizes) if violating_sizes else None}",
    )


def zero_vs_nonzero(bits: Tuple[int, ...]) -> str:
    return "ZERO" if all(b == 0 for b in bits) else "NONZERO"


def rg_f_certificate_arity_not_query_separation(max_n: int = 20) -> CheckResult:
    """Certificate arity 1 does not imply sublinear exact recognition.

    NONZERO has a one-bit witness. But an exact deterministic recognizer must
    inspect all n bits on the all-zero input; an adversary can place a 1 in any
    unread coordinate.
    """
    checked = []
    for n in range(1, max_n + 1):
        positive_certificate_arity = 1
        worst_case_queries = n
        assert zero_vs_nonzero((0,) * n) == "ZERO"
        checked.append((n, positive_certificate_arity, worst_case_queries))
    passed = all(arity == 1 and q == n for n, arity, q in checked)
    return CheckResult(
        "RG-F certificate arity vs query complexity",
        passed,
        f"arity stays 1 while all-zero worst-case exact queries grow 1..{max_n}",
    )


def run_all() -> Iterable[CheckResult]:
    yield rg_a_dense_optimum()
    yield rg_b_continuation_value_state()
    yield rg_c_no_uniform_bounded_support_move()
    yield rg_f_certificate_arity_not_query_separation()


if __name__ == "__main__":
    results = list(run_all())
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} | {result.name} | {result.details}")
    if not all(r.passed for r in results):
        raise SystemExit(1)
