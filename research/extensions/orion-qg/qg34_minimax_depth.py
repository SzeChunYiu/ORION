"""QG-34 exact minimax adaptive probe depth over the 92 joint classes.
Bellman recursion D(S) = 1 + min_p max_v D(S_v), D(singleton) = 0."""
import json, sys
from collections import defaultdict
sys.setrecursionlimit(100000)
P = json.load(open("primitives.json"))
K = P["K"]; NP = P["n_probes"]; joint = P["joint"]

def partitions_on(S):
    """distinct partitions of S induced by the 384 probes, dedup'd, each as a
    tuple of blocks; only probes that actually split S are kept."""
    seen = {}
    for p in range(NP):
        g = defaultdict(list)
        for o in S: g[K[o][p]].append(o)
        if len(g) == 1: continue
        blocks = tuple(sorted(tuple(v) for v in g.values()))
        if blocks not in seen: seen[blocks] = p
    return seen

def max_arity(S):
    a = 1
    for p in range(NP):
        a = max(a, len({K[o][p] for o in S}))
    return a

memo = {}
def feasible(S, d):
    if len(S) <= 1: return True
    if d <= 0: return False
    key = (S, d)
    if key in memo: return memo[key]
    parts = partitions_on(S)
    if not parts: memo[key] = False; return False
    a = max(len(b) for b in parts)          # best available arity
    if a ** d < len(S): memo[key] = False; return False
    order = sorted(parts, key=lambda b: (max(len(x) for x in b), -len(b)))
    for blocks in order:
        if all(feasible(b, d - 1) for b in blocks):
            memo[key] = True; return True
    memo[key] = False; return False

def depth(S):
    if len(S) <= 1: return 0
    d = 1
    while d <= 12:
        if feasible(S, d): return d
        d += 1
    return None

import math
rows = []
for cls in joint:
    S = tuple(sorted(cls))
    a = max_arity(S) if len(S) > 1 else 1
    lb = 0 if len(S) <= 1 else math.ceil(math.log(len(S), a)) if a > 1 else None
    d = depth(S)
    rows.append({"size": len(S), "max_arity": a, "arity_lower_bound": lb, "depth": d,
                 "lb_tight": (lb == d) if (lb is not None and d is not None) else None})
    print(f"class size {len(S):>3}  arity {a:>3}  lb {lb}  D = {d}", flush=True)
Dstar = max(r["depth"] for r in rows)
worst = [r for r in rows if r["depth"] == Dstar]
print()
print("D_* =", Dstar)
print("classes attaining D_*:", len(worst), "sizes:", sorted({r['size'] for r in worst}))
print("arity lower bound tight on", sum(1 for r in rows if r["lb_tight"]), "of", len(rows), "classes")
json.dump({"D_star": Dstar, "rows": rows,
           "classes_attaining_D_star": len(worst),
           "memo_states": len(memo)}, open("qg34_depths.json","w"), indent=2)
