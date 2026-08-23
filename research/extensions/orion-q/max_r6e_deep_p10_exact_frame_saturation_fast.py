#!/usr/bin/env python3
"""Sparse exact executor for the frozen MAX-R6E deep-P10 diagnostic.

Scientific population, comparator and responsibility outcomes are identical to
max_r6e_deep_p10_exact_frame_saturation.py. This implementation accelerates only
the exact-joint *cost* calculation: the local 512-state parity transition has 26
finite dependent deltas and 109 finite independent deltas, so a sparse min-plus
XOR recurrence replaces the dense 512x512 matrices. Every strict row is then
reconstructed with the original proof-producing exact solver, and frozen boundary
ranks are replayed with the original exact-joint and frame-only implementations.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6e_deep_p10_exact_frame_saturation as base
import max_r6_p10_candidate_blind_frame_optimizer as p10

INF = exact.INF
PARITY_STATES = exact.PARITY_STATES
_STATES = np.arange(PARITY_STATES, dtype=np.int16)


def _accepting_arrays():
    dep = []
    indep = []
    for parity in range(PARITY_STATES):
        labels = tuple(
            2 * ((parity >> (3 + k)) & 1) + ((parity >> (6 + k)) & 1)
            for k in range(3)
        )
        if parity & 0b111 != 0b111 or len(set(labels)) != 3:
            continue
        indep.append(parity)
        if labels[0] ^ labels[1] ^ labels[2] == 0:
            dep.append(parity)
    return np.array(dep, dtype=np.int16), np.array(indep, dtype=np.int16)


_ACCEPT_DEP, _ACCEPT_INDEP = _accepting_arrays()


@lru_cache(maxsize=None)
def _sparse_local(p0: int, p1: int, p2: int, central: int):
    costs0, costs1, *_ = exact._local_table(p0, p1, p2, central)
    d0 = np.flatnonzero(costs0 < INF).astype(np.int16)
    d1 = np.flatnonzero(costs1 < INF).astype(np.int16)
    if len(d0) != 26 or len(d1) != 109:
        raise AssertionError(
            {
                "unexpected_sparse_local_support": [p0, p1, p2, central],
                "dependent": len(d0),
                "independent": len(d1),
            }
        )
    return d0, costs0[d0].astype(np.int64), d1, costs1[d1].astype(np.int64)


def _apply_sparse(dp: np.ndarray, deltas: np.ndarray, costs: np.ndarray) -> np.ndarray:
    out = np.full(PARITY_STATES, INF, dtype=np.int64)
    for delta, cost in zip(deltas, costs, strict=True):
        out = np.minimum(out, dp[np.bitwise_xor(_STATES, delta)] + cost)
    return out


def exact_joint_cost_sparse(targets, n: int) -> int:
    target_codes = tuple(p10.codes(target, n) for target in targets)
    best = INF
    for permutation in itertools.permutations(range(3)):
        for central in range(3):
            dp0 = np.full(PARITY_STATES, INF, dtype=np.int64)
            dp1 = np.full(PARITY_STATES, INF, dtype=np.int64)
            dp0[0] = 0
            for q in range(n):
                local_targets = tuple(target_codes[permutation[k]][q] for k in range(3))
                d0, c0, d1, c1 = _sparse_local(*local_targets, central)
                ndp0 = _apply_sparse(dp0, d0, c0)
                ndp1 = np.minimum.reduce(
                    (
                        _apply_sparse(dp1, d0, c0),
                        _apply_sparse(dp0, d1, c1),
                        _apply_sparse(dp1, d1, c1),
                    )
                )
                dp0, dp1 = ndp0, ndp1
            raw = min(
                int(dp0[_ACCEPT_DEP].min(initial=INF)),
                int(dp1[_ACCEPT_INDEP].min(initial=INF)),
            )
            best = min(best, raw - 10)
    if best >= INF:
        raise AssertionError("sparse exact-joint solver produced no accepting state")
    return int(best)


def sparse_hostile_equivalence() -> dict[str, Any]:
    panels = {
        "n2_a": (2, ((0b01, 0b00), (0b00, 0b10), (0b11, 0b01))),
        "n2_b": (2, ((0b10, 0b01), (0b01, 0b11), (0b11, 0b10))),
        "n3_a": (3, ((0b001, 0b110), (0b101, 0b010), (0b011, 0b100))),
        "n3_b": (3, ((0b110, 0b001), (0b011, 0b101), (0b100, 0b111))),
    }
    rows = {}
    for name, (n, targets) in panels.items():
        sparse = exact_joint_cost_sparse(targets, n)
        original = int(exact.exact_joint(targets, n)["C_joint"])
        brute = int(exact.brute_joint_cost(targets, n))
        passed = sparse == original == brute
        rows[name] = {
            "n": n,
            "sparse_cost": sparse,
            "original_cost": original,
            "brute_cost": brute,
            "pass": passed,
        }
        if not passed:
            raise AssertionError({"sparse_hostile_mismatch": name, **rows[name]})
    return {"panels": rows, "all_pass": all(row["pass"] for row in rows.values())}


def exact_scan_subject(name: str, cfg) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    terms, population, eligible, max_imag = base.p10_population(cfg)
    if eligible != base.EXPECTED_ELIGIBLE[name]:
        raise AssertionError(
            {"p10_eligible_population_drift": name, "got": eligible, "expected": base.EXPECTED_ELIGIBLE[name]}
        )
    if len(population) != base.EXPECTED_IMPROVING[name]:
        raise AssertionError(
            {
                "p10_improving_population_drift": name,
                "got": len(population),
                "expected": base.EXPECTED_IMPROVING[name],
            }
        )

    n = int(cfg["n_qubits"])
    full_table: list[dict[str, Any]] = []
    strict_details: list[dict[str, Any]] = []
    for rank, source in enumerate(population):
        indices = tuple(int(i) for i in source["term_indices"])
        targets = tuple(terms[i][0] for i in indices)
        joint_cost = exact_joint_cost_sparse(targets, n)
        frame = base.frame_only_fast(targets, n)
        if not base._frame_witness_valid(frame, targets):
            raise AssertionError({"frame_witness_invalid": name, "rank": rank, "indices": indices})
        delta = int(frame["C_joint"] - joint_cost)
        row = {
            "p10_rank": int(rank),
            "window_start": int(source["window_start"]),
            "term_indices": list(indices),
            "p10_delta": int(source["p10_delta"]),
            "p10_fraction": float(source["p10_fraction"]),
            "Lambda_TARE3": float(source["Lambda_TARE3"]),
            "C_joint": int(joint_cost),
            "C_frame": int(frame["C_joint"]),
            "delta_exact_vs_frame": delta,
        }
        full_table.append(row)
        if delta > 0:
            joint = exact.exact_joint(targets, n)
            if int(joint["C_joint"]) != joint_cost or not all(joint["checks"].values()):
                raise AssertionError(
                    {
                        "strict_sparse_original_disagreement": name,
                        "rank": rank,
                        "sparse": joint_cost,
                        "original": joint.get("C_joint"),
                    }
                )
            strict_details.append(
                {
                    **row,
                    "targets": [list(x) for x in targets],
                    "joint": joint,
                    "frame_only": frame,
                    "joint_witness_valid": True,
                    "frame_witness_valid": True,
                }
            )

    strict_details.sort(key=base._strict_key)
    strict_ranks = sorted(int(row["p10_rank"]) for row in strict_details)
    boundary_ranks = sorted(
        set(
            rank
            for rank in (*base.BOUNDARY_BASE, len(full_table) - 1)
            if 0 <= rank < len(full_table)
        )
    )
    boundary_replay = []
    for rank in boundary_ranks:
        row = full_table[rank]
        indices = tuple(int(i) for i in row["term_indices"])
        targets = tuple(terms[i][0] for i in indices)
        original_joint = exact.exact_joint(targets, n)
        original_frame = exact.frame_only_strong(targets, n)
        passed = (
            int(original_joint["C_joint"]) == int(row["C_joint"])
            and int(original_frame["C_joint"]) == int(row["C_frame"])
        )
        boundary_replay.append(
            {
                "rank": rank,
                "sparse_joint": int(row["C_joint"]),
                "original_joint": int(original_joint["C_joint"]),
                "fast_frame": int(row["C_frame"]),
                "original_frame": int(original_frame["C_joint"]),
                "pass": passed,
            }
        )
        if not passed:
            raise AssertionError({"boundary_replay_mismatch": name, **boundary_replay[-1]})

    table_sha = base.digest(full_table)
    summary = {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": n,
        "max_imag": float(max_imag),
        "eligible_non_direct_triples": eligible,
        "p10_improving_rows": len(full_table),
        "strict_exact_vs_frame_rows": len(strict_details),
        "strict_fraction_of_p10_population": 0.0 if not full_table else len(strict_details) / len(full_table),
        "first_strict_p10_rank": None if not strict_ranks else strict_ranks[0],
        "max_exact_vs_frame_delta": 0 if not strict_details else max(int(row["delta_exact_vs_frame"]) for row in strict_details),
        "strict_outside_old_top4": any(rank >= 4 for rank in strict_ranks),
        "strict_outside_old_top8": any(rank >= 8 for rank in strict_ranks),
        "best_strict_rows": strict_details[:16],
        "boundary_replay": boundary_replay,
        "complete_table_sha256": table_sha,
        "complete_table_rows": len(full_table),
        "all_boundary_replays_pass": all(row["pass"] for row in boundary_replay),
        "all_strict_witnesses_valid": all(
            row["joint_witness_valid"] and row["frame_witness_valid"] for row in strict_details
        ),
    }
    return summary, full_table


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table-json", type=Path, default=None)
    args = parser.parse_args()

    hostile = exact.hostile_exactness()
    sparse_hostile = sparse_hostile_equivalence()
    summaries: dict[str, Any] = {}
    tables: dict[str, Any] = {}
    for name, cfg in p10.base.SUBJECTS.items():
        summaries[name], tables[name] = exact_scan_subject(name, cfg)

    strict_h4 = summaries["H4"]["strict_exact_vs_frame_rows"] > 0
    strict_n2 = summaries["N2"]["strict_exact_vs_frame_rows"] > 0
    if strict_h4 and strict_n2:
        authority = "MAX_R6E_CURRENT_SEARCH_INCOMPLETE__NOT_R6"
        responsibility = "RESP:CURRENT_SEARCH_INCOMPLETE"
    elif strict_h4 or strict_n2:
        authority = "MAX_R6E_PARTIAL_SEARCH_REOPEN__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_SEARCH_AND_METHOD_SPLIT"
    else:
        authority = "MAX_R6E_EXACT_FRAME_SATURATION_SUPPORTED__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_DONOR_CLOSURE"

    table_bundle = {
        "schema": "ORIONQ.MAXR6E.DeepP10ExactFrameTable.v1",
        "subjects": tables,
    }
    serialized = base.canonical_json(table_bundle)
    bundle_sha = hashlib.sha256(serialized.encode()).hexdigest()
    parsed = json.loads(serialized)
    roundtrip_ok = base.digest(parsed) == bundle_sha
    persisted_ok = True
    persisted = parsed
    if args.table_json is not None:
        args.table_json.write_text(serialized + "\n")
        persisted = json.loads(args.table_json.read_text())
        persisted_ok = base.digest(persisted) == bundle_sha
    subject_digests_ok = all(
        base.digest(tables[name]) == summaries[name]["complete_table_sha256"]
        and base.digest(persisted["subjects"][name]) == summaries[name]["complete_table_sha256"]
        for name in ("H4", "N2")
    )

    gates = {
        "original_exact_joint_hostile_pass": hostile["all_exact"],
        "sparse_exact_matches_original_and_brute_hostile": sparse_hostile["all_pass"],
        "p10_population_counts_match_frozen_receipt": all(
            summaries[name]["p10_improving_rows"] == base.EXPECTED_IMPROVING[name]
            and summaries[name]["eligible_non_direct_triples"] == base.EXPECTED_ELIGIBLE[name]
            for name in ("H4", "N2")
        ),
        "boundary_replays_pass": all(summaries[name]["all_boundary_replays_pass"] for name in ("H4", "N2")),
        "strict_witnesses_valid": all(summaries[name]["all_strict_witnesses_valid"] for name in ("H4", "N2")),
        "serialized_table_bundle_roundtrip_digest_match": roundtrip_ok,
        "persisted_table_bundle_digest_match": persisted_ok,
        "subject_table_digests_match_summaries": subject_digests_ok,
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"r6e_fast_integrity_gate_failure": gates})

    result = {
        "schema": "ORIONQ.MAXR6E.DeepP10ExactFrameSaturation.v1",
        "implementation": "SPARSE_EXACT_COST_V1_WITH_ORIGINAL_STRICT_AND_BOUNDARY_REPLAY",
        "authority": authority,
        "scope": "OPEN_H4_EQ_N2_COMPLETE_P10_IMPROVING_POPULATION__NOT_R6",
        "responsibility": responsibility,
        "subjects": summaries,
        "complete_table_bundle_sha256": bundle_sha,
        "complete_table_total_rows": sum(len(rows) for rows in tables.values()),
        "gates": gates,
        "reserved_stretched_n2_accessed": False,
        "novelty_credit": False,
        "r6_authority": False,
    }
    print("ORIONQ_MAX_R6E_DEEP_P10=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
