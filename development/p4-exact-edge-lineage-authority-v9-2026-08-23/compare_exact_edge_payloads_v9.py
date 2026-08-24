#!/usr/bin/env python3
from pathlib import Path
import urllib.request,urllib.error,hashlib,json,tarfile,zipfile,tempfile,datetime,os
R=Path(__file__).resolve().parent
UA='ORION-P4-v9 exact-edge research'
targets={
 91:{'archive':'https://zenodo.org/api/records/20171460/files/THE_PU~1.GZ/content','commit':'9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59','repo':'NutritionalLungImmunity/PAI'},
 133:{'archive':'https://zenodo.org/api/records/20026885/files/woodtapper-0.0.13.tar.gz/content','commit':'7ac6d23d504404c4004faad663f6b889427109e6','repo':'artefactory/woodtapper'},
 165:{'archive':'https://zenodo.org/api/records/19661454/files/databallpy-0.7.3.zip/content','commit':'b52a049f685af3fc849359673c4ac183e7ccc5d3','repo':'Alek050/databallpy'},
}
def download(url,p):
 h=hashlib.sha256(); n=0
 req=urllib.request.Request(url,headers={'User-Agent':UA})
 with urllib.request.urlopen(req,timeout=240) as r, p.open('wb') as f:
  while True:
   b=r.read(1024*1024)
   if not b: break
   f.write(b);h.update(b);n+=len(b)
  return {'url':url,'status':r.status,'final_url':r.geturl(),'bytes':n,'sha256':h.hexdigest(),'content_type':r.headers.get('Content-Type')}
def manifest(p):
 out={}; kind=None
 if zipfile.is_zipfile(p):
  kind='zip'
  with zipfile.ZipFile(p) as z:
   infos=[x for x in z.infolist() if not x.is_dir()]
   roots={x.filename.split('/')[0] for x in infos if '/' in x.filename}
   for x in infos:
    rel='/'.join(x.filename.split('/')[1:]) if len(roots)==1 else x.filename
    d=z.read(x);out[rel]={'sha256':hashlib.sha256(d).hexdigest(),'bytes':len(d)}
 else:
  kind='tar'
  with tarfile.open(p,'r:*') as t:
   infos=[x for x in t.getmembers() if x.isfile() or x.issym()]
   roots={x.name.split('/')[0] for x in infos if '/' in x.name}
   for x in infos:
    rel='/'.join(x.name.split('/')[1:]) if len(roots)==1 else x.name
    if x.isfile():
     d=t.extractfile(x).read();out[rel]={'sha256':hashlib.sha256(d).hexdigest(),'bytes':len(d)}
    else: out[rel]={'symlink':x.linkname}
 return kind,out
res={'schema_version':'orion.p4.exact-edge-payload-comparison.v9','finished_at':None,'rows':[]}
with tempfile.TemporaryDirectory(prefix='p4v9-') as td:
 td=Path(td)
 for i,t in targets.items():
  ap=td/f'{i}_archive';cp=td/f'{i}_commit'
  ar=download(t['archive'],ap)
  cr=download(f'https://codeload.github.com/{t["repo"]}/legacy.tar.gz/{t["commit"]}',cp)
  ak,A=manifest(ap);ck,B=manifest(cp)
  oa=sorted(set(A)-set(B));ob=sorted(set(B)-set(A));df=sorted(x for x in set(A)&set(B) if A[x]!=B[x])
  row={'frozen_index':i,'archive':ar,'commit_archive':cr,'archive_kind':ak,'commit_kind':ck,'archive_file_count':len(A),'commit_file_count':len(B),'exact_normalized_manifest_equal':A==B,'archive_is_byte_identical_subset_of_commit_except_generated_paths':not df and all(x in {'PKG-INFO','METADATA'} or x.endswith(('/PKG-INFO','/METADATA')) for x in oa),'only_archive_count':len(oa),'only_commit_count':len(ob),'different_common_count':len(df),'only_archive':oa,'only_commit':ob,'different_common':df,'archive_manifest_sha256':hashlib.sha256(json.dumps(A,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'commit_manifest_sha256':hashlib.sha256(json.dumps(B,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
  res['rows'].append(row)
  print(i,len(A),len(B),A==B,len(oa),len(ob),len(df),row['archive_is_byte_identical_subset_of_commit_except_generated_paths'])
res['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(R/'EXACT_EDGE_PAYLOAD_COMPARISON_V9.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
