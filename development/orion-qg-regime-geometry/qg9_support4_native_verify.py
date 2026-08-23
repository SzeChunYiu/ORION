#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ORION_Q=ROOT/'research/extensions/orion-q';sys.path.insert(0,str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
A=ROOT/'artifacts/orion-qg-qg9-support4-combined-exchange.json';G=ROOT/'artifacts/orion-qg-qg9-support4-generic-verification.json';Q=ROOT/'research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json';OUT=ROOT/'artifacts/orion-qg-qg9-support4-native-verification.json';TOKEN='ORIONQG_QG9_SUPPORT4_NATIVE='
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(A.read_text());g=json.loads(G.read_text());q=json.loads(Q.read_text())
 algebra=all(int(r6i._MUL[x,y])==p10.h.local_mul(x,y) and int(r6i._SYMP[x,y])==p10.h.local_symp(x,y) for x in range(4) for y in range(4)) and all(int(r6i._LW[x])==p10.h.local_wt(x) for x in range(4))
 checks={'positive_terminal':a.get('terminal')=='QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED','generic_accept':g.get('decision')=='ACCEPT' and all(g.get('checks',{}).values()),'production_algebra_exact':algebra and a['production_binding']['all_exact'],'qg1_parent_support5':'SUPPORT5_SUFFICES_ALL_N' in str(q.get('authority','')) and all(q.get('gates',{}).values()),'support5_boundary_closed':a['support5_boundary']['unsafe_count']==0 and a['support5_boundary']['retained_irreducible_patterns']>0,'support4_obstructions_remain':a['support4_control']['unsafe_count']>0,'proof_audit':all(a.get('proof_audit',{}).values()),'support_bound4':a.get('support_bound')==4,'no_support3_or_tightness_claim':a.get('support3_claim') is False and a.get('tightness_claim') is False,'authority_ceiling':a.get('new_theorem_authority') is False and a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 dec='ACCEPT_SUPPORT4' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9.NativeVerification.v1','decision':dec,'checks':checks,'scope':'R6I_UNIT_OBJECTIVE_ONLY','support3_authority':False,'tightness_authority':False,'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
