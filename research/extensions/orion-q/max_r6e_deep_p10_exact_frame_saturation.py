#!/usr/bin/env python3
"""MAX-R6E exhaustive deep-P10 exact-joint vs exact-frame saturation scan.

Frozen by MAX_R6E_DEEP_P10_EXACT_FRAME_SATURATION_PROTOCOL.md.
Uses only already-open H4/equilibrium-N2 subjects and never reads the protected
stretched-N2 prospective discriminator. This is a responsibility diagnostic,
not R6 or novelty authority.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6_p10_candidate_blind_frame_optimizer as p10

EXPECTED_IMPROVING = {"H4": 452, "N2": 671}
EXPECTED_ELIGIBLE = {"H4": 4812, "N2": 11132}
BOUNDARY_BASE = (0, 1, 2, 3, 4, 7, 8, 15, 31)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _p10_key(row: dict[str, Any]):
    return (-float(row["p10_fraction"]), -int(row["p10_delta"]), tuple(row["term_indices"]))


def _strict_key(row: dict[str, Any]):
    return (
        -int(row["delta_exact_vs_frame"]),
        -float(row["p10_fraction"]),
        -int(row["p10_delta"]),
        tuple(row["term_indices"]),
    )


@lru_cache(maxsize=None)
def _frame_templates(n: int):
    """Exact Erratum-3 frame-only minimum set with Tag work precomputed per n."""
    rows = []
    for q in range(n):
        xyz = ((1 << q, 0), (1 << q, 1 << q), (0, 1 << q))
        for rs in itertools.permutations(xyz, 3):
            rs = tuple(rs)
            if p10.uanti_support(rs, 0) != 0:
                raise AssertionError("frame-only Uanti-minimum template is not zero")
            for labels in exact.DEPENDENT_LABEL_TRIPLES:
                hi_syn = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
                lo_syn = sum(((labels[k] & 1) << k) for k in range(3))
                wh, shi = p10.tag_min_weight(rs, hi_syn, n)
                wl, slo = p10.tag_min_weight(rs, lo_syn, n)
                rows.append(
                    (
                        rs,
                        tuple(int(x) for x in labels),
                        tuple(shi),
                        tuple(slo),
                        int(2 * (wh + wl)),
                    )
                )
    return tuple(rows)


def frame_only_fast(targets, n: int) -> dict[str, Any]:
    """Independent implementation of the exact frame-only comparator."""
    best = None
    best_record = None
    for rs, labels, shi, slo, tag_twice in _frame_templates(n):
        for permutation in itertools.permutations(range(3)):
            permuted = tuple(targets[permutation[k]] for k in range(3))
            restores = tuple(p10.mul(permuted[k], rs[k]) for k in range(3))
            cost = tag_twice + sum(p10.wt(t) for t in restores)
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
                    "definition": "B_FRAME_ONLY_STRONG_INDEPENDENT",
                }
    if best_record is None:
        raise AssertionError("independent frame-only comparator produced no witness")
    return best_record


def _frame_witness_valid(witness: dict[str, Any], targets) -> bool:
    rs = tuple(tuple(x) for x in witness["R"])
    ss = tuple(tuple(x) for x in witness["S"])
    ts = tuple(tuple(x) for x in witness["T"])
    permutation = tuple(int(x) for x in witness["target_permutation"])
    labels = tuple(int(x) for x in witness["labels"])
    if len(rs) != 3 or len(ss) != 2 or len(ts) != 3 or sorted(permutation) != [0, 1, 2]:
        return False
    if not p10.is_pairwise_anti(rs):
        return False
    if p10.uanti_support(rs, 0) != 0:
        return False
    if tuple(2 * p10.symp(ss[0], r) + p10.symp(ss[1], r) for r in rs) != labels:
        return False
    if len(set(labels)) != 3 or labels[0] ^ labels[1] ^ labels[2] != 0:
        return False
    permuted = tuple(targets[permutation[k]] for k in range(3))
    if not all(p10.mul(ts[k], rs[k]) == permuted[k] for k in range(3)):
        return False
    recomputed = 2 * (p10.wt(ss[0]) + p10.wt(ss[1])) + sum(p10.wt(t) for t in ts)
    return recomputed == int(witness["C_joint"])


def p10_population(cfg) -> tuple[list[Any], list[dict[str, Any]], int, float]:
    terms, max_imag = p10.load_terms(cfg)
    n = int(cfg["n_qubits"])
    eligible = 0
    improved: list[dict[str, Any]] = []
    for start in range(0, len(terms), p10.WINDOW):
        end = min(start + p10.WINDOW, len(terms))
        for comb in itertools.combinations(range(start, end), 3):
            targets = tuple(terms[i][0] for i in comb)
            if p10.is_direct_triple(targets):
                continue
            eligible += 1
            donor = p10.canonical_best(targets, n)
            generated = p10.rank2_best(targets, n)
            delta = int(donor["cost"] - generated["cost"])
            if delta <= 0:
                continue
            improved.append(
                {
                    "window_start": int(start),
                    "term_indices": list(comb),
                    "p10_delta": delta,
                    "p10_fraction": float(delta / donor["cost"] if donor["cost"] else 0.0),
                    "Lambda_TARE3": float(
                        math.sqrt(3.0)
                        * math.sqrt(sum(float(terms[i][1]) ** 2 for i in comb))
                    ),
                }
            )
    improved.sort(key=_p10_key)
    return terms, improved, eligible, max_imag


def exact_scan_subject(name: str, cfg) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    terms, population, eligible, max_imag = p10_population(cfg)
    if eligible != EXPECTED_ELIGIBLE[name]:
        raise AssertionError(
            {"p10_eligible_population_drift": name, "got": eligible, "expected": EXPECTED_ELIGIBLE[name]}
        )
    if len(population) != EXPECTED_IMPROVING[name]:
        raise AssertionError(
            {
                "p10_improving_population_drift": name,
                "got": len(population),
                "expected": EXPECTED_IMPROVING[name],
            }
        )

    n = int(cfg["n_qubits"])
    full_table: list[dict[str, Any]] = []
    strict_details: list[dict[str, Any]] = []
    for rank, base in enumerate(population):
        indices = tuple(int(i) for i in base["term_indices"])
        targets = tuple(terms[i][0] for i in indices)
        joint = exact.exact_joint(targets, n)
        frame = frame_only_fast(targets, n)
        if not all(joint["checks"].values()):
            raise AssertionError({"joint_witness_invalid": name, "rank": rank, "indices": indices})
        if not _frame_witness_valid(frame, targets):
            raise AssertionError({"frame_witness_invalid": name, "rank": rank, "indices": indices})
        delta = int(frame["C_joint"] - joint["C_joint"])
        row = {
            "p10_rank": int(rank),
            "window_start": int(base["window_start"]),
            "term_indices": list(indices),
            "p10_delta": int(base["p10_delta"]),
            "p10_fraction": float(base["p10_fraction"]),
            "Lambda_TARE3": float(base["Lambda_TARE3"]),
            "C_joint": int(joint["C_joint"]),
            "C_frame": int(frame["C_joint"]),
            "delta_exact_vs_frame": delta,
        }
        full_table.append(row)
        if delta > 0:
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

    strict_details.sort(key=_strict_key)
    strict_ranks = sorted(int(row["p10_rank"]) for row in strict_details)
    boundary_ranks = sorted(
        set(rank for rank in (*BOUNDARY_BASE, len(full_table) - 1) if 0 <= rank < len(full_table))
    )
    boundary_replay = []
    for rank in boundary_ranks:
        row = full_table[rank]
        indices = tuple(int(i) for i in row["term_indices"])
        targets = tuple(terms[i][0] for i in indices)
        joint = exact.exact_joint(targets, n)
        frame_reference = exact.frame_only_strong(targets, n)
        passed = (
            int(joint["C_joint"]) == int(row["C_joint"])
            and int(frame_reference["C_joint"]) == int(row["C_frame"])
        )
        boundary_replay.append(
            {
                "rank": rank,
                "joint_full": int(row["C_joint"]),
                "joint_replay": int(joint["C_joint"]),
                "frame_full": int(row["C_frame"]),
                "frame_reference_replay": int(frame_reference["C_joint"]),
                "pass": passed,
            }
        )
        if not passed:
            raise AssertionError({"boundary_replay_mismatch": name, **boundary_replay[-1]})

    table_sha = digest(full_table)
    summary = {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": n,
        "max_imag": float(max_imag),
        "eligible_non_direct_triples": eligible,
        "p10_improving_rows": len(full_table),
        "strict_exact_vs_frame_rows": len(strict_details),
        "strict_fraction_of_p10_population": (
            0.0 if not full_table else len(strict_details) / len(full_table)
        ),
        "first_strict_p10_rank": None if not strict_ranks else strict_ranks[0],
        "max_exact_vs_frame_delta": (
            0 if not strict_details else max(int(row["delta_exact_vs_frame"]) for row in strict_details)
        ),
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
    serialized_bundle = canonical_json(table_bundle)
    bundle_sha = hashlib.sha256(serialized_bundle.encode()).hexdigest()

    # Verify the serialized object through an independent JSON parse rather than
    # comparing a digest to the value just used to create it. When a table path
    # is supplied (the CI path), also re-read and hash the persisted artifact.
    roundtrip_bundle = json.loads(serialized_bundle)
    roundtrip_digest_ok = digest(roundtrip_bundle) == bundle_sha
    persisted_bundle = roundtrip_bundle
    persisted_digest_ok = True
    if args.table_json is not None:
        args.table_json.write_text(serialized_bundle + "\n")
        persisted_bundle = json.loads(args.table_json.read_text())
        persisted_digest_ok = digest(persisted_bundle) == bundle_sha

    subject_table_digests_match = all(
        digest(tables[name]) == summaries[name]["complete_table_sha256"]
        and digest(persisted_bundle["subjects"][name]) == summaries[name]["complete_table_sha256"]
        for name in ("H4", "N2")
    )

    gates = {
        "exact_joint_hostile_pass": hostile["all_exact"],
        "p10_population_counts_match_frozen_receipt": all(
            summaries[name]["p10_improving_rows"] == EXPECTED_IMPROVING[name]
            and summaries[name]["eligible_non_direct_triples"] == EXPECTED_ELIGIBLE[name]
            for name in ("H4", "N2")
        ),
        "boundary_replays_pass": all(
            summaries[name]["all_boundary_replays_pass"] for name in ("H4", "N2")
        ),
        "strict_witnesses_valid": all(
            summaries[name]["all_strict_witnesses_valid"] for name in ("H4", "N2")
        ),
        "serialized_table_bundle_roundtrip_digest_match": roundtrip_digest_ok,
        "persisted_table_bundle_digest_match": persisted_digest_ok,
        "subject_table_digests_match_summaries": subject_table_digests_match,
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"r6e_integrity_gate_failure": gates})

    result = {
        "schema": "ORIONQ.MAXR6E.DeepP10ExactFrameSaturation.v1",
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
