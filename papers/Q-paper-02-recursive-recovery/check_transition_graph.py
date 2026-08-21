#!/usr/bin/env python3
"""Validate Q2's publication transition graph against the frozen evidence cut.

This validates publication integrity only. It does not decide scientific causality beyond
edges already declared in Q2_TRANSITION_GRAPH_V2.json.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRAPH_PATH = ROOT / "papers/Q-paper-02-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json"
EVIDENCE_CUT = "ca7df1055a43f97eaf8d142a62011c4c261af368"

EXPECTED_NODE_COUNT = 23
EXPECTED_EDGE_COUNT = 13
EXPECTED_MAIN_CHAIN_NODES = {
    "R6M_EXACT_THREE_TARE",
    "R6N_SUPPORT_DOMINANCE",
    "R6O_ENLARGED_TAG",
    "R6P_SUPPORT2_FINITE_CLOSURE",
    "R6Q_REGIME_PREDICATE",
    "R6R_FRESH_SUBJECT",
    "R6S_ALL_N_SUPPORT2",
    "QG5_CLOSED_FORM_FORECAST",
    "QG5B_BPRIME_REPAIR",
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


def main() -> int:
    data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if data.get("publication_cut") != EVIDENCE_CUT:
        errors.append("PUBLICATION_CUT_MISMATCH")

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

    artifacts: dict[str, str] = {}
    for node in nodes:
        node_id = node.get("id")
        artifact = node.get("artifact")
        disposition = node.get("disposition")
        if not node_id or not artifact or not disposition:
            errors.append(f"INCOMPLETE_NODE:{node}")
            continue
        path = ROOT / artifact
        if not path.is_file():
            errors.append(f"MISSING_ARTIFACT:{node_id}:{artifact}")
            continue
        try:
            cut_blob = git("rev-parse", f"{EVIDENCE_CUT}:{artifact}")
        except subprocess.CalledProcessError:
            errors.append(f"ARTIFACT_NOT_PRESENT_AT_CUT:{node_id}:{artifact}")
            continue
        current_blob = git("hash-object", artifact)
        if current_blob != cut_blob:
            errors.append(
                f"ARTIFACT_DRIFT_SINCE_Q2_CUT:{node_id}:{artifact}:{cut_blob}->{current_blob}"
            )
        artifacts[node_id] = cut_blob

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

    missing_main_nodes = EXPECTED_MAIN_CHAIN_NODES - node_ids
    if missing_main_nodes:
        errors.append(f"MISSING_MAIN_CHAIN_NODES:{sorted(missing_main_nodes)}")
    missing_main_edges = EXPECTED_MAIN_CHAIN_EDGES - set(edge_pairs)
    if missing_main_edges:
        errors.append(f"MISSING_MAIN_CHAIN_EDGES:{sorted(missing_main_edges)}")

    standalone = set(data.get("standalone_negative_or_absorbed_nodes_without_asserted_successor_edge", []))
    if not standalone <= node_ids:
        errors.append(f"UNKNOWN_STANDALONE_NODES:{sorted(standalone-node_ids)}")
    outbound = {src for src, _ in edge_pairs}
    accidentally_linked = standalone & outbound
    if accidentally_linked:
        errors.append(f"STANDALONE_NODE_GAINED_SUCCESSOR:{sorted(accidentally_linked)}")

    # Every narrative-visible negative/donor class remains visible as a node instead of being
    # collapsed into its successor.
    negative_tokens = ("NEGATIVE", "REFUTED", "DONOR_ABSORBED", "MIXED", "PARTIAL")
    negative_nodes = [
        n["id"] for n in nodes
        if any(tok in n.get("disposition", "") for tok in negative_tokens)
    ]
    if len(negative_nodes) < 10:
        errors.append(f"NEGATIVE_VISIBILITY_REGRESSION:{len(negative_nodes)}")

    if errors:
        print("Q2_TRANSITION_GRAPH_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q2_TRANSITION_GRAPH_CHECK=PASS")
    print(f"PUBLICATION_CUT={EVIDENCE_CUT}")
    print(f"NODES={len(nodes)}")
    print(f"EDGES={len(edges)}")
    print(f"NEGATIVE_OR_PARTIAL_NODES={len(negative_nodes)}")
    print(f"STANDALONE_WITHOUT_INVENTED_SUCCESSOR={len(standalone)}")
    print(f"CUT_BOUND_ARTIFACTS={len(artifacts)}")
    print("SCIENTIFIC_CAUSALITY_AUTHORITY=NOT_GRANTED_BY_VALIDATOR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
