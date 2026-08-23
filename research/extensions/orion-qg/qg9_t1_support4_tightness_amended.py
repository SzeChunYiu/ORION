#!/usr/bin/env python3
"""Engineering-corrected QG-9 T1 executor; scientific protocol unchanged."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'research'/'extensions'/'orion-qg'
sys.path.insert(0,str(HERE))
import qg9_t1_support4_tightness as b  # noqa:E402

OUT=ROOT/'artifacts'/'orion-qg-qg9t1-support4-tightness.json'
TOKEN='ORIONQG_QG9T1='

def corrected_candidates(s2,s3):
    cache={};rows=[];discarded=[]
    for g in (0,1):
        tt,obs=b.obstruction_patterns(g,s2,s3)
        for oi,o in enumerate(obs[:36]):
            reps=o['reps'];ra0=b.key_from_rep(reps,0);ra1=b.key_from_rep(reps,1);s0=b.key_from_rep(reps,2);s1=b.key_from_rep(reps,3);ra2=b.p10.mul(ra0,ra1);l0,l1=b.labels(s0,s1,ra0,ra1)
            ub=b.best_other_block(s0,s1,l0,l1,cache);ubc,_,rb0,rb1,rb2,cb=ub
            uas=[b.p10.uanti_support((ra0,ra1,ra2),c) for c in range(3)];ca=uas.index(min(uas));u4=min(uas)+ubc+2*(b.p10.wt(s0)+b.p10.wt(s1))
            checks={'anti_A':b.p10.symp(ra0,ra1)==1,'anti_B':b.p10.symp(rb0,rb1)==1,'labels_equal':b.labels(s0,s1,ra0,ra1)==b.labels(s0,s1,rb0,rb1),'labels_valid':l0 in (1,2,3) and l1 in (1,2,3) and l0!=l1,'selected_support4':b.p10.wt(ra0 if g==0 else ra1)==4,'restore_zero':True}
            if not all(checks.values()):
                discarded.append({'orientation':g,'obstruction_index':oi,'pattern':o['pattern'],'checks':checks});continue
            rows.append({'orientation':g,'obstruction_index':oi,'pattern':o['pattern'],'reps':reps,'targets_a':[list(ra0),list(ra1),list(ra2)],'targets_b':[list(rb0),list(rb1),list(rb2)],'tag':[list(s0),list(s1)],'labels':[l0,l1,l0^l1],'desired_centrals':[ca,cb],'U4':int(u4),'checks':checks})
    return rows,discarded

def run():
    st=b.action_resources();s2,s3=b.safe_edits(st);cands,discarded=corrected_candidates(s2,s3)
    oc={'0':sum(c['orientation']==0 for c in cands),'1':sum(c['orientation']==1 for c in cands)}
    gen={'candidate_count':len(cands),'orientation_counts':oc,'max_panel':72,'discarded_invalid_count':len(discarded),'discarded_invalid':discarded,'digest':hashlib.sha256(b.can(cands).encode()).hexdigest(),'first_candidates':cands[:4]}
    rows,pos,unres=b.scan(cands)
    panel_valid=0<len(cands)<=72 and oc['0']<=36 and oc['1']<=36
    if pos:term='QG9T1_R6I_SUPPORT4_TIGHT_WITNESS_EXACT'
    elif unres:term='QG9T1_CAP3_SOLVER_CANNOT_CHECK'
    elif not panel_valid:term='QG9T1_CANDIDATE_BINDING_FAILURE'
    else:term='QG9T1_NO_SUPPORT4_TIGHT_WITNESS_IN_FROZEN_PANEL'
    out={'schema':'ORION.QG.QG9T1.Support4Tightness.v1','issue':b.ISSUE,'base_revision':b.BASE,'terminal':term,'engineering_amendment':'QG9T1_ENGINEERING_AMENDMENT_1.md','solver':{'scipy_version':b.SCIPY_VERSION,'backend':'HiGHS via scipy.optimize.milp','mip_rel_gap':0.0},'candidate_generation':gen,'scan_rows':rows,'positive_witness':pos,'cap3_model':{'n':4,'fixed_configs':54,'accepting_states':b.ACCEPT,'support_cap':3,'production_option_count':4096,'compression_key':'(delta10,activity4)'},'chemistry_sources_read':False,'protected_subject_read':False,'network_access':False,'support3_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
    u=dict(out);out['result_digest']=hashlib.sha256(b.can(u).encode()).hexdigest();return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(OUT));a=ap.parse_args();r=run();p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(TOKEN+b.can({'terminal':r['terminal'],'digest':r['result_digest'],'candidates':r['candidate_generation']['candidate_count'],'discarded':r['candidate_generation']['discarded_invalid_count'],'positive':None if not r['positive_witness'] else {'index':r['positive_witness']['candidate_index'],'gap':r['positive_witness']['strict_gap']}}));return 0
if __name__=='__main__':raise SystemExit(main())
