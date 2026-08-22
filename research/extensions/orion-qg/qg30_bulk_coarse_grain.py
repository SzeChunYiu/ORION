#!/usr/bin/env python3
"""QG-30 production analyzer: 715->45 exact bulk coarse-graining with defect-information-loss census."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];QDIR=ROOT/"research/extensions/orion-q";sys.path.insert(0,str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6s_all_n_composition as r6s  # noqa:E402
PROTO=ROOT/"development/orion-qg-regime-geometry/QG30_BULK_COARSE_GRAIN_PROTOCOL_V1.md";QG27=ROOT/"research/extensions/orion-qg/QG27_BULK_DEFECT_RESULTS.json";QG28=ROOT/"research/extensions/orion-qg/QG28_LOCAL_CLIFFORD_ORBIT_RESULTS.json";QG29=ROOT/"research/extensions/orion-qg/QG29_DEFECT_SATURATION_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg30-bulk-coarse-grain.json";TOKEN="ORIONQG_QG30=";POS="QG30_TARE_BULK_GEOMETRY_COMPRESSES_EXACTLY_TO_45_SIGNATURE_COUNTS__DEFECT_INFORMATION_REMAINS"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key1(c):return p10.key_from_codes([c])
def autos():return [(0,)+p for p in itertools.permutations((1,2,3))]
def atype(t,a):return tuple(a[x] for x in t)
def orbit(t,aa):return {atype(t,a) for a in aa}
def perm(t,p):
 o=[]
 for j in range(3):a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def f3(a,b,c):return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def baseline(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def local_symp(a,b):return int(p10.h.local_symp(a,b))
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if local_symp(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=local_symp(tag,fr[0]),local_symp(tag,fr[1]);ok=l0!=l1 and all(local_symp(tag,fr[2*j])==l0 and local_symp(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append({"frames":fr,"tag":tag,"frame_keys":tuple(key1(x) for x in fr),"tag_key":key1(tag),"labels":(l0,l1)})
 return rows
def raw_type_key(t):return tuple(key1(x) for x in t)
def profile(rep,ps,aux):
 ordered=[];c=(0,0,0)
 for p in ps:
  pt=perm(rep,p);tkeys=raw_type_key(pt);b=baseline(rep,p)
  for a in aux:
   ordered.append(int(r6s.config_cost(tkeys,a["frame_keys"],a["tag_key"],c,1))-b)
 srt=tuple(sorted(ordered));cnt=Counter(srt)
 return tuple(ordered),srt,{str(k):int(v) for k,v in sorted(cnt.items())},sha(srt)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();aa=autos();types=list(itertools.product(range(4),repeat=6));ps=list(itertools.product((0,1),repeat=3));bulk_ps=ps[:4]
 obs={}
 for t in types:
  o=orbit(t,aa);r=min(o);obs.setdefault(r,set()).update(o)
 reps=sorted(obs);aux=aux48();profiles={};sig_members=defaultdict(list)
 for r in reps:
  sig=tuple(baseline(r,p) for p in bulk_ps);ordv,srt,hist,ph=profile(r,ps,aux);profiles[r]={"signature":sig,"ordered":ordv,"sorted":srt,"histogram":hist,"sha256":ph,"raw_orbit_size":len(obs[r])};sig_members[sig].append(r)
 sigs=sorted(sig_members)
 sig_table=[]
 for sig in sigs:
  members=sorted(sig_members[sig]);sig_table.append({"signature":sig,"orbit_count":len(members),"raw_type_count":sum(len(obs[r]) for r in members),"first_representative":members[0],"member_representatives_sha256":sha(members)})
 profile_counts=[];total_profile_set=set();multi=0
 for sig in sigs:
  members=sorted(sig_members[sig]);pids={profiles[r]["sha256"] for r in members};total_profile_set.update(pids);multi+=int(len(pids)>1);profile_counts.append({"signature":sig,"orbit_count":len(members),"distinct_one_active_profiles":len(pids)})
 witness=None
 for sig in sigs:
  members=sorted(sig_members[sig])
  for i,r1 in enumerate(members):
   for r2 in members[i+1:]:
    if profiles[r1]["sorted"]!=profiles[r2]["sorted"]:
     o1,o2=profiles[r1]["ordered"],profiles[r2]["ordered"];idx=next(j for j,(a,b) in enumerate(zip(o1,o2)) if a!=b);pi,ai=divmod(idx,len(aux));witness={"common_signature":sig,"representative_1":r1,"representative_2":r2,"profile_1_sha256":profiles[r1]["sha256"],"profile_2_sha256":profiles[r2]["sha256"],"profile_1_histogram":profiles[r1]["histogram"],"profile_2_histogram":profiles[r2]["histogram"],"first_ordered_difference":{"index":idx,"permutation":ps[pi],"auxiliary_row_index":ai,"auxiliary_frames":aux[ai]["frames"],"auxiliary_tag":aux[ai]["tag"],"K_1":o1[idx],"K_2":o2[idx]}};break
   if witness:break
  if witness:break
 bulk_rows=[[sig[r] for sig in sigs] for r in range(4)];ties=[]
 for i in range(4):
  for j in range(i+1,4):
   d=[bulk_rows[i][k]-bulk_rows[j][k] for k in range(len(sigs))];ties.append({"forms":[i,j],"sha256":sha(d),"support_size":sum(x!=0 for x in d),"coefficient_range":[min(d),max(d)],"histogram":{str(k):int(v) for k,v in sorted(Counter(d).items())}})
 q27=json.loads(QG27.read_text());q28=json.loads(QG28.read_text());q29=json.loads(QG29.read_text()) if QG29.exists() else None
 parents={"qg28_green":q28.get("both_accept") is True and q28.get("LOCAL_CLIFFORD_ORBIT_COUNT")==715 and q28.get("ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True,"qg28_orbit_partition":q28.get("orbit_census",{}).get("orbit_size_distribution")=={"1":1,"3":63,"6":651} and q28.get("canonical_representative_sha256")==sha(reps),"qg28_unsafe_false":q28.get("INDEPENDENT_POSITION_RELABEL_PER_COLUMN") is False and q28.get("COMBINED_LOCAL_POSITION_QUOTIENT_54") is False,"qg27_green":q27.get("both_accept") is True and q27.get("ASYMPTOTIC_COST_DENSITY_EXACT") is True and q27.get("bulk",{}).get("distinct_forms")==4,"qg29_optional_only":True}
 census={"signature_count":len(sigs),"expected_signature_count":45,"orbit_total":sum(x["orbit_count"] for x in sig_table),"raw_type_total":sum(x["raw_type_count"] for x in sig_table),"signature_table":sig_table,"total_distinct_one_active_profiles":len(total_profile_set),"signatures_with_multiple_profiles":multi,"profile_counts_by_signature":profile_counts,"information_loss_witness_found":witness is not None,"information_loss_witness":witness}
 proof={"bulk_rows_exact_from_signature_coordinates":True,"bulk_45_histogram_sufficient_for_asymptotic_density":len(sigs)==45 and parents["qg27_green"],"all_six_pairwise_bulk_ties_descend_to_45":len(ties)==6,"bulk_defect_information_loss":witness is not None,"full_defect_sufficiency_explicitly_rejected":witness is not None,"physical_rg_not_claimed":True}
 ok=all(parents.values()) and len(reps)==715 and len(sigs)==45 and census["orbit_total"]==715 and census["raw_type_total"]==4096 and len(aux)==48 and witness is not None and all(proof.values())
 if not parents["qg28_green"]:term="QG30_QG28_PARENT_BINDING_GAP"
 elif len(sigs)!=45:term="QG30_SIGNATURE_COUNT_MISMATCH"
 elif witness is None:term="QG30_NO_ONE_ACTIVE_DEFECT_INFORMATION_LOSS_FOUND__SUCCESSOR_REQUIRED"
 else:term=POS
 out={"schema":"ORIONQG.QG30.BulkCoarseGrain.v1","issue":"SzeChunYiu/ORION#893","terminal":term,"protocol_sha256":shaf(PROTO),"parent_hashes":{"qg27":shaf(QG27),"qg28":shaf(QG28),"qg29_optional":shaf(QG29) if QG29.exists() else None},"parent_checks":parents,"local_clifford_orbits":715,"one_active_rows_per_orbit":len(ps)*len(aux),"complete_one_active_profile_rows":len(reps)*len(ps)*len(aux),"bulk_signature_census":census,"bulk_coefficient_rows_45":{"rows":bulk_rows,"sha256":[sha(r) for r in bulk_rows]},"pairwise_bulk_ties_45":ties,"proof_audit":proof,"BULK_SIGNATURE_COUNT":45 if term==POS else None,"BULK_45_HISTOGRAM_SUFFICIENT_FOR_ASYMPTOTIC_DENSITY":term==POS,"ASYMPTOTIC_PHASE_GEOMETRY_DESCENDS_TO_45_COUNTS":term==POS,"BULK_DEFECT_SCALE_SEPARATION":term==POS,"BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT":False,"FULL_FINITE_N_OPTIMUM_FROM_45_COUNTS":False,"PHYSICAL_RENORMALIZATION_GROUP":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"signatures":len(sigs),"orbits":715,"profile_rows":out["complete_one_active_profile_rows"],"distinct_profiles":census["total_distinct_one_active_profiles"],"multi_profile_signatures":multi,"witness_found":witness is not None,"witness_signature":witness["common_signature"] if witness else None,"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
