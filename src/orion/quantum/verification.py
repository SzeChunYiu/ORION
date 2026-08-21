from __future__ import annotations

import math
import random
from statistics import mean
from typing import Any, Mapping

from .contracts import (
    QAccessMatch,
    QAdvantageReceipt,
    QResourceSummary,
    QuantumAccessMode,
    QuantumAdvantageTerminal,
    QuantumContractError,
    QuantumEvidenceMode,
    validate_advantage_receipt,
)


_PINNED_QISKIT = "2.5.1"
_PINNED_AER = "0.17.2"
_EXPECTED_BACKEND = {
    "qiskit_version": _PINNED_QISKIT,
    "qiskit_aer_version": _PINNED_AER,
    "backend_family": "qiskit-aer",
    "backend_name": "AerSimulator",
    "method": "statevector",
    "noise_model": "none",
    "evidence_mode": "LOCAL_SIMULATION",
}


def _invalid_case(errors: list[str], *, case_id: str = "") -> dict[str, Any]:
    return {
        "schema": "ORION.QN.S1ACaseReconstruction.v1",
        "case_id": case_id,
        "valid_record": False,
        "candidate_verified": False,
        "errors": errors,
    }


def _expected_positions(n_qubits: int) -> tuple[int, ...]:
    search_size = 1 << n_qubits
    generator = random.Random(734000 + n_qubits)
    interior = sorted(generator.sample(range(1, search_size - 1), 6))
    return (0, search_size - 1, *interior)


def _analytic_probability(search_size: int, iterations: int) -> float:
    theta = math.asin(1.0 / math.sqrt(search_size))
    return math.sin((2 * iterations + 1) * theta) ** 2


def _expected_iterations(search_size: int) -> int:
    theta = math.asin(1.0 / math.sqrt(search_size))
    target = math.pi / (4 * theta) - 0.5
    lower = max(0, math.floor(target))
    upper = max(0, math.ceil(target))
    candidates = sorted({lower, upper})
    return max(candidates, key=lambda value: (_analytic_probability(search_size, value), -value))


def _expected_random_calls(search_size: int, marked_index: int, seed: int) -> int:
    order = list(range(search_size))
    random.Random(seed).shuffle(order)
    return order.index(marked_index) + 1


def _query_model_comparison(n_qubits: int) -> dict[str, Any]:
    """Independent hidden-uniform comparator using the strongest free-final-guess ceiling."""

    search_size = 1 << n_qubits
    iterations = _expected_iterations(search_size)
    success_probability = _analytic_probability(search_size, iterations)
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


