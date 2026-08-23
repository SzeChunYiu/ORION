#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DEV=ROOT/'development/orion-qg-regime-geometry'; RESULT=ROOT/'artifacts/orion-qg-programme-scientific-closure.json'; INDEX=DEV/'QG_PROGRAMME_CLOSURE_EVIDENCE_V1.json'; SUPP=DEV/'QG7D_SUPPLEMENTAL_N2_EVIDENCE_V1.json'; PROTOCOL=DEV/'QG_PROGRAMME_SCIENTIFIC_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-programme-closure-generic.json'; TOKEN='ORIONQG_PROGRAMME_CLOSURE_GENERIC='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); idx=json.loads(INDEX.read_text()); supp=json.loads(SUPP.read_text()); u=dict(a); obs=u.pop('result_digest',None); e=idx['evidence']; expected={'portfolio','qg18','qg17r','qg15c','qg10c','qg11c','qg14c','qg7d'}
 closure_types={'portfolio':'MIXED_THEOREM_REFUTATION_BOUNDARIES_PRESERVED','qg18':'KAPPA_IS_2','qg17r':'NO_SUPPORT2_WITNESS','qg15c':'STILL_INSUFFICIENT','qg10c':'DONOR_DEPENDENT_OR_WEAK','qg11c':'REAL_ESTIMATOR_CANNOT_CHECK','qg14c':'HIDDEN_COUPLING_REFUTES_LOCAL_SELECTION','qg7d':'CANNOT_CHECK_ALL_N_PINNED_CLOSURE'}
 checks={
  'schema':a.get('schema')=='ORION.QG.ProgrammeScientificClosure.v1',
  'result_digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),
  'protocol_hash':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
  'index_hash':a.get('evidence_index_sha256')==hashlib.sha256(INDEX.read_bytes()).hexdigest(),
  'supplement_hash':a.get('qg7d_supplemental_n2_sha256')==hashlib.sha256(SUPP.read_bytes()).hexdigest(),
  'evidence_keys':set(e)==expected,
  'evidence_digests_bound':a.get('evidence_result_digests')=={k:v['result_digest'] for k,v in e.items()} and a.get('evidence_artifact_digests')=={k:v['artifact_digest'] for k,v in e.items()},
  'terminal_classes':all(closure_types[k] in e[k]['terminal'] for k in expected),
  'qg7d_not_theorem':e['qg7d']['facts']['all_n_identity'].startswith('UNPROVED_CANNOT_CHECK') and e['qg7d']['facts']['btripleprime'].startswith('UNFOUND'),
  'qg7d_n2_supplement':supp.get('terminal')=='QG7D_N2_DIRECT_NO_GAP_IN_COMMITTED_T4B_ROWS' and supp.get('rows_evaluated')==40 and supp.get('identity_target_rows')==27 and supp.get('strict_witness_count')==0 and supp.get('generic_decision')=='ACCEPT_BOUNDED_NEGATIVE' and supp.get('native_decision')=='ACCEPT_BOUNDED_NEGATIVE' and supp.get('global_all_n_closure_authority') is False and a.get('supplemental_qg7d_n2',{}).get('result_digest')==supp.get('result_digest'),
  'qg11_real_cannot_check':e['qg11c']['facts']['real_ft_estimator']=='CANNOT_CHECK_REAL_ESTIMATOR',
  'qg17_bounded':e['qg17r']['facts']['global_phase_boundary_complete'] is False and sum(e['qg17r']['facts'][k] for k in ('strict_O0','strict_O_tag_out','strict_O_restore_out','strict_O_nc_out'))==0,
  'qg10_no_incremental_scalable':e['qg10c']['facts']['new_scalable_interval_value_supported'] is False,
  'qg15c_no_heldout':e['qg15c']['facts']['mixed_cells']==3 and e['qg15c']['facts']['heldout_stage_authorized'] is False,
  'qg18_exact_kappa':e['qg18']['facts']['kappa_TARE']==2 and e['qg18']['facts']['dp']<e['qg18']['facts']['cap1'],
  'qg14_no_universal_compression':e['qg14c']['facts']['universal_interface_compression_claim'] is False,
  'portfolio_complete':set(e['portfolio']['covers'])=={'QG-2','QG-3','QG-4','QG-5','QG-6','QG-8','QG-12','QG-13'},
  'bounded_cannot_checks_named':set(a.get('bounded_cannot_checks',{}))=={'qg7d','qg11'},
  'unproved_list_nonempty':len(a.get('unproved_not_promoted',[]))>=5,
  'future_reopen_new_freeze':a.get('future_reopen_requires_new_freeze') is True,
  'authorities_false':a.get('novelty_authority') is False and a.get('r6_authority') is False and a.get('physical_quantum_advantage_claim') is False and a.get('publication_acceptance_authority') is False,
  'all_analyzer_gates':a.get('all_gates') is True and all(a.get('gates',{}).values()),
 }
 decision='ACCEPT_PROGRAMME_SCIENTIFIC_CLOSURE' if all(checks.values()) and a.get('terminal')=='ORION_QG_PROGRAMME_SCIENTIFICALLY_CLOSED__THEOREMS_REFUTATIONS_AND_BOUNDED_CANNOT_CHECKS_RECEIPTED__NOT_NOVELTY_AUTHORITY' else 'REJECT'; out={'schema':'ORION.QG.ProgrammeClosureGeneric.v1','issue':'SzeChunYiu/ORION#839','decision':decision,'checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'bounded_cannot_checks':a.get('bounded_cannot_checks'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
