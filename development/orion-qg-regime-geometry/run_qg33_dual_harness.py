#!/usr/bin/env python3
"""Run QG-33 production/generic/native SixLCU label-value verification in isolated ORION harnesses."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg33-generic";NW=ROOT/".orion-qg-qg33-native"
SEP="QG33_SIXLCU_EXACT_LABEL_QUOTIENT_IS_NOT_EXACT_VALUE_QUOTIENT__N2_COMPLETE";SUFF="QG33_SIXLCU_ONE_LITERAL_LABEL_QUOTIENT_ALSO_VALUE_SUFFICIENT__N2_COMPLETE"
def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows),s[-1200:]))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout=120):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ("orion-qg-qg33-sixlcu-label-value.json","orion-qg-qg33-generic-verification.json","orion-qg-qg33-native-verification.json","orion-qg-qg33-dual-harness.json"):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);at=run(gw,"research/extensions/orion-qg/qg33_sixlcu_label_value.py","ORIONQG_QG33=",120);gt=run(gw,"development/orion-qg-regime-geometry/qg33_generic_verify.py","ORIONQG_QG33_GENERIC=",120);a=json.loads((ART/"orion-qg-qg33-sixlcu-label-value.json").read_text());g=json.loads((ART/"orion-qg-qg33-generic-verification.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nt=run(nw,"development/orion-qg-regime-geometry/qg33_native_verify.py","ORIONQG_QG33_NATIVE=",60);n=json.loads((ART/"orion-qg-qg33-native-verification.json").read_text());term=a.get("terminal");expected="ACCEPT_LABEL_VALUE_SUFFICIENCY" if term==SUFF else ("ACCEPT_LABEL_VALUE_SEPARATION" if term==SEP else "");both=term in {SEP,SUFF} and g.get("decision")==expected and g.get("all_checks") is True and n.get("decision")==expected and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest")
 out={"schema":"ORIONQG.QG33.DualHarness.v1","issue":"SzeChunYiu/ORION#920","terminal":term if both else "QG33_GENERIC_NATIVE_DISAGREEMENT","both_accept":bool(both),"source_result_digest":a.get("result_digest"),"COMPLETE_N2_DOMAIN":bool(both),"LABEL_QUOTIENT_VALUE_SUFFICIENT":a.get("LABEL_QUOTIENT_VALUE_SUFFICIENT") if both else None,"FULL_FEATURE_VECTOR_VALUE_SUFFICIENT":a.get("FULL_FEATURE_VECTOR_VALUE_SUFFICIENT") if both else None,"delta_histogram":a.get("delta_histogram"),"full_feature_vector":a.get("full_feature_vector"),"generic_summary":gt,"native_summary":nt,"NO_POST_OUTCOME_FEATURE_INVENTION":bool(both),"ALL_N_VALUE_THEOREM":False,"GLOBAL_PREDICATE_MINIMALITY":False,"NEW_FEATURE_VOCABULARY_AUTHORITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg33-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":out["terminal"],"both_accept":both,"label_value_sufficient":out["LABEL_QUOTIENT_VALUE_SUFFICIENT"],"feature_value_sufficient":out["FULL_FEATURE_VECTOR_VALUE_SUFFICIENT"],"delta_values":len(a.get("delta_histogram",{})),"mixed_feature_cells":a.get("full_feature_vector",{}).get("mixed_delta_cell_count"),"value_floor":a.get("full_feature_vector",{}).get("irreducible_exact_value_error_floor"),"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
