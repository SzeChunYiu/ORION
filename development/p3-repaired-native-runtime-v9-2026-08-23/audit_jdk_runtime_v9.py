#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,platform,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
JAVA_HOME=Path('/opt/homebrew/Cellar/openjdk@17/17.0.19/libexec/openjdk.jdk/Contents/Home')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
files=[];legal=[]
for p in sorted(JAVA_HOME.rglob('*')):
 if p.is_file() and not p.is_symlink():
  r={'path':str(p.relative_to(JAVA_HOME)),'bytes':p.stat().st_size,'sha256':sha(p)};files.append(r)
  if r['path'].startswith('legal/'):legal.append(r)
version=subprocess.run([str(JAVA_HOME/'bin/java'),'-version'],capture_output=True,text=True,check=True).stderr.strip()
base_license=next((x for x in legal if x['path']=='legal/java.base/LICENSE'),None)
out={'schema_version':'orion.p3.repaired-native-runtime.jdk-manifest.v9','authority':'SYSTEM_JDK_CONTENT_AND_LEGAL_FILE_HASH_BINDING','java_home':str(JAVA_HOME),'java_version':version,'machine':platform.machine(),'files':files,'legal_files':legal,'summary':{'file_count':len(files),'legal_file_count':len(legal),'bytes':sum(x['bytes'] for x in files)},'base_license':base_license,'rights_gate':'PASS__GPL_2_0_WITH_CLASSPATH_EXCEPTION_AND_BUNDLED_COMPONENT_LEGAL_FILES_PRESENT' if base_license and legal else 'CANNOT_CHECK_JDK_RIGHTS'}
(ROOT/'JDK_RUNTIME_MANIFEST_V9.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'summary':out['summary'],'rights_gate':out['rights_gate'],'base_license':base_license},sort_keys=True))
