#!/usr/bin/env python3
"""Execute QG-7e through independent generic and native ORION lanes."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg7e-generic";NW=ROOT/".orion-qg-qg7e-native";POS="QG7E_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN"
def tok(s,p):
 r=[x for x in s.splitlines() if x.startswith(p)]
 if len(r)!=1:raise ValueError((p,len(r)))
 return json.loads(r[0][len(p):])
def run(ws,path,prefix,timeout):
 req=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":res.error,"output":res.output})
 return req,res,tok(str(res.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for n in ("orion-qg-qg7e-pp-single-pinner.json","orion-qg-qg7e-generic-verification.json","orion-qg-qg7e-native-verification.json","orion-qg-qg7e-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);ar,ao,at=run(gw,"research/extensions/orion-qg/qg7e_pp_single_pinner.py","ORIONQG_QG7E=",1200);gr,go,gt=run(gw,"development/orion-qg-regime-geometry/qg7e_generic_verify.py","ORIONQG_QG7E_GENERIC=",1200);a=json.loads((ART/"orion-qg-qg7e-pp-single-pinner.json").read_text());g=json.loads((ART/"orion-qg-qg7e-generic-verification.json").read_text())
 if at.get("result_digest")!=a.get("result_digest"):raise AssertionError("analyzer digest token mismatch")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,nt=run(nw,"development/orion-qg-regime-geometry/qg7e_native_verify.py","ORIONQG_QG7E_NATIVE=",60);n=json.loads((ART/"orion-qg-qg7e-native-verification.json").read_text());both=a.get("terminal")==POS and a.get("all_gates") is True and g.get("decision")=="ACCEPT_PP_SINGLE_PINNER_ALL_N" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_PP_SINGLE_PINNER_ALL_N" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest");term=a.get("terminal") if both else "QG7E_GENERIC_NATIVE_DISAGREEMENT";d={"schema":"ORIONQG.QG7E.DualHarness.v1","issue":"SzeChunYiu/ORION#872","terminal":term,"both_accept":both,"source_result_digest":a.get("result_digest"),"visible_failures":a.get("visible",{}).get("failures"),"product_domain":a.get("product_domain"),"relocation_residual":a.get("relocation",{}).get("residual_count"),"dplus_residual":a.get("dplus",{}).get("residual_count"),"bprime_final":a.get("bprime",{}).get("final_residual"),"generic_lane":{"summary":gt,"request":gr.as_dict(),"result":go.as_dict(),"verification":g},"native_lane":{"summary":nt,"request":nr.as_dict(),"result":no.as_dict(),"verification":n},"analyzer_request":ar.as_dict(),"analyzer_result":ao.as_dict(),"PP_SINGLE_PINNER_ALL_N":both,"CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg7e-dual-harness.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"visible":d["visible_failures"],"product":d["product_domain"],"screen":d["relocation_residual"],"dplus":d["dplus_residual"],"bprime_final":d["bprime_final"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
