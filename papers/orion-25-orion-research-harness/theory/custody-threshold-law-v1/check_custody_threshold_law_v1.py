#!/usr/bin/env python3
"""Exhaustive finite regression for ORION25.CUSTODY_THRESHOLD_LAW.v1."""
from itertools import combinations


def subsets_upto(n, k):
    universe = range(n)
    for r in range(k + 1):
        yield from combinations(universe, r)


def main():
    configurations = 0
    for n in range(1, 9):
        for f in range(n + 1):
            for a in range(n + 1):
                for q in range(1, n + 1):
                    safe_formula = q > f
                    live_formula = q <= n - a

                    compromised_can_form_quorum = any(
                        len(compromised) >= q for compromised in subsets_upto(n, f)
                    )
                    safe_enum = not compromised_can_form_quorum
                    live_enum = all(
                        n - len(unavailable) >= q for unavailable in subsets_upto(n, a)
                    )
                    assert safe_formula == safe_enum
                    assert live_formula == live_enum
                    assert (safe_formula and live_formula) == (f + 1 <= q <= n - a)
                    configurations += 1

    # Governance-quotient control: nominal 3-of-5 keys, but three keys share
    # one principal.  One principal compromise can therefore supply quorum.
    key_to_domain = {0: "A", 1: "A", 2: "A", 3: "B", 4: "C"}
    compromised_domain = "A"
    compromised_keys = [k for k, d in key_to_domain.items() if d == compromised_domain]
    assert len(compromised_keys) == 3
    assert len(compromised_keys) >= 3  # nominal q=3 is defeated by one domain.

    print(
        "ORION25_CUSTODY_THRESHOLD_LAW_V1_PASS "
        f"configurations={configurations} governance_quotient_control=PASS"
    )


if __name__ == "__main__":
    main()
