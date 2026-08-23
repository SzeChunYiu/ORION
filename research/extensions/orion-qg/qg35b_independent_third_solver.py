"""Independent third implementation of D_sel and D_act (iterative deepening on
sorted tuples), checking the two headline claims rather than trusting the pair."""
import json, sys
from collections import Counter
P=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=P["K"]; joint=P["joint"]; NP=P["n_probes"]; n=len(K)
best=[min(K[i]) for i in range(n)]
argmin=[frozenset(p for p in range(NP) if K[i][p]==best[i]) for i in range(n)]
def term_id(S):  return len(S)<=1
def term_sel(S): return len({argmin[o] for o in S})==1
def term_act(S):
    c=argmin[S[0]]
    for o in S[1:]:
        c=c&argmin[o]
        if not c: return False
    return bool(c)
def parts(S):
    seen=set()
    for p in range(NP):
        g={}
        for o in S: g.setdefault(K[o][p],[]).append(o)
        if len(g)==1: continue
        seen.add(tuple(sorted(tuple(v) for v in g.values())))
    return seen
def feas(S, term, cap, memo):
    """can this state be resolved within `cap` probes?  (D_act <= D_sel <= D_id
    holds because singletons are terminal for all three, so cap=3 is sound)"""
    S=tuple(sorted(S))
    if term(S): return True
    if cap<=0: return False
    key=(S,cap)
    if key in memo: return memo[key]
    for blocks in sorted(parts(S), key=lambda b: max(len(x) for x in b)):
        if all(feas(b,term,cap-1,memo) for b in blocks):
            memo[key]=True; return True
    memo[key]=False; return False
def depth(S, term, memo):
    for d in range(0,4):
        if feas(S,term,d,memo): return d
    return 99
res={}
for name,term in (("identification",term_id),("selection",term_sel),("actionable",term_act)):
    memo={}
    ds=[depth(tuple(c),term,memo) for c in joint]
    res[name]=ds
    print(f"{name:15s} D* = {max(ds)}  worst-class count = {sum(1 for d in ds if d==max(ds)):2d}  histogram = {dict(sorted(Counter(ds).items()))}")
ident,sel,act=res["identification"],res["selection"],res["actionable"]
print()
print("selection == identification on all 92 classes :", ident==sel)
print("actionable strictly cheaper than identification on:",
      sum(1 for a,b in zip(act,ident) if a<b), "of 92 classes")
print("actionable ever MORE expensive (must be 0)    :", sum(1 for a,b in zip(act,ident) if a>b))
