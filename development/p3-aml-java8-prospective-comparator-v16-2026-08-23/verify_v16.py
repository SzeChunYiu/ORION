#!/usr/bin/env python3
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'RESULT_V16.json').read_text())
p=ROOT/'AML_ALIGNMENT_V16.rdf'
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['output']['sha256']
assert len([x for x in ET.parse(p).getroot().iter() if x.tag.endswith('Cell')])==46
assert r['execution']['attempts']==1 and r['execution']['retries']==0
assert r['execution']['returncode']==0 and not r['execution']['timed_out']
assert r['comparator']['reference_alignment_argument_supplied'] is False
assert r['claim_boundary']['performance']==r['claim_boundary']['superiority']=='CANNOT_CHECK'
print('P3_V16_AML_JAVA8_PROSPECTIVE_COMPARATOR_PASS')
