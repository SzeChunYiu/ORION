#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2]; ART=ROOT/'artifacts'; GW=ROOT/'.orion-qg-qg7d-pad-generic'; NW=ROOT/'.orion-qg-qg7d-pad-native'
def token(s,p):
 rows=[r for r in s.splitlines() if r.startswith(p)]
 if len(rows)!=1: raise ValueError({'prefix':p,'rows':len(rows)})
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout=120):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout}); res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0: raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists(): shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ('orion-qg-qg7d-padding-ablation.json','orion-qg-qg7d-padding-generic.json','orion-qg-qg7d-padding-native.json','orion-qg-qg7d-padding-dual.json'):
  p=ART/name
  if p.exists(): p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True); areq,ares,_=run(gw,'research/extensions/orion-qg/qg7d_padding_ablation.py','ORIONQG_QG7D_PAD=',120); greq,gres,_=run(gw,'development/orion-qg-regime-geometry/qg7d_padding_generic_verify.py','ORIONQG_QG7D_PAD_GENERIC=',120)
 a=json.loads((ART/'orion-qg-qg7d-padding-ablation.json').read_text()); g=json.loads((ART/'orion-qg-qg7d-padding-generic.json').read_text())
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True); nreq,nres,_=run(nw,'development/orion-qg-regime-geometry/qg7d_padding_native_verify.py','ORIONQG_QG7D_PAD_NATIVE=',120); n=json.loads((ART/'orion-qg-qg7d-padding-native.json').read_text())
 positive=a['terminal'].startswith('QG7D_BTRIPLEPRIME'); expected='ACCEPT_BTRIPLEPRIME_WITNESS' if positive else 'ACCEPT_BOUNDED_NEGATIVE'; both=g.get('decision')==expected and n.get('decision')==expected
 terminal=a.get('terminal') if both else 'QG7D_PADDING_GENERIC_NATIVE_DISAGREEMENT'; d={'schema':'ORION.QG.QG7D.PaddingDual.v1','issue':'SzeChunYiu/ORION#836','terminal':terminal,'both_accept':both,'positive_btripleprime':positive and both,'all_n_theorem_authority':False,'generic_lane':{'decision':g.get('decision'),'request':greq.as_dict(),'result':gres.as_dict()},'native_lane':{'decision':n.get('decision'),'request':nreq.as_dict(),'result':nres.as_dict()},'analyzer_request':areq.as_dict(),'analyzer_result':ares.as_dict(),'novelty_authority':False}; (ART/'orion-qg-qg7d-padding-dual.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); print(json.dumps({'terminal':terminal,'both_accept':both,'gap_counts':{k:v['strict_gap_count'] for k,v in a['policies'].items()}},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
