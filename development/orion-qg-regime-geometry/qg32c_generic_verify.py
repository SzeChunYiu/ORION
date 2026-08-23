#!/usr/bin/env python3
"""Independent verifier for QG-32c exact 2+2 meet-in-the-middle replication."""
from __future__ import annotations
import argparse, hashlib, itertools, json, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEV=ROOT/"development/orion-qg-regime-geometry";sys.path.insert(0,str(DEV))
import qg32_generic_verify as base  # noqa:E402
SRC=ROOT/"artifacts/orion-qg-qg32c-mitm-replication.json";OUT=ROOT/"artifacts/orion-qg-qg32c-generic-verification.json";TOKEN="ORIONQG_QG32C_GENERIC="
YES="QG32C_INDEPENDENT_REPLICATION_FINDS_FOUR_OR_FEWER_SEPARATOR";NO="QG32C_INDEPENDENT_REPLICATION_CONFIRMS_NO_FOUR_PROBE_SEPARATOR"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(d):
 u={k:v for k,v in d.items() if k!="result_digest"};return d.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def collapse(covers):
 by=defaultdict(list)
 for p,c in enumerate(covers):
  if c:by[int(c)].append(p)
 rows=sorted(((c,min(ps)) for c,ps in by.items()),key=lambda x:(-x[0].bit_count(),x[1]));keep=[]
 for c,p in rows:
  if any((c|d)==d for d,_ in keep):continue
  keep.append((c,p))
 return sorted(keep,key=lambda x:x[1])
def halves(entries):
 d={0:()}
 for i,(c,_) in enumerate(entries):d.setdefault(c,(i,))
 for i,j in itertools.combinations(range(len(entries)),2):
  m=entries[i][0]|entries[j][0];w=(i,j)
  if m not in d or w<d[m]:d[m]=w
 # Deliberately order by decreasing coverage, unlike production's witness-first order.
 return sorted(((m,w) for m,w in d.items()),key=lambda x:(-x[0].bit_count(),x[0],x[1]))
def decide(entries,npairs):
 U=(1<<npairs)-1;hs=halves(entries);post=[[] for _ in range(npairs)]
 for i,(m,_) in enumerate(hs):
  x=m
  while x:
   b=x&-x;post[b.bit_length()-1].append(i);x-=b
 order=sorted(range(npairs),key=lambda j:(len(post[j]),j));tested=0
 for ai,(a,wa) in enumerate(hs):
  missing=U&~a
  if not missing:return True,tuple(sorted(entries[i][1] for i in wa)),{"half_union_count":len(hs),"halves_scanned":ai+1,"tested":tested}
  pivot=next(j for j in order if (missing>>j)&1)
  # Exact because every completing second half must cover pivot; full union is checked.
  for bi in post[pivot]:
   tested+=1;b,wb=hs[bi]
   if (a|b)==U:
    idx=tuple(sorted(set(wa)|set(wb)));return True,tuple(sorted(entries[i][1] for i in idx)),{"half_union_count":len(hs),"halves_scanned":ai+1,"tested":tested}
 return False,(),{"half_union_count":len(hs),"halves_scanned":len(hs),"tested":tested}
def covers(z,ps):
 rem=(1<<len(z["pairs"]))-1
 for p in ps:rem&=~int(z["covers"][p])
 return rem==0
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());z=base.construct();entries=collapse(z["covers"]);exists,w,stats=decide(entries,len(z["pairs"]));wok=(not exists) or (1<=len(w)<=4 and covers(z,w));sm=(exists and src.get("terminal")==YES and src.get("EXISTS_SEPARATOR_AT_MOST_4") is True) or ((not exists) and src.get("terminal")==NO and src.get("EXISTS_SEPARATOR_AT_MOST_4") is False);checks={"digest":valid(src),"source_match":sm,"witness":wok,"orbits":len(z["reps"])==715,"probes":z["mat"].shape[1]==384,"joint":len(z["joint"])==92,"pairs":len(z["pairs"])==5895,"classes":len(entries)==168,"boundaries":all(src.get(k) is False for k in ("ADAPTIVE_TREE_OPTIMALITY","MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","novelty_authority","physical_quantum_advantage_claim"))};ok=all(checks.values());dec="ACCEPT_YES" if ok and exists else ("ACCEPT_NO" if ok and not exists else "REJECT");out={"schema":"ORIONQG.QG32C.GenericVerification.v1","decision":dec,"all_checks":ok,"checks":checks,"independent":{"method":"EXACT_2_PLUS_2_MITM_PIVOT_POSTING","EXISTS_SEPARATOR_AT_MOST_4":exists,"witness_probe_indices":list(w),**stats},"ADAPTIVE_TREE_OPTIMALITY":False,"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":dec,"exists_le4":exists,"witness":list(w),**stats}));return 0
if __name__=="__main__":raise SystemExit(main())
