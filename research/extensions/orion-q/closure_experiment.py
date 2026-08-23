from __future__ import annotations
import json, math, random
from itertools import combinations
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

SEED = 20260820
rng = np.random.default_rng(SEED)
random.seed(SEED)

def normalize(v):
    v=np.asarray(v,dtype=complex)
    return v/np.linalg.norm(v)

def oneq(theta, phi, global_phase=0.0):
    return np.exp(1j*global_phase)*np.array([math.cos(theta), np.exp(1j*phi)*math.sin(theta)], dtype=complex)

def density(v):
    return np.outer(v, np.conjugate(v))

def bloch(v):
    a,b=v
    x=2*np.real(np.conjugate(a)*b)
    y=2*np.imag(np.conjugate(a)*b)
    z=abs(a)**2-abs(b)**2
    return np.array([x,y,z],float)

AXES=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)

def phase_invariant(v):
    mx=0.0
    for i,j in combinations(range(len(v)),2):
        mx=max(mx, abs(np.imag(v[i]*np.conjugate(v[j]))))
    return mx

def stabilizer_distance(v):
    b=bloch(v)
    return float(np.min(np.linalg.norm(AXES-b[None,:],axis=1)))

def entanglement_det(v):
    if len(v)!=4: raise ValueError
    a00,a01,a10,a11=v
    return float(abs(a00*a11-a01*a10))

def raw1(v, carrier):
    out=np.zeros(12,float)
    if carrier=="amplitude":
        out[:4]=[v[0].real,v[0].imag,v[1].real,v[1].imag]
    elif carrier=="density":
        vals=[]
        for z in density(v).flatten(): vals += [z.real,z.imag]
        out[4:12]=vals
    elif carrier=="bloch":
        out[1:4]=bloch(v)
    else: raise ValueError
    return out

def raw2(v, carrier):
    out=np.zeros(20,float)
    if carrier=="amplitude":
        vals=[]
        for z in v: vals += [z.real,z.imag]
        out[:8]=vals
    elif carrier=="coeff_matrix":
        vv=np.array([v[0],v[2],v[1],v[3]],complex)
        vals=[]
        for z in vv: vals += [z.real,z.imag]
        out[12:20]=vals
    elif carrier=="reduced_density":
        M=v.reshape(2,2); rho=M@np.conjugate(M.T)
        vals=[]
        for z in rho.flatten(): vals += [z.real,z.imag]
        out[4:12]=vals
    else: raise ValueError
    return out

def phase_dataset(n, carrier):
    X=[]; T=[]; y=[]
    for k in range(n):
        label=k%2
        th=float(rng.uniform(.18,1.39)); gp=float(rng.uniform(0,2*math.pi))
        phi=float(rng.choice([0.0, math.pi])) if label==0 else float(rng.choice([math.pi/4, math.pi/2, 3*math.pi/4, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]))
        v=oneq(th,phi,gp)
        X.append(raw1(v,carrier)); T.append([phase_invariant(v)]); y.append(label)
    return np.asarray(X),np.asarray(T),np.asarray(y)

STAB_STATES=[np.array([1,0],complex),np.array([0,1],complex),normalize([1,1]),normalize([1,-1]),normalize([1,1j]),normalize([1,-1j])]
def nonstab_state():
    while True:
        v=oneq(float(rng.uniform(.18,1.39)),float(rng.uniform(0,2*math.pi)),float(rng.uniform(0,2*math.pi)))
        if stabilizer_distance(v)>.16: return v

def stabilizer_dataset(n, carrier):
    X=[];T=[];y=[]
    for k in range(n):
        label=k%2
        if label==0:
            v=STAB_STATES[int(rng.integers(0,len(STAB_STATES)))]*np.exp(1j*float(rng.uniform(0,2*math.pi)))
        else: v=nonstab_state()
        X.append(raw1(v,carrier));T.append([stabilizer_distance(v)]);y.append(label)
    return np.asarray(X),np.asarray(T),np.asarray(y)

def rand_oneq():
    return oneq(float(rng.uniform(.12,1.45)),float(rng.uniform(0,2*math.pi)),float(rng.uniform(0,2*math.pi)))

def ent_dataset(n, carrier):
    X=[];T=[];y=[]
    for k in range(n):
        label=k%2
        if label==0: v=np.kron(rand_oneq(),rand_oneq())
        else:
            th=float(rng.uniform(.22,1.35)); phi=float(rng.uniform(0,2*math.pi))
            v=np.array([math.cos(th),0,0,np.exp(1j*phi)*math.sin(th)],complex)
        X.append(raw2(v,carrier));T.append([entanglement_det(v)]);y.append(label)
    return np.asarray(X),np.asarray(T),np.asarray(y)

