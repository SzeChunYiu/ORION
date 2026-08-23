#!/usr/bin/env python3
from __future__ import annotations
import json,shutil
from pathlib import Path
from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG13V4_SUPPORT4_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace
R=Path(__file__).resolve().parents[2];A=R/'artifacts';G=R/'.orion-qg-qg13v4-generic';N=R/'.orion-qg-qg13v4-native';AP=A/'orion-qg-qg13v4-support4.json';GP=A/'orion-qg-qg13v4-generic-verification.json';DP=A/'orion-qg-qg13v4-dual-harness.json'
def local(ws,code):
 q=ws.get_or_create_request(capability='PYTHON',payload={'code':code,'cwd':'.','timeout':180});z=service_local_request(ws,q.request_id)
 if not z.success or not isinstance(z.output,dict) or z.output.get('returncode')!=0 or z.output.get('sandboxed') is not False:raise RuntimeError(z.error or 'local failure')
 return q,z
def main():
 for p in(G,N):
  if p.exists():shutil.rmtree(p)
 for p in(AP,GP,DP):p.unlink(missing_ok=True)
 A.mkdir(parents=True,exist_ok=True);ws=ResearchWorkspace.initialize(G,project_root=R,allow_process_tools=True);ar,az=local(ws,"import runpy;runpy.run_path('research/extensions/orion-qg/qg13_v4_support4.py',run_name='__main__')");gr,gz=local(ws,"import runpy;runpy.run_path('development/orion-qg-regime-geometry/qg13_v4_generic_verify.py',run_name='__main__')");a=json.loads(AP.read_text());g=json.loads(GP.read_text());validate_manifest(QG13V4_SUPPORT4_CAMPAIGN_MANIFEST);nw=ResearchWorkspace.initialize(N,project_root=R,allow_process_tools=True);o=run_campaign(nw,QG13V4_SUPPORT4_CAMPAIGN_MANIFEST,max_cycles=4,auto_service_local=True);s=CampaignState.from_dict(nw.load_latest_campaign_state(QG13V4_SUPPORT4_CAMPAIGN_MANIFEST['campaign_id']));mp={'THEOREM_RECORDED':'ACCEPT_SUPPORT4_THEOREM_EVIDENCE','COUNTER_RECORDED':'ACCEPT_ANCHORED_COUNTEREXAMPLE','SPEC_GAP_RECORDED':'ACCEPT_SPECTATOR_GAP','PARENT_FAIL_RECORDED':'ACCEPT_PARENT_BINDING_FAILURE','REJECT_RECORDED':'REJECT'};n=mp.get(s.phase_id,'INCOMPLETE');ok=g.get('decision')=='ACCEPT' and n.startswith('ACCEPT_');t=a.get('terminal') if ok else 'QG13V4_NATIVE_GENERIC_DISAGREEMENT';d={'schema':'ORION.QG.QG13V4.DualHarness.v1','issue':'SzeChunYiu/ORION#790','terminal':t,'both_accept':ok,'generic_lane':{'decision':g.get('decision'),'analyzer_request':ar.as_dict(),'analyzer_result':az.as_dict(),'verifier_request':gr.as_dict(),'verifier_result':gz.as_dict()},'native_lane':{'decision':n,'outcome':o,'final_state':s.as_dict()},'scope':'R6I_SUPPORT4_ONLY','novelty_authority':False,'physical_quantum_advantage_claim':False};DP.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'terminal':t,'native':n,'g0':a['anchored_slices']['g0']['union_covered'],'g1':a['anchored_slices']['g1']['union_covered']},sort_keys=True,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
