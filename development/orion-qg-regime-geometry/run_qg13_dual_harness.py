#!/usr/bin/env python3
from __future__ import annotations
import json, shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'artifacts'
GW=ROOT/'.orion-qg-qg13-generic'
NW=ROOT/'.orion-qg-qg13-native'

def token(stdout,prefix):
    rows=[x for x in stdout.splitlines() if x.startswith(prefix)]
    if len(rows)!=1: raise ValueError({'prefix':prefix,'count':len(rows)})
    return json.loads(rows[0][len(prefix):])

def run_local(ws, path, prefix, timeout=300):
    code=f"import runpy;runpy.run_path({path!r},run_name='__main__')"
    req=ws.get_or_create_request(capability='PYTHON',payload={'code':code,'cwd':'.','timeout':timeout})
    res=service_local_request(ws,req.request_id)
    if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0:
        raise RuntimeError({'path':path,'error':res.error,'output':res.output})
    return req,res,token(str(res.output.get('stdout','')),prefix)

def main():
    for p in (GW,NW):
        if p.exists(): shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
    ar,ao,a=run_local(gw,'research/extensions/orion-qg/qg13_theorem_miner.py','ORIONQG_QG13_THEOREM_MINER=',300)
    gr,go,g=run_local(gw,'development/orion-qg-regime-geometry/qg13_generic_verify.py','ORIONQG_QG13_GENERIC_VERIFY=',300)
    nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
    nr,no,n=run_local(nw,'development/orion-qg-regime-geometry/qg13_native_verify.py','ORIONQG_QG13_NATIVE_VERIFY=',120)
    both=g.get('decision')=='ACCEPT' and n.get('decision')=='ACCEPT_RECOVERY'
    terminal=a.get('terminal') if both else 'QG13_GENERIC_NATIVE_DISAGREEMENT'
    dual={
        'schema':'ORION.QG.QG13.DualHarness.v1','issue':'SzeChunYiu/ORION#767','terminal':terminal,
        'source_result_digest':a.get('result_digest'),'both_accept':both,
        'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':ao.as_dict(),'verifier_request':gr.as_dict(),'verifier_result':go.as_dict(),'verification':g},
        'native_lane':{'decision':n.get('decision'),'request':nr.as_dict(),'result':no.as_dict(),'verification':n},
        'new_theorem_authority':False,'novelty_authority':False,
    }
    (ART/'orion-qg-qg13-dual-harness.json').write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'terminal':terminal,'both_accept':both,'generic':g.get('decision'),'native':n.get('decision')},sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
