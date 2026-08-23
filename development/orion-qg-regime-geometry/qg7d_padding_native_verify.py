#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/'artifacts/orion-qg-qg7d-padding-ablation.json'; GENERIC=ROOT/'artifacts/orion-qg-qg7d-padding-generic.json'; OUT=ROOT/'artifacts/orion-qg-qg7d-padding-native.json'; TOKEN='ORIONQG_QG7D_PAD_NATIVE='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); g=json.loads(GENERIC.read_text()); positive=a.get('terminal')=='QG7D_BTRIPLEPRIME_REGIME_FOUND__PADDING_ABLATION_EXACT_WITNESS'
 expected='ACCEPT_BTRIPLEPRIME_WITNESS' if positive else 'ACCEPT_BOUNDED_NEGATIVE'
 checks={'all_analyzer_gates':a.get('all_gates') is True,'generic':g.get('decision')==expected and g.get('all_checks') is True,'terminal_allowed':a.get('terminal') in {'QG7D_BTRIPLEPRIME_REGIME_FOUND__PADDING_ABLATION_EXACT_WITNESS','QG7D_PADDING_ABLATION_NO_BTRIPLEPRIME_IN_FROZEN_ROWS__J5_REQUIRED'},'negative_not_theorem':positive or a.get('all_n_theorem_authority') is False,'scope':a.get('protected_subject_read') is False and a.get('chemistry_sources_read') is False,'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 decision=expected if all(checks.values()) else 'REJECT'; responsibility=('BTRIPLEPRIME_WITNESS' if positive else 'BOUNDED_NEGATIVE_J5_REQUIRED') if decision!='REJECT' else 'CANNOT_CHECK'
 out={'schema':'ORION.QG.QG7D.PaddingNative.v1','issue':'SzeChunYiu/ORION#836','decision':decision,'responsibility':responsibility,'checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'all_n_theorem_authority':False,'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
