#!/usr/bin/env python3
"""Harvest only the frozen 200 JOSS DOI identities for the V5 archive bridge."""
from __future__ import annotations
import concurrent.futures, datetime as dt, hashlib, html, json, pathlib, re, time, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parent
MANIFEST=json.loads((ROOT/'FROZEN_JOSS_IDENTITIES_V5.json').read_text())
UA='ORION-P4-V5-public-metadata/1.0 (bounded JOSS exact-version bridge)'
DOI_RE=re.compile(r'10\.\d{4,9}/[^\s"<>?#]+',re.I)
MAX_WORKERS=6

class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.anchors=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=='a': self.stack.append({'href':dict(attrs).get('href',''),'text':[]})
    def handle_data(self,data):
        if self.stack: self.stack[-1]['text'].append(data)
    def handle_endtag(self,tag):
        if tag.lower()=='a' and self.stack:
            a=self.stack.pop(); a['text']=' '.join(''.join(a['text']).split()); self.anchors.append(a)

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def shab(b:bytes): return hashlib.sha256(b).hexdigest()
def norm_doi(value):
    if not isinstance(value,str): return None
    s=urllib.parse.unquote(html.unescape(value)).strip().lower()
    s=re.sub(r'^(?:doi:|https?://(?:dx\.)?doi\.org/)','',s)
    m=DOI_RE.search(s)
    return m.group(0).rstrip('.,;:)]}') if m else None

def fetch(url,accept='application/json'):
    attempts=[]
    for attempt in range(1,4):
        started=now()
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':accept})
            with urllib.request.urlopen(req,timeout=45) as resp:
                body=resp.read(); status=resp.status; ctype=resp.headers.get('Content-Type')
            attempts.append({'attempt':attempt,'started_at':started,'http_status':status,'body_bytes':len(body),'body_sha256':shab(body),'content_type':ctype,'error':None})
            return body,attempts
        except urllib.error.HTTPError as e:
            body=e.read()
            attempts.append({'attempt':attempt,'started_at':started,'http_status':e.code,'body_bytes':len(body),'body_sha256':shab(body),'content_type':e.headers.get('Content-Type') if e.headers else None,'error':f'HTTPError:{e.code}'})
            if e.code not in (429,500,502,503,504): break
        except Exception as e:
            attempts.append({'attempt':attempt,'started_at':started,'http_status':None,'body_bytes':0,'body_sha256':None,'content_type':None,'error':f'{type(e).__name__}:{e}'})
        time.sleep(0.75*attempt)
    return None,attempts

def joss_one(item):
    doi=item['publication_doi']; url=f'https://joss.theoj.org/papers/{doi}'
    body,attempts=fetch(url,'text/html')
    out={'frozen_index':item['frozen_index'],'publication_doi':doi,'v4_identity':item,'joss':{'url':url,'attempts':attempts,'repository_links':[],'archive_links':[]}}
    if body is None: return out
    p=AnchorParser(); p.feed(body.decode('utf-8','replace'))
    repos=[]; archives=[]
    for a in p.anchors:
        label=a['text'].strip().casefold()
        if label=='software repository': repos.append({'href':a['href'],'label':a['text']})
        if label=='software archive': archives.append({'href':a['href'],'label':a['text'],'archive_doi':norm_doi(a['href'])})
    out['joss']['repository_links']=repos; out['joss']['archive_links']=archives
    out['joss']['repository_relation_status']='PASS' if len(repos)==1 else 'CANNOT_CHECK_LABELLED_REPOSITORY_RELATION_CARDINALITY'
    out['joss']['archive_relation_status']='PASS' if len(archives)==1 and archives[0]['archive_doi'] else 'CANNOT_CHECK_LABELLED_ARCHIVE_DOI_RELATION_CARDINALITY_OR_IDENTITY'
    out['archive_doi']=archives[0]['archive_doi'] if out['joss']['archive_relation_status']=='PASS' else None
    return out

