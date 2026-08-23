#!/usr/bin/env python3
"""MAX-R6O enlarged-Tag donor closure test.

Frozen by MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md (frozen before outcome).

R6N refuted the weight-one donor-family closure of the frozen R6M grammar at
its declared Tag-repair gap (synthetic n2_b: unrestricted DP 8 < weight-one
donor 9, DP witness anchored at different qubits with a weight-2 shared Tag).
R6O tests the repair hypothesis: the enlarged donor family

    D+ = { three weight-one TARE-M2 frames with arbitrary per-block anchor
           qubits + one shared Tag of unrestricted support, minimized subject
           to the common label constraints + donor-owned all-three Restore
           factoring }

restores exact family closure: C_DP == C_D+ on every instance.

The unrestricted optimum comes from the frozen R6M module unmodified; the D+
enumerator is written independently of the DP code paths (frozen local
algebra primitives and its own F3 table only). Honest outcome either way: any
instance with C_DP < C_D+ is a second new regime and is reported verbatim.
Not R6; no novelty credit; the protected stretched-N2 discriminator is never
read.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6b_tare_transformation_reuse_donor as reuse  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
INF = r6m.INF
BIG = np.int32(10 ** 9)
MATCHING = r6m._SYNTHETIC_MATCHING  # ((0, 1), (2, 3), (4, 5))
ORDERED_PAIRS = tuple(itertools.permutations((1, 2, 3), 2))  # 6 ordered pairs
LABEL_ORIENTATIONS = ((0, 1), (1, 0))
CENTRALS8 = tuple(itertools.product((0, 1), repeat=3))
VERBATIM_CAP = 20
RANDOM_SEED = 20260821

# ---- independent local algebra (bound to the frozen table below) ------------
LW = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
F3 = np.zeros((4, 4, 4), dtype=np.int32)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            if _a == _b == _c != 0:
                F3[_a, _b, _c] = 1
            else:
                F3[_a, _b, _c] = int(LW[_a] + LW[_b] + LW[_c])


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _letter_key(letter: int, q: int):
    bx, bz = h.CODE_BITS[letter]
    return (bx << q, bz << q)


def _local_code(key, q: int) -> int:
    return h.BITS_CODE[((key[0] >> q) & 1, (key[1] >> q) & 1)]


# ---- frozen minimal-Tag closed form and its verification ---------------------

def _forced_letter(pair, labels) -> int:
    """Unique local Tag letter forced at a block's anchor qubit."""
    return pair[0] if labels == (0, 1) else pair[1]


def verify_tag_minimality() -> dict[str, Any]:
    # (i) local forced-letter uniqueness: 6 ordered pairs x 2 labels, each
    # over all 4 candidate letters.
    local_cases = 0
    local_ok = True
    for a, b in ORDERED_PAIRS:
        for labels in LABEL_ORIENTATIONS:
            sols = [
                s for s in range(4)
                if (h.local_symp(s, a), h.local_symp(s, b)) == labels
            ]
            local_cases += 1
            if sols != [_forced_letter((a, b), labels)]:
                local_ok = False
    # (ii) full global brute at n=2: all 8 anchor triples x 216 letter-pair
    # triples x 2 labels against all 256 two-qubit Paulis.
    n = 2
    keys = [(x, z) for x in range(4) for z in range(4)]
    key_wt = [p10.wt(k) for k in keys]
    # feasibility bit-vector per single block choice (anchor, pair, labels)
    feas_vec: dict[tuple, list[bool]] = {}
    for q in range(n):
        for pair in ORDERED_PAIRS:
            r0, r1 = _letter_key(pair[0], q), _letter_key(pair[1], q)
            for labels in LABEL_ORIENTATIONS:
                feas_vec[(q, pair, labels)] = [
                    (p10.symp(k, r0), p10.symp(k, r1)) == labels for k in keys
                ]
    combos = 0
    brute_ok = True
    for anchors in itertools.product(range(n), repeat=3):
        for pairs3 in itertools.product(ORDERED_PAIRS, repeat=3):
            for labels in LABEL_ORIENTATIONS:
                combos += 1
                ok_keys = [
                    all(feas_vec[(anchors[j], pairs3[j], labels)][i] for j in range(3))
                    for i in range(len(keys))
                ]
                feas_wts = [key_wt[i] for i in range(len(keys)) if ok_keys[i]]
                # closed form
                forced: dict[int, int] = {}
                cf_feasible = True
                for j in range(3):
                    u = _forced_letter(pairs3[j], labels)
                    if anchors[j] in forced and forced[anchors[j]] != u:
                        cf_feasible = False
                        break
                    forced[anchors[j]] = u
                if cf_feasible:
                    if not feas_wts or min(feas_wts) != len(forced):
                        brute_ok = False
                else:
                    if feas_wts:
                        brute_ok = False
    return {
        "local_uniqueness_cases": local_cases,
        "local_uniqueness_ok": local_ok,
        "n2_global_brute_combos": combos,
        "n2_global_brute_ok": brute_ok,
        "verified": local_ok and brute_ok and combos == 3456,
    }


