#!/usr/bin/env python3
"""QG-32 production analyzer: fixed separating probes above joint bulk+spectrum summaries."""
from __future__ import annotations
import argparse,hashlib,itertools,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds
from scipy.sparse import coo_array,csr_array

ROOT=Path(__file__).resolve().parents[3];QDIR=ROOT/"research/extensions/orion-q";sys.path.insert(0,str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6s_all_n_composition as r6s  # noqa:E402
PROTO=ROOT/"development/orion-qg-regime-geometry/QG32_MIN_SEPARATING_PROBES_PROTOCOL_V1.md";QG31=ROOT/"research/extensions/orion-qg/QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg32-min-probes.json";TOKEN="ORIONQG_QG32="
PROD="QG32_PRODUCTION_MINIMUM_FIXED_PROBE_CANDIDATE_MILP_OPTIMAL";UPPER="QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY"
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def key1(c):return p10.key_from_codes([c])
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def orbit(t,aa):return {tuple(a[x] for x in t) for a in aa}
def perm(t,p):
 o=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def f3(a,b,c):return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def baseline(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def sy(a,b):return int(p10.h.local_symp(a,b))
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=sy(tag,fr[0]),sy(tag,fr[1]);ok=l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append({"frames":fr,"tag":tag,"frame_keys":tuple(key1(x) for x in fr),"tag_key":key1(tag)})
 return rows
def response(rep,ps,aux):
 out=[];c=(0,0,0)
 for p in ps:
  pt=perm(rep,p);tkeys=tuple(key1(x) for x in pt);b=baseline(rep,p)
  for a in aux:out.append(int(r6s.config_cost(tkeys,a["frame_keys"],a["tag_key"],c,1))-b)
 return tuple(out)
def pair_count(groups):return sum(len(g)*(len(g)-1)//2 for g in groups if len(g)>1)
def largest(groups):return max((len(g) for g in groups),default=0)
def hist(groups):return {str(k):int(v) for k,v in sorted(Counter(len(g) for g in groups).items())}
def make_groups(vals):
 d=defaultdict(list)
 for i,v in enumerate(vals):d[v].append(i)
 return [d[k] for k in sorted(d,key=lambda x:canon(x))]
def pairs_from_groups(groups):return [(a,b) for g in groups for a,b in itertools.combinations(g,2)]
def greedy_refine(base_groups,mat):
 groups=[list(g) for g in base_groups];chosen=[];unused=set(range(mat.shape[1]))
 while any(len(g)>1 for g in groups):
  best=None
  for p in sorted(unused):
   unresolved=0
   for g in groups:
    if len(g)<=1:continue
    cnt=Counter(int(mat[i,p]) for i in g);unresolved+=sum(n*(n-1)//2 for n in cnt.values())
   cand=(unresolved,p)
   if best is None or cand<best:best=cand
  if best is None:break
  _,p=best;chosen.append(p);unused.remove(p);new=[]
  for g in groups:
   if len(g)<=1:new.append(g);continue
   d=defaultdict(list)
   for i in g:d[int(mat[i,p])].append(i)
   new.extend(d[k] for k in sorted(d))
  groups=new
 return chosen,groups
def coverage_classes(pairs,mat):
 bits=[0]*mat.shape[1]
 for ridx,(a,b) in enumerate(pairs):
  diff=np.flatnonzero(mat[a]!=mat[b]);assert len(diff)>0;bit=1<<ridx
  for p in diff:bits[int(p)]|=bit
 groups=defaultdict(list)
 for p,b in enumerate(bits):
  if b:groups[b].append(p)
 covers=sorted(groups,key=lambda b:(min(groups[b]),b));reps=[min(groups[b]) for b in covers]
 return bits,covers,reps,groups
def incidence(covers,npairs):
 rows=[];cols=[]
 for j,b in enumerate(covers):
  x=b
  while x:
   l=x&-x;i=l.bit_length()-1;rows.append(i);cols.append(j);x-=l
 return csr_array(coo_array((np.ones(len(rows)),(np.array(rows),np.array(cols))),shape=(npairs,len(covers))))
def solve_minimum(A,time_limit=10.0):
 n=A.shape[1]
 return milp(c=np.ones(n),integrality=np.ones(n,dtype=int),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(A,np.ones(A.shape[0]),np.full(A.shape[0],np.inf)),options={"time_limit":time_limit,"mip_rel_gap":0.0,"presolve":True})
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();aa=autos();ps=list(itertools.product((0,1),repeat=3));aux=aux48();obs={}
 for t in itertools.product(range(4),repeat=6):
  o=orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs);bulk=[tuple(baseline(r,p) for p in ps[:4]) for r in reps];resp=np.array([response(r,ps,aux) for r in reps],dtype=np.int16);spect=[tuple(sorted(int(x) for x in row)) for row in resp]
 raw_groups=[list(range(len(reps)))];bulk_groups=make_groups(bulk);spec_groups=make_groups(spect);joint_groups=make_groups([(bulk[i],spect[i]) for i in range(len(reps))])
 q31=json.loads(QG31.read_text());parent={"green":q31.get("both_accept") is True and q31.get("QUERY_INDEXED_ABSTRACTION_REQUIRED") is True,"counts":q31.get("class_counts")=={"bulk":45,"defect_spectrum":54,"indexed_local_response":715},"same_joint_collision":q31.get("witnesses",{}).get("same_spectrum_same_bulk_different_indexed_response") is not None}
 qmax=max(len(set(int(x) for x in resp[:,p])) for p in range(resp.shape[1]));abl={}
 for name,groups in (("raw",raw_groups),("bulk",bulk_groups),("spectrum",spec_groups),("joint",joint_groups)):
  greedy,final=greedy_refine(groups,resp);mc=largest(groups);lb=0 if mc<=1 else max(1,math.ceil(math.log(mc,qmax)));abl[name]={"class_count":len(groups),"largest_class":mc,"unresolved_pair_count":pair_count(groups),"greedy_probe_upper_bound":len(greedy),"greedy_probe_indices":greedy,"safe_cardinality_lower_bound":lb,"greedy_separates":all(len(g)==1 for g in final)}
 pairs=pairs_from_groups(joint_groups);physical_bits,covers,reps_for_cover,cover_groups=coverage_classes(pairs,resp);A=incidence(covers,len(pairs));res=solve_minimum(A,10.0);milp_ok=res.status==0 and res.x is not None
 if milp_ok:
  minimum=int(round(float(res.fun)));chosen=[j for j,x in enumerate(res.x) if x>0.5];selected=tuple(sorted(reps_for_cover[j] for j in chosen));selection_basis="EXACT_MILP_MINIMUM"
 else:
  minimum=None;selected=tuple(int(p) for p in abl["joint"]["greedy_probe_indices"]);selection_basis="DETERMINISTIC_GREEDY_CERTIFIED_UPPER_BOUND"
 sigs={(bulk[i],spect[i],tuple(int(resp[i,p]) for p in selected)) for i in range(len(reps))};separates=len(sigs)==715
 selected_details=[]
 for p in selected:
  pi,ai=divmod(p,len(aux));vals=Counter(int(resp[i,p]) for i in range(len(reps)));selected_details.append({"probe_index":p,"permutation":ps[pi],"auxiliary_row_index":ai,"auxiliary_frames":aux[ai]["frames"],"auxiliary_tag":aux[ai]["tag"],"response_histogram":{str(k):int(v) for k,v in sorted(vals.items())},"joint_unresolved_pair_coverage":int(physical_bits[p].bit_count()),"coverage_equivalent_probe_count":len(cover_groups[physical_bits[p]])})
 if all(parent.values()) and separates and milp_ok:term=PROD
 elif all(parent.values()) and separates:term=UPPER
 else:term="QG32_PRODUCTION_CANNOT_CHECK"
 out={"schema":"ORIONQG.QG32.MinSeparatingProbes.v1","issue":"SzeChunYiu/ORION#911","terminal":term,"protocol_sha256":shaf(PROTO),"parent_hashes":{"qg31":shaf(QG31)},"parent_checks":parent,"universe":{"orbits":len(reps),"physical_probes":resp.shape[1],"distinct_pair_coverage_classes":len(covers)},"joint_partition":{"class_count":len(joint_groups),"class_size_histogram":hist(joint_groups),"largest_class":largest(joint_groups),"unresolved_pair_count":len(pairs)},"minimum_probe_cardinality":minimum,"certified_probe_upper_bound":len(selected) if separates else None,"selected_probe_indices":list(selected),"selected_probe_details":selected_details,"selected_separates_715":separates,"selection_basis":selection_basis,"milp":{"status":int(res.status),"message":str(res.message),"objective":float(res.fun) if res.fun is not None else None,"optimal":milp_ok},"lower_bound_packing":{"attempted":False,"size":0,"closes_minimum":False,"pairs":[]},"ablations":abl,"JOINT_PARTITION_RECONSTRUCTED":all(parent.values()),"UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID":True,"JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED":bool(separates),"PRODUCTION_MILP_MINIMUM_OPTIMAL":bool(milp_ok),"PRODUCTION_PACKING_LOWER_BOUND_CLOSES":False,"MINIMUM_FIXED_PROBE_BASIS_AUTHORITY":bool(milp_ok and separates),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"ADAPTIVE_TREE_OPTIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"joint_classes":len(joint_groups),"unresolved_pairs":len(pairs),"coverage_classes":len(covers),"minimum":minimum,"upper_bound":out["certified_probe_upper_bound"],"selected":list(selected),"milp_status":int(res.status),"milp_objective":out["milp"]["objective"],"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
