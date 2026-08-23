#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-32 minimum fixed probe cardinality."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any
import numpy as np

ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/orion-qg-qg32-min-probes.json";QG31=ROOT/"research/extensions/orion-qg/QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg32-generic-verification.json";TOKEN="ORIONQG_QG32_GENERIC="
BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def mul(a,b):ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def sy(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def f3(a,b,c):return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def orbit(t,aa):return {tuple(a[x] for x in t) for a in aa}
def perm(t,p):
 o=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def baseline(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=sy(tag,fr[0]),sy(tag,fr[1]);ok=l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append((fr,tag))
 return rows
def structural(fr,tag):
 raw=0
 for j in range(3):raw+=2*int(fr[2*j]!=0)+4*int(fr[2*j+1]!=0)
 return raw+2*int(tag!=0)-18
def restore(pt,fr):
 r=[mul(pt[i],fr[i]) for i in range(6)];return f3(r[0],r[2],r[4])+f3(r[1],r[3],r[5])
def response(rep,ps,aux):
 out=[]
 for p in ps:
  pt=perm(rep,p);b=baseline(rep,p)
  for fr,tag in aux:out.append(structural(fr,tag)+restore(pt,fr)-b)
 return tuple(out)
def make_groups(vals):
 d=defaultdict(list)
 for i,v in enumerate(vals):d[v].append(i)
 return [d[k] for k in sorted(d,key=lambda x:canon(x))]
def pairs_from_groups(groups):return [(a,b) for g in groups for a,b in itertools.combinations(g,2)]
def h(groups):return {str(k):int(v) for k,v in sorted(Counter(len(g) for g in groups).items())}
def construct():
 aa=autos();ps=list(itertools.product((0,1),repeat=3));aux=aux48();obs={}
 for t in itertools.product(range(4),repeat=6):
  o=orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs);bulk=[tuple(baseline(r,p) for p in ps[:4]) for r in reps];mat=np.array([response(r,ps,aux) for r in reps],dtype=np.int16);spec=[tuple(sorted(int(x) for x in row)) for row in mat];joint=make_groups([(bulk[i],spec[i]) for i in range(len(reps))]);pairs=pairs_from_groups(joint);covers=[0]*mat.shape[1]
 for j,(a,b) in enumerate(pairs):
  ds=np.flatnonzero(mat[a]!=mat[b]);assert len(ds)>0;bit=1<<j
  for p in ds:covers[int(p)]|=bit
 return {"ps":ps,"aux":aux,"reps":reps,"bulk":bulk,"mat":mat,"spec":spec,"joint":joint,"pairs":pairs,"covers":covers}
def nondominated_unique(covers):
 uniq=sorted(set(int(c) for c in covers if c),key=lambda x:(-x.bit_count(),x))
 keep=[]
 for c in uniq:
  if any((c|d)==d for d in keep):continue
  keep.append(c)
 return tuple(keep)
def verify_minimum(z,src):
 m=int(src["minimum_probe_cardinality"]);selected=tuple(int(x) for x in src["selected_probe_indices"]);M=len(z["pairs"]);U=(1<<M)-1;physical=z["covers"]
 rem=U
 for p in selected:rem &= ~physical[p]
 selected_separates=rem==0 and len(selected)==m
 covers=nondominated_unique(physical)
 pair_candidates=[]
 for j in range(M):
  bit=1<<j;pair_candidates.append(tuple(i for i,c in enumerate(covers) if c&bit))
 @lru_cache(maxsize=None)
 def search(rem:int,slots:int,start:int)->bool:
  if rem==0:return True
  if slots<=0:return False
  bestcov=0
  for i in range(start,len(covers)):
   n=(covers[i]&rem).bit_count()
   if n>bestcov:bestcov=n
  if bestcov==0 or (rem.bit_count()+bestcov-1)//bestcov>slots:return False
  # Choose a remaining pair with the fewest still-available probe classes.
  best_choices=None
  x=rem
  while x:
   lsb=x&-x;j=lsb.bit_length()-1;x-=lsb
   choices=tuple(i for i in pair_candidates[j] if i>=start and (covers[i]&rem))
   if not choices:return False
   if best_choices is None or len(choices)<len(best_choices):
    best_choices=choices
    if len(choices)==1:break
  ordered=sorted(best_choices,key=lambda i:(-(covers[i]&rem).bit_count(),i))
  for i in ordered:
   nr=rem & ~covers[i]
   if nr!=rem and search(nr,slots-1,i+1):return True
  return False
 no_smaller=not search(U,m-1,0)
 pack=src.get("lower_bound_packing",{});packing_attempted=bool(pack.get("attempted"));packing_closes=False;packing_valid=True
 if packing_attempted:
  rep_to_i={tuple(r):i for i,r in enumerate(z["reps"])};sets=[]
  for row in pack.get("pairs",[]):
   a=rep_to_i.get(tuple(row["representative_1"]));b=rep_to_i.get(tuple(row["representative_2"]));
   if a is None or b is None:packing_valid=False;break
   ds=frozenset(int(p) for p in np.flatnonzero(z["mat"][a]!=z["mat"][b]));packing_valid &= len(ds)==row.get("distinguishing_probe_count") and hashlib.sha256(canon(tuple(sorted(ds))).encode()).hexdigest()==row.get("distinguishing_probes_sha256");sets.append(ds)
  if packing_valid:
   for i in range(len(sets)):
    for j in range(i+1,len(sets)):
     if sets[i]&sets[j]:packing_valid=False
  packing_closes=packing_valid and len(sets)==m
 return {"selected_separates":selected_separates,"physical_probe_count":len(physical),"unique_nondominated_cover_classes":len(covers),"packing_attempted":packing_attempted,"packing_valid":packing_valid,"packing_closes":packing_closes,"no_smaller":no_smaller,"branch_cache":search.cache_info()._asdict()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());z=construct();q31=json.loads(QG31.read_text());v=verify_minimum(z,src)
 parent=q31.get("both_accept") is True and q31.get("QUERY_INDEXED_ABSTRACTION_REQUIRED") is True and q31.get("class_counts")=={"bulk":45,"defect_spectrum":54,"indexed_local_response":715}
 checks={"source_digest":valid(src),"parent":parent,"orbits":len(z["reps"])==715,"probes":z["mat"].shape[1]==384,"joint_count":len(z["joint"])==src.get("joint_partition",{}).get("class_count"),"joint_hist":h(z["joint"])==src.get("joint_partition",{}).get("class_size_histogram"),"unresolved_pairs":len(z["pairs"])==src.get("joint_partition",{}).get("unresolved_pair_count"),"selected":v["selected_separates"],"minimum":v["no_smaller"],"authority_false":all(src.get(k) is False for k in ("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","ADAPTIVE_TREE_OPTIMALITY","novelty_authority","physical_quantum_advantage_claim"))}
 ok=all(checks.values());out={"schema":"ORIONQG.QG32.GenericVerification.v1","decision":"ACCEPT_MINIMUM_FIXED_PROBE_BASIS" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"independent":{"joint_class_count":len(z["joint"]),"joint_class_size_histogram":h(z["joint"]),"unresolved_pair_count":len(z["pairs"]),"minimum_probe_cardinality":src.get("minimum_probe_cardinality"),"selected_probe_indices":src.get("selected_probe_indices"),"proof":v},"source_result_digest":src.get("result_digest"),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"ADAPTIVE_TREE_OPTIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"joint_classes":len(z["joint"]),"pairs":len(z["pairs"]),"m":src.get("minimum_probe_cardinality"),"cover_classes":v["unique_nondominated_cover_classes"],"packing_closes":v["packing_closes"],"no_smaller":v["no_smaller"],"branch_cache":v["branch_cache"]}));return 0
if __name__=="__main__":raise SystemExit(main())
