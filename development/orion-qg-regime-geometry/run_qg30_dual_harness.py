#!/usr/bin/env python3
"""Run QG-30 production, generic ORION and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg30-generic";NW=ROOT/".orion-qg-qg30-native";POS="QG30_TARE_BULK_GEOMETRY_COMPRESSES_EXACTLY_TO_45_SIGNATURE_COUNTS__DEFECT_INFORMATION_REMAINS"
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
 for n in ("orion-qg-qg30-bulk-coarse-grain.json","orion-qg-qg30-generic-verification.json","orion-qg-qg30-native-verification.json","orion-qg-qg30-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);ar,ao,at=run(gw,"research/extensions/orion-qg/qg30_bulk_coarse_grain.py","ORIONQG_QG30=",300);gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg30_generic_verify.py","ORIONQG_QG30_GENERIC=",300)
 a=json.loads((ART/"orion-qg-qg30-bulk-coarse-grain.json").read_text());g=json.loads((ART/"orion-qg-qg30-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer token/result digest mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg30_native_verify.py","ORIONQG_QG30_NATIVE=",60);n=json.loads((ART/"orion-qg-qg30-native-verification.json").read_text())
 both=(a.get("terminal")==POS and a.get("BULK_SIGNATURE_COUNT")==45 and a.get("BULK_DEFECT_SCALE_SEPARATION") is True and g.get("decision")=="ACCEPT_BULK45_DEFECT_SEPARATION" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_BULK45_DEFECT_SEPARATION" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG30_GENERIC_NATIVE_DISAGREEMENT";c=a.get("bulk_signature_census",{});out={"schema":"ORIONQG.QG30.DualHarness.v1","issue":"SzeChunYiu/ORION#893","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"orbits":a.get("local_clifford_orbits"),"bulk_signatures":c.get("signature_count"),"profile_rows":a.get("complete_one_active_profile_rows"),"distinct_profiles":c.get("total_distinct_one_active_profiles"),"multi_profile_signatures":c.get("signatures_with_multiple_profiles"),"information_loss_witness":c.get("information_loss_witness"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"BULK_SIGNATURE_COUNT_45":45 if both else None,"BULK_45_HISTOGRAM_SUFFICIENT_FOR_ASYMPTOTIC_DENSITY":bool(both),"ASYMPTOTIC_PHASE_GEOMETRY_DESCENDS_TO_45_COUNTS":bool(both),"BULK_DEFECT_SCALE_SEPARATION":bool(both),"BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT":False,"FULL_FINITE_N_OPTIMUM_FROM_45_COUNTS":False,"PHYSICAL_RENORMALIZATION_GROUP":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg30-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"orbits":out["orbits"],"signatures":out["bulk_signatures"],"profile_rows":out["profile_rows"],"distinct_profiles":out["distinct_profiles"],"multi_profile_signatures":out["multi_profile_signatures"],"witness_found":out["information_loss_witness"] is not None,"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
