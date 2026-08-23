#!/usr/bin/env python3
"""P12 transfer study — independent second checker V1.

Deliberately different algorithm classes from the runner:
  SAT  : full-rescan fixpoint UP (runner truth uses occurrence-queue UP).
  PATH : bidirectional BFS distance (runner truth uses reverse-BFS table).
  KNAP : exhaustive 2^n enumeration (runner truth uses full-table DP).

Independently re-derives the frozen allocator decision (own implementation of
tau=4, greedy-by-q, cumulative<=B) and every arm's regret from the case file
alone, then cross-checks against the runner's emitted result JSON on stdin's
path (default ./p12_transfer_allocation_v1.json in this directory).

Terminal: P12_TRANSFER_ALLOCATION_SECOND_INDEPENDENT_CHECKER_GREEN
"""
import json
import os
import sys
from collections import deque

TAU = 4
BUDGET = 500
ALLOC = "P12_TRANSFER_ALLOCATOR_V1"


# ---------------------------------------------------- independent SAT engine

def sat_rescan_up(cnf, assumptions):
    assign = {}
    for lit in assumptions:
        assign[abs(lit)] = lit > 0
    while True:
        changed = False
        for clause in cnf:
            status = []
            for lit in clause:
                v = abs(lit)
                status.append("T" if v in assign and (lit > 0) == assign[v]
                              else ("F" if v in assign else "U"))
            if "T" in status:
                continue
            if "U" not in status:
                return None
            if status.count("U") == 1:
                lit = clause[status.index("U")]
                assign[abs(lit)] = lit > 0
                changed = True
        if not changed:
            break
    return sorted((v if assign[v] else -v) for v in assign)


# ---------------------------------------------------- independent PATH engine

def path_bidir_distance(grid, start, goal):
    if start == goal:
        return 0
    def neigh(cell):
        x, y = cell
        res = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 15 and 0 <= ny < 15 and grid[ny][nx] == 0:
                res.append((nx, ny))
        return res
    df = {start: 0}
    db = {goal: 0}
    qf = deque([start])
    qb = deque([goal])
    while qf and qb:
        cur = qf.popleft()
        for nxt in neigh(cur):
            if nxt not in df:
                df[nxt] = df[cur] + 1
                qf.append(nxt)
                if nxt in db:
                    return df[nxt] + db[nxt]
        cur = qb.popleft()
        for nxt in neigh(cur):
            if nxt not in db:
                db[nxt] = db[cur] + 1
                qb.append(nxt)
                if nxt in df:
                    return df[nxt] + db[nxt]
    return None


# ---------------------------------------------------- independent KNAP engine

def knap_bruteforce(items, cap):
    n = len(items)
    best = 0
    for mask in range(1 << n):
        w = v = 0
        for i in range(n):
            if mask & (1 << i):
                w += items[i][0]
                v += items[i][1]
        if w <= cap and v > best:
            best = v
    return best


# ---------------------------------------------- independent cost recomputation

def naive_cost(domain, st):
    """Independent reason-locus cost model (mirrors frozen convention)."""
    if domain == "SAT_PROPAGATION":
        total = 0
        for assumps in st["queries"]:
            assign = {}
            for lit in assumps:
                assign[abs(lit)] = lit > 0
            while True:
                changed = False
                for clause in st["cnf"]:
                    total += 1
                    sat = False
                    un = []
                    for lit in clause:
                        v = abs(lit)
                        if v in assign:
                            if (lit > 0) == assign[v]:
                                sat = True
                                break
                        else:
                            un.append(lit)
                    if sat or len(un) != 1:
                        continue
                    assign[abs(un[0])] = un[0] > 0
                    changed = True
                if not changed:
                    break
        return total
    if domain == "PATH_PLANNING":
        total = 0
        for s in st["queries"]:
            # forward BFS expansions (charge = cells popped)
            start, goal = tuple(s), tuple(st["goal"])
            if start == goal:
                total += 1
                continue
            dist = {start: 0}
            q = deque([start])
            while q:
                cur = q.popleft()
                total += 1
                x, y = cur
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 15 and 0 <= ny < 15 and st["grid"][ny][nx] == 0 \
                            and (nx, ny) not in dist:
                        dist[(nx, ny)] = dist[cur] + 1
                        if (nx, ny) == goal:
                            q = deque()
                            break
                        q.append((nx, ny))
        return total
    total = 0
    for cap in st["queries"]:
        total += len(st["items"]) * (cap + 1)
    return total


def state_serving_cost(domain, st):
    """Independent state-locus serving cost model."""
    if domain == "SAT_PROPAGATION":
        occ = {}
        for clause in st["cnf"]:
            for lit in clause:
                occ.setdefault(lit, 0)
                occ[lit] += 0  # count below properly
        # occurrence-queue UP examinations, counted independently
        o = {}
        for clause in st["cnf"]:
            for lit in clause:
                o[lit] = o.get(lit, 0) + 1
        total = 0
        for assumps in st["queries"]:
            assign = {}
            for lit in assumps:
                assign[abs(lit)] = lit > 0
            queue = list(assumps)
            while queue:
                p = queue.pop(0)
                total += o.get(-p, 0)
                # find clauses containing -p
                for clause in st["cnf"]:
                    if -p not in clause:
                        continue
                    sat = False
                    un = []
                    for lit in clause:
                        v = abs(lit)
                        if v in assign:
                            if (lit > 0) == assign[v]:
                                sat = True
                                break
                        else:
                            un.append(lit)
                    if sat or len(un) != 1:
                        continue
                    assign[abs(un[0])] = un[0] > 0
                    queue.append(un[0])
        return total
    if domain == "PATH_PLANNING":
        # serving = descent steps = shortest distance (bidir BFS truth)
        total = 0
        for s in st["queries"]:
            d = path_bidir_distance(st["grid"], tuple(s), tuple(st["goal"]))
            total += d if d is not None else 0
        return total
    return len(st["queries"])  # one row lookup per query


