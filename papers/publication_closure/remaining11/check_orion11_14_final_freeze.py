#!/usr/bin/env python3
"""Fail-closed whole-tree science/content freeze for ORION-11..14."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUTDIR=ROOT/'papers/publication_closure/receipts/remaining11'
PAPERS={
 'ORION-11':{
  'title':'Recursive Epistemic Reconstruction','dir':'papers/orion-11-recursive-epistemic-reconstruction','readiness':'JOURNAL_READINESS.md',
  'must':['bounded mechanical claim is `SUPPORTED`','NOT_SUBMISSION_READY','independent implementation','40,348','zero mismatches'],
  'terminal':'ORION_11_BOUNDED_MECHANICAL_SCIENCE_AND_PAPER_CONTENT_FROZEN',
  'boundary':'Frozen generator/mechanism result with primary and disjoint-seed independent recomputation. Model-general, naturalistic and open-ended superiority and current submission-package readiness are not authorized.'},
 'ORION-12':{
  'title':'Open-World Scientific Discovery','dir':'papers/orion-12-open-world-scientific-discovery','readiness':'JOURNAL_READINESS.md',
  'must':['ORION-12 = PEER_REVIEW_READY','External ORION-vs-baseline superiority remains `CANNOT_CHECK`','the pass gate **fails**','2.8x the reads'],
  'terminal':'ORION_12_NARROWED_METHODS_SCIENCE_AND_PAPER_CONTENT_FROZEN',
  'boundary':'Narrowed methods/critical-system-design claim only. The measured external superiority gate fails recall noninferiority/cost and remains CANNOT_CHECK; no generic retrieval or completeness superiority is claimed.'},
 'ORION-13':{
  'title':'Global Knowledge Portrait','dir':'papers/orion-13-global-knowledge-portrait','readiness':'JOURNAL_READINESS.md',
  'must':['PEER_REVIEW_READY','structured-mapping claim','false merge `0.000` vs flat canonicalization `0.1875`','raw-text end-to-end extraction superiority'],
  'terminal':'ORION_13_SCOPED_MAPPING_SCIENCE_AND_PAPER_CONTENT_FROZEN',
  'boundary':'Scoped structured-mapping/obstruction result only. Raw-text extraction superiority, universal coordinate necessity, expert-atlas adequacy, downstream answer quality and general method-learning performance remain unclaimed.'},
 'ORION-14':{
  'title':'Verified Scientific Discovery','dir':'papers/orion-14-verified-scientific-discovery','readiness':'JOURNAL_READINESS.md',
  'must':['ORION-14 = PEER_REVIEW_READY','ORION `0/360`','both `60/60`','**NOT_SUPPORTED**: both `30/30`','H3 null is retained as a null result'],
  'terminal':'ORION_14_PROTECTED_V2_SCIENCE_AND_PAPER_CONTENT_FROZEN',
  'boundary':'Protected V2 non-compensatory scientific-authority transition over the frozen campaign. H1/H2 are positive, H3 is retained NOT_SUPPORTED; external original-system execution and broader generality are not claimed.'},
}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def req(x:bool,m:str)->None:
 if not x: raise AssertionError(m)
def git(*a:str)->str:return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()

def main()->int:
 subject=git('rev-parse','HEAD'); OUTDIR.mkdir(parents=True,exist_ok=True)
 for pid,cfg in PAPERS.items():
  d=ROOT/cfg['dir']; r=d/cfg['readiness']; req(d.is_dir(),f'{pid} dir'); req(r.is_file(),f'{pid} readiness')
  text=r.read_text(encoding='utf-8')
  for token in cfg['must']: req(token in text,f'{pid} readiness boundary missing: {token}')
  tree=git('rev-parse',f"HEAD:{cfg['dir']}"); req(len(tree)==40,f'{pid} tree')
  receipt={
   'schema':'ORION.PaperScienceContentFreeze.v1','paper_id':pid,'title':cfg['title'],'date':'2026-08-27','subject_commit':subject,
   'paper_directory':cfg['dir'],'paper_tree_oid':tree,'controlling_readiness':str(r.relative_to(ROOT)),'controlling_readiness_sha256':sha(r),
   'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,'top_tier_ready':False,
   'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,'terminal':cfg['terminal'],'boundary':cfg['boundary'],
   'reopen_rule':'New scientific breadth or promotion must be an explicit successor version; null/adverse/CANNOT_CHECK evidence remains immutable.'}
  out=OUTDIR/f'{pid}_SCIENCE_CONTENT_FREEZE_V1.json'; out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(cfg['terminal'])
 return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except AssertionError as e:
  print(f'ORION_11_14_FINAL_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
