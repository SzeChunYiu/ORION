#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ORION_Q=ROOT/'research/extensions/orion-q';sys.path.insert(0,str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
S1=ROOT/'artifacts/orion-qg-qg9-t2-stage1.json';R=ROOT/'artifacts/orion-qg-qg9-t2-result.json';G=ROOT/'artifacts/orion-qg-qg9-t2-generic-verification.json';P=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json';OUT=ROOT/'artifacts/orion-qg-qg9-t2-native-verification.json';TOKEN='ORIONQG_QG9_T2_NATIVE='
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 s=json.loads(S1.read_text());r=json.loads(R.read_text());g=json.loads(G.read_text());p=json.loads(P.read_text())
 alg=all(int(r6i._MUL[x,y])==p10.h.local_mul(x,y) and int(r6i._SYMP[x,y])==p10.h.local_symp(x,y) for x in range(4) for y in range(4)) and all(int(r6i._LW[x])==p10.h.local_wt(x) for x in range(4))
 pos=r.get('positive_witness') is not None
 checks={'parent_support2':p.get('terminal')=='QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED' and p.get('both_accept') is True,'generic_accept':g.get('decision')=='ACCEPT' and all(g.get('checks',{}).values()),'production_algebra_exact':alg,'stage1_ground_truth_closed':s.get('cap1_opened') is False and s.get('unrestricted_dp_opened') is False,'candidate_count_nonzero':s.get('canonical_candidate_count',0)>0,'terminal_consistent':(pos and r.get('terminal')=='QG9_SUPPORT2_TIGHT_WITNESS_FOUND__CAP1_STRICT_GAP') or ((not pos) and r.get('terminal')=='QG9_T2_NO_TIGHT_WITNESS_IN_FROZEN_INVERSE_DESIGN_DOMAIN'),'support1_authority_false':r.get('support1_authority') is False and g.get('support1_authority') is False,'novelty_false':r.get('novelty_authority') is False and g.get('novelty_authority') is False}
 if pos:
  q=r['positive_witness'];checks['strict_gap']=int(q['C_DP'])<=int(q['candidate']['U2'])<int(q['cap1']['C_cap1']);checks['production_witness_checks']=all(q['production_witness'].get('checks',{}).values())
  dec='ACCEPT_TIGHT_WITNESS' if all(checks.values()) else 'REJECT'
 else:
  checks['bounded_negative_only']=r.get('support2_tightness_claim') is False and r.get('unrestricted_dp_opened') is False
  dec='ACCEPT_BOUNDED_NEGATIVE' if all(checks.values()) else 'REJECT'
 out={'schema':'ORION.QG.QG9.T2.NativeVerification.v1','issue':'SzeChunYiu/ORION#803','decision':dec,'responsibility':'TIGHT_WITNESS' if pos else 'BOUNDED_NEGATIVE_ONLY','checks':checks,'terminal':r.get('terminal'),'support1_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
 OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
