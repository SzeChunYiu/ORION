#!/usr/bin/env python3
"""Fail-closed production-registry audit for AB PR #1469."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

TARGET_PR=1469


def run(*args:str,cwd:Path|None=None)->str:
    return subprocess.check_output(args,cwd=cwd,text=True).strip()


def canonical(value:Any)->str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def walk(value:Any,path:str=""):
    if isinstance(value,dict):
        for key,child in value.items():
            child_path=f"{path}/{key}"
            yield child_path,child
            yield from walk(child,child_path)
    elif isinstance(value,list):
        for index,child in enumerate(value):
            yield from walk(child,f"{path}/{index}")


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--base',required=True)
    parser.add_argument('--head',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    changed=run('git','diff','--name-only',f'{args.base}...{args.head}',cwd=args.repo).splitlines()
    ab_changed=sorted(path for path in changed if '/AB/' in path or 'production' in path.lower() or 'registry' in path.lower() or 'rewrite' in path.lower())
    json_receipts=[]
    scalar=[]
    for relative in ab_changed:
        path=args.repo/relative
        if not path.is_file() or path.suffix.lower()!='.json' or path.stat().st_size>50_000_000:
            continue
        try:value=json.loads(path.read_text())
        except Exception:continue
        rows=[]
        for key_path,child in walk(value):
            key=key_path.rsplit('/',1)[-1].lower()
            if key in {
                'declared_complete','production_registry_complete','registry_complete',
                'source_digest','source_sha256','semantic_preservation','objective_nonincrease',
                'support_preservation','strict_support_descent','weak_move_lifting',
                'omission_hostile_audit','omitted_move_control','confluence','local_peak_joinability',
                'terminal','result_terminal','production_intrinsic_support','weak_terminal_complexity'
            } and not isinstance(child,(dict,list)):
                rows.append({'path':key_path,'value':child}); scalar.append((key_path.lower(),child))
        json_receipts.append({'path':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'hits':rows})
    text='\n'.join((args.repo/path).read_text(errors='replace') for path in ab_changed if (args.repo/path).is_file() and (args.repo/path).stat().st_size<10_000_000)
    blocker_seen='PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE' in text
    pass_terminal='PRODUCTION_EXACT_TRANSFER_PASS' in text or 'PROOF_LANGUAGE_WASTE_CERTIFIED' in text
    def truth(keys:set[str])->bool:
        return any(any(path.endswith('/'+key) for key in keys) and (value is True or str(value).upper() in {'PASS','TRUE','VERIFIED','COMPLETE'}) for path,value in scalar)
    complete=truth({'declared_complete','production_registry_complete','registry_complete'})
    source_bound=any(('source_digest' in path or 'source_sha256' in path) and isinstance(value,str) and len(value)>=40 for path,value in scalar)
    semantic=truth({'semantic_preservation'})
    objective=truth({'objective_nonincrease'})
    support=truth({'support_preservation'}) and truth({'strict_support_descent'})
    lifting=truth({'weak_move_lifting'})
    omission=truth({'omission_hostile_audit','omitted_move_control'})
    interactions=truth({'confluence','local_peak_joinability'})
    executable_registry=bool(re.search(r'(enum|list|registry).{0,80}(rewrite|move)',text,re.IGNORECASE|re.DOTALL))
    pass_gate=all([complete,source_bound,semantic,objective,support,lifting,omission,interactions,executable_registry,pass_terminal]) and not blocker_seen
    result={
        'schema':'ORION.AB.PR1469ProductionRegistryAudit.R20.v1',
        'target_pr':TARGET_PR,'base_sha':args.base,'head_sha':args.head,
        'changed_files':changed,'ab_changed_files':ab_changed,'json_receipts':json_receipts,
        'gates':{
            'registry_declared_complete':complete,
            'registry_source_content_bound':source_bound,
            'semantic_preservation_verified':semantic,
            'objective_nonincrease_verified':objective,
            'support_preservation_and_descent_verified':support,
            'every_weak_move_lifted':lifting,
            'omitted_move_hostile_control':omission,
            'interaction_joinability_verified':interactions,
            'executable_move_registry_present':executable_registry,
            'typed_transfer_terminal_present':pass_terminal,
            'incomplete_registry_blocker_absent':not blocker_seen,
        },
        'terminal':'AB_PR1469_PRODUCTION_REGISTRY_PASS' if pass_gate else 'AB_PR1469_PRODUCTION_TRANSFER_NOT_ESTABLISHED',
        'authority':{
            'production_transfer':pass_gate,
            'quantum_compiler_transfer':False,
            'measured_search_value':False,
            'external_independence':False,
            'journal_authority':False,
        },
    }
    payload=canonical(result)+'\n';args.output.write_text(payload)
    print(result['terminal'],hashlib.sha256(payload.encode()).hexdigest())
    return 0

if __name__=='__main__':raise SystemExit(main())
