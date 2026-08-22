#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-28 local-Clifford orbit compression."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/orion-qg-qg28-local-clifford-orbits.json";QG26=ROOT/"research/extensions/orion-qg/QG26_PARIKH_HISTOGRAM_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg28-generic-verification.json";TOKEN="ORIONQG_QG28_GENERIC=";POS="QG28_TARE_EXACT_COST_DESCENDS_TO_715_LOCAL_CLIFFORD_COLUMN_ORBIT_COUNTS_ALL_N";BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def valid(r):u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def mul(a,b):ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def symp(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def wt(a):return int(a!=0)
def f3(a,b,c):return 1 if a==b==c!=0 else wt(a)+wt(b)+wt(c)
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def atype(t,a):return tuple(a[x] for x in t)
def cmap_all(types,aa):
 cm={};ai={};obs={}
 for t in types:
  o={atype(t,a) for a in aa};c=min(o);cm[t]=c
  for i,a in enumerate(aa):
   if atype(t,a)==c:ai[t]=i;break
  obs.setdefault(c,set()).update(o)
 return cm,ai,obs
def perm(t,p):
 o=[]
 for j in range(3):a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def base(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def accept(fr,tag):
 if any(x==0 for x in fr):return False,None
 if any(symp(fr[2*j],fr[2*j+1])!=1 for j in range(3)):return False,None
 l0,l1=symp(tag,fr[0]),symp(tag,fr[1])
 if l0==l1:return False,None
 if any(symp(tag,fr[2*j])!=l0 or symp(tag,fr[2*j+1])!=l1 for j in (1,2)):return False,None
 return True,(l0,l1)
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if symp(a,b)==1];out=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   ok,lab=accept(fr,tag)
   if ok:out.append((fr,tag,lab))
 return out
def struct(fr,tag):return sum((2 if j%2==0 else 4)*int(fr[j]!=0) for j in range(6))+2*int(tag!=0)-18
def restore(pt,fr):
 r=[mul(pt[i],fr[i]) for i in range(6)];return f3(r[0],r[2],r[4])+f3(r[1],r[3],r[5])
