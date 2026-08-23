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
