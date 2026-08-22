#!/usr/bin/env python3
"""QG-36 receipt-only fair fixed-vs-adaptive composition."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[3]
PROTO=ROOT/"development/orion-qg-regime-geometry/QG36_FAIR_ADAPTIVITY_COMPOSITION_PROTOCOL_V1.md"
Q34=ROOT/"research/extensions/orion-qg/QG34_ADAPTIVE_PROBE_TREE_RESULTS.json"
Q35=ROOT/"research/extensions/orion-qg/QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json"
OUT=ROOT/"artifacts/orion-qg-qg36-fair-adaptivity-composition.json";TOKEN="ORIONQG_QG36="
STRICT="QG36_TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT";TIE="QG36_NO_STRICT_POSTSUMMARY_ADAPTIVITY_ADVANTAGE__EXACT_TIE";BAD="QG36_PARENT_INCONSISTENCY__ADAPTIVE_WORSE_THAN_OPTIMAL_FIXED"
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args()
 if not Q35.exists():
  print(TOKEN+canon({'terminal':'QG36_QG35_TARGET_RECEIPT_MISSING__CANNOT_CHECK'}));return 2
 a=json.loads(Q34.read_text());f=json.loads(Q35.read_text());D=a.get('class_depths');F=f.get('class_minima')
 aq=a.get('terminal')=='QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED' and a.get('both_accept') is True and a.get('EXACT_ADAPTIVE_MINIMAX_AUTHORITY') is True and isinstance(D,list) and len(D)==92 and a.get('worst_case_depth')==max(D)
 fq=f.get('terminal')=='QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED' and f.get('both_accept') is True and f.get('EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY') is True and isinstance(F,list) and len(F)==92 and f.get('worst_case_class_conditioned_fixed_minimum')==max(F)
 same_parent=aq and fq and isinstance(a.get('parent_qg32_sha256'),str) and a.get('parent_qg32_sha256')==f.get('parent_qg32_sha256')
 universe=f.get('universe',{});universe_ok=universe.get('orbits')==715 and universe.get('probes')==384 and universe.get('joint_classes')==92
 range_ok=aq and fq and all(isinstance(x,int) and 0<=x<=5 for x in D+F)
 violations=[];strict=[];ties=[]
 if range_ok:
  for i,(d,x) in enumerate(zip(D,F)):
   if d>x:violations.append({'class_index':i,'adaptive_depth':d,'fixed_minimum':x})
   elif d<x:strict.append(i)
   else:ties.append(i)
 parent_ok=aq and fq and same_parent and universe_ok and range_ok
 if not parent_ok:terminal='QG36_CANNOT_CHECK'
 elif violations:terminal=BAD
 else:
  ds=max(D);fs=max(F);terminal=STRICT if ds<fs else (TIE if ds==fs else BAD)
 ds=max(D) if aq else None;fs=max(F) if fq else None;positive=terminal==STRICT
 out={'schema':'ORIONQG.QG36.FairAdaptivityComposition.v1','issue':'SzeChunYiu/ORION#933','terminal':terminal,'protocol_sha256':shaf(PROTO),'parent_hashes':{'qg34':shaf(Q34),'qg35':shaf(Q35)},'parent_checks':{'qg34_exact':aq,'qg35_exact':fq,'same_qg32_parent_hash':same_parent,'universe':universe_ok,'ranges':range_ok},'class_order_binding':'IDENTICAL_QG32_PARENT_HASH__CANONICAL_QG32_MAKE_GROUPS_ORDER','adaptive_class_depths':D if aq else None,'fixed_class_minima':F if fq else None,'D_star':ds,'F_star':fs,'pointwise_violation_count':len(violations),'first_pointwise_violation':violations[0] if violations else None,'strict_improvement_class_indices':strict,'tie_class_indices':ties,'TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT':positive,'EXACT_FAIR_FIXED_VS_ADAPTIVE_COMPARISON_AUTHORITY':terminal in {STRICT,TIE},'COMPILER_OPTIMIZATION_COST_ADVANTAGE':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'GENERIC_ADAPTIVE_TESTING_NOVELTY':False,'AUTONOMOUS_SKILL_SELECTION_AUTHORITY':False,'physical_quantum_advantage_claim':False}
 raw=canon(out);out['result_digest']=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':terminal,'D_star':ds,'F_star':fs,'violations':len(violations),'strict_classes':len(strict),'result_digest':out['result_digest']}));return 0
if __name__=='__main__':raise SystemExit(main())
