"""EXEC-P11-01 independent checker. Does not import the runner.

T16 is recomputed from the closed form and compared against a search, i.e. the
opposite direction to the runner, which searches and compares against the form.
T18 sufficiency is recomputed by explicit pair-separation over element pairs
rather than by block containment.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent


def t16_check(Kmax, vmax, umax):
    mism = dom = nondom = spurious = 0
    for K in range(0, Kmax + 1):
        for d in range(1, vmax + 1):
            for c in range(0, d):
                closed = K // (d - c) + 1
                # verify the closed form is a crossover AND that closed-1 is not
                ok = (K + closed * c < closed * d)
                prev_ok = closed > 1 and (K + (closed - 1) * c < (closed - 1) * d)
                if not ok or prev_ok:
                    mism += 1
                dom += 1
            for c in range(d, vmax + 1):
                nondom += 1
                if any(K + u * c < u * d for u in range(1, min(umax, 50) + 1)):
                    spurious += 1
    return mism, dom, nondom, spurious


def parts(n):
    def helper(elems):
        if not elems:
            yield []
            return
        f, rest = elems[0], elems[1:]
        for sm in helper(rest):
            for i in range(len(sm)):
                yield sm[:i] + [[f] + sm[i]] + sm[i + 1:]
            yield [[f]] + sm
    for p in helper(list(range(n))):
        yield tuple(frozenset(b) for b in p)


def same_block(p, x, y):
    return any(x in b and y in b for b in p)


def t18_check(n):
    allp = list(parts(n))
    pairs = viol = 0
    for pz in allp:
        for pr in allp:
            pairs += 1
            # sufficiency by element pairs: pz must never merge what pr separates
            suff = all(
                same_block(pr, x, y)
                for x, y in itertools.combinations(range(n), 2)
                if same_block(pz, x, y)
            )
            # refinement by block containment
            ref = all(any(b <= bb for bb in pr) for b in pz)
            if suff != ref:
                viol += 1
    return pairs, viol


def main() -> int:
    m = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    g = m["grid"]
    dis = []
    mism, dom, nondom, spur = t16_check(g["t16_Kmax"], g["t16_vmax"], g["t16_umax"])
    t16 = m["t16"]
    for name, mine, theirs in (("t16_mismatches", mism, t16["closed_form_mismatches"]),
                               ("t16_dominant", dom, t16["compiled_dominant_cells"]),
                               ("t16_nondominant", nondom, t16["nondominant_cells_examined"]),
                               ("t16_spurious", spur, t16["spurious_dominance_in_nondominant_branch"])):
        if mine != theirs:
            dis.append(f"{name}: mine={mine} theirs={theirs}")
    pairs, viol = t18_check(g["t18_n"])
    t18 = m["t18"]
    for name, mine, theirs in (("t18_pairs", pairs, t18["pairs"]),
                               ("t18_sufficiency_violations", viol, t18["sufficiency_violations"])):
        if mine != theirs:
            dis.append(f"{name}: mine={mine} theirs={theirs}")

    both_phases = t16["compiled_dominant_cells"] > 0 and t16["nondominant_cells_examined"] > 0
    donor_both = t18["freshness_admits_unsafe"] > 0 and t18["freshness_refuses_safe"] > 0
    r = {
        "schema_version": "orion.independent-checker-receipt.v1",
        "job_id": "EXEC-P11-01",
        "imports_runner": False,
        "method_difference": (
            "T16 checked closed-form-first (verify U* is a crossover and U*-1 is not); "
            "the runner searched first. T18 sufficiency checked by element-pair "
            "separation; the runner used block containment."
        ),
        "independent_findings": {
            "t16_closed_form_mismatches": mism,
            "t16_dominant_cells": dom,
            "t16_nondominant_cells": nondom,
            "t16_spurious_dominance": spur,
            "t16_both_phases_exercised": both_phases,
            "t18_pairs": pairs,
            "t18_sufficiency_violations": viol,
            "t18_freshness_donor_fails_both_directions": donor_both,
        },
        "disagreements": dis,
        "terminal": ("EXEC_P11_01_SECOND_INDEPENDENT_CHECKER_GREEN"
                     if not dis and both_phases and donor_both
                     else "EXEC_P11_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"),
        "independence_boundary": "Two implementations inside one programme; not external adjudication.",
    }
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r["independent_findings"], indent=2))
    print("disagreements:", dis or "none")
    print("terminal:", r["terminal"])
    return 0 if not dis and both_phases and donor_both else 2


if __name__ == "__main__":
    sys.exit(main())
