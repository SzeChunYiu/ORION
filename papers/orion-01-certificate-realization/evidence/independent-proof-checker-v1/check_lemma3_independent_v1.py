#!/usr/bin/env python3
"""Implementation-independent checker for ORION-01 theory-A Lemma 3.

Written from the THEOREM STATEMENT in theory-A-MANUSCRIPT_V2.md, not from any
production module. Nothing is imported from src/orion.

Statement as written:
  F_b(a_1..a_b) = 1                      if all letters are the same
                                          nonidentity Pauli
              = #{i : a_i != I}           otherwise
  Lemma 3: replacing ONE argument of F_b increases its value by at most b-1,
           and the bound is attained.
"""
from itertools import product
import json

PAULIS = ("I", "X", "Y", "Z")          # I is the identity letter

def F(a):
    """F_b exactly as the manuscript defines it."""
    nz = [x for x in a if x != "I"]
    if len(a) > 0 and len(nz) == len(a) and len(set(nz)) == 1:
        return 1                        # all letters the same nonidentity Pauli
    return len(nz)                      # otherwise: number of nonidentity letters

def check(b):
    worst = -10**9
    attained = []
    for a in product(PAULIS, repeat=b):
        base = F(a)
        for j in range(b):
            for c in PAULIS:
                if c == a[j]:
                    continue
                nxt = a[:j] + (c,) + a[j+1:]
                d = F(nxt) - base
                if d > worst:
                    worst = d
                    attained = [(a, j, c, base, F(nxt))]
                elif d == worst and len(attained) < 3:
                    attained.append((a, j, c, base, F(nxt)))
    return worst, attained

def main():
    rows = []
    ok = True
    for b in range(2, 9):
        worst, ex = check(b)
        bound_ok = worst <= b - 1          # "increases by at most b-1"
        tight_ok = worst == b - 1          # "and the bound is attained"
        ok &= bound_ok and tight_ok
        rows.append({
            "b": b,
            "max_increase_observed": worst,
            "claimed_bound_b_minus_1": b - 1,
            "at_most_holds": bound_ok,
            "bound_attained": tight_ok,
            "witness": {"from": "".join(ex[0][0]), "position": ex[0][1],
                        "replaced_by": ex[0][2],
                        "F_before": ex[0][3], "F_after": ex[0][4]},
            "tuples_checked": 4 ** b,
        })

    # ---- mutation controls: the checker must REJECT a wrong F ----
    global F
    true_F = F
    def F_no_special(a):                   # drops the all-same-nonidentity case
        return len([x for x in a if x != "I"])
    F = F_no_special
    mut_worst, _ = check(4)
    F = true_F
    # under the mutated F one replacement changes the count by at most 1,
    # so the b-1=3 bound is NOT attained -> the checker must notice
    mutation_detected = mut_worst != 3

    out = {
        "checker": "ORION01.THEORY_A.LEMMA3.INDEPENDENT.v1",
        "source": "theorem statement only; no import from src/orion",
        "rows": rows,
        "all_b_pass": bool(ok),
        "mutation_control": {
            "mutation": "F without the all-same-nonidentity special case",
            "max_increase_under_mutation_b4": mut_worst,
            "detected_as_different": bool(mutation_detected),
        },
        "terminal": ("LEMMA3_EXHAUSTIVELY_VERIFIED_b2_b8"
                     if ok and mutation_detected else "LEMMA3_CHECK_FAILED"),
    }
    print(json.dumps(out, indent=2))
    return 0 if (ok and mutation_detected) else 1

if __name__ == "__main__":
    raise SystemExit(main())
