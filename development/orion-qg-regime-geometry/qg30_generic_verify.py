#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-30 bulk coarse-graining / defect information loss."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/orion-qg-qg30-bulk-coarse-grain.json";QG27=ROOT/"research/extensions/orion-qg/QG27_BULK_DEFECT_RESULTS.json";QG28=ROOT/"research/extensions/orion-qg/QG28_LOCAL_CLIFFORD_ORBIT_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg30-generic-verification.json";TOKEN="ORIONQG_QG30_GENERIC=";POS="QG30_TARE_BULK_GEOMETRY_COMPRESSES_EXACTLY_TO_45_SIGNATURE_COUNTS__DEFECT_INFORMATION_REMAINS"
BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def valid(r):u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def mul(a,b):ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def sy(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def f3(a,b,c):return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def atype(t,a):return tuple(a[x] for x in t)
def orbit(t,aa):return {atype(t,a) for a in aa}
def perm(t,p):
 o=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def baseline(t,p):
 q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=sy(tag,fr[0]),sy(tag,fr[1]);ok=l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append((fr,tag,(l0,l1)))
 return rows
def structural(fr,tag,c=(0,0,0)):
 raw=0
 for j in range(3):
  raw+=(2 if c[j]==0 else 4)*int(fr[2*j]!=0)
  raw+=(2 if c[j]==1 else 4)*int(fr[2*j+1]!=0)
 return raw+2*int(tag!=0)-18
def aux_restore(pt,fr):
 r=[mul(pt[i],fr[i]) for i in range(6)];return f3(r[0],r[2],r[4])+f3(r[1],r[3],r[5])
def profile(rep,ps,aux):
 ordered=[]
 for p in ps:
  pt=perm(rep,p);b=baseline(rep,p)
  for fr,tag,_ in aux:ordered.append(structural(fr,tag)+aux_restore(pt,fr)-b)
 srt=tuple(sorted(ordered));return tuple(ordered),srt,{str(k):int(v) for k,v in sorted(Counter(srt).items())},sha(srt)
def construct():
 aa=autos();types=list(itertools.product(range(4),repeat=6));ps=list(itertools.product((0,1),repeat=3));bulk_ps=ps[:4];obs={}
 for t in types:
  o=orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs);aux=aux48();profiles={};members=defaultdict(list)
 for r in reps:
  sig=tuple(baseline(r,p) for p in bulk_ps);ordered,srt,hist,ph=profile(r,ps,aux);profiles[r]={"signature":sig,"ordered":ordered,"sorted":srt,"histogram":hist,"sha256":ph};members[sig].append(r)
 sigs=sorted(members);table=[];profile_counts=[];all_profiles=set();multi=0
 for sig in sigs:
  ms=sorted(members[sig]);table.append({"signature":list(sig),"orbit_count":len(ms),"raw_type_count":sum(len(obs[r]) for r in ms),"first_representative":list(ms[0]),"member_representatives_sha256":sha(ms)});pids={profiles[r]["sha256"] for r in ms};all_profiles.update(pids);multi+=int(len(pids)>1);profile_counts.append({"signature":list(sig),"orbit_count":len(ms),"distinct_one_active_profiles":len(pids)})
 witness=None
 for sig in sigs:
  ms=sorted(members[sig])
  for i,r1 in enumerate(ms):
   for r2 in ms[i+1:]:
    if profiles[r1]["sorted"]!=profiles[r2]["sorted"]:
     o1,o2=profiles[r1]["ordered"],profiles[r2]["ordered"];idx=next(k for k,(a,b) in enumerate(zip(o1,o2)) if a!=b);pi,ai=divmod(idx,len(aux));fr,tag,_=aux[ai];witness={"common_signature":list(sig),"representative_1":list(r1),"representative_2":list(r2),"profile_1_sha256":profiles[r1]["sha256"],"profile_2_sha256":profiles[r2]["sha256"],"profile_1_histogram":profiles[r1]["histogram"],"profile_2_histogram":profiles[r2]["histogram"],"first_ordered_difference":{"index":idx,"permutation":list(ps[pi]),"auxiliary_row_index":ai,"auxiliary_frames":list(fr),"auxiliary_tag":tag,"K_1":o1[idx],"K_2":o2[idx]}};break
   if witness:break
  if witness:break
 bulk_rows=[[sig[r] for sig in sigs] for r in range(4)];ties=[]
 for i in range(4):
  for j in range(i+1,4):
   d=[bulk_rows[i][k]-bulk_rows[j][k] for k in range(len(sigs))];ties.append({"forms":[i,j],"sha256":sha(d),"support_size":sum(x!=0 for x in d),"coefficient_range":[min(d),max(d)],"histogram":{str(k):int(v) for k,v in sorted(Counter(d).items())}})
 return {"reps":reps,"orbits":obs,"aux":aux,"sigs":sigs,"table":table,"profile_counts":profile_counts,"distinct_profiles":len(all_profiles),"multi":multi,"witness":witness,"bulk_rows":bulk_rows,"ties":ties,"rows":len(reps)*len(ps)*len(aux)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();src=json.loads(x.input.read_text());z=construct()
 # Parent/source binding happens only after the full generic construction above is sealed.
 q27=json.loads(QG27.read_text());q28=json.loads(QG28.read_text());c=src.get("bulk_signature_census",{})
 parents={"qg27":q27.get("both_accept") is True and q27.get("ASYMPTOTIC_COST_DENSITY_EXACT") is True and q27.get("bulk",{}).get("distinct_forms")==4,"qg28":q28.get("both_accept") is True and q28.get("LOCAL_CLIFFORD_ORBIT_COUNT")==715 and q28.get("ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True,"unsafe_false":q28.get("INDEPENDENT_POSITION_RELABEL_PER_COLUMN") is False and q28.get("COMBINED_LOCAL_POSITION_QUOTIENT_54") is False}
 source={"digest":valid(src),"positive":src.get("terminal")==POS,"issue":src.get("issue")=="SzeChunYiu/ORION#893","signature_count":c.get("signature_count")==len(z["sigs"])==45,"totals":c.get("orbit_total")==715 and c.get("raw_type_total")==4096,"table":c.get("signature_table")==z["table"],"profile_rows":src.get("complete_one_active_profile_rows")==z["rows"]==274560,"profile_counts":c.get("profile_counts_by_signature")==z["profile_counts"],"distinct_profiles":c.get("total_distinct_one_active_profiles")==z["distinct_profiles"],"multi":c.get("signatures_with_multiple_profiles")==z["multi"],"witness":c.get("information_loss_witness")==z["witness"] and z["witness"] is not None,"bulk_rows":src.get("bulk_coefficient_rows_45",{}).get("rows")==z["bulk_rows"],"ties":src.get("pairwise_bulk_ties_45")==z["ties"],"stronger_false":all(src.get(k) is False for k in ("BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT","FULL_FINITE_N_OPTIMUM_FROM_45_COUNTS","PHYSICAL_RENORMALIZATION_GROUP","FINITE_N_GLOBAL_PHASE_BOUNDARY","CHAIN_ALL_N","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","novelty_authority","r6_authority","physical_quantum_advantage_claim"))}
 independent={"automorphisms":len(autos())==6,"orbit_count":len(z["reps"])==715,"orbit_size_distribution":Counter(len(z["orbits"][r]) for r in z["reps"])==Counter({6:651,3:63,1:1}),"aux48":len(z["aux"])==48,"signature_count":len(z["sigs"])==45,"witness_found":z["witness"] is not None,"bulk_rows_four":len(z["bulk_rows"])==4 and all(len(r)==45 for r in z["bulk_rows"]),"ties_six":len(z["ties"])==6}
 ok=all(parents.values()) and all(source.values()) and all(independent.values())
 out={"schema":"ORIONQG.QG30.GenericVerification.v1","decision":"ACCEPT_BULK45_DEFECT_SEPARATION" if ok else "REJECT","all_checks":bool(ok),"parent_checks":parents,"source_checks":source,"independent_checks":independent,"independent_summary":{"orbits":len(z["reps"]),"signatures":len(z["sigs"]),"profile_rows":z["rows"],"distinct_profiles":z["distinct_profiles"],"multi_profile_signatures":z["multi"],"witness":z["witness"],"bulk_rows_sha256":[sha(r) for r in z["bulk_rows"]]},"source_result_digest":src.get("result_digest"),"BULK_SIGNATURE_COUNT_45":45 if ok else None,"BULK_45_HISTOGRAM_SUFFICIENT_FOR_ASYMPTOTIC_DENSITY":bool(ok),"ASYMPTOTIC_PHASE_GEOMETRY_DESCENDS_TO_45_COUNTS":bool(ok),"BULK_DEFECT_SCALE_SEPARATION":bool(ok),"BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT":False,"FULL_FINITE_N_OPTIMUM_FROM_45_COUNTS":False,"PHYSICAL_RENORMALIZATION_GROUP":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"orbits":len(z["reps"]),"signatures":len(z["sigs"]),"profile_rows":z["rows"],"distinct_profiles":z["distinct_profiles"],"multi_profile_signatures":z["multi"],"witness_found":z["witness"] is not None}));return 0
if __name__=="__main__":raise SystemExit(main())
