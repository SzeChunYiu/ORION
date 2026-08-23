#!/usr/bin/env python3
"""Independent generic ORION verifier for the pre-frozen MAX-R4E-B0 QG-32 forecast."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/orion-q-max-r4eb0-heldout-qg32.json";SKILL=ROOT/"research/extensions/orion-q/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_RESULTS.json";TARGET=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json";PROTO=ROOT/"development/orion-q-max-r0/MAX_R4EB0_HELDOUT_QG32_FORECAST_PROTOCOL.md";OUT=ROOT/"artifacts/orion-q-max-r4eb0-generic-verification.json";TOKEN="ORIONQ_MAX_R4EB0_GENERIC=";POS="MAX_R4EB0_QG_DERIVED_AUTHORITY_SKILL_TRANSFERS_PROSPECTIVELY_TO_HELD_OUT_TARE_QUERY"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def adjudicate(t):
 stronger=("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","ADAPTIVE_TREE_OPTIMALITY","novelty_authority","physical_quantum_advantage_claim")
 boundary=all(t.get(k) is False for k in stronger);parent=t.get("parent_checks_all_green") is True or all(t.get("parent_checks",{}).values());dual=t.get("both_accept") is True;sep=t.get("JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED") is True;exact=t.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is True;loc=t.get("UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID") is True;m=t.get("minimum_probe_cardinality")
 if parent and dual and boundary and loc and sep and exact and isinstance(m,int) and m>0:return "BORNE_OUT_EXACT_MINIMUM"
 if parent and dual and boundary and loc and sep and not exact:return "BORNE_OUT_UPPER_BOUND_ONLY"
 if dual and boundary and isinstance(m,int) and m==0:return "REFUTED_JOINT_ALREADY_SUFFICIENT"
 if dual and loc is False:return "REFUTED_PROBE_LOCALIZATION_INVALID"
 return "CANNOT_CHECK"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());skill=json.loads(SKILL.read_text());t=json.loads(TARGET.read_text());adj=adjudicate(t);positive=adj in {"BORNE_OUT_EXACT_MINIMUM","BORNE_OUT_UPPER_BOUND_ONLY"}
 checks={"source_digest":valid(src),"protocol_bound":src.get("protocol_sha256")==hashlib.sha256(PROTO.read_bytes()).hexdigest(),"skill_green":skill.get("both_accept") is True and skill.get("AUTHORITY_INDEXED_ROUTER_REAL_RECEIPT_CALIBRATION") is True,"adjudication_match":src.get("adjudication")==adj,"positive_terminal_match":(src.get("terminal")==POS)==positive,"number_free":src.get("forecast_number_present") is False,"hidden_outcome_free":src.get("hidden_outcome_dependency_count")==0,"false_authority_zero":src.get("false_authority_count")==0,"scope":src.get("MAX_R4E_QG_SKILLS_COMPILER_GENERAL") is False and src.get("MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE") is False and src.get("MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER") is False and src.get("AUTONOMOUS_SKILL_SELECTION_AUTHORITY") is False and src.get("GENERAL_QUANTUM_SCIENCE_IMPROVEMENT") is False and src.get("NOVELTY_AUTHORITY") is False}
 ok=all(checks.values());out={"schema":"ORIONQ.MAXR4EB0.GenericVerification.v1","decision":"ACCEPT_HELDOUT_TARE_ACTION_TRANSFER" if ok and positive else ("ACCEPT_HELDOUT_REFUTATION_OR_CANNOT_CHECK" if ok else "REJECT"),"all_checks":bool(ok),"checks":checks,"independent_adjudication":adj,"positive_transfer":bool(ok and positive),"source_result_digest":src.get("result_digest"),"MAX_R4E_QG_SKILLS_COMPILER_GENERAL":False,"MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE":False,"MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER":False,"AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"adjudication":adj,"positive":out["positive_transfer"],"all_checks":ok}));return 0
if __name__=="__main__":raise SystemExit(main())
