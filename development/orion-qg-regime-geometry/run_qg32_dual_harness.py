#!/usr/bin/env python3
"""Run QG-32 production/generic/native minimum-probe verification in isolated ORION harness workspaces."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"artifacts"
GW=ROOT/".orion-qg-qg32-generic"
NW=ROOT/".orion-qg-qg32-native"
PROD="QG32_PRODUCTION_MINIMUM_FIXED_PROBE_CANDIDATE_MILP_OPTIMAL"
STRONG="QG32_MINIMUM_FIXED_PROBE_BASIS_ABOVE_JOINT_BULK_SPECTRUM_MACHINE_CHECKED"

def parse(s:str,prefix:str):
    rows=[x for x in s.splitlines() if x.startswith(prefix)]
    if len(rows)!=1: raise ValueError((prefix,len(rows),s[-1500:]))
    return json.loads(rows[0][len(prefix):])

def run(ws:ResearchWorkspace,path:str,prefix:str,timeout:int):
    req=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout})
    res=service_local_request(ws,req.request_id)
    if not res.success or not isinstance(res.output,dict) or res.output.get("returncode")!=0:
        raise RuntimeError({"path":path,"error":res.error,"output":res.output})
    return parse(str(res.output.get("stdout","")),prefix)

def main()->int:
    for p in (GW,NW):
        if p.exists(): shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    for name in ("orion-qg-qg32-min-probes.json","orion-qg-qg32-generic-verification.json","orion-qg-qg32-native-verification.json","orion-qg-qg32-dual-harness.json"):
        p=ART/name
        if p.exists():p.unlink()

    gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
    at=run(gw,"research/extensions/orion-qg/qg32_min_separating_probes.py","ORIONQG_QG32=",600)
    gt=run(gw,"development/orion-qg-regime-geometry/qg32_generic_verify.py","ORIONQG_QG32_GENERIC=",600)
    a=json.loads((ART/"orion-qg-qg32-min-probes.json").read_text())
    g=json.loads((ART/"orion-qg-qg32-generic-verification.json").read_text())
    assert at.get("result_digest")==a.get("result_digest")

    nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
    nt=run(nw,"development/orion-qg-regime-geometry/qg32_native_verify.py","ORIONQG_QG32_NATIVE=",120)
    n=json.loads((ART/"orion-qg-qg32-native-verification.json").read_text())

    both=(a.get("terminal")==PROD and g.get("decision")=="ACCEPT_MINIMUM_FIXED_PROBE_BASIS" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_MINIMUM_FIXED_PROBE_BASIS" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
    term=STRONG if both else "QG32_GENERIC_NATIVE_DISAGREEMENT"
    out={
        "schema":"ORIONQG.QG32.DualHarness.v1",
        "issue":"SzeChunYiu/ORION#911",
        "terminal":term,
        "both_accept":bool(both),
        "source_result_digest":a.get("result_digest"),
        "joint_partition":a.get("joint_partition"),
        "minimum_probe_cardinality":a.get("minimum_probe_cardinality"),
        "selected_probe_indices":a.get("selected_probe_indices"),
        "packing_lower_bound":a.get("lower_bound_packing"),
        "ablations":a.get("ablations"),
        "generic_summary":gt,
        "native_summary":nt,
        "MINIMUM_FIXED_PROBE_BASIS_AUTHORITY":bool(both),
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,
        "HARDWARE_MEASUREMENT_MINIMUM":False,
        "QG28_GLOBAL_STATE_MINIMALITY":False,
        "ADAPTIVE_TREE_OPTIMALITY":False,
        "novelty_authority":False,
        "physical_quantum_advantage_claim":False,
    }
    (ART/"orion-qg-qg32-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"terminal":term,"both_accept":both,"joint_classes":a.get("joint_partition",{}).get("class_count"),"unresolved_pairs":a.get("joint_partition",{}).get("unresolved_pair_count"),"m_joint":a.get("minimum_probe_cardinality"),"selected":a.get("selected_probe_indices"),"packing_size":a.get("lower_bound_packing",{}).get("size"),"packing_closes":a.get("lower_bound_packing",{}).get("closes_minimum"),"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
