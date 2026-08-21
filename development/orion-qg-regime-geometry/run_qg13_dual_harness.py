#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.orion_qg.qg13_theorem_miner import QG13_THEOREM_MINER_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg13-generic';NW=ROOT/'.orion-qg-qg13-native'
def token(s,p):
 rows=[x for x in s.splitlines() if x.startswith(p)];
 if len(rows)!=1: raise ValueError((p,len(rows)))
 return json.loads(rows[0][len(p):])
def runlocal(ws,code,timeout=180):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':code,'cwd':'.','timeout':timeout});res=service_local_request(ws,req.request_id)
 if not res.success or res.output.get('returncode')!=0: raise RuntimeError(res.error or res.output)
 return req,res
def main():
 for p in (GW,NW):
  if p.exists(): shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 ar,ao=runlocal(gw,"import runpy;runpy.run_path('research/extensions/orion-qg/qg13_theorem_miner.py',run_name='__main__')",240)
 a=token(str(ao.output.get('stdout','')),'ORIONQG_QG13_THEOREM_MINER=')
 vr,vo=runlocal(gw,"import runpy;runpy.run_path('development/orion-qg-regime-geometry/qg13_generic_verify.py',run_name='__main__')",240)
 g=token(str(vo.output.get('stdout','')),'ORIONQG_QG13_GENERIC_VERIFY=')
 validate_manifest(QG13_THEOREM_MINER_CAMPAIGN_MANIFEST);nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True)
 no=run_campaign(nw,QG13_THEOREM_MINER_CAMPAIGN_MANIFEST,max_cycles=4,auto_service_local=True);fs=CampaignState.from_dict(nw.load_latest_campaign_state(QG13_THEOREM_MINER_CAMPAIGN_MANIFEST['campaign_id']))
 nd={'ACCEPT_RECORDED':'ACCEPT','REJECT_RECORDED':'REJECT'}.get(fs.phase_id,'INCOMPLETE'); both=g.get('decision')=='ACCEPT' and nd=='ACCEPT'
 dual={'schema':'ORION.QG.QG13.DualHarness.v1','issue':'SzeChunYiu/ORION#767','terminal':a.get('terminal') if both else 'QG13_NATIVE_GENERIC_DISAGREEMENT','source_result_digest':a.get('result_digest'),'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':ao.as_dict(),'verifier_request':vr.as_dict(),'verifier_result':vo.as_dict(),'verification':g},'native_lane':{'decision':nd,'outcome':no,'final_state':fs.as_dict()},'both_accept':both,'new_theorem_authority':False,'novelty_authority':False}
 (ART/'orion-qg-qg13-dual-harness.json').write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'terminal':dual['terminal'],'both_accept':both,'generic':g.get('decision'),'native':nd},sort_keys=True));return 0
if __name__=='__main__': raise SystemExit(main())
