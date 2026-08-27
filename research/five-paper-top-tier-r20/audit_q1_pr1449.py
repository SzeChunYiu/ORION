#!/usr/bin/env python3
"""Fail-closed resource and novelty audit for Q1 PR #1449."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from typing import Any
TARGET_PR=1449

def run(*args:str,cwd:Path|None=None)->str:return subprocess.check_output(args,cwd=cwd,text=True).strip()
def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--base',required=True);p.add_argument('--head',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 changed=run('git','diff','--name-only',f'{a.base}...{a.head}',cwd=a.repo).splitlines();paths=sorted(x for x in changed if '/Q1/' in x or 'q1' in x.lower() or 'resource' in x.lower() or 'literature' in x.lower())
 rows=[];text_parts=[]
 for rel in paths:
  path=a.repo/rel
  if not path.is_file() or path.stat().st_size>20_000_000:continue
  text=path.read_text(errors='replace');text_parts.append(text);rows.append({'path':rel,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 text='\n'.join(text_parts)
 exact_nine=bool(re.search(r'(exactly|exact)\s+9|nine arbitrary-angle',text,re.I))
 conditional_logical=bool(re.search(r'conditional logical|all-to-all parity|two-qubit Clifford',text,re.I))
 ties=bool(re.search(r'90\s*/\s*90|90 of 90',text,re.I)) and bool(re.search(r'(tie|donor)',text,re.I))
 sensitivity=bool(re.search(r'18\s*/\s*90|18 of 90',text,re.I))
 partial='PARTIAL_RESOURCE_MAP' in text
 novelty_not='NOVELTY_NOT_ESTABLISHED' in text
 forbidden_absent=not bool(re.search(r'(physical|hardware).{0,50}(advantage|improvement).{0,50}(established|proved|verified)',text,re.I|re.S))
 symphony=bool(re.search(r'Symphony',text,re.I))
 measured=bool(re.search(r'Q1_PRODUCTION_RESOURCE_MAPPING_MATERIAL|APP_Q1_PRODUCTION_RESOURCE_MAPPING_MATERIAL',text))
 pass_map=all([exact_nine,conditional_logical,ties,sensitivity,partial,novelty_not,forbidden_absent])
 result={'schema':'ORION.Q1.PR1449ResourceAudit.R20.v1','target_pr':TARGET_PR,'base_sha':a.base,'head_sha':a.head,'changed_files':changed,'q1_changed_files':paths,'file_hashes':rows,'gates':{'nine_arbitrary_rotations_exact':exact_nine,'conditional_logical_two_qubit_map':conditional_logical,'primary_90_of_90_donor_ties_preserved':ties,'18_of_90_sensitivity_preserved':sensitivity,'partial_resource_map_terminal':partial,'novelty_not_established_terminal':novelty_not,'no_physical_advantage_promoted':forbidden_absent,'current_symphony_baseline_named':symphony,'measured_production_resource_terminal':measured},'terminal':'Q1_PR1449_PARTIAL_RESOURCE_MAP_AUDITED__MEASURED_BENCHMARK_OPEN' if pass_map else 'Q1_PR1449_RESOURCE_AUTHORITY_NOT_ESTABLISHED','authority':{'logical_template_map':pass_map,'production_resource_value':measured,'physical_resource_value':False,'novelty':False,'external_quantum_review':False,'journal_authority':False}}
 payload=canonical(result)+'\n';a.output.write_text(payload);print(result['terminal'],hashlib.sha256(payload.encode()).hexdigest());return 0
if __name__=='__main__':raise SystemExit(main())
