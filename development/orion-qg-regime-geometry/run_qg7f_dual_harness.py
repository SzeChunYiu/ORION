#!/usr/bin/env python3
"""Run QG-7f representation audit through generic ORION and native ORION-Q."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg7f-generic";NW=ROOT/".orion-qg-qg7f-native";POS="QG7F_TWO_COORD_REDUCTION_REFUTED__TAG3_MULTI_COMM_S2_CONFIGURATION"
def parse(s,p):
 r=[x for x in s.splitlines() if x.startswith(p)]
 if len(r)!=1:raise ValueError((p,len(r)))
 return json.loads(r[0][len(p):])
def run(ws,path,prefix,timeout=120):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for n in ("orion-qg-qg7f-chain-representation-audit.json","orion-qg-qg7f-generic-verification.json","orion-qg-qg7f-native-verification.json","orion-qg-qg7f-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);at=run(gw,"research/extensions/orion-qg/qg7f_chain_representation_audit.py","ORIONQG_QG7F=");gt=run(gw,"development/orion-qg-regime-geometry/qg7f_generic_verify.py","ORIONQG_QG7F_GENERIC=");a=json.loads((ART/"orion-qg-qg7f-chain-representation-audit.json").read_text());g=json.loads((ART/"orion-qg-qg7f-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest");nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nt=run(nw,"development/orion-qg-regime-geometry/qg7f_native_verify.py","ORIONQG_QG7F_NATIVE=");n=json.loads((ART/"orion-qg-qg7f-native-verification.json").read_text());both=a.get("terminal")==POS and a.get("representation_premise_refuted") is True and g.get("decision")=="ACCEPT_REPRESENTATION_PREMISE_REFUTATION" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_REPRESENTATION_PREMISE_REFUTATION" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest");term=POS if both else "QG7F_GENERIC_NATIVE_DISAGREEMENT";d={"schema":"ORIONQG.QG7F.DualHarness.v1","issue":"SzeChunYiu/ORION#874","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"tag_weight":a.get("candidate",{}).get("tag_weight"),"comm_s2_support_pairs":a.get("observed_comm_s2_support_pairs"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"REPRESENTATION_PREMISE_REFUTATION":bool(both),"CHAIN_REPRESENTATION_COMPLETE":False,"CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"FIFTH_REGIME_FOUND":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg7f-dual-harness.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"tag_weight":d["tag_weight"],"support_pairs":d["comm_s2_support_pairs"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
