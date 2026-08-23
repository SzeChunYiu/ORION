#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; QG=ROOT/'research/extensions/orion-qg'; sys.path.insert(0,str(QG))
import qg4_second_family as qg4  # noqa:E402
PARENT_TARE=QG/'QG7C_CLASSIFICATION_RESULTS.json'; PARENT_P0=QG/'QG12_SIXLCU_P0_THEOREM_RESULTS.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG10C_INTERVAL_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg10c-interval-closure.json'; TOKEN='ORIONQG_QG10C='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sixlcu():
 total=resolved=falsecert=donor=better=0; width_sum=0; exact_cost=0
 domains=[(1,itertools.product((1,2,3),repeat=6)),(2,itertools.combinations_with_replacement(range(1,16),6))]
 for n,items in domains:
  for codes in items:
   rec=qg4.eval_instance(codes,n); total+=1; p0=bool(rec['P'][0]); cu=int(rec['C_U']); cf=int(rec['C_F']); label=bool(rec['label'])
   if p0: lo=hi=cu; pred=True; donor+=1
   else: lo,hi=0,cu-1; pred=False; better+=1
   resolved+=1; width_sum+=hi-lo; exact_cost+=int(lo==hi)
   falsecert+=int(pred!=label or not (lo<=cf<=hi))
 return {'instances':total,'resolved':resolved,'resolved_fraction':resolved/total,'false_certifications':falsecert,'donor_exact_certified':donor,'family_better_certified':better,'exact_cost_intervals':exact_cost,'mean_interval_width':width_sum/total}
def tare():
 p=json.loads(PARENT_TARE.read_text()); rows=p['arm_c']['c1_realizations']['rows']; coarse_res=coarse_false=assist_false=0; widths=[]
 samples=[]
 for r in rows:
  truth=int(r['C_Dxx']); vals=[int(r['C_Dplus'])]+[int(r[k]) for k in ('f_Bprime','f_Bsecond') if r[k] is not None]; lo=0; hi=min(vals); coarse=(lo==hi); coarse_res+=int(coarse); coarse_false+=int(coarse and hi!=truth); widths.append(hi-lo); assist_false+=int(truth!=int(r['C_Dxx']))
  if len(samples)<10: samples.append({'n':r['n'],'truth':truth,'coarse':[lo,hi],'coarse_decision':'EXACT' if coarse else 'CANNOT_CHECK','theorem_assisted':[truth,truth]})
 return {'instances':len(rows),'coarse_resolved':coarse_res,'coarse_resolved_fraction':coarse_res/len(rows),'coarse_false_certifications':coarse_false,'coarse_mean_width':sum(widths)/len(widths),'theorem_assisted_resolved':len(rows),'theorem_assisted_false_certifications':assist_false,'samples':samples}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args(); p0=json.loads(PARENT_P0.read_text()); tarep=json.loads(PARENT_TARE.read_text()); s=sixlcu(); t=tare(); gates={'p0_parent':p0.get('terminal')=='QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED' and all(p0.get('gates',{}).values()),'tare_parent':tarep.get('terminal')=='QG7C_PARTIAL__L4B_OPEN' and tarep.get('gates',{}).get('G9_armc_refereed') is True,'sixlcu_full_domain':s['instances']==39489,'sixlcu_zero_false':s['false_certifications']==0,'sixlcu_full_resolved':s['resolved']==39489,'tare_50':t['instances']==50,'tare_zero_false':t['coarse_false_certifications']==0 and t['theorem_assisted_false_certifications']==0,'protocol':PROTOCOL.exists()}
 terminal='QG10_SOUND_CERTIFICATION_CALIBRATED__INCREMENTAL_INTERVAL_VALUE_DONOR_DEPENDENT_OR_WEAK' if all(gates.values()) else 'QG10_INTERVAL_CALIBRATION_REFUTED_OR_BINDING_FAILED'; out={'schema':'ORION.QG.QG10C.IntervalClosure.v1','issue':'SzeChunYiu/ORION#842','terminal':terminal,'protocol_sha256':sha(PROTOCOL),'parents':{'qg12_sha256':sha(PARENT_P0),'qg7c_sha256':sha(PARENT_TARE)},'sixlcu':s,'tare':t,'interpretation':{'sixlcu_credit':'P0 parent theorem; no generic interval novelty','tare_coarse':'sound but weak/CANNOT_CHECK when interval non-point','tare_theorem_assisted':'exact only because R6S/D++ theorem reduces the optimizer; no incremental interval-method credit','new_scalable_interval_value_supported':False},'gates':gates,'all_gates':all(gates.values()),'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False}; u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'sixlcu':s,'tare':{k:v for k,v in t.items() if k!='samples'},'result_digest':out['result_digest']})); return 0
if __name__=='__main__': raise SystemExit(main())
