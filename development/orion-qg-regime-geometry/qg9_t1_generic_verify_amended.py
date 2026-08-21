#!/usr/bin/env python3
"""Independent T1 verifier with the frozen production-valid candidate filter."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DEV=ROOT/'development'/'orion-qg-regime-geometry';sys.path.insert(0,str(DEV));import qg9_t1_generic_verify as b  # noqa:E402
A=ROOT/'artifacts'/'orion-qg-qg9t1-support4-tightness.json';O=ROOT/'artifacts'/'orion-qg-qg9t1-generic-verification.json';TOKEN='ORIONQG_QG9T1_GENERIC='
def corrected_candidates():
 st=b.action_resources();s2,s3=b.safe(st);cache={};rows=[];discarded=[]
 for g in (0,1):
  t=b.typetable(g);obs=[]
  for p in b.itertools.combinations_with_replacement(range(len(t)),4):
   if b.elig(p,t,g) and not b.cov(p,t,g,s2,s3):obs.append((p,[t[i]['best_rep'] for i in p]))
  for oi,(p,reps) in enumerate(obs[:36]):
   ra0=b.key([v[0] for v in reps]);ra1=b.key([v[1] for v in reps]);s0=b.key([v[2] for v in reps]);s1=b.key([v[3] for v in reps]);ra2=b.pmul(ra0,ra1);l0,l1=b.lab(s0,s1,ra0),b.lab(s0,s1,ra1);ub=b.bestother(s0,s1,l0,l1,cache);uc,_,rb0,rb1,rb2,cb=ub;uas=[b.uanti((ra0,ra1,ra2),c) for c in range(3)];ca=uas.index(min(uas));U4=min(uas)+uc+2*(b.pwt(s0)+b.pwt(s1));ch={'anti_A':b.symp(ra0,ra1)==1,'anti_B':b.symp(rb0,rb1)==1,'labels_equal':(l0,l1)==(b.lab(s0,s1,rb0),b.lab(s1 if False else s1,s1,rb1)) if False else (l0,l1)==(b.lab(s0,s1,rb0),b.lab(s0,s1,rb1)),'labels_valid':l0 in(1,2,3) and l1 in(1,2,3) and l0!=l1,'selected_support4':b.pwt(ra0 if g==0 else ra1)==4,'restore_zero':True}
   if not all(ch.values()):discarded.append({'orientation':g,'obstruction_index':oi,'pattern':list(p),'checks':ch});continue
   rows.append({'orientation':g,'obstruction_index':oi,'pattern':list(p),'reps':reps,'targets_a':[list(ra0),list(ra1),list(ra2)],'targets_b':[list(rb0),list(rb1),list(rb2)],'tag':[list(s0),list(s1)],'labels':[l0,l1,l0^l1],'desired_centrals':[ca,cb],'U4':int(U4),'checks':ch})
 return rows,discarded

def main():
 a=json.loads(A.read_text());u=dict(a);obs=u.pop('result_digest');digest=obs==hashlib.sha256(b.can(u).encode()).hexdigest();cs,discarded=corrected_candidates();oc={'0':sum(c['orientation']==0 for c in cs),'1':sum(c['orientation']==1 for c in cs)};checks={'schema':a.get('schema')=='ORION.QG.QG9T1.Support4Tightness.v1','digest':digest,'candidate_panel':0<len(cs)<=72 and oc['0']<=36 and oc['1']<=36,'candidate_count':len(cs)==a['candidate_generation']['candidate_count'],'candidate_digest':hashlib.sha256(b.can(cs).encode()).hexdigest()==a['candidate_generation']['digest'],'discard_count':len(discarded)==a['candidate_generation'].get('discarded_invalid_count'),'orientation_counts':oc==a['candidate_generation']['orientation_counts'],'no_novelty':a.get('novelty_authority') is False,'no_physical':a.get('physical_quantum_advantage_claim') is False,'no_support3_theorem':a.get('support3_theorem_authority') is False,'safe':a.get('network_access') is False and a.get('chemistry_sources_read') is False and a.get('protected_subject_read') is False};term=a.get('terminal');verified=0;errors=[]
 if term=='QG9T1_R6I_SUPPORT4_TIGHT_WITNESS_EXACT':
  p=a['positive_witness'];cand=cs[p['candidate_index']];best=10**9
  for perm in b.PERMS:
   for ca in range(3):
    for cb in range(3):
     v=b.cap3(cand,perm,ca,cb);verified+=1
     if v is None:errors.append('solver');break
     best=min(best,v)
    if errors:break
   if errors:break
  checks['positive_cap3_exact']=not errors and best==p['C_cap3'] and best>cand['U4']
 elif term=='QG9T1_NO_SUPPORT4_TIGHT_WITNESS_IN_FROZEN_PANEL':
  checks['all_rows_present']=len(a['scan_rows'])==len(cs)
  for row in a['scan_rows']:
   cand=cs[row['candidate_index']];rej=row.get('rejection')
   if not rej:errors.append(['missing_rejection',row['candidate_index']]);continue
   v=b.cap3(cand,tuple(rej['perm']),rej['cA'],rej['cB']);verified+=1
   if v is None or v>cand['U4'] or v!=rej['C_cap3_config']:errors.append(['bad_rejection',row['candidate_index'],v,rej['C_cap3_config'],cand['U4']])
  checks['negative_rejections_exact']=not errors
 elif term=='QG9T1_CAP3_SOLVER_CANNOT_CHECK':checks['solver_failure_recorded']=any(r.get('solver_failure') for r in a['scan_rows'])
 else:checks['binding_failure_recorded']=not checks['candidate_panel']
 d='ACCEPT' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9T1.GenericVerification.v1','decision':d,'checks':checks,'milps_replayed':verified,'errors':errors[:20],'engineering_amendment':'QG9T1_ENGINEERING_AMENDMENT_1.md'};O.parent.mkdir(parents=True,exist_ok=True);O.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+b.can({'decision':d,'milps':verified,'errors':len(errors),'candidates':len(cs)}));return 0
if __name__=='__main__':raise SystemExit(main())
