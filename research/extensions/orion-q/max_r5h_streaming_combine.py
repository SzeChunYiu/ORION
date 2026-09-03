#!/usr/bin/env python3
"""Memory-bounded, EXACTLY-EQUAL replacement for fast_combine_frontiers.

Why this exists (2026-09-03, LUNARC jobs 3572244/3572255): the N2 chunked
fold was oom-killed at donor window 31 / mixed window 30 with frontier
~53.7k against the ~5.3G default lu48 cgroup. fast_combine_frontiers
streams the full |a| x |c| Cartesian product into ONE dict keyed by
discrete coordinates before any pruning happens, so peak live memory is
proportional to the product's distinct-key count -- unbounded while the
fold's frontier keeps growing toward the engine's own 200000
pareto_saturation guard. Chunking windows cannot fix a single-window
combine that exceeds memory; only bounding the combine itself can.

Exactness (output tuple IDENTICAL to fast_combine_frontiers, including
order). Write P = products(a, c) = {x + y : x in a, y in c} -- NOTE c is
a set of ALTERNATIVES (the window's local Pareto frontier of choices);
each product pairs an accumulated state with exactly ONE window choice.
The reference is

    reference(a, c) = fast_prune(collapse(P))

where collapse keeps the min (lam, partition) per discrete key
(cnot, t, blocks, ancilla) and fast_prune drops dominated states in
state_key order. (An earlier draft of this module folded slice results
CUMULATIVELY -- F_i = prune(products(F_{i-1}, c_i)) -- which computes
sums over SEVERAL window choices and is a different (wrong) function;
the randomized equality selftest caught it immediately. The left operand
must always be the original a.)

The bounded form streams the products into a running collapsed dict D
and periodically REPLACES D by fast_prune(D)'s representatives:

    D = {}; for each slice c_i: for y in c_i, x in a: D[key(x+y)] =min-> x+y
          whenever |D| exceeds the row budget: D = collapse(fast_prune(D))
    return fast_prune(D)

Two facts make this exactly the reference:

1. collapse composes over unions: the min (lam, partition) per key over
   P equals the fold of per-slice minima, so streaming all slices into D
   (with no intermediate prune) reproduces collapse(P) exactly.

2. An intermediate prune only drops dominated states, and dropping
   dominated states never changes a later prune: dominance is
   coordinatewise with transitivity (o <= s, s <= s' implies o <= s',
   strictness preserved through the same coordinate), so anything a
   dropped state would have dominated is dominated by a surviving
   dominator instead. Re-collapsing the pruned representatives into D is
   likewise exact: fast_prune output never contains two states of the
   same discrete key with lam difference > 1e-13, and same-key states
   within tolerance collapse to the same representative the reference
   collapse would keep (min (lam, partition)).

fast_prune's output order is a deterministic function of its input set
(sort by state_key; each key appears once), so the final tuple equals
the reference element-for-element.

Slice sizing keeps the live dict at ORIONQ_R5H_STREAM_ROWS collapsed rows
(default 2,000,000: ~2M retained State+partition objects is single-digit
GB, well inside a --mem=100G class allocation; slice_len = budget/|a| is
stable because the left operand stays the original a).

Usage (chunked runner):
    import max_r5h_streaming_combine as stream
    stream.install()          # patches b.combine_frontiers exactly once
"""
from __future__ import annotations

import os

import max_r5h_mixed_cardinality_development as b
import max_r5h_mixed_cardinality_development_fast as accel

STREAM_ROWS_DEFAULT = 2_000_000  # justified in module docstring


def streaming_combine_frontiers(a, c, max_live_rows: int | None = None):
    """Exactly-equal, memory-bounded fast_combine_frontiers(a, c)."""
    if max_live_rows is None:
        max_live_rows = int(os.environ.get("ORIONQ_R5H_STREAM_ROWS", STREAM_ROWS_DEFAULT))
    if not a or not c:
        # Mirror the reference exactly: an empty operand yields an empty
        # product stream, and fast_prune(()) == (). (Never hit by the fold,
        # which starts from the identity State and non-empty window locals.)
        return accel.fast_prune(())
    a = tuple(a)
    d: dict = {}
    i = 0
    while i < len(c):
        # Left operand is ALWAYS the original a (c holds alternatives, so
        # cumulative folding would sum several window choices -- wrong
        # function). slice_len is stable because |a| is fixed.
        slice_len = max(1, min(len(c) - i, max_live_rows // len(a)))
        for y in c[i:i + slice_len]:
            for x in a:
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
        i += slice_len
        if len(d) > max_live_rows:
            kept = accel.fast_prune(d.values())
            d = {(s.cnot, s.t, s.blocks, s.ancilla): s for s in kept}
    return accel.fast_prune(d.values())


def install() -> None:
    """Patch the engine's combine to the streaming form (idempotent)."""
    b.combine_frontiers = streaming_combine_frontiers
