#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg7d-n2-generic';NW=ROOT/'.orion-qg-qg7d-n2-native'

def token(stdout,prefix):
    r=[x for x in stdout.splitlines() if x.startswith(prefix)]
    if len(r)!=1:raise ValueError({'prefix':prefix,'rows':len(r)})
    return json.loads(r[0][len(prefix):])
def run(ws,path,prefix,timeout=120):
    req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout})
    res=service_local_request(ws,req.request_id)
    if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0:raise RuntimeError({'path':path,'error':res.error,'output':res.output})
    return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
    for p in (GW,NW):
        if p.exists():shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    for n in ('orion-qg-qg7d-n2-direct.json','orion-qg-qg7d-n2-generic-verification.json','orion-qg-qg7d-n2-native-verification.json','orion-qg-qg7d-n2-dual-harness.json'):
        p=ART/n
        if p.exists():p.unlink()
    gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
    ar,asv,ao=run(gw,'research/extensions/orion-qg/qg7d_n2_direct.py','ORIONQG_QG7D_N2=',120)
    gr,gsv,go=run(gw,'development/orion-qg-regime-geometry/qg7d_n2_generic_verify.py','ORIONQG_QG7D_N2_GENERIC=',120)
    a=json.loads((ART/'orion-qg-qg7d-n2-direct.json').read_text());g=json.loads((ART/'orion-qg-qg7d-n2-generic-verification.json').read_text())
    if ao.get('result_digest')!=a.get('result_digest'):raise AssertionError('analyzer stdout/file mismatch')
    nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
    nr,nsv,no=run(nw,'development/orion-qg-regime-geometry/qg7d_n2_native_verify.py','ORIONQG_QG7D_N2_NATIVE=',120)
    n=json.loads((ART/'orion-qg-qg7d-n2-native-verification.json').read_text())
    pos=a.get('terminal')=='QG7D_BTRIPLEPRIME_REGIME_FOUND__PINNED_COMM_S2_EXACT_WITNESS';expected='ACCEPT_BTRIPLEPRIME_WITNESS' if pos else 'ACCEPT_BOUNDED_NEGATIVE'
    both=g.get('decision')==expected and g.get('all_checks') is True and n.get('decision')==expected and n.get('all_checks') is True
    terminal=a.get('terminal') if both else 'QG7D_N2_GENERIC_NATIVE_DISAGREEMENT'
    d={'schema':'ORIONQG.QG7D.N2DualHarness.v1','issue':'SzeChunYiu/ORION#836','terminal':terminal,'source_result_digest':a.get('result_digest'),'both_accept':both,'positive':pos,'strict_witness_count':a.get('strict_witness_count'),'selected':a.get('selected'),'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':asv.as_dict(),'verifier_request':gr.as_dict(),'verifier_result':gsv.as_dict()},'native_lane':{'decision':n.get('decision'),'request':nr.as_dict(),'result':nsv.as_dict()},'global_all_n_closure_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
    (ART/'orion-qg-qg7d-n2-dual-harness.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'terminal':terminal,'both_accept':both,'strict_witness_count':a.get('strict_witness_count'),'selected_index':None if a.get('selected') is None else a['selected']['index']},sort_keys=True))
    if not both: raise AssertionError({'generic':g.get('decision'),'native':n.get('decision'),'expected':expected})
    if not all(a.get('gates',{}).values()): raise AssertionError({'analyzer_gates':a.get('gates')})
    if a.get('global_all_n_closure_authority') is not False: raise AssertionError('N2_DIRECT may not grant all-n authority')
    return 0
if __name__=='__main__':raise SystemExit(main())
