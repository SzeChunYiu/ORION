"""PHENOMENON-TRANSFER CHECK v2 (NOT a performance comparison).
Corrected: the relabelling quotient acts on the BUILT CIRCUIT (validated
covariant in validate_symmetry2.py: 8/8), not on the Pauli strings.

ORION-QG QG-34/35 object      |  this experiment (real compiler)
------------------------------+-------------------------------------------
715 local-Clifford orbit reps |  canonical circuits mod qubit permutation
384 Tag-constrained frames    |  n! initial layouts on a fixed coupling map
config_cost (R6M grammar)     |  Qiskit post-routing 2-qubit gate count
bulk = 4 cheap baselines      |  (raw cx count, raw depth)  [deliberately coarse]
spectrum = sorted 384-vector  |  sorted n!-cost vector
No cost NUMBER crosses between the two systems; only the dimensionless
"fraction of exact-collision classes with non-constant argmin".
"""
import itertools, json, random, sys, time
from collections import defaultdict, Counter
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

N=int(sys.argv[1]); NCIRC=int(sys.argv[2]); MTERMS=int(sys.argv[3])
OPT=int(sys.argv[4]); ROUTE=sys.argv[5]
cmap=CouplingMap.from_line(N); BASIS=["rz","sx","x","cx"]
PERMS=list(itertools.permutations(range(N)))

def build(terms,angle=0.31):
    qc=QuantumCircuit(N)
    for term in terms:
        supp=[q for q,p in enumerate(term) if p!="I"]
        if not supp: continue
        for q in supp:
            if term[q]=="X": qc.h(q)
            elif term[q]=="Y": qc.sdg(q); qc.h(q)
        for a,b in zip(supp,supp[1:]): qc.cx(a,b)
        qc.rz(angle,supp[-1])
        for a,b in reversed(list(zip(supp,supp[1:]))): qc.cx(a,b)
        for q in supp:
            if term[q]=="X": qc.h(q)
            elif term[q]=="Y": qc.h(q); qc.s(q)
    return qc
def permute_circuit(qc,p):
    out=QuantumCircuit(N); out.compose(qc,qubits=[p[i] for i in range(N)],inplace=True); return out
def gatelist(qc):
    idx={q:i for i,q in enumerate(qc.qubits)}
    return tuple((ins.operation.name,tuple(idx[q] for q in ins.qubits),
                  tuple(round(float(x),6) for x in ins.operation.params)) for ins in qc.data)
def canonical_circ(qc): return min(gatelist(permute_circuit(qc,p)) for p in PERMS)
def cost(qc,L):
    return transpile(qc,coupling_map=cmap,basis_gates=BASIS,initial_layout=list(L),
        routing_method=ROUTE,optimization_level=OPT,seed_transpiler=1234).count_ops().get("cx",0)

random.seed(20260822); seen=set(); reps=[]; tries=0
while len(reps)<NCIRC and tries<NCIRC*300:
    tries+=1
    terms=tuple("".join(random.choice("IIXYZ") for _ in range(N)) for _ in range(MTERMS))
    if min(len([1 for p in t if p!="I"]) for t in terms)<2: continue
    qc=build(terms); c=canonical_circ(qc)
    if c in seen: continue
    seen.add(c); reps.append((terms,qc))

t0=time.time(); rows=[]
for i,(terms,qc) in enumerate(reps):
    vec=tuple(cost(qc,L) for L in PERMS); m=min(vec)
    rows.append({"terms":terms,"bulk":(qc.count_ops().get("cx",0),qc.depth()),
                 "spec":tuple(sorted(vec)),"vec":vec,"opt":m,
                 "argmin":tuple(j for j,v in enumerate(vec) if v==m)})
    if (i+1)%200==0: print(f"  {i+1}/{len(reps)} {(time.time()-t0)/(i+1):.3f}s/circ",flush=True)

