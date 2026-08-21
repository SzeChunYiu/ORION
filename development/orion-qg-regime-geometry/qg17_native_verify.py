#!/usr/bin/env python3
"""Native ORION-Q admission for QG-17 phase-sharpness evidence."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/'artifacts/orion-qg-qg17-r6i-phase-sharpness.json';GENERIC=ROOT/'artifacts/orion-qg-qg17-generic-verification.json';PARENT=ROOT/'development/orion-qg-regime-geometry/QG16_PROTECTED_RUN_RECEIPT_2026-08-21.json';OUT=ROOT/'artifacts/orion-qg-qg17-native-verification.json';TOKEN='ORIONQG_QG17_NATIVE='
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text());g=json.loads(GENERIC.read_text());p=json.loads(PARENT.read_text());positive=a.get('terminal')=='QG17_SUPPORT2_PHASE_WITNESS_FOUND_AT_FROZEN_OUTSIDE_OBJECTIVE';outside=a.get('outside_objectives_with_strict_witness',[])
 checks={'parent_qg16_protected':p.get('terminal')=='QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED' and p.get('both_accept') is True,'generator_and_scan_gates':all(a.get('gates',{}).values()),'generic_accept':g.get('decision')==('ACCEPT_SUPPORT2_PHASE_WITNESS' if positive else 'ACCEPT_BOUNDED_NEGATIVE') and g.get('all_checks') is True,'O0_zero':a.get('objectives',{}).get('O0',{}).get('strict_count')==0,'positive_consistent':(positive and bool(outside)) or ((not positive) and not outside),'global_incomplete':a.get('global_phase_boundary_complete') is False,'no_novelty':a.get('novelty_authority') is False,'no_physical_advantage':a.get('physical_quantum_advantage_claim') is False}
 decision=('ACCEPT_SUPPORT2_PHASE_WITNESS' if positive else 'ACCEPT_BOUNDED_NEGATIVE') if all(checks.values()) else 'REJECT'
 out={'schema':'ORION.QG.QG17.NativeVerification.v1','issue':'SzeChunYiu/ORION#814','decision':decision,'responsibility':'SUPPORT2_PHASE_WITNESS' if positive else 'NO_WITNESS_ON_FROZEN_V5_DOMAIN','checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'outside_objectives':outside,'facet_affine_match_count':len(a.get('facet_affine_matches',[])),'global_phase_boundary_complete':False,'phase_witness_authority':positive and decision=='ACCEPT_SUPPORT2_PHASE_WITNESS','novelty_authority':False,'physical_quantum_advantage_claim':False}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(out));return 0
if __name__=='__main__':raise SystemExit(main())
