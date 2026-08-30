#!/usr/bin/env python3
"""Finite exact regression for ORION24.STRATUM_TRANSPORT_PARTIAL_IDENTIFICATION.v1."""
from __future__ import annotations

import itertools
from fractions import Fraction

GRID = (Fraction(-1), Fraction(0), Fraction(1))


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def main():
    systems = 0
    completions = 0
    sign_checks = 0

    # Exact rational weights on denominator 4; all bounded {-1,0,1} effects.
    for n in range(2, 5):
        for counts in compositions(4, n):
            weights = tuple(Fraction(c, 4) for c in counts)
            if sum(weights) != 1:
                raise AssertionError
            for observed_mask in range(1, (1 << n) - 1):
                observed = tuple(i for i in range(n) if (observed_mask >> i) & 1)
                unobserved = tuple(i for i in range(n) if i not in observed)
                for observed_effects in itertools.product(GRID, repeat=len(observed)):
                    effect_map = dict(zip(observed, observed_effects))
                    A = sum(weights[i] * effect_map[i] for i in observed)
                    W = sum(weights[i] for i in unobserved)
                    lower, upper = A - W, A + W

                    realised = []
                    for missing_effects in itertools.product(GRID, repeat=len(unobserved)):
                        all_effects = dict(effect_map)
                        all_effects.update(zip(unobserved, missing_effects))
                        delta = sum(weights[i] * all_effects[i] for i in range(n))
                        assert lower <= delta <= upper
                        realised.append(delta)
                        completions += 1

                    # Sharp endpoints are realised by all -1 / all +1 missing effects.
                    assert min(realised) == lower
                    assert max(realised) == upper

                    # Strict sign guarantee is equivalent to excluding zero and
                    # the opposite sign from the sharp interval.
                    guaranteed_positive = all(delta > 0 for delta in realised)
                    guaranteed_negative = all(delta < 0 for delta in realised)
                    assert guaranteed_positive == (lower > 0)
                    assert guaranteed_negative == (upper < 0)
                    sign_checks += 2
                    systems += 1

    # Single-stratum algebra control: d=1 requires p>1/2 for strict positivity.
    for p_num in range(5):
        p = Fraction(p_num, 4)
        d = Fraction(1)
        lower = p * d - (1 - p)
        assert (lower > 0) == (p > Fraction(1, 2))

    print(
        "ORION24_STRATUM_TRANSPORT_BOUNDS_V1_PASS "
        f"partial_systems={systems} bounded_completions={completions} "
        f"sign_checks={sign_checks} sharp_endpoints=PASS"
    )


if __name__ == "__main__":
    main()