# ---- independent D+ enumerator ----------------------------------------------

_block_cache: dict[tuple, tuple] = {}


def _block_choices(target_pair, n: int, labels):
    """Per-block choice arrays over (anchor q, ordered pair, permutation)."""
    key = (target_pair, n, labels)
    hit = _block_cache.get(key)
    if hit is not None:
        return hit
    m = n * 6 * 2
    anchors = np.empty(m, dtype=np.int16)
    forced = np.empty(m, dtype=np.int16)
    letters = np.empty((m, 2, n), dtype=np.int64)
    c = 0
    for q in range(n):
        for pair in ORDERED_PAIRS:
            for perm in (0, 1):
                ordered = target_pair if perm == 0 else (target_pair[1], target_pair[0])
                anchors[c] = q
                forced[c] = _forced_letter(pair, labels)
                for k in range(2):
                    t = p10.mul(ordered[k], _letter_key(pair[k], q))
                    for qq in range(n):
                        letters[c, k, qq] = _local_code(t, qq)
                c += 1
    out = (anchors, forced, letters)
    _block_cache[key] = out
    return out


def _decode_choice(c: int):
    q, rem = divmod(int(c), 12)
    pair_idx, perm = divmod(rem, 2)
    return q, ORDERED_PAIRS[pair_idx], perm


def dplus_pairs(target_pairs, n: int) -> dict[str, Any]:
    """Exact D+ optimum for one instance (three ordered target pairs)."""
    target_pairs = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    best = None
    for labels in LABEL_ORIENTATIONS:
        per_block = [_block_choices(tp, n, labels) for tp in target_pairs]
        (aa, fa, la), (ab, fb, lb), (ac, fc, lc) = per_block
        m = aa.shape[0]
        fc_total = np.zeros((m, m, m), dtype=np.int32)
        for k in range(2):
            for q in range(n):
                np.add(
                    fc_total,
                    F3[
                        la[:, k, q][:, None, None],
                        lb[:, k, q][None, :, None],
                        lc[:, k, q][None, None, :],
                    ],
                    out=fc_total,
                )
        s_ab = (aa[:, None] == ab[None, :])
        s_ac = (aa[:, None] == ac[None, :])
        s_bc = (ab[:, None] == ac[None, :])
        ok_ab = (~s_ab) | (fa[:, None] == fb[None, :])
        ok_ac = (~s_ac) | (fa[:, None] == fc[None, :])
        ok_bc = (~s_bc) | (fb[:, None] == fc[None, :])
        feas = ok_ab[:, :, None] & ok_ac[:, None, :] & ok_bc[None, :, :]
        all3 = s_ab[:, :, None] & s_ac[:, None, :]
        ndistinct = (
            3
            - s_ab[:, :, None].astype(np.int32)
            - s_ac[:, None, :].astype(np.int32)
            - s_bc[None, :, :].astype(np.int32)
            + all3.astype(np.int32)
        )
        total = fc_total + 2 * ndistinct
        total = np.where(feas, total, BIG)
        flat = int(np.argmin(total))
        value = int(total.reshape(-1)[flat])
        if value >= int(BIG):
            raise AssertionError("r6o D+ family produced no feasible point")
        if best is None or value < best[0]:
            ia, rem = divmod(flat, m * m)
            ib, ic = divmod(rem, m)
            best = (value, labels, (ia, ib, ic))
    value, labels, choice = best
    blocks = []
    for j, c in enumerate(choice):
        q, pair, perm = _decode_choice(c)
        blocks.append({"block": "ABC"[j], "anchor_qubit": q,
                       "frame_letters": [LETTERS[pair[0]], LETTERS[pair[1]]],
                       "target_permutation": perm})
    forced_map: dict[int, int] = {}
    for j, c in enumerate(choice):
        q, pair, _ = _decode_choice(c)
        forced_map[q] = _forced_letter(pair, labels)
    s_key = (0, 0)
    for q, u in sorted(forced_map.items()):
        s_key = p10.mul(s_key, _letter_key(u, q))
    return {
        "C_Dplus": int(value),
        "labels": list(labels),
        "blocks": blocks,
        "S": list(s_key),
        "tag_weight": int(p10.wt(s_key)),
        "distinct_anchors": len(forced_map),
    }


