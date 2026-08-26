#!/usr/bin/env python3
"""Clean-room replay of the FiberGuard R8 finite panels.

This implementation does not import or call the reference FiberGuard program.
It uses:
- graph-atlas relabeling + independent-set-cover DP for graph colouring;
- coverage-state BFS for set cover;
- recursive formula simplification (DPLL counting) for 2-CNF.
A primitive third checker is run only on selected endpoint witnesses.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Hashable, Iterable, Sequence

import networkx as nx

SCHEMA = "ORION.FiberGuardR8.CleanRoomReplay.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


@dataclass
class Fibre:
    lo: int
    hi: int
    lo_witness: Any
    hi_witness: Any
    count: int = 1

    @property
    def diameter(self) -> int:
        return self.hi - self.lo


def update(table: dict[Hashable, Fibre], feature: Hashable, target: int, witness: Any) -> None:
    row = table.get(feature)
    if row is None:
        table[feature] = Fibre(target, target, witness, witness)
        return
    row.count += 1
    if target < row.lo:
        row.lo = target
        row.lo_witness = witness
    if target > row.hi:
        row.hi = target
        row.hi_witness = witness


def select_max(table: dict[Hashable, Fibre]) -> tuple[Hashable, Fibre]:
    return max(table.items(), key=lambda kv: (kv[1].diameter, kv[1].count, repr(kv[0])))


def refinement(records: Sequence[tuple[Any, int]], base: Callable[[Any], Hashable], candidates: dict[str, Callable[[Any], Hashable]], baseline: str) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name, extra in candidates.items():
        tab: dict[Hashable, Fibre] = {}
        for instance, target in records:
            update(tab, (base(instance), extra(instance)), target, None)
        results[name] = {
            "refined_fibre_count": len(tab),
            "ambiguous_fibre_count": sum(row.diameter > 0 for row in tab.values()),
            "maximum_fibre_diameter": max(row.diameter for row in tab.values()),
        }
    selected = min(results, key=lambda name: (results[name]["maximum_fibre_diameter"], results[name]["ambiguous_fibre_count"], name))
    return {
        "candidate_results": results,
        "collision_guided_selection": selected,
        "collision_guided_result": results[selected],
        "matched_baseline_selection": baseline,
        "matched_baseline_result": results[baseline],
        "strict_improvement_over_baseline": (
            results[selected]["maximum_fibre_diameter"], results[selected]["ambiguous_fibre_count"]
        ) < (
            results[baseline]["maximum_fibre_diameter"], results[baseline]["ambiguous_fibre_count"]
        ),
    }


# ---------------- graph domain ----------------
EDGE_PAIRS_6 = tuple((i, j) for i in range(6) for j in range(i + 1, 6))
EDGE_INDEX_6 = {edge: i for i, edge in enumerate(EDGE_PAIRS_6)}


def graph_mask_from_edges(edges: Iterable[tuple[int, int]]) -> int:
    mask = 0
    for u, v in edges:
        if u > v:
            u, v = v, u
        mask |= 1 << EDGE_INDEX_6[(u, v)]
    return mask


def graph_masks_from_atlas() -> tuple[int, ...]:
    reps = [g for g in nx.graph_atlas_g() if len(g) == 6]
    assert len(reps) == 156, len(reps)
    masks: set[int] = set()
    for g in reps:
        nodes = tuple(sorted(g.nodes()))
        edges = tuple(g.edges())
        for perm in itertools.permutations(range(6)):
            mapping = {nodes[i]: perm[i] for i in range(6)}
            masks.add(graph_mask_from_edges((mapping[u], mapping[v]) for u, v in edges))
    assert len(masks) == 1 << 15, len(masks)
    return tuple(sorted(masks))


def graph_adj(mask: int) -> tuple[int, ...]:
    adj = [0] * 6
    for bit, (i, j) in enumerate(EDGE_PAIRS_6):
        if (mask >> bit) & 1:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    return tuple(adj)


def graph_feature(mask: int) -> tuple[tuple[int, ...], int]:
    adj = graph_adj(mask)
    degrees = tuple(sorted(x.bit_count() for x in adj))
    triangles = 0
    for i, j, k in itertools.combinations(range(6), 3):
        if ((adj[i] >> j) & 1) and ((adj[i] >> k) & 1) and ((adj[j] >> k) & 1):
            triangles += 1
    return degrees, triangles


def chromatic_independent_cover(mask: int) -> int:
    adj = graph_adj(mask)
    independent = [True] * 64
    for subset in range(64):
        independent[subset] = all(not ((subset >> v) & 1) or not (adj[v] & (subset & ~((1 << (v + 1)) - 1))) for v in range(6))

    @functools.lru_cache(None)
    def solve(remaining: int) -> int:
        if remaining == 0:
            return 0
        pivot = (remaining & -remaining).bit_length() - 1
        best = 6
        sub = remaining
        while sub:
            if ((sub >> pivot) & 1) and independent[sub]:
                best = min(best, 1 + solve(remaining ^ sub))
            sub = (sub - 1) & remaining
        return best

    return solve(63)


def graph_extras(mask: int) -> dict[str, int]:
    adj = graph_adj(mask)
    seen = 0
    components = 0
    for start in range(6):
        if (seen >> start) & 1:
            continue
        components += 1
        stack = [start]
        seen |= 1 << start
        while stack:
            v = stack.pop()
            unseen = adj[v] & ~seen
            while unseen:
                bit = unseen & -unseen
                seen |= bit
                stack.append(bit.bit_length() - 1)
                unseen ^= bit
    four_cycles_twice = 0
    for i in range(6):
        for j in range(i + 1, 6):
            c = (adj[i] & adj[j]).bit_count()
            four_cycles_twice += c * (c - 1) // 2
    four_cycles = four_cycles_twice // 2
    clique = 0
    for subset in range(64):
        if subset.bit_count() <= clique:
            continue
        ok = True
        for v in range(6):
            if (subset >> v) & 1:
                others = subset & ~(1 << v)
                if others & ~adj[v]:
                    ok = False
                    break
        if ok:
            clique = subset.bit_count()
    return {"connected_component_count": components, "four_cycle_count": four_cycles, "clique_number": clique}


def chromatic_assignment_check(mask: int) -> int:
    edges = [edge for bit, edge in enumerate(EDGE_PAIRS_6) if (mask >> bit) & 1]
    for k in range(1, 7):
        for colors in itertools.product(range(k), repeat=6):
            if all(colors[u] != colors[v] for u, v in edges):
                return k
    raise AssertionError


def run_graph() -> dict[str, Any]:
    table: dict[Hashable, Fibre] = {}
    records: list[tuple[int, int]] = []
    masks = graph_masks_from_atlas()
    for mask in masks:
        target = chromatic_independent_cover(mask)
        records.append((mask, target))
        update(table, graph_feature(mask), target, {"edge_mask": mask})
    feature, row = select_max(table)
    assert chromatic_assignment_check(row.lo_witness["edge_mask"]) == row.lo
    assert chromatic_assignment_check(row.hi_witness["edge_mask"]) == row.hi
    candidates = {name: (lambda m, name=name: graph_extras(m)[name]) for name in graph_extras(0)}
    return {
        "domain": "GRAPH_COLOURING_N6",
        "generator": {"method": "NetworkX graph atlas representatives exhaustively relabeled", "unlabeled_representatives": 156, "unique_labeled_masks": len(masks)},
        "instance_count": len(masks), "fibre_count": len(table), "maximum_fibre_diameter": row.diameter,
        "endpoint_values": [row.lo, row.hi], "fibre_multiplicity": row.count,
        "endpoint_witnesses": [row.lo_witness, row.hi_witness],
        "representation_feature": [list(feature[0]), feature[1]],
        "refinement_experiment": refinement(records, graph_feature, candidates, "connected_component_count"),
        "endpoint_third_checker": "complete color-assignment enumeration",
    }


# ---------------- set cover domain ----------------
def cover_feature(family: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(sorted(x.bit_count() for x in family)), tuple(sorted((family[i] & family[j]).bit_count() for i in range(5) for j in range(i + 1, 5)))


def cover_bfs(family: tuple[int, ...]) -> int:
    dist = [-1] * 32
    dist[0] = 0
    q = deque([0])
    while q:
        state = q.popleft()
        if state == 31:
            return dist[state]
        for subset in family:
            nxt = state | subset
            if dist[nxt] < 0:
                dist[nxt] = dist[state] + 1
                q.append(nxt)
    raise AssertionError


def cover_extras(family: tuple[int, ...]) -> dict[str, Hashable]:
    return {
        "pairwise_union_multiset": tuple(sorted((family[i] | family[j]).bit_count() for i in range(5) for j in range(i + 1, 5))),
        "element_frequency_multiset": tuple(sorted(sum((s >> e) & 1 for s in family) for e in range(5))),
        "triple_intersection_multiset": tuple(sorted((family[i] & family[j] & family[k]).bit_count() for i in range(5) for j in range(i + 1, 5) for k in range(j + 1, 5))),
    }


def cover_subset_check(family: tuple[int, ...]) -> int:
    for size in range(1, 6):
        for chosen in itertools.combinations(family, size):
            if functools.reduce(int.__or__, chosen, 0) == 31:
                return size
    raise AssertionError


def run_cover() -> dict[str, Any]:
    table: dict[Hashable, Fibre] = {}
    records: list[tuple[tuple[int, ...], int]] = []
    count = 0
    for family in itertools.combinations(range(1, 32), 5):
        if functools.reduce(int.__or__, family, 0) != 31:
            continue
        count += 1
        target = cover_bfs(family)
        records.append((family, target))
        update(table, cover_feature(family), target, {"sets": list(family)})
    feature, row = select_max(table)
    lo_family = tuple(row.lo_witness["sets"]); hi_family = tuple(row.hi_witness["sets"])
    assert cover_subset_check(lo_family) == row.lo
    assert cover_subset_check(hi_family) == row.hi
    candidates = {name: (lambda fam, name=name: cover_extras(fam)[name]) for name in cover_extras((1,2,4,8,16))}
    return {
        "domain": "SET_COVER_U5_M5", "generator": {"method": "ordered five-subset recursion over nonempty U5 subsets with exact union filter"},
        "instance_count": count, "fibre_count": len(table), "maximum_fibre_diameter": row.diameter,
        "endpoint_values": [row.lo, row.hi], "fibre_multiplicity": row.count,
        "endpoint_witnesses": [row.lo_witness, row.hi_witness],
        "representation_feature": [list(feature[0]), list(feature[1])],
        "refinement_experiment": refinement(records, cover_feature, candidates, "element_frequency_multiset"),
        "endpoint_third_checker": "cardinality-ordered subset enumeration",
    }


# ---------------- 2-CNF domain ----------------
LITERAL_ORDER = (1,2,3,4,-1,-2,-3,-4)
LITERAL_RANK = {lit:i for i,lit in enumerate(LITERAL_ORDER)}


def canonical_clause(a: int, b: int) -> tuple[int,int]:
    return (a,b) if LITERAL_RANK[a] < LITERAL_RANK[b] else (b,a)


def clause_universe() -> tuple[tuple[int,int], ...]:
    clauses = {canonical_clause(si*i, sj*j) for i in range(1,5) for j in range(i+1,5) for si in (1,-1) for sj in (1,-1)}
    return tuple(sorted(clauses, key=lambda c:(LITERAL_RANK[c[0]],LITERAL_RANK[c[1]])))


def simplify_formula(formula: tuple[tuple[int,...], ...], var: int, value: bool) -> tuple[tuple[int,...], ...] | None:
    output=[]
    for clause in formula:
        satisfied=False; rem=[]
        for lit in clause:
            if abs(lit)==var:
                truth = value if lit>0 else not value
                if truth:
                    satisfied=True; break
            else:
                rem.append(lit)
        if satisfied:
            continue
        if not rem:
            return None
        output.append(tuple(rem))
    return tuple(sorted(output))


def count_dpll(formula: tuple[tuple[int,int], ...]) -> int:
    @functools.lru_cache(None)
    def rec(var: int, current: tuple[tuple[int,...], ...]) -> int:
        if current is None:
            return 0
        if var == 5:
            return 1
        total=0
        for value in (False, True):
            nxt=simplify_formula(current,var,value)
            if nxt is not None:
                total += rec(var+1,nxt)
        return total
    return rec(1, tuple(tuple(c) for c in formula))


def sat_feature(formula: tuple[tuple[int,int], ...]) -> tuple[tuple[int,...], tuple[int,...]]:
    pos=[0]*4; neg=[0]*4; pairs=[[0]*4 for _ in range(4)]
    for a,b in formula:
        for lit in (a,b):
            (pos if lit>0 else neg)[abs(lit)-1]+=1
        i,j=sorted((abs(a)-1,abs(b)-1)); pairs[i][j]+=1
    return tuple(pos+neg), tuple(pairs[i][j] for i in range(4) for j in range(i+1,4))


def sat_extras(formula: tuple[tuple[int,int], ...]) -> dict[str,Hashable]:
    global_types=[0]*4; per_pair:dict[tuple[int,int],list[int]]={}
    for a,b in formula:
        if abs(a)>abs(b): a,b=b,a
        t=(0 if a>0 else 2)+(0 if b>0 else 1)
        global_types[t]+=1
        pair=(abs(a)-1,abs(b)-1)
        per_pair.setdefault(pair,[0]*4)[t]+=1
    labeled=tuple(tuple(per_pair.get((i,j),[0]*4)) for i in range(4) for j in range(i+1,4))
    return {"global_clause_sign_type_counts":tuple(global_types),"variable_pair_signed_profile_multiset":tuple(sorted(labeled)),"labeled_variable_pair_signed_profile":labeled}


def count_truth_table(formula: tuple[tuple[int,int], ...]) -> int:
    total=0
    for assignment in range(16):
        def val(lit:int)->bool:
            b=bool((assignment>>(abs(lit)-1))&1)
            return b if lit>0 else not b
        if all(val(a) or val(b) for a,b in formula): total+=1
    return total


def run_sat() -> dict[str,Any]:
    clauses=clause_universe(); assert len(clauses)==24
    table:dict[Hashable,Fibre]={}; records=[]; count=0
    for formula in itertools.combinations(clauses,5):
        count+=1; target=count_dpll(formula); records.append((formula,target))
        update(table,sat_feature(formula),target,{"clauses":[list(c) for c in formula]})
    feature,row=select_max(table)
    lo=tuple(tuple(c) for c in row.lo_witness['clauses']); hi=tuple(tuple(c) for c in row.hi_witness['clauses'])
    assert count_truth_table(lo)==row.lo; assert count_truth_table(hi)==row.hi
    candidates={name:(lambda f,name=name:sat_extras(f)[name]) for name in sat_extras(records[0][0])}
    return {"domain":"TWO_CNF_N4_M5","generator":{"method":"variable-pair/sign clause product with canonical literal-order ranking","clause_count":len(clauses)},
        "instance_count":count,"fibre_count":len(table),"maximum_fibre_diameter":row.diameter,"endpoint_values":[row.lo,row.hi],"fibre_multiplicity":row.count,
        "endpoint_witnesses":[row.lo_witness,row.hi_witness],"representation_feature":[list(feature[0]),list(feature[1])],
        "refinement_experiment":refinement(records,sat_feature,candidates,"global_clause_sign_type_counts"),"endpoint_third_checker":"complete truth-table enumeration"}


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=Path('FIBERGUARD_CLEANROOM_R8_RESULTS.json')); args=ap.parse_args()
    result={"schema":SCHEMA,"authority":{"clean_room_implementation":True,"independent_external_replay":False,"grants_novelty_or_journal_authority":False},"software":{"networkx_version":nx.__version__},"domains":[run_graph(),run_cover(),run_sat()]}
    result['content_sha256']=digest(result)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
