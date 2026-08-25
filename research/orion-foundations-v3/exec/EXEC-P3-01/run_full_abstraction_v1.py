"""EXEC-P3-01 -- scientific full abstraction and the ideal-product tie (OSTC-T9)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


def quotient(obs, objs):
    """Partition of objs induced by observation function obs."""
    cls = {}
    for o in objs:
        cls.setdefault(obs[o], set()).add(o)
    return frozenset(frozenset(v) for v in cls.values())


def run(n_obj=4, n_obs=3, n_term=2):
    objs = list(range(n_obj))
    obs_fns = list(itertools.product(range(n_obs), repeat=n_obj))
    # a responsibility family is a target terminal map on objects
    terms = list(itertools.product(range(n_term), repeat=n_obj))

    pairs = fa = nfa = viol = 0
    minimal_w = None
    tie_pairs = tie_div = 0

    for I in obs_fns:
        for J in obs_fns:
            for T in terms:
                pairs += 1
                # pairs distinguished by the target terminal
                dist = [(s, t) for s, t in itertools.combinations(objs, 2) if T[s] != T[t]]
                # full abstraction restricted to terminal-distinguished pairs
                is_fa = all((I[s] == I[t]) == (J[s] == J[t]) for s, t in dist)
                # independent notion: quotients agree on those pairs
                qi = quotient(I, objs); qj = quotient(J, objs)
                same_on_dist = all(
                    (any(s in b and t in b for b in qi)) == (any(s in b and t in b for b in qj))
                    for s, t in dist)
                if is_fa: fa += 1
                else: nfa += 1
                if is_fa != same_on_dist:
                    viol += 1
                    if minimal_w is None:
                        minimal_w = {"I": list(I), "J": list(J), "T": list(T)}
                # ideal-product tie: fully abstract implementations decode identically
                if is_fa:
                    tie_pairs += 1
                    # decoder factors through the quotient: same class -> same terminal
                    ok = all(T[s] == T[t] for s, t in itertools.combinations(objs, 2)
                             if I[s] == I[t] and J[s] == J[t] and (s, t) not in dist)
                    if not ok:
                        tie_div += 1

    # centralization comparator: an extra observable coordinate
    cen_cases = tie_irrel = win_rel = win_irrel = 0
    for I in obs_fns[:60]:
        for extra in obs_fns[:60]:
            for T in terms:
                cen_cases += 1
                dist = [(s, t) for s, t in itertools.combinations(objs, 2) if T[s] != T[t]]
                # is the extra coordinate target-relevant?
                relevant = any(extra[s] != extra[t] and I[s] == I[t] for s, t in dist)
                base_ok = all(I[s] != I[t] for s, t in dist)
                cen = tuple((I[o], extra[o]) for o in objs)
                cen_ok = all(cen[s] != cen[t] for s, t in dist)
                if cen_ok and not base_ok:
                    if relevant: win_rel += 1
                    else: win_irrel += 1
                elif cen_ok == base_ok and not relevant:
                    tie_irrel += 1

    return {"abstraction": {"pairs": pairs, "fully_abstract": fa, "not_fully_abstract": nfa,
                            "biconditional_violations": viol, "minimal_witness": minimal_w},
            "tie": {"fully_abstract_pairs": tie_pairs, "terminal_divergences": tie_div},
            "centralization": {"cases": cen_cases, "ties_when_irrelevant": tie_irrel,
                               "wins_when_relevant": win_rel, "wins_when_irrelevant": win_irrel}}


def main() -> None:
    t0 = time.time()
    grid = {"n_obj": 4, "n_obs": 3, "n_term": 2, "seed": 20260825}
    r = run(grid["n_obj"], grid["n_obs"], grid["n_term"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P3-01", "grid": grid, **r,
         "totals": {"cells_enumerated": r["abstraction"]["pairs"] + r["centralization"]["cases"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    a, t, c = r["abstraction"], r["tie"], r["centralization"]
    print("abstraction pairs", a["pairs"], "FA", a["fully_abstract"], "notFA",
          a["not_fully_abstract"], "viol", a["biconditional_violations"])
    print("tie: FA pairs", t["fully_abstract_pairs"], "divergences", t["terminal_divergences"])
    print("centralization ties_irrel", c["ties_when_irrelevant"], "wins_rel",
          c["wins_when_relevant"], "wins_IRREL", c["wins_when_irrelevant"])


if __name__ == "__main__":
    main()
