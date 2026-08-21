#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg9-tight-generic';NW=ROOT/'.orion-qg-qg9-tight-native'
def token(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout=900):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout});res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0:raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True);gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 ar,ao,a=run(gw,'research/extensions/orion-qg/qg9_support2_tightness.py','ORIONQG_QG9_TIGHTNESS=',900)
 gr,go,g=run(gw,'development/orion-qg-regime-geometry/qg9_support2_tightness_generic_verify.py','ORIONQG_QG9_TIGHT_GENERIC=',900)
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nr,no,n=run(nw,'development/orion-qg-regime-geometry/qg9_support2_tightness_native_verify.py','ORIONQG_QG9_TIGHT_NATIVE=',180)
 positive=a.get('terminal')=='QG9_SUPPORT2_TIGHT_WITNESS_MACHINE_VERIFIED';both=(g.get('decision')=='ACCEPT_TIGHTNESS' and n.get('decision')=='ACCEPT_TIGHTNESS') if positive else (n.get('decision')=='RECORD_NEGATIVE_PANEL')
 terminal=a.get('terminal') if both else 'QG9_GENERIC_NATIVE_DISAGREEMENT'
 dual={'schema':'ORION.QG.QG9.TightnessDualHarness.v1','issue':'SzeChunYiu/ORION#795','terminal':terminal,'source_result_digest':a.get('result_digest'),'both_accept':bool(both),'positive':positive,'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':ao.as_dict(),'verifier_request':gr.as_dict(),'verifier_result':go.as_dict(),'verification':g},'native_lane':{'decision':n.get('decision'),'request':nr.as_dict(),'result':no.as_dict(),'verification':n},'tightness_authority':bool(positive and both),'support1_authority':False,'novelty_authority':False}
 (ART/'orion-qg-qg9-support2-tightness-dual-harness.json').write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':terminal,'positive':positive,'both_accept':bool(both),'generic':g.get('decision'),'native':n.get('decision')},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
