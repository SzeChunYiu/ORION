#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve();ROOT=HERE.parent.parent;P=ROOT/'PROTOCOL.json';F=ROOT/'CONTROL_FIXTURES.json';R=ROOT/'CONTROL_RESULT.json';O=ROOT/'GENERIC_RESULT.json'
def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def fsha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rh(r):u=dict(r);u.pop('receipt_hash',None);return sha(canon(u))
def decision(r,p):
 g=p['gates'];z=[]
 if Fraction(r['p_value'])>Fraction(r['alpha_spend']):z.append('STATISTICAL_GATE')
 if Fraction(r['fresh_lcb'])<=Fraction(g['fresh_lcb_strictly_greater_than']):z.append('FRESH_GATE')
 if Fraction(r['retention_lcb'])<=Fraction(g['retention_lcb_strictly_greater_than']):z.append('RETENTION_GATE')
 if Fraction(r['harm_ucb'])>=Fraction(g['harm_ucb_strictly_less_than']):z.append('HARM_GATE')
 if r['replay_only_gain']:z.append('REPLAY_ONLY')
 if r['authority_violations']:z.append('AUTHORITY_VIOLATION')
 if r['resource_overrun']:z.append('RESOURCE_OVERRUN')
 if r['protected_feedback_bits_released']>g['max_protected_feedback_bits_per_candidate']:z.append('FEEDBACK_BUDGET')
 return 'PROMOTE_CONTROL' if not z else 'REJECT_CONTROL:'+','.join(z)
def check(rows,p):
 req=set(p['required_receipt_fields']);seen={};errs=[];decs=[];prev='0'*64;hist=None;round0=epoch0=0;spent=Fraction(0)
 for i,r in enumerate(rows,1):
  miss=req-set(r)
  if miss:errs.append(f'{i}:MISSING:{sorted(miss)}');continue
  rid=r['receipt_id'];c=canon(r)
  if rid in seen:
   if seen[rid]!=c:errs.append(f'{i}:CONFLICTING_DUPLICATE')
   continue
  seen[rid]=c
  if r['receipt_hash']!=rh(r):errs.append(f'{i}:HASH')
  if r['previous_receipt_hash']!=prev:errs.append(f'{i}:PREVIOUS')
  if r['round_index']<=round0:errs.append(f'{i}:ROUND')
  if r['evaluator_epoch']<epoch0:errs.append(f'{i}:EPOCH')
  if hist is not None and r['history_before']!=hist:errs.append(f'{i}:HISTORY_CHAIN')
  if r['history_after']!=sha(r['history_before']+':'+r['outcome_digest']):errs.append(f'{i}:HISTORY_HASH')
  try:
   spent+=Fraction(r['alpha_spend'])
   if spent>Fraction(p['global_false_promotion_budget']):errs.append(f'{i}:ALPHA_BUDGET')
   d=decision(r,p);decs.append(d)
   if d!=r['decision']:errs.append(f'{i}:DECISION')
  except Exception as e:errs.append(f'{i}:NUMERIC:{e}')
  prev=r['receipt_hash'];hist=r['history_after'];round0=r['round_index'];epoch0=r['evaluator_epoch']
 term='LEDGER_BLOCKED' if errs else 'CONTROL_PROMOTED' if decs and all(d=='PROMOTE_CONTROL' for d in decs) else 'CONTROL_REJECTED'
 return {'terminal':term,'errors':errs,'unique_receipts':len(seen),'cumulative_alpha':str(spent),'decisions':decs}
def run():
 p=json.loads(P.read_text());fx=json.loads(F.read_text());src=json.loads(R.read_text());u=dict(src);obs=u.pop('result_digest',None)
 checks={'protocol_schema':p['schema']=='ORION.SafeLongitudinalSelfImprovement.ReusableSealedEvalProtocol.v1','subject_bound':p['subject_main_sha']=='b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8','source_digest':obs==sha(canon(u)),'protocol_hash':src['protocol_sha256']==fsha(P),'fixture_hash':src['fixture_file_sha256']==fsha(F),'authority_fail_closed':not any(src[k] for k in ['protected_transfer_authority','frontier_agent_performance_authority','negative_history_effect_authority','submission_authority'])}
 results={}
 for name,rows in sorted(fx.items()):
  got=check(rows,p);exp=src['fixture_terminals'][name];ok=got['terminal']==exp;checks['fixture:'+name]=ok;results[name]={'expected':exp,'observed':got,'ok':ok}
 good=all(checks.values());r={'schema':'ORION.ReusableSealedPromotion.GenericVerification.v1','decision':'CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN' if good else 'CONTROL_PLANE_REJECTED','checks':checks,'fixtures':results,'theorem_and_control_plane_authority':good,'protected_transfer_authority':False,'frontier_agent_performance_authority':False,'negative_history_effect_authority':False,'submission_authority':False};r['verification_digest']=sha(canon(r));return r
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=O);z=a.parse_args();r=run();z.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(canon({'decision':r['decision'],'digest':r['verification_digest']}));return 0 if all(r['checks'].values()) else 1
if __name__=='__main__':raise SystemExit(main())
