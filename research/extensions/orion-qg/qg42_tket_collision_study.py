"""Second compiler: is the phenomenon Qiskit-specific? Same design, tket routing.
Options = 24 placements on a line Architecture; cost = CX count after tket routing.
"""
import itertools, json, random, sys, time
from collections import defaultdict, Counter
from pytket.circuit import Circuit, Node, OpType
from pytket.architecture import Architecture
from pytket.passes import RoutingPass, FullPeepholeOptimise, SequencePass
import pytket

N=4; NCIRC=int(sys.argv[1]); MTERMS=3
POST = (len(sys.argv)>2 and sys.argv[2]=="opt")     # add FullPeepholeOptimise
arch=Architecture([(i,i+1) for i in range(N-1)])
PERMS=list(itertools.permutations(range(N)))

def build(terms,angle=0.31/3.14159265358979):
    c=Circuit(N)
    for term in terms:
        supp=[q for q,p in enumerate(term) if p!="I"]
        if not supp: continue
        for q in supp:
            if term[q]=="X": c.H(q)
            elif term[q]=="Y": c.Sdg(q); c.H(q)
        for a,b in zip(supp,supp[1:]): c.CX(a,b)
        c.Rz(angle,supp[-1])
        for a,b in reversed(list(zip(supp,supp[1:]))): c.CX(a,b)
        for q in supp:
            if term[q]=="X": c.H(q)
            elif term[q]=="Y": c.H(q); c.S(q)
    return c
def permuted(c,p):
    out=Circuit(N)
    for cmd in c.get_commands():
        qs=[p[c.qubits.index(q)] for q in cmd.qubits]
        out.add_gate(cmd.op.type,cmd.op.params,qs)
    return out
def gatelist(c):
    return tuple((str(cmd.op.type),tuple(c.qubits.index(q) for q in cmd.qubits),
                  tuple(round(float(x),6) for x in cmd.op.params)) for cmd in c.get_commands())
def canonical(c): return min(gatelist(permuted(c,p)) for p in PERMS)
def cost(c,L):
    c2=c.copy(); c2.rename_units({c2.qubits[i]:Node(L[i]) for i in range(N)})
    RoutingPass(arch).apply(c2)
    if POST: FullPeepholeOptimise(allow_swaps=False).apply(c2)
    return c2.n_gates_of_type(OpType.CX)

# determinism + covariance validation FIRST
random.seed(1); t=("XXII","IZZI","IIXX")
c=build(t); a=[cost(c,L) for L in PERMS]; b=[cost(c,L) for L in PERMS]
p=PERMS[7]; cv=sorted(cost(permuted(c,p),L) for L in PERMS)
print(f"tket {pytket.__version__} deterministic={a==b} covariant={sorted(a)==cv}",flush=True)
if a!=b or sorted(a)!=cv:
    print("VALIDATION FAILED - not reporting downstream numbers"); sys.exit(1)

random.seed(20260822); seen=set(); reps=[]; tries=0
while len(reps)<NCIRC and tries<NCIRC*300:
    tries+=1
    terms=tuple("".join(random.choice("IIXYZ") for _ in range(N)) for _ in range(MTERMS))
    if min(len([1 for x in tt if x!="I"]) for tt in terms)<2: continue
    c=build(terms); k=canonical(c)
    if k in seen: continue
    seen.add(k); reps.append((terms,c))
t0=time.time(); rows=[]
for i,(terms,c) in enumerate(reps):
    vec=tuple(cost(c,L) for L in PERMS); m=min(vec)
    raw=c.n_gates_of_type(OpType.CX)
    rows.append({"terms":terms,"bulk":(raw,c.depth()),"spec":tuple(sorted(vec)),"vec":vec,
                 "opt":m,"argmin":tuple(j for j,v in enumerate(vec) if v==m)})
    if (i+1)%500==0: print(f"  {i+1}/{len(reps)} {(time.time()-t0)/(i+1):.3f}s",flush=True)
def analyse(keyfn,label):
    cls=defaultdict(list)
    for r in rows: cls[keyfn(r)].append(r)
    multi={k:v for k,v in cls.items() if len(v)>1}
    nt={k:v for k,v in multi.items() if len({r["vec"] for r in v})>1}
    nc=lambda v,k: len({r[k] for r in v})>1
    sant={k:v for k,v in nt.items() if nc(v,"argmin")}
    so={k:v for k,v in multi.items() if nc(v,"opt")}
    dcl=sum(1 for v in sant.values() if any(not(set(a)&set(b))
            for a,b in itertools.combinations({r["argmin"] for r in v},2)))
    return {"label":label,"n_classes_ge2":len(multi),
      "classes_nonconstant_OPTIMAL_VALUE":len(so),
      "NONTRIVIAL_classes":len(nt),"NONTRIVIAL_nonconstant_ARGMIN":len(sant),
      "NONTRIVIAL_frac":(round(len(sant)/len(nt),3) if nt else None),
      "CLASSES_with_disjoint_argmin_pair":dcl,
      "distinct_argmin_sets_overall":len({r["argmin"] for r in rows}),
      "median_distinct_sets_per_nontrivial_class":
        (sorted(len({r["argmin"] for r in v}) for v in nt.values())[len(nt)//2] if nt else None)}
res={"config":{"compiler":f"pytket {pytket.__version__}","n_qubits":N,"n_options":24,
      "n_terms":MTERMS,"post_opt":POST,"cost":"CX after RoutingPass"+("+FullPeepholeOptimise" if POST else ""),
      "n_canonical_circuits":len(rows),"elapsed_s":round(time.time()-t0,1)},
     "bulk_x_spectrum":analyse(lambda r:(r["bulk"],r["spec"]),"bulk x spectrum"),
     "spectrum_only":analyse(lambda r:r["spec"],"spectrum only"),
     "bulk_only":analyse(lambda r:r["bulk"],"bulk only")}
json.dump(res,open(f"tket_n4_{'opt' if POST else 'route'}_c{len(rows)}.json","w"),indent=1,default=str)
print(json.dumps(res,indent=1,default=str))
