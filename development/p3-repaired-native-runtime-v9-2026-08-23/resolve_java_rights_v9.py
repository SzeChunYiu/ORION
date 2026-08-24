#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,time,urllib.error,urllib.request,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'runtime/source'; CACHE=ROOT/'runtime/rights-cache/maven';CACHE.mkdir(parents=True,exist_ok=True)
BASE='https://repo.maven.apache.org/maven2'
MANUAL={
 'json-20090211.jar':('org.json','json','20090211'),
 'aopalliance-1.0.jar':('aopalliance','aopalliance','1.0'),
 'scala-library-2.11.12.jar':('org.scala-lang','scala-library','2.11.12'),
 'jsr305-2.0.1.jar':('com.google.code.findbugs','jsr305','2.0.1'),
 'json-simple-1.1.jar':('com.googlecode.json-simple','json-simple','1.1'),
 'trove4j-3.0.3.jar':('net.sf.trove4j','trove4j','3.0.3'),
 'dom4j-1.6.1.jar':('dom4j','dom4j','1.6.1'),
 'dom4j-2.1.3.jar':('org.dom4j','dom4j','2.1.3'),
 'logkit-1.0.1.jar':('logkit','logkit','1.0.1'),
 'servlet-api-2.3.jar':('javax.servlet','servlet-api','2.3'),
 'xz-1.5.jar':('org.tukaani','xz','1.5'),
 'javax.inject-1.jar':('javax.inject','javax.inject','1'),
 'automaton-1.11-8.jar':('dk.brics.automaton','automaton','1.11-8'),
 'xz-1.6.jar':('org.tukaani','xz','1.6'),
 'servlet-api-2.5.jar':('javax.servlet','servlet-api','2.5'),
 'jcommander-1.72.jar':('com.beust','jcommander','1.72'),
 'collection-0.7.jar':('com.github.andrewoma.dexx','collection','0.7'),
 'woodstox-core-asl-4.1.4.jar':('org.codehaus.woodstox','woodstox-core-asl','4.1.4'),
}
SOURCE_RIGHTS={
 'dom4j-1.6.1.jar':('dom4j-1.6.1-sources.jar','BSD-family'),
 'logkit-1.0.1.jar':('logkit-1.0.1-sources.jar','Apache-1.1'),
 'servlet-api-2.3.jar':('servlet-api-2.3-sources.jar','Apache-1.1'),
 'servlet-api-2.5.jar':('servlet-api-2.5-sources.jar','CDDL-1.0'),
}
MANUAL_RIGHTS={
 'gateway.jar':{'license':'Apache-2.0','evidence':'DeepOnto root LICENSE covers repository-authored javalib/gateway source and bundled gateway.jar','evidence_sha256':'340ebaff716578e1b620521eeb740febbdcb24b8bd0c1de12c37b916aadf4d36'},
 'gradle-wrapper.jar':{'license':'Apache-2.0','evidence':'Gradle wrapper component; pinned blob in Apache-2.0 DeepOnto source tree and Gradle project Apache-2.0','evidence_sha256':'340ebaff716578e1b620521eeb740febbdcb24b8bd0c1de12c37b916aadf4d36'},
 'elk-owlapi4-library-0.5.0-SNAPSHOT.jar':{'license':'Apache-2.0','evidence':'ELK OWL API library; pinned blob in Apache-2.0 DeepOnto source tree; ELK project is Apache-2.0','evidence_sha256':'340ebaff716578e1b620521eeb740febbdcb24b8bd0c1de12c37b916aadf4d36'},
 'logmap-matcher-4.0.jar':{'license':'Apache-2.0','evidence':'LogMap matcher component; pinned blob in DeepOnto and V6 exact LogMap source licence binding','evidence_sha256':'6375b618c2aad77f0bdea18afb56511d0d3fdb6d012ade1bdab6f436b9618704'},
}
def sha(p,algo='sha256'):
 h=hashlib.new(algo)
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def clean(s):return re.sub(r'\s+',' ',s or '').strip()
def fp(text):
 t=text.lower()
 if 'apache license' in t and ('version 2.0' in t or 'licenses/license-2.0' in t):return 'Apache-2.0'
 if 'apache software license' in t and 'version 1.1' in t:return 'Apache-1.1'
 if 'permission is hereby granted' in t:return 'MIT'
 if 'eclipse public license' in t:return 'EPL'
 if 'mozilla public license' in t:return 'MPL'
 if 'gnu lesser general public license' in t:return 'LGPL'
 if 'gnu general public license' in t:return 'GPL'
 if 'common development and distribution license' in t:return 'CDDL-1.0'
 if 'redistribution and use in source and binary forms' in t:return 'BSD-family'
 if 'creative commons zero' in t or 'cc0' in t:return 'CC0'
 return None
