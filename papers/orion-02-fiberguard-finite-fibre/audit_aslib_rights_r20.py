#!/usr/bin/env python3
"""Content-bound public-source and rights preflight for ORION-02."""
from __future__ import annotations
import argparse,base64,hashlib,json,os,urllib.error,urllib.request
from typing import Any

REPO='coseal/aslib_data';COMMIT='551b22beef8df17de59286b4822ef720e0aa4d6f'
SCENARIOS=('SAT12-ALL','SAT11-HAND-ALGO','MAXSAT12-PMS','MAXSAT19-UCMS','QBF-2016')

def api(url:str)->Any:
 headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'ORION-02-rights-audit'}
 token=os.environ.get('GITHUB_TOKEN')
 if token:headers['Authorization']=f'Bearer {token}'
 request=urllib.request.Request(url,headers=headers)
 try:
  with urllib.request.urlopen(request,timeout=60) as response:return json.load(response)
 except urllib.error.HTTPError as exc:
  if exc.code==404:return None
  raise

def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 license_obj=api(f'https://api.github.com/repos/{REPO}/license?ref={COMMIT}')
 tree=api(f'https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1')
 if not tree or tree.get('truncated'):raise SystemExit('complete source tree unavailable')
 paths=sorted(row['path'] for row in tree['tree'] if row['type']=='blob')
 candidates=[path for path in paths if path.rsplit('/',1)[-1].lower() in {'license','license.txt','license.md','copying','copying.txt','copyright'}]
 scenario_rows=[]
 for scenario in SCENARIOS:
  present=any(path.startswith(scenario+'/') for path in paths)
  local=[path for path in candidates if path.startswith(scenario+'/')]
  description=f'{scenario}/description.txt'
  scenario_rows.append({'scenario':scenario,'present_at_commit':present,'description_present':description in paths,'scenario_local_license_files':local})
 root_license=None
 if license_obj:
  content=base64.b64decode(license_obj.get('content',''))
  root_license={'path':license_obj.get('path'),'sha':license_obj.get('sha'),'spdx_id':license_obj.get('license',{}).get('spdx_id'),'name':license_obj.get('license',{}).get('name'),'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}
 explicit_all=bool(root_license and root_license['spdx_id'] not in {None,'NOASSERTION','OTHER'})
 scenario_local_all=all(row['scenario_local_license_files'] for row in scenario_rows)
 result={'schema':'ORION.ORION02.ASlibRightsAudit.R20.v1','repository':REPO,'commit':COMMIT,'root_license':root_license,'all_license_like_files':candidates,'scenarios':scenario_rows,'terminal':'ASLIB_REPOSITORY_LICENSE_PRESENT__SCENARIO_DATA_RIGHTS_REQUIRE_AUTHOR_REVIEW' if explicit_all else 'CANNOT_CHECK_ASLIB_REPOSITORY_LICENSE','authority':{'repository_license_identified':explicit_all,'scenario_local_license_for_every_used_subject':scenario_local_all,'legal_interpretation_complete':False,'redistribution_authorized':False,'journal_data_rights_complete':False}}
 payload=canonical(result)+'\n';open(a.output,'w').write(payload);print(result['terminal'],hashlib.sha256(payload.encode()).hexdigest());return 0
if __name__=='__main__':raise SystemExit(main())
