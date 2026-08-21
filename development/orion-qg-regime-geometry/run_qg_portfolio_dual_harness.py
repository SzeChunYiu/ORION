#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2]; ART=ROOT/'artifacts'; GW=ROOT/'.orion-qg-portfolio-generic'; NW=ROOT/'.orion-qg-portfolio-native'
def token(s,p):
 rows=[r for r in s.splitlines() if r.startswith(p)]
 if len(rows)!=1: raise ValueError({'prefix':p,'rows':len(rows)})
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':120}); res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0: raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists(): shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for n in ('orion-qg-portfolio-closure.json','orion-qg-portfolio-generic.json','orion-qg-portfolio-native.json','orion-qg-portfolio-dual.json'):
  p=ART/n
  if p.exists(): p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True); areq,ares,_=run(gw,'research/extensions/orion-qg/qg_portfolio_closure.py','ORIONQG_PORTFOLIO='); greq,gres,_=run(gw,'development/orion-qg-regime-geometry/qg_portfolio_generic_verify.py','ORIONQG_PORTFOLIO_GENERIC='); a=json.loads((ART/'orion-qg-portfolio-closure.json').read_text()); g=json.loads((ART/'orion-qg-portfolio-generic.json').read_text())
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True); nreq,nres,_=run(nw,'development/orion-qg-regime-geometry/qg_portfolio_native_verify.py','ORIONQG_PORTFOLIO_NATIVE='); n=json.loads((ART/'orion-qg-portfolio-native.json').read_text()); both=g.get('decision')=='ACCEPT_PORTFOLIO_CLOSURE' and n.get('decision')=='ACCEPT_PORTFOLIO_CLOSURE'; terminal=a.get('terminal') if both else 'ORION_QG_PORTFOLIO_GENERIC_NATIVE_DISAGREEMENT'; d={'schema':'ORION.QG.PortfolioDual.v1','terminal':terminal,'both_accept':both,'lane_terminals':{k:v['terminal'] for k,v in a['lanes'].items()},'generic_request':greq.as_dict(),'generic_result':gres.as_dict(),'native_request':nreq.as_dict(),'native_result':nres.as_dict(),'analyzer_request':areq.as_dict(),'analyzer_result':ares.as_dict(),'novelty_authority':False}; (ART/'orion-qg-portfolio-dual.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); print(json.dumps({'terminal':terminal,'both_accept':both,'lanes':{k:v['closed'] for k,v in a['lanes'].items()}},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
