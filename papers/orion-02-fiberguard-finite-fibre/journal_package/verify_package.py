#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--require-render', action='store_true')
a = p.parse_args()
root = Path(__file__).resolve().parent
m = json.loads((root/'SUBMISSION_MANIFEST.json').read_text())

def git_blob(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def fail(msg: str):
    raise SystemExit('FAIL: '+msg)

for local, key in [('SOURCE.md','canonical_source'),('CLAIM_LEDGER.md','canonical_claim_ledger')]:
    lp = root/local; cp = (root/m[key]).resolve()
    if not lp.is_file() or not cp.is_file(): fail(f'missing {local} or canonical source')
    data = lp.read_bytes(); canon = cp.read_bytes()
    if data != canon: fail(f'{local} differs from {m[key]}')
    got = git_blob(data); want = m['git_blob_sha1'][local]
    if got != want: fail(f'{local} git blob {got} != manifest {want}')
if not (root/'SOURCE.md').read_text(errors='replace').startswith('# '+m['title']): fail('title/source mismatch')
for name in ['README.md','SUBMISSION_MANIFEST.json','verify_package.py','build.sh','COMPILE.md','REPRODUCIBILITY.md','FILING_CHECKLIST.md','COVER_LETTER_DRAFT.md','DATA_CODE_AVAILABILITY.md','LICENSE_STATUS.md']:
    if not (root/name).is_file(): fail(f'missing required file {name}')
if a.require_render:
    pdf = root/m['render']['pdf']; sums = root/m['render']['checksums']
    if not pdf.is_file() or not sums.is_file(): fail('render or checksum receipt missing')
    if not pdf.read_bytes().startswith(b'%PDF-'): fail('main.pdf lacks PDF signature')
    expected = {}
    for line in sums.read_text().splitlines():
        fields=line.split()
        if len(fields)>=2: expected[fields[-1].lstrip('*')] = fields[0]
    for name in ['SOURCE.md','CLAIM_LEDGER.md',m['render']['pdf']]:
        got=hashlib.sha256((root/name).read_bytes()).hexdigest()
        if expected.get(name) != got: fail(f'SHA256 receipt mismatch for {name}')
print(json.dumps({'paper_id':m['paper_id'],'source_blob':m['git_blob_sha1']['SOURCE.md'],'ledger_blob':m['git_blob_sha1']['CLAIM_LEDGER.md'],'render_required':a.require_render,'status':'PASS'}, sort_keys=True))
