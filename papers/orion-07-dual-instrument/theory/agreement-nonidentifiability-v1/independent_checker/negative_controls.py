#!/usr/bin/env python3
"""Negative controls for the ORION-07 agreement-non-identifiability checker.

A checker that cannot fail proves nothing. This harness perturbs the CLAIMED
statement in ways that make it false and asserts that the checker rejects each
perturbation, then asserts that the unperturbed statement is accepted.

It perturbs only the two functions that encode the claim under test
(`in_region`, `region_vertices`). The measurement machinery -- `observables`,
`polytope_vertices`, `in_hull` -- is left untouched, so a control that fires
demonstrates real discriminating power rather than a broken harness.

Exit codes
    0  every control behaved as required (checker discriminates)
    2  a control did NOT fire, or the true statement was rejected
    3  the harness could not run  (CANNOT_CHECK)
"""

from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location(
        "orion07_checker", HERE / "check_agreement_nonidentifiability.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verdict(mod):
    """Run both routes plus corollaries; return True iff everything passes."""
    ok_a, _, _, achieved = mod.route_a()
    ok_b, _, _ = mod.route_b()
    cors = mod.corollaries(achieved)
    return ok_a and ok_b and all(v.get("pass") for v in cors.values())


CONTROLS = {
    # Region tightened on the sum constraint -> some achievable point escapes it.
    "tighten_sum_lower_bound": lambda m: setattr(
        m, "in_region",
        lambda a, u, v: (
            0 <= u <= 1 and 0 <= v <= 1
            and abs(u - v) <= 1 - a
            and 1 - a + Fraction(1, 100) <= u + v <= 1 + a
        ),
    ),
    # Region tightened on the spread constraint.
    "tighten_spread_bound": lambda m: setattr(
        m, "in_region",
        lambda a, u, v: (
            0 <= u <= 1 and 0 <= v <= 1
            and abs(u - v) <= (1 - a) / 2
            and 1 - a <= u + v <= 1 + a
        ),
    ),
    # Region loosened: claims accuracy pairs that agreement in fact forbids.
    # Caught by completeness, since the loosened region has vertices no law attains.
    "loosen_to_unit_square": lambda m: (
        setattr(m, "in_region", lambda a, u, v: 0 <= u <= 1 and 0 <= v <= 1),
        setattr(m, "region_vertices", lambda a: [
            (Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
            (Fraction(1), Fraction(1)), (Fraction(0), Fraction(1)),
        ]),
    ),
    # A vertex that is not achievable for small agreement.
    "false_vertex_one_one": lambda m: setattr(
        m, "region_vertices",
        lambda a: [(1 - a, Fraction(0)), (Fraction(1), a), (a, Fraction(1)),
                   (Fraction(0), 1 - a), (Fraction(1), Fraction(1))],
    ),
    # Wrong slope: swaps the roles of a and 1-a in the interval.
    "swap_a_and_one_minus_a": lambda m: setattr(
        m, "in_region",
        lambda a, u, v: (
            0 <= u <= 1 and 0 <= v <= 1
            and abs(u - v) <= a
            and a <= u + v <= 2 - a
        ),
    ),
}


def main():
    try:
        baseline = load()
        if not verdict(baseline):
            json.dump({"status": "FAIL", "why": "true statement was rejected"},
                      sys.stdout, indent=2)
            print()
            return 2

        results = {}
        for name, perturb in CONTROLS.items():
            mod = load()
            perturb(mod)
            fired = not verdict(mod)
            results[name] = {"checker_rejected_perturbation": fired,
                             "pass": fired}
    except Exception as exc:                                   # noqa: BLE001
        json.dump({"status": "CANNOT_CHECK",
                   "error": f"{type(exc).__name__}: {exc}"}, sys.stdout, indent=2)
        print()
        return 3

    all_fired = all(v["pass"] for v in results.values())
    report = {
        "schema": "ORION.ORION07.AgreementNonidentifiability.NegativeControls.v1",
        "true_statement_accepted": True,
        "controls": results,
        "controls_total": len(results),
        "controls_fired": sum(1 for v in results.values() if v["pass"]),
        "status": "PASS" if all_fired else "FAIL",
    }
    (HERE.parent / "NEGATIVE_CONTROLS.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0 if all_fired else 2


if __name__ == "__main__":
    sys.exit(main())
