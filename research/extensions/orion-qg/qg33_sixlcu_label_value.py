#!/usr/bin/env python3
"""QG-33 production analyzer: SixLCU exact label-vs-value quotient on complete n=2."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
QDIR=ROOT/"research/extensions/orion-qg";sys.path.insert(0,str(QDIR))
import qg4_second_family as qg4  # noqa:E402
import qg15b_predicate_language as qg15b  # noqa:E402

PROTO=ROOT/"development/orion-qg-regime-geometry/QG33_SIXLCU_LABEL_VALUE_PROTOCOL_V1.md"
Q12=QDIR/"QG12_SIXLCU_P0_THEOREM_RESULTS.json"
Q15=QDIR/"QG15B_PREDICATE_LANGUAGE_RESULTS.json"
OUT=ROOT/"artifacts/orion-qg-qg33-sixlcu-label-value.json"
TOKEN="ORIONQG_QG33="
SEP="QG33_SIXLCU_EXACT_LABEL_QUOTIENT_IS_NOT_EXACT_VALUE_QUOTIENT__N2_COMPLETE"
SUFF="QG33_SIXLCU_ONE_LITERAL_LABEL_QUOTIENT_ALSO_VALUE_SUFFICIENT__N2_COMPLETE"

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def literal_from_q15(res):
 w=res["sixlcu"]["minerr_surface"]["K1_D1"]["witness"]["conjunctions"]
 assert len(w)==1 and len(w[0])==1
 return w[0][0]
def literal_eval(vec,lit):
 i=qg15b.SIX_FEATURES.index(lit["feature"]);v=vec[i];t=lit["threshold"];op=lit["op"]
 flag=(v==t) if op=="==" else ((v<=t) if op=="<=" else (v>=t))
 return (not flag) if lit.get("negated") else flag
def feat_vec(rec,codes,n):
 f=rec["features"];wts=[qg4.term_wt(c,n) for c in codes]
 return (f["maxg2"],f["best2"],f["best3"],f["maxg3"],f["maxg4"],f["maxg5"],f["g6"],rec["W"],rec["wF"][63],max(wts),max(rec["wF"][pm] for pm in qg4.PAIR_MASKS))
def hist_json(c):return {str(k):int(v) for k,v in sorted(c.items())}
def confusion(flags,labels):
 tp=fp=fn=tn=0
 for p,l in zip(flags,labels):
  if p and l:tp+=1
  elif p:fp+=1
  elif l:fn+=1
  else:tn+=1
 return {"TP":tp,"FP":fp,"FN":fn,"TN":tn,"errors":fp+fn}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();q12=json.loads(Q12.read_text());q15=json.loads(Q15.read_text());lit=literal_from_q15(q15)
 parent={"qg12":q12.get("terminal")=="QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED" and q12.get("blind_complete_regression",{}).get("n2_count")==38760 and q12.get("blind_complete_regression",{}).get("zero_mismatches") is True,"qg15b":q15.get("q3",{}).get("E_floor")==0 and q15.get("q3",{}).get("zero_error_cells",{}).get("headline_cell")==[1,1] and q15.get("sixlcu",{}).get("minerr_surface",{}).get("K1_D1",{}).get("minerr")==0}
 delta_hist=Counter();binary={False:Counter(),True:Counter()};feature=defaultdict(Counter);feature_examples={};first_by_label_delta={};rows=0;preds=[];labels=[];p0s=[];bounded_all=True
 for n,codes in qg4.gen_exhaustive_n2():
  codes=tuple(codes);rec=qg4.eval_instance(codes,n);vec=feat_vec(rec,codes,n);delta=int(rec["C_U"]-rec["C_F"]);pred=bool(literal_eval(vec,lit));lab=bool(rec["label"]);p0=bool(rec["P"][0]);rows+=1;bounded_all &= rec.get("bounded_complete") is True and delta>=0
  delta_hist[delta]+=1;binary[pred][delta]+=1;feature[vec][delta]+=1;preds.append(pred);labels.append(lab);p0s.append(p0)
  key=(pred,delta)
  if key not in first_by_label_delta:first_by_label_delta[key]={"codes":codes,"C_U":int(rec["C_U"]),"C_F":int(rec["C_F"]),"Delta":delta,"A_label":pred,"P0":p0,"label":lab,"feature_vector":vec}
  feature_examples.setdefault((vec,delta),{"codes":codes,"C_U":int(rec["C_U"]),"C_F":int(rec["C_F"]),"Delta":delta,"feature_vector":vec,"A_label":pred,"P0":p0})
 label_sufficient=all(len(c)<=1 for c in binary.values())
 lp=None
 if not label_sufficient:
  candidates=[]
  for flag in (False,True):
   ds=sorted(binary[flag])
   for a,b in itertools.combinations(ds,2):
    x=first_by_label_delta[(flag,a)];y=first_by_label_delta[(flag,b)];pair=sorted((x,y),key=lambda z:tuple(z["codes"]));candidates.append(pair)
  lp=min(candidates,key=lambda p:(tuple(p[0]["codes"]),tuple(p[1]["codes"])))
 mixed=[];floor=0
 for vec,c in feature.items():
  floor+=sum(c.values())-max(c.values())
  if len(c)>1:mixed.append((vec,c))
 mixed.sort(key=lambda x:x[0]);fp=None
 if mixed:
  vec,c=mixed[0];ds=sorted(c);a,b=ds[0],ds[1];fp={"feature_vector":vec,"delta_histogram":hist_json(c),"example_1":feature_examples[(vec,a)],"example_2":feature_examples[(vec,b)]}
 full_sufficient=len(mixed)==0
 conf=confusion(preds,labels);p0conf=confusion(p0s,labels)
 checks={"rows_38760":rows==38760,"parents":all(parent.values()),"literal_exact_label":conf["errors"]==0,"p0_exact_label":p0conf["errors"]==0,"bounded_complete":bounded_all,"positive_count":sum(labels)==1}
 if not all(checks.values()):term="QG33_CANNOT_CHECK"
 else:term=SUFF if label_sufficient else SEP
 out={"schema":"ORIONQG.QG33.SixLCULabelValue.v1","issue":"SzeChunYiu/ORION#920","terminal":term,"protocol_sha256":shaf(PROTO),"parent_hashes":{"qg12":shaf(Q12),"qg15b":shaf(Q15)},"parent_checks":parent,"COMPLETE_N2_DOMAIN":rows==38760,"instance_count":rows,"label_literal":lit,"label_confusion":conf,"p0_confusion":p0conf,"delta_histogram":hist_json(delta_hist),"binary_label_delta_histograms":{"false":hist_json(binary[False]),"true":hist_json(binary[True])},"LABEL_QUOTIENT_VALUE_SUFFICIENT":label_sufficient,"label_value_separation_witness":lp,"full_feature_vector":{"feature_names":list(qg15b.SIX_FEATURES),"cell_count":len(feature),"mixed_delta_cell_count":len(mixed),"irreducible_exact_value_error_floor":int(floor),"first_mixed_delta_cell":fp},"FULL_FEATURE_VECTOR_VALUE_SUFFICIENT":full_sufficient,"NO_POST_OUTCOME_FEATURE_INVENTION":True,"ALL_N_VALUE_THEOREM":False,"GLOBAL_PREDICATE_MINIMALITY":False,"NEW_FEATURE_VOCABULARY_AUTHORITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"instances":rows,"delta_values":len(delta_hist),"label_value_sufficient":label_sufficient,"feature_value_sufficient":full_sufficient,"feature_cells":len(feature),"mixed_feature_cells":len(mixed),"value_floor":floor,"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
