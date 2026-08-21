#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ORION_Q=ROOT/'research/extensions/orion-q';sys.path.insert(0,str(ORION_Q))
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
A=ROOT/'artifacts/orion-qg-qg9-support2-tightness.json';G=ROOT/'artifacts/orion-qg-qg9-support2-tightness-generic-verification.json';PR=ROOT/'research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json';PP=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json';OUT=ROOT/'artifacts/orion-qg-qg9-support2-tightness-native-verification.json';TOKEN='ORIONQG_QG9_TIGHT_NATIVE='
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(A.read_text());g=json.loads(G.read_text());pr=json.loads(PR.read_text());pp=json.loads(PP.read_text());sel=a.get('selected');prod=a.get('production_referee')
 parent=pr.get('terminal')=='QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED' and pp.get('terminal')==pr.get('terminal') and pp.get('both_accept') is True and pr.get('support_bound')==2
 if sel is None:
  checks={'parent_support2_protected':parent,'negative_terminal':a.get('terminal')=='QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL','tightness_false':a.get('tightness_authority') is False,'generic_negative_bounded':g.get('decision')=='NEGATIVE_PANEL_NOT_INDEPENDENTLY_REPLAYED'}
  dec='RECORD_NEGATIVE_PANEL' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9.TightnessNativeVerification.v1','decision':dec,'checks':checks,'tightness_authority':False,'support1_authority':False,'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
 checks={'parent_support2_protected':parent,'positive_terminal':a.get('terminal')=='QG9_SUPPORT2_TIGHT_WITNESS_MACHINE_VERIFIED','generic_accept':g.get('decision')=='ACCEPT_TIGHTNESS' and all(g.get('checks',{}).values()),'strict_cap_gap':sel['C_cap2']<sel['C_cap1'],'production_present':prod is not None,'production_matches_cap2':prod is not None and prod['C_shared']==sel['C_cap2'],'production_witness_checks':prod is not None and all(prod.get('checks',{}).values()),'production_witness_uses_support2':prod is not None and max(prod.get('independent_generator_supports',[]),default=0)==2,'production_accepting_states_present':len(r6i.ACCEPTING)==6,'authority_ceiling':a.get('support1_authority') is False and a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 dec='ACCEPT_TIGHTNESS' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9.TightnessNativeVerification.v1','decision':dec,'checks':checks,'tightness_authority':dec=='ACCEPT_TIGHTNESS','support1_authority':False,'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
