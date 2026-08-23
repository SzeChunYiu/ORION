#!/usr/bin/env python3
"""Run QG-26 production, generic ORION and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg26-generic";NW=ROOT/".orion-qg-qg26-native";POS="QG26_TARE_EXACT_COST_IS_FINITE_GUARDED_TROPICAL_FUNCTION_OF_4096_COLUMN_COUNTS_ALL_N"
def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return q,r,parse(str(r.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for n in ("orion-qg-qg26-parikh-histogram.json","orion-qg-qg26-generic-verification.json","orion-qg-qg26-native-verification.json","orion-qg-qg26-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);ar,ao,at=run(gw,"research/extensions/orion-qg/qg26_parikh_histogram.py","ORIONQG_QG26=",900);gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg26_generic_verify.py","ORIONQG_QG26_GENERIC=",900)
 a=json.loads((ART/"orion-qg-qg26-parikh-histogram.json").read_text());g=json.loads((ART/"orion-qg-qg26-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer token/result digest mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg26_native_verify.py","ORIONQG_QG26_NATIVE=",60);n=json.loads((ART/"orion-qg-qg26-native-verification.json").read_text())
 both=(a.get("terminal")==POS and a.get("HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True and a.get("FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION") is True and g.get("decision")=="ACCEPT_PARIKH_GUARDED_TROPICAL_GEOMETRY" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_PARIKH_GUARDED_TROPICAL_GEOMETRY" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG26_GENERIC_NATIVE_DISAGREEMENT"
 out={"schema":"ORIONQG.QG26.DualHarness.v1","issue":"SzeChunYiu/ORION#884","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"histogram_dimension":a.get("column_alphabet",{}).get("histogram_dimension"),"distinct_baselines":a.get("spectator_baselines",{}).get("distinct_vectors"),"template_upper_digits":a.get("template_finiteness",{}).get("upper_bound_decimal_digits"),"one_active_rows":a.get("one_active_decomposition_control",{}).get("rows"),"structural_rows":a.get("structural_cost_control",{}).get("rows"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":bool(both),"FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION":bool(both),"COUNT_SPACE_REGIME_GEOMETRY_EXISTS":bool(both),"EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"CHAIN_ALL_N":False,"GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
 (ART/"orion-qg-qg26-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"histogram_dimension":out["histogram_dimension"],"distinct_baselines":out["distinct_baselines"],"template_upper_digits":out["template_upper_digits"],"one_active_rows":out["one_active_rows"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
