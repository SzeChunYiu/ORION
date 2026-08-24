from __future__ import annotations
from dataclasses import dataclass
import math, random
import numpy as np
import sympy as sp
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import roc_auc_score

X = sp.Symbol('x')
SEED=20260818
random.seed(SEED); np.random.seed(SEED)

@dataclass
class Task:
    coeffs: tuple[int,...]
    interval: tuple[float,float]

    @property
    def degree(self): return len(self.coeffs)-1
    def poly(self): return sp.Poly(sum(c*X**(self.degree-i) for i,c in enumerate(self.coeffs)), X)


def gen_task(shift=False):
    degree=random.choice([1,2,2,3,3,4])
    # Mix constructed integer-root polynomials with unconstrained polynomials.
    if random.random() < (0.55 if not shift else 0.35):
        roots=[random.randint(-8,8) for _ in range(degree)]
        p=sp.Poly(1,X)
        for r in roots: p*=sp.Poly(X-r,X)
        scale=random.choice([1,1,2,3,5] if not shift else [1,2,5,10,20])
        coeffs=tuple(int(scale*c) for c in p.all_coeffs())
    else:
        scale=10 if not shift else 30
        while True:
            coeffs=tuple([random.choice([-3,-2,-1,1,2,3])] + [random.randint(-scale,scale) for _ in range(degree)])
            if coeffs[-1] != 0: break
    radius=random.choice([2,4,8,12] if not shift else [3,6,12,20])
    center=random.choice([0,0,0,random.randint(-4,4)])
    return Task(coeffs,(center-radius,center+radius))


def eval_poly(coeffs,x): return float(np.polyval(np.array(coeffs,dtype=float),x))

def rational_root(task):
    # Integer-root specializer; intentionally bounded enumeration.
    c=abs(task.coeffs[-1]); cap=min(80,max(1,c))
    candidates=[0]
    for d in range(1,cap+1):
        if c==0 or c%d==0: candidates += [d,-d]
    effort=len(candidates)
    for r in candidates:
        if abs(eval_poly(task.coeffs,r)) < 1e-9: return True, effort
    return False, effort

def bisection(task):
    a,b=task.interval; fa,fb=eval_poly(task.coeffs,a),eval_poly(task.coeffs,b)
    if fa==0 or fb==0: return True,1
    if fa*fb>0: return False,2
    for i in range(1,45):
        m=(a+b)/2; fm=eval_poly(task.coeffs,m)
        if abs(fm)<1e-7: return True,i+2
        if fa*fm<=0: b,fb=m,fm
        else: a,fa=m,fm
    return abs(eval_poly(task.coeffs,(a+b)/2))<1e-5,47

def newton(task):
    # Several deterministic starts, but derivative pathologies can still defeat it.
    coeff=np.array(task.coeffs,dtype=float); deriv=np.polyder(coeff)
    effort=0
    starts=[0.0, task.interval[0], task.interval[1], sum(task.interval)/2]
    for start in starts:
        z=start
        for _ in range(18):
            effort+=1; f=np.polyval(coeff,z); d=np.polyval(deriv,z)
            if abs(f)<1e-7: return True,effort
            if not np.isfinite(f) or not np.isfinite(d) or abs(d)<1e-10: break
            z-=f/d
            if not np.isfinite(z) or abs(z)>1e6: break
    return False,effort

def companion(task):
    effort=8*task.degree**2
    coeff=np.array(task.coeffs,dtype=float)
    dyn=max(abs(coeff))/max(1e-12,min(abs(coeff[np.nonzero(coeff)])))
    # Numeric solver degrades on deliberately ill-scaled instances.
    if dyn>25_000: return False,effort
    roots=np.roots(coeff)
    ok=any(abs(eval_poly(task.coeffs,float(r.real)))<1e-5 for r in roots if abs(r.imag)<1e-7)
    return bool(ok),effort

def symbolic(task):
    # High-cost verifier/fallback. Success means at least one real algebraic root exists.
    roots=sp.polys.polytools.ground_roots(task.poly())
    if roots:
        ok=any(bool(sp.im(r).equals(0)) for r in roots)
    else:
        rr=sp.nroots(task.poly(), maxsteps=100)
        ok=any(abs(float(sp.im(r)))<1e-8 for r in rr)
    return bool(ok), 70+18*task.degree+sum(math.log2(abs(c)+2) for c in task.coeffs)

SOLVERS={'rational':rational_root,'bisection':bisection,'newton':newton,'companion':companion,'symbolic':symbolic}

