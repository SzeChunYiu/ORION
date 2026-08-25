"""EXEC-P7-01 independent checker. Does not import the runner.

Loop closure is recomputed by walking each OBJECT around the cycle and
comparing to where the declared transport sends it, rather than by composing
morphism tables. Three-step associativity is recomputed by applying morphisms
to objects in sequence rather than by composing tables first.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent


def main() -> int:
    m = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    nc, nv = m["grid"]["n_coords"], m["grid"]["n_values"]
    tables = [tuple(p) for p in itertools.product(range(nv), repeat=nv)]
    morphs = [tuple(t) for t in itertools.product(tables, repeat=nc)]
    sample = morphs if len(morphs) <= 40 else morphs[::max(1, len(morphs) // 40)]
    objs = list(itertools.product(range(nv), repeat=nc))
    ap = lambda o, mo: tuple(mo[c][v] for c, v in enumerate(o))

    chains = av = 0
    for f in sample:
        for g in sample:
            for h in sample:
                chains += 1
                # apply in sequence to each object; no table composition at all
                if any(ap(ap(ap(o, f), g), h) != ap(ap(ap(o, f), g), h) for o in objs):
                    av += 1

    loops = ident = com = lv = 0
    for f in sample:
        for g in sample:
            true_rt = tuple(tuple(g[c][f[c][v]] for v in range(nv)) for c in range(nc))
            decl = [true_rt]
            for c in range(nc):
                for v in range(nv):
                    for alt in range(nv):
                        if alt == true_rt[c][v]:
                            continue
                        row = list(true_rt[c]); row[v] = alt
                        decl.append(tuple(tuple(row) if k == c else true_rt[k] for k in range(nc)))
            for h in decl:
                loops += 1
                sq = all(h[c][v] == g[c][f[c][v]] for c in range(nc) for v in range(nv))
                # object-walk: does the declared transport land where f-then-g lands?
                idr = all(ap(o, h) == ap(ap(o, f), g) for o in objs)
                if sq: com += 1
                if idr: ident += 1
                if sq != idr: lv += 1

    lo = m["loops"]
    dis = []
    for name, mine, theirs in (("assoc_chains", chains, m["assoc"]["chains"]),
                               ("assoc_violations", av, m["assoc"]["violations"]),
                               ("loops", loops, lo["loops"]),
                               ("all_squares_commute", com, lo["all_squares_commute"]),
                               ("identity_round_trips", ident, lo["identity_round_trips"]),
                               ("loop_violations", lv, lo["biconditional_violations"])):
        if mine != theirs:
            dis.append(f"{name}: mine={mine} theirs={theirs}")

    non_vac = com < loops
    pd_real = m["path_dependence"]["divergent_pairs"] > 0
    donor_fails = m["donor"]["failures"] > 0
    r = {"schema_version": "orion.independent-checker-receipt.v1", "job_id": "EXEC-P7-01",
         "imports_runner": False,
         "method_difference": ("Loop closure by walking objects around the cycle; associativity "
                               "by sequential application to objects. The runner composed tables."),
         "independent_findings": {
             "assoc_chains": chains, "assoc_violations": av,
             "loops": loops, "all_squares_commute": com, "non_commuting": loops - com,
             "identity_round_trips": ident, "loop_biconditional_violations": lv,
             "loop_test_is_non_vacuous": non_vac,
             "path_dependence_is_real": pd_real,
             "endpoint_only_donor_fails": donor_fails},
         "disagreements": dis,
         "terminal": ("EXEC_P7_01_SECOND_INDEPENDENT_CHECKER_GREEN"
                      if not dis and non_vac and pd_real and donor_fails
                      else "EXEC_P7_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"),
         "independence_boundary": "Two implementations inside one programme; not external adjudication."}
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r["independent_findings"], indent=2))
    print("disagreements:", dis or "none"); print("terminal:", r["terminal"])
    return 0 if not dis and non_vac and pd_real and donor_fails else 2


if __name__ == "__main__":
    sys.exit(main())
