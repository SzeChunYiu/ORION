#!/usr/bin/env python3
"""QG-42 production compiler transfer on the prebuilt compiler-blind panel."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from importlib.metadata import version
from pathlib import Path
from typing import Any

from pytket import Circuit
from pytket.architecture import Architecture
from pytket.mapping import LexiRouteRoutingMethod, MappingManager
from pytket.placement import place_with_map
from pytket.unit_id import Node

ROOT = Path(__file__).resolve().parents[3]
PANEL = ROOT / "artifacts/orion-qg-qg42-panel.json"
PROTO = ROOT / "development/orion-qg-regime-geometry/QG42_PYTKET_HELDOUT_SELECTION_TRANSFER_PROTOCOL_V1.md"
OUT = ROOT / "artifacts/orion-qg-qg42-pytket.json"
TOKEN = "ORIONQG_QG42="
N = 6
LAYOUTS = tuple(itertools.permutations(range(N)))
ARCHS = {
    "line6": ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)),
    "ring6": ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)),
}


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def shaf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def valid(d: dict[str, Any]) -> bool:
    return d.get("result_digest") == sha({k: v for k, v in d.items() if k != "result_digest"})


def build(edges):
    c = Circuit(N)
    for a, b in edges:
        c.CX(int(a), int(b))
    return c


def architecture_nodes(uids):
    """Normalize routed single-index UnitIDs to the Node type required by pybind."""
    out = []
    for uid in uids:
        idx = tuple(uid.index)
        if len(idx) != 1:
            raise RuntimeError(f"unexpected routed UnitID index: {uid!r}")
        out.append(Node(int(idx[0])))
    return tuple(out)


def route_cost(edges, arch_edges, layout):
    c = build(edges)
    arc = Architecture(list(arch_edges))
    qmap = {c.qubits[q]: Node(int(layout[q])) for q in range(N)}
    place_with_map(c, qmap)
    route_return = bool(MappingManager(arc).route_circuit(c, [LexiRouteRoutingMethod(10)]))

    invalid = []
    for cmd in c.get_commands():
        if len(cmd.qubits) == 2:
            nodes = architecture_nodes(cmd.qubits)
            if not arc.valid_operation(nodes, True):
                invalid.append(str(cmd))
    if invalid:
        raise RuntimeError("architecture-invalid routed operation: " + invalid[0])

    return {
        "cost": int(c.n_2qb_gates()),
        "depth2q": int(c.depth_2q()),
        "total_gates": int(c.n_gates),
        "implicit_wireswaps": bool(c.has_implicit_wireswaps),
        "route_return": route_return,
    }


def eval_graph(edges, arch_edges):
    costs, depths, totals = [], [], []
    implicit = 0
    route_true = 0
    for layout in LAYOUTS:
        row = route_cost(edges, arch_edges, layout)
        costs.append(row["cost"])
        depths.append(row["depth2q"])
        totals.append(row["total_gates"])
        implicit += int(row["implicit_wireswaps"])
        route_true += int(row["route_return"])
    minimum = min(costs)
    argmin = [i for i, x in enumerate(costs) if x == minimum]
    return {
        "minimum_two_qubit_gates": minimum,
        "argmin_layout_indices": argmin,
        "argmin_count": len(argmin),
        "cost_range": [min(costs), max(costs)],
        "cost_histogram": {str(k): int(v) for k, v in sorted(Counter(costs).items())},
        "cost_vector_sha256": sha(costs),
        "depth2q_vector_sha256": sha(depths),
        "total_gate_vector_sha256": sha(totals),
        "implicit_wireswap_layout_count": implicit,
        "route_return_true_layout_count": route_true,
        "instrument_varies": max(costs) > min(costs),
        "router_exercised": max(totals) > 7 or max(costs) > 7,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=PANEL)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()

    panel = json.loads(args.panel.read_text())
    pkg = version("pytket")
    parent = {
        "panel_digest": valid(panel),
        "panel_terminal": panel.get("terminal") == "QG42_PANEL_FROZEN_BEFORE_ROUTING",
        "panel_count": len(panel.get("pairs", [])) == 12,
        "panel_compiler_blind": panel.get("PYTKET_IMPORTED") is False,
        "protocol": panel.get("protocol_sha256") == shaf(PROTO),
        "pytket_version": pkg == "2.18.1",
    }

    graph_cache = {}
    records = []
    any_var = False
    any_router = False
    for pair in panel.get("pairs", []):
        rec = {
            "pair_index": pair["pair_index"],
            "degree_summary": pair["degree_summary"],
            "graph_A_edges": pair["graph_A_edges"],
            "graph_B_edges": pair["graph_B_edges"],
            "architectures": {},
        }
        for arch_name, arch_edges in ARCHS.items():
            vals = []
            for side in ("A", "B"):
                edges = tuple(tuple(x) for x in pair[f"graph_{side}_edges"])
                key = (edges, arch_name)
                if key not in graph_cache:
                    graph_cache[key] = eval_graph(edges, arch_edges)
                vals.append(graph_cache[key])
                any_var |= graph_cache[key]["instrument_varies"]
                any_router |= graph_cache[key]["router_exercised"]

            x, y = vals
            ax = set(x["argmin_layout_indices"])
            ay = set(y["argmin_layout_indices"])
            inter = sorted(ax & ay)
            same = x["minimum_two_qubit_gates"] == y["minimum_two_qubit_gates"]
            separates = same and ax != ay
            disjoint = separates and not inter
            rec["architectures"][arch_name] = {
                "A": x,
                "B": y,
                "same_optimum_value": same,
                "argmin_sets_differ": ax != ay,
                "argmin_intersection_count": len(inter),
                "argmin_intersection_indices": inter,
                "jaccard": len(inter) / len(ax | ay) if ax | ay else 1.0,
                "selection_separation": separates,
                "disjoint_selection_separation": disjoint,
            }
        records.append(rec)

    line = any(r["architectures"]["line6"]["selection_separation"] for r in records)
    ring = any(r["architectures"]["ring6"]["selection_separation"] for r in records)
    dline = any(r["architectures"]["line6"]["disjoint_selection_separation"] for r in records)
    dring = any(r["architectures"]["ring6"]["disjoint_selection_separation"] for r in records)
    stable = [
        r["pair_index"]
        for r in records
        if r["architectures"]["line6"]["disjoint_selection_separation"]
        and r["architectures"]["ring6"]["disjoint_selection_separation"]
    ]

    dead_cost = [7] * len(LAYOUTS)
    dead_detected = max(dead_cost) == min(dead_cost)

    if not all(parent.values()) or not any_var or not any_router or not dead_detected:
        terminal = "QG42_CANNOT_CHECK"
    elif line and ring:
        terminal = "QG42_PYTKET_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED"
    elif line or ring:
        terminal = "QG42_PYTKET_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY"
    else:
        terminal = "QG42_PYTKET_NO_SELECTION_SEPARATION_ON_FROZEN_PANEL"

    out = {
        "schema": "ORIONQG.QG42.PytketSelectionTransfer.v1",
        "terminal": terminal,
        "protocol_sha256": shaf(PROTO),
        "panel_result_digest": panel.get("result_digest"),
        "panel_digest": panel.get("panel_digest"),
        "pytket_version": pkg,
        "parent_checks": parent,
        "universe": {
            "pairs": len(records),
            "graphs": len(graph_cache) // len(ARCHS),
            "layouts_per_graph_per_architecture": len(LAYOUTS),
            "architectures": list(ARCHS),
            "primary_cost": "post-routing n_2qb_gates",
            "routing_method": "LexiRouteRoutingMethod(10)",
        },
        "records": records,
        "selection_separation": {
            "line6": line,
            "ring6": ring,
            "disjoint_line6": dline,
            "disjoint_ring6": dring,
            "topology_stable_disjoint_pair_indices": stable,
        },
        "instrument_controls": {
            "any_layout_dependent_cost": any_var,
            "router_exercised": any_router,
            "input_cx_count_dead_instrument_detected": dead_detected,
        },
        "BOUNDED_PYTKET_SELECTION_INFORMATION_AUTHORITY": terminal.startswith("QG42_PYTKET_"),
        "ALL_CIRCUIT_THEOREM": False,
        "ALL_PYTKET_VERSION_CLAIM": False,
        "OPTIMAL_ROUTING_CLAIM": False,
        "COMPARATIVE_COMPILER_PERFORMANCE": False,
        "HARDWARE_NOISE_OR_FT_CLAIM": False,
        "physical_quantum_advantage_claim": False,
        "GENERIC_SYMMETRY_DECISION_THEORY_NOVELTY": False,
        "novelty_authority": False,
    }
    out["result_digest"] = sha(out)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({
        "terminal": terminal,
        "line": line,
        "ring": ring,
        "disjoint_line": dline,
        "disjoint_ring": dring,
        "stable": stable,
        "instrument": out["instrument_controls"],
        "result_digest": out["result_digest"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
