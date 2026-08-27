#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'papers/orion-20-structured-problem-solving'
FORMAL=P/'top_tier/P10_OCME_FORMAL_RESULT_RECEIPT_V1.md'
GENERATED=P/'top_tier/P10_GENERATED_OCME_RESULT_RECEIPT_V1.md'
ADDENDUM=P/'top_tier/P10_OCME_MANUSCRIPT_ADDENDUM_V1.md'
OUT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-20_SCIENCE_FREEZE_V1.json'
TERMINAL='ORION_20_BOUNDED_OCME_SCIENCE_FROZEN__NATIVE_PROMOTION_PENDING'
def req(x,m):
    if not x: raise AssertionError(m)
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def blob(p): return git('hash-object',str(p))
def main():
    f=FORMAL.read_text(); g=GENERATED.read_text(); a=ADDENDUM.read_text()
    for tok in ('P10_OCME_FORMAL_NONVACUITY_V1_GREEN','P10_OCME_FORMAL_SECOND_INDEPENDENT_CHECKER_GREEN','false expansion count is `0`'):
        req(tok in f,f'formal receipt missing {tok}')
    for tok in ('P10_GENERATED_OCME_V1_SUPPORTED','P10_GENERATED_OCME_SECOND_INDEPENDENT_CHECKER_GREEN','6/6','false expansions on known-method controls: `0`','ORIGIN_ONLY__HELD_OUT_OPENED_AFTER_SELECTION'):
        req(tok in g,f'generated receipt missing {tok}')
    lower=a.lower()
    req('generated finite ocme' in lower,'manuscript addendum missing generated finite OCME')
    req('may not state that it has established unrestricted autonomous mathematical invention' in lower,'manuscript addendum missing unrestricted-autonomy boundary')
    req('donor' in lower,'manuscript addendum missing donor boundary')
    row={'schema':'ORION.Remaining11.ScienceFreeze.v1','paper_id':'ORION-20','title':'Structured Problem Solving','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'formal_receipt':str(FORMAL.relative_to(ROOT)),'formal_receipt_git_blob':blob(FORMAL),'generated_receipt':str(GENERATED.relative_to(ROOT)),'generated_receipt_git_blob':blob(GENERATED),'terminal':TERMINAL,'science_frozen':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'bounded_claim':'Exact finite OCME obstruction/expansion in two registered finite method-language settings, including prospectively generated outside-closure selections with 6/6 held-out transfer and zero false expansion.','remaining_top_tier_work':['native donor-complete theorem-proving/search/repair/retrieval/synthesis/evolution first refusal','native obstruction certificates','protected post-expansion transfer in native systems','final current nearest-work and package binding'],'boundary':'Candidate grammars and composition templates were prospectively supplied; no unrestricted autonomous method invention or native-system superiority is claimed.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');print(TERMINAL);return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as e: print(f'ORION_20_SCIENCE_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
