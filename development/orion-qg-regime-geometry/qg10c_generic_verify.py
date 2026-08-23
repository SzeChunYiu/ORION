#!/usr/bin/env python3
from __future__ import annotations
import hashlib,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; QG=ROOT/'research/extensions/orion-qg'; sys.path.insert(0,str(QG))
import qg4_second_family as qg4  # noqa:E402
RESULT=ROOT/'artifacts/orion-qg-qg10c-interval-closure.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG10C_INTERVAL_CLOSURE_PROTOCOL_V1.md'; TARE=QG/'QG7C_CLASSIFICATION_RESULTS.json'; OUT=ROOT/'artifacts/orion-qg-qg10c-generic.json'; TOKEN='ORIONQG_QG10C_GENERIC='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None); total=bad=donor=better=0
 for n,items in ((1,itertools.product((1,2,3),repeat=6)),(2,itertools.combinations_with_replacement(range(1,16),6))):
  for codes in items:
   r=qg4.eval_instance(codes,n); p0=bool(r['P'][0]); cu=int(r['C_U']); cf=int(r['C_F']); lo,hi=(cu,cu) if p0 else (0,cu-1); total+=1; bad+=int((p0!=bool(r['label'])) or not(lo<=cf<=hi)); donor+=int(p0); better+=int(not p0)
 tr=json.loads(TARE.read_text()); rows=tr['arm_c']['c1_realizations']['rows']; coarse=sum(int(0==min([int(r['C_Dplus'])]+[int(r[k]) for k in ('f_Bprime','f_Bsecond') if r[k] is not None])) for r in rows)
 checks={'schema':a.get('schema')=='ORION.QG.QG10C.IntervalClosure.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'sixlcu_count':total==39489==a['sixlcu']['instances'],'sixlcu_zero_false':bad==0==a['sixlcu']['false_certifications'],'sixlcu_counts':donor==a['sixlcu']['donor_exact_certified'] and better==a['sixlcu']['family_better_certified'],'tare_count':len(rows)==50==a['tare']['instances'],'tare_coarse':coarse==a['tare']['coarse_resolved'],'interpretation_bounded':a['interpretation']['new_scalable_interval_value_supported'] is False,'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 decision='ACCEPT_BOUNDED_CLOSURE' if all(checks.values()) and a.get('terminal')=='QG10_SOUND_CERTIFICATION_CALIBRATED__INCREMENTAL_INTERVAL_VALUE_DONOR_DEPENDENT_OR_WEAK' else 'REJECT'; out={'schema':'ORION.QG.QG10C.Generic.v1','issue':'SzeChunYiu/ORION#842','decision':decision,'checks':checks,'all_checks':all(checks.values()),'sixlcu_rebuild':{'instances':total,'false':bad,'donor':donor,'better':better},'tare_coarse_resolved':coarse,'terminal':a.get('terminal'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
