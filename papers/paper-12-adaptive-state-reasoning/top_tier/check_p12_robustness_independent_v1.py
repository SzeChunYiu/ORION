#!/usr/bin/env python3
"""P12 robustness stress — independent second checker V1.

Deliberately different algorithm classes from the runner (which imports the
frozen V1 engines):
  SAT  : full-rescan fixpoint UP for truth; own rescan / occurrence-count
         cost models mirroring the frozen charged-unit conventions
         (including the frozen stop-on-conflict semantics)
  PATH : bidirectional BFS run to completion on both sides, exact shortest
         distance = min over meeting nodes (truth + state serving); own
         forward-BFS expansion counting (reason charge)
  KNAP : exhaustive 2^n enumeration for truth; closed-form charge models

Independently re-derives, from the case files alone:
  - the frozen allocator decision (own implementation of tau=4,
    greedy-by-q, cumulative<=B, ties by case order) and both restrictions;
  - every arm's priced realized cost and priced regret under all five
    pre-registered price regimes (own priced oracle, own subset
    enumeration, same first-mask tie-break as the runner);
  - exact truth and per-arm outputs, compared against the runner's
    recorded ground_truth / arm_outputs;
  - the B1 case-mix aggregates and the B2 joint shared-budget mixes from
    the checker's own numbers (never from runner cells);
  - the runner's coverage counts, FLAT-replication flag and verdicts;
then cross-checks all of it against the runner's emitted JSON (default
./p12_robustness_stress_v1.json in the working directory).

Terminal: P12_ROBUSTNESS_SECOND_CHECKER_GREEN (zero discrepancies).
"""
import json
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
TAU = 4
BUDGET = 500
ALLOC = "P12_TRANSFER_ALLOCATOR_V1"
ARMS = ["REASON_ONLY", "STATE_ALWAYS", ALLOC]

REGIMES = [("FLAT", 1, 1), ("MEM2X", 2, 1), ("CMP2X", 1, 2),
           ("MEM4X", 4, 1), ("CMP4X", 1, 4)]

B1_MIXES = [
    ("MIX_BAL_27", {"SAT_PROPAGATION": 9, "PATH_PLANNING": 9, "KNAPSACK": 9}),
    ("MIX_KNAP_HEAVY", {"SAT_PROPAGATION": 4, "PATH_PLANNING": 4,
                        "KNAPSACK": 9}),
    ("MIX_PATH_HEAVY", {"SAT_PROPAGATION": 4, "PATH_PLANNING": 9,
                        "KNAPSACK": 4}),
    ("MIX_SAT_HEAVY", {"SAT_PROPAGATION": 9, "PATH_PLANNING": 4,
                       "KNAPSACK": 4}),
]
B2_MIXES = [
    ("JOINT_BAL", {"SAT_PROPAGATION": 3, "PATH_PLANNING": 3, "KNAPSACK": 3}),
    ("JOINT_KNAP_HEAVY", {"SAT_PROPAGATION": 2, "PATH_PLANNING": 2,
                          "KNAPSACK": 6}),
    ("JOINT_PATH_HEAVY", {"SAT_PROPAGATION": 2, "PATH_PLANNING": 6,
                          "KNAPSACK": 2}),
]
DOMAIN_ORDER = ["SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK"]

# Case-record keys are (tag, domain, case_id): the expanded set carries the
# nine V1 case_ids verbatim, so a (domain, case_id) key would silently
# overwrite the V1 pass and collapse cases_checked from 36 records to 27.
V1_TAG = "V1_9"
EXPANDED_TAG = "EXPANDED_27"


# ---------------------------------------------------- independent SAT engine

def sat_rescan_up(cnf, assumptions):
    """Full-rescan fixpoint UP; None on conflict (frozen convention)."""
    assign = {}
    for lit in assumptions:
        assign[abs(lit)] = lit > 0
    while True:
        changed = False
        for clause in cnf:
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
            if sat:
                continue
            if not un:
                return None
            if len(un) == 1:
                assign[abs(un[0])] = un[0] > 0
                changed = True
        if not changed:
            break
    return sorted((v if assign[v] else -v) for v in assign)


