#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-33 SixLCU label-vs-value census."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/orion-qg-qg33-sixlcu-label-value.json";Q12=ROOT/"research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json";Q15=ROOT/"research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg33-generic-verification.json";TOKEN="ORIONQG_QG33_GENERIC="
FEATURES=("maxg2","best2","best3","maxg3","maxg4","maxg5","g6","W","wF6","maxwt","maxpair")
PAIR=[(1<<i)|(1<<j) for i,j in itertools.combinations(range(6),2)];DISJ=[(a,b) for a,b in itertools.combinations(PAIR,2) if not(a&b)];MATCH=[(a,b,c) for a,b,c in itertools.combinations(PAIR,3) if not(a&b or a&c or b&c) and (a|b|c)==63];TRI=[sum(1<<i for i in z) for z in itertools.combinations(range(6),3)];QUAD=[63^p for p in PAIR];QUINT=[63^(1<<i) for i in range(6)]
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def wt(c,n=2):return sum(1 for q in range(n) if ((c>>(2*q))&3)!=0)
def calc(codes):
 wts=[wt(c) for c in codes];W=sum(wts);sw=[0]*64;wf=[0]*64
 for mask in range(1,64):
  low=mask&-mask;sw[mask]=sw[mask^low]+wts[low.bit_length()-1]
 for q in range(2):
  mv=[0,0,0,0]
  for i,c in enumerate(codes):mv[(c>>(2*q))&3]|=1<<i
  for mask in range(1,64):
   low=mask&-mask;v=(codes[low.bit_length()-1]>>(2*q))&3
   if v and (mask&~mv[v])==0:wf[mask]+=1
 g={m:4*wf[m]-sw[m] for m in PAIR};maxg2=max(g.values());best2=max(g[a]+g[b]+1 for a,b in DISJ);best3=max(g[a]+g[b]+g[c]+2 for a,b,c in MATCH);maxg3=max(10*wf[m]-2*sw[m]-1 for m in TRI);maxg4=max(14*wf[m]-2*sw[m]-1 for m in QUAD);maxg5=max(23*wf[m]-3*sw[m]-3 for m in QUINT);g6=23*wf[63]-2*W+1;delta=max(0,maxg2,best2,best3,maxg3,maxg4,maxg5,g6);CU=2*W+15;CF=CU-delta;p0=maxg2<=0 and best2<=0 and best3<=0;vec=(maxg2,best2,best3,maxg3,maxg4,maxg5,g6,W,wf[63],max(wts),max(wf[p] for p in PAIR));return {"C_U":CU,"C_F":CF,"Delta":delta,"P0":p0,"label":delta==0,"vec":vec}
def lit(res):return res["sixlcu"]["minerr_surface"]["K1_D1"]["witness"]["conjunctions"][0][0]
def eval_lit(vec,L):
 i=FEATURES.index(L["feature"]);v=vec[i];t=L["threshold"];flag=v==t if L["op"]=="==" else (v<=t if L["op"]=="<=" else v>=t);return not flag if L.get("negated") else flag
