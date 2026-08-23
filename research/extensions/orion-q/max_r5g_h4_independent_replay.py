#!/usr/bin/env python3
"""Independent MAX-R5G replay of the fresh H4 R5F result.

Does not import R5C/R5E/R5F compiler or proof code. Reuses only the verified
R4D DUCC->Jordan-Wigner semantic layer, then independently reconstructs the
controlled-cost DP, exact 12-term matching search, witnesses, and frozen hashes.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache

import max_r4d_h2o_ducc_confirmation as h

SOURCE_COMMIT = "be306f5830549304176365750d712093950bbdde"
SOURCE_BLOB = "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5"
SOURCE_PATH = "H4/cc-pVDZ/2.0au/DUCC3/H4.cc-pvdz_files/restricted/ducc/H4.cc-pvdz.ducc.results.txt"
h.SOURCE_COMMIT = SOURCE_COMMIT
h.SOURCE_BLOB = SOURCE_BLOB
h.SOURCE_PATH = SOURCE_PATH
h.SOURCE_URL = "https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/" + SOURCE_COMMIT + "/" + SOURCE_PATH
h.N_OCC = 2; h.N_VIRT = 2; h.N_ORB = 4; h.N_QUBITS = 8

N = 8
WINDOW = 12
TARGET = 0b101
NORM_FRAC = 0.01
RZ_T = 48
DIRECT_T = 288
TARE_T = 322
DIRECT_FIXED_CNOT = 6
TARE_FIXED_CNOT = 33
EXPECTED = {
    "sorted_terms": "39d5897efd90f9ab3e639cd5586d06b46e9fccb3e04bb675a23e0798280c1a6b",
    "inc_pair_list": "917b0dbf4a380225e609e78918252a4bf2ddb3ed8180c52247d676d0e34f4611",
    "suc_pair_list": "c516fcac4914190beefc099823b7933e8af449aa8723c882c78accd5c30c5608",
    "inc_witness": "29cf9f601d4a783cbb2398fabdecb55193a6bd3816a877fb722d4a66f77ff889",
    "suc_witness": "9dd11ff0cbac36373a7da4ccd4625153aa0cb9527e6bf6400d29377e1f5381a1",
}
EXPECTED_AGG = {
    "inc_Lambda": 5.15888533051182,
    "inc_CNOT": 5332,
    "inc_T": 43148,
    "inc_direct": 0,
    "suc_Lambda": 4.862865511405695,
    "suc_CNOT": 4198,
    "suc_T": 40224,
    "suc_direct": 86,
    "enumerated": 228693,
}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def wt(k): return (k[0] | k[1]).bit_count()
def mul(a,b): return (a[0]^b[0], a[1]^b[1])
def symp(a,b): return ((a[0]&b[1]).bit_count() + (a[1]&b[0]).bit_count()) & 1


def codes(k):
    x,z=k
    for q in range(N):
        yield h.BITS_CODE[((x>>q)&1, (z>>q)&1)]


def pack(seq, slot):
    x=z=0
    for q,triple in enumerate(seq):
        bx,bz=h.CODE_BITS[triple[slot]]
        x |= bx<<q; z |= bz<<q
    return (x,z)


def delta(r0,r1,s):
    return h.local_symp(r0,r1) | (h.local_symp(s,r0)<<1) | (h.local_symp(s,r1)<<2)


def local_cost(p0,p1,r0,r1,s,base):
    t0=h.local_mul(p0,r0); t1=h.local_mul(p1,r1); tx=h.local_mul(t0,t1)
    tb=t0 if base==0 else t1
    return 4*h.local_wt(r0)+2*h.local_wt(r1)+2*h.local_wt(s)+h.local_wt(tx)+h.local_wt(tb)


def orientation(a,b,base):
    # Independent brute local enumeration: all 64 triples, no precomputed table.
    states={0:(0,tuple())}
    for p0,p1 in zip(codes(a),codes(b)):
        nxt={}
        for prev,(pcost,pseq) in states.items():
            for r0 in range(4):
                for r1 in range(4):
                    for s in range(4):
                        d=delta(r0,r1,s)
                        key=prev^d
                        cand=(pcost+local_cost(p0,p1,r0,r1,s,base),pseq+((r0,r1,s),))
                        if key not in nxt or cand<nxt[key]: nxt[key]=cand
        states=nxt
    raw,seq=states[TARGET]
    return int(raw-6+TARE_FIXED_CNOT),seq


@lru_cache(maxsize=100000)
def witness(k0,k1):
    if symp(k0,k1):
        opts=[]
        for oid,(a,b) in enumerate(((k0,k1),(k1,k0))):
            c=4*(wt(a)-1)+2*(wt(b)-1)+DIRECT_FIXED_CNOT
            opts.append((c,oid,a,b))
        c,oid,a,b=min(opts,key=lambda x:(x[0],x[1]))
        return {"type":"DIRECT_ANTI_UNITARY","orientation":oid,"controlled_CNOT":int(c),"projected_T":DIRECT_T,
                "checks":{"targets_anticommute":symp(k0,k1)==1}}
    opts=[]
    for oid,(a,b) in enumerate(((k0,k1),(k1,k0))):
        for base in (0,1):
            c,seq=orientation(a,b,base)
            opts.append((c,oid,base,seq,a,b))
    c,oid,base,seq,a,b=min(opts,key=lambda x:(x[0],x[1],x[2],x[3]))
    r0,r1,s=pack(seq,0),pack(seq,1),pack(seq,2)
    t0,t1=mul(a,r0),mul(b,r1); tx=mul(t0,t1)
    branch=wt(tx)+(wt(t0) if base==0 else wt(t1))
    recomputed=4*(wt(r0)-1)+2*(wt(r1)-1)+2*wt(s)+branch+TARE_FIXED_CNOT
    checks={
        "R0_anticommutes_R1":symp(r0,r1)==1,
        "S_commutes_R0":symp(s,r0)==0,
        "S_anticommutes_R1":symp(s,r1)==1,
        "T0R0_equals_P0":mul(t0,r0)==a,
        "T1R1_equals_P1":mul(t1,r1)==b,
        "restore_branch_is_min_for_witness":branch==wt(tx)+min(wt(t0),wt(t1)),
        "controlled_CNOT_recomputed":recomputed==c,
    }
    if not all(checks.values()): raise AssertionError({"witness":checks,"k0":k0,"k1":k1,"base":base})
    return {"type":"TARE_M2","orientation":oid,"restore_base":base,"R0":list(r0),"R1":list(r1),"S":list(s),
            "T0":list(t0),"T1":list(t1),"restore_support":int(branch),"controlled_CNOT":int(c),"projected_T":TARE_T,
            "checks":checks}


@lru_cache(maxsize=100000)
def edge_cached(k0,k1,a0,a1):
    w=witness(k0,k1)
    direct=w["type"]=="DIRECT_ANTI_UNITARY"
    lam=math.hypot(abs(a0),abs(a1)) if direct else math.sqrt(2.0)*math.hypot(abs(a0),abs(a1))
    return float(lam),int(w["controlled_CNOT"]),int(w["projected_T"]),int(direct)


def edge(terms,i,j):
    k0,a0=terms[i]; k1,a1=terms[j]
    return edge_cached(k0,k1,float(a0),float(a1))


def metrics(terms,pairs):
    lam=0.0;c=t=d=0
    for i,j in pairs:
        le,ce,te,de=edge(terms,i,j);lam+=le;c+=ce;t+=te;d+=de
    return {"Lambda":float(lam),"CNOT":int(c),"T":int(t),"direct":int(d),"pairs":len(pairs)}


def patterns(idx):
    if len(idx)==2:return [[(idx[0],idx[1])]]
    return [[(idx[0],idx[1]),(idx[2],idx[3])],[(idx[0],idx[2]),(idx[1],idx[3])],[(idx[0],idx[3]),(idx[1],idx[2])]]


def incumbent_pairs(terms):
    out=[]
    for s in range(0,len(terms),4):
        idx=list(range(s,min(s+4,len(terms))))
        choices=[]
        for oi,ps in enumerate(patterns(idx)):
            m=metrics(terms,ps); choices.append((m["Lambda"],m["T"],m["CNOT"],oi,tuple(ps)))
        out.extend(min(choices)[4])
    return out


def enumerate_matchings(items):
    items=tuple(items)
    if not items:
        yield tuple();return
    a=items[0];rest=items[1:]
    for pos,b in enumerate(rest):
        rem=rest[:pos]+rest[pos+1:]
        for tail in enumerate_matchings(rem): yield ((a,b),)+tail


def local_frontier(terms,idx,bpairs):
    base=metrics(terms,bpairs)
    # Independent representation: at each direct delta keep, for each exact CNOT
    # delta, only the minimum lambda-delta row; then scan CNOT ascending.
    bins={};count=0
    for ps in enumerate_matchings(idx):
        count+=1;m=metrics(terms,ps)
        dD=m["direct"]-base["direct"];dC=m["CNOT"]-base["CNOT"];dl=m["Lambda"]-base["Lambda"]
        key=(dD,dC);cand=(dl,ps)
        if key not in bins or cand<bins[key]:bins[key]=cand
    grouped={}
    for (dD,dC),(dl,ps) in bins.items():grouped.setdefault(dD,[]).append({"dD":dD,"dC":dC,"dl":dl,"pairs":ps})
    reduced=[]
    for dD,rows in grouped.items():
        rows.sort(key=lambda r:(r["dC"],r["dl"],r["pairs"]))
        best=float("inf")
        for r in rows:
            if r["dl"]<best-1e-15:reduced.append(r);best=r["dl"]
    keep=[]
    for i,a in enumerate(reduced):
        dominated=False
        for j,b in enumerate(reduced):
            if i==j:continue
            if b["dD"]>=a["dD"] and b["dC"]<=a["dC"] and b["dl"]<=a["dl"]+1e-15 and (b["dD"]>a["dD"] or b["dC"]<a["dC"] or b["dl"]<a["dl"]-1e-15):
                dominated=True;break
        if not dominated:keep.append(a)
    keep.sort(key=lambda r:(-r["dD"],r["dC"],r["dl"],r["pairs"]))
    return base,keep,count


def prune(states):
    grouped={}
    for (dD,dC),(dl,ch) in states.items():grouped.setdefault(dD,[]).append((dC,dl,ch))
    out={}
    for dD,rows in grouped.items():
        rows.sort();best=float("inf")
        for dC,dl,ch in rows:
            if dl<best-1e-15:out[(dD,dC)]=(dl,ch);best=dl
    return out


def exact_successor(terms,bpairs):
    windows=[];total=0
    for start in range(0,len(terms),WINDOW):
        end=min(start+WINDOW,len(terms));idx=list(range(start,end))
        bp=[p for p in bpairs if start<=p[0]<end and start<=p[1]<end]
        assert len(bp)==len(idx)//2
        base,front,count=local_frontier(terms,idx,bp);total+=count
        windows.append((base,front))
    suf_l=[0.0]*(len(windows)+1);suf_d=[0]*(len(windows)+1)
    for i in range(len(windows)-1,-1,-1):
        f=windows[i][1];suf_l[i]=suf_l[i+1]+min(r["dl"] for r in f);suf_d[i]=suf_d[i+1]+max(r["dD"] for r in f)
    b=metrics(terms,bpairs);budget=NORM_FRAC*b["Lambda"];states={(0,0):(0.0,tuple())}
    for wi,(_base,front) in enumerate(windows):
        nxt={}
        for (dD0,dC0),(dl0,ch0) in states.items():
            for oi,r in enumerate(front):
                dD=dD0+r["dD"];dC=dC0+r["dC"];dl=dl0+r["dl"]
                if dl+suf_l[wi+1]>budget+1e-12 or dD+suf_d[wi+1]<0:continue
                key=(dD,dC);cand=(dl,ch0+(oi,))
                if key not in nxt or cand<nxt[key]:nxt[key]=cand
        states=prune(nxt)
    feasible=[]
    for (dD,dC),(dl,ch) in states.items():
        if dD>=0 and dl<=budget+1e-12:feasible.append((dC,dl,-dD,ch,dD))
    dC,dl,_neg,ch,dD=min(feasible,key=lambda x:(x[0],x[1],x[2],x[3]))
    pairs=[]
    for wi,oi in enumerate(ch):pairs.extend(windows[wi][1][oi]["pairs"])
    return pairs,total


def proof_payload(terms,pairs):
    out=[]
    for i,j in pairs:
        k0,a0=terms[i];k1,a1=terms[j];w=witness(k0,k1)
        direct=w["type"]=="DIRECT_ANTI_UNITARY"
        lam=math.hypot(abs(a0),abs(a1)) if direct else math.sqrt(2.0)*math.hypot(abs(a0),abs(a1))
        rec={"term_indices":[int(i),int(j)],"input_keys":[list(k0),list(k1)],"type":w["type"],"orientation":w["orientation"],
             "lambda_pair":round(float(lam),16),"controlled_CNOT":w["controlled_CNOT"],"projected_T":w["projected_T"]}
        for key in ("restore_base","R0","R1","S","T0","T1","restore_support"):
            if key in w:rec[key]=w[key]
        out.append(rec)
    return out


def main():
    text=h.fetch_source();one,two=h.parse_ducc(text);paulis,max_imag=h.jordan_wigner_paulis(one,two);paulis.pop((0,0),None)
    terms=sorted(paulis.items(),key=lambda kv:(-abs(kv[1]),kv[0][0],kv[0][1]))
    assert len(terms)==268 and len(terms)%2==0
    bp=incumbent_pairs(terms);ep,total=exact_successor(terms,bp)
    bm,em=metrics(terms,bp),metrics(terms,ep)
    got={
      "sorted_terms":sha([[list(k),format(float(a),".17g")] for k,a in terms]),
      "inc_pair_list":sha([[int(i),int(j)] for i,j in bp]),
      "suc_pair_list":sha([[int(i),int(j)] for i,j in ep]),
      "inc_witness":sha(proof_payload(terms,bp)),
      "suc_witness":sha(proof_payload(terms,ep)),
    }
    hash_match={k:got[k]==EXPECTED[k] for k in EXPECTED}
    aggregate_match={
      "inc_Lambda":abs(bm["Lambda"]-EXPECTED_AGG["inc_Lambda"])<=1e-12,"inc_CNOT":bm["CNOT"]==EXPECTED_AGG["inc_CNOT"],
      "inc_T":bm["T"]==EXPECTED_AGG["inc_T"],"inc_direct":bm["direct"]==EXPECTED_AGG["inc_direct"],
      "suc_Lambda":abs(em["Lambda"]-EXPECTED_AGG["suc_Lambda"])<=1e-12,"suc_CNOT":em["CNOT"]==EXPECTED_AGG["suc_CNOT"],
      "suc_T":em["T"]==EXPECTED_AGG["suc_T"],"suc_direct":em["direct"]==EXPECTED_AGG["suc_direct"],
      "enumerated":total==EXPECTED_AGG["enumerated"],
    }
    norm_weight_cnot=(em["Lambda"]*em["CNOT"])/(bm["Lambda"]*bm["CNOT"])
    norm_weight_t=(em["Lambda"]*em["T"])/(bm["Lambda"]*bm["T"])
    sign={"CNOT":em["CNOT"]<bm["CNOT"],"T":em["T"]<bm["T"],"Lambda":em["Lambda"]<bm["Lambda"],
          "weighted_CNOT":norm_weight_cnot<1,"weighted_T":norm_weight_t<1}
    if not all(hash_match.values()) or not all(aggregate_match.values()) or not all(sign.values()):
        raise AssertionError({"hash_match":hash_match,"aggregate_match":aggregate_match,"sign":sign,"got":got,"inc":bm,"suc":em,"enumerated":total})
    result={"schema":"ORIONQ.MAXR5G.H4IndependentReplay.v1","authority":"MAX_R5G_H4_INDEPENDENT_REPLAY_GREEN",
            "source_blob":SOURCE_BLOB,"max_pauli_imaginary_residual":max_imag,"hashes":got,"hash_match":hash_match,
            "aggregate_match":aggregate_match,"incumbent":bm,"successor":em,"perfect_matchings_enumerated":total,
            "normalization_weighted_CNOT_ratio":norm_weight_cnot,"normalization_weighted_T_ratio":norm_weight_t,"positive_signs":sign,
            "independent_replay_pass":True}
    print("ORIONQ_MAX_R5G_H4_INDEPENDENT="+json.dumps(result,sort_keys=True));return result
if __name__=="__main__":main()
