#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, hashlib, json, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
E=ROOT/'evidence'; E.mkdir(exist_ok=True)
PROTOCOL=json.loads((ROOT/'PROTOCOL_V9.json').read_text())
UA='ORION-P4-exact-edge-authority-v9/1.0 (research; contact unavailable)'

def get(url:str, slug:str):
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/vnd.github+json, application/json'})
    body=b''; status=None; final=url; headers={}; error=None
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            status=r.status; final=r.geturl(); headers=dict(r.headers); body=r.read()
    except urllib.error.HTTPError as e:
        status=e.code; final=e.geturl(); headers=dict(e.headers); body=e.read(); error=f'HTTPError:{e.code}'
    except Exception as e:
        error=f'{type(e).__name__}:{e}'
    path=E/f'{slug}.body'
    path.write_bytes(body)
    receipt={'url':url,'started_at':started,'finished_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':status,'final_url':final,'headers':{k:v for k,v in headers.items() if k.lower() in {'content-type','content-length','etag','last-modified','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','link'}},'body_path':str(path.relative_to(ROOT)),'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'error':error}
    (E/f'{slug}.receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt, body

def forms(v):
    out=[]
    for x in [v, v[1:] if v and v.startswith('v') else 'v'+v if v else None]:
        if x and x not in out: out.append(x)
    return out

summary=[]
for t in PROTOCOL['targets']:
    i=t['frozen_index']; repo=t['repository']; ver=t['publication_version']; rec=t['archive_doi'].split('.')[-1]
    row={'frozen_index':i,'repository':repo,'version':ver,'requests':[]}
    urls=[('zenodo_record',f'https://zenodo.org/api/records/{rec}'),('github_repo',f'https://api.github.com/repos/{repo}'),('github_tags',f'https://api.github.com/repos/{repo}/tags?per_page=100'),('github_releases',f'https://api.github.com/repos/{repo}/releases?per_page=100'),('crossref',f'https://api.crossref.org/works/{urllib.parse.quote(t["publication_doi"],safe="")}')]
    for name,url in urls:
        rr,_=get(url,f'{i}_{name}'); row['requests'].append(rr); time.sleep(.25)
    for n,tag in enumerate(forms(ver)):
        rr,_=get(f'https://api.github.com/repos/{repo}/git/ref/tags/{urllib.parse.quote(tag,safe="")}',f'{i}_github_ref_{n}'); row['requests'].append(rr); time.sleep(.25)
        rr,_=get(f'https://api.github.com/repos/{repo}/releases/tags/{urllib.parse.quote(tag,safe="")}',f'{i}_github_release_{n}'); row['requests'].append(rr); time.sleep(.25)
    origin=urllib.parse.quote(f'https://github.com/{repo}',safe='')
    rr,_=get(f'https://archive.softwareheritage.org/api/1/origin/{origin}/get/',f'{i}_swh_origin'); row['requests'].append(rr); time.sleep(.25)
    summary.append(row)
receipt={'schema_version':'orion.p4.primary-authority-probe.v9','finished_at':dt.datetime.now(dt.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL_V9.json').read_bytes()).hexdigest(),'rows':summary}
(ROOT/'PRIMARY_AUTHORITY_PROBE_RECEIPT_V9.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'rows':len(summary),'requests':sum(len(x['requests']) for x in summary),'statuses':{str(s):sum(1 for x in summary for r in x['requests'] if r['status']==s) for s in sorted({r['status'] for x in summary for r in x['requests']},key=lambda x:(x is None,x))}},sort_keys=True))
