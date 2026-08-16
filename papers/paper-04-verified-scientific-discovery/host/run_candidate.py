#!/usr/bin/env python3
"""Candidate-visible adapter for the frozen P4 protected campaign.

This program receives only opaque case ids and ``candidate_visible`` material.
It never accepts attack-family labels or protected gold. Exact content binding
is resolved through the production evidence resolver, and its authority terminal
is obtained from the production ORION non-compensatory hard-gate evaluator in
the frozen subject revision.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any

from orion.kernel.evidence import EvidenceStatus, resolve_evidence_ref
from orion.kernel.hard_gates import (
    HardGateContract,
    HardGateObservation,
    HardGateRequirement,
    HardGateState,
    evaluate_hard_gates,
)

GATE_IDS = (
    "EXACT_CONTENT_BINDING",
    "SOURCE_OWNERSHIP",
    "SEMANTIC_SUPPORT",
    "CHECKER_INDEPENDENCE",
    "CHECKER_DISCRIMINATION",
    "BEHAVIORAL_INFLUENCE",
    "EVALUATOR_CHRONOLOGY_INTEGRITY",
    "SEARCH_CONTAMINATION_CLEAR",
    "PROTECTED_ACCESS_CLEAR",
)


def _contract() -> HardGateContract:
    return HardGateContract(
        contract_id="P4.protected-authority.production-gates.v1",
        requirements=tuple(
            HardGateRequirement(gate_id, gate_id.replace("_", " ").lower())
            for gate_id in GATE_IDS
        ),
        frozen_at_round=0,
    )


def _read_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            raw = json.loads(line)
            if set(raw) != {"case_id", "candidate_visible"}:
                raise ValueError("candidate manifest may contain only case_id and candidate_visible")
            rows.append(raw)
    return rows


def _assigned_evidence(view: dict[str, Any]) -> dict[str, Any] | None:
    claim = view.get("claim", {})
    assigned = claim.get("assigned_evidence_id")
    evidence = view.get("evidence", [])
    if not isinstance(evidence, list):
        return None
    for item in evidence:
        if isinstance(item, dict) and item.get("evidence_id") == assigned:
            return item
    return None


def _content_binding_state(item: dict[str, Any] | None) -> HardGateState:
    if item is None:
        return HardGateState.CANNOT_CHECK
    content = item.get("content")
    actual_declared = item.get("content_hash")
    frozen_declared = item.get("declared_content_hash")
    provenance = item.get("provenance_hash")
    frozen_provenance = item.get("declared_provenance_hash")
    if not all(
        isinstance(value, str) and value
        for value in (
            content,
            actual_declared,
            frozen_declared,
            provenance,
            frozen_provenance,
        )
    ):
        return HardGateState.CANNOT_CHECK
    with tempfile.TemporaryDirectory(prefix="orion-p4-evidence-") as root:
        evidence_root = Path(root)
        artifact = evidence_root / "assigned-evidence.txt"
        artifact.write_text(content, encoding="utf-8")
        resolution = resolve_evidence_ref(
            f"evidence:assigned-evidence.txt@{frozen_declared}",
            {"evidence": evidence_root},
            require_digest=True,
        )
    if resolution.status is not EvidenceStatus.RESOLVED:
        return HardGateState.FAIL
    return (
        HardGateState.PASS
        if resolution.actual_digest == actual_declared
        and provenance == frozen_provenance
        else HardGateState.FAIL
    )


def _source_state(item: dict[str, Any] | None) -> HardGateState:
    if item is None:
        return HardGateState.CANNOT_CHECK
    source = item.get("source_id")
    assigned = item.get("assigned_source_id")
    if not isinstance(source, str) or not isinstance(assigned, str) or not source or not assigned:
        return HardGateState.CANNOT_CHECK
    return HardGateState.PASS if source == assigned else HardGateState.FAIL


def _support_marker(view: dict[str, Any], item: dict[str, Any]) -> HardGateState:
    token = view.get("claim", {}).get("support_token")
    content = item.get("content")
    if not isinstance(token, str) or not token or not isinstance(content, str):
        return HardGateState.CANNOT_CHECK
    if f"SUPPORT::{token}" in content:
        return HardGateState.PASS
    if f"CONTRADICT::{token}" in content:
        return HardGateState.FAIL
    return HardGateState.CANNOT_CHECK


def _support_state(view: dict[str, Any], item: dict[str, Any] | None) -> HardGateState:
    if item is None:
        return HardGateState.CANNOT_CHECK
    return _support_marker(view, item)


def _pooled_support_state(view: dict[str, Any]) -> HardGateState:
    items: list[dict[str, Any]] = []
    for key in ("evidence", "retrieval_pool"):
        values = view.get(key, [])
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict) and item not in items:
                    items.append(item)
    states = tuple(_support_marker(view, item) for item in items)
    if any(state is HardGateState.PASS for state in states):
        return HardGateState.PASS
    if any(state is HardGateState.FAIL for state in states):
        return HardGateState.FAIL
    return HardGateState.CANNOT_CHECK


def _checker_independence(view: dict[str, Any]) -> HardGateState:
    answer_lineage = view.get("answer", {}).get("lineage_id")
    checker_lineage = view.get("checker", {}).get("lineage_id")
    if not isinstance(answer_lineage, str) or not isinstance(checker_lineage, str):
        return HardGateState.CANNOT_CHECK
    return HardGateState.PASS if answer_lineage != checker_lineage else HardGateState.FAIL


def _checker_discrimination(view: dict[str, Any]) -> HardGateState:
    probe = view.get("checker", {}).get("hostile_probe")
    if probe == "PASS":
        return HardGateState.PASS
    if probe == "FAIL":
        return HardGateState.FAIL
    return HardGateState.CANNOT_CHECK


def _behavioral_influence(view: dict[str, Any], item: dict[str, Any] | None) -> HardGateState:
    if item is None:
        return HardGateState.CANNOT_CHECK
    used = view.get("behavioral_trace", {}).get("used_evidence_ids")
    if not isinstance(used, list):
        return HardGateState.CANNOT_CHECK
    return HardGateState.PASS if item.get("evidence_id") in used else HardGateState.FAIL


def _evaluator_integrity(view: dict[str, Any]) -> HardGateState:
    answer_round = view.get("answer", {}).get("created_round")
    checker_round = view.get("checker", {}).get("created_round")
    frozen_round = view.get("evaluator", {}).get("frozen_round")
    integrity = view.get("evaluator", {}).get("integrity")
    if not all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in (answer_round, checker_round, frozen_round)
    ):
        return HardGateState.CANNOT_CHECK
    if integrity != "INTACT":
        return HardGateState.FAIL
    if checker_round > answer_round or frozen_round > answer_round:
        return HardGateState.FAIL
    return HardGateState.PASS


def _contamination_state(view: dict[str, Any]) -> HardGateState:
    trace = view.get("search_trace")
    if not isinstance(trace, list):
        return HardGateState.CANNOT_CHECK
    contaminated = any(
        isinstance(item, dict) and item.get("benchmark_gold_visible") is True
        for item in trace
    )
    return HardGateState.FAIL if contaminated else HardGateState.PASS


def _protected_access_state(view: dict[str, Any]) -> HardGateState:
    requests = view.get("access_requests")
    if not isinstance(requests, list):
        return HardGateState.CANNOT_CHECK
    hostile = any(
        isinstance(item, dict)
        and (
            item.get("scope") == "PROTECTED"
            or "/protected/" in str(item.get("path", ""))
            or str(item.get("path", "")).startswith("protected/")
        )
        for item in requests
    )
    return HardGateState.FAIL if hostile else HardGateState.PASS


def evaluate_case(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter_ns()
    item = _assigned_evidence(view)
    states = {
        "EXACT_CONTENT_BINDING": _content_binding_state(item),
        "SOURCE_OWNERSHIP": _source_state(item),
        "SEMANTIC_SUPPORT": _support_state(view, item),
        "CHECKER_INDEPENDENCE": _checker_independence(view),
        "CHECKER_DISCRIMINATION": _checker_discrimination(view),
        "BEHAVIORAL_INFLUENCE": _behavioral_influence(view, item),
        "EVALUATOR_CHRONOLOGY_INTEGRITY": _evaluator_integrity(view),
        "SEARCH_CONTAMINATION_CLEAR": _contamination_state(view),
        "PROTECTED_ACCESS_CLEAR": _protected_access_state(view),
    }
    contract = _contract()
    observations = tuple(
        HardGateObservation(
            gate_id=gate_id,
            subject_id=case_id,
            state=state,
            contract_fingerprint=contract.fingerprint,
            evidence_ids=(f"candidate-visible:{case_id}:{gate_id.lower()}",),
            detail=state.value,
        )
        for gate_id, state in states.items()
    )
    report = evaluate_hard_gates(
        contract, observations, subject_id=case_id, round_index=1
    )
    terminal = {
        HardGateState.PASS: "PROMOTE",
        HardGateState.FAIL: "BLOCK",
        HardGateState.CANNOT_CHECK: "CANNOT_CHECK",
    }[report.state]
    pooled = _pooled_support_state(view)
    source_state = states["SOURCE_OWNERSHIP"]
    content_state = states["EXACT_CONTENT_BINDING"]
    return {
        "case_id": case_id,
        "system_id": "ORION",
        "authority_terminal": terminal,
        "claim_correct_prediction": pooled is HardGateState.PASS,
        "source_attribution_prediction": source_state is HardGateState.PASS,
        "support_prediction": (
            "SUPPORTED"
            if pooled is HardGateState.PASS
            else "CONTRADICTED"
            if pooled is HardGateState.FAIL
            else "INSUFFICIENT"
        ),
        "conflation_detected": source_state is HardGateState.FAIL,
        "substitution_detected": content_state is HardGateState.FAIL,
        "tamper_leakage_detected": (
            states["PROTECTED_ACCESS_CLEAR"] is HardGateState.FAIL
            or states["EVALUATOR_CHRONOLOGY_INTEGRITY"] is HardGateState.FAIL
        ),
        "search_contamination_detected": (
            states["SEARCH_CONTAMINATION_CLEAR"] is HardGateState.FAIL
        ),
        "reason_codes": list(report.reasons),
        "resource_units": 9.0,
        "latency_seconds": (time.perf_counter_ns() - started) / 1_000_000_000,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = _read_cases(args.manifest)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            result = evaluate_case(row["case_id"], row["candidate_visible"])
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
