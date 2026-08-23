#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-32's frozen upper-bound-only terminal."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/orion-qg-qg32-min-probes.json"
QG31=ROOT/"research/extensions/orion-qg/QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json"
OUT=ROOT/"artifacts/orion-qg-qg32-generic-verification.json"
TOKEN="ORIONQG_QG32_GENERIC="
sys.path.insert(0,str(ROOT/"development/orion-qg-regime-geometry"))
import qg32_generic_verify as base  # noqa:E402

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args()
 src=json.loads(ns.input.read_text());z=base.construct();q31=json.loads(QG31.read_text())
 selected=tuple(int(x) for x in src.get("selected_probe_indices",[]));M=len(z["pairs"]);rem=(1<<M)-1
 for p in selected:rem &= ~z["covers"][p]
 separates=rem==0 and bool(selected)
 parent=q31.get("both_accept") is True and q31.get("QUERY_INDEXED_ABSTRACTION_REQUIRED") is True and q31.get("class_counts")=={"bulk":45,"defect_spectrum":54,"indexed_local_response":715}
 upper=src.get("certified_probe_upper_bound")
 checks={
  "source_digest":valid(src),
  "parent":parent,
  "source_upper_terminal":src.get("terminal")=="QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY",
  "orbits":len(z["reps"])==715,
  "probes":z["mat"].shape[1]==384,
  "joint_count":len(z["joint"])==src.get("joint_partition",{}).get("class_count"),
  "joint_hist":base.h(z["joint"])==src.get("joint_partition",{}).get("class_size_histogram"),
  "unresolved_pairs":M==src.get("joint_partition",{}).get("unresolved_pair_count"),
  "selected_separates":separates,
  "upper_bound_consistent":isinstance(upper,int) and upper==len(selected),
  "minimum_not_claimed":src.get("minimum_probe_cardinality") is None and src.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is False and src.get("PRODUCTION_MILP_MINIMUM_OPTIMAL") is False,
  "localization":src.get("UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID") is True,
  "authority_false":all(src.get(k) is False for k in ("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","ADAPTIVE_TREE_OPTIMALITY","novelty_authority","physical_quantum_advantage_claim")),
 }
 ok=all(checks.values())
 out={"schema":"ORIONQG.QG32.GenericUpperBoundVerification.v1","decision":"ACCEPT_FIXED_PROBE_UPPER_BOUND" if ok else "REJECT","authority_level":"UPPER_ONLY" if ok else "NONE","all_checks":bool(ok),"checks":checks,"independent":{"joint_class_count":len(z["joint"]),"joint_class_size_histogram":base.h(z["joint"]),"unresolved_pair_count":M,"selected_probe_indices":list(selected),"selected_separates":separates,"certified_probe_upper_bound":upper},"source_result_digest":src.get("result_digest"),"MINIMUM_FIXED_PROBE_BASIS_AUTHORITY":False,"JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED":bool(ok),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"ADAPTIVE_TREE_OPTIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False}
 ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(TOKEN+canon({"decision":out["decision"],"authority":"UPPER_ONLY" if ok else "NONE","joint_classes":len(z["joint"]),"pairs":M,"upper":upper,"selected":list(selected)}));return 0
if __name__=="__main__":raise SystemExit(main())
