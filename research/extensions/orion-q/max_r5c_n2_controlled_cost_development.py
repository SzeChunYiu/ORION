#!/usr/bin/env python3
"""Development-only controlled-SELECT-aware successor on the now-open N2 case.

N2 is no longer protected after MAX-R5B. This script diagnoses the outer-control
negative and develops the next method before a new subject is frozen. It is NOT
a fresh confirmation and cannot authorize R5/R6.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache

import numpy as np
import max_r4d_h2o_ducc_confirmation as h

h.SOURCE_COMMIT = "be306f5830549304176365750d712093950bbdde"
h.SOURCE_BLOB = "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba"
h.SOURCE_PATH = "N2/cc-pVTZ/6Elec_6Orbs/1.0_Eq-2.0680au/DUCC2/N2.cc-pvtz.ducc.results.txt"
h.SOURCE_URL = "https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/" + h.SOURCE_COMMIT + "/" + h.SOURCE_PATH
h.N_OCC = 3; h.N_VIRT = 3; h.N_ORB = 6; h.N_QUBITS = 12
N = 12
TARGET = 0b101
INF = 10**9
XOR = np.bitwise_xor(np.arange(8)[:,None], np.arange(8)[None,:])

# Same frozen projection as R5B.
RZ_T = 48
DIRECT_T = 3 * 2 * RZ_T                       # 288
TARE_T = DIRECT_T + 3 * 2 + 4 * 7            # +3 CH*2T + 4 Toffoli*7T = 322
DIRECT_FIXED_CNOT = 3 * 2                     # three controlled Rz
TARE_FIXED_CNOT = 3*2 + 3*1 + 4*6             # cRz + controlled-H + four Toffolis = 33


def weight(k): return (k[0] | k[1]).bit_count()
def symp(a,b): return ((a[0]&b[1]).bit_count() + (a[1]&b[0]).bit_count()) & 1

def codes(k):
    x,z=k
    for q in range(N): yield h.BITS_CODE[((x>>q)&1,(z>>q)&1)]

# For each local target pair, parity delta, and deterministic Restore base branch,
# exact additive controlled-CNOT support contribution. Global orientation constants
# are handled after the 8-state DP.
LOCAL = np.full((4,4,2,8), INF, dtype=np.int32)
for p0 in range(4):
    for p1 in range(4):
        for r0 in range(4):
            for r1 in range(4):
                for s in range(4):
                    d = h.local_symp(r0,r1) | (h.local_symp(s,r0)<<1) | (h.local_symp(s,r1)<<2)
                    t0 = h.local_mul(p0,r0); t1 = h.local_mul(p1,r1); tx = h.local_mul(t0,t1)
                    common = 4*h.local_wt(r0)+2*h.local_wt(r1)+2*h.local_wt(s)+h.local_wt(tx)
                    for base,tb in enumerate((t0,t1)):
                        c = common + h.local_wt(tb)
                        if c < LOCAL[p0,p1,base,d]: LOCAL[p0,p1,base,d]=c

@lru_cache(maxsize=400000)
def tare_ctrl_cnot(k0,k1):
    best=INF
    for a,b in ((k0,k1),(k1,k0)):
        ca=tuple(codes(a)); cb=tuple(codes(b))
        for base in (0,1):
            dp=np.full(8,INF,dtype=np.int32); dp[0]=0
            for p0,p1 in zip(ca,cb):
                loc=LOCAL[p0,p1,base]
                dp=np.min(dp[:,None]+loc[XOR],axis=0)
            # raw has 4wR0+2wR1; subtract 6 for (w-1), then add fixed controlled overhead 33.
            best=min(best,int(dp[TARGET]-6+TARE_FIXED_CNOT))
    return int(best)

@lru_cache(maxsize=400000)
def direct_ctrl_cnot(k0,k1):
    if not symp(k0,k1): raise ValueError
    w0,w1=weight(k0),weight(k1)
    parity=min(4*(w0-1)+2*(w1-1),4*(w1-1)+2*(w0-1))
    return int(parity+DIRECT_FIXED_CNOT)


def edge(t0,t1):
    (k0,a0),(k1,a1)=t0,t1
    if symp(k0,k1):
        return {"lambda":math.hypot(abs(a0),abs(a1)),"CNOT":direct_ctrl_cnot(k0,k1),"T":DIRECT_T,"direct":1}
    return {"lambda":math.sqrt(2)*math.hypot(abs(a0),abs(a1)),"CNOT":tare_ctrl_cnot(k0,k1),"T":TARE_T,"direct":0}


def metrics(terms,pairs):
    out={"Lambda":0.0,"CNOT":0,"T":0,"direct":0,"pairs":len(pairs)}
    for i,j in pairs:
        e=edge(terms[i],terms[j]); out["Lambda"]+=e["lambda"]; out["CNOT"]+=e["CNOT"]; out["T"]+=e["T"]; out["direct"]+=e["direct"]
    return out


def pats(idx):
    if len(idx)==2:return [[(idx[0],idx[1])]]
    return [[(idx[0],idx[1]),(idx[2],idx[3])],[(idx[0],idx[2]),(idx[1],idx[3])],[(idx[0],idx[3]),(idx[1],idx[2])]]


def compile_controlled(terms,frac):
    q=[]
    for s in range(0,len(terms),4):
        opts=[]
        idx=list(range(s,min(s+4,len(terms))))
        for oi,ps in enumerate(pats(idx)):
            opts.append((oi,ps,metrics(terms,ps)))
        # Absorb outer-control knowledge into the incumbent's deterministic tie-break.
        opts.sort(key=lambda x:(x[2]["Lambda"],x[2]["T"],x[2]["CNOT"],x[0])); q.append(opts)
    choice={qi:opts[0][0] for qi,opts in enumerate(q)}
    def assemble(ch):
        pairs=[]
        for qi,opts in enumerate(q):
            by={oi:ps for oi,ps,_ in opts}; pairs+=by[ch[qi]]
        return pairs
    base_pairs=assemble(choice); base=metrics(terms,base_pairs)
    budget=frac*base["Lambda"]; used=0.0; moves=[]
    for qi,opts in enumerate(q):
        bid=choice[qi]; bm=next(m for oi,_p,m in opts if oi==bid)
        local=[]
        for oi,_p,m in opts:
            if oi==bid:continue
            dl=m["Lambda"]-bm["Lambda"]; dc=bm["CNOT"]-m["CNOT"]; dt=bm["T"]-m["T"]
            # Non-compensatory fault-tolerant rule: never worsen either projected resource.
            if dc>0 and dt>=0 and dl>=-1e-12:
                score=float("inf") if dl<=1e-15 else dc/dl
                local.append((score,dc,dt,max(0.0,dl),oi))
        if local:
            local.sort(key=lambda x:(-x[0],-x[1],-x[2],x[3],x[4])); moves.append((*local[0],qi))
    # Stored tuple: score,dc,dt,dl,oi,qi
    moves.sort(key=lambda x:(-x[0],-x[1],-x[2],x[3],x[5],x[4]))
    moved=0
    for _score,_dc,_dt,dl,oi,qi in moves:
        if used+dl<=budget+1e-12:
            choice[qi]=oi;used+=dl;moved+=1
    suc=metrics(terms,assemble(choice)); suc["budget_used"]=used;suc["moved_quartets"]=moved
    return base,suc


def main():
    text=h.fetch_source();one,two=h.parse_ducc(text);paulis,max_imag=h.jordan_wigner_paulis(one,two);paulis.pop((0,0),None)
    terms=sorted(paulis.items(),key=lambda kv:(-abs(kv[1]),kv[0][0],kv[0][1]))
    assert len(terms)%2==0
    rows={}
    for frac in (0.0,0.0025,0.005,0.01,0.02,0.05):
        base,suc=compile_controlled(terms,frac)
        rows[str(frac)]={"base":base,"successor":suc,"norm_over":suc["Lambda"]/base["Lambda"]-1,
                         "CNOT_reduction":1-suc["CNOT"]/base["CNOT"],"T_reduction":1-suc["T"]/base["T"]}
    out={"schema":"ORIONQ.MAXR5C.N2ControlledCostDevelopment.v1","authority":"DEVELOPMENT_ONLY__N2_ALREADY_OPEN",
         "source_blob":h.SOURCE_BLOB,"n_qubits":12,"terms":len(terms),"max_imag":max_imag,
         "projection":{"DIRECT_T":DIRECT_T,"TARE_T":TARE_T,"DIRECT_FIXED_CNOT":DIRECT_FIXED_CNOT,"TARE_FIXED_CNOT":TARE_FIXED_CNOT},
         "controlled_exact_DP":"8_state_x_2_restore_base_x_2_orientation","rows":rows}
    print("ORIONQ_MAX_R5C_DEV="+json.dumps(out,sort_keys=True));return out
if __name__=="__main__":main()
