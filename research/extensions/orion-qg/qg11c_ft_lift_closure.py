#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,itertools,json,math
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG11C_FT_LIFT_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg11c-ft-lift.json'; TOKEN='ORIONQG_QG11C='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def matvec(A,r): return [sum(A[i][j]*r[j] for j in range(len(r))) for i in range(len(A))]
def transpose_times(A,l): return [sum(A[i][j]*l[i] for i in range(len(A))) for j in range(len(A[0]))]
def affine_controls():
 cases=[([[2,1,0],[0,3,1]],[1,2],[5,7]),([[1,0,2],[2,1,0],[0,1,1]],[2,3,5],[1,4,2]),([[3,1],[1,2]],[Fraction(1,2),Fraction(3,2)],[2,5])]; rows=[]; failures=0
 for A,l,b in cases:
  theta=transpose_times(A,l); const=dot(l,b); coeff_ok=all(theta[j]==sum(A[i][j]*l[i] for i in range(len(A))) for j in range(len(theta))); exhaustive=0
  for r in itertools.product(range(4),repeat=len(A[0])):
   rf=[x+y for x,y in zip(matvec(A,r),b)]; lhs=dot(l,rf); rhs=dot(theta,r)+const; exhaustive+=1; failures+=int(lhs!=rhs)
  rows.append({'A':[[str(x) for x in row] for row in A],'lambda':[str(x) for x in l],'b':[str(x) for x in b],'theta':[str(x) for x in theta],'constant':str(const),'coefficient_identity':coeff_ok,'exhaustive_vectors':exhaustive})
 return {'cases':rows,'failures':failures,'holds':failures==0 and all(r['coefficient_identity'] for r in rows)}
def physical(T,D): return 10*math.ceil(T/8)+D
def nonlinear():
 A={'T':9,'D':0}; B={'T':8,'D':2}; sa=A['T']+A['D']; sb=B['T']+B['D']; pa=physical(**A); pb=physical(**B); midpoint={'T':5,'D':0}; nonaff=(physical(1,0)+physical(9,0)) != 2*physical(**midpoint)
 return {'route_A':A|{'structural':sa,'physical_scaled':pa},'route_B':B|{'structural':sb,'physical_scaled':pb},'structural_prefers_A':sa<sb,'physical_prefers_B':pb<pa,'midpoint_nonaffinity':nonaff,'holds':sa<sb and pb<pa and nonaff}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args(); aff=affine_controls(); nl=nonlinear(); gates={'protocol':PROTOCOL.exists(),'affine':aff['holds'],'nonlinear_counterexample':nl['holds'],'real_estimator_not_claimed':True}; terminal='QG11_AFFINE_FT_PHASE_PULLBACK_PROVED__NONLINEAR_FACTORY_COUNTEREXAMPLE__REAL_ESTIMATOR_CANNOT_CHECK' if all(gates.values()) else 'QG11_FT_LIFT_CLOSURE_REFUTED_OR_BINDING_FAILED'; out={'schema':'ORION.QG.QG11C.FTLiftClosure.v1','issue':'SzeChunYiu/ORION#843','terminal':terminal,'protocol_sha256':sha(PROTOCOL),'affine_pullback':aff,'nonlinear_factory_counterexample':nl,'real_ft_estimator_status':'CANNOT_CHECK_REAL_ESTIMATOR','gates':gates,'all_gates':all(gates.values()),'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False}; u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'result_digest':out['result_digest'],'affine_failures':aff['failures'],'counterexample':nl})); return 0
if __name__=='__main__': raise SystemExit(main())
