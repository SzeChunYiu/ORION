#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2]; ART=ROOT/'artifacts'; GW=ROOT/'.orion-qg-programme-closure-generic'; NW=ROOT/'.orion-qg-programme-closure-native'
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
 ART.mkdir(exist_ok=True)
 for n in ('orion-qg-programme-scientific-closure.json','orion-qg-programme-closure-generic.json','orion-qg-programme-closure-native.json','orion-qg-programme-closure-dual.json'):
  p=ART/n
  if p.exists(): p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True); ar,as_,_=run(gw,'research/extensions/orion-qg/qg_programme_scientific_closure.py','ORIONQG_PROGRAMME_CLOSURE='); gr,gs,_=run(gw,'development/orion-qg-regime-geometry/qg_programme_closure_generic_verify.py','ORIONQG_PROGRAMME_CLOSURE_GENERIC='); a=json.loads((ART/'orion-qg-programme-scientific-closure.json').read_text()); g=json.loads((ART/'orion-qg-programme-closure-generic.json').read_text())
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True); nr,ns,_=run(nw,'development/orion-qg-regime-geometry/qg_programme_closure_native_verify.py','ORIONQG_PROGRAMME_CLOSURE_NATIVE='); n=json.loads((ART/'orion-qg-programme-closure-native.json').read_text()); both=g.get('decision')=='ACCEPT_PROGRAMME_SCIENTIFIC_CLOSURE' and n.get('decision')=='ACCEPT_PROGRAMME_SCIENTIFIC_CLOSURE'; t=a.get('terminal') if both else 'ORION_QG_PROGRAMME_CLOSURE_GENERIC_NATIVE_DISAGREEMENT'; d={'schema':'ORION.QG.ProgrammeClosureDual.v1','issue':'SzeChunYiu/ORION#839','programme_issue':'SzeChunYiu/ORION#740','terminal':t,'both_accept':both,'scientifically_closed':both,'result_digest':a.get('result_digest'),'bounded_cannot_checks':a.get('bounded_cannot_checks'),'analyzer_request':ar.as_dict(),'analyzer_result':as_.as_dict(),'generic_request':gr.as_dict(),'generic_result':gs.as_dict(),'native_request':nr.as_dict(),'native_result':ns.as_dict(),'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False}; (ART/'orion-qg-programme-closure-dual.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); print(json.dumps({'terminal':t,'both_accept':both,'closed':both,'result_digest':a.get('result_digest')},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
