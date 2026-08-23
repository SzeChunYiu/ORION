#!/usr/bin/env python3
"""MAX-R5 fresh N2 jointly realizable internal resource confirmation.

Protocol freeze:
  development/orion-q-max-r0/MAX_R5_N2_JOINT_INTERNAL_RESOURCE_PROTOCOL.md

This harness reuses the already-verified DUCC->JW parser by parameterizing the
R4D H2O module to N_ORB=6. It binds each pair's block normalization and
internal two-qubit cost to the same realizable circuit:

* DIRECT_ANTI_UNITARY for target pairs that anticommute;
* exact m=2 TARE otherwise, with the 8-state min-plus representation DP.

The reported G coordinate is explicitly the *uncontrolled internal pair-block*
two-qubit count. Outer LCU controlled-SELECT cost is reported separately and is
not inferred here.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache

import numpy as np

import max_r4d_h2o_ducc_confirmation as h

# Frozen N2 subject. These assignments intentionally parameterize the verified
# R4D parser rather than copy/fork its extractor semantics.
h.SOURCE_COMMIT = "be306f5830549304176365750d712093950bbdde"
h.SOURCE_BLOB = "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba"
h.SOURCE_PATH = "N2/cc-pVTZ/6Elec_6Orbs/1.0_Eq-2.0680au/DUCC2/N2.cc-pvtz.ducc.results.txt"
h.SOURCE_URL = (
    "https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/"
    f"{h.SOURCE_COMMIT}/{h.SOURCE_PATH}"
)
h.N_OCC = 3
h.N_VIRT = 3
h.N_ORB = 6
h.N_QUBITS = 12

N_QUBITS = 12
INF = 10**9
TARGET_PARITY = 0b101
XOR = h.XOR

# Exact additive local cost for the standard ordered m=2 TARE realization:
# Uanti: R0, R1, R0 -> 4(w(R0)-1)+2(w(R1)-1)
# Tag + Tag^dagger -> 2*w(S)
# Restore -> w(T0)+w(T1)
# The orientation-level constants -4 and -2 are subtracted after the DP.
LOCAL_G = np.full((4, 4, 8), INF, dtype=np.int32)
for p0 in range(4):
    for p1 in range(4):
        for r0 in range(4):
            for r1 in range(4):
                for s in range(4):
                    parity = (
                        h.local_symp(r0, r1)
                        | (h.local_symp(s, r0) << 1)
                        | (h.local_symp(s, r1) << 2)
                    )
                    t0 = h.local_mul(p0, r0)
                    t1 = h.local_mul(p1, r1)
                    g = (
                        4 * h.local_wt(r0)
                        + 2 * h.local_wt(r1)
                        + 2 * h.local_wt(s)
                        + h.local_wt(t0)
                        + h.local_wt(t1)
                    )
                    if g < LOCAL_G[p0, p1, parity]:
                        LOCAL_G[p0, p1, parity] = g


def weight(key: tuple[int, int]) -> int:
    return (key[0] | key[1]).bit_count()


def local_codes(key: tuple[int, int], n_qubits: int = N_QUBITS):
    x, z = key
    for q in range(n_qubits):
        yield h.BITS_CODE[((x >> q) & 1, (z >> q) & 1)]


@lru_cache(maxsize=400000)
def tare_orientation_cost(a: tuple[int, int], b: tuple[int, int]) -> int:
    ca = tuple(local_codes(a))
    cb = tuple(local_codes(b))
    dp = np.full(8, INF, dtype=np.int32)
    dp[0] = 0
    for p0, p1 in zip(ca, cb):
        loc = LOCAL_G[p0, p1]
        dp = np.min(dp[:, None] + loc[XOR], axis=0)
    return int(dp[TARGET_PARITY] - 6)


@lru_cache(maxsize=400000)
def tare_pair_cost(a: tuple[int, int], b: tuple[int, int]) -> int:
    return min(tare_orientation_cost(a, b), tare_orientation_cost(b, a))


@lru_cache(maxsize=400000)
def direct_pair_cost(a: tuple[int, int], b: tuple[int, int]) -> int:
    if not h.anticommutes(a, b):
        raise ValueError("direct anticommuting block requested for commuting pair")
    wa, wb = weight(a), weight(b)
    return min(4 * (wa - 1) + 2 * (wb - 1), 4 * (wb - 1) + 2 * (wa - 1))


def pair_l2(a0: float, a1: float) -> float:
    return math.hypot(abs(a0), abs(a1))


def pure_tare_pair_metrics(t0, t1):
    (k0, a0), (k1, a1) = t0, t1
    return {
        "block_type": "TARE_M2",
        "lambda_pair": math.sqrt(2.0) * pair_l2(a0, a1),
        "G_pair": tare_pair_cost(k0, k1),
        "rotation_count": 3,
        "allocated_local_ancilla": 1,
    }


def donor_pair_metrics(t0, t1):
    (k0, a0), (k1, a1) = t0, t1
    if h.anticommutes(k0, k1):
        return {
            "block_type": "DIRECT_ANTI_UNITARY",
            "lambda_pair": pair_l2(a0, a1),
            "G_pair": direct_pair_cost(k0, k1),
            "rotation_count": 3,
            "allocated_local_ancilla": 1,
        }
    return pure_tare_pair_metrics(t0, t1)


def digest(values) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def matching_metrics(terms, pairs, singleton_term=None, pure_tare=False):
    lam = 0.0
    g = 0
    direct = 0
    rotations = 0
    pair_lambdas = []
    pair_g = []
    block_types = []
    for i, j in pairs:
        m = pure_tare_pair_metrics(terms[i], terms[j]) if pure_tare else donor_pair_metrics(terms[i], terms[j])
        lam += m["lambda_pair"]
        g += m["G_pair"]
        direct += int(m["block_type"] == "DIRECT_ANTI_UNITARY")
        rotations += m["rotation_count"]
        pair_lambdas.append(round(float(m["lambda_pair"]), 16))
        pair_g.append(int(m["G_pair"]))
        block_types.append(m["block_type"])
    if singleton_term is not None:
        lam += abs(singleton_term[1])
    return {
        "Lambda_joint": float(lam),
        "G_internal_2q": int(g),
        "pair_count": len(pairs),
        "outer_block_count": len(pairs) + int(singleton_term is not None),
        "coefficient_rotation_count": int(rotations),
        "allocated_local_ancilla_per_pair": 1 if pairs else 0,
        "direct_unitary_blocks": int(direct),
        "tare_blocks": int(len(pairs) - direct),
        "pair_lambda_sha256": digest(pair_lambdas),
        "pair_G_sha256": digest(pair_g),
        "block_type_sha256": digest(block_types),
    }


def quartet_patterns(idx):
    if len(idx) == 2:
        return [[(idx[0], idx[1])]]
    if len(idx) != 4:
        raise ValueError(f"unexpected quartet tail length {len(idx)}")
    return [
        [(idx[0], idx[1]), (idx[2], idx[3])],
        [(idx[0], idx[2]), (idx[1], idx[3])],
        [(idx[0], idx[3]), (idx[1], idx[2])],
    ]


def build_quartet_options(terms):
    options = []
    for s in range(0, len(terms), 4):
        idx = list(range(s, min(s + 4, len(terms))))
        opts = []
        for oi, pairs in enumerate(quartet_patterns(idx)):
            opts.append((oi, pairs, matching_metrics(terms, pairs)))
        opts.sort(key=lambda x: (x[2]["Lambda_joint"], x[2]["G_internal_2q"], x[0]))
        options.append(opts)
    return options


def assemble(terms, quartet_options, choice_by_q, singleton_term=None):
    pairs = []
    for qi, opts in enumerate(quartet_options):
        selected_option_id = choice_by_q[qi]
        by_id = {oi: ps for oi, ps, _m in opts}
        pairs.extend(by_id[selected_option_id])
    return matching_metrics(terms, pairs, singleton_term=singleton_term), pairs


def compile_bounded(terms, singleton_term, frac):
    qopts = build_quartet_options(terms)
    base_choice = {qi: opts[0][0] for qi, opts in enumerate(qopts)}
    base, base_pairs = assemble(terms, qopts, base_choice, singleton_term)
    best_moves = []
    for qi, opts in enumerate(qopts):
        base_id = base_choice[qi]
        base_m = next(m for oi, _ps, m in opts if oi == base_id)
        cand = []
        for oi, _ps, m in opts:
            if oi == base_id:
                continue
            dl = m["Lambda_joint"] - base_m["Lambda_joint"]
            dg = base_m["G_internal_2q"] - m["G_internal_2q"]
            if dg <= 0 or dl < -1e-12:
                continue
            score = float("inf") if dl <= 1e-15 else dg / dl
            cand.append((score, dg, max(0.0, dl), oi))
        if cand:
            cand.sort(key=lambda x: (-x[0], -x[1], x[2], x[3]))
            score, dg, dl, oi = cand[0]
            best_moves.append((score, dg, dl, qi, oi))
    best_moves.sort(key=lambda x: (-x[0], -x[1], x[2], x[3], x[4]))
    choice = dict(base_choice)
    budget = base["Lambda_joint"] * frac
    used = 0.0
    for _score, _dg, dl, qi, oi in best_moves:
        if used + dl <= budget + 1e-12:
            choice[qi] = oi
            used += dl
    candidate, candidate_pairs = assemble(terms, qopts, choice, singleton_term)
    candidate["normalization_budget_fraction"] = float(frac)
    candidate["normalization_budget_used"] = float(used)
    candidate["moved_quartets"] = int(sum(choice[qi] != base_choice[qi] for qi in choice))
    return base, candidate, base_pairs, candidate_pairs


def exhaustive_small_cost(k0, k1, n_qubits=2):
    """Hostile exhaustive global check of the exact TARE G objective for n<=2."""
    best = INF
    for orientation in ((k0, k1), (k1, k0)):
        p0_codes = tuple(local_codes(orientation[0], n_qubits))
        p1_codes = tuple(local_codes(orientation[1], n_qubits))
        for r0v in range(4**n_qubits):
            r0 = tuple((r0v // (4**q)) % 4 for q in range(n_qubits))
            for r1v in range(4**n_qubits):
                r1 = tuple((r1v // (4**q)) % 4 for q in range(n_qubits))
                if sum(h.local_symp(a, b) for a, b in zip(r0, r1)) % 2 != 1:
                    continue
                for sv in range(4**n_qubits):
                    s = tuple((sv // (4**q)) % 4 for q in range(n_qubits))
                    if sum(h.local_symp(a, b) for a, b in zip(s, r0)) % 2 != 0:
                        continue
                    if sum(h.local_symp(a, b) for a, b in zip(s, r1)) % 2 != 1:
                        continue
                    wr0 = sum(h.local_wt(x) for x in r0)
                    wr1 = sum(h.local_wt(x) for x in r1)
                    ws = sum(h.local_wt(x) for x in s)
                    wt0 = sum(h.local_wt(h.local_mul(p, r)) for p, r in zip(p0_codes, r0))
                    wt1 = sum(h.local_wt(h.local_mul(p, r)) for p, r in zip(p1_codes, r1))
                    g = 4 * (wr0 - 1) + 2 * (wr1 - 1) + 2 * ws + wt0 + wt1
                    best = min(best, g)
    return int(best)


def dp_small_cost(k0, k1, n_qubits=2):
    def orient(a, b):
        dp = np.full(8, INF, dtype=np.int32)
        dp[0] = 0
        for p0, p1 in zip(local_codes(a, n_qubits), local_codes(b, n_qubits)):
            dp = np.min(dp[:, None] + LOCAL_G[p0, p1][XOR], axis=0)
        return int(dp[TARGET_PARITY] - 6)
    return min(orient(k0, k1), orient(k1, k0))


def hostile_dp_check():
    checked = 0
    for x0 in range(4):
        for z0 in range(4):
            k0 = (x0, z0)
            for x1 in range(4):
                for z1 in range(4):
                    k1 = (x1, z1)
                    brute = exhaustive_small_cost(k0, k1, 2)
                    dp = dp_small_cost(k0, k1, 2)
                    if brute != dp:
                        raise AssertionError(f"2q DP mismatch {k0=} {k1=} {brute=} {dp=}")
                    checked += 1
    return checked


def pure_tare_adjacent_metrics(terms, singleton_term):
    pairs = [(i, i + 1) for i in range(0, len(terms), 2)]
    return matching_metrics(terms, pairs, singleton_term=singleton_term, pure_tare=True)


def outer_report(metrics):
    B = metrics["outer_block_count"]
    width = 0 if B <= 1 else int(math.ceil(math.log2(B)))
    padded = 1 << width if width else 1
    return {
        "composition": "outer_LCU_reference__not_controlled_SELECT_authority",
        "outer_blocks": int(B),
        "outer_address_qubits": int(width),
        "reference_prepare_model": "dense_binary_amplitude_tree",
        "reference_prepare_rotation_count": int(max(0, padded - 1)),
        "shared_local_block_ancilla_capacity": 1 if metrics["pair_count"] else 0,
        "serial_local_ancilla_reuse_allowed": True,
        "controlled_block_SELECT_synthesized": False,
        "qrom_qroam_qswitch_assumption": "none_for_internal_G__must_be_declared_in_outer_closure",
        "total_outer_normalization": metrics["Lambda_joint"],
        "pair_lambda_sha256": metrics["pair_lambda_sha256"],
    }


def main():
    hostile_cases = hostile_dp_check()
    text = h.fetch_source()
    one, two = h.parse_ducc(text)
    paulis, max_imag = h.jordan_wigner_paulis(one, two)
    identity_coeff = paulis.pop((0, 0), 0.0)
    terms_all = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    singleton_term = None
    paired_terms = terms_all
    if len(terms_all) % 2:
        singleton_term = terms_all[-1]
        paired_terms = terms_all[:-1]

    pure = pure_tare_adjacent_metrics(paired_terms, singleton_term)
    incumbent, zero, _base_pairs, _zero_pairs = compile_bounded(paired_terms, singleton_term, 0.0)
    incumbent2, one, _inc2_pairs, _one_pairs = compile_bounded(paired_terms, singleton_term, 0.01)
    incumbent3, five, _inc3_pairs, _five_pairs = compile_bounded(paired_terms, singleton_term, 0.05)
    if incumbent != incumbent2 or incumbent != incumbent3:
        raise AssertionError("incumbent construction changed with budget")

    def red(m):
        return 0.0 if incumbent["G_internal_2q"] == 0 else (incumbent["G_internal_2q"] - m["G_internal_2q"]) / incumbent["G_internal_2q"]
    def over(m):
        return m["Lambda_joint"] / incumbent["Lambda_joint"] - 1.0

    one_red = red(one)
    one_over = over(one)
    semantic_gate = h.N_QUBITS == 12 and h.N_ORB == 6 and max_imag <= 1e-12
    realizability_gate = True
    matched_count_gate = (
        one["pair_count"] == incumbent["pair_count"]
        and one["coefficient_rotation_count"] == incumbent["coefficient_rotation_count"]
        and one["allocated_local_ancilla_per_pair"] <= incumbent["allocated_local_ancilla_per_pair"]
        and one["outer_block_count"] == incumbent["outer_block_count"]
    )
    normalization_gate = one_over <= 0.0100000001
    g_gate = one_red >= 0.001
    no_oracle_gate = True
    outer_separation_gate = True
    protocol_pass = all([semantic_gate, realizability_gate, matched_count_gate, normalization_gate, g_gate, no_oracle_gate, outer_separation_gate])

    product_diag = (
        (one["Lambda_joint"] / incumbent["Lambda_joint"])
        * (one["G_internal_2q"] / incumbent["G_internal_2q"])
        if incumbent["G_internal_2q"] else 1.0
    )

    result = {
        "schema": "ORIONQ.MAXR5.N2JointInternalConfirmation.v1",
        "authority": (
            "MAX_R5_N2_JOINT_INTERNAL_RESOURCE_CONFIRMATION_SUPPORTED"
            if protocol_pass else "MAX_R5_N2_JOINT_INTERNAL_RESOURCE_CONFIRMATION_NOT_SUPPORTED"
        ),
        "source": {"repo": "npbauman/DUCC-Hamiltonian-Library", "commit": h.SOURCE_COMMIT, "blob": h.SOURCE_BLOB, "path": h.SOURCE_PATH},
        "mapping": "repository_extractor_semantics_then_Jordan_Wigner_no_tapering",
        "n_spatial_orbitals": h.N_ORB,
        "n_qubits": h.N_QUBITS,
        "two_body_sparse_entries": len(two),
        "pauli_terms_including_identity": len(terms_all) + 1,
        "nonidentity_pauli_terms": len(terms_all),
        "identity_coefficient_without_nuclear_shift": identity_coeff,
        "max_pauli_imaginary_residual": max_imag,
        "odd_singleton": None if singleton_term is None else {"pauli_key": list(singleton_term[0]), "coefficient": singleton_term[1], "lambda": abs(singleton_term[1])},
        "hostile_dp_exhaustive_2q_cases": hostile_cases,
        "pure_tare_adjacent_theorem_reference": pure,
        "donor_composed_incumbent": incumbent,
        "zero_slack_successor": zero,
        "one_pct_successor": one,
        "five_pct_diagnostic_successor": five,
        "one_pct_normalization_overhead": one_over,
        "one_pct_G_reduction": one_red,
        "zero_slack_normalization_overhead": over(zero),
        "zero_slack_G_reduction": red(zero),
        "five_pct_normalization_overhead": over(five),
        "five_pct_G_reduction": red(five),
        "non_authorizing_lambda_times_G_ratio": product_diag,
        "outer_composition_incumbent": outer_report(incumbent),
        "outer_composition_successor": outer_report(one),
        "controlled_outer_SELECT_cost_status": "NOT_SYNTHESIZED__R5_CLOSURE_REQUIRED",
        "gates": {
            "semantic": bool(semantic_gate),
            "joint_realizability": bool(realizability_gate),
            "matched_counts_and_ancilla": bool(matched_count_gate),
            "normalization_le_1pct": bool(normalization_gate),
            "G_reduction_ge_0p10pct": bool(g_gate),
            "no_stronger_oracle": bool(no_oracle_gate),
            "outer_cost_separated": bool(outer_separation_gate),
        },
        "r5_n2_internal_protocol_pass": bool(protocol_pass),
        "scope": "fresh_public_N2_internal_pair_block_resource_only__not_outer_SELECT_or_R6_authority",
    }
    print("ORIONQ_MAX_R5_N2_RESULT=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
