#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
R=Path(__file__).resolve().parents[2];A=R/'artifacts';G=R/'.orion-qg-qg13v3-generic';N=R/'.orion-qg-qg13v3-native';AP=A/'orion-qg-qg13v3-three-column.json';GP=A/'orion-qg-qg13v3-generic-verification.json';DP=A/'orion-qg-qg13v3-dual-harness.json'
def local(ws,code):
 q=ws.get_or_create_request(capability='PYTHON',payload={'code':code,'cwd':'.','timeout':120});z=service_local_request(ws,q.request_id)
 if not z.success or not isinstance(z.output,dict) or z.output.get('returncode')!=0 or z.output.get('sandboxed') is not False:raise RuntimeError(z.error or 'local failure')
 return q,z
def main():
 for p in(G,N):
  if p.exists():shutil.rmtree(p)
 for p in(AP,GP,DP):p.unlink(missing_ok=True)
 A.mkdir(parents=True,exist_ok=True);ws=ResearchWorkspace.initialize(G,project_root=R,allow_process_tools=True);ar,az=local(ws,"import runpy;runpy.run_path('research/extensions/orion-qg/qg13_v3_three_column.py',run_name='__main__')");gr,gz=local(ws,"import runpy;runpy.run_path('development/orion-qg-regime-geometry/qg13_v3_generic_verify.py',run_name='__main__')");a=json.loads(AP.read_text());g=json.loads(GP.read_text());validate_manifest(QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST);nw=ResearchWorkspace.initialize(N,project_root=R,allow_process_tools=True);o=run_campaign(nw,QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST,max_cycles=4,auto_service_local=True);s=CampaignState.from_dict(nw.load_latest_campaign_state(QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST['campaign_id']));mp={'CANDIDATE_RECORDED':'ACCEPT_E3_SUPPORT4_CANDIDATE','CLOSEDNEW_RECORDED':'ACCEPT_V2_CLOSED_NEW_REMAINS','OBSTRUCTION_RECORDED':'ACCEPT_THREE_COLUMN_OBSTRUCTION','RESOURCE_RECORDED':'ACCEPT_RESOURCE_BOUNDARY','REJECT_RECORDED':'REJECT'};n=mp.get(s.phase_id,'INCOMPLETE');ok=g.get('decision')=='ACCEPT' and n.startswith('ACCEPT_');t=a.get('terminal') if ok else 'QG13V3_NATIVE_GENERIC_DISAGREEMENT';d={'schema':'ORION.QG.QG13V3.DualHarness.v1','issue':'SzeChunYiu/ORION#785','terminal':t,'both_accept':ok,'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':az.as_dict(),'verifier_request':gr.as_dict(),'verifier_result':gz.as_dict()},'native_lane':{'decision':n,'outcome':o,'final_state':s.as_dict()},'new_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False};DP.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':t,'native':n,'e3':a['census']['e3_covered'],'v3_closes_v2':a['census']['v3_closes_v2'],'union':a['census']['cumulative_e2_e3_covered']},indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
