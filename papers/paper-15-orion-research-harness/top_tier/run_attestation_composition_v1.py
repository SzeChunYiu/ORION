#!/usr/bin/env python3
"""Execute frozen P15 Ed25519 attestation-composition study."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
HERE=Path(__file__).resolve().parent
FAULTS=HERE/'sei_fault_cases_v1.jsonl';GOLD=HERE/'sei_fault_gold_v1.json';REAL=HERE/'p15_real_workflow_receipts_v1.json';PROTOCOL=HERE/'P15_ATTESTATION_COMPOSITION_PROTOCOL_V1.md'
EXEC_FIELDS=("execution_id","occurrence_id","tool_id","input_digest","output_digest","spawn_ok","host_ok","timeout","exit_zero","output_present","output_complete","reaped","finalized_after_reap","cleanup_complete","retry_accounting_valid","invocation_match","input_digest_match","result_digest_match","occurrence_unique","fresh","coverage_complete","replay_match","lane_applicable","lane_agree")
SCI_FIELDS=("scientific_contract_available","scientific_contract_valid","claim_authority_available","claim_authority","scientific_disposition")

def execution_integrity(c): return all((c['spawn_ok'],c['host_ok'],not c['timeout'],c['exit_zero'],c['output_present'],c['output_complete'],c['reaped'],c['finalized_after_reap'],c['cleanup_complete'],c['retry_accounting_valid'],c['invocation_match'],c['input_digest_match'],c['result_digest_match'],c['occurrence_unique'],c['fresh'],c['coverage_complete']))
def sei(e,s):
    if not execution_integrity(e): return 'EXECUTION_INVALID'
    if s is None or not s['scientific_contract_available']: return 'CANNOT_CHECK'
    if not s['scientific_contract_valid']: return 'INVALID_SCIENCE'
    if not s['claim_authority_available']: return 'CANNOT_CHECK'
    if not s['claim_authority']: return 'VALID_BUT_NOT_AUTHORIZED'
    return 'AUTHORIZED_SCIENCE'
def norm_fault(c):
    x={k:c[k] for k in c if k not in SCI_FIELDS and k not in ('id','case_type')};x.update({'execution_id':f"fault:{c['id']}",'occurrence_id':f"fault:{c['id']}:1",'tool_id':'p15-sei-fault-fixture','input_digest':'sha256:'+hashlib.sha256((c['id']+':input').encode()).hexdigest(),'output_digest':'sha256:'+hashlib.sha256((c['id']+':output').encode()).hexdigest()})
    return {k:x[k] for k in EXEC_FIELDS},{k:c[k] for k in SCI_FIELDS if k in c}
def norm_real(c): return {k:c[k] for k in EXEC_FIELDS},{k:c[k] for k in SCI_FIELDS if k in c}
def canonical(e): return json.dumps({k:e[k] for k in EXEC_FIELDS},sort_keys=True,separators=(',',':')).encode()
def main():
    faults=[json.loads(x) for x in FAULTS.read_text().splitlines() if x.strip()];gold=json.loads(GOLD.read_text());real=json.loads(REAL.read_text())['receipts'];cases=[]
    for c in faults:
        e,s=norm_fault(c);cases.append(('fault',c['id'],e,s,gold[c['id']]))
    for c in real:
        e,s=norm_real(c);cases.append(('real',c['id'],e,s,c['expected_disposition']))
    seed=hashlib.sha256(b'P15-ATTESTATION-COMPOSITION-V1-TEST-KEY').digest();priv=Ed25519PrivateKey.from_private_bytes(seed);pub=priv.public_key();pubraw=pub.public_bytes(Encoding.Raw,PublicFormat.Raw)
    rows=[];tamper_ok=0;valid_ok=0;leakage=0
    for group,cid,e,s,expected in cases:
        payload=canonical(e);sig=priv.sign(payload);pub.verify(sig,payload);valid_ok+=1
        tampered=dict(e);tampered['occurrence_id']=str(tampered['occurrence_id'])+'-tampered'
        try: pub.verify(sig,canonical(tampered)); tamper=False
        except InvalidSignature: tamper=True
        tamper_ok+=int(tamper)
        signed_keys=set(json.loads(payload));leakage+=sum(k in signed_keys for k in SCI_FIELDS)
        native=sei(e,s);att_only='EXECUTION_INVALID' if not execution_integrity(e) else 'CANNOT_CHECK';misuse='AUTHORIZED_SCIENCE' if execution_integrity(e) else 'EXECUTION_INVALID';combined=sei(e,s)
        rows.append({'group':group,'id':cid,'expected':expected,'native':native,'attestation_only':att_only,'attestation_as_science':misuse,'attestation_plus_sei':combined,'payload_sha256':hashlib.sha256(payload).hexdigest(),'signature_hex':sig.hex(),'signature_bytes':len(sig),'public_key_bytes':len(pubraw),'tamper_detected':tamper})
    assert all(r['native']==r['expected'] for r in rows)
    disagreement=sum(r['attestation_plus_sei']!=r['native'] for r in rows)
    att_false=sum(r['attestation_only']=='AUTHORIZED_SCIENCE' and r['expected']!='AUTHORIZED_SCIENCE' for r in rows)
    misuse_false=sum(r['attestation_as_science']=='AUTHORIZED_SCIENCE' and r['expected']!='AUTHORIZED_SCIENCE' for r in rows)
    rr=[r for r in rows if r['group']=='real'];false_reject=sum(r['expected']=='AUTHORIZED_SCIENCE' and r['attestation_plus_sei']!='AUTHORIZED_SCIENCE' for r in rr);false_promote=sum(r['expected']!='AUTHORIZED_SCIENCE' and r['attestation_plus_sei']=='AUTHORIZED_SCIENCE' for r in rr)
    positive=(valid_ok==len(rows) and tamper_ok==len(rows) and leakage==0 and disagreement==0 and att_false==0 and misuse_false>0 and false_reject==0 and false_promote==0)
    receipt={'schema':'P15.AttestationCompositionResult.v1','protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'case_count':len(rows),'public_key_hex':pubraw.hex(),'valid_signature_rate':valid_ok/len(rows),'tamper_detection_rate':tamper_ok/len(rows),'scientific_field_leakage_count':leakage,'native_combined_disagreement_count':disagreement,'attestation_only_false_scientific_success_count':att_false,'hostile_attestation_as_science_false_success_count':misuse_false,'real_false_rejection_count':false_reject,'real_false_promotion_count':false_promote,'signature_bytes':64,'public_key_bytes':32,'rows':rows,'terminal':'P15_ATTESTATION_COMPOSITION_V1_SUPPORTED' if positive else 'P15_ATTESTATION_COMPOSITION_V1_GATE_NOT_MET'}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=='__main__':raise SystemExit(main())
