#!/usr/bin/env python3
"""MAX-R6 interface closure after native Self-ORION selected CHANGE_INTERFACE.

Frozen by MAX_R6_INTERFACE_CLOSURE_PROTOCOL.md.
This is a donor-favourable lower envelope, not an achievable FOQCS PREP claim.
"""
from __future__ import annotations

import json

N_QUBITS = 8

INCUMBENT = {
    "Lambda": 4.862157873932594,
    "clifford_two_qubit_equiv": 1428,
    "projected_T": 5568,
    "blocks": 246,
    "ancilla": 0,
    "reference_total_T": 31028,
}

PAULI_L1 = 5.158046205600001


def weakly_dominates(a: dict[str, float | int], b: dict[str, float | int]) -> bool:
    keys = ("Lambda", "clifford_two_qubit_equiv", "projected_T", "blocks", "ancilla")
    le = all(a[k] <= b[k] + (1e-13 if k == "Lambda" else 0) for k in keys)
    strict = any(a[k] < b[k] - (1e-13 if k == "Lambda" else 0) for k in keys)
    return bool(le and strict)


def main() -> dict:
    foqcs = {
        "label": "OPTIMISTIC_FOQCS_ZERO_PREP_ENVELOPE",
        "Lambda": PAULI_L1,
        "select_CNOT": N_QUBITS,
        "select_CZ": N_QUBITS,
        "clifford_two_qubit_equiv": 2 * N_QUBITS,
        "projected_T": 0,
        "blocks": 1,
        "activation_ancilla": 2 * N_QUBITS,
        "extra_PREP_ancilla": 0,
        "ancilla": 2 * N_QUBITS,
        "PREP_R_two_qubit": 0,
        "PREP_Ldag_two_qubit": 0,
        "PREP_T": 0,
        "achievable_claim": False,
    }

    worse = {
        "Lambda": foqcs["Lambda"] > INCUMBENT["Lambda"] + 1e-13,
        "ancilla": foqcs["ancilla"] > INCUMBENT["ancilla"],
    }
    better = {
        "clifford_two_qubit_equiv": foqcs["clifford_two_qubit_equiv"]
        < INCUMBENT["clifford_two_qubit_equiv"],
        "projected_T": foqcs["projected_T"] < INCUMBENT["projected_T"],
        "blocks": foqcs["blocks"] < INCUMBENT["blocks"],
    }
    foqcs_dominates = weakly_dominates(foqcs, INCUMBENT)
    incumbent_dominates = weakly_dominates(INCUMBENT, foqcs)

    gates = {
        "h4_qubits_bound": N_QUBITS == 8,
        "h4_pauli_l1_bound": abs(PAULI_L1 - 5.158046205600001) <= 1e-15,
        "incumbent_bound": INCUMBENT
        == {
            "Lambda": 4.862157873932594,
            "clifford_two_qubit_equiv": 1428,
            "projected_T": 5568,
            "blocks": 246,
            "ancilla": 0,
            "reference_total_T": 31028,
        },
        "foqcs_select_exact": foqcs["select_CNOT"] == 8
        and foqcs["select_CZ"] == 8
        and foqcs["clifford_two_qubit_equiv"] == 16,
        "foqcs_activation_ancilla_exact": foqcs["activation_ancilla"] == 16,
        "zero_prep_explicitly_optimistic": foqcs["PREP_R_two_qubit"] == 0
        and foqcs["PREP_Ldag_two_qubit"] == 0
        and foqcs["PREP_T"] == 0
        and foqcs["achievable_claim"] is False,
        "optimistic_envelope_not_dominating": foqcs_dominates is False,
        "hard_worsening_present": any(worse.values()),
        "foqcs_is_distinct_pareto_capability": incumbent_dominates is False
        and any(better.values()),
    }

    passed = all(gates.values())
    out = {
        "schema": "ORIONQ.MAXR6.FOQCSInterfaceEnvelope.v1",
        "authority": (
            "INTERFACE_CANNOT_DOMINATE_EVEN_OPTIMISTIC"
            if passed
            else "INTERFACE_CLOSURE_PROTOCOL_NEGATIVE_OR_INVALID"
        ),
        "scope": "donor_favourable_interface_lower_bound__not_R6",
        "incumbent": INCUMBENT,
        "foqcs_optimistic_envelope": foqcs,
        "foqcs_dominates_incumbent": foqcs_dominates,
        "incumbent_dominates_foqcs": incumbent_dominates,
        "strictly_worse_hard_coordinates": [k for k, v in worse.items() if v],
        "strictly_better_coordinates": [k for k, v in better.items() if v],
        "interface_envelope_registered": passed,
        "current_method_incremental_value_on_h4": "NONE_OVER_DIRECT_CLIQUE_DONOR",
        "fresh_r6_subject_coefficients_accessed": False,
        "gates": gates,
        "pass": passed,
    }
    print("ORIONQ_MAX_R6_FOQCS_INTERFACE=" + json.dumps(out, sort_keys=True))
    if not passed:
        raise SystemExit(1)
    return out


if __name__ == "__main__":
    main()