def analyse(keyfn,label):
    cls=defaultdict(list)
    for r in rows: cls[keyfn(r)].append(r)
    multi={k:v for k,v in cls.items() if len(v)>1}
    nt={k:v for k,v in multi.items() if len({r["vec"] for r in v})>1}   # full vector differs
    nc=lambda v,k: len({r[k] for r in v})>1
    sa={k:v for k,v in multi.items() if nc(v,"argmin")}
    sant={k:v for k,v in nt.items() if nc(v,"argmin")}
    so={k:v for k,v in multi.items() if nc(v,"opt")}
    # ORION part (a) checks FIVE predicates; add the cheap second one: |argmin|
    nopt=lambda r: len(r["argmin"])
    so_n={k:v for k,v in multi.items() if len({nopt(r) for r in v})>1}
    dis=[]; dis_classlevel=0
    for k,v in sant.items():
        S=[r["argmin"] for r in v]
        if any(not(set(a)&set(b)) for a,b in itertools.combinations(set(S),2)): dis_classlevel+=1
    for k,v in sant.items():
        for a,b in itertools.combinations(v,2):
            if not (set(a["argmin"])&set(b["argmin"])):
                dis.append({"A":a["terms"],"B":b["terms"],"opt":a["opt"],
                            "argminA":a["argmin"],"argminB":b["argmin"]})
    # DIVERSITY: 959 "pairs" can be k*m from ONE structural fact. Count distinct sets.
    per_class_distinct=[len({r["argmin"] for r in v}) for v in nt.values()]
    from collections import Counter as _C
    diversity={"distinct_argmin_sets_overall":len({r["argmin"] for r in rows}),
       "distinct_argmin_sets_within_nontrivial_classes":
           len({r["argmin"] for v in nt.values() for r in v}),
       "distinct_sets_per_nontrivial_class_histogram":dict(sorted(_C(per_class_distinct).items())),
       "median_distinct_sets_per_nontrivial_class":
           (sorted(per_class_distinct)[len(per_class_distinct)//2] if per_class_distinct else None),
       "n_total_circuits":len(rows)}
    return {"summary":label,"diversity":diversity,"n_classes_ge2":len(multi),
            "n_circuits_in_them":sum(len(v) for v in multi.values()),
            "classes_nonconstant_OPTIMAL_VALUE":len(so),
            "classes_nonconstant_NUMBER_OF_OPTIMAL_OPTIONS":len(so_n),
            "classes_nonconstant_ARGMIN":len(sa),
            "NONTRIVIAL_classes_vec_differs":len(nt),
            "NONTRIVIAL_classes_nonconstant_ARGMIN":len(sant),
            "NONTRIVIAL_frac_nonconstant_ARGMIN":(round(len(sant)/len(nt),3) if nt else None),
            "pairs_DISJOINT_argmin":len(dis),
            "CLASSES_containing_a_disjoint_argmin_pair":dis_classlevel,"disjoint_examples":dis[:4]}

res={"config":{"n_qubits":N,"coupling":"line","n_options":len(PERMS),"n_terms":MTERMS,
      "optimization_level":OPT,"routing_method":ROUTE,"cost":"post-routing cx count",
      "n_canonical_circuits":len(rows),"elapsed_s":round(time.time()-t0,1),
      "quotient":"circuit-level qubit permutation (covariance validated 8/8)"},
     "bulk_x_spectrum":analyse(lambda r:(r["bulk"],r["spec"]),"bulk x spectrum"),
     "spectrum_only":analyse(lambda r:r["spec"],"spectrum only"),
     "bulk_only":analyse(lambda r:r["bulk"],"bulk only")}
tag=f"v2_n{N}_m{MTERMS}_opt{OPT}_{ROUTE}_c{len(rows)}"
json.dump(res,open(f"{tag}.json","w"),indent=1,default=str)
print(json.dumps(res,indent=1,default=str)[:3800])
