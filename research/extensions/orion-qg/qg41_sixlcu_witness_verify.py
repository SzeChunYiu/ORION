"""SECOND CODE PATH: re-derive the headline witnesses by looping qg4.member_cost
directly over all 2430 (part,phi). Nothing here touches the numpy tensor."""
import sys, itertools, json
sys.path.insert(0,"/Users/billy/Desktop/projects/ORION-claude/research/extensions/orion-qg")
import qg4_second_family as qg4
def const_part(part,shared):
    k=len(part); flag=1 if k>=2 else 0
    prep=(0 if k==1 else 2*k-3)+sum((len(b)-1)*(1+flag)+qg4.DS[len(b)] for b in part if len(b)>=2)
    bs=[qg4.bbits(len(b)) for b in part]
    return prep+(k if k>=2 else 0)+((max(bs) if bs else 0) if shared else sum(bs))
def solve(colstr):
    col=[ "IXYZ".index(ch) for ch in colstr ]; costs={}
    for pi,part in enumerate(qg4.PARTITIONS):
        for phi in itertools.product((0,1),repeat=len(part)):
            costs[(pi,phi)]=qg4.member_cost(col,1,part,phi,True)-const_part(part,True)
    b=min(costs.values()); return b,{k for k,v in costs.items() if v==b},costs
out={}
for pair in [("IIIXXY","IIIXYX"),("XXYYZZ","XYXYZZ"),("IIXXXY","IIXXYX")]:
    (ba,Aa,ca),(bb,Ab,cb)=solve(pair[0]),solve(pair[1])
    shp=lambda S:sorted({tuple(sorted((len(x) for x in qg4.PARTITIONS[pi]),reverse=True)) for pi,_ in S})
    print(f"{pair[0]} vs {pair[1]}:  optima {ba} / {bb}  equal={ba==bb}")
    print(f"   |argmin| {len(Aa)} / {len(Ab)}   INTERSECTION {len(Aa&Ab)}   disjoint={len(Aa&Ab)==0}")
    print(f"   spectrum equal: {sorted(ca.values())==sorted(cb.values())}")
    print(f"   optimal SHAPE sets equal: {shp(Aa)==shp(Ab)}  -> {shp(Aa)}")
    out[f"{pair[0]}|{pair[1]}"]={"opt":[ba,bb],"argmin_sizes":[len(Aa),len(Ab)],
      "intersection":len(Aa&Ab),"spectrum_equal":sorted(ca.values())==sorted(cb.values()),
      "shape_sets_equal":shp(Aa)==shp(Ab)}
json.dump(out,open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/broadclass/witness_verify.json","w"),indent=2)
