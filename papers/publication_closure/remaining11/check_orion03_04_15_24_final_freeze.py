#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; O=ROOT/'papers/publication_closure/receipts/remaining11'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def req(x,m):
 if not x:raise AssertionError(m)
def write(pid,title,d,terminal,boundary,authority,successors,extra=None):
 rec={'schema':'ORION.PaperScienceContentFreeze.v1','paper_id':pid,'title':title,'date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'paper_directory':d,'paper_tree_oid':git('rev-parse',f'HEAD:{d}'),'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,'terminal':terminal,'boundary':boundary,'controlling_authority':authority,'successor_only_work':successors}
 if extra:rec.update(extra)
 (O/f'{pid}_SCIENCE_CONTENT_FREEZE_V1.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');print(terminal)
def main():
 O.mkdir(parents=True,exist_ok=True)
 # ORION-03
 d='papers/orion-03-typed-merge-falsification'; led=ROOT/d/'CLAIM_LEDGER_R2.md'; man=ROOT/d/'MANUSCRIPT_V2.md'; t=led.read_text()
 for cid in [f'D2-C{i}' for i in range(1,8)]:req(f'| {cid} |' in t,cid)
 req('D2-C9' in t and 'OPEN; NOT CLAIMED' in t and 'D2-C10' in t and 'FORBIDDEN' in t,'ORION-03 boundaries')
 write('ORION-03','Typed Merge Falsification',d,'ORION_03_TYPED_AUTHORITY_SCIENCE_AND_PAPER_CONTENT_FROZEN','Positive finite typed-authority/retraction calculus at D2-C1..D2-C7 only. Arbitrary negation/probability/inconsistency and broad human-science usability are not claimed.',{'claim_ledger':str(led.relative_to(ROOT)),'claim_ledger_sha256':sha(led),'manuscript':str(man.relative_to(ROOT)),'manuscript_sha256':sha(man)},['claude/science-orion03-20260827 prospective external-policy study','any broader negation/probability calculus','external-domain usability authority'])
 # ORION-04
 d='papers/orion-04-rooted-completion-certificates'; led=ROOT/d/'CLAIM_LEDGER_R2.md'; man=ROOT/d/'MANUSCRIPT_V2.md'; t=led.read_text()
 for cid in [f'N2-C{i}' for i in range(1,8)]:req(f'| {cid} |' in t,cid)
 req('N2-C8' in t and 'BOUNDED COMPUTATIONAL EVIDENCE' in t and 'N2-C9' in t and 'OPEN; TOP-TIER BLOCKER' in t and 'N2-C13' in t and 'FORBIDDEN' in t,'ORION-04 boundaries')
 write('ORION-04','Rooted Completion Certificates',d,'ORION_04_ROOTED_COMPLETION_SCIENCE_AND_PAPER_CONTENT_FROZEN','Width-one corridor and structural obstruction theory N2-C1..N2-C7 are frozen. Support-through-22 is bounded computation only; exact D4, C0(31), and external replay authority remain open.',{'claim_ledger':str(led.relative_to(ROOT)),'claim_ledger_sha256':sha(led),'manuscript':str(man.relative_to(ROOT)),'manuscript_sha256':sha(man)},['claude/science-orion04-20260827 exact-replay successor','exact D4/C0(31) resolution','independent external replay'])
 # ORION-15 scoped current paper
 d='papers/orion-15-self-orion'; scoped=ROOT/d/'SCOPED_PUBLICATION_TRACK_V1.md'; ready=ROOT/d/'JOURNAL_READINESS.md'; report=ROOT/d/'evidence/glm-5.2-attribution/report.json'; v3=ROOT/'research/self-orion-v3/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json'; st=scoped.read_text(); rr=json.loads(report.read_text()); vv=json.loads(v3.read_text())
 req('SCOPED_NON_SELF_PROMOTION_TRACK_SELECTED' in st,'ORION-15 scoped track');req(rr['metrics']['correct_attributions']==21 and rr['metrics']['total_cases']==24 and rr['metrics']['incorrect_attributions']==3,'ORION-15 21/24');req(vv['frozen_rule_evaluation']['terminal']=='NO_TERMINAL_UNDER_FROZEN_RULES','ORION-15 V3 terminal')
 wrong=[x['case_id'] for x in rr['per_case_summary'] if not x['correct']];req(wrong==['P5-HC-002','P5-HC-012','P5-HC-018'],'ORION-15 errors')
 write('ORION-15','Self-ORION: Failure-Governed Evolution without Self-Promotion',d,'ORION_15_SCOPED_NON_SELF_PROMOTION_SCIENCE_AND_PAPER_CONTENT_FROZEN','Current paper freezes the structural non-self-authorizing diagnosis/proposal/adoption architecture with the 21/24 diagnostic errors retained and V3 NO_TERMINAL retained. It does not claim general self-improvement performance.',{'scoped_track':str(scoped.relative_to(ROOT)),'scoped_track_sha256':sha(scoped),'journal_readiness_sha256':sha(ready),'diagnostic_report_sha256':sha(report),'v3_receipt_sha256':sha(v3)},['claude/science-orion15-20260827 V4 performance candidate','fresh protected self-improvement campaign with immutable pre-outcome protocol custody','live-provider/general self-improvement authority'],{'v4_successor_disposition':{'branch':'claude/science-orion15-20260827','candidate_commit':'7e8e347f560f10390e7e71507a7ea01e73c5d400','current_paper_authority_delta':'NONE','reason':'Candidate execution receipt self-grants no scientific authority; independent audit found the claimed pre-outcome protocol bytes are not recoverable from the parent Git commit, so V4 is not promoted into the current paper.'}})
 # ORION-24 current controlled conformance
 d='papers/orion-24-orion-rse'; a=ROOT/d/'P14_ACTIVE_CLAIM_AUTHORITY_V1.json'; r=ROOT/d/'PEER_REVIEW_READINESS.md'; m=ROOT/d/'MANUSCRIPT.md'; x=json.loads(a.read_text()); c=x['active_claim'];req(c['status']=='SUPPORTED' and c['scientific_terminal']=='P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED','ORION-24 terminal');req('28-case, seven-implementation' in c['scope'],'ORION-24 scope');req(x['external_validity']=='OPEN','ORION-24 external boundary');req(x['prospective_external_validation']['execution_authorized'] is False,'ORION-24 P14D boundary');req('READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT' in r.read_text(),'ORION-24 readiness')
 for k in ('result_artifact','replay_artifact'):
  p=ROOT/d/c[k];req(p.is_file(),k);req(sha(p)==c[k.replace('artifact','sha256')],k+' hash')
 write('ORION-24','ORION-RSE',d,'ORION_24_CONTROLLED_GOVERNANCE_CONFORMANCE_SCIENCE_AND_CONTENT_FROZEN','Controlled specification-separated governance conformance over the frozen 28-case seven-implementation register is supported. External scientific validity and real-agent superiority remain OPEN/unexecuted.',{'active_authority':str(a.relative_to(ROOT)),'active_authority_sha256':sha(a),'peer_review_readiness_sha256':sha(r),'manuscript_sha256':sha(m)},['claude/science-orion24-20260827 / P14D external validation successor','real-agent/frontier workflow validation','longitudinal negative-history value'])
if __name__=='__main__':
 try:main()
 except AssertionError as e:print('ORION03_04_15_24_FREEZE=FAIL:',e,file=sys.stderr);raise SystemExit(2)
