#!/usr/bin/env python3
"""Native ORION-Q authority gate for QG-32b four-probe feasibility."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-qg-qg32b-four-probe.json";G=ROOT/"artifacts/orion-qg-qg32b-generic-verification.json";P=ROOT/"development/orion-qg-regime-geometry/QG32B_FOUR_PROBE_FEASIBILITY_PROTOCOL_V1.md";OUT=ROOT/"artifacts/orion-qg-qg32b-native-verification.json";TOKEN="ORIONQG_QG32B_NATIVE="
YES="QG32B_FOUR_PROBE_SEPARATOR_EXISTS__WITNESS_MACHINE_CHECKED";NO="QG32B_NO_FOUR_PROBE_SEPARATOR__FIVE_IS_EXACT_MINIMUM_MACHINE_CHECKED"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();a=json.loads(ns.analyzer.read_text());g=json.loads(ns.generic.read_text());term=a.get("terminal");exists=a.get("EXISTS_SEPARATOR_AT_MOST_4")
 expected_generic="ACCEPT_FOUR_PROBE_EXISTS" if term==YES else ("ACCEPT_NO_FOUR_PROBE_SEPARATOR" if term==NO else "")
 checks={"analyzer_digest":valid(a),"protocol_bound":a.get("protocol_sha256")==hashlib.sha256(P.read_bytes()).hexdigest(),"parent":all(a.get("parent_checks",{}).values()),"terminal_decided":term in {YES,NO},"generic":g.get("decision")==expected_generic and g.get("all_checks") is True,"digest_bound":g.get("source_result_digest")==a.get("result_digest"),"existence_consistency":(term==YES and exists is True) or (term==NO and exists is False),"yes_witness":term!=YES or (a.get("witness_size",99)<=4 and a.get("witness_separates_715") is True and g.get("independent",{}).get("EXISTS_SEPARATOR_AT_MOST_4") is True),"no_minimum_closure":term!=NO or (a.get("MINIMUM_FIXED_PROBE_CARDINALITY")==5 and a.get("MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY") is True and g.get("independent",{}).get("EXISTS_SEPARATOR_AT_MOST_4") is False),"boundaries":all(a.get(k) is False and g.get(k) is False for k in ("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","ADAPTIVE_TREE_OPTIMALITY","QG28_GLOBAL_STATE_MINIMALITY","novelty_authority","physical_quantum_advantage_claim"))}
 ok=all(checks.values());responsibility=("FOUR_OR_FEWER_FIXED_PROBE_SEPARATOR_WITNESS_ONLY" if term==YES else "EXACT_FIXED_PROBE_MINIMUM_FIVE_FOR_INDEXED_IDENTITY_ONLY") if ok else "CANNOT_CHECK"
 out={"schema":"ORIONQG.QG32B.NativeVerification.v1","decision":expected_generic if ok else "REJECT","responsibility":responsibility,"all_checks":bool(ok),"checks":checks,"source_result_digest":a.get("result_digest"),"EXISTS_SEPARATOR_AT_MOST_4":exists if ok else None,"MINIMUM_FIXED_PROBE_CARDINALITY":5 if ok and term==NO else None,"MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY":bool(ok and term==NO),"FOUR_OR_FEWER_SEPARATOR_WITNESS_AUTHORITY":bool(ok and term==YES),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"ADAPTIVE_TREE_OPTIMALITY":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False}
 ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"responsibility":responsibility,"exists_le4":out["EXISTS_SEPARATOR_AT_MOST_4"],"minimum":out["MINIMUM_FIXED_PROBE_CARDINALITY"]}));return 0
if __name__=="__main__":raise SystemExit(main())
