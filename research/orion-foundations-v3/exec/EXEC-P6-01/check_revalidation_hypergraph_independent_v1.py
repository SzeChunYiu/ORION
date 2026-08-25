"""EXEC-P6-01 independent checker. Does not import the runner.

Survival is recomputed by forward closure from the SURVIVING token set --
build the set of tokens that remain, then ask whether any family is a subset of
it -- rather than by intersecting families with the revoked set. Minimality is
recomputed by pairwise strict-superset elimination rather than by the runner's
comprehension. The two routes can disagree.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent


def minsup_by_elimination(fams):
    out = []
    for f in fams:
        if not any(g != f and g <= f for g in fams):
            out.append(f)
    return out


def main() -> int:
    m = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    g = m["grid"]
    toks = list(range(g["n_tokens"]))
    cost = {t: 1 + (t % 3) for t in toks}
    all_fams = [frozenset(c) for c in itertools.combinations(toks, g["fam_size"])]

    cells = surv = died = viol = 0
    rep = heur = optb = ties = 0
    for fams in itertools.combinations(all_fams, g["max_fam"]):
        ms = minsup_by_elimination(list(fams))
        for rsize in range(0, g["n_tokens"] + 1):
            for R in itertools.combinations(toks, rsize):
                Rs = frozenset(R)
                alive = frozenset(toks) - Rs          # forward: what survives
                cells += 1
                by_closure = any(F <= alive for F in fams)
                by_minsup = any(F <= alive for F in ms)
                if by_closure:
                    surv += 1
                else:
                    died += 1
                if by_closure != by_minsup:
                    viol += 1
                if not by_closure and ms:
                    rep += 1
                    oc = min(sum(cost[t] for t in (F & Rs)) for F in ms)
                    hf = min(ms, key=lambda F: len(F & Rs))
                    hc = sum(cost[t] for t in (hf & Rs))
                    if hc < oc:
                        heur += 1
                    elif oc < hc:
                        optb += 1
                    else:
                        ties += 1

    t11 = m["t11"]; rp = m["repair"]
    dis = []
    for name, mine, theirs in (("cells", cells, t11["cells"]),
                               ("survived", surv, t11["survived"]),
                               ("died", died, t11["died"]),
                               ("biconditional_violations", viol, t11["biconditional_violations"]),
                               ("repair_cells", rep, rp["cells"]),
                               ("heuristic_wins", heur, rp["heuristic_wins"]),
                               ("optimum_strictly_better", optb, rp["optimum_strictly_better"])):
        if mine != theirs:
            dis.append(f"{name}: mine={mine} theirs={theirs}")

    both = surv > 0 and died > 0
    cost_does_work = optb > 0
    r = {"schema_version": "orion.independent-checker-receipt.v1", "job_id": "EXEC-P6-01",
         "imports_runner": False,
         "method_difference": ("Survival recomputed by forward closure from the surviving "
                               "token set (F subset-of alive) rather than by family-revocation "
                               "intersection; minimality by pairwise strict-superset elimination."),
         "independent_findings": {
             "cells": cells, "survived": surv, "died": died,
             "biconditional_violations": viol,
             "both_outcomes_occur": both,
             "blocker_losses": m["t10"]["blocker_losses"],
             "repair_cells": rep, "heuristic_wins": heur,
             "optimum_strictly_better": optb, "ties": ties,
             "cost_model_does_work": cost_does_work},
         "disagreements": dis,
         "terminal": ("EXEC_P6_01_SECOND_INDEPENDENT_CHECKER_GREEN"
                      if not dis and both and cost_does_work
                      else "EXEC_P6_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"),
         "independence_boundary": "Two implementations inside one programme; not external adjudication."}
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r["independent_findings"], indent=2))
    print("disagreements:", dis or "none")
    print("terminal:", r["terminal"])
    return 0 if not dis and both and cost_does_work else 2


if __name__ == "__main__":
    sys.exit(main())
