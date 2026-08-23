#!/usr/bin/env python3
"""P12 robustness stress — frozen constructive case generator V1.

Expands the V1 transfer set (9 cases) to 27 cases (9 per domain):
  - the nine V1 cases are carried over BYTE-IDENTICALLY from
    p12_transfer_cases_v1.json (same case_id, same data);
  - eighteen new cases are appended, six per domain, one per pre-registered
    stress shape of P12_ROBUSTNESS_PROTOCOL_V2.md:
      T4_TAU_EDGE      single structure, q = tau - 1 = 3
      T5_TAU_EXACT     single structure, q = tau = 4
      T6_TIE_RACE      equal-q structures whose combined cost exceeds B
      T7_OVER_BUDGET   one high-multiplicity structure with declared > B
                       (PATH: structurally impossible, declared fixed at 225;
                        the case is emitted as the high-multiplicity stress)
      T8_MANY_SMALL    all eligible structures jointly fit B
                       (PATH: at most two 225-cost structures fit; emitted so)
      T9_MIXED         eligible + sub-threshold structures under binding budget

All construction is literal and deterministic (no RNG). SAT clause lists
cycle a frozen 8-pattern base over <= 8 variables; PATH grids materialize
the four frozen obstacle families of the procedural study (OPEN,
CENTER_GATE, DOUBLE_GATE, HORIZONTAL_GATE); knapsack item sets are explicit.

Declared-cost conventions (asserted at emit time):
  SAT_PROPAGATION : declared_cost == len(cnf)
  PATH_PLANNING   : declared_cost == 225
  KNAPSACK        : declared_cost == n * (c_max + 1)

Output: p12_transfer_cases_expanded_v1.json on stdout (indent=1). CI asserts
byte-identity with the committed case file.
"""
import json
import os
import sys

TAU = 4
BUDGET = 500
N = 15

# --------------------------------------------------------------- SAT builder

_SAT_BASE = [
    [1, 2, 3], [-1, 2, 4], [-2, -3, 5], [1, -4, -5],
    [3, 4, -6], [-1, 5, 6], [2, -5, -6], [-3, 4, 5],
]


