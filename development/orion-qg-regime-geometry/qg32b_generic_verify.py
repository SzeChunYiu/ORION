#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-32b four-probe feasibility."""
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds
from scipy.sparse import coo_array,csr_array

ROOT=Path(__file__).resolve().parents[2]
DEV=ROOT/"development/orion-qg-regime-geometry";sys.path.insert(0,str(DEV))
import qg32_generic_verify as base  # noqa:E402
SRC=ROOT/"artifacts/orion-qg-qg32b-four-probe.json";PARENT=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg32b-generic-verification.json";TOKEN="ORIONQG_QG32B_GENERIC="
YES="QG32B_FOUR_PROBE_SEPARATOR_EXISTS__WITNESS_MACHINE_CHECKED";NO="QG32B_NO_FOUR_PROBE_SEPARATOR__FIVE_IS_EXACT_MINIMUM_MACHINE_CHECKED"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def collapse_nondominated(covers):
 groups=defaultdict(list)
 for p,c in enumerate(covers):
  if c:groups[int(c)].append(p)
 entries=[(c,min(ps),tuple(ps)) for c,ps in groups.items()]
 entries.sort(key=lambda e:(-e[0].bit_count(),e[1]));keep=[]
 for e in entries:
  c=e[0]
  if any((c|d)==d for d,_,_ in keep):continue
  keep.append(e)
 keep.sort(key=lambda e:e[1]);return keep

def incidence(entries,npairs):
 rows=[];cols=[]
 for j,(c,_,_) in enumerate(entries):
  x=c
  while x:
   l=x&-x;i=l.bit_length()-1;rows.append(i);cols.append(j);x-=l
 return csr_array(
  coo_array(
   (np.ones(len(rows)),(np.array(rows,dtype=int),np.array(cols,dtype=int))),
   shape=(npairs,len(entries)),
  )
 )
def solve(entries,npairs):
 A=incidence(entries,npairs);n=len(entries);constraints=[LinearConstraint(A,np.ones(npairs),np.full(npairs,np.inf)),LinearConstraint(np.ones((1,n)),np.array([-np.inf]),np.array([4.0]))]
 return milp(c=np.zeros(n),integrality=np.ones(n,dtype=int),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=constraints,options={"time_limit":100.0,"mip_rel_gap":0.0,"presolve":True})
def separates(z,physical):
 U=(1<<len(z["pairs"]))-1
 for p in physical:U&=~z["covers"][p]
 return U==0
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text())
 z=base.construct();entries=collapse_nondominated(z["covers"]);res=solve(entries,len(z["pairs"]))
 if res.status==0 and res.x is not None:
  chosen=[i for i,x in enumerate(res.x) if x>0.5];witness=tuple(sorted(entries[i][1] for i in chosen));decision_exists=True;solver_decided=True;witness_ok=len(witness)<=4 and separates(z,witness)
 elif res.status==2:
  witness=();decision_exists=False;solver_decided=True;witness_ok=True
 else:
  witness=();decision_exists=None;solver_decided=False;witness_ok=False
 parent=json.loads(PARENT.read_text())
 parent_ok=parent.get("terminal")=="QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY" and parent.get("certified_probe_upper_bound")==5 and parent.get("JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED") is True and parent.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is False
 source_exists=src.get("EXISTS_SEPARATOR_AT_MOST_4")
 source_terminal=src.get("terminal")
 source_match=(decision_exists is True and source_exists is True and source_terminal==YES) or (decision_exists is False and source_exists is False and source_terminal==NO)
 recon=src.get("reconstruction",{})
 checks={"source_digest":valid(src),"parent":parent_ok,"solver_decided":solver_decided,"source_match":source_match,"witness_if_yes":witness_ok,"orbits":len(z["reps"])==715,"probes":z["mat"].shape[1]==384,"joint_classes":len(z["joint"])==92==recon.get("joint_classes"),"unresolved_pairs":len(z["pairs"])==5895==recon.get("unresolved_pairs"),"nondominated_count":len(entries)==recon.get("nondominated_coverage_classes"),"authority_boundary":all(src.get(k) is False for k in ("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","ADAPTIVE_TREE_OPTIMALITY","QG28_GLOBAL_STATE_MINIMALITY","novelty_authority","physical_quantum_advantage_claim"))}
 ok=all(checks.values())
 out={"schema":"ORIONQG.QG32B.GenericVerification.v1","decision":"ACCEPT_FOUR_PROBE_EXISTS" if ok and decision_exists is True else ("ACCEPT_NO_FOUR_PROBE_SEPARATOR" if ok and decision_exists is False else "REJECT"),"all_checks":bool(ok),"checks":checks,"independent":{"solver_status":int(res.status),"solver_message":str(res.message),"EXISTS_SEPARATOR_AT_MOST_4":decision_exists,"witness_probe_indices":list(witness),"witness_separates":witness_ok,"nondominated_coverage_classes":len(entries)},"source_result_digest":src.get("result_digest"),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"ADAPTIVE_TREE_OPTIMALITY":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False}
 ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"decided":solver_decided,"exists_le4":decision_exists,"witness":list(witness),"nondominated":len(entries),"status":int(res.status)}));return 0
if __name__=="__main__":raise SystemExit(main())
