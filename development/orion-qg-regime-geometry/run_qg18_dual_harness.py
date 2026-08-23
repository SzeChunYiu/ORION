#!/usr/bin/env python3
from __future__ import annotations
import json, shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2]; ART=ROOT/'artifacts'; GW=ROOT/'.orion-qg-qg18-generic'; NW=ROOT/'.orion-qg-qg18-native'

def token(stdout,prefix):
    rows=[r for r in stdout.splitlines() if r.startswith(prefix)]
    if len(rows)!=1: raise ValueError({'prefix':prefix,'rows':len(rows)})
    return json.loads(rows[0][len(prefix):])
def run(ws,path,prefix,timeout=120):
    req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout})
    res=service_local_request(ws,req.request_id)
    if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0: raise RuntimeError({'path':path,'error':res.error,'output':res.output})
    return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
    for p in (GW,NW):
        if p.exists(): shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    for name in ('orion-qg-qg18-tare-kappa2.json','orion-qg-qg18-generic-verification.json','orion-qg-qg18-native-verification.json','orion-qg-qg18-dual-harness.json'):
        p=ART/name
        if p.exists(): p.unlink()
    gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
    areq,ares,_=run(gw,'research/extensions/orion-qg/qg18_tare_kappa2.py','ORIONQG_QG18=',120)
    greq,gres,_=run(gw,'development/orion-qg-regime-geometry/qg18_generic_verify.py','ORIONQG_QG18_GENERIC=',120)
    result=json.loads((ART/'orion-qg-qg18-tare-kappa2.json').read_text()); generic=json.loads((ART/'orion-qg-qg18-generic-verification.json').read_text())
    nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
    nreq,nres,_=run(nw,'development/orion-qg-regime-geometry/qg18_native_verify.py','ORIONQG_QG18_NATIVE=',120)
    native=json.loads((ART/'orion-qg-qg18-native-verification.json').read_text())
    both=generic.get('decision')=='ACCEPT_KAPPA2' and native.get('decision')=='ACCEPT_KAPPA2'
    terminal=result.get('terminal') if both else 'QG18_GENERIC_NATIVE_DISAGREEMENT'
    dual={'schema':'ORION.QG.QG18.DualHarness.v1','issue':'SzeChunYiu/ORION#838','terminal':terminal,'both_accept':both,'intrinsic_support_number':2 if both else None,'generic_lane':{'decision':generic.get('decision'),'analyzer_request':areq.as_dict(),'analyzer_result':ares.as_dict(),'verifier_request':greq.as_dict(),'verifier_result':gres.as_dict()},'native_lane':{'decision':native.get('decision'),'request':nreq.as_dict(),'result':nres.as_dict()},'novelty_authority':False,'physical_quantum_advantage_claim':False}
    (ART/'orion-qg-qg18-dual-harness.json').write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'terminal':terminal,'both_accept':both,'kappa':dual['intrinsic_support_number']},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
