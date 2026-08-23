"""Solver B: INDEPENDENT re-derivation.
 - state encoding: integer BITMASK over 715 type ids (solver A used sorted tuples)
 - terminal predicate INDEPENDENTLY written: precomputed block_id[] array, test
   len({block_id[o]}) == 1   (solver A tested frozenset equality of argmin directly)
 - search: exact value recursion with best-first probe ordering + branch-and-bound
   (solver A used iterative-deepening feasibility)
 - NOTE per freeze pin P7: state space stays sets of TYPES; we never quotient the
   dynamics to block ids -- block_id is used ONLY inside the stopping test."""
import json, sys
D="/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/descaudit"
P=json.load(open(D+"/primitives_regen.json"))
K=P["K"]; NP=P["n_probes"]; n=len(K); joint=P["joint"]
MODE=sys.argv[1] if len(sys.argv)>1 else "sel"

best=[min(r) for r in K]
amin=[tuple(sorted(p for p in range(NP) if K[i][p]==best[i])) for i in range(n)]
uniq={}; block_id=[]
for a in amin:
    if a not in uniq: uniq[a]=len(uniq)
    block_id.append(uniq[a])
# independent frame-membership bitsets for the ACT test
frame_mask=[0]*n
for i,a in enumerate(amin):
    m=0
    for p in a: m |= (1<<p)
    frame_mask[i]=m

def bits(mask):
    out=[]
    while mask:
        b=mask & -mask; out.append(b.bit_length()-1); mask^=b
    return out

def is_terminal(mask):
    e=bits(mask)
    if MODE=="sel":
        return len({block_id[o] for o in e})==1
    c=frame_mask[e[0]]
    for o in e[1:]:
        c &= frame_mask[o]
        if c==0: return False
    return c!=0

memo={}
def value(mask, cap):
    """exact depth if <= cap else cap+1"""
    if is_terminal(mask): return 0
    if cap<=0: return 1
    if (mask,cap) in memo: return memo[(mask,cap)]
    e=bits(mask); bestv=cap+1
    cand=[]
    for p in range(NP):
        g={}
        for o in e: g[K[o][p]]=g.get(K[o][p],0)|(1<<o)
        if len(g)>1: cand.append((-len(g), max(bin(x).count('1') for x in g.values()), tuple(g.values())))
    cand.sort()
    for _,_,blocks in cand:
        w=0
        for b in blocks:
            w=max(w, value(b, bestv-2 if bestv-2>=0 else 0))
            if w+1>=bestv: break
        if w+1<bestv: bestv=w+1
        if bestv==1: break
    memo[(mask,cap)]=bestv; return bestv

rows=[]
for c in joint:
    mask=0
    for o in c: mask|=(1<<o)
    v=value(mask,6)
    rows.append({"first":min(c),"size":len(c),"D":v})
Dstar=max(r["D"] for r in rows)
import collections
print(f"MODE={MODE}  SOLVER B  D*={Dstar}")
print(" depth histogram:", dict(sorted(collections.Counter(r['D'] for r in rows).items())))
json.dump({"mode":MODE,"D_star":Dstar,"rows":rows}, open(D+f"/solverB_{MODE}.json","w"), indent=1)
