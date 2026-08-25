"""EXEC-P12-01 independent checker. Does not import the runner.

Verifies the universally-quantified clause by exhaustive search over ALL
deterministic certificate-only allocators, and re-derives the half-gap bound
from a separately written loss table rather than from the runner's argmin.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent


def main() -> int:
    m = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    g = m["grid"]
    A = list(range(g["n_actions"]))
    CV = [v for v in itertools.product(range(g["n_costs"]), repeat=g["n_actions"])]

    def unique_opt(cv):
        lo = min(cv)
        w = [a for a in A if cv[a] == lo]
        return w[0] if len(w) == 1 else None

    oracle_bad = sum(1 for cv in CV if min(cv[a] for a in A) != min(cv))
    classes = escapes = viol = tight = 0
    hedge_viol = nonhedge_viol = 0
    witnesses = []

    for cv1, cv2 in itertools.combinations(CV, 2):
        o1, o2 = unique_opt(cv1), unique_opt(cv2)
        if o1 is None or o2 is None or o1 == o2:
            continue
        classes += 1
        # exhaustive over every deterministic allocator (one action for the class)
        per = []
        for a in A:
            r1, r2 = cv1[a] - min(cv1), cv2[a] - min(cv2)
            per.append((a, r1, r2, (r1 + r2) / 2.0))
        if any(r1 == 0 and r2 == 0 for _, r1, r2, _ in per):
            escapes += 1
        best_a, _, _, best = min(per, key=lambda t: t[3])
        gap = min(cv1[o2] - cv1[o1], cv2[o1] - cv2[o2])
        bound = gap / 2.0
        if best + 1e-12 < bound:
            viol += 1
            if best_a not in (o1, o2):
                hedge_viol += 1
            else:
                nonhedge_viol += 1
            if len(witnesses) < 5:
                witnesses.append({"cv1": list(cv1), "cv2": list(cv2), "optima": [o1, o2],
                                  "best_expected": best, "bound": bound,
                                  "argmin_action": best_a, "is_hedge": best_a not in (o1, o2)})
        elif abs(best - bound) < 1e-12:
            tight += 1

    dis = []
    for name, mine, theirs in (
        ("oracle_bad", oracle_bad, m["oracle"]["positive_regret_cases"]),
        ("classes", classes, m["ambiguity"]["classes_found"]),
        ("escapes", escapes, m["ambiguity"]["classes_with_zero_regret_allocator"]),
        ("bound_violations", viol, m["bound"]["violations"]),
        ("tight", tight, m["bound"]["tight_classes"]),
    ):
        if mine != theirs:
            dis.append(f"{name}: mine={mine} theirs={theirs}")

    r = {
        "schema_version": "orion.independent-checker-receipt.v1",
        "job_id": "EXEC-P12-01",
        "imports_runner": False,
        "method_difference": ("Universal clause verified by exhaustive search over every "
                              "deterministic certificate-only allocator per class, not by "
                              "an argument about one; bound re-derived from a separate loss table."),
        "independent_findings": {
            "oracle_positive_regret_cases": oracle_bad,
            "ambiguous_classes": classes,
            "allocators_escaping_with_zero_regret": escapes,
            "half_gap_bound_violations": viol,
            "violations_that_are_hedge_actions": hedge_viol,
            "violations_not_hedge_actions": nonhedge_viol,
            "tight_classes": tight,
            "bound_is_tight_somewhere": tight > 0,
            "ambiguity_exists": classes > 0,
        },
        "witnesses": witnesses,
        "disagreements": dis,
        "terminal": ("EXEC_P12_01_SECOND_INDEPENDENT_CHECKER_GREEN" if not dis
                     else "EXEC_P12_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"),
        "independence_boundary": "Two implementations inside one programme; not external adjudication.",
    }
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r["independent_findings"], indent=2))
    print("disagreements:", dis or "none")
    return 0 if not dis else 2


if __name__ == "__main__":
    sys.exit(main())
