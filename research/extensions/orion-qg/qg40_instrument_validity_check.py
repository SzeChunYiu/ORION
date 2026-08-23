"""Validity check: is the Qiskit experiment even capable of showing a separation?
If every layout is optimal, or if cost never varies with layout, the negative is
vacuous and must not be reported."""
import itertools
from collections import Counter
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
N=5; CM=CouplingMap.from_line(N); PERMS=list(itertools.permutations(range(N)))
def circ(edges):
    qc=QuantumCircuit(N)
    for a,b in edges: qc.cx(a,b)
    return qc
tests={"star (0 central)":[(0,1),(0,2),(0,3),(0,4),(0,1),(0,2)],
       "path":[(0,1),(1,2),(2,3),(3,4),(0,1),(1,2)],
       "two triangles":[(0,1),(1,2),(0,2),(2,3),(3,4),(2,4)]}
for name,e in tests.items():
    qc=circ(e)
    cs=[transpile(qc,coupling_map=CM,initial_layout=list(p),optimization_level=0,
                  seed_transpiler=7).count_ops().get("cx",0) for p in PERMS]
    m=min(cs)
    print(f"{name:18s} cx range [{m},{max(cs)}]  |argmin|={sum(1 for x in cs if x==m)}/120  "
          f"distinct costs={len(set(cs))}")
