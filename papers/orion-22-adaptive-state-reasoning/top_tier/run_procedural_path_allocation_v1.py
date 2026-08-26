#!/usr/bin/env python3
from __future__ import annotations
from collections import deque
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; CASES=HERE/"p12_procedural_path_cases_v1.json"; PROTOCOL=HERE/"P12_PROCEDURAL_PATH_ALLOCATION_PROTOCOL_V1.md"
N=15; BUDGET=500
DIRS=((1,0),(-1,0),(0,1),(0,-1))
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
        if 0<=q[0]<N and 0<=q[1]<N and q not in w: yield q
def bfs_path(start,goal,w):
    q=deque([start]); prev={start:None}; expansions=0
    while q:
        p=q.popleft(); expansions+=1
        if p==goal: break
        for z in nbrs(p,w):
            if z not in prev: prev[z]=p; q.append(z)
    if goal not in prev: return None,expansions
    path=[]; p=goal
    while p is not None: path.append(p); p=prev[p]
    return list(reversed(path)),expansions
def reverse_state(goal,w):
    q=deque([goal]); dist={goal:0}; expansions=0
    while q:
        p=q.popleft(); expansions+=1
        for z in nbrs(p,w):
            if z not in dist: dist[z]=dist[p]+1; q.append(z)
    return dist,expansions
def state_path(start,goal,w,dist):
    if start not in dist:return None
    path=[start]; p=start
    while p!=goal:
        options=[z for z in nbrs(p,w) if z in dist and dist[z]==dist[p]-1]
        if not options:return None
        p=min(options); path.append(p)
    return path
def independent_distance(start,goal,w):
    q=deque([(start,0)]); seen={start}; checks=0
    while q:
        p,d=q.popleft()
        if p==goal:return d,checks
        for z in nbrs(p,w):
            checks+=1
            if z not in seen: seen.add(z); q.append((z,d+1))
    return None,checks
def verify(path,start,goal,w):
    d,checks=independent_distance(start,goal,w); assert d is not None
    if path is None:return False,checks
    ok=path[0]==start and path[-1]==goal and len(path)-1==d
    for a,b in zip(path,path[1:]):
        checks+=1
        ok=ok and b in set(nbrs(a,w)) and b not in w
    return ok,checks
def run_arm(case,arm):
    w=walls(case["pattern"]); goal=tuple(case["goal"]); starts=[tuple(x) for x in case["starts"]]
    assert goal not in w and all(s not in w for s in starts)
    sc=qs=mat=edges=checks=0; valid=0
    if arm=="STATE_FIRST":
        dist,sc=reverse_state(goal,w); mat=len(dist)
        paths=[state_path(s,goal,w,dist) for s in starts]
    else:
        paths=[]
        for s in starts:
            p,e=bfs_path(s,goal,w); qs+=e; paths.append(p)
    for s,p in zip(starts,paths):
        ok,c=verify(p,s,goal,w); checks+=c; valid+=int(ok); edges+=0 if p is None else len(p)-1
    total=sc+qs
    return {"arm":arm,"valid_paths":valid,"query_count":len(starts),"state_construction_expansions":sc,"query_search_expansions":qs,"total_expansions":total,"materialized_distance_cells":mat,"path_output_edges":edges,"verification_edge_checks":checks,"budget_exhausted":total>BUDGET}
def main():
    spec=json.loads(CASES.read_text()); rows=[]; selections=[]
    for case in spec["cases"]:
        reason=run_arm(case,"REASON_ONLY"); state=run_arm(case,"STATE_FIRST")
        oracle="STATE_FIRST" if state["total_expansions"]<reason["total_expansions"] else "REASON_ONLY"
        adaptive="STATE_FIRST" if len(case["starts"])>=4 else "REASON_ONLY"
        selected=state if adaptive=="STATE_FIRST" else reason
        selections.append({"id":case["id"],"pattern":case["pattern"],"query_count":len(case["starts"]),"oracle":oracle,"adaptive":adaptive,"regret":selected["total_expansions"]-min(reason["total_expansions"],state["total_expansions"])})
        rows += [{"id":case["id"],**reason},{"id":case["id"],**state},{"id":case["id"],**{**selected,"arm":"ADAPTIVE_LOCATION"}}]
    agg={}
    for arm in ("REASON_ONLY","STATE_FIRST","ADAPTIVE_LOCATION"):
        xs=[r for r in rows if r["arm"]==arm]; agg[arm]={"total_expansions":sum(r["total_expansions"] for r in xs),"budget_exhaustions":sum(r["budget_exhausted"] for r in xs),"verified_paths":sum(r["valid_paths"] for r in xs)}
    correct=sum(s["oracle"]==s["adaptive"] for s in selections); low_overhead=any(s["query_count"]<4 and s["oracle"]=="REASON_ONLY" for s in selections); high_benefit=any(s["query_count"]>=4 and s["oracle"]=="STATE_FIRST" for s in selections)
    positive=(all(r["valid_paths"]==r["query_count"] for r in rows) and correct>=7 and agg["ADAPTIVE_LOCATION"]["total_expansions"]<agg["REASON_ONLY"]["total_expansions"] and agg["ADAPTIVE_LOCATION"]["total_expansions"]<agg["STATE_FIRST"]["total_expansions"] and low_overhead and high_benefit and agg["ADAPTIVE_LOCATION"]["budget_exhaustions"]<=min(agg["REASON_ONLY"]["budget_exhaustions"],agg["STATE_FIRST"]["budget_exhaustions"]))
    receipt={"schema":"P12.ProceduralPathAllocationResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"cases_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),"case_count":len(spec["cases"]),"adaptive_oracle_agreement":correct/len(selections),"selections":selections,"aggregate":agg,"rows":rows,"terminal":"P12_PROCEDURAL_PATH_ALLOCATION_V1_SUPPORTED" if positive else "P12_PROCEDURAL_PATH_ALLOCATION_V1_GATE_NOT_MET"}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode(); receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest(); print(json.dumps(receipt,indent=2,sort_keys=True)); assert positive,receipt;return 0
if __name__=="__main__":raise SystemExit(main())
