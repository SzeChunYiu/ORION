#!/usr/bin/env python3
"""Exhaustive finite controls for universal origin-erasure safety R10.

On three claims, enumerate every program formed from all unary and genuine
binary nonempty-body Horn rules whose head is outside the body. Compare:

- semantic preservation of binary unions for every pair of seed sets; and
- the rule-local singleton-closure criterion in Theorem D-R10.2.

The generic all-size closure equivalence is analytic/contextual; this is an
implementation and hostile-counterexample audit only.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

SCHEMA="ORION.TypedAuthority.UniversalOriginErasureSafety.R10.v1"
Q=tuple(range(3))

RULES=[]
for head in Q:
    others=[q for q in Q if q != head]
    for size in (1,2):
        for body in itertools.combinations(others,size):
            RULES.append((body,head))
assert len(RULES)==9


def closure(program_mask,seeds):
    reached=set(seeds)
    changed=True
    while changed:
        changed=False
        for idx,(body,head) in enumerate(RULES):
            if (program_mask>>idx)&1 and set(body)<=reached and head not in reached:
                reached.add(head); changed=True
    return frozenset(reached)


def semantic_union_safe(program_mask):
    seedsets=[]
    for mask in range(1<<len(Q)):
        seedsets.append(frozenset(q for q in Q if (mask>>q)&1))
    cl={s:closure(program_mask,s) for s in seedsets}
    for s in seedsets:
        for t in seedsets:
            if cl[s|t] != cl[s] | cl[t]:
                return False,(s,t,cl[s],cl[t],cl[s|t])
    return True,None


def local_criterion(program_mask):
    singleton={q:closure(program_mask,{q}) for q in Q}
    for idx,(body,head) in enumerate(RULES):
        if not ((program_mask>>idx)&1):
            continue
        if not any(head in singleton[b] for b in body):
            return False,{"rule_index":idx,"body":list(body),"head":head,"singleton_closures":{str(b):sorted(singleton[b]) for b in body}}
    return True,None


def run():
    programs=1<<len(RULES)
    safe=0; unsafe=0; mismatches=0
    first_unsafe=None
    for p in range(programs):
        sem,sem_w=semantic_union_safe(p)
        loc,loc_w=local_criterion(p)
        if sem!=loc:
            mismatches += 1
            raise AssertionError({"program":p,"semantic":sem,"local":loc,"semantic_witness":sem_w,"local_witness":loc_w})
        if sem:
            safe += 1
        else:
            unsafe += 1
            if first_unsafe is None:
                first_unsafe={
                    "program_mask":p,
                    "rules":[{"body":list(b),"head":h} for i,(b,h) in enumerate(RULES) if (p>>i)&1],
                    "semantic_witness": [sorted(x) if isinstance(x,frozenset) else x for x in sem_w],
                    "local_violating_rule":loc_w,
                }
    assert safe+unsafe==programs
    assert mismatches==0

    # Explicit one genuinely conjunctive rule: {0,1}->2 must be unsafe.
    idx=RULES.index(((0,1),2))
    sem,_=semantic_union_safe(1<<idx)
    loc,_=local_criterion(1<<idx)
    assert sem is False and loc is False

    # Same conjunctive syntax can become semantically harmless if 0->2 is also
    # present; the test must inspect closure, not syntax alone.
    idx_u=RULES.index(((0,),2))
    sem,_=semantic_union_safe((1<<idx)|(1<<idx_u))
    loc,_=local_criterion((1<<idx)|(1<<idx_u))
    assert sem is True and loc is True

    result={
        "schema":SCHEMA,
        "status":"PASS",
        "claims":len(Q),
        "rule_schemas":len(RULES),
        "programs_exhausted":programs,
        "universally_safe_programs":safe,
        "unsafe_programs":unsafe,
        "semantic_local_criterion_mismatches":mismatches,
        "genuine_conjunction_unsafe_control":"PASS",
        "syntactic_conjunction_semantically_harmless_control":"PASS",
        "first_unsafe":first_unsafe,
        "authority":{
            "all_size_equivalence_from_computation":False,
            "all_size_equivalence_from_displayed_proof":True,
            "finite_controls_exact":True,
            "generic_closure_theory_novelty":False,
            "external_policy_value":False,
        },
    }
    payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode()
    result["content_sha256"]=hashlib.sha256(payload).hexdigest()
    return result


def main():
    result=run()
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    print(text,end="")
    Path(__file__).with_name("UNIVERSAL_ORIGIN_ERASURE_SAFETY_R10_RESULTS.json").write_text(text)


if __name__=="__main__":
    main()
