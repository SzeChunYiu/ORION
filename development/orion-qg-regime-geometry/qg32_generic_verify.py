#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-32 minimum separating probes."""
from __future__ import annotations
import argparse, hashlib, itertools, json, math
from collections import Counter, defaultdict
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
 reps=sorted(obs);bulk=[tuple(baseline(r,p) for p in ps[:4]) for r in reps];mat=np.array([response(r,ps,aux) for r in reps],dtype=np.int16);spec=[tuple(sorted(int(x) for x in row)) for row in mat];joint=make_groups([(bulk[i],spec[i]) for i in range(len(reps))]);pairs=pairs_from_groups(joint)
 covers=[0]*mat.shape[1];cand=[]
 for j,(a,b) in enumerate(pairs):
  ds=tuple(int(p) for p in np.flatnonzero(mat[a]!=mat[b]));cand.append(ds);bit=1<<j
  for p in ds:covers[p]|=bit
 return {"ps":ps,"aux":aux,"reps":reps,"bulk":bulk,"mat":mat,"spec":spec,"joint":joint,"pairs":pairs,"covers":covers,"cand":cand}

def verifier(z,src):
 m=int(src["minimum_probe_cardinality"]);selected=tuple(int(x) for x in src["selected_probe_indices"]);M=len(z["pairs"]);U=(1<<M)-1;covers=z["covers"];cand=z["cand"]
 # A static rare-pair order improves the exact branch search without importing production incidence.
 pair_order=sorted(range(M),key=lambda j:(len(cand[j]),j))
 @lru_cache(maxsize=None)
 def search(rem:int,slots:int,minp:int):
  if rem==0:return ()
  if slots<=0:return None
  rc=rem.bit_count();bestcov=0
  for p in range(minp,len(covers)):
   c=(covers[p]&rem).bit_count()
   if c>bestcov:bestcov=c
  if bestcov==0 or (rc+bestcov-1)//bestcov>slots:return None
  j=None;choices=None
  for jj in pair_order:
   if (rem>>jj)&1:
    cc=[p for p in cand[jj] if p>=minp]
    if not cc:return None
    j=jj;choices=cc;break
  choices.sort(key=lambda p:(-(covers[p]&rem).bit_count(),p))
  for p in choices:
   nr=rem & ~covers[p]
   sol=search(nr,slots-1,minp)
   if sol is not None:return (p,)+sol
  return None
 # Selected set separation.
 rem=U
 for p in selected:rem &= ~covers[p]
 selected_separates=rem==0
 # Preferred independent packing certificate.
 rep_to_i={tuple(r):i for i,r in enumerate(z["reps"])};pack=src.get("lower_bound_packing",{}).get("pairs",[]);pack_sets=[];pack_valid=True
 for row in pack:
  a=rep_to_i.get(tuple(row["representative_1"]));b=rep_to_i.get(tuple(row["representative_2"]));
  if a is None or b is None:pack_valid=False;break
  ds=frozenset(int(p) for p in np.flatnonzero(z["mat"][a]!=z["mat"][b]));pack_valid &= len(ds)==row.get("distinguishing_probe_count") and hashlib.sha256(canon(tuple(sorted(ds))).encode()).hexdigest()==row.get("distinguishing_probes_sha256");pack_sets.append(ds)
 if pack_valid:
  for i in range(len(pack_sets)):
   for j in range(i+1,len(pack_sets)):
    if pack_sets[i]&pack_sets[j]:pack_valid=False
 packing_closes=pack_valid and len(pack_sets)==m
 # If the simple packing does not close, independently prove no size-(m-1) hitting set.
 no_smaller=True if packing_closes else (search(U,m-1,0) is None)
 # Lexicographic minimum check: no solution with same earlier prefix and smaller next probe.
 lex_ok=selected_separates and len(selected)==m;prefix_rem=U;prev=-1
 if lex_ok:
  for i,p in enumerate(selected):
   for q in range(prev+1,p):
    rq=prefix_rem & ~covers[q]
    if search(rq,m-i-1,q+1) is not None:lex_ok=False;break
   if not lex_ok:break
   prefix_rem &= ~covers[p];prev=p
  lex_ok &= prefix_rem==0
 return {"selected_separates":selected_separates,"packing_valid":pack_valid,"packing_closes":packing_closes,"no_smaller":no_smaller,"lexicographically_minimum":lex_ok,"branch_cache":search.cache_info()._asdict()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());z=construct();q31=json.loads(QG31.read_text());v=verifier(z,src)
 parent=q31.get("both_accept") is True and q31.get("QUERY_INDEXED_ABSTRACTION_REQUIRED") is True and q31.get("class_counts")=={"bulk":45,"defect_spectrum":54,"indexed_local_response":715}
 checks={"source_digest":valid(src),"parent":parent,"orbits":len(z["reps"])==715,"probes":z["mat"].shape[1]==384,"joint_count":len(z["joint"])==src.get("joint_partition",{}).get("class_count"),"joint_hist":h(z["joint"])==src.get("joint_partition",{}).get("class_size_histogram"),"unresolved_pairs":len(z["pairs"])==src.get("joint_partition",{}).get("unresolved_pair_count"),"selected":v["selected_separates"],"minimum":v["no_smaller"],"lex":v["lexicographically_minimum"],"authority_false":all(src.get(k) is False for k in ("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","ADAPTIVE_TREE_OPTIMALITY","novelty_authority","physical_quantum_advantage_claim"))}
 ok=all(checks.values());out={"schema":"ORIONQG.QG32.GenericVerification.v1","decision":"ACCEPT_MINIMUM_FIXED_PROBE_BASIS" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"independent":{"joint_class_count":len(z["joint"]),"joint_class_size_histogram":h(z["joint"]),"unresolved_pair_count":len(z["pairs"]),"minimum_probe_cardinality":src.get("minimum_probe_cardinality"),"selected_probe_indices":src.get("selected_probe_indices"),"proof":v},"source_result_digest":src.get("result_digest"),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"ADAPTIVE_TREE_OPTIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"joint_classes":len(z["joint"]),"pairs":len(z["pairs"]),"m":src.get("minimum_probe_cardinality"),"packing_closes":v["packing_closes"],"no_smaller":v["no_smaller"],"lex":v["lexicographically_minimum"],"branch_cache":v["branch_cache"]}));return 0
if __name__=="__main__":raise SystemExit(main())
