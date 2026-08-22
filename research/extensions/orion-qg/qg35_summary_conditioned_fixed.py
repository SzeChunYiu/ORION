#!/usr/bin/env python3
"""QG-35 production exact summary-conditioned fixed probe complexity."""
from __future__ import annotations
import argparse, hashlib, itertools, json, sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
DEV=ROOT/"development/orion-qg-regime-geometry";sys.path.insert(0,str(DEV))
import qg32_generic_verify as base  # noqa:E402

PROTO=DEV/"QG35_SUMMARY_CONDITIONED_FIXED_PROTOCOL_V1.md"
PARENT=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json"
OUT=ROOT/"artifacts/orion-qg-qg35-summary-conditioned-fixed.json";TOKEN="ORIONQG_QG35="
TERM="QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED"
FIXED=(18,68,101,181,139)

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def class_cover_problem(mat,members):
 pairs=list(itertools.combinations(range(len(members)),2));M=len(pairs);physical=[0]*mat.shape[1]
 for j,(a,b) in enumerate(pairs):
  bit=1<<j;ga,gb=members[a],members[b]
  for p in range(mat.shape[1]):
   if int(mat[ga,p])!=int(mat[gb,p]):physical[p]|=bit
 groups=defaultdict(list)
 for p,c in enumerate(physical):
  if c:groups[int(c)].append(p)
 rows=[(c,min(ps),tuple(ps)) for c,ps in groups.items()]
 rows.sort(key=lambda x:(-x[0].bit_count(),x[1]));keep=[];dominated=0
 for row in rows:
  c=row[0]
  if any((c|d)==d for d,_,_ in keep):dominated+=1;continue
  keep.append(row)
 keep.sort(key=lambda x:x[1])
 return pairs,physical,keep,dominated

def separates(mat,members,probes):
 return len({tuple(int(mat[g,p]) for p in probes) for g in members})==len(members)