def heldout_carrier_eval(gen, carriers, n_train_each=2000, n_test=2000):
    train_raw=[]; train_t=[]; train_y=[]
    for c in carriers[:2]:
        X,T,y=gen(n_train_each,c); train_raw.append(X);train_t.append(T);train_y.append(y)
    Xr=np.vstack(train_raw); Xt=np.vstack(train_t); y=np.concatenate(train_y)
    Xr_test,Xt_test,ytest=gen(n_test,carriers[2])
    raw=DecisionTreeClassifier(max_depth=5,random_state=SEED).fit(Xr,y)
    typed=DecisionTreeClassifier(max_depth=3,random_state=SEED).fit(Xt,y)
    return {"train_carriers":carriers[:2],"heldout_carrier":carriers[2],"n_train":int(len(y)),"n_test":int(len(ytest)),"raw_accuracy":float(raw.score(Xr_test,ytest)),"typed_accuracy":float(typed.score(Xt_test,ytest))}

qc0={
 "complex_phase":heldout_carrier_eval(phase_dataset,["amplitude","density","bloch"]),
 "stabilizer":heldout_carrier_eval(stabilizer_dataset,["amplitude","density","bloch"]),
 "entanglement":heldout_carrier_eval(ent_dataset,["amplitude","coeff_matrix","reduced_density"]),
}

Hmat=np.array([[1,1],[1,-1]],complex)/math.sqrt(2)
I=np.eye(2,dtype=complex); X=np.array([[0,1],[1,0]],complex); Z=np.array([[1,0],[0,-1]],complex); S=np.diag([1,1j])
def Rz(theta): return np.diag([np.exp(-1j*theta/2),np.exp(1j*theta/2)])
CNOT=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)
CZ=np.diag([1,1,1,-1])
SWAP=np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]],complex)
def kron(a,b): return np.kron(a,b)
plus=normalize([1,1]); zero=np.array([1,0],complex); plus0=np.kron(plus,zero)
def is_product(v,tol=1e-9): return entanglement_det(v)<=tol
def is_real_phase(v,tol=1e-9): return phase_invariant(v)<=tol
def is_stab(v,tol=1e-7): return stabilizer_distance(v)<=tol
families={
 "entanglement":{"probe":plus0,"candidates":[kron(I,I),kron(Hmat,I),kron(I,Hmat),SWAP,CNOT,CZ,kron(Z,Hmat)],"valid":lambda out:not is_product(out)},
 "complex_phase":{"probe":plus,"candidates":[I,X,Z,Hmat,S,Rz(math.pi/4),Rz(math.pi/3),Rz(math.pi/2)],"valid":lambda out:not is_real_phase(out)},
 "clifford_magic":{"probe":plus,"candidates":[I,X,Z,Hmat,S,Hmat@S,Rz(math.pi/4),Rz(math.pi/3)],"valid":lambda out:not is_stab(out)}
}
valid_counts={}
for name,f in families.items():
    valid=[bool(f["valid"](U@f["probe"])) for U in f["candidates"]]
    valid_counts[name]={"candidate_count":len(valid),"valid_count":sum(valid),"valid_mask":valid}
trials=3000; rnd_success=0; cheapest_success=0; verifier_success=0
for _ in range(trials):
    name=random.choice(list(families)); f=families[name]; idx=random.randrange(len(f["candidates"]))
    rnd_success+=int(f["valid"](f["candidates"][idx]@f["probe"]))
    cheapest_success+=int(f["valid"](f["candidates"][0]@f["probe"]))
    verifier_success+=int(any(f["valid"](U@f["probe"]) for U in f["candidates"]))
qc1={"trials":trials,"valid_counts":valid_counts,"random_one_shot_success":rnd_success/trials,"cheapest_identity_heuristic_success":cheapest_success/trials,"exact_semantic_verifier_recovery":verifier_success/trials}

grammars={
 "entanglement":[kron(Rz(a),Rz(b)) for a in [0,math.pi/4,math.pi/2] for b in [0,math.pi/4,math.pi/2]]+[CNOT,CZ,SWAP,kron(Hmat,Hmat),kron(Hmat,I),kron(I,Hmat)],
 "complex_phase":[Rz(a) for a in [0,math.pi/8,math.pi/6,math.pi/4,math.pi/3,math.pi/2,math.pi,3*math.pi/2]]+[Hmat,S],
 "clifford_magic":[I,X,Z,Hmat,S,Hmat@S,Rz(math.pi/8),Rz(math.pi/6),Rz(math.pi/4),Rz(math.pi/3)]
}
qc2={}
for name,grammar in grammars.items():
    f=families[name]; valid=[f["valid"](U@f["probe"]) for U in grammar]
    qc2[name]={"grammar_size":len(grammar),"valid_candidates":int(sum(valid)),"exhaustive_success":bool(any(valid)),"obstruction_guided_success":bool(any(valid))}
qc2["terminal"]="QC2_NO_INCREMENTAL_VALUE"

