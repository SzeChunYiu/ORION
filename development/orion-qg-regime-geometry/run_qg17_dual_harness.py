#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg17-generic';NW=ROOT/'.orion-qg-qg17-native'
def token(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout=120):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout});res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0:raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ('orion-qg-qg17-r6i-phase-sharpness.json','orion-qg-qg17-generic-verification.json','orion-qg-qg17-native-verification.json','orion-qg-qg17-dual-harness.json'):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True);areq,ares,asum=run(gw,'research/extensions/orion-qg/qg17_r6i_phase_sharpness.py','ORIONQG_QG17=',120);greq,gres,gsum=run(gw,'development/orion-qg-regime-geometry/qg17_generic_verify.py','ORIONQG_QG17_GENERIC=',120)
 a=json.loads((ART/'orion-qg-qg17-r6i-phase-sharpness.json').read_text());g=json.loads((ART/'orion-qg-qg17-generic-verification.json').read_text())
 if asum.get('result_digest')!=a.get('result_digest'):raise AssertionError('analyzer digest mismatch')
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nreq,nres,nsum=run(nw,'development/orion-qg-regime-geometry/qg17_native_verify.py','ORIONQG_QG17_NATIVE=',120);n=json.loads((ART/'orion-qg-qg17-native-verification.json').read_text())
 pos=a.get('terminal')=='QG17_SUPPORT2_PHASE_WITNESS_FOUND_AT_FROZEN_OUTSIDE_OBJECTIVE';expected='ACCEPT_SUPPORT2_PHASE_WITNESS' if pos else 'ACCEPT_BOUNDED_NEGATIVE';both=g.get('decision')==expected and n.get('decision')==expected;terminal=a.get('terminal') if both else 'QG17_GENERIC_NATIVE_DISAGREEMENT'
 d={'schema':'ORION.QG.QG17.DualHarness.v1','issue':'SzeChunYiu/ORION#814','terminal':terminal,'source_result_digest':a.get('result_digest'),'both_accept':both,'positive':pos,'outside_objectives':a.get('outside_objectives_with_strict_witness',[]),'annotation':a.get('annotation'),'generic_lane':{'decision':g.get('decision'),'analyzer_request':areq.as_dict(),'analyzer_result':ares.as_dict(),'verifier_request':greq.as_dict(),'verifier_result':gres.as_dict(),'verification':g},'native_lane':{'decision':n.get('decision'),'request':nreq.as_dict(),'result':nres.as_dict(),'verification':n},'global_phase_boundary_complete':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
 (ART/'orion-qg-qg17-dual-harness.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':terminal,'both_accept':both,'outside_objectives':d['outside_objectives'],'annotation':d['annotation'],'strict_counts':{k:v['strict_count'] for k,v in a['objectives'].items()}},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
