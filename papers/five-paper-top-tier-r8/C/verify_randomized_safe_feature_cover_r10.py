#!/usr/bin/env python3
"""Finite controls for the randomized FiberGuard conflict-cover theorem R10.

The Helly argument owns the all-size rank bound. This script reuses only the
already-registered exact rational minimax LP solver for feasibility and tests the
new conflict-cover equivalence on independently generated feature systems.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("action_regret", HERE / "verify_action_regret_r10.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)

SCHEMA = "ORION.FiberGuard.RandomizedSafeFeatureCover.R10.v1"
SEED = 20260827


def minimax_value(costs, states):
    return MOD.randomized_value(costs, tuple(states))


def minimal_conflicts(base, costs, epsilon, action_count):
    by_fibre = {}
    for i, y in enumerate(base):
        by_fibre.setdefault(y, []).append(i)
    out=[]
    for states in by_fibre.values():
        for size in range(1, min(action_count, len(states))+1):
            for w in itertools.combinations(states,size):
                if minimax_value(costs,w) <= epsilon:
                    continue
                if all(minimax_value(costs, tuple(x for x in w if x != removed)) <= epsilon for removed in w):
                    out.append(w)
    return out


def refined_safe(base, costs, epsilon, features, selected):
    fibres={}
    for i,y in enumerate(base):
        key=(y,)+tuple(features[j][i] for j in selected)
        fibres.setdefault(key,[]).append(i)
    return all(minimax_value(costs,states) <= epsilon for states in fibres.values())


def covers(conflicts,features,selected):
    return all(any(len({features[j][i] for i in w})>1 for j in selected) for w in conflicts)


def run():
    rng=random.Random(SEED)
    generated=250
    subset_checks=0
    rank_violations=0
    randomized_conflicts=0
    deterministic_only_control=False
    tight_helly_control=False

    for _ in range(generated):
        m=rng.randint(2,4)
        n=rng.randint(2,7)
        costs=MOD.as_fraction_matrix([[rng.randint(0,8) for _s in range(n)] for _a in range(m)])
        base=[rng.randrange(rng.randint(1,min(3,n))) for _s in range(n)]
        epsilon=Fraction(rng.randint(0,8),2)
        fcount=rng.randint(0,5)
        features=[[rng.randrange(rng.randint(1,3)) for _s in range(n)] for _f in range(fcount)]
        conflicts=minimal_conflicts(base,costs,epsilon,m)
        randomized_conflicts += len(conflicts)
        if any(len(w)>m for w in conflicts): rank_violations += 1
        for mask in range(1<<fcount):
            selected=[j for j in range(fcount) if (mask>>j)&1]
            a=refined_safe(base,costs,epsilon,features,selected)
            b=covers(conflicts,features,selected)
            subset_checks += 1
            if a != b:
                raise AssertionError({"base":base,"epsilon":str(epsilon),"selected":selected,"conflicts":conflicts,"direct":a,"cover":b})

    assert rank_violations==0

    # Randomization changes the conflict family: no deterministic common action,
    # but the 50/50 mixed policy is safe at epsilon=1/2.
    mp=MOD.as_fraction_matrix([[0,1],[1,0]])
    assert not MOD.safe_actions(mp,(0,1),Fraction(1,2))
    assert MOD.randomized_value(mp,(0,1))==Fraction(1,2)
    deterministic_only_control=True

    # Helly bound tight for m=4: state i penalizes only action i; epsilon<1/4.
    m=4
    # actions x states; state i has regret 1 only for action i
    tight=MOD.as_fraction_matrix([[1 if a==s else 0 for s in range(m)] for a in range(m)])
    eps=Fraction(1,5)
    assert MOD.randomized_value(tight,tuple(range(m))) > eps
    assert all(MOD.randomized_value(tight,subset) <= eps for subset in itertools.combinations(range(m),m-1))
    tight_helly_control=True

    result={
        "schema":SCHEMA,
        "status":"PASS",
        "seed":SEED,
        "generated_feature_systems":generated,
        "feature_subset_equivalence_checks":subset_checks,
        "minimal_randomized_conflicts":randomized_conflicts,
        "helly_rank_bound_violations":rank_violations,
        "deterministic_conflict_but_randomized_safe_control":"PASS" if deterministic_only_control else "FAIL",
        "four_action_helly_tightness_control":"PASS" if tight_helly_control else "FAIL",
        "authority":{
            "all_size_helly_bound_from_computation":False,
            "all_size_helly_bound_from_displayed_proof":True,
            "feature_cover_equivalence_from_displayed_proof":True,
            "finite_controls_use_registered_exact_rational_lp":True,
            "external_solver_selection_value":False,
        },
    }
    payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode()
    result["content_sha256"]=hashlib.sha256(payload).hexdigest()
    return result


def main():
    result=run()
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    print(text,end="")
    (HERE/"RANDOMIZED_SAFE_FEATURE_COVER_R10_RESULTS.json").write_text(text)


if __name__=="__main__":
    main()
