#!/usr/bin/env python3
"""Resume only the same frozen Zenodo record identities whose first V5 request did not return 2xx."""
from __future__ import annotations
import datetime as dt,hashlib,json,pathlib,time,urllib.error,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
ROWS=[json.loads(l) for l in (ROOT/'HARVEST_RECORDS_V5.jsonl').open() if l.strip()]
UA='ORION-P4-V5-public-metadata/1.0 (same-identity Zenodo transport resume)'
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def shab(b):return hashlib.sha256(b).hexdigest()
def one(r):
 z=r.get('zenodo') or {}; attempts=z.get('attempts') or []; last=(attempts[-1].get('http_status') or 0) if attempts else 0
 if last//100==2:return None
 url=z.get('url'); out={'frozen_index':r['frozen_index'],'publication_doi':r['publication_doi'],'archive_doi':r['archive_doi'],'prior_final_status':last,'url':url,'attempts':[],'metadata':None}
 if not url:return out
 time.sleep(1.05)
 for i in range(1,4):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
   with urllib.request.urlopen(req,timeout=45) as resp: body=resp.read(); status=resp.status; ct=resp.headers.get('Content-Type')
   out['attempts'].append({'attempt':i,'started_at':now(),'http_status':status,'body_bytes':len(body),'body_sha256':shab(body),'content_type':ct,'error':None})
   d=json.loads(body); md=d.get('metadata') or {}
   out['metadata']={'id':d.get('id'),'doi':d.get('doi'),'conceptdoi':d.get('conceptdoi'),'conceptrecid':d.get('conceptrecid'),'created':d.get('created'),'modified':d.get('modified'),'status':d.get('status'),'state':d.get('state'),'submitted':d.get('submitted'),'version':md.get('version'),'license':md.get('license'),'access_right':md.get('access_right'),'resource_type':md.get('resource_type'),'related_identifiers':md.get('related_identifiers'),'relations':md.get('relations'),'swh':d.get('swh'),'files':[{'key':f.get('key'),'size':f.get('size'),'checksum':f.get('checksum'),'content_url':(f.get('links') or {}).get('self')} for f in d.get('files') or []]}
   return out
  except urllib.error.HTTPError as e:
   b=e.read(); out['attempts'].append({'attempt':i,'started_at':now(),'http_status':e.code,'body_bytes':len(b),'body_sha256':shab(b),'content_type':e.headers.get('Content-Type') if e.headers else None,'error':f'HTTPError:{e.code}'})
   if e.code not in (429,500,502,503,504):return out
  except Exception as e:out['attempts'].append({'attempt':i,'started_at':now(),'http_status':None,'body_bytes':0,'body_sha256':None,'error':f'{type(e).__name__}:{e}'})
  time.sleep(2*i)
 return out
started=now(); out=[]
for r in ROWS:
 x=one(r)
 if x:out.append(x)
p=ROOT/'ZENODO_SAME_IDENTITY_RESUME_V5.jsonl';p.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in out))
counts={'same_frozen_identities_resumed':len(out),'resume_final_2xx':sum(((r['attempts'][-1].get('http_status') or 0)//100==2) for r in out if r['attempts']),'resume_final_non_2xx':sum(((r['attempts'][-1].get('http_status') or 0)//100!=2) for r in out if r['attempts']),'new_or_replacement_identities':0}
rec={'schema_version':'orion.p4.m6.joss-exact-version-bridge.zenodo-resume-receipt.v5','created_at':now(),'started_at':started,'artifact':str(p),'artifact_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'counts':counts,'preserves_original_transport_failures':True,'outcomes_accessed':False}
(ROOT/'ZENODO_RESUME_RECEIPT_V5.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');print(json.dumps(counts,indent=2,sort_keys=True))
