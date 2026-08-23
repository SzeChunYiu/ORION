#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import heapq
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QG = REPO / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG))

import qg15_third_family as qg15  # noqa: E402
import qg15b_predicate_language as qg15b  # noqa: E402

ARTIFACTS = REPO / "artifacts"
SELECTION = ARTIFACTS / "orion-qg-qg20-recovery-v5-n5-selection.json"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v5-n5.json"
OUT = ARTIFACTS / "orion-qg-qg20-recovery-v5-n5-verification.json"
PREFIX = "ORIONQG_QG20_RECOVERY_V5_N5_VERIFY="
N=5; SEED=2026082305; WALK_LENGTH=14; POOL_CAP=100_000; GROUPS_REQUIRED=32; STATES_PER_GROUP=2
TRIPLES=tuple((a,b,c) for a in range(N+1) for b in range(N+1) for c in range(N+1) if 1 <= a+b+c <= N)


def canon(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def complete_direct(state):
    mask=(1<<N)-1; coeff={t:0 for t in TRIPLES}
    for raw in state:
        z=raw&mask; x=(raw>>N)&mask
        t=((x&~z&mask).bit_count(), (x&z).bit_count(), (z&~x&mask).bit_count())
        if t != (0,0,0): coeff[t] += -1 if raw>>(2*N) else 1
    return tuple(coeff[t] for t in TRIPLES)


def rep_key(state):
    _prep, cd, feats, _gates=qg15.donor(state,N)
    lb,rx,c=qg15.lower_bound(state,N)
    base=(feats['nCZ'],feats['nY'],feats['nSignX'],feats['nSignZ'],feats['nCN'],cd,rx,c,lb,cd-lb,N-c,feats['nCN']-(N-1),cd-2*N)
    return base+complete_direct(state), cd


def rebuild_selection():
    gates=qg15.make_ctx(N)['gates']; rng=random.Random(SEED); seen=set(); groups=defaultdict(list); costs={}; stop=0
    for index in range(1,POOL_CAP+1):
        state=qg15.start_state(N)
        for _ in range(WALK_LENGTH): state=qg15.apply_state(state,rng.choice(gates),N)
        if state in seen: continue
        seen.add(state); key,cd=rep_key(state); groups[key].append(state); costs[state]=cd; stop=index
        if sum(len(v)>=2 for v in groups.values()) >= GROUPS_REQUIRED: break
    keys=[k for k,v in groups.items() if len(v)>=2]
    keys.sort(key=lambda k: canon(list(k)))
    chosen=keys[:GROUPS_REQUIRED]
    selected=[]; targets=[]
    for key in chosen:
        states=sorted(groups[key])[:2]; targets.extend(states)
        selected.append({
            'representation_key_sha256': hashlib.sha256(canon(list(key)).encode()).hexdigest(),
            'state_digests':[hashlib.sha256(canon(list(s)).encode()).hexdigest() for s in states],
            'states':[list(s) for s in states],
            'donor_costs':[costs[s] for s in states],
        })
    return tuple(targets), {'pool_unique_states':len(seen),'stream_stop_index':stop,'collision_groups_available':len(keys),'selected_groups':selected}


def exact_targets(targets):
    target_set=set(targets); gates=qg15.make_ctx(N)['gates']; start=qg15.start_state(N)
    dist={start:0}; heap=[(0,start)]; settled={}; popped=0
    while heap and len(settled)<len(target_set):
        d,state=heapq.heappop(heap)
        if dist.get(state)!=d: continue
        popped+=1
        if state in target_set: settled[state]=d
        for gate in gates:
            nxt=qg15.apply_state(state,gate,N); nd=d+qg15.COST[gate[0]]
            old=dist.get(nxt)
            if old is None or nd<old:
                dist[nxt]=nd; heapq.heappush(heap,(nd,nxt))
    return settled, {'settled_state_count':popped,'discovered_state_count':len(dist),'targets_settled':len(settled),'max_settled_target_cost':max(settled.values(),default=None)}


def main():
    sel=json.loads(SELECTION.read_text()); result=json.loads(RESULT.read_text())
    targets, rebuilt_pre=rebuild_selection()
    selection_checks={
        'selection_constants': sel.get('n')==N and sel.get('seed')==SEED and sel.get('walk_length')==WALK_LENGTH and sel.get('pool_cap')==POOL_CAP,
        'coefficient_triples': sel.get('coefficient_triples')==[list(t) for t in TRIPLES],
        'pool_counts': sel.get('pool_unique_states')==rebuilt_pre['pool_unique_states'] and sel.get('stream_stop_index')==rebuilt_pre['stream_stop_index'],
        'selected_groups_identical': sel.get('selected_groups')==rebuilt_pre['selected_groups'],
        'labels_sealed': sel.get('exact_labels_accessed') is False,
    }
    if not all(selection_checks.values()):
        exact={}; search={}; group_results=[]; mixed=floor=exact_count=inexact_count=0
    else:
        exact,search=exact_targets(targets); group_results=[]; mixed=floor=exact_count=inexact_count=0
        for group in rebuilt_pre['selected_groups']:
            states=[tuple(s) for s in group['states']]; labels=[]; exact_costs=[]
            for state,cd in zip(states,group['donor_costs'],strict=True):
                opt=exact[state]; label=cd==opt; labels.append(label); exact_costs.append(opt); exact_count+=int(label); inexact_count+=int(not label)
            pos=sum(labels); neg=len(labels)-pos; mixed+=int(pos>0 and neg>0); floor+=min(pos,neg)
            group_results.append({'representation_key_sha256':group['representation_key_sha256'],'state_digests':group['state_digests'],'donor_costs':group['donor_costs'],'exact_costs':exact_costs,'labels':labels})
    checks={**selection_checks,
        'all_targets_settled': len(exact)==len(set(targets)) if targets else False,
        'search_stats_agree': search==result.get('search'),
        'label_counts_agree': exact_count==result.get('exact_label_count') and inexact_count==result.get('inexact_label_count'),
        'mixed_floor_agree': mixed==result.get('mixed_groups') and floor==result.get('error_floor'),
        'group_results_agree': group_results==result.get('group_results'),
        'independent_pool_and_dijkstra': True,
    }
    decision='ACCEPT' if all(checks.values()) else 'REJECT'
    payload={'schema':'orion-qg.qg20_recovery_v5_n5_verify.v1','decision':decision,'checks':checks,'source_result_digest':result.get('result_digest'),'rebuilt_search':search,'exact_label_count':exact_count,'inexact_label_count':inexact_count,'mixed_groups':mixed,'error_floor':floor}
    payload['verification_digest']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(PREFIX+json.dumps(payload,sort_keys=True,separators=(",", ":")))
    return 0 if decision=='ACCEPT' else 2

if __name__=='__main__': raise SystemExit(main())
