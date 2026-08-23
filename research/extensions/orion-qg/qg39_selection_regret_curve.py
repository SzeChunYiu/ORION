"""QG-39 probe: what does the impossibility COST, in the cost model's own units?

A summary-only compiler sees the joint class, not the type, and must commit to a
frame.  Define worst-case REGRET with a probe budget k:

  regret of committing to p on state S :  max_{o in S} [ K_p(o) - min_q K_q(o) ]
  R_0(S) = min_p (that)
  R_k(S) = min( R_0-style commit ,  min_p max_v R_{k-1}(S_v) )

R_k* = max over the 92 initial joint classes.  R_k = 0 means the budget suffices
to always pick an optimal frame."""
import json
from collections import defaultdict
P=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=P["K"]; joint=P["joint"]; NP=P["n_probes"]; n=len(K)
best=[min(K[i]) for i in range(n)]
def commit_regret(S):
    return min(max(K[o][p]-best[o] for o in S) for p in range(NP))
def commit_regret_mean(S):
    return min(sum(K[o][p]-best[o] for o in S)/len(S) for p in range(NP))
def parts(S):
    seen=set()
    for p in range(NP):
        g=defaultdict(list)
        for o in S: g[K[o][p]].append(o)
        if len(g)>1: seen.add(tuple(sorted(tuple(v) for v in g.values())))
    return seen
memo={}
def R(S,k):
    S=tuple(sorted(S))
    if len(S)==1: return 0
    key=(S,k)
    if key in memo: return memo[key]
    v=commit_regret(S)
    if k>0 and v>0:
        for blocks in parts(S):
            w=max(R(b,k-1) for b in blocks)
            if w<v: v=w
            if v==0: break
    memo[key]=v; return v
print("worst-case regret of frame choice, by probe budget (cost-model units):")
rows=[]
for k in range(0,4):
    vals=[R(tuple(c),k) for c in joint]
    rows.append(vals)
    nz=sum(1 for v in vals if v>0)
    print(f"  budget {k} probes:  worst-case regret over all 92 classes = {max(vals)}"
          f"   classes with nonzero regret: {nz}/92")
print()
print("per-class regret histogram at budget 0 (summary only):",
      dict(sorted(__import__('collections').Counter(rows[0]).items())))
# scale reference: what is the spread of achievable cost at all?
allK=[v for row in K for v in row]
print()
print(f"cost-model scale reference: K ranges over [{min(allK)}, {max(allK)}]"
      f"; optimal values min_p K_p(o) range over [{min(best)}, {max(best)}]")
mean0=max(commit_regret_mean(tuple(c)) for c in joint)
print(f"worst-class MEAN regret at budget 0: {mean0:.4f}")
json.dump({"worst_case_regret_by_budget":{str(k):max(rows[k]) for k in range(4)},
           "classes_with_nonzero_regret":{str(k):sum(1 for v in rows[k] if v>0) for k in range(4)},
           "K_range":[min(allK),max(allK)],"optimal_value_range":[min(best),max(best)],
           "worst_class_mean_regret_budget0":mean0}, open("/tmp/regret.json","w"), indent=2)
