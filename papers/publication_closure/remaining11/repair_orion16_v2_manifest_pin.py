#!/usr/bin/env python3
"""Repair exactly one stale ORION-16 V2 content-manifest pin.

The V1 manifest was sanctioned-regenerated after #1494 to restore a truthful
BOUND subject identity. V2 retained the pre-regeneration SHA. This script
permits only that known one-row re-pin and the outer checksum update.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'papers/orion-16-formal-epistemic-structures-and-mechanics'
V1=P/'CONTENT_MANIFEST_V1.json'; V2=P/'CONTENT_MANIFEST_V2.json'; SUMS=P/'content_binding_v2/SHA256SUMS'
OUT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-16_V2_MANIFEST_REPIN_V1.json'
TARGET='papers/orion-16-formal-epistemic-structures-and-mechanics/CONTENT_MANIFEST_V1.json'
OLD='d5b521c0a75f4c2f8eeb8139be514bb02b8cf9cb0780fa0a04b13366e32a1638'
AUDITED_CURRENT='7b7266af57c8b4df22c7ad5b299def1d9c49af3e56b83dbfde14e4f66ad11947'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(x,m):
 if not x: raise AssertionError(m)
def main():
 req(sha(V1)==AUDITED_CURRENT,f'V1 bytes changed since complete drift audit: {sha(V1)}')
 v2=json.loads(V2.read_text())
 rows=[r for r in v2['bound_files'] if r['path']==TARGET]
 req(len(rows)==1,'target V1 row cardinality')
 req(rows[0]['sha256']==OLD,f'unexpected existing V1 pin: {rows[0]["sha256"]}')
 rows[0]['sha256']=AUDITED_CURRENT
 V2.write_text(json.dumps(v2,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 v2sha=sha(V2)
 SUMS.write_text(f'{v2sha}  {V2.relative_to(ROOT)}\n',encoding='utf-8')
 rec={'schema':'ORION.CustodyRepin.v1','paper_id':'ORION-16','date':'2026-08-27','target':TARGET,'old_sha256':OLD,'new_sha256':AUDITED_CURRENT,'v2_manifest_sha256_after':v2sha,'outer_checksum_sha256':sha(SUMS),'scientific_verdict_changed':False,'reason':'Sanctioned post-#1494 CONTENT_MANIFEST_V1 regeneration restored a truthful BOUND subject identity; CONTENT_MANIFEST_V2 retained the prior V1 byte digest. Complete drift audit found no other V2 bound-file mismatch.','terminal':'ORION_16_V2_SINGLE_PIN_REPAIRED'}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n'); print(rec['terminal'])
if __name__=='__main__':
 try: main()
 except AssertionError as e: print(f'ORION16_V2_REPIN=FAIL: {e}',file=sys.stderr); raise SystemExit(2)
