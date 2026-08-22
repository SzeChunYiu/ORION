#!/usr/bin/env python3
"""Run QG-31 production/generic/native confirmation through isolated ORION harnesses."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg31-generic";NW=ROOT/".orion-qg-qg31-native";POS="QG31_QUERY_INDEXED_ABSTRACTION_LADDER_CONFIRMED__INDEXED_LOCAL_RESPONSE_INJECTIVE_ON_715_ORBITS"
def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout=120):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for n in ("orion-qg-qg31-query-abstraction.json","orion-qg-qg31-generic-verification.json","orion-qg-qg31-native-verification.json","orion-qg-qg31-dual-harness.json"):
  p=ART/n
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);at=run(gw,"research/extensions/orion-qg/qg31_query_indexed_abstraction.py","ORIONQG_QG31=",180);gt=run(gw,"development/orion-qg-regime-geometry/qg31_generic_verify.py","ORIONQG_QG31_GENERIC=",180);a=json.loads((ART/"orion-qg-qg31-query-abstraction.json").read_text());g=json.loads((ART/"orion-qg-qg31-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nt=run(nw,"development/orion-qg-regime-geometry/qg31_native_verify.py","ORIONQG_QG31_NATIVE=",60);n=json.loads((ART/"orion-qg-qg31-native-verification.json").read_text());both=a.get("terminal")==POS and g.get("decision")=="ACCEPT_QUERY_INDEXED_ABSTRACTION" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_QUERY_INDEXED_ABSTRACTION" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest";)
 return 0
if __name__=="__main__":raise SystemExit(main())
