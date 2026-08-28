#!/usr/bin/env python3
"""Fail-closed whole-tree bounded science/content freeze for ORION-17/19/22/23."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STATUS=ROOT/'papers/TOP_TIER_PROMOTION_STATUS_V1.md'
OUTDIR=ROOT/'papers/publication_closure/receipts/remaining11'
PAPERS={
 'ORION-17':{
  'title':'Epistemic Navigation in Open Worlds','dir':'papers/orion-17-epistemic-navigation-open-worlds',
  'must':['three executed non-synthetic change classes','witness-aware 1.0','THREE_CLASS_REAL_REGIME_TRANSPORT_EARNED__EXTERNAL_PROMOTION_PENDING'],
  'terminal':'ORION_17_THREE_CLASS_REGIME_TRANSPORT_SCIENCE_AND_CONTENT_FROZEN',
  'boundary':'T7.1–T7.3 plus three non-synthetic change classes only; arbitrary scientific-regime transport, stronger external donor/lens authority and target-ambiguity generalization require a successor.'},
 'ORION-19':{
  'title':'Structured Epistemic Learning','dir':'papers/orion-19-structured-epistemic-learning',
  'must':['wine null','Qwen scaling negative','causal diagnostic 4/5 vs 1/5 generic compute','SURVIVES_FULL_ACCOUNTING'],
  'terminal':'ORION_19_ACCOUNTED_CAUSAL_DIAGNOSTIC_SCIENCE_AND_CONTENT_FROZEN',
  'boundary':'Current real-data positives, Wine null, Qwen negative and fully accounted causal diagnostic are frozen jointly; transferable crossover laws and hostile representation/format generality require a successor.'},
 'ORION-22':{
  'title':'Adaptive State Reasoning','dir':'papers/orion-22-adaptive-state-reasoning',
  'must':['SAT/path/knapsack: 9/9 zero-regret','one identical rule','complete resource vectors'],
  'terminal':'ORION_22_UNCHANGED_ALLOCATOR_TRANSFER_SCIENCE_AND_CONTENT_FROZEN',
  'boundary':'Unchanged allocator transfer across the registered SAT/path/knapsack panel is frozen; robustness under changed resource prices, task shifts and hidden parameters requires a successor.'},
 'ORION-23':{
  'title':'Responsibility-Carrying State','dir':'papers/orion-23-responsibility-carrying-state',
  'must':['transport 60/60 with 0 unsound / 0 needless','donor-complete D2 baseline','drift-bounded certificate transport'],
  'terminal':'ORION_23_RESPONSIBILITY_SAFE_TRANSPORT_SCIENCE_AND_CONTENT_FROZEN',
  'boundary':'Current digits/CNF responsibility shifts, D2 donor and 60/60 drift-bounded transport are frozen; real-workflow authority and richer semantic drift require a successor if claimed.'},
}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def req(x:bool,m:str)->None:
 if not x: raise AssertionError(m)
def git(*a:str)->str:return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()

def main()->int:
 text=STATUS.read_text(encoding='utf-8'); status_sha=sha(STATUS); subject=git('rev-parse','HEAD'); OUTDIR.mkdir(parents=True,exist_ok=True)
 req('still-unearned broad external authority' in text,'promotion authority distinction missing')
 for pid,cfg in PAPERS.items():
  for token in cfg['must']: req(token in text,f'{pid} earned-state token missing: {token}')
  d=ROOT/cfg['dir']; req(d.is_dir(),f'{pid} dir'); tree=git('rev-parse',f"HEAD:{cfg['dir']}"); req(len(tree)==40,f'{pid} tree')
  receipt={
   'schema':'ORION.PaperScienceContentFreeze.v1','paper_id':pid,'title':cfg['title'],'date':'2026-08-27','subject_commit':subject,
   'paper_directory':cfg['dir'],'paper_tree_oid':tree,'controlling_promotion_status':str(STATUS.relative_to(ROOT)),'controlling_promotion_status_sha256':status_sha,
   'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,'top_tier_ready':False,
   'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,'terminal':cfg['terminal'],'boundary':cfg['boundary'],
   'reopen_rule':'The higher promotion target is not part of this current-version freeze. New breadth must be an explicit successor and must retain all null/adverse/CANNOT_CHECK evidence.'}
  out=OUTDIR/f'{pid}_SCIENCE_CONTENT_FREEZE_V1.json'; out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(cfg['terminal'])
 return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except AssertionError as e:
  print(f'ORION_17_19_22_23_FINAL_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
