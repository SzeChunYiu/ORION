#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/'artifacts/orion-qg-qg7d-n2-direct.json';G=ROOT/'artifacts/orion-qg-qg7d-n2-generic-verification.json';OUT=ROOT/'artifacts/orion-qg-qg7d-n2-native-verification.json';TOKEN='ORIONQG_QG7D_N2_NATIVE='

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
    a=json.loads(A.read_text());g=json.loads(G.read_text());pos=a.get('terminal')=='QG7D_BTRIPLEPRIME_REGIME_FOUND__PINNED_COMM_S2_EXACT_WITNESS'
    expected='ACCEPT_BTRIPLEPRIME_WITNESS' if pos else 'ACCEPT_BOUNDED_NEGATIVE'
    checks={
        'generic_accepts':g.get('decision')==expected and g.get('all_checks') is True,
        'all_analyzer_gates':all(a.get('gates',{}).values()),
        'identity_control':a.get('identity_target_control',{}).get('pass') is True,
        'rows_40':a.get('rows_evaluated')==40,
        'positive_replay':(not pos) or (a.get('selected') is not None and a['selected']['evaluation']['dp_replay']['pass'] is True),
        'positive_authority_exact':a.get('btripleprime_authority') is pos,
        'alln_blocked':a.get('global_all_n_closure_authority') is False,
        'authority_ceiling':a.get('novelty_authority') is False and a.get('r6_authority') is False and a.get('physical_quantum_advantage_claim') is False,
        'no_subject_data':a.get('chemistry_data_read') is False and a.get('reserved_stretched_n2_accessed') is False,
    }
    decision=expected if all(checks.values()) else 'REJECT'
    out={'schema':'ORIONQG.QG7D.N2NativeVerification.v1','issue':'SzeChunYiu/ORION#836','decision':decision,'checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'global_all_n_closure_authority':False,'novelty_authority':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(out));return 0
if __name__=='__main__':raise SystemExit(main())
