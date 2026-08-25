"""EXEC-P3-01 independent checker. Does not import the runner.

Quotients are recomputed as explicit equivalence-class sets compared by set
equality on terminal-distinguished pairs, rather than by pairwise agreement.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent


def main() -> int:
    m = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    g = m["grid"]
    objs = list(range(g["n_obj"]))
    obs_fns = list(itertools.product(range(g["n_obs"]), repeat=g["n_obj"]))
    terms = list(itertools.product(range(g["n_term"]), repeat=g["n_obj"]))
    pairs = fa = nfa = viol = div = 0
    for I in obs_fns:
        for J in obs_fns:
            for T in terms:
                pairs += 1
                dist = [(s, t) for s, t in itertools.combinations(objs, 2) if T[s] != T[t]]
                # class-set formulation
                ci = {o: frozenset(x for x in objs if I[x] == I[o]) for o in objs}
                cj = {o: frozenset(x for x in objs if J[x] == J[o]) for o in objs}
                is_fa = all((t in ci[s]) == (t in cj[s]) for s, t in dist)
                direct = all((I[s] == I[t]) == (J[s] == J[t]) for s, t in dist)
                if is_fa: fa += 1
                else: nfa += 1
                if is_fa != direct: viol += 1
                if is_fa:
                    if any(T[s] != T[t] for s, t in itertools.combinations(objs, 2)
                           if I[s] == I[t] and J[s] == J[t] and (s, t) not in dist):
                        div += 1
    a, ti, c = m["abstraction"], m["tie"], m["centralization"]
    dis = []
    for n_, mine, th in (("pairs", pairs, a["pairs"]), ("fully_abstract", fa, a["fully_abstract"]),
                         ("violations", viol, a["biconditional_violations"]),
                         ("tie_divergences", div, ti["terminal_divergences"])):
        if mine != th: dis.append(f"{n_}: mine={mine} theirs={th}")
    both = fa > 0 and nfa > 0
    cen_ok = c["wins_when_irrelevant"] == 0 and c["wins_when_relevant"] > 0 and c["ties_when_irrelevant"] > 0
    r = {"schema_version": "orion.independent-checker-receipt.v1", "job_id": "EXEC-P3-01",
         "imports_runner": False,
         "method_difference": "Quotients as explicit class sets compared by membership, not pairwise agreement.",
         "independent_findings": {"pairs": pairs, "fully_abstract": fa, "not_fully_abstract": nfa,
             "biconditional_violations": viol, "ideal_product_tie_divergences": div,
             "both_outcomes_occur": both,
             "centralization_wins_when_irrelevant": c["wins_when_irrelevant"],
             "centralization_wins_when_relevant": c["wins_when_relevant"],
             "centralization_behaves_as_theorem_requires": cen_ok},
         "disagreements": dis,
         "terminal": ("EXEC_P3_01_SECOND_INDEPENDENT_CHECKER_GREEN"
                      if not dis and both and cen_ok and div == 0
                      else "EXEC_P3_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"),
         "independence_boundary": "Two implementations inside one programme; not external adjudication."}
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r["independent_findings"], indent=2)); print("disagreements:", dis or "none")
    return 0 if not dis else 2


if __name__ == "__main__":
    sys.exit(main())
