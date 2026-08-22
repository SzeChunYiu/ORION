#!/usr/bin/env python3
"""QG-34 production exact adaptive minimax probe tree above QG-32 joint summaries."""
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
DEV=ROOT/"development/orion-qg-regime-geometry";sys.path.insert(0,str(DEV))
import qg32_generic_verify as base  # noqa:E402

PROTO=DEV/"QG34_ADAPTIVE_PROBE_TREE_PROTOCOL_V1.md"
PARENT=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json"
OUT=ROOT/"artifacts/orion-qg-qg34-adaptive-probe-tree.json";TOKEN="ORIONQG_QG34="
TERM="QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED"
FIXED=(18,68,101,181,139)

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

class Solver:
 def __init__(self,mat,globals_):
  self.mat=mat;self.globals=tuple(globals_);self.n=len(self.globals);self.full=(1<<self.n)-1
  self.probe_parts={};seen={}
  for p in range(mat.shape[1]):
   by={}
   for li,gi in enumerate(self.globals):
    v=int(mat[gi,p]);by[v]=by.get(v,0)|(1<<li)
   if len(by)<=1:continue
   key=tuple(sorted(by.values()))
   if key in seen:continue
   seen[key]=p;self.probe_parts[p]=tuple(sorted(by.items()))
  self.probes=tuple(sorted(self.probe_parts));self.max_arity=max((len(x) for x in self.probe_parts.values()),default=1)
  self.choice={};self.stats=Counter()
  @lru_cache(maxsize=None)
  def can(mask,d):
   self.stats['calls']+=1;n=mask.bit_count()
   if n<=1:return True
   if d<=0:return False
   if n>self.max_arity**d:self.stats['info_prunes']+=1;return False
   cap=self.max_arity**(d-1);cands=[];seen_restricted=set()
   for p in self.probes:
    children=tuple(sorted((m&mask for _,m in self.probe_parts[p] if m&mask),key=lambda x:(-x.bit_count(),x)))
    if len(children)<=1:continue
    sig=tuple(sorted(children))
    if sig in seen_restricted:self.stats['restricted_duplicate_prunes']+=1;continue
    seen_restricted.add(sig)
    mx=max(c.bit_count() for c in children)
    if mx>cap:self.stats['child_capacity_prunes']+=1;continue
    cands.append((mx,-len(children),p,children))
   cands.sort()
   for _mx,_neg,p,children in cands:
    ok=True
    for child in children:
     if not can(child,d-1):ok=False;break
    if ok:self.choice[(mask,d)]=p;return True
   return False
  self.can=can
 def minimum_depth(self):
  if self.n<=1:return 0
  lb=0;cap=1
  while cap<self.n:lb+=1;cap*=self.max_arity
  for d in range(lb,5):
   if self.can(self.full,d):return d
  sigs={tuple(int(self.mat[g,p]) for p in FIXED) for g in self.globals}
  if len(sigs)!=self.n:raise AssertionError('QG32 fixed upper bound did not separate class')
  return 5
 def _partition(self,mask,p):
  by={}
  for li,gi in enumerate(self.globals):
   if (mask>>li)&1:
    v=int(self.mat[gi,p]);by[v]=by.get(v,0)|(1<<li)
  return tuple(sorted(by.items()))
 def build_choice_tree(self,mask,d,reps):
  if mask.bit_count()==1:
   li=(mask&-mask).bit_length()-1;gi=self.globals[li]
   return {'type':'leaf','orbit_index':gi,'representative':list(reps[gi])}
  p=self.choice.get((mask,d))
  if p is None:raise AssertionError(('missing choice',mask,d))
  children=[]
  for v,ch in self._partition(mask,p):
   if ch:children.append({'response':v,'node':self.build_choice_tree(ch,d-1,reps)})
  if len(children)<=1:raise AssertionError('non-splitting policy node')
  return {'type':'probe','probe_index':p,'state_size':mask.bit_count(),'children':children}
 def build_fixed_tree(self,mask,pos,reps):
  if mask.bit_count()==1:
   li=(mask&-mask).bit_length()-1;gi=self.globals[li]
   return {'type':'leaf','orbit_index':gi,'representative':list(reps[gi])}
  k=pos
  while k<len(FIXED):
   p=FIXED[k];parts=[(v,ch) for v,ch in self._partition(mask,p) if ch]
   if len(parts)>1:
    return {'type':'probe','probe_index':p,'state_size':mask.bit_count(),'children':[{'response':v,'node':self.build_fixed_tree(ch,k+1,reps)} for v,ch in parts]}
   k+=1
  raise AssertionError('fixed basis exhausted before singleton')

