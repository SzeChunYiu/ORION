#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ORION_Q=ROOT/'research/extensions/orion-q';sys.path.insert(0,str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
A=ROOT/'artifacts/orion-qg-qg9-support3-relabel-exchange.json';G=ROOT/'artifacts/orion-qg-qg9-support3-generic-verification.json';V2R=ROOT/'research/extensions/orion-qg/QG9_SUPPORT4_COMBINED_EXCHANGE_RESULTS.json';V2P=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT4_PROTECTED_RUN_RECEIPT_2026-08-21.json';OUT=ROOT/'artifacts/orion-qg-qg9-support3-native-verification.json';TOKEN='ORIONQG_QG9_SUPPORT3_NATIVE='
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(A.read_text());g=json.loads(G.read_text());v=json.loads(V2R.read_text());p=json.loads(V2P.read_text())
 alg=all(int(r6i._MUL[x,y])==p10.h.local_mul(x,y) and int(r6i._SYMP[x,y])==p10.h.local_symp(x,y) for x in range(4) for y in range(4)) and all(int(r6i._LW[x])==p10.h.local_wt(x) for x in range(4))
 checks={'positive_terminal':a.get('terminal')=='QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED','generic_accept':g.get('decision')=='ACCEPT' and all(g.get('checks',{}).values()),'production_algebra_exact':alg,'parent_v2_positive':v.get('terminal')=='QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED' and p.get('terminal')==v.get('terminal') and p.get('both_accept') is True,'parent_support_bound4':v.get('support_bound')==4,'rich_grammar_contains_parent_deletions':a['parent_deletion_subset_check']['all_deletions_contained_or_dominated'] is True,'all_support4_survivors_closed':a['support4_parent_survivors']['unsafe_type_cases']==0 and a['support4_parent_survivors']['action_profile_type_cases']>0,'support3_method_obstruction_remains':a['support3_boundary_control']['unsafe_type_cases']>0,'proof_audit':all(a.get('proof_audit',{}).values()),'support_bound3':a.get('support_bound')==3,'no_support2_or_tightness_claim':a.get('support2_claim') is False and a.get('tightness_claim') is False,'authority_ceiling':a.get('new_theorem_authority') is False and a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 dec='ACCEPT_SUPPORT3' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9.Support3NativeVerification.v1','decision':dec,'checks':checks,'scope':'R6I_UNIT_OBJECTIVE_ONLY','support2_authority':False,'tightness_authority':False,'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
