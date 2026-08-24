#!/usr/bin/env python3
"""Repair only the frozen 41 P4 V5 same-identity bridge failures.

Development evidence only.  No case text, labels, system outputs, or protected
outcomes are read.  Files/tags/commits/requests remain evidence and never n.
"""
from __future__ import annotations
import datetime as dt, gzip, hashlib, io, json, os, re, shutil, stat, subprocess, tarfile, tempfile, time, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path, PurePosixPath
from typing import Any

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
V5=REPO/'development/p4-m6-joss-exact-version-bridge-v5-2026-08-23'
UA='orion-p4-v6-same-identity-bridge-repair/1.0'
ACCEPTED={'MIT','Apache-2.0','GPL-2.0-only','GPL-2.0-or-later','GPL-3.0-only','GPL-3.0-or-later','BSD-2-Clause','BSD-3-Clause','MPL-2.0','ISC','LGPL-2.1-only','LGPL-2.1-or-later','LGPL-3.0-only','LGPL-3.0-or-later'}
ALIASES={'mit':'MIT','mit-license':'MIT','apache-2.0':'Apache-2.0','apache2.0':'Apache-2.0','bsd-2-clause':'BSD-2-Clause','bsd-2-clause-netbsd':'BSD-2-Clause','bsd-3-clause':'BSD-3-Clause','gpl-2.0':'GPL-2.0-only','gpl-3.0':'GPL-3.0-only','gpl-3.0-or-later':'GPL-3.0-or-later','mpl-2.0':'MPL-2.0','isc':'ISC','lgpl-2.1':'LGPL-2.1-only','lgpl-3.0':'LGPL-3.0-only'}

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha_bytes(b:bytes): return hashlib.sha256(b).hexdigest()
def sha_file(p:Path): return sha_bytes(p.read_bytes())
def load_jsonl(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def canon_sha(obj): return sha_bytes(json.dumps(obj,sort_keys=True,separators=(',',':')).encode())
def spdx(x):
    if not x:return None
    s=str(x).strip(); return s if s in ACCEPTED else ALIASES.get(s.casefold())

def github_token():
    for k in ('GITHUB_TOKEN','GH_TOKEN'):
        if os.environ.get(k): return os.environ[k]
    try:return subprocess.check_output(['gh','auth','token'],text=True,stderr=subprocess.DEVNULL,timeout=10).strip()
    except Exception:return ''
TOKEN=github_token()
MAX_SOURCE_DOWNLOAD_BYTES=int(os.environ.get('P4_V6_MAX_SOURCE_DOWNLOAD_BYTES','10000000'))
ONLY_INDICES={int(x) for x in os.environ.get('P4_V6_ONLY_INDICES','').split(',') if x.strip()}

def fetch(url:str, *, github=False, binary=False, attempts=3)->tuple[bytes|None,dict]:
    trail=[]
    for a in range(1,attempts+1):
        t=now(); headers={'User-Agent':UA,'Accept':'application/vnd.github+json' if github else 'application/json'}
        if github and TOKEN:headers['Authorization']=f'Bearer {TOKEN}'
        req=urllib.request.Request(url,headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=120) as resp:
                body=resp.read(); rec={'attempt':a,'started_at':t,'http_status':resp.status,'final_url':resp.geturl(),'content_type':resp.headers.get('Content-Type'),'body_bytes':len(body),'body_sha256':sha_bytes(body),'error':None}
                trail.append(rec); return body,{'url':url,'attempts':trail}
        except urllib.error.HTTPError as e:
            body=e.read(); trail.append({'attempt':a,'started_at':t,'http_status':e.code,'final_url':e.geturl(),'content_type':e.headers.get('Content-Type'),'body_bytes':len(body),'body_sha256':sha_bytes(body),'error':f'HTTPError:{e.code}'})
            if e.code not in (429,500,502,503,504):break
        except Exception as e:
            trail.append({'attempt':a,'started_at':t,'http_status':None,'final_url':None,'content_type':None,'body_bytes':0,'body_sha256':None,'error':type(e).__name__})
        time.sleep(min(8,2**(a-1)))
    return None,{'url':url,'attempts':trail}

def json_fetch(url,github=False):
    b,r=fetch(url,github=github)
    if b is None:return None,r
    try:return json.loads(b),r
    except Exception:r['parse_error']='JSONDecodeError'; return None,r

def repo_parts(full):
    a,b=full.split('/',1); return a,b

def resolve_tag(repo,tag):
    owner,name=repo_parts(repo); q=urllib.parse.quote(tag,safe='')
    obj,rec=json_fetch(f'https://api.github.com/repos/{owner}/{name}/git/ref/tags/{q}',True)
    reqs=[{'purpose':'resolve_tag_ref',**rec}]
    if not isinstance(obj,dict):return None,reqs
    o=obj.get('object') or {}; typ=o.get('type'); s=o.get('sha')
    if typ=='tag' and re.fullmatch(r'[0-9a-f]{40}',str(s or '')):
        t,rr=json_fetch(f'https://api.github.com/repos/{owner}/{name}/git/tags/{s}',True);reqs.append({'purpose':'dereference_annotated_tag',**rr})
        if isinstance(t,dict):o=t.get('object') or {};typ=o.get('type');s=o.get('sha')
    return (str(s).lower() if typ=='commit' and re.fullmatch(r'[0-9a-fA-F]{40}',str(s or '')) else None),reqs

def resolve_commit(repo,prefix):
    owner,name=repo_parts(repo)
    obj,rec=json_fetch(f'https://api.github.com/repos/{owner}/{name}/commits/{urllib.parse.quote(prefix,safe="")}',True)
    sha=(obj or {}).get('sha') if isinstance(obj,dict) else None
    return (str(sha).lower() if re.fullmatch(r'[0-9a-fA-F]{40}',str(sha or '')) else None),[{'purpose':'resolve_source_native_commit_prefix',**rec}]

def commit_tree(repo,commit):
    owner,name=repo_parts(repo);obj,rec=json_fetch(f'https://api.github.com/repos/{owner}/{name}/git/commits/{commit}',True)
    tree=((obj or {}).get('tree') or {}).get('sha') if isinstance(obj,dict) else None
    return (str(tree).lower() if re.fullmatch(r'[0-9a-fA-F]{40}',str(tree or '')) else None),{'purpose':'bind_commit_root_tree',**rec}

def license_at(repo,commit):
    owner,name=repo_parts(repo);obj,rec=json_fetch(f'https://api.github.com/repos/{owner}/{name}/license?ref={commit}',True)
    lic=(obj or {}).get('license') or {} if isinstance(obj,dict) else {}
    md={'spdx_id':lic.get('spdx_id'),'name':lic.get('name'),'key':lic.get('key'),'license_blob_sha':(obj or {}).get('sha') if isinstance(obj,dict) else None,'path':(obj or {}).get('path') if isinstance(obj,dict) else None}
    return spdx(md['spdx_id']),{'purpose':'bind_license_at_exact_commit','metadata':md,**rec}

def version_candidates(*vals):
    out=[]
    for raw in vals:
        if raw is None:continue
        s=str(raw).strip()
        if not s:continue
        for x in (s, s.lower(), s[1:] if s[:1] in 'vV' else 'v'+s, (s[1:] if s[:1] in 'vV' else 'v'+s).lower()):
            if x and x not in out:out.append(x)
    return out

def parse_swh(md):
    s=(md.get('swh') or {}).get('swhid') if isinstance(md.get('swh'),dict) else None
    if not s:return {'swhid':None,'directory_id':None,'anchor_release_id':None,'path':None,'commit_prefix':None}
    dm=re.search(r'^swh:1:dir:([0-9a-f]{40})',s);am=re.search(r'(?:^|;)anchor=swh:1:rel:([0-9a-f]{40})',s);pm=re.search(r'(?:^|;)path=([^;]*)',s)
    path=urllib.parse.unquote(pm.group(1)) if pm else None;cm=re.search(r'(?:-|_)([0-9a-f]{7,40})/?$',path or '')
    return {'swhid':s,'directory_id':dm.group(1) if dm else None,'anchor_release_id':am.group(1) if am else None,'path':path,'commit_prefix':cm.group(1) if cm else None}

def resolve_swh_path(directory_id, path):
    """Resolve a qualified SWHID path to its content directory identifier."""
    current=directory_id; receipts=[]
    parts=[p for p in (path or '').strip('/').split('/') if p]
    for part in parts:
        obj,rec=json_fetch(f'https://archive.softwareheritage.org/api/1/directory/{current}/')
        receipts.append({'purpose':'resolve_qualified_swhid_path_component','component':part,**rec})
        matches=[x for x in (obj or []) if isinstance(x,dict) and x.get('name')==part and x.get('type')=='dir'] if isinstance(obj,list) else []
        if len(matches)!=1:return None,receipts
        target=matches[0].get('target')
        if not re.fullmatch(r'[0-9a-f]{40}',str(target or '')):return None,receipts
        current=target
    return current,receipts

def safe_parts(name):
    p=PurePosixPath(name.replace('\\','/'))
    if p.is_absolute() or '..' in p.parts:return None
    return [x for x in p.parts if x not in ('','.')]

def strip_wrapper(items):
    first={x['path'].split('/',1)[0] for x in items if x.get('path')}
    if len(first)==1 and all('/' in x['path'] for x in items):
        for x in items:x['path']=x['path'].split('/',1)[1]
    return items

def archive_manifest(path:Path):
    items=[];kind=None
    try:
        if zipfile.is_zipfile(path):
            kind='zip'
            with zipfile.ZipFile(path) as z:
                seen=set()
                for i in z.infolist():
                    if i.is_dir():continue
                    parts=safe_parts(i.filename)
                    if not parts:return None,{'status':'REJECT_UNSAFE_PATH','archive_kind':kind}
                    name='/'.join(parts)
                    if name in seen:return None,{'status':'REJECT_DUPLICATE_PATH','archive_kind':kind}
                    seen.add(name); mode=(i.external_attr>>16)&0o177777; data=z.read(i)
                    typ='symlink' if stat.S_ISLNK(mode) else 'file'; exe=bool(mode&0o111) if typ=='file' else False
                    items.append({'path':name,'type':typ,'executable':exe,'size':len(data),'sha256':sha_bytes(data)})
        elif tarfile.is_tarfile(path):
            kind='tar'
            with tarfile.open(path,'r:*') as t:
                seen=set()
                for i in t.getmembers():
                    if i.isdir():continue
                    parts=safe_parts(i.name)
                    if not parts:return None,{'status':'REJECT_UNSAFE_PATH','archive_kind':kind}
                    name='/'.join(parts)
                    if name in seen:return None,{'status':'REJECT_DUPLICATE_PATH','archive_kind':kind}
                    seen.add(name)
                    if i.issym():data=i.linkname.encode();typ='symlink';exe=False
                    elif i.isfile():
                        f=t.extractfile(i);data=f.read() if f else b'';typ='file';exe=bool(i.mode&0o111)
                    else:continue
                    items.append({'path':name,'type':typ,'executable':exe,'size':len(data),'sha256':sha_bytes(data)})
        else:return None,{'status':'CANNOT_CHECK_UNSUPPORTED_ARCHIVE','archive_kind':None}
    except Exception as e:return None,{'status':f'CANNOT_CHECK_EXTRACTION_{type(e).__name__}','archive_kind':kind}
    items=strip_wrapper(items);items.sort(key=lambda x:(x['path'],x['type']))
    return items,{'status':'PASS','archive_kind':kind,'file_count':len(items),'manifest_sha256':canon_sha(items),'total_uncompressed_bytes':sum(x['size'] for x in items)}

def download(url,path,github=False):
    b,rec=fetch(url,github=github,binary=True,attempts=3)
    if b is not None:path.write_bytes(b)
    return (path if b is not None else None),rec

def selected_native(md):
    return {'id':md.get('id'),'doi':md.get('doi'),'conceptdoi':md.get('conceptdoi'),'conceptrecid':md.get('conceptrecid'),'version':md.get('version'),'license':md.get('license'),'status':md.get('status'),'state':md.get('state'),'created':md.get('created'),'modified':md.get('modified'),'swh':md.get('swh'),'links':{k:(md.get('links') or {}).get(k) for k in ('self','doi','parent','parent_doi','versions')},'files':[{'key':f.get('key'),'size':f.get('size'),'checksum':f.get('checksum'),'content_url':(f.get('links') or {}).get('self')} for f in md.get('files') or []]}

def fetch_native(row, v5_harvest, v5_resume):
    """Reuse the content-hashed V5 source-native capture.

    Zenodo concept-record endpoints can later redirect to a newer version, so a
    live re-read would destroy exact-version identity.  V6 therefore treats the
    already captured V5 response body hash/metadata as the primary frozen
    source-native receipt.  Only the previously unfrozen Figshare route is read
    live below.
    """
    doi=row['archive_version_doi'];m=re.fullmatch(r'10\.5281/zenodo\.(\d+)',doi,re.I)
    if m:
        h=v5_harvest[row['frozen_index']]
        z=(h.get('zenodo') or {})
        resumed=v5_resume.get(row['frozen_index']) or {}
        md=resumed.get('metadata') or z.get('metadata')
        rec={'route':'REUSED_V5_CONTENT_HASHED_SOURCE_NATIVE_CAPTURE','v5_attempts':resumed.get('attempts') or z.get('attempts') or [],'v5_url':resumed.get('url') or z.get('url'),'v5_harvest_record_sha256':canon_sha(h),'v5_resume_record_sha256':canon_sha(resumed) if resumed else None}
        return ('ZENODO',md,rec)
    m=re.fullmatch(r'10\.6084/m9\.figshare\.(\d+)(?:\.v(\d+))?',doi,re.I)
    if m:
        obj,rec=json_fetch(f'https://api.figshare.com/v2/articles/{m.group(1)}')
        md=None
        if isinstance(obj,dict):
            md={'id':obj.get('id'),'doi':obj.get('doi'),'conceptdoi':None,'version':obj.get('version'),'license':obj.get('license'),'status':obj.get('status'),'state':None,'created':obj.get('date_created'),'modified':obj.get('date_modified'),'swh':None,'links':{'self':obj.get('url_public_api'),'doi':obj.get('url_public_html'),'parent':None,'parent_doi':None,'versions':obj.get('url_public_api')+'/versions' if obj.get('url_public_api') else None},'files':[{'key':f.get('name'),'size':f.get('size'),'checksum':f.get('supplied_md5') or f.get('computed_md5'),'content_url':f.get('download_url')} for f in obj.get('files') or []]}
        return ('FIGSHARE',md,rec)
    return ('UNSUPPORTED',None,{'url':None,'attempts':[]})

def main():
    start=now(); cache=HERE/'cache_v6';cache.mkdir(exist_ok=True)
    bridge=load_jsonl(V5/'BRIDGE_ROWS_V5.jsonl'); v5gh={r['frozen_index']:r for r in load_jsonl(V5/'GITHUB_ARCHIVE_RELATION_RESOLUTION_V5.jsonl')}
    v5_harvest={r['frozen_index']:r for r in load_jsonl(V5/'HARVEST_RECORDS_V5.jsonl')}
    v5_resume={r['frozen_index']:r for r in load_jsonl(V5/'ZENODO_SAME_IDENTITY_RESUME_V5.jsonl')}
    all_failed=[r for r in bridge if r['gates']['v4_provider_qualified_predecessor_preserved'] and not r['exact_publication_archive_repository_commit_rights_bridge_pass']]
    failed=[r for r in all_failed if not ONLY_INDICES or r['frozen_index'] in ONLY_INDICES]
    prior_rows={}
    out_path=HERE/'BRIDGE_REPAIR_ROWS_V6.jsonl'
    if ONLY_INDICES and out_path.exists():prior_rows={r['frozen_index']:r for r in load_jsonl(out_path)}
    prior_receipt_sha=sha_file(HERE/'HARVEST_RECEIPT_V6.json') if ONLY_INDICES and (HERE/'HARVEST_RECEIPT_V6.json').exists() else None
    out=[]
    for pos,row in enumerate(failed,1):
        idx=row['frozen_index']; repo=row['joss_repository']; provider,md,native_req=fetch_native(row,v5_harvest,v5_resume); md=md or {}
        frozen_archive=row['archive_version_doi'].casefold();native_doi=str(md.get('doi') or '').casefold();concept=str(md.get('conceptdoi') or '').casefold()
        exact_native_version=(native_doi==frozen_archive)
        distinct_concept=bool(exact_native_version and concept and concept!=native_doi)
        native_lic=spdx(((md.get('license') or {}).get('id') if isinstance(md.get('license'),dict) else md.get('license')))
        archive_lic=next((spdx(x) for x in row.get('archive_spdx_rights') or [] if spdx(x)),None) or native_lic
        swh=parse_swh(md)
        resolved_swh_dir=None; swh_path_requests=[]
        if swh['directory_id']:
            resolved_swh_dir,swh_path_requests=resolve_swh_path(swh['directory_id'],swh['path'])
        swh['resolved_directory_id']=resolved_swh_dir
        swh['path_resolution_requests']=swh_path_requests
        candidates=[]
        old=v5gh.get(idx,{})
        old_commit=row.get('immutable_commit_sha')
        if old_commit:candidates.append({'kind':'V5_RESOLVED_ARCHIVE_EXPLICIT_COMMIT','value':old_commit,'commit':old_commit,'requests':[]})
        if swh['commit_prefix']:
            c,reqs=resolve_commit(repo,swh['commit_prefix']);candidates.append({'kind':'SOURCE_NATIVE_SWH_PATH_COMMIT_PREFIX','value':swh['commit_prefix'],'commit':c,'requests':reqs})
        for tag in version_candidates(md.get('version'),row.get('archive_version')):
            c,reqs=resolve_tag(repo,tag);candidates.append({'kind':'SOURCE_NATIVE_VERSION_TAG_DISCOVERY','value':tag,'commit':c,'requests':reqs})
        # exact duplicate commits do not multiply evidence; retain candidate failures separately
        commit_options=[]
        for c in candidates:
            if c.get('commit') and c['commit'] not in [x['commit'] for x in commit_options]:commit_options.append(c)
        identities=[];accepted=None
        for c in commit_options:
            tree,treq=commit_tree(repo,c['commit']); ident={'candidate_kind':c['kind'],'candidate_value':c['value'],'commit_sha':c['commit'],'tree_sha':tree,'requests':c['requests']+[treq], 'content_identity_method':None,'content_identity_pass':False}
            if resolved_swh_dir and tree==resolved_swh_dir:
                ident.update({'content_identity_method':'QUALIFIED_SWHID_PATH_DIRECTORY_EQUALS_GIT_COMMIT_ROOT_TREE','content_identity_pass':True,'source_manifest':{'status':'PASS_QUALIFIED_SWHID_PATH_DIRECTORY','swhid_root_directory_sha1':swh['directory_id'],'qualified_path':swh['path'],'manifest_sha1':resolved_swh_dir},'github_manifest':{'status':'PASS_GIT_TREE','manifest_sha1':tree}})
            identities.append(ident)
            if ident['content_identity_pass'] and accepted is None:accepted=ident
        # For exact version rows without an accepted SWH equality, compare source-native archive bytes with commit archive(s).
        source_download_bytes=sum(int(f.get('size') or 0) for f in (md.get('files') or []))
        content_download_route_eligible=(source_download_bytes <= MAX_SOURCE_DOWNLOAD_BYTES)
        if exact_native_version and accepted is None and commit_options and md.get('files') and content_download_route_eligible:
            source_manifests=[]
            for fi,f in enumerate(md.get('files') or []):
                url=f.get('content_url'); key=f.get('key') or f'file-{fi}'
                if not url:continue
                ext=''.join(Path(key).suffixes) or '.bin'; fp=cache/f'{idx}-source-{fi}{ext}'
                got,dreq=download(url,fp,False)
                if got:
                    man,meta=archive_manifest(got);meta.update({'source_key':key,'download':dreq,'download_sha256':sha_file(got),'download_bytes':got.stat().st_size})
                    source_manifests.append((man,meta))
            for ident in identities:
                if ident['content_identity_pass']:continue
                owner,name=repo_parts(repo);gp=cache/f"{idx}-github-{ident['commit_sha']}.tar.gz"
                got,greq=download(f'https://api.github.com/repos/{owner}/{name}/tarball/{ident["commit_sha"]}',gp,True)
                if not got:
                    ident['github_manifest']={'status':'CANNOT_CHECK_DOWNLOAD','download':greq};continue
                gm,gmeta=archive_manifest(got);gmeta.update({'download':greq,'download_sha256':sha_file(got),'download_bytes':got.stat().st_size})
                ident['github_manifest']=gmeta
                matches=[]
                for sm,smeta in source_manifests:
                    matches.append({'source_key':smeta.get('source_key'),'source_manifest':smeta,'exact_manifest_match':bool(sm is not None and gm is not None and sm==gm)})
                ident['source_manifest_comparisons']=matches
                if sum(x['exact_manifest_match'] for x in matches)==1:
                    ident['content_identity_method']='SOURCE_NATIVE_ARCHIVE_MANIFEST_EQUALS_GITHUB_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST';ident['content_identity_pass']=True
                    if accepted is None:accepted=ident
        commit=accepted['commit_sha'] if accepted else None
        commit_lic=None;lic_req=None
        if commit:commit_lic,lic_req=license_at(repo,commit)
        repaired_gates={
          'source_native_exact_version_to_distinct_concept':distinct_concept,
          'source_native_archive_version_to_same_repository_immutable_commit_content_identity':bool(accepted),
          'accepted_source_native_or_doi_registered_archive_spdx_rights':bool(archive_lic),
          'accepted_spdx_rights_at_exact_immutable_commit':bool(commit_lic),
          'source_native_archive_transport':bool(md),
        }
        # Other V5 gates were already true for these 41 and remain immutable.
        repaired=all(repaired_gates.values())
        causes=[]
        if not md:causes.append('SOURCE_NATIVE_ARCHIVE_TRANSPORT_CANNOT_CHECK')
        if md and not exact_native_version:
            causes.append('FROZEN_ARCHIVE_DOI_IS_CONCEPT_OR_MUTABLE_LATEST_REDIRECT__EXACT_PUBLICATION_VERSION_CANNOT_CHECK')
        elif not distinct_concept:causes.append('SOURCE_NATIVE_DISTINCT_VERSION_CONCEPT_RELATION_CANNOT_CHECK')
        if not accepted:causes.append('SOURCE_ARCHIVE_TO_IMMUTABLE_REPOSITORY_COMMIT_CONTENT_IDENTITY_CANNOT_CHECK')
        if exact_native_version and not accepted and commit_options and md.get('files') and not content_download_route_eligible:
            causes.append('CONTENT_MANIFEST_COMPARISON_DEFERRED_ABOVE_DISCLOSED_EXECUTION_BYTE_BOUND')
        if not archive_lic:causes.append('EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED')
        if not commit:causes.append('IMMUTABLE_COMMIT_CANNOT_CHECK')
        elif not commit_lic:causes.append('EXACT_COMMIT_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED')
        if repaired:causes=[]
        out.append({'schema_version':'orion.p4.m6.joss-bridge-repair.row.v6','frozen_index':idx,'publication_doi':row['publication_doi'],'archive_doi':row['archive_version_doi'],'repository':repo,'domain':row['domain_discovery'],'v5_failure_causes':row['failure_causes'],'source_native_provider':provider,'source_native_request':native_req,'source_native_metadata':md,'source_native_exact_version_doi_match':exact_native_version,'source_native_distinct_concept_identity':concept or None,'source_native_archive_spdx':archive_lic,'swh_identity':swh,'source_native_download_bytes':source_download_bytes,'content_manifest_execution_byte_bound':MAX_SOURCE_DOWNLOAD_BYTES,'content_download_route_eligible':content_download_route_eligible,'deterministic_candidates':candidates,'content_identity_attempts':identities,'accepted_content_identity':accepted,'exact_commit_sha':commit,'commit_spdx':commit_lic,'commit_license_request':lic_req,'repaired_gates':repaired_gates,'v6_exact_bridge_repaired':repaired,'v6_failure_causes':causes,'author_lineage_independence':'CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED','natural_pair_eligibility':'CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED','counts_as_unit':1})
        print(f'[{pos:02d}/{len(failed):02d}] index={idx} repaired={repaired} exact_version={exact_native_version} content={bool(accepted)} archive_license={archive_lic} commit_license={commit_lic}',flush=True)
    if ONLY_INDICES:
        for r in out:prior_rows[r['frozen_index']]=r
        out=[prior_rows[r['frozen_index']] for r in all_failed]
    p=out_path;p.write_text('\n'.join(json.dumps(x,sort_keys=True) for x in out)+'\n')
    # delete downloaded bytes; receipts preserve URL, byte counts, and SHA-256 plus normalized manifest digests.
    shutil.rmtree(cache,ignore_errors=True)
    receipt={'schema_version':'orion.p4.m6.joss-bridge-repair.harvest-receipt.v6','created_at':now(),'started_at':start,'artifact':str(p),'artifact_sha256':sha_file(p),'counts':{'frozen_failed_identities':len(out),'repaired':sum(r['v6_exact_bridge_repaired'] for r in out),'unresolved':sum(not r['v6_exact_bridge_repaired'] for r in out),'source_native_transport':sum(bool(r['source_native_metadata']) for r in out),'exact_native_version_match':sum(r['source_native_exact_version_doi_match'] for r in out),'content_identity_bound':sum(bool(r['accepted_content_identity']) for r in out),'exact_commit_rights_bound':sum(bool(r['commit_spdx']) for r in out),'content_manifest_deferred_above_byte_bound':sum('CONTENT_MANIFEST_COMPARISON_DEFERRED_ABOVE_DISCLOSED_EXECUTION_BYTE_BOUND' in r['v6_failure_causes'] for r in out)},'github_authentication_available':bool(TOKEN),'token_retained':False,'download_payloads_retained':False,'content_manifest_execution_byte_bound':MAX_SOURCE_DOWNLOAD_BYTES,'updated_indices':sorted(ONLY_INDICES) if ONLY_INDICES else [r['frozen_index'] for r in all_failed],'prior_execution_receipt_sha256':prior_receipt_sha,'files_tags_commits_requests_counted_as_units':False,'new_or_replacement_publication_dois':0,'protected_or_system_outcomes_accessed':False}
    (HERE/'HARVEST_RECEIPT_V6.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt['counts'],sort_keys=True))
if __name__=='__main__':main()