def sat_rescan_cost(cnf, assumptions):
    """Reason charge: clause examinations, stopping at the first conflict."""
    assign = {}
    for lit in assumptions:
        assign[abs(lit)] = lit > 0
    total = 0
    while True:
        changed = False
        for clause in cnf:
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
            if sat:
                continue
            if not un:
                return total
            if len(un) == 1:
                assign[abs(un[0])] = un[0] > 0
                changed = True
        if not changed:
            break
    return total


def sat_state_serve_cost(cnf, queries):
    """State serving charge: occurrence-list examinations per propagated
    literal, stopping the query at the first conflict (frozen convention)."""
    o = {}
    for clause in cnf:
        for lit in clause:
            o[lit] = o.get(lit, 0) + 1
    total = 0
    for assumps in queries:
        assign = {}
        for lit in assumps:
            assign[abs(lit)] = lit > 0
        queue = list(assumps)
        while queue:
            p = queue.pop(0)
            total += o.get(-p, 0)
            for clause in cnf:
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
                if sat:
                    continue
                if not un:
                    queue = []
                    break
                if len(un) == 1:
                    assign[abs(un[0])] = un[0] > 0
                    queue.append(un[0])
    return total


# ---------------------------------------------------- independent PATH engine

def path_neigh(grid, cell):
    x, y = cell
    res = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < 15 and 0 <= ny < 15 and grid[ny][nx] == 0:
            res.append((nx, ny))
    return res


def path_bidir_distance(grid, start, goal):
    """Exact bidirectional BFS: both searches run to completion; the answer
    is the minimum over all meeting nodes (provably the shortest distance,
    unlike meet-stop early termination)."""
    df = {start: 0}
    db = {goal: 0}
    qf = deque([start])
    qb = deque([goal])
    while qf:
        cur = qf.popleft()
        for nxt in path_neigh(grid, cur):
            if nxt not in df:
                df[nxt] = df[cur] + 1
                qf.append(nxt)
    while qb:
        cur = qb.popleft()
        for nxt in path_neigh(grid, cur):
            if nxt not in db:
                db[nxt] = db[cur] + 1
                qb.append(nxt)
    meet = [df[v] + db[v] for v in df if v in db]
    return min(meet) if meet else None


def path_bfs_expansions(grid, start, goal):
    """Reason charge: forward-BFS cells expanded (start counts; a goal
    discovered as a neighbour is not expanded) — frozen convention."""
    if start == goal:
        return 1
    dist = {start: 0}
    q = deque([start])
    expansions = 0
    while q:
        cur = q.popleft()
        expansions += 1
        for nxt in path_neigh(grid, cur):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                if nxt == goal:
                    return expansions
                q.append(nxt)
    return expansions


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


# ---------------------------------------------------- independent cost model

def charges(domain, st):
    """(declared, reason_serve, state_serve, truth_outputs)."""
    if domain == "SAT_PROPAGATION":
        truth = [sat_rescan_up(st["cnf"], a) for a in st["queries"]]
        reason = sum(sat_rescan_cost(st["cnf"], a) for a in st["queries"])
        state = sat_state_serve_cost(st["cnf"], st["queries"])
        return st["declared_cost"], reason, state, truth
    if domain == "PATH_PLANNING":
        goal = tuple(st["goal"])
        truth = [path_bidir_distance(st["grid"], tuple(s), goal)
                 for s in st["queries"]]
        reason = sum(path_bfs_expansions(st["grid"], tuple(s), goal)
                     for s in st["queries"])
        state = sum((d if d is not None else 0)
                    for d in truth)
        return st["declared_cost"], reason, state, truth
    truth = [knap_bruteforce(st["items"], c) for c in st["queries"]]
    reason = sum(len(st["items"]) * (c + 1) for c in st["queries"])
    return st["declared_cost"], reason, len(st["queries"]), truth


def own_allocator_pick(structures):
    idx = [(i, st) for i, st in enumerate(structures)
           if len(st["queries"]) >= TAU]
    idx.sort(key=lambda p: (-len(p[1]["queries"]), p[0]))
    chosen, cum = [], 0
    for i, st in idx:
        if cum + st["declared_cost"] <= BUDGET:
            chosen.append(st["sid"])
            cum += st["declared_cost"]
    return chosen


