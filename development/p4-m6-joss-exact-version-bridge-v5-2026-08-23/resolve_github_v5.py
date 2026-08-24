#!/usr/bin/env python3
"""Resolve only archive-explicit GitHub tag/commit relations for the frozen V5 frame."""
from __future__ import annotations
import concurrent.futures, datetime as dt, hashlib, json, pathlib, re, subprocess, time, urllib.error, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
ROWS=[json.loads(l) for l in (ROOT/'HARVEST_RECORDS_V5.jsonl').open() if l.strip()]
UA='ORION-P4-V5-public-metadata/1.0 (bounded exact-version relation resolver)'
MAX_WORKERS=6
try:
    TOKEN=subprocess.run(['gh','auth','token'],check=True,capture_output=True,text=True).stdout.strip()
except Exception:
    TOKEN=''

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def shab(b):return hashlib.sha256(b).hexdigest()
def fetch(url):
    attempts=[]
    for attempt in range(1,4):
        try:
            headers={'User-Agent':UA,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
            if TOKEN: headers['Authorization']=f'Bearer {TOKEN}'
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=45) as resp:
                body=resp.read(); status=resp.status; ct=resp.headers.get('Content-Type')
            attempts.append({'attempt':attempt,'started_at':now(),'http_status':status,'body_bytes':len(body),'body_sha256':shab(body),'content_type':ct,'error':None})
            return body,attempts
        except urllib.error.HTTPError as e:
            b=e.read(); attempts.append({'attempt':attempt,'started_at':now(),'http_status':e.code,'body_bytes':len(b),'body_sha256':shab(b),'content_type':e.headers.get('Content-Type') if e.headers else None,'error':f'HTTPError:{e.code}'})
            if e.code not in (429,500,502,503,504): break
        except Exception as e:
            attempts.append({'attempt':attempt,'started_at':now(),'http_status':None,'body_bytes':0,'body_sha256':None,'content_type':None,'error':f'{type(e).__name__}:{e}'})
        time.sleep(0.75*attempt)
    return None,attempts

def parse_repo(url):
    p=urllib.parse.urlparse(url); seg=[urllib.parse.unquote(s) for s in p.path.strip('/').split('/')]
    if p.hostname not in ('github.com','www.github.com') or len(seg)<2:return None
    return {'owner':seg[0],'repo':seg[1].removesuffix('.git'),'full_name_casefolded':f'{seg[0]}/{seg[1].removesuffix(".git")}'.casefold(),'segments':seg}

def candidates(row):
    out=[]
    for ri in (row.get('datacite',{}).get('metadata') or {}).get('relatedIdentifiers') or []:
        u=ri.get('relatedIdentifier') or ''; parsed=parse_repo(u)
        if not parsed: continue
        seg=parsed.pop('segments'); kind=None; value=None
        if len(seg)>=4 and seg[2]=='tree': kind='TAG_CANDIDATE_FROM_TREE_URL'; value='/'.join(seg[3:])
        elif len(seg)>=5 and seg[2]=='releases' and seg[3]=='tag': kind='TAG_CANDIDATE_FROM_RELEASE_URL'; value='/'.join(seg[4:])
        elif len(seg)>=4 and seg[2]=='commit' and re.fullmatch(r'[0-9a-fA-F]{7,40}',seg[3]): kind='COMMIT_CANDIDATE'; value=seg[3].lower()
        if kind and value:
            out.append({**parsed,'kind':kind,'value':value,'url':u,'relation_type':ri.get('relationType'),'related_identifier_type':ri.get('relatedIdentifierType')})
    # exact duplicate URLs/tags do not multiply evidence
    unique=[]; seen=set()
    for c in out:
        k=(c['full_name_casefolded'],c['kind'].split('_CANDIDATE')[0],c['value'].casefold())
        if k not in seen: seen.add(k); unique.append(c)
    return unique

