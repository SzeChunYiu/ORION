#!/usr/bin/env python3
"""Native ORION-Q admission for QG-13 recovery evidence."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ORION_Q=ROOT/'research/extensions/orion-q'
sys.path.insert(0,str(ORION_Q))
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

A=ROOT/'artifacts/orion-qg-qg13-theorem-miner.json'
G=ROOT/'artifacts/orion-qg-qg13-generic-verification.json'
R6S=ORION_Q/'MAX_R6S_ALL_N_COMPOSITION_RESULTS.json'
QG1=ROOT/'research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json'
OUT=ROOT/'artifacts/orion-qg-qg13-native-verification.json'
TOKEN='ORIONQG_QG13_NATIVE_VERIFY='

def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)

def main():
    a=json.loads(A.read_text()); g=json.loads(G.read_text()); r6s=json.loads(R6S.read_text()); qg1=json.loads(QG1.read_text())
    checks={
        'positive_recovery_terminal':a.get('terminal')=='QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS',
        'generic_accept':g.get('decision')=='ACCEPT' and all(g.get('checks',{}).values()),
        'r6m_production_width':getattr(r6m,'PARITY_STATES',None)==512,
        'r6i_production_width':len(getattr(r6i,'ACCEPTING',()))==6,
        'r6m_support_bound_2':a['r6m_theorem_candidate']['support_bound']==2,
        'r6i_support_bound_5':a['r6i_theorem_candidate']['support_bound']==5,
        'r6m_cone_exact':a['r6m_theorem_candidate']['resource_cone']['objective_cone']==['t_c >= 2*t_r','t_nc >= 2*t_r'],
        'r6i_unit_edit_nonincreasing':a['r6i_theorem_candidate']['unit_objective_resource']['max_delta_c']<=0,
        'r6s_parent_machine_checked':'ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED' in str(r6s.get('authority','')),
        'qg1_parent_support5':'SUPPORT5_SUFFICES_ALL_N' in str(qg1.get('authority','')),
        'authority_ceiling':a.get('new_theorem_authority') is False and a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False,
    }
    decision='ACCEPT_RECOVERY' if all(checks.values()) else 'REJECT'
    out={'schema':'ORION.QG.QG13.NativeVerification.v1','decision':decision,'checks':checks,'scope':'R6M_R6I_RECOVERY_ONLY','new_edit_requires_new_freeze':True,'new_theorem_authority':False,'novelty_authority':False}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
