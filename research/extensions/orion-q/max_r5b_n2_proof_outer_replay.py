#!/usr/bin/env python3
"""MAX-R5B proof-carrying replay + fixed outer-control accounting for N2.

This script does NOT change the frozen R5 N2 grouping or normalization budget.
It reconstructs canonical exact m=2 TARE witnesses with backpointers, verifies
all symplectic obligations from Pauli masks, and wraps those frozen witnesses in
the fixed controlled outer-LCU model frozen in MAX_R5B.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache

import max_r5_n2_joint_internal_confirmation as v1

h = v1.h
N = 12
TARGET = 0b101
INF = 10**9

# Fault-tolerant projection constants, all declared rather than hidden.
SYNTH_EPS = 1e-10
RZ_T = int(math.ceil(1.149 * math.log2(1.0 / SYNTH_EPS) + 9.2))
CRZ_CNOT = 2
CRZ_RZ_SYNTH = 2
CH_CNOT = 1
CH_T = 2
TOFFOLI_CNOT = 6
TOFFOLI_T = 7


def sha(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def mask_from_codes(codes):
    x = z = 0
    for q, code in enumerate(codes):
        bx, bz = h.CODE_BITS[code]
        x |= bx << q
        z |= bz << q
    return (x, z)


def weight(k):
    return (k[0] | k[1]).bit_count()


def mul_key(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def symp(a, b):
    return ((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) & 1


def local_codes(key):
    x, z = key
    for q in range(N):
        yield h.BITS_CODE[((x >> q) & 1, (z >> q) & 1)]


# Enumerate all local triples once, ordered lexicographically I,X,Y,Z in each slot.
LOCAL = {}
for p0 in range(4):
    for p1 in range(4):
        by_delta = {d: [] for d in range(8)}
        for r0 in range(4):
            for r1 in range(4):
                for s in range(4):
                    d = (
                        h.local_symp(r0, r1)
                        | (h.local_symp(s, r0) << 1)
                        | (h.local_symp(s, r1) << 2)
                    )
                    t0 = h.local_mul(p0, r0)
                    t1 = h.local_mul(p1, r1)
                    cost = (
                        4 * h.local_wt(r0)
                        + 2 * h.local_wt(r1)
                        + 2 * h.local_wt(s)
                        + h.local_wt(t0)
                        + h.local_wt(t1)
                    )
                    by_delta[d].append((cost, (r0, r1, s)))
        for d in range(8):
            by_delta[d].sort(key=lambda x: (x[0], x[1]))
        LOCAL[p0, p1] = by_delta


def orientation_witness(p0_key, p1_key):
    # State value is (cost, full lexicographic sequence). Keeping the sequence in
    # the DP makes the frozen tie break explicit rather than implicit in numpy.
    states = {0: (0, tuple())}
    for p0, p1 in zip(local_codes(p0_key), local_codes(p1_key)):
        nxt = {}
        for prev_parity, (prev_cost, prev_seq) in states.items():
            for delta in range(8):
                # For a fixed local delta, only the cheapest lexicographic triple
                # can ever improve a global state because future costs depend only
                # on accumulated parity.
                local_cost, triple = LOCAL[p0, p1][delta][0]
                parity = prev_parity ^ delta
                cand = (prev_cost + local_cost, prev_seq + (triple,))
                if parity not in nxt or cand < nxt[parity]:
                    nxt[parity] = cand
        states = nxt
    raw_cost, seq = states[TARGET]
    return raw_cost - 6, seq


@lru_cache(maxsize=400000)
def tare_witness(k0, k1):
    choices = []
    for orient, (a, b) in enumerate(((k0, k1), (k1, k0))):
        cost, seq = orientation_witness(a, b)
        # Frozen ordering: cost, original orientation first, then local sequence.
        choices.append((cost, orient, seq, a, b))
    cost, orient, seq, a, b = min(choices, key=lambda x: (x[0], x[1], x[2]))
    r0 = mask_from_codes([t[0] for t in seq])
    r1 = mask_from_codes([t[1] for t in seq])
    s = mask_from_codes([t[2] for t in seq])
    t0 = mul_key(a, r0)
    t1 = mul_key(b, r1)
    recomputed = (
        4 * (weight(r0) - 1)
        + 2 * (weight(r1) - 1)
        + 2 * weight(s)
        + weight(t0)
        + weight(t1)
    )
    checks = {
        "R0_anticommutes_R1": symp(r0, r1) == 1,
        "S_commutes_R0": symp(s, r0) == 0,
        "S_anticommutes_R1": symp(s, r1) == 1,
        "T0R0_equals_P0_bits": mul_key(t0, r0) == a,
        "T1R1_equals_P1_bits": mul_key(t1, r1) == b,
        "G_recomputed": recomputed == cost,
    }
    if not all(checks.values()):
        raise AssertionError({"checks": checks, "k0": k0, "k1": k1})
    return {
        "type": "TARE_M2",
        "orientation": orient,
        "ordered_targets": [list(a), list(b)],
        "R0": list(r0),
        "R1": list(r1),
        "S": list(s),
        "T0": list(t0),
        "T1": list(t1),
        "G_internal_2q": int(cost),
        "checks": checks,
    }


def direct_witness(k0, k1):
    if symp(k0, k1) != 1:
        raise AssertionError("DIRECT witness on commuting targets")
    vals = []
    for orient, (a, b) in enumerate(((k0, k1), (k1, k0))):
        g = 4 * (weight(a) - 1) + 2 * (weight(b) - 1)
        vals.append((g, orient, a, b))
    g, orient, a, b = min(vals, key=lambda x: (x[0], x[1]))
    return {
        "type": "DIRECT_ANTI_UNITARY",
        "orientation": orient,
        "ordered_targets": [list(a), list(b)],
        "G_internal_2q": int(g),
        "checks": {"targets_anticommute": True, "G_recomputed": True},
    }


def pair_witness(terms, i, j):
    k0, a0 = terms[i]
    k1, a1 = terms[j]
    if symp(k0, k1) == 1:
        w = direct_witness(k0, k1)
        lam = math.hypot(abs(a0), abs(a1))
    else:
        w = tare_witness(k0, k1)
        lam = math.sqrt(2.0) * math.hypot(abs(a0), abs(a1))
    w = dict(w)
    w.update({
        "term_indices": [int(i), int(j)],
        "input_keys": [list(k0), list(k1)],
        "coefficient_sign_bits": [int(a0 < 0), int(a1 < 0)],
        "lambda_pair": float(lam),
    })
    return w


def controlled_vector(w):
    g = int(w["G_internal_2q"])
    if w["type"] == "DIRECT_ANTI_UNITARY":
        return {
            "parity_CNOT": g,
            "controlled_Rz": 3,
            "controlled_H": 0,
            "controlled_Pauli_support": 0,
            "AND2_compute_uncompute_pairs": 0,
            "extra_conjunction_scratch": 0,
        }
    r0 = tuple(w["R0"]); r1 = tuple(w["R1"]); s = tuple(w["S"])
    t0 = tuple(w["T0"]); t1 = tuple(w["T1"])
    uanti = 4 * (weight(r0) - 1) + 2 * (weight(r1) - 1)
    restore_support = min(weight(t0), weight(t1)) + weight(mul_key(t0, t1))
    return {
        "parity_CNOT": int(uanti),
        "controlled_Rz": 3,
        "controlled_H": 3,
        "controlled_Pauli_support": int(2 * weight(s) + restore_support),
        "AND2_compute_uncompute_pairs": 2,
        "extra_conjunction_scratch": 1,
    }


def sum_vectors(vecs):
    keys = vecs[0].keys() if vecs else []
    return {k: int(sum(v[k] for v in vecs)) for k in keys}


def project_ft(vec):
    # One AND compute/uncompute pair = two exact Toffolis.
    toffoli_count = 2 * vec["AND2_compute_uncompute_pairs"]
    cnot = (
        vec["parity_CNOT"]
        + vec["controlled_Pauli_support"]
        + CRZ_CNOT * vec["controlled_Rz"]
        + CH_CNOT * vec["controlled_H"]
        + TOFFOLI_CNOT * toffoli_count
    )
    # Generic controlled Rz is two synthesized one-qubit Rz rotations.
    t = (
        CRZ_RZ_SYNTH * RZ_T * vec["controlled_Rz"]
        + CH_T * vec["controlled_H"]
        + TOFFOLI_T * toffoli_count
    )
    return {
        "CNOT": int(cnot),
        "T": int(t),
        "synthesized_Rz_instances": int(CRZ_RZ_SYNTH * vec["controlled_Rz"]),
        "exact_Toffoli_count": int(toffoli_count),
    }


def project_native(vec):
    # Keeps coherent AND as a separate 3q primitive instead of pretending all
    # native two-qubit gates have the same meaning.
    twoq = (
        vec["parity_CNOT"]
        + vec["controlled_Pauli_support"]
        + vec["controlled_Rz"]
        + vec["controlled_H"]
    )
    return {
        "native_two_qubit_primitives_excluding_AND": int(twoq),
        "coherent_AND_compute_uncompute_pairs": int(vec["AND2_compute_uncompute_pairs"]),
        "controlled_arbitrary_rotations": int(vec["controlled_Rz"]),
    }


def aggregate(terms, pairs):
    witnesses = [pair_witness(terms, i, j) for i, j in pairs]
    lam = sum(w["lambda_pair"] for w in witnesses)
    g = sum(w["G_internal_2q"] for w in witnesses)
    direct = sum(w["type"] == "DIRECT_ANTI_UNITARY" for w in witnesses)
    vec = sum_vectors([controlled_vector(w) for w in witnesses])
    # Canonical proof payload deliberately includes the representations.
    proof_payload = []
    for w in witnesses:
        compact = {
            "term_indices": w["term_indices"],
            "type": w["type"],
            "orientation": w["orientation"],
            "input_keys": w["input_keys"],
            "ordered_targets": w["ordered_targets"],
            "coefficient_sign_bits": w["coefficient_sign_bits"],
            "lambda_pair": round(w["lambda_pair"], 16),
            "G_internal_2q": w["G_internal_2q"],
        }
        for key in ("R0", "R1", "S", "T0", "T1"):
            if key in w:
                compact[key] = w[key]
        proof_payload.append(compact)
    return {
        "Lambda_joint": float(lam),
        "G_internal_2q": int(g),
        "pair_count": len(pairs),
        "direct_unitary_blocks": int(direct),
        "tare_blocks": int(len(pairs) - direct),
        "pair_list_sha256": sha([[int(i), int(j)] for i, j in pairs]),
        "canonical_witness_sha256": sha(proof_payload),
        "all_witness_checks_pass": all(all(w["checks"].values()) for w in witnesses),
        "controlled_outer_primitive_vector": vec,
        "controlled_outer_standard_CliffordT_projection": project_ft(vec),
        "controlled_outer_native_projection": project_native(vec),
        "max_extra_conjunction_scratch": max((controlled_vector(w)["extra_conjunction_scratch"] for w in witnesses), default=0),
    }


def sorted_terms_hash(terms):
    return sha([[list(k), format(float(a), ".17g")] for k, a in terms])


def main():
    text = h.fetch_source()
    one, two = h.parse_ducc(text)
    paulis, max_imag = h.jordan_wigner_paulis(one, two)
    identity = paulis.pop((0, 0), 0.0)
    terms_all = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    singleton = terms_all[-1] if len(terms_all) % 2 else None
    terms = terms_all[:-1] if singleton is not None else terms_all

    inc, suc, inc_pairs, suc_pairs = v1.compile_bounded(terms, singleton, 0.01)
    inc_r = aggregate(terms, inc_pairs)
    suc_r = aggregate(terms, suc_pairs)
    if singleton is not None:
        sl = abs(singleton[1])
        inc_r["Lambda_joint"] += sl
        suc_r["Lambda_joint"] += sl

    # Bind replay back to the frozen v1 aggregate instead of silently changing it.
    binds = {
        "inc_Lambda": abs(inc_r["Lambda_joint"] - inc["Lambda_joint"]) <= 1e-12,
        "suc_Lambda": abs(suc_r["Lambda_joint"] - suc["Lambda_joint"]) <= 1e-12,
        "inc_G": inc_r["G_internal_2q"] == inc["G_internal_2q"],
        "suc_G": suc_r["G_internal_2q"] == suc["G_internal_2q"],
        "inc_direct": inc_r["direct_unitary_blocks"] == inc["direct_unitary_blocks"],
        "suc_direct": suc_r["direct_unitary_blocks"] == suc["direct_unitary_blocks"],
        "all_witnesses": inc_r["all_witness_checks_pass"] and suc_r["all_witness_checks_pass"],
    }
    if not all(binds.values()):
        raise AssertionError({"replay_bindings": binds})

    # Common outer layer. The dense Prepare count is per Prepare invocation;
    # standard block encoding uses Prepare and Prepare^dagger.
    B = inc_r["pair_count"] + int(singleton is not None)
    address = int(math.ceil(math.log2(B))) if B > 1 else 0
    padded = 1 << address if address else 1
    common = {
        "outer_blocks": B,
        "outer_address_qubits": address,
        "dense_prepare_rotations_per_Prepare": max(0, padded - 1),
        "dense_prepare_rotations_two_sided": 2 * max(0, padded - 1),
        "unary_selector_routing_T_reference": 4 * max(0, B - 1),
        "selector_routing_reference": "Loaiza-Brahmachari-Izmaylov MTD 2025 unary-iteration overhead",
        "local_TARE_ancilla_capacity": 1,
        "max_conjunction_scratch": max(inc_r["max_extra_conjunction_scratch"], suc_r["max_extra_conjunction_scratch"]),
    }

    # Add common routing to FT projection only as a separately visible total.
    for r in (inc_r, suc_r):
        p = r["controlled_outer_standard_CliffordT_projection"]
        p["T_plus_common_selector_routing"] = p["T"] + common["unary_selector_routing_T_reference"]

    lam_ratio = suc_r["Lambda_joint"] / inc_r["Lambda_joint"]
    comparisons = {
        "normalization_ratio_successor_over_incumbent": lam_ratio,
        "internal_G_reduction": 1.0 - suc_r["G_internal_2q"] / inc_r["G_internal_2q"],
    }
    for proj, key in (("controlled_outer_standard_CliffordT_projection", "T"),
                      ("controlled_outer_standard_CliffordT_projection", "CNOT"),
                      ("controlled_outer_native_projection", "native_two_qubit_primitives_excluding_AND")):
        a = inc_r[proj][key]
        b = suc_r[proj][key]
        comparisons[f"{key}_raw_ratio_successor_over_incumbent"] = (b / a if a else 1.0)
        comparisons[f"{key}_normalization_weighted_ratio"] = (lam_ratio * b / a if a else lam_ratio)

    result = {
        "schema": "ORIONQ.MAXR5B.N2ProofOuterReplay.v1",
        "authority": "R5_REPLAY_OUTER_ACCOUNTING_ONLY__NOT_R6",
        "source": {"commit": h.SOURCE_COMMIT, "blob": h.SOURCE_BLOB, "path": h.SOURCE_PATH},
        "n_qubits": N,
        "nonidentity_pauli_terms": len(terms_all),
        "identity_coefficient_without_nuclear_shift": identity,
        "max_pauli_imaginary_residual": max_imag,
        "sorted_terms_sha256": sorted_terms_hash(terms_all),
        "fault_tolerant_projection_constants": {
            "synthesis_precision": SYNTH_EPS,
            "T_per_synthesized_Rz": RZ_T,
            "controlled_Rz_CNOT": CRZ_CNOT,
            "controlled_Rz_synthesized_Rz_instances": CRZ_RZ_SYNTH,
            "controlled_H_CNOT": CH_CNOT,
            "controlled_H_T": CH_T,
            "exact_Toffoli_CNOT": TOFFOLI_CNOT,
            "exact_Toffoli_T": TOFFOLI_T,
        },
        "common_outer_layer": common,
        "incumbent": inc_r,
        "successor": suc_r,
        "replay_bindings": binds,
        "comparisons": comparisons,
        "proof_carrying_replay_pass": all(binds.values()),
        "full_R5_closure": False,
        "remaining": ["independent_second_implementation", "donor_composed_audit", "hostile_novelty_authority"],
    }
    print("ORIONQ_MAX_R5B_PROOF_OUTER=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
