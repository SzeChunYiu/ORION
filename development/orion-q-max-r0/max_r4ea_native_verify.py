#!/usr/bin/env python3
"""Native ORION-Q responsibility gate for MAX-R4E-A authority-indexed routing."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-q-max-r4ea-authority-router.json"
G=ROOT/"artifacts/orion-q-max-r4ea-generic-verification.json"
P=ROOT/"development/orion-q-max-r0/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PROTOCOL.md"
OUT=ROOT/"artifacts/orion-q-max-r4ea-native-verification.json"
TOKEN="ORIONQ_MAX_R4EA_NATIVE="
POS="MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PARETO_DOMINATES_STATIC_ABSTRACTION_POLICIES_ON_REAL_RECEIPTS"

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()

def rowmap(b):return {r["case_id"]:r for r in b.get("rows",[])}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();a=json.loads(ns.analyzer.read_text());g=json.loads(ns.generic.read_text());b=a.get("baselines",{});b0=b.get("B0",{});b1=b.get("B1",{});b2=b.get("B2",{});r2=rowmap(b2)
 checks={
  "analyzer_positive":a.get("terminal")==POS and valid(a),
  "generic_positive":g.get("decision")=="ACCEPT_AUTHORITY_INDEXED_ROUTER_CALIBRATION" and g.get("all_checks") is True,
  "digest_bound":g.get("source_result_digest")==a.get("result_digest"),
  "protocol_bound":a.get("protocol_sha256")==hashlib.sha256(P.read_bytes()).hexdigest(),
  "receipt_bindings":all(a.get("binding_checks",{}).values()),
  "b2_all_correct":b2.get("correct_route_count")==10,
  "b2_zero_false":b2.get("false_authority_count")==0,
  "b2_zero_overcompression":b2.get("overcompression_count")==0,
  "b2_zero_avoidable":b2.get("avoidable_rich_state_count")==0,
  "b2_all_compact":b2.get("compact_authorized_captured")==b2.get("compact_authorized_opportunities") and (b2.get("compact_authorized_opportunities") or 0)>0,
  "b0_safe_rich":b0.get("false_authority_count")==0 and b0.get("overcompression_count")==0 and (b0.get("avoidable_rich_state_count") or 0)>0,
  "b1_unsafe":(b1.get("false_authority_count") or 0)>0 or (b1.get("overcompression_count") or 0)>0,
  "hostile_stabprep":r2.get("C6",{}).get("selected")=="EXACT_RICH_STATE" and r2.get("C6",{}).get("correct") is True,
  "hostile_total_resource":r2.get("C9",{}).get("selected")=="IMPLEMENTATION_AWARE_RESOURCE" and r2.get("C9",{}).get("correct") is True,
  "hostile_full_circuit":r2.get("C10",{}).get("selected")=="CANNOT_AUTHORIZE" and r2.get("C10",{}).get("correct") is True,
  "tare_sizes":b2.get("tare_selected_representation_sizes")==[45,54,715,715],
  "input_blindness":"family_name" in a.get("router_input_excludes",[]) and "gold_route" in a.get("router_input_excludes",[]),
  "authority_boundary":a.get("HELD_OUT_TRANSFER_AUTHORITY") is False and a.get("AUTONOMOUS_SKILL_SELECTION_AUTHORITY") is False and a.get("GENERAL_QUANTUM_SCIENCE_IMPROVEMENT") is False and a.get("NOVELTY_AUTHORITY") is False,
 }
 ok=all(checks.values())
 out={"schema":"ORIONQ.MAXR4EA.NativeVerification.v1","decision":"ACCEPT_AUTHORITY_INDEXED_ROUTER_CALIBRATION" if ok else "REJECT","responsibility":"QUERY_SCOPED_REPRESENTATION_AND_RESOURCE_ROUTING_ONLY" if ok else "CANNOT_CHECK","all_checks":bool(ok),"checks":checks,"source_result_digest":a.get("result_digest"),"AUTHORITY_INDEXED_ROUTER_REAL_RECEIPT_CALIBRATION":bool(ok),"HELD_OUT_TRANSFER_AUTHORITY":False,"AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False}
 ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"responsibility":out["responsibility"],"all_checks":ok}));return 0
if __name__=="__main__":raise SystemExit(main())
