#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; Q=ROOT/'research/extensions/orion-q'; QG=ROOT/'research/extensions/orion-qg'
sys.path.insert(0,str(Q)); sys.path.insert(0,str(QG))
import qg7c_classification as q7c  # noqa:E402
RESULT=ROOT/'artifacts/orion-qg-qg7d-padding-ablation.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG7D_PADDING_ABLATION_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg7d-padding-generic.json'; TOKEN='ORIONQG_QG7D_PAD_GENERIC='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None)
 checks={'schema':a.get('schema')=='ORION.QG.QG7D.PaddingAblation.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'parent_bound':a.get('gates',{}).get('parent_digest') is True and a.get('gates',{}).get('parent_t4b_census') is True,'160_rows':a.get('counters',{}).get('rows')==160,'no_parent_referee_failures':not a.get('counters',{}).get('sandwich_failures') and not a.get('counters',{}).get('dxx_witness_failures') and not a.get('counters',{}).get('replay_failures'),'no_overclaim':a.get('all_n_theorem_authority') is False and a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 positive=a.get('terminal')=='QG7D_BTRIPLEPRIME_REGIME_FOUND__PADDING_ABLATION_EXACT_WITNESS'
 selected=[]; replay_ok=True
 if positive:
  for pname,st in a['policies'].items():
   rec=st.get('first')
   if not rec: continue
   tp=tuple((tuple(x[0]),tuple(x[1])) for x in rec['target_pairs']); counters={'rows':0,'sandwich_failures':[],'dxx_witness_rows':0,'dxx_witness_failures':[],'replay_rows':0,'replay_failures':[]}; gaps=[]
   vals=q7c._eval_instance(tp,3,['generic',pname],gaps,counters)
   ok=vals[4]<0 and not counters['sandwich_failures'] and not counters['dxx_witness_failures'] and not counters['replay_failures'] and bool(gaps)
   selected.append({'policy':pname,'gap':int(vals[4]),'replay_ok':ok}); replay_ok &= ok
 checks['selected_positive_replay']=replay_ok
 allc=all(checks.values()); decision=('ACCEPT_BTRIPLEPRIME_WITNESS' if positive and allc else ('ACCEPT_BOUNDED_NEGATIVE' if (not positive) and allc else 'REJECT'))
 out={'schema':'ORION.QG.QG7D.PaddingGeneric.v1','issue':'SzeChunYiu/ORION#836','decision':decision,'checks':checks,'all_checks':allc,'selected_replay':selected,'terminal':a.get('terminal'),'all_n_theorem_authority':False,'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
