#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg9-t2-generic';NW=ROOT/'.orion-qg-qg9-t2-native'
def token(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)]
 if len(rows)!=1:raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def run(ws,path,prefix,timeout):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':f"import runpy;runpy.run_path({path!r},run_name='__main__')",'cwd':'.','timeout':timeout});res=service_local_request(ws,req.request_id)
 if not res.success or not isinstance(res.output,dict) or res.output.get('returncode')!=0:raise RuntimeError({'path':path,'error':res.error,'output':res.output})
 return req,res,token(str(res.output.get('stdout','')),prefix)
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 for name in ('orion-qg-qg9-t2-stage1.json','orion-qg-qg9-t2-result.json','orion-qg-qg9-t2-generic-verification.json','orion-qg-qg9-t2-native-verification.json','orion-qg-qg9-t2-dual-harness.json'):
  p=ART/name
  if p.exists():p.unlink()
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 sreq,sres,ss=run(gw,'research/extensions/orion-qg/qg9_t2_stage1_candidates.py','ORIONQG_QG9_T2_STAGE1=',600)
 rreq,rres,rs=run(gw,'research/extensions/orion-qg/qg9_t2_cap1_referee.py','ORIONQG_QG9_T2_REFEREE=',600)
 greq,gres,gs=run(gw,'development/orion-qg-regime-geometry/qg9_t2_generic_verify.py','ORIONQG_QG9_T2_GENERIC=',600)
 s1=json.loads((ART/'orion-qg-qg9-t2-stage1.json').read_text());result=json.loads((ART/'orion-qg-qg9-t2-result.json').read_text());generic=json.loads((ART/'orion-qg-qg9-t2-generic-verification.json').read_text())
 if ss.get('result_digest')!=s1.get('result_digest') or rs.get('result_digest')!=result.get('result_digest'):raise AssertionError('stdout/file digest mismatch')
 nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);nreq,nres,ns=run(nw,'development/orion-qg-regime-geometry/qg9_t2_native_verify.py','ORIONQG_QG9_T2_NATIVE=',180);native=json.loads((ART/'orion-qg-qg9-t2-native-verification.json').read_text())
 pos=result.get('positive_witness') is not None
 expected_native='ACCEPT_TIGHT_WITNESS' if pos else 'ACCEPT_BOUNDED_NEGATIVE'
 both=generic.get('decision')=='ACCEPT' and native.get('decision')==expected_native
 terminal=result.get('terminal') if both else 'QG9_T2_GENERIC_NATIVE_DISAGREEMENT'
 dual={'schema':'ORION.QG.QG9.T2.DualHarness.v1','issue':'SzeChunYiu/ORION#803','terminal':terminal,'source_result_digest':result.get('result_digest'),'stage1_result_digest':s1.get('result_digest'),'candidate_digest':s1.get('candidate_digest'),'both_accept':both,'generic_lane':{'decision':generic.get('decision'),'stage1_request':sreq.as_dict(),'stage1_result':sres.as_dict(),'referee_request':rreq.as_dict(),'referee_result':rres.as_dict(),'verifier_request':greq.as_dict(),'verifier_result':gres.as_dict(),'verification':generic},'native_lane':{'decision':native.get('decision'),'request':nreq.as_dict(),'result':nres.as_dict(),'verification':native},'positive':pos,'support1_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
 (ART/'orion-qg-qg9-t2-dual-harness.json').write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':terminal,'both_accept':both,'positive':pos,'candidate_count':s1.get('canonical_candidate_count'),'evaluated':result.get('candidates_evaluated')},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
