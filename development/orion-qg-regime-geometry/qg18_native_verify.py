#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/'artifacts/orion-qg-qg18-tare-kappa2.json'
GENERIC=ROOT/'artifacts/orion-qg-qg18-generic-verification.json'
OUT=ROOT/'artifacts/orion-qg-qg18-native-verification.json'
TOKEN='ORIONQG_QG18_NATIVE='

def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
    a=json.loads(RESULT.read_text()); g=json.loads(GENERIC.read_text())
    checks={
        'positive_terminal':a.get('terminal')=='QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_MACHINE_VERIFIED',
        'production_gates':all(a.get('gates',{}).values()),
        'generic_accept':g.get('decision')=='ACCEPT_KAPPA2' and g.get('all_checks') is True,
        'lower_bound_strict':a['selected_witness']['unrestricted_dp']==7 and a['selected_witness']['cap1']['C_Dxx']==8,
        'upper_bound_all_n':a.get('proof',{}).get('intrinsic_support_number')==2,
        'scope_clean':a.get('chemistry_sources_read') is False and a.get('protected_stretched_n2_read') is False,
        'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False and a.get('r6_authority') is False,
    }
    decision='ACCEPT_KAPPA2' if all(checks.values()) else 'REJECT'
    out={'schema':'ORION.QG.QG18.NativeVerification.v1','issue':'SzeChunYiu/ORION#838','responsibility':'EXACT_INTRINSIC_SUPPORT_NUMBER' if decision.startswith('ACCEPT') else 'CANNOT_CHECK','decision':decision,'checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'intrinsic_support_number':2 if decision.startswith('ACCEPT') else None,'novelty_authority':False,'physical_quantum_advantage_claim':False}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
