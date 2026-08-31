#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve();ROOT=HERE.parent.parent;RESULT=ROOT/'RESULT.json';OUT=ROOT/'GENERIC_RESULT.json'
SOURCES=['engine_high_u128.c','engine_high_avx.c','engine_rank3_u128.c','engine_rank3_avx.c','engine_c4rank2_u128.c','engine_c4rank2_avx.c']
def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def expected_keys():
 full=json.loads((ROOT/'FULL_CUBE_COVER.json').read_text());z=[]
 for b in full['lower_branches']+full['upper_branches']:
  z.append(f"s{b['support']}:a{b['a1']}:b{b['b2']}:c{b['c4']}:{b['branch']}")
 return sorted(z)
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=OUT);z=a.parse_args();r=json.loads(RESULT.read_text());u=dict(r);dig=u.pop('result_digest',None)
 rows=r.get('runs',[]);branches=r.get('branches',[]);by={}
 for q in rows:by.setdefault(q['key'],{})[q['engine']]=q
 checks={'schema':r.get('schema')=='ORION.ORION04.GlobalSupport14To31DualReplayResult.v1','result_digest':dig==sha(canon(u).encode()),'subject_bound':r.get('subject_main_sha')=='b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8','run_count_156':len(rows)==156,'branch_count_78':len(branches)==78,'key_cover_exact':sorted(by)==expected_keys(),'source_hashes':True,'all_pairs':True,'all_exact':True,'all_zero':True,'all_clean':True,'authority_fail_closed':r.get('external_independent_replay_complete') is False and r.get('novelty_authority') is False and r.get('venue_authority') is False and r.get('submission_authority') is False}
 obs=r.get('source_sha256',{})
 mapping={'engine_high_u128.c':('high','u128'),'engine_high_avx.c':('high','avx'),'engine_rank3_u128.c':('rank3','u128'),'engine_rank3_avx.c':('rank3','avx'),'engine_c4rank2_u128.c':('c4rank2','u128'),'engine_c4rank2_avx.c':('c4rank2','avx')}
 for f in SOURCES:
  fam,e=mapping[f];checks['source_hashes']&=obs.get(fam,{}).get(e)==sha((ROOT/f).read_bytes())
 for k,p in by.items():
  checks['all_pairs']&=set(p)=={'u128','avx'}
  if set(p)=={'u128','avx'}:
   checks['all_exact']&=p['u128']['stdout']==p['avx']['stdout'] and p['u128']['stdout_sha256']==sha(p['u128']['stdout'].encode()) and p['avx']['stdout_sha256']==sha(p['avx']['stdout'].encode())
   checks['all_zero']&=p['u128']['solutions']==0 and p['avx']['solutions']==0 and bool(re.search(r'solutions=0',p['u128']['stdout']))
   checks['all_clean']&=p['u128']['returncode']==0 and p['avx']['returncode']==0 and not p['u128']['stderr'] and not p['avx']['stderr']
 checks['runner_checks']=all(r.get('checks',{}).values());checks['terminal']=r.get('terminal')=='ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30';good=all(checks.values())
 out={'schema':'ORION.ORION04.GlobalIndependentVerification.v1','decision':'ACCEPT_ORION04_C0_31_D4_30' if good else 'REJECT_ORION04_GLOBAL_RESULT','checks':checks,'source_result_digest':dig,'finite_theorem_authority':good,'external_independent_replay_complete':False,'novelty_authority':False,'venue_authority':False,'submission_authority':False};out['verification_digest']=sha(canon(out).encode());z.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(canon({'decision':out['decision'],'digest':out['verification_digest']}));return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
