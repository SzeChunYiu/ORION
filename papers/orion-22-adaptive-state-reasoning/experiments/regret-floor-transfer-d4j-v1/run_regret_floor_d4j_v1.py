#!/usr/bin/env python3
"""ORION-22 regret-floor transfer to Defects4J. Protocol regret-floor-transfer-d4j-v1.

Two phases. Phase 1 reads ONLY the prediction half, writes PREDICTIONS_V1.json and
prints its SHA-256. Phase 2 then scores the protected half once. The interval rule
is a Clopper-Pearson 95% interval on the pooled floor rate; it is fixed in phase 1
and written into the predictions file before any protected bug is read.
"""
from __future__ import annotations
import hashlib, json, os, random, sys
from collections import defaultdict

SEED = 20260830
d = json.load(open(os.path.expanduser("~/d4j_data.json")))
OUT = os.path.expanduser("~/o22_")

def pkg(f): return ".".join(f.split(".")[:-1])

def cp(k, n, lo=True, alpha=0.05):
    """Clopper-Pearson bound without scipy: bisect the Beta CDF via the binomial tail."""
    from math import comb
    def tail_le(p, k, n):   # P(X <= k)
        return sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(k+1))
    if n == 0: return 0.0
    if lo:
        if k == 0: return 0.0
        a, b = 0.0, 1.0
        for _ in range(60):
            m = (a+b)/2
            if 1 - tail_le(m, k-1, n) > alpha/2: b = m
            else: a = m
        return a
    if k == n: return 1.0
    a, b = 0.0, 1.0
    for _ in range(60):
        m = (a+b)/2
        if tail_le(m, k, n) < alpha/2: b = m
        else: a = m
    return b

def build(bugs, ids, alias):
    """alias: bug -> class key. Returns class -> {action -> catch count}, class size."""
    cls = defaultdict(lambda: defaultdict(int)); size = defaultdict(int)
    for b in ids:
        mods, trig = bugs[b]["mods"], set(bugs[b]["trigs"])
        tp = {pkg(t) for t in trig}
        if not tp: continue
        k = alias(mods)
        size[k] += 1
        for p in tp: cls[k][p] += 1
    return cls, size

def floor_of(cls, size):
    tot, pos, mx, per = 0, 0, 0, {}
    for k, n in size.items():
        best = max(cls[k].values()) if cls[k] else 0
        f = n - best
        per[k] = {"size": n, "best_action_catches": best, "floor": f}
        tot += f; pos += (f > 0); mx = max(mx, f)
    return tot, pos, mx, per

A_COARSE  = lambda mods: pkg(mods[0])
A_REFINED = lambda mods: (pkg(mods[0]), mods[0].split(".")[-1])

report = {"schema": "ORION22.REGRET_FLOOR_TRANSFER_D4J.v1", "split_seed": SEED,
          "interval_rule": "Clopper-Pearson 95% on the pooled floor rate, fixed in phase 1",
          "projects": {}}
tot_pred_n, tot_pred_f = 0, 0
for proj, bugs in sorted(d.items()):
    ids = sorted(bugs); r = random.Random(SEED); sh = ids[:]; r.shuffle(sh)
    h = len(sh)//2
    pred_ids, prot_ids = sorted(sh[:h]), sorted(sh[h:])
    cP, sP = build(bugs, pred_ids, A_COARSE)
    if not sP: continue
    tP, pP, mP, perP = floor_of(cP, sP)
    cPr, sPr = build(bugs, pred_ids, A_REFINED)
    tPr, _, _, _ = floor_of(cPr, sPr)
    n = sum(sP.values())
    report["projects"][proj] = {
        "prediction_half": {"bugs_used": n, "classes": len(sP), "total_floor": tP,
                            "positive_regret_classes": pP, "max_class_floor": mP,
                            "floor_rate": round(tP/n, 6) if n else None,
                            "refined_total_floor": tPr,
                            "predicted_refinement_reduction": tP - tPr},
        "excluded_no_trigger_pkg": len(pred_ids) - n,
    }
    tot_pred_n += n; tot_pred_f += tP

lo, hi = cp(tot_pred_f, tot_pred_n, True), cp(tot_pred_f, tot_pred_n, False)
report["pooled_prediction"] = {"bugs": tot_pred_n, "floor": tot_pred_f,
                               "floor_rate": round(tot_pred_f/tot_pred_n, 6),
                               "cp95_lo": round(lo, 6), "cp95_hi": round(hi, 6)}
pf = OUT + "PREDICTIONS_V1.json"
with open(pf, "w") as fh: json.dump(report, fh, indent=1, sort_keys=True); fh.write("\n")
dig = hashlib.sha256(open(pf, "rb").read()).hexdigest()
print(f"PHASE 1 written: {pf}\n  sha256 {dig}")
print(f"  pooled prediction: floor {tot_pred_f}/{tot_pred_n} = {tot_pred_f/tot_pred_n:.4f}"
      f"  CP95 [{lo:.4f}, {hi:.4f}]")

