#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-7e.

No imports from QG-7/QG-5b production analyzers. Rebuilds phase-free Pauli
letters, PP G1-G4, the full hidden domain, the globally consistent relocation
library, exact support-one D+, and exact B' for the 24 residuals.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/"artifacts/orion-qg-qg7e-pp-single-pinner.json"
OUT=ROOT/"artifacts/orion-qg-qg7e-generic-verification.json"
TOKEN="ORIONQG_QG7E_GENERIC="
POS="QG7E_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN"
X,Z=1,3
SIGMAS=tuple(itertools.product((0,1),repeat=3))
EXPECTED=(4057,3678,4057,3678,3678,4057,3678,4057,217,187,217,187,187,217,187,217)


def canon(v:Any)->str: return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def verify_digest(r):
    u={k:v for k,v in r.items() if k!="result_digest"}; return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def lm(a,b):
    if a==0:return b
    if b==0:return a
    if a==b:return 0
    return 6-a-b
def sy(a,b): return int(a!=0 and b!=0 and a!=b)
def f3(a,b,c): return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
LM=np.array([[lm(a,b) for b in range(4)] for a in range(4)],dtype=np.int8)
F3=np.array([[[f3(a,b,c) for c in range(4)] for b in range(4)] for a in range(4)],dtype=np.int8)
F3E=np.array([[f3(a,u,v) for u in range(4) for v in range(4)] for a in range(4)],dtype=np.int8)
F3T=np.array([[[f3(a,b,e) for e in range(4)] for b in range(4)] for a in range(4)],dtype=np.int8)
AC={s:tuple(r for r in (1,2,3) if sy(s,r)) for s in (1,2,3)}


def pp_cell(ja,rb,ra,p):
    t4=np.arange(4,dtype=np.int64); t0=np.repeat(t4,16); t1=np.tile(np.repeat(t4,4),4); t2=np.tile(t4,16)
    w=lm(ra,Z); o0b=LM[t0,rb]; o1b=t1; o1bp=LM[t2,p]; o0a=LM[t0,ra]; o1a=LM[t1,w]; o1ap=t2
    oldb=F3E[o0b][:,:,None]+F3T[o1b,o1bp][:,None,:]; olda=F3E[o0a][:,:,None]+F3T[o1a,o1ap][:,None,:]
    best=np.full((64,64,64,64),99,dtype=np.int16)
    def group(bp,ap,s):
        fb=np.stack([F3E[x][:,:,None]+F3T[y,z][:,None,:]-oldb for x,y,z in bp]).min(axis=0).reshape(64,64)
        fa=np.stack([F3E[x][:,:,None]+F3T[y,z][:,None,:]-olda for x,y,z in ap]).min(axis=0).reshape(64,64)
        np.minimum(best,fb[:,:,None,None]+fa[None,None,:,:]+np.int16(s),out=best)
    for sw in (0,1):
        s0,s1=(t0,t1) if sw==0 else (t1,t0)
        group([(s0,s1,LM[t2,pp]) for pp in (1,2)],[(LM[s0,Z],LM[s1,c],o1ap) for c in (1,2)],-2)
        group([(LM[s0,Z],LM[s1,c],LM[t2,pp]) for c in (1,2) for pp in (1,2)],[(s0,s1,o1ap)],-2-2*ja)
        if ja: group([(s0,LM[s1,e],LM[t2,pp]) for e in (1,2) for pp in (1,2)],[(LM[s0,m0],LM[s1,m1],o1ap) for m0 in (1,2,3) for m1 in (1,2,3) if m1!=m0],-2)
        group([(LM[s0,m0],LM[s1,m1],t2) for m0 in (1,2,3) for m1 in (1,2,3) if m1!=m0],[(s0,LM[s1,e],LM[t2,l]) for e in (1,2) for l in (1,2)],-2)
    return best,oldb,olda


def vis_targets(ja,idx):
    cb,eb,ca,ea=(idx[:,k].astype(np.int64) for k in range(4)); t0b,t1b,t2b=cb//16,(cb//4)%4,cb%4; t0a,t1a,t2a=ca//16,(ca//4)%4,ca%4
    e0b,e1b=eb//4,eb%4; u0b,v0b=e0b//4,e0b%4; e0a,e1a=ea//4,ea%4; u0a,v0a=e0a//4,e0a%4
    t=np.empty((len(idx),3,2,2),dtype=np.int8); t[:,0,0,0]=t0b;t[:,0,0,1]=t0a;t[:,0,1,0]=t1b;t[:,0,1,1]=t1a;t[:,1,0,0]=u0b;t[:,1,0,1]=u0a;t[:,1,1,0]=t2b;t[:,1,1,1]=t2a;t[:,2,0,0]=v0b
    if ja==0: t[:,2,0,1]=LM[v0a,Z];t[:,2,1,0]=e1b;t[:,2,1,1]=LM[e1a,X]
    else: t[:,2,0,1]=v0a;t[:,2,1,0]=LM[e1b,X];t[:,2,1,1]=e1a
    return t