def own_state_always(structures):
    chosen, cum = [], 0
    for st in structures:
        if st["declared_cost"] <= BUDGET and \
                cum + st["declared_cost"] <= BUDGET:
            chosen.append(st["sid"])
            cum += st["declared_cost"]
    return chosen


def priced_oracle(sids, declared, reason, state, p_b, p_s):
    """Exhaustive priced hindsight optimum; first-mask tie-break (matches
    the runner's enumeration order)."""
    n = len(sids)
    best, best_set = None, None
    for mask in range(1 << n):
        sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
        if sum(declared[s] for s in sset) > BUDGET:
            continue
        build = sum(declared[s] for s in sset)
        serve = sum(state[s] if s in sset else reason[s] for s in sids)
        val = p_b * build + p_s * serve
        if best is None or val < best:
            best, best_set = val, sset
    return best_set, best


def check_case(rep_case, domain, case, discrepancies, tag, my_alloc_regret):
    """Cross-check one case; fill my_alloc_regret[(tag, domain, case_id)]."""
    structures = case["structures"]
    sids = [st["sid"] for st in structures]
    declared, reason, state, truth = {}, {}, {}, {}
    for st in structures:
        d, r, s, t = charges(domain, st)
        declared[st["sid"]], reason[st["sid"]], state[st["sid"]] = d, r, s
        truth[st["sid"]] = t

    cid = case["case_id"]
    key = f"{tag}:{cid}"

    # truth recorded by the runner vs independent truth
    runner_truth = rep_case["ground_truth"]
    for st, rt in zip(structures, runner_truth):
        if truth[st["sid"]] != rt:
            discrepancies.append(f"{key}: truth mismatch sid={st['sid']}")
    # per-arm outputs recorded by the runner vs independent truth
    for arm in ARMS:
        if rep_case["arm_outputs"][arm] != [truth[s] for s in sids]:
            discrepancies.append(f"{key}:{arm}: arm outputs != truth")
    if rep_case["outputs_exact_all_arms_all_regimes"] != \
            all(rep_case["arm_outputs"][a] == [truth[s] for s in sids]
                for a in ARMS):
        discrepancies.append(f"{key}: exactness flag inconsistent")

    picks = {
        "REASON_ONLY": [],
        "STATE_ALWAYS": own_state_always(structures),
        ALLOC: own_allocator_pick(structures),
    }
    if sorted(picks[ALLOC]) != rep_case["selections"][ALLOC]:
        discrepancies.append(f"{key}: allocator selection differs")
    if sorted(picks["STATE_ALWAYS"]) != rep_case["selections"][
            "STATE_ALWAYS"]:
        discrepancies.append(f"{key}: state_always selection differs")

    my_alloc_regret[(tag, domain, cid)] = {}
    for regime, p_b, p_s in REGIMES:
        cell = rep_case["regimes"][regime]
        oset, oval = priced_oracle(sids, declared, reason, state, p_b, p_s)
        if sorted(oset) != cell["priced_oracle"]["materialized"] or \
                oval != cell["priced_oracle"]["priced_realized"]:
            discrepancies.append(
                f"{key}:{regime}: priced oracle differs")
        for arm in ARMS:
            sel = set(picks[arm])
            build = sum(declared[s] for s in sel)
            serve = sum(state[s] if s in sel else reason[s] for s in sids)
            val = p_b * build + p_s * serve
            mine = {
                "materialized": sorted(sel),
                "priced_realized": val,
                "priced_regret": val - oval,
            }
            theirs = cell["arms"][arm]
            for k, v in mine.items():
                if theirs[k] != v:
                    discrepancies.append(
                        f"{key}:{regime}:{arm}:{k} mine={v} theirs={theirs[k]}")
            if arm == ALLOC:
                my_alloc_regret[(tag, domain, cid)][regime] = \
                    mine["priced_regret"]


