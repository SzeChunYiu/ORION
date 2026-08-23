#!/usr/bin/env python3
"""Exact dominance accelerator for max_r6_donor_closure_h4.

The frozen donor-closure packet explicitly permits target-specific exact
feasibility. This wrapper changes only Pareto bookkeeping, using a 2D Fenwick
minimum over (T, block-count) while rows are processed in ascending CNOT.
Hyper/nonhyper states are pruned independently because hyperblock usage is a
formal discriminator coordinate.
"""
from __future__ import annotations

import math

import max_r6_donor_closure_h4 as c


def fast_prune(states):
    collapsed = {}
    for s in states:
        if not c.within_target(s):
            continue
        key = (s.cnot, s.t, s.blocks, s.ancilla, s.uses_hyper)
        old = collapsed.get(key)
        if old is None or (s.lam, s.partition) < (old.lam, old.partition):
            collapsed[key] = s

    result = []
    # All frozen block T costs are multiples of 96. The target is 5568 = 58*96.
    max_t_index = c.TARGET["T"] // 96 + 2
    max_b_index = c.TARGET["blocks"] + 2
    inf = math.inf

    for flag in (False, True):
        rows = [s for s in collapsed.values() if s.uses_hyper is flag]
        rows.sort(key=lambda s: (s.cnot, s.t, s.blocks, s.lam, s.partition))
        bit = [[inf] * (max_b_index + 1) for _ in range(max_t_index + 1)]

        def t_index(t):
            if t % 96:
                raise AssertionError({"non_multiple_of_96_T": t})
            return t // 96 + 1

        def query(ti, bi):
            value = inf
            i = ti
            while i > 0:
                j = bi
                while j > 0:
                    value = min(value, bit[i][j])
                    j -= j & -j
                i -= i & -i
            return value

        def update(ti, bi, value):
            i = ti
            while i <= max_t_index:
                j = bi
                while j <= max_b_index:
                    if value < bit[i][j]:
                        bit[i][j] = value
                    j += j & -j
                i += i & -i

        for s in rows:
            ti = t_index(s.t)
            bi = s.blocks + 1
            # Rows are ascending in CNOT. If a prior state also has T<=, blocks<=
            # and lambda<=, it dominates this state. Exact-discrete duplicates
            # were already collapsed, so at least one coordinate is strict.
            if query(ti, bi) <= s.lam + 1e-13:
                continue
            result.append(s)
            update(ti, bi, s.lam)

    return tuple(
        sorted(
            result,
            key=lambda s: (
                s.uses_hyper,
                round(s.lam, 15),
                s.cnot,
                s.t,
                s.blocks,
                s.ancilla,
                s.partition,
            ),
        )
    )


def main():
    c.prune = fast_prune
    return c.main()


if __name__ == "__main__":
    main()
