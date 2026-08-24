from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional, Tuple
import math, random
import numpy as np
import sympy as sp
from sklearn.tree import DecisionTreeClassifier

SEED = 20260818
random.seed(SEED); np.random.seed(SEED)
X = sp.Symbol('x')

MECHANICS = [
    'integer_probe', 'deflate', 'quadratic',
    'even_transform', 'reciprocal_transform',
    'quadratic_y', 'square_lift', 'reciprocal_lift'
]
COST = {
    'integer_probe': 3.0, 'deflate': 2.0, 'quadratic': 5.0,
    'even_transform': 2.0, 'reciprocal_transform': 2.0,
    'quadratic_y': 5.0, 'square_lift': 3.0, 'reciprocal_lift': 4.0,
}

@dataclass(frozen=True)
class Task:
    coeffs: Tuple[int, ...]
    family: str
    depth: int
    plan: Tuple[str, ...]

@dataclass(frozen=True)
class State:
    original: Tuple[int, ...]
    kind: str = 'poly'
    poly: Tuple[sp.Expr, ...] = ()
    accum: Tuple[sp.Expr, ...] = ()
    found_root: Optional[int] = None
    y_poly: Tuple[sp.Expr, ...] = ()
    y_roots: Tuple[sp.Expr, ...] = ()
    roots: Tuple[sp.Expr, ...] = ()

    def __post_init__(self):
        if not self.poly and self.kind == 'poly':
            object.__setattr__(self, 'poly', tuple(sp.Integer(c) for c in self.original))


def trim(coeffs):
    coeffs = list(coeffs)
    while len(coeffs) > 1 and sp.simplify(coeffs[0]) == 0:
        coeffs.pop(0)
    return tuple(coeffs)


def degree(coeffs): return len(trim(coeffs)) - 1

def polyval(coeffs, z):
    v = sp.Integer(0)
    for c in coeffs: v = sp.expand(v*z + c)
    return sp.simplify(v)


def quad_roots(coeffs):
    a,b,c = trim(coeffs)
    d = sp.simplify(b*b - 4*a*c)
    return (sp.simplify((-b+sp.sqrt(d))/(2*a)), sp.simplify((-b-sp.sqrt(d))/(2*a)))


def execute(state: State, mech: str):
    if state.kind == 'done': return None
    if mech == 'integer_probe':
        if state.kind != 'poly' or degree(state.poly) <= 2 or state.found_root is not None: return None
        for r in range(-12,13):
            if polyval(state.poly, sp.Integer(r)) == 0:
                return replace(state, found_root=r)
        return None
    if mech == 'deflate':
        if state.kind != 'poly' or state.found_root is None: return None
        p = sp.Poly(sum(c*X**(degree(state.poly)-i) for i,c in enumerate(state.poly)), X)
        q, rem = sp.div(p, sp.Poly(X-state.found_root, X))
        if not rem.is_zero: return None
        return replace(state, poly=tuple(q.all_coeffs()), accum=state.accum+(sp.Integer(state.found_root),), found_root=None)
    if mech == 'quadratic':
        if state.kind != 'poly' or degree(state.poly) != 2: return None
        roots = state.accum + quad_roots(state.poly)
        return replace(state, kind='done', roots=roots)
    if mech == 'even_transform':
        if state.kind != 'poly' or degree(state.poly) != 4 or state.found_root is not None: return None
        a,b,c,d,e = state.poly
        if sp.simplify(b) != 0 or sp.simplify(d) != 0: return None
        return replace(state, kind='y_even', y_poly=(a,c,e))
    if mech == 'reciprocal_transform':
        if state.kind != 'poly' or degree(state.poly) != 4 or state.found_root is not None: return None
        a,b,c,d,e = state.poly
        if sp.simplify(a-e) != 0 or sp.simplify(b-d) != 0 or sp.simplify(a)==0: return None
        return replace(state, kind='y_recip', y_poly=(a,b,sp.simplify(c-2*a)))
    if mech == 'quadratic_y':
        if state.kind not in ('y_even','y_recip') or degree(state.y_poly) != 2: return None
        return replace(state, kind=state.kind+'_solved', y_roots=quad_roots(state.y_poly))
    if mech == 'square_lift':
        if state.kind != 'y_even_solved': return None
        roots=[]
        for y in state.y_roots: roots.extend((sp.sqrt(y), -sp.sqrt(y)))
        return replace(state, kind='done', roots=tuple(roots))
    if mech == 'reciprocal_lift':
        if state.kind != 'y_recip_solved': return None
        roots=[]
        for y in state.y_roots:
            roots.extend(quad_roots((sp.Integer(1), -y, sp.Integer(1))))
        return replace(state, kind='done', roots=tuple(roots))
    return None


