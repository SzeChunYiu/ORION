#!/usr/bin/env python3
"""Freeze ORION-25 at its current bounded SEI/provenance/attestation result."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'papers/orion-25-orion-research-harness'
AUTH=P/'P15_ACTIVE_CLAIM_AUTHORITY_V3.json'
README=P/'README.md'
RECEIPT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-25_SCIENCE_FREEZE_V1.json'
TERMINAL='ORION_25_BOUNDED_SCIENCE_FROZEN__PRODUCTION_PROMOTION_PENDING'

def req(x,m):
    if not x: raise AssertionError(m)
def git(*a): return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def blob(path): return git('hash-object',str(path))

def main():
    a=json.loads(AUTH.read_text())
    req(a['schema']=='ORION.P15.ActiveClaimAuthority.v3','authority schema')
    req(a['active_terminal']=='P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED','active terminal')
    req(a['lifecycle_state']=='BOUNDED_SCIENTIFIC_RESULT_EARNED','lifecycle state')
    req(a['scientific_result_state']=='BOUNDED_EMPIRICAL_SUPPORTED','science state')
    req(a['promotion_allowed'] is False,'top-tier promotion must remain false')
    for _,row in a['result_authority'].items():
        p=ROOT/row['artifact']; req(p.is_file(),f'missing {p}'); req(blob(p)==row['git_blob_sha'],f'blob drift {p}')
        if 'deterministic_replay' in row:
            r=row['deterministic_replay']; rp=ROOT/r['artifact']; req(rp.is_file(),f'missing {rp}'); req(blob(rp)==r['git_blob_sha'],f'blob drift {rp}')
    b=a['bounded_findings']
    req(b['sei_false_authorized_science']==0,'SEI false promotion drift')
    req(b['provenance_round_trip_rate']==1.0 and b['provenance_scientific_field_leakage']==0,'provenance boundary drift')
    req(b['attestation_chain_plus_sei_gold_agreement']=='22/22','attestation agreement drift')
    req(b['attestation_valid_workload_false_rejections']==0,'false rejection drift')
    req(b['full_key_compromise_signature_detections']==0 and b['full_key_compromise_false_promotions']==6,'key compromise negative drift')
    forb=set(a['forbidden_states']); req({'SIGNATURE_PROVES_SCIENTIFIC_TRUTH','PRODUCTION_SCALE_VALIDATED','TOP_TIER_SUBMISSION_READY'}<=forb,'forbidden states incomplete')
    t=README.read_text();
    for token in ('22-case','0/6','CANNOT_CHECK','PRODUCTION_COMPARATORS_PENDING'):
        req(token in t,f'README boundary missing {token}')
    receipt={
      'schema':'ORION.Remaining11.ScienceFreeze.v1','paper_id':'ORION-25','title':'Scientific Execution Integrity','date':'2026-08-27',
      'subject_commit':git('rev-parse','HEAD'),'active_authority':str(AUTH.relative_to(ROOT)),'active_authority_git_blob':blob(AUTH),
      'terminal':TERMINAL,'science_frozen':True,'top_tier_ready':False,'journal_authority':False,'submission_authority':False,
      'bounded_findings':b,'full_key_compromise_boundary':a['full_key_compromise_boundary'],
      'remaining_top_tier_work':a['remaining_external_requirements'],
      'boundary':'Freeze covers only the registered 18-case SEI plus 22-case provenance/attestation studies; signatures do not establish key custody, fact truth, scientific validity, or production-scale reliability.'}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(TERMINAL); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as e: print(f'ORION_25_SCIENCE_FREEZE=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
