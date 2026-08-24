#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'IDENTITY_PACKET_V15.json').read_text())
r=json.loads((ROOT/'PRIMARY_RECEIPT_V15.json').read_text())
assert p['provider']['archive']['sha256']=='f22aac206773e4eacdd54cf9519ffe997332a430326bdae29f4210a24efab0b4'
assert p['case']['source']['sha256']=='d6143780103217a4a562e4982f0d4c724c09d3a3e7dc146a6b42cecc3e9f1064'
assert p['case']['target']['sha256']=='e3643a6fcd237a162d120e58227df2e24e0398668c6f2428e4fea850180405cf'
assert p['case']['reference']['sha256']=='0afb0f2c9764201d91c226c5fb60d4b25425168acf6c2604fb191be906e9ec16'
assert p['same_universe_comparator']['release_sha256']=='7855c2d8efa131f012595313814a6466ad48f4e7ba26906c4f54801cd5a21f27'
assert all(p['admission_gates'][k] for k in ['exact_version_bound','rights_bound','source_hash_bound','target_hash_bound','reference_hash_bound','same_universe_comparator_identity_bound'])
assert not p['admission_gates']['prospective_execution_ready']
assert r['matcher_attempts']==r['scoring_attempts']==0
assert p['claim_boundary']['performance']==p['claim_boundary']['superiority']=='CANNOT_CHECK'
print('P3_V15_PROVIDER_NATIVE_IDENTITY_PACKET_PASS')
