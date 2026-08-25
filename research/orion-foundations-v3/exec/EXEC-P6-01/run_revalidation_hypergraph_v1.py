"""EXEC-P6-01 -- dependency-hypergraph selective revalidation (OSTC-T10, T11)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


def minimal_antichain(families):
    """Inclusion-minimal families only (MinSup)."""
    fs = [frozenset(f) for f in families]
    return [f for f in fs if not any(g < f for g in fs)]


def survives_by_minsup(minsup, R):
    return any(not (F & R) for F in minsup)


def survives_by_replay(families, R):
    """Independent notion: some complete family has every token surviving."""
    return any(all(t not in R for t in F) for F in families)


def min_cost_repair(minsup, R, cost):
    """Cheapest set of revoked tokens to restore so that some family is clean."""
    best = None
    for F in minsup:
        need = F & R
        c = sum(cost[t] for t in need)
        if best is None or c < best[0]:
            best = (c, sorted(need))
    return best if best else (0, [])


def min_cardinality_repair(minsup, R):
    best = None
    for F in minsup:
        need = F & R
        if best is None or len(need) < len(best[1]):
            best = (len(need), sorted(need))
    return best if best else (0, [])


def run(n_tokens=6, max_fam=3, fam_size=3):
    toks = list(range(n_tokens))
    cost = {t: 1 + (t % 3) for t in toks}          # non-uniform, so cost != cardinality
    all_fams = [frozenset(c) for c in itertools.combinations(toks, fam_size)]

    cells = survived = died = bicond_viol = 0
    minimal_w = None
    donor_agree = donor_dis = 0
    rep_cells = heur_wins = opt_better = ties = 0

    for fams in itertools.combinations(all_fams, max_fam):
        minsup = minimal_antichain(fams)
        for rsize in range(0, n_tokens + 1):
            for R in itertools.combinations(toks, rsize):
                Rs = frozenset(R)
                cells += 1
                a = survives_by_minsup(minsup, Rs)
                b = survives_by_replay(fams, Rs)
                if a:
                    survived += 1
                else:
                    died += 1
                if a != b:
                    bicond_viol += 1
                    if minimal_w is None:
                        minimal_w = {"families": [sorted(f) for f in fams],
                                     "revoked": sorted(R), "minsup": a, "replay": b}
                # any-support donor: uses all families, not just minimal
                donor = any(not (frozenset(f) & Rs) for f in fams)
                if donor == a:
                    donor_agree += 1
                else:
                    donor_dis += 1
                # repair comparison only where j is currently dead
                if not a and minsup:
                    rep_cells += 1
                    oc, _ = min_cost_repair(minsup, Rs, cost)
                    hn, hset = min_cardinality_repair(minsup, Rs)
                    hc = sum(cost[t] for t in hset)
                    if hc < oc:
                        heur_wins += 1
                    elif oc < hc:
                        opt_better += 1
                    else:
                        ties += 1

    # T10 on hypergraphs: composing two certificates must retain blockers
    comps = losses = 0
    for b1 in itertools.product((0, 1), repeat=3):
        for b2 in itertools.product((0, 1), repeat=3):
            comps += 1
            out = tuple(x | y for x, y in zip(b1, b2))   # union retains blockers
            if any(x and not o for x, o in zip(b1, out)) or any(y and not o for y, o in zip(b2, out)):
                losses += 1

    return {"t11": {"cells": cells, "survived": survived, "died": died,
                    "biconditional_violations": bicond_viol, "minimal_witness": minimal_w},
            "t10": {"compositions": comps, "blocker_losses": losses},
            "repair": {"cells": rep_cells, "heuristic_wins": heur_wins,
                       "optimum_strictly_better": opt_better, "ties": ties},
            "donor": {"agreements": donor_agree, "disagreements": donor_dis}}


def main() -> None:
    t0 = time.time()
    grid = {"n_tokens": 6, "max_fam": 3, "fam_size": 3, "seed": 20260825}
    r = run(grid["n_tokens"], grid["max_fam"], grid["fam_size"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P6-01",
         "grid": grid, **r,
         "totals": {"cells_enumerated": r["t11"]["cells"] + r["t10"]["compositions"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    print("t11 cells", r["t11"]["cells"], "survived", r["t11"]["survived"],
          "died", r["t11"]["died"], "viol", r["t11"]["biconditional_violations"])
    print("t10 comps", r["t10"]["compositions"], "blocker_losses", r["t10"]["blocker_losses"])
    print("repair cells", r["repair"]["cells"], "heur_wins", r["repair"]["heuristic_wins"],
          "opt_better", r["repair"]["optimum_strictly_better"], "ties", r["repair"]["ties"])
    print("donor agree", r["donor"]["agreements"], "disagree", r["donor"]["disagreements"])


if __name__ == "__main__":
    main()
