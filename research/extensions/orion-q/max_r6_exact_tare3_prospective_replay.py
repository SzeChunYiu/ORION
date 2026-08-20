#!/usr/bin/env python3
"""Structurally independent replay for the frozen exact-TARE3 R6 prospect.

The primary performs the gated protected-source read. This verifier consumes its
serialized proof-carrying receipt, reconstructs every selected Pauli triple, and
recomputes the exact joint optimum and both frozen comparator optima with a
separately coded implementation. It never calls the primary solver for an
optimality decision.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import max_r6_exact_tare3_prospective_primary as primary

ROOT = Path(__file__).resolve().parents[3]
PRIMARY_PATH = "research/extensions/orion-q/max_r6_exact_tare3_prospective_primary.py"
PRIMARY_BLOB = "06151630efc66f73f2e0013f82a9b0bc92171c78"
NOVELTY_PATH = "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_FINAL_HOSTILE_NOVELTY_FREEZE.md"
NOVELTY_BLOB = "93e6daa21083890e8474eab4ef737c5805a9b8b8"
PROSPECTIVE_PROTOCOL_PATH = "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_PROSPECTIVE_PROTOCOL.md"
PROSPECTIVE_PROTOCOL_BLOB = "b9c11f683ccf5246b1e9a601ca717dd88cd4821f"

INF = 10**12
PARITY_STATES = 512
XOR512 = np.bitwise_xor(
    np.arange(PARITY_STATES)[:, None],
    np.arange(PARITY_STATES)[None, :],
)
ALL_LABELS = tuple(itertools.permutations(range(4), 3))
DEPENDENT_LABELS = tuple(row for row in ALL_LABELS if row[0] ^ row[1] ^ row[2] == 0)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def mul(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return int(a[0]) ^ int(b[0]), int(a[1]) ^ int(b[1])


def wt(a: tuple[int, int]) -> int:
    return (int(a[0]) | int(a[1])).bit_count()


def symp(a: tuple[int, int], b: tuple[int, int]) -> int:
    return (
        ((int(a[0]) & int(b[1])).bit_count())
        + ((int(a[1]) & int(b[0])).bit_count())
    ) & 1


def local_code(target: tuple[int, int], q: int) -> int:
    return ((target[0] >> q) & 1) | (((target[1] >> q) & 1) << 1)


def local_symp(a: int, b: int) -> int:
    ax, az = a & 1, (a >> 1) & 1
    bx, bz = b & 1, (b >> 1) & 1
    return (ax * bz + az * bx) & 1


def local_wt(a: int) -> int:
    return int(a != 0)


def uanti_support(rs: tuple[tuple[int, int], ...], central: int) -> int:
    multiplicities = [4, 4, 4]
    multiplicities[central] = 2
    return sum(multiplicities[k] * (wt(rs[k]) - 1) for k in range(3))


def pairwise_anti(rs: tuple[tuple[int, int], ...]) -> bool:
    return all(symp(rs[i], rs[j]) == 1 for i in range(3) for j in range(i + 1, 3))


def gf2_rank(rs: tuple[tuple[int, int], ...], n: int) -> int:
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


def tag_min_weight(rs: tuple[tuple[int, int], ...], syndrome: int, n: int) -> int:
    dp = [INF] * 8
    dp[0] = 0
    for q in range(n):
        local = [INF] * 8
        for s in range(4):
            delta = 0
            for k, r in enumerate(rs):
                delta |= local_symp(s, local_code(r, q)) << k
            local[delta] = min(local[delta], local_wt(s))
        nxt = [INF] * 8
        for old in range(8):
            for delta in range(8):
                nxt[old ^ delta] = min(nxt[old ^ delta], dp[old] + local[delta])
        dp = nxt
    if dp[syndrome] >= INF:
        raise AssertionError({"independent_tag_unsolved": syndrome})
    return int(dp[syndrome])


@lru_cache(maxsize=None)
def independent_local_table(p0: int, p1: int, p2: int, central: int):
    targets = (p0, p1, p2)
    dep = np.full(PARITY_STATES, INF, dtype=np.int64)
    indep = np.full(PARITY_STATES, INF, dtype=np.int64)
    multiplicities = [4, 4, 4]
    multiplicities[central] = 2

    for r0, r1, r2, s0, s1 in itertools.product(range(4), repeat=5):
        rs = (r0, r1, r2)
        parity = 0
        parity |= local_symp(r0, r1) << 0
        parity |= local_symp(r0, r2) << 1
        parity |= local_symp(r1, r2) << 2
        for k, r in enumerate(rs):
            parity |= local_symp(s0, r) << (3 + k)
            parity |= local_symp(s1, r) << (6 + k)

        local_independent = int((r0 ^ r1 ^ r2) != 0)
        raw = (
            sum(multiplicities[k] * local_wt(rs[k]) for k in range(3))
            + 2 * local_wt(s0)
            + 2 * local_wt(s1)
            + sum(local_wt(targets[k] ^ rs[k]) for k in range(3))
        )
        table = indep if local_independent else dep
        if raw < int(table[parity]):
            table[parity] = raw
    return dep, indep


def accepting(parity: int, independent_seen: int) -> bool:
    if parity & 0b111 != 0b111:
        return False
    labels = tuple(
        2 * ((parity >> (3 + k)) & 1) + ((parity >> (6 + k)) & 1)
        for k in range(3)
    )
    if len(set(labels)) != 3:
        return False
    if not independent_seen and labels[0] ^ labels[1] ^ labels[2] != 0:
        return False
    return True


ACCEPT_DEP = np.array([p for p in range(PARITY_STATES) if accepting(p, 0)], dtype=int)
ACCEPT_INDEP = np.array([p for p in range(PARITY_STATES) if accepting(p, 1)], dtype=int)


def independent_joint_cost(targets: tuple[tuple[int, int], ...], n: int) -> int:
    target_codes = tuple(
        tuple(local_code(target, q) for q in range(n))
        for target in targets
    )
    best = INF

    for permutation in itertools.permutations(range(3)):
        for central in range(3):
            layers = np.full((2, PARITY_STATES), INF, dtype=np.int64)
            layers[0, 0] = 0
            for q in range(n):
                p0, p1, p2 = (target_codes[permutation[k]][q] for k in range(3))
                dep, indep = independent_local_table(p0, p1, p2, central)

                dep_from_dep = (layers[0, :, None] + dep[XOR512]).min(axis=0)
                indep_from_dep = (layers[0, :, None] + indep[XOR512]).min(axis=0)
                indep_from_indep_dep = (layers[1, :, None] + dep[XOR512]).min(axis=0)
                indep_from_indep_indep = (layers[1, :, None] + indep[XOR512]).min(axis=0)
                layers = np.vstack(
                    (
                        dep_from_dep,
                        np.minimum.reduce(
                            (indep_from_dep, indep_from_indep_dep, indep_from_indep_indep)
                        ),
                    )
                )

            local_best = min(
                int(layers[0, ACCEPT_DEP].min(initial=INF)),
                int(layers[1, ACCEPT_INDEP].min(initial=INF)),
            )
            best = min(best, local_best - 10)

    if best >= INF:
        raise AssertionError("independent exact-joint replay produced no optimum")
    return int(best)


def independent_canonical_cost(targets: tuple[tuple[int, int], ...], n: int) -> int:
    if n < 2:
        raise ValueError("canonical TARE-3 frame requires n>=2")
    rs = ((1, 0), (1, 1), (2, 1))
    best = INF
    tag_cache: dict[tuple[int, int, int], tuple[int, int]] = {}
    for labels in ALL_LABELS:
        if labels not in tag_cache:
            hi = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
            lo = sum(((labels[k] & 1) << k) for k in range(3))
            tag_cache[labels] = (tag_min_weight(rs, hi, n), tag_min_weight(rs, lo, n))
        wh, wl = tag_cache[labels]
        for permutation in itertools.permutations(range(3)):
            restores = tuple(mul(targets[permutation[k]], rs[k]) for k in range(3))
            restore = sum(wt(t) for t in restores)
            for central in range(3):
                best = min(best, uanti_support(rs, central) + 2 * (wh + wl) + restore)
    return int(best)


def independent_frame_only_cost(targets: tuple[tuple[int, int], ...], n: int) -> int:
    best = INF
    for q in range(n):
        xyz = ((1 << q, 0), (1 << q, 1 << q), (0, 1 << q))
        for rs in itertools.permutations(xyz, 3):
            if not pairwise_anti(tuple(rs)) or uanti_support(tuple(rs), 0) != 0:
                raise AssertionError("independent frame-only minimum characterization failed")
            for labels in DEPENDENT_LABELS:
                hi = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
                lo = sum(((labels[k] & 1) << k) for k in range(3))
                wh = tag_min_weight(tuple(rs), hi, n)
                wl = tag_min_weight(tuple(rs), lo, n)
                for permutation in itertools.permutations(range(3)):
                    restores = tuple(mul(targets[permutation[k]], rs[k]) for k in range(3))
                    best = min(best, 2 * (wh + wl) + sum(wt(t) for t in restores))
    return int(best)


def reconstruct_and_check_witness(row: dict[str, Any], n: int) -> tuple[tuple[tuple[int, int], ...], dict[str, bool]]:
    joint = row["joint"]
    rs = tuple((int(x), int(z)) for x, z in joint["R"])
    ss = tuple((int(x), int(z)) for x, z in joint["S"])
    restores = tuple((int(x), int(z)) for x, z in joint["T"])
    permutation = tuple(int(x) for x in joint["target_permutation"])
    central = int(joint["central"])

    permuted_targets = tuple(mul(restores[k], rs[k]) for k in range(3))
    original: list[tuple[int, int] | None] = [None, None, None]
    for k, source_index in enumerate(permutation):
        original[source_index] = permuted_targets[k]
    if any(item is None for item in original):
        raise AssertionError("invalid target permutation in primary witness")
    targets = tuple(item for item in original if item is not None)

    labels = tuple(2 * symp(ss[0], r) + symp(ss[1], r) for r in rs)
    dependent = mul(mul(rs[0], rs[1]), rs[2]) == (0, 0)
    recomputed_uanti = uanti_support(rs, central)
    recomputed_tag = 2 * (wt(ss[0]) + wt(ss[1]))
    recomputed_restore = sum(wt(t) for t in restores)
    recomputed_cost = recomputed_uanti + recomputed_tag + recomputed_restore
    checks = {
        "pairwise_anti": pairwise_anti(rs),
        "rank_consistent": gf2_rank(rs, n) == int(joint["rank"]) and int(joint["rank"]) in (2, 3),
        "labels_match_serialized": labels == tuple(int(x) for x in joint["labels"]),
        "distinct_labels": len(set(labels)) == 3,
        "dependent_label_consistency": (not dependent) or (labels[0] ^ labels[1] ^ labels[2] == 0),
        "restore_reconstructs_targets": all(mul(restores[k], rs[k]) == permuted_targets[k] for k in range(3)),
        "uanti_support_matches": recomputed_uanti == int(joint["uanti_support"]),
        "tag_support_matches": recomputed_tag == int(joint["tag_support_twice"]),
        "restore_support_matches": recomputed_restore == int(joint["restore_support"]),
        "cost_matches": recomputed_cost == int(joint["C_joint"]),
    }
    return targets, checks


def replay_row(row: dict[str, Any], n: int) -> dict[str, Any]:
    targets, witness_checks = reconstruct_and_check_witness(row, n)
    joint_cost = independent_joint_cost(targets, n)
    canonical_cost = independent_canonical_cost(targets, n)
    frame_only_cost = independent_frame_only_cost(targets, n)
    strongest = min(canonical_cost, frame_only_cost)
    independent_strict = joint_cost < strongest
    return {
        "term_indices": list(row["term_indices"]),
        "targets_reconstructed_from_primary_witness": [list(t) for t in targets],
        "witness_checks": witness_checks,
        "independent_joint_C_joint": joint_cost,
        "primary_joint_C_joint": int(row["joint"]["C_joint"]),
        "independent_canonical_C_joint": canonical_cost,
        "primary_canonical_C_joint": int(row["B_CANONICAL_STRONG"]["C_joint"]),
        "independent_frame_only_C_joint": frame_only_cost,
        "primary_frame_only_C_joint": int(row["B_FRAME_ONLY_STRONG"]["C_joint"]),
        "independent_strongest_comparator_C_joint": int(strongest),
        "independent_strict_vs_strongest": bool(independent_strict),
        "primary_strict_vs_strongest": bool(row["strict_vs_strongest"]),
        "joint_exact_match": joint_cost == int(row["joint"]["C_joint"]),
        "canonical_exact_match": canonical_cost == int(row["B_CANONICAL_STRONG"]["C_joint"]),
        "frame_only_exact_match": frame_only_cost == int(row["B_FRAME_ONLY_STRONG"]["C_joint"]),
        "strict_predicate_match": independent_strict is bool(row["strict_vs_strongest"]),
    }


def main() -> dict[str, Any]:
    primary_blob_ok = git_blob_sha((ROOT / PRIMARY_PATH).read_bytes()) == PRIMARY_BLOB
    novelty_blob_ok = git_blob_sha((ROOT / NOVELTY_PATH).read_bytes()) == NOVELTY_BLOB
    prospective_protocol_blob_ok = (
        git_blob_sha((ROOT / PROSPECTIVE_PROTOCOL_PATH).read_bytes()) == PROSPECTIVE_PROTOCOL_BLOB
    )
    if not (primary_blob_ok and novelty_blob_ok and prospective_protocol_blob_ok):
        raise RuntimeError("pre-outcome primary/protocol/novelty freeze drift")

    primary_result = primary.main()
    fresh = primary_result.get("fresh_subject")
    if not isinstance(fresh, dict):
        result = {
            "schema": "ORIONQ.MAXR6.ExactTARE3ProspectiveReplay.v1",
            "authority": "MAX_R6_NOT_EARNED__PROTECTED_SUBJECT_NOT_OPENED",
            "primary_authority": primary_result.get("authority"),
            "primary_blob_ok": primary_blob_ok,
            "novelty_blob_ok": novelty_blob_ok,
            "prospective_protocol_blob_ok": prospective_protocol_blob_ok,
            "primary_pre_access_ready": primary_result.get("pre_access_ready") is True,
            "protected_stretched_n2_accessed": primary_result.get("protected_stretched_n2_accessed") is True,
            "replay_rows": [],
            "final_gates": {"primary_prospective_supported": False},
            "r6_earned": False,
        }
        print("ORIONQ_MAX_R6_EXACT_TARE3_PROSPECTIVE_REPLAY=" + json.dumps(result, sort_keys=True))
        return result

    triples = fresh.get("triples", [])
    n = int(fresh["n_qubits"])
    replay_rows = [replay_row(row, n) for row in triples]
    selected_indices = [list(row["term_indices"]) for row in triples]
    top8 = [list(row) for row in fresh.get("p10_top8_term_indices", [])]

    panel_selection_consistent = selected_indices == top8[: len(selected_indices)]
    all_witnesses = bool(replay_rows) and all(
        all(row["witness_checks"].values()) for row in replay_rows
    )
    all_joint_exact = bool(replay_rows) and all(row["joint_exact_match"] for row in replay_rows)
    all_canonical_exact = bool(replay_rows) and all(row["canonical_exact_match"] for row in replay_rows)
    all_frame_only_exact = bool(replay_rows) and all(row["frame_only_exact_match"] for row in replay_rows)
    all_predicates_match = bool(replay_rows) and all(row["strict_predicate_match"] for row in replay_rows)
    replay_prospective_supported = (
        len(replay_rows) == 4
        and panel_selection_consistent
        and all_witnesses
        and all_joint_exact
        and all_canonical_exact
        and all_frame_only_exact
        and all_predicates_match
        and any(row["independent_strict_vs_strongest"] for row in replay_rows)
    )

    fresh_digest_match = sha256_json(fresh) == primary_result.get("fresh_subject_digest")
    frozen_novelty_bound = (
        primary_result.get("frozen_blobs", {}).get(NOVELTY_PATH) == NOVELTY_BLOB
    )
    final_gates = {
        "primary_blob_frozen": primary_blob_ok,
        "prospective_protocol_frozen": prospective_protocol_blob_ok,
        "hostile_novelty_freeze_bound": novelty_blob_ok and frozen_novelty_bound,
        "primary_pre_access_ready": primary_result.get("pre_access_ready") is True,
        "primary_prospective_supported": primary_result.get("prospective_supported") is True,
        "fresh_subject_receipt_digest_matches": fresh_digest_match,
        "fresh_source_blob_matches_frozen": fresh.get("source_blob") == primary.FRESH_CFG["blob"],
        "exactly_four_frozen_panel_rows": len(replay_rows) == 4,
        "panel_selection_consistent": panel_selection_consistent,
        "all_independent_witness_checks": all_witnesses,
        "all_independent_joint_optima_match": all_joint_exact,
        "all_independent_canonical_optima_match": all_canonical_exact,
        "all_independent_frame_only_optima_match": all_frame_only_exact,
        "all_primary_strict_predicates_match": all_predicates_match,
        "independent_prospective_support": replay_prospective_supported,
        "primary_and_replay_support_agree": (
            replay_prospective_supported is (primary_result.get("prospective_supported") is True)
        ),
    }
    r6_earned = all(final_gates.values())
    result = {
        "schema": "ORIONQ.MAXR6.ExactTARE3ProspectiveReplay.v1",
        "authority": (
            "MAX_R6_EARNED__EXACT_TARE3_FIXED_BLOCK_PROSPECTIVE_REPLAYED"
            if r6_earned
            else "MAX_R6_NOT_EARNED__PROSPECTIVE_OR_REPLAY_GATE_FAILED"
        ),
        "claim_scope": (
            "exact linear-in-system-qubit finite-state compiler for fixed three-term TARE auxiliary representations; "
            "joint auxiliary-frame/control-label/Tag/Restore/target/Uanti optimization only; "
            "not whole-Hamiltonian or global block-encoding superiority"
        ),
        "primary_authority": primary_result.get("authority"),
        "primary_fresh_subject_digest": primary_result.get("fresh_subject_digest"),
        "protected_stretched_n2_accessed": primary_result.get("protected_stretched_n2_accessed") is True,
        "replay_rows": replay_rows,
        "final_gates": final_gates,
        "r6_earned": r6_earned,
    }
    print("ORIONQ_MAX_R6_EXACT_TARE3_PROSPECTIVE_REPLAY=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
