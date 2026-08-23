#!/usr/bin/env python3
"""Exact confirmatory checker for the Freeze--Schmid C_5^3, k=2 lower witness.

Committed after exploratory discovery of insertion saturation.  This is replay
code, not a prospective discovery instrument.
"""
from __future__ import annotations

import json
from itertools import product

P = 5


def zero_subcounts(vectors, counts):
    out = []
    for sub in product(*(range(c + 1) for c in counts)):
        if not any(sub):
            continue
        total = [0, 0, 0]
        for n, v in zip(sub, vectors):
            for j in range(3):
                total[j] = (total[j] + n * v[j]) % P
        if total == [0, 0, 0]:
            out.append(tuple(sub))
    return tuple(out)


def has_two(vectors, counts):
    zeros = zero_subcounts(vectors, counts)
    for a in zeros:
        rem = tuple(c - x for c, x in zip(counts, a))
        for b in zeros:
            if all(x <= r for x, r in zip(b, rem)):
                return True
    return False


def main() -> None:
    e1 = (1, 0, 0)
    e2 = (0, 1, 0)
    e3 = (0, 0, 1)
    g1 = (1, 1, 0)
    g2 = (1, 0, 1)
    g3 = (0, 1, 1)
    vectors = (e1, e2, e3, g1, g2, g3)

    # Freeze--Schmid Theorem 4.1 with p=5, r=s=3, t=1, k=2:
    # T=(g1 g2 g3)^2 g3 and S=T*e1^4*e2^4*e3^4.
    counts = (4, 4, 4, 2, 2, 3)
    assert sum(counts) == 19
    assert not has_two(vectors, counts)

    failures = []
    for x in product(range(P), repeat=3):
        if x in vectors:
            i = vectors.index(x)
            ext = list(counts)
            ext[i] += 1
            ok = has_two(vectors, tuple(ext))
        else:
            ok = has_two(vectors + (x,), counts + (1,))
        if not ok:
            failures.append(x)

    result = {
        "schema": "ORION.RG.X1F.FreezeSchmidK2InsertionSaturation.v1",
        "group": "C_5^3",
        "k": 2,
        "base_length": 19,
        "base_has_two_disjoint_zero_sums": False,
        "extensions_checked": 125,
        "extension_failures": [list(x) for x in failures],
        "all_one_term_extensions_have_two_disjoint_zero_sums": not failures,
        "claim_ceiling": "BOUNDED_EXACT_CONFIRMATORY_ONLY",
        "exact_D2_authority": False,
        "novelty_authority": False,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
