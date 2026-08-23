"""Native ORION-Q bounded admission for QG-13 theorem-miner recovery."""
_LOAD='ORIONQG_QG13_NATIVE_LOAD='; _DEC='ORIONQG_QG13_NATIVE_DECISION='

def _decision(decision,next_phase):
    payload={'decision':decision,'new_theorem_authority':False,'novelty_authority':False,'v2_scope':'NEW_EDIT_REQUIRES_NEW_FREEZE'}
    code="import json;print('"+_DEC+"'+json.dumps("+repr(payload)+",sort_keys=True,separators=(',',':')))"
    return {'host_capability':'PYTHON','payload':{'code':code,'cwd':'.','timeout':30},'result_contract':{'kind':'SHELL_JSON_TOKEN','prefix':_DEC,'required_payload_values':[{'path':['decision'],'equals':decision},{'path':['new_theorem_authority'],'equals':False},{'path':['novelty_authority'],'equals':False}],'evidence_rules':[{'evidence_key':'QG13_DECISION','path':['decision'],'transform':'STRING'}]},'next_phase':next_phase}

_LOAD_CODE=r'''
import hashlib,json
from pathlib import Path
a=json.loads(Path('artifacts/orion-qg-qg13-theorem-miner.json').read_text());g=json.loads(Path('artifacts/orion-qg-qg13-generic-verification.json').read_text())
u=dict(a);obs=u.pop('result_digest');canon=json.dumps(u,sort_keys=True,separators=(',',':'),allow_nan=False)
out={'positive':a.get('terminal')=='QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS','digest':obs==hashlib.sha256(canon.encode()).hexdigest(),'gates':all(a.get('gates',{}).values()),'generic':g.get('decision')=='ACCEPT' and all(g.get('checks',{}).values()),'r6m_bound':a.get('r6m_theorem_candidate',{}).get('support_bound')==2,'r6i_bound':a.get('r6i_theorem_candidate',{}).get('support_bound')==5,'cone':a.get('r6m_theorem_candidate',{}).get('objective_cone')==['t_c >= 2*t_r','t_nc >= 2*t_r'],'authority':a.get('new_theorem_authority') is False and a.get('novelty_authority') is False}
print('ORIONQG_QG13_NATIVE_LOAD='+json.dumps(out,sort_keys=True,separators=(',',':')))
'''
_ACCEPT={k:['YES'] for k in ['QG13_POSITIVE','QG13_DIGEST','QG13_GATES','QG13_GENERIC','QG13_R6M','QG13_R6I','QG13_CONE','QG13_AUTH']}
QG13_THEOREM_MINER_CAMPAIGN_MANIFEST={
 'schema':'ORION.ResearchCampaignManifest.v1','campaign_id':'orion-qg:qg13-theorem-miner-v1','claim_id':'orion-qg:qg13-parent-recovery','initial_phase':'S0','initial_observations':{'QG13_NEED':'YES'},'authority_ceiling':'NON_AUTHORIZING_THEOREM_MINER_RECOVERY','protected_refs':[],
 'capabilities':{
  'qg13.load':{'host_capability':'PYTHON','payload':{'code':_LOAD_CODE,'cwd':'.','timeout':30},'declared_read_paths':['artifacts/orion-qg-qg13-theorem-miner.json','artifacts/orion-qg-qg13-generic-verification.json'],'result_contract':{'kind':'SHELL_JSON_TOKEN','prefix':_LOAD,'required_payload_values':[{'path':['authority'],'equals':True}],'evidence_rules':[{'evidence_key':'QG13_POSITIVE','path':['positive'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_DIGEST','path':['digest'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_GATES','path':['gates'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_GENERIC','path':['generic'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_R6M','path':['r6m_bound'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_R6I','path':['r6i_bound'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_CONE','path':['cone'],'transform':'BOOL_YES_NO'},{'evidence_key':'QG13_AUTH','path':['authority'],'transform':'BOOL_YES_NO'}]},'next_phase':'D0'},
  'qg13.accept':_decision('ACCEPT_RECOVERY','ACCEPT_RECORDED'),'qg13.reject':_decision('REJECT','REJECT_RECORDED')},
 'phases':{
  'S0':{'active_hard_obligations':['QG13_LOAD'],'responsibility_hypotheses':[{'hypothesis_id':'RESP:LOAD','expected_observations':{'QG13_NEED':['YES']}}],'interface_checks':[{'check_id':'IFACE:SERIALIZED','scope':'EVIDENCE_BINDING','state':'PASS'}],'revision_mechanics':[{'mechanic_id':'REV:WAIT','kind':'WAIT_EVIDENCE','write_coordinates':['EVIDENCE'],'cost':0.1}],'computation_actions':[{'action_id':'COMPUTE:LOAD','kind':'VERIFY','expected_decision_value':5.0,'cost':0.1,'discharges_obligations':['QG13_LOAD']}],'responsibility_bindings':{'RESP:LOAD':['REV:WAIT']},'selected_capabilities':{'COMPUTE:LOAD':'qg13.load'}},
  'D0':{'active_hard_obligations':[],'responsibility_hypotheses':[{'hypothesis_id':'RESP:ACCEPT','expected_observations':_ACCEPT},{'hypothesis_id':'RESP:REJECT','expected_observations':{'QG13_POSITIVE':['NO']}}],'interface_checks':[{'check_id':'IFACE:NO_SELF_AUTH','scope':'AUTHORITY','state':'PASS'}],'revision_mechanics':[{'mechanic_id':'REV:ACCEPT','kind':'ACCEPT_BOUNDED_RECOVERY','read_coordinates':['EVIDENCE'],'write_coordinates':['BOUNDED_RESULT'],'cost':0.1},{'mechanic_id':'REV:REJECT','kind':'REJECT','read_coordinates':['EVIDENCE'],'write_coordinates':['TERMINAL'],'cost':0.1}],'computation_actions':[{'action_id':'COMPUTE:NONE','kind':'NONE','expected_decision_value':0.0,'cost':1.0}],'responsibility_bindings':{'RESP:ACCEPT':['REV:ACCEPT'],'RESP:REJECT':['REV:REJECT']},'selected_capabilities':{'REV:ACCEPT':'qg13.accept','REV:REJECT':'qg13.reject'}},
  'ACCEPT_RECORDED':{'terminal':True,'terminal_name':'QG13_NATIVE_ACCEPT_RECORDED','active_hard_obligations':[]},'REJECT_RECORDED':{'terminal':True,'terminal_name':'QG13_NATIVE_REJECT_RECORDED','active_hard_obligations':[]}}}
