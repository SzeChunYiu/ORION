#!/usr/bin/env python3
"""Run QG-29 production, generic ORION and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg29-generic";NW=ROOT/".orion-qg-qg29-native";POS="QG29_TARE_DEFECTS_CLIP_AT_6_AND_ALL_SCALING_RAYS_AFFINE_BY_K43_MACHINE_CHECKED"
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
 for n in ("orion-qg-qg29-defect-saturation.json","orion-qg-qg29-generic-verification.json","orion-qg-qg29-native-verification.json","orion-qg-qg29-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);ar,ao,at=run(gw,"research/extensions/orion-qg/qg29_defect_saturation.py","ORIONQG_QG29=",180);gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg29_generic_verify.py","ORIONQG_QG29_GENERIC=",180)
 a=json.loads((ART/"orion-qg-qg29-defect-saturation.json").read_text());g=json.loads((ART/"orion-qg-qg29-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer token/result digest mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg29_native_verify.py","ORIONQG_QG29_NATIVE=",60);n=json.loads((ART/"orion-qg-qg29-native-verification.json").read_text())
 both=(a.get("terminal")==POS and a.get("DEFECT_POTENTIAL_CLIP6_SUFFICIENT") is True and a.get("PURE_SCALING_RAY_AFFINE_BY_K43") is True and g.get("decision")=="ACCEPT_DEFECT_CLIP6_K43_AFFINITY" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_DEFECT_CLIP6_K43_AFFINITY" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG29_GENERIC_NATIVE_DISAGREEMENT";out={"schema":"ORIONQG.QG29.DualHarness.v1","issue":"SzeChunYiu/ORION#890","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"clip_threshold":a.get("defect_potential",{}).get("individual_guard_threshold_max"),"integer_defect_levels":a.get("defect_potential",{}).get("kappa_level_count"),"max_strict_drops":a.get("defect_potential",{}).get("strict_defect_level_drops_max"),"guard_stable_by_k":a.get("scaling_rays",{}).get("kappa_r_constant_for_all_k_ge"),"affine_by_k":a.get("scaling_rays",{}).get("universal_affine_onset_k"),"abstract_cases":a.get("abstract_crossover_control",{}).get("pairwise_obstruction_cases"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"DEFECT_POTENTIAL_CLIP6_SUFFICIENT":bool(both),"DEFECT_LEVEL_CHANGES_AT_MOST_42_PER_BULK_CLASS":bool(both),"PURE_SCALING_RAY_DEFECTS_STABLE_BY_K6":bool(both),"PURE_SCALING_RAY_AFFINE_BY_K43":bool(both),"K43_SHARP_FOR_REAL_TARE":False,"EXPLICIT_Q_H_FORECASTER":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg29-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"clip":out["clip_threshold"],"levels":out["integer_defect_levels"],"drops":out["max_strict_drops"],"stable_k":out["guard_stable_by_k"],"affine_k":out["affine_by_k"],"cases":out["abstract_cases"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
