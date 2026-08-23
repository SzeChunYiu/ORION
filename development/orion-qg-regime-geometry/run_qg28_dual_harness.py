#!/usr/bin/env python3
"""Run QG-28 production, generic ORION and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg28-generic";NW=ROOT/".orion-qg-qg28-native";POS="QG28_TARE_EXACT_COST_DESCENDS_TO_715_LOCAL_CLIFFORD_COLUMN_ORBIT_COUNTS_ALL_N"
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
 for n in ("orion-qg-qg28-local-clifford-orbits.json","orion-qg-qg28-generic-verification.json","orion-qg-qg28-native-verification.json","orion-qg-qg28-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);ar,ao,at=run(gw,"research/extensions/orion-qg/qg28_local_clifford_orbits.py","ORIONQG_QG28=",900);gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg28_generic_verify.py","ORIONQG_QG28_GENERIC=",900)
 a=json.loads((ART/"orion-qg-qg28-local-clifford-orbits.json").read_text());g=json.loads((ART/"orion-qg-qg28-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer token/result digest mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg28_native_verify.py","ORIONQG_QG28_NATIVE=",60);n=json.loads((ART/"orion-qg-qg28-native-verification.json").read_text())
 both=(a.get("terminal")==POS and a.get("LOCAL_CLIFFORD_EQUIVARIANCE_PER_QUBIT") is True and a.get("LOCAL_CLIFFORD_ORBIT_COUNT")==715 and a.get("ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True and a.get("GUARDED_TROPICAL_GEOMETRY_DESCENDS_TO_715_COUNTS") is True and g.get("decision")=="ACCEPT_LOCAL_CLIFFORD_ORBIT_COMPRESSION" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_LOCAL_CLIFFORD_ORBIT_COMPRESSION" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG28_GENERIC_NATIVE_DISAGREEMENT";out={"schema":"ORIONQG.QG28.DualHarness.v1","issue":"SzeChunYiu/ORION#888","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"orbit_count":a.get("LOCAL_CLIFFORD_ORBIT_COUNT"),"orbit_size_distribution":a.get("orbit_census",{}).get("orbit_size_distribution"),"active_rows":a.get("active_canonicalization_control",{}).get("rows"),"distinct_baselines":a.get("baseline_quotient",{}).get("checks",{}).get("distinct_quotient_vectors"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"LOCAL_CLIFFORD_EQUIVARIANCE_PER_QUBIT":bool(both),"LOCAL_CLIFFORD_ORBIT_COUNT":715 if both else None,"ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":bool(both),"GUARDED_TROPICAL_GEOMETRY_DESCENDS_TO_715_COUNTS":bool(both),"INDEPENDENT_POSITION_RELABEL_PER_COLUMN":False,"COMBINED_LOCAL_POSITION_QUOTIENT_54":False,"EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg28-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"orbits":out["orbit_count"],"sizes":out["orbit_size_distribution"],"active_rows":out["active_rows"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