def sat_clauses(m):
    """m clauses, cycling the frozen base with a variable rotation."""
    clauses = []
    for k in range(m):
        rot = (k // len(_SAT_BASE)) % 8
        clauses.append([((v - 1 + rot) % 8) + 1 if v > 0
                        else -(((((-v) - 1 + rot)) % 8) + 1)
                        for v in _SAT_BASE[k % len(_SAT_BASE)]])
    return clauses


def sat_case(case_id, structures):
    for st in structures:
        assert st["declared_cost"] == len(st["cnf"]), (case_id, st["sid"])
        assert all(len(cl) == 3 for cl in st["cnf"])
        assert all(1 <= abs(l) <= 8 for cl in st["cnf"] for l in cl)
    return {"case_id": case_id, "structures": structures}


# ------------------------------------------------------------- PATH builder

def walls(pattern):
    if pattern == "OPEN":
        return set()
    if pattern == "CENTER_GATE":
        return {(7, y) for y in range(N) if y != 7}
    if pattern == "DOUBLE_GATE":
        return {(5, y) for y in range(N) if y != 3} | \
               {(10, y) for y in range(N) if y != 11}
    if pattern == "HORIZONTAL_GATE":
        return {(x, 8) for x in range(N) if x != 4}
    raise ValueError(pattern)


def grid_of(pattern):
    w = walls(pattern)
    return [[1 if (x, y) in w else 0 for x in range(N)] for y in range(N)]


def path_structure(sid, pattern, starts):
    goal = [14, 14]
    w = walls(pattern)
    assert (goal[0], goal[1]) not in w
    for s in starts:
        assert tuple(s) not in w, (sid, s)
        assert 0 <= s[0] < N and 0 <= s[1] < N
    return {
        "sid": sid,
        "grid": grid_of(pattern),
        "goal": goal,
        "declared_cost": 225,
        "queries": [list(s) for s in starts],
    }


def path_case(case_id, structures):
    for st in structures:
        assert st["declared_cost"] == 225
        assert len(st["grid"]) == 15 and all(len(r) == 15 for r in st["grid"])
    return {"case_id": case_id, "structures": structures}


# ------------------------------------------------------------- KNAP builder

def knap_structure(sid, items, c_max, caps):
    for w, v in items:
        assert 1 <= w <= 15 and 1 <= v <= 30
    assert all(1 <= c <= c_max for c in caps)
    return {
        "sid": sid,
        "items": [list(iv) for iv in items],
        "c_max": c_max,
        "declared_cost": len(items) * (c_max + 1),
        "queries": list(caps),
    }


def knap_case(case_id, structures):
    for st in structures:
        assert st["declared_cost"] == len(st["items"]) * (st["c_max"] + 1)
        assert len(st["items"]) <= 16
    return {"case_id": case_id, "structures": structures}


_ITEMS = {
    "K4": [(2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)],
    "K5": [(3, 5), (4, 7), (5, 9), (6, 11), (7, 13), (8, 15)],
    "K6A": [(2, 4), (3, 6), (4, 8), (5, 10), (6, 12), (7, 14), (8, 16),
            (9, 18), (10, 20), (11, 22)],
    "K6B": [(2, 5), (4, 9), (6, 13), (8, 17), (10, 21), (12, 25), (14, 29),
            (15, 30)],
    "K7": [(2, 3), (3, 5), (4, 7), (5, 9), (6, 11), (7, 13), (8, 15), (9, 17),
           (10, 19), (11, 21), (12, 23), (13, 25), (14, 27)],
    "K8A": [(3, 6), (5, 10), (7, 14), (9, 18), (11, 22), (13, 26)],
    "K8B": [(4, 8), (7, 14), (10, 20), (13, 26), (15, 30)],
    "K8C": [(2, 7), (5, 12), (8, 17), (11, 22), (14, 27), (15, 29)],
    "K9A": [(2, 6), (4, 10), (6, 14), (8, 18), (10, 22), (12, 26), (14, 28),
            (15, 30)],
    "K9B": [(3, 9), (6, 15), (9, 21), (12, 27), (15, 30)],
    "K9C": [(4, 11), (8, 19), (12, 27), (13, 28), (15, 30)],
}


def build_expanded(v1_cases):
    sat_new = [
        sat_case("SAT_T4_TAU_EDGE", [{
            "sid": "S4", "cnf": sat_clauses(10), "declared_cost": 10,
            "queries": [[1], [-2], [4]]}]),
        sat_case("SAT_T5_TAU_EXACT", [{
            "sid": "S5", "cnf": sat_clauses(10), "declared_cost": 10,
            "queries": [[1], [2], [3], [4]]}]),
        sat_case("SAT_T6_TIE_RACE", [
            {"sid": "S6A", "cnf": sat_clauses(170), "declared_cost": 170,
             "queries": [[1], [-1], [2], [-2], [3]]},
            {"sid": "S6B", "cnf": sat_clauses(180), "declared_cost": 180,
             "queries": [[4], [-4], [5], [-5], [6]]},
            {"sid": "S6C", "cnf": sat_clauses(170), "declared_cost": 170,
             "queries": [[7], [-7], [8], [-8], [1]]}]),
        sat_case("SAT_T7_OVER_BUDGET", [{
            "sid": "S7", "cnf": sat_clauses(520), "declared_cost": 520,
            "queries": [[1], [-1], [2], [-2], [3], [-3], [4], [-4], [5]]}]),
        sat_case("SAT_T8_MANY_SMALL", [
            {"sid": "S8A", "cnf": sat_clauses(90), "declared_cost": 90,
             "queries": [[1], [2], [3], [4], [5], [6], [7]]},
            {"sid": "S8B", "cnf": sat_clauses(120), "declared_cost": 120,
             "queries": [[-1], [-2], [-3], [-4], [-5], [-6]]},
            {"sid": "S8C", "cnf": sat_clauses(200), "declared_cost": 200,
             "queries": [[5], [-5], [6], [-6], [7]]}]),
        sat_case("SAT_T9_MIXED", [
            {"sid": "S9A", "cnf": sat_clauses(150), "declared_cost": 150,
             "queries": [[1], [-1], [2], [-2], [3], [-3], [4], [-4]]},
            {"sid": "S9B", "cnf": sat_clauses(30), "declared_cost": 30,
             "queries": [[5], [-5], [6]]},
            {"sid": "S9C", "cnf": sat_clauses(300), "declared_cost": 300,
             "queries": [[7], [-7], [8], [-8], [1]]}]),
    ]
    path_new = [
        path_case("PATH_T4_TAU_EDGE", [
            path_structure("P4", "OPEN", [[0, 0], [7, 7], [12, 5]])]),
        path_case("PATH_T5_TAU_EXACT", [
            path_structure("P5", "OPEN", [[0, 0], [7, 7], [12, 5], [3, 11]])]),
        path_case("PATH_T6_TIE_RACE", [
            path_structure("P6A", "CENTER_GATE",
                           [[0, 0], [14, 0], [0, 14], [3, 3], [11, 2],
                            [2, 11]]),
            path_structure("P6B", "DOUBLE_GATE",
                           [[0, 0], [14, 0], [2, 8], [12, 4], [0, 14],
                            [13, 12]]),
            path_structure("P6C", "HORIZONTAL_GATE",
                           [[0, 0], [14, 0], [0, 14], [3, 3], [11, 2]])]),
        path_case("PATH_T7_OVER_BUDGET", [
            path_structure("P7", "OPEN",
                           [[0, 0], [0, 7], [0, 14], [7, 0], [14, 0], [14, 7],
                            [14, 14], [7, 7], [5, 12]])]),
        path_case("PATH_T8_MANY_SMALL", [
            path_structure("P8A", "OPEN",
                           [[0, 0], [0, 7], [0, 14], [7, 0], [14, 0], [14, 7],
                            [12, 5]]),
            path_structure("P8B", "CENTER_GATE",
                           [[0, 0], [14, 0], [0, 14], [3, 3], [11, 2],
                            [2, 11]])]),
        path_case("PATH_T9_MIXED", [
            path_structure("P9A", "HORIZONTAL_GATE",
                           [[0, 0], [14, 0], [0, 14], [3, 3], [11, 2], [6, 12],
                            [2, 5]]),
            path_structure("P9B", "DOUBLE_GATE",
                           [[0, 0], [2, 8], [12, 4]])]),
    ]
    knap_new = [
        knap_case("KNAP_T4_TAU_EDGE", [
            knap_structure("K4", _ITEMS["K4"], 30, [5, 9, 13])]),
        knap_case("KNAP_T5_TAU_EXACT", [
            knap_structure("K5", _ITEMS["K5"], 40, [7, 14, 21, 28])]),
        knap_case("KNAP_T6_TIE_RACE", [
            knap_structure("K6A", _ITEMS["K6A"], 30, [6, 12, 18, 24, 30]),
            knap_structure("K6B", _ITEMS["K6B"], 35, [5, 13, 21, 29, 35])]),
        knap_case("KNAP_T7_OVER_BUDGET", [
            knap_structure("K7", _ITEMS["K7"], 39,
                           [4, 9, 14, 19, 24, 29, 34, 39])]),
        knap_case("KNAP_T8_MANY_SMALL", [
            knap_structure("K8A", _ITEMS["K8A"], 29, [4, 8, 12, 16, 20, 24, 28]),
            knap_structure("K8B", _ITEMS["K8B"], 31, [6, 11, 16, 21, 26, 31]),
            knap_structure("K8C", _ITEMS["K8C"], 24, [5, 9, 13, 17, 21])]),
        knap_case("KNAP_T9_MIXED", [
            knap_structure("K9A", _ITEMS["K9A"], 24,
                           [3, 6, 9, 12, 15, 18, 21, 24]),
            knap_structure("K9B", _ITEMS["K9B"], 19, [4, 10, 16]),
            knap_structure("K9C", _ITEMS["K9C"], 38, [8, 15, 23, 31])]),
    ]

    by_domain = {d["domain"]: dict(d) for d in v1_cases["domains"]}
    assert set(by_domain) == {"SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK"}
    out_domains = []
    for domain, new_cases in (("SAT_PROPAGATION", sat_new),
                              ("PATH_PLANNING", path_new),
                              ("KNAPSACK", knap_new)):
        d = by_domain[domain]
        carried = json.loads(json.dumps(d["cases"]))  # deep copy, byte-stable
        assert len(carried) == 3
        ids = [c["case_id"] for c in carried]
        assert not set(ids) & {c["case_id"] for c in new_cases}
        out_domains.append({
            "domain": domain,
            "charged_unit": d["charged_unit"],
            "cases": carried + new_cases,
        })
        assert len(out_domains[-1]["cases"]) == 9
    return {
        "schema": "p12-transfer-allocation-cases-expanded-v1",
        "protocol": "P12_ROBUSTNESS_PROTOCOL_V2",
        "allocator": dict(v1_cases["allocator"]),
        "domains": out_domains,
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "p12_transfer_cases_v1.json")) as f:
        v1_cases = json.load(f)
    assert v1_cases["schema"] == "p12-transfer-allocation-cases-v1"
    assert v1_cases["allocator"] == {"tau": TAU, "budget_B": BUDGET}
    expanded = build_expanded(v1_cases)
    total = sum(len(d["cases"]) for d in expanded["domains"])
    assert total == 27, total
    sys.stdout.write(json.dumps(expanded, indent=1) + "\n")


if __name__ == "__main__":
    main()
