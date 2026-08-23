import sys, json, itertools
from collections import defaultdict
import numpy as np
OUT="/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/broadclass"
D=np.load(f"{OUT}/sixlcu_prims.npz"); M=json.load(open(f"{OUT}/sixlcu_meta.json"))
K=D["K"]; canonL=D["canonL"]; canonF=D["canonF"]; A=D["A"]
CHOICES=[(pi,tuple(phi)) for pi,phi in M["choices"]]; PARTS=[tuple(tuple(b) for b in p) for p in M["parts"]]
CS=M["const_shared"]; CD=M["const_dedicated"]; n,NC=K.shape
def T(i): return "".join("IXYZ"[x] for x in A[i])
print(f"types={n} choices={NC}   shared<=dedicated for every partition: {all(a<=b for a,b in zip(CS,CD))}")
print("  -> the `shared` degree of freedom is DEGENERATE: shared=True is optimal for all 203 partitions.\n")

best=K.min(axis=1); argmin=[frozenset(np.flatnonzero(K[i]==best[i]).tolist()) for i in range(n)]
spec=[np.sort(K[i]).tobytes() for i in range(n)]
resp=[K[i].tobytes() for i in range(n)]
SHAPE=[tuple(sorted((len(b) for b in PARTS[pi]),reverse=True)) for pi,_ in CHOICES]
PARTOF=[pi for pi,_ in CHOICES]

def nclass(keys): return len(set(keys))
print("=== TOWER (SixLCU) ===  cf TARE 4096 -> 715 -> 54")
print(f"  4096 types -> {nclass(resp)} distinct indexed response vectors -> {nclass(spec)} spectrum classes")
print(f"  letter-orbits (S_3) = {nclass(canonL.tolist())}; full orbits (S_3xS_6) = {nclass(canonF.tolist())}")
print(f"  response vector constant on letter-orbits: {all(len({resp[i] for i in g})==1 for g in _g0) if (_g0:=[np.flatnonzero(canonL==c).tolist() for c in set(canonL.tolist())]) else '?'}")
print(f"  spectrum constant on full orbits         : {all(len({spec[i] for i in g})==1 for g in [np.flatnonzero(canonF==c).tolist() for c in set(canonF.tolist())])}")
print(f"  => spectrum partition == orbit partition (C1 analogue): {nclass(spec)==nclass(canonF.tolist())}\n")

# ---- bulk definitions ----
sup=[tuple((A[i]!=0).astype(int).tolist()) for i in range(n)]
UN=[c for c,(pi,phi) in enumerate(CHOICES) if PARTS[pi]==tuple((j,) for j in range(6))]
BI=[c for c,(pi,phi) in enumerate(CHOICES) if PARTS[pi]==(tuple(range(6)),)]
bulks={"A support pattern (6 bits)":[sup[i] for i in range(n)],
       "B distinguished unary+binary responses":[tuple(K[i][UN+BI].tolist()) for i in range(n)],
       "C = A + B":[(sup[i],tuple(K[i][UN+BI].tolist())) for i in range(n)]}
def blocks(keys):
    d=defaultdict(list)
    for i,k in enumerate(keys): d[k].append(i)
    return list(d.values())
def split(pred,bl): return [b for b in bl if len({pred[i] for i in b})>1]

print("=== JOINT SUMMARIES and BOTH HALVES ===")
res={}
for bn,bv in bulks.items():
    joint=blocks([(bv[i],spec[i]) for i in range(n)])
    ex={"min cost (achievable optimum)":[int(best[i]) for i in range(n)],
        "|argmin| (number of optimal choices)":[len(argmin[i]) for i in range(n)],
        "full multiset of achievable costs":[spec[i] for i in range(n)]}
    for thr in range(0,13,4): ex[f"improvement available at level {thr}"]=[bool(best[i]<=thr) for i in range(n)]
    sel={"optimal-CHOICE set (part,phi)":[argmin[i] for i in range(n)],
         "optimal-PARTITION set":[frozenset(PARTOF[c] for c in argmin[i]) for i in range(n)],
         "lexicographically first optimal choice":[min(argmin[i]) for i in range(n)],
         "optimal-SHAPE set  <-- symmetry-blind":[frozenset(SHAPE[c] for c in argmin[i]) for i in range(n)]}
    print(f"\n-- bulk = {bn}   ({nclass(bv)} bulk classes, {len(joint)} joint classes)")
    print("   EXISTENCE half:")
    for k,v in ex.items(): print(f"     {k:44s} split {len(split(v,joint)):3d}  {'DETERMINED' if not split(v,joint) else 'NOT'}")
    print("   SELECTION half:")
    for k,v in sel.items(): print(f"     {k:44s} split {len(split(v,joint)):3d}  {'DETERMINED' if not split(v,joint) else 'NOT'}")
    res[bn]={"bulk_classes":nclass(bv),"joint_classes":len(joint),
        "existence_all_determined":all(not split(v,joint) for v in ex.values()),
        "selection_choice_split":len(split(sel["optimal-CHOICE set (part,phi)"],joint)),
        "selection_shape_split":len(split(sel["optimal-SHAPE set  <-- symmetry-blind"],joint)),
        "types_in_split_classes":sum(len(b) for b in split(sel["optimal-CHOICE set (part,phi)"],joint))}

# ---- witnesses under the FINEST bulk (C) ----
jointC=blocks([(bulks["C = A + B"][i],spec[i]) for i in range(n)])
wits=[]
for b in jointC:
    for a,c in itertools.combinations(b,2):
        if argmin[a]!=argmin[c] and best[a]==best[c]:
            wits.append((a,c,len(b),int(best[a]),len(argmin[a]&argmin[c]))); break
print(f"\n=== WITNESSES (finest bulk C: identical support, identical distinguished responses, identical spectrum) ===")
print(f"witness pairs: {len(wits)}")
for a,c,sz,v,sh in wits[:6]:
    print(f"  {T(a)} vs {T(c)}  class size {sz}, both optimal value {v}, |argmin| {len(argmin[a])}/{len(argmin[c])}, shared optimal choices {sh}")
    print(f"      opt shapes: {sorted({SHAPE[x] for x in argmin[a]})} vs {sorted({SHAPE[x] for x in argmin[c]})}")
# advisor's suggested pair
p1=int(np.flatnonzero((A==np.array([1,1,2,2,3,3])).all(axis=1))[0]); p2=int(np.flatnonzero((A==np.array([1,2,1,2,3,3])).all(axis=1))[0])
print(f"\n  suggested pair {T(p1)} vs {T(p2)}: same spectrum {spec[p1]==spec[p2]}, same bulkC {bulks['C = A + B'][p1]==bulks['C = A + B'][p2]},")
print(f"      argmin equal {argmin[p1]==argmin[p2]}, shared optimal choices {len(argmin[p1]&argmin[p2])}, opt value {int(best[p1])}/{int(best[p2])}")
print(f"      optimal partitions: {sorted(frozenset(PARTOF[c] for c in argmin[p1]))[:6]} vs {sorted(frozenset(PARTOF[c] for c in argmin[p2]))[:6]}")
json.dump(res,open(f"{OUT}/analysis.json","w"),indent=2,default=str)
