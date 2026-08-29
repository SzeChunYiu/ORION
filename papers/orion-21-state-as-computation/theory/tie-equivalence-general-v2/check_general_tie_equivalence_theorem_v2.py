#!/usr/bin/env python3
"""Independent regression for ORION21.TIE_EQUIVALENCE_GENERAL.v2."""

from __future__ import annotations

import itertools
import json


def sign(x: int) -> int:
    return (x > 0) - (x < 0)


def admissible_supports(c: tuple[int, ...], r: int):
    """Subset-predicate route; intentionally not fixed/tied construction."""
    p = len(c)
    out = []
    for s in itertools.combinations(range(p), r):
        chosen = set(s)
        selected = [abs(c[i]) for i in chosen]
        unselected = [abs(c[j]) for j in range(p) if j not in chosen]
        min_in = min(selected)
        max_out = max(unselected) if unselected else -1
        if min_in >= max_out:
            out.append(s)
    return out


def boundary(c: tuple[int, ...], r: int) -> int:
    return sorted((abs(x) for x in c), reverse=True)[r - 1]


def signature(c: tuple[int, ...], support: tuple[int, ...]):
    rows = itertools.product((-1, 1), repeat=len(c))
    return tuple(
        int(sum(row[i] * sign(c[i]) for i in support) > 0)
        for row in rows
    )


def exhaustive_small_scope():
    checked_classes = 0
    non_singleton = 0
    benign = 0
    binding = 0

    for p in range(2, 7):
        for c in itertools.product((-1, 0, 1), repeat=p):
            for r in range(1, p + 1):
                supports = admissible_supports(c, r)
                assert supports
                checked_classes += 1
                if len(supports) == 1:
                    continue

                non_singleton += 1
                sigs = {signature(c, s) for s in supports}
                is_benign = len(sigs) == 1
                predicted_benign = boundary(c, r) == 0
                assert is_benign == predicted_benign, {
                    "p": p,
                    "c": c,
                    "r": r,
                    "boundary": boundary(c, r),
                    "supports": supports,
                    "signatures": len(sigs),
                }
                if is_benign:
                    benign += 1
                else:
                    binding += 1

    return {
        "classes_checked": checked_classes,
        "non_singleton": non_singleton,
        "benign_boundary_zero": benign,
        "binding_boundary_positive": binding,
    }


def general_witness_regression():
    rows = []
    for p in range(2, 13):
        c = (1, 1) + (0,) * (p - 2)
        supports = admissible_supports(c, 1)
        assert (0,) in supports and (1,) in supports
        assert signature(c, (0,)) != signature(c, (1,))
        rows.append({"p": p, "class_size": len(supports), "boundary": 1})
    return rows


def main() -> int:
    out = {
        "status": "PASS",
        "small_scope": exhaustive_small_scope(),
        "general_witness_regression": general_witness_regression(),
        "theorem_scope": (
            "proof is arbitrary p/integer c/1<=r<=p with complete sign-row bank; "
            "checker is finite regression only"
        ),
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
