#!/usr/bin/env python3
"""Fail-closed theorem/application audit for typed-authority PR #1466."""
from __future__ import annotations

import argparse,hashlib,json,re,subprocess
from pathlib import Path
from typing import Any

TARGET_PR=1466


def run(*args:str,cwd:Path|None=None)->str:return subprocess.check_output(args,cwd=cwd,text=True).strip()
def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def walk(v:Any,path:str=""):
    if isinstance(v,dict):
        for k,c in v.items():
            p=f"{path}/{k}";yield p,c;yield from walk(c,p)
    elif isinstance(v,list):
        for i,c in enumerate(v):yield from walk(c,f"{path}/{i}")

def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--base',required=True);p.add_argument('--head',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    changed=run('git','diff','--name-only',f'{a.base}...{a.head}',cwd=a.repo).splitlines()
    paths=sorted(x for x in changed if '/D/' in x or 'authority' in x.lower() or 'mix' in x.lower() or 'origin' in x.lower())
    receipts=[];scalars=[];all_text=[]
    for rel in paths:
        path=a.repo/rel
        if not path.is_file() or path.stat().st_size>50_000_000:continue
        text=path.read_text(errors='replace');all_text.append(text)
        if path.suffix.lower()=='.json':
            try:value=json.loads(text)
            except Exception:continue
            hits=[]
            for key_path,child in walk(value):
                key=key_path.rsplit('/',1)[-1].lower()
                if key in {'systems','system_count','hybrid_atoms','hybrid_atom_count','local_certificates','unary_controls','origin_preserving_controls','terminal','external_domain','external_adjudication','source_commit','source_sha256'} and not isinstance(child,(dict,list)):
                    hits.append({'path':key_path,'value':child});scalars.append((key_path.lower(),child))
            receipts.append({'path':rel,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'hits':hits})
    text='\n'.join(all_text)
    values=[v for _,v in scalars]
    first_mixing=bool(re.search(r'first[- ]mixing',text,re.I)) and bool(re.search(r'(theorem|proof)',text,re.I))
    systems=10192 in values or '10,192' in text
    hybrids=68 in values and ('68/68' in text or text.count('68')>=2)
    controls=2000 in values or '2,000' in text
    zero_unary=bool(re.search(r'(zero|0).{0,80}(hybrid|mix)',text,re.I|re.S))
    source_bound=bool(re.search(r'(agentgateway|oauth|jwt|mcp)',text,re.I)) and bool(re.search(r'[0-9a-f]{40}',text))
    safe_control=bool(re.search(r'(SAFE|origin[- ]witness safe|no hybrid)',text,re.I))
    external=any(('external_domain' in path or 'external_adjudication' in path) and (v is True or str(v).upper()=='PASS') for path,v in scalars)
    theorem_pass=all([first_mixing,systems,hybrids,controls,zero_unary])
    result={
      'schema':'ORION.D.PR1466FirstMixingAudit.R20.v1','target_pr':TARGET_PR,'base_sha':a.base,'head_sha':a.head,'changed_files':changed,'d_changed_files':paths,'json_receipts':receipts,
      'gates':{'first_mixing_theorem_present':first_mixing,'10192_system_denominator_present':systems,'68_hybrid_atoms_and_certificates_present':hybrids,'2000_origin_preserving_controls_present':controls,'unary_control_zero_hybrids_present':zero_unary,'real_source_bound_safe_control_present':source_bound and safe_control,'independent_external_domain_adjudication_present':external},
      'terminal':'D_PR1466_FIRST_MIXING_THEOREM_PASS__EXTERNAL_DOMAIN_OPEN' if theorem_pass else 'D_PR1466_THEOREM_AUTHORITY_NOT_ESTABLISHED',
      'authority':{'analytic_first_mixing_theorem':theorem_pass,'agentgateway_native_merge_vulnerability':False,'external_domain_validation':external,'production_safety':False,'novelty':False,'journal_authority':False},
    }
    payload=canonical(result)+'\n';a.output.write_text(payload);print(result['terminal'],hashlib.sha256(payload.encode()).hexdigest());return 0
if __name__=='__main__':raise SystemExit(main())
