#!/usr/bin/env python3
"""QG-17: exact sharpness attack on the R6I support1 objective phase.

Uses the already-frozen V5 candidate generator unchanged. For each registered
objective it compares a verified feasible support2 witness against the exact
weighted support1 family. A strict gap proves support1 failure at that exact
objective without invoking a weighted unrestricted DP.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
ORION_QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(ORION_Q)); sys.path.insert(0, str(ORION_QG))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import qg9_support2_tightness as v5  # noqa: E402

ISSUE = "SzeChunYiu/ORION#814"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG17_R6I_PHASE_SHARPNESS_PROTOCOL_V1.md"
PARENT_QG16 = ROOT / "research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json"
PARENT_QG16_RECEIPT = ROOT / "development/orion-qg-regime-geometry/QG16_PROTECTED_RUN_RECEIPT_2026-08-21.json"
PARENT_V5 = ROOT / "research/extensions/orion-qg/QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg17-r6i-phase-sharpness.json"
TOKEN = "ORIONQG_QG17="
EXPECTED_GENERATOR_DIGEST = "bb07c127d037f68e2a1f6ca6b5defee0fbadcebdb3ae23aedd4e7266f184a4fa"
FAMILIES = ["IDENTITY_RESTORE", "ONE_DEFECT_A", "ONE_DEFECT_B", "MATCHED_DEFECT"]

# Coefficients are (t_nc,t_c,t_tag,t_r) multiplied by `scale`.
OBJECTIVES = [
    ("O0", (4, 2, 2, 1), 1),
    ("O_tag_out", (8, 4, 5, 2), 2),
    ("O_restore_out", (16, 8, 8, 5), 4),
    ("O_nc_out", (3, 3, 2, 2), 2),
]

# QG-16 facets in cost-difference coefficient order (t_c,t_nc,t_tag,t_r).
QG16_FACETS = [
    (0, 2, 0, -5),
    (1, 1, 0, -5),
    (0, 2, -2, -2),
    (1, 1, -2, -2),
]


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def K(x):
    return (int(x[0]), int(x[1]))


def keyj(x):
    return [int(x[0]), int(x[1])]


def frame_triple(r0, r1):
    return (r0, r1, p10.mul(r0, r1))


def labels(s0, s1, r0, r1):
    return (2 * p10.symp(s0, r0) + p10.symp(s1, r0), 2 * p10.symp(s0, r1) + p10.symp(s1, r1))


def objective_json(coeffs, scale):
    names = ("t_nc", "t_c", "t_tag", "t_r")
    out = {}
    for name, x in zip(names, coeffs):
        g = math.gcd(abs(x), scale)
        out[name] = {"numerator": x // g, "denominator": scale // g}
    return out


def frac_json(num: int, den: int):
    if den < 0:
        num, den = -num, -den
    g = math.gcd(abs(num), den)
    return {"numerator": num // g, "denominator": den // g}


def support1_pairs():
    keys = [(x, z) for x in range(4) for z in range(4) if (x, z) != (0, 0) and p10.wt((x, z)) <= 1]
    pairs = tuple((a, b) for a in keys for b in keys if p10.symp(a, b) == 1)
    if len(pairs) != 12:
        raise AssertionError({"support1_pair_count": len(pairs)})
    return pairs


PAIRS = support1_pairs()
ALL_KEYS = tuple((x, z) for x in range(4) for z in range(4))
PERMS = tuple(itertools.permutations(range(3)))


def build_tag_support_table():
    """Exact shared-Tag support minima for each support1 frame-pair cell.

    Not every A/B ordered support1 frame pair admits equal nonzero distinct
    labels under a shared Tag.  Such Cartesian pair cells are infeasible and
    are represented by None; exact cap1 minimizes over feasible cells only.
    """
    table = []
    for pa in PAIRS:
        row = []
        for pb in PAIRS:
            best = None
            for s0 in ALL_KEYS:
                for s1 in ALL_KEYS:
                    la = labels(s0, s1, *pa)
                    lb = labels(s0, s1, *pb)
                    if la != lb or la[0] not in (1, 2, 3) or la[1] not in (1, 2, 3) or la[0] == la[1]:
                        continue
                    cand = (p10.wt(s0) + p10.wt(s1), s0, s1, la)
                    if best is None or cand < best:
                        best = cand
            row.append(best)
        table.append(tuple(row))
    return tuple(table)


TAG_TABLE = build_tag_support_table()
TAG_FEASIBLE_CELLS = sum(int(TAG_TABLE[i][j] is not None) for i in range(12) for j in range(12))
TAG_FEASIBLE_PER_A = tuple(sum(int(TAG_TABLE[i][j] is not None) for j in range(12)) for i in range(12))
if TAG_FEASIBLE_CELLS <= 0 or any(x <= 0 for x in TAG_FEASIBLE_PER_A):
    raise AssertionError({"support1_tag_feasibility_degenerate": [TAG_FEASIBLE_CELLS, TAG_FEASIBLE_PER_A]})


class WeightedCap1:
    def __init__(self):
        self.a_cache = {}
        self.b_cache = {}
        self.bh_cache = {}

    @staticmethod
    def tkey(ts):
        return tuple((int(x[0]), int(x[1])) for x in ts)

    def rest_a(self, ts):
        k = self.tkey(ts)
        if k not in self.a_cache:
            vals = []
            for a, b in PAIRS:
                rs = frame_triple(a, b)
                vals.append(sum(p10.wt(p10.mul(ts[i], rs[i])) for i in range(3)))
            self.a_cache[k] = tuple(vals)
        return self.a_cache[k]

    def rest_b(self, ts):
        k = self.tkey(ts)
        if k not in self.b_cache:
            vals = []
            for a, b in PAIRS:
                rs = frame_triple(a, b)
                vals.append(min(sum(p10.wt(p10.mul(ts[perm[i]], rs[i])) for i in range(3)) for perm in PERMS))
            self.b_cache[k] = tuple(vals)
        return self.b_cache[k]

    def bh(self, obj_name, coeffs, ts):
        # For each A pair, best feasible B-pair contribution including shared Tag.
        k = (obj_name, self.tkey(ts))
        if k not in self.bh_cache:
            _tnc, _tc, ttag, tr = coeffs
            rb = self.rest_b(ts)
            rows = []
            for i in range(12):
                best = None
                for j in range(12):
                    tag = TAG_TABLE[i][j]
                    if tag is None:
                        continue
                    score = tr * rb[j] + ttag * tag[0]
                    cand = (score, j, tag[0], rb[j], tag[1], tag[2], tag[3])
                    if best is None or cand < best:
                        best = cand
                if best is None:
                    raise AssertionError({"no_feasible_B_partner_for_A_pair": i})
                rows.append(best)
            self.bh_cache[k] = tuple(rows)
        return self.bh_cache[k]

    def exact(self, obj_name, coeffs, scale, ta, tb):
        _tnc, _tc, _ttag, tr = coeffs
        ra = self.rest_a(ta)
        bh = self.bh(obj_name, coeffs, tb)
        best = None
        for i in range(12):
            score = tr * ra[i] + bh[i][0]
            cand = (score, i, bh[i][1], ra[i], bh[i][3], bh[i][2], bh[i][4], bh[i][5], bh[i][6])
            if best is None or cand < best:
                best = cand
        score, i, j, rA, rB, tag_support, s0, s1, lab = best
        return {
            "scaled_cost": int(score),
            "scale": scale,
            "resource": [0, 0, int(tag_support), int(rA + rB)],
            "pair_A_index": i,
            "pair_B_index": j,
            "pair_A": [keyj(x) for x in PAIRS[i]],
            "pair_B": [keyj(x) for x in PAIRS[j]],
            "S0": keyj(s0),
            "S1": keyj(s1),
            "labels": list(lab),
            "restore_A": int(rA),
            "restore_B": int(rB),
        }


def support2_frame_choice(pair, coeffs):
    tnc, tc, _ttag, _tr = coeffs
    rs = frame_triple(*pair)
    best = None
    for central in range(3):
        uc = p10.wt(rs[central]) - 1
        unc = sum(p10.wt(rs[k]) - 1 for k in range(3) if k != central)
        score = tc * uc + tnc * unc
        cand = (score, central, uc, unc)
        if best is None or cand < best:
            best = cand
    return best


def support2_static(ba, bb, ta, tb):
    ra = (K(ba["R0"]), K(ba["R1"]))
    rb = (K(bb["R0"]), K(bb["R1"]))
    s0a, s1a = K(ba["S0"]), K(ba["S1"])
    s0b, s1b = K(bb["S0"]), K(bb["S1"])
    if (s0a, s1a, tuple(ba["labels"])) != (s0b, s1b, tuple(bb["labels"])):
        raise AssertionError("V5 compatible pair lost shared Tag identity")
    if p10.symp(*ra) != 1 or p10.symp(*rb) != 1:
        raise AssertionError("support2 witness frame not symplectic")
    if labels(s0a, s1a, *ra) != tuple(ba["labels"]) or labels(s0a, s1a, *rb) != tuple(bb["labels"]):
        raise AssertionError("support2 witness labels drift")
    rsa, rsb = frame_triple(*ra), frame_triple(*rb)
    rest_a = sum(p10.wt(p10.mul(ta[k], rsa[k])) for k in range(3))
    best_b = None
    for perm in PERMS:
        rest = sum(p10.wt(p10.mul(tb[perm[k]], rsb[k])) for k in range(3))
        cand = (rest, tuple(perm))
        if best_b is None or cand < best_b:
            best_b = cand
    return {
        "pair_A": ra,
        "pair_B": rb,
        "S0": s0a,
        "S1": s1a,
        "labels": tuple(ba["labels"]),
        "tag_support": p10.wt(s0a) + p10.wt(s1a),
        "restore_A": int(rest_a),
        "restore_B": int(best_b[0]),
        "permutation_B": best_b[1],
    }


def support2_score(static, coeffs, scale):
    tnc, tc, ttag, tr = coeffs
    fa = support2_frame_choice(static["pair_A"], coeffs)
    fb = support2_frame_choice(static["pair_B"], coeffs)
    uc = fa[2] + fb[2]
    unc = fa[3] + fb[3]
    tag = static["tag_support"]
    rest = static["restore_A"] + static["restore_B"]
    score = tc * uc + tnc * unc + ttag * tag + tr * rest
    return {
        "scaled_cost": int(score),
        "scale": scale,
        "resource": [int(uc), int(unc), int(tag), int(rest)],
        "central_A": int(fa[1]),
        "central_B": int(fb[1]),
        "permutation_B": list(static["permutation_B"]),
    }


def normalize_vector(v):
    vals = list(v)
    g = 0
    for x in vals:
        g = math.gcd(g, abs(int(x)))
    if g:
        vals = [int(x) // g for x in vals]
    o0 = (2, 4, 2, 1)
    dot = sum(vals[i] * o0[i] for i in range(4))
    if dot < 0 or (dot == 0 and next((x for x in vals if x), 1) < 0):
        vals = [-x for x in vals]
    return tuple(vals)


def facet_match(diff):
    nd = normalize_vector(diff)
    matches = []
    for f in QG16_FACETS:
        if normalize_vector(f) == nd:
            matches.append(list(f))
    return nd, matches


def witness_record(candidate_index, family, pair_kind, i, j, tmeta, blocks, ta, tb, obj_name, coeffs, scale, c2, c1):
    diff = tuple(c2["resource"][k] - c1["resource"][k] for k in range(4))
    nd, matches = facet_match(diff)
    gap_scaled = c1["scaled_cost"] - c2["scaled_cost"]
    return {
        "candidate_index": candidate_index,
        "objective": obj_name,
        "theta": objective_json(coeffs, scale),
        "family": family,
        "pair_kind": pair_kind,
        "block_indices": [i, j],
        "block_A": blocks[i],
        "block_B": blocks[j],
        "targets_A": [keyj(x) for x in ta],
        "targets_B": [keyj(x) for x in tb],
        "template": tmeta,
        "support2": c2,
        "cap1": c1,
        "gap_cap1_minus_support2": frac_json(gap_scaled, scale),
        "difference_vector_t_c_t_nc_t_tag_t_r": list(diff),
        "normalized_difference_vector": list(nd),
        "qg16_facet_matches": matches,
        "affine_classification": "QG16_FACET_AFFINE_MATCH" if matches else "NEW_TRUE_PHASE_BOUNDARY_CANDIDATE",
    }


def main() -> int:
    qg16 = json.loads(PARENT_QG16.read_text())
    qg16r = json.loads(PARENT_QG16_RECEIPT.read_text())
    v5r = json.loads(PARENT_V5.read_text())
    parent_checks = {
        "qg16_terminal": qg16.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED",
        "qg16_protected": qg16r.get("terminal") == qg16.get("terminal") and qg16r.get("both_accept") is True,
        "qg16_sharpness_open": qg16.get("global_phase_boundary_sharpness") == "OPEN",
        "v5_terminal": v5r.get("terminal") == "QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL",
        "v5_generator_digest": v5r.get("candidate_generator_digest_before_scoring") == EXPECTED_GENERATOR_DIGEST,
    }
    if not all(parent_checks.values()):
        raise AssertionError({"parent_binding_gap": parent_checks})

    blocks, bmeta = v5.obstruction_blocks()
    pairs = v5.candidate_pairs(blocks)
    generator = {"blocks": blocks, "block_metadata": bmeta, "pair_count": len(pairs), "pairs": pairs, "template_families": FAMILIES}
    generator_digest = hashlib.sha256(canonical(generator).encode()).hexdigest()
    if generator_digest != EXPECTED_GENERATOR_DIGEST:
        raise AssertionError({"generator_digest_drift": [generator_digest, EXPECTED_GENERATOR_DIGEST]})

    cap1 = WeightedCap1()
    stats = {
        name: {"objective": objective_json(coeffs, scale), "strict_count": 0, "first": None, "max_gap": None, "family_histogram": {}, "pair_kind_histogram": {}}
        for name, coeffs, scale in OBJECTIVES
    }
    family_counts = defaultdict(int)
    tested = 0

    for family in FAMILIES:
        for i, j, pair_kind in pairs:
            for ta, tb, tmeta in v5.template_instances(blocks[i], blocks[j], family):
                tested += 1
                family_counts[family] += 1
                static = support2_static(blocks[i], blocks[j], ta, tb)
                for name, coeffs, scale in OBJECTIVES:
                    c2 = support2_score(static, coeffs, scale)
                    c1 = cap1.exact(name, coeffs, scale, ta, tb)
                    if c2["scaled_cost"] < c1["scaled_cost"]:
                        rec = witness_record(tested, family, pair_kind, i, j, tmeta, blocks, ta, tb, name, coeffs, scale, c2, c1)
                        st = stats[name]
                        st["strict_count"] += 1
                        st["family_histogram"][family] = st["family_histogram"].get(family, 0) + 1
                        st["pair_kind_histogram"][pair_kind] = st["pair_kind_histogram"].get(pair_kind, 0) + 1
                        if st["first"] is None:
                            st["first"] = rec
                        if st["max_gap"] is None:
                            st["max_gap"] = rec
                        else:
                            old = st["max_gap"]["gap_cap1_minus_support2"]
                            new = rec["gap_cap1_minus_support2"]
                            if new["numerator"] * old["denominator"] > old["numerator"] * new["denominator"]:
                                st["max_gap"] = rec

    expected_family_counts = v5r.get("family_candidates_tested", {})
    outside_names = ("O_tag_out", "O_restore_out", "O_nc_out")
    outside_positive = [name for name in outside_names if stats[name]["strict_count"] > 0]
    facet_matches = []
    for name in outside_positive:
        for role in ("first", "max_gap"):
            rec = stats[name][role]
            if rec and rec["qg16_facet_matches"]:
                facet_matches.append({"objective": name, "role": role, "matches": rec["qg16_facet_matches"], "difference": rec["normalized_difference_vector"]})

    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "parents_bound": all(parent_checks.values()),
        "generator_digest_exact": generator_digest == EXPECTED_GENERATOR_DIGEST,
        "unique_blocks_1296": len(blocks) == 1296,
        "pair_count_4104": len(pairs) == 4104,
        "candidate_count_211248": tested == 211248,
        "family_counts_match_v5": dict(family_counts) == expected_family_counts,
        "support1_pair_count_12": len(PAIRS) == 12,
        "support1_tag_feasible_cells_nonzero": TAG_FEASIBLE_CELLS > 0,
        "every_A_pair_has_feasible_B_partner": all(x > 0 for x in TAG_FEASIBLE_PER_A),
        "O0_zero_strict": stats["O0"]["strict_count"] == 0,
    }
    positive = bool(outside_positive) and all(gates.values())
    terminal = "QG17_SUPPORT2_PHASE_WITNESS_FOUND_AT_FROZEN_OUTSIDE_OBJECTIVE" if positive else "QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN"
    annotation = "QG17_QG16_FACET_LOCALLY_SHARP_BY_AFFINE_WITNESS" if facet_matches else None

    result = {
        "schema": "ORION.QG.QG17.R6IPhaseSharpness.v1",
        "issue": ISSUE,
        "protocol_sha256": sha(PROTOCOL),
        "parent_qg16_sha256": sha(PARENT_QG16),
        "parent_qg16_receipt_sha256": sha(PARENT_QG16_RECEIPT),
        "parent_v5_sha256": sha(PARENT_V5),
        "parent_checks": parent_checks,
        "candidate_generator_digest": generator_digest,
        "candidate_generator_summary": {"unique_blocks": len(blocks), "pair_count": len(pairs), "template_families": FAMILIES},
        "support1_tag_table": {"total_pair_cells": 144, "feasible_pair_cells": TAG_FEASIBLE_CELLS, "feasible_B_partners_per_A_pair": list(TAG_FEASIBLE_PER_A)},
        "candidates_tested": tested,
        "family_candidates_tested": dict(family_counts),
        "objectives": stats,
        "outside_objectives_with_strict_witness": outside_positive,
        "facet_affine_matches": facet_matches,
        "annotation": annotation,
        "cap1_cache": {"a_target_classes": len(cap1.a_cache), "b_target_classes": len(cap1.b_cache), "b_envelope_entries": len(cap1.bh_cache)},
        "gates": gates,
        "terminal": terminal,
        "global_phase_boundary_complete": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "network_access": False,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    ap = argparse.ArgumentParser(); ap.add_argument("--output", default=str(DEFAULT_OUT)); ns = ap.parse_args()
    p = Path(ns.output); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({"terminal": terminal, "annotation": annotation, "result_digest": result["result_digest"], "candidates_tested": tested, "tag_feasible_cells": TAG_FEASIBLE_CELLS, "strict_counts": {name: stats[name]["strict_count"] for name, _coeffs, _scale in OBJECTIVES}, "outside_positive": outside_positive, "facet_match_count": len(facet_matches)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
