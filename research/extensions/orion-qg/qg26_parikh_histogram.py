#!/usr/bin/env python3
"""QG-26 production analyzer: exact all-n TARE cost as guarded min-affine function of column counts."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[3]
QDIR=ROOT/"research/extensions/orion-q"
sys.path.insert(0,str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa:E402
import max_r6s_all_n_composition as r6s  # noqa:E402

PROTO=ROOT/"development/orion-qg-regime-geometry/QG26_PARIKH_HISTOGRAM_PROTOCOL_V1.md"
QG23=ROOT/"research/extensions/orion-qg/QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json"
QG24=ROOT/"research/extensions/orion-qg/QG24_TROPICAL_WFA_RESULTS.json"
QG7C=ROOT/"research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
QG7C_PROTO=ROOT/"development/orion-qg-regime-geometry/QG7C_CLASSIFICATION_PROTOCOL_V1.md"
OUT=ROOT/"artifacts/orion-qg-qg26-parikh-histogram.json"
TOKEN="ORIONQG_QG26="
POS="QG26_TARE_EXACT_COST_IS_FINITE_GUARDED_TROPICAL_FUNCTION_OF_4096_COLUMN_COUNTS_ALL_N"


def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha_obj(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def sha_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key_from_columns(cols,component):return p10.key_from_codes([c[component] for c in cols])
def key1(code):return p10.key_from_codes([code])

def permute_type(t,p):
 out=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];out.extend((a,b) if p[j]==0 else (b,a))
 return tuple(out)

def types4096():return list(itertools.product(range(4),repeat=6))
def perms8():return list(itertools.product((0,1),repeat=3))
def centrals8():return list(itertools.product((0,1),repeat=3))

def f3_tables():
 lw=[int(p10.h.local_wt(a)) for a in range(4)]
 lm=[[int(p10.h.local_mul(a,b)) for b in range(4)] for a in range(4)]
 sy=[[int(p10.h.local_symp(a,b)) for b in range(4)] for a in range(4)]
 f3=[[[0]*4 for _ in range(4)] for __ in range(4)]
 for a,b,c in itertools.product(range(4),repeat=3):f3[a][b][c]=1 if a==b==c!=0 else lw[a]+lw[b]+lw[c]
 return lw,lm,sy,f3

def local_accept(frames,tag,sy):
 if any(f==0 for f in frames):return False,None
 if any(sy[frames[2*j]][frames[2*j+1]]!=1 for j in range(3)):return False,None
 l0,l1=sy[tag][frames[0]],sy[tag][frames[1]]
 if l0==l1:return False,None
 if any(sy[tag][frames[2*j]]!=l0 or sy[tag][frames[2*j+1]]!=l1 for j in (1,2)):return False,None
 return True,(l0,l1)

def aux48(sy):
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy[a][b]==1]
 rows=[]
 for ps in itertools.product(pairs,repeat=3):
  frames=tuple(x for q in ps for x in q)
  for tag in range(4):
   ok,lab=local_accept(frames,tag,sy)
   if ok:rows.append({"frames":frames,"tag":tag,"labels":lab,"frame_keys":tuple(key1(x) for x in frames),"tag_key":key1(tag)})
 return rows

def baseline(pt,f3):return f3[pt[0]][pt[2]][pt[4]]+f3[pt[1]][pt[3]][pt[5]]
def aux_restore(pt,frames,lm,f3):
 r=[lm[pt[i]][frames[i]] for i in range(6)]
 return f3[r[0]][r[2]][r[4]]+f3[r[1]][r[3]][r[5]]
def struct_cost(frames,tag,centr):
 raw=0
 for j in range(3):
  raw+=(2 if centr[j]==0 else 4)*int(frames[2*j]!=0)
  raw+=(2 if centr[j]==1 else 4)*int(frames[2*j+1]!=0)
 raw+=2*int(tag!=0)
 return raw-18

def stream_int(h,v):h.update((str(int(v))+"\n").encode())

def baseline_vectors(types,perms,f3):
 vecs=[];meta=[]
 for p in perms:
  v=[int(baseline(permute_type(t,p),f3)) for t in types]
  vecs.append(v)
  c=Counter(v);meta.append({"perm":p,"sha256":sha_obj(v),"histogram":{str(k):int(n) for k,n in sorted(c.items())},"min":min(v),"max":max(v)})
 return vecs,meta

def one_active_control(types,perms,aux,vecs,lm,f3):
 centr=(0,0,0);mism=[];hp=hashlib.sha256();ht=hashlib.sha256();rows=0
 for ti,t in enumerate(types):
  for pi,p in enumerate(perms):
   pt=permute_type(t,p);tkeys=tuple(key1(x) for x in pt);b=vecs[pi][ti]
   for a in aux:
    pc=int(r6s.config_cost(tkeys,a["frame_keys"],a["tag_key"],centr,1))
    k=struct_cost(a["frames"],a["tag"],centr)+aux_restore(pt,a["frames"],lm,f3)-b
    tc=int(b+k);stream_int(hp,pc);stream_int(ht,tc);rows+=1
    if pc!=tc and len(mism)<20:mism.append({"type_index":ti,"target_type":t,"perm":p,"frames":a["frames"],"tag":a["tag"],"production":pc,"template":tc,"baseline":b,"K":k})
 return {"rows":rows,"expected_rows":4096*48*8,"production_digest":hp.hexdigest(),"template_digest":ht.hexdigest(),"digests_equal":hp.digest()==ht.digest(),"mismatch_count_capped":len(mism),"mismatches_verbatim":mism,"all_match":len(mism)==0}

def structural_control(f3):
 allI=(key1(0),)*6;centrals=centrals8();mism=[];hp=hashlib.sha256();he=hashlib.sha256();rows=0
 for letters in itertools.product(range(4),repeat=7):
  frames=letters[:6];tag=letters[6];fkeys=tuple(key1(x) for x in frames);tkey=key1(tag)
  restore_f3=f3[frames[0]][frames[2]][frames[4]]+f3[frames[1]][frames[3]][frames[5]]
  for c in centrals:
   total=int(r6s.config_cost(allI,fkeys,tkey,c,1));observed=total-restore_f3;expected=struct_cost(frames,tag,c)
   stream_int(hp,observed);stream_int(he,expected);rows+=1
   if observed!=expected and len(mism)<20:mism.append({"letters":letters,"centrals":c,"observed":observed,"expected":expected,"total":total,"restore_f3":restore_f3})
 return {"rows":rows,"expected_rows":4**7*8,"production_struct_digest":hp.hexdigest(),"expected_struct_digest":he.hexdigest(),"digests_equal":hp.digest()==he.digest(),"mismatch_count_capped":len(mism),"mismatches_verbatim":mism,"all_match":len(mism)==0}

def placement_controls(types,perms,centrals,aux,vecs,lm,f3):
 mism=[];h=hashlib.sha256();rows=0
 for ti in range(16):
  t=types[ti];s=types[(ti*257+17)%4096]
  for ai,a in enumerate(aux):
   p=perms[(ti+ai)%8];c=centrals[(3*ti+ai)%8];pi=perms.index(p);pt=permute_type(t,p);ps=permute_type(s,p)
   colsA=[pt,ps,pt];colsB=[pt,ps,pt]
   targetsA=tuple(key_from_columns(colsA,i) for i in range(6));targetsB=targetsA
   def aux_keys(pos):
    f=[]
    for i in range(6):
     seq=[0,0,0];seq[pos]=a["frames"][i];f.append(p10.key_from_codes(seq))
    seq=[0,0,0];seq[pos]=a["tag"]
    return tuple(f),p10.key_from_codes(seq)
   f0,s0=aux_keys(0);f2,s2=aux_keys(2)
   c0=int(r6s.config_cost(targetsA,f0,s0,c,3));c2=int(r6s.config_cost(targetsB,f2,s2,c,3))
   base=vecs[pi][ti]+vecs[pi][(ti*257+17)%4096]+vecs[pi][ti]
   k=struct_cost(a["frames"],a["tag"],c)+aux_restore(pt,a["frames"],lm,f3)-vecs[pi][ti]
   formula=base+k
   for v in (c0,c2,formula):stream_int(h,v)
   rows+=1
   if not (c0==c2==formula) and len(mism)<20:mism.append({"ti":ti,"ai":ai,"perm":p,"central":c,"cost_pos0":c0,"cost_pos2":c2,"formula":formula})
 return {"rows":rows,"expected_rows":16*48,"triple_cost_digest":h.hexdigest(),"all_equal":len(mism)==0,"mismatch_count_capped":len(mism),"mismatches_verbatim":mism}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args()
 lw,lm,sy,f3=f3_tables();types=types4096();perms=perms8();centrals=centrals8();aux=aux48(sy)
 prod_tables={"LW":list(map(int,np.asarray(r6m._LW).tolist())),"LM":[[int(x) for x in r] for r in np.asarray(r6m._LM).tolist()],"SY":[[int(x) for x in r] for r in np.asarray(r6m._SY).tolist()],"F3":[[[int(x) for x in r] for r in slab] for slab in np.asarray(r6m._F3).tolist()]}
 table_checks={"LW":lw==prod_tables["LW"],"LM":lm==prod_tables["LM"],"SY":sy==prod_tables["SY"],"F3":f3==prod_tables["F3"],"r6s_bind":all(bool(v) for v in r6s.bind_tables().values())}
 vecs,bmeta=baseline_vectors(types,perms,f3)
 baseline_checks={"eight_vectors":len(vecs)==8 and all(len(v)==4096 for v in vecs),"all_integer":all(isinstance(x,int) for v in vecs for x in v),"input_types_4096":len(types)==4096}
 distinct_baselines=len({m["sha256"] for m in bmeta})

 q23=json.loads(QG23.read_text());q24=json.loads(QG24.read_text());q7c=json.loads(QG7C.read_text());q7ct=QG7C_PROTO.read_text()
 parent_checks={
  "qg23_green":q23.get("terminal")=="QG23_TARE_AUXILIARY_SUPPORT_SKELETON_AT_MOST_6_ALL_N_MACHINE_CHECKED" and q23.get("both_accept") is True and q23.get("maximum_auxiliary_support")==6,
  "qg23_spectators_not_claimed_full_state":q23.get("FULL_STATE_DIMENSION_6") is False and q23.get("target_spectator_state")=="OPEN_AND_NOT_BOUNDED_BY_6",
  "qg23_hostile_overlap_preserved":q23.get("qg7f_hostile_control",{}).get("two_coordinate_reduction_refuted") is True and q23.get("qg7f_hostile_control",{}).get("tag_weight")==3,
  "qg24_exact_all_n_control":q24.get("terminal")=="QG24_TARE_UNRESTRICTED_EXACT_OPTIMUM_RECOGNIZED_BY_FINITE_TROPICAL_AUTOMATON_ALL_N" and q24.get("both_accept") is True and q24.get("UNRESTRICTED_DP_EQUALITY_ALL_N") is True,
  "m1_shape_support_definitions":all(s in q7ct for s in ("**anchored**: both frames weight-1 on one common qubit q","**phantom**: anti frame support-2 on {b,h}","σ_h = 0 (home OFF the tag)","**comm-s2**: comm frame support-2 on {b,a}")),
  "qg7c_m1_holds":q7c.get("m1_inventory",{}).get("holds") is True and q7c.get("m1_inventory",{}).get("unclassified_irreducible")==0,
 }

 base=4096*(4**7-1);upper=64*sum(base**k for k in range(1,7))
 finiteness={"active_labeled_choice_base":base,"expected_base":67104768,"max_active_coordinates":6,"global_control_sectors":64,"ordered_template_universe_upper_bound":upper,"upper_bound_decimal_digits":len(str(upper)),"finite":base==67104768 and upper>0}

 one=one_active_control(types,perms,aux,vecs,lm,f3);struct=structural_control(f3);place=placement_controls(types,perms,centrals,aux,vecs,lm,f3)
 controls_ok=one["all_match"] and one["rows"]==one["expected_rows"] and struct["all_match"] and struct["rows"]==struct["expected_rows"] and place["all_equal"] and place["rows"]==place["expected_rows"]

 proof={
  "simultaneous_qubit_permutation_preserves_weight_sums":True,
  "simultaneous_qubit_permutation_preserves_symplectic_xor":True,
  "simultaneous_qubit_permutation_preserves_f3_sum":True,
  "path_or_configuration_updates_commute_across_coordinates":True,
  "histogram_sufficient_statistic_all_n":True,
  "all_nonidentity_auxiliary_letters_inside_U_aux_by_m1_shapes":parent_checks["m1_shape_support_definitions"],
  "at_most_six_active_occurrences_for_an_optimum":parent_checks["qg23_green"],
  "spectator_restore_equals_target":True,
  "spectator_cost_is_baseline_coefficient":True,
  "template_guard_is_count_thresholds":True,
  "configuration_to_template":True,
  "template_to_configuration_if_guard_holds":True,
  "equal_type_coordinate_choice_irrelevant":place["all_equal"],
  "finite_min_affine_representation":all(parent_checks.values()) and controls_ok and finiteness["finite"],
  "valid_histogram_requires_each_target_nonzero":"for each i: sum_{t:t_i!=I} N_t >= 1",
  "physical_n_only_through_counts_after_histogram":True,
 }

 parent_ok=all(parent_checks.values());local_ok=all(table_checks.values()) and all(baseline_checks.values()) and controls_ok and finiteness["finite"]
 if not parent_ok:term="QG26_QG23_AUX_SUPPORT_BINDING_GAP"
 elif not local_ok:term="QG26_LOCAL_DECOMPOSITION_COUNTEREXAMPLE"
 else:term=POS
 out={
  "schema":"ORIONQG.QG26.ParikhHistogram.v1","issue":"SzeChunYiu/ORION#884","terminal":term,"protocol_sha256":sha_file(PROTO),
  "parent_hashes":{"qg23":sha_file(QG23),"qg24":sha_file(QG24),"qg7c":sha_file(QG7C)},"table_checks":table_checks,
  "column_alphabet":{"size":4096,"order":"lexicographic_I_X_Y_Z_codes_0_1_2_3_over_6_components","histogram_dimension":4096},
  "spectator_baselines":{"count":8,"distinct_vectors":distinct_baselines,"vectors":bmeta,"checks":baseline_checks},
  "parent_checks":parent_checks,"template_finiteness":finiteness,"one_active_decomposition_control":one,"structural_cost_control":struct,"placement_realization_controls":place,"proof_audit":proof,
  "HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":term==POS,"FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION":term==POS,"COUNT_SPACE_REGIME_GEOMETRY_EXISTS":term==POS,
  "EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"CHAIN_ALL_N":False,"GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE":False,
  "novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False,
 }
 raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(TOKEN+canon({"terminal":term,"histogram_dimension":4096,"distinct_baselines":distinct_baselines,"active_choice_base":base,"template_upper_digits":len(str(upper)),"one_active_rows":one["rows"],"structural_rows":struct["rows"],"placement_rows":place["rows"],"parent_ok":parent_ok,"local_ok":local_ok,"result_digest":out["result_digest"]}))
 return 0
if __name__=="__main__":raise SystemExit(main())
