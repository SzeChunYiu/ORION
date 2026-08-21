#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/'artifacts/orion-qg-portfolio-closure.json'; GENERIC=ROOT/'artifacts/orion-qg-portfolio-generic.json'; OUT=ROOT/'artifacts/orion-qg-portfolio-native.json'; TOKEN='ORIONQG_PORTFOLIO_NATIVE='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); g=json.loads(GENERIC.read_text()); checks={'portfolio_positive':a.get('all_closed') is True,'generic_accept':g.get('decision')=='ACCEPT_PORTFOLIO_CLOSURE' and g.get('all_checks') is True,'terminal':a.get('terminal')=='ORION_QG_EARNED_PORTFOLIO_LANES_ADJUDICATED_CLOSED__MIXED_THEOREM_REFUTATION_BOUNDARIES_PRESERVED','no_overclaim':a.get('novelty_authority') is False and a.get('r6_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 decision='ACCEPT_PORTFOLIO_CLOSURE' if all(checks.values()) else 'REJECT'; out={'schema':'ORION.QG.PortfolioNative.v1','decision':decision,'responsibility':'EARNED_LANE_CLOSURE_ADJUDICATION' if decision.startswith('ACCEPT') else 'CANNOT_CHECK','checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