def build_visible():
    ts=[];olds=[];pds=[];counts=[];hist=Counter()
    for ja,rb,ra,p in itertools.product((0,1),(1,2),(1,2),(1,2)):
        b,ob,oa=pp_cell(ja,rb,ra,p); idx=np.argwhere(b>0); counts.append(len(idx)); cb,eb,ca,ea=(idx[:,k].astype(np.int64) for k in range(4)); d=b[cb,eb,ca,ea]; old=ob[cb,eb//4,eb%4]+oa[ca,ea//4,ea%4]
        ts.append(vis_targets(ja,idx));olds.append(old);pds.append(d);hist.update(int(x) for x in d)
    return np.concatenate(ts),np.concatenate(olds).astype(np.int16),np.concatenate(pds).astype(np.int16),tuple(counts),hist


def relocation(vis,hidden):
    vi=np.zeros((len(vis),8),dtype=np.int16); hi=np.zeros((len(hidden),8),dtype=np.int16); hh=np.full((len(hidden),8),99,dtype=np.int16); vq=np.full((2,len(vis),8),99,dtype=np.int16)
    for si,sg in enumerate(SIGMAS):
        v=np.zeros(len(vis),dtype=np.int16); h=np.zeros(len(hidden),dtype=np.int16)
        for br in (0,1):
            for q in (0,1):
                l=[vis[:,j,sg[j] if br==0 else 1-sg[j],q] for j in range(3)]; v+=F3[l[0],l[1],l[2]]
            cols=[j if (sg[j] if br==0 else 1-sg[j])==0 else j+3 for j in range(3)]; l=[hidden[:,cols[j]] for j in range(3)]; h+=F3[l[0],l[1],l[2]]
        vi[:,si]=v;hi[:,si]=h
        hb=np.full(len(hidden),99,dtype=np.int16)
        for s in (1,2,3):
            for rs in itertools.product(AC[s],repeat=3):
                v=np.zeros(len(hidden),dtype=np.int16)
                for br in (0,1):
                    l=[]
                    for j in range(3):
                        src=sg[j] if br==0 else 1-sg[j]; col=j if src==0 else j+3; l.append(LM[hidden[:,col],s if br==0 else rs[j]])
                    v+=F3[l[0],l[1],l[2]]
                hb=np.minimum(hb,v)
        hh[:,si]=hb
        for q in (0,1):
            other=1-q; vb=np.full(len(vis),99,dtype=np.int16)
            for s in (1,2,3):
                for rs in itertools.product(AC[s],repeat=3):
                    v=np.zeros(len(vis),dtype=np.int16)
                    for br in (0,1):
                        l=[]
                        for j in range(3):
                            src=sg[j] if br==0 else 1-sg[j];l.append(LM[vis[:,j,src,q],s if br==0 else rs[j]])
                        v+=F3[l[0],l[1],l[2]];l=[vis[:,j,sg[j] if br==0 else 1-sg[j],other] for j in range(3)];v+=F3[l[0],l[1],l[2]]
                    vb=np.minimum(vb,v)
            vq[q,:,si]=vb
    return vi,hi,hh,vq


def screen(vis,old,pd,hidden,oh,vi,hi,hh,vq):
    res=[];hist=Counter()
    for st in range(0,len(vis),500):
        n=min(500,len(vis)-st); new=np.full((n,len(hidden)),99,dtype=np.int16)
        for si in range(8):
            new=np.minimum(new,vq[0,st:st+n,si,None]+hi[None,:,si]);new=np.minimum(new,vq[1,st:st+n,si,None]+hi[None,:,si]);new=np.minimum(new,vi[st:st+n,si,None]+hh[None,:,si])
        d=new-old[st:st+n,None]-oh[None,:]-6; b=np.minimum(d,pd[st:st+n,None]); vals,cnts=np.unique(b,return_counts=True);hist.update({int(x):int(y) for x,y in zip(vals,cnts)});ii,jj=np.where(b>0);res.extend((st+int(i),int(j)) for i,j in zip(ii,jj))
    return res,hist


def dplus_templates():
    fr=[];sg=[];tc=[]
    for S in itertools.product(range(4),repeat=3):
        if S==(0,0,0):continue
        opts=[(q,s,r,p) for q,s in enumerate(S) if s for r in AC[s] for p in (0,1)]; tag=2*sum(int(x!=0) for x in S)
        for oo in itertools.product(opts,repeat=3):
            f=np.zeros((3,2,3),dtype=np.int8);ps=[]
            for j,(q,s,r,p) in enumerate(oo):f[j,0,q]=s;f[j,1,q]=r;ps.append(p)
            fr.append(f);sg.append(ps);tc.append(tag)
    return np.array(fr,dtype=np.int8),np.array(sg,dtype=np.int8),np.array(tc,dtype=np.int16)


def score_dplus(t,fr,sg,tc):
    outs=[]
    for st in range(0,len(t),100):
        tb=t[st:st+100];c=np.broadcast_to(tc,(len(tb),len(fr))).copy().astype(np.int16)
        for br in (0,1):
            for q in range(3):
                l=[]
                for j in range(3):src=sg[:,j] if br==0 else 1-sg[:,j];l.append(LM[tb[:,j,:,q][:,src],fr[:,j,br,q][None,:]])
                c+=F3[l[0],l[1],l[2]]
        outs.append(c.min(axis=1))
    return np.concatenate(outs)


def bprime_cost(t):
    n=3;union=[q for q in range(n) if any(int(t[j,b,q]) for j in range(3) for b in (0,1))];pool=list(union)
    for q in range(n):
        if q not in union:pool.append(q);break
    pool=sorted(pool);best=10**6
    for qt in list(union)+[q for q in pool if q not in union]:
        homes=[q for q in pool if q!=qt]
        if not homes:continue
        for v in (1,2,3):
            blocks=[]
            for j in range(3):
                rows=[]
                for c in (1,2,3):
                    if c==v:continue
                    for p in (0,1):
                        r0=[0]*3;r1=[0]*3;r0[qt]=v;r1[qt]=c;rows.append((0,np.array([[LM[int(t[j,p,q]),r0[q]] for q in pool],[LM[int(t[j,1-p,q]),r1[q]] for q in pool]],dtype=np.int8)))
                for h in homes:
                    for e in (1,2,3):
                        if e==v:continue
                        for m0 in (1,2,3):
                            for m1 in (1,2,3):
                                if m1==m0:continue
                                for p in (0,1):
                                    r0=[0]*3;r1=[0]*3;r0[h]=m0;r1[qt]=e;r1[h]=m1;rows.append((2,np.array([[LM[int(t[j,p,q]),r0[q]] for q in pool],[LM[int(t[j,1-p,q]),r1[q]] for q in pool]],dtype=np.int8)))
                ded=[]
                for ex in (0,2):
                    seen=set()
                    for e,r in rows:
                        if e==ex and r.tobytes() not in seen:seen.add(r.tobytes());ded.append((e,r))
                blocks.append(ded)
            ex=[np.array([x[0] for x in b],dtype=np.int16) for b in blocks];rr=[np.stack([x[1] for x in b]) for b in blocks];tot=ex[0][:,None,None]+ex[1][None,:,None]+ex[2][None,None,:]
            for br in (0,1):
                for qi in range(len(pool)):tot+=F3[rr[0][:,br,qi][:,None,None],rr[1][:,br,qi][None,:,None],rr[2][:,br,qi][None,None,:]]
            na=[int((e==0).sum()) for e in ex];tot[:na[0],:na[1],:na[2]]=999;best=min(best,int(tot.min())+2)
    return None if best>=10**6 else best


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=INPUT);ap.add_argument("--output",type=Path,default=OUT);args=ap.parse_args();src=json.loads(args.input.read_text())
    vis,old,pd,counts,ph=build_visible();hidden=np.array(list(itertools.product(range(4),repeat=6)),dtype=np.int8);oh=(F3[hidden[:,0],LM[hidden[:,1],Z],hidden[:,2]]+F3[hidden[:,3],LM[hidden[:,4],X],hidden[:,5]]).astype(np.int16);vi,hi,hh,vq=relocation(vis,hidden);res,rh=screen(vis,old,pd,hidden,oh,vi,hi,hh,vq)
    rv=np.array([x[0] for x in res],dtype=np.int32);ri=np.array([x[1] for x in res],dtype=np.int32);t=np.zeros((len(res),3,2,3),dtype=np.int8);t[:,:,:,0:2]=vis[rv];hv=hidden[ri]
    for j in range(3):t[:,j,0,2]=hv[:,j];t[:,j,1,2]=hv[:,j+3]
    cref=8+old[rv]+oh[ri];fr,sg,tc=dplus_templates();cd=score_dplus(t,fr,sg,tc);dd=cd.astype(int)-cref.astype(int);dh=Counter(dd);pos=np.flatnonzero(dd>0);bp=np.array([bprime_cost(t[i]) for i in pos],dtype=np.int16);bd=bp.astype(int)-cref[pos].astype(int)
    src_targets=[r["target_letters"] for r in src.get("bprime",{}).get("rows",[])]
    checks={"source_schema":src.get("schema")=="ORIONQG.QG7E.PPSinglePinner.v1","source_digest":verify_digest(src),"source_positive":src.get("terminal")==POS and src.get("all_gates") is True,"visible":len(vis)==32556==src.get("visible",{}).get("failures"),"visible_hist":ph==Counter({1:32116,2:440}),"cell_counts":counts==EXPECTED==tuple(src.get("visible",{}).get("cell_counts",[])),"hidden":len(hidden)==4096,"product":len(vis)*len(hidden)==133349376==src.get("product_domain"),"screen":len(res)==6488==src.get("relocation",{}).get("residual_count") and rh.get(1,0)==6488,"dplus_templates":len(fr)==61056==src.get("dplus",{}).get("template_count"),"dplus_hist":dh==Counter({-2:136,-1:3676,0:2652,1:24}) and src.get("dplus",{}).get("delta_histogram")=={"-2":136,"-1":3676,"0":2652,"1":24},"dplus_residual":len(pos)==24==src.get("dplus",{}).get("residual_count"),"bprime":Counter(bd)==Counter({-1:24}) and src.get("bprime",{}).get("delta_histogram")=={"-1":24},"bprime_targets_exact":src_targets==[t[i].tolist() for i in pos],"scope":src.get("PP_SINGLE_PINNER_ALL_N") is True and src.get("CHAIN_ALL_N") is False and src.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False,"authority":src.get("novelty_authority") is False and src.get("r6_authority") is False and src.get("physical_quantum_advantage_claim") is False}
    decision="ACCEPT_PP_SINGLE_PINNER_ALL_N" if all(checks.values()) else "REJECT";out={"schema":"ORIONQG.QG7E.GenericVerification.v1","decision":decision,"all_checks":bool(all(checks.values())),"checks":{k:bool(v) for k,v in checks.items()},"source_result_digest":src.get("result_digest"),"visible_failures":len(vis),"product_domain":len(vis)*len(hidden),"screen_residual":len(res),"dplus_template_count":len(fr),"dplus_delta_histogram":{str(k):int(v) for k,v in sorted(dh.items())},"dplus_residual":len(pos),"bprime_delta_histogram":{str(k):int(v) for k,v in sorted(Counter(bd).items())},"PP_SINGLE_PINNER_ALL_N":decision=="ACCEPT_PP_SINGLE_PINNER_ALL_N","CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":decision,"all_checks":out["all_checks"],"screen":len(res),"dplus":len(pos),"bprime_final":int((bd>0).sum())}));return 0
