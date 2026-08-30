#!/usr/bin/env python3
"""Independent checker for ORION07.AGREEMENT_NONIDENTIFIABILITY.v1.

INDEPENDENCE CONTRACT
---------------------
This checker deliberately imports NONE of the generating proof logic. It never
uses Lemma 1, Theorem 1, Theorem 3, or any algebraic rearrangement from
THEORY.md. Every quantity is recomputed from its DEFINITION by counting cells of
{0,1}^3, and the claimed region is then tested against the achievable set that
those counts actually produce.

Concretely the only thing taken from THEORY.md is the STATEMENT under test:

    R(a) = { (u,v) in [0,1]^2 : |u-v| <= 1-a  and  1-a <= u+v <= 1+a }

Two independent routes are run.

Route A -- exhaustive finite-sample enumeration.
    For n = 1..N_MAX, enumerate every multiset of n units over the 8 cells of
    {0,1}^3, compute (a_hat, pX_hat, pY_hat) by direct counting, and assert the
    resulting point lies in R(a_hat). This is soundness on every realizable
    finite sample up to N_MAX. It also records which points are achieved, which
    supplies sharpness witnesses.

Route B -- exact vertex enumeration of the population polytope.
    For each rational a on a grid, the set of laws on {0,1}^3 with P(X=Y)=a is a
    polytope with two equality constraints, so its vertices have support <= 2.
    Enumerate them exactly, push them through the linear map p -> (pX, pY), and
    check (i) every image lies in R(a) -- soundness -- and (ii) every vertex of
    R(a) lies in the convex hull of the images -- completeness/sharpness.

All arithmetic is exact (fractions.Fraction). No floating point anywhere.

Exit codes
    0  all checks passed
    2  a check FAILED  (the theorem statement is wrong)
    3  the checker could not run  (CANNOT_CHECK -- never conflated with pass)
"""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

# ---------------------------------------------------------------------------
# Cells of {0,1}^3, in the order (x, y, t).
# ---------------------------------------------------------------------------
CELLS = [(x, y, t) for x in (0, 1) for y in (0, 1) for t in (0, 1)]
assert len(CELLS) == 8

N_MAX = 7          # Route A: exhaustive over all multisets of size <= 7
GRID_DEN = 12      # Route B: a ranges over k/12 for k = 0..12


# ---------------------------------------------------------------------------
# Definitions. These are the ONLY place the observables are computed, and each
# is a literal transcription of the definition in THEORY.md section 2.
# ---------------------------------------------------------------------------
def observables(mass):
    """(a, pX, pY) from a mass vector over CELLS, by direct counting."""
    total = sum(mass)
    if total == 0:
        raise ZeroDivisionError("empty sample")
    a = sum(m for m, (x, y, _) in zip(mass, CELLS) if x == y) / total
    p_x = sum(m for m, (x, _, t) in zip(mass, CELLS) if x == t) / total
    p_y = sum(m for m, (_, y, t) in zip(mass, CELLS) if y == t) / total
    return a, p_x, p_y


def in_region(a, u, v):
    """Membership test for the CLAIMED region R(a). Statement under test."""
    return (
        Fraction(0) <= u <= Fraction(1)
        and Fraction(0) <= v <= Fraction(1)
        and abs(u - v) <= 1 - a
        and 1 - a <= u + v <= 1 + a
    )


def region_vertices(a):
    """Claimed vertices of R(a). Statement under test."""
    return [
        (1 - a, Fraction(0)),
        (Fraction(1), a),
        (a, Fraction(1)),
        (Fraction(0), 1 - a),
    ]


# ---------------------------------------------------------------------------
# Exact 2-D convex geometry (used only by Route B).
# ---------------------------------------------------------------------------
def _cross(o, p, q):
    return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])


def in_hull(pt, pts):
    """Exact: is pt in conv(pts)?  2-D Caratheodory -- in some triangle/segment."""
    pts = sorted(set(pts))
    if pt in pts:
        return True
    for a1, b1 in itertools.combinations(pts, 2):          # on a segment?
        if _cross(a1, b1, pt) == 0:
            if (
                min(a1[0], b1[0]) <= pt[0] <= max(a1[0], b1[0])
                and min(a1[1], b1[1]) <= pt[1] <= max(a1[1], b1[1])
            ):
                return True
    for a1, b1, c1 in itertools.combinations(pts, 3):      # inside a triangle?
        d1, d2, d3 = _cross(a1, b1, pt), _cross(b1, c1, pt), _cross(c1, a1, pt)
        if (d1 >= 0 and d2 >= 0 and d3 >= 0) or (d1 <= 0 and d2 <= 0 and d3 <= 0):
            return True
    return False


# ---------------------------------------------------------------------------
# Route A
# ---------------------------------------------------------------------------
def route_a(n_max=N_MAX):
    checked = 0
    achieved = {}
    for n in range(1, n_max + 1):
        for cut in itertools.combinations(range(n + 7), 7):
            counts, prev = [], -1
            for c in cut:
                counts.append(c - prev - 1)
                prev = c
            counts.append(n + 7 - prev - 1)
            a, p_x, p_y = observables([Fraction(c) for c in counts])
            if not in_region(a, p_x, p_y):
                return False, {
                    "route": "A",
                    "n": n,
                    "counts": counts,
                    "a": str(a),
                    "pX": str(p_x),
                    "pY": str(p_y),
                }, checked, achieved
            achieved.setdefault(a, set()).add((p_x, p_y))
            checked += 1
    return True, None, checked, achieved


