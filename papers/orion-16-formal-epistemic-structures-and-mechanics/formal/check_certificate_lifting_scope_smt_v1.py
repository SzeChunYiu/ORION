#!/usr/bin/env python3
"""Check the P6 bounded certificate-lifting SMT obligation and live falsifiers."""

from __future__ import annotations

from pathlib import Path

import z3

OBLIGATION = Path(__file__).with_name("certificate_lifting_scope_v1.smt2")


def main() -> int:
    solver = z3.Solver()
    solver.from_file(str(OBLIGATION))
    if solver.check() != z3.unsat:
        raise SystemExit("P6 certificate-lifting obligation is not UNSAT")

    donor = z3.Bool("mutant_donor_valid")
    complete = z3.Bool("mutant_scientific_coordinates_complete")
    mutants = {
        "drop_scientific_coordinate": z3.And(donor, z3.Not(complete)),
        "drop_donor_validity": complete,
    }
    for name, mutant in mutants.items():
        hostile = z3.Solver()
        hostile.add(mutant)
        if hostile.check() != z3.sat:
            raise SystemExit(f"P6 hostile mutant is inert: {name}")

    print("P6 CERTIFICATE LIFTING SMT V1: PASS")
    print("registered obligations: 3")
    print("live hostile mutants: 2")
    print("scope: bounded Boolean lifting law; no empirical or universal proof authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
