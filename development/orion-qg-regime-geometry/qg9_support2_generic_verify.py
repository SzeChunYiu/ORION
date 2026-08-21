#!/usr/bin/env python3
"""Independent QG-9 V4 verifier built on the independently implemented V3 algebra/search."""
from __future__ import annotations
import hashlib,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'development/orion-qg-regime-geometry'))
import qg9_support3_generic_verify as gv3  # noqa: E402
ART=ROOT/'artifacts/orion-qg-qg9-support2-full-acceptance.json';OUT=ROOT/'artifacts/orion-qg-qg9-support2-generic-verification.json';TOKEN='ORIONQG_QG9_SUPPORT2_GENERIC='
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def accepted(co):
 a=u0=v0=u1=v1=0
 for d in co:a^=d[3];u0^=d[4];v0^=d[5];u1^=d[6];v1^=d[7]
 c0=2*u0+v0;c1=2*u1+v1
 return a==1 and c0 in (1,2,3) and c1 in (1,2,3) and c0!=c1

def boundary(w,descs,oldp,byd,acts):
 ret,surv=gv3.survivors(w,descs,oldp);tc=bu=ac=asu=0
 for inds in surv:
  co=[descs[i] for i in inds];ok=accepted(co)
  for keys in itertools.product(*[byd[d] for d in co]):
   tc+=1;safe=gv3.rich_safe(keys,acts)
   if not safe:bu+=1
   if ok:
    ac+=1;asu+=int(not safe)
 return {'retained':len(ret),'survivors':len(surv),'type_cases':tc,'broad_unsafe':bu,'accepted_type_cases':ac,'accepted_unsafe':asu}
def main():
 a=json.loads(ART.read_text());tmp=dict(a);obs=tmp.pop('result_digest',None);digest=hashlib.sha256(canon(tmp).encode()).hexdigest();reps,oldp=gv3.old_profiles();descs=sorted(reps);states,acts,byd=gv3.build_rich_types();b3=boundary(3,descs,oldp,byd,acts);b2=boundary(2,descs,oldp,byd,acts)
 checks={'digest':obs==digest,'descriptor_count':len(descs)==28,'support3_retained':b3['retained']==a['support3_full_acceptance']['qg1_irreducible_descriptor_count'],'support3_survivors':b3['survivors']==a['support3_full_acceptance']['v2_survivor_descriptor_count'],'support3_type_cases':b3['type_cases']==a['support3_full_acceptance']['v3_action_profile_type_cases'],'support3_broad_unsafe':b3['broad_unsafe']==a['support3_full_acceptance']['v3_broad_unsafe_type_cases'],'support3_accepted_count':b3['accepted_type_cases']==a['support3_full_acceptance']['full_accepted_type_cases'],'support3_zero_accepted_unsafe':b3['accepted_unsafe']==0==a['support3_full_acceptance']['full_accepted_unsafe_type_cases'],'support2_counts':b2['accepted_type_cases']==a['support2_boundary_control']['full_accepted_type_cases'] and b2['accepted_unsafe']==a['support2_boundary_control']['full_accepted_unsafe_type_cases'],'support2_obstruction_nonempty':b2['accepted_unsafe']>0,'authority_false':a['support1_claim'] is False and a['tightness_claim'] is False and a['novelty_authority'] is False}
 dec='ACCEPT' if all(checks.values()) and a['terminal']=='QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED' else 'REJECT';out={'schema':'ORION.QG.QG9.Support2GenericVerification.v1','decision':dec,'checks':checks,'independent_counts':{'support3':b3,'support2':b2,'action_profile_types':len(states)},'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
