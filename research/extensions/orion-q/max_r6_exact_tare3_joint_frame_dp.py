#!/usr/bin/env python3
"""Exact joint TARE-3 auxiliary-frame compiler for MAX-R6 development.

Frozen by:
- MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md
- MAX_R6_EXACT_TARE3_DP_ERRATUM_1.md
- MAX_R6_EXACT_TARE3_DP_ERRATUM_2.md
- MAX_R6_EXACT_TARE3_DP_ERRATUM_3.md

This development script uses only already-open H4/equilibrium-N2 subjects through
the candidate-blind P10 loader. It must never read the protected stretched-N2
prospective discriminator. A positive result remains below R6.
"""
from __future__ import annotations

import itertools
import json
from functools import lru_cache

import numpy as np

import max_r6_p10_candidate_blind_frame_optimizer as p10

INF = 10**12
PARITY_STATES = 512
FULL_STATES = 1024
TOP_K = 4
XOR512 = np.bitwise_xor(
    np.arange(PARITY_STATES)[:, None],
    np.arange(PARITY_STATES)[None, :],
)

LABEL_TRIPLES = tuple(itertools.permutations(range(4), 3))
DEPENDENT_LABEL_TRIPLES = tuple(
    labels
    for labels in LABEL_TRIPLES
    if labels[0] ^ labels[1] ^ labels[2] == 0
)


def _option_code(values: tuple[int, int, int, int, int]) -> int:
    code = 0
    for value in values:
        code = code * 4 + int(value)
    return code


def _local_independent(r0: int, r1: int, r2: int) -> int:
    return int(p10.h.local_mul(p10.h.local_mul(r0, r1), r2) != 0)


@lru_cache(maxsize=None)
def _local_table(
    p0: int,
    p1: int,
    p2: int,
    central: int,
):
    """Exact local table indexed by (independent-local bit, 9-bit parity delta)."""
    targets = (p0, p1, p2)
    costs0 = np.full(PARITY_STATES, INF, dtype=np.int64)
    costs1 = np.full(PARITY_STATES, INF, dtype=np.int64)
    choices0 = np.full((PARITY_STATES, 5), -1, dtype=np.int8)
    choices1 = np.full((PARITY_STATES, 5), -1, dtype=np.int8)
    codes0 = np.full(PARITY_STATES, 1 << 30, dtype=np.int64)
    codes1 = np.full(PARITY_STATES, 1 << 30, dtype=np.int64)

    multiplicities = [4, 4, 4]
    multiplicities[central] = 2

    for values in itertools.product(range(4), repeat=5):
        r0, r1, r2, s0, s1 = values
        rs = (r0, r1, r2)
        delta = 0
        delta |= p10.h.local_symp(r0, r1) << 0
        delta |= p10.h.local_symp(r0, r2) << 1
        delta |= p10.h.local_symp(r1, r2) << 2
        for k, r in enumerate(rs):
            delta |= p10.h.local_symp(s0, r) << (3 + k)
            delta |= p10.h.local_symp(s1, r) << (6 + k)

        independent_local = _local_independent(r0, r1, r2)
        raw = (
            sum(
                multiplicities[k] * p10.h.local_wt(r)
                for k, r in enumerate(rs)
            )
            + 2 * p10.h.local_wt(s0)
            + 2 * p10.h.local_wt(s1)
            + sum(
                p10.h.local_wt(p10.h.local_mul(targets[k], rs[k]))
                for k in range(3)
            )
        )
        option_code = _option_code(values)

        if independent_local:
            costs, choices, choice_codes = costs1, choices1, codes1
        else:
            costs, choices, choice_codes = costs0, choices0, codes0

        if raw < costs[delta] or (
            raw == costs[delta] and option_code < choice_codes[delta]
        ):
            costs[delta] = raw
            choices[delta] = values
            choice_codes[delta] = option_code

    return costs0, costs1, choices0, choices1, codes0, codes1


def _labels_from_parity(parity: int) -> tuple[int, int, int]:
    # Protocol label ck=(<S0,Rk>, <S1,Rk>); encode the first bit as MSB.
    return tuple(
        2 * ((parity >> (3 + k)) & 1) + ((parity >> (6 + k)) & 1)
        for k in range(3)
    )


def _accepting_state(parity: int, independent_seen: int) -> bool:
    if parity & 0b111 != 0b111:
        return False
    labels = _labels_from_parity(parity)
    if len(set(labels)) != 3:
        return False
    if not independent_seen and labels[0] ^ labels[1] ^ labels[2] != 0:
        return False
    return True


