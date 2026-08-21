#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2]; ART=ROOT/'artifacts'; GW=ROOT/'.orion-qg-qg7d-info-generic'; NW=ROOT/'.orion-qg-qg7d-info-native'
def tok(s,p):
 r=[x for x in s.splitlines() if x.startswith(p)]
 if len(r)!=1: raise ValueError((p,len(r)))
 return json.loads(r[0][len(p):])
def run(ws,path,prefix):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':120}); res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0: raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,tok(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists(): shutil.rmtree(p)
 ART.mkdir(exist_ok=True); gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True); ar,as_,_=run(gw,'research/extensions/orion-qg/qg7d_information_closure.py','ORIONQG_QG7D_INFO='); gr,gs,_=run(gw,'development/orion-qg-regime-geometry/qg7d_information_generic_verify.py','ORIONQG_QG7D_INFO_GENERIC='); a=json.loads((ART/'orion-qg-qg7d-information-closure.json').read_text()); g=json.loads((ART/'orion-qg-qg7d-information-generic.json').read_text()); nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True); nr,ns,_=run(nw,'development/orion-qg-regime-geometry/qg7d_information_native_verify.py','ORIONQG_QG7D_INFO_NATIVE='); n=json.loads((ART/'orion-qg-qg7d-information-native.json').read_text()); both=g['decision']=='ACCEPT_CANNOT_CHECK' and n['decision']=='ACCEPT_CANNOT_CHECK'; t=a['terminal'] if both else 'QG7D_INFORMATION_GENERIC_NATIVE_DISAGREEMENT'; d={'schema':'ORION.QG.QG7D.InformationDual.v1','issue':'SzeChunYiu/ORION#836','terminal':t,'both_accept':both,'scientifically_closed_under_stop_rules':both,'all_n_theorem_authority':False,'analyzer_request':ar.as_dict(),'analyzer_result':as_.as_dict(),'generic_request':gr.as_dict(),'generic_result':gs.as_dict(),'native_request':nr.as_dict(),'native_result':ns.as_dict(),'novelty_authority':False}; (ART/'orion-qg-qg7d-information-dual.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); print(json.dumps({'terminal':t,'both_accept':both,'closed':both,'delta_range':[a['hidden_home_test']['delta_min'],a['hidden_home_test']['delta_max']]},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
