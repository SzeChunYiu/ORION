#!/usr/bin/env python3
"""Hash-bind frozen WorkflowHub before/after RO-Crate content without gold."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SNAPSHOT_DIR=HERE/'workflowhub-source-census-v1'
MAX_BYTES=50*1024*1024
UA='ORION-A3-content-binding-v1/1.0 (+https://github.com/SzeChunYiu/ORION)'


def sha256_bytes(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def load_snapshot()->tuple[dict[str,Any],list[dict[str,Any]]]:
    m=json.loads((SNAPSHOT_DIR/'CENSUS_SNAPSHOT_V1.json').read_text())
    if m.get('schema')!='ORION.A3.WorkflowHubVersionedSourceCensusSnapshotManifest.v1':
        raise ValueError('snapshot manifest schema mismatch')
    rows=[]; seen=set()
    for c in m['chunks']:
        p=ROOT/c['path']
        raw=p.read_bytes()
        if sha256_bytes(raw)!=c['sha256']:
            raise ValueError(f"snapshot chunk hash mismatch: {c['path']}")
        d=json.loads(raw)
        if d.get('schema')!='ORION.A3.WorkflowHubVersionedSourceCensusChunk.v1':
            raise ValueError('snapshot chunk schema mismatch')
        cols=d['columns']
        for values in d['candidate_rows']:
            row=dict(zip(cols,values,strict=True))
            if row['workflow_id'] in seen: raise ValueError('duplicate workflow id in snapshot')
            seen.add(row['workflow_id']); rows.append(row)
    digest=hashlib.sha256(json.dumps([[r[c] for c in m['columns']] for r in rows],separators=(',',':')).encode()).hexdigest()
    if digest!=m['snapshot_candidate_rows_sha256']:
        raise ValueError('combined snapshot rows digest mismatch')
    if len(rows)!=m['versioned_public_licensed_candidate_families']!=128:
        raise ValueError('snapshot candidate count mismatch')
    return m,rows


def read_limited(response,max_bytes:int=MAX_BYTES)->bytes:
    data=response.read(max_bytes+1)
    if len(data)>max_bytes: raise ValueError(f'RO-Crate exceeds {max_bytes} bytes')
    return data


def validate_rocrate_bytes(data:bytes)->dict[str,Any]:
    if not data: raise ValueError('empty RO-Crate response')
    try:
        with zipfile.ZipFile(io.BytesIO(data),'r') as zf:
            names=zf.namelist()
            if 'ro-crate-metadata.json' not in names:
                raise ValueError('RO-Crate zip lacks root ro-crate-metadata.json')
            bad=zf.testzip()
            if bad is not None: raise ValueError(f'RO-Crate zip CRC failure: {bad}')
            meta=zf.read('ro-crate-metadata.json')
    except zipfile.BadZipFile as exc:
        raise ValueError('response is not a valid ZIP') from exc
    return {
        'bytes':len(data),
        'sha256':sha256_bytes(data),
        'ro_crate_metadata_sha256':sha256_bytes(meta),
        'zip_member_count':len(names),
    }


def fetch_rocrate(workflow_id:str,version:int,retries:int=3,timeout:float=60.0)->dict[str,Any]:
    url=f"https://workflowhub.eu/workflows/{urllib.parse.quote(workflow_id,safe='')}/ro_crate?version={version}"
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/zip'})
            with urllib.request.urlopen(req,timeout=timeout) as resp:
                status=getattr(resp,'status',200)
                if status!=200: raise RuntimeError(f'HTTP {status}')
                data=read_limited(resp)
                result=validate_rocrate_bytes(data)
                result.update({'url':url,'content_type':resp.headers.get('Content-Type'),'etag':resp.headers.get('ETag')})
                return result
        except (urllib.error.URLError,TimeoutError,RuntimeError,ValueError,OSError) as exc:
            last=exc
            if attempt+1<retries: time.sleep(0.75*(attempt+1))
    raise RuntimeError(f'failed RO-Crate fetch after {retries} attempts: {last}')


def bind_pair(row:dict[str,Any])->dict[str,Any]:
    wid=row['workflow_id']; before=int(row['version_before']); after=int(row['version_after'])
    base={
        'workflow_id':wid,'version_before':before,'version_after':after,
        'license_before':row['license_before'],'license_after':row['license_after'],
        'metadata_sha256_before':row['metadata_sha256_before'],'metadata_sha256_after':row['metadata_sha256_after'],
    }
    try:
        b=fetch_rocrate(wid,before); a=fetch_rocrate(wid,after)
        same=b['sha256']==a['sha256']
        return {**base,'status':'UNCHANGED_CONTENT' if same else 'CONTENT_BOUND_DIFFERENT','before':b,'after':a,'content_sha256_differ':not same}
    except Exception as exc:
        return {**base,'status':'CANNOT_CHECK_CONTENT_BINDING','reason':str(exc)[:500]}


def bind_all(max_workers:int=4)->dict[str,Any]:
    m,rows=load_snapshot()
    by_id={r['workflow_id']:r for r in rows}
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs={ex.submit(bind_pair,r):r['workflow_id'] for r in rows}
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    results.sort(key=lambda r:int(r['workflow_id']) if str(r['workflow_id']).isdigit() else r['workflow_id'])
    bound=[r for r in results if r['status']=='CONTENT_BOUND_DIFFERENT']
    unchanged=[r for r in results if r['status']=='UNCHANGED_CONTENT']
    failures=[r for r in results if r['status']=='CANNOT_CHECK_CONTENT_BINDING']
    result_digest=hashlib.sha256(json.dumps(results,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    success=len(bound)==128 and not unchanged and not failures
    return {
        'schema':'ORION.A3.WorkflowHubContentBindingResult.v1',
        'terminal':'WORKFLOWHUB_128_FROZEN_FAMILIES_ROCRATE_CONTENT_BOUND' if success else 'CANNOT_CHECK_WORKFLOWHUB_CONTENT_BINDING_FOR_128_FAMILIES',
        'source_snapshot_rows_sha256':m['snapshot_candidate_rows_sha256'],
        'source_candidate_manifest_sha256':m['candidate_manifest_sha256'],
        'candidate_n':len(results),
        'content_bound_different_n':len(bound),
        'unchanged_content_n':len(unchanged),
        'cannot_check_n':len(failures),
        'result_rows_sha256':result_digest,
        'results':results,
        'change_stratum_adjudicated':False,
        'external_gold_accessed':False,
        'protected_orion_predictions_accessed':False,
        'scientific_authority_delta':'NONE__PUBLIC_CONTENT_HASH_PREFLIGHT_ONLY',
    }


def fake_zip(payload:bytes=b'{}')->bytes:
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('ro-crate-metadata.json',payload)
        zf.writestr('workflow.cwl',b'cwlVersion: v1.2\n')
    return buf.getvalue()


def self_test()->dict[str,Any]:
    z=fake_zip(); r=validate_rocrate_bytes(z)
    assert r['bytes']==len(z) and r['zip_member_count']==2
    bad=io.BytesIO()
    with zipfile.ZipFile(bad,'w') as zf: zf.writestr('workflow.cwl','x')
    try: validate_rocrate_bytes(bad.getvalue())
    except ValueError as exc: assert 'metadata' in str(exc)
    else: raise AssertionError('zip without RO-Crate metadata accepted')
    try: validate_rocrate_bytes(b'not-a-zip')
    except ValueError as exc: assert 'ZIP' in str(exc)
    else: raise AssertionError('nonzip accepted')
    m,rows=load_snapshot()
    assert len(rows)==128 and m['snapshot_candidate_rows_sha256']=='a2d9f82fb78a0b73b9f6fa623cc9c115dddc25387208be17165140b6d2973f55'
    return {'decision':'GREEN','snapshot_n':len(rows),'invalid_zip_rejected':True,'missing_metadata_rejected':True,'network_accessed':False}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); ap.add_argument('--output',type=Path); ap.add_argument('--workers',type=int,default=4)
    args=ap.parse_args()
    if args.self_test: result=self_test(); code=0
    else:
        if not 1<=args.workers<=4: ap.error('--workers must be 1..4')
        result=bind_all(args.workers); code=0 if result['terminal'].startswith('WORKFLOWHUB_128') else 2
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output: args.output.write_text(text)
    print(text,end='')
    return code

if __name__=='__main__': raise SystemExit(main())