def realized(domain, structures, chosen):
    total = 0
    for st in structures:
        if st["sid"] in chosen:
            total += st["declared_cost"] + state_serving_cost(domain, st)
        else:
            total += naive_cost(domain, st)
    return total


def allocator_pick(structures):
    idx = [(i, st) for i, st in enumerate(structures)
           if len(st["queries"]) >= TAU]
    idx.sort(key=lambda p: (-len(p[1]["queries"]), p[0]))
    chosen, cum = [], 0
    for i, st in idx:
        if cum + st["declared_cost"] <= BUDGET:
            chosen.append(st["sid"])
            cum += st["declared_cost"]
    return chosen


def truth_for(domain, st):
    outs = []
    if domain == "SAT_PROPAGATION":
        for assumps in st["queries"]:
            outs.append(sat_rescan_up(st["cnf"], assumps))
    elif domain == "PATH_PLANNING":
        for s in st["queries"]:
            outs.append(path_bidir_distance(st["grid"], tuple(s),
                                            tuple(st["goal"])))
    else:
        for cap in st["queries"]:
            outs.append(knap_bruteforce(st["items"], cap))
    return outs


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "p12_transfer_cases_v1.json")) as f:
        cases = json.load(f)
    result_path = os.path.join(os.getcwd(), "p12_transfer_allocation_v1.json")
    if not os.path.exists(result_path):
        result_path = os.path.join(here, "p12_transfer_allocation_v1.json")
    with open(result_path) as f:
        runner = json.load(f)

    ok_exact = True
    ok_selection = True
    ok_regret = True
    checks = []

    rdom = {d["domain"]: d for d in runner["domains"]}
    for dom in cases["domains"]:
        domain = dom["domain"]
        rcase = {c["case_id"]: c for c in rdom[domain]["cases"]}
        for case in dom["cases"]:
            structures = case["structures"]
            rc = rcase[case["case_id"]]

            # G1 independent truth
            for st, rtruth in zip(structures, rc["ground_truth"]):
                if truth_for(domain, st) != rtruth:
                    ok_exact = False
                    checks.append({"case": case["case_id"], "sid": st["sid"],
                                   "issue": "truth_mismatch"})

            # independent allocator decision
            pick = allocator_pick(structures)
            rpick = rc["arms"][ALLOC]["materialized"]
            if pick != rpick:
                ok_selection = False
                checks.append({"case": case["case_id"],
                               "issue": "selection_mismatch",
                               "independent": pick, "runner": rpick})

            # independent oracle + regrets
            n = len(structures)
            best = None
            for mask in range(1 << n):
                sset = {structures[i]["sid"] for i in range(n) if mask & (1 << i)}
                if sum(st["declared_cost"] for st in structures
                       if st["sid"] in sset) > BUDGET:
                    continue
                r = realized(domain, structures, sset)
                if best is None or r < best:
                    best = r
            for arm in ("REASON_ONLY", "STATE_ALWAYS", ALLOC):
                if arm == "REASON_ONLY":
                    sel = []
                elif arm == "STATE_ALWAYS":
                    sel, cum = [], 0
                    for st in structures:
                        if cum + st["declared_cost"] <= BUDGET:
                            sel.append(st["sid"])
                            cum += st["declared_cost"]
                else:
                    sel = pick
                rr = realized(domain, structures, set(sel)) - best
                if rr != rc["arms"][arm]["regret_vs_oracle"]:
                    ok_regret = False
                    checks.append({"case": case["case_id"], "arm": arm,
                                   "issue": "regret_mismatch",
                                   "independent": rr,
                                   "runner": rc["arms"][arm]["regret_vs_oracle"]})

    green = ok_exact and ok_selection and ok_regret
    out = {
        "schema": "p12-transfer-allocation-independent-check-v1",
        "checker_algorithms": {
            "SAT_PROPAGATION": "full_rescan_fixpoint_up",
            "PATH_PLANNING": "bidirectional_bfs",
            "KNAPSACK": "exhaustive_2pow_n_enumeration",
        },
        "independent_truth_exact": ok_exact,
        "independent_allocator_selection_agrees": ok_selection,
        "independent_regret_agrees": ok_regret,
        "discrepancies": checks,
        "terminal": ("P12_TRANSFER_ALLOCATION_SECOND_INDEPENDENT_CHECKER_GREEN"
                     if green else
                     "P12_TRANSFER_ALLOCATION_SECOND_INDEPENDENT_CHECKER_RED"),
    }
    sys.stdout.write(json.dumps(out, indent=1, sort_keys=False) + "\n")
    if not green:
        sys.exit(1)


if __name__ == "__main__":
    main()
