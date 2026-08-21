from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from statistics import mean
from typing import Any

from .contracts import (
    QAccessMatch,
    QAdvantageReceipt,
    QResourceSummary,
    QuantumAccessMode,
    QuantumAdvantageTerminal,
    QuantumEvidenceMode,
    validate_advantage_receipt,
)
from .simulator import (
    analytic_grover_probability,
    execute_s1a_case,
    frozen_s1a_marked_positions,
    optimal_single_marked_iterations,
)
from .verification import reconstruct_s1a_campaign


_PROTOCOL_PATH = Path(
    "research/extensions/orion-qn/VS1_P6_P2_P4_LOCAL_SIMULATION_PROTOCOL_V1.md"
)
_IMPLEMENTATION_PACKET_PATH = Path("development/orion-qn-q2/S1A_IMPLEMENTATION_PACKET_V1.md")
_ACCESS_AMENDMENT_PATH = Path("research/extensions/orion-qn/S1A_ACCESS_MODEL_AMENDMENT_V1.md")
_BENCHMARK_AMENDMENT_PATH = Path(
    "research/extensions/orion-qn/S1A_BENCHMARK_DEPENDENCE_AMENDMENT_V1.md"
)
_CLASSICAL_CEILING_AMENDMENT_PATH = Path(
    "research/extensions/orion-qn/S1A_CLASSICAL_QUERY_CEILING_AMENDMENT_V1.md"
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def query_model_comparison(n_qubits: int) -> dict[str, Any]:
    """Return the hidden-uniform single-mark query comparator independent of fixtures."""

    if n_qubits < 3 or n_qubits > 10:
        raise ValueError("S1A v4 query model requires 3 <= n_qubits <= 10")
    search_size = 1 << n_qubits
    iterations = optimal_single_marked_iterations(search_size)
    success_probability = analytic_grover_probability(search_size, iterations)

    # A strongest no-side-information classical query strategy may make K distinct
    # predicate queries and, if all fail, output one of the remaining positions as a
    # free final guess. Its optimal success ceiling is (K+1)/N for K < N. External
    # output verification is accounted separately for both routes.
    classical_budget = min(
        search_size - 1,
        max(0, math.ceil(success_probability * search_size) - 1),
    )
    classical_expected = classical_budget - (
        classical_budget * (classical_budget - 1) / (2 * search_size)
    )
    return {
        "model": "HIDDEN_UNIFORM_SINGLE_MARK_QUERY_MODEL",
        "fixture_cases_used_for_advantage": False,
        "success_probability_source": "ANALYTIC_GROVER_AMPLITUDE",
        "quantum_single_run_success_probability": success_probability,
        "quantum_query_budget": iterations,
        "classical_matching_query_budget": classical_budget,
        "classical_matching_expected_queries": classical_expected,
        "classical_free_final_guess_allowed": True,
        "external_output_verification_is_separate_resource": True,
        "benchmark_correlated_side_information_admitted": False,
    }


def _semantic_green(cases: list[dict[str, Any]]) -> bool:
    return all(
        item["returned_candidate"] == item["marked_index"]
        and abs(
            float(item["simulated_marked_probability"])
            - float(item["analytic_marked_probability"])
        )
        <= 1e-10
        and float(item["normalization_error"]) <= 1e-10
        for item in cases
    )


def _size_terminal(n_qubits: int, cases: list[dict[str, Any]]) -> QuantumAdvantageTerminal:
    if not _semantic_green(cases):
        return QuantumAdvantageTerminal.INVALID_COMPARISON
    comparison = query_model_comparison(n_qubits)
    quantum_queries = int(comparison["quantum_query_budget"])
    classical_budget = int(comparison["classical_matching_query_budget"])
    classical_expected = float(comparison["classical_matching_expected_queries"])
    if quantum_queries < classical_budget and quantum_queries < classical_expected:
        return QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY
    return QuantumAdvantageTerminal.QUANTUM_FEASIBLE_NO_ADVANTAGE


def _summary_for_size(n_qubits: int, cases: list[dict[str, Any]]) -> dict[str, Any]:
    query_comparison = query_model_comparison(n_qubits)
    query_terminal = _size_terminal(n_qubits, cases)
    query_receipt = QAdvantageReceipt(
        receipt_id=f"vs1-s1a-query-model-n{n_qubits}",
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=query_terminal,
        access_match=QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            quantum_access_mode=QuantumAccessMode.NATIVE_COHERENT_ORACLE,
        ),
        resources=QResourceSummary(
            unresolved_end_to_end_coordinates=(
                "coherent_oracle_construction",
                "fault_tolerant_logical_resources",
                "physical_qubits",
                "ft_runtime",
            )
        ),
        query_claim_bounded=(
            query_terminal is QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY
        ),
    )
    validate_advantage_receipt(query_receipt)

    ordinary_terminal = (
        QuantumAdvantageTerminal.INVALID_COMPARISON
        if query_terminal is QuantumAdvantageTerminal.INVALID_COMPARISON
        else QuantumAdvantageTerminal.CANNOT_CHECK_ACCESS_MODEL
    )
    ordinary_receipt = QAdvantageReceipt(
        receipt_id=f"vs1-s1a-classical-input-n{n_qubits}",
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=ordinary_terminal,
        access_match=QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            stronger_quantum_interface_unresolved=True,
            quantum_access_mode=QuantumAccessMode.CLASSICAL_PREDICATE_ONLY,
            coherent_oracle_derivation_resolved=False,
        ),
        resources=query_receipt.resources,
        query_claim_bounded=False,
    )
    validate_advantage_receipt(ordinary_receipt)

    return {
        "n_qubits": n_qubits,
        "search_size": 1 << n_qubits,
        "case_count": len(cases),
        "terminal": query_terminal.value,
        "query_model_terminal": query_terminal.value,
        "quantum_access_mode": QuantumAccessMode.NATIVE_COHERENT_ORACLE.value,
        "oracle_construction_status": "QUERY_MODEL_ASSUMPTION",
        "ordinary_input_terminal": ordinary_terminal.value,
        "ordinary_input_quantum_access_mode": QuantumAccessMode.CLASSICAL_PREDICATE_ONLY.value,
        "ordinary_input_coherent_oracle_derivation_resolved": False,
        "advantage_adjudication_source": "HIDDEN_UNIFORM_ANALYTIC_QUERY_MODEL",
        **query_comparison,
        # Retained from the original packet as non-authorizing execution diagnostics only.
        "fixture_classical_diagnostic_only": True,
        "mean_fixture_quantum_oracle_calls": mean(int(item["oracle_calls"]) for item in cases),
        "mean_fixture_classical_ordered_calls": mean(
            int(item["classical_ordered_calls"]) for item in cases
        ),
        "mean_fixture_classical_random_calls": mean(
            int(item["classical_random_calls"]) for item in cases
        ),
        "max_simulation_probability_error": max(
            abs(
                float(item["simulated_marked_probability"])
                - float(item["analytic_marked_probability"])
            )
            for item in cases
        ),
        "max_normalization_error": max(float(item["normalization_error"]) for item in cases),
        "all_candidates_verified_by_executor_predicate": all(
            item["returned_candidate"] == item["marked_index"] for item in cases
        ),
        "evidence_mode": QuantumEvidenceMode.LOCAL_SIMULATION.value,
        "query_claim_bounded": query_terminal
        is QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
        "unresolved_end_to_end_coordinates": list(
            query_receipt.resources.unresolved_end_to_end_coordinates
        ),
    }


