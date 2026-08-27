#!/usr/bin/env python3
"""Freeze ORION-01--04 at their current earned scientific/content ceilings.

This does not mark the wider convergence programme closed. It turns any later
promotion experiment into successor-only work, while preserving current
established, adverse, null, retracted and CANNOT_CHECK evidence as immutable
paper authority.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
STATUS_PATH=ROOT/'research/orion-01-05-convergence-v1/SCIENCE_STATUS_V1.json'
OUT=ROOT/'papers/publication_closure/receipts/remaining11'
PAPERS={
 'ORION-01':{
   'title':'Certificate Realization','dir':'papers/orion-01-certificate-realization',
   'manuscripts':['papers/orion-01-certificate-realization/theory-A-MANUSCRIPT_V2.md','papers/orion-01-certificate-realization/theory-B-MANUSCRIPT_V2.md'],
   'addendum':'papers/orion-01-certificate-realization/PUBLICATION_FREEZE_ADDENDUM_V1.md',
   'terminal':'ORION_01_CURRENT_EARNED_SCIENCE_AND_CONTENT_FROZEN__PRODUCTION_SUCCESSOR_ONLY'},
 'ORION-02':{
   'title':'FiberGuard Finite Fibre','dir':'papers/orion-02-fiberguard-finite-fibre',
   'manuscripts':['papers/orion-02-fiberguard-finite-fibre/MANUSCRIPT_V2.md'],
   'addendum':'papers/orion-02-fiberguard-finite-fibre/PUBLICATION_FREEZE_ADDENDUM_V1.md',
   'terminal':'ORION_02_CURRENT_EARNED_SCIENCE_AND_CONTENT_FROZEN__TRANSFER_SUCCESSOR_ONLY'},
 'ORION-03':{
   'title':'Typed Merge Falsification','dir':'papers/orion-03-typed-merge-falsification',
   'manuscripts':['papers/orion-03-typed-merge-falsification/MANUSCRIPT_V2.md'],
   'addendum':'papers/orion-03-typed-merge-falsification/PUBLICATION_FREEZE_ADDENDUM_V1.md',
   'terminal':'ORION_03_CURRENT_EARNED_SCIENCE_AND_CONTENT_FROZEN__EXTERNAL_POLICY_SUCCESSOR_ONLY'},
 'ORION-04':{
   'title':'Rooted Completion Certificates','dir':'papers/orion-04-rooted-completion-certificates',
   'manuscripts':['papers/orion-04-rooted-completion-certificates/MANUSCRIPT_V2.md'],
   'addendum':'papers/orion-04-rooted-completion-certificates/PUBLICATION_FREEZE_ADDENDUM_V1.md',
   'terminal':'ORION_04_CURRENT_EARNED_STRUCTURAL_SCIENCE_AND_CONTENT_FROZEN__EXACT_D4_SUCCESSOR_ONLY'},
}
def req(x,m):
    if not x: raise AssertionError(m)
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def blob(path:str)->str: return git('hash-object',str(ROOT/path))
def sha256(path:str)->str: return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def asset(path:str)->dict:
    p=ROOT/path; req(p.is_file(),f'missing content asset {path}')
    return {'path':path,'git_blob':blob(path),'sha256':sha256(path),'bytes':p.stat().st_size}
def main():
    status=json.loads(STATUS_PATH.read_text())
    req(status['terminal']=='ORION_01_05_CONVERGENCE_V1_EVIDENCE_BOUND__SCIENCE_CLOSURE_OPEN__SUBMISSION_NOT_YET_AUTHORIZED','convergence terminal drift')
    req(not any(status['global_authority'].values()),'global authority unexpectedly promoted')
    status_blob=blob(str(STATUS_PATH.relative_to(ROOT)))
    for paper_id,cfg in PAPERS.items():
        p=status['papers'][paper_id]
        req(p['science_status']=='OPEN',f'{paper_id} source convergence status changed')
        req(p['established_scope'],f'{paper_id} has no established scope to freeze')
        req(p['open_science_gates'],f'{paper_id} successor gates missing')
        authority=p['authority']
        for key in ('production_authority_established','external_independence_established','novelty_authority_established','journal_authority_established','submission_authorized'):
            if key in authority: req(authority[key] is False,f'{paper_id} unexpected authority {key}')
        ledgers=[]
        for row in p['claim_ledgers']:
            path=row['path']; a=asset(path)
            req(a['git_blob']==row['baseline_blob'],f'{paper_id} claim ledger blob drift {path}')
            req(a['sha256']==row['sha256'],f'{paper_id} claim ledger sha drift {path}')
            a['claim_dispositions']=row['claim_dispositions']; ledgers.append(a)
        content=[asset(x) for x in cfg['manuscripts']]+[asset(cfg['addendum'])]
        add=(ROOT/cfg['addendum']).read_text().lower()
        req('successor' in add and 'frozen' in add,f'{paper_id} addendum lacks successor/frozen semantics')
        req('submission authority' in add,f'{paper_id} addendum lacks submission boundary')
        extra={}
        if paper_id=='ORION-01':
            values={r['value'] for r in p['evidence_status']['preserved_records']}
            req('FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED' in values,'ORION-01 adverse production result missing')
        elif paper_id=='ORION-02':
            values={r['value'] for r in p['evidence_status']['preserved_records']}
            for v in ('FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE','VALID_WITHOUT_COVERAGE_OR_VALUE'):
                req(v in values,f'ORION-02 binding adverse result missing {v}')
        elif paper_id=='ORION-03':
            req(authority.get('bounded_internal_first_mixing_theorem') is True,'ORION-03 bounded theorem authority missing')
            req(authority.get('external_domain_validation_established') is False,'ORION-03 external boundary drift')
        elif paper_id=='ORION-04':
            audit_path='papers/orion-04-rooted-completion-certificates/evidence/convergence-v1/NQ_PR1472_EXACT_SUBJECT_AUDIT_V2.json'
            audit=json.loads((ROOT/audit_path).read_text())
            req(audit['terminal']=='NQ_PR1472_NOT_FULL_REPLAY_AUTHORITY','ORION-04 exact-subject audit terminal drift')
            req(audit['authority']['D4_authority'] is False and audit['authority']['D2_D3_numerical_authority'] is False,'ORION-04 numerical authority unexpectedly promoted')
            req(audit['gates']['full_census_executed_true'] is False,'ORION-04 full census unexpectedly claimed')
            extra['exact_subject_audit']=asset(audit_path)
            extra['exact_subject_terminal']=audit['terminal']
        receipt={
          'schema':'ORION.Remaining11.ScienceContentFreeze.v1','paper_id':paper_id,'title':cfg['title'],'date':'2026-08-27',
          'subject_commit':git('rev-parse','HEAD'),'source_convergence_status':'OPEN','source_convergence_status_path':str(STATUS_PATH.relative_to(ROOT)),'source_convergence_status_git_blob':status_blob,
          'science_frozen':True,'paper_content_frozen':True,'freeze_semantics':'CURRENT_EARNED_CEILING_IMMUTABLE__PROMOTION_REQUIRES_EXPLICIT_SUCCESSOR_OR_THAW',
          'programme_science_closed':False,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,
          'established_scope':p['established_scope'],'successor_only_open_science_gates':p['open_science_gates'],'claim_ledgers':ledgers,'content_assets':content,
          'terminal':cfg['terminal'],**extra}
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/f'{paper_id}_SCIENCE_CONTENT_FREEZE_V1.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(cfg['terminal'])
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as e:
        print(f'ORION_01_04_SCIENCE_CONTENT_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
