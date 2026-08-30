#!/usr/bin/env python3
from __future__ import annotations
import argparse,concurrent.futures,hashlib,json,re,subprocess,tempfile,time
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent
RESULT=ROOT/'RESULT.json'
TOKEN='ORION04_GLOBAL_REPLAY='
SOURCES={
 'high':{'u128':ROOT/'engine_high_u128.c','avx':ROOT/'engine_high_avx.c'},
 'rank3':{'u128':ROOT/'engine_rank3_u128.c','avx':ROOT/'engine_rank3_avx.c'},
 'c4rank2':{'u128':ROOT/'engine_c4rank2_u128.c','avx':ROOT/'engine_c4rank2_avx.c'},
}
def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fsha(p:Path)->str:return sha_bytes(p.read_bytes())
def compile_all(td:Path):
 ex={}
 for fam,pair in SOURCES.items():
  ex[fam]={}
  for eng,src in pair.items():
   out=td/f'{fam}_{eng}';cmd=['gcc','-std=gnu11','-O3','-march=native','-Wall','-Wextra','-Werror',str(src),'-o',str(out)]
   p=subprocess.run(cmd,capture_output=True,text=True)
   if p.returncode:raise RuntimeError({'cmd':cmd,'stdout':p.stdout,'stderr':p.stderr})
   ex[fam][eng]=out
 return ex
def jobs(cover):
 z=[]
 for b in cover['lower_branches']:
  fam=b['engine_family'];a,c2,c4=b['a1'],b['b2'],b['c4']
  args=[a,c2,c4,*b['seed_multiplicities'],0] if fam=='high' else [a,c2,c4] if fam=='rank3' else [a,c2]
  key=f"s{b['support']}:a{a}:b{c2}:c{c4}:{b['branch']}"
  for e in ('u128','avx'):z.append((key,b,fam,args,e))
 for b in cover['upper_branches']:
  a,c2,c4=b['a1'],b['b2'],b['c4'];args=[a,c2,c4,*b['seed_multiplicities'],int(b['plane_doubletons'])]
  key=f"s{b['support']}:a{a}:b{c2}:c{c4}:{b['branch']}"
  for e in ('u128','avx'):z.append((key,b,'high',args,e))
 return z
def run_one(ex,j):
 key,b,fam,args,e=j;t=time.perf_counter();p=subprocess.run([str(ex[fam][e]),*map(str,args)],capture_output=True,text=True,timeout=7200)
 m=re.search(r'solutions=(\d+)',p.stdout.strip().splitlines()[-1] if p.stdout.strip() else '')
 return {'key':key,'support':b['support'],'pattern':[b['a1'],b['b2'],b['c4']],'branch':b['branch'],'family':fam,'engine':e,'args':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'stdout_sha256':sha_bytes(p.stdout.encode()),'solutions':int(m.group(1)) if m else None}
def build(max_workers:int):
 cover=json.loads((ROOT/'FULL_CUBE_COVER.json').read_text());js=jobs(cover)
 with tempfile.TemporaryDirectory(prefix='orion04-global-') as d:
  ex=compile_all(Path(d));rows=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
   futs=[pool.submit(run_one,ex,j) for j in js]
   for f in concurrent.futures.as_completed(futs):rows.append(f.result())
 rows.sort(key=lambda r:(r['support'],r['pattern'],r['branch'],r['engine']))
 by={}
 for r in rows:by.setdefault(r['key'],{})[r['engine']]=r
 branch_rows=[]
 for key,pair in sorted(by.items()):
  exact=set(pair)=={'u128','avx'} and pair['u128']['stdout']==pair['avx']['stdout']
  branch_rows.append({'key':key,'support':pair['u128']['support'],'pattern':pair['u128']['pattern'],'branch':pair['u128']['branch'],'family':pair['u128']['family'],'args':pair['u128']['args'],'exact_stdout_agreement':exact,'stdout_sha256':pair['u128']['stdout_sha256'],'final_line':pair['u128']['stdout'].strip().splitlines()[-1],'solutions':pair['u128']['solutions']})
 checks={'cover_patterns_60':cover['pattern_count']==60,'cover_branches_78':cover['branch_count']==78,'engine_runs_156':len(rows)==156,'branch_rows_78':len(branch_rows)==78,'all_return_zero':all(r['returncode']==0 for r in rows),'all_stderr_empty':all(not r['stderr'] for r in rows),'all_solutions_zero':all(r['solutions']==0 for r in rows),'all_exact_stdout_agreement':all(r['exact_stdout_agreement'] for r in branch_rows),'parent_support_le13_bound':cover['parent_support_le13_result_digest']=='6e25fbf0a483817bb5edb4908640e0b0b83be47d2cc4b2da6192feb9fecbc004'}
 good=all(checks.values())
 res={'schema':'ORION.ORION04.GlobalSupport14To31DualReplayResult.v1','subject_main_sha':'b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8','terminal':'ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30' if good else 'ORION04_GLOBAL_REPLAY_REJECTED','checks':checks,'cover_digest':cover['digest'],'source_sha256':{fam:{e:fsha(p) for e,p in pair.items()} for fam,pair in SOURCES.items()},'branches':branch_rows,'runs':rows,'theorem':'No length-31 total-zero sequence over C_5^3 is free of nonempty zero sums of lengths at most five. Thus 31 is in C_0(C_5^3); under the committed implication, D_4(C_5^3)=30.','finite_theorem_authority':good,'external_independent_replay_complete':False,'novelty_authority':False,'venue_authority':False,'submission_authority':False}
 res['result_digest']=sha_bytes(canon(res).encode());return res
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=RESULT);a.add_argument('--max-workers',type=int,default=5);z=a.parse_args();r=build(z.max_workers);z.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':r['terminal'],'digest':r['result_digest']}));return 0 if r['finite_theorem_authority'] else 1
if __name__=='__main__':raise SystemExit(main())
