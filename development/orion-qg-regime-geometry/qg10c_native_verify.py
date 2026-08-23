#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/'artifacts/orion-qg-qg10c-interval-closure.json'; GENERIC=ROOT/'artifacts/orion-qg-qg10c-generic.json'; OUT=ROOT/'artifacts/orion-qg-qg10c-native.json'; TOKEN='ORIONQG_QG10C_NATIVE='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); g=json.loads(GENERIC.read_text()); checks={'analyzer':a.get('all_gates') is True,'generic':g.get('decision')=='ACCEPT_BOUNDED_CLOSURE' and g.get('all_checks') is True,'terminal':a.get('terminal')=='QG10_SOUND_CERTIFICATION_CALIBRATED__INCREMENTAL_INTERVAL_VALUE_DONOR_DEPENDENT_OR_WEAK','sixlcu_sound':a['sixlcu']['false_certifications']==0 and a['sixlcu']['resolved']==39489,'tare_bounded':a['tare']['coarse_false_certifications']==0 and a['interpretation']['new_scalable_interval_value_supported'] is False,'no_overclaim':a.get('novelty_authority') is False and a.get('r6_authority') is False and a.get('physical_quantum_advantage_claim') is False}; decision='ACCEPT_BOUNDED_CLOSURE' if all(checks.values()) else 'REJECT'; out={'schema':'ORION.QG.QG10C.Native.v1','issue':'SzeChunYiu/ORION#842','decision':decision,'responsibility':'SOUND_CALIBRATION__NO_INCREMENTAL_SCALABLE_VALUE' if decision.startswith('ACCEPT') else 'CANNOT_CHECK','checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'scientifically_closed':decision.startswith('ACCEPT'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
