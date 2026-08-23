#!/usr/bin/env python3
"""Run QG-32b production/generic/native four-probe decision through isolated ORION harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg32b-generic";NW=ROOT/".orion-qg-qg32b-native"
YES="QG32B_FOUR_PROBE_SEPARATOR_EXISTS__WITNESS_MACHINE_CHECKED";NO="QG32B_NO_FOUR_PROBE_SEPARATOR__FIVE_IS_EXACT_MINIMUM_MACHINE_CHECKED"
def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows),s[-1500:]))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ("orion-qg-qg32b-four-probe.json","orion-qg-qg32b-generic-verification.json","orion-qg-qg32b-native-verification.json","orion-qg-qg32b-dual-harness.json"):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 at=run(gw,"research/extensions/orion-qg/qg32b_four_probe_feasibility.py","ORIONQG_QG32B=",120)
 gt=run(gw,"development/orion-qg-regime-geometry/qg32b_generic_verify.py","ORIONQG_QG32B_GENERIC=",120)
 a=json.loads((ART/"orion-qg-qg32b-four-probe.json").read_text());g=json.loads((ART/"orion-qg-qg32b-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
 nt=run(nw,"development/orion-qg-regime-geometry/qg32b_native_verify.py","ORIONQG_QG32B_NATIVE=",60)
 n=json.loads((ART/"orion-qg-qg32b-native-verification.json").read_text());term=a.get("terminal");expected="ACCEPT_FOUR_PROBE_EXISTS" if term==YES else ("ACCEPT_NO_FOUR_PROBE_SEPARATOR" if term==NO else "")
 both=term in {YES,NO} and g.get("decision")==expected and g.get("all_checks") is True and n.get("decision")==expected and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest")
 out={"schema":"ORIONQG.QG32B.DualHarness.v1","issue":"SzeChunYiu/ORION#918","terminal":term if both else "QG32B_GENERIC_NATIVE_DISAGREEMENT","both_accept":bool(both),"source_result_digest":a.get("result_digest"),"EXISTS_SEPARATOR_AT_MOST_4":a.get("EXISTS_SEPARATOR_AT_MOST_4") if both else None,"witness_probe_indices":a.get("witness_probe_indices") if both else [],"MINIMUM_FIXED_PROBE_CARDINALITY":5 if both and term==NO else None,"MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY":bool(both and term==NO),"FOUR_OR_FEWER_SEPARATOR_WITNESS_AUTHORITY":bool(both and term==YES),"production_search":a.get("search"),"reconstruction":a.get("reconstruction"),"generic_summary":gt,"native_summary":nt,"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"ADAPTIVE_TREE_OPTIMALITY":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg32b-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":out["terminal"],"both_accept":both,"exists_le4":out["EXISTS_SEPARATOR_AT_MOST_4"],"witness":out["witness_probe_indices"],"minimum":out["MINIMUM_FIXED_PROBE_CARDINALITY"],"nodes":a.get("search",{}).get("stats",{}).get("nodes"),"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
