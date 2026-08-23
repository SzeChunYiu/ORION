#!/usr/bin/env python3
"""Official QG-7e V2 corrected PP single-pinner confirmatory analyzer."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];QG=ROOT/"research/extensions/orion-qg";sys.path.insert(0,str(QG))
import qg7e_pp_single_pinner as v1  # noqa:E402
PROTOCOL=ROOT/"development/orion-qg-regime-geometry/QG7E_V2_PP_SINGLE_PINNER_PROTOCOL.md";PARENT=QG/"QG7C_CLASSIFICATION_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg7e-v2-pp-single-pinner.json";TOKEN="ORIONQG_QG7E_V2=";POS="QG7E_V2_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN";PD="0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def corrected(ja,idx):
 cb,eb,ca,ea=(idx[:,k].astype(np.int64) for k in range(4));t0b,t1b,t2b=cb//16,(cb//4)%4,cb%4;t0a,t1a,t2a=ca//16,(ca//4)%4,ca%4;e0b,e1b=eb//4,eb%4;u0b,v0b=e0b//4,e0b%4;e0a,e1a=ea//4,ea%4;u0a,v0a=e0a//4,e0a%4;t=np.empty((len(idx),3,2,2),dtype=np.int8);t[:,0,0,0]=t0b;t[:,0,0,1]=t0a;t[:,0,1,0]=t1b;t[:,0,1,1]=t1a;t[:,1,0,0]=u0b;t[:,1,0,1]=u0a;t[:,1,1,0]=t2b;t[:,1,1,1]=t2a
 if ja==0:t[:,2,0,0]=v0b;t[:,2,0,1]=v1.LM[v0a,v1.Z];t[:,2,1,0]=e1b;t[:,2,1,1]=v1.LM[e1a,v1.X]
 else:t[:,2,0,0]=v1.LM[v0b,v1.Z];t[:,2,0,1]=v0a;t[:,2,1,0]=v1.LM[e1b,v1.X];t[:,2,1,1]=e1a
 return t
v1.visible_targets=corrected
def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();parent=json.loads(PARENT.read_text());vis,old,pd,param,cells,ph=v1.build_visible();hidden=np.array(list(itertools.product(range(4),repeat=6)),dtype=np.int8);oh=(v1.F3[hidden[:,0],v1.LM[hidden[:,1],v1.Z],hidden[:,2]]+v1.F3[hidden[:,3],v1.LM[hidden[:,4],v1.X],hidden[:,5]]).astype(np.int16);vi,hi,hh,vq=v1.relocation_tables(vis,hidden);res,sh,smax=v1.screen_product(vis,old,pd,hidden,oh,vi,hi,hh,vq);rv=np.array([a for a,b in res],dtype=np.int32);rh=np.array([b for a,b in res],dtype=np.int32);full=np.zeros((len(res),3,2,3),dtype=np.int8);full[:,:,:,0:2]=vis[rv];hv=hidden[rh]
 for j in range(3):full[:,j,0,2]=hv[:,j];full[:,j,1,2]=hv[:,j+3]
 cref=(8+old[rv]+oh[rh]).astype(np.int16);fr,sg,tc=v1.dplus_templates();cd=v1.score_dplus(full,fr,sg,tc);dd=cd.astype(np.int32)-cref.astype(np.int32);dh=Counter(int(z) for z in dd);pos=np.flatnonzero(dd>0)
 ctl=[];cf=[]
 ids=list(map(int,pos[:3]));
 for d in (-2,-1,0):
  z=np.flatnonzero(dd==d)
  if len(z):ids.append(int(z[0]))
 for rid in ids:
  tp=v1.target_pairs(full[rid]);prod=int(v1.q7c.r6p.dxx_search(tp,3,max_weight=1)["C_Dxx"]);ok=prod==int(cd[rid]);ctl.append({"i":rid,"delta":int(dd[rid]),"vectorized":int(cd[rid]),"production":prod,"ok":bool(ok)});cf+=[] if ok else [rid]
 rows=[];bh=Counter();bf=[];rf=[]
 for rid in map(int,pos):
  tp=v1.target_pairs(full[rid]);val,wit=v1.q7c.qg5b.bprime_family_min(tp,3,want_witness=True);val=None if val is None else int(val);bd=None if val is None else val-int(cref[rid]);ok=bool(val is not None and v1.q7c.qg5b.verify_bprime_witness(tp,3,wit));bh.update([999 if bd is None else bd]);bf+=[] if ok else [rid];frames,tag=v1.reference_frames(param[rv[rid]]);acc,labels=v1.q7c.r6s.config_labels(frames,tag);t6=(tp[0][0],tp[0][1],tp[1][0],tp[1][1],tp[2][0],tp[2][1]);rc=int(v1.q7c.r6s.config_cost(t6,frames,tag,(0,1,1),3)) if acc else None;rok=bool(acc and labels==(0,1) and rc==int(cref[rid]));rf+=[] if rok else [rid];rows.append({"i":rid,"visible":int(rv[rid]),"hidden":int(rh[rid]),"target":full[rid].tolist(),"reference_cost":int(cref[rid]),"dplus_cost":int(cd[rid]),"bprime_cost":val,"bprime_delta":bd,"bprime_verified":ok,"reference_verified":rok,"bprime_witness":wit})
 gates={"protocol":PROTOCOL.exists(),"parent":parent.get("result_digest")==PD and parent.get("terminal")=="QG7C_PARTIAL__L4B_OPEN","visible":len(vis)==32556 and ph==Counter({1:32116,2:440}) and tuple(cells)==v1.EXPECTED_CELL_COUNTS,"hidden":len(hidden)==4096 and len(vis)*len(hidden)==133349376,"screen":len(res)==5684 and smax==1 and sh.get(1,0)==5684,"dplus_templates":len(fr)==61056,"dplus_hist":dh==Counter({-2:132,-1:2456,0:2716,1:380}),"dplus_residual":len(pos)==380,"dplus_controls":not cf,"bprime":len(rows)==380 and bh==Counter({-1:380}) and not bf,"reference":not rf,"final":all(r["bprime_delta"] is not None and r["bprime_delta"]<=0 for r in rows)}
 term=POS if all(gates.values()) else ("QG7E_V2_REFERENCE_BINDING_GAP" if not gates["reference"] else "QG7E_V2_RELOCATION_FINGERPRINT_MISMATCH" if not gates["screen"] else "QG7E_V2_DPLUS_FINGERPRINT_MISMATCH" if not gates["dplus_hist"] or not gates["dplus_residual"] else "QG7E_V2_BPRIME_HANDOFF_REFUTED" if not gates["bprime"] or not gates["final"] else "QG7E_V2_CANNOT_CHECK")
 out={"schema":"ORIONQG.QG7E.V2.PPSinglePinner.v1","issue":"SzeChunYiu/ORION#872","terminal":term,"protocol_sha256":sha(PROTOCOL),"parent_qg7c_digest":parent.get("result_digest"),"visible":{"failures":len(vis),"hist":{str(k):v for k,v in sorted(ph.items())},"cells":list(cells)},"hidden_domain":len(hidden),"product_domain":len(vis)*len(hidden),"relocation":{"library":576,"residual":len(res),"hist":{"1":sh.get(1,0)}},"dplus":{"templates":len(fr),"hist":{str(k):v for k,v in sorted(dh.items())},"residual":len(pos),"controls":ctl,"control_failures":cf},"bprime":{"rows":rows,"hist":{str(k):v for k,v in sorted(bh.items())},"witness_failures":bf,"reference_failures":rf,"final_residual":sum(int(r["bprime_delta"] is None or r["bprime_delta"]>0) for r in rows)},"gates":{k:bool(v) for k,v in gates.items()},"all_gates":bool(all(gates.values())),"PP_SINGLE_PINNER_ALL_N":term==POS,"CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False,"protected_subject_read":False};u=dict(out);out["result_digest"]=hashlib.sha256(canon(u).encode()).hexdigest();x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"screen":len(res),"dplus":len(pos),"bprime_final":out["bprime"]["final_residual"],"reference_failures":len(rf),"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
