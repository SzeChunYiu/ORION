#!/usr/bin/env python3
"""Run QG-32 production/generic/native verification in isolated ORION harness workspaces."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/"artifacts";GW=ROOT/".orion-qg-qg32-generic";NW=ROOT/".orion-qg-qg32-native"
PROD="QG32_PRODUCTION_MINIMUM_FIXED_PROBE_CANDIDATE_MILP_OPTIMAL";UPPER="QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY";STRONG="QG32_MINIMUM_FIXED_PROBE_BASIS_ABOVE_JOINT_BULK_SPECTRUM_MACHINE_CHECKED"
def parse(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows),s[-1500:]))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout):
 q=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout});r=service_local_request(ws,q.request_id)
 if not r.success or not isinstance(r.output,dict) or r.output.get("returncode")!=0:raise RuntimeError({"path":path,"error":r.error,"output":r.output})
 return parse(str(r.output.get("stdout","")),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ("orion-qg-qg32-min-probes.json","orion-qg-qg32-generic-verification.json","orion-qg-qg32-native-verification.json","orion-qg-qg32-dual-harness.json"):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);at=run(gw,"research/extensions/orion-qg/qg32_min_separating_probes.py","ORIONQG_QG32=",120);a=json.loads((ART/"orion-qg-qg32-min-probes.json").read_text());assert at.get("result_digest")==a.get("result_digest")
 if a.get("terminal")==PROD:
  gpath="development/orion-qg-regime-geometry/qg32_generic_verify.py";npath="development/orion-qg-regime-geometry/qg32_native_verify.py";gaccept="ACCEPT_MINIMUM_FIXED_PROBE_BASIS";naccept="ACCEPT_MINIMUM_FIXED_PROBE_BASIS"
 elif a.get("terminal")==UPPER:
  gpath="development/orion-qg-regime-geometry/qg32_upper_bound_generic_verify.py";npath="development/orion-qg-regime-geometry/qg32_upper_bound_native_verify.py";gaccept="ACCEPT_FIXED_PROBE_UPPER_BOUND";naccept="ACCEPT_FIXED_PROBE_UPPER_BOUND"
 else:raise RuntimeError({"unexpected_production_terminal":a.get("terminal")})
 gt=run(gw,gpath,"ORIONQG_QG32_GENERIC=",120);g=json.loads((ART/"orion-qg-qg32-generic-verification.json").read_text())
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nt=run(nw,npath,"ORIONQG_QG32_NATIVE=",120);n=json.loads((ART/"orion-qg-qg32-native-verification.json").read_text())
 both=g.get("decision")==gaccept and g.get("all_checks") is True and n.get("decision")==naccept and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest")
 term=(STRONG if a.get("terminal")==PROD else UPPER) if both else "QG32_GENERIC_NATIVE_DISAGREEMENT"
 out={"schema":"ORIONQG.QG32.DualHarness.v1","issue":"SzeChunYiu/ORION#911","terminal":term,"both_accept":bool(both),"authority_level":"MINIMUM" if term==STRONG else ("UPPER_ONLY" if term==UPPER else "NONE"),"source_result_digest":a.get("result_digest"),"joint_partition":a.get("joint_partition"),"minimum_probe_cardinality":a.get("minimum_probe_cardinality"),"certified_probe_upper_bound":a.get("certified_probe_upper_bound"),"selected_probe_indices":a.get("selected_probe_indices"),"ablations":a.get("ablations"),"generic_summary":gt,"native_summary":nt,"UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID":bool(both and a.get("UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID")),"JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED":bool(both),"MINIMUM_FIXED_PROBE_BASIS_AUTHORITY":bool(both and term==STRONG),"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"ADAPTIVE_TREE_OPTIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};(ART/"orion-qg-qg32-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"terminal":term,"both_accept":both,"authority":out["authority_level"],"joint_classes":a.get("joint_partition",{}).get("class_count"),"unresolved_pairs":a.get("joint_partition",{}).get("unresolved_pair_count"),"minimum":a.get("minimum_probe_cardinality"),"upper":a.get("certified_probe_upper_bound"),"selected":a.get("selected_probe_indices"),"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
