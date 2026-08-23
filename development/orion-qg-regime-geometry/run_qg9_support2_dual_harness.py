#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg9-support2-generic';NW=ROOT/'.orion-qg-qg9-support2-native'
def token(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout=600):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout});res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0:raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True);gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 ar,ao,a=run(gw,'research/extensions/orion-qg/qg9_support2_full_acceptance.py','ORIONQG_QG9_SUPPORT2=',600)
 gr,go,g=run(gw,'development/orion-qg-regime-geometry/qg9_support2_generic_verify.py','ORIONQG_QG9_SUPPORT2_GENERIC=',600)
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,n=run(nw,'development/orion-qg-regime-geometry/qg9_support2_native_verify.py','ORIONQG_QG9_SUPPORT2_NATIVE=',180)
 both=g.get('decision')=='ACCEPT' and n.get('decision')=='ACCEPT_SUPPORT2';terminal=a.get('terminal') if both else 'QG9_GENERIC_NATIVE_DISAGREEMENT'
 dual={'schema':'ORION.QG.QG9.Support2DualHarness.v1','issue':'SzeChunYiu/ORION#762','terminal':terminal,'source_result_digest':a.get('result_digest'),'both_accept':both,'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':ao.as_dict(),'verifier_request':gr.as_dict(),'verifier_result':go.as_dict(),'verification':g},'native_lane':{'decision':n.get('decision'),'request':nr.as_dict(),'result':no.as_dict(),'verification':n},'support1_authority':False,'tightness_authority':False,'novelty_authority':False}
 (ART/'orion-qg-qg9-support2-dual-harness.json').write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':terminal,'both_accept':both,'generic':g.get('decision'),'native':n.get('decision')},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
