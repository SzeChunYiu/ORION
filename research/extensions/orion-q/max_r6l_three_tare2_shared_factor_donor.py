#!/usr/bin/env python3
"""MAX-R6L donor-owned three-TARE2 shared-Tag / all-three Restore-factor composition.

Frozen by MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_PROTOCOL.md and amended by
MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_ERRATUM_1.md (conservative empty-envelope
comparator; no gate weakened). This lane grants the donor the strongest natural
six-term M2 composition: all 15 perfect matchings into three TARE-M2 blocks, the
complete weight-one M2 frame family, one shared one-bit Tag across all three
blocks, and exact all-three Restore common-factor extraction. Any saving is
donor-owned with zero novelty credit; R6L can never set r6_earned=true.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

import max_r6b_tare_transformation_reuse_donor as reuse
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6h_partial_tag_sharing_donor as r6h
import max_r6j_partial_restore_factor_donor as r6j
import max_r6_p10_candidate_blind_frame_optimizer as p10

TOL = 1e-12
INF = 10**9
SQRT2 = math.sqrt(2.0)
# Non-compensatory coordinate: each TARE-M2 block carries the frozen 2m-1 = 3
# arbitrary Uanti rotations; the two-M3 incumbent carries 2*(2*3-1) = 10.
ROTATIONS_R6L = 9
ROTATIONS_TWO_M3 = 10
M2_LABEL_CHOICES = ((0, 1), (1, 0))
RESULTS_PATH = Path(__file__).resolve().with_name(
    "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json"
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _local_letter(key: tuple[int, int], q: int) -> tuple[int, int]:
    return ((key[0] >> q) & 1, (key[1] >> q) & 1)


def _set_local(key: tuple[int, int], q: int, bits: tuple[int, int]) -> tuple[int, int]:
    x, z = key
    x &= ~(1 << q)
    z &= ~(1 << q)
    x |= int(bits[0]) << q
    z |= int(bits[1]) << q
    return int(x), int(z)


# ---- 15 canonical unordered perfect matchings ------------------------------

def perfect_matchings(items) -> tuple[tuple[tuple[int, int], ...], ...]:
    """All unordered perfect matchings of six items into three sorted pairs."""
    pool = tuple(sorted(int(i) for i in items))
    if len(pool) != 6 or len(set(pool)) != 6:
        raise AssertionError({"R6L_matching_universe_not_six_unique": pool})

    def rec(remaining: tuple[int, ...]):
        if not remaining:
            yield ()
            return
        first = remaining[0]
        for idx in range(1, len(remaining)):
            pair = (first, remaining[idx])
            rest = remaining[1:idx] + remaining[idx + 1:]
            for tail in rec(rest):
                yield (pair,) + tail

    seen = set()
    for rows in rec(pool):
        canonical = tuple(sorted(tuple(sorted(pair)) for pair in rows))
        seen.add(canonical)
    result = tuple(sorted(seen))
    if len(result) != 15:
        raise AssertionError({"R6L_not_fifteen_matchings": len(result)})
    for matching in result:
        flat = sorted(i for pair in matching for i in pair)
        if flat != list(pool):
            raise AssertionError({"R6L_matching_not_perfect": matching})
    return result


# ---- Frozen weight-one TARE-M2 representation grammar ----------------------

def pair_tag_min_weight(rs, syndrome: int, n: int) -> tuple[int, tuple[int, int]]:
    """Exact minimum-weight Tag S with <S,R_k> = bit k of syndrome, k in {0,1}."""
    rc = [p10.codes(r, n) for r in rs]
    dp = [0, INF, INF, INF]
    parents = []
    for q in range(n):
        local = [INF] * 4
        choice = [-1] * 4
        for s in range(4):
            d = p10.h.local_symp(s, rc[0][q]) | (p10.h.local_symp(s, rc[1][q]) << 1)
            c = p10.h.local_wt(s)
            if c < local[d] or (c == local[d] and s < choice[d]):
                local[d] = c
                choice[d] = s
        ndp = [INF] * 4
        prev = [0] * 4
        delta = [0] * 4
        for d in range(4):
            for pd in range(4):
                c = dp[pd] + local[pd ^ d]
                if c < ndp[d]:
                    ndp[d] = c
                    prev[d] = pd
                    delta[d] = pd ^ d
        parents.append((prev, delta, choice))
        dp = ndp
    if dp[syndrome] >= INF:
        raise AssertionError({"R6L_pair_tag_syndrome_unsolved": syndrome, "R": rs})
    state = syndrome
    seq = [0] * n
    for q in range(n - 1, -1, -1):
        prev, delta, choice = parents[q]
        seq[q] = int(choice[delta[state]])
        state = int(prev[state])
    s = p10.key_from_codes(seq)
    got = p10.symp(s, rs[0]) | (p10.symp(s, rs[1]) << 1)
    if got != syndrome or p10.wt(s) != int(dp[syndrome]):
        raise AssertionError({"R6L_pair_tag_reconstruction_failed": [rs, syndrome, s]})
    return int(dp[syndrome]), s


def brute_pair_tag(rs, syndrome: int, n: int) -> tuple[int, tuple[int, int]]:
    best = None
    for x in range(1 << n):
        for z in range(1 << n):
            s = (x, z)
            got = p10.symp(s, rs[0]) | (p10.symp(s, rs[1]) << 1)
            if got != syndrome:
                continue
            rec = (p10.wt(s), s)
            if best is None or rec < best:
                best = rec
    if best is None:
        raise AssertionError({"R6L_brute_pair_tag_infeasible": [rs, syndrome]})
    return int(best[0]), best[1]


def m2_representations(block: dict[str, Any], n: int) -> list[dict[str, Any]]:
    """Complete ordered weight-one TARE-M2 grammar for one two-term block."""
    targets = tuple(tuple(x) for x in block["targets"])
    if len(targets) != 2:
        raise AssertionError({"R6L_block_not_two_terms": block})
    reps: list[dict[str, Any]] = []
    for q in range(n):
        xyz = ((1 << q, 0), (1 << q, 1 << q), (0, 1 << q))
        for rs in itertools.permutations(xyz, 2):
            rs = tuple(rs)
            if p10.symp(rs[0], rs[1]) != 1 or any(p10.wt(r) != 1 for r in rs):
                raise AssertionError({"R6L_weight_one_frame_invalid": rs})
            for labels in M2_LABEL_CHOICES:
                syndrome = labels[0] | (labels[1] << 1)
                tag_weight, s = pair_tag_min_weight(rs, syndrome, n)
                got_labels = tuple(p10.symp(s, r) for r in rs)
                if got_labels != labels or len(set(labels)) != 2:
                    raise AssertionError({"R6L_tag_labels_not_reproduced": [rs, labels, s]})
                # Frozen Uanti M2 rule: 4x non-central + 2x central minus constant 6.
                uanti_by_central = tuple(
                    4 * p10.wt(rs[1 - central]) + 2 * p10.wt(rs[central]) - 6
                    for central in range(2)
                )
                if uanti_by_central != (0, 0):
                    raise AssertionError({"R6L_weight_one_uanti_nonzero": rs})
                for perm in ((0, 1), (1, 0)):
                    permuted = tuple(targets[perm[k]] for k in range(2))
                    ts = tuple(p10.mul(permuted[k], rs[k]) for k in range(2))
                    signed = tuple(
                        (reuse.correction_phase(permuted[k], rs[k], ts[k], n), ts[k])
                        for k in range(2)
                    )
                    reps.append(
                        {
                            "q": int(q),
                            "rs": rs,
                            "labels": tuple(int(x) for x in labels),
                            "s": tuple(s),
                            "tag_weight": int(tag_weight),
                            "perm": tuple(int(x) for x in perm),
                            "signed_t": signed,
                            "uanti_support": 0,
                            "rotations": 3,
                        }
                    )
    if len(reps) != 24 * n:
        raise AssertionError({"R6L_grammar_incomplete": [len(reps), 24 * n]})
    return reps


def group_by_tag(reps: list[dict[str, Any]]):
    groups: dict[Any, list[dict[str, Any]]] = {}
    for rep in reps:
        groups.setdefault((rep["s"], rep["labels"]), []).append(rep)
    for key in groups:
        groups[key].sort(key=lambda r: (r["q"], r["rs"], r["perm"]))
    return groups


# ---- Exact all-three Restore common-factor rule ----------------------------

def factor_restore_triple(signed_triple, n: int) -> dict[str, Any]:
    """Factor the support-minimizing common Hermitian Pauli across all three blocks."""
    phases = tuple(int(row[0]) for row in signed_triple)
    ts = tuple(tuple(row[1]) for row in signed_triple)
    g = (0, 0)
    matching_nonidentity = 0
    for q in range(n):
        letters = tuple(_local_letter(t, q) for t in ts)
        if letters[0] == letters[1] == letters[2] and letters[0] != (0, 0):
            g = _set_local(g, q, letters[0])
            matching_nonidentity += 1
    us = tuple(p10.mul(g, t) for t in ts)
    product_phases = []
    residual_phases = []
    binary_ok = True
    for j in range(3):
        got, exponent = reuse.mul_phase(g, us[j], n)
        binary_ok = binary_ok and got == ts[j]
        product_phases.append(int(exponent))
        residual_phases.append((phases[j] - int(exponent)) % 4)
    support = int(p10.wt(g) + sum(p10.wt(u) for u in us))
    original = int(sum(p10.wt(t) for t in ts))
    rec = {
        "G": list(g),
        "U": [list(u) for u in us],
        "original_phases": list(phases),
        "G_times_U_phases": product_phases,
        "residual_phases": residual_phases,
        "matching_nonidentity_local_letters": int(matching_nonidentity),
        "original_restore_support": original,
        "support": support,
        "restore_support_saved": int(original - support),
        "checks": {
            "binary_identity_all_three": binary_ok,
            "phase_identity_all_three": all(
                (residual_phases[j] + product_phases[j]) % 4 == phases[j] for j in range(3)
            ),
            "support_formula": support == original - 2 * matching_nonidentity,
            "saving_is_twice_all_three_matches": original - support == 2 * matching_nonidentity,
        },
    }
    if not all(rec["checks"].values()):
        raise AssertionError({"R6L_factor_witness_failed": rec})
    return rec


# ---- Best compatible representation triple per matching --------------------

def _serialize_rep(rep: dict[str, Any], block: dict[str, Any]) -> dict[str, Any]:
    return {
        "term_indices": [int(i) for i in block["term_indices"]],
        "targets": [list(t) for t in block["targets"]],
        "q": int(rep["q"]),
        "frame_R": [list(r) for r in rep["rs"]],
        "target_permutation": list(rep["perm"]),
        "signed_T": [
            {"phase": int(phase), "T": list(t)} for phase, t in rep["signed_t"]
        ],
        "uanti_support": 0,
        "rotations": 3,
    }


def best_shared_factor_triple(blocks, n: int, rep_cache=None) -> dict[str, Any]:
    idx = [set(int(i) for i in block["term_indices"]) for block in blocks]
    disjoint = (
        idx[0].isdisjoint(idx[1]) and idx[0].isdisjoint(idx[2]) and idx[1].isdisjoint(idx[2])
    )
    if not disjoint:
        raise AssertionError({"R6L_blocks_not_disjoint": [sorted(s) for s in idx]})
    grouped = []
    counts = []
    for block in blocks:
        key = tuple(int(i) for i in block["term_indices"])
        if rep_cache is not None and key in rep_cache:
            reps = rep_cache[key]
        else:
            reps = m2_representations(block, n)
            if rep_cache is not None:
                rep_cache[key] = reps
        counts.append(len(reps))
        grouped.append(group_by_tag(reps))
    common = sorted(set(grouped[0]) & set(grouped[1]) & set(grouped[2]))
    best = None
    evaluated = 0
    for key in common:
        s, labels = key
        tag_support = int(2 * p10.wt(s))
        for ra in grouped[0][key]:
            for rb in grouped[1][key]:
                for rc in grouped[2][key]:
                    evaluated += 1
                    branches = [
                        factor_restore_triple(
                            (ra["signed_t"][k], rb["signed_t"][k], rc["signed_t"][k]), n
                        )
                        for k in range(2)
                    ]
                    factor_support = int(sum(row["support"] for row in branches))
                    original_total = int(
                        sum(row["original_restore_support"] for row in branches)
                    )
                    uanti_total = int(
                        ra["uanti_support"] + rb["uanti_support"] + rc["uanti_support"]
                    )
                    total = int(tag_support + factor_support + uanti_total)
                    saved = int(original_total - factor_support)
                    checks = {
                        "same_tag_key_all_three": (ra["s"], ra["labels"])
                        == (rb["s"], rb["labels"])
                        == (rc["s"], rc["labels"])
                        == key,
                        "one_bit_labels_distinct": tuple(sorted(labels)) == (0, 1),
                        "blocks_pairwise_disjoint": disjoint,
                        "uanti_support_zero": uanti_total == 0,
                        "branch_factor_checks": all(
                            all(row["checks"].values()) for row in branches
                        ),
                        "cost_recomputed": total
                        == 2 * p10.wt(s)
                        + sum(row["support"] for row in branches)
                        + uanti_total,
                    }
                    if not all(checks.values()):
                        raise AssertionError({"R6L_triple_checks_failed": checks})
                    order = (
                        total,
                        -saved,
                        tag_support,
                        original_total,
                        key,
                        (ra["q"], ra["rs"], ra["perm"]),
                        (rb["q"], rb["rs"], rb["perm"]),
                        (rc["q"], rc["rs"], rc["perm"]),
                    )
                    if best is None or order < best[0]:
                        rec = {
                            "C_R6L": total,
                            "tag_support_twice_shared": tag_support,
                            "uanti_support_total": uanti_total,
                            "factorized_restore_support": factor_support,
                            "original_restore_support_total": original_total,
                            "restore_support_saved": saved,
                            "rotation_count": ROTATIONS_R6L,
                            "tag_key": {"S": list(s), "labels": list(labels)},
                            "blocks": [
                                _serialize_rep(rep, block)
                                for rep, block in zip((ra, rb, rc), blocks, strict=True)
                            ],
                            "branches": branches,
                            "checks": checks,
                        }
                        best = (order, rec)
    if best is None:
        raise AssertionError("R6L target-independent grammar produced no common Tag key")
    return {
        "representation_counts": [int(c) for c in counts],
        "common_tag_key_count": len(common),
        "evaluated_triples": int(evaluated),
        "best": best[1],
    }


def brute_shared_factor_triple(blocks, n: int) -> int:
    """Independent nested-loop replay of the same frozen grammar (hostile only)."""
    tag_cache: dict[Any, tuple[int, tuple[int, int]]] = {}

    def reps(block):
        targets = tuple(tuple(x) for x in block["targets"])
        out = []
        for q in range(n):
            xyz = ((1 << q, 0), (1 << q, 1 << q), (0, 1 << q))
            for rs in itertools.permutations(xyz, 2):
                for labels in M2_LABEL_CHOICES:
                    syndrome = labels[0] | (labels[1] << 1)
                    cache_key = (rs, syndrome)
                    if cache_key not in tag_cache:
                        tag_cache[cache_key] = brute_pair_tag(rs, syndrome, n)
                    _w, s = tag_cache[cache_key]
                    for perm in ((0, 1), (1, 0)):
                        ts = tuple(p10.mul(targets[perm[k]], rs[k]) for k in range(2))
                        out.append((s, labels, ts))
        return out

    reps_a = reps(blocks[0])
    reps_b = reps(blocks[1])
    reps_c = reps(blocks[2])
    best = None
    for sa, la, ta in reps_a:
        for sb, lb, tb in reps_b:
            if (sa, la) != (sb, lb):
                continue
            for sc, lc, tc in reps_c:
                if (sa, la) != (sc, lc):
                    continue
                cost = 2 * p10.wt(sa)
                for k in range(2):
                    for q in range(n):
                        letters = [
                            _local_letter(ta[k], q),
                            _local_letter(tb[k], q),
                            _local_letter(tc[k], q),
                        ]
                        nonid = [x for x in letters if x != (0, 0)]
                        if len(nonid) == 3 and letters[0] == letters[1] == letters[2]:
                            cost += 1
                        else:
                            cost += len(nonid)
                if best is None or cost < best:
                    best = cost
    if best is None:
        raise AssertionError("R6L brute triple search found no common Tag key")
    return int(best)


# ---- Independent witness recomputation (serialized data only) --------------

def recompute_witness(witness: dict[str, Any], terms, n: int, frozen_indices) -> dict[str, Any]:
    matching = tuple(tuple(int(i) for i in pair) for pair in witness["matching"])
    flat = sorted(i for pair in matching for i in pair)
    checks = {"matching_conserves_six_terms": flat == sorted(int(i) for i in frozen_indices)}
    lam = sum(
        SQRT2 * math.sqrt(float(terms[i][1]) ** 2 + float(terms[j][1]) ** 2)
        for i, j in matching
    )
    checks["lambda_recomputed"] = abs(lam - float(witness["Lambda_R6L"])) <= TOL
    s = tuple(int(x) for x in witness["tag_key"]["S"])
    labels = tuple(int(x) for x in witness["tag_key"]["labels"])
    checks["labels_one_bit_distinct"] = labels in M2_LABEL_CHOICES
    total = 2 * p10.wt(s)
    signed_by_block = []
    for block_rec, pair in zip(witness["blocks"], matching, strict=True):
        rs = tuple(tuple(int(x) for x in r) for r in block_rec["frame_R"])
        perm = tuple(int(x) for x in block_rec["target_permutation"])
        q = int(block_rec["q"])
        expected_xyz = {(1 << q, 0), (1 << q, 1 << q), (0, 1 << q)}
        checks.setdefault("frames_weight_one_same_qubit", True)
        if not (
            len(rs) == 2
            and rs[0] != rs[1]
            and set(rs) <= expected_xyz
            and all(p10.wt(r) == 1 for r in rs)
        ):
            checks["frames_weight_one_same_qubit"] = False
        checks.setdefault("frames_anticommute", True)
        if p10.symp(rs[0], rs[1]) != 1:
            checks["frames_anticommute"] = False
        checks.setdefault("labels_reproduced_by_S", True)
        if tuple(p10.symp(s, r) for r in rs) != labels:
            checks["labels_reproduced_by_S"] = False
        checks.setdefault("tag_weight_minimal", True)
        syndrome = labels[0] | (labels[1] << 1)
        if pair_tag_min_weight(rs, syndrome, n)[0] != p10.wt(s):
            checks["tag_weight_minimal"] = False
        checks.setdefault("targets_match_terms", True)
        targets = tuple(terms[i][0] for i in pair)
        if [list(t) for t in targets] != [list(t) for t in block_rec["targets"]]:
            checks["targets_match_terms"] = False
        checks.setdefault("restore_identity_and_phase", True)
        signed = []
        for k in range(2):
            permuted = targets[perm[k]]
            t = p10.mul(permuted, rs[k])
            phase = reuse.correction_phase(permuted, rs[k], t, n)
            row = block_rec["signed_T"][k]
            if list(t) != list(row["T"]) or int(phase) != int(row["phase"]):
                checks["restore_identity_and_phase"] = False
            signed.append((int(phase), t))
        signed_by_block.append(tuple(signed))
    for k in range(2):
        branch = witness["branches"][k]
        rec = factor_restore_triple(tuple(sb[k] for sb in signed_by_block), n)
        key = f"branch_{k}_factor_recomputed"
        checks[key] = (
            rec["G"] == list(branch["G"])
            and rec["U"] == [list(u) for u in branch["U"]]
            and rec["residual_phases"] == list(branch["residual_phases"])
            and rec["support"] == int(branch["support"])
        )
        total += rec["support"]
    checks["cost_recomputed"] = int(total) == int(witness["C_R6L"])
    checks["rotation_count_nine"] = int(witness["rotation_count"]) == ROTATIONS_R6L
    if not all(checks.values()):
        raise AssertionError({"R6L_witness_recompute_failed": checks})
    return checks


# ---- Strongest incumbent envelope (frame-only / R6B / R6H / R6J) -----------

def _incumbent_rows(terms, source_indices, n: int):
    ev = r6d._evaluate_fixed_batch(terms, source_indices, n)
    if len(ev.get("all_partitions", [])) != 10 or ev.get("all_witnesses_valid") is not True:
        raise AssertionError("R6L incumbent R6D replay failed")
    rows = []
    for partition in ev["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        base = next(
            row for row in ev["eligible_points"] if row["partition"] == [list(a), list(b)]
        )
        block_a, block_b = r6j._block(terms, a), r6j._block(terms, b)
        h_best = r6h.best_partial_tag(block_a, block_b, n)
        j_best = r6j.best_restore_factor(block_a, block_b, n)
        components = {
            "FRAME_ONLY": int(base["C_frame_only"]),
            "R6B_REUSE": None if base.get("C_reuse") is None else int(base["C_reuse"]),
            "R6H_COMMON_TAG": None
            if h_best["best"] is None
            else int(h_best["best"]["C_partial_tag"]),
            "R6J_RESTORE_FACTOR": None
            if j_best["best"] is None
            else int(j_best["best"]["C_restore_factor"]),
        }
        known = {k: v for k, v in components.items() if v is not None}
        r6d_consistent = int(base["C_incumbent"]) == min(
            v for k, v in known.items() if k in ("FRAME_ONLY", "R6B_REUSE")
        )
        if not r6d_consistent:
            raise AssertionError({"R6L_r6d_incumbent_inconsistent": base["partition"]})
        c_inc, source = min((v, k) for k, v in known.items())
        rows.append(
            {
                "partition": [list(a), list(b)],
                "Lambda_batch": float(r6j._lambda(terms, a) + r6j._lambda(terms, b)),
                "C_incumbent": int(c_inc),
                "incumbent_source": source,
                "components": components,
                "rotation_count": ROTATIONS_TWO_M3,
            }
        )
    if not rows:
        raise AssertionError("R6L incumbent stack produced no eligible partition")
    return ev, rows


def _pick_incumbent(rows):
    return min(
        rows,
        key=lambda row: (int(row["C_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )


def _erratum1_comparator(rows, lam: float):
    """Parent lower-envelope rule; conservative global cost floor when empty."""
    eligible = [row for row in rows if float(row["Lambda_batch"]) <= lam + TOL]
    if eligible:
        best = _pick_incumbent(eligible)
        return "MATCHED_LOWER_ENVELOPE", int(best["C_incumbent"]), best
    best = _pick_incumbent(rows)
    return "CONSERVATIVE_GLOBAL_COST_FLOOR", int(best["C_incumbent"]), best


def _pareto_points(points):
    keep = []
    for row in points:
        lam = float(row["Lambda_R6L"])
        cost = int(row["C_R6L"])
        dominated = False
        for other in points:
            if other is row:
                continue
            olam = float(other["Lambda_R6L"])
            ocost = int(other["C_R6L"])
            if olam <= lam + TOL and ocost <= cost and (olam < lam - TOL or ocost < cost):
                dominated = True
                break
        if not dominated:
            keep.append({"matching": row["matching"], "Lambda_R6L": lam, "C_R6L": cost})
    return sorted(keep, key=lambda item: (item["Lambda_R6L"], item["C_R6L"], item["matching"]))


# ---- Hostile validation ----------------------------------------------------

def hostile_validation() -> dict[str, Any]:
    inherited = {
        "r6b_signed_phase_hostile_pass": reuse.hostile_validation()["all_pass"],
        "r6d_partition_envelope_hostile_pass": r6d.hostile_validation()["all_pass"],
        "r6h_partial_tag_hostile_pass": r6h.hostile_validation()["all_pass"],
        "r6j_restore_factor_hostile_pass": r6j.hostile_validation()["all_pass"],
    }

    matchings = perfect_matchings(range(6))
    matchings_ok = len(matchings) == 15 and len(set(matchings)) == 15

    tag_cases = 0
    tag_ok = True
    for q in range(2):
        xyz = ((1 << q, 0), (1 << q, 1 << q), (0, 1 << q))
        for rs in itertools.permutations(xyz, 2):
            for syndrome in range(4):
                w_dp, s_dp = pair_tag_min_weight(rs, syndrome, 2)
                w_bf, _s_bf = brute_pair_tag(rs, syndrome, 2)
                got = p10.symp(s_dp, rs[0]) | (p10.symp(s_dp, rs[1]) << 1)
                tag_ok = tag_ok and w_dp == w_bf and got == syndrome
                tag_cases += 1

    x, y, z = (1, 0), (1, 1), (0, 1)
    q1z = (0, 2)
    # Gate 7/8: exact all-three factor rule on single-qubit letters.
    same = factor_restore_triple(((0, x), (0, x), (0, x)), 1)
    mixed = factor_restore_triple(((0, x), (0, x), (0, z)), 1)
    two_of_three = factor_restore_triple(((0, (0, 0)), (0, z), (0, z)), 1)

    # Gate 6: synthetic three-block common-Tag triple with different Restore strings.
    n = 2
    triple_all = [
        {"targets": [list(p10.mul(x, q1z)), list(p10.mul(y, q1z))], "term_indices": [0, 1]},
        {"targets": [list(p10.mul(y, q1z)), list(p10.mul(z, q1z))], "term_indices": [2, 3]},
        {"targets": [list(p10.mul(x, q1z)), list(p10.mul(z, q1z))], "term_indices": [4, 5]},
    ]
    result_all = best_shared_factor_triple(triple_all, n)
    best_all = result_all["best"]
    restores_all = [tuple(canonical_json(b["signed_T"]) for b in best_all["blocks"])]
    different_restore = len(set(restores_all[0])) > 1
    brute_all = brute_shared_factor_triple(triple_all, n)

    # Subset-only common letters (two of three) must yield no factor saving there.
    triple_subset = [
        {"targets": [list(x), list(y)], "term_indices": [0, 1]},
        {"targets": [list(p10.mul(y, q1z)), list(p10.mul(z, q1z))], "term_indices": [2, 3]},
        {"targets": [list(p10.mul(x, q1z)), list(p10.mul(z, q1z))], "term_indices": [4, 5]},
    ]
    result_subset = best_shared_factor_triple(triple_subset, n)
    best_subset = result_subset["best"]
    brute_subset = brute_shared_factor_triple(triple_subset, n)
    subset_q1_identity = all(
        _local_letter(tuple(branch["G"]), 1) == (0, 0) for branch in best_subset["branches"]
    )

    gates = {
        **inherited,
        "exactly_fifteen_matchings_synthetic": matchings_ok,
        "pair_tag_dp_equals_brute": tag_ok and tag_cases == 48,
        "identical_letter_triple_saves_exactly_two": same["support"] == 1
        and same["restore_support_saved"] == 2
        and same["matching_nonidentity_local_letters"] == 1,
        "mixed_letter_triple_no_false_saving": mixed["support"] == 3
        and mixed["restore_support_saved"] == 0,
        "two_of_three_letter_no_false_saving": two_of_three["support"] == 2
        and two_of_three["restore_support_saved"] == 0,
        "exact_phase_reconstruction": all(same["checks"].values())
        and all(mixed["checks"].values())
        and all(two_of_three["checks"].values()),
        "synthetic_common_tag_different_restore_accepted": best_all is not None
        and different_restore
        and all(best_all["checks"].values()),
        "synthetic_all_three_saving_realized": best_all["restore_support_saved"] == 4,
        "structured_equals_brute_all_common": int(best_all["C_R6L"]) == brute_all,
        "structured_equals_brute_subset_only": int(best_subset["C_R6L"]) == brute_subset,
        "subset_only_no_common_factor_letter": subset_q1_identity,
    }
    if not all(gates.values()):
        raise AssertionError({"R6L_hostile_failure": gates})
    return {
        "gates": gates,
        "all_pass": True,
        "pair_tag_cases": tag_cases,
        "same_letter": same,
        "mixed_letter": mixed,
        "two_of_three_letter": two_of_three,
        "synthetic_all_common_best": best_all,
        "synthetic_all_common_brute_cost": brute_all,
        "synthetic_subset_best": best_subset,
        "synthetic_subset_brute_cost": brute_subset,
    }


# ---- Subjects --------------------------------------------------------------

def run_subject(name: str, cfg) -> dict[str, Any]:
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    if len(source_indices) != 6:
        return {
            "subject": name,
            "source_blob_expected": cfg["blob"],
            "source_blob_observed": observed_blob,
            "source_blob_verified": observed_blob == cfg["blob"],
            "batch_complete": False,
            "r6b_window_champions_available": len(champions),
            "frozen_source_indices": list(source_indices),
            "matching_count": 0,
            "strict_count": 0,
            "strict_budget_matched_improvement_exists": False,
            "best_strict": None,
            "max_imag": float(max_imag),
        }

    targets6 = [tuple(terms[i][0]) for i in source_indices]
    pairwise_commute = all(
        p10.symp(targets6[a], targets6[b]) == 0
        for a in range(6)
        for b in range(a + 1, 6)
    )
    if not pairwise_commute:
        raise AssertionError({"R6L_frozen_terms_not_pairwise_commuting": name})

    matchings = perfect_matchings(source_indices)
    r6d_eval, incumbent_rows = _incumbent_rows(terms, source_indices, n)
    floor_row = _pick_incumbent(incumbent_rows)
    global_floor = int(floor_row["C_incumbent"])

    rep_cache: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    points = []
    conservation_ok = True
    for matching in matchings:
        blocks = []
        for pair in matching:
            blocks.append(
                {
                    "targets": [list(terms[i][0]) for i in pair],
                    "term_indices": [int(i) for i in pair],
                    "coefficients": [float(terms[i][1]) for i in pair],
                }
            )
        flat = sorted(i for pair in matching for i in pair)
        coeff_count = sum(len(b["coefficients"]) for b in blocks)
        conserved = flat == sorted(source_indices) and coeff_count == 6
        conservation_ok = conservation_ok and conserved
        if not conserved:
            raise AssertionError({"R6L_matching_conservation_failed": matching})

        candidate = best_shared_factor_triple(blocks, n, rep_cache)
        cost = int(candidate["best"]["C_R6L"])
        lam = float(
            sum(
                SQRT2 * math.sqrt(float(terms[i][1]) ** 2 + float(terms[j][1]) ** 2)
                for i, j in matching
            )
        )
        mode, c_env, env_row = _erratum1_comparator(incumbent_rows, lam)
        delta = int(c_env - cost)
        rotation_not_worse = ROTATIONS_R6L <= int(env_row["rotation_count"])
        strict = delta > 0 and rotation_not_worse
        witness = {
            "matching": [list(pair) for pair in matching],
            "Lambda_R6L": lam,
            **candidate["best"],
        }
        recompute = recompute_witness(witness, terms, n, source_indices)
        points.append(
            {
                "matching": [list(pair) for pair in matching],
                "Lambda_R6L": lam,
                "C_R6L": cost,
                "rotation_count": ROTATIONS_R6L,
                "candidate_search": {
                    "representation_counts": candidate["representation_counts"],
                    "common_tag_key_count": candidate["common_tag_key_count"],
                    "evaluated_triples": candidate["evaluated_triples"],
                },
                "witness": witness,
                "witness_recompute": recompute,
                "comparator_mode": mode,
                "C_incumbent_comparator": int(c_env),
                "incumbent_witness": env_row,
                "incumbent_rotation_count": int(env_row["rotation_count"]),
                "rotation_not_worse_than_incumbent": rotation_not_worse,
                "delta_vs_incumbent": delta,
                "strict_budget_matched_improvement": strict,
            }
        )

    strict_rows = sorted(
        (row for row in points if row["strict_budget_matched_improvement"]),
        key=lambda row: (-int(row["delta_vs_incumbent"]), float(row["Lambda_R6L"]), row["matching"]),
    )
    best_point = min(
        points, key=lambda row: (int(row["C_R6L"]), float(row["Lambda_R6L"]), row["matching"])
    )
    best_r6l_cost = int(best_point["C_R6L"])
    grammar_ok = all(
        len(reps) == 24 * n for reps in rep_cache.values()
    ) and len(rep_cache) == 15

    return {
        "subject": name,
        "source_blob_expected": cfg["blob"],
        "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"],
        "batch_complete": True,
        "n_qubits": n,
        "max_imag": float(max_imag),
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": list(source_indices),
        "six_terms_pairwise_commute": pairwise_commute,
        "direct_pair_substitution_available": not pairwise_commute,
        "matching_count": len(matchings),
        "grammar_representation_count_per_block": 24 * n,
        "grammar_complete": grammar_ok,
        "conservation_verified": conservation_ok,
        "incumbent": {
            "partition_count": len(r6d_eval["all_partitions"]),
            "eligible_partition_count": len(incumbent_rows),
            "r6d_all_witnesses_valid": bool(r6d_eval["all_witnesses_valid"]),
            "rows": incumbent_rows,
        },
        "incumbent_replay_pass": bool(r6d_eval["all_witnesses_valid"])
        and len(r6d_eval["all_partitions"]) == 10,
        "erratum1_conservative_global_donor_cost_floor": global_floor,
        "erratum1_global_floor_witness": floor_row,
        "best_r6l_cost": best_r6l_cost,
        "donor_floor_after_r6l_absorption": min(global_floor, best_r6l_cost),
        "points": points,
        "pareto_points": _pareto_points(points),
        "best_point": best_point,
        "comparator_modes_used": sorted({row["comparator_mode"] for row in points}),
        "strict_count": len(strict_rows),
        "strict_budget_matched_improvement_exists": bool(strict_rows),
        "best_strict": None if not strict_rows else strict_rows[0],
        "rotation_gate_pass": all(
            row["rotation_count"] == ROTATIONS_R6L and row["rotation_not_worse_than_incumbent"]
            for row in points
        ),
        "witness_recompute_pass": all(
            all(row["witness_recompute"].values()) for row in points
        ),
    }


# ---- Main ------------------------------------------------------------------

def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-json", type=Path, default=RESULTS_PATH)
    args = parser.parse_args()
    hostile = hostile_validation()
    summaries = {name: run_subject(name, cfg) for name, cfg in p10.base.SUBJECTS.items()}

    h4 = summaries["H4"]["strict_budget_matched_improvement_exists"]
    n2 = summaries["N2"]["strict_budget_matched_improvement_exists"]
    if h4 and n2:
        authority = "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_POSITIVE__ABSORB__NOT_R6"
        responsibility = "RESP:ABSORB_THREE_TARE2_SHARED_FACTOR_DONOR"
        supported = True
    elif h4 or n2:
        authority = "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_PARTIAL__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_DONOR_SPLIT"
        supported = False
    else:
        authority = "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_THREE_TARE2_CLOSURE"
        supported = False

    complete = [row for row in summaries.values() if row["batch_complete"]]
    gates = {
        "hostile_pass": hostile["all_pass"],
        "exactly_fifteen_perfect_matchings": bool(complete)
        and all(row["matching_count"] == 15 for row in complete),
        "six_terms_pairwise_commute_no_direct_pair_route": bool(complete)
        and all(
            row["six_terms_pairwise_commute"] and not row["direct_pair_substitution_available"]
            for row in complete
        ),
        "complete_weight_one_m2_frame_grammar": bool(complete)
        and all(row["grammar_complete"] for row in complete),
        "tag_labels_distinct_and_reproduced": bool(complete)
        and all(
            all(row2["witness_recompute"]["labels_one_bit_distinct"]
                and row2["witness_recompute"]["labels_reproduced_by_S"]
                for row2 in row["points"])
            for row in complete
        ),
        "exact_restore_identity_and_phase": bool(complete)
        and all(
            all(row2["witness_recompute"]["restore_identity_and_phase"]
                and row2["witness_recompute"]["branch_0_factor_recomputed"]
                and row2["witness_recompute"]["branch_1_factor_recomputed"]
                for row2 in row["points"])
            for row in complete
        ),
        "synthetic_common_tag_different_restore_accepted": hostile["gates"][
            "synthetic_common_tag_different_restore_accepted"
        ],
        "identical_letter_triple_saves_exactly_two": hostile["gates"][
            "identical_letter_triple_saves_exactly_two"
        ],
        "mixed_letter_triple_no_false_saving": hostile["gates"][
            "mixed_letter_triple_no_false_saving"
        ],
        "blocks_disjoint_and_six_terms_conserved": bool(complete)
        and all(row["conservation_verified"] for row in complete),
        "witness_cost_and_lambda_recompute": bool(complete)
        and all(row["witness_recompute_pass"] for row in complete),
        "incumbent_stack_replay_pass": bool(complete)
        and all(row["incumbent_replay_pass"] for row in complete),
        "uanti_rotation_count_nine_and_not_worse": bool(complete)
        and all(row["rotation_gate_pass"] for row in complete),
        "source_blobs_observed_match": all(
            row["source_blob_verified"] for row in summaries.values()
        ),
        "frozen_sixterm_batches_complete": all(
            row["batch_complete"] for row in summaries.values()
        ),
        "erratum1_comparator_defined_for_all_points": bool(complete)
        and all(
            all(
                row2["comparator_mode"]
                in ("MATCHED_LOWER_ENVELOPE", "CONSERVATIVE_GLOBAL_COST_FLOOR")
                for row2 in row["points"]
            )
            for row in complete
        ),
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"R6L_integrity_gate_failure": gates})

    result = {
        "schema": "ORIONQ.MAXR6L.ThreeTare2SharedFactorDonor.v1",
        "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_THREE_TARE2_SHARED_TAG_RESTORE_FACTOR__NOT_R6",
        "responsibility": responsibility,
        "development_supported": supported,
        "erratum_1_applied": True,
        "comparator_rule": "MATCHED_LOWER_ENVELOPE_ELSE_CONSERVATIVE_GLOBAL_COST_FLOOR",
        "rotation_counts": {
            "r6l_three_tare2": ROTATIONS_R6L,
            "incumbent_two_m3": ROTATIONS_TWO_M3,
        },
        "erratum1_conservative_global_donor_cost_floor": {
            name: (
                None
                if not row["batch_complete"]
                else int(row["erratum1_conservative_global_donor_cost_floor"])
            )
            for name, row in summaries.items()
        },
        "donor_floor_after_r6l_absorption": {
            name: (
                None if not row["batch_complete"] else int(row["donor_floor_after_r6l_absorption"])
            )
            for name, row in summaries.items()
        },
        "subjects": summaries,
        "hostile": hostile,
        "gates": gates,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
        "fresh_r6_subject_coefficients_accessed": False,
    }
    print("ORIONQ_MAX_R6L_THREE_TARE2_SHARED_FACTOR=" + canonical_json(result))
    if args.results_json is not None:
        args.results_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        if json.loads(args.results_json.read_text()) != json.loads(canonical_json(result)):
            raise AssertionError("R6L persisted results mismatch")
    return result


if __name__ == "__main__":
    main()
