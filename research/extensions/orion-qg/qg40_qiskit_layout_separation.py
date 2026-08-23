"""Same question, but with summary-collisions built by CONSTRUCTION rather than
hoped for by sampling -- the same move that made the TARE result possible.

Circuits are CX multigraphs on 5 qubits.  The cheap summary is the pair
(sorted degree sequence, sorted edge-multiplicity multiset) -- both invariant
under relabelling qubits, and both computable without any transpiler call.
Non-isomorphic multigraphs sharing a summary are the analogue of two TARE types
in one joint class."""
import itertools, json, random
from collections import Counter, defaultdict
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
N=5; E=6
CM=CouplingMap.from_line(N); PERMS=list(itertools.permutations(range(N)))
PAIRS=[(a,b) for a in range(N) for b in range(a+1,N)]

def summary(mg):
    deg=Counter()
    for (a,b),m in mg.items(): deg[a]+=m; deg[b]+=m
    return (tuple(sorted(deg[v] for v in range(N))), tuple(sorted(mg.values())))
def canon(mg):
    """canonical form under qubit relabelling -> detects genuine non-isomorphism"""
    best=None
    for p in PERMS:
        k=tuple(sorted(((min(p[a],p[b]),max(p[a],p[b])),m) for (a,b),m in mg.items()))
        if best is None or k<best: best=k
    return best
groups=defaultdict(dict)
for combo in itertools.combinations_with_replacement(range(len(PAIRS)),E):
    mg=Counter(PAIRS[i] for i in combo)
    groups[summary(mg)][canon(mg)]=mg          # dedupe by isomorphism class
cand=[(s,list(d.values())) for s,d in groups.items() if len(d)>1]
cand.sort(key=lambda t:-len(t[1]))
print(f"summary classes with >1 NON-ISOMORPHIC multigraph: {len(cand)}")
print(f"  largest class holds {len(cand[0][1])} non-isomorphic circuits")
def circ(mg):
    qc=QuantumCircuit(N)
    for (a,b),m in sorted(mg.items()):
        for _ in range(m): qc.cx(a,b)
    return qc
def costs(mg):
    qc=circ(mg)
    out=[]
    for p in PERMS:
        t=transpile(qc,coupling_map=CM,initial_layout=list(p),
                    optimization_level=1,seed_transpiler=7)
        o=t.count_ops()
        out.append(o.get("cx",0)+o.get("swap",0))   # TOTAL two-qubit gates: routing
    return out                                       # inserts SWAPs, which is the cost
rng=random.Random(3)
use=cand[:14]
same_cost_diff_layout=[]; cost_split=0; tested=0
for s,members in use:
    ms=members[:4]
    recs=[]
    for mg in ms:
        c=costs(mg); m=min(c)
        recs.append({"mg":dict((f"{a}{b}",v) for (a,b),v in mg.items()),
                     "min":m,"argmin":frozenset(i for i,x in enumerate(c) if x==m)})
        tested+=1
    if len({r["min"] for r in recs})>1: cost_split+=1
    for a,b in itertools.combinations(recs,2):
        if a["min"]==b["min"] and a["argmin"]!=b["argmin"]:
            same_cost_diff_layout.append((a,b,len(a["argmin"]&b["argmin"]),s))
print(f"circuits transpiled: {tested} x {len(PERMS)} layouts")
print(f"summary classes where the optimal COST differs (existence NOT determined): {cost_split}/{len(use)}")
print(f"pairs with SAME summary, SAME optimal cost, DIFFERENT optimal-layout set: {len(same_cost_diff_layout)}")
disj=[t for t in same_cost_diff_layout if t[2]==0]
print(f"   of which DISJOINT optimal-layout sets: {len(disj)}")
for a,b,sh,s in same_cost_diff_layout[:4]:
    print(f"   deg{s[0]} mult{s[1]}: optimal cx={a['min']}, |argmin| {len(a['argmin'])} vs {len(b['argmin'])}, shared {sh}")
    print(f"      A={a['mg']}   B={b['mg']}")
json.dump({"summary_classes_multi":len(cand),"classes_tested":len(use),"circuits":tested,
 "classes_where_optimal_cost_differs":cost_split,
 "pairs_same_summary_same_cost_diff_layout":len(same_cost_diff_layout),
 "of_which_disjoint":len(disj)}, open("sep2_result.json","w"), indent=2)