def hj(c):return {str(k):int(v) for k,v in sorted(c.items())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());q12=json.loads(Q12.read_text());q15=json.loads(Q15.read_text());L=lit(q15);dh=Counter();binary={False:Counter(),True:Counter()};fc=defaultdict(Counter);first={};fex={};rows=0;conf=[0,0,0,0];pconf=[0,0,0,0]
 for codes in itertools.combinations_with_replacement(range(1,16),6):
  r=calc(codes);pr=bool(eval_lit(r["vec"],L));lab=r["label"];p0=r["P0"];d=r["Delta"];rows+=1;dh[d]+=1;binary[pr][d]+=1;fc[r["vec"]][d]+=1
  idx=0 if pr and lab else (1 if pr and not lab else (2 if (not pr) and lab else 3));conf[idx]+=1;idx=0 if p0 and lab else (1 if p0 and not lab else (2 if (not p0) and lab else 3));pconf[idx]+=1
  first.setdefault((pr,d),{"codes":list(codes),"C_U":r["C_U"],"C_F":r["C_F"],"Delta":d,"A_label":pr,"P0":p0,"label":lab,"feature_vector":list(r["vec"])});fex.setdefault((r["vec"],d),{"codes":list(codes),"C_U":r["C_U"],"C_F":r["C_F"],"Delta":d,"feature_vector":list(r["vec"]),"A_label":pr,"P0":p0})
 ls=all(len(c)<=1 for c in binary.values());lp=None
 if not ls:
  cands=[]
  for flag in (False,True):
   for a,b in itertools.combinations(sorted(binary[flag]),2):cands.append(sorted((first[(flag,a)],first[(flag,b)]),key=lambda x:tuple(x["codes"])))
  lp=min(cands,key=lambda p:(tuple(p[0]["codes"]),tuple(p[1]["codes"])))
 mixed=sorted(((v,c) for v,c in fc.items() if len(c)>1),key=lambda x:x[0]);floor=sum(sum(c.values())-max(c.values()) for c in fc.values());fp=None
 if mixed:
  v,c=mixed[0];a,b=sorted(c)[:2];fp={"feature_vector":list(v),"delta_histogram":hj(c),"example_1":fex[(v,a)],"example_2":fex[(v,b)]}
 fs=not mixed;parent=q12.get("terminal")=="QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED" and q15.get("q3",{}).get("E_floor")==0
 expected={"instance_count":rows,"delta_histogram":hj(dh),"binary_label_delta_histograms":{"false":hj(binary[False]),"true":hj(binary[True])},"LABEL_QUOTIENT_VALUE_SUFFICIENT":ls,"label_value_separation_witness":lp,"feature_cell_count":len(fc),"mixed_delta_cell_count":len(mixed),"floor":floor,"first_mixed":fp,"FULL_FEATURE_VECTOR_VALUE_SUFFICIENT":fs,"label_confusion":{"TP":conf[0],"FP":conf[1],"FN":conf[2],"TN":conf[3],"errors":conf[1]+conf[2]},"p0_confusion":{"TP":pconf[0],"FP":pconf[1],"FN":pconf[2],"TN":pconf[3],"errors":pconf[1]+pconf[2]}}
 sf=src.get("full_feature_vector",{});checks={"source_digest":valid(src),"parent":parent,"rows":rows==38760==src.get("instance_count"),"literal":src.get("label_literal")==L,"delta_hist":src.get("delta_histogram")==expected["delta_histogram"],"binary":src.get("binary_label_delta_histograms")==expected["binary_label_delta_histograms"],"label_suff":src.get("LABEL_QUOTIENT_VALUE_SUFFICIENT") is ls,"label_witness":src.get("label_value_separation_witness")==lp,"label_confusion":src.get("label_confusion")==expected["label_confusion"],"p0_confusion":src.get("p0_confusion")==expected["p0_confusion"],"feature_counts":sf.get("cell_count")==len(fc) and sf.get("mixed_delta_cell_count")==len(mixed) and sf.get("irreducible_exact_value_error_floor")==floor,"feature_witness":sf.get("first_mixed_delta_cell")==fp,"feature_suff":src.get("FULL_FEATURE_VECTOR_VALUE_SUFFICIENT") is fs,"no_invention":src.get("NO_POST_OUTCOME_FEATURE_INVENTION") is True,"scope":all(src.get(k) is False for k in ("ALL_N_VALUE_THEOREM","GLOBAL_PREDICATE_MINIMALITY","NEW_FEATURE_VOCABULARY_AUTHORITY","novelty_authority","physical_quantum_advantage_claim"))};ok=all(checks.values());decision="ACCEPT_LABEL_VALUE_SEPARATION" if ok and not ls else ("ACCEPT_LABEL_VALUE_SUFFICIENCY" if ok and ls else "REJECT");out={"schema":"ORIONQG.QG33.GenericVerification.v1","decision":decision,"all_checks":bool(ok),"checks":checks,"independent":{"instance_count":rows,"delta_histogram":expected["delta_histogram"],"LABEL_QUOTIENT_VALUE_SUFFICIENT":ls,"FULL_FEATURE_VECTOR_VALUE_SUFFICIENT":fs,"feature_cell_count":len(fc),"mixed_delta_cell_count":len(mixed),"irreducible_exact_value_error_floor":floor},"source_result_digest":src.get("result_digest"),"ALL_N_VALUE_THEOREM":False,"GLOBAL_PREDICATE_MINIMALITY":False,"NEW_FEATURE_VOCABULARY_AUTHORITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":decision,"all_checks":ok,"instances":rows,"delta_values":len(dh),"label_value_sufficient":ls,"feature_value_sufficient":fs,"feature_cells":len(fc),"mixed_feature_cells":len(mixed),"floor":floor}));return 0
if __name__=="__main__":raise SystemExit(main())
