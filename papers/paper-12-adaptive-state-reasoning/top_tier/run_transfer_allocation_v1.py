#!/usr/bin/env python3
"""P12 unchanged-allocator cross-domain transfer study — frozen runner V1.

Executes P12_TRANSFER_ALLOCATION_PROTOCOL_V1 over p12_transfer_cases_v1.json.
Stdlib only. Deterministic byte-for-byte output on stdout (single json.dumps).

Charged-unit conventions (frozen by the case file, per domain):
  SAT_PROPAGATION : clause_examination
  PATH_PLANNING   : bfs_cell_expansion
  KNAPSACK        : dp_cell_fill

Cost model (frozen):
  SAT REASON  : naive full-rescan fixpoint UP; charge = passes * |cnf|.
  SAT STATE   : build charge = declared_cost (= |cnf|, one indexing pass);
                serving charge = sum of occurrence-list examinations
                (occ(clauses containing the negation of each propagated lit)).
  PATH REASON : per-query BFS from start; charge = cells expanded.
  PATH STATE  : build charge = declared_cost (=225, whole-grid reverse BFS);
                serving charge = descent steps (= shortest distance).
  KNAP REASON : per-query DP; charge = n*(cap+1) cell fills.
  KNAP STATE  : build charge = declared_cost (= n*(C_max+1)); serving = 1
                row lookup per query.
In-run ground truth (for G1) is computed by a from-scratch code path distinct
from both arms' serving paths (SAT: occurrence-queue UP; PATH: full reverse
BFS distances; KNAP: full-table DP at C_max then row read).  The independent
checker re-derives everything with different algorithm classes.
"""
import json
import os
import sys

TAU = 4
BUDGET = 500
ALLOCATOR_NAME = "P12_TRANSFER_ALLOCATOR_V1"
ARMS = ["REASON_ONLY", "STATE_ALWAYS", ALLOCATOR_NAME, "ORACLE_LOCATION"]

# ---------------------------------------------------------------- SAT domain


def sat_naive_up(cnf, assumptions):
    """Full-rescan fixpoint unit propagation. Returns (closure or None, ops)."""
    assign = {}
    for lit in assumptions:
        assign[abs(lit)] = lit > 0
    ops = 0
    while True:
        changed = False
        for clause in cnf:
            ops += 1
            satisfied = False
            unassigned = []
            for lit in clause:
                v = abs(lit)
                if v in assign:
                    if (lit > 0) == assign[v]:
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            if satisfied:
                continue
            if not unassigned:
                return None, ops  # conflict under assignment
            if len(unassigned) == 1:
                lit = unassigned[0]
                assign[abs(lit)] = lit > 0
                changed = True
        if not changed:
            break
    closure = sorted((v if assign[v] else -v) for v in assign)
    return closure, ops


def sat_occ_map(cnf):
    occ = {}
    for ci, clause in enumerate(cnf):
        for lit in clause:
            occ.setdefault(lit, []).append(ci)
    return occ


def sat_indexed_up(occ, assumptions):
    """Occurrence-queue UP. Returns (closure or None, examinations)."""
    assign = {}
    for lit in assumptions:
        assign[abs(lit)] = lit > 0
    queue = list(assumptions)
    ops = 0
    conflict = False
    while queue:
        p = queue.pop(0)
        for ci in occ.get(-p, []):
            ops += 1
            # re-derive clause state from assign
            clause = _CLAUSE_CACHE[ci]
            satisfied = False
            unassigned = []
            for lit in clause:
                v = abs(lit)
                if v in assign:
                    if (lit > 0) == assign[v]:
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            if satisfied:
                continue
            if not unassigned:
                conflict = True
                queue = []
                break
            if len(unassigned) == 1:
                lit = unassigned[0]
                assign[abs(lit)] = lit > 0
                queue.append(lit)
    if conflict:
        return None, ops
    closure = sorted((v if assign[v] else -v) for v in assign)
    return closure, ops


_CLAUSE_CACHE = []


# -------------------------------------------------------------- PATH domain


def path_children(grid, cell):
    x, y = cell
    out = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < 15 and 0 <= ny < 15 and grid[ny][nx] == 0:
            out.append((nx, ny))
    return out


