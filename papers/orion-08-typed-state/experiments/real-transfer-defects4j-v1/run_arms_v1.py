#!/usr/bin/env python3
"""ORION-08 D4J: the full registered arm set and oracle-gap capture.

Arms named by #1701: coarse; strongest deterministic proxy; generic
acquisition/info-gain; typed binding; oracle.
"""
from __future__ import annotations
import json, math, os, random
from collections import defaultdict

U = {(1, 1): 1.0, (1, 0): -0.05, (0, 1): -1.0, (0, 0): 0.0}
TH = 0.05 / 2.05
SEED = 20260830
d = json.load(open(os.path.expanduser("~/d4j_data.json")))

def pkg(f): return ".".join(f.split(".")[:-1])
def nm(mods, t):
    ts = t.split(".")[-1]; s = {m.split(".")[-1] for m in mods}
    if any(ts == x + "Test" or ts == "Test" + x for x in s): return "exact"
    if any(x and x in ts for x in s): return "prefix"
    return "none"
def opt(v): return 1 if (sum(v) / len(v)) > TH else 0

def mi(rows, keyfn):
    """Mutual information between a candidate feature and catch, in bits."""
    n = len(rows); joint = defaultdict(int); px = defaultdict(int); py = defaultdict(int)
    for k, c in rows:
        joint[(k, c)] += 1; px[k] += 1; py[c] += 1
    tot = 0.0
    for (k, c), v in joint.items():
        p = v / n; a = px[k] / n; b = py[c] / n
        if p > 0 and a > 0 and b > 0: tot += p * math.log2(p / (a * b))
    return tot

out = {}
for proj, bugs in sorted(d.items()):
    ids = sorted(bugs); r = random.Random(SEED); sh = ids[:]; r.shuffle(sh)
    tr = sorted(sh[:len(sh) // 2])
    T = sorted({t for b in tr for t in bugs[b]["rels"]})
    if not T: continue
    rows = []           # (coarse, name_match, catch)
    for b in tr:
        mods = bugs[b]["mods"]; trig = set(bugs[b]["trigs"])
        for t in T: rows.append((pkg(t), nm(mods, t), 1 if t in trig else 0))

    def regret_and_cost(action_of):
        tot, n, runs = 0.0, 0, 0
        for cf, nmv, c in rows:
            a = action_of(cf, nmv, c)
            tot += U[(c, c)] - U[(a, c)]; n += 1; runs += a
        return tot / n, runs / n

    # coarse
    A = defaultdict(list)
    for cf, _, c in rows: A[cf].append(c)
    a_co = {k: opt(v) for k, v in A.items()}
    # typed
    B = defaultdict(list)
    for cf, nmv, c in rows: B[(cf, nmv)].append(c)
    a_ty = {k: opt(v) for k, v in B.items()}
    # deterministic proxy: run iff the test names the changed class. No statistics.
    # generic info-gain: refine coarse on whichever single feature carries most MI
    #   with catch, chosen without reference to the theorem's impurity criterion.
    cand = {"name_match": [( x[1], x[2]) for x in rows],
            "coarse_pkg":  [(x[0], x[2]) for x in rows]}
    mis = {k: mi(v, None) for k, v in cand.items()}
    pick = max(mis, key=lambda k: (mis[k], k))
    if pick == "name_match":
        C = defaultdict(list)
        for _, nmv, c in rows: C[nmv].append(c)
        a_ig = {k: opt(v) for k, v in C.items()}
        ig = lambda cf, nmv, c: a_ig[nmv]
    else:
        ig = lambda cf, nmv, c: a_co[cf]

    res = {}
    res["coarse"]        = regret_and_cost(lambda cf, nmv, c: a_co[cf])
    res["det_proxy"]     = regret_and_cost(lambda cf, nmv, c: 1 if nmv == "exact" else 0)
    res["info_gain"]     = regret_and_cost(ig)
    res["typed"]         = regret_and_cost(lambda cf, nmv, c: a_ty[(cf, nmv)])
    res["oracle"]        = regret_and_cost(lambda cf, nmv, c: c)

    r_co = res["coarse"][0]; r_or = res["oracle"][0]
    span = r_co - r_or
    out[proj] = {
        "mi_bits": {k: round(v, 5) for k, v in mis.items()}, "info_gain_feature": pick,
        "arms": {k: {"regret": round(v[0], 6), "run_rate": round(v[1], 4),
                     "oracle_gap_captured": (round((r_co - v[0]) / span, 4) if span > 1e-12 else None)}
                 for k, v in res.items()},
    }

print(f"{'proj':<12}{'coarse':>9}{'det_prox':>9}{'infogain':>9}{'typed':>9}{'oracle':>8}   typed_gap  typed_runrate")
for p, v in out.items():
    a = v["arms"]
    g = a["typed"]["oracle_gap_captured"]
    print(f"{p:<12}{a['coarse']['regret']:>9.4f}{a['det_proxy']['regret']:>9.4f}"
          f"{a['info_gain']['regret']:>9.4f}{a['typed']['regret']:>9.4f}{a['oracle']['regret']:>8.4f}"
          f"   {'n/a' if g is None else f'{g:.3f}':>8}   {a['typed']['run_rate']:.3f}")
json.dump(out, open(os.path.expanduser("~/d4j_ARMS_V1.json"), "w"), indent=1, sort_keys=True)
gaps = [v["arms"]["typed"]["oracle_gap_captured"] for v in out.values() if v["arms"]["typed"]["oracle_gap_captured"] is not None]
print(f"\ntyped captures {min(gaps):.3f}-{max(gaps):.3f} of the oracle gap (mean {sum(gaps)/len(gaps):.3f})")
beat = sum(1 for v in out.values() if v["arms"]["typed"]["regret"] <= v["arms"]["det_proxy"]["regret"] + 1e-12)
beat2 = sum(1 for v in out.values() if v["arms"]["typed"]["regret"] <= v["arms"]["info_gain"]["regret"] + 1e-12)
print(f"typed <= det_proxy on {beat}/{len(out)}; typed <= info_gain on {beat2}/{len(out)}")