def tree_depth(t):
 if t['type']=='leaf':return 0
 return 1+max(tree_depth(x['node']) for x in t['children'])
def leaf_count(t):
 if t['type']=='leaf':return 1
 return sum(leaf_count(x['node']) for x in t['children'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args();z=base.construct();parent=json.loads(PARENT.read_text())
 parent_ok=parent.get('both_accept') is True and parent.get('JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED') is True and parent.get('certified_probe_upper_bound')==5 and tuple(parent.get('selected_probe_indices',[]))==FIXED and parent.get('ADAPTIVE_TREE_OPTIMALITY') is False
 expected_hist={'1':7,'2':22,'3':6,'4':6,'6':25,'8':2,'12':14,'24':8,'48':2};size_hist={str(k):int(v) for k,v in sorted(Counter(len(g) for g in z['joint']).items())}
 recon_ok=len(z['reps'])==715 and z['mat'].shape==(715,384) and len(z['joint'])==92 and size_hist==expected_hist
 depths=[];summaries=[];aggregate=Counter();solvers=[]
 for ci,g in enumerate(z['joint']):
  s=Solver(z['mat'],g);d=s.minimum_depth();solvers.append(s);depths.append(d);aggregate.update(s.stats)
  summaries.append({'class_index':ci,'size':len(g),'depth':d,'max_response_arity':s.max_arity,'unique_full_probe_partitions':len(s.probes),'can_cache':s.can.cache_info()._asdict(),'stats':dict(s.stats)})
 dh={str(k):int(v) for k,v in sorted(Counter(depths).items())};mass=Counter()
 for g,d in zip(z['joint'],depths):mass[d]+=len(g)
 mdh={str(k):int(v) for k,v in sorted(mass.items())};worst=max(depths);worst_ids=[i for i,d in enumerate(depths) if d==worst];wi=worst_ids[0];ws=solvers[wi]
 tree=ws.build_choice_tree(ws.full,worst,z['reps']) if worst<5 else ws.build_fixed_tree(ws.full,0,z['reps']);td=tree_depth(tree);lc=leaf_count(tree);tree_ok=td==worst and lc==len(z['joint'][wi])
 exact=parent_ok and recon_ok and tree_ok and all(0<=d<=5 for d in depths)
 out={'schema':'ORIONQG.QG34.AdaptiveProbeTree.v1','issue':'SzeChunYiu/ORION#924','terminal':TERM if exact else 'QG34_CANNOT_CHECK','protocol_sha256':shaf(PROTO),'parent_qg32_sha256':shaf(PARENT),'parent_checks':{'qg32_fixed_upper_bound':parent_ok,'reconstruction':recon_ok},'universe':{'orbits':len(z['reps']),'probes':z['mat'].shape[1],'joint_classes':len(z['joint']),'joint_class_size_histogram':size_hist},'class_depths':depths,'depth_histogram':dh,'orbit_mass_depth_histogram':mdh,'worst_case_depth':worst,'worst_class_indices':worst_ids,'worst_class_sizes':[len(z['joint'][i]) for i in worst_ids],'class_summaries':summaries,'first_worst_class_policy':{'class_index':wi,'class_members':list(z['joint'][wi]),'tree_depth':td,'leaf_count':lc,'tree':tree},'aggregate_dp_stats':dict(aggregate),'QG32_CERTIFIED_FIXED_BASIS_LENGTH':5,'ADAPTIVE_DEPTH_BELOW_QG32_CERTIFIED_FIXED_BASIS_LENGTH':worst<5,'EXACT_ADAPTIVE_MINIMAX_AUTHORITY':bool(exact),'EXACT_FIXED_PROBE_MINIMUM_BOUND':False,'ADAPTIVITY_ADVANTAGE_OVER_EXACT_FIXED_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'QG28_GLOBAL_STATE_MINIMALITY':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
 raw=canon(out);out['result_digest']=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':out['terminal'],'worst_depth':worst,'depth_histogram':dh,'orbit_mass_depth_histogram':mdh,'worst_classes':worst_ids,'dp_calls':aggregate['calls'],'result_digest':out['result_digest']}));return 0
if __name__=='__main__':raise SystemExit(main())