def reconstruct_s1a_case(record: Mapping[str, Any]) -> dict[str, Any]:
    """Independently reconstruct one S1A fixture without consuming executor PASS state."""

    errors: list[str] = []
    try:
        n_qubits = int(record["n_qubits"])
        search_size = int(record["search_size"])
        case_index = int(record["case_index"])
        marked_index = int(record["marked_index"])
        iterations = int(record["iterations"])
        attempts = int(record["attempts"])
        oracle_calls = int(record["oracle_calls"])
        verification_calls = int(record["verification_predicate_calls"])
        measurement_shots = int(record["measurement_shots"])
        returned_candidate_raw = record.get("returned_candidate")
        returned_candidate = (
            None if returned_candidate_raw is None else int(returned_candidate_raw)
        )
        measured_candidates = tuple(int(value) for value in record["measured_candidates"])
    except (KeyError, TypeError, ValueError) as exc:
        return _invalid_case([f"malformed case record: {type(exc).__name__}: {exc}"])

    expected_case_id = f"S1A-n{n_qubits}-case{case_index}-marked{marked_index}"
    if n_qubits < 3 or n_qubits > 10:
        return _invalid_case(["n_qubits outside frozen S1A ladder"], case_id=expected_case_id)

    expected_search_size = 1 << n_qubits
    if search_size != expected_search_size:
        return _invalid_case(["search_size does not equal 2^n"], case_id=expected_case_id)

    positions = _expected_positions(n_qubits)
    if case_index < 0 or case_index >= len(positions):
        return _invalid_case(["case_index outside frozen subject set"], case_id=expected_case_id)
    if marked_index < 0 or marked_index >= search_size:
        return _invalid_case(["marked_index outside frozen search space"], case_id=expected_case_id)
    if positions[case_index] != marked_index:
        return _invalid_case(
            ["marked_index does not match frozen subject generator"], case_id=expected_case_id
        )

    if record.get("case_id") != expected_case_id:
        errors.append("case_id does not bind the case coordinates")

    expected_iterations = _expected_iterations(search_size)
    if iterations != expected_iterations:
        errors.append("Grover iteration count differs from frozen analytic rule")

    expected_probability = _analytic_probability(search_size, expected_iterations)
    try:
        recorded_analytic = float(record["analytic_marked_probability"])
        recorded_simulated = float(record["simulated_marked_probability"])
        normalization_error = float(record["normalization_error"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"probability fields malformed: {type(exc).__name__}: {exc}")
        recorded_analytic = math.nan
        recorded_simulated = math.nan
        normalization_error = math.inf

    if not math.isclose(recorded_analytic, expected_probability, rel_tol=0.0, abs_tol=1e-12):
        errors.append("analytic probability does not reconstruct")
    if abs(recorded_simulated - expected_probability) > 1e-10:
        errors.append("statevector probability exceeds frozen analytic tolerance")
    if normalization_error > 1e-10:
        errors.append("statevector normalization exceeds frozen tolerance")

    if attempts < 1 or attempts > 5:
        errors.append("attempt count outside frozen 1..5 range")
    if len(measured_candidates) != attempts:
        errors.append("measured-candidate count differs from attempts")
    if measurement_shots != attempts:
        errors.append("measurement shot count differs from attempts")
    if verification_calls != attempts:
        errors.append("predicate verification calls differ from attempts")
    if oracle_calls != iterations * attempts:
        errors.append("oracle-call accounting differs from iterations * attempts")

    for candidate in measured_candidates:
        if candidate < 0 or candidate >= search_size:
            errors.append("measured candidate outside search space")
            break

    candidate_verified = returned_candidate == marked_index
    if returned_candidate is not None:
        if not measured_candidates or measured_candidates[-1] != returned_candidate:
            errors.append("returned candidate was not the final measured candidate")
        if returned_candidate != marked_index:
            errors.append("returned candidate fails the original predicate")
    elif any(candidate == marked_index for candidate in measured_candidates):
        errors.append("record drops a successful measured candidate")

    expected_ordered = marked_index + 1
    try:
        recorded_ordered = int(record["classical_ordered_calls"])
    except (KeyError, TypeError, ValueError):
        recorded_ordered = -1
    if recorded_ordered != expected_ordered:
        errors.append("ordered classical baseline call count does not reconstruct")

    expected_seed = 73500000 + n_qubits * 1000 + case_index
    try:
        recorded_seed = int(record["classical_random_seed"])
        recorded_random_calls = int(record["classical_random_calls"])
    except (KeyError, TypeError, ValueError):
        recorded_seed = -1
        recorded_random_calls = -1
    if recorded_seed != expected_seed:
        errors.append("classical randomized baseline seed drift")
    expected_random_calls = _expected_random_calls(search_size, marked_index, expected_seed)
    if recorded_random_calls != expected_random_calls:
        errors.append("randomized classical baseline call count does not reconstruct")

    backend = record.get("backend_identity")
    if not isinstance(backend, Mapping):
        errors.append("backend identity missing or malformed")
    else:
        normalized_backend = {str(key): str(value) for key, value in backend.items()}
        if normalized_backend != _EXPECTED_BACKEND:
            errors.append("backend identity/version differs from frozen packet")

    return {
        "schema": "ORION.QN.S1ACaseReconstruction.v1",
        "case_id": expected_case_id,
        "valid_record": not errors,
        "candidate_verified": candidate_verified,
        "errors": errors,
        "recomputed_iterations": expected_iterations,
        "recomputed_analytic_probability": expected_probability,
        "recomputed_classical_ordered_calls": expected_ordered,
        "recomputed_classical_random_calls": expected_random_calls,
    }


def _terminal_for_size(
    n_qubits: int, reconstructions: list[dict[str, Any]]
) -> QuantumAdvantageTerminal:
    if not all(item["valid_record"] for item in reconstructions):
        return QuantumAdvantageTerminal.INVALID_COMPARISON
    if not all(item["candidate_verified"] for item in reconstructions):
        return QuantumAdvantageTerminal.INVALID_COMPARISON
    comparison = _query_model_comparison(n_qubits)
    quantum_queries = int(comparison["quantum_query_budget"])
    classical_budget = int(comparison["classical_matching_query_budget"])
    classical_expected = float(comparison["classical_matching_expected_queries"])
    if quantum_queries < classical_budget and quantum_queries < classical_expected:
        return QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY
    return QuantumAdvantageTerminal.QUANTUM_FEASIBLE_NO_ADVANTAGE


def _validate_top_level_contracts(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("schema") != "ORION.QN.VS1.S1A.Campaign.v4":
        errors.append("campaign schema is not strongest-classical/access/benchmark-hardened v4")
    if report.get("fixture_cases_used_for_advantage") is not False:
        errors.append("public fixture cases are being used to authorize advantage")
    if report.get("advantage_adjudication_source") != "HIDDEN_UNIFORM_ANALYTIC_QUERY_MODEL":
        errors.append("advantage adjudication source is not the frozen hidden-uniform model")

    interpretations = report.get("access_interpretations")
    if not isinstance(interpretations, Mapping):
        errors.append("campaign access_interpretations missing or malformed")
        return
    query_model = interpretations.get("query_model")
    ordinary = interpretations.get("ordinary_classical_input")
    if not isinstance(query_model, Mapping):
        errors.append("query-model access interpretation missing")
    else:
        if query_model.get("quantum_access_mode") != QuantumAccessMode.NATIVE_COHERENT_ORACLE.value:
            errors.append("query-model access is not explicitly native coherent oracle")
        if query_model.get("oracle_construction_status") != "QUERY_MODEL_ASSUMPTION":
            errors.append("query-model oracle construction status drift")
        if query_model.get("maximum_terminal") != QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY.value:
            errors.append("query-model maximum terminal exceeds or differs from frozen ceiling")
    if not isinstance(ordinary, Mapping):
        errors.append("ordinary classical-input access interpretation missing")
    else:
        if ordinary.get("quantum_access_mode") != QuantumAccessMode.CLASSICAL_PREDICATE_ONLY.value:
            errors.append("ordinary input does not preserve classical-predicate-only access")
        if ordinary.get("coherent_oracle_derivation_resolved") is not False:
            errors.append("ordinary input falsely resolves coherent-oracle derivation")
        if ordinary.get("terminal") != QuantumAdvantageTerminal.CANNOT_CHECK_ACCESS_MODEL.value:
            errors.append("ordinary input must remain CANNOT_CHECK_ACCESS_MODEL")


def reconstruct_s1a_campaign(report: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute semantic fixtures and strongest hidden-uniform query terminals."""

    errors: list[str] = []
    _validate_top_level_contracts(report, errors)

    raw_cases = report.get("cases")
    if not isinstance(raw_cases, list):
        return {
            "schema": "ORION.QN.S1ACampaignReconstruction.v4",
            "valid": False,
            "errors": [*errors, "campaign cases missing or malformed"],
            "case_reconstructions": [],
            "size_summaries": [],
        }

    case_reconstructions = [reconstruct_s1a_case(item) for item in raw_cases]
    grouped: dict[int, list[tuple[Mapping[str, Any], dict[str, Any]]]] = {}
    for raw, reconstructed in zip(raw_cases, case_reconstructions, strict=True):
        try:
            n_qubits = int(raw["n_qubits"])
        except (KeyError, TypeError, ValueError):
            errors.append("campaign contains case without valid n_qubits")
            continue
        grouped.setdefault(n_qubits, []).append((raw, reconstructed))

    expected_sizes = tuple(range(3, 11))
    if tuple(sorted(grouped)) != expected_sizes:
        errors.append("campaign does not contain exactly the frozen n=3..10 ladder")

    recorded_summaries = report.get("size_summaries")
    recorded_by_n: dict[int, Mapping[str, Any]] = {}
    if isinstance(recorded_summaries, list):
        for item in recorded_summaries:
            if isinstance(item, Mapping) and "n_qubits" in item:
                try:
                    recorded_by_n[int(item["n_qubits"])] = item
                except (TypeError, ValueError):
                    pass
    else:
        errors.append("size_summaries missing or malformed")

    recomputed_summaries: list[dict[str, Any]] = []
    for n_qubits in expected_sizes:
        pairs = grouped.get(n_qubits, [])
        if len(pairs) != 8:
            errors.append(f"n={n_qubits} does not contain exactly eight frozen fixtures")
            continue
        case_records = [raw for raw, _ in pairs]
        reconstructions = [item for _, item in pairs]
        comparison = _query_model_comparison(n_qubits)
        query_terminal = _terminal_for_size(n_qubits, reconstructions)
        ordinary_terminal = (
            QuantumAdvantageTerminal.INVALID_COMPARISON
            if query_terminal is QuantumAdvantageTerminal.INVALID_COMPARISON
            else QuantumAdvantageTerminal.CANNOT_CHECK_ACCESS_MODEL
        )

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
        )
        for label, receipt in (("query", query_receipt), ("ordinary", ordinary_receipt)):
            try:
                validate_advantage_receipt(receipt)
            except QuantumContractError as exc:
                errors.append(f"n={n_qubits} reconstructed {label} terminal violates Q1: {exc}")

        fixture_mean_quantum = mean(int(item["oracle_calls"]) for item in case_records)
        fixture_mean_ordered = mean(int(item["classical_ordered_calls"]) for item in case_records)
        fixture_mean_random = mean(int(item["classical_random_calls"]) for item in case_records)

        recorded = recorded_by_n.get(n_qubits)
        if recorded is None:
            errors.append(f"n={n_qubits} recorded size summary missing")
        else:
            exact_fields = {
                "terminal": query_terminal.value,
                "query_model_terminal": query_terminal.value,
                "quantum_access_mode": QuantumAccessMode.NATIVE_COHERENT_ORACLE.value,
                "oracle_construction_status": "QUERY_MODEL_ASSUMPTION",
                "ordinary_input_terminal": ordinary_terminal.value,
                "ordinary_input_quantum_access_mode": QuantumAccessMode.CLASSICAL_PREDICATE_ONLY.value,
                "ordinary_input_coherent_oracle_derivation_resolved": False,
                "advantage_adjudication_source": "HIDDEN_UNIFORM_ANALYTIC_QUERY_MODEL",
                "model": comparison["model"],
                "fixture_cases_used_for_advantage": False,
                "success_probability_source": comparison["success_probability_source"],
                "quantum_query_budget": comparison["quantum_query_budget"],
                "classical_matching_query_budget": comparison["classical_matching_query_budget"],
                "classical_free_final_guess_allowed": True,
                "external_output_verification_is_separate_resource": True,
                "benchmark_correlated_side_information_admitted": False,
                "fixture_classical_diagnostic_only": True,
            }
            for key, expected in exact_fields.items():
                if recorded.get(key) != expected:
                    errors.append(f"n={n_qubits} summary field {key} does not reconstruct")

            float_fields = {
                "quantum_single_run_success_probability": comparison[
                    "quantum_single_run_success_probability"
                ],
                "classical_matching_expected_queries": comparison[
                    "classical_matching_expected_queries"
                ],
                "mean_fixture_quantum_oracle_calls": fixture_mean_quantum,
                "mean_fixture_classical_ordered_calls": fixture_mean_ordered,
                "mean_fixture_classical_random_calls": fixture_mean_random,
            }
            for key, expected in float_fields.items():
                try:
                    observed = float(recorded[key])
                except (KeyError, TypeError, ValueError):
                    errors.append(f"n={n_qubits} summary field {key} malformed")
                    continue
                if not math.isclose(observed, float(expected), rel_tol=0.0, abs_tol=1e-12):
                    errors.append(f"n={n_qubits} summary field {key} does not reconstruct")

            unresolved = recorded.get("unresolved_end_to_end_coordinates")
            if not isinstance(unresolved, list) or "coherent_oracle_construction" not in unresolved:
                errors.append(f"n={n_qubits} coherent oracle construction vanished from unknowns")

        recomputed_summaries.append(
            {
                "n_qubits": n_qubits,
                "search_size": 1 << n_qubits,
                "query_model_terminal": query_terminal.value,
                "quantum_access_mode": QuantumAccessMode.NATIVE_COHERENT_ORACLE.value,
                "ordinary_input_terminal": ordinary_terminal.value,
                "ordinary_input_quantum_access_mode": QuantumAccessMode.CLASSICAL_PREDICATE_ONLY.value,
                **comparison,
                "all_case_records_valid": all(item["valid_record"] for item in reconstructions),
                "all_candidates_verified": all(
                    item["candidate_verified"] for item in reconstructions
                ),
            }
        )

    return {
        "schema": "ORION.QN.S1ACampaignReconstruction.v4",
        "valid": not errors and all(item["valid_record"] for item in case_reconstructions),
        "errors": errors,
        "case_reconstructions": case_reconstructions,
        "size_summaries": recomputed_summaries,
    }