# ---------------------------------------------------------------------------
# Route B
# ---------------------------------------------------------------------------
def polytope_vertices(a):
    """Exact vertices of {p >= 0 : sum p = 1, sum_{x=y} p = a}: support <= 2."""
    g = [Fraction(1) if x == y else Fraction(0) for (x, y, _) in CELLS]
    verts = set()
    for i in range(8):                                    # support 1
        if g[i] == a:
            m = [Fraction(0)] * 8
            m[i] = Fraction(1)
            verts.add(tuple(m))
    for i, j in itertools.combinations(range(8), 2):      # support 2
        if g[i] == g[j]:
            continue
        pi = (a - g[j]) / (g[i] - g[j])
        pj = Fraction(1) - pi
        if Fraction(0) <= pi <= 1 and Fraction(0) <= pj <= 1:
            m = [Fraction(0)] * 8
            m[i], m[j] = pi, pj
            verts.add(tuple(m))
    return verts


def route_b(den=GRID_DEN):
    results = []
    for k in range(den + 1):
        a = Fraction(k, den)
        images = set()
        for m in polytope_vertices(a):
            aa, p_x, p_y = observables(list(m))
            if aa != a:
                return False, {"route": "B", "a": str(a), "why": "agreement mismatch"}, results
            if not in_region(a, p_x, p_y):
                return False, {
                    "route": "B", "a": str(a), "pX": str(p_x), "pY": str(p_y),
                    "why": "achievable point outside claimed region",
                }, results
            images.add((p_x, p_y))
        for vtx in region_vertices(a):
            if not in_hull(vtx, images):
                return False, {
                    "route": "B", "a": str(a), "vertex": [str(vtx[0]), str(vtx[1])],
                    "why": "claimed vertex not achievable",
                }, results
        results.append({"a": str(a), "polytope_image_points": len(images)})
    return True, None, results


# ---------------------------------------------------------------------------
# Corollary spot-checks, recomputed from Route A's achieved set.
# ---------------------------------------------------------------------------
def corollaries(achieved):
    out = {}
    one, zero = Fraction(1), Fraction(0)

    qs = sorted({(u + v) / 2 for (u, v) in achieved.get(one, set())})
    out["c2_1_perfect_agreement_vacuous"] = {
        "min_q": str(qs[0]) if qs else None,
        "max_q": str(qs[-1]) if qs else None,
        "pass": bool(qs) and qs[0] == zero and qs[-1] == one,
    }

    qs0 = {(u + v) / 2 for (u, v) in achieved.get(zero, set())}
    out["c2_2_perfect_disagreement_pins_half"] = {
        "observed_q_values": sorted(str(q) for q in qs0),
        "pass": qs0 == {Fraction(1, 2)},
    }

    widths = {}
    for a, pts in achieved.items():
        qs_a = [(u + v) / 2 for (u, v) in pts]
        widths[a] = max(qs_a) - min(qs_a)
    out["c2_3_interval_width_at_most_a"] = {
        "pass": all(w <= a for a, w in widths.items()),
        "note": "achieved width <= a for every achieved agreement level",
    }

    out["c3_1_spread_bound"] = {
        "pass": all(abs(u - v) <= 1 - a for a, pts in achieved.items() for (u, v) in pts)
    }
    return out


def main():
    try:
        ok_a, fail_a, checked_a, achieved = route_a()
        ok_b, fail_b, grid = route_b()
        cors = corollaries(achieved)
    except Exception as exc:                                  # noqa: BLE001
        json.dump(
            {"status": "CANNOT_CHECK", "error": f"{type(exc).__name__}: {exc}"},
            sys.stdout, indent=2,
        )
        print()
        return 3

    cor_ok = all(v.get("pass") for v in cors.values())
    passed = ok_a and ok_b and cor_ok

    report = {
        "schema": "ORION.ORION07.AgreementNonidentifiability.CheckerReport.v1",
        "successor_id": "ORION07.AGREEMENT_NONIDENTIFIABILITY.v1",
        "independence": "no proof logic imported; observables recomputed from definitions",
        "arithmetic": "exact (fractions.Fraction); no floating point",
        "route_a_exhaustive_finite_samples": {
            "n_max": N_MAX,
            "samples_checked": checked_a,
            "distinct_agreement_levels": len(achieved),
            "pass": ok_a,
            "counterexample": fail_a,
        },
        "route_b_exact_polytope_vertices": {
            "agreement_grid_denominator": GRID_DEN,
            "grid_points": len(grid),
            "pass": ok_b,
            "counterexample": fail_b,
            "detail": grid,
        },
        "corollaries": cors,
        "status": "PASS" if passed else "FAIL",
    }
    out = Path(__file__).resolve().parent.parent / "RESULT.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    json.dump({k: report[k] for k in ("status", "route_a_exhaustive_finite_samples",
                                      "route_b_exact_polytope_vertices")},
              sys.stdout, indent=2)
    print()
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