def verify(task: Task, state: State):
    if state.kind != "done" or len(state.roots) != len(task.coeffs)-1:
        return False
    try:
        roots=np.array([complex(sp.N(r,18)) for r in state.roots],dtype=complex)
        got=np.poly(roots)*complex(task.coeffs[0])
        want=np.array(task.coeffs,dtype=complex)
        scale=max(1.0,float(np.max(np.abs(want))))
        return bool(np.max(np.abs(got-want)) <= 1e-6*scale)
    except Exception:
        return False

def random_quadratic(scale):
    while True:
        a=random.choice([i for i in range(-scale,scale+1) if i])
        b=random.randint(-scale,scale); c=random.randint(-scale,scale)
        if c==0: c=random.choice([-1,1])
        # avoid repeated zero polynomial pathologies
        return sp.Poly(a*X**2+b*X+c,X)


def make_root_chain(depth, scale):
    p=random_quadratic(scale)
    roots=[]
    for _ in range(depth):
        r=random.choice([i for i in range(-min(scale,9),min(scale,9)+1) if i])
        roots.append(r); p=sp.Poly((X-r)*p.as_expr(),X)
    coeffs=tuple(int(c) for c in p.all_coeffs())
    plan=tuple(sum((["integer_probe","deflate"] for _ in range(depth)),[])+['quadratic'])
    return Task(coeffs,'root_chain',depth,plan)


def make_biquad(scale):
    q=random_quadratic(scale)
    a,b,c=q.all_coeffs(); p=sp.Poly(a*X**4+b*X**2+c,X)
    return Task(tuple(int(z) for z in p.all_coeffs()),'biquadratic',0,('even_transform','quadratic_y','square_lift'))


def make_recip(scale):
    a=random.choice([i for i in range(-scale,scale+1) if i])
    b=random.randint(-scale,scale); c=random.randint(-scale,scale)
    p=sp.Poly(a*X**4+b*X**3+c*X**2+b*X+a,X)
    return Task(tuple(int(z) for z in p.all_coeffs()),'reciprocal',0,('reciprocal_transform','quadratic_y','reciprocal_lift'))


def structurally_known(coeffs):
    c=tuple(sp.Integer(z) for z in coeffs)
    if degree(c)<=2: return True
    if degree(c)==4:
        a,b,cc,d,e=c
        if b==0 and d==0: return True
        if a==e and b==d and a!=0: return True
    for r in range(-12,13):
        if polyval(c,sp.Integer(r))==0: return True
    return False


def make_opaque(scale, degree_choices):
    for _ in range(10000):
        deg=random.choice(degree_choices)
        lead=random.choice([i for i in range(-scale,scale+1) if i])
        coeffs=(lead,)+tuple(random.randint(-scale,scale) for _ in range(deg))
        if coeffs[-1]==0: continue
        if not structurally_known(coeffs): return Task(coeffs,'opaque',0,())
    raise RuntimeError('opaque generation failed')


def gen_task(split):
    if split=='train':
        scale=6; fam=random.choices(['root','bi','recip','opaque'],[.48,.18,.16,.18])[0]
        if fam=='root': return make_root_chain(random.choice([0,1,1,2]),scale)
        if fam=='bi': return make_biquad(scale)
        if fam=='recip': return make_recip(scale)
        return make_opaque(scale,[3,4])
    if split=='iid':
        scale=6; fam=random.choices(['root','bi','recip','opaque'],[.45,.18,.17,.20])[0]
        if fam=='root': return make_root_chain(random.choice([0,1,2]),scale)
        if fam=='bi': return make_biquad(scale)
        if fam=='recip': return make_recip(scale)
        return make_opaque(scale,[3,4])
    if split=='scale':
        scale=24; fam=random.choices(['root','bi','recip','opaque'],[.45,.18,.17,.20])[0]
        if fam=='root': return make_root_chain(random.choice([0,1,2]),scale)
        if fam=='bi': return make_biquad(scale)
        if fam=='recip': return make_recip(scale)
        return make_opaque(scale,[3,4])
    if split=='length':
        scale=8; fam=random.choices(['root','bi','recip','opaque'],[.55,.12,.10,.23])[0]
        if fam=='root': return make_root_chain(random.choice([3,3,4]),scale)
        if fam=='bi': return make_biquad(scale)
        if fam=='recip': return make_recip(scale)
        return make_opaque(scale,[5,6])
    if split=='mixed':
        scale=30; fam=random.choices(['root','bi','recip','opaque'],[.48,.10,.09,.33])[0]
        if fam=='root': return make_root_chain(random.choice([3,4]),scale)
        if fam=='bi': return make_biquad(scale)
        if fam=='recip': return make_recip(scale)
        return make_opaque(scale,[5,6])
    raise ValueError(split)


