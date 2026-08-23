#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-34 adaptive minimax depth."""
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEV=ROOT/"development/orion-qg-regime-geometry";sys.path.insert(0,str(DEV))
import qg32_generic_verify as base  # noqa:E402
SRC=ROOT/"artifacts/orion-qg-qg34-adaptive-probe-tree.json";PARENT=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg34-generic-verification.json";TOKEN="ORIONQG_QG34_GENERIC=";FIXED=(18,68,101,181,139)
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(d):
 u={k:v for k,v in d.items() if k!='result_digest'};return d.get('result_digest')==hashlib.sha256(canon(u).encode()).hexdigest()
class V:
 def __init__(self,mat,members):
  self.mat=mat;self.members=tuple(members);self.max_arity=max(len(set(int(mat[g,p]) for g in self.members)) for p in range(mat.shape[1])) if len(self.members)>1 else 1;self.stats=Counter()
  @lru_cache(maxsize=None)
  def can(state,d):
   self.stats['calls']+=1;n=len(state)
   if n<=1:return True
   if d<=0:return False
   if n>self.max_arity**d:self.stats['info_prunes']+=1;return False
   cap=self.max_arity**(d-1);seen=set();cands=[]
   for p in range(mat.shape[1]-1,-1,-1):
    by={}
    for g in state:
     v=int(mat[g,p]);by.setdefault(v,[]).append(g)
    if len(by)<=1:continue
    children=tuple(tuple(x) for _,x in sorted((v,tuple(sorted(gs))) for v,gs in by.items()))
    sig=tuple(sorted(children))
    if sig in seen:continue
    seen.add(sig);mx=max(len(x) for x in children)
    if mx>cap:continue
    cands.append((-len(children),mx,-p,p,children))
   cands.sort()
   for _ng,_mx,_np,p,children in cands:
    if all(can(ch,d-1) for ch in sorted(children,key=lambda x:(-len(x),x))):return True
   return False
  self.can=can
 def min_depth(self):
  if len(self.members)<=1:return 0
  for d in range(0,5):
   if self.can(self.members,d):return d
  if len({tuple(int(self.mat[g,p]) for p in FIXED) for g in self.members})!=len(self.members):raise AssertionError('fixed upper bound binding')
  return 5

def verify_tree(node,state,mat,reps):
 if node.get('type')=='leaf':
  ok=len(state)==1 and node.get('orbit_index')==state[0] and node.get('representative')==list(reps[state[0]])
  return ok,0,1
 if node.get('type')!='probe' or node.get('state_size')!=len(state):return False,0,0
 p=node.get('probe_index')
 if not isinstance(p,int) or not 0<=p<mat.shape[1]:return False,0,0
 by={}
 for g in state:by.setdefault(int(mat[g,p]),[]).append(g)
 if len(by)<=1:return False,0,0
 got=node.get('children',[]);want=sorted(by)
 if [x.get('response') for x in got]!=want:return False,0,0
 md=0;leaves=0
 for row in got:
  v=row['response'];ch=tuple(sorted(by[v]));ok,d,l=verify_tree(row.get('node',{}),ch,mat,reps)
  if not ok:return False,0,0
  md=max(md,1+d);leaves+=l
 return True,md,leaves

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=SRC);ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());z=base.construct();parent=json.loads(PARENT.read_text());depths=[];agg=Counter();sol=[]
 for g in z['joint']:
  v=V(z['mat'],tuple(g));depths.append(v.min_depth());agg.update(v.stats);sol.append(v)
 dh={str(k):int(v) for k,v in sorted(Counter(depths).items())};mass=Counter()
 for g,d in zip(z['joint'],depths):mass[d]+=len(g)
 mdh={str(k):int(v) for k,v in sorted(mass.items())};worst=max(depths);wids=[i for i,d in enumerate(depths) if d==worst];pol=src.get('first_worst_class_policy',{});ci=pol.get('class_index');tree_ok=False;td=lc=None
 if isinstance(ci,int) and 0<=ci<len(z['joint']):tree_ok,td,lc=verify_tree(pol.get('tree',{}),tuple(z['joint'][ci]),z['mat'],z['reps']);tree_ok=tree_ok and td==depths[ci] and lc==len(z['joint'][ci])
 parent_ok=parent.get('both_accept') is True and parent.get('certified_probe_upper_bound')==5 and tuple(parent.get('selected_probe_indices',[]))==FIXED
 checks={'digest':valid(src),'parent':parent_ok,'orbits':len(z['reps'])==715,'probes':z['mat'].shape[1]==384,'joint_classes':len(z['joint'])==92,'class_depths':src.get('class_depths')==depths,'depth_histogram':src.get('depth_histogram')==dh,'orbit_mass_histogram':src.get('orbit_mass_depth_histogram')==mdh,'worst':src.get('worst_case_depth')==worst and src.get('worst_class_indices')==wids,'policy':tree_ok,'authority':src.get('EXACT_ADAPTIVE_MINIMAX_AUTHORITY') is True and all(src.get(k) is False for k in ('EXACT_FIXED_PROBE_MINIMUM_BOUND','ADAPTIVITY_ADVANTAGE_OVER_EXACT_FIXED_MINIMUM','MINIMUM_FULL_FINITE_OPTIMUM_PROBES','HARDWARE_MEASUREMENT_MINIMUM','QG28_GLOBAL_STATE_MINIMALITY','novelty_authority','physical_quantum_advantage_claim'))};ok=all(checks.values());out={'schema':'ORIONQG.QG34.GenericVerification.v1','decision':'ACCEPT_EXACT_ADAPTIVE_MINIMAX' if ok else 'REJECT','all_checks':ok,'checks':checks,'independent':{'class_depths':depths,'depth_histogram':dh,'orbit_mass_depth_histogram':mdh,'worst_case_depth':worst,'worst_class_indices':wids,'dp_stats':dict(agg),'policy_tree_depth':td,'policy_leaf_count':lc},'EXACT_FIXED_PROBE_MINIMUM_BOUND':False,'ADAPTIVITY_ADVANTAGE_OVER_EXACT_FIXED_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'QG28_GLOBAL_STATE_MINIMALITY':False,'novelty_authority':False,'physical_quantum_advantage_claim':False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'decision':out['decision'],'worst_depth':worst,'depth_histogram':dh,'dp_calls':agg['calls'],'policy_ok':tree_ok}));return 0
if __name__=='__main__':raise SystemExit(main())