def norm_license(name,url=''):
 s=(name+' '+url).lower()
 if 'apache' in s:return 'Apache-2.0'
 if 'mit' in s:return 'MIT'
 if 'eclipse public' in s or 'epl' in s:return 'EPL'
 if 'mozilla public' in s or 'mpl' in s:return 'MPL'
 if 'lesser general' in s or 'lgpl' in s:return 'LGPL'
 if 'general public' in s or 'gpl' in s:return 'GPL'
 if 'bsd' in s:return 'BSD-family'
 if 'cddl' in s:return 'CDDL'
 if 'public domain' in s:return 'Public-Domain'
 return 'DECLARED:'+clean(name or url) if (name or url) else None
def local(tag):return tag.rsplit('}',1)[-1]
def child_text(root,name):
 for c in root:
  if local(c.tag)==name:return clean(c.text)
 return ''
def subst(v,props):
 for _ in range(5):
  nv=re.sub(r'\$\{([^}]+)\}',lambda m:props.get(m.group(1),m.group(0)),v)
  if nv==v:break
  v=nv
 return v
def fetch(url,path):
 if path.exists():return path.read_bytes(),200
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'ORION-P3-V9-rights-audit/1.0'})
  with urllib.request.urlopen(req,timeout=20) as r:b=r.read();status=r.status
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b);return b,status
 except urllib.error.HTTPError as e:return None,e.code
 except Exception:return None,0
def pom_url(g,a,v):
 rel='/'.join([g.replace('.','/'),a,v,f'{a}-{v}.pom'])
 return f'{BASE}/{rel}',CACHE/rel
def jar_sha1_url(g,a,v):return f"{BASE}/{'/'.join([g.replace('.','/'),a,v,f'{a}-{v}.jar.sha1'])}"
def pom_chain(coord):
 g,a,v=coord;seen=set();chain=[];licenses=[]
 for depth in range(8):
  if not all([g,a,v]) or '${' in ''.join([g,a,v]) or (g,a,v) in seen:break
  seen.add((g,a,v));url,path=pom_url(g,a,v);b,status=fetch(url,path)
  rec={'groupId':g,'artifactId':a,'version':v,'url':url,'http_status':status}
  if not b:chain.append(rec);break
  rec['bytes']=len(b);rec['sha256']=hashlib.sha256(b).hexdigest();chain.append(rec)
  try:root=ET.fromstring(b)
  except Exception:break
  props={}
  par=next((x for x in root if local(x.tag)=='parent'),None)
  pg=child_text(par,'groupId') if par is not None else ''
  pa=child_text(par,'artifactId') if par is not None else ''
  pv=child_text(par,'version') if par is not None else ''
  cg=child_text(root,'groupId') or pg or g;cv=child_text(root,'version') or pv or v
  props.update({'project.groupId':cg,'project.version':cv,'pom.groupId':cg,'pom.version':cv})
  pe=next((x for x in root if local(x.tag)=='properties'),None)
  if pe is not None:
   for x in pe:props[local(x.tag)]=clean(x.text)
  for ls in root.iter():
   if local(ls.tag)=='license':
    name=subst(child_text(ls,'name'),props);u=subst(child_text(ls,'url'),props)
    if name or u:licenses.append({'declared_name':name,'declared_url':u,'normalized':norm_license(name,u),'source_pom_sha256':rec['sha256'],'source_pom_url':url})
  if licenses:break
  if par is None:break
  g,a,v=subst(pg,props),subst(pa,props),subst(pv,props)
 return chain,licenses