def exact_minimum(entries,npairs,fixed_ok):
 if npairs==0:return 0,(),{"depth_attempts":{},"selected_depth":0}
 covers=[x[0] for x in entries];reps=[x[1] for x in entries];M=npairs;U=(1<<M)-1
 pair_cands=[]
 for j in range(M):
  bit=1<<j;cc=tuple(i for i,c in enumerate(covers) if c&bit)
  if not cc:raise AssertionError(("uncoverable pair",j))
  pair_cands.append(cc)
 attempts={}
 for target in range(1,5):
  stats=Counter()
  @lru_cache(maxsize=None)
  def search(rem,slots,start):
   stats['calls']+=1
   if rem==0:return ()
   if slots<=0:return None
   bestcov=0
   for i in range(start,len(covers)):
    n=(covers[i]&rem).bit_count()
    if n>bestcov:bestcov=n
   if bestcov==0 or (rem.bit_count()+bestcov-1)//bestcov>slots:
    stats['maxcover_prunes']+=1;return None
   best=None
   x=rem
   while x:
    low=x&-x;j=low.bit_length()-1;x-=low
    choices=tuple(i for i in pair_cands[j] if i>=start and (covers[i]&rem))
    if not choices:return None
    key=(len(choices),j)
    if best is None or key<best[0]:best=(key,choices)
    if len(choices)==1:break
   choices=sorted(best[1],key=lambda i:(-(covers[i]&rem).bit_count(),reps[i]))
   for i in choices:
    nr=rem&~covers[i]
    if nr==rem:continue
    tail=search(nr,slots-1,i+1)
    if tail is not None:return (i,)+tail
   return None
  sol=search(U,target,0);ci=search.cache_info()._asdict();attempts[str(target)]={"stats":dict(stats),"cache":ci,"found":sol is not None}
  if sol is not None:
   ps=tuple(sorted(reps[i] for i in sol));return len(ps),ps,{"depth_attempts":attempts,"selected_depth":target}
 if not fixed_ok:raise AssertionError('earned universal five-probe upper bound failed on class')
 return 5,FIXED,{"depth_attempts":attempts,"selected_depth":5,"fallback":"QG32_CERTIFIED_UNIVERSAL_FIVE_PROBE_BASIS"}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args();z=base.construct();parent=json.loads(PARENT.read_text())
 parent_ok=parent.get('both_accept') is True and parent.get('JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED') is True and parent.get('certified_probe_upper_bound')==5 and tuple(parent.get('selected_probe_indices',[]))==FIXED
 size_hist={str(k):int(v) for k,v in sorted(Counter(len(g) for g in z['joint']).items())};expected={'1':7,'2':22,'3':6,'4':6,'6':25,'8':2,'12':14,'24':8,'48':2};recon_ok=len(z['reps'])==715 and z['mat'].shape==(715,384) and len(z['joint'])==92 and size_hist==expected
 minima=[];witnesses=[];summaries=[]
 for ci,g in enumerate(z['joint']):
  members=tuple(g)
  if len(members)<=1:
   m,ps,proof=0,(),{"depth_attempts":{},"selected_depth":0};pairs=[];entries=[];dom=0;fixed_ok=True
  else:
   pairs,_physical,entries,dom=class_cover_problem(z['mat'],members);fixed_ok=separates(z['mat'],members,FIXED);m,ps,proof=exact_minimum(entries,len(pairs),fixed_ok)
  wok=separates(z['mat'],members,ps) if len(members)>1 else len(ps)==0
  if not wok:raise AssertionError((ci,m,ps))
  minima.append(m);witnesses.append(list(ps));summaries.append({'class_index':ci,'size':len(members),'pair_count':len(pairs),'minimum':m,'witness_probe_indices':list(ps),'witness_separates':wok,'nondominated_cover_classes':len(entries),'dominated_classes_removed':dom,'proof':proof})
 mh={str(k):int(v) for k,v in sorted(Counter(minima).items())};mass=Counter()
 for g,m in zip(z['joint'],minima):mass[m]+=len(g)
 massh={str(k):int(v) for k,v in sorted(mass.items())};fstar=max(minima);worst=[i for i,m in enumerate(minima) if m==fstar];worst_w=[{'class_index':i,'size':len(z['joint'][i]),'minimum':minima[i],'witness_probe_indices':witnesses[i]} for i in worst]
 exact=parent_ok and recon_ok and len(minima)==92 and all(0<=m<=5 for m in minima) and all(s['witness_separates'] for s in summaries)
 out={'schema':'ORIONQG.QG35.SummaryConditionedFixed.v1','issue':'SzeChunYiu/ORION#932','terminal':TERM if exact else 'QG35_CANNOT_CHECK','protocol_sha256':shaf(PROTO),'parent_qg32_sha256':shaf(PARENT),'parent_checks':{'qg32_five_probe_upper_bound':parent_ok,'reconstruction':recon_ok},'universe':{'orbits':len(z['reps']),'probes':z['mat'].shape[1],'joint_classes':len(z['joint']),'joint_class_size_histogram':size_hist},'class_minima':minima,'minimum_histogram':mh,'orbit_mass_minimum_histogram':massh,'worst_case_class_conditioned_fixed_minimum':fstar,'worst_class_indices':worst,'worst_class_sizes':[len(z['joint'][i]) for i in worst],'worst_class_witnesses':worst_w,'class_summaries':summaries,'EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY':bool(exact),'ADAPTIVE_MINIMAX_AUTHORITY':False,'STRICT_ADAPTIVITY_ADVANTAGE_AUTHORITY':False,'UNIVERSAL_FIXED_MINIMUM_REDERIVED':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'QG28_GLOBAL_STATE_MINIMALITY':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
 raw=canon(out);out['result_digest']=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':out['terminal'],'F_star':fstar,'minimum_histogram':mh,'orbit_mass_histogram':massh,'worst_classes':worst,'result_digest':out['result_digest']}));return 0
if __name__=='__main__':raise SystemExit(main())