def recompute_verdicts(my_alloc_regret, b1_mine, b2_mine):
    green_regimes = []
    for regime, _, _ in REGIMES:
        if all(cells[regime] == 0 for cells in my_alloc_regret.values()):
            green_regimes.append(regime)
    joint_green = [r for r, _, _ in REGIMES
                   if all(m[r] == 0 for m in b2_mine.values())]
    price_green = [r for r in green_regimes if r in joint_green]
    if len(price_green) == len(REGIMES):
        price_verdict = "ROBUST"
    elif price_green:
        price_verdict = "REGIME_CONDITIONAL"
    else:
        price_verdict = "BROKEN"
    shift_cells_ok = all(all(v == 0 for v in mix.values())
                         for mix in b1_mine.values())
    shift_joint_ok = len(joint_green) == len(REGIMES)
    if shift_cells_ok and shift_joint_ok:
        shift_verdict = "ROBUST"
    elif shift_cells_ok or shift_joint_ok:
        shift_verdict = "REGIME_CONDITIONAL"
    else:
        shift_verdict = "BROKEN"
    return {
        "price_axis": price_verdict,
        "price_axis_zero_regret_regimes": price_green,
        "distribution_shift_axis": shift_verdict,
        "shift_case_mixes_zero_regret": shift_cells_ok,
        "shift_joint_mixes_zero_regret_regimes": joint_green,
    }


