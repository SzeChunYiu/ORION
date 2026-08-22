#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-35 class-conditioned fixed minima."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEV=ROOT/"development/orion-qg-regime-geometry";sys.path.insert(0,str(DEV))
import qg32_generic_verify as base  # noqa:E402
SRC=ROOT/"artifacts/orion-qg-qg35-summary-conditioned-fixed.json";PARENT=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg35-generic-verification.json";TOKEN="ORIONQG_QG35_GENERIC=";FIXED=(18,68,101,181,139)
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(d):
 u={k:v for k,v in d.items() if k!='result_digest'};return d.get('result_digest')==hashlib.sha256(canon(u).encode()).hexdigest()

def problem(mat,members):
 pairs=list(itertools.combinations(range(len(members)),2));physical=[0]*mat.shape[1]
 for j,(a,b) in enumerate(pairs):
  ga,gb=members[a],members[b];bit=1<<j
  for p in range(mat.shape[1]):
   if int(mat[ga,p])!=int(mat[gb,p]):physical[p]|=bit
 groups=defaultdict(list)
 for p,c in enumerate(physical):
  if c:groups[int(c)].append(p)
 rows=sorted(((c,min(ps)) for c,ps in groups.items()),key=lambda x:(-x[0].bit_count(),x[1]));keep=[]
 for c,p in rows:
  if any((c|d)==d for d,_ in keep):continue
  keep.append((c,p))
 return pairs,physical,sorted(keep,key=lambda x:x[1])
def separates(mat,members,ps):return len({tuple(int(mat[g,p]) for p in ps) for g in members})==len(members)

def halves(entries):
 best={0:()}
 for i,(c,_p) in enumerate(entries):best.setdefault(int(c),(i,))
 for i,j in itertools.combinations(range(len(entries)),2):
  m=int(entries[i][0])|int(entries[j][0]);w=(i,j);old=best.get(m)
  if old is None or (len(w),w)<(len(old),old):best[m]=w
 return sorted(((m,w) for m,w in best.items()),key=lambda x:(len(x[1]),x[1],x[0]))
def combine(entries,wa,wb):return tuple(sorted({entries[i][1] for i in tuple(wa)+tuple(wb)}))
def completion_search(U,lefts,rights,entries,max_total):
 # Posting lists by uncovered pair bit; every returned candidate is exact-union checked.
 post=defaultdict(list)
 for ri,(m,w) in enumerate(rights):
  if len(w)>2:continue
  x=m
  while x:
   b=x&-x;post[b.bit_length()-1].append(ri);x-=b
 tested=0
 for a,wa in lefts:
  if len(wa)>2:continue
  missing=U&~a
  if not missing:
   ps=combine(entries,wa,());
   if len(ps)<=max_total:return ps,tested
  bits=[];x=missing
  while x:
   b=x&-x;j=b.bit_length()-1;x-=b;bits.append((len(post[j]),j))
  if not bits:continue
  _n,pivot=min(bits)
  for ri in post[pivot]:
   b,wb=rights[ri]
   if len(wa)+len(wb)>max_total:continue
   tested+=1
   if (a|b)==U:
    ps=combine(entries,wa,wb)
    if len(ps)<=max_total:return ps,tested
 return None,tested