def metadata_one(row):
    doi=row.get('archive_doi')
    if not doi: return row
    dc_url='https://api.datacite.org/dois/'+urllib.parse.quote(doi,safe='')
    body,attempts=fetch(dc_url)
    dc={'url':dc_url,'attempts':attempts,'metadata':None}
    if body is not None:
        try:
            a=json.loads(body).get('data',{}).get('attributes',{})
            dc['metadata']={k:a.get(k) for k in ['doi','version','rightsList','relatedIdentifiers','url','publisher','types','titles','alternateIdentifiers','container']}
        except Exception as e: dc['parse_error']=f'{type(e).__name__}:{e}'
    row['datacite']=dc
    m=re.fullmatch(r'10\.5281/zenodo\.(\d+)',doi,re.I)
    if m:
        zurl=f'https://zenodo.org/api/records/{m.group(1)}'
        zbody,zattempts=fetch(zurl)
        z={'url':zurl,'attempts':zattempts,'metadata':None}
        if zbody is not None:
            try:
                d=json.loads(zbody); md=d.get('metadata') or {}
                z['metadata']={
                    'id':d.get('id'),'recid':d.get('recid'),'doi':d.get('doi'),'conceptdoi':d.get('conceptdoi'),'conceptrecid':d.get('conceptrecid'),
                    'created':d.get('created'),'modified':d.get('modified'),'status':d.get('status'),'state':d.get('state'),'submitted':d.get('submitted'),
                    'version':md.get('version'),'license':md.get('license'),'access_right':md.get('access_right'),'resource_type':md.get('resource_type'),
                    'related_identifiers':md.get('related_identifiers'),'relations':md.get('relations'),'alternate_identifiers':md.get('alternate_identifiers'),
                    'swh':d.get('swh'),'files':[{'key':f.get('key'),'size':f.get('size'),'checksum':f.get('checksum'),'content_url':(f.get('links') or {}).get('self')} for f in d.get('files') or []],
                    'links':{k:(d.get('links') or {}).get(k) for k in ['self','doi','parent','parent_doi','latest','versions','archive']},
                }
            except Exception as e: z['parse_error']=f'{type(e).__name__}:{e}'
        row['zenodo']=z
    return row

def main():
    started=now(); identities=MANIFEST['identities']
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        rows=list(ex.map(joss_one,identities))
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        rows=list(ex.map(metadata_one,rows))
    rows.sort(key=lambda r:r['frozen_index'])
    out=ROOT/'HARVEST_RECORDS_V5.jsonl'
    out.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in rows))
    counts={
      'frozen_identities':len(rows),
      'joss_final_2xx':sum((r['joss']['attempts'][-1].get('http_status') or 0)//100==2 for r in rows if r['joss']['attempts']),
      'exactly_one_labelled_repository_relation':sum(r['joss'].get('repository_relation_status')=='PASS' for r in rows),
      'exactly_one_labelled_archive_doi_relation':sum(r['joss'].get('archive_relation_status')=='PASS' for r in rows),
      'datacite_final_2xx':sum((r.get('datacite',{}).get('attempts') or [{}])[-1].get('http_status',0)//100==2 for r in rows if r.get('datacite')),
      'zenodo_archive_dois':sum('zenodo' in r for r in rows),
      'zenodo_final_2xx':sum((r.get('zenodo',{}).get('attempts') or [{}])[-1].get('http_status',0)//100==2 for r in rows if r.get('zenodo')),
    }
    receipt={'schema_version':'orion.p4.m6.joss-exact-version-bridge.harvest-receipt.v5','created_at':now(),'started_at':started,'status':'BOUNDED_FROZEN_IDENTITY_HARVEST_COMPLETE','record_jsonl':str(out),'record_jsonl_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'counts':counts,'new_doi_identities_added':0,'replacement_identities_added':0,'case_text_labels_or_system_outcomes_accessed':False}
    (ROOT/'HARVEST_RECEIPT_V5.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__': main()
