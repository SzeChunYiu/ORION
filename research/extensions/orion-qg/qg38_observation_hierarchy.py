#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PROTO=ROOT/'development/orion-qg-regime-geometry/QG38_EXACT_OBSERVATION_HIERARCHY_PROTOCOL_V1.md'
Q36=ROOT/'research/extensions/orion-qg/QG38_PARENT_QG36_PROJECTION.json'
Q32C=ROOT/'research/extensions/orion-qg/QG38_PARENT_QG32C_PROJECTION.json'
OUT=ROOT/'artifacts/orion-qg-qg38-observation-hierarchy.json'
TOKEN='ORIONQG_QG38='
STRICT='QG38_EXACT_STRICT_OBSERVATION_COST_HIERARCHY_MACHINE_CHECKED'
TIE='QG38_EXACT_THREE_WAY_TIE_MACHINE_CHECKED'
MONO='QG38_EXACT_NONSTRICT_MONOTONE_HIERARCHY_MACHINE_CHECKED'
BAD='QG38_PARENT_INCONSISTENCY_OR_NONMONOTONE_MODEL_ORDERING'
CANNOT='QG38_CANNOT_CHECK_PARENT_OR_SEMANTIC_BINDING'
Q32='4a4a0429f2e0d9d3a65573549e31e28f7ac8ca473e905d86c0f8f497111be64d'
Q36_SOURCE='e9a6204c57991667fd36859e67c7e2da2e4844fd8e98ad4a0d3aba1216a723a1'
Q32C_SOURCE='adf1b8f5f4420c20468254715ceff6319b61cc0822b654dbb7b7d586593be25a'

def canon(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def valid(d):
 u={k:v for k,v in d.items() if k!='result_digest'}
 return d.get('result_digest')==hashlib.sha256(canon(u).encode()).hexdigest()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ratio(a,b):
 if b==0:return None
 f=Fraction(a,b);return f'{f.numerator}/{f.denominator}'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args()
 a=json.loads(Q36.read_text());u=json.loads(Q32C.read_text())
 universe={'orbits':715,'probes':384,'joint_classes':92}
 checks={
  'qg36_digest':valid(a),
  'qg32c_digest':valid(u),
  'qg36_source':a.get('source_result_digest')==Q36_SOURCE and a.get('source_workflow_run_id')==32597286849 and a.get('source_artifact_id')==9481900449,
  'qg32c_source':u.get('source_result_digest')==Q32C_SOURCE and u.get('source_workflow_run_id')==32591149612 and u.get('source_artifact_id')==9480417797,
  'qg36_authority':a.get('both_accept') is True and a.get('EXACT_FAIR_FIXED_VS_ADAPTIVE_COMPARISON_AUTHORITY') is True and a.get('pointwise_violation_count')==0,
  'qg32c_authority':u.get('both_accept') is True and u.get('MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY') is True and u.get('EXISTS_SEPARATOR_AT_MOST_4') is False,
  'shared_parent':a.get('qg32_parent_sha256')==u.get('qg32_parent_sha256')==Q32,
  'universe':a.get('universe')==u.get('universe')==universe,
  'semantics':a.get('D_semantics')=='POSTSUMMARY_CLASS_CONDITIONED_ADAPTIVE_MINIMAX_PROBE_DEPTH' and a.get('F_semantics')=='POSTSUMMARY_CLASS_CONDITIONED_NONADAPTIVE_FIXED_SET_MINIMUM_WORST_CASE' and u.get('U_semantics')=='UNIVERSAL_NONADAPTIVE_FIXED_SET_MINIMUM_ACROSS_ALL_SUMMARY_CLASSES',
 }
 D,F,U=a.get('D_star'),a.get('F_star'),u.get('MINIMUM_FIXED_PROBE_CARDINALITY')
 checks['integer_values']=all(isinstance(x,int) and not isinstance(x,bool) and x>=0 for x in (D,F,U))
 parent_ok=all(checks.values())
 if not parent_ok: term=CANNOT
 elif D<F<U: term=STRICT
 elif D==F==U: term=TIE
 elif D<=F<=U: term=MONO
 else: term=BAD
 exact=parent_ok and term in {STRICT,TIE,MONO,BAD}
 out={
  'schema':'ORIONQG.QG38.ObservationHierarchy.v1','issue':'SzeChunYiu/ORION#942','terminal':term,
  'protocol_sha256':sha(PROTO),'parent_checks':checks,'parent_hashes':{'qg36_projection_sha256':sha(Q36),'qg32c_projection_sha256':sha(Q32C),'qg32_parent_sha256':Q32 if parent_ok else None},
  'universe':universe if parent_ok else None,
  'models':{
   'D_star':{'value':D if parent_ok else None,'semantics':'POSTSUMMARY_CLASS_CONDITIONED_ADAPTIVE_MINIMAX_PROBE_DEPTH'},
   'F_star':{'value':F if parent_ok else None,'semantics':'POSTSUMMARY_CLASS_CONDITIONED_NONADAPTIVE_FIXED_SET_MINIMUM_WORST_CASE'},
   'U_star':{'value':U if parent_ok else None,'semantics':'UNIVERSAL_NONADAPTIVE_FIXED_SET_MINIMUM_ACROSS_ALL_SUMMARY_CLASSES'}},
  'gaps':{'F_minus_D':F-D if parent_ok else None,'U_minus_F':U-F if parent_ok else None,'U_minus_D':U-D if parent_ok else None},
  'ratios':{'F_over_D':ratio(F,D) if parent_ok else None,'U_over_F':ratio(U,F) if parent_ok else None,'U_over_D':ratio(U,D) if parent_ok else None},
  'strict_adaptive_improvement_class_count':a.get('strict_improvement_class_count') if parent_ok else None,
  'EXACT_OBSERVATION_COST_HIERARCHY_AUTHORITY':exact,
  'STRICT_THREE_LEVEL_HIERARCHY_AUTHORITY':term==STRICT,
  'HARDWARE_MEASUREMENT_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'COMPILER_OPTIMIZATION_COST_ADVANTAGE':False,'COMPILER_RUNTIME_ADVANTAGE':False,'GENERIC_ACTIVE_LEARNING_NOVELTY':False,'AUTONOMOUS_SKILL_SELECTION_AUTHORITY':False,'physical_quantum_advantage_claim':False,'novelty_authority':False}
 raw=canon(out);out['result_digest']=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(TOKEN+canon({'terminal':term,'D_star':D if parent_ok else None,'F_star':F if parent_ok else None,'U_star':U if parent_ok else None,'result_digest':out['result_digest']}));return 0 if parent_ok else 2
if __name__=='__main__':raise SystemExit(main())
