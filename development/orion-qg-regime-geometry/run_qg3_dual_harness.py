#!/usr/bin/env python3
"""Run QG-3 stage 1 through generic harness and native ORION-Q admission."""
from __future__ import annotations
import json,shutil
from pathlib import Path
from typing import Any
from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
REPO_ROOT=Path(__file__).resolve().parents[2];ARTIFACT_DIR=REPO_ROOT/'artifacts';STAGE1_PATH=ARTIFACT_DIR/'orion-qg-qg3-stage1.json';DUAL_PATH=ARTIFACT_DIR/'orion-qg-qg3-dual-admission.json';GENERIC_WS=REPO_ROOT/'.orion-qg-qg3-generic';NATIVE_WS=REPO_ROOT/'.orion-qg-qg3-native';STAGE1_PREFIX='ORIONQG_QG3_STAGE1=';GENERIC_PREFIX='ORIONQG_QG3_GENERIC_ADMISSION=';STAGE1_TIMEOUT_SECONDS=2400

def _token(stdout:str,prefix:str)->dict[str,Any]:
 rows=[line for line in stdout.splitlines() if line.startswith(prefix)]
 if len(rows)!=1:raise ValueError(f'expected exactly one {prefix} token, got {len(rows)}')
 value=json.loads(rows[0][len(prefix):])
 if not isinstance(value,dict):raise TypeError('token payload must be an object')
 return value

def _run_local(workspace:ResearchWorkspace,code:str):
 request=workspace.get_or_create_request(capability='PYTHON',payload={'code':code,'cwd':'.','timeout':STAGE1_TIMEOUT_SECONDS});result=service_local_request(workspace,request.request_id)
 if not result.success:raise RuntimeError(f'local harness capability failed: {result.error}')
 if not isinstance(result.output,dict) or result.output.get('returncode')!=0:raise RuntimeError('local harness process did not exit cleanly')
 if result.output.get('sandboxed') is not False:raise RuntimeError('process receipt must preserve sandboxed=false')
 return request,result

def main()->int:
 for path in (GENERIC_WS,NATIVE_WS):
  if path.exists():shutil.rmtree(path)
 for path in (STAGE1_PATH,DUAL_PATH):path.unlink(missing_ok=True)
 ARTIFACT_DIR.mkdir(parents=True,exist_ok=True)
 generic_ws=ResearchWorkspace.initialize(GENERIC_WS,project_root=REPO_ROOT,allow_process_tools=True)
 stage1_code="import runpy; runpy.run_path('research/extensions/orion-qg/qg3_stage1_select.py', run_name='__main__')"
 stage1_request,stage1_result=_run_local(generic_ws,stage1_code);stage1_summary=_token(str(stage1_result.output.get('stdout','')),STAGE1_PREFIX)
 if not STAGE1_PATH.is_file():raise FileNotFoundError('QG-3 stage-1 artifact missing after generic harness run')
 stage1=json.loads(STAGE1_PATH.read_text(encoding='utf-8'))
 if stage1_summary.get('stage1_digest')!=stage1.get('stage1_digest'):raise ValueError('stage-1 stdout digest does not match stage-1 artifact')
 admission_code="import runpy; runpy.run_path('development/orion-qg-regime-geometry/qg3_generic_admission.py', run_name='__main__')"
 generic_request,generic_result=_run_local(generic_ws,admission_code);generic_decision=_token(str(generic_result.output.get('stdout','')),GENERIC_PREFIX)
 if generic_decision.get('stage1_digest')!=stage1.get('stage1_digest'):raise ValueError('generic admission is not bound to current stage-1 packet')
 validate_manifest(QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST);native_ws=ResearchWorkspace.initialize(NATIVE_WS,project_root=REPO_ROOT,allow_process_tools=True);native_outcome=run_campaign(native_ws,QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST,max_cycles=4,auto_service_local=True);final_state=CampaignState.from_dict(native_ws.load_latest_campaign_state(QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST['campaign_id']));phase_to_decision={'OPEN_RECORDED':'OPEN','NO_POSITIVE_RECORDED':'NO_POSITIVE','INVALID_RECORDED':'INVALID'};native_decision=phase_to_decision.get(final_state.phase_id,'INCOMPLETE');native_stage1_digest=final_state.observation_map.get('QG3_STAGE1_DIGEST','')
 if native_stage1_digest!=stage1.get('stage1_digest'):raise ValueError('native campaign is not bound to current stage-1 packet')
 both_open=generic_decision.get('decision')=='OPEN' and native_decision=='OPEN';dual={'schema':'ORION.QG.QG3.DualAdmission.v1','issue':'SzeChunYiu/ORION#745','stage1_digest':stage1.get('stage1_digest'),'positive_found':stage1.get('positive_found'),'generic_lane':{'decision':generic_decision.get('decision'),'decision_payload':generic_decision,'stage1_request':stage1_request.as_dict(),'stage1_result':stage1_result.as_dict(),'admission_request':generic_request.as_dict(),'admission_result':generic_result.as_dict()},'native_lane':{'decision':native_decision,'outcome':native_outcome,'final_state':final_state.as_dict()},'both_open':both_open,'ground_truth_opened':False,'novelty_authority':False};DUAL_PATH.write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps({'stage1':str(STAGE1_PATH),'dual_admission':str(DUAL_PATH),'positive_found':stage1.get('positive_found'),'generic_decision':generic_decision.get('decision'),'native_decision':native_decision,'both_open':both_open,'selected':stage1.get('selected'),'stage1_timeout_seconds':STAGE1_TIMEOUT_SECONDS},indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())