def features(task):
    coeff=np.array(task.coeffs,dtype=float)
    nz=np.abs(coeff[np.nonzero(coeff)])
    a,b=task.interval
    disc=0.0
    if task.degree==2:
        A,B,C=task.coeffs; disc=float(B*B-4*A*C)
    # V2: cheap mechanic-specific landmarkers. The V1 shift failure showed that
    # global/coarse features are not enough to estimate a specialist's boundary.
    probe_vals=[abs(eval_poly(task.coeffs,z)) for z in range(-4,5)]
    probe_zero=float(any(v < 1e-9 for v in probe_vals))
    probe_min=math.log2(min(probe_vals)+1.0)
    return [task.degree, math.log2(max(abs(coeff))+2), float(len(nz))/len(coeff),
            math.log2((max(nz)/min(nz))+1) if len(nz) else 0,
            float(np.sign(eval_poly(task.coeffs,a))*np.sign(eval_poly(task.coeffs,b))),
            b-a, (a+b)/2, np.sign(disc), math.log2(abs(disc)+2),
            probe_zero, probe_min]

def collect(n,shift=False):
    tasks=[gen_task(shift) for _ in range(n)]
    F=np.array([features(t) for t in tasks])
    outcomes={s:[] for s in SOLVERS}; costs={s:[] for s in SOLVERS}
    for t in tasks:
        for name,fn in SOLVERS.items():
            try: ok,cost=fn(t)
            except Exception: ok,cost=False,500.0
            outcomes[name].append(int(ok)); costs[name].append(float(cost))
    return tasks,F,{k:np.array(v) for k,v in outcomes.items()},{k:np.array(v) for k,v in costs.items()}

train=collect(1800,False); test=collect(700,False); shift=collect(700,True)
models={}; cost_models={}
for s in SOLVERS:
    clf=RandomForestClassifier(n_estimators=250,min_samples_leaf=4,random_state=SEED,n_jobs=-1).fit(train[1],train[2][s])
    reg=RandomForestRegressor(n_estimators=180,min_samples_leaf=4,random_state=SEED,n_jobs=-1).fit(train[1],np.log1p(train[3][s]))
    models[s]=clf; cost_models[s]=reg

def predict_prob(model,F):
    if len(model.classes_)==1:
        return np.ones(len(F)) if model.classes_[0]==1 else np.zeros(len(F))
    idx=list(model.classes_).index(1); return model.predict_proba(F)[:,idx]

def evaluate(data,label):
    tasks,F,Y,C=data
    solver_names=list(SOLVERS)
    # Fixed solver summary.
    fixed={s:(Y[s].mean(), C[s].mean()) for s in solver_names}
    best_fixed=max(solver_names,key=lambda s:(fixed[s][0],-fixed[s][1]))

    probs=np.column_stack([predict_prob(models[s],F) for s in solver_names])
    pred_cost=np.column_stack([np.expm1(cost_models[s].predict(F)) for s in solver_names])
    # Learned schedule: descending expected success per unit predicted effort, but keep symbolic as final verifier/fallback.
    total_success=0; total_cost=0.; first_choice_success=0
    oracle_cost=0.; oracle_success=0
    for i in range(len(F)):
        score=probs[i]/np.maximum(pred_cost[i],1.0)
        order=list(np.argsort(-score))
        sym=solver_names.index('symbolic')
        order=[j for j in order if j!=sym]+[sym]
        first=order[0]
        if Y[solver_names[first]][i]: first_choice_success+=1
        solved=False
        for j in order:
            s=solver_names[j]; total_cost+=C[s][i]
            if Y[s][i]: solved=True; break
        total_success+=int(solved)
        successes=[j for j,s in enumerate(solver_names) if Y[s][i]]
        if successes:
            oracle_success+=1; oracle_cost+=min(C[solver_names[j]][i] for j in successes)
    auc={}
    for j,s in enumerate(solver_names):
        if len(np.unique(Y[s]))>1:
            auc[s]=roc_auc_score(Y[s],probs[:,j])
    return {
        'label':label,'n':len(F),'fixed':fixed,'best_fixed':best_fixed,
        'schedule_success':total_success/len(F),'schedule_cost':total_cost/len(F),
        'first_choice_success':first_choice_success/len(F),
        'oracle_success':oracle_success/len(F),'oracle_cost':oracle_cost/max(1,oracle_success),'auc':auc
    }

for data,label in [(test,'IID holdout'),(shift,'distribution shift')]:
    r=evaluate(data,label)
    print('\n==',label,'==')
    for s,(sr,c) in r['fixed'].items(): print(f'{s:10s} success={sr:.3f} effort={c:.1f}')
    print('best_fixed:',r['best_fixed'])
    print(f"learned schedule: success={r['schedule_success']:.3f} effort={r['schedule_cost']:.1f}; first-choice success={r['first_choice_success']:.3f}")
    print(f"oracle: success={r['oracle_success']:.3f} effort={r['oracle_cost']:.1f}")
    print('competence AUC:',', '.join(f'{k}={v:.3f}' for k,v in r['auc'].items()))