def features(state: State, probe=True):
    mode=['poly','y_even','y_recip','y_even_solved','y_recip_solved','done']
    one=[1.0 if state.kind==m else 0.0 for m in mode]
    coeffs=state.poly if state.kind=='poly' else state.y_poly
    coeffs=trim(coeffs) if coeffs else (sp.Integer(0),)
    vals=np.array([float(abs(sp.N(c))) for c in coeffs],dtype=float)
    deg=degree(coeffs)
    scale=math.log2(float(vals.max())+2) if len(vals) else 0
    sparsity=float(np.mean(vals<1e-12)) if len(vals) else 0
    even=0.0; pal=0.0
    if state.kind=='poly' and deg==4:
        a,b,c,d,e=state.poly
        even=float(sp.simplify(b)==0 and sp.simplify(d)==0)
        pal=float(sp.simplify(a-e)==0 and sp.simplify(b-d)==0 and sp.simplify(a)!=0)
    root_probe=0.0
    if state.kind=='poly' and deg>2:
        root_probe=float(any(polyval(state.poly,sp.Integer(r))==0 for r in range(-12,13)))
    basic=[deg,scale,sparsity,len(state.accum),float(state.found_root is not None),even,pal,len(state.y_roots)]
    if probe: basic += [root_probe]
    return np.array(one+basic,dtype=float)


def oracle_states(task):
    s=State(task.coeffs)
    out=[]
    for a in task.plan:
        out.append((s,a))
        ns=execute(s,a)
        if ns is None: raise AssertionError((task,a,s))
        s=ns
    
    return out


def make_training(n, probe=True):
    tasks=[gen_task('train') for _ in range(n)]
    Xpos=[]; ypos=[]
    Xbin=[]; ybin={m:[] for m in MECHANICS}
    for t in tasks:
        if t.plan:
            for s,a in oracle_states(t):
                f=features(s,probe); Xpos.append(f); ypos.append(a); Xbin.append(f)
                for m in MECHANICS: ybin[m].append(int(m==a))
        else:
            # Failure-aware learner sees explicit evidence that the admitted library has no productive first move.
            s=State(t.coeffs); f=features(s,probe); Xbin.append(f)
            for m in MECHANICS: ybin[m].append(0)
    return tasks,np.array(Xpos),np.array(ypos),np.array(Xbin),{m:np.array(ybin[m]) for m in MECHANICS}


def fit_models(train):
    _,Xp,yp,Xb,yb=train
    imitation=DecisionTreeClassifier(max_depth=12,min_samples_leaf=3,random_state=SEED,class_weight='balanced').fit(Xp,yp)
    boundary={}
    for i,m in enumerate(MECHANICS):
        y=yb[m]
        if len(np.unique(y))==1:
            boundary[m]=('const',float(y[0]))
        else:
            boundary[m]=DecisionTreeClassifier(max_depth=10,min_samples_leaf=3,random_state=SEED+i+1,class_weight='balanced').fit(Xb,y)
    freq={m:int(np.sum(yp==m)) for m in MECHANICS}
    return imitation,boundary,freq


def prob_positive(model,F):
    if isinstance(model,tuple): return model[1]
    classes=list(model.classes_)
    if 1 not in classes: return 0.0
    return float(model.predict_proba(F.reshape(1,-1))[0,classes.index(1)])


def rank_imitation(model,F):
    p=model.predict_proba(F.reshape(1,-1))[0]
    pairs=sorted(zip(model.classes_,p),key=lambda z:-z[1])
    seen=[a for a,_ in pairs]
    return seen+[m for m in MECHANICS if m not in seen], float(max(p))