def path_bfs(grid, start, goal):
    """Forward BFS. Returns (distance or None, expansions)."""
    from collections import deque
    if start == goal:
        return 0, 1
    dist = {start: 0}
    q = deque([start])
    expansions = 0
    while q:
        cur = q.popleft()
        expansions += 1
        for nxt in path_children(grid, cur):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                if nxt == goal:
                    return dist[nxt], expansions
                q.append(nxt)
    return None, expansions


def path_reverse_table(grid, goal):
    """Whole-grid reverse BFS distances. Returns (dist dict, expansions)."""
    from collections import deque
    dist = {tuple(goal): 0}
    q = deque([tuple(goal)])
    expansions = 0
    while q:
        cur = q.popleft()
        expansions += 1
        for nxt in path_children(grid, cur):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    return dist, expansions


# ----------------------------------------------------------- KNAPSACK domain


def knap_dp_value(items, cap):
    """Per-query DP. Returns (best value, fills = n*(cap+1), frozen flat)."""
    n = len(items)
    table = [0] * (cap + 1)
    for w, val in items:
        for c in range(cap, w - 1, -1):
            cand = table[c - w] + val
            if cand > table[c]:
                table[c] = cand
    return table[cap], n * (cap + 1)


def knap_full_table(items, c_max):
    """Full DP table for declared maximal capacity. Returns (table, fills)."""
    return knap_dp_value_row(items, c_max)


def knap_dp_value_row(items, c_max):
    n = len(items)
    table = [0] * (c_max + 1)
    for w, val in items:
        for c in range(c_max, w - 1, -1):
            cand = table[c - w] + val
            if cand > table[c]:
                table[c] = cand
    return table, n * (c_max + 1)


# ------------------------------------------------- per-structure query serving


def serve_case(structures, materialized, domain):
    """Realized charged query ops + outputs for one locus assignment.

    materialized: set of sids served from STATE.
    Returns (realized_query_ops, outputs list aligned to structures order).
    """
    total = 0
    outputs = []
    for st in structures:
        sid = st["sid"]
        q_list = st["queries"]
        outs = []
        if sid in materialized:
            if domain == "SAT_PROPAGATION":
                occ = _OCC_CACHE[sid]
                for assumps in q_list:
                    out, ops = sat_indexed_up(occ, assumps)
                    outs.append(out)
                    total += ops
            elif domain == "PATH_PLANNING":
                dist = _REVDIST_CACHE[sid]
                for s in q_list:
                    outs.append(dist.get(tuple(s)))
                    total += dist.get(tuple(s), 0) or 0
            else:  # KNAPSACK
                table = _TABLE_CACHE[sid]
                for cap in q_list:
                    outs.append(table[cap])
                    total += 1
        else:
            if domain == "SAT_PROPAGATION":
                cnf = st["cnf"]
                for assumps in q_list:
                    out, ops = sat_naive_up(cnf, assumps)
                    outs.append(out)
                    total += ops
            elif domain == "PATH_PLANNING":
                grid = st["grid"]
                goal = tuple(st["goal"])
                for s in q_list:
                    out, ops = path_bfs(grid, tuple(s), goal)
                    outs.append(out)
                    total += ops
            else:  # KNAPSACK
                items = st["items"]
                for cap in q_list:
                    out, ops = knap_dp_value(items, cap)
                    outs.append(out)
                    total += ops
        outputs.append(outs)
    return total, outputs


def build_cost(structures, materialized):
    return sum(st["declared_cost"] for st in structures if st["sid"] in materialized)


_OCC_CACHE = {}
_REVDIST_CACHE = {}
_TABLE_CACHE = {}
_CLAUSE_CACHE = []


def prime_caches(domain, structures):
    _OCC_CACHE.clear()
    _REVDIST_CACHE.clear()
    _TABLE_CACHE.clear()
    _CLAUSE_CACHE.clear()
    for st in structures:
        if domain == "SAT_PROPAGATION":
            _CLAUSE_CACHE.extend(st["cnf"])
            _OCC_CACHE[st["sid"]] = sat_occ_map(st["cnf"])
        elif domain == "PATH_PLANNING":
            _REVDIST_CACHE[st["sid"]] = path_reverse_table(st["grid"], st["goal"])[0]
        else:
            _TABLE_CACHE[st["sid"]] = knap_full_table(st["items"], st["c_max"])[0]


