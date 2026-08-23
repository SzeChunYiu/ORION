#!/usr/bin/env python3
"""Run QG-24 production, generic ORION and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"artifacts"
GW=ROOT/".orion-qg-qg24-generic"
NW=ROOT/".orion-qg-qg24-native"
POS="QG24_TARE_UNRESTRICTED_EXACT_OPTIMUM_RECOGNIZED_BY_FINITE_TROPICAL_AUTOMATON_ALL_N"


def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])

def run(ws,path,prefix,timeout):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout})
 r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return q,r,parse(str(r.output.get("stdout","")),prefix)

def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for n in ("orion-qg-qg24-tropical-wfa.json","orion-qg-qg24-generic-verification.json","orion-qg-qg24-native-verification.json","orion-qg-qg24-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 ar,ao,at=run(gw,"research/extensions/orion-qg/qg24_tropical_wfa.py","ORIONQG_QG24=",900)
 gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg24_generic_verify.py","ORIONQG_QG24_GENERIC=",900)
 a=json.loads((ART/"orion-qg-qg24-tropical-wfa.json").read_text());g=json.loads((ART/"orion-qg-qg24-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer token/result digest mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
 nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg24_native_verify.py","ORIONQG_QG24_NATIVE=",60)
 n=json.loads((ART/"orion-qg-qg24-native-verification.json").read_text())
 both=(a.get("terminal")==POS and a.get("FINITE_STATE_EXACT_COMPILER") is True and a.get("UNRESTRICTED_DP_EQUALITY_ALL_N") is True and g.get("decision")=="ACCEPT_FINITE_TROPICAL_EXACT_COMPILER" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_FINITE_TROPICAL_EXACT_COMPILER" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG24_GENERIC_NATIVE_DISAGREEMENT"
 out={
  "schema":"ORIONQG.QG24.DualHarness.v1",
  "issue":"SzeChunYiu/ORION#880",
  "terminal":term,
  "both_accept":bool(both),
  "source_result_digest":a.get("result_digest"),
  "state_count_per_sector":a.get("state_contract",{}).get("raw_states_per_sector"),
  "global_control_sectors":a.get("state_contract",{}).get("global_control_sectors"),
  "input_alphabet_size":a.get("state_contract",{}).get("input_alphabet_size"),
  "n1_target_words":a.get("n1_calibration",{}).get("valid_target_words"),
  "n1_minimum_vector_sha256":a.get("n1_calibration",{}).get("production_minimum_vector_sha256"),
  "n1_histogram":a.get("n1_calibration",{}).get("minimum_cost_histogram"),
  "generic":{"summary":gt,"verification":g},
  "native":{"summary":nt,"verification":n},
  "FINITE_STATE_EXACT_COMPILER":bool(both),
  "UNRESTRICTED_DP_EQUALITY_ALL_N":bool(both),
  "AUTOMATON_MINIMALITY":False,
  "CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,
  "CHAIN_ALL_N":False,
  "ASYMPTOTIC_PHASE_BOUNDARY":False,
  "GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY":False,
  "novelty_authority":False,
  "r6_authority":False,
  "physical_quantum_advantage_claim":False,
 }
 (ART/"orion-qg-qg24-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"terminal":term,"both_accept":both,"states":out["state_count_per_sector"],"sectors":out["global_control_sectors"],"alphabet":out["input_alphabet_size"],"n1":out["n1_target_words"],"n1_digest":out["n1_minimum_vector_sha256"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True))
 return 0

if __name__=="__main__":raise SystemExit(main())
