#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-7e V2 corrected binding."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qg7e_generic_verify as g1
ROOT=Path(__file__).resolve().parents[2];INPUT=ROOT/"artifacts/orion-qg-qg7e-v2-pp-single-pinner.json";OUT=ROOT/"artifacts/orion-qg-qg7e-v2-generic-verification.json";TOKEN="ORIONQG_QG7E_V2_GENERIC=";POS="QG7E_V2_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def vd(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def corrected(ja,idx):
 cb,eb,ca,ea=(idx[:,k].astype(np.int64) for k in range(4));t0b,t1b,t2b=cb//16,(cb//4)%4,cb%4;t0a,t1a,t2a=ca//16,(ca//4)%4,ca%4;e0b,e1b=eb//4,eb%4;u0b,v0b=e0b//4,e0b%4;e0a,e1a=ea//4,ea%4;u0a,v0a=e0a//4,e0a%4;t=np.empty((len(idx),3,2,2),dtype=np.int8);t[:,0,0,0]=t0b;t[:,0,0,1]=t0a;t[:,0,1,0]=t1b;t[:,0,1,1]=t1a;t[:,1,0,0]=u0b;t[:,1,0,1]=u0a;t[:,1,1,0]=t2b;t[:,1,1,1]=t2a
 if ja==0:t[:,2,0,0]=v0b;t[:,2,0,1]=g1.LM[v0a,g1.Z];t[:,2,1,0]=e1b;t[:,2,1,1]=g1.LM[e1a,g1.X]
 else:t[:,2,0,0]=g1.LM[v0b,g1.Z];t[:,2,0,1]=v0a;t[:,2,1,0]=g1.LM[e1b,g1.X];t[:,2,1,1]=e1a
 return t
g1.vis_targets=corrected
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=INPUT);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();src=json.loads(x.input.read_text());vis,old,pd,cells,ph=g1.build_visible();hidden=np.array(list(itertools.product(range(4),repeat=6)),dtype=np.int8);oh=(g1.F3[hidden[:,0],g1.LM[hidden[:,1],g1.Z],hidden[:,2]]+g1.F3[hidden[:,3],g1.LM[hidden[:,4],g1.X],hidden[:,5]]).astype(np.int16);vi,hi,hh,vq=g1.relocation(vis,hidden);res,rh=g1.screen(vis,old,pd,hidden,oh,vi,hi,hh,vq);rv=np.array([a for a,b in res],dtype=np.int32);ri=np.array([b for a,b in res],dtype=np.int32);t=np.zeros((len(res),3,2,3),dtype=np.int8);t[:,:,:,0:2]=vis[rv];hv=hidden[ri]
 for j in range(3):t[:,j,0,2]=hv[:,j];t[:,j,1,2]=hv[:,j+3]
 cref=8+old[rv]+oh[ri];fr,sg,tc=g1.dplus_templates();cd=g1.score_dplus(t,fr,sg,tc);dd=cd.astype(int)-cref.astype(int);dh=Counter(int(z) for z in dd);pos=np.flatnonzero(dd>0);bp=np.array([g1.bprime_cost(t[int(i)]) for i in pos],dtype=np.int16);bd=bp.astype(int)-cref[pos].astype(int);src_targets=[r["target"] for r in src.get("bprime",{}).get("rows",[])]
 checks={"source":src.get("schema")=="ORIONQG.QG7E.V2.PPSinglePinner.v1" and vd(src) and src.get("terminal")==POS and src.get("all_gates") is True,"visible":len(vis)==32556 and ph==Counter({1:32116,2:440}) and tuple(cells)==g1.EXPECTED,"product":len(vis)*len(hidden)==133349376,"screen":len(res)==5684 and rh.get(1,0)==5684,"dplus":len(fr)==61056 and dh==Counter({-2:132,-1:2456,0:2716,1:380}) and len(pos)==380,"bprime":Counter(int(z) for z in bd)==Counter({-1:380}),"targets":src_targets==[t[int(i)].tolist() for i in pos],"scope":src.get("PP_SINGLE_PINNER_ALL_N") is True and src.get("CHAIN_ALL_N") is False and src.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False,"authority":src.get("novelty_authority") is False and src.get("r6_authority") is False and src.get("physical_quantum_advantage_claim") is False};ok=all(checks.values());o={"schema":"ORIONQG.QG7E.V2.GenericVerification.v1","decision":"ACCEPT_PP_SINGLE_PINNER_ALL_N" if ok else "REJECT","all_checks":bool(ok),"checks":{k:bool(v) for k,v in checks.items()},"source_result_digest":src.get("result_digest"),"screen_residual":len(res),"dplus_hist":{str(k):v for k,v in sorted(dh.items())},"dplus_residual":len(pos),"bprime_hist":{str(k):v for k,v in sorted(Counter(int(z) for z in bd).items())},"PP_SINGLE_PINNER_ALL_N":bool(ok),"CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":o["decision"],"all_checks":o["all_checks"],"screen":len(res),"dplus":len(pos),"bprime_final":int((bd>0).sum())}));return 0
if __name__=="__main__":raise SystemExit(main())
