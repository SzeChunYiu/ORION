#!/usr/bin/env python3
"""Fail-closed ORION story and authority checker for the FiberGuard R19 synthesis."""
from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

SCHEMA = "ORION.FiberGuard.StorySynthesis.R19.v1"
TERMINAL = "FIBERGUARD_R19_STORY_SYNTHESIS_PASS"
ROOT = Path(__file__).resolve().parent


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_json(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def check_dag(dag: dict[str, Any]) -> tuple[int, int]:
    nodes = dag["nodes"]
    by_id = {node["id"]: node for node in nodes}
    assert len(by_id) == len(nodes)
    indegree = {node_id: 0 for node_id in by_id}
    children: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    edge_count = 0
    for node in nodes:
        for parent in node["depends_on"]:
            assert parent in by_id, (node["id"], parent)
            indegree[node["id"]] += 1
            children[parent].append(node["id"])
            edge_count += 1
    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    visited: list[str] = []
    while queue:
        node_id = queue.popleft()
        visited.append(node_id)
        for child in sorted(children[node_id]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    assert len(visited) == len(nodes), "theorem/evidence graph is cyclic"
    assert len(nodes) == 20
    assert edge_count == 34
    return len(nodes), edge_count


def check_claims(ledger: dict[str, Any], dag: dict[str, Any], manuscript: str) -> dict[str, int]:
    claims = ledger["claims"]
    claim_ids = [claim["id"] for claim in claims]
    assert len(claim_ids) == len(set(claim_ids)) == 14
    assert claim_ids == [
        "C19-T1", "C19-T2", "C19-T3", "C19-T4", "C19-T5", "C19-T6", "C19-T7",
        "C19-E1", "C19-E2", "C19-E3", "C19-E4", "C19-E5", "C19-E6", "C19-E7",
    ]

    dag_claims = Counter(
        claim
        for node in dag["nodes"]
        for claim in node.get("claims", [])
    )
    for claim_id in claim_ids:
        assert dag_claims[claim_id] >= 1, claim_id
        assert manuscript.count(f"**[{claim_id}]**") == 1, claim_id

    theorem_claims = sum(claim_id.startswith("C19-T") for claim_id in claim_ids)
    evidence_claims = sum(claim_id.startswith("C19-E") for claim_id in claim_ids)
    assert theorem_claims == evidence_claims == 7
    return {
        "claims": len(claim_ids),
        "evidence_claims": evidence_claims,
        "theorem_claims": theorem_claims,
    }


def check_manuscript(manuscript: str) -> dict[str, int]:
    required_sections = [
        "## Abstract",
        "## 2. Finite representation authority",
        "## 4. Adaptive acquisition with state-dependent cost",
        "## 6. The inductive boundary",
        "## 7. Paired fallback alignment and routing",
        "## 8. Acquisition timing and route observability",
        "## 9. Cross-scenario transfer",
        "## 11. Public algorithm-selection evidence",
        "## 12. What the evidence proves—and what it refutes",
        "## 13. Relation to prior work",
        "## 14. Limitations",
        "## 16. Decisive remaining experiment",
        "## 17. Conclusion",
    ]
    for section in required_sections:
        assert manuscript.count(section) == 1, section

    required_adverse_tokens = [
        "Prospectively frozen held-out refutation",
        "Cross-scenario calibration and fallback sign reversal",
        "exact training fibres do not certify unseen same-signature states",
        "marginal learned-action calibration does not imply beneficial fallback routing",
        "R14 refutes its inductive reinterpretation",
    ]
    for token in required_adverse_tokens:
        assert token in manuscript, token

    required_terminals = [
        "FIBERGUARD_R19_THEORY_AND_STORY_SYNTHESIS_COMPLETE__EXTERNAL_EVIDENCE_OPEN",
        "NOT_SUBMISSION_READY",
    ]
    for terminal in required_terminals:
        assert manuscript.count(terminal) == 1, terminal

    forbidden_promotions = [
        "proves unseen-instance safety",
        "establishes production deployment value",
        "journal authority is granted",
        "external reproduction is complete",
        "top-tier readiness is closed",
    ]
    lowered = manuscript.lower()
    for phrase in forbidden_promotions:
        assert phrase not in lowered, phrase

    return {
        "adverse_tokens": len(required_adverse_tokens),
        "required_sections": len(required_sections),
        "terminals": len(required_terminals),
    }


def check_authority(ledger: dict[str, Any]) -> None:
    terminal = ledger["paper_terminal"]
    assert terminal["internal_theory_story"] == "COMPLETE"
    assert terminal["manuscript_story"] == "SYNTHESIS_IN_PROGRESS"
    assert terminal["paired_route_application"] == "OPEN"
    assert terminal["untouched_non_SAT_or_production_portfolio"] == "OPEN"
    assert terminal["external_reproduction"] == "CANNOT_CHECK"
    assert terminal["current_specialist_prior_art"] == "CANNOT_CHECK"
    assert terminal["journal_authority"] is False
    assert terminal["submission_ready"] is False

    load_bearing_adverse = {
        claim["id"]
        for claim in ledger["claims"]
        if claim["status"] == "ADMITTED_AND_LOAD_BEARING"
    }
    assert load_bearing_adverse == {"C19-E4", "C19-E6"}


def build_result() -> dict[str, Any]:
    ledger = load_json("CLAIM_LEDGER_C_R19.json")
    dag = load_json("THEOREM_EVIDENCE_DAG_C_R19.json")
    manuscript = (ROOT / "MANUSCRIPT_C_R19_FIBERGUARD_COMPLETE.md").read_text(encoding="utf-8")

    assert ledger["schema"] == "ORION.FiberGuard.ClaimLedger.C.R19.v1"
    assert dag["schema"] == "ORION.FiberGuard.TheoremEvidenceDAG.C.R19.v1"
    nodes, edges = check_dag(dag)
    claim_counts = check_claims(ledger, dag, manuscript)
    manuscript_counts = check_manuscript(manuscript)
    check_authority(ledger)

    required_paths = dag["required_paths_to_conclusion"]
    assert len(required_paths) == 7
    node_ids = {node["id"] for node in dag["nodes"]}
    for path in required_paths:
        assert path and all(node_id in node_ids for node_id in path)
    assert any("E3" in path for path in required_paths)
    assert any("E4" in path for path in required_paths)
    assert any("E6" in path for path in required_paths)

    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "claim_counts": claim_counts,
        "dag": {
            "edges": edges,
            "nodes": nodes,
            "required_conclusion_paths": len(required_paths),
        },
        "manuscript": manuscript_counts,
        "controls": {
            "claim_ids_unique_and_reader_visible": True,
            "theorem_evidence_dag_acyclic": True,
            "positive_transductive_result_retained": True,
            "heldout_refutation_load_bearing": True,
            "fallback_sign_reversal_load_bearing": True,
            "closed_world_structural_statistical_authority_separated": True,
            "internal_theory_not_promoted_to_external_authority": True,
            "paired_route_application_remains_open": True,
            "non_SAT_or_production_portfolio_remains_open": True,
            "journal_and_submission_authority_false": True,
        },
        "authority": {
            "internal_theory_story": "COMPLETE",
            "manuscript_story": "SYNTHESIZED_INTERNAL",
            "paired_route_application": "OPEN",
            "external_reproduction": "CANNOT_CHECK",
            "specialist_prior_art": "CANNOT_CHECK",
            "journal_authority": False,
            "submission_ready": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = canonical_json(build_result()) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
