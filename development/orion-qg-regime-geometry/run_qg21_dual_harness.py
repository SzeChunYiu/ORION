#!/usr/bin/env python3
"""Run QG-21 through generic ORION and native ORION-Q."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg21-generic";NW=ROOT/".orion-qg-qg21-native";POS="QG21_CERTIFIED_REGIME_ROBUSTNESS_RADIUS_MACHINE_CHECKED"
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
 for n in ("orion-qg-qg21-regime-robustness.json","orion-qg-qg21-generic-verification.json","orion-qg-qg21-native-verification.json","orion-qg-qg21-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);at=run(gw,"research/extensions/orion-qg/qg21_regime_robustness.py","ORIONQG_QG21=");gt=run(gw,"development/orion-qg-regime-geometry/qg21_generic_verify.py","ORIONQG_QG21_GENERIC=")
 a=json.loads((ART/"orion-qg-qg21-regime-robustness.json").read_text());g=json.loads((ART/"orion-qg-qg21-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nt=run(nw,"development/orion-qg-regime-geometry/qg21_native_verify.py","ORIONQG_QG21_NATIVE=")
 n=json.loads((ART/"orion-qg-qg21-native-verification.json").read_text());both=a.get("terminal")==POS and a.get("certificate_margin_authority") is True and g.get("decision")=="ACCEPT_CERTIFICATE_ROBUSTNESS" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_CERTIFICATE_ROBUSTNESS" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest")
 term=POS if both else "QG21_GENERIC_NATIVE_DISAGREEMENT";d={"schema":"ORIONQG.QG21.DualHarness.v1","issue":"SzeChunYiu/ORION#864","terminal":term,"both_accept":both,"source_result_digest":a.get("result_digest"),"qg8_O0_radius":a.get("qg8",{}).get("O0",{}).get("linf_fixed_tr_radius"),"qg16_Oin_radius":a.get("qg16",{}).get("O_in",{}).get("linf_fixed_tr_radius"),"generic":{"summary":gt,"verification":g},"native":{"summary":nt,"verification":n},"CERTIFICATE_MARGIN":bool(both),"TRUE_PHASE_BOUNDARY":False,"TRUE_PHASE_BRACKET":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg21-dual-harness.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"qg8_O0_radius":d["qg8_O0_radius"],"qg16_Oin_radius":d["qg16_Oin_radius"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
