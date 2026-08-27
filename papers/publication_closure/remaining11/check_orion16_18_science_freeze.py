#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'papers/publication_closure/receipts/remaining11'

def req(x,m):
    if not x: raise AssertionError(m)
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def blob(p): return git('hash-object',str(p))
def freeze16():
    p=ROOT/'papers/orion-16-formal-epistemic-structures-and-mechanics'
    r=p/'top_tier/P6_REAL_TRANSITION_AUDIT_RESULT_RECEIPT_V1.md'; t=r.read_text(); m=(p/'manuscript/FINAL_V5.md').read_text()
    for tok in ('P6_REAL_TRANSITION_AUDIT_V1_SUPPORTED','P6_REAL_TRANSITION_AUDIT_SECOND_INDEPENDENT_CHECKER_GREEN','16','4 real-domain families','0 unnecessary reopen'):
        req(tok in t,f'ORION-16 result token missing: {tok}')
    for tok in ('61,440','51,712','withdraw','tautolog'):
        req(tok.lower() in m.lower(),f'ORION-16 repaired-manuscript boundary missing: {tok}')
    return {'schema':'ORION.Remaining11.ScienceFreeze.v1','paper_id':'ORION-16','title':'Formal Epistemic Structures and Mechanics','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'result_receipt':str(r.relative_to(ROOT)),'result_receipt_git_blob':blob(r),'terminal':'ORION_16_BOUNDED_SCIENCE_FROZEN__REAL_SYSTEM_PROMOTION_PENDING','science_frozen':True,'top_tier_ready':False,'submission_authority':False,'bounded_claim':'Repaired finite ETS theory plus the frozen 16-case/4-family real transition audit at its explicit scope.','remaining_top_tier_work':['donor-complete real transition-system first refusal','general reopening/restoration semantics','final current donor/nearest-work refresh'],'boundary':'No universal real-system law or top-tier authority is granted.'}
def freeze18():
    p=ROOT/'papers/orion-18-epistemic-authority-autonomous-science'
    r=p/'top_tier/P8_REAL_EVIDENCE_DISCHARGE_RESULT_RECEIPT_V1.md'; t=r.read_text()
    for tok in ('P8_REAL_EVIDENCE_DISCHARGE_V1_SUPPORTED','P8_REAL_EVIDENCE_DISCHARGE_SECOND_INDEPENDENT_CHECKER_GREEN','20','4-domain','zero false promotions'):
        req(tok.lower() in t.lower(),f'ORION-18 result token missing: {tok}')
    return {'schema':'ORION.Remaining11.ScienceFreeze.v1','paper_id':'ORION-18','title':'Epistemic Authority in Autonomous Science','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'result_receipt':str(r.relative_to(ROOT)),'result_receipt_git_blob':blob(r),'terminal':'ORION_18_BOUNDED_SCIENCE_FROZEN__GENERAL_AUTHORITY_PROMOTION_PENDING','science_frozen':True,'top_tier_ready':False,'submission_authority':False,'bounded_claim':'Bounded scientific-authorization theory plus the frozen 20-case/4-domain real evidence-discharge study with zero false promotions.','remaining_top_tier_work':['sound donor-composition to general-calculus interpretation','real integrated authorization/evidence donor','independent scientific adjudication'],'boundary':'No autonomous scientific authority in the wild or general authority calculus is claimed.'}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for row in (freeze16(),freeze18()):
        (OUT/f"{row['paper_id']}_SCIENCE_FREEZE_V1.json").write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
        print(row['terminal'])
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as e: print(f'ORION_16_18_SCIENCE_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
