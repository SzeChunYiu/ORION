#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; D='papers/orion-02-fiberguard-finite-fibre'; P=ROOT/D
C=P/'rounds/r22-proposal-ordering/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_CUSTODY.json'; R=P/'rounds/r22-proposal-ordering/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_RESULTS.json'; V=P/'rounds/r22-proposal-ordering/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_VERIFICATION.txt'; M=P/'MANUSCRIPT_V2.md'; LED=P/'CLAIM_LEDGER_R2.md'; OUT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-02_SCIENCE_CONTENT_FREEZE_V1.json'; TERM='ORION_02_FINITE_FIBRE_SCIENCE_AND_NEGATIVE_R22_CONTENT_FROZEN'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def req(x,m):
 if not x:raise AssertionError(m)
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def main():
 c=json.loads(C.read_text()); r=json.loads(R.read_text()); v=V.read_text()
 req(c['schema']=='ORION.FiberGuard.PMLBProposalOrdering.R22.Custody.v1','custody schema'); req(c['execution']['terminal']=='C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE','terminal'); req(c['execution']['byte_identical_complete_runs']==2,'two runs'); req(c['authority']['scientific_authority_delta']=='NONE' and c['authority']['top_tier_gate_pass'] is False and c['authority']['freeze_authorized'] is False,'authority boundary'); req(c['authority']['original_negative_must_remain_visible'] is True,'negative retention'); req(c['measured_boundary']['n_evaluations']==44 and c['measured_boundary']['primary_tau_full_state']==0.0,'measured boundary'); req(sha(R)==c['execution']['result_sha256'],'result hash'); req('VERIFY_OK' in v and '[PASS] terminal independently re-derived' in v and '[PASS] policy replay (88 decisions)' in v,'verification log'); req(M.is_file() and LED.is_file(),'paper surfaces')
 tree=git('rev-parse',f'HEAD:{D}'); rec={'schema':'ORION.PaperScienceContentFreeze.v1','paper_id':'ORION-02','title':'FiberGuard Finite Fibre','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'paper_directory':D,'paper_tree_oid':tree,'claim_ledger':str(LED.relative_to(ROOT)),'claim_ledger_sha256':sha(LED),'manuscript':str(M.relative_to(ROOT)),'manuscript_sha256':sha(M),'r22_custody':str(C.relative_to(ROOT)),'r22_custody_sha256':sha(C),'r22_terminal':c['execution']['terminal'],'r22_result_sha256':sha(R),'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,'terminal':TERM,'boundary':'Complete finite-fibre theory and prior bounded FiberGuard evidence are frozen together with the prospectively executed R22 PMLB negative: no certified coverage (tau_full_state=0.0). R22 grants no authority delta. Future coverage/value or external-replay science requires a successor and the negative remains immutable.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');print(TERM)
if __name__=='__main__':
 try:main()
 except AssertionError as e:print(f'ORION02_FINAL_FREEZE=FAIL: {e}',file=sys.stderr);raise SystemExit(2)
