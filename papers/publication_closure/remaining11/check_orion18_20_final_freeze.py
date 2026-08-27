#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; O=ROOT/'papers/publication_closure/receipts/remaining11'
CFG={
 'ORION-18':('papers/orion-18-epistemic-authority-autonomous-science','ORION-18_SCIENCE_FREEZE_V1.json','ORION_18_BOUNDED_SCIENCE_AND_PAPER_CONTENT_FROZEN'),
 'ORION-20':('papers/orion-20-structured-problem-solving','ORION-20_SCIENCE_FREEZE_V1.json','ORION_20_BOUNDED_OCME_SCIENCE_AND_PAPER_CONTENT_FROZEN')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def req(x,m):
 if not x:raise AssertionError(m)
def main():
 for pid,(d,sname,term) in CFG.items():
  s=O/sname; x=json.loads(s.read_text()); req(x['science_frozen'] is True and x['submission_authority'] is False,pid+' science boundary')
  if pid=='ORION-18':
   p=ROOT/x['result_receipt'];req(p.is_file(),pid+' result');req(git('rev-parse',f"HEAD:{x['result_receipt']}")==x['result_receipt_git_blob'],pid+' result blob')
  else:
   for k in ('formal','generated'):
    pth=x[k+'_receipt'];req(git('rev-parse',f'HEAD:{pth}')==x[k+'_receipt_git_blob'],pid+' '+k+' blob')
  rec={'schema':'ORION.PaperScienceContentFreeze.v1','paper_id':pid,'title':x['title'],'date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'paper_directory':d,'paper_tree_oid':git('rev-parse',f'HEAD:{d}'),'science_receipt':str(s.relative_to(ROOT)),'science_receipt_sha256':sha(s),'science_terminal':x['terminal'],'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,'terminal':term,'boundary':x['boundary'],'successor_only_work':x['remaining_top_tier_work'],'claude_freeze_lane_repair_integrated':True}
  (O/f'{pid}_SCIENCE_CONTENT_FREEZE_V1.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');print(term)
if __name__=='__main__':
 try:main()
 except AssertionError as e:print('ORION18_20_FREEZE=FAIL:',e,file=sys.stderr);raise SystemExit(2)