def run_s1a_campaign() -> dict[str, Any]:
    """Execute semantic fixtures and separately adjudicate the frozen query model."""

    cases: list[dict[str, Any]] = []
    size_summaries: list[dict[str, Any]] = []
    for n_qubits in range(3, 11):
        size_cases: list[dict[str, Any]] = []
        for case_index, marked_index in enumerate(frozen_s1a_marked_positions(n_qubits)):
            record = execute_s1a_case(n_qubits, case_index, marked_index).as_dict()
            cases.append(record)
            size_cases.append(record)
        size_summaries.append(_summary_for_size(n_qubits, size_cases))

    report: dict[str, Any] = {
        "schema": "ORION.QN.VS1.S1A.Campaign.v4",
        "programme_issue": "SzeChunYiu/ORION#734",
        "evidence_mode": QuantumEvidenceMode.LOCAL_SIMULATION.value,
        "subject_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND"),
        "protocol_path": str(_PROTOCOL_PATH),
        "protocol_sha256": _sha256_file(_PROTOCOL_PATH),
        "implementation_packet_path": str(_IMPLEMENTATION_PACKET_PATH),
        "implementation_packet_sha256": _sha256_file(_IMPLEMENTATION_PACKET_PATH),
        "access_amendment_path": str(_ACCESS_AMENDMENT_PATH),
        "access_amendment_sha256": _sha256_file(_ACCESS_AMENDMENT_PATH),
        "benchmark_amendment_path": str(_BENCHMARK_AMENDMENT_PATH),
        "benchmark_amendment_sha256": _sha256_file(_BENCHMARK_AMENDMENT_PATH),
        "classical_ceiling_amendment_path": str(_CLASSICAL_CEILING_AMENDMENT_PATH),
        "classical_ceiling_amendment_sha256": _sha256_file(_CLASSICAL_CEILING_AMENDMENT_PATH),
        "physical_quantum_speedup_claim_permitted": False,
        "fixture_cases_used_for_advantage": False,
        "advantage_adjudication_source": "HIDDEN_UNIFORM_ANALYTIC_QUERY_MODEL",
        "access_interpretations": {
            "query_model": {
                "quantum_access_mode": QuantumAccessMode.NATIVE_COHERENT_ORACLE.value,
                "oracle_construction_status": "QUERY_MODEL_ASSUMPTION",
                "maximum_terminal": QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY.value,
            },
            "ordinary_classical_input": {
                "quantum_access_mode": QuantumAccessMode.CLASSICAL_PREDICATE_ONLY.value,
                "coherent_oracle_derivation_resolved": False,
                "terminal": QuantumAdvantageTerminal.CANNOT_CHECK_ACCESS_MODEL.value,
            },
        },
        "cases": cases,
        "size_summaries": size_summaries,
        "literature_boundary": [
            {
                "source": "standard quantum query model",
                "role": "coherent-oracle access boundary",
                "disposition": (
                    "query-count evidence is valid only when native coherent oracle access is "
                    "explicitly registered"
                ),
            },
            {
                "source": "arXiv:2607.13090",
                "role": "benchmark-dependence / side-information hostile donor",
                "disposition": (
                    "public known-answer fixture support is semantic-only and cannot authorize "
                    "the query-advantage comparator"
                ),
            },
            {
                "source": "strongest hidden-uniform classical query ceiling",
                "role": "classical free-final-guess correction",
                "disposition": (
                    "classical comparator may make K distinct queries and a free final guess; "
                    "external verification is a separate resource for both routes"
                ),
            },
            {
                "source": "Quantum 10, 1975 (2026)",
                "role": "structured-problem/resource hostile donor",
                "disposition": "S1A query result cannot generalize to structured/end-to-end advantage",
            },
            {
                "source": "arXiv:2605.21380",
                "role": "quantum-oracle resource modelling donor",
                "disposition": "oracle construction remains explicit S3 coordinate",
            },
            {
                "source": "arXiv:2402.13895",
                "role": "concrete Grover-oracle resource-accounting donor",
                "disposition": "generic query reduction is separate from implementation cost",
            },
        ],
    }
    report["p4_reconstruction"] = reconstruct_s1a_campaign(report)
    return report


def run_s1a_campaign_json() -> str:
    return json.dumps(run_s1a_campaign(), sort_keys=True, separators=(",", ":"))
