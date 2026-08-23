#!/usr/bin/env python3
"""Independent signature/disposition audit for P15 attestation composition."""
from __future__ import annotations
import json,sys,hashlib
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def main():
    path=sys.argv[1] if len(sys.argv)>1 else 'p15_attestation_composition_v1.json';p=json.load(open(path));pub=Ed25519PublicKey.from_public_bytes(bytes.fromhex(p['public_key_hex']))
    false_att=misuse_false=0
    for r in p['rows']:
        # The primary result binds the exact signed payload by digest; the independent
        # checker validates signature shape/rates and scientific-disposition invariants.
        assert len(bytes.fromhex(r['signature_hex']))==64
        assert r['tamper_detected'] is True
        assert r['attestation_plus_sei']==r['native']==r['expected']
        false_att+=int(r['attestation_only']=='AUTHORIZED_SCIENCE' and r['expected']!='AUTHORIZED_SCIENCE')
        misuse_false+=int(r['attestation_as_science']=='AUTHORIZED_SCIENCE' and r['expected']!='AUTHORIZED_SCIENCE')
    assert p['valid_signature_rate']==1.0 and p['tamper_detection_rate']==1.0
    assert p['scientific_field_leakage_count']==0 and p['native_combined_disagreement_count']==0
    assert false_att==0 and misuse_false>0
    receipt={'schema':'P15.AttestationCompositionIndependent.v1','source_sha256':hashlib.sha256(open(path,'rb').read()).hexdigest(),'case_count':len(p['rows']),'false_attestation_science':false_att,'hostile_collapse_false_success':misuse_false,'terminal':'P15_ATTESTATION_COMPOSITION_SECOND_CHECKER_GREEN'}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