def verify_dplus_witness(target_pairs, n: int, wit: dict[str, Any]) -> bool:
    """Independent re-verification through the frozen donor factor machinery."""
    labels = tuple(wit["labels"])
    s_key = tuple(wit["S"])
    frames = []
    ordered_targets = []
    for j, blk in enumerate(wit["blocks"]):
        q = int(blk["anchor_qubit"])
        a, b = (LETTERS.index(x) for x in blk["frame_letters"])
        r0, r1 = _letter_key(a, q), _letter_key(b, q)
        frames.append((r0, r1))
        tp = tuple(tuple(t) for t in target_pairs[j])
        ordered_targets.append(tp if blk["target_permutation"] == 0 else (tp[1], tp[0]))
    checks = {
        "weight_one_anticommuting_frames": all(
            p10.wt(r0) == 1 and p10.wt(r1) == 1 and p10.symp(r0, r1) == 1
            for r0, r1 in frames
        ),
        "labels_common_and_distinct": labels[0] != labels[1]
        and all(
            (p10.symp(s_key, r0), p10.symp(s_key, r1)) == labels for r0, r1 in frames
        ),
        "tag_weight_equals_distinct_anchors": p10.wt(s_key) == int(wit["distinct_anchors"]),
    }
    signed = []
    for j in range(3):
        row = []
        for k in range(2):
            t = p10.mul(ordered_targets[j][k], frames[j][k])
            phase = reuse.correction_phase(ordered_targets[j][k], frames[j][k], t, n)
            row.append((int(phase), t))
        signed.append(row)
    branch_factors = [
        r6m.factor_restore_triple(signed[0][k], signed[1][k], signed[2][k], n)
        for k in range(2)
    ]
    checks["factor_checks"] = all(all(bf["checks"].values()) for bf in branch_factors)
    checks["cost_recomputed"] = (
        int(2 * p10.wt(s_key) + sum(bf["support"] for bf in branch_factors))
        == int(wit["C_Dplus"])
    )
    return all(checks.values())


# ---- frozen DP readers (bound to the frozen module by sampling) --------------

def _permute6(t6, perm_b: int, perm_c: int):
    a0, a1, b0, b1, c0, c1 = t6
    if perm_b:
        b0, b1 = b1, b0
    if perm_c:
        c0, c1 = c1, c0
    return (a0, a1, b0, b1, c0, c1)


