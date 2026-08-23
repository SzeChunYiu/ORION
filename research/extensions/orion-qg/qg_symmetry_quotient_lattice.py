"""Exact orbit counts of the 4096 TARE target-column types under every natural
subgroup of  S_3(letters) x Sym(6 positions).  Purely combinatorial; rebuilt
from primitives.  Purpose: say which QG partition cardinalities (45 bulk,
54 spectrum, 715 indexed) are symmetry quotients and which are not."""
from itertools import product, permutations
import json
TYPES=list(product("IXYZ",repeat=6))
NON=["X","Y","Z"]
AUTS=[]
for pm in permutations(NON):
    d={"I":"I"}; d.update(dict(zip(NON,pm))); AUTS.append(d)
IDA=[{"I":"I","X":"X","Y":"Y","Z":"Z"}]

def posgrp(name):
    if name=="trivial": return [tuple(range(6))]
    if name=="swaps":                      # S_2^3 : swap the 2 targets in each block
        return [tuple(x for bi in range(3) for x in ((2*bi+1,2*bi) if s[bi] else (2*bi,2*bi+1)))
                for s in product((0,1),repeat=3)]
    if name=="blocks":                     # S_3 permuting the 3 blocks
        return [tuple(x for b in bl for x in (2*b,2*b+1)) for bl in permutations(range(3))]
    if name=="wreath":                     # S_2 wr S_3
        out=set()
        for bl in permutations(range(3)):
            for s in product((0,1),repeat=3):
                p=[]
                for bi in range(3):
                    a,b=2*bl[bi],2*bl[bi]+1
                    p+= [b,a] if s[bi] else [a,b]
                out.add(tuple(p))
        return sorted(out)
    if name=="full_S6": return list(permutations(range(6)))
rows=[]
for lname,L in (("trivial",IDA),("S_3_letters",AUTS)):
    for pname in ("trivial","swaps","blocks","wreath","full_S6"):
        P=posgrp(pname)
        seen=set(); n=0; sizes={}
        for t in TYPES:
            if t in seen: continue
            orb={tuple(phi[t[i]] for i in p) for phi in L for p in P}
            seen|=orb; n+=1; sizes[len(orb)]=sizes.get(len(orb),0)+1
        rows.append({"letter_group":lname,"position_group":pname,
                     "group_order":len(L)*len(P),"orbit_count":n,
                     "orbit_size_histogram":{str(k):v for k,v in sorted(sizes.items())}})
qg={"45_bulk_signature":45,"54_unlabeled_defect_spectrum":54,"715_indexed_response":715}
matches={k:[f"{r['letter_group']} x {r['position_group']}" for r in rows if r["orbit_count"]==v]
         for k,v in qg.items()}
print(json.dumps({"schema":"ORION.QG.SymmetryQuotientLattice.v1",
                  "alphabet_size":len(TYPES),"rows":rows,
                  "qg31_reported_cardinalities":qg,
                  "symmetry_quotients_matching_those_cardinalities":matches},
                 indent=2,sort_keys=True))