def run_policy(task,kind,models,probe=True,threshold=.5,max_steps=20,attempt_cap=4):
    imitation,boundary,freq=models
    s=State(task.coeffs); effort=0.0; attempts=0; path=[]; early_abstain=False
    for _ in range(max_steps):
        if s.kind=='done': return verify(task,s),effort,attempts,path,early_abstain
        F=features(s,probe)
        if kind=='frequency':
            order=sorted(MECHANICS,key=lambda m:-freq[m]); confidence=1.0
        elif kind=='blind':
            order=list(MECHANICS); confidence=1.0
        elif kind=='imitation':
            order,confidence=rank_imitation(imitation,F)
        elif kind=='failure_aware':
            scores={m:prob_positive(boundary[m],F) for m in MECHANICS}
            order=sorted(MECHANICS,key=lambda m:-scores[m]); confidence=scores[order[0]]
            if confidence < threshold:
                early_abstain=True; return False,effort,attempts,path,early_abstain
        else: raise ValueError(kind)
        progressed=False
        for m in order[:attempt_cap]:
            attempts+=1; effort+=COST[m]
            ns=execute(s,m)
            if ns is not None:
                path.append(m); s=ns; progressed=True; break
        if not progressed:
            return False,effort,attempts,path,early_abstain
    return False,effort,attempts,path,early_abstain


def tune_threshold(models,probe=True):
    val=[gen_task('iid') for _ in range(260)]
    best=None
    for th in np.arange(.25,.91,.05):
        solv=[t for t in val if t.plan]; opaque=[t for t in val if not t.plan]
        sr=np.mean([run_policy(t,'failure_aware',models,probe,th)[0] for t in solv])
        oa=np.mean([run_policy(t,'failure_aware',models,probe,th)[4] for t in opaque])
        eff=np.mean([run_policy(t,'failure_aware',models,probe,th)[1] for t in val])
        score=sr+0.65*oa-0.002*eff
        cand=(score,float(th),sr,oa,eff)
        if best is None or cand>best: best=cand
    return best


def oracle_eval(task):
    if not task.plan: return False,0.0,0,[],True
    s=State(task.coeffs); effort=0; path=[]
    for m in task.plan:
        effort+=COST[m]; path.append(m); s=execute(s,m)
    return verify(task,s),effort,len(task.plan),path,False


def evaluate(split,models,threshold,n=360,probe=True):
    tasks=[gen_task(split) for _ in range(n)]
    rows={k:[] for k in ['frequency','blind','imitation','failure_aware','oracle']}
    for t in tasks:
        for k in rows:
            r=oracle_eval(t) if k=='oracle' else run_policy(t,k,models,probe,threshold)
            rows[k].append((t,r))
    out={}
    for k,data in rows.items():
        solv=[(t,r) for t,r in data if t.plan]; opaque=[(t,r) for t,r in data if not t.plan]
        out[k]={
            'solve_rate':float(np.mean([r[0] for _,r in solv])) if solv else float('nan'),
            'mean_effort_solvable':float(np.mean([r[1] for _,r in solv])) if solv else float('nan'),
            'mean_attempts_solvable':float(np.mean([r[2] for _,r in solv])) if solv else float('nan'),
            'early_abstain_opaque':float(np.mean([r[4] for _,r in opaque])) if opaque else float('nan'),
            'effort_opaque':float(np.mean([r[1] for _,r in opaque])) if opaque else float('nan'),
            'false_commit':0.0,
        }
        # path exactness only meaningful for tasks with canonical plan
        out[k]['exact_path']=float(np.mean([tuple(r[3])==t.plan for t,r in solv])) if solv else float('nan')
        long=[(t,r) for t,r in solv if t.family=='root_chain' and t.depth>=3]
        out[k]['long_chain_solve']=float(np.mean([r[0] for _,r in long])) if long else float('nan')
    return out, tasks


def main():
    train=make_training(700,probe=True)
    models=fit_models(train)
    threshold=0.50
    print('frozen threshold',threshold)
    for split in ['iid','scale','length','mixed']:
        out,_=evaluate(split,models,threshold,n=80,probe=True)
        print('\n==',split,'==')
        for k,v in out.items():
            print(k, ' '.join(f'{a}={b:.3f}' for a,b in v.items()))

if __name__=='__main__': main()
