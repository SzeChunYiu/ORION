"""Instance level = the NATIVE SixLCU question (full_sweep picks ONE (part,phi,shared) per instance).
QG-36 analogue: is the instance's achievable cost determined by the aggregate cheap summary?"""
import sys, json, itertools, random
from collections import defaultdict
import numpy as np
sys.path.insert(0,"/Users/billy/Desktop/projects/ORION-claude/research/extensions/orion-qg")
import qg4_second_family as qg4
OUT="/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/broadclass"
D=np.load(f"{OUT}/sixlcu_prims.npz"); M=json.load(open(f"{OUT}/sixlcu_meta.json"))
K=D["K"].astype(np.int32); A=D["A"]; CHOICES=[(pi,tuple(phi)) for pi,phi in M["choices"]]
CS=M["const_shared"]; PARTOF=np.array([pi for pi,_ in CHOICES])
CONSTV=np.array([CS[pi] for pi in PARTOF],dtype=np.int32); n,NC=K.shape
def T(i): return "".join("IXYZ"[x] for x in A[i])
COLS=[tuple(A[i]) for i in range(n)]; COL_INDEX={c:i for i,c in enumerate(COLS)}

def inst_cost(idxs):   # min over (part,phi); shared=True always optimal
    return int((K[list(idxs)].sum(axis=0)+CONSTV).min())

# ---- V4: instance cost vs qg4.full_sweep (the family's own exact referee) ----
random.seed(3); bad=0
for _ in range(30):
    nq=random.randint(1,3); codes=[random.randrange(4**nq) for _ in range(6)]
    cols=[COL_INDEX[tuple((codes[i]>>(2*q))&3 for i in range(6))] for q in range(nq)]
    bad += (qg4.full_sweep(codes,nq)!=inst_cost(cols))
print(f"V4 instance cost vs qg4.full_sweep: {bad} mismatches / 30\n")

best=K.min(axis=1); spec=[np.sort(K[i]).tobytes() for i in range(n)]
sup=[tuple((A[i]!=0).astype(int).tolist()) for i in range(n)]
UN=[c for c,(pi,_) in enumerate(CHOICES) if len(M["parts"][pi])==6]
BI=[c for c,(pi,_) in enumerate(CHOICES) if len(M["parts"][pi])==1]
jkey=[(sup[i],tuple(K[i][UN+BI].tolist()),spec[i]) for i in range(n)]
cls_of={}; 
for ci,(k,g) in enumerate(((k,g) for k,g in ((k,[i for i in range(n) if jkey[i]==k]) for k in dict.fromkeys(jkey)))): pass
byk=defaultdict(list)
for i in range(n): byk[jkey[i]].append(i)
for ci,(k,g) in enumerate(byk.items()):
    for i in g: cls_of[i]=ci
print(f"aggregate summary = multiset of per-column joint classes ({len(byk)} classes)")

# ---- size-2 instances: identical aggregate summary, different achievable cost ----
found=[]; tot=0; cnt=0
random.seed(4)
for k,g in byk.items():
    if len(g)<2: continue
    for a,b in itertools.combinations(g,2):
        for x in random.sample(range(n),40):
            tot+=1
            ca,cb=inst_cost([a,x]),inst_cost([b,x])
            if ca!=cb:
                cnt+=1
                if len(found)<6: found.append((a,b,x,ca,cb))
print(f"size-2 probes: {cnt}/{tot} pairs where identical aggregate summary gives DIFFERENT achievable cost")
print("EXISTENCE at instance level:", "NOT DETERMINED" if found else "determined in this search")
for a,b,x,ca,cb in found[:4]:
    print(f"  A={{{T(a)},{T(x)}}} cost {ca}   vs   B={{{T(b)},{T(x)}}} cost {cb}")
    print(f"     per-column optima identical: {int(best[a])}=={int(best[b])} (and {int(best[x])}); same summary: {cls_of[a]==cls_of[b]}")
json.dump({"instance_existence_determined":not found,"failing_probe_pairs":cnt,"probes":tot,
  "witnesses":[{"A":[T(a),T(x)],"B":[T(b),T(x)],"costA":ca,"costB":cb} for a,b,x,ca,cb in found]},
  open(f"{OUT}/instance.json","w"),indent=2)
