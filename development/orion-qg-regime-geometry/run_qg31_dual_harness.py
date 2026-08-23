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
 for name in ("orion-qg-qg31-query-abstraction.json","orion-qg-qg31-generic-verification.json","orion-qg-qg31-native-verification.json","orion-qg-qg31-dual-harness.json"):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 at=run(gw,"research/extensions/orion-qg/qg31_query_indexed_abstraction.py","ORIONQG_QG31=",180)
 gt=run(gw,"development/orion-qg-regime-geometry/qg31_generic_verify.py","ORIONQG_QG31_GENERIC=",180)
 a=json.loads((ART/"orion-qg-qg31-query-abstraction.json").read_text());g=json.loads((ART/"orion-qg-qg31-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
 nt=run(nw,"development/orion-qg-regime-geometry/qg31_native_verify.py","ORIONQG_QG31_NATIVE=",60)
 n=json.loads((ART/"orion-qg-qg31-native-verification.json").read_text())
 both=(a.get("terminal")==POS and g.get("decision")=="ACCEPT_QUERY_INDEXED_ABSTRACTION" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_QUERY_INDEXED_ABSTRACTION" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
 term=POS if both else "QG31_GENERIC_NATIVE_DISAGREEMENT"
 out={"schema":"ORIONQG.QG31.DualHarness.v1","issue":"SzeChunYiu/ORION#904","terminal":term,"both_accept":bool(both),"source_result_digest":a.get("result_digest"),"class_counts":a.get("class_counts"),"partition_relations":a.get("partition_relations"),"witnesses":a.get("witnesses"),"generic_summary":gt,"native_summary":nt,"BULK_QUERY_CLASSES_45":bool(both),"DEFECT_SPECTRUM_QUERY_CLASSES_54":bool(both),"INDEXED_LOCAL_RESPONSE_CLASSES_715":bool(both),"INDEXED_RESPONSE_MINIMALITY_715":bool(both),"BULK_SPECTRUM_PARTITIONS_INCOMPARABLE":bool(both and a.get("BULK_SPECTRUM_PARTITIONS_INCOMPARABLE")),"QUERY_INDEXED_ABSTRACTION_REQUIRED":bool(both),"FULL_FINITE_N_OPTIMUM_REQUIRES_715_CLASSES":False,"QG28_ORBIT_HISTOGRAM_GLOBALLY_MINIMAL":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
 (ART/"orion-qg-qg31-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"terminal":term,"both_accept":both,"counts":out["class_counts"],"incomparable":out["BULK_SPECTRUM_PARTITIONS_INCOMPARABLE"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