def one(row):
    jrepos=row['joss'].get('repository_links') or []
    jrepo=parse_repo(jrepos[0]['href']) if len(jrepos)==1 else None
    if jrepo: jrepo.pop('segments',None)
    cs=candidates(row)
    same=[c for c in cs if jrepo and c['full_name_casefolded']==jrepo['full_name_casefolded']]
    out={
      'frozen_index':row['frozen_index'],'publication_doi':row['publication_doi'],'archive_doi':row.get('archive_doi'),
      'joss_repository':jrepo,'archive_explicit_github_candidates':cs,'same_joss_repository_candidates':same,
      'selection_status':None,'selected_candidate':None,'resolution':None,'license_at_commit':None,
    }
    keys={(c['kind'].split('_CANDIDATE')[0],c['value'].casefold()) for c in same}
    if not jrepo: out['selection_status']='CANNOT_CHECK_JOSS_REPOSITORY_IDENTITY'; return out
    if not same: out['selection_status']='CANNOT_CHECK_NO_ARCHIVE_EXPLICIT_TAG_OR_COMMIT_FOR_JOSS_REPOSITORY'; return out
    if len(keys)!=1: out['selection_status']='CANNOT_CHECK_MULTIPLE_ARCHIVE_EXPLICIT_TAG_OR_COMMIT_IDENTITIES'; return out
    c=same[0]; out['selected_candidate']=c; out['selection_status']='PASS_UNIQUE_ARCHIVE_EXPLICIT_GITHUB_IDENTITY'
    owner=urllib.parse.quote(c['owner'],safe=''); repo=urllib.parse.quote(c['repo'],safe='')
    requests=[]; commit=None; terminal=None
    if c['kind'].startswith('TAG_'):
        tag=urllib.parse.quote(c['value'],safe='')
        url=f'https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{tag}'
        body,attempts=fetch(url); requests.append({'purpose':'resolve_tag_ref','url':url,'attempts':attempts})
        if body is not None:
            try:
                d=json.loads(body); obj=d.get('object') or {}; terminal=obj.get('type'); sha=obj.get('sha')
                if terminal=='commit' and re.fullmatch(r'[0-9a-f]{40}',sha or ''): commit=sha
                elif terminal=='tag' and re.fullmatch(r'[0-9a-f]{40}',sha or ''):
                    turl=f'https://api.github.com/repos/{owner}/{repo}/git/tags/{sha}'
                    tb,ta=fetch(turl); requests.append({'purpose':'dereference_annotated_tag','url':turl,'attempts':ta})
                    if tb is not None:
                        td=json.loads(tb); to=td.get('object') or {}; terminal=to.get('type'); tsha=to.get('sha')
                        if terminal=='commit' and re.fullmatch(r'[0-9a-f]{40}',tsha or ''): commit=tsha
            except Exception: pass
    else:
        value=urllib.parse.quote(c['value'],safe='')
        url=f'https://api.github.com/repos/{owner}/{repo}/commits/{value}'
        body,attempts=fetch(url); requests.append({'purpose':'resolve_explicit_commit','url':url,'attempts':attempts})
        if body is not None:
            try:
                sha=json.loads(body).get('sha'); terminal='commit'
                if re.fullmatch(r'[0-9a-f]{40}',sha or ''): commit=sha
            except Exception: pass
    out['resolution']={'requests':requests,'terminal_object_type':terminal,'commit_sha':commit,'status':'PASS' if commit else 'CANNOT_CHECK_ARCHIVE_EXPLICIT_IDENTITY_TO_COMMIT'}
    if commit:
        curl=f'https://api.github.com/repos/{owner}/{repo}/license?ref={commit}'
        lb,la=fetch(curl); license_info=None
        if lb is not None:
            try:
                ld=json.loads(lb); lic=ld.get('license') or {}; license_info={'spdx_id':lic.get('spdx_id'),'name':lic.get('name'),'key':lic.get('key'),'license_blob_sha':ld.get('sha'),'path':ld.get('path'),'html_url':ld.get('html_url')}
            except Exception: pass
        out['license_at_commit']={'url':curl,'attempts':la,'metadata':license_info}
    return out

def main():
    started=now()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex: out=list(ex.map(one,ROWS))
    out.sort(key=lambda r:r['frozen_index'])
    p=ROOT/'GITHUB_ARCHIVE_RELATION_RESOLUTION_V5.jsonl'; p.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in out))
    counts={
      'frozen_rows':len(out),
      'archive_explicit_github_identity_any_repository':sum(bool(r['archive_explicit_github_candidates']) for r in out),
      'unique_archive_explicit_identity_same_as_joss_repository':sum(r['selection_status']=='PASS_UNIQUE_ARCHIVE_EXPLICIT_GITHUB_IDENTITY' for r in out),
      'resolved_to_immutable_commit':sum((r.get('resolution') or {}).get('status')=='PASS' for r in out),
      'license_metadata_at_commit_bound':sum(bool((r.get('license_at_commit') or {}).get('metadata')) for r in out),
    }
    rec={'schema_version':'orion.p4.m6.joss-exact-version-bridge.github-resolution-receipt.v5','created_at':now(),'started_at':started,'github_authentication_available':bool(TOKEN),'token_retained':False,'artifact':str(p),'artifact_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'counts':counts,'new_identites_added':0,'outcomes_accessed':False}
    (ROOT/'GITHUB_RESOLUTION_RECEIPT_V5.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