def exact_min(entries,npairs,fixed_ok):
 if npairs==0:return 0,(),{"half_union_count":1,"tested_3":0,"tested_4":0}
 U=(1<<npairs)-1;hs=halves(entries)
 # exact 1/2 directly from complete half family
 best12=None
 for m,w in hs:
  if m==U and len(w) in (1,2):
   ps=combine(entries,w,());key=(len(ps),ps)
   if best12 is None or key<best12[0]:best12=(key,ps)
 if best12 is not None:return len(best12[1]),best12[1],{"half_union_count":len(hs),"tested_3":0,"tested_4":0}
 left1=[x for x in hs if len(x[1])<=1]
 p3,t3=completion_search(U,left1,hs,entries,3)
 if p3 is not None:return len(p3),p3,{"half_union_count":len(hs),"tested_3":t3,"tested_4":0}
 p4,t4=completion_search(U,hs,hs,entries,4)
 if p4 is not None:return len(p4),p4,{"half_union_count":len(hs),"tested_3":t3,"tested_4":t4}
 if not fixed_ok:raise AssertionError('five-probe parent upper bound failed')
 return 5,FIXED,{"half_union_count":len(hs),"tested_3":t3,"tested_4":t4,"no_le4_complete":True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=SRC);ap.add_argument('--output',type=Path,default=OUT);ns=ap.parse_args();src=json.loads(ns.input.read_text());z=base.construct();parent=json.loads(PARENT.read_text());mins=[];wits=[];proofs=[]
 for g in z['joint']:
  members=tuple(g)
  if len(members)<=1:m,ps,pr=0,(),{"half_union_count":1,"tested_3":0,"tested_4":0}
  else:
   pairs,_physical,entries=problem(z['mat'],members);m,ps,pr=exact_min(entries,len(pairs),separates(z['mat'],members,FIXED))
  if (len(members)>1 and not separates(z['mat'],members,ps)) or (len(members)<=1 and ps):raise AssertionError((members,m,ps))
  mins.append(m);wits.append(list(ps));proofs.append(pr)
 mh={str(k):int(v) for k,v in sorted(Counter(mins).items())};mass=Counter()
 for g,m in zip(z['joint'],mins):mass[m]+=len(g)
 massh={str(k):int(v) for k,v in sorted(mass.items())};fstar=max(mins);worst=[i for i,m in enumerate(mins) if m==fstar]
 parent_ok=parent.get('both_accept') is True and parent.get('certified_probe_upper_bound')==5 and tuple(parent.get('selected_probe_indices',[]))==FIXED
 sw=src.get('worst_class_witnesses',[]);swmap={int(x['class_index']):tuple(x['witness_probe_indices']) for x in sw};worst_witness_ok=set(swmap)==set(worst) and all(len(swmap[i])==mins[i] and separates(z['mat'],tuple(z['joint'][i]),swmap[i]) for i in worst)
 checks={'digest':valid(src),'parent':parent_ok,'orbits':len(z['reps'])==715,'probes':z['mat'].shape[1]==384,'joint_classes':len(z['joint'])==92,'class_minima':src.get('class_minima')==mins,'minimum_histogram':src.get('minimum_histogram')==mh,'orbit_mass_histogram':src.get('orbit_mass_minimum_histogram')==massh,'F_star':src.get('worst_case_class_conditioned_fixed_minimum')==fstar,'worst_classes':src.get('worst_class_indices')==worst,'worst_witnesses':worst_witness_ok,'authority':src.get('EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY') is True and all(src.get(k) is False for k in ('ADAPTIVE_MINIMAX_AUTHORITY','STRICT_ADAPTIVITY_ADVANTAGE_AUTHORITY','UNIVERSAL_FIXED_MINIMUM_REDERIVED','MINIMUM_FULL_FINITE_OPTIMUM_PROBES','HARDWARE_MEASUREMENT_MINIMUM','QG28_GLOBAL_STATE_MINIMALITY','novelty_authority','physical_quantum_advantage_claim'))};ok=all(checks.values());out={'schema':'ORIONQG.QG35.GenericVerification.v1','decision':'ACCEPT_EXACT_SUMMARY_CONDITIONED_FIXED' if ok else 'REJECT','all_checks':ok,'checks':checks,'independent':{'class_minima':mins,'minimum_histogram':mh,'orbit_mass_minimum_histogram':massh,'F_star':fstar,'worst_class_indices':worst,'proof_summaries':proofs},'ADAPTIVE_MINIMAX_AUTHORITY':False,'STRICT_ADAPTIVITY_ADVANTAGE_AUTHORITY':False,'UNIVERSAL_FIXED_MINIMUM_REDERIVED':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'QG28_GLOBAL_STATE_MINIMALITY':False,'novelty_authority':False,'physical_quantum_advantage_claim':False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'decision':out['decision'],'F_star':fstar,'minimum_histogram':mh,'worst_classes':worst,'total_half_unions':sum(x['half_union_count'] for x in proofs),'tested_3':sum(x.get('tested_3',0) for x in proofs),'tested_4':sum(x.get('tested_4',0) for x in proofs)}));return 0
if __name__=='__main__':raise SystemExit(main())
