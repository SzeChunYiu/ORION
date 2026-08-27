#!/usr/bin/env python3
"""Fail-closed current-version science/content freeze for scoped ORION-15."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'papers/orion-15-self-orion'
SCOPED=P/'SCOPED_PUBLICATION_TRACK_V1.md'
READY=P/'JOURNAL_READINESS.md'
MAIN=P/'manuscript/main.tex'
PDF=P/'manuscript/main.pdf'
REPORT=P/'evidence/glm-5.2-attribution/report.json'
CONF=ROOT/'research/self-orion-v3/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json'
OUT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-15_SCIENCE_CONTENT_FREEZE_V1.json'
TERMINAL='ORION_15_SCOPED_NON_SELF_PROMOTION_SCIENCE_AND_PAPER_CONTENT_FROZEN'

def req(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()

def main():
    scoped=SCOPED.read_text(); ready=READY.read_text(); manuscript=MAIN.read_text()
    report=json.loads(REPORT.read_text()); conf=json.loads(CONF.read_text())
    req('SCOPED_NON_SELF_PROMOTION_TRACK_SELECTED' in scoped,'scoped track not selected')
    req('Fallible self-diagnosis and method proposal can be structurally non-self-authorizing' in scoped,'scoped conclusion drift')
    req('NO_TERMINAL_UNDER_FROZEN_RULES' in ready,'readiness no-terminal drift')
    req('No baseline or ablation arm has been executed' in ready,'absent baseline disclosure drift')
    m=report['metrics']
    req((m['total_cases'],m['correct_attributions'],m['incorrect_attributions'])==(24,21,3),'21/24 diagnostic drift')
    wrong=[r['case_id'] for r in report['per_case_summary'] if not r['correct']]
    req(wrong==['P5-HC-002','P5-HC-012','P5-HC-018'],'retained error identities drift')
    req(conf['terminal']=='NO_TERMINAL_UNDER_FROZEN_RULES','confirmatory terminal drift')
    req(conf['no_frozen_terminal_fired'] is True,'confirmatory no-terminal flag drift')
    full=conf['decision_layer_by_policy']['FULL_T7']
    req((full['correct_revision_count'],full['revision_label_accuracy'])==(12,0.125),'FULL_T7 12/96 drift')
    # Reader-visible manuscript must preserve the bounded interpretation.
    for token in ('Failure-Governed Evolution without Self-Promotion','scores 21/24 with three residual errors retained','does not establish\ntransferable self-improvement','none of the seven registered\nterminals fired'):
        req(token in manuscript,f'manuscript boundary missing: {token}')
    req(PDF.is_file() and PDF.stat().st_size>100000,'committed PDF missing/implausible')
    paper_dir='papers/orion-15-self-orion'
    tree=git('rev-parse',f'HEAD:{paper_dir}')
    receipt={
      'schema':'ORION.PaperScienceContentFreeze.v1',
      'paper_id':'ORION-15','title':'Minimal Method Revision under Observational Equivalence: Failure-Governed Evolution without Self-Promotion','date':'2026-08-27',
      'subject_commit':git('rev-parse','HEAD'),'paper_directory':paper_dir,'paper_tree_oid':tree,
      'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,
      'terminal':TERMINAL,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,
      'bounded_claim':'Fallible internal diagnosis and method proposal are structurally non-self-authorizing in the registered Self-ORION architecture; adoption remains behind protected host/evidence authority.',
      'diagnostic_result':{'correct':21,'total':24,'incorrect':3,'wrong_case_ids':wrong,'report_sha256':sha(REPORT)},
      'revision_panel':{'terminal':conf['terminal'],'full_t7_correct':12,'total':96,'confirmatory_receipt_sha256':sha(CONF)},
      'content_roots':{'main_tex_sha256':sha(MAIN),'main_pdf_sha256':sha(PDF),'scoped_track_sha256':sha(SCOPED),'journal_readiness_sha256':sha(READY)},
      'successor_only_work':['protected V1-vs-V2 performance campaign','matched no-edit/direct-self-edit/strong self-improvement baselines','fresh held-out transfer and harmful-transfer evaluation','external evaluator/adjudication authority when mechanically unavoidable'],
      'boundary':'No self-improvement superiority or protected-transfer benefit is claimed; missing performance cells remain CANNOT_CHECK and future performance science requires a successor version.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(TERMINAL); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as e:
        print(f'ORION_15_FINAL_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
