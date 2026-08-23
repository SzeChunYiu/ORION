#!/usr/bin/env python3
"""Native ORION-Q gate for QG-32's certified fixed-probe upper bound."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-qg-qg32-min-probes.json";G=ROOT/"artifacts/orion-qg-qg32-generic-verification.json";P=ROOT/"development/orion-qg-regime-geometry/QG32_MIN_SEPARATING_PROBES_PROTOCOL_V1.md";OUT=ROOT/"artifacts/orion-qg-qg32-native-verification.json";TOKEN="ORIONQG_QG32_NATIVE="
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();a=json.loads(ns.analyzer.read_text());g=json.loads(ns.generic.read_text())
 checks={
  "analyzer_digest":valid(a),
  "protocol_bound":a.get("protocol_sha256")==hashlib.sha256(P.read_bytes()).hexdigest(),
  "parent":all(a.get("parent_checks",{}).values()),
  "upper_terminal":a.get("terminal")=="QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY",
  "production_upper":a.get("JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED") is True and a.get("selected_separates_715") is True and isinstance(a.get("certified_probe_upper_bound"),int),
  "minimum_withheld":a.get("minimum_probe_cardinality") is None and a.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is False and a.get("PRODUCTION_MILP_MINIMUM_OPTIMAL") is False,
  "generic_accept":g.get("decision")=="ACCEPT_FIXED_PROBE_UPPER_BOUND" and g.get("authority_level")=="UPPER_ONLY" and g.get("all_checks") is True,
  "digest_bound":g.get("source_result_digest")==a.get("result_digest"),
  "localization":a.get("UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID") is True,
  "boundaries":all(a.get(k) is False and g.get(k) is False for k in ("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","ADAPTIVE_TREE_OPTIMALITY","novelty_authority","physical_quantum_advantage_claim")),
 }
 ok=all(checks.values());out={"schema":"ORIONQG.QG32.NativeUpperBoundVerification.v1","decision":"ACCEPT_FIXED_PROBE_UPPER_BOUND" if ok else "REJECT","responsibility":"JOINT_SUMMARY_PLUS_CERTIFIED_FIXED_PROBE_UPPER_BOUND_ONLY" if ok else "CANNOT_CHECK","all_checks":bool(ok),"checks":checks,"source_result_digest":a.get("result_digest"),"MINIMUM_FIXED_PROBE_BASIS_AUTHORITY":False,"JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED":bool(ok),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"ADAPTIVE_TREE_OPTIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"responsibility":out["responsibility"],"upper":a.get("certified_probe_upper_bound"),"minimum_authority":False}));return 0
if __name__=="__main__":raise SystemExit(main())
