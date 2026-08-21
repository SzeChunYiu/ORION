#!/usr/bin/env python3
"""MAX-R5 development-only exact m=2 TARE internal gate accounting on H2O.

Uses the already-exposed H2O subject only to freeze the next fresh N2 protocol.
No N2 source is read here.
"""
from __future__ import annotations

import json
from functools import lru_cache
import numpy as np

import max_r4d_h2o_ducc_confirmation as h

INF = 10**8
# exact additive local cost for standard m=2 TARE:
# Uanti: R0,R1,R0 => 4(w(R0)-1)+2(w(R1)-1) CNOTs;
# Tag and Tag^dagger => 2*w(S) controlled-Pauli factors;
# Restore => w(T0)+w(T1).
LOCAL_G = np.full((4,4,8), INF, dtype=np.int32)
for p0 in range(4):
    for p1 in range(4):
        for r0 in range(4):
            for r1 in range(4):
                for s in range(4):
                    d = h.local_symp(r0,r1) | (h.local_symp(s,r0)<<1) | (h.local_symp(s,r1)<<2)
                    t0=h.local_mul(p0,r0); t1=h.local_mul(p1,r1)
                    g=(4*h.local_wt(r0)+2*h.local_wt(r1)+2*h.local_wt(s)+h.local_wt(t0)+h.local_wt(t1))
                    if g<LOCAL_G[p0,p1,d]: LOCAL_G[p0,p1,d]=g

XOR=h.XOR

def weight(key): return (key[0] | key[1]).bit_count()

@lru_cache(maxsize=300000)
def corrected_orientation(a,b):
    ca=tuple(h.local_codes(a)); cb=tuple(h.local_codes(b))
    dp=np.full(8,INF,dtype=np.int32); dp[0]=0
    for p0,p1 in zip(ca,cb):
        loc=LOCAL_G[p0,p1]
        dp=np.min(dp[:,None]+loc[XOR],axis=0)
    # subtract constants from Pauli-rotation CNOT formula: 4+2=6.
    return int(dp[5]-6)

@lru_cache(maxsize=300000)
def pair_gate_cost(a,b):
    corr=min(corrected_orientation(a,b), corrected_orientation(b,a))
    if h.anticommutes(a,b):
        wa,wb=weight(a),weight(b)
        direct=min(4*(wa-1)+2*(wb-1),4*(wb-1)+2*(wa-1))
        return min(corr,direct)
    return corr

def pair_lam(x,y): return h.pair_lambda(x,y)

def metrics(terms,pairs):
    return {
      "Lambda":float(sum(pair_lam(terms[i][1],terms[j][1]) for i,j in pairs)),
      "G_internal_2q":int(sum(pair_gate_cost(terms[i][0],terms[j][0]) for i,j in pairs)),
      "pair_count":len(pairs),
      "coefficient_rotation_count":3*len(pairs),
    }

def compile_quartets(terms,frac):
    base_pairs=[(i,i+1) for i in range(0,len(terms),2)]
    base=metrics(terms,base_pairs)
    budget=base["Lambda"]*frac
    selected=[]; used=0.0
    for s in range(0,len(terms),4):
        idx=list(range(s,min(s+4,len(terms))))
        if len(idx)<4:
            selected.append([(idx[0],idx[1])]); continue
        pats=[[(idx[0],idx[1]),(idx[2],idx[3])],[(idx[0],idx[2]),(idx[1],idx[3])],[(idx[0],idx[3]),(idx[1],idx[2])]]
        vals=[metrics(terms,p) for p in pats]
        b=vals[0]
        candidates=[]
        for oi in (1,2):
            dl=vals[oi]["Lambda"]-b["Lambda"]
            dg=b["G_internal_2q"]-vals[oi]["G_internal_2q"]
            if dg>0 and dl>=-1e-12:
                candidates.append((float('inf') if dl<=1e-15 else dg/dl,dg,dl,oi))
        # window-local best efficiency; global sort is done later by returning move record
        best=max(candidates,default=None)
        selected.append((pats,vals,best))
    moves=[]
    for qi,item in enumerate(selected):
        if isinstance(item,list): continue
        pats,vals,best=item
        if best is not None: moves.append((*best,qi))
    moves.sort(reverse=True)
    choice=[0]*len(selected)
    for score,dg,dl,oi,qi in moves:
        if used+dl<=budget+1e-12:
            choice[qi]=oi; used+=max(0.0,dl)
    pairs=[]
    for qi,item in enumerate(selected):
        if isinstance(item,list): pairs.extend(item)
        else: pairs.extend(item[0][choice[qi]])
    return base,metrics(terms,pairs)

def main():
    text=h.fetch_source(); one,two=h.parse_ducc(text); paulis,_=h.jordan_wigner_paulis(one,two)
    paulis.pop((0,0),None)
    terms=sorted(paulis.items(),key=lambda kv:abs(kv[1]),reverse=True)
    singleton=None
    if len(terms)%2:
        singleton=terms[-1]; terms=terms[:-1]
    base,g0=compile_quartets(terms,0.0)
    _,g1=compile_quartets(terms,0.01)
    _,g5=compile_quartets(terms,0.05)
    if singleton is not None:
        for m in (base,g0,g1,g5): m["Lambda"]+=abs(singleton[1])
    def red(m): return (base["G_internal_2q"]-m["G_internal_2q"])/base["G_internal_2q"]
    out={"schema":"ORIONQ.MAXR5.H2OFullPairGateDevelopment.v1","subject":"H2O_DEVELOPMENT_ONLY","base":base,"zero_slack":g0,"one_pct":g1,"five_pct":g5,"zero_slack_G_reduction":red(g0),"one_pct_G_reduction":red(g1),"five_pct_G_reduction":red(g5),"authority":"development_only__used_to_freeze_N2_not_confirmation"}
    print("ORIONQ_MAX_R5_DEV="+json.dumps(out,sort_keys=True))

if __name__=='__main__': main()
