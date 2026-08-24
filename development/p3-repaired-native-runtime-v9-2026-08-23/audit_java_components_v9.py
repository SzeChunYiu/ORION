#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'runtime/source'
OUT=ROOT/'JAVA_COMPONENT_SBOM_V9.json'

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''): h.update(x)
 return h.hexdigest()
def text_clean(b):
 try: return b.decode('utf-8','replace')[:200000]
 except Exception:return ''
def pom_licenses(xml):
 try:
  root=ET.fromstring(xml)
 except Exception:return []
 out=[]
 for e in root.iter():
  if e.tag.rsplit('}',1)[-1]=='license':
   row={}
   for c in e:
    k=c.tag.rsplit('}',1)[-1]
    if k in {'name','url','distribution','comments'} and c.text: row[k]=c.text.strip()
   if row: out.append(row)
 return out
def properties(b):
 d={}
 for line in text_clean(b).splitlines():
  line=line.strip()
  if line and not line.startswith('#') and '=' in line:
   k,v=line.split('=',1);d[k.strip()]=v.strip()
 return d
rows=[]
for p in sorted(SRC.rglob('*.jar')):
 rel=str(p.relative_to(SRC))
 row={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'zip_valid':False,'coordinates':[],'embedded_rights_files':[],'pom_licenses':[],'manifest':{}}
 try:
  with zipfile.ZipFile(p) as z:
   bad=z.testzip(); row['zip_valid']=bad is None; row['zip_bad_member']=bad
   names=z.namelist()
   for n in names:
    low=n.lower(); base=low.rsplit('/',1)[-1]
    if low=='meta-inf/manifest.mf':
     m=text_clean(z.read(n))
     for line in m.splitlines():
      if ':' in line:
       k,v=line.split(':',1)
       if k in {'Implementation-Title','Implementation-Version','Bundle-Name','Bundle-SymbolicName','Bundle-Version','Automatic-Module-Name','Specification-Title','Specification-Version'}: row['manifest'][k]=v.strip()
    if low.startswith('meta-inf/maven/') and low.endswith('/pom.properties'):
     d=properties(z.read(n));
     if d: row['coordinates'].append({'source':n,**d})
    if low.startswith('meta-inf/maven/') and low.endswith('/pom.xml'):
     ls=pom_licenses(z.read(n)); row['pom_licenses'].extend({'source':n,**x} for x in ls)
    if base.startswith(('license','licence','copying','notice','copyright')) or base in {'about.html','about_files'}:
     if not low.endswith('/'):
      b=z.read(n)
      row['embedded_rights_files'].append({'path':n,'bytes':len(b),'sha256':sha_bytes(b),'preview':text_clean(b)[:240].replace('\n',' ')})
 except Exception as e: row['zip_error']=f'{type(e).__name__}: {e}'
 row['coordinates']=sorted(row['coordinates'],key=lambda x:x.get('source',''))
 row['embedded_rights_files']=sorted(row['embedded_rights_files'],key=lambda x:x['path'])
 row['pom_licenses']=sorted(row['pom_licenses'],key=lambda x:(x.get('name',''),x.get('url','')))
 rows.append(row)
by={}
for r in rows:
 u=by.setdefault(r['sha256'],{'sha256':r['sha256'],'bytes':r['bytes'],'paths':[],'coordinates':[],'embedded_rights_files':[],'pom_licenses':[],'manifests':[],'zip_valid':True})
 u['paths'].append(r['path']);u['coordinates']+=r['coordinates'];u['embedded_rights_files']+=r['embedded_rights_files'];u['pom_licenses']+=r['pom_licenses'];u['manifests'].append(r['manifest']);u['zip_valid'] &= r['zip_valid']
unique=[]
for u in by.values():
 # dedup structured rows
 for key in ['coordinates','embedded_rights_files','pom_licenses','manifests']:
  seen=set(); vals=[]
  for x in u[key]:
   s=json.dumps(x,sort_keys=True)
   if s not in seen:seen.add(s);vals.append(x)
  u[key]=vals
 u['paths']=sorted(u['paths'])
 if u['embedded_rights_files'] or u['pom_licenses']:
  u['rights_evidence']='EMBEDDED_LICENSE_OR_POM_METADATA_PRESENT__ADJUDICATION_REQUIRED'
 else:u['rights_evidence']='ABSENT'
 unique.append(u)
unique.sort(key=lambda x:x['sha256'])
summary={'tracked_jar_paths':len(rows),'unique_jar_hashes':len(unique),'zip_valid_paths':sum(r['zip_valid'] for r in rows),'unique_with_embedded_or_pom_rights_metadata':sum(u['rights_evidence']!='ABSENT' for u in unique),'unique_without_rights_metadata':sum(u['rights_evidence']=='ABSENT' for u in unique)}
out={'schema_version':'orion.p3.repaired-native-runtime.java-component-sbom.v9','authority':'STATIC_JAR_ZIP_METADATA_AND_RIGHTS_EVIDENCE_AUDIT_ONLY__NO_JAR_EXECUTED','source_commit':'74ca8d47f01bad0b8739f19ee2c392bdf6d9c090','source_tree':'b499cb5780bbe749f7db44d0bc872d275a2737ea','summary':summary,'rights_gate':'PASS' if summary['unique_without_rights_metadata']==0 and summary['zip_valid_paths']==summary['tracked_jar_paths'] else 'CANNOT_CHECK_COMPONENT_RIGHTS_OR_INTEGRITY','unique_components':unique,'path_inventory':rows}
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'summary':summary,'rights_gate':out['rights_gate']},sort_keys=True))
