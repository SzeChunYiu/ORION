#!/usr/bin/env python3
"""Fail-closed exact-subject audit for NQ PR #1472.

This auditor does not infer scientific success from filenames or CI. It scans
all changed NQ receipts, requires the complete registered denominators, verifies
that every claimed proof checker is explicitly external, and rejects circular
use of the conditional D3=25 completion/factorization specialization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

TARGET_PR = 1472
EXPECTED_MATRIX_DENOMINATOR = 98622
EXPECTED_CANDIDATE_DENOMINATOR = 230983


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def walk(value: Any, path: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}/{key}"
            yield child_path, child
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}/{index}")


def scalar_hits(value: Any, wanted: set[str]) -> list[dict[str, Any]]:
    rows=[]
    for path, child in walk(value):
        key=path.rsplit('/',1)[-1].lower()
        if key in wanted and not isinstance(child,(dict,list)):
            rows.append({'path':path,'value':child})
    return rows


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--base',required=True)
    parser.add_argument('--head',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    repo=args.repo
    changed=run('git','diff','--name-only',f'{args.base}...{args.head}',cwd=repo).splitlines()
    nq_changed=sorted(path for path in changed if '/NQ/' in path or 'davenport' in path.lower() or 'zero-sum' in path.lower())
    json_rows=[]
    parse_failures=[]
    for relative in nq_changed:
        if not relative.endswith('.json'):
            continue
        path=repo/relative
        if not path.is_file() or path.stat().st_size>50_000_000:
            continue
        try:
            value=json.loads(path.read_text())
        except Exception as exc:
            parse_failures.append({'path':relative,'error':type(exc).__name__})
            continue
        hits=scalar_hits(value,{
            'full_census_executed','independent_replay_authority','scientific_authority',
            'matrix_count','matrix_denominator','candidate_count','candidate_denominator',
            'external_proof_check','external_proof_checker','all_unsat_proofs_verified',
            'terminal','result_terminal','authority_terminal','d2','d3','d_2','d_3'
        })
        json_rows.append({'path':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'hits':hits})

    text_rows=[]
    forbidden=[]
    for relative in nq_changed:
        path=repo/relative
        if not path.is_file() or path.suffix.lower() not in {'.py','.md','.json','.yml','.yaml','.sh'} or path.stat().st_size>10_000_000:
            continue
        text=path.read_text(errors='replace')
        text_rows.append({'path':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        patterns={
            'conditional_D3_value':r'D_?3\s*\(?C_?5\^?3\)?\s*=\s*25',
            'completion_specialization':r'(rooted|completion|factorization).{0,120}D_?3.{0,40}25',
            'forbidden_outcome_import':r'(import|read|load|open).{0,160}(completion|factorization|invariant_kernel|D3_25)',
        }
        for name,pattern in patterns.items():
            if re.search(pattern,text,re.IGNORECASE|re.DOTALL):
                forbidden.append({'path':relative,'pattern':name})

    flattened=[hit for row in json_rows for hit in row['hits']]
    values=[hit['value'] for hit in flattened]
    paths=[hit['path'].lower() for hit in flattened]
    full_true=any(path.endswith('/full_census_executed') and value is True for path,value in zip(paths,values))
    matrix_complete=EXPECTED_MATRIX_DENOMINATOR in values
    candidate_complete=EXPECTED_CANDIDATE_DENOMINATOR in values
    external_proofs=any(
        ('external_proof' in path or 'all_unsat_proofs_verified' in path)
        and (value is True or str(value).upper() in {'PASS','VERIFIED','ALL_VERIFIED'})
        for path,value in zip(paths,values)
    )
    replay_pass=any(
        ('terminal' in path) and ('PASS' in str(value).upper()) and ('NQ' in str(value).upper() or 'REPLAY' in str(value).upper())
        for path,value in zip(paths,values)
    )
    circular_block=bool(forbidden)
    pass_gate=all([full_true,matrix_complete,candidate_complete,external_proofs,replay_pass]) and not circular_block
    result={
        'schema':'ORION.NQ.PR1472ExactSubjectAudit.R20.v1',
        'target_pr':TARGET_PR,
        'base_sha':args.base,
        'head_sha':args.head,
        'changed_files':changed,
        'nq_changed_files':nq_changed,
        'json_receipts':json_rows,
        'parse_failures':parse_failures,
        'forbidden_circular_inputs':forbidden,
        'gates':{
            'full_census_executed_true':full_true,
            'matrix_denominator_98622_present':matrix_complete,
            'candidate_denominator_230983_present':candidate_complete,
            'external_unsat_proofs_verified':external_proofs,
            'typed_NQ_replay_PASS_present':replay_pass,
            'conditional_D3_25_not_used_by_replay':not circular_block,
        },
        'terminal':'NQ_PR1472_FULL_REPLAY_SUBJECT_PASS' if pass_gate else 'NQ_PR1472_NOT_FULL_REPLAY_AUTHORITY',
        'authority':{
            'D2_D3_numerical_authority':pass_gate,
            'D4_authority':False,
            'external_independence':False,
            'journal_authority':False,
        },
    }
    payload=canonical(result)+'\n'
    args.output.write_text(payload)
    print(result['terminal'],hashlib.sha256(payload.encode()).hexdigest())
    return 0


if __name__=='__main__':
    raise SystemExit(main())
