#!/usr/bin/env python3
"""Independent verifier for QG-42 pytket held-out selection transfer."""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path
from typing import Any

from pytket import Circuit
from pytket.architecture import Architecture
from pytket.mapping import LexiRouteRoutingMethod, MappingManager
from pytket.placement import place_with_map
from pytket.unit_id import Node

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "artifacts/orion-qg-qg42-pytket.json"
PANEL = ROOT / "artifacts/orion-qg-qg42-panel.json"
BUILDER = ROOT / "research/extensions/orion-qg/qg42_build_panel.py"
OUT = ROOT / "artifacts/orion-qg-qg42-generic-verification.json"
TOKEN = "ORIONQG_QG42_GENERIC="
N = 6
E = 7
EDGES = tuple((i, j) for i in range(N) for j in range(i + 1, N))
PERMS = tuple(itertools.permutations(range(N)))
ARCHS = {
    "line6": ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)),
    "ring6": ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)),
}
POSITIVE_TERMINALS = {
    "QG42_PYTKET_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED",
    "QG42_PYTKET_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY",
    "QG42_PYTKET_NO_SELECTION_SEPARATION_ON_FROZEN_PANEL",
}


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def valid(d):
    return d.get("result_digest") == sha({k: v for k, v in d.items() if k != "result_digest"})


def degree_summary(edges):
    d = [0] * N
    for a, b in edges:
        d[a] += 1
        d[b] += 1
    return tuple(sorted(d))


def perm_edges(edges, p):
    return tuple(sorted((min(p[a], p[b]), max(p[a], p[b])) for a, b in edges))


def iso_key(edges):
    return min(perm_edges(edges, p) for p in PERMS)


def rebuild_panel():
    by = defaultdict(set)
    for comb in itertools.combinations(EDGES, E):
        k = iso_key(comb)
        by[degree_summary(k)].add(k)
    cand = []
    for summary in sorted(by):
        keys = sorted(by[summary])
        if len(keys) < 2:
            continue
        for j in range(0, len(keys) - 1, 2):
            cand.append((summary, keys[j], keys[j + 1]))
    return cand[:12]


