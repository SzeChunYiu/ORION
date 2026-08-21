#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG13_V2_SUPPORT4_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';GW=ROOT/'.orion-qg-qg13v2-generic';NW=ROOT/'.orion-qg-qg13v2-native'
def tok(stdout,p):
 r=[x for x in stdout.splitlines() if x.startswith(p)];
 if len(r)!=1:raise ValueError((p,len(r)))
 return json.loads(r[0][len(p):])
def runlocal(ws,code,t=240):
 req=ws.get_or_create_request(capability='PYTHON',payload={'code':code,'cwd':'.','timeout':t});res=service_local_request(ws,req.request_id)
 if not res.success or res.output.get('returncode')!=0:raise RuntimeError(res.error or res.output)
 return req,res
def main():
 for p in (GW,NW):
  if p.exists():shutil.rmtree(p)
 ART.mkdir(exist_ok=True)
 gw=ResearchWorkspace.initialize(GW,project_root=ROOT,allow_process_tools=True)
 ar,ao=runlocal(gw,"import runpy;runpy.run_path('research/extensions/orion-qg/qg13_v2_r6i_support4.py',run_name='__main__')",300);a=tok(str(ao.output.get('stdout','')),'ORIONQG_QG13_V2_SUPPORT4=')
 vr,vo=runlocal(gw,"import runpy;runpy.run_path('development/orion-qg-regime-geometry/qg13_v2_generic_verify.py',run_name='__main__')",300);g=tok(str(vo.output.get('stdout','')),'ORIONQG_QG13_V2_GENERIC_VERIFY=')
 validate_manifest(QG13_V2_SUPPORT4_CAMPAIGN_MANIFEST);nw=ResearchWorkspace.initialize(NW,project_root=ROOT,allow_process_tools=True);no=run_campaign(nw,QG13_V2_SUPPORT4_CAMPAIGN_MANIFEST,max_cycles=4,auto_service_local=True);fs=CampaignState.from_dict(nw.load_latest_campaign_state(QG13_V2_SUPPORT4_CAMPAIGN_MANIFEST['campaign_id']))
 nd={'ACCEPT_RECORDED':'ACCEPT','REJECT_RECORDED':'REJECT'}.get(fs.phase_id,'INCOMPLETE');both=g.get('decision')=='ACCEPT' and nd=='ACCEPT'
 terminal='QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED' if both and a.get('terminal')=='QG13_V2_R6I_SUPPORT4_CANDIDATE_COMPLETE' else 'QG13_V2_NATIVE_GENERIC_DISAGREEMENT'
 d={'schema':'ORION.QG.QG13V2.DualHarness.v1','issue':'SzeChunYiu/ORION#762','terminal':terminal,'source_result_digest':a.get('result_digest'),'generic':{'decision':g.get('decision'),'checks':g.get('checks'),'analyzer_request':ar.as_dict(),'analyzer_result':ao.as_dict(),'verifier_request':vr.as_dict(),'verifier_result':vo.as_dict()},'native':{'decision':nd,'outcome':no,'final_state':fs.as_dict()},'both_accept':both,'support3_authority':False,'tightness4_authority':False,'novelty_authority':False}
 (ART/'orion-qg-qg13-v2-dual-harness.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':terminal,'both_accept':both,'generic':g.get('decision'),'native':nd},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
