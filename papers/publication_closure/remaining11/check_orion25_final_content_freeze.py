#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
D='papers/orion-25-orion-research-harness'; P=ROOT/D
A=P/'P15_ACTIVE_CLAIM_AUTHORITY_V3.json'; M=P/'MANUSCRIPT.md'; OUT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-25_SCIENCE_CONTENT_FREEZE_V1.json'
TERM='ORION_25_BOUNDED_SCIENCE_AND_PAPER_CONTENT_FROZEN'
def req(x,m):
 if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def main():
 a=json.loads(A.read_text())
 req(a['schema']=='ORION.P15.ActiveClaimAuthority.v3','authority schema')
 req(a['active_terminal']=='P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED','terminal')
 req(a['scientific_result_state']=='BOUNDED_EMPIRICAL_SUPPORTED','result state')
 req(a['promotion_allowed'] is False,'promotion boundary')
 expected={'sei_false_authorized_science':0,'provenance_round_trip_rate':1.0,'provenance_scientific_field_leakage':0,'attestation_base_chain_verification_rate':1.0,'attestation_non_compromise_attack_detection_complete':True,'attestation_valid_workload_false_rejections':0,'attestation_chain_plus_sei_gold_agreement':'22/22','full_key_compromise_signature_detections':0,'full_key_compromise_false_promotions':6}
 req(a['bounded_findings']==expected,'bounded findings')
 req({'SIGNATURE_PROVES_SCIENTIFIC_TRUTH','KEY_CUSTODY_VERIFIED','UNIVERSAL_EXECUTION_CORRECTNESS','PRODUCTION_SCALE_VALIDATED','SUPERIORITY_SUPPORTED','EXTERNAL_VALIDATION_COMPLETE','TOP_TIER_SUBMISSION_READY'}<=set(a['forbidden_states']),'forbidden states')
 bindings=[]
 for name,row in a['result_authority'].items():
  path=ROOT/row['artifact']; req(path.is_file(),f'missing {name}'); blob=git('rev-parse',f"HEAD:{row['artifact']}"); req(blob==row['git_blob_sha'],f'blob drift {name}'); bindings.append({'name':name,'artifact':row['artifact'],'git_blob_sha':blob})
  if name=='attestation_composition_v2':
   rr=row['deterministic_replay']; rp=ROOT/rr['artifact']; req(rp.is_file(),'run2 missing'); req(git('rev-parse',f"HEAD:{rr['artifact']}")==rr['git_blob_sha'],'run2 blob')
 req(M.is_file() and M.stat().st_size>10000,'manuscript')
 tree=git('rev-parse',f'HEAD:{D}')
 rec={'schema':'ORION.PaperScienceContentFreeze.v1','paper_id':'ORION-25','title':'Scientific Execution Integrity','date':'2026-08-27','subject_commit':git('rev-parse','HEAD'),'paper_directory':D,'paper_tree_oid':tree,'active_authority':str(A.relative_to(ROOT)),'active_authority_git_blob':git('rev-parse',f'HEAD:{A.relative_to(ROOT)}'),'active_authority_sha256':sha(A),'result_authority':bindings,'bounded_findings':expected,'science_frozen':True,'paper_content_frozen':True,'successor_required_for_future_science':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,'external_peer_review_claimed':False,'terminal':TERM,'boundary':a['full_key_compromise_boundary']+' '+a['authorized_claim'],'successor_only_work':a['remaining_external_requirements'],'supersedes_stale_science_receipt':'papers/publication_closure/receipts/remaining11/ORION-25_SCIENCE_FREEZE_V1.json','supersession_reason':'Merged R0 pin-layer repair changed living authority bytes without changing the scientific terminal; this receipt binds the current V3 authority and whole canonical paper tree.'}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n'); print(TERM)
if __name__=='__main__':
 try: main()
 except AssertionError as e: print(f'ORION_25_FINAL_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
