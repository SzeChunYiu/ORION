#!/usr/bin/env python3
"""Independent receipt-only verifier for QG-36 fair adaptivity composition."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/orion-qg-qg36-fair-adaptivity-composition.json";Q34=ROOT/"research/extensions/orion-qg/QG34_ADAPTIVE_PROBE_TREE_RESULTS.json";Q35=ROOT/"research/extensions/orion-qg/QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json";Q35D=ROOT/"development/orion-qg-regime-geometry/QG35_PROTECTED_RUN_RECEIPT_2026-08-22.json";OUT=ROOT/"artifacts/orion-qg-qg36-generic-verification.json";TOKEN="ORIONQG_QG36_GENERIC=";Q34_BLOB="0fb6e2a0b6ff7d9960ab09942a402a304a890d71";STRICT="QG36_TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT";TIE="QG36_NO_STRICT_POSTSUMMARY_ADAPTIVITY_ADVANTAGE__EXACT_TIE";BAD="QG36_PARENT_INCONSISTENCY__ADAPTIVE_WORSE_THAN_OPTIMAL_FIXED"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(d):
 u={k:v for k,v in d.items() if k!='result_digest'};return d.get('result_digest')==hashlib.sha256(canon(u).encode()).hexdigest()
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def no_dupes(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError("duplicate committed-result keys: "+k)
  d[k]=v
 return d
def load_committed_result(p):return json.loads(p.read_text(),object_pairs_hook=no_dupes)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=SRC);ap.add_argument('--qg35',type=Path,default=Q35);ap.add_argument('--qg35-dual',type=Path,default=Q35D);ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());a=load_committed_result(Q34);f=json.loads(ns.qg35.read_text());fd=json.loads(ns.qg35_dual.read_text());D=a.get('class_depths');F=f.get('class_minima');aq=blob(Q34)==Q34_BLOB and a.get('terminal')=='QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED' and a.get('both_accept') is True and a.get('EXACT_ADAPTIVE_MINIMAX_AUTHORITY') is True and isinstance(D,list) and len(D)==92 and max(D)==a.get('worst_case_depth');fq=valid(f) and f.get('terminal')=='QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED' and f.get('EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY') is True and isinstance(F,list) and len(F)==92 and max(F)==f.get('worst_case_class_conditioned_fixed_minimum');fdual=fd.get('terminal')=='QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED' and fd.get('both_accept') is True and fd.get('EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY') is True and fd.get('F_star')==max(F) and fd.get('class_minima')==F;same=aq and fq and a.get('parent_qg32_sha256')==f.get('parent_qg32_sha256');u=f.get('universe',{});universe=u.get('orbits')==715 and u.get('probes')==384 and u.get('joint_classes')==92;rangeok=aq and fq and all(isinstance(x,int) and 0<=x<=5 for x in list(reversed(D))+list(reversed(F)));viol=[];strict=[];ties=[]
 if rangeok:
  for i in range(91,-1,-1):
   d,x=D[i],F[i]
   if d>x:viol.append((i,d,x))
   elif d<x:strict.append(i)
   else:ties.append(i)
 viol.sort();strict.sort();ties.sort();ds=max(D) if aq else None;fs=max(F) if fq else None;parent=aq and fq and fdual and same and universe and rangeok
 if not parent:term='QG36_CANNOT_CHECK'
 elif viol:term=BAD
 elif ds<fs:term=STRICT
 elif ds==fs:term=TIE
 else:term=BAD
 checks={'source_digest':valid(src),'qg34':aq,'qg35':fq,'qg35_dual':fdual,'same_parent':same,'universe':universe,'ranges':rangeok,'terminal':src.get('terminal')==term,'arrays':src.get('adaptive_class_depths')==D and src.get('fixed_class_minima')==F,'maxima':src.get('D_star')==ds and src.get('F_star')==fs,'violations':src.get('pointwise_violation_count')==len(viol) and src.get('first_pointwise_violation')==(None if not viol else {'class_index':viol[0][0],'adaptive_depth':viol[0][1],'fixed_minimum':viol[0][2]}),'strict':src.get('strict_improvement_class_indices')==strict,'ties':src.get('tie_class_indices')==ties,'positive':src.get('TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT') is (term==STRICT),'boundary':all(src.get(k) is False for k in ('COMPILER_OPTIMIZATION_COST_ADVANTAGE','HARDWARE_MEASUREMENT_MINIMUM','MINIMUM_FULL_FINITE_OPTIMUM_PROBES','GENERIC_ADAPTIVE_TESTING_NOVELTY','AUTONOMOUS_SKILL_SELECTION_AUTHORITY','physical_quantum_advantage_claim'))};ok=all(checks.values());out={'schema':'ORIONQG.QG36.GenericVerification.v1','decision':'ACCEPT_FAIR_COMPARISON' if ok and term in {STRICT,TIE} else ('ACCEPT_PARENT_INCONSISTENCY' if ok and term==BAD else 'REJECT'),'all_checks':ok,'checks':checks,'independent':{'terminal':term,'D_star':ds,'F_star':fs,'pointwise_violation_count':len(viol),'strict_improvement_class_indices':strict,'tie_class_indices':ties},'TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT':bool(ok and term==STRICT),'COMPILER_OPTIMIZATION_COST_ADVANTAGE':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'GENERIC_ADAPTIVE_TESTING_NOVELTY':False,'AUTONOMOUS_SKILL_SELECTION_AUTHORITY':False,'physical_quantum_advantage_claim':False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'decision':out['decision'],'terminal':term,'D_star':ds,'F_star':fs,'violations':len(viol),'strict_classes':len(strict)}));return 0
if __name__=='__main__':raise SystemExit(main())
