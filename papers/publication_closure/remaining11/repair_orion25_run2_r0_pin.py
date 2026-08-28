#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
AUTH=ROOT/'papers/orion-25-orion-research-harness/P15_ACTIVE_CLAIM_AUTHORITY_V3.json'
BUILDER=ROOT/'src/orion/study/p15/active_claim_authority.py'
RUN2=ROOT/'papers/orion-25-orion-research-harness/top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2_RUN2.md'
SUMS=ROOT/'papers/orion-25-orion-research-harness/SHA256SUMS'
OUT=ROOT/'papers/publication_closure/receipts/remaining11/ORION-25_RUN2_R0_REPIN_V1.json'
OLD_BLOB='61ca00bba4fefdc9213a7830d3eeaf16b6577f69'; NEW_BLOB='fb2a3fbab8bdab7bb8bc5b627593d4848e8752dc'
PRE='8f250fc3e55d6d6a28fb1fb33d9932ef1a8760b5'
OLD_PATH='papers/paper-15-orion-research-harness/top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2_RUN2.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
 b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def req(x,m):
 if not x:raise AssertionError(m)
def main():
 req(blob(RUN2)==NEW_BLOB,'live run2 blob drift')
 old=subprocess.check_output(['git','-C',str(ROOT),'show',f'{PRE}:{OLD_PATH}'])
 req(hashlib.sha1(f'blob {len(old)}\0'.encode()+old).hexdigest()==OLD_BLOB,'historical blob drift')
 # R0 changed canonical paper identity text from P15 to ORION-25 and no science endpoints.
 normalized=RUN2.read_text().replace('ORION-25','P15').encode()
 req(normalized==old,'run2 differs beyond exact R0 identity rebind')
 a=json.loads(AUTH.read_text()); row=a['result_authority']['attestation_composition_v2']['deterministic_replay']
 req(row['git_blob_sha']==OLD_BLOB,'authority old run2 pin unexpected'); row['git_blob_sha']=NEW_BLOB
 AUTH.write_text(json.dumps(a,indent=2,sort_keys=True)+'\n')
 text=BUILDER.read_text(); oldline=f'ATTESTATION_RUN2_RECEIPT_BLOB_SHA = "{OLD_BLOB}"'; newline=f'ATTESTATION_RUN2_RECEIPT_BLOB_SHA = "{NEW_BLOB}"'
 req(text.count(oldline)==1,'builder old constant unexpected'); BUILDER.write_text(text.replace(oldline,newline))
 # Re-pin only the changed authority row in the candidate checksum file.
 auth_rel=str(AUTH.relative_to(ROOT)); lines=SUMS.read_text().splitlines(); hits=0; out=[]
 for line in lines:
  if line.strip().endswith('  '+auth_rel): out.append(f'{sha(AUTH)}  {auth_rel}'); hits+=1
  else: out.append(line)
 req(hits==1,'authority checksum row cardinality'); SUMS.write_text('\n'.join(out)+'\n')
 rec={'schema':'ORION.CustodyRepin.v1','paper_id':'ORION-25','date':'2026-08-27','old_run2_blob':OLD_BLOB,'new_run2_blob':NEW_BLOB,'proof':'current run2 with ORION-25→P15 is byte-identical to pre-R0 blob','authority_sha256_after':sha(AUTH),'builder_updated':True,'scientific_verdict_changed':False,'terminal':'ORION_25_RUN2_R0_PIN_REPAIRED'}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n'); print(rec['terminal'])
if __name__=='__main__':
 try:main()
 except AssertionError as e:print(f'ORION25_RUN2_REPIN=FAIL: {e}',file=sys.stderr);raise SystemExit(2)
