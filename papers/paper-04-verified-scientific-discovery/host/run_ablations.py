#!/usr/bin/env python3
"""Gold-blind ORION mechanism ablations for the frozen P4 campaign.

Every variant receives exactly the same candidate-visible packet and resource
budget as full ORION. Each hard-gate ablation removes only the named governance
coordinate; the soft-confidence variant replaces the non-compensatory terminal
with a predeclared two-thirds pass threshold.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from orion.kernel.hard_gates import (
    HardGateContract,
    HardGateObservation,
    HardGateRequirement,
    HardGateState,
    evaluate_hard_gates,
)

import run_candidate as full

ABLATION_IDS = (
    "ablation-no-exact-content-binding",
    "ablation-no-content-provenance-distinction",
    "ablation-no-checker-lineage-independence",
    "ablation-no-hostile-checker-battery",
    "ablation-no-behavioral-influence",
    "ablation-no-evaluator-protection-telemetry",
    "ablation-soft-confidence",
    "ablation-no-search-contamination-block",
)


def _read_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            raw = json.loads(line)
            if set(raw) != {"case_id", "candidate_visible"}:
                raise ValueError("ablation manifest may contain only case_id and candidate_visible")
            rows.append(raw)
    return rows


def _base_states(view: dict[str, Any]) -> dict[str, HardGateState]:
    item = full._assigned_evidence(view)
    return {
        "EXACT_CONTENT_BINDING": full._content_binding_state(item),
        "SOURCE_OWNERSHIP": full._source_state(item),
        "SEMANTIC_SUPPORT": full._support_state(view, item),
        "CHECKER_INDEPENDENCE": full._checker_independence(view),
        "CHECKER_DISCRIMINATION": full._checker_discrimination(view),
        "BEHAVIORAL_INFLUENCE": full._behavioral_influence(view, item),
        "EVALUATOR_CHRONOLOGY_INTEGRITY": full._evaluator_integrity(view),
        "SEARCH_CONTAMINATION_CLEAR": full._contamination_state(view),
        "PROTECTED_ACCESS_CLEAR": full._protected_access_state(view),
    }


def _variant_states(
    ablation_id: str, states: dict[str, HardGateState]
) -> dict[str, HardGateState]:
    out = dict(states)
    if ablation_id == "ablation-no-exact-content-binding":
        out["EXACT_CONTENT_BINDING"] = HardGateState.PASS
    elif ablation_id == "ablation-no-content-provenance-distinction":
        out["SOURCE_OWNERSHIP"] = HardGateState.PASS
    elif ablation_id == "ablation-no-checker-lineage-independence":
        out["CHECKER_INDEPENDENCE"] = HardGateState.PASS
    elif ablation_id == "ablation-no-hostile-checker-battery":
        out["CHECKER_DISCRIMINATION"] = HardGateState.PASS
    elif ablation_id == "ablation-no-behavioral-influence":
        out["BEHAVIORAL_INFLUENCE"] = HardGateState.PASS
    elif ablation_id == "ablation-no-evaluator-protection-telemetry":
        out["EVALUATOR_CHRONOLOGY_INTEGRITY"] = HardGateState.PASS
        out["PROTECTED_ACCESS_CLEAR"] = HardGateState.PASS
    elif ablation_id == "ablation-soft-confidence":
        pass
    elif ablation_id == "ablation-no-search-contamination-block":
        out["SEARCH_CONTAMINATION_CLEAR"] = HardGateState.PASS
    else:  # pragma: no cover - tuple and caller are fixed together
        raise ValueError(f"unknown ablation: {ablation_id}")
    return out


def _hard_terminal(
    case_id: str, ablation_id: str, states: dict[str, HardGateState]
) -> tuple[str, list[str]]:
    contract = HardGateContract(
        contract_id=f"P4.protected-authority.{ablation_id}.v1",
        requirements=tuple(
            HardGateRequirement(gate_id, gate_id.replace("_", " ").lower())
            for gate_id in full.GATE_IDS
        ),
        frozen_at_round=0,
    )
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
    return terminal, list(report.reasons)


def _soft_terminal(states: dict[str, HardGateState]) -> tuple[str, list[str]]:
    pass_count = sum(state is HardGateState.PASS for state in states.values())
    threshold = 6  # prospectively frozen: ceil(2/3 * 9 gates)
    terminal = "PROMOTE" if pass_count >= threshold else "BLOCK"
    return terminal, [f"soft_confidence_passes:{pass_count}/9", f"threshold:{threshold}/9"]


def _one(case_id: str, view: dict[str, Any], ablation_id: str) -> dict[str, Any]:
    started = time.perf_counter_ns()
    base = _base_states(view)
    states = _variant_states(ablation_id, base)
    if ablation_id == "ablation-soft-confidence":
        terminal, reasons = _soft_terminal(states)
    else:
        terminal, reasons = _hard_terminal(case_id, ablation_id, states)

    pooled = full._pooled_support_state(view)
    source = base["SOURCE_OWNERSHIP"]
    content = base["EXACT_CONTENT_BINDING"]
    return {
        "case_id": case_id,
        "system_id": ablation_id,
        "authority_terminal": terminal,
        "claim_correct_prediction": pooled is HardGateState.PASS,
        "source_attribution_prediction": source is HardGateState.PASS,
        "support_prediction": (
            "SUPPORTED"
            if pooled is HardGateState.PASS
            else "CONTRADICTED"
            if pooled is HardGateState.FAIL
            else "INSUFFICIENT"
        ),
        "conflation_detected": source is HardGateState.FAIL,
        "substitution_detected": content is HardGateState.FAIL,
        "tamper_leakage_detected": (
            base["PROTECTED_ACCESS_CLEAR"] is HardGateState.FAIL
            or base["EVALUATOR_CHRONOLOGY_INTEGRITY"] is HardGateState.FAIL
        ),
        "search_contamination_detected": (
            base["SEARCH_CONTAMINATION_CLEAR"] is HardGateState.FAIL
        ),
        "reason_codes": reasons,
        "resource_units": 9.0,
        "latency_seconds": (time.perf_counter_ns() - started) / 1_000_000_000,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    cases = _read_cases(args.manifest)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in cases:
            for ablation_id in ABLATION_IDS:
                handle.write(
                    json.dumps(
                        _one(row["case_id"], row["candidate_visible"], ablation_id),
                        sort_keys=True,
                    )
                    + "\n"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
