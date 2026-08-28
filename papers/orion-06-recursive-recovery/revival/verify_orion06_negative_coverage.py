#!/usr/bin/env python3
"""Recompute ORION-06 negative visibility and mechanism dispositions."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROTOCOL = HERE / "ORION06_NEGATIVE_COVERAGE_PROTOCOL.json"
GRAPH = ROOT / "papers/orion-06-recursive-recovery/Q2_TRANSITION_GRAPH_V2.json"
INVENTORY = ROOT / "papers/orion-06-recursive-recovery/Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json"

ROW_RULES = {
    "R2_KNOWN_OPERATOR_TRANSFER": ("METHOD_SELECTION", "generic V4 table learner", "RETAINED_NEGATIVE", "exact 1.0 tie in all four folds with held-out support fully seen; the ORION-specific policy is donor-absorbed in this frozen known-operator claim"),
    "R3B_JOINT_OBLIGATION_BINDING": ("OBLIGATION_REPRESENTATION", "P7/P4 joint-bound obligation donor", "RETAINED_NEGATIVE", "joint binding attains 1.0 on 4,800 exact-synthetic cases while the local-view candidate ceiling is 0.5"),
    "R4C_H2_REGIME_LIMITED": ("EVALUATION_OBJECTIVE", "frozen direct-unitary coverage gate", "UNFINISHED", "the receipt explicitly requires actual Restore/outer-SELECT Pareto accounting; no registered executed successor edge exists"),
    "R5B_PROOF_OUTER_REPLAY": ("RESOURCE_PROJECTION", "incumbent outer-resource vector", "UNFINISHED", "the advantage changes sign across projections and the named controlled-SELECT-aware new-subject attack is unexecuted"),
    "R6I_EXACT_RANK2": ("METHOD_LANGUAGE", "registered incumbent envelope", "UNFINISHED", "zero strict wins on both subjects localizes method-language inadequacy; no asserted successor edge licenses adjacent results as its revival"),
    "R6K_EXACT_RESTORE_FACTOR": ("METHOD_LANGUAGE", "R6J/registered incumbent envelope", "UNFINISHED", "zero strict wins after joint Tag/Restore factoring localizes method-language inadequacy; no asserted successor edge exists"),
    "N1C_TYPED_FAILURE_STATE": ("POLICY_SELECTION", "ideal value-of-information parent", "RETAINED_NEGATIVE", "typed scoped learner ties the ideal VOI parent exactly (paired solve delta 0.0), so policy novelty is donor-absorbed while state value remains bounded"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _excluded_count(excluded: dict[str, list[str]]) -> int:
    return sum(len(rows) for rows in excluded.values())


def build_audit(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    graph_path = root / GRAPH.relative_to(ROOT)
    inventory_path = root / INVENTORY.relative_to(ROOT)
    protocol_path = root / PROTOCOL.relative_to(ROOT)
    graph = json.loads(graph_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    required = protocol["required_standalone_set"]
    observed = graph["standalone_negative_or_absorbed_nodes_without_asserted_successor_edge"]
    if observed != required:
        raise AssertionError({"standalone_set_drift": [required, observed]})
    nodes = {node["id"]: node for node in graph["nodes"]}
    standalone_rows = []
    for node_id in required:
        stage, comparator, outcome, proof = ROW_RULES[node_id]
        node = nodes[node_id]
        artifact = root / node["artifact"]
        if not artifact.is_file():
            raise FileNotFoundError(artifact)
        standalone_rows.append({
            "id": node_id,
            "artifact": node["artifact"],
            "artifact_sha256": sha256(artifact),
            "recorded_disposition": node["disposition"],
            "mechanism_stage": stage,
            "strongest_parent_or_comparator": comparator,
            "revival_outcome": outcome,
            "mechanistic_disposition": proof,
            "asserted_successor_edge": False,
        })
    denominator = {"eligible": inventory["counts"]["universe"], "included": len(graph["nodes"]), "excluded": _excluded_count(inventory["excluded_28"]), "edges": len(graph["edges"])}
    expected = {"eligible": 51, "included": 23, "excluded": 28, "edges": 13}
    if denominator != expected or denominator["eligible"] != denominator["included"] + denominator["excluded"]:
        raise AssertionError({"denominator_drift": denominator})
    return {
        "schema": "ORION.ORION06.NegativeCoverageAudit.v1",
        "date": "2026-08-27",
        "terminal": "ORION06_NEGATIVE_VISIBILITY_RECOMPUTED__FOUR_UNFINISHED__GENERAL_METHOD_CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "source_hashes": {"protocol": sha256(protocol_path), "transition_graph": sha256(graph_path), "eligible_inventory": sha256(inventory_path)},
        "denominator": denominator,
        "standalone_rows": standalone_rows,
        "cross_domain_general_method": {
            "mechanism_stage": "EXTERNAL_COMPARATIVE_EVALUATION",
            "strongest_parent_or_comparator": "matched NAIVE_ITERATION and DONOR_STOP workflows across prospective Domains B/C",
            "revival_outcome": "CANNOT_CHECK",
            "precondition": "no prospectively admitted non-quantum formal programme and computational/empirical programme with matched workflow budgets and independent scoring exists under the frozen protocol",
            "disposition": "blocked/unfinished, not unsolvable; bounded single-programme case-study evidence remains separate",
        },
        "authority": {"cross_domain_effectiveness": False, "productivity_superiority": False, "external_independence": False, "journal_or_submission": False, "final_freeze": False},
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = build_audit(args.root)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print("ORION06_NEGATIVE_COVERAGE=PASS")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
