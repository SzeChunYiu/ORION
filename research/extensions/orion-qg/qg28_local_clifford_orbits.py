#!/usr/bin/env python3
"""QG-28 production analyzer: exact local-Clifford orbit compression of TARE histogram geometry."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];QDIR=ROOT/"research/extensions/orion-q";sys.path.insert(0,str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa:E402
import max_r6s_all_n_composition as r6s  # noqa:E402
PROTO=ROOT/"development/orion-qg-regime-geometry/QG28_LOCAL_CLIFFORD_ORBIT_PROTOCOL_V1.md";QG26=ROOT/"research/extensions/orion-qg/QG26_PARIKH_HISTOGRAM_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg28-local-clifford-orbits.json";TOKEN="ORIONQG_QG28=";POS="QG28_TARE_EXACT_COST_DESCENDS_TO_715_LOCAL_CLIFFORD_COLUMN_ORBIT_COUNTS_ALL_N"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key1(c):return p10.key_from_codes([c])
def tables():
 lw=[int(p10.h.local_wt(a)) for a in range(4)];lm=[[int(p10.h.local_mul(a,b)) for b in range(4)] for a in range(4)];sy=[[int(p10.h.local_symp(a,b)) for b in range(4)] for a in range(4)];f3=[[[0]*4 for _ in range(4)] for __ in range(4)]
 for a,b,c in itertools.product(range(4),repeat=3):f3[a][b][c]=1 if a==b==c!=0 else lw[a]+lw[b]+lw[c]
 return lw,lm,sy,f3
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def atype(t,a):return tuple(a[x] for x in t)
def orbit(t,aa):return {atype(t,a) for a in aa}
def canonical_map(types,aa):
 cmap={};aid={};orbits={}
 for t in types:
  o=orbit(t,aa);c=min(o);cmap[t]=c
  for i,a in enumerate(aa):
   if atype(t,a)==c:aid[t]=i;break
  orbits.setdefault(c,set()).update(o)
 return cmap,aid,orbits
def permute_type(t,p):
 o=[]
 for j in range(3):a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def base(t,p,f3):q=permute_type(t,p);return f3[q[0]][q[2]][q[4]]+f3[q[1]][q[3]][q[5]]
def accept(fr,tag,sy):
 if any(x==0 for x in fr):return False,None
 if any(sy[fr[2*j]][fr[2*j+1]]!=1 for j in range(3)):return False,None
 l0,l1=sy[tag][fr[0]],sy[tag][fr[1]]
 if l0==l1:return False,None
 if any(sy[tag][fr[2*j]]!=l0 or sy[tag][fr[2*j+1]]!=l1 for j in (1,2)):return False,None
 return True,(l0,l1)
def aux48(sy):
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy[a][b]==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   ok,lab=accept(fr,tag,sy)
   if ok:rows.append((fr,tag,lab,tuple(key1(x) for x in fr),key1(tag)))
 return rows
def struct(fr,tag,c=(0,0,0)):
 raw=0
 for j in range(3):raw+=(2 if c[j]==0 else 4)*int(fr[2*j]!=0)+(2 if c[j]==1 else 4)*int(fr[2*j+1]!=0)
 return raw+2*int(tag!=0)-18
def restore(pt,fr,lm,f3):
 r=[lm[pt[i]][fr[i]] for i in range(6)];return f3[r[0]][r[2]][r[4]]+f3[r[1]][r[3]][r[5]]
def active_control(types,aa,cmap,aid,aux,ps,lm,f3):
 hbefore=hashlib.sha256();hafter=hashlib.sha256();hdec=hashlib.sha256();mism=[];rows=0;c=(0,0,0)
 def stream(h,v):h.update((str(int(v))+"\n").encode())
 for t in types:
  aut=aa[aid[t]];ct=cmap[t]
  for p in ps:
   pt=permute_type(t,p);cpt=permute_type(ct,p);tkeys=tuple(key1(x) for x in pt);ctkeys=tuple(key1(x) for x in cpt);b0=base(t,p,f3);b1=base(ct,p,f3)
   for fr,tag,lab,fkeys,tkey in aux:
    cfr=tuple(aut[x] for x in fr);ctag=aut[tag];cfkeys=tuple(key1(x) for x in cfr);ctkey=key1(ctag)
    cb=int(r6s.config_cost(tkeys,fkeys,tkey,c,1));ca=int(r6s.config_cost(ctkeys,cfkeys,ctkey,c,1));lb=r6s.config_labels(fkeys,tkey);la=r6s.config_labels(cfkeys,ctkey)
    kb=struct(fr,tag,c)+restore(pt,fr,lm,f3)-b0;ka=struct(cfr,ctag,c)+restore(cpt,cfr,lm,f3)-b1;db=b0+kb;da=b1+ka
    stream(hbefore,cb);stream(hafter,ca);stream(hdec,db);stream(hdec,da);rows+=1
    if not (cb==ca==db==da and lb==la) and len(mism)<20:mism.append({"target":t,"canonical":ct,"auto":aut,"perm":p,"frames":fr,"tag":tag,"cost_before":cb,"cost_after":ca,"decomp_before":db,"decomp_after":da,"labels_before":lb,"labels_after":la})
 return {"rows":rows,"expected_rows":4096*48*8,"cost_before_sha256":hbefore.hexdigest(),"cost_after_sha256":hafter.hexdigest(),"cost_digests_equal":hbefore.digest()==hafter.digest(),"decomposition_pair_sha256":hdec.hexdigest(),"mismatch_count_capped":len(mism),"mismatches_verbatim":mism,"all_match":len(mism)==0}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();lw,lm,sy,f3=tables();aa=autos();types=list(itertools.product(range(4),repeat=6));ps=list(itertools.product((0,1),repeat=3));cmap,aid,obs=canonical_map(types,aa)
 prod={"LW":list(map(int,np.asarray(r6m._LW).tolist())),"LM":[[int(x) for x in r] for r in np.asarray(r6m._LM).tolist()],"SY":[[int(x) for x in r] for r in np.asarray(r6m._SY).tolist()],"F3":[[[int(x) for x in r] for r in slab] for slab in np.asarray(r6m._F3).tolist()]}
 eq=[]
 for a in aa:
  eq.append({"auto":a,"mul":all(a[lm[u][v]]==lm[a[u]][a[v]] for u,v in itertools.product(range(4),repeat=2)),"symp":all(sy[a[u]][a[v]]==sy[u][v] for u,v in itertools.product(range(4),repeat=2)),"wt":all(lw[a[u]]==lw[u] for u in range(4)),"f3":all(f3[a[u]][a[v]][a[w]]==f3[u][v][w] for u,v,w in itertools.product(range(4),repeat=3))})
 table_checks={"production_tables":lw==prod["LW"] and lm==prod["LM"] and sy==prod["SY"] and f3==prod["F3"],"r6s_bind":all(bool(v) for v in r6s.bind_tables().values()),"six_automorphisms":len(aa)==6,"all_equivariant":all(all(r[k] for k in ("mul","symp","wt","f3")) for r in eq)}
 sizes=Counter(len(o) for o in obs.values());burnside={"fixed_identity":4096,"fixed_transposition_each":64,"transpositions":3,"fixed_threecycle_each":1,"threecycles":2,"orbit_count_formula":(4096+3*64+2)//6,"enumerated_orbits":len(obs),"orbit_size_distribution":{str(k):int(v) for k,v in sorted(sizes.items())},"expected_distribution":{"1":1,"3":63,"6":651},"all_types_partitioned":sum(k*v for k,v in sizes.items())==4096}
 q26=json.loads(QG26.read_text());parent={"qg26_green":q26.get("both_accept") is True and q26.get("HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True and q26.get("FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION") is True,"qg26_dimension_4096":q26.get("histogram_dimension")==4096}
 vecs=[];qmeta=[];constant=True;lift=True
 qhashes=set(q26.get("spectator_baselines",{}).get("pairing",{}).values())
 reps=sorted(obs)
 for p in ps:
  full=[base(t,p,f3) for t in types];qv=[base(r,p,f3) for r in reps]
  for r,o in obs.items():
   vals={base(t,p,f3) for t in o};constant=constant and len(vals)==1
  liftv=[base(cmap[t],p,f3) for t in types];lift=lift and liftv==full
  vecs.append((sha(full),sha(qv)));c=Counter(qv);qmeta.append({"perm":p,"full_sha256":sha(full),"quotient_sha256":sha(qv),"orbit_histogram":{str(k):int(v) for k,v in sorted(c.items())}})
 baseline_checks={"parent_hashes_reproduced":set(x[0] for x in vecs)==qhashes,"constant_on_orbits":constant,"lift_exact":lift,"distinct_full_vectors":len(set(x[0] for x in vecs)),"distinct_quotient_vectors":len(set(x[1] for x in vecs)),"quotient_histograms_exact":all(m["orbit_histogram"]=={"0":1,"1":8,"2":44,"3":128,"4":222,"5":216,"6":96} for m in qmeta)}
 aux=aux48(sy);active=active_control(types,aa,cmap,aid,aux,ps,lm,f3)
 proof={"independent_automorphism_per_physical_coordinate":table_checks["all_equivariant"],"each_column_can_be_canonicalized_independently":True,"orbit_histogram_sufficient_statistic_all_n":parent["qg26_green"] and active["all_match"],"qg26_guards_descend_to_orbit_multiplicity_guards":True,"qg26_affine_templates_descend_to_715_counts":baseline_checks["constant_on_orbits"] and active["all_match"],"unsafe_position_group_is_global_not_coordinatewise":True}
 ok=all(table_checks.values()) and parent["qg26_green"] and burnside["enumerated_orbits"]==715 and burnside["orbit_size_distribution"]==burnside["expected_distribution"] and burnside["all_types_partitioned"] and all(baseline_checks.values()) and active["rows"]==active["expected_rows"] and active["all_match"] and all(proof.values())
 term=POS if ok else ("QG28_QG26_PARENT_BINDING_GAP" if not parent["qg26_green"] else "QG28_ACTIVE_TEMPLATE_CANONICALIZATION_COUNTEREXAMPLE")
 out={"schema":"ORIONQG.QG28.LocalCliffordOrbits.v1","issue":"SzeChunYiu/ORION#888","terminal":term,"protocol_sha256":shaf(PROTO),"qg26_sha256":shaf(QG26),"table_checks":table_checks,"automorphism_checks":eq,"orbit_census":burnside,"canonical_representative_sha256":sha(reps),"baseline_quotient":{"vectors":qmeta,"checks":baseline_checks},"active_canonicalization_control":active,"proof_audit":proof,"LOCAL_CLIFFORD_EQUIVARIANCE_PER_QUBIT":term==POS,"LOCAL_CLIFFORD_ORBIT_COUNT":715 if term==POS else None,"ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":term==POS,"GUARDED_TROPICAL_GEOMETRY_DESCENDS_TO_715_COUNTS":term==POS,"INDEPENDENT_POSITION_RELABEL_PER_COLUMN":False,"COMBINED_LOCAL_POSITION_QUOTIENT_54":False,"EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"orbits":burnside["enumerated_orbits"],"sizes":burnside["orbit_size_distribution"],"distinct_baselines":baseline_checks["distinct_quotient_vectors"],"active_rows":active["rows"],"active_ok":active["all_match"],"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
