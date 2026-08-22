#!/usr/bin/env python3
"""Run MAX-R4E-A production/generic/native calibration through isolated ORION harness workspaces."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-q-max-r4ea-generic";NW=ROOT/".orion-q-max-r4ea-native"
POS="MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PARETO_DOMINATES_STATIC_ABSTRACTION_POLICIES_ON_REAL_RECEIPTS"

def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows),s[-1000:]))
 return json.loads(rows[0][len(p):])

def run(ws,path,prefix,timeout=60):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)

def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ("orion-q-max-r4ea-authority-router.json","orion-q-max-r4ea-generic-verification.json","orion-q-max-r4ea-native-verification.json","orion-q-max-r4ea-dual-harness.json"):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 at=run(gw,"research/extensions/orion-q/max_r4ea_authority_indexed_router.py","ORIONQ_MAX_R4EA=",60)
 gt=run(gw,"development/orion-q-max-r0/max_r4ea_generic_verify.py","ORIONQ_MAX_R4EA_GENERIC=",60)
 a=json.loads((ART/"orion-q-max-r4ea-authority-router.json").read_text());g=json.loads((ART/"orion-q-max-r4ea-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
 nt=run(nw,"development/orion-q-max-r0/max_r4ea_native_verify.py","ORIONQ_MAX_R4EA_NATIVE=",60)
 n=json.loads((ART/"orion-q-max-r4ea-native-verification.json").read_text())
 both=(a.get("terminal")==POS and g.get("decision")=="ACCEPT_AUTHORITY_INDEXED_ROUTER_CALIBRATION" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_AUTHORITY_INDEXED_ROUTER_CALIBRATION" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "MAX_R4EA_GENERIC_NATIVE_DISAGREEMENT"
 out={"schema":"ORIONQ.MAXR4EA.DualHarness.v1","issue":"SzeChunYiu/ORION#908","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"baseline_summaries":{b:{k:v for k,v in a.get("baselines",{}).get(b,{}).items() if k!="rows"} for b in ("B0","B1","B2")},"generic_summary":gt,"native_summary":nt,"AUTHORITY_INDEXED_ROUTER_REAL_RECEIPT_CALIBRATION":bool(both),"HELD_OUT_TRANSFER_AUTHORITY":False,"AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False}
 (ART/"orion-q-max-r4ea-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"terminal":term,"both_accept":both,"B0":out["baseline_summaries"]["B0"],"B1":out["baseline_summaries"]["B1"],"B2":out["baseline_summaries"]["B2"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
