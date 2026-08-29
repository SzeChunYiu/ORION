#!/usr/bin/env python3
"""Exact finite regression for ORION19.INTERVENTION_IDENTIFIABILITY.v1."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "FACTORIAL_SUCCESSOR_PROTOCOL_V1.json"


def signatures(matrix, selected):
    return [tuple(row[j] for j in selected) for row in matrix]


def identifies(matrix, selected):
    sigs = signatures(matrix, selected)
    return len(set(sigs)) == len(sigs)


def hits_all_pair_separations(matrix, selected):
    n_h = len(matrix)
    for h in range(n_h):
        for g in range(h + 1, n_h):
            separation = {j for j in range(len(matrix[0])) if matrix[h][j] != matrix[g][j]}
            if not separation.intersection(selected):
                return False
    return True


def minimum_identifying_sets(matrix):
    n_j = len(matrix[0])
    for size in range(n_j + 1):
        winners = []
        for selected in itertools.combinations(range(n_j), size):
            if identifies(matrix, selected):
                winners.append(selected)
        if winners:
            return winners
    return []


def predicted_repair(hypothesis_id, factors):
    factors = set(factors)
    if hypothesis_id == "H_INFO":
        return "task_relevant_information" in factors
    if hypothesis_id == "H_ACCESS":
        return "access_or_representation" in factors
    if hypothesis_id == "H_COMPUTE":
        return "search_or_inference_compute" in factors
    if hypothesis_id == "H_CONJUNCTIVE":
        return {
            "task_relevant_information",
            "access_or_representation",
            "search_or_inference_compute",
        } <= factors
    raise AssertionError(hypothesis_id)


def exhaustive_theorem_regression():
    matrices = 0
    subset_checks = 0
    for n_h in range(2, 5):
        for n_j in range(1, 4):
            for bits in itertools.product((0, 1), repeat=n_h * n_j):
                matrix = [list(bits[h * n_j : (h + 1) * n_j]) for h in range(n_h)]
                for mask in range(1 << n_j):
                    selected = tuple(j for j in range(n_j) if (mask >> j) & 1)
                    assert identifies(matrix, selected) == hits_all_pair_separations(matrix, selected)
                    subset_checks += 1
                matrices += 1
    return matrices, subset_checks


def validate_protocol():
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema_version"] == "orion19.mechanism-factorial-successor.v1"
    assert p["identity"] == "ORION19.MECHANISM_INTERVENTION_MULTIPLEX.v1"
    assert p["status"] == "DESIGN_ONLY__NO_OUTCOME_AUTHORITY"
    assert p["scientific_authority_delta"] == "NONE"

    hypotheses = [h["id"] for h in p["candidate_hypotheses"]]
    assert hypotheses == ["H_INFO", "H_ACCESS", "H_COMPUTE", "H_CONJUNCTIVE"]
    interventions = p["factorial_interventions"]
    ids = [j["id"] for j in interventions]
    assert ids == ["J_I", "J_A", "J_C", "J_IA", "J_IC", "J_AC", "J_IAC"]

    matrix = [
        [predicted_repair(h, intervention["factors"]) for intervention in interventions]
        for h in hypotheses
    ]
    minima = minimum_identifying_sets(matrix)
    assert minima
    assert len(minima[0]) == 2
    recorded_min = tuple(ids.index(x) for x in p["minimum_identifying_set_over_full_factorial_library"])
    assert recorded_min in minima
    assert p["minimum_identifying_set_size"] == 2

    pure_ids = ["J_I", "J_A", "J_C"]
    pure_indices = [ids.index(x) for x in pure_ids]
    assert identifies(matrix, pure_indices)
    for size in range(3):
        for selected in itertools.combinations(pure_indices, size):
            assert not identifies(matrix, selected)
    assert p["minimum_single_factor_purity_core"] == pure_ids
    assert p["minimum_single_factor_purity_core_size"] == 3

    assert p["response"]["repair_threshold_must_be_frozen_before_outcomes"] is True
    assert p["response"]["stochastic_outcomes_require_pre_frozen_statistical_model_and_power_analysis"] is True
    required_terminals = {
        "MECHANISM_DISCRIMINATED",
        "NO_MECHANISM_DISCRIMINATION",
        "CANNOT_CHECK_INTERVENTION_PURITY",
        "CANNOT_CHECK_HYPOTHESES_OBSERVATIONALLY_EQUIVALENT_UNDER_FROZEN_LIBRARY",
        "CANNOT_CHECK_INSUFFICIENT_POWER_OR_FAMILY_COUNT",
        "ADVERSE_UNMODELLED_RESPONSE_SIGNATURE",
    }
    assert required_terminals <= set(p["terminals"])
    assert len(p["required_controls"]) >= 5
    assert len(p["anti_leakage"]) >= 5
    return matrix, minima


def main():
    matrices, subset_checks = exhaustive_theorem_regression()
    matrix, minima = validate_protocol()
    print(
        "ORION19_INTERVENTION_IDENTIFIABILITY_V1_PASS "
        f"binary_response_matrices={matrices} subset_checks={subset_checks} "
        f"factorial_minimum_size={len(minima[0])} factorial_minima={len(minima)} "
        f"frozen_candidate_signatures={matrix}"
    )


if __name__ == "__main__":
    main()
