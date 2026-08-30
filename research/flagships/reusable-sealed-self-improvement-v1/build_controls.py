#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent; P=ROOT/'PROTOCOL.json'; F=ROOT/'CONTROL_FIXTURES.json'; R=ROOT/'CONTROL_RESULT.json'
def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def fsha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rh(r):
 u=dict(r);u.pop('receipt_hash',None);return sha(canon(u))
def hist(before,outcome):return sha(before+':'+outcome)
def reasons(r,p):
 g=p['gates'];z=[]
 if Fraction(r['p_value'])>Fraction(r['alpha_spend']):z.append('STATISTICAL_GATE')
 if Fraction(r['fresh_lcb'])<=Fraction(g['fresh_lcb_strictly_greater_than']):z.append('FRESH_GATE')
 if Fraction(r['retention_lcb'])<=Fraction(g['retention_lcb_strictly_greater_than']):z.append('RETENTION_GATE')
 if Fraction(r['harm_ucb'])>=Fraction(g['harm_ucb_strictly_less_than']):z.append('HARM_GATE')
 if r['replay_only_gain']:z.append('REPLAY_ONLY')
 if r['authority_violations']:z.append('AUTHORITY_VIOLATION')
 if r['resource_overrun']:z.append('RESOURCE_OVERRUN')
 if r['protected_feedback_bits_released']>g['max_protected_feedback_bits_per_candidate']:z.append('FEEDBACK_BUDGET')
 return z
def receipt(p,*,rid,prev='0'*64,round_index=1,epoch=1,cid='C',before=None,alpha='0.005',pv='0.001',fresh='0.08',ret='-0.005',harm='0.005',replay=False,auth=(),over=False,bits=1,tag='ok'):
 before=before or sha('ORION.REUSABLE.SEALED.HISTORY.GENESIS.v1');out=sha('outcome:'+rid+':'+tag)
 r={'schema':'ORION.ReusableSealedPromotion.Receipt.v1','receipt_id':rid,'previous_receipt_hash':prev,'round_index':round_index,'evaluator_epoch':epoch,'candidate_id':cid,'candidate_sha256':sha('candidate:'+cid),'evaluator_sha256':sha('evaluator:'+str(epoch)),'history_before':before,'outcome_digest':out,'history_after':hist(before,out),'alpha_spend':alpha,'p_value':pv,'fresh_lcb':fresh,'retention_lcb':ret,'harm_ucb':harm,'replay_only_gain':replay,'authority_violations':list(auth),'resource_overrun':over,'protected_feedback_bits_released':bits}
 z=reasons(r,p);r['decision']='PROMOTE_CONTROL' if not z else 'REJECT_CONTROL:'+','.join(z);r['receipt_hash']=rh(r);return r
def build():
 p=json.loads(P.read_text());G=sha('ORION.REUSABLE.SEALED.HISTORY.GENESIS.v1');x={}
 valid=receipt(p,rid='R-VALID',cid='C-VALID',before=G);x['valid_promotion']=[valid];x['identical_duplicate_idempotent']=[valid,dict(valid)]
 x['replay_only_rejected']=[receipt(p,rid='R-REPLAY',cid='C-REPLAY',before=G,replay=True)]
 x['retention_collapse_rejected']=[receipt(p,rid='R-RET',cid='C-RET',before=G,ret='-0.03')]
 x['harm_rejected']=[receipt(p,rid='R-HARM',cid='C-HARM',before=G,harm='0.03')]
 x['authority_mutation_rejected']=[receipt(p,rid='R-AUTH',cid='C-AUTH',before=G,auth=('EVALUATOR_MUTATION',))]
 x['feedback_overrun_rejected']=[receipt(p,rid='R-FB',cid='C-FB',before=G,bits=2)]
 x['resource_overrun_rejected']=[receipt(p,rid='R-RES',cid='C-RES',before=G,over=True)]
 a=receipt(p,rid='R-A1',cid='C-A1',before=G,alpha='0.03');b=receipt(p,rid='R-A2',cid='C-A2',prev=a['receipt_hash'],round_index=2,before=a['history_after'],alpha='0.03');x['alpha_budget_overrun_blocked']=[a,b]
 a=receipt(p,rid='R-E1',cid='C-E1',before=G,epoch=2);b=receipt(p,rid='R-E2',cid='C-E2',prev=a['receipt_hash'],round_index=2,before=a['history_after'],epoch=1);x['evaluator_epoch_regression_blocked']=[a,b]
 a=receipt(p,rid='R-H1',cid='C-H1',before=G);b=receipt(p,rid='R-H2',cid='C-H2',prev=a['receipt_hash'],round_index=2,before=G);x['negative_history_deletion_blocked']=[a,b]
 bad=dict(valid);bad['candidate_id']='CONFLICT';bad['candidate_sha256']=sha('candidate:CONFLICT');bad['receipt_hash']=rh(bad);x['conflicting_duplicate_blocked']=[valid,bad]
 bad=dict(valid);bad['fresh_lcb']='0.50';x['receipt_hash_tamper_blocked']=[bad]
 bad=dict(valid);bad.pop('evaluator_sha256');bad['receipt_hash']=rh(bad);x['missing_required_field_blocked']=[bad]
 F.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
 rejected={k for k in x if k.endswith('_rejected')};blocked={k for k in x if k.endswith('_blocked')}
 terms={k:('LEDGER_BLOCKED' if k in blocked else 'CONTROL_REJECTED' if k in rejected else 'CONTROL_PROMOTED') for k in x}
 r={'schema':'ORION.ReusableSealedPromotion.ControlResult.v1','protocol_sha256':fsha(P),'fixture_file_sha256':fsha(F),'fixture_terminals':dict(sorted(terms.items())),'terminal':'CONTROL_PLANE_GENERATED__INDEPENDENT_CHECK_REQUIRED','theorem_and_control_plane_authority':True,'protected_transfer_authority':False,'frontier_agent_performance_authority':False,'negative_history_effect_authority':False,'submission_authority':False};r['result_digest']=sha(canon(r));R.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');return r
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=R);z=a.parse_args();r=build();
 if z.output!=R:z.output.write_bytes(R.read_bytes())
 print(canon({'terminal':r['terminal'],'digest':r['result_digest']}))
if __name__=='__main__':main()
