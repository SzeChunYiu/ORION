#!/usr/bin/env python3
"""Broad calibration sweep: engine_a's method against published closed forms.

The four-control suite establishes that the independent route is not obviously
broken. It does not establish that it is right across a range. This sweep computes
D_k exhaustively for every small group where exhaustive computation is feasible and
compares against the closed forms

    D_k(C_n)          = k*n
    D_k(C_m (+) C_n)  = m + k*n - 1        for m | n

which come from outside every implementation under test. That is the whole point:
a search implementation validated only against its own fixtures is validated against
nothing, and a sole researcher has no reviewer to supply the outside view. The
published formulas are the outside view.

Definition used, stated so the computation is checkable: D_k(G) is the least l such
that EVERY sequence of length >= l over G contains k disjoint nonempty zero-sum
subsequences. So D_k = L+1 exactly when some length-L sequence has fewer than k,
and every length-(L+1) sequence has at least k.

Exhaustive over multisets, since the property is invariant under reordering.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

SCHEMA = "ORION04.CalibrationSweep.ClosedForms.v1"


def add(a, b, orders):
    return tuple((x + y) % o for x, y, o in zip(a, b, orders))


def max_disjoint_zero_sums(seq, orders) -> int:
    n = len(seq)
    z = tuple(0 for _ in orders)
    reach = {z: {0}}
    for i in range(n):
        nxt = {k: set(v) for k, v in reach.items()}
        for s, masks in reach.items():
            s2 = add(s, seq[i], orders)
            bit = 1 << i
            nxt.setdefault(s2, set()).update(m | bit for m in masks)
        reach = nxt
    masks = sorted(m for m in reach.get(z, set()) if m)
    best = 0

    def pack(used, count, start):
        nonlocal best
        if count > best:
            best = count
        for j in range(start, len(masks)):
            m = masks[j]
            if m & used:
                continue
            pack(used | m, count + 1, j + 1)

    pack(0, 0, 0)
    return best


def every_sequence_has_k(length: int, orders, k: int) -> bool:
    """True iff EVERY length-`length` multiset over the group has >= k disjoint zero sums."""
    elems = [tuple(e) for e in itertools.product(*(range(o) for o in orders))]
    for combo in itertools.combinations_with_replacement(elems, length):
        if max_disjoint_zero_sums(list(combo), orders) < k:
            return False
    return True


def compute_d_k(orders, k: int, ceiling: int) -> int | None:
    """Least l such that every length-l sequence has k disjoint zero sums."""
    for l in range(1, ceiling + 1):
        if every_sequence_has_k(l, orders, k):
            return l
    return None


def closed_form(orders, k: int) -> int | None:
    if len(orders) == 1:
        return k * orders[0]
    if len(orders) == 2:
        m, n = sorted(orders)
        return m + k * n - 1 if n % m == 0 else None
    return None


CASES = [
    ((2,), 1), ((2,), 2), ((2,), 3),
    ((3,), 1), ((3,), 2),
    ((4,), 1), ((4,), 2),
    ((5,), 1), ((5,), 2),
    ((6,), 1),
    ((7,), 1),
    ((2, 2), 1),
    ((2, 4), 1),
    ((3, 3), 1),
]


def main() -> int:
    rows = []
    for orders, k in CASES:
        expected = closed_form(orders, k)
        if expected is None:
            rows.append({"group": str(orders), "k": k, "status": "NO_CLOSED_FORM"})
            continue
        t0 = time.monotonic()
        got = compute_d_k(orders, k, ceiling=expected + 2)
        ms = int((time.monotonic() - t0) * 1000)
        rows.append({
            "group": "C_" + " (+) C_".join(str(o) for o in orders),
            "orders": list(orders), "k": k,
            "closed_form": expected, "computed": got,
            "agrees": got == expected, "wall_milliseconds": ms,
        })
        print(json.dumps(rows[-1], sort_keys=True), flush=True)
    checked = [r for r in rows if "agrees" in r]
    out = {
        "schema": SCHEMA,
        "ground_truth": "published closed forms D_k(C_n)=k n and D_k(C_m (+) C_n)=m+k n-1",
        "external_to_every_implementation_under_test": True,
        "cases_checked": len(checked),
        "cases_agreeing": sum(1 for r in checked if r["agrees"]),
        "all_agree": all(r["agrees"] for r in checked),
        "disagreements": [r for r in checked if not r["agrees"]],
        "rows": rows,
        "scientific_authority_delta": "NONE",
        "d4_outcome_accessed": False,
    }
    Path(__file__).with_name("CALIBRATION_SWEEP_V1.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("cases_checked", "cases_agreeing", "all_agree", "disagreements")},
                     indent=2, sort_keys=True))
    return 0 if out["all_agree"] else 1


if __name__ == "__main__":
    sys.exit(main())
