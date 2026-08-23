#!/usr/bin/env python3
"""Independent P12 procedural allocation verifier using heap-based Dijkstra."""
from __future__ import annotations
import hashlib, heapq, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=HERE/"p12_procedural_path_cases_v1.json"
PROTOCOL=HERE/"P12_PROCEDURAL_PATH_ALLOCATION_PROTOCOL_V1.md"
N=15
DIRS=((0,1),(1,0),(0,-1),(-1,0))  # deliberately different order from primary

def walls(pattern):
    if pattern=="OPEN": return set()
    if pattern=="CENTER_GATE": return {(7,y) for y in range(N) if y!=7}
    if pattern=="DOUBLE_GATE": return {(5,y) for y in range(N) if y!=3}|{(10,y) for y in range(N) if y!=11}
    if pattern=="HORIZONTAL_GATE": return {(x,8) for x in range(N) if x!=4}
    raise ValueError(pattern)

def nbrs(p,w):
    x,y=p
    for dx,dy in DIRS:
        q=(x+dx,y+dy)
        if 0<=q[0]<N and 0<=q[1]<N and q not in w:
            yield q

def dijkstra(start,goal,w):
    pq=[(0,start)]; dist={start:0}; expansions=0
    while pq:
        d,p=heapq.heappop(pq)
        if d!=dist[p]: continue
        expansions+=1
        if p==goal: return d,expansions
        for q in nbrs(p,w):
            nd=d+1
            if nd<dist.get(q,10**9):
                dist[q]=nd; heapq.heappush(pq,(nd,q))
    raise AssertionError((start,goal))

def reverse_all(goal,w):
    pq=[(0,goal)]; dist={goal:0}; expansions=0
    while pq:
        d,p=heapq.heappop(pq)
        if d!=dist[p]: continue
        expansions+=1
        for q in nbrs(p,w):
            nd=d+1
            if nd<dist.get(q,10**9):
                dist[q]=nd; heapq.heappush(pq,(nd,q))
    return dist,expansions

def main():
    spec=json.loads(CASES.read_text())
    rows=[]; correct=0
    for case in spec['cases']:
        w=walls(case['pattern']); goal=tuple(case['goal']); starts=[tuple(s) for s in case['starts']]
        reverse, state_expansions=reverse_all(goal,w)
        assert all(s in reverse for s in starts)
        reason_expansions=0
        distances=[]
        for s in starts:
            d,e=dijkstra(s,goal,w); reason_expansions+=e; distances.append(d)
            assert d==reverse[s]
        oracle='STATE_FIRST' if state_expansions<reason_expansions else 'REASON_ONLY'
        adaptive='STATE_FIRST' if len(starts)>=4 else 'REASON_ONLY'
        correct+=int(oracle==adaptive)
        rows.append({
            'id':case['id'],'pattern':case['pattern'],'query_count':len(starts),
            'reason_dijkstra_expansions':reason_expansions,
            'state_reverse_dijkstra_expansions':state_expansions,
            'oracle':oracle,'adaptive':adaptive,'shortest_distances':distances,
        })
    assert correct==len(rows)==8, rows
    assert all(r['oracle']=='REASON_ONLY' for r in rows if r['query_count']<4)
    assert all(r['oracle']=='STATE_FIRST' for r in rows if r['query_count']>=4)
    receipt={
        'schema':'P12.ProceduralPathAllocationIndependent.v1',
        'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        'cases_sha256':hashlib.sha256(CASES.read_bytes()).hexdigest(),
        'case_count':len(rows),'adaptive_oracle_agreement':correct/len(rows),'rows':rows,
        'terminal':'P12_PROCEDURAL_PATH_ALLOCATION_SECOND_INDEPENDENT_CHECKER_GREEN',
    }
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt,indent=2,sort_keys=True));return 0
if __name__=='__main__': raise SystemExit(main())
