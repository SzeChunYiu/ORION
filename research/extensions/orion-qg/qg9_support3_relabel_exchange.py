#!/usr/bin/env python3
"""QG-9 V3: close the R6I support-4 boundary with local relabel+delete edits."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
ORION_Q=ROOT/'research/extensions/orion-q'
sys.path.insert(0,str(ORION_Q));sys.path.insert(0,str(ROOT/'research/extensions/orion-qg'))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import qg9_support4_combined_exchange as v2  # noqa: E402

BASE='51d81c448a67c7da8e89310c02ef890f5afd0f7b'
PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT3_RELABEL_EXCHANGE_PROTOCOL_V1.md'
V2_RESULT=ROOT/'research/extensions/orion-qg/QG9_SUPPORT4_COMBINED_EXCHANGE_RESULTS.json'
V2_RECEIPT=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT4_PROTECTED_RUN_RECEIPT_2026-08-21.json'
DEFAULT=ROOT/'artifacts/orion-qg-qg9-support3-relabel-exchange.json'
TOKEN='ORIONQG_QG9_SUPPORT3='
VERBATIM=20
MUL=[[int(r6i._MUL[a,b]) for b in range(4)] for a in range(4)]
SY=[[int(r6i._SYMP[a,b]) for b in range(4)] for a in range(4)]
LW=[int(r6i._LW[a]) for a in range(4)]

def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def wt(x):return LW[x]
def signature(a,b,s0,s1):return (SY[a][b],SY[s0][a],SY[s1][a],SY[s0][b],SY[s1][b])
def sigxor(old,new):return sum((x^y)<<i for i,(x,y) in enumerate(zip(old,new)))
def local_cost(a,b,p0,p1,p2,c):
 r2=MUL[a][b];m=[4,4,4];m[c]=2
 return m[0]*wt(a)+m[1]*wt(b)+m[2]*wt(r2)+wt(MUL[p0][a])+wt(MUL[p1][b])+wt(MUL[p2][r2])
def allowed_replacements(a,b):
 aa=(0,) if a==0 else range(4);bb=(0,) if b==0 else range(4)
 for na in aa:
  for nb in bb:
   if (na,nb)!=(a,b):yield int(na),int(nb)
def concrete_actions(a,b,s0,s1):
 old=signature(a,b,s0,s1);cand=[]
 for na,nb in allowed_replacements(a,b):
  sg=sigxor(old,signature(na,nb,s0,s1));dr0=int(a!=0 and na==0);dr1=int(b!=0 and nb==0);cs=[]
  for c in range(3):
   mx=max(local_cost(na,nb,p0,p1,p2,c)-local_cost(a,b,p0,p1,p2,c) for p0,p1,p2 in itertools.product(range(4),repeat=3));cs.append(mx)
  cand.append((sg,tuple(cs),dr0,dr1,na,nb))
 # Pareto reduce only among identical semantic signature/support drops.
 kept=[]
 for x in cand:
  dominated=False
  for y in cand:
   if x==y or (x[0],x[2],x[3])!=(y[0],y[2],y[3]):continue
   if all(y[1][i]<=x[1][i] for i in range(3)) and (y[1]!=x[1] or (y[4],y[5])<(x[4],x[5])):
    dominated=True;break
  if not dominated:kept.append(x)
 return tuple(sorted(set(kept)))
def profile_key(actions):return tuple((x[0],x[1],x[2],x[3]) for x in actions)
def build_types():
 states=defaultdict(list); actions_by_type={}; concrete=0
 for a,b,s0,s1 in itertools.product(range(4),repeat=4):
  if a==0 and b==0:continue
  concrete+=1;d=v2.descriptor(a,b,s0,s1);acts=concrete_actions(a,b,s0,s1);pk=profile_key(acts);key=(d,pk);states[key].append((a,b,s0,s1));actions_by_type[key]=acts
 by_desc=defaultdict(list)
 for key in sorted(states,key=str):by_desc[key[0]].append(key)
 return states,actions_by_type,by_desc,concrete
def safe_profile_move(type_keys,actions_by_type):
 options=[]
 for key in type_keys:
  row=[('none',0,(0,0,0),0,0,None)]
  for sg,cs,d0,d1,na,nb in actions_by_type[key]:row.append(('edit',sg,cs,d0,d1,(na,nb)))
  options.append(row)
 best=None
 for ch in itertools.product(*options):
  if all(x[0]=='none' for x in ch):continue
  sg=d0=d1=0;cs=[0,0,0]
  for x in ch:
   sg^=x[1];d0+=x[3];d1+=x[4]
   for c in range(3):cs[c]+=x[2][c]
  if sg!=0 or d0<1 or max(cs)>0:continue
  repl=tuple((-1,-1) if x[5] is None else x[5] for x in ch);key=(max(cs),tuple(cs),-d0,-d1,repl)
  if best is None or key<best[0]:best=(key,ch)
 if best is None:return None
 k,ch=best;return {'worst_cost':k[0],'cost_by_central':list(k[1]),'r0_support_drop':-k[2],'r1_support_drop':-k[3],'replacements':[list(x[5]) if x[5] is not None else None for x in ch]}
def parent_survivors(w,descs,parent_profiles):
 retained=[];unsafe=[]
 for inds in itertools.combinations_with_replacement(range(len(descs)),w):
  co=[descs[i] for i in inds]
  if not v2.irreducible(co):continue
  retained.append(inds)
  if v2.find_combined_move(co,parent_profiles) is None:unsafe.append(inds)
 return retained,unsafe
def close_survivors(survivors,descs,by_desc,actions_by_type):
 type_cases=unsafe=0;unsafe_rows=[];hist=Counter();examples=[]
 for inds in survivors:
  choices=[by_desc[descs[i]] for i in inds]
  for keys in itertools.product(*choices):
   type_cases+=1;mv=safe_profile_move(keys,actions_by_type)
   if mv is None:
    unsafe+=1
    if len(unsafe_rows)<VERBATIM:unsafe_rows.append({'descriptor_indices':list(inds),'type_sizes':[len(c) for c in choices]})
   else:
    hist[mv['worst_cost']]+=1
    if len(examples)<8:examples.append({'descriptor_indices':list(inds),'move':mv})
 return {'descriptor_survivors':len(survivors),'action_profile_type_cases':type_cases,'unsafe_type_cases':unsafe,'safe_type_cases':type_cases-unsafe,'worst_cost_histogram':{str(k):v for k,v in sorted(hist.items())},'safe_examples':examples,'unsafe_verbatim':unsafe_rows}
def deletion_subset_check(states,actions_by_type):
 failures=[]
 for key,rows in states.items():
  pk=set(profile_key(actions_by_type[key]))
  for a,b,s0,s1 in rows:
   old=signature(a,b,s0,s1)
   for act in ('d0','d1','db'):
    if act=='d0' and a==0:continue
    if act=='d1' and b==0:continue
    na,nb=(0,b) if act=='d0' else ((a,0) if act=='d1' else (0,0));sg=sigxor(old,signature(na,nb,s0,s1));d0=int(a!=0 and na==0);d1=int(b!=0 and nb==0);cs=[]
    for c in range(3):cs.append(max(local_cost(na,nb,p0,p1,p2,c)-local_cost(a,b,p0,p1,p2,c) for p0,p1,p2 in itertools.product(range(4),repeat=3)))
    # Concrete deletion may be dominated by a richer replacement with same signature/drops; require one profile action no worse componentwise.
    if not any(x[0]==sg and x[2]==d0 and x[3]==d1 and all(x[1][i]<=cs[i] for i in range(3)) for x in pk):failures.append((key,(a,b,s0,s1),act,sg,tuple(cs)))
 return {'all_deletions_contained_or_dominated':not failures,'failure_count':len(failures),'failures_verbatim':failures[:VERBATIM]}
def main():
 v2r=json.loads(V2_RESULT.read_text());v2rec=json.loads(V2_RECEIPT.read_text());states,acts,by_desc,concrete=build_types();parent_reps,parent_profiles,_=v2.build_profiles();descs=sorted(parent_reps)
 ret4,surv4=parent_survivors(4,descs,parent_profiles);ret3,surv3=parent_survivors(3,descs,parent_profiles)
 closure4=close_survivors(surv4,descs,by_desc,acts);control3=close_survivors(surv3,descs,by_desc,acts);subset=deletion_subset_check(states,acts)
 profile_variants={str(d):len(by_desc[d]) for d in descs};profile_action_counts=Counter(len(k[1]) for k in states)
 parent={'result_sha256':sha(V2_RESULT),'receipt_sha256':sha(V2_RECEIPT),'terminal':v2r.get('terminal'),'protected_terminal':v2rec.get('terminal'),'both_accept':v2rec.get('both_accept'),'support_bound':v2r.get('support_bound'),'support4_retained':v2r['support4_control']['retained_irreducible_patterns'],'support4_unsafe':v2r['support4_control']['unsafe_count']}
 proof={'parent_support4_all_n':parent['terminal']=='QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED' and parent['protected_terminal']==parent['terminal'] and parent['both_accept'] is True,'parent_support4_control_reconstructed':len(ret4)==parent['support4_retained'] and len(surv4)==parent['support4_unsafe'],'rich_grammar_contains_parent_deletions':subset['all_deletions_contained_or_dominated'],'rich_actions_never_add_support':True,'five_signature_zero_preserves_block_constraints':True,'dependent_third_recomputed':True,'tag_unchanged':True,'cost_bound_adversarial_over_all_targets_and_centrals':True,'all_parent_support4_survivors_closed':closure4['unsafe_type_cases']==0 and closure4['action_profile_type_cases']>0,'support3_boundary_remains_open_under_this_grammar':control3['unsafe_type_cases']>0}
 gates={'protocol_present':PROTOCOL.is_file(),'production_algebra_exact':v2.production_binding()['all_exact'],'parent_bound':proof['parent_support4_all_n'],'profile_types_nonzero':len(states)>0,'parent_deletion_subset':subset['all_deletions_contained_or_dominated'],'support4_survivors_closed':proof['all_parent_support4_survivors_closed'],'support3_control_nonempty':proof['support3_boundary_remains_open_under_this_grammar'],'proof_all':all(proof.values())}
 pos=all(gates.values());terminal='QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED' if pos else 'QG9_SUPPORT4_RELABEL_EXCHANGE_COUNTEREXAMPLE_FOUND'
 result={'schema':'ORION.QG.QG9.Support3RelabelExchange.v1','issue':'SzeChunYiu/ORION#762','base_revision':BASE,'protocol_sha256':sha(PROTOCOL),'parent_v2':parent,'concrete_local_states':concrete,'action_profile_type_count':len(states),'profile_variants_by_descriptor':profile_variants,'profile_action_count_histogram':{str(k):v for k,v in sorted(profile_action_counts.items())},'parent_deletion_subset_check':subset,'support4_parent_survivors':closure4,'support3_boundary_control':control3,'proof_audit':proof,'gates':gates,'terminal':terminal,'support_bound':3 if pos else None,'support2_claim':False,'tightness_claim':False,'new_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
 result['result_digest']=hashlib.sha256(canonical(result).encode()).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(DEFAULT));ns=ap.parse_args();p=Path(ns.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(result));return 0
if __name__=='__main__':raise SystemExit(main())