def cost(pt,fr,tag):return struct(fr,tag)+restore(pt,fr)
def active(types,aa,cm,ai,rows,ps):
 hb=hashlib.sha256();ha=hashlib.sha256();hd=hashlib.sha256();bad=[];n=0
 def stream(h,v):h.update((str(int(v))+"\n").encode())
 for t in types:
  a=aa[ai[t]];ct=cm[t]
  for p in ps:
   pt=perm(t,p);cpt=perm(ct,p);b0=base(t,p);b1=base(ct,p)
   for fr,tag,lab in rows:
    cfr=tuple(a[x] for x in fr);ctag=a[tag];cb=cost(pt,fr,tag);ca=cost(cpt,cfr,ctag);okb,labb=accept(fr,tag);oka,laba=accept(cfr,ctag);db=b0+(struct(fr,tag)+restore(pt,fr)-b0);da=b1+(struct(cfr,ctag)+restore(cpt,cfr)-b1)
    stream(hb,cb);stream(ha,ca);stream(hd,db);stream(hd,da);n+=1
    if not (cb==ca==db==da and okb and oka and labb==laba==lab) and len(bad)<20:bad.append({"target":t,"canonical":ct,"auto":a,"perm":p,"frames":fr,"tag":tag,"before":cb,"after":ca,"labels":[lab,labb,laba]})
 return {"rows":n,"cost_before_sha256":hb.hexdigest(),"cost_after_sha256":ha.hexdigest(),"decomposition_pair_sha256":hd.hexdigest(),"all_match":len(bad)==0,"mismatches":bad}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();s=json.loads(x.input.read_text());aa=autos();types=list(itertools.product(range(4),repeat=6));ps=list(itertools.product((0,1),repeat=3));cm,ai,obs=cmap_all(types,aa)
 eq=[]
 for a in aa:eq.append(all(a[mul(u,v)]==mul(a[u],a[v]) and symp(a[u],a[v])==symp(u,v) for u,v in itertools.product(range(4),repeat=2)) and all(wt(a[u])==wt(u) for u in range(4)) and all(f3(a[u],a[v],a[w])==f3(u,v,w) for u,v,w in itertools.product(range(4),repeat=3)))
 sizes=Counter(len(o) for o in obs.values());reps=sorted(obs);q26=json.loads(QG26.read_text());qh=set(q26.get("spectator_baselines",{}).get("pairing",{}).values());meta=[];const=True;lift=True
 for p in ps:
  full=[base(t,p) for t in types];qv=[base(r,p) for r in reps];const=const and all(len({base(t,p) for t in o})==1 for o in obs.values());lift=lift and [base(cm[t],p) for t in types]==full;c=Counter(qv);meta.append({"perm":list(p),"full_sha256":sha(full),"quotient_sha256":sha(qv),"orbit_histogram":{str(k):int(v) for k,v in sorted(c.items())}})
 rows=aux48();ac=active(types,aa,cm,ai,rows,ps)
 checks={"source_digest":valid(s),"source_positive":s.get("terminal")==POS,"qg26_parent":q26.get("both_accept") is True and q26.get("HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True,"six_autos":len(aa)==6 and all(eq),"burnside_715":len(obs)==715 and sizes==Counter({6:651,3:63,1:1}),"partition_4096":sum(k*v for k,v in sizes.items())==4096,"parent_baseline_hashes":set(m["full_sha256"] for m in meta)==qh,"baseline_constant":const and lift,"four_quotient_vectors":len({m["quotient_sha256"] for m in meta})==4,"quotient_hist":all(m["orbit_histogram"]=={"0":1,"1":8,"2":44,"3":128,"4":222,"5":216,"6":96} for m in meta),"active_rows":ac["rows"]==1572864 and ac["all_match"],"active_digests":ac["cost_before_sha256"]==s.get("active_canonicalization_control",{}).get("cost_before_sha256") and ac["cost_after_sha256"]==s.get("active_canonicalization_control",{}).get("cost_after_sha256") and ac["decomposition_pair_sha256"]==s.get("active_canonicalization_control",{}).get("decomposition_pair_sha256"),"unsafe_false":s.get("INDEPENDENT_POSITION_RELABEL_PER_COLUMN") is False and s.get("COMBINED_LOCAL_POSITION_QUOTIENT_54") is False,"stronger_false":all(s.get(k) is False for k in ("EXPLICIT_TEMPLATE_BASIS_ENUMERATED","PRACTICAL_STATIC_FORECASTER","CHAIN_ALL_N","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","novelty_authority","r6_authority","physical_quantum_advantage_claim"))};ok=all(checks.values())
 out={"schema":"ORIONQG.QG28.GenericVerification.v1","decision":"ACCEPT_LOCAL_CLIFFORD_ORBIT_COMPRESSION" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"orbit_count":len(obs),"orbit_size_distribution":{str(k):int(v) for k,v in sorted(sizes.items())},"baseline_meta":meta,"active_control":ac,"source_result_digest":s.get("result_digest"),"LOCAL_CLIFFORD_EQUIVARIANCE_PER_QUBIT":bool(ok),"LOCAL_CLIFFORD_ORBIT_COUNT":715 if ok else None,"ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":bool(ok),"GUARDED_TROPICAL_GEOMETRY_DESCENDS_TO_715_COUNTS":bool(ok),"INDEPENDENT_POSITION_RELABEL_PER_COLUMN":False,"COMBINED_LOCAL_POSITION_QUOTIENT_54":False,"EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"orbits":len(obs),"sizes":out["orbit_size_distribution"],"active_rows":ac["rows"]}));return 0
if __name__=="__main__":raise SystemExit(main())
