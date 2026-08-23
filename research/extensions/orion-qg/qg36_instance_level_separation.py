"""QG-36 probe: does the existence/selection separation survive at INSTANCE level?

QG-28: cost depends only on the 715-vector M of column-type multiplicities.
If a single frame must serve the whole instance (the shared-frame model), the
achievable cost is   min_p  sum_o M_o * K_p(o).
Question: is THAT determined by the aggregate bulk+spectrum summary?

If not, then at instance level not even EXISTENCE is free -- strictly stronger
than QG-35, which found existence free at the single-column level."""
import json, itertools
from collections import defaultdict
P=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=P["K"]; reps=P["reps"]; joint=P["joint"]; NP=P["n_probes"]; n=len(K)
def T(i): return "".join("IXYZ"[x] for x in reps[i])
cls_of={}
for ci,c in enumerate(joint):
    for o in c: cls_of[o]=ci

def shared_cost(inst):          # inst: list of type indices (with multiplicity)
    return min(sum(K[o][p] for o in inst) for p in range(NP))
def agg(inst):                  # the aggregate cheap summary: multiset of joint classes
    d=defaultdict(int)
    for o in inst: d[cls_of[o]]+=1
    return tuple(sorted(d.items()))

# search size-2 instances: same aggregate summary, different shared-frame cost
found=[]
for c in joint:
    if len(c)<2: continue
    for a,b in itertools.combinations(c,2):
        if cls_of[a]!=cls_of[b]: continue
        for x in range(n):
            if cls_of[x]!=cls_of[a]:      # keep the aggregate identical: x in a fixed class
                pass
            ia=[a,x]; ib=[b,x]
            if agg(ia)!=agg(ib): continue
            ca,cb=shared_cost(ia),shared_cost(ib)
            if ca!=cb:
                found.append((a,b,x,ca,cb)); break
        if found: break
    if found: break
print("size-2 instances with IDENTICAL aggregate bulk+spectrum summary but DIFFERENT")
print("shared-frame achievable cost:", "FOUND" if found else "none at size 2")
if found:
    a,b,x,ca,cb=found[0]
    print(f"  instance A = {{{T(a)}, {T(x)}}}   shared-frame optimum = {ca}")
    print(f"  instance B = {{{T(b)}, {T(x)}}}   shared-frame optimum = {cb}")
    print(f"  aggregate summaries identical: {agg([a,x])==agg([b,x])}")
    print(f"  per-column optima identical  : {min(K[a])}=={min(K[b])} and {min(K[x])}")
    print(f"  => the cheap summary determines every COLUMN's optimum yet not the INSTANCE's")
    # how common?
    cnt=0; tot=0
    for c2 in joint:
        if len(c2)<2: continue
        for a2,b2 in itertools.combinations(c2,2):
            for x2 in range(0,n,37):
                tot+=1
                if agg([a2,x2])==agg([b2,x2]) and shared_cost([a2,x2])!=shared_cost([b2,x2]): cnt+=1
    print(f"  sampled size-2 pairs where the summary fails: {cnt}/{tot}")
