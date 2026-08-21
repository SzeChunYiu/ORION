#!/usr/bin/env python3
"""Conservative R4D confirmation wrapper.

The original confirmation harness reports two independently minimized local
implementation coordinates. This wrapper uses only `C` (Tag/Restore support)
for promotion so no result can combine incompatible local auxiliary TARE
representations. `E_support` remains a non-authorizing diagnostic lower bound.
"""
from __future__ import annotations

import json

import max_r4d_h2o_ducc_confirmation as h


def reduction(base, m, key):
    return 0.0 if base[key] == 0 else (base[key] - m[key]) / base[key]


def main():
    text = h.fetch_source()
    one, two = h.parse_ducc(text)
    paulis, max_imag = h.jordan_wigner_paulis(one, two)
    identity_coeff = paulis.pop((0, 0), 0.0)
    terms = sorted(paulis.items(), key=lambda kv: abs(kv[1]), reverse=True)

    singleton_term = None
    if len(terms) % 2:
        singleton_term = {"coefficient": terms[-1][1], "abs": abs(terms[-1][1])}
        paired_terms = terms[:-1]
    else:
        paired_terms = terms

    base, g1, g5 = h.compile_quartets(paired_terms)
    if singleton_term is not None:
        for m in (base, g1, g5):
            m["Lambda"] += singleton_term["abs"]

    g1_over = g1["Lambda"] / base["Lambda"] - 1.0
    g5_over = g5["Lambda"] / base["Lambda"] - 1.0
    g1_c = reduction(base, g1, "C")
    g5_c = reduction(base, g5, "C")

    # Conservative specialization of the frozen protocol's "either E or C" gate:
    # authorize only from the jointly realizable C coordinate.
    gate1 = g1_over <= 0.0100000001 and g1_c >= 0.05
    gate5 = g5_over <= 0.0500000001 and g5["C"] < base["C"]

    result = {
        "schema": "ORIONQ.MAXR4D.H2ODUCCConfirmationStrict.v1",
        "source": {
            "repo": "npbauman/DUCC-Hamiltonian-Library",
            "commit": h.SOURCE_COMMIT,
            "blob": h.SOURCE_BLOB,
            "path": h.SOURCE_PATH,
        },
        "mapping": "repository_extractor_semantics_then_Jordan_Wigner_no_tapering",
        "n_spatial_orbitals": h.N_ORB,
        "n_qubits": h.N_QUBITS,
        "two_body_sparse_entries": len(two),
        "pauli_terms_including_identity": len(paulis) + 1,
        "nonidentity_pauli_terms": len(terms),
        "identity_coefficient_without_nuclear_shift": identity_coeff,
        "max_pauli_imaginary_residual": max_imag,
        "odd_singleton": singleton_term,
        "coefficient_optimum": base,
        "greedy_1pct": g1,
        "greedy_5pct": g5,
        "greedy_1pct_normalization_overhead": g1_over,
        "greedy_5pct_normalization_overhead": g5_over,
        "greedy_1pct_C_reduction": g1_c,
        "greedy_5pct_C_reduction": g5_c,
        "E_support_status": "diagnostic_independent_minimum_not_jointly_authorizing",
        "gate_1pct_5pct_C_reduction": bool(gate1),
        "gate_5pct_strict_C_pareto": bool(gate5),
        "r4d_protocol_pass": bool(gate1 and gate5),
        "authority": "fresh_public_hamiltonian_confirmation_only__not_novelty_authority",
    }
    print("ORIONQ_MAX_R4D_RESULT=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
