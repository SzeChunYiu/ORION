#!/usr/bin/env python3
"""Independent generic ORION confirmation for QG-31 query-indexed abstraction partitions."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/orion-qg-qg31-query-abstraction.json";QG30=ROOT/"research/extensions/orion-qg/QG30_BULK_COARSE_GRAIN_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg31-generic-verification.json";TOKEN="ORIONQG_QG31_GENERIC=";POS="QG31_QUERY_INDEXED_ABSTRACTION_LADDER_CONFIRMED__INDEXED_LOCAL_RESPONSE_INJECTIVE_ON_715_ORBITS"
BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def valid(r):u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def mul(a,b):ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def sy(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def f3(a,b,c):return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def orbit(t,aa):return {tuple(a[x] for x in t) for a in aa}
def perm(t,p):
 o=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def baseline(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=sy(tag,fr[0]),sy(tag,fr[1]);ok=l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append((fr,tag))
 return rows
def structural(fr,tag):
 raw=0
 for j in range(3):raw+=2*int(fr[2*j]!=0)+4*int(fr[2*j+1]!=0)
 return raw+2*int(tag!=0)-18
def restore(pt,fr):
 r=[mul(pt[i],fr[i]) for i in range(6)];return f3(r[0],r[2],r[4])+f3(r[1],r[3],r[5])
def response(rep,ps,aux):
 out=[]
 for p in ps:
  pt=perm(rep,p);b=baseline(rep,p)
  for fr,tag in aux:out.append(structural(fr,tag)+restore(pt,fr)-b)
 return tuple(out)
def groups(reps,vals):
 g=defaultdict(list)
 for r in reps:g[vals[r]].append(r)
 return g
def hist(g):return {str(k):int(v) for k,v in sorted(Counter(len(x) for x in g.values()).items())}
def refines(fine,coarse):return all(len({coarse[r] for r in ms})==1 for ms in fine.values())
def first_pair(g,other):
 for key in sorted(g,key=lambda z:canon(z)):
  ms=sorted(g[key])
  for i,a in enumerate(ms):
   for b in ms[i+1:]:
    if other[a]!=other[b]:return a,b,key
 return None
def pair_compact(p,bulk,spec,indexed,ps,aux,common):
 if p is None:return None
 a,b,k=p;diff=next(i for i,(x,y) in enumerate(zip(indexed[a],indexed[b])) if x!=y);return {"representative_1":list(a),"representative_2":list(b),common:list(k) if len(k)<10 else {"sha256":sha(k),"histogram":{str(x):int(n) for x,n in sorted(Counter(k).items())}},"bulk_1":list(bulk[a]),"bulk_2":list(bulk[b]),"spectrum_sha256":sha(spec[a]) if spec[a]==spec[b] else None,"first_indexed_difference":{"index":diff,"permutation":list(ps[diff//len(aux)]),"auxiliary_row_index":diff%len(aux),"K_1":indexed[a][diff],"K_2":indexed[b][diff]}}
def construct():
 aa=autos();ps=list(itertools.product((0,1),repeat=3));aux=aux48();obs={}
 for t in itertools.product(range(4),repeat=6):
  o=orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs);bulk={r:tuple(baseline(r,p) for p in ps[:4]) for r in reps};indexed={r:response(r,ps,aux) for r in reps};spec={r:tuple(sorted(indexed[r])) for r in reps};gb,gs,gi=groups(reps,bulk),groups(reps,spec),groups(reps,indexed);bid={k:i for i,k in enumerate(sorted(gb,key=lambda z:canon(z)))};sid={k:i for i,k in enumerate(sorted(gs,key=lambda z:canon(z)))};cont=Counter((bid[bulk[r]],sid[spec[r]]) for r in reps)
 return {"reps":reps,"obs":obs,"ps":ps,"aux":aux,"bulk":bulk,"indexed":indexed,"spec":spec,"gb":gb,"gs":gs,"gi":gi,"counts":{"bulk":len(gb),"spectrum":len(gs),"indexed":len(gi)},"hist":{"bulk":hist(gb),"spectrum":hist(gs),"indexed":hist(gi)},"relations":{"spectrum_refines_bulk":refines(gs,bulk),"bulk_refines_spectrum":refines(gb,spec),"indexed_refines_bulk":refines(gi,bulk),"indexed_refines_spectrum":refines(gi,spec)},"cont":[{"bulk_class":b,"spectrum_class":s,"orbit_count":n} for (b,s),n in sorted(cont.items())]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();src=json.loads(x.input.read_text());z=construct();parent=json.loads(QG30.read_text())
 rel=z["relations"];incomp=not rel["spectrum_refines_bulk"] and not rel["bulk_refines_spectrum"];w={"same_spectrum_different_bulk":pair_compact(first_pair(z["gs"],z["bulk"]),z["bulk"],z["spec"],z["indexed"],z["ps"],z["aux"],"common_spectrum"),"same_bulk_different_spectrum":pair_compact(first_pair(z["gb"],z["spec"]),z["bulk"],z["spec"],z["indexed"],z["ps"],z["aux"],"common_bulk"),"same_spectrum_different_indexed":pair_compact(first_pair(z["gs"],z["indexed"]),z["bulk"],z["spec"],z["indexed"],z["ps"],z["aux"],"common_spectrum")}
 checks={"source_digest":valid(src),"source_positive":src.get("terminal")==POS,"parent":parent.get("both_accept") is True and parent.get("BULK_SIGNATURE_COUNT_45")==45,"orbit_count":len(z["reps"])==715,"orbit_sizes":Counter(len(z["obs"][r]) for r in z["reps"])==Counter({6:651,3:63,1:1}),"aux48":len(z["aux"])==48,"counts":z["counts"]==src.get("class_counts")=={"bulk":45,"spectrum":54,"indexed":715},"histograms":z["hist"]==src.get("class_size_histograms"),"relations":src.get("partition_relations",{}).get("spectrum_refines_bulk")==rel["spectrum_refines_bulk"] and src.get("partition_relations",{}).get("bulk_refines_spectrum")==rel["bulk_refines_spectrum"] and src.get("partition_relations",{}).get("indexed_refines_bulk")==rel["indexed_refines_bulk"] and src.get("partition_relations",{}).get("indexed_refines_spectrum")==rel["indexed_refines_spectrum"],"contingency":z["cont"]==src.get("contingency_nonzero"),"incomparable":src.get("BULK_SPECTRUM_PARTITIONS_INCOMPARABLE") is incomp,"stronger_false":src.get("FULL_FINITE_N_OPTIMUM_REQUIRES_715_CLASSES") is False and src.get("QG28_ORBIT_HISTOGRAM_GLOBALLY_MINIMAL") is False}
 ok=all(checks.values());out={"schema":"ORIONQG.QG31.GenericVerification.v1","decision":"ACCEPT_QUERY_INDEXED_ABSTRACTION" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"independent_counts":z["counts"],"independent_relations":dict(rel,bulk_spectrum_incomparable=incomp),"independent_witnesses":w,"source_result_digest":src.get("result_digest"),"BULK_QUERY_CLASSES_45":bool(ok),"DEFECT_SPECTRUM_QUERY_CLASSES_54":bool(ok),"INDEXED_LOCAL_RESPONSE_CLASSES_715":bool(ok),"INDEXED_RESPONSE_MINIMALITY_715":bool(ok),"BULK_SPECTRUM_PARTITIONS_INCOMPARABLE":bool(ok and incomp),"QUERY_INDEXED_ABSTRACTION_REQUIRED":bool(ok),"FULL_FINITE_N_OPTIMUM_REQUIRES_715_CLASSES":False,"QG28_ORBIT_HISTOGRAM_GLOBALLY_MINIMAL":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"counts":z["counts"],"incomparable":incomp,"all_checks":ok}));return 0
if __name__=="__main__":raise SystemExit(main())
