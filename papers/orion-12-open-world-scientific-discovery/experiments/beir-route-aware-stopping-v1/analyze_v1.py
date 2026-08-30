#!/usr/bin/env python3
"""Score the ORION-12 BEIR run against the predeclared conditions. No tuning."""
import json, os
r = json.load(open(os.path.expanduser("~/beir/RESULTS_V1.json")))
C = r["corpora"]; D = [str(d) for d in r["depths"]]

def curve(c, arm):  # (cost, recall) ascending by cost
    return sorted(((C[c]["by_depth"][d][arm]["cost"], C[c]["by_depth"][d][arm]["recall"]) for d in D))

def interp_recall(cur, cost):
    if cost <= cur[0][0]: return cur[0][1]
    if cost >= cur[-1][0]: return cur[-1][1]
    for i in range(1, len(cur)):
        if cur[i][0] >= cost:
            (x0,y0),(x1,y1) = cur[i-1], cur[i]
            return y0 + (y1-y0)*(cost-x0)/max(x1-x0, 1e-9)
    return cur[-1][1]

def interp_cost(cur, rec):   # cheapest cost reaching recall
    for i in range(len(cur)):
        if cur[i][1] >= rec:
            if i == 0: return cur[0][0]
            (x0,y0),(x1,y1) = cur[i-1], cur[i]
            return x0 + (x1-x0)*(rec-y0)/max(y1-y0, 1e-9)
    return None

print(f"{'corpus':<10}{'depth':>6}  {'ras_r':>7}{'ras_c':>7}  {'fus_r':>7}{'fus_c':>7}  "
      f"{'fus_r@ras_c':>12}  {'d_recall':>9}  {'fus_c@ras_r':>12}  {'cheaper':>8}")
rows = []
for c in C:
    fus, ras = curve(c, "fusion"), curve(c, "route_aware_stop")
    for d in D:
        a = C[c]["by_depth"][d]
        rr, rc = a["route_aware_stop"]["recall"], a["route_aware_stop"]["cost"]
        fr, fc = a["fusion"]["recall"], a["fusion"]["cost"]
        f_at = interp_recall(fus, rc)
        c_at = interp_cost(fus, rr)
        cheaper = (c_at is not None and rc < c_at)
        rows.append({"corpus": c, "depth": d, "ras_recall": rr, "ras_cost": rc,
                     "fusion_recall_at_ras_cost": round(f_at, 4),
                     "recall_deficit": round(f_at - rr, 4),
                     "fusion_cost_at_ras_recall": (round(c_at,1) if c_at else None),
                     "ras_cheaper_at_matched_recall": cheaper,
                     "ras_fc": a["route_aware_stop"]["false_complete_rate"],
                     "ga_fc": a["generic_active"]["false_complete_rate"]})
        print(f"{c:<10}{d:>6}  {rr:>7.3f}{rc:>7.0f}  {fr:>7.3f}{fc:>7.0f}  {f_at:>12.3f}  "
              f"{f_at-rr:>+9.3f}  {str(c_at if c_at is None else round(c_at,1)):>12}  {str(cheaper):>8}")

worst_def = max(x["recall_deficit"] for x in rows)
c1 = worst_def <= 0.02
fc_gaps = [(x["ras_fc"] - x["ga_fc"]) for x in rows if x["ras_fc"] is not None and x["ga_fc"] is not None]
c2 = (max(fc_gaps) <= 0.02) if fc_gaps else None
c3 = all(x["ras_cheaper_at_matched_recall"] for x in rows)
jac = {c: C[c]["mean_pairwise_jaccard_at100"] for c in C}
hetero = any(v < 0.9 for v in jac.values())

print(f"\nmean pairwise Jaccard@100 per corpus: {jac}")
print(f"C1 recall within 0.02 of fusion at equal cost : {c1}  (worst deficit {worst_def:+.4f})")
print(f"C2 false-complete no worse than generic +0.02 : {c2}  (worst gap {max(fc_gaps):+.4f})")
print(f"C3 strictly cheaper at matched recall         : {c3}  "
      f"({sum(x['ras_cheaper_at_matched_recall'] for x in rows)}/{len(rows)} cells)")
term = ("CANNOT_CHECK_INSUFFICIENT_ROUTE_HETEROGENEITY" if not hetero
        else "ROUTE_AWARE_STOPPING_SUPPORTED_ON_FRESH_CORPORA" if (c1 and c2 and c3)
        else "ROUTE_AWARE_STOPPING_NOT_SUPPORTED")
print(f"TERMINAL: {term}")
out = {"schema": "ORION12.BEIR_ROUTE_AWARE_STOPPING.v1.analysis", "cells": rows,
       "jaccard": jac, "route_heterogeneity_ok": hetero,
       "C1_recall_within_0.02": c1, "worst_recall_deficit": round(worst_def, 4),
       "C2_false_complete_within_0.02": c2, "worst_fc_gap": round(max(fc_gaps), 4),
       "C3_cheaper_at_matched_recall": c3, "terminal": term}
json.dump(out, open(os.path.expanduser("~/beir/ANALYSIS_V1.json"), "w"), indent=1, sort_keys=True)
