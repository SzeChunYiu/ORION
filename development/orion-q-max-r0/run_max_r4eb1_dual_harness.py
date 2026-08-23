#!/usr/bin/env python3
"""Run MAX-R4E-B1 SixLCU different-family adjudication in isolated ORION harnesses."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-q-max-r4eb1-generic";NW=ROOT/".orion-q-max-r4eb1-native";POS="MAX_R4EB1_QG_DERIVED_AUTHORITY_SKILL_TRANSFERS_PROSPECTIVELY_TO_DIFFERENT_COMPILER_FAMILY"
def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows),s[-1200:]))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":60});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)
def main():
 target=ROOT/"research/extensions/orion-qg/QG33_SIXLCU_LABEL_VALUE_RESULTS.json"
 if not target.exists():raise RuntimeError("QG-33 committed target receipt missing; different-family adjudication remains frozen and unexecuted")
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ("orion-q-max-r4eb1-sixlcu-label-value.json","orion-q-max-r4eb1-generic-verification.json","orion-q-max-r4eb1-native-verification.json","orion-q-max-r4eb1-dual-harness.json"):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);at=run(gw,"research/extensions/orion-q/max_r4eb1_sixlcu_label_value_adjudicator.py","ORIONQ_MAX_R4EB1=");gt=run(gw,"development/orion-q-max-r0/max_r4eb1_generic_verify.py","ORIONQ_MAX_R4EB1_GENERIC=");a=json.loads((ART/"orion-q-max-r4eb1-sixlcu-label-value.json").read_text());g=json.loads((ART/"orion-q-max-r4eb1-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nt=run(nw,"development/orion-q-max-r0/max_r4eb1_native_verify.py","ORIONQ_MAX_R4EB1_NATIVE=");n=json.loads((ART/"orion-q-max-r4eb1-native-verification.json").read_text());positive=a.get("terminal")==POS;both=g.get("all_checks") is True and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest") and g.get("positive_transfer") is positive and n.get("MAX_R4E_QG_SKILLS_COMPILER_GENERAL") is positive
 out={"schema":"ORIONQ.MAXR4EB1.DualHarness.v1","issue":"SzeChunYiu/ORION#921","terminal":POS if both and positive else (a.get("terminal") if both else "MAX_R4EB1_GENERIC_NATIVE_DISAGREEMENT"),"both_accept":bool(both),"positive_transfer":bool(both and positive),"adjudication":a.get("adjudication"),"secondary_full_feature_adjudication":a.get("secondary_full_feature_adjudication"),"source_result_digest":a.get("result_digest"),"generic_summary":gt,"native_summary":nt,"MAX_R4E_QG_SKILLS_COMPILER_GENERAL":bool(both and positive),"MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE":False,"MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER":False,"AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False};(ART/"orion-q-max-r4eb1-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":out["terminal"],"both_accept":both,"positive_transfer":out["positive_transfer"],"adjudication":out["adjudication"],"secondary":out["secondary_full_feature_adjudication"],"compiler_general":out["MAX_R4E_QG_SKILLS_COMPILER_GENERAL"]},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
