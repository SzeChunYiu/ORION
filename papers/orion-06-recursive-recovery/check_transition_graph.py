#!/usr/bin/env python3
"""Validate Q2's publication transition graph and declared receipt denominator.

This validates publication integrity only. It does not decide scientific causality beyond
edges already declared in Q2_TRANSITION_GRAPH_V2.json.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / "papers/orion-06-recursive-recovery"
GRAPH_PATH = BASE / "Q2_TRANSITION_GRAPH_V2.json"
INVENTORY_PATH = BASE / "Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json"
EVIDENCE_CUT = "ca7df1055a43f97eaf8d142a62011c4c261af368"

EXPECTED_NODE_COUNT = 23
EXPECTED_EDGE_COUNT = 13
EXPECTED_UNIVERSE = 51
EXPECTED_EXCLUDED = 28
EXPECTED_MAIN_CHAIN_NODES = {
    "R6M_EXACT_THREE_TARE", "R6N_SUPPORT_DOMINANCE", "R6O_ENLARGED_TAG",
    "R6P_SUPPORT2_FINITE_CLOSURE", "R6Q_REGIME_PREDICATE", "R6R_FRESH_SUBJECT",
    "R6S_ALL_N_SUPPORT2", "QG5_CLOSED_FORM_FORECAST", "QG5B_BPRIME_REPAIR",
}
EXPECTED_MAIN_CHAIN_EDGES = {
    ("R6M_EXACT_THREE_TARE", "R6N_SUPPORT_DOMINANCE"),
    ("R6N_SUPPORT_DOMINANCE", "R6O_ENLARGED_TAG"),
    ("R6O_ENLARGED_TAG", "R6P_SUPPORT2_FINITE_CLOSURE"),
    ("R6P_SUPPORT2_FINITE_CLOSURE", "R6Q_REGIME_PREDICATE"),
    ("R6Q_REGIME_PREDICATE", "R6R_FRESH_SUBJECT"),
    ("R6P_SUPPORT2_FINITE_CLOSURE", "R6S_ALL_N_SUPPORT2"),
    ("R6R_FRESH_SUBJECT", "QG5_CLOSED_FORM_FORECAST"),
    ("QG5_CLOSED_FORM_FORECAST", "QG5B_BPRIME_REPAIR"),
}


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return proc.stdout.strip()


def cut_bind(path: str, errors: list[str], label: str) -> str | None:
    p = ROOT / path
    if not p.is_file():
        errors.append(f"MISSING_{label}:{path}")
        return None
    try:
        cut_blob = git("rev-parse", f"{EVIDENCE_CUT}:{path}")
    except subprocess.CalledProcessError:
        errors.append(f"{label}_NOT_PRESENT_AT_CUT:{path}")
        return None
    current_blob = git("hash-object", path)
    if current_blob != cut_blob:
        errors.append(f"{label}_DRIFT_SINCE_CUT:{path}:{cut_blob}->{current_blob}")
    return cut_blob


def flatten_excluded(excluded: dict[str, list[str]]) -> list[str]:
    out: list[str] = []
    for key, values in excluded.items():
        if not isinstance(values, list):
            raise ValueError(f"excluded category {key} must be a list")
        out.extend(values)
    return out


def main() -> int:
    data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    inv = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if data.get("publication_cut") != EVIDENCE_CUT:
        errors.append("GRAPH_PUBLICATION_CUT_MISMATCH")
    if inv.get("publication_cut") != EVIDENCE_CUT:
        errors.append("INVENTORY_PUBLICATION_CUT_MISMATCH")

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if len(nodes) != EXPECTED_NODE_COUNT:
        errors.append(f"NODE_COUNT_DRIFT:{len(nodes)}!={EXPECTED_NODE_COUNT}")
    if len(edges) != EXPECTED_EDGE_COUNT:
        errors.append(f"EDGE_COUNT_DRIFT:{len(edges)}!={EXPECTED_EDGE_COUNT}")

    ids = [node.get("id") for node in nodes]
    if len(ids) != len(set(ids)):
        errors.append("DUPLICATE_NODE_ID")
    node_ids = set(ids)

    graph_artifacts: dict[str, str] = {}
    for node in nodes:
        node_id = node.get("id")
        artifact = node.get("artifact")
        disposition = node.get("disposition")
        if not node_id or not artifact or not disposition:
            errors.append(f"INCOMPLETE_NODE:{node}")
            continue
        blob = cut_bind(artifact, errors, f"GRAPH_ARTIFACT:{node_id}")
        if blob:
            graph_artifacts[node_id] = blob

    edge_pairs: list[tuple[str, str]] = []
    for edge in edges:
        src = edge.get("from")
        dst = edge.get("to")
        rel = edge.get("relation")
        reason = edge.get("reason")
        if src not in node_ids or dst not in node_ids:
            errors.append(f"EDGE_ENDPOINT_MISSING:{src}->{dst}")
        if src == dst:
            errors.append(f"SELF_EDGE:{src}")
        if not rel or not reason:
            errors.append(f"UNJUSTIFIED_EDGE:{src}->{dst}")
        edge_pairs.append((src, dst))
    if len(edge_pairs) != len(set(edge_pairs)):
        errors.append("DUPLICATE_EDGE")

    if EXPECTED_MAIN_CHAIN_NODES - node_ids:
        errors.append(f"MISSING_MAIN_CHAIN_NODES:{sorted(EXPECTED_MAIN_CHAIN_NODES-node_ids)}")
    if EXPECTED_MAIN_CHAIN_EDGES - set(edge_pairs):
        errors.append(f"MISSING_MAIN_CHAIN_EDGES:{sorted(EXPECTED_MAIN_CHAIN_EDGES-set(edge_pairs))}")

    standalone = set(data.get("standalone_negative_or_absorbed_nodes_without_asserted_successor_edge", []))
    if not standalone <= node_ids:
        errors.append(f"UNKNOWN_STANDALONE_NODES:{sorted(standalone-node_ids)}")
    outbound = {src for src, _ in edge_pairs}
    if standalone & outbound:
        errors.append(f"STANDALONE_NODE_GAINED_SUCCESSOR:{sorted(standalone&outbound)}")

    negative_tokens = ("NEGATIVE", "REFUTED", "DONOR_ABSORBED", "MIXED", "PARTIAL")
    negative_nodes = [n["id"] for n in nodes if any(t in n.get("disposition", "") for t in negative_tokens)]
    if len(negative_nodes) < 10:
        errors.append(f"NEGATIVE_VISIBILITY_REGRESSION:{len(negative_nodes)}")

    # Declared selection denominator: exactly partition 51 cut-bound receipts into 23
    # graph nodes and 28 explicit exclusions.
    base40 = inv.get("base_receipts_40", [])
    aug11 = inv.get("augmentation_11", [])
    included = inv.get("included_graph_nodes_23", [])
    try:
        excluded = flatten_excluded(inv.get("excluded_28", {}))
    except ValueError as exc:
        errors.append(f"INVALID_EXCLUSION_SHAPE:{exc}")
        excluded = []
    universe = base40 + aug11

    if len(base40) != 40 or len(aug11) != 11 or len(universe) != EXPECTED_UNIVERSE:
        errors.append(f"INVENTORY_UNIVERSE_COUNT_DRIFT:{len(base40)}+{len(aug11)}={len(universe)}")
    if len(included) != EXPECTED_NODE_COUNT:
        errors.append(f"INVENTORY_INCLUDED_COUNT_DRIFT:{len(included)}")
    if len(excluded) != EXPECTED_EXCLUDED:
        errors.append(f"INVENTORY_EXCLUDED_COUNT_DRIFT:{len(excluded)}")
    if len(universe) != len(set(universe)):
        errors.append("INVENTORY_DUPLICATE_UNIVERSE_PATH")
    if set(included) & set(excluded):
        errors.append("INVENTORY_INCLUDED_EXCLUDED_OVERLAP")
    if set(included) | set(excluded) != set(universe):
        errors.append("INVENTORY_DOES_NOT_PARTITION_UNIVERSE")

    graph_paths = {n.get("artifact") for n in nodes}
    if graph_paths != set(included):
        errors.append(
            f"GRAPH_INVENTORY_MISMATCH:graph_only={sorted(graph_paths-set(included))}:"
            f"inventory_only={sorted(set(included)-graph_paths)}"
        )

    # Every denominator receipt existed at the frozen cut and remains byte-identical on
    # the checked tree; this prevents later main drift from quietly changing Q2's case set.
    denominator_blobs = 0
    for path in universe:
        if cut_bind(path, errors, "INVENTORY_RECEIPT"):
            denominator_blobs += 1

    if errors:
        print("Q2_TRANSITION_GRAPH_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q2_TRANSITION_GRAPH_CHECK=PASS")
    print(f"PUBLICATION_CUT={EVIDENCE_CUT}")
    print(f"DECLARED_RECEIPT_UNIVERSE={len(universe)}")
    print(f"INCLUDED_GRAPH_NODES={len(nodes)}")
    print(f"EXCLUDED_WITH_REASON={len(excluded)}")
    print(f"ASSERTED_SUCCESSOR_EDGES={len(edges)}")
    print(f"NEGATIVE_OR_PARTIAL_NODES={len(negative_nodes)}")
    print(f"STANDALONE_WITHOUT_INVENTED_SUCCESSOR={len(standalone)}")
    print(f"CUT_BOUND_DENOMINATOR_RECEIPTS={denominator_blobs}")
    print("SCIENTIFIC_CAUSALITY_AUTHORITY=NOT_GRANTED_BY_VALIDATOR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