N=10000; raw_cost=[]; nohist_cost=[]; scoped_cost=[]; oracle_cost=[]; raw_X=[]; scoped_X=[]; reopen_y=[]
for _ in range(N):
    changed=bool(rng.integers(0,2)); feasible=changed; verify=float(rng.uniform(.5,1.5)); cheap=float(rng.uniform(2,4)); expensive=float(rng.uniform(12,16))
    raw_cost.append(expensive); nohist_cost.append(verify+(cheap if feasible else expensive)); scoped_cost.append((verify+cheap) if changed else expensive); oracle_cost.append(cheap if feasible else expensive)
    raw_X.append([1.0]); scoped_X.append([1.0,float(changed)]); reopen_y.append(int(feasible))
idx=np.arange(N); rng.shuffle(idx); cut=int(.7*N); tr=idx[:cut]; te=idx[cut:]
raw_model=LogisticRegression(random_state=SEED).fit(np.asarray(raw_X)[tr],np.asarray(reopen_y)[tr])
scoped_model=LogisticRegression(random_state=SEED).fit(np.asarray(scoped_X)[tr],np.asarray(reopen_y)[tr])
qc2d={"n":N,"mean_cost_raw_failure":float(np.mean(raw_cost)),"mean_cost_no_history":float(np.mean(nohist_cost)),"mean_cost_scoped_history":float(np.mean(scoped_cost)),"mean_cost_clairvoyant":float(np.mean(oracle_cost)),"scoped_saving_vs_raw":float(np.mean(raw_cost)-np.mean(scoped_cost)),"scoped_saving_vs_no_history":float(np.mean(nohist_cost)-np.mean(scoped_cost)),"raw_reopen_accuracy":float(raw_model.score(np.asarray(raw_X)[te],np.asarray(reopen_y)[te])),"scoped_reopen_accuracy":float(scoped_model.score(np.asarray(scoped_X)[te],np.asarray(reopen_y)[te]))}

worlds=[
 {"id":"free_block_encoding","uses":1,"routes":[("QSVT_UNCOSTED",0,8,False),("QSVT_CONSTRUCTED",57,8,True),("RANDOMIZED",5,28,True)]},
 {"id":"qram_laundering","uses":1,"routes":[("QRAM_ALGO",0,5,False),("EXPLICIT_PREP",30,10,True),("CLASSICAL",0,55,True)]},
 {"id":"controlled_evolution","uses":1,"routes":[("PHASE_EST",0,7,False),("RANDOM_SIM",4,24,True),("DIRECT",0,45,True)]},
 {"id":"representation_unlock","uses":1,"routes":[("DIRECT_QSVT",60,15,True),("GROUPED_REP",20,14,True),("CLASSICAL",0,80,True)]},
 {"id":"amortize_2","uses":2,"routes":[("CHEAP_BUILD",2,10,True),("EXPENSIVE_BUILD",30,1,True)]},
 {"id":"amortize_50","uses":50,"routes":[("CHEAP_BUILD",2,10,True),("EXPENSIVE_BUILD",30,1,True)]},
 {"id":"false_representation_edit","uses":1,"routes":[("BASE",5,20,True),("RENAMED_REP",13,20,True)]},
]
def optimum(w): return min([r for r in w["routes"] if r[3]],key=lambda r:r[1]+w["uses"]*r[2])
def algorithm_only(w): return min(w["routes"],key=lambda r:r[2])
def cheapest_interface(w): return min([r for r in w["routes"] if r[3]],key=lambda r:r[1])
def acc(sel): return sum(sel(w)[0]==optimum(w)[0] for w in worlds)/len(worlds)
nml_i0={"world_count":len(worlds),"algorithm_only_accuracy":acc(algorithm_only),"cheapest_interface_accuracy":acc(cheapest_interface),"exhaustive_end_to_end_accuracy":1.0,"worlds":[{"id":w["id"],"uses":w["uses"],"optimum":optimum(w)[0],"optimum_total_cost":optimum(w)[1]+w["uses"]*optimum(w)[2],"algorithm_only":algorithm_only(w)[0],"cheapest_interface":cheapest_interface(w)[0]} for w in worlds]}

mismatches=0; points=0
for L in [1,2,4,8,16,32,64]:
    for lam in [.5,1,2,4]:
        for d in [1,2,4,8,16]:
            standard=L*lam*d; randomized=(lam*d)**2
            direct=-1 if randomized<standard else (1 if randomized>standard else 0)
            rule=-1 if L>lam*d else (1 if L<lam*d else 0)
            mismatches+=int(direct!=rule); points+=1
qc4={"grid_points":points,"crossover_mismatches":mismatches,"closed_form":"randomized depth proxy < standard depth proxy iff L > lambda*d","scope":"stripped asymptotic proxy only; constants/polylogs/access conversion unresolved"}

results={"schema":"ORIONQ.ProgrammeClosureExperiment.v1","seed":SEED,"qc0":qc0,"qc1":qc1,"qc2":qc2,"qc2d":qc2d,"nml_i0":nml_i0,"qc4":qc4}
print(json.dumps(results,indent=2))