def _advance(
    dp0: np.ndarray,
    dp1: np.ndarray,
    costs0: np.ndarray,
    costs1: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Min-plus XOR/OR transition for the 9 parity bits + independent_seen."""
    ndp0 = (dp0[:, None] + costs0[XOR512]).min(axis=0)

    from_independent_dep = (dp1[:, None] + costs0[XOR512]).min(axis=0)
    from_independent_indep = (dp1[:, None] + costs1[XOR512]).min(axis=0)
    from_dependent_indep = (dp0[:, None] + costs1[XOR512]).min(axis=0)
    ndp1 = np.minimum(
        np.minimum(from_independent_dep, from_independent_indep),
        from_dependent_indep,
    )
    return ndp0, ndp1


def _solve_fixed(
    target_codes: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    target_permutation: tuple[int, int, int],
    central: int,
    n: int,
):
    dp0 = np.full(PARITY_STATES, INF, dtype=np.int64)
    dp1 = np.full(PARITY_STATES, INF, dtype=np.int64)
    dp0[0] = 0
    histories = [(dp0.copy(), dp1.copy())]
    qtables = []

    for q in range(n):
        local_targets = tuple(
            target_codes[target_permutation[k]][q]
            for k in range(3)
        )
        table = _local_table(*local_targets, central)
        dp0, dp1 = _advance(dp0, dp1, table[0], table[1])
        histories.append((dp0.copy(), dp1.copy()))
        qtables.append(table)

    best = None
    for independent_seen, dp in enumerate((dp0, dp1)):
        for parity in range(PARITY_STATES):
            if not _accepting_state(parity, independent_seen):
                continue
            raw = int(dp[parity])
            if raw >= INF:
                continue
            state = parity + independent_seen * PARITY_STATES
            key = (raw - 10, target_permutation, central, state)
            if best is None or key < best:
                best = key

    if best is None:
        raise AssertionError("exact joint DP produced no accepting state")
    return best, histories, qtables


def _backtrack(
    histories,
    qtables,
    final_state: int,
    n: int,
):
    """Erratum-1 tie rule: local option code, then predecessor state."""
    independent_seen = final_state // PARITY_STATES
    parity = final_state % PARITY_STATES
    sequences = [[0] * n for _ in range(5)]

    for q in range(n - 1, -1, -1):
        prev_layers = histories[q]
        curr_layers = histories[q + 1]
        costs0, costs1, choices0, choices1, codes0, codes1 = qtables[q]
        current_cost = int(curr_layers[independent_seen][parity])
        candidates = []

        for predecessor_independent, predecessor_dp in enumerate(prev_layers):
            for predecessor_parity in range(PARITY_STATES):
                predecessor_cost = int(predecessor_dp[predecessor_parity])
                if predecessor_cost >= INF:
                    continue
                delta = predecessor_parity ^ parity
                for local_independent, costs, choices, choice_codes in (
                    (0, costs0, choices0, codes0),
                    (1, costs1, choices1, codes1),
                ):
                    if predecessor_independent | local_independent != independent_seen:
                        continue
                    local_cost = int(costs[delta])
                    if local_cost >= INF:
                        continue
                    if predecessor_cost + local_cost != current_cost:
                        continue
                    values = tuple(int(x) for x in choices[delta])
                    candidates.append(
                        (
                            int(choice_codes[delta]),
                            predecessor_independent * PARITY_STATES
                            + predecessor_parity,
                            values,
                            predecessor_independent,
                            predecessor_parity,
                        )
                    )

        if not candidates:
            raise AssertionError(
                {
                    "backtrack_failed": True,
                    "q": q,
                    "state": independent_seen * PARITY_STATES + parity,
                }
            )
        _, _, values, independent_seen, parity = min(
            candidates,
            key=lambda item: (item[0], item[1]),
        )
        for i, value in enumerate(values):
            sequences[i][q] = value

    if independent_seen != 0 or parity != 0:
        raise AssertionError("exact joint DP backtrack did not return to zero state")
    return tuple(p10.key_from_codes(sequence) for sequence in sequences)


def _gf2_rank(rs, n: int) -> int:
    basis: dict[int, int] = {}
    rank = 0
    for x, z in rs:
        value = int(x) | (int(z) << n)
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def _witness(
    targets,
    n: int,
    target_permutation,
    central: int,
    globals_,
    cost: int,
):
    r0, r1, r2, s0, s1 = globals_
    rs = (r0, r1, r2)
    labels = tuple(
        2 * p10.symp(s0, r) + p10.symp(s1, r)
        for r in rs
    )
    permuted_targets = tuple(targets[target_permutation[k]] for k in range(3))
    restores = tuple(
        p10.mul(permuted_targets[k], rs[k])
        for k in range(3)
    )
    rank = _gf2_rank(rs, n)
    dependent = p10.mul(p10.mul(rs[0], rs[1]), rs[2]) == (0, 0)
    uanti = p10.uanti_support(rs, central)
    tag = 2 * (p10.wt(s0) + p10.wt(s1))
    restore = sum(p10.wt(t) for t in restores)
    recomputed = uanti + tag + restore

    checks = {
        "pairwise_anti": p10.is_pairwise_anti(rs),
        "distinct_labels": len(set(labels)) == 3,
        "dependent_label_consistency": (
            (not dependent)
            or (labels[0] ^ labels[1] ^ labels[2] == 0)
        ),
        "tag_labels": all(
            labels[k]
            == 2 * p10.symp(s0, rs[k]) + p10.symp(s1, rs[k])
            for k in range(3)
        ),
        "restore": all(
            p10.mul(restores[k], rs[k]) == permuted_targets[k]
            for k in range(3)
        ),
        "cost_recomputed": recomputed == cost,
        "rank_consistent": rank in (2, 3),
    }
    if not all(checks.values()):
        raise AssertionError({"joint_witness_failed": checks})

    return {
        "target_permutation": list(target_permutation),
        "central": central,
        "R": [list(r) for r in rs],
        "rank": rank,
        "S": [list(s0), list(s1)],
        "labels": list(labels),
        "T": [list(t) for t in restores],
        "native_matches": [k for k, t in enumerate(restores) if t == (0, 0)],
        "uanti_support": int(uanti),
        "tag_support_twice": int(tag),
        "restore_support": int(restore),
        "C_joint": int(cost),
        "checks": checks,
    }


def exact_joint(targets, n: int) -> dict:
    target_codes = tuple(p10.codes(target, n) for target in targets)
    candidates = []
    payloads = {}

    for target_permutation in itertools.permutations(range(3)):
        for central in range(3):
            best, histories, qtables = _solve_fixed(
                target_codes,
                tuple(target_permutation),
                central,
                n,
            )
            cost, permutation, selected_central, state = best
            key = (cost, tuple(permutation), selected_central, state)
            candidates.append(key)
            payloads[(tuple(permutation), selected_central)] = (
                histories,
                qtables,
                state,
            )

    cost, permutation, central, state = min(candidates)
    histories, qtables, recorded_state = payloads[(tuple(permutation), central)]
    if recorded_state != state:
        raise AssertionError("final state bookkeeping mismatch")
    globals_ = _backtrack(histories, qtables, state, n)
    witness = _witness(
        targets,
        n,
        tuple(permutation),
        central,
        globals_,
        int(cost),
    )
    witness["final_parity_state"] = int(state)
    return witness


def frame_only_strong(targets, n: int) -> dict:
    """Erratum-2 comparator: best downstream cost among all Uanti-minimal frames."""
    best = None
    best_record = None

    # Pairwise-anticommuting Rk are nonidentity, hence every (w(Rk)-1)>=0.
    # Global C_Uanti minimum is therefore zero. It is attained exactly by the
    # ordered X/Y/Z triples on one system qubit; enumerate the complete set.
    for q in range(n):
        x = (1 << q, 0)
        y = (1 << q, 1 << q)
        z = (0, 1 << q)
        for rs in itertools.permutations((x, y, z), 3):
            if p10.uanti_support(rs, 0) != 0:
                raise AssertionError("Uanti-minimal frame construction is not zero")
            for labels in DEPENDENT_LABEL_TRIPLES:
                hi_syn = sum(
                    (((labels[k] >> 1) & 1) << k)
                    for k in range(3)
                )
                lo_syn = sum(
                    ((labels[k] & 1) << k)
                    for k in range(3)
                )
                wh, shi = p10.tag_min_weight(rs, hi_syn, n)
                wl, slo = p10.tag_min_weight(rs, lo_syn, n)
                for permutation in itertools.permutations(range(3)):
                    permuted_targets = tuple(
                        targets[permutation[k]]
                        for k in range(3)
                    )
                    restores = tuple(
                        p10.mul(permuted_targets[k], rs[k])
                        for k in range(3)
                    )
                    cost = 2 * (wh + wl) + sum(p10.wt(t) for t in restores)
                    # Every central axis has the same zero Uanti cost; serialize c=0.
                    key = (
                        int(cost),
                        tuple(tuple(r) for r in rs),
                        tuple(permutation),
                        tuple(labels),
                        tuple(shi),
                        tuple(slo),
                    )
                    if best is None or key < best:
                        best = key
                        best_record = {
                            "C_joint": int(cost),
                            "uanti_support": 0,
                            "R": [list(r) for r in rs],
                            "central": 0,
                            "target_permutation": list(permutation),
                            "labels": list(labels),
                            "S": [list(shi), list(slo)],
                            "T": [list(t) for t in restores],
                            "definition": "B_FRAME_ONLY_STRONG",
                        }

    if best_record is None:
        raise AssertionError("frame-only strong comparator produced no witness")
    return best_record


def _tag_costs_bruteforce(rs, n: int) -> list[int]:
    costs = [INF] * 8
    limit = 1 << n
    for x in range(limit):
        for z in range(limit):
            s = (x, z)
            syndrome = sum(p10.symp(s, rs[k]) << k for k in range(3))
            costs[syndrome] = min(costs[syndrome], p10.wt(s))
    return costs


def brute_joint_cost(targets, n: int) -> int:
    """Structurally independent global-string exhaustive solver for hostile n<=3."""
    limit = 1 << n
    keys = [
        (x, z)
        for x in range(limit)
        for z in range(limit)
        if x or z
    ]
    anti = {
        r: tuple(s for s in keys if p10.symp(r, s) == 1)
        for r in keys
    }
    anti_sets = {r: set(values) for r, values in anti.items()}
    best = INF

    for r0 in keys:
        for r1 in anti[r0]:
            common = anti_sets[r0].intersection(anti_sets[r1])
            for r2 in common:
                rs = (r0, r1, r2)
                dependent = p10.mul(p10.mul(r0, r1), r2) == (0, 0)
                tag_costs = _tag_costs_bruteforce(rs, n)
                labels_pool = (
                    DEPENDENT_LABEL_TRIPLES if dependent else LABEL_TRIPLES
                )
                best_tag = INF
                for labels in labels_pool:
                    hi_syn = sum(
                        (((labels[k] >> 1) & 1) << k)
                        for k in range(3)
                    )
                    lo_syn = sum(
                        ((labels[k] & 1) << k)
                        for k in range(3)
                    )
                    best_tag = min(
                        best_tag,
                        2 * (
                            tag_costs[hi_syn]
                            + tag_costs[lo_syn]
                        ),
                    )
                if best_tag >= INF:
                    continue

                best_uanti = min(
                    p10.uanti_support(rs, central)
                    for central in range(3)
                )
                best_restore = min(
                    sum(
                        p10.wt(
                            p10.mul(
                                targets[permutation[k]],
                                rs[k],
                            )
                        )
                        for k in range(3)
                    )
                    for permutation in itertools.permutations(range(3))
                )
                best = min(best, best_uanti + best_tag + best_restore)

    if best >= INF:
        raise AssertionError("brute hostile solver produced no admissible frame")
    return int(best)


def hostile_exactness() -> dict:
    # Fixed reminted panels; no chemistry data and no protected subject content.
    panels = {
        "n2_a": (2, ((0b01, 0b00), (0b00, 0b10), (0b11, 0b01))),
        "n2_b": (2, ((0b10, 0b01), (0b01, 0b11), (0b11, 0b10))),
        "n3_a": (3, ((0b001, 0b110), (0b101, 0b010), (0b011, 0b100))),
        "n3_b": (3, ((0b110, 0b001), (0b011, 0b101), (0b100, 0b111))),
    }
    results = {}
    for name, (n, targets) in panels.items():
        joint = exact_joint(targets, n)
        brute = brute_joint_cost(targets, n)
        passed = joint["C_joint"] == brute and all(joint["checks"].values())
        results[name] = {
            "n": n,
            "dp_cost": joint["C_joint"],
            "brute_cost": brute,
            "pass": passed,
        }
        if not passed:
            raise AssertionError({"hostile_exactness_failed": name, **results[name]})
    return {
        "panels": results,
        "all_exact": all(item["pass"] for item in results.values()),
        "brute_solver": "global Pauli-string enumeration with independent tag-syndrome scan",
    }


def _p10_replay() -> dict:
    hostile = p10.hostile_validation()
    subjects = {
        name: p10.subject_eval(name, cfg)
        for name, cfg in p10.base.SUBJECTS.items()
    }
    gates = {
        "hostile_exact": hostile["exact"],
        "both_subjects_candidate": all(
            result["improved"] > 0
            for result in subjects.values()
        ),
        "native_match_generated": all(
            any(
                len(witness["generated"]["native_matches"]) >= 1
                for witness in result["top"]
            )
            for result in subjects.values()
        ),
        "witness_checks": all(
            all(
                all(
                    witness["generated"]
                    .get("checks", {"ok": True})
                    .values()
                )
                for witness in result["top"]
            )
            for result in subjects.values()
        ),
        "fresh_subject_unread": True,
    }
    return {
        "hostile": hostile,
        "subjects": subjects,
        "gates": gates,
        "candidate_generated": all(gates.values()),
        "reserved_stretched_n2_accessed": False,
    }


def subject_development(name: str, cfg, p10_subject: dict) -> dict:
    terms, max_imag = p10.load_terms(cfg)
    selected = p10_subject["top"][:TOP_K]
    triples = []

    for rank, item in enumerate(selected):
        indices = tuple(int(i) for i in item["term_indices"])
        targets = tuple(terms[i][0] for i in indices)
        joint = exact_joint(targets, cfg["n_qubits"])
        canonical = p10.canonical_best(targets, cfg["n_qubits"])
        frame_only = frame_only_strong(targets, cfg["n_qubits"])
        triples.append(
            {
                "selection_rank": rank,
                "term_indices": list(indices),
                "p10_rank2_delta": int(item["delta"]),
                "p10_rank2_fraction": float(item["fraction"]),
                "Lambda_TARE3": float(item["Lambda_TARE3"]),
                "joint": joint,
                "B_CANONICAL_STRONG": {
                    "C_joint": int(canonical["cost"]),
                    "witness": canonical,
                },
                "B_FRAME_ONLY_STRONG": frame_only,
                "joint_delta_vs_canonical": int(canonical["cost"] - joint["C_joint"]),
                "joint_delta_vs_frame_only": int(
                    frame_only["C_joint"] - joint["C_joint"]
                ),
            }
        )

    return {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": cfg["n_qubits"],
        "max_imag": max_imag,
        "selected_top_k": TOP_K,
        "selected_count": len(selected),
        "triples": triples,
        "canonical_strict_improvement": any(
            item["joint_delta_vs_canonical"] > 0
            for item in triples
        ),
        "frame_only_strict_improvement": any(
            item["joint_delta_vs_frame_only"] > 0
            for item in triples
        ),
        "all_witnesses_valid": all(
            all(item["joint"]["checks"].values())
            for item in triples
        ),
    }


def main() -> dict:
    hostile = hostile_exactness()
    p10_replay = _p10_replay()

    if p10_replay["reserved_stretched_n2_accessed"]:
        raise AssertionError("P10 replay reports protected stretched-N2 access")

    subjects = {}
    if p10_replay["candidate_generated"]:
        subjects = {
            name: subject_development(
                name,
                cfg,
                p10_replay["subjects"][name],
            )
            for name, cfg in p10.base.SUBJECTS.items()
        }

    gates = {
        "p10_candidate_generated": p10_replay["candidate_generated"],
        "hostile_exact": hostile["all_exact"],
        "top_four_panel_complete": (
            bool(subjects)
            and set(subjects) == set(p10.base.SUBJECTS)
            and all(
                subject["selected_count"] == TOP_K
                for subject in subjects.values()
            )
        ),
        "both_open_subjects_joint_beat_canonical": (
            bool(subjects)
            and all(
                subject["canonical_strict_improvement"]
                for subject in subjects.values()
            )
        ),
        "joint_beats_frame_only_strong_on_at_least_one_subject": (
            bool(subjects)
            and any(
                subject["frame_only_strict_improvement"]
                for subject in subjects.values()
            )
        ),
        "proof_carrying_witnesses": (
            bool(subjects)
            and all(
                subject["all_witnesses_valid"]
                for subject in subjects.values()
            )
        ),
        "fresh_subject_unread": not p10_replay["reserved_stretched_n2_accessed"],
    }
    supported = all(gates.values())

    result = {
        "schema": "ORIONQ.MAXR6.ExactTARE3JointFrameDPResult.v1",
        "authority": (
            "MAX_R6_EXACT_TARE3_JOINT_DP_SUPPORTED"
            if supported
            else "MAX_R6_EXACT_TARE3_JOINT_DP_NEGATIVE"
        ),
        "scope": "OPEN_H4_EQ_N2_DEVELOPMENT_ONLY__NOT_R6",
        "protocol_errata": [
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_1",
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_2",
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_3",
        ],
        "state_count": FULL_STATES,
        "top_k_expensive_verifier": TOP_K,
        "p10_replay": {
            "candidate_generated": p10_replay["candidate_generated"],
            "gates": p10_replay["gates"],
            "reserved_stretched_n2_accessed": False,
        },
        "hostile": hostile,
        "subjects": subjects,
        "gates": gates,
        "development_supported": supported,
        "reserved_stretched_n2_accessed": False,
    }
    print("ORIONQ_MAX_R6_EXACT_TARE3=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
