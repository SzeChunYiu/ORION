#!/usr/bin/env python3
"""Freeze ORION-15 scoped architecture and ORION-24 controlled conformance."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'papers/publication_closure/receipts/remaining11'
def req(x,m):
    if not x: raise AssertionError(m)
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def asset(path:str)->dict:
    p=ROOT/path;req(p.is_file(),f'missing {path}')
    return {'path':path,'git_blob':git('hash-object',str(p)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def freeze15():
    base='papers/orion-15-self-orion/'
    scoped=(ROOT/(base+'SCOPED_PUBLICATION_TRACK_V1.md')).read_text()
    ready=(ROOT/(base+'JOURNAL_READINESS.md')).read_text()
    report=json.loads((ROOT/(base+'evidence/glm-5.2-attribution/report.json')).read_text())
    conf_path='research/self-orion-v3/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json'
    conf=json.loads((ROOT/conf_path).read_text())
    req('SCOPED_NON_SELF_PROMOTION_TRACK_SELECTED' in scoped,'ORION-15 scoped track not selected')
    req('NO_TERMINAL_UNDER_FROZEN_RULES' in ready,'ORION-15 readiness terminal drift')
    req('No baseline or ablation arm has been executed' in ready,'ORION-15 absent-baseline disclosure drift')
    m=report['metrics'];req((m['total_cases'],m['correct_attributions'],m['incorrect_attributions'])==(24,21,3),'ORION-15 diagnostic denominator drift')
    wrong=[r['case_id'] for r in report['per_case_summary'] if not r['correct']]
    req(wrong==['P5-HC-002','P5-HC-012','P5-HC-018'],'ORION-15 retained error identities drift')
    req(conf['terminal']=='NO_TERMINAL_UNDER_FROZEN_RULES' and conf['no_frozen_terminal_fired'] is True,'ORION-15 V3 no-terminal drift')
    req(conf['decision_layer_by_policy']['FULL_T7']['correct_revision_count']==12,'ORION-15 FULL_T7 12/96 drift')
    req(conf['decision_layer_by_policy']['FULL_T7']['revision_label_accuracy']==0.125,'ORION-15 FULL_T7 rate drift')
    content=[asset(base+x) for x in ('manuscript/main.tex','manuscript/main.pdf','SCOPED_PUBLICATION_TRACK_V1.md','JOURNAL_READINESS.md','THEORY_CLAIM_LEDGER_V2.md','PUBLICATION_FREEZE_ADDENDUM_V1.md')]
    return {'schema':'ORION.Remaining11.ScienceContentFreeze.v1','paper_id':'ORION-15','title':'Self-ORION — Scoped Non-Self-Promotion Architecture','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'terminal':'ORION_15_SCOPED_NON_SELF_PROMOTION_SCIENCE_AND_CONTENT_FROZEN__PERFORMANCE_SUCCESSOR_ONLY','science_frozen':True,'paper_content_frozen':True,'top_tier_ready':False,'peer_review_ready_for_broad_self_improvement':False,'journal_authority':False,'submission_authority':False,'bounded_claim':'Fallible internal diagnosis and method proposal are structurally non-self-authorizing in the registered Self-ORION architecture; adoption remains behind protected host/evidence authority.','diagnostic_result':{'correct':21,'total':24,'incorrect':3,'wrong_case_ids':wrong},'revision_panel':{'terminal':conf['terminal'],'full_t7_correct':12,'total':96},'confirmatory_receipt':asset(conf_path),'content_assets':content,'successor_only_work':['protected V1-vs-V2 performance campaign','matched no-edit/direct-self-edit/strong self-improvement baselines','fresh held-out transfer and harmful-transfer evaluation','external evaluator/adjudication authority'],'boundary':'No self-improvement superiority or protected-transfer benefit is claimed; every missing performance cell remains CANNOT_CHECK.'}
def freeze24():
    base='papers/orion-24-orion-rse/'
    auth_path=base+'P14_ACTIVE_CLAIM_AUTHORITY_V1.json';auth=json.loads((ROOT/auth_path).read_text())
    req(auth['schema']=='ORION.P14.ActiveClaimAuthority.v1','ORION-24 authority schema drift')
    a=auth['active_claim'];req(a['status']=='SUPPORTED','ORION-24 active claim not supported')
    req(a['scientific_terminal']=='P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED','ORION-24 scientific terminal drift')
    req('28-case, seven-implementation' in a['scope'],'ORION-24 scope drift')
    req(auth['external_validity']=='OPEN','ORION-24 external validity unexpectedly promoted')
    req(auth['prospective_external_validation']['execution_authorized'] is False,'ORION-24 P14D unexpectedly authorized')
    result_path=base+a['result_artifact'];replay_path=base+a['replay_artifact']
    req(hashlib.sha256((ROOT/result_path).read_bytes()).hexdigest()==a['result_sha256'],'ORION-24 result SHA drift')
    req(hashlib.sha256((ROOT/replay_path).read_bytes()).hexdigest()==a['replay_sha256'],'ORION-24 replay SHA drift')
    hist=auth['historical_adjudicated_record'];req(hist['authority']=='NONE' and hist['disposition']=='RETAINED_GATE_ATTAINABILITY_DEFECT','ORION-24 P14A negative history drift')
    replay=json.loads((ROOT/replay_path).read_text());req(replay['authoritative_terminal']==a['scientific_terminal'],'ORION-24 replay authority terminal drift')
    req(all(replay['gates'].values()),'ORION-24 authoritative replay gates not all green')
    ready=(ROOT/(base+'PEER_REVIEW_READINESS.md')).read_text();req('READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT' in ready,'ORION-24 readiness drift')
    content=[asset(base+x) for x in ('MANUSCRIPT.md','CLAIM_EVIDENCE_LEDGER.md','PEER_REVIEW_READINESS.md','P14_ACTIVE_CLAIM_AUTHORITY_V1.json','CONTENT_MANIFEST_V1.json','PUBLICATION_FREEZE_ADDENDUM_V1.md')]
    return {'schema':'ORION.Remaining11.ScienceContentFreeze.v1','paper_id':'ORION-24','title':'ORION-RSE Controlled Governance Conformance','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'terminal':'ORION_24_CONTROLLED_GOVERNANCE_CONFORMANCE_SCIENCE_AND_CONTENT_FROZEN__EXTERNAL_VALIDITY_SUCCESSOR_ONLY','science_frozen':True,'paper_content_frozen':True,'peer_review_ready_controlled_scope':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'active_authority':asset(auth_path),'result_artifact':asset(result_path),'replay_artifact':asset(replay_path),'content_assets':content,'bounded_claim':a['scope'],'successor_only_work':['blinded realistic multi-domain research packets','matched frontier research-agent workflows','independent human/model adjudication where mechanically unavoidable','longitudinal negative-history value under genuine regime change'],'boundary':'External validity remains OPEN; controlled specification conformance is not real-science effectiveness or real-agent superiority.'}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for row in (freeze15(),freeze24()):
        (OUT/f"{row['paper_id']}_SCIENCE_CONTENT_FREEZE_V1.json").write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
        print(row['terminal'])
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as e: print(f'ORION_15_24_SCIENCE_CONTENT_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
