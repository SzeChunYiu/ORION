#!/usr/bin/env python3
"""Execute QG-22 through independent generic and native ORION lanes."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"artifacts"
GW=ROOT/".orion-qg-qg22-generic"
NW=ROOT/".orion-qg-qg22-native"
POS="QG22_HIDDEN_HOME_J5_DELTA_EXACTLY_DETERMINED_BY_MINIMAL_5_PREDICATE_STATE"


def parse(stdout,prefix):
    rows=[x for x in stdout.splitlines() if x.startswith(prefix)]
    if len(rows)!=1: raise ValueError({"prefix":prefix,"count":len(rows)})
    return json.loads(rows[0][len(prefix):])

def run(ws,path,prefix,timeout=120):
    req=ws.get_or_create_request(capability="PYTHON",payload={"code":f"import runpy;runpy.run_path({path!r},run_name='__main__')","cwd":".","timeout":timeout})
    res=service_local_request(ws,req.request_id)
    if not res.success or not isinstance(res.output,dict) or res.output.get("returncode")!=0:
        raise RuntimeError({"path":path,"error":res.error,"output":res.output})
    return req,res,parse(str(res.output.get("stdout","")),prefix)

def main()->int:
    for p in (GW,NW):
        if p.exists(): shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    for name in ("orion-qg-qg22-hidden-home-state.json","orion-qg-qg22-generic-verification.json","orion-qg-qg22-native-verification.json","orion-qg-qg22-dual-harness.json"):
        p=ART/name
        if p.exists(): p.unlink()
    gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
    areq,ares,asum=run(gw,"research/extensions/orion-qg/qg22_hidden_home_state.py","ORIONQG_QG22=",120)
    greq,gres,gsum=run(gw,"development/orion-qg-regime-geometry/qg22_generic_verify.py","ORIONQG_QG22_GENERIC=",120)
    a=json.loads((ART/"orion-qg-qg22-hidden-home-state.json").read_text()); g=json.loads((ART/"orion-qg-qg22-generic-verification.json").read_text())
    if asum.get("result_digest")!=a.get("result_digest"): raise AssertionError("QG22 analyzer digest token mismatch")
    nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
    nreq,nres,nsum=run(nw,"development/orion-qg-regime-geometry/qg22_native_verify.py","ORIONQG_QG22_NATIVE=",60)
    n=json.loads((ART/"orion-qg-qg22-native-verification.json").read_text())
    both=(a.get("terminal")==POS and a.get("all_gates") is True and g.get("decision")=="ACCEPT_STATE_QUOTIENT" and g.get("all_checks") is True and n.get("decision")=="ACCEPT_STATE_QUOTIENT" and n.get("all_checks") is True and g.get("source_result_digest")==a.get("result_digest")==n.get("source_result_digest"))
    terminal=a.get("terminal") if both else "QG22_GENERIC_NATIVE_DISAGREEMENT"
    d={"schema":"ORIONQG.QG22.DualHarness.v1","issue":"SzeChunYiu/ORION#868","terminal":terminal,"both_accept":both,"result_digest":a.get("result_digest"),"minimum_determining_cardinality":a.get("minimum_determining_cardinality"),"minimum_determining_subsets":a.get("minimum_determining_subsets"),"branch_cells":a.get("selected_cell_counts"),"pair_cells":a.get("paired",{}).get("signature_cells"),"delta_range":[a.get("paired",{}).get("delta_min"),a.get("paired",{}).get("delta_max")],"pp_failures_parent":a.get("parent",{}).get("pp_failures"),"generic_lane":{"summary":gsum,"request":greq.as_dict(),"result":gres.as_dict(),"verification":g},"native_lane":{"summary":nsum,"request":nreq.as_dict(),"result":nres.as_dict(),"verification":n},"scientific_scope":"EXACT_J5_HIDDEN_HOME_DELTA_STATE_ONLY","all_n_theorem_authority":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
    (ART/"orion-qg-qg22-dual-harness.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"terminal":terminal,"both_accept":both,"minimum_k":d["minimum_determining_cardinality"],"minimum_subset_count":len(d["minimum_determining_subsets"] or []),"branch_cells":d["branch_cells"],"pair_cells":d["pair_cells"],"delta_range":d["delta_range"],"generic":g.get("decision"),"native":n.get("decision")},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
