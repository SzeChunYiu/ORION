#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.metadata as md,json,os,platform,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
rows=[]; all_files=[]
for dist in md.distributions():
 m=dist.metadata; name=m.get('Name') or 'UNKNOWN'; version=dist.version
 classifiers=[x for x in (m.get_all('Classifier') or []) if x.startswith('License ::')]
 license_files=[]
 for rel in m.get_all('License-File') or []:
  p=Path(dist.locate_file(rel))
  if p.is_file():license_files.append({'declared':rel,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 files=[]
 for rel in dist.files or []:
  p=Path(dist.locate_file(rel))
  if p.is_file() and not p.is_symlink():
   rec={'path':str(rel),'bytes':p.stat().st_size,'sha256':sha(p)};files.append(rec);all_files.append({'distribution':name,'version':version,**rec})
 evidence={'license_expression':m.get('License-Expression'),'license':m.get('License'),'license_classifiers':classifiers,'license_files':license_files}
 has=bool(evidence['license_expression'] or evidence['license'] or classifiers or license_files)
 rows.append({'name':name,'version':version,'metadata_path':str(getattr(dist,'_path','')),'rights_evidence':evidence,'rights_status':'METADATA_OR_LICENSE_FILE_PRESENT__NOT_LEGAL_ADVICE' if has else 'ABSENT','installed_files':files,'installed_file_count':len(files)})
rows.sort(key=lambda x:(x['name'].casefold(),x['version']))
base=Path(sys.base_prefix)
base_files=[]
for p in sorted(base.rglob('*')):
 if p.is_file() and not p.is_symlink():base_files.append({'path':str(p.relative_to(base)),'bytes':p.stat().st_size,'sha256':sha(p)})
base_lic=[]
for rel in ['lib/python3.10/LICENSE.txt']:
 p=base/rel
 if p.is_file():base_lic.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
summary={'distribution_count':len(rows),'distributions_with_rights_evidence':sum(x['rights_status']!='ABSENT' for x in rows),'distributions_without_rights_evidence':sum(x['rights_status']=='ABSENT' for x in rows),'installed_distribution_file_records':len(all_files),'python_base_file_records':len(base_files),'python_base_license_files':len(base_lic)}
out={'schema_version':'orion.p3.repaired-native-runtime.python-sbom.v9','authority':'INSTALLED_DISTRIBUTION_METADATA_FILE_HASH_AND_BASE_RUNTIME_AUDIT__NO_DEEPONTO_IMPORT','environment':{'python':platform.python_version(),'implementation':platform.python_implementation(),'machine':platform.machine(),'executable':sys.executable,'base_prefix':sys.base_prefix,'prefix':sys.prefix},'summary':summary,'rights_gate':'PASS' if summary['distributions_without_rights_evidence']==0 and base_lic else 'CANNOT_CHECK_PYTHON_RIGHTS','distributions':rows,'python_base_runtime':{'root':str(base),'files':base_files,'license_files':base_lic}}
(ROOT/'PYTHON_RUNTIME_SBOM_V9.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'summary':summary,'rights_gate':out['rights_gate'],'missing':[x['name'] for x in rows if x['rights_status']=='ABSENT']},sort_keys=True))
