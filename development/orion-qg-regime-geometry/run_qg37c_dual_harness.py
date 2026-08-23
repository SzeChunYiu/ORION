#!/usr/bin/env python3
"""Run frozen QG-37c composition, third generic verification, native gate, and tamper test."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';PROD=ART/'orion-qg-qg37-robust.json';REPL=ART/'orion-qg-qg37b-pbsat.json';SRC=ART/'orion-qg-qg37c-closure.json';GEN=ART/'orion-qg-qg37c-generic-verification.json';NAT=ART/'orion-qg-qg37c-native-verification.json';DUAL=ART/'orion-qg-qg37c-dual-harness.json';SUCCESS='QG37C_EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_CLOSED_BY_INDEPENDENT_REPLICATION'
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def run(path,*args,expect=0):
 p=subprocess.run([sys.executable,str(ROOT/path),*map(str,args)],cwd=ROOT,text=True,capture_output=True);print(p.stdout,end='');
 if p.returncode!=expect:print(p.stderr,end='',file=sys.stderr);raise SystemExit(p.returncode or 1)
 return p
def main():
 ART.mkdir(exist_ok=True);run('research/extensions/orion-qg/qg37c_replication_closure.py');run('development/orion-qg-regime-geometry/qg37c_generic_verify.py');run('development/orion-qg-regime-geometry/qg37c_native_verify.py');s=json.loads(SRC.read_text());g=json.loads(GEN.read_text());n=json.loads(NAT.read_text());ok=s.get('terminal')==g.get('terminal')==n.get('terminal')==SUCCESS and g.get('all_checks') is True and n.get('all_checks') is True and s.get('R1_star')==g.get('R1_star')==n.get('R1_star')
 tamper_rejected=False
 if ok:
  t=json.loads(REPL.read_text());i=next(i for i,r in enumerate(t['classes']) if r['class_size']>1);t['classes'][i]['D3_minimum']=int(t['classes'][i]['D3_minimum'])+1;t['result_digest']=hashlib.sha256(canon({k:v for k,v in t.items() if k!='result_digest'}).encode()).hexdigest();tp=ART/'qg37c-tampered-replica.json';to=ART/'qg37c-tampered-closure.json';tg=ART/'qg37c-tampered-generic.json';tp.write_text(json.dumps(t,indent=2,sort_keys=True)+'\n');run('research/extensions/orion-qg/qg37c_replication_closure.py','--replica',tp,'--output',to);run('development/orion-qg-regime-geometry/qg37c_generic_verify.py','--input',to,'--replica',tp,'--output',tg);gd=json.loads(tg.read_text());tamper_rejected=gd.get('all_checks') is False and gd.get('decision')=='REJECT'
 ok=ok and tamper_rejected
 o={'schema':'ORIONQG.QG37C.DualHarness.v1','terminal':SUCCESS if ok else 'QG37C_FRONTIER_HARNESS_REJECT','both_accept':bool(ok),'R1_star':s.get('R1_star') if ok else None,'maximum_robustness_overhead':s.get('maximum_robustness_overhead') if ok else None,'robustness_overhead_histogram':s.get('robustness_overhead_histogram') if ok else None,'strict_puncturing_exception_class_indices':s.get('strict_puncturing_exception_class_indices') if ok else None,'semantic_tamper_rejected':bool(tamper_rejected),'EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_AUTHORITY':bool(ok),'EXACT_ROBUSTNESS_OVERHEAD_AUTHORITY':bool(ok),'UNIVERSAL_ROBUST_MINIMUM_AUTHORITY':False,'HARDWARE_MEASUREMENT_NOISE_MODEL':False,'FAULT_TOLERANCE_THRESHOLD':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'physical_quantum_advantage_claim':False,'novelty_authority':False};DUAL.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps(o,sort_keys=True));return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