def dp_cost_n1_reader(p6) -> int:
    """C_DP at n=1 straight off the frozen _local_table accepting entries."""
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            q6 = _permute6(p6, perm_b, perm_c)
            for centrals in CENTRALS8:
                cost, _ = r6m._local_table(q6, centrals)
                for state in r6m.ACCEPTING_STATES:
                    v = int(cost[state])
                    if v < INF and (best is None or v < best):
                        best = v
    if best is None:
        raise AssertionError("r6o n=1 DP reader found no accepting option")
    return best - 18


def dp_cost_n2_reader(target_pairs) -> int:
    """C_DP at n=2 via the frozen two-qubit DP identity on _local_table."""
    flat = tuple(t for pair in target_pairs for t in pair)
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            t6 = _permute6(flat, perm_b, perm_c)
            p60 = tuple(_local_code(t, 0) for t in t6)
            p61 = tuple(_local_code(t, 1) for t in t6)
            for centrals in CENTRALS8:
                c0, _ = r6m._local_table(p60, centrals)
                c1, _ = r6m._local_table(p61, centrals)
                for state in r6m.ACCEPTING_STATES:
                    v = int((c0 + c1[r6m.XOR512[state]]).min())
                    if v < INF and (best is None or v < best):
                        best = v
    if best is None:
        raise AssertionError("r6o n=2 DP reader found no accepting option")
    return best - 18


def dp_cost_frozen_configs(terms, n: int) -> int:
    """C_DP via the frozen _dp_config_cost, minimized over all 32 configs."""
    values = []
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            for centrals in CENTRALS8:
                v = r6m._dp_config_cost(terms, MATCHING, perm_b, perm_c, centrals, n)
                if v is not None:
                    values.append(int(v))
    if not values:
        raise AssertionError("r6o frozen config sweep found no accepting state")
    return min(values)


# ---- domain (a): R6N synthetic R6M-grammar panels ---------------------------