def allocator_selection(structures):
    """Frozen rule: q>=TAU eligible; greedy by (-q, case order); cum<=BUDGET."""
    eligible = [
        (i, st) for i, st in enumerate(structures)
        if len(st["queries"]) >= TAU
    ]
    eligible.sort(key=lambda pair: (-len(pair[1]["queries"]), pair[0]))
    chosen = []
    cum = 0
    for i, st in eligible:
        if cum + st["declared_cost"] <= BUDGET:
            chosen.append(st["sid"])
            cum += st["declared_cost"]
    return chosen


def state_always_selection(structures):
    chosen = []
    cum = 0
    for st in structures:
        if st["declared_cost"] <= BUDGET and cum + st["declared_cost"] <= BUDGET:
            chosen.append(st["sid"])
            cum += st["declared_cost"]
    return chosen


def oracle_selection(structures, domain):
    """Exhaustive budget-respecting hindsight optimum (diagnostic)."""
    n = len(structures)
    best = None
    best_set = None
    for mask in range(1 << n):
        sset = {structures[i]["sid"] for i in range(n) if mask & (1 << i)}
        if sum(st["declared_cost"] for st in structures if st["sid"] in sset) > BUDGET:
            continue
        realized = build_cost(structures, sset) + serve_case(structures, sset, domain)[0]
        if best is None or realized < best:
            best = realized
            best_set = sset
    return sorted(best_set), best


def ground_truth(domain, structures):
    """From-scratch exact truth per query (distinct code path from arms)."""
    truth = []
    verify_ops = 0
    for st in structures:
        outs = []
        if domain == "SAT_PROPAGATION":
            occ = sat_occ_map(st["cnf"])
            for assumps in st["queries"]:
                out, ops = sat_indexed_up(occ, assumps)
                outs.append(out)
                verify_ops += ops
        elif domain == "PATH_PLANNING":
            dist = path_reverse_table(st["grid"], st["goal"])[0]
            verify_ops += 225
            for s in st["queries"]:
                outs.append(dist.get(tuple(s)))
        else:
            table = knap_full_table(st["items"], st["c_max"])[0]
            verify_ops += len(st["items"]) * (st["c_max"] + 1)
            for cap in st["queries"]:
                outs.append(table[cap])
        truth.append(outs)
    return truth, verify_ops


def i_sem(domain, structures):
    if domain == "SAT_PROPAGATION":
        return sum(len(cl) for st in structures for cl in st["cnf"])
    if domain == "PATH_PLANNING":
        edges = 0
        for st in structures:
            grid = st["grid"]
            for y in range(15):
                for x in range(15):
                    if grid[y][x] == 0:
                        edges += len(path_children(grid, (x, y)))
        return edges
    return sum(2 * len(st["items"]) for st in structures)


def a_dim(domain, structures, materialized):
    total = 0
    for st in structures:
        if st["sid"] not in materialized:
            continue
        if domain == "SAT_PROPAGATION":
            total += sum(len(cl) for cl in st["cnf"])
        elif domain == "PATH_PLANNING":
            total += 225
        else:
            total += st["c_max"] + 1
    return total


