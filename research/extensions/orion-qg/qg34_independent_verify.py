"""Independent re-derivation of QG-34's D_* with a different state encoding
(integer bitmasks over the 715 orbit ids, iterative bottom-up value table)
plus the d-1 infeasibility certificate and an explicit optimal tree witness."""
import json, math
from collections import defaultdict
P=json.load(open("primitives.json")); K=P["K"]; NP=P["n_probes"]; joint=P["joint"]

PCACHE={}
def arity_lb(mask, elems):
    """ceil(log_a n) with a the best available arity: an admissible lower bound"""
    n=mask.bit_count()
    if n<=1: return 0
    S=[o for o in elems if (mask>>o)&1]
    a=1
    for p in range(NP):
        a=max(a,len({K[o][p] for o in S}))
    return math.inf if a<2 else math.ceil(math.log(n,a)-1e-12)

def parts_mask(mask, elems):
    """distinct partitions of the set encoded by `mask`, as tuples of submasks"""
    if mask in PCACHE: return PCACHE[mask]
    S=[o for o in elems if (mask>>o)&1]
    out={}
    for p in range(NP):
        g=defaultdict(int)
        for o in S: g[K[o][p]] |= (1<<o)
        if len(g)==1: continue
        blocks=tuple(sorted(g.values()))
        out.setdefault(blocks,p)
    PCACHE[mask]=out
    return out

VAL={}
def val(mask, elems):
    """exact minimax depth of the state, computed bottom-up by popcount order"""
    if mask.bit_count()<=1: return 0
    if mask in VAL: return VAL[mask]
    pr=parts_mask(mask, elems)
    if not pr: VAL[mask]=math.inf; return math.inf
    lb=arity_lb(mask, elems)
    best=math.inf
    for blocks in sorted(pr, key=lambda b: max(x.bit_count() for x in b)):
        w=0
        for b in blocks:
            w=max(w, val(b, elems))
            if w+1>=best: break            # branch and bound
        if w+1<best: best=w+1
        if best<=lb: break                 # provably optimal, stop
    VAL[mask]=best; return best

rows=[]; worst=[]
for cls in joint:
    elems=cls; m=0
    for o in cls: m|=(1<<o)
    d=val(m, elems)
    rows.append({"size":len(cls),"depth":d})
    if len(cls)>1: worst.append((d,len(cls),m,tuple(elems)))
Dstar=max(r["depth"] for r in rows)
print("independent re-derivation: D_* =",Dstar)
prev=json.load(open("qg34_depths.json"))
agree = [r["depth"] for r in rows]==[r["depth"] for r in prev["rows"]]
print("per-class agreement with the recursive solver:",agree)

# d-1 infeasibility certificate on every worst class
biggest=[w for w in worst if w[0]==Dstar]
print("classes attaining D_* =",len(biggest))
def feasible_at(mask, elems, d):
    if mask.bit_count()<=1: return True
    if d<=0: return False
    pr=parts_mask(mask, elems)
    for blocks in pr:
        if all(feasible_at(b, elems, d-1) for b in blocks): return True
    return False
cert=all(not feasible_at(m, list(e), Dstar-1) for _,_,m,e in biggest)
print(f"infeasibility certificate at depth {Dstar-1} holds on ALL worst classes:",cert)

# explicit optimal tree witness for the largest worst class
d,sz,m,elems=max(biggest,key=lambda w:w[1])
def build(mask, elems, d):
    if mask.bit_count()<=1: return {"leaf":[o for o in elems if (mask>>o)&1]}
    pr=parts_mask(mask, elems)
    for blocks,p in sorted(pr.items(), key=lambda kv: max(x.bit_count() for x in kv[0])):
        if all(val(b,elems)<=d-1 for b in blocks):
            return {"probe":p,"children":[build(b,elems,d-1) for b in blocks]}
    return None
tree=build(m, list(elems), d)
def tdepth(t): return 0 if "leaf" in t else 1+max(tdepth(c) for c in t["children"])
def tleaves(t): return len(t["leaf"]) if "leaf" in t else sum(tleaves(c) for c in t["children"])
print(f"witness tree on the size-{sz} class: depth {tdepth(tree)}, leaves cover {tleaves(tree)} types, "
      f"all singleton: {all_s if (all_s:=True) else ''}")
def allsing(t): return len(t["leaf"])==1 if "leaf" in t else all(allsing(c) for c in t["children"])
print("every leaf a singleton:",allsing(tree))
# Q4 secondary: expected depth under the uniform prior over 715 types
tot=0
for cls in joint:
    m2=0
    for o in cls: m2|=(1<<o)
    tot += val(m2, cls)*len(cls)
print("expected depth under uniform prior over 715 types: %.4f"%(tot/715))
json.dump({"D_star":Dstar,"agrees_with_recursive_solver":agree,
  "classes_attaining_D_star":len(biggest),
  "infeasibility_certificate_at_d_minus_1":cert,
  "witness_class_size":sz,"witness_tree_depth":tdepth(tree),
  "witness_all_leaves_singleton":allsing(tree),
  "expected_depth_uniform_prior":tot/715,
  "distinct_states_valued":len(VAL)}, open("qg34_verify.json","w"), indent=2)