if __name__=="__main__":raise SystemExit(main())
"""Independent generic verifier for ORION-QG QG-7e (the twelve states).

Pure-primitive rebuild.  This file imports NOTHING from the analyzer lanes:
no `qg7c_classification`, no `qg7d_last_link`, no `qg7e_twelve_states`, no
`max_r6*`, no `qg5b/qg7b`.  The Pauli algebra is rebuilt from (x, z) bit pairs,
the F3 objective from its definition, the frame charge from the central-optimal
multiplier pair, the role inventory and geometry list from the frozen
protocol's role table, and the per-block target permutation group from its
definition.  P1E is re-derived with a deliberately different traversal
(grouped by the frame pattern at the SECOND comm-s2 qubit, coverage bitset
transposed), so an implementation bug in the lane script cannot reproduce
itself here.

Checks (all read-only; this verifier never writes a receipt):
  V1  primitives: multiplication / symplectic form / weight / F3 / charge
  V2  mirror identity on the complete 4^6 x 4^6 domain
  V3  letter-permutation gauge on the complete domain, all 6 permutations
  V4  geometry inventory rebuilt independently (roles, unordered pairs)
  V5  the per-block target permutation group rebuilt independently: eight
      involutions on the six target slots, PERM[0] = id, PERM[7] = SWAP
  V6  P1E re-derived for EVERY geometry with all eight permutations; the
      residue must be zero everywhere, matching the receipt geometry by
      geometry, and each of the twelve QG-7d residual states must be
      re-confirmed dominated by direct evaluation of the whole menu
  V7  the UN-enlarged lemma re-derived for the five residual geometries: it
      must reproduce the QG-7d receipt's twelve residual states row for row,
      so the enlargement and not an implementation difference is what closes
  V8  census dispatch arithmetic against the committed QG-7c census
  V9  referee bookkeeping (coverage, sandwich, gap rows) and E3a settlement
  V10 terminal selection re-derived from the receipt's own values
  V11 result digest recomputed from the receipt minus timing

Prints ACCEPT or REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

RESULTS = (Path(__file__).resolve().parents[2] / "research" / "extensions"
           / "orion-qg" / "QG7E_TWELVE_STATES_RESULTS.json")
QG7D_RESULTS = (Path(__file__).resolve().parents[2] / "research" / "extensions"
                / "orion-qg" / "QG7D_LAST_LINK_RESULTS.json")
PROTOCOL = Path(__file__).resolve().parent / "QG7E_TWELVE_STATES_PROTOCOL_V1.md"

COMMITTED_CENSUS = {
    "PA_ja0_delta1": 97072, "PA_ja0_delta2": 2376, "PA_ja1_delta1": 3600,
    "PP_ja0_delta1": 30500, "PP_ja0_delta2": 440, "PP_ja1_delta1": 1616,
}

# ---- V1: primitives rebuilt from (x, z) bits --------------------------------
# letter codes on the wire: 0 = I, 1 = X, 2 = Y, 3 = Z
BITS = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
CODE = {v: k for k, v in BITS.items()}


def mul(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return CODE[(ax ^ bx, az ^ bz)]


def sy(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return (ax * bz + az * bx) & 1


def wt(a: int) -> int:
    return 0 if a == 0 else 1


def f3(a: int, b: int, c: int) -> int:
    if a == b == c != 0:
        return 1
    return wt(a) + wt(b) + wt(c)


def charge(w0: int, w1: int) -> int:
    """Central-optimal per-block frame charge, normalised so (1,1) -> 0."""
    return min(2 * w0 + 4 * w1, 4 * w0 + 2 * w1) - 6


def v1_primitives() -> list[str]:
    bad = []
    for a in range(4):
        for b in range(4):
            if mul(a, b) != (b if a == 0 else a if b == 0 else
                             0 if a == b else 6 - a - b):
                bad.append(f"mul({a},{b})")
            if sy(a, b) != (1 if (a and b and a != b) else 0):
                bad.append(f"sy({a},{b})")
    for a in range(4):
        for b in range(4):
            for c in range(4):
                want = 1 if (a == b == c != 0) else wt(a) + wt(b) + wt(c)
                if f3(a, b, c) != want:
                    bad.append(f"f3({a},{b},{c})")
    for w0 in (1, 2):
        for w1 in (1, 2):
            if charge(w0, w1) != 4 * (min(w0, w1) - 1) + 2 * (max(w0, w1) - 1):
                bad.append(f"charge({w0},{w1})")
    return bad


IDX = np.arange(4096, dtype=np.int64)
DIG = [(IDX >> (2 * (5 - k))) & 3 for k in range(6)]
F3TAB = np.zeros((4, 4, 4), dtype=np.int8)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            F3TAB[_a, _b, _c] = f3(_a, _b, _c)
MUL = np.array([[mul(a, b) for b in range(4)] for a in range(4)],
               dtype=np.int64)
GTAB = (F3TAB[DIG[0], DIG[2], DIG[4]]
        + F3TAB[DIG[1], DIG[3], DIG[5]]).astype(np.int8)

# FP[frame pattern, state] = F3 total over the six composed letters
FP = np.empty((4096, 4096), dtype=np.int8)
for _fl in range(4096):
    _fd = [(_fl >> (2 * (5 - _k))) & 3 for _k in range(6)]
    _perm = np.zeros(4096, dtype=np.int64)
    for _k in range(6):
        _perm |= MUL[DIG[_k], _fd[_k]] << (2 * (5 - _k))
    FP[_fl] = GTAB[_perm]


def enc(letters) -> int:
    return sum(int(letters[k]) << (2 * (5 - k)) for k in range(6))


# ---- V5: the per-block target permutation group -----------------------------

def perm_index(p: int) -> np.ndarray:
    out = np.zeros(4096, dtype=np.int64)
    for k in range(6):
        j, e = k // 2, k % 2
        src = 2 * j + (1 - e) if (p >> j) & 1 else k
        out |= DIG[src] << (2 * (5 - k))
    return out


PERM = np.stack([perm_index(p) for p in range(8)])
SWAP = PERM[7]


def v5_permutation_group() -> list[str]:
    bad = []
    if not np.array_equal(PERM[0], IDX):
        bad.append("PERM[0] is not the identity")
    swap_direct = np.zeros(4096, dtype=np.int64)
    for k, src in enumerate((1, 0, 3, 2, 5, 4)):
        swap_direct |= DIG[src] << (2 * (5 - k))
    if not np.array_equal(PERM[7], swap_direct):
        bad.append("PERM[7] is not the global target swap")
    for p in range(8):
        if not np.array_equal(PERM[p][PERM[p]], IDX):
            bad.append(f"PERM[{p}] is not an involution")
    for p in range(8):
        for qv in range(8):
            if not np.array_equal(PERM[p][PERM[qv]], PERM[p ^ qv]):
                bad.append(f"group law {p},{qv}")
    return bad


# ---- V2 / V3 ----------------------------------------------------------------

def v2_mirror() -> int:
    bad = 0
    for fl in range(4096):
        fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
        fm = enc([fd[1], fd[0], fd[3], fd[2], fd[5], fd[4]])
        if not np.array_equal(FP[fm][SWAP], FP[fl]):
            bad += 1
    return bad


def v3_gauge() -> int:
    bad = 0
    for perm in itertools.permutations((1, 2, 3)):
        table = np.array([0, perm[0], perm[1], perm[2]], dtype=np.int64)
        pst = np.zeros(4096, dtype=np.int64)
        for k in range(6):
            pst |= table[DIG[k]] << (2 * (5 - k))
        for fl in range(4096):
            fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
            fp = enc([int(table[v]) for v in fd])
            if not np.array_equal(FP[fp][pst], FP[fl]):
                bad += 1
    return bad


# ---- V4: role inventory rebuilt from the protocol table ---------------------

def other(*ex):
    for c in (1, 2, 3):
        if c not in ex:
            return c
    raise AssertionError


def roles():
    out = []

    def add(name, loc, ext, cs2):
        out.append({"name": name, "loc": tuple(loc), "ext": tuple(ext),
                    "cs2": bool(cs2)})

    add("OUT_ANCH", (0, 0, 0, 0), (1, 1, 0, 1, 1), False)
    add("OUT_PHANTOM", (0, 0, 0, 0), (1, 2, 0, 1, 1), False)
    add("OUT_COMMS2", (0, 0, 0, 0), (2, 1, 0, 1, 1), True)
    for p in (1, 2):
        add(f"ANCH_B_{p}", (3, p, 0, 0), (0, 0, 0, 0, 0), False)
        add(f"ANCH_A_{p}", (0, 0, 3, p), (0, 0, 0, 0, 0), False)
        add(f"BORROW_B_{p}", (0, p, 0, 0), (1, 1, 0, 0, 1), False)
        add(f"BORROW_A_{p}", (0, 0, 0, p), (1, 1, 0, 0, 1), False)
        add(f"CS2_B_ANTIOUT_{p}", (p, 0, 0, 0), (1, 1, 1, 1, 1), True)
        add(f"CS2_B_ANTIB_{p}", (p, other(3, p), 0, 0), (1, 0, 1, 0, 0), True)
        add(f"CS2_A_ANTIOUT_{p}", (0, 0, p, 0), (1, 1, 1, 1, 1), True)
        add(f"CS2_A_ANTIA_{p}", (0, 0, p, other(3, p)), (1, 0, 1, 0, 0), True)
    for u in (1, 2):
        for v in (1, 2):
            add(f"CS2_BA_ANTIA_{u}{v}", (u, 0, v, other(3, v)),
                (0, 0, 0, 0, 0), True)
            add(f"CS2_BA_ANTIB_{u}{v}", (u, other(3, u), v, 0),
                (0, 0, 0, 0, 0), True)
    return out


OURS = {"name": "COMMS2_OURS", "loc": (1, 0, 1, 2), "ext": (0, 0, 0, 0, 0),
        "cs2": True}


def feasible_block(loc, ext, sb, sa, orient, allow_cs2):
    """Independent rebuild of the per-block option list."""
    w0e, w1e, s0e, s1e, xe = ext
    out = []
    sig = (sb, sa)
    for l0b in range(4):
        for l1b in range(4):
            for l0a in range(4):
                for l1a in range(4):
                    w0 = wt(l0b) + wt(l0a) + w0e
                    w1 = wt(l1b) + wt(l1a) + w1e
                    if not (1 <= w0 <= 2 and 1 <= w1 <= 2):
                        continue
                    if (sy(sb, l0b) + sy(sa, l0a) + s0e) % 2 != orient[0]:
                        continue
                    if (sy(sb, l1b) + sy(sa, l1a) + s1e) % 2 != orient[1]:
                        continue
                    if (sy(l0b, l1b) + sy(l0a, l1a) + xe) % 2 != 1:
                        continue
                    if not allow_cs2:
                        if orient[0] == 0:
                            f0, fw0, fw1 = (l0b, l0a), w0, w1
                            e_sy, e_w = s0e, w0e
                        else:
                            f0, fw0, fw1 = (l1b, l1a), w1, w0
                            e_sy, e_w = s1e, w1e
                        if fw0 == 2 and fw1 == 1 and e_sy == e_w and all(
                                sy(sig[q], f0[q]) == 1
                                for q in range(2) if f0[q]):
                            continue
                    out.append((l0b * 4 + l1b, l0a * 4 + l1a,
                                charge(w0, w1)))
    return out


def geometry_tables(r1, r2):
    bl = [OURS, r1, r2]
    xb = enc([b["loc"][k] for b in bl for k in (0, 1)])
    xa = enc([b["loc"][k] for b in bl for k in (2, 3)])
    base = 4
    for b in bl:
        l0b, l1b, l0a, l1a = b["loc"]
        base += charge(wt(l0b) + wt(l0a) + b["ext"][0],
                       wt(l1b) + wt(l1a) + b["ext"][1])
    return bl, FP[xb].astype(np.int16), FP[xa].astype(np.int16), base


def mirrored(b):
    l0b, l1b, l0a, l1a = b["loc"]
    w0, w1, s0, s1, xe = b["ext"]
    return {"name": b["name"], "loc": (l1b, l0b, l1a, l0a),
            "ext": (w1, w0, s1, s0, xe), "cs2": b["cs2"]}


def menu_streams(bl):
    """(branch, {(frame pattern at b, frame pattern at a): cost}) per branch."""
    out = []
    for branch in (0, 1):
        blocks = bl if branch == 0 else [mirrored(b) for b in bl]
        for orient in ((0, 1), (1, 0)):
            best = {}
            for sb in range(4):
                for sa in range(4):
                    opts = [feasible_block(b["loc"], b["ext"], sb, sa, orient,
                                           b["cs2"] and jj > 0)
                            for jj, b in enumerate(blocks)]
                    if any(not o for o in opts):
                        continue
                    tagw = 2 * (wt(sb) + wt(sa))
                    for o0 in opts[0]:
                        for o1 in opts[1]:
                            for o2 in opts[2]:
                                fb = o0[0] * 256 + o1[0] * 16 + o2[0]
                                fa = o0[1] * 256 + o1[1] * 16 + o2[1]
                                c = o0[2] + o1[2] + o2[2] + tagw
                                k = (fb, fa)
                                if k not in best or c < best[k]:
                                    best[k] = c
            out.append((branch, best))
    return out


def p1e_residue(r1, r2, perms=range(8)):
    """Independent re-derivation, grouped by the frame pattern at qubit a."""
    bl, XB, XA, baseX = geometry_tables(r1, r2)
    groups = []
    for branch, best in menu_streams(bl):
        bya = {}
        for (fb, fa), c in best.items():
            cur = bya.setdefault(fa, {})
            if fb not in cur or c < cur[fb]:
                cur[fb] = c
        for fa, parts in bya.items():
            for p in perms:
                groups.append((branch, int(p), fa, parts))
    covered_t = np.zeros((4096, 512), dtype=np.uint8)   # [s_a][bits over s_b]
    sparse = None

    def gamma_delta(branch, p, fa, parts):
        fbs = np.fromiter(parts.keys(), dtype=np.int64, count=len(parts))
        cs = np.fromiter(parts.values(), dtype=np.int16, count=len(parts))
        W = (FP[fbs].astype(np.int16) + cs[:, None]).min(axis=0)
        idx = PERM[p ^ (7 if branch else 0)]
        return (FP[fa][idx].astype(np.int16) - XA, XB - W[idx] + baseX)

    for pos, (branch, p, fa, parts) in enumerate(groups):
        gamma, delta = gamma_delta(branch, p, fa, parts)
        lo, hi = int(gamma.min()), int(gamma.max())
        masks = np.zeros((hi - lo + 1, 512), dtype=np.uint8)
        for v in range(lo, hi + 1):
            masks[v - lo] = np.packbits(delta >= v)
        covered_t |= masks[gamma - lo]
        if (pos + 1) % 128 == 0:
            cnt = int(4096 * 4096
                      - int(np.unpackbits(covered_t.reshape(-1)).sum()))
            if cnt == 0:
                break
            if cnt <= 50000:
                rows = np.argwhere(np.unpackbits(covered_t, axis=1) == 0)
                sa_l = rows[:, 0].astype(np.int64)
                sb_l = rows[:, 1].astype(np.int64)
                for g2 in groups[pos + 1:]:
                    if sb_l.size == 0:
                        break
                    ga, de = gamma_delta(*g2)
                    alive = ga[sa_l] > de[sb_l]
                    sa_l, sb_l = sa_l[alive], sb_l[alive]
                sparse = (sb_l, sa_l)
                break
    if sparse is None:
        rows = np.argwhere(np.unpackbits(covered_t, axis=1) == 0)
        sparse = (rows[:, 1].astype(np.int64), rows[:, 0].astype(np.int64))
    return sorted((int(b), int(a)) for b, a in zip(*sparse))


def direct_delta(r1, r2, sb_state, sa_state, perms=range(8)):
    """Brute force at one state -- no grouping, no bitsets, no coverage."""
    bl, XB, XA, baseX = geometry_tables(r1, r2)
    xcost = int(XB[sb_state]) + int(XA[sa_state]) + baseX
    best = 10 ** 6
    for branch, menu in menu_streams(bl):
        for p in perms:
            idx = PERM[p ^ (7 if branch else 0)]
            pb, pa = int(idx[sb_state]), int(idx[sa_state])
            for (fb, fa), c in menu.items():
                v = int(FP[fb][pb]) + int(FP[fa][pa]) + c
                if v < best:
                    best = v
    return best - xcost


# ---- main -------------------------------------------------------------------

def main() -> int:
    rec = json.loads(RESULTS.read_text())
    qg7d = json.loads(QG7D_RESULTS.read_text())
    fail: list[str] = []
    checks: dict[str, object] = {}

    # V1
    bad = v1_primitives()
    checks["V1_primitives"] = "ok" if not bad else bad[:8]
    if bad:
        fail.append("V1")

    # V2
    n_bad = v2_mirror()
    checks["V2_mirror_failures"] = n_bad
    if n_bad or int(rec["g2_mirror_identity"]["domain_size"]) != 16777216:
        fail.append("V2")

    # V3
    n_bad = v3_gauge()
    checks["V3_gauge_failures"] = n_bad
    if n_bad or int(rec["g3_gauge_permutations"]["domain_size"]) != 6 * 4096 * 4096:
        fail.append("V3")

    # V4
    rl = roles()
    names = [r["name"] for r in rl]
    pairs = list(itertools.combinations_with_replacement(range(len(rl)), 2))
    checks["V4_roles"] = len(rl)
    checks["V4_geometries"] = len(pairs)
    if (len(rl) != 27 or len(pairs) != 378
            or names != rec["p1e_domination_lemma"]["roles"]
            or int(rec["p1e_domination_lemma"]["geometry_count"]) != 378
            or int(rec["p1e_domination_lemma"]["total_states"]) != 6341787648):
        fail.append("V4")

    # V5
    bad = v5_permutation_group()
    checks["V5_permutation_group"] = "ok" if not bad else bad[:8]
    if bad or int(rec["p1e_domination_lemma"]["permutations_admitted"]) != 8:
        fail.append("V5")

    # V6: P1E for every geometry
    by_name = {r["name"]: r for r in rl}
    residue_total = 0
    geom_bad = []
    per_geom = {tuple(g["geometry"]): g for g in
                rec["p1e_domination_lemma"]["per_geometry"]}
    if len(per_geom) != 378:
        fail.append("V6_geometry_count")
    for i, j in pairs:
        rows = p1e_residue(rl[i], rl[j])
        residue_total += len(rows)
        g = per_geom.get((rl[i]["name"], rl[j]["name"]))
        if g is None or int(g["residue"]) != len(rows) \
                or int(g["state_domain"]) != 16777216:
            geom_bad.append([rl[i]["name"], rl[j]["name"], len(rows)])
    checks["V6_p1e_residue_total"] = residue_total
    checks["V6_geometry_mismatches"] = geom_bad[:8]
    if residue_total != 0 or geom_bad \
            or int(rec["p1e_domination_lemma"]["residue_total"]) != 0 \
            or int(rec["p1e_domination_lemma"]["geometries_closed"]) != 378:
        fail.append("V6")

    # V6b: the twelve QG-7d states re-confirmed dominated, brute force
    twelve = []
    for g in qg7d["p1_domination_lemma"]["per_geometry"]:
        for r in g.get("residue_rows_verbatim", []):
            twelve.append((tuple(g["geometry"]), int(r["state_b"]),
                           int(r["state_a"])))
    deltas = []
    for geom, sb, sa in twelve:
        d = direct_delta(by_name[geom[0]], by_name[geom[1]], sb, sa)
        deltas.append(d)
    checks["V6b_twelve_states"] = len(twelve)
    checks["V6b_deltas"] = deltas
    if len(twelve) != 12 or any(d > 0 for d in deltas):
        fail.append("V6b")
    e3a_rows = {(tuple(r["geometry"]), r["state_b"], r["state_a"]): r
                for r in rec["e3a_local_settlement"]["rows"]}
    for (geom, sb, sa), d in zip(twelve, deltas):
        r = e3a_rows.get((geom, sb, sa))
        if r is None or int(r["delta"]) != d:
            fail.append("V6b_e3a_delta")
            break

    # V7: the un-enlarged lemma must reproduce QG-7d's twelve rows
    want = {}
    for geom, sb, sa in twelve:
        want.setdefault(geom, []).append((sb, sa))
    v7_bad = []
    v7_total = 0
    for geom in sorted(want):
        rows = p1e_residue(by_name[geom[0]], by_name[geom[1]], perms=(0,))
        v7_total += len(rows)
        if rows != sorted(want[geom]):
            v7_bad.append([list(geom), rows, sorted(want[geom])])
    checks["V7_unenlarged_residue_total"] = v7_total
    checks["V7_mismatches"] = v7_bad[:4]
    r1 = rec["r1_qg7d_residue_reproduction"]
    if v7_total != 12 or v7_bad or not r1["holds"] \
            or int(r1["residue_total"]) != 12 \
            or int(r1["state_domain_total"]) != 5 * 16777216:
        fail.append("V7")

    # V8: census dispatch arithmetic
    t4b = rec["inherited_lemmas"]["t4b_pinned_summary"]
    p2s = rec["p2_state_level_dispatch"]
    ok8 = (t4b["failing_census"] == COMMITTED_CENSUS
           and int(t4b["domain_size"]) == 536870912
           and int(t4b["failures_total"]) == 135604
           and int(t4b["worst_delta"]) == 2
           and sum(COMMITTED_CENSUS.values()) == 135604
           and int(p2s["patterns_dispatched_closed"]) == 135604
           and int(p2s["patterns_open"]) == 0
           and bool(p2s["dispatch_sums_to_census"])
           and bool(rec["p2_verbatim_dispatch"]["all_dispatched"]))
    checks["V8_census"] = ok8
    if not ok8:
        fail.append("V8")

    # V9: referee bookkeeping and E3a settlement
    ref = rec["referee"]
    e3a = rec["e3a_local_settlement"]
    counted = (len(rec["p3_hostile_arm"]["c1_census_realizations"]["rows"])
               + sum(v["instances"] for v in
                     rec["p3_hostile_arm"]["c2_dense_random_control"].values())
               + len(rec["p3_hostile_arm"]["c3_qg7d_residue_panel"]["rows"])
               + rec["e3b_realized_referee"]["spare_realizations"]["instances"]
               + rec["e3b_realized_referee"]["third_qubit_complete_sweep"]
                    ["instances"])
    ok9 = (int(ref["rows"]) == int(ref["dxx_witness_rows"]) == counted
           and not ref["sandwich_failures"] and not ref["dxx_witness_failures"]
           and not ref["replay_failures"] and int(ref["gap_rows_total"]) == 0
           and int(e3a["states_settled"]) == 12
           and all(int(r["delta"]) <= 0 for r in e3a["rows"])
           and all(int(r["comm_s2_count_alternative"])
                   < int(r["comm_s2_count_original"]) for r in e3a["rows"]))
    checks["V9_referee_rows"] = int(ref["rows"])
    checks["V9_recount"] = counted
    checks["V9_ok"] = ok9
    if not ok9:
        fail.append("V9")

    # V9b: every realized row satisfies the sandwich and shows gap 0
    sand = 0
    gaps = 0
    for blockname, rows in (
            ("c1", rec["p3_hostile_arm"]["c1_census_realizations"]["rows"]),
            ("c3", rec["p3_hostile_arm"]["c3_qg7d_residue_panel"]["rows"]),
            ("e3b_spare",
             rec["e3b_realized_referee"]["spare_realizations"]["rows"]),
            ("e3b_sweep",
             rec["e3b_realized_referee"]["third_qubit_complete_sweep"]["rows"])):
        for r in rows:
            fam = [r["C_Dplus"]]
            for k in ("f_Bprime", "f_Bsecond"):
                if r[k] is not None:
                    fam.append(r[k])
            if any(int(r["C_Dxx"]) > int(v) for v in fam):
                sand += 1
            if int(r["C_Dxx"]) - min(int(v) for v in fam) != int(r["gap"]):
                sand += 1
            if int(r["gap"]) != 0:
                gaps += 1
    checks["V9b_sandwich_violations"] = sand
    checks["V9b_nonzero_gaps"] = gaps
    if sand or gaps:
        fail.append("V9b")

    # V10: terminal selection re-derived
    gates = rec["gates"]
    integrity = all(bool(v) for v in gates.values())
    if integrity and int(ref["gap_rows_total"]) == 0 \
            and bool(rec["p1e_domination_lemma"]["holds"]) \
            and bool(rec["p2_state_level_dispatch"]["holds"]) \
            and bool(rec["p2_verbatim_dispatch"]["all_dispatched"]) \
            and bool(e3a["holds"]):
        want_terminal = "QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
    elif not integrity or int(ref["gap_rows_total"]) > 0:
        want_terminal = "QG7E_CANNOT_CHECK"
    elif not bool(rec["p1e_domination_lemma"]["holds"]):
        want_terminal = "QG7E_PARTIAL__P1E_RESIDUE_OPEN"
    elif not bool(e3a["holds"]):
        want_terminal = "QG7E_PARTIAL__E3_RESIDUE_OPEN"
    else:
        want_terminal = "QG7E_PARTIAL__CENSUS_RESIDUE_OPEN"
    checks["V10_terminal_expected"] = want_terminal
    checks["V10_terminal_receipt"] = rec["terminal"]
    if rec["terminal"] != want_terminal or "NOT_R6" not in rec["authority"] \
            or rec["r6_authority"] or rec["novelty_credit"] \
            or rec["donor_novelty_credit"] or rec["chemistry_data_read"] \
            or rec["reserved_stretched_n2_accessed"]:
        fail.append("V10")

    # V11: digest and protocol hash
    body = {k: v for k, v in rec.items()
            if k not in ("timing", "result_digest")}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"),
                   allow_nan=False).encode()).hexdigest()
    proto = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    checks["V11_digest_match"] = digest == rec["result_digest"]
    checks["V11_protocol_match"] = proto == rec["protocol_sha256"]
    if digest != rec["result_digest"] or proto != rec["protocol_sha256"]:
        fail.append("V11")

    print("QG7E_GENERIC_VERIFY=" + json.dumps(
        {"checks": checks, "failed": fail,
         "decision": "ACCEPT" if not fail else "REJECT"},
        sort_keys=True, separators=(",", ":")))
    print("ACCEPT" if not fail else "REJECT")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
