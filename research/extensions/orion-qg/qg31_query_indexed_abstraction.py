#!/usr/bin/env python3
"""QG-31 production analyzer: query-indexed abstraction partitions over 715 TARE local-Clifford orbit types."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];QDIR=ROOT/"research/extensions/orion-q";sys.path.insert(0,str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6s_all_n_composition as r6s  # noqa:E402
PROTO=ROOT/"development/orion-qg-regime-geometry/QG31_QUERY_INDEXED_ABSTRACTION_PROTOCOL_V1.md";QG30=ROOT/"research/extensions/orion-qg/QG30_BULK_COARSE_GRAIN_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg31-query-abstraction.json";TOKEN="ORIONQG_QG31=";POS="QG31_QUERY_INDEXED_ABSTRACTION_LADDER_CONFIRMED__INDEXED_LOCAL_RESPONSE_INJECTIVE_ON_715_ORBITS"
BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mul(a,b):ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def sy(a,b):return int(p10.h.local_symp(a,b))
def f3(a,b,c):return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def orbit(t,aa):return {tuple(a[x] for x in t) for a in aa}
def perm(t,p):
 o=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def baseline(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def key1(c):return p10.key_from_codes([c])
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=sy(tag,fr[0]),sy(tag,fr[1]);ok=l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append((fr,tag,tuple(key1(x) for x in fr),key1(tag)))
 return rows
def response(rep,ps,aux):
 out=[];c=(0,0,0)
 for p in ps:
  pt=perm(rep,p);tkeys=tuple(key1(x) for x in pt);b=baseline(rep,p)
  for fr,tag,fkeys,tkey in aux:out.append(int(r6s.config_cost(tkeys,fkeys,tkey,c,1))-b)
 return tuple(out)
def class_hist(groups):return {str(k):int(v) for k,v in sorted(Counter(len(x) for x in groups.values()).items())}
def first_pair_same(groups,other,require_diff=True):
 for key in sorted(groups,key=lambda z:canon(z)):
  ms=sorted(groups[key])
  for i,a in enumerate(ms):
   for b in ms[i+1:]:
    if (other[a]!=other[b])==require_diff:return a,b,key
 return None
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();aa=autos();ps=list(itertools.product((0,1),repeat=3));aux=aux48();obs={}
 for t in itertools.product(range(4),repeat=6):
  o=orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs);bulk={r:tuple(baseline(r,p) for p in ps[:4]) for r in reps};indexed={};spectrum={}
 for r in reps:
  v=response(r,ps,aux);indexed[r]=v;spectrum[r]=tuple(sorted(v))
 gb=defaultdict(list);gs=defaultdict(list);gi=defaultdict(list)
 for r in reps:gb[bulk[r]].append(r);gs[spectrum[r]].append(r);gi[indexed[r]].append(r)
 bulk_ids={k:i for i,k in enumerate(sorted(gb,key=lambda z:canon(z)))};spec_ids={k:i for i,k in enumerate(sorted(gs,key=lambda z:canon(z)))};cont=Counter((bulk_ids[bulk[r]],spec_ids[spectrum[r]]) for r in reps)
 contingency=[{"bulk_class":b,"spectrum_class":s,"orbit_count":n} for (b,s),n in sorted(cont.items())]
 def refines(fine,coarse):return all(len({coarse[r] for r in ms})==1 for ms in fine.values())
 spectrum_refines_bulk=refines(gs,bulk);bulk_refines_spectrum=refines(gb,spectrum);indexed_refines_bulk=refines(gi,bulk);indexed_refines_spectrum=refines(gi,spectrum)
 p_sb=first_pair_same(gs,bulk,True);p_bs=first_pair_same(gb,spectrum,True);p_si=first_pair_same(gs,indexed,True)
 witness=lambda p,common_name: None if p is None else {"representative_1":p[0],"representative_2":p[1],common_name:p[2],"bulk_1":bulk[p[0]],"bulk_2":bulk[p[1]],"spectrum_sha256":sha(spectrum[p[0]]) if spectrum[p[0]]==spectrum[p[1]] else None,"first_indexed_difference":next(({"index":i,"permutation":ps[i//len(aux)],"auxiliary_row_index":i%len(aux),"K_1":a,"K_2":b} for i,(a,b) in enumerate(zip(indexed[p[0]],indexed[p[1]])) if a!=b),None)}
 parent=json.loads(QG30.read_text());parents={"qg30_green":parent.get("both_accept") is True and parent.get("BULK_SIGNATURE_COUNT_45")==45 and parent.get("BULK_DEFECT_SCALE_SEPARATION") is True,"qg30_witness":parent.get("BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT") is False}
 counts={"bulk":len(gb),"spectrum":len(gs),"indexed":len(gi)};ok=all(parents.values()) and len(reps)==715 and len(aux)==48 and counts=={"bulk":45,"spectrum":54,"indexed":715} and indexed_refines_bulk and indexed_refines_spectrum
 term=POS if ok else "QG31_CONFIRMATION_MISMATCH_OR_PARENT_GAP"
 out={"schema":"ORIONQG.QG31.QueryIndexedAbstraction.v1","issue":"SzeChunYiu/ORION#904","terminal":term,"protocol_sha256":shaf(PROTO),"parent_hashes":{"qg30":shaf(QG30)},"parent_checks":parents,"universe":{"orbit_types":len(reps),"probe_rows_per_orbit":len(ps)*len(aux),"complete_response_rows":len(reps)*len(ps)*len(aux)},"class_counts":counts,"class_size_histograms":{"bulk":class_hist(gb),"spectrum":class_hist(gs),"indexed":class_hist(gi)},"partition_relations":{"spectrum_refines_bulk":spectrum_refines_bulk,"bulk_refines_spectrum":bulk_refines_spectrum,"indexed_refines_bulk":indexed_refines_bulk,"indexed_refines_spectrum":indexed_refines_spectrum,"bulk_spectrum_incomparable":not spectrum_refines_bulk and not bulk_refines_spectrum},"contingency_nonzero":contingency,"witnesses":{"same_spectrum_different_bulk":witness(p_sb,"common_spectrum"),"same_bulk_different_spectrum":witness(p_bs,"common_bulk"),"same_spectrum_different_indexed":witness(p_si,"common_spectrum"),"indexed_collision":None if len(gi)==715 else first_pair_same(gi,bulk,False)},"BULK_QUERY_CLASSES_45":term==POS,"DEFECT_SPECTRUM_QUERY_CLASSES_54":term==POS,"INDEXED_LOCAL_RESPONSE_CLASSES_715":term==POS,"INDEXED_RESPONSE_MINIMALITY_715":term==POS,"BULK_SPECTRUM_PARTITIONS_INCOMPARABLE":term==POS and (not spectrum_refines_bulk and not bulk_refines_spectrum),"QUERY_INDEXED_ABSTRACTION_REQUIRED":term==POS,"FULL_FINITE_N_OPTIMUM_REQUIRES_715_CLASSES":False,"QG28_ORBIT_HISTOGRAM_GLOBALLY_MINIMAL":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"counts":counts,"incomparable":out["BULK_SPECTRUM_PARTITIONS_INCOMPARABLE"],"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
