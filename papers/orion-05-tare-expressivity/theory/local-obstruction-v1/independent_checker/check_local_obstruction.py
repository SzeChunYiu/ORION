#!/usr/bin/env python3
"""Independent checker for ORION05.LOCAL_SUPPORT_ONE_OBSTRUCTION.v1.

INDEPENDENCE CONTRACT
---------------------
Nothing from the R6S implementation or from HUMAN_PROOF_R6S is imported. The
only things taken from the paper are the DEFINITIONS in Lemma B:

    class            c_q = (alpha_q, beta_q) in F_2^2
    global parity    sum_q alpha_q = 1  (mod 2)
    descent exists   there is a nonempty PROPER subset Q of the support with
                     |Q| <= 2 and sum_{q in Q} c_q = (0,0)

Everything else is enumerated from those definitions. In particular the claimed
classification is NOT used to filter; it is compared against what enumeration
produces.

Checks
    A. Classification at support two -- derive the irreducible ordered class
       pairs by brute force over all 16 pairs and compare with the claim.
    B. Descent always exists for support 3..8 -- Lemma B's conclusion, checked
       exhaustively over every odd-alpha class tuple.
    C. Corroboration count -- the number of odd-alpha class tuples over support
       2..8 must equal the 43,688 recorded in MANUSCRIPT_V3_REFINED.
    D. Negative controls -- perturbed statements must be rejected.

Exit codes
    0  all checks passed
    2  a check FAILED
    3  could not run  -- CANNOT_CHECK
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

CLASSES = [(a, b) for a in (0, 1) for b in (0, 1)]          # F_2^2
WMAX = 8

# The claim under test (Upgrade A of the Wave-1 deep-upgrade note, PR #1617).
CLAIMED_IRREDUCIBLE_ORDERED = {
    ((0, 1), (1, 0)),
    ((1, 0), (0, 1)),
    ((0, 1), (1, 1)),
    ((1, 1), (0, 1)),
}
MANUSCRIPT_TUPLE_COUNT_2_TO_8 = 43688
MANUSCRIPT_SUPPORT_TWO_FAILURES = 4


def odd_alpha(tup) -> bool:
    """Global frame-anticommutation parity constraint."""
    return sum(c[0] for c in tup) % 2 == 1


def descent_exists(tup) -> bool:
    """A nonempty PROPER subset of size <= 2 summing to (0,0) in F_2^2."""
    w = len(tup)
    for size in (1, 2):
        if size >= w:                      # must stay a proper subset
            continue
        for q in itertools.combinations(range(w), size):
            a = sum(tup[i][0] for i in q) % 2
            b = sum(tup[i][1] for i in q) % 2
            if (a, b) == (0, 0):
                return True
    return False


def enumerate_support(w):
    """(total odd-alpha tuples, list of irreducible ones) at support w."""
    total, irreducible = 0, []
    for tup in itertools.product(CLASSES, repeat=w):
        if not odd_alpha(tup):
            continue
        total += 1
        if not descent_exists(tup):
            irreducible.append(tup)
    return total, irreducible


def main() -> int:
    try:
        per_w, totals = {}, 0
        irr2 = None
        for w in range(2, WMAX + 1):
            total, irr = enumerate_support(w)
            totals += total
            per_w[w] = {"odd_alpha_tuples": total, "irreducible": len(irr)}
            if w == 2:
                irr2 = set(irr)

        # A. classification at support two
        check_a = irr2 == CLAIMED_IRREDUCIBLE_ORDERED
        unordered = {frozenset([tuple(x) for x in t]) if t[0] != t[1] else frozenset([t[0]])
                     for t in irr2}

        # B. descent always exists for support 3..8
        check_b = all(per_w[w]["irreducible"] == 0 for w in range(3, WMAX + 1))

        # C. corroboration count recorded in the manuscript
        check_c = totals == MANUSCRIPT_TUPLE_COUNT_2_TO_8
        check_c2 = per_w[2]["irreducible"] == MANUSCRIPT_SUPPORT_TWO_FAILURES

        # D. negative controls -- the enumeration must be able to reject
        controls = {}
        # D1: dropping the odd-alpha constraint must change the support-two answer
        allpairs = [t for t in itertools.product(CLASSES, repeat=2)
                    if not descent_exists(t)]
        controls["odd_alpha_constraint_is_load_bearing"] = {
            "irreducible_without_parity_constraint": len(allpairs),
            "differs_from_4": len(allpairs) != 4,
            "pass": len(allpairs) != 4,
        }
        # D2: a wrong claimed set must be rejected by the same comparison
        wrong = set(CLAIMED_IRREDUCIBLE_ORDERED) | {((1, 0), (1, 1))}
        controls["wrong_classification_rejected"] = {"pass": irr2 != wrong}
        # D3: moving the descent target off (0,0) must change the answer
        def descent_to(tup, target):
            w = len(tup)
            for size in (1, 2):
                if size >= w:
                    continue
                for q in itertools.combinations(range(w), size):
                    if (sum(tup[i][0] for i in q) % 2,
                            sum(tup[i][1] for i in q) % 2) == target:
                        return True
            return False
        off_target = [t for t in itertools.product(CLASSES, repeat=2)
                      if odd_alpha(t) and not descent_to(t, (0, 1))]
        controls["descent_target_is_load_bearing"] = {
            "irreducible_if_target_were_0_1": len(off_target),
            "pass": set(off_target) != irr2,
        }
        # D4: the structural criterion -- no irreducible pair may contain (0,0)
        controls["no_irreducible_pair_contains_zero_class"] = {
            "pass": all((0, 0) not in t for t in irr2),
        }

        # Observation (not a control): at support two the properness restriction
        # is automatically satisfied, because odd alpha-parity already forbids
        # the full-support subset from summing to (0,0). Recorded because a
        # reader may otherwise assume properness is doing work here; it is not.
        def descent_allowing_improper(tup):
            w = len(tup)
            for size in (1, 2):
                for q in itertools.combinations(range(w), size):
                    if (sum(tup[i][0] for i in q) % 2,
                            sum(tup[i][1] for i in q) % 2) == (0, 0):
                        return True
            return False
        improper2 = {t for t in itertools.product(CLASSES, repeat=2)
                     if odd_alpha(t) and not descent_allowing_improper(t)}
        observation_properness = {
            "irreducible_set_unchanged_if_subset_may_be_improper": improper2 == irr2,
            "why": ("odd alpha-parity forces alpha_1 + alpha_2 = 1, so the full "
                    "support can never sum to (0,0); properness is therefore "
                    "vacuous at support two, though it is essential for w >= 3"),
        }

        controls_ok = all(v["pass"] for v in controls.values())
        passed = check_a and check_b and check_c and check_c2 and controls_ok
    except Exception as exc:                                    # noqa: BLE001
        json.dump({"status": "CANNOT_CHECK",
                   "error": f"{type(exc).__name__}: {exc}"}, sys.stdout, indent=2)
        print()
        return 3

    report = {
        "schema": "ORION.ORION05.LocalObstruction.CheckerReport.v1",
        "successor_id": "ORION05.LOCAL_SUPPORT_ONE_OBSTRUCTION.v1",
        "independence": ("no R6S implementation or generating proof imported; "
                         "only the Lemma B definitions are transcribed"),
        "check_A_support_two_classification": {
            "derived_irreducible_ordered": sorted(tuple(map(list, t)) for t in irr2),
            "claimed": sorted(tuple(map(list, t)) for t in CLAIMED_IRREDUCIBLE_ORDERED),
            "match": check_a,
            "count": len(irr2),
            "unordered_types_up_to_swap": len(unordered),
        },
        "check_B_descent_exists_support_3_to_8": {
            "per_support": per_w,
            "all_zero_irreducible_for_w_ge_3": check_b,
        },
        "check_C_manuscript_corroboration": {
            "odd_alpha_tuples_support_2_to_8_recomputed": totals,
            "manuscript_records": MANUSCRIPT_TUPLE_COUNT_2_TO_8,
            "match": check_c,
            "support_two_failures_recomputed": per_w[2]["irreducible"],
            "manuscript_records_failures": MANUSCRIPT_SUPPORT_TWO_FAILURES,
            "match_failures": check_c2,
        },
        "check_D_negative_controls": controls,
        "observation_properness_vacuous_at_support_two": observation_properness,
        "status": "PASS" if passed else "FAIL",
    }
    out = Path(__file__).resolve().parent.parent / "RESULT.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    json.dump({k: report[k] for k in
               ("status", "check_A_support_two_classification",
                "check_C_manuscript_corroboration")}, sys.stdout, indent=2)
    print()
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
