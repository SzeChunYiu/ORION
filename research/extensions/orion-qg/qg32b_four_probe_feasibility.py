#!/usr/bin/env python3
"""QG-32b production exact decision: does any <=4 fixed probe separator exist?"""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
DEV=ROOT/"development/orion-qg-regime-geometry"
sys.path.insert(0,str(DEV))
import qg32_min_separating_probes as q32  # noqa:E402

PROTO=DEV/"QG32B_FOUR_PROBE_FEASIBILITY_PROTOCOL_V1.md"
PARENT=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json"
OUT=ROOT/"artifacts/orion-qg-qg32b-four-probe.json"
TOKEN="ORIONQG_QG32B="
YES="QG32B_FOUR_PROBE_SEPARATOR_EXISTS__WITNESS_MACHINE_CHECKED"
NO="QG32B_NO_FOUR_PROBE_SEPARATOR__FIVE_IS_EXACT_MINIMUM_MACHINE_CHECKED"

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()

def reconstruct():
 aa=q32.autos();ps=list(itertools.product((0,1),repeat=3));aux=q32.aux48();obs={}
 for t in itertools.product(range(4),repeat=6):
  o=q32.orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs)
 bulk=[tuple(q32.baseline(r,p) for p in ps[:4]) for r in reps]
 mat=np.array([q32.response(r,ps,aux) for r in reps],dtype=np.int16)
 spectrum=[tuple(sorted(int(x) for x in row)) for row in mat]
 joint=q32.make_groups([(bulk[i],spectrum[i]) for i in range(len(reps))])
 pairs=q32.pairs_from_groups(joint)
 physical_bits,covers,physical_reps,cover_groups=q32.coverage_classes(pairs,mat)
 return {"ps":ps,"aux":aux,"reps":reps,"bulk":bulk,"mat":mat,"spectrum":spectrum,"joint":joint,"pairs":pairs,"physical_bits":physical_bits,"covers":covers,"physical_reps":physical_reps,"cover_groups":cover_groups}

def nondominated(z):
 entries=[(int(c),int(p),tuple(int(x) for x in z["cover_groups"][c])) for c,p in zip(z["covers"],z["physical_reps"])]
 entries.sort(key=lambda e:(-e[0].bit_count(),e[1]))
 keep=[];dominated=0
 for c,p,phys in entries:
  if any((c|d)==d for d,_,_ in keep):dominated+=1;continue
  keep.append((c,p,phys))
 keep.sort(key=lambda e:e[1])
 return keep,dominated

def exact_search(z,entries,max_slots=4):
 covers=[e[0] for e in entries];reps=[e[1] for e in entries];M=len(z["pairs"]);U=(1<<M)-1
 pair_cands=[]
 for j in range(M):
  bit=1<<j;cc=tuple(i for i,c in enumerate(covers) if c&bit)
  if not cc:raise AssertionError(("uncoverable pair",j))
  pair_cands.append(cc)
 pair_order=sorted(range(M),key=lambda j:(len(pair_cands[j]),j))
 false_memo=set();stats={"nodes":0,"memo_hits":0,"bound_prunes":0,"no_progress_prunes":0,"dead_pair_prunes":0,"max_depth":0}
 def rec(rem,slots,depth):
  stats["nodes"]+=1;stats["max_depth"]=max(stats["max_depth"],depth)
  if rem==0:return ()
  if slots==0:return None
  key=(rem,slots)
  if key in false_memo:stats["memo_hits"]+=1;return None
  maxcov=0
  for c in covers:
   n=(c&rem).bit_count()
   if n>maxcov:maxcov=n
  if maxcov==0 or (rem.bit_count()+maxcov-1)//maxcov>slots:
   stats["bound_prunes"]+=1;false_memo.add(key);return None
  pivot=None;choices=None
  for j in pair_order:
   if (rem>>j)&1:
    cc=[i for i in pair_cands[j] if covers[i]&rem]
    if not cc:
     stats["dead_pair_prunes"]+=1;false_memo.add(key);return None
    pivot=j;choices=cc;break
  choices.sort(key=lambda i:(-(covers[i]&rem).bit_count(),reps[i]))
  for i in choices:
   nr=rem&~covers[i]
   if nr==rem:stats["no_progress_prunes"]+=1;continue
   sol=rec(nr,slots-1,depth+1)
   if sol is not None:return (i,)+sol
  false_memo.add(key);return None
 sol=rec(U,max_slots,0)
 physical=tuple(sorted(reps[i] for i in sol)) if sol is not None else ()
 return physical,stats,len(false_memo),sha([(c,p) for c,p,_ in entries])

def separates(z,probes):
 sig={(z["bulk"][i],z["spectrum"][i],tuple(int(z["mat"][i,p]) for p in probes)) for i in range(len(z["reps"]))}
 return len(sig)==715

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();z=reconstruct();entries,dominated=nondominated(z);witness,stats,memo_size,family_digest=exact_search(z,entries,4)
 parent=json.loads(PARENT.read_text())
 parent_checks={
  "upper_only":parent.get("terminal")=="QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY" and parent.get("authority_level")=="UPPER_ONLY",
  "parent_counts":parent.get("joint_partition",{}).get("class_count")==92 and parent.get("joint_partition",{}).get("unresolved_pair_count")==5895,
  "five_probe_separator":parent.get("JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED") is True and parent.get("certified_probe_upper_bound")==5 and len(parent.get("selected_probe_indices",[]))==5,
  "minimum_withheld":parent.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is False and parent.get("minimum_probe_cardinality") is None,
 }
 recon={"orbits":len(z["reps"]),"probes":z["mat"].shape[1],"joint_classes":len(z["joint"]),"unresolved_pairs":len(z["pairs"]),"distinct_coverage_classes":len(z["covers"]),"nondominated_coverage_classes":len(entries),"dominated_classes_removed":dominated,"coverage_family_sha256":family_digest}
 recon_ok=recon["orbits"]==715 and recon["probes"]==384 and recon["joint_classes"]==92 and recon["unresolved_pairs"]==5895
 exists=bool(witness);witness_ok=separates(z,witness) if witness else True
 if not all(parent_checks.values()) or not recon_ok or not witness_ok:term="QG32B_CANNOT_CHECK"
 elif exists:term=YES
 else:term=NO
 out={
  "schema":"ORIONQG.QG32B.FourProbeFeasibility.v1","issue":"SzeChunYiu/ORION#918","terminal":term,"protocol_sha256":shaf(PROTO),"parent_hashes":{"qg32":shaf(PARENT)},"parent_checks":parent_checks,"reconstruction":recon,
  "EXISTS_SEPARATOR_AT_MOST_4":exists if term in {YES,NO} else None,"witness_probe_indices":list(witness),"witness_size":len(witness),"witness_separates_715":bool(witness and witness_ok),
  "search":{"max_slots":4,"stats":stats,"false_memo_size":memo_size,"complete_no_if_no_witness":term==NO},
  "PARENT_FIVE_PROBE_UPPER_BOUND_BOUND":all(parent_checks.values()),
  "MINIMUM_FIXED_PROBE_CARDINALITY":5 if term==NO else None,
  "MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY":term==NO,
  "FOUR_OR_FEWER_SEPARATOR_WITNESS_AUTHORITY":term==YES,
  "MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"ADAPTIVE_TREE_OPTIMALITY":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False,
 }
 raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(TOKEN+canon({"terminal":term,"exists_le4":out["EXISTS_SEPARATOR_AT_MOST_4"],"witness":list(witness),"nondominated":len(entries),"nodes":stats["nodes"],"memo":memo_size,"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
