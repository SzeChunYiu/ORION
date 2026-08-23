#!/usr/bin/env python3
"""Run QG-27 production, generic ORION and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg27-generic";NW=ROOT/".orion-qg-qg27-native";POS="QG27_TARE_BULK_DEFECT_LAW_AND_EXACT_ASYMPTOTIC_COST_DENSITY_ALL_N_MACHINE_CHECKED"
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
 for n in ("orion-qg-qg27-bulk-defect.json","orion-qg-qg27-generic-verification.json","orion-qg-qg27-native-verification.json","orion-qg-qg27-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);ar,ao,at=run(gw,"research/extensions/orion-qg/qg27_bulk_defect.py","ORIONQG_QG27=",600);gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg27_generic_verify.py","ORIONQG_QG27_GENERIC=",600)
 a=json.loads((ART/"orion-qg-qg27-bulk-defect.json").read_text());g=json.loads((ART/"orion-qg-qg27-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer token/result digest mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg27_native_verify.py","ORIONQG_QG27_NATIVE=",60);n=json.loads((ART/"orion-qg-qg27-native-verification.json").read_text())
 both=(a.get("terminal")==POS and a.get("BULK_DEFECT_UNIFORM_BOUND_ALL_N") is True and a.get("ASYMPTOTIC_COST_DENSITY_EXACT") is True and a.get("PURE_SCALING_RAY_EVENTUALLY_AFFINE") is True and a.get("ASYMPTOTIC_COUNT_SPACE_PHASE_GEOMETRY") is True and g.get("decision")=="ACCEPT_BULK_DEFECT_THERMODYNAMIC_LIMIT" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_BULK_DEFECT_THERMODYNAMIC_LIMIT" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG27_GENERIC_NATIVE_DISAGREEMENT";out={"schema":"ORIONQG.QG27.DualHarness.v1","issue":"SzeChunYiu/ORION#886","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"defect_band":[a.get("local_bounds",{}).get("lower_defect_constant"),a.get("local_bounds",{}).get("upper_defect_constant")],"bulk_forms":a.get("baseline",{}).get("distinct_vectors"),"correction_range":a.get("local_bounds",{}).get("two_branch_correction_range"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"BULK_DEFECT_UNIFORM_BOUND_ALL_N":bool(both),"ASYMPTOTIC_COST_DENSITY_EXACT":bool(both),"PURE_SCALING_RAY_EVENTUALLY_AFFINE":bool(both),"ASYMPTOTIC_COUNT_SPACE_PHASE_GEOMETRY":bool(both),"DEFECT_CONSTANTS_SHARP":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"PHYSICAL_PHASE_TRANSITION":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
 (ART/"orion-qg-qg27-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"band":out["defect_band"],"bulk_forms":out["bulk_forms"],"correction":out["correction_range"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
