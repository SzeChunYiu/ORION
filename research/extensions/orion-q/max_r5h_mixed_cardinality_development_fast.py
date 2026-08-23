#!/usr/bin/env python3
"""Semantics-preserving accelerator for MAX-R5H.

The frozen scientific protocol/search space lives in
max_r5h_mixed_cardinality_development.py. This wrapper changes only Pareto
bookkeeping: reference_total_T is monotone in (internal T, block count), both of
which are already explicit dominance coordinates, so it need not be recomputed
inside pairwise dominance tests.
"""
from __future__ import annotations

import max_r5h_mixed_cardinality_development as b


def _discrete_collapse(states):
    d = {}
    for s in states:
        k = (s.cnot, s.t, s.blocks, s.ancilla)
        old = d.get(k)
        if old is None or (s.lam, s.partition) < (old.lam, old.partition):
            d[k] = s
    return d


def fast_prune(states):
    rows = sorted(_discrete_collapse(states).values(), key=b.state_key)
    keep = []
    # Rows are sorted first by lambda, then by every discrete resource coordinate
    # in a dominance-compatible order. A state can therefore only be dominated by
    # an already-seen state; future equal-lambda rows cannot dominate an earlier
    # row because CNOT is the next ascending key.
    for s in rows:
        dominated = False
        for o in keep:
            if (
                o.lam <= s.lam + 1e-13
                and o.cnot <= s.cnot
                and o.t <= s.t
                and o.blocks <= s.blocks
                and o.ancilla <= s.ancilla
                and (
                    o.lam < s.lam - 1e-13
                    or o.cnot < s.cnot
                    or o.t < s.t
                    or o.blocks < s.blocks
                    or o.ancilla < s.ancilla
                )
            ):
                # R5H reference_total_T = internal_T + f(blocks), with f monotone
                # nondecreasing, so the two explicit inequalities above imply the
                # omitted reference-total-T inequality exactly.
                dominated = True
                break
        if not dominated:
            keep.append(s)
    return tuple(keep)


def fast_combine_frontiers(a, c):
    # Collapse identical discrete coordinates while streaming the Cartesian
    # product, avoiding the very large transient list built by the reference code.
    d = {}
    for x in a:
        for y in c:
            s = b.State(
                x.lam + y.lam,
                x.cnot + y.cnot,
                x.t + y.t,
                x.blocks + y.blocks,
                max(x.ancilla, y.ancilla),
                x.partition + y.partition,
            )
            k = (s.cnot, s.t, s.blocks, s.ancilla)
            old = d.get(k)
            if old is None or (s.lam, s.partition) < (old.lam, old.partition):
                d[k] = s
    return fast_prune(d.values())


def main():
    b.prune = fast_prune
    b.combine_frontiers = fast_combine_frontiers
    return b.main()


if __name__ == "__main__":
    main()
