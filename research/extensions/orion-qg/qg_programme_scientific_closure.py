#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; QG=ROOT/'research/extensions/orion-qg'; DEV=ROOT/'development/orion-qg-regime-geometry'; OUT=ROOT/'artifacts/orion-qg-programme-scientific-closure.json'; TOKEN='ORIONQG_PROGRAMME_CLOSURE='
PROTOCOL=DEV/'QG_PROGRAMME_SCIENTIFIC_CLOSURE_PROTOCOL_V1.md'; INDEX=DEV/'QG_PROGRAMME_CLOSURE_EVIDENCE_V1.json'; SUPP=DEV/'QG7D_SUPPLEMENTAL_N2_EVIDENCE_V1.json'; W1=DEV/'QG_WAVE1_CLOSURE_PACKET.md'; W2=DEV/'QG_WAVE2_RECORD.md'
PARENTS={'qg7c':QG/'QG7C_CLASSIFICATION_RESULTS.json','qg9v6':QG/'QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json','qg12':QG/'QG12_SIXLCU_P0_THEOREM_RESULTS.json','qg15b':QG/'QG15B_PREDICATE_LANGUAGE_RESULTS.json'}
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args(); idx=json.loads(INDEX.read_text()); e=idx['evidence']; supp=json.loads(SUPP.read_text()); p={k:json.loads(v.read_text()) for k,v in PARENTS.items()}
 expected={'portfolio','qg18','qg17r','qg15c','qg10c','qg11c','qg14c','qg7d'}; terminals={k:v['terminal'] for k,v in e.items()}
 gates={
  'protocol_index_supplement':PROTOCOL.exists() and INDEX.exists() and SUPP.exists(),
  'canonical_main':idx.get('canonical_main')=='c5ba39fef4f25c46de5fb69bf07f50530f4693ca',
  'evidence_keys':set(e)==expected,
  'all_result_digests_sha256':all(len(v['result_digest'])==64 and all(c in '0123456789abcdef' for c in v['result_digest']) for v in e.values()),
  'all_artifact_digests_bound':all(str(v['artifact_digest']).startswith('sha256:') and len(v['artifact_digest'])==71 for v in e.values()),
  'portfolio_terminal':e['portfolio']['terminal']=='ORION_QG_EARNED_PORTFOLIO_LANES_ADJUDICATED_CLOSED__MIXED_THEOREM_REFUTATION_BOUNDARIES_PRESERVED' and set(e['portfolio']['covers'])=={'QG-2','QG-3','QG-4','QG-5','QG-6','QG-8','QG-12','QG-13'},
  'qg18_kappa2':e['qg18']['terminal']=='QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_MACHINE_VERIFIED' and e['qg18']['facts']['kappa_TARE']==2 and e['qg18']['facts']['cap1']==8 and e['qg18']['facts']['dp']==7,
  'qg17_bounded_negative':e['qg17r']['terminal']=='QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN' and e['qg17r']['facts']['candidates']==211248 and not e['qg17r']['facts']['global_phase_boundary_complete'] and sum(e['qg17r']['facts'][k] for k in ('strict_O0','strict_O_tag_out','strict_O_restore_out','strict_O_nc_out'))==0,
  'qg15c_negative':e['qg15c']['terminal']=='QG15C_ENLARGED_DONOR_PATH_VOCABULARY_STILL_INSUFFICIENT__MIXED_CELLS_MACHINE_VERIFIED' and e['qg15c']['facts']['mixed_cells']==3 and e['qg15c']['facts']['irreducible_floor']==5 and not e['qg15c']['facts']['heldout_stage_authorized'],
  'qg10_bounded':e['qg10c']['terminal']=='QG10_SOUND_CERTIFICATION_CALIBRATED__INCREMENTAL_INTERVAL_VALUE_DONOR_DEPENDENT_OR_WEAK' and e['qg10c']['facts']['sixlcu_false']==0 and not e['qg10c']['facts']['new_scalable_interval_value_supported'],
  'qg11_boundary':e['qg11c']['terminal']=='QG11_AFFINE_FT_PHASE_PULLBACK_PROVED__NONLINEAR_FACTORY_COUNTEREXAMPLE__REAL_ESTIMATOR_CANNOT_CHECK' and e['qg11c']['facts']['real_ft_estimator']=='CANNOT_CHECK_REAL_ESTIMATOR' and e['qg11c']['facts']['route_A_structural']<e['qg11c']['facts']['route_B_structural'] and e['qg11c']['facts']['route_A_physical']>e['qg11c']['facts']['route_B_physical'],
  'qg14_bounded':e['qg14c']['terminal']=='QG14_SEPARABLE_COMPOSITION_PROVED__HIDDEN_COUPLING_REFUTES_LOCAL_SELECTION__COUPLING_AWARE_SUMMARY_RECOVERS_CONTROL' and e['qg14c']['facts']['separable_proved'] and e['qg14c']['facts']['independent_hidden_coupling_wrong'] and e['qg14c']['facts']['coupling_summary_recovers_control'] and not e['qg14c']['facts']['universal_interface_compression_claim'],
  'qg7d_cannot_check':e['qg7d']['terminal']=='QG7D_CANNOT_CHECK_ALL_N_PINNED_CLOSURE__PP_HIDDEN_HOME_ENVIRONMENT_NOT_IN_PARENT_STATE__PADDING_ABLATION_NEGATIVE' and e['qg7d']['facts']['pp_parent_failures']==32556 and e['qg7d']['facts']['hidden_home_domain']==4096 and e['qg7d']['facts']['hidden_home_delta_min']==-4 and e['qg7d']['facts']['hidden_home_delta_max']==4 and e['qg7d']['facts']['all_n_identity']=='UNPROVED_CANNOT_CHECK_FROM_CURRENT_PARENT_QUOTIENT' and e['qg7d']['facts']['btripleprime']=='UNFOUND_IN_FROZEN_PADDING_ABLATION',
  'qg7d_n2_supplemental_negative':supp.get('terminal')=='QG7D_N2_DIRECT_NO_GAP_IN_COMMITTED_T4B_ROWS' and supp.get('rows_evaluated')==40 and supp.get('identity_target_rows')==27 and supp.get('strict_witness_count')==0 and supp.get('generic_decision')=='ACCEPT_BOUNDED_NEGATIVE' and supp.get('native_decision')=='ACCEPT_BOUNDED_NEGATIVE' and supp.get('global_all_n_closure_authority') is False,
  'main_qg7c_parent_partial':p['qg7c'].get('terminal')=='QG7C_PARTIAL__L4B_OPEN' and p['qg7c']['t4b_pinned']['failures_total']==135604,
  'main_r6i_kappa1':p['qg9v6'].get('intrinsic_support_number')==1 and p['qg9v6'].get('both_accept') is True,
  'main_sixlcu_theorem':p['qg12'].get('terminal')=='QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED' and all(p['qg12'].get('gates',{}).values()),
  'main_stabprep_parent_negative':p['qg15b'].get('q2',{}).get('mixed_cell_count')==12 and p['qg15b'].get('q2',{}).get('E_floor')==43,
  'global_authority_false':all(v is False for v in idx['global_authority'].values()),
  'wave_ledgers_exist':W1.exists() and W2.exists(),
 }
 closed=all(gates.values()); terminal='ORION_QG_PROGRAMME_SCIENTIFICALLY_CLOSED__THEOREMS_REFUTATIONS_AND_BOUNDED_CANNOT_CHECKS_RECEIPTED__NOT_NOVELTY_AUTHORITY' if closed else 'ORION_QG_PROGRAMME_CLOSURE_REJECTED__EVIDENCE_OR_SCOPE_GAP'
 out={'schema':'ORION.QG.ProgrammeScientificClosure.v1','issue':'SzeChunYiu/ORION#839','programme_issue':'SzeChunYiu/ORION#740','terminal':terminal,'scientifically_closed':closed,'canonical_main':idx['canonical_main'],'protocol_sha256':sha(PROTOCOL),'evidence_index_sha256':sha(INDEX),'qg7d_supplemental_n2_sha256':sha(SUPP),'wave1_sha256':sha(W1),'wave2_sha256':sha(W2),'parent_sha256':{k:sha(v) for k,v in PARENTS.items()},'evidence_result_digests':{k:v['result_digest'] for k,v in e.items()},'evidence_artifact_digests':{k:v['artifact_digest'] for k,v in e.items()},'evidence_terminals':terminals,'supplemental_qg7d_n2':{'result_digest':supp['result_digest'],'artifact_digest':supp['artifact_digest'],'terminal':supp['terminal']},'gates':gates,'all_gates':closed,'bounded_cannot_checks':{'qg7d':'all-n Bsecond pinned PP closure cannot be checked from current state quotient','qg11':'real FT resource-estimator/backend transfer not checked'},'unproved_not_promoted':['TARE all-n C_DP=min(C_D+,f_Bprime,f_Bsecond)','global R6I weighted support phase boundary','real FT hardware phase map','universal compressed composition interface','universal low-order boundary predicate'],'future_reopen_requires_new_freeze':True,'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False,'publication_acceptance_authority':False}
 u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'closed':closed,'result_digest':out['result_digest'],'gates':gates})); return 0
if __name__=='__main__': raise SystemExit(main())