def main():
    discrepancies = []
    with open(os.path.join(HERE, "p12_transfer_cases_v1.json")) as f:
        v1_cases = json.load(f)
    with open(os.path.join(HERE,
                           "p12_transfer_cases_expanded_v1.json")) as f:
        exp_cases = json.load(f)

    result_path = os.path.join(os.getcwd(), "p12_robustness_stress_v1.json")
    if not os.path.exists(result_path):
        result_path = os.path.join(HERE, "p12_robustness_stress_v1.json")
    with open(result_path) as f:
        runner = json.load(f)

    my_alloc_regret = {}

    for cases, key, tag in ((v1_cases, "v1_set", V1_TAG),
                            (exp_cases, "expanded_set", EXPANDED_TAG)):
        rep = runner[key]
        if rep["case_count"] != sum(len(d["cases"])
                                    for d in cases["domains"]):
            discrepancies.append(f"{tag}: case_count differs")
        for dom, rep_dom in zip(cases["domains"], rep["domains"]):
            for case, rep_case in zip(dom["cases"], rep_dom["cases"]):
                check_case(rep_case, dom["domain"], case, discrepancies,
                           tag, my_alloc_regret)

    # ---- FLAT replication of the V1 zero-regret claim (own numbers)
    v1_flat = all(
        my_alloc_regret[(V1_TAG, d["domain"], c["case_id"])]["FLAT"] == 0
        for d in v1_cases["domains"] for c in d["cases"])
    if runner["v1_set"]["v1_flat_zero_regret_replicated"] != v1_flat:
        discrepancies.append("v1_flat_zero_regret_replicated differs")

    # ---- B1 aggregates from the checker's own per-cell regrets
    ordered = {d["domain"]: [c["case_id"] for c in d["cases"]]
               for d in exp_cases["domains"]}
    b1_report = {m["mix"]: m for m in runner["b1_case_mixes"]}
    b1_mine = {}
    for mix, counts in B1_MIXES:
        b1_mine[mix] = {}
        for regime, _, _ in REGIMES:
            total = sum(
                my_alloc_regret[(EXPANDED_TAG, domain, cid)][regime]
                for domain in DOMAIN_ORDER
                for cid in ordered[domain][:counts[domain]])
            b1_mine[mix][regime] = total
            theirs = b1_report[mix]["regimes"][regime][
                "allocator_total_priced_regret"]
            if total != theirs:
                discrepancies.append(
                    f"{mix}:{regime}: b1 aggregate mine={total} "
                    f"theirs={theirs}")

    # ---- B2 joint mixes: own union allocator + own priced oracle + outputs
    b2_report = {m["mix"]: m for m in runner["b2_joint_mixes"]}
    b2_mine = {}
    for mix, counts in B2_MIXES:
        union = []
        for domain in DOMAIN_ORDER:
            dom = next(d for d in exp_cases["domains"]
                       if d["domain"] == domain)
            for case in dom["cases"][:counts[domain]]:
                for st in case["structures"]:
                    union.append((domain, st))
        sids = [st["sid"] for _, st in union]
        declared, reason, state, truth_u = {}, {}, {}, []
        for domain, st in union:
            d, r, s, t = charges(domain, st)
            declared[st["sid"]], reason[st["sid"]], state[st["sid"]] = d, r, s
            truth_u.append(t)
        union_structs = [st for _, st in union]
        picks = {
            "REASON_ONLY": [],
            "STATE_ALWAYS": own_state_always(union_structs),
            ALLOC: own_allocator_pick(union_structs),
        }
        rep = b2_report[mix]
        key = mix
        if rep["structure_count"] != len(union):
            discrepancies.append(f"{key}: joint structure count differs")
        if sorted(picks[ALLOC]) != rep["selections"][ALLOC]:
            discrepancies.append(f"{key}: joint allocator selection differs")
        if rep["ground_truth"] != truth_u:
            discrepancies.append(f"{key}: joint truth mismatch")
        for arm in ARMS:
            # arm outputs: state output if materialized else reason output;
            # both loci must equal truth when exact — compare recorded
            # outputs to independent truth directly
            if rep["arm_outputs"][arm] != truth_u:
                discrepancies.append(f"{key}:{arm}: joint outputs != truth")
        b2_mine[mix] = {}
        for regime, p_b, p_s in REGIMES:
            oset, oval = priced_oracle(sids, declared, reason, state,
                                       p_b, p_s)
            cell = rep["regimes"][regime]
            if sorted(oset) != cell["priced_oracle"]["materialized"] or \
                    oval != cell["priced_oracle"]["priced_realized"]:
                discrepancies.append(f"{key}:{regime}: joint oracle differs")
            for arm in ARMS:
                sel = set(picks[arm])
                build = sum(declared[s] for s in sel)
                serve = sum(state[s] if s in sel else reason[s]
                            for s in sids)
                val = p_b * build + p_s * serve
                if cell["arms"][arm]["priced_realized"] != val or \
                        cell["arms"][arm]["priced_regret"] != val - oval:
                    discrepancies.append(
                        f"{key}:{regime}:{arm}: joint priced cell differs")
                if arm == ALLOC:
                    b2_mine[mix][regime] = val - oval

    # ---- coverage, verdicts
    cov = runner["coverage"]
    expected_cov = {
        "v1_case_regime_cells": 9 * len(REGIMES),
        "expanded_case_regime_cells": 27 * len(REGIMES),
        "b1_mixes": len(B1_MIXES),
        "b2_joint_mixes": len(B2_MIXES),
    }
    for k, v in expected_cov.items():
        if cov.get(k) != v:
            discrepancies.append(f"coverage {k}: mine={v} theirs={cov.get(k)}")

    verdicts_mine = recompute_verdicts(my_alloc_regret, b1_mine, b2_mine)
    for k, v in verdicts_mine.items():
        if runner["verdicts"].get(k) != v:
            discrepancies.append(f"verdict {k}: mine={v} "
                                 f"theirs={runner['verdicts'].get(k)}")

    green = not discrepancies
    report = {
        "schema": "p12-robustness-independent-checker-v1",
        "study": "P12_ROBUSTNESS_STRESS_V1",
        "algorithm_classes": {
            "sat": "full-rescan fixpoint UP + own occurrence counting "
                   "(frozen conflict-stop semantics)",
            "path": "exact bidirectional BFS (completion, min over meets) + "
                    "own forward-BFS expansion counting",
            "knapsack": "exhaustive 2^n enumeration",
        },
        "cases_checked": len(my_alloc_regret),
        "own_verdicts": verdicts_mine,
        "discrepancies": discrepancies[:100],
        "discrepancy_count": len(discrepancies),
        "runner_verdicts": runner["verdicts"],
        "terminal": ("P12_ROBUSTNESS_SECOND_CHECKER_GREEN" if green
                     else "P12_ROBUSTNESS_SECOND_CHECKER_FAILED"),
    }
    sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