# ---------- phase 2: protected ----------
res = {"schema": "ORION22.REGRET_FLOOR_TRANSFER_D4J.v1.protected",
       "predictions_sha256": dig, "projects": {}}
tn, tf, tfr = 0, 0, 0
viol_mono, viol_exact, zero_cls, pos_cls = [], [], 0, 0
for proj, bugs in sorted(d.items()):
    if proj not in report["projects"]: continue
    ids = sorted(bugs); r = random.Random(SEED); sh = ids[:]; r.shuffle(sh)
    prot = sorted(sh[len(sh)//2:])
    c, s = build(bugs, prot, A_COARSE)
    if not s: continue
    t, p, m, per = floor_of(c, s)
    cr, sr = build(bugs, prot, A_REFINED)
    tr, _, _, perr = floor_of(cr, sr)
    # per-class: refinement must be non-increasing, and strictly decrease exactly
    # on classes whose refined sub-classes disagree about the best action.
    sub = defaultdict(list)
    for (cf, cn) in sr: sub[cf].append((cf, cn))
    for k in s:
        base = per[k]["floor"]
        ref = sum(perr[x]["floor"] for x in sub.get(k, []))
        # A fibre is action-impure exactly when its parts share NO optimal action.
        # Comparing one argmax per part is wrong: a part with several tied optima
        # would be reported as disagreeing with a part that shares one of them.
        optsets = []
        for x in sub.get(k, []):
            if not cr[x]: continue
            mx = max(cr[x].values())
            optsets.append({a for a, v in cr[x].items() if v == mx})
        common = set.intersection(*optsets) if optsets else set()
        disagree = len(optsets) > 1 and not common
        acts = common
        if ref > base: viol_mono.append({"proj": proj, "class": str(k), "base": base, "refined": ref})
        strict = ref < base
        if strict != disagree:
            viol_exact.append({"proj": proj, "class": str(k), "base": base,
                               "refined": ref, "common_optimal_actions": sorted(map(str, acts))})
        zero_cls += (base == 0); pos_cls += (base > 0)
    # strongest heuristic: schedule the test package whose name best matches the
    # modified class's package. No outcome statistics.
    hreg = 0
    for b in prot:
        trig = {pkg(t) for t in bugs[b]["trigs"]}
        if not trig: continue
        mp = pkg(bugs[b]["mods"][0])
        univ = {pkg(t) for t in bugs[b]["rels"]} | trig
        def score(q):
            a, bb = mp.split("."), q.split(".")
            i = 0
            while i < min(len(a), len(bb)) and a[i] == bb[i]: i += 1
            return (i, -len(bb))
        pick = max(univ, key=lambda q: (score(q), q)) if univ else None
        hreg += 0 if pick in trig else 1
    res["projects"][proj] = {"bugs_used": sum(s.values()), "classes": len(s),
                             "total_floor": t, "positive_regret_classes": p,
                             "max_class_floor": m, "refined_total_floor": tr,
                             "refinement_reduction": t - tr, "heuristic_regret": hreg,
                             "oracle_regret": 0}
    tn += sum(s.values()); tf += t; tfr += tr

rate = tf / tn if tn else 0.0
inside = lo <= rate <= hi
res["pooled_protected"] = {"bugs": tn, "total_floor": tf, "floor_rate": round(rate, 6),
                           "refined_total_floor": tfr, "reduction": tf - tfr,
                           "predicted_cp95": [round(lo, 6), round(hi, 6)],
                           "inside_predicted_interval": inside}
res["monotonicity_violations"] = viol_mono
res["exactly_when_violations"] = viol_exact[:20]
res["exactly_when_violation_count"] = len(viol_exact)
res["zero_regret_classes"] = zero_cls
res["positive_regret_classes"] = pos_cls

if not (zero_cls and pos_cls):
    res["terminal"] = "CANNOT_CHECK_NO_CONTRAST"
elif viol_mono or viol_exact or not inside:
    res["terminal"] = "REGRET_FLOOR_LAW_FAILS_ON_D4J"
else:
    res["terminal"] = "REGRET_FLOOR_LAW_TRANSFERS"

with open(OUT + "RESULTS_V1.json", "w") as fh:
    json.dump(res, fh, indent=1, sort_keys=True); fh.write("\n")
print(f"\nPHASE 2 protected: floor {tf}/{tn} = {rate:.4f}  inside CP95 {inside}")
print(f"  refined {tfr}  reduction {tf-tfr}")
print(f"  zero-regret classes {zero_cls}  positive-regret classes {pos_cls}")
print(f"  monotonicity violations {len(viol_mono)}  exactly-when violations {len(viol_exact)}")
for p, v in sorted(res["projects"].items()):
    print(f"   {p:<12} n={v['bugs_used']:>3} cls={v['classes']:>3} floor={v['total_floor']:>3}"
          f" pos={v['positive_regret_classes']:>2} max={v['max_class_floor']:>3}"
          f" refined={v['refined_total_floor']:>3} heur={v['heuristic_regret']:>3}")
print(f"TERMINAL: {res['terminal']}")