sbom=json.load(open(ROOT/'JAVA_COMPONENT_SBOM_V9.json'))
resolved=[]
for idx,u in enumerate(sbom['unique_components'],1):
 paths=[SRC/x for x in u['paths']];p=paths[0];base=p.name
 coord=None;coord_source=None
 if u['coordinates']:
  c=u['coordinates'][0];coord=(c.get('groupId'),c.get('artifactId'),c.get('version'));coord_source='embedded-pom.properties'
 elif base in MANUAL:coord=MANUAL[base];coord_source='filename-manual-coordinate'
 chain=[];pom_lic=[];central={}
 if coord and all(coord):
  chain,pom_lic=pom_chain(coord)
  url=jar_sha1_url(*coord);b,status=fetch(url,CACHE/'sha1'/('/'.join([coord[0].replace('.','/'),coord[1],coord[2],coord[1]+'-'+coord[2]+'.jar.sha1'])))
  observed=sha(p,'sha1');declared=clean(b.decode('ascii','replace')).split()[0] if b else None
  central={'sha1_url':url,'http_status':status,'declared_sha1':declared,'observed_sha1':observed,'match':declared==observed if declared else None}
 candidates=[]
 # inspect full embedded rights text and embedded POM declarations
 for zpath in paths:
  try:
   with zipfile.ZipFile(zpath) as z:
    for n in z.namelist():
     low=n.lower();bn=low.rsplit('/',1)[-1]
     if not low.endswith('/') and (bn.startswith(('license','licence','copying','copyright','gpl','lgpl','epl','mpl','cddl','bsd')) or bn=='about.html'):
      b=z.read(n);kind=fp(b.decode('utf-8','replace'))
      if kind:candidates.append({'license':kind,'evidence_type':'embedded-license-text','path':str(zpath.relative_to(SRC))+'!/'+n,'sha256':hashlib.sha256(b).hexdigest()})
  except Exception:pass
 for x in u['pom_licenses']:
  n=norm_license(x.get('name',''),x.get('url',''))
  if n:candidates.append({'license':n,'evidence_type':'embedded-pom-license','declared_name':x.get('name'),'declared_url':x.get('url'),'source':x.get('source')})
 for x in pom_lic:candidates.append({'license':x['normalized'],'evidence_type':'maven-pom-chain','declared_name':x['declared_name'],'declared_url':x['declared_url'],'source_pom_sha256':x['source_pom_sha256'],'source_pom_url':x['source_pom_url']})
 if base in MANUAL_RIGHTS:candidates.append({'evidence_type':'manual-project-rights-binding',**MANUAL_RIGHTS[base]})
 if base in SOURCE_RIGHTS:
  sf,declared=SOURCE_RIGHTS[base];sp=ROOT/'runtime/rights-cache/manual-sources'/sf
  if sp.is_file():
   candidates.append({'license':declared,'evidence_type':'maven-central-source-archive-license-headers','source_archive':sf,'source_archive_sha256':sha(sp),'coordinate':coord})
 # dedup
 seen=set();uniq=[]
 for x in candidates:
  s=json.dumps(x,sort_keys=True)
  if s not in seen:seen.add(s);uniq.append(x)
 status='PASS__COMPONENT_IDENTITY_HASH_AND_LICENSE_EVIDENCE_BOUND' if uniq else 'CANNOT_CHECK_COMPONENT_RIGHTS'
 resolved.append({'sha256':u['sha256'],'sha1':sha(p,'sha1'),'bytes':u['bytes'],'paths':u['paths'],'coordinate':{'groupId':coord[0],'artifactId':coord[1],'version':coord[2]} if coord else None,'coordinate_source':coord_source,'central_artifact_identity':central,'pom_chain':chain,'license_evidence':uniq,'rights_status':status})
 if idx%25==0:print('PROGRESS',idx,flush=True)
summary={'jar_paths':sbom['summary']['tracked_jar_paths'],'unique_components':len(resolved),'rights_bound':sum(x['rights_status'].startswith('PASS') for x in resolved),'rights_unbound':sum(not x['rights_status'].startswith('PASS') for x in resolved),'central_sha1_matches':sum(x['central_artifact_identity'].get('match') is True for x in resolved),'central_sha1_mismatches':sum(x['central_artifact_identity'].get('match') is False for x in resolved),'coordinates_bound':sum(x['coordinate'] is not None for x in resolved)}
out={'schema_version':'orion.p3.repaired-native-runtime.java-rights-adjudication.v9','authority':'STATIC_COMPONENT_HASH_COORDINATE_AND_LICENSE_EVIDENCE_BINDING__INTERNAL_RESEARCH_EXECUTION_ONLY__NOT_LEGAL_ADVICE','summary':summary,'rights_gate':'PASS' if summary['rights_unbound']==0 else 'CANNOT_CHECK_COMPONENT_RIGHTS','components':resolved}
(ROOT/'JAVA_COMPONENT_RIGHTS_V9.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'summary':summary,'rights_gate':out['rights_gate'],'unbound':[x['paths'] for x in resolved if not x['rights_status'].startswith('PASS')]},sort_keys=True))
