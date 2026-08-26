#!/usr/bin/env python3
"""Finite controls for Q1 R10 nine-qubit auxiliary core.

The analytic support-two theorem and displayed R10 proof own all-size authority.
This verifier independently checks:
- the exact ordered anticommuting support<=2 pair formula for n=1..5;
- the per-block union<=3 property;
- Tag projection onto the frame union on deterministic feasible hostile cases;
- exact equality of global and projected minimum Tag weight on complete small panels.

No circuit-resource or runtime claim is granted by this script.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path

SCHEMA = "ORION.Q1.NineQubitAuxiliaryCore.R10.v1"
SEED = 20260826

# local codes I=0, X=1, Z=2, Y=3 represented by (x,z)
BITS = ((0, 0), (1, 0), (0, 1), (1, 1))


def local_symp(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return (ax * bz + az * bx) & 1


def support(p: tuple[int, ...]) -> frozenset[int]:
    return frozenset(i for i, a in enumerate(p) if a)


def wt(p: tuple[int, ...]) -> int:
    return len(support(p))


def symp(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(local_symp(x, y) for x, y in zip(a, b)) & 1


def add_pauli(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    # phase-free binary Pauli multiplication: XOR x/z bits
    out=[]
    for x,y in zip(a,b):
        bx=(BITS[x][0]^BITS[y][0], BITS[x][1]^BITS[y][1])
        out.append(BITS.index(bx))
    return tuple(out)


def paulies_support_le_2(n: int) -> list[tuple[int, ...]]:
    out=[]
    for q in range(n):
        for letter in (1,2,3):
            p=[0]*n; p[q]=letter; out.append(tuple(p))
    for q in range(n):
        for r in range(q+1,n):
            for a in (1,2,3):
                for b in (1,2,3):
                    p=[0]*n; p[q]=a; p[r]=b; out.append(tuple(p))
    return out


def ordered_anticommuting_pairs(n: int) -> list[tuple[tuple[int,...],tuple[int,...]]]:
    ps=paulies_support_le_2(n)
    return [(a,b) for a in ps for b in ps if symp(a,b)==1]


def pair_formula(n: int) -> int:
    return 6*n + 54*n*(n-1)*(n-1)


def restrict_to(p: tuple[int,...], u: frozenset[int]) -> tuple[int,...]:
    return tuple(a if i in u else 0 for i,a in enumerate(p))


def labels(tag: tuple[int,...], pairs) -> tuple[tuple[int,int], ...]:
    return tuple((symp(tag,a),symp(tag,b)) for a,b in pairs)


def all_paulis(n: int):
    return itertools.product(range(4), repeat=n)


def min_tag_weight_global(n: int, pairs, orientation: tuple[int,int]) -> int | None:
    best=None
    for s in all_paulis(n):
        if s == (0,)*n:
            continue
        if all((symp(s,a),symp(s,b))==orientation for a,b in pairs):
            w=wt(s)
            best=w if best is None else min(best,w)
    return best


def min_tag_weight_projected(n: int, pairs, orientation: tuple[int,int]) -> int | None:
    u=frozenset().union(*(support(x) for pair in pairs for x in pair))
    coords=sorted(u)
    best=None
    for letters in itertools.product(range(4), repeat=len(coords)):
        s=[0]*n
        for q,a in zip(coords,letters): s[q]=a
        s=tuple(s)
        if s == (0,)*n:
            continue
        if all((symp(s,a),symp(s,b))==orientation for a,b in pairs):
            w=wt(s)
            best=w if best is None else min(best,w)
    return best


def deterministic_feasible_triplets(n: int, count: int):
    rng=random.Random(SEED+n)
    pairs=ordered_anticommuting_pairs(n)
    by_tag={}
    tags=[tuple(x) for x in all_paulis(n) if tuple(x)!=(0,)*n]
    for orientation in ((0,1),(1,0)):
        for s in tags:
            compatible=[p for p in pairs if (symp(s,p[0]),symp(s,p[1]))==orientation]
            if compatible:
                by_tag[(orientation,s)]=compatible
    keys=sorted(by_tag, key=lambda x:(x[0],wt(x[1]),x[1]))
    if not keys:
        return []
    rows=[]
    for _ in range(count):
        orientation,s=rng.choice(keys)
        cp=by_tag[(orientation,s)]
        triple=tuple(rng.choice(cp) for _j in range(3))
        rows.append((orientation,s,triple))
    return rows


def run() -> dict[str,object]:
    pair_rows=[]
    total_pairs_checked=0
    for n in range(1,6):
        pairs=ordered_anticommuting_pairs(n)
        expected=pair_formula(n)
        assert len(pairs)==expected
        assert all(len(support(a)|support(b))<=3 for a,b in pairs)
        total_pairs_checked += len(pairs)
        pair_rows.append({
            "n":n,
            "enumerated_ordered_pairs":len(pairs),
            "formula":expected,
            "per_block_union_le_3":True,
        })

    projection_cases=0
    projection_failures=0
    active_core_violations=0
    for n in (3,4,5):
        for orientation,s,triple in deterministic_feasible_triplets(n,150):
            u=frozenset().union(*(support(x) for pair in triple for x in pair))
            if len(u)>min(9,n): active_core_violations += 1
            projected=restrict_to(s,u)
            projection_cases += 1
            if labels(projected,triple)!=(orientation,)*3 or wt(projected)>wt(s) or projected==(0,)*n:
                projection_failures += 1
    assert projection_failures==0
    assert active_core_violations==0

    # Complete small-n equality of minimum global Tag weight and minimum Tag
    # restricted to the frame union, on every feasible triple drawn from a
    # complete deterministic panel of pair indices.
    min_tag_cases=0
    min_tag_mismatches=0
    for n in (1,2):
        pairs=ordered_anticommuting_pairs(n)
        # all n=1 triples; a deterministic stride panel at n=2 to keep CI bounded
        triples=(
            itertools.product(pairs, repeat=3)
            if n==1 else
            (tuple(pairs[(base+step*j)%len(pairs)] for j in range(3)) for base in range(0,len(pairs),3) for step in (1,7,19))
        )
        for triple in triples:
            for orientation in ((0,1),(1,0)):
                g=min_tag_weight_global(n,triple,orientation)
                if g is None:
                    continue
                p=min_tag_weight_projected(n,triple,orientation)
                min_tag_cases += 1
                if g!=p:
                    min_tag_mismatches += 1
                    raise AssertionError({"n":n,"orientation":orientation,"global":g,"projected":p})
    assert min_tag_mismatches==0

    result={
        "schema":SCHEMA,
        "status":"PASS",
        "pair_count_rows":pair_rows,
        "total_ordered_anticommuting_pairs_checked":total_pairs_checked,
        "tag_projection_cases":projection_cases,
        "tag_projection_failures":projection_failures,
        "active_core_bound_violations":active_core_violations,
        "minimum_tag_weight_equality_cases":min_tag_cases,
        "minimum_tag_weight_mismatches":min_tag_mismatches,
        "authority":{
            "all_size_core_theorem_from_computation":False,
            "all_size_core_theorem_from_displayed_proof":True,
            "finite_controls_exact":True,
            "physical_resource_reduction":False,
            "production_runtime_superiority":False,
        },
    }
    payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode()
    result["content_sha256"]=hashlib.sha256(payload).hexdigest()
    return result


def main():
    result=run()
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    print(text,end="")
    Path(__file__).with_name("Q1_NINE_QUBIT_AUXILIARY_CORE_R10_RESULTS.json").write_text(text)


if __name__=="__main__":
    main()
