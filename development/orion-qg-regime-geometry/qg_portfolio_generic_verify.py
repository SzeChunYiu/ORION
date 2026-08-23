#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; QG=ROOT/'research/extensions/orion-qg'; RESULT=ROOT/'artifacts/orion-qg-portfolio-closure.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG_PORTFOLIO_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-portfolio-generic.json'; TOKEN='ORIONQG_PORTFOLIO_GENERIC='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None)
 checks={'schema':a.get('schema')=='ORION.QG.PortfolioClosure.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==sha(PROTOCOL),'all_closed':a.get('all_closed') is True,'seven_lane_groups':set(a.get('lanes',{}))=={'qg2','qg3','qg4_qg5','qg6','qg8','qg12','qg13'},'every_lane_closed':all(x.get('closed') is True for x in a.get('lanes',{}).values()),'mixed_wording_preserved':all(('MIXED' in x.get('terminal','')) or k=='qg3' for k,x in a.get('lanes',{}).items()),'no_overclaim':a.get('novelty_authority') is False and a.get('r6_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 decision='ACCEPT_PORTFOLIO_CLOSURE' if all(checks.values()) else 'REJECT'; out={'schema':'ORION.QG.PortfolioGeneric.v1','decision':decision,'checks':checks,'all_checks':all(checks.values()),'source_terminal':a.get('terminal'),'lanes':{k:v.get('terminal') for k,v in a.get('lanes',{}).items()},'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
