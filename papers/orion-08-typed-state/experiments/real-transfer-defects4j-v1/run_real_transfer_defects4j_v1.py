#!/usr/bin/env python3
"""ORION-08 Defects4J leg. Protocol real-transfer-defects4j-v1 + AMENDMENT_V1_BINDING."""
from __future__ import annotations
import json, os, random
from collections import defaultdict

U = {(1, 1): 1.0, (1, 0): -0.05, (0, 1): -1.0, (0, 0): 0.0}  # (action, catches)
THRESH = 0.05 / 2.05          # run iff P(catch|fibre) > this
SPLIT_SEED = 20260830
MIN_MASS = 1
DEGEN = 0.5                   # >50% singleton refined fibres -> CANNOT_CHECK

data = json.load(open(os.path.expanduser("~/d4j_data.json")))

def pkg(f): return ".".join(f.split(".")[:-1])

def name_match(mods, test):
    ts = test.split(".")[-1]
    simples = {m.split(".")[-1] for m in mods}
    if any(ts == s + "Test" or ts == "Test" + s for s in simples): return "exact"
    if any(s and s in ts for s in simples): return "prefix"
    return "none"

def opt(rows):
    """rows: list of catches in {0,1}. Optimal single action for the fibre."""
    p = sum(rows) / len(rows)
    return 1 if p > THRESH else 0

def regret(rows_by_fibre):
    """Mean per-row regret vs the per-row oracle."""
    tot, n = 0.0, 0
    for rows in rows_by_fibre.values():
        a = opt(rows)
        for c in rows:
            tot += U[(c, c)] - U[(a, c)]   # oracle action == c
            n += 1
    return tot / n if n else 0.0

out = {"schema": "ORION08.REAL_TRANSFER_DEFECTS4J.v1", "utility": {str(k): v for k, v in U.items()},
       "threshold": round(THRESH, 6), "split_seed": SPLIT_SEED, "min_mass": MIN_MASS,
       "projects": {}}
degenerate = []

for proj, bugs in sorted(data.items()):
    ids = sorted(bugs)
    rnd = random.Random(SPLIT_SEED); sh = ids[:]; rnd.shuffle(sh)
    h = len(sh) // 2
    train, test = sorted(sh[:h]), sorted(sh[h:])
    if not train or not test: continue
    T = sorted({t for b in train for t in bugs[b]["rels"]})
    if not T: continue

    def build(bugset):
        co, re_, sub = defaultdict(list), defaultdict(list), defaultdict(lambda: defaultdict(list))
        for b in bugset:
            mods, trig = bugs[b]["mods"], set(bugs[b]["trigs"])
            for t in T:
                c = 1 if t in trig else 0
                cf = pkg(t)
                rf = (cf, name_match(mods, t))
                co[cf].append(c); re_[rf].append(c); sub[cf][rf].append(c)
        return co, re_, sub

    co, re_, sub = build(train)
    sing = sum(1 for v in re_.values() if len(v) == 1)
    frac_sing = sing / max(len(re_), 1)
    if frac_sing > DEGEN:
        degenerate.append(proj)

    # prediction from the training half alone
    impure = []
    for cf, subs in sub.items():
        if len(co[cf]) < MIN_MASS: continue
        acts = {rf: opt(v) for rf, v in subs.items() if len(v) >= MIN_MASS}
        if len(set(acts.values())) > 1:
            impure.append({"coarse_fibre": cf, "sub_actions": {str(k): v for k, v in acts.items()}})
    predicted = len(impure) > 0

    r_co, r_re = regret(co), regret(re_)
    observed = (r_co - r_re) > 1e-12

    # out-of-sample transfer: apply train-fitted actions to the held-out half
    co_t, re_t, _ = build(test)
    a_co = {f: opt(v) for f, v in co.items()}
    a_re = {f: opt(v) for f, v in re_.items()}
    def oos(rows_by_fibre, actions, fallback):
        tot, n = 0.0, 0
        for f, rows in rows_by_fibre.items():
            a = actions.get(f, fallback)
            for c in rows:
                tot += U[(c, c)] - U[(a, c)]; n += 1
        return tot / n if n else 0.0
    g_co = opt([c for v in co.values() for c in v])
    g_re = g_co
    oos_co, oos_re = oos(co_t, a_co, g_co), oos(re_t, a_re, g_re)

    out["projects"][proj] = {
        "bugs_train": len(train), "bugs_test": len(test), "test_universe": len(T),
        "rows_train": sum(len(v) for v in co.values()),
        "coarse_fibres": len(co), "refined_fibres": len(re_),
        "refined_singleton_frac": round(frac_sing, 4),
        "predicted_value": predicted, "n_impure_coarse_fibres": len(impure),
        "impure_examples": impure[:3],
        "regret_coarse": round(r_co, 6), "regret_refined": round(r_re, 6),
        "observed_value": observed, "agrees": predicted == observed,
        "oos_regret_coarse": round(oos_co, 6), "oos_regret_refined": round(oos_re, 6),
        "oos_refinement_helps": (oos_co - oos_re) > 1e-12,
    }

P = out["projects"]
val = [p for p, v in P.items() if v["predicted_value"]]
nov = [p for p, v in P.items() if not v["predicted_value"]]
dis = [p for p, v in P.items() if not v["agrees"]]
out["strata"] = {"value": val, "no_value": nov}
out["disagreements"] = dis
out["degenerate_projects"] = degenerate

if degenerate:
    out["terminal"] = "CANNOT_CHECK_DEGENERATE_BINDING"
elif not val or not nov:
    out["terminal"] = "CANNOT_CHECK_NO_CONTRAST"
elif dis:
    out["terminal"] = "THEOREM_FAILS_ON_REAL_DATA_D4J"
else:
    out["terminal"] = "THEOREM_PREDICTS_REAL_TRANSFER_D4J"

with open(os.path.expanduser("~/d4j_RESULTS_V1.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True); fh.write("\n")

print(f"{'proj':<12}{'univ':>5}{'cF':>4}{'rF':>4}{'sing':>6}  pred  obs  agree   r_co     r_re     oos_helps")
for p, v in sorted(P.items()):
    print(f"{p:<12}{v['test_universe']:>5}{v['coarse_fibres']:>4}{v['refined_fibres']:>4}"
          f"{v['refined_singleton_frac']:>6.2f}  {str(v['predicted_value'])[0]}     "
          f"{str(v['observed_value'])[0]}    {str(v['agrees']):<6}"
          f"{v['regret_coarse']:>8.4f} {v['regret_refined']:>8.4f}  {v['oos_refinement_helps']}")
print(f"\nvalue stratum:    {val}")
print(f"no-value stratum: {nov}")
print(f"disagreements:    {dis}")
print(f"TERMINAL: {out['terminal']}")