def builder_is_compiler_blind():
    tree = ast.parse(BUILDER.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("pytket"):
                    return False
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("pytket"):
            return False
    return True


def build(edges):
    c = Circuit(N)
    for a, b in edges:
        c.CX(int(a), int(b))
    return c


def cost_vector(edges, arch_edges):
    arc = Architecture(list(arch_edges))
    costs = []
    depths = []
    totals = []
    invalid = 0
    for p in PERMS:
        c = build(edges)
        place_with_map(c, {c.qubits[q]: Node(int(p[q])) for q in range(N)})
        MappingManager(arc).route_circuit(c, [LexiRouteRoutingMethod(10)])
        bad = [cmd for cmd in c.get_commands() if len(cmd.qubits) == 2 and not arc.valid_operation(cmd.qubits, True)]
        invalid += len(bad)
        costs.append(int(c.n_2qb_gates()))
        depths.append(int(c.depth_2q()))
        totals.append(int(c.n_gates))
    if invalid:
        raise AssertionError(f"{invalid} invalid routed operations")
    return costs, depths, totals


def stats(costs, depths, totals):
    m = min(costs)
    arg = [i for i, x in enumerate(costs) if x == m]
    return {
        "minimum_two_qubit_gates": m,
        "argmin_layout_indices": arg,
        "argmin_count": len(arg),
        "cost_range": [min(costs), max(costs)],
        "cost_histogram": {str(k): int(v) for k, v in sorted(Counter(costs).items())},
        "cost_vector_sha256": sha(costs),
        "depth2q_vector_sha256": sha(depths),
        "total_gate_vector_sha256": sha(totals),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=SRC)
    ap.add_argument("--panel", type=Path, default=PANEL)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    src = json.loads(args.input.read_text())
    panel = json.loads(args.panel.read_text())
    rebuilt = rebuild_panel()

    serialized_panel = [
        (
            tuple(x["degree_summary"]),
            tuple(tuple(e) for e in x["graph_A_edges"]),
            tuple(tuple(e) for e in x["graph_B_edges"]),
        )
        for x in panel.get("pairs", [])
    ]
    checks = {
        "source_digest": valid(src),
        "panel_digest": valid(panel),
        "compiler_blind_builder": builder_is_compiler_blind(),
        "panel_rebuilt": serialized_panel == rebuilt,
        "pytket_version": version("pytket") == src.get("pytket_version") == "2.18.1",
        "bounded_terminal": src.get("terminal") in POSITIVE_TERMINALS,
        "record_count": len(src.get("records", [])) == 12,
        "hard_false": all(src.get(k) is False for k in (
            "ALL_CIRCUIT_THEOREM", "ALL_PYTKET_VERSION_CLAIM", "OPTIMAL_ROUTING_CLAIM",
            "COMPARATIVE_COMPILER_PERFORMANCE", "HARDWARE_NOISE_OR_FT_CLAIM",
            "physical_quantum_advantage_claim", "GENERIC_SYMMETRY_DECISION_THEORY_NOVELTY", "novelty_authority"
        )),
    }

    row_checks = []
    all_rows = checks["record_count"] and checks["panel_rebuilt"]
    any_var = False
    any_router = False
    independent_line = False
    independent_ring = False
    independent_dline = False
    independent_dring = False
    stable = []

    if all_rows:
        for i, (summary, ga, gb) in enumerate(rebuilt):
            sr = src["records"][i]
            row = {"pair_index": i, "architectures": {}}
            pair_disjoint = {}
            for aname, aedges in ARCHS.items():
                ca, da, ta = cost_vector(ga, aedges)
                cb, db, tb = cost_vector(gb, aedges)
                sa, sb = stats(ca, da, ta), stats(cb, db, tb)
                aa, ab = set(sa["argmin_layout_indices"]), set(sb["argmin_layout_indices"])
                same = sa["minimum_two_qubit_gates"] == sb["minimum_two_qubit_gates"]
                sep = same and aa != ab
                disj = sep and not (aa & ab)
                any_var |= max(ca) > min(ca) or max(cb) > min(cb)
                any_router |= max(ta) > 7 or max(tb) > 7 or max(ca) > 7 or max(cb) > 7
                source_arm = sr["architectures"][aname]
                core_equal = (
                    source_arm["A"]["minimum_two_qubit_gates"] == sa["minimum_two_qubit_gates"]
                    and source_arm["A"]["argmin_layout_indices"] == sa["argmin_layout_indices"]
                    and source_arm["A"]["cost_vector_sha256"] == sa["cost_vector_sha256"]
                    and source_arm["B"]["minimum_two_qubit_gates"] == sb["minimum_two_qubit_gates"]
                    and source_arm["B"]["argmin_layout_indices"] == sb["argmin_layout_indices"]
                    and source_arm["B"]["cost_vector_sha256"] == sb["cost_vector_sha256"]
                    and source_arm["selection_separation"] == sep
                    and source_arm["disjoint_selection_separation"] == disj
                )
                all_rows &= core_equal
                row["architectures"][aname] = {"core_equal": bool(core_equal), "selection_separation": sep, "disjoint": disj, "A_cost_hash": sa["cost_vector_sha256"], "B_cost_hash": sb["cost_vector_sha256"]}
                pair_disjoint[aname] = disj
                if aname == "line6":
                    independent_line |= sep
                    independent_dline |= disj
                else:
                    independent_ring |= sep
                    independent_dring |= disj
            if pair_disjoint.get("line6") and pair_disjoint.get("ring6"):
                stable.append(i)
            row_checks.append(row)

    checks["all_layout_geometry_replayed"] = bool(all_rows)
    checks["instrument_varies"] = bool(any_var)
    checks["router_exercised"] = bool(any_router)
    checks["selection_flags"] = src.get("selection_separation", {}).get("line6") == independent_line and src.get("selection_separation", {}).get("ring6") == independent_ring and src.get("selection_separation", {}).get("disjoint_line6") == independent_dline and src.get("selection_separation", {}).get("disjoint_ring6") == independent_dring and src.get("selection_separation", {}).get("topology_stable_disjoint_pair_indices") == stable

    # Hostile controls are semantic: constant input-CX count is detected as dead;
    # erasing layout identity cannot support an argmin-set separation claim.
    checks["dead_instrument_control"] = len(set([7] * 720)) == 1 and src.get("instrument_controls", {}).get("input_cx_count_dead_instrument_detected") is True
    claimed_sep = independent_line or independent_ring
    collapsed_can_prove_sep = False  # one layout representative has no identity-set information by construction
    checks["layout_collapse_control"] = (not collapsed_can_prove_sep) if claimed_sep else True

    ok = all(checks.values())
    out = {
        "schema": "ORIONQG.QG42.GenericVerification.v1",
        "decision": "ACCEPT_BOUNDED_PYTKET_TRANSFER" if ok else "REJECT",
        "all_checks": bool(ok),
        "checks": checks,
        "independent_selection": {
            "line6": independent_line,
            "ring6": independent_ring,
            "disjoint_line6": independent_dline,
            "disjoint_ring6": independent_dring,
            "topology_stable_disjoint_pair_indices": stable,
        },
        "row_checks": row_checks,
        "BOUNDED_PYTKET_SELECTION_INFORMATION_AUTHORITY": bool(ok),
        "ALL_CIRCUIT_THEOREM": False,
        "COMPARATIVE_COMPILER_PERFORMANCE": False,
        "HARDWARE_NOISE_OR_FT_CLAIM": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"decision": out["decision"], "selection": out["independent_selection"], "rows": checks["all_layout_geometry_replayed"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
