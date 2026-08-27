#!/usr/bin/env python3
"""Independent finite corroboration for the ORION-02 R20 theorem story."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path
from typing import Iterable

SCHEMA='ORION.ORION02.R20StoryVerifier.v1'
TERMINAL='ORION02_R20_STORY_FINITE_CORROBORATION_PASS'
SEED=20260827


def canonical(value:object)->str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def det_value(profiles:tuple[tuple[int,...],...])->int:
    return min(max(row) for row in profiles)


def witness(profiles:tuple[tuple[int,...],...])->tuple[int,...]:
    state_count=len(profiles[0]);states=set()
    for row in profiles:
        maximum=max(row)
        states.add(next(index for index in range(state_count) if row[index]==maximum))
    return tuple(sorted(states))


def restricted(profiles:tuple[tuple[int,...],...],states:Iterable[int])->tuple[tuple[int,...],...]:
    ordered=tuple(states)
    return tuple(tuple(row[index] for index in ordered) for row in profiles)


def verify_witnesses()->dict[str,int]:
    rng=random.Random(SEED);systems=1000;compressed=0
    for _ in range(systems):
        actions=rng.randint(2,6);states=rng.randint(2,12)
        profiles=tuple(tuple(rng.randrange(30) for _ in range(states)) for _ in range(actions))
        selected=witness(profiles)
        if len(selected)>actions or det_value(profiles)!=det_value(restricted(profiles,selected)):
            raise AssertionError('witness compression disagreement')
        compressed+=states-len(selected)
    return {'systems':systems,'states_removed':compressed}


def verify_no_free_extension()->dict[str,int]:
    cases=0
    for observed_actions in range(2,7):
        for observed_states in range(1,8):
            base=tuple(tuple((action+state)%5 for state in range(observed_states)) for action in range(observed_actions))
            for target in range(1,21):
                # Add one unseen state for each action, making every common action
                # pay target somewhere while one alternative is oracle-optimal.
                extended=[]
                for action,row in enumerate(base):
                    suffix=tuple(0 if action==hidden else target for hidden in range(observed_actions))
                    extended.append(row+suffix)
                if det_value(tuple(extended))<target:
                    raise AssertionError('no-free extension construction failed')
                if any(extended[a][:observed_states]!=base[a] for a in range(observed_actions)):
                    raise AssertionError('observed subject changed')
                cases+=1
    return {'extensions':cases,'maximum_forced_regret':20}


def verify_fallback_identity()->dict[str,int]:
    cases=0;improve=worsen=tie=0
    for states in range(1,5):
        values=range(4)
        for learned in itertools.product(values,repeat=states):
            for fallback in itertools.product(values,repeat=states):
                for route in itertools.product((0,1),repeat=states):
                    deployed=tuple(learned[i]+route[i]*(fallback[i]-learned[i]) for i in range(states))
                    direct=tuple(fallback[i] if route[i] else learned[i] for i in range(states))
                    if deployed!=direct:raise AssertionError('fallback identity disagreement')
                    delta=sum(deployed)-sum(learned)
                    if delta<0:improve+=1
                    elif delta>0:worsen+=1
                    else:tie+=1
                    cases+=1
    return {'cases':cases,'improving':improve,'worsening':worsen,'ties':tie}


def randomized_two_profile_value(a:tuple[int,int],b:tuple[int,int])->Fraction:
    # min_{p in [0,1]} max(p*a+(1-p)*b), exact candidate endpoints/intersection.
    candidates={Fraction(0),Fraction(1)}
    denominator=(a[0]-b[0])-(a[1]-b[1])
    if denominator:
        p=Fraction(b[1]-b[0],denominator)
        if 0<=p<=1:candidates.add(p)
    return min(max(p*a[0]+(1-p)*b[0],p*a[1]+(1-p)*b[1]) for p in candidates)


def verify_joint_nonidentifiability()->dict[str,str]:
    # Same arm marginals {(0,100),(100,0)}. Full compatibility permits
    # cross-coordinate legal route (0,0); diagonal compatibility does not.
    full_profiles=((0,0),(0,100),(100,0),(100,100))
    diagonal_profiles=((0,100),(100,0))
    full_det=det_value(full_profiles);diag_det=det_value(diagonal_profiles)
    full_rand=Fraction(0);diag_rand=randomized_two_profile_value(*diagonal_profiles)
    if (full_det,diag_det,full_rand,diag_rand)!=(0,100,Fraction(0),Fraction(50)):
        raise AssertionError('joint nonidentifiability control drift')
    return {'full_deterministic':'0','diagonal_deterministic':'100','full_randomized':'0','diagonal_randomized':'50'}


def upper_closed_dominated(profile:tuple[int,int],profiles:tuple[tuple[int,int],...])->bool:
    return any(row[0]<=profile[0] and row[1]<=profile[1] for row in profiles)


def pareto(profiles:Iterable[tuple[int,int]])->tuple[tuple[int,int],...]:
    rows=tuple(sorted(set(profiles)))
    return tuple(row for row in rows if not any(other!=row and other[0]<=row[0] and other[1]<=row[1] for other in rows))


def verify_lower_images()->dict[str,int]:
    # Integer-grid finite control: equal Pareto lower boundaries yield identical
    # minima for every registered nonnegative linear monotone objective.
    points=tuple(itertools.product(range(4),repeat=2));families=[]
    for mask in range(1,1<<len(points)):
        if mask.bit_count()>3:continue
        families.append(tuple(points[i] for i in range(len(points)) if (mask>>i)&1))
    weights=tuple((a,b) for a in range(4) for b in range(4) if a+b>0)
    comparisons=0
    for left in families:
        for right in families:
            same=pareto(left)==pareto(right)
            equal_all=all(min(a*x+b*y for x,y in left)==min(a*x+b*y for x,y in right) for a,b in weights)
            # On this bounded grid, the chosen weight menu may fail to separate
            # every distinct lower image; only the forward implication is load-bearing.
            if same and not equal_all:raise AssertionError('lower-image forward implication failed')
            comparisons+=1
    return {'families':len(families),'ordered_comparisons':comparisons,'monotone_linear_objectives':len(weights)}


def verify_r18_custody(root:Path)->dict[str,object]:
    custody=json.loads((root/'extensions/r18/R18_RECOVERY_CUSTODY.json').read_text())
    if custody['former_positive_terminal']!='RETRACTED' or custody['current_terminal']!='FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE':
        raise AssertionError('R18 custody drift')
    if custody['scientific_result']['development_feasible_candidates']!=0:
        raise AssertionError('R18 null denominator drift')
    if any(value!=0.0 for value in custody['scientific_result']['route_coverage'].values()):
        raise AssertionError('R18 route coverage drift')
    return {'candidate_denominator':custody['recovery']['candidate_denominator'],'former_positive_terminal':custody['former_positive_terminal'],'current_terminal':custody['current_terminal']}


def build(root:Path)->dict[str,object]:
    return {'schema':SCHEMA,'terminal':TERMINAL,'seed':SEED,'deterministic_witnesses':verify_witnesses(),'no_free_extension':verify_no_free_extension(),'fallback_alignment':verify_fallback_identity(),'joint_nonidentifiability':verify_joint_nonidentifiability(),'lower_image_controls':verify_lower_images(),'r18_custody':verify_r18_custody(root),'authority':{'analytic_proofs_carried_by_manuscript':True,'finite_verification':'IMPLEMENTATION_CORROBORATION_ONLY','external_independence':False,'novelty':False,'journal_authority':False}}


def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parent
    result=build(root);payload=canonical(result)+'\n';args.output.write_text(payload)
    print(TERMINAL,'sha256='+hashlib.sha256(payload.encode()).hexdigest());return 0
if __name__=='__main__':raise SystemExit(main())