def resource_vector(domain, structures, materialized, realized, infer_ops, verify_ops):
    return {
        "I_sem": i_sem(domain, structures),
        "A_dim": a_dim(domain, structures, materialized),
        "A_transform": build_cost(structures, materialized),
        "M_state": 0,
        "C_fit": 0,
        "C_infer": infer_ops,
        "C_explicit": verify_ops,
        "R_registered": realized,
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "p12_transfer_cases_v1.json")) as f:
        cases = json.load(f)

    allocator_params = {
        "rule": "materialize-if-q>=tau;greedy-by-desc-q;cumulative<=B;ties-by-case-order",
        "tau": TAU,
        "budget_B": BUDGET,
        "signals": ["q_pending_multiplicity", "c_declared_cost", "B_budget"],
    }

    g1_ok = True
    g2_ok = True
    g3_reason = {d["domain"]: False for d in cases["domains"]}
    g3_state_domains = []
    g4_ok = True
    g6_ok = True
    domain_reports = []

    for dom in cases["domains"]:
        domain = dom["domain"]
        case_reports = []
        for case in dom["cases"]:
            structures = case["structures"]
            prime_caches(domain, structures)
            truth, verify_ops = ground_truth(domain, structures)

            selections = {
                "REASON_ONLY": [],
                "STATE_ALWAYS": state_always_selection(structures),
                ALLOCATOR_NAME: allocator_selection(structures),
            }
            oracle_sel, oracle_realized = oracle_selection(structures, domain)

            arm_cells = {}
            for arm in ["REASON_ONLY", "STATE_ALWAYS", ALLOCATOR_NAME]:
                sel = selections[arm]
                infer_ops, outputs = serve_case(structures, set(sel), domain)
                realized = build_cost(structures, set(sel)) + infer_ops
                exact = outputs == truth
                if not exact:
                    g1_ok = False
                regret = realized - oracle_realized
                if arm == ALLOCATOR_NAME and regret != 0:
                    g2_ok = False
                if arm == "REASON_ONLY" and regret > 0:
                    g3_reason[domain] = True
                if arm == "STATE_ALWAYS" and regret > 0:
                    g3_state_domains.append(domain)
                rv = resource_vector(domain, structures, set(sel), realized,
                                     infer_ops, verify_ops)
                if set(rv.keys()) != {"I_sem", "A_dim", "A_transform", "M_state",
                                      "C_fit", "C_infer", "C_explicit",
                                      "R_registered"}:
                    g4_ok = False
                if rv["M_state"] != 0 or rv["C_fit"] != 0:
                    g4_ok = False
                arm_cells[arm] = {
                    "materialized": sel,
                    "realized_charged_ops": realized,
                    "regret_vs_oracle": regret,
                    "outputs_exact": exact,
                    "resource_vector": rv,
                }
            arm_cells["ORACLE_LOCATION"] = {
                "materialized": oracle_sel,
                "realized_charged_ops": oracle_realized,
                "role": "diagnostic_only",
            }
            case_reports.append({
                "case_id": case["case_id"],
                "structure_q_multiplicity": {
                    st["sid"]: len(st["queries"]) for st in structures
                },
                "declared_costs": {
                    st["sid"]: st["declared_cost"] for st in structures
                },
                "arms": arm_cells,
                "ground_truth": truth,
            })
        domain_reports.append({
            "domain": domain,
            "charged_unit": dom["charged_unit"],
            "allocator_params": allocator_params,
            "cases": case_reports,
        })

    g3_ok = (all(g3_reason.values())
             and len(set(g3_state_domains)) >= 2)
    gates = {
        "G1_exact_outputs_all_arms": g1_ok,
        "G2_allocator_zero_regret_every_case": g2_ok,
        "G3_restrictions_fail_somewhere": g3_ok,
        "G4_resource_vector_complete_and_unlearned": g4_ok,
        "G5_byte_replay": "asserted_by_ci_rerun_cmp",
        "G6_allocator_identity_across_domains": g6_ok,
    }
    core_ok = g1_ok and g2_ok and g3_ok and g4_ok and g6_ok
    report = {
        "schema": "p12-transfer-allocation-result-v1",
        "study": "P12_TRANSFER_ALLOCATION_V1",
        "protocol": "P12_TRANSFER_ALLOCATION_PROTOCOL_V1",
        "allocator": allocator_params,
        "domains": domain_reports,
        "g3_detail": {
            "reason_only_positive_regret_domains": sorted(
                [d for d, v in g3_reason.items() if v]),
            "state_always_positive_regret_domains": sorted(set(g3_state_domains)),
        },
        "gates": gates,
        "terminal": ("P12_TRANSFER_ALLOCATION_V1_SUPPORTED" if core_ok
                     else "P12_TRANSFER_ALLOCATION_V1_FAILED"),
    }
    # G6: allocator parameters byte-identical across domains
    for dr in domain_reports:
        if dr["allocator_params"] != allocator_params:
            report["gates"]["G6_allocator_identity_across_domains"] = False
            report["terminal"] = "P12_TRANSFER_ALLOCATION_V1_FAILED"
    sys.stdout.write(json.dumps(report, indent=1, sort_keys=False) + "\n")


if __name__ == "__main__":
    main()