def domain_r6n_panels() -> dict[str, Any]:
    rows = []
    instances = [
        (name, 1, tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in pairs))
        for name, pairs in sorted(r6m._HOSTILE_N1_PANELS.items())
    ]
    instances += [
        (name, 2, tuple((tuple(a), tuple(b)) for a, b in pairs))
        for name, pairs in sorted(r6m._HOSTILE_N2_PANELS.items())
    ]
    for name, n, target_pairs in instances:
        terms = r6m._synthetic_terms(target_pairs)
        dp_wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
        c_dp = int(dp_wit["C_R6M"])
        dplus = dplus_pairs(target_pairs, n)
        c_dplus = int(dplus["C_Dplus"])
        c_r6l = int(r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"])
        if not (c_dp <= c_dplus <= c_r6l):
            raise AssertionError({"r6o_sandwich_violated": [name, c_dp, c_dplus, c_r6l]})
        if not verify_dplus_witness(target_pairs, n, dplus):
            raise AssertionError({"r6o_dplus_witness_failed": name})
        rows.append(
            {
                "panel": name,
                "n": n,
                "C_unrestricted_dp": c_dp,
                "C_Dplus": c_dplus,
                "C_R6L_weight_one_donor": c_r6l,
                "equal": c_dp == c_dplus,
                "was_r6n_refuting_instance": name == "n2_b",
                "dplus_witness": dplus,
                "dp_witness_checks_pass": all(dp_wit["checks"].values()),
            }
        )
    return {
        "instances": len(rows),
        "equal_count": sum(r["equal"] for r in rows),
        "rows": rows,
        "all_equal": all(r["equal"] for r in rows),
    }


# ---- domain (b1): exhaustive n=1 --------------------------------------------

def domain_exhaustive_n1() -> dict[str, Any]:
    violations = []
    equal = 0
    binding_rows = 0
    binding_ok = True
    exact_binding_ok = True
    cost_min, cost_max = None, None
    for idx in range(4096):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        p6 = tuple((idx >> (2 * (5 - t))) & 3 for t in range(6))
        target_pairs = tuple(
            (_letter_key(p6[2 * j], 0), _letter_key(p6[2 * j + 1], 0)) for j in range(3)
        )
        c_dp = dp_cost_n1_reader(p6)
        dplus = dplus_pairs(target_pairs, 1)
        c_dplus = int(dplus["C_Dplus"])
        if c_dp > c_dplus:
            raise AssertionError({"r6o_n1_soundness_violated": [idx, c_dp, c_dplus]})
        if idx % 32 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            frozen = dp_cost_frozen_configs(terms, 1)
            binding_rows += 1
            if frozen != c_dp:
                binding_ok = False
        if idx % 512 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            wit = r6m.exact_r6m_matching(terms, MATCHING, 1, list(range(6)))
            if int(wit["C_R6M"]) != c_dp:
                exact_binding_ok = False
        if idx % 64 == 0 and not verify_dplus_witness(target_pairs, 1, dplus):
            raise AssertionError({"r6o_n1_dplus_witness_failed": idx})
        cost_min = c_dp if cost_min is None else min(cost_min, c_dp)
        cost_max = c_dp if cost_max is None else max(cost_max, c_dp)
        if c_dp == c_dplus:
            equal += 1
        elif len(violations) < VERBATIM_CAP:
            violations.append(
                {
                    "instance_index": idx,
                    "targets_A0A1B0B1C0C1": "".join(LETTERS[x] for x in p6),
                    "C_unrestricted_dp": c_dp,
                    "C_Dplus": c_dplus,
                }
            )
    r6m._local_table.cache_clear()
    return {
        "instances": 4096,
        "equal_count": equal,
        "all_equal": equal == 4096,
        "dp_cost_range": [cost_min, cost_max],
        "binding_sample_rows": binding_rows,
        "binding_exact": binding_ok,
        "exact_matcher_binding_rows": 8,
        "exact_matcher_binding_exact": exact_binding_ok,
        "violating_instances_verbatim": violations,
    }


# ---- domain (b2): exhaustive structured n=2 ---------------------------------

def domain_structured_n2() -> dict[str, Any]:
    wt1 = [_letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]  # 21 canonical pairs
    violations = []
    equal = 0
    binding_rows = 0
    binding_ok = True
    swap_rows = 0
    swap_ok = True
    total = 21 ** 3
    idx = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        target_pairs = tuple(
            (wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic)
        )
        c_dp = dp_cost_n2_reader(target_pairs)
        dplus = dplus_pairs(target_pairs, 2)
        c_dplus = int(dplus["C_Dplus"])
        if c_dp > c_dplus:
            raise AssertionError({"r6o_n2_soundness_violated": [idx, c_dp, c_dplus]})
        if idx % 97 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            frozen = dp_cost_frozen_configs(terms, 2)
            binding_rows += 1
            if frozen != c_dp:
                binding_ok = False
            if not verify_dplus_witness(target_pairs, 2, dplus):
                raise AssertionError({"r6o_n2_dplus_witness_failed": idx})
        if idx % 290 == 0:
            swapped = ((target_pairs[0][1], target_pairs[0][0]),) + target_pairs[1:]
            swap_rows += 1
            if dp_cost_n2_reader(swapped) != c_dp:
                swap_ok = False
        if c_dp == c_dplus:
            equal += 1
        elif len(violations) < VERBATIM_CAP:
            violations.append(
                {
                    "instance_index": idx,
                    "block_pairs": [list(upairs[s]) for s in (ia, ib, ic)],
                    "targets": [[list(a), list(b)] for a, b in target_pairs],
                    "C_unrestricted_dp": c_dp,
                    "C_Dplus": c_dplus,
                }
            )
        idx += 1
    r6m._local_table.cache_clear()
    _block_cache.clear()
    return {
        "instances": total,
        "equal_count": equal,
        "all_equal": equal == total,
        "binding_sample_rows": binding_rows,
        "binding_exact": binding_ok,
        "block_a_swap_invariance_rows": swap_rows,
        "block_a_swap_invariance_ok": swap_ok,
        "violating_instances_verbatim": violations,
    }


# ---- domain (c): seeded random panel ----------------------------------------

def domain_random_panel() -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    rows = []
    violations = []
    for n in (2, 3):
        for i in range(120):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            target_pairs = tuple(
                (targets[2 * j], targets[2 * j + 1]) for j in range(3)
            )
            terms = r6m._synthetic_terms(target_pairs)
            r6m._local_table.cache_clear()
            c_dp = dp_cost_frozen_configs(terms, n)
            dplus = dplus_pairs(target_pairs, n)
            c_dplus = int(dplus["C_Dplus"])
            c_r6l = int(
                r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"]
            )
            if not (c_dp <= c_dplus <= c_r6l):
                raise AssertionError(
                    {"r6o_random_sandwich_violated": [n, i, c_dp, c_dplus, c_r6l]}
                )
            if i % 10 == 0 and not verify_dplus_witness(target_pairs, n, dplus):
                raise AssertionError({"r6o_random_dplus_witness_failed": [n, i]})
            row = {
                "n": n,
                "index": i,
                "C_unrestricted_dp": c_dp,
                "C_Dplus": c_dplus,
                "C_R6L_weight_one_donor": c_r6l,
                "equal": c_dp == c_dplus,
            }
            rows.append(row)
            if not row["equal"] and len(violations) < VERBATIM_CAP:
                violations.append(
                    {**row, "targets": [list(t) for t in targets]}
                )
    _block_cache.clear()
    return {
        "instances": len(rows),
        "equal_count": sum(r["equal"] for r in rows),
        "all_equal": all(r["equal"] for r in rows),
        "dplus_strictly_below_r6l_count": sum(
            r["C_Dplus"] < r["C_R6L_weight_one_donor"] for r in rows
        ),
        "rows": rows,
        "violating_instances_verbatim": violations,
    }


# ---- domain (d): frozen chemistry subjects ----------------------------------

def domain_chemistry() -> dict[str, Any]:
    receipt = json.loads(
        Path(__file__)
        .with_name("MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json")
        .read_text()
    )
    subjects = {}
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        terms, source_indices, _champions, _max_imag, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"r6o_chemistry_blob_mismatch": name})
        n = int(cfg["n_qubits"])
        six = [int(i) for i in source_indices]
        rec_sub = receipt["subjects"][name]
        if sorted(six) != sorted(int(i) for i in rec_sub["frozen_source_indices"]):
            raise AssertionError({"r6o_chemistry_source_indices_mismatch": name})
        rec_rows = {
            canonical_json(row["matching"]): row for row in rec_sub["candidate_points"]
        }
        matchings = r6m.perfect_matchings(six)
        rows = []
        for pairs in matchings:
            key = canonical_json([list(p) for p in pairs])
            if key not in rec_rows:
                raise AssertionError({"r6o_chemistry_receipt_matching_missing": [name, key]})
            rec_row = rec_rows[key]
            c_dp = int(rec_row["C_R6M"])
            c_r6l_receipt = int(rec_row["C_R6L_same_matching"])
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            dplus = dplus_pairs(target_pairs, n)
            c_dplus = int(dplus["C_Dplus"])
            c_r6l = int(r6m.donor_r6l_matching(terms, pairs, n, six)["C_R6L"])
            if c_r6l != c_r6l_receipt:
                raise AssertionError(
                    {"r6o_chemistry_r6l_receipt_mismatch": [name, key, c_r6l, c_r6l_receipt]}
                )
            if not (c_dp <= c_dplus <= c_r6l):
                raise AssertionError(
                    {"r6o_chemistry_sandwich_violated": [name, key, c_dp, c_dplus, c_r6l]}
                )
            if not verify_dplus_witness(target_pairs, n, dplus):
                raise AssertionError({"r6o_chemistry_dplus_witness_failed": [name, key]})
            rows.append(
                {
                    "matching": [list(p) for p in pairs],
                    "C_R6M_receipt_dp": c_dp,
                    "C_Dplus": c_dplus,
                    "C_R6L_recomputed": c_r6l,
                    "C_R6L_receipt": c_r6l_receipt,
                    "dp_equal": c_dp == c_dplus,
                    "ties_r6l": c_dplus == c_r6l,
                }
            )
        subjects[name] = {
            "n_qubits": n,
            "source_blob_verified": True,
            "matchings": len(rows),
            "rows": rows,
            "all_dp_equal": all(r["dp_equal"] for r in rows),
            "all_tie_r6l": all(r["ties_r6l"] for r in rows),
        }
        _block_cache.clear()
    return {
        "receipt_authority": receipt["authority"],
        "subjects": subjects,
        "matchings_checked": sum(s["matchings"] for s in subjects.values()),
        "all_dp_equal": all(s["all_dp_equal"] for s in subjects.values()),
        "all_tie_r6l": all(s["all_tie_r6l"] for s in subjects.values()),
    }


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "Frozen R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar with the "
        "donor-owned all-three Restore common-factor rule under the frozen raw "
        "support-count objective; the enlarged donor family D+ (weight-one frames "
        "with arbitrary per-block anchors, unique minimum-weight shared Tag, "
        "donor-owned factoring) satisfies C_DP <= C_D+ <= C_R6L on every instance."
    ),
    "machine_evidenced_only": (
        "Equality C_DP == C_D+ is machine-evidenced on the stated finite domains "
        "only: exhaustively at n=1 (all 4096 instances) and on the structured "
        "weight-one n=2 slice (all 9261 instances), plus the 5 R6N R6M-grammar "
        "panels, 240 seeded random n=2/n=3 instances, and all 30 recorded "
        "chemistry matchings. It is NOT a theorem for all n; the Tag-repair "
        "coupling remains analytically unbounded and is repaired here by "
        "enlarging the family, not by a proof."
    ),
    "does_not_cover": (
        "Other objectives, rotation-count trade-offs beyond the frozen fixed "
        "counts, larger Tag ranks, grammars outside the frozen family (including "
        "the R6I rank-2 grammar, whose weight-one closure R6N verified "
        "separately), or any fresh subject data. No novelty credit, no donor "
        "credit, no R6 authority: D+ is donor-owned machinery and the anchor "
        "enlargement is bookkeeping."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    f3_binding = bool(np.array_equal(F3.astype(np.int64), r6m._F3))
    if not f3_binding:
        raise AssertionError("r6o independent F3 table does not bind to frozen r6m._F3")

    tag_min = verify_tag_minimality()
    if not tag_min["verified"]:
        raise AssertionError({"r6o_tag_minimality_failed": tag_min})

    panels = domain_r6n_panels()
    n1 = domain_exhaustive_n1()
    n2 = domain_structured_n2()
    random_panel = domain_random_panel()
    chemistry = domain_chemistry()

    gates = {
        "dp_dplus_equal_r6n_panels": panels["all_equal"],
        "dp_dplus_equal_exhaustive_n1": n1["all_equal"],
        "dp_dplus_equal_structured_n2": n2["all_equal"],
        "dp_dplus_equal_random_panel": random_panel["all_equal"],
        "chemistry_dplus_equals_receipt_dp": chemistry["all_dp_equal"],
        "chemistry_dplus_ties_r6l": chemistry["all_tie_r6l"],
        "dp_reader_binding_exact": f3_binding
        and n1["binding_exact"]
        and n1["exact_matcher_binding_exact"]
        and n2["binding_exact"]
        and n2["block_a_swap_invariance_ok"],
        "tag_minimality_verified": tag_min["verified"],
        "witness_reverification_pass": all(
            row["dp_witness_checks_pass"] for row in panels["rows"]
        ),
        "no_new_subject_data": True,
    }
    integrity = {
        k: gates[k]
        for k in ("dp_reader_binding_exact", "tag_minimality_verified", "no_new_subject_data")
    }
    if not all(integrity.values()):
        raise AssertionError({"r6o_integrity_gate_failure": integrity})

    all_violations = (
        [row for row in panels["rows"] if not row["equal"]]
        + n1["violating_instances_verbatim"]
        + n2["violating_instances_verbatim"]
        + random_panel["violating_instances_verbatim"]
        + [
            {**row, "subject": name}
            for name, sub in chemistry["subjects"].items()
            for row in sub["rows"]
            if not row["dp_equal"]
        ]
    )
    verified = not all_violations and all(gates.values())
    if verified:
        authority = (
            "MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_VERIFIED__"
            "FAMILY_CLOSURE_RESTORED_ON_VERIFIED_DOMAINS__NOT_R6"
        )
        responsibility = (
            "RESP:ENLARGED_TAG_DONOR_FAMILY_MATCHES_EXACT_DP_ON_ALL_VERIFIED_FINITE_DOMAINS__"
            "R6N_TAG_ANCHOR_COUPLING_GAP_REPAIRED_BY_FAMILY_ENLARGEMENT"
        )
        discovery = None
    else:
        authority = (
            "MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_REFUTED__SECOND_NEW_REGIME_FOUND__NOT_R6"
        )
        responsibility = "RESP:SECOND_SPREAD_REGIME_DISCOVERED__REPORT_VERBATIM_AND_RE_FREEZE"
        discovery = {
            "instances_with_dp_strictly_below_dplus": all_violations,
            "note": (
                "Weight-one frames with unrestricted minimal shared Tag are still "
                "insufficient: a second coupling mechanism beyond the R6N "
                "Tag-anchor coupling is present on the listed instances."
            ),
        }

    runtime = time.monotonic() - start
    result = {
        "schema": "ORIONQ.MAXR6O.EnlargedTagDonorClosure.v1",
        "authority": authority,
        "scope": (
            "ENLARGED_TAG_DONOR_FAMILY_CLOSURE_TEST_OVER_FROZEN_R6M_GRAMMAR__"
            "EXPLANATORY_FAMILY_CLOSURE__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL",
        "dplus_definition": {
            "family": (
                "Three weight-one TARE-M2 frames with arbitrary per-block anchor "
                "qubits and ordered distinct non-identity letter pairs, per-block "
                "target permutation, common label orientation across blocks, and "
                "the unique minimum-weight shared Tag (forced letter at each "
                "distinct anchor qubit, identity elsewhere; w(S) = number of "
                "distinct anchors; feasible iff co-anchored blocks force the same "
                "letter); cost = 2 w(S) + donor-owned all-three factored Restore "
                "support; Uanti = 0; centrals cost-irrelevant."
            ),
            "enumeration": (
                "2 labels x 8 permutations x n^3 anchor triples x 216 ordered "
                "letter-pair triples; complete because the minimal Tag is unique "
                "per feasible choice tuple."
            ),
            "containments": "C_DP <= C_D+ <= C_R6L (hard integrity assertions).",
        },
        "domains": {
            "r6n_panels": panels,
            "exhaustive_n1": n1,
            "structured_n2": n2,
            "random_panel": {
                **{k: v for k, v in random_panel.items() if k != "rows"},
                "rows": random_panel["rows"],
            },
            "chemistry": chemistry,
        },
        "tag_minimality": tag_min,
        "f3_table_binding_exact": f3_binding,
        "random_seed": RANDOM_SEED,
        "gates": gates,
        "discovery": discovery,
        "claim_boundary": CLAIM_BOUNDARY,
        "runtime_seconds": round(runtime, 3),
        "chemistry_sources_read_via_frozen_batch_only": True,
        "heavy_subject_dp_rerun": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("R6O authority ceiling violated")
    Path(__file__).with_name("MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("ORIONQ_MAX_R6O_ENLARGED_TAG_DONOR=" + canonical_json(result))
    return result


if __name__ == "__main__":
    main()
