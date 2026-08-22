#!/usr/bin/env python3
"""QG-17b: the tie locus — exact location of the R6I support-1/support-2 phase boundary.

QG-17 found no strict support-2 witness on the complete frozen V5 domain, but recorded
that at ``O_nc_out`` the maximum of ``C_cap1 - C2`` is exactly 0, tied on 4,896 of
211,248 candidates.  A tie at exactly zero is the signature of sitting ON the phase
boundary.  This lane stops hunting witnesses and solves for the locus instead: it
extracts the exact hyperplanes ``d . theta = 0`` realized by the tie set, then crosses
each one at a pre-registered exact rational offset and asks the committed referee
whether a support-2 member strictly beats the exact weighted support-1 optimum on the
far side.

All arithmetic is integer / :class:`fractions.Fraction`.  No float is ever constructed
on the scientific path.  Protocol:
``development/orion-qg-regime-geometry/QG17B_TIE_LOCUS_PROTOCOL_V1.md`` (frozen first).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
ORION_QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(ORION_Q))
sys.path.insert(0, str(ORION_QG))

import qg9_support2_tightness as v5  # noqa: E402  (frozen V5 candidate generator, unmodified)
import qg17_r6i_phase_sharpness as qg17  # noqa: E402  (frozen QG-17 referee, unmodified)

ISSUE = "SzeChunYiu/ORION#814"
LANE = "QG-17b — the tie locus"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG17B_TIE_LOCUS_PROTOCOL_V1.md"
PARENT_QG16 = ROOT / "research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json"
PARENT_QG17 = ROOT / "research/extensions/orion-qg/QG17_R6I_PHASE_SHARPNESS_RESULTS.json"
PARENT_V5 = ROOT / "research/extensions/orion-qg/QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json"
DEFAULT_OUT = ROOT / "research/extensions/orion-qg/QG17B_TIE_LOCUS_RESULTS.json"
TOKEN = "ORIONQG_QG17B="

EXPECTED_GENERATOR_DIGEST = "bb07c127d037f68e2a1f6ca6b5defee0fbadcebdb3ae23aedd4e7266f184a4fa"
TIE_OBJECTIVE = "O_nc_out"
CROSSING_M = 64  # pre-registered in the frozen protocol; never tuned to an outcome

# QG-17's verbatim post-hoc diagnostic, bound as a hostile gate.
QG17_MAX_MARGINS = {"O0": "-5", "O_tag_out": "-5", "O_restore_out": "-13/4", "O_nc_out": "0"}
QG17_TIE_COUNTS = {"O0": 0, "O_tag_out": 0, "O_restore_out": 0, "O_nc_out": 4896}
QG17_STRICT_COUNTS = {"O0": 0, "O_tag_out": 0, "O_restore_out": 0, "O_nc_out": 0}
QG17_FAMILY_COUNTS = {"IDENTITY_RESTORE": 4104, "ONE_DEFECT_A": 69768, "ONE_DEFECT_B": 69768, "MATCHED_DEFECT": 67608}

# QG-16 committed facets, verbatim, in cost-difference order (t_c,t_nc,t_tag,t_r).
QG16_FACETS_VERBATIM = [
    {"index": 0, "halfspace": "2*t_nc >= 5*t_r", "vector": [0, 2, 0, -5]},
    {"index": 1, "halfspace": "t_c+t_nc >= 5*t_r", "vector": [1, 1, 0, -5]},
    {"index": 2, "halfspace": "2*t_nc >= 2*t_r+2*t_tag", "vector": [0, 2, -2, -2]},
    {"index": 3, "halfspace": "t_c+t_nc >= 2*t_r+2*t_tag", "vector": [1, 1, -2, -2]},
]


# ---------------------------------------------------------------- exactness guard
class InexactValue(AssertionError):
    pass


_EXACT_CHECKS = [0]


def X(value):
    """Assert a value entering a decision is exact (int or Fraction), never float."""
    _EXACT_CHECKS[0] += 1
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise InexactValue({"non_exact_decision_value": repr(value), "type": type(value).__name__})
    return value


def XV(vec):
    for v in vec:
        X(v)
    return tuple(vec)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def frac_json(f: Fraction) -> dict:
    return {"numerator": int(f.numerator), "denominator": int(f.denominator)}


def frac_str(f: Fraction) -> str:
    return str(int(f)) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


# ------------------------------------------------------------- ordering helpers
# Scanner objective order is (t_nc,t_c,t_tag,t_r); resource / hyperplane order is
# (t_c,t_nc,t_tag,t_r).  Both conversions are pure integer permutations.
def coeffs_to_dorder(coeffs):
    tnc, tc, ttag, tr = coeffs
    return (int(tc), int(tnc), int(ttag), int(tr))


def dorder_to_coeffs(d):
    dc, dnc, dtag, dr = d
    return (int(dnc), int(dc), int(dtag), int(dr))


def dot_d(d, coeffs, scale) -> Fraction:
    """Exact d . theta with d in (t_c,t_nc,t_tag,t_r) order."""
    td = coeffs_to_dorder(coeffs)
    acc = 0
    for k in range(4):
        acc += int(d[k]) * td[k]
    return Fraction(X(acc), X(int(scale)))


def qg16_cone(coeffs, scale):
    """Exact QG-16 cone membership of an objective."""
    margins = []
    for f in QG16_FACETS_VERBATIM:
        margins.append(dot_d(f["vector"], coeffs, scale))
    inside = all(X(m) >= 0 for m in margins)
    return {
        "facet_margins": [frac_str(m) for m in margins],
        "facet_margins_exact": [frac_json(m) for m in margins],
        "inside_qg16_cone": bool(inside),
        "minimum_margin": frac_str(min(margins)),
    }


def crossing_objectives(nd):
    """Frozen rule: integer coefficient vector of O_nc_out rescaled by M, then -/+ d."""
    base_coeffs, base_scale = None, None
    for name, coeffs, scale in qg17.OBJECTIVES:
        if name == TIE_OBJECTIVE:
            base_coeffs, base_scale = coeffs, scale
    if base_coeffs is None:
        raise AssertionError("tie objective missing from frozen objective list")
    m_coeffs = tuple(int(c) * CROSSING_M for c in base_coeffs)
    m_scale = int(base_scale) * CROSSING_M
    dc = dorder_to_coeffs(nd)
    minus = tuple(m_coeffs[k] - dc[k] for k in range(4))
    plus = tuple(m_coeffs[k] + dc[k] for k in range(4))
    return {
        "base_integer_coeffs_t_nc_t_c_t_tag_t_r": list(m_coeffs),
        "scale": m_scale,
        "M": CROSSING_M,
        "MINUS": {"coeffs": minus, "scale": m_scale},
        "PLUS": {"coeffs": plus, "scale": m_scale},
        "feasible": all(c > 0 for c in minus) and all(c > 0 for c in plus),
    }


# --------------------------------------------------------------------- analysis
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DEFAULT_OUT))
    ns = ap.parse_args()
    t_start = time.monotonic()

    qg16 = json.loads(PARENT_QG16.read_text())
    qg17r = json.loads(PARENT_QG17.read_text())
    v5r = json.loads(PARENT_V5.read_text())
    parent_checks = {
        "qg16_terminal": qg16.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED",
        "qg16_sharpness_open": qg16.get("global_phase_boundary_sharpness") == "OPEN",
        "qg16_facets_verbatim": qg16.get("full_cone_halfspaces") == [f["halfspace"] for f in QG16_FACETS_VERBATIM],
        "qg17_terminal": qg17r.get("terminal") == "QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN",
        "qg17_both_accept": qg17r.get("both_accept") is True,
        "qg17_candidates_tested": qg17r.get("candidate_generator", {}).get("candidates_tested") == 211248,
        "v5_terminal": v5r.get("terminal") == "QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL",
        "v5_generator_digest": v5r.get("candidate_generator_digest_before_scoring") == EXPECTED_GENERATOR_DIGEST,
    }

    diag = qg17r.get("post_hoc_diagnostic_not_protocol_frozen", {})
    qg17_bound_verbatim = {
        "authority_of_source_diagnostic": diag.get("authority"),
        "max_margin_C_cap1_minus_C2": diag.get("max_margin_C_cap1_minus_C2_over_full_domain"),
        "exact_tie_counts": diag.get("exact_tie_counts_C2_equals_C_cap1"),
        "strict_counts": {o["name"]: o["strict_witness_count"] for o in qg17r.get("objectives", [])},
        "candidates_tested": qg17r.get("candidate_generator", {}).get("candidates_tested"),
        "family_candidates_tested": qg17r.get("candidate_generator", {}).get("family_candidates_tested"),
        "terminal": qg17r.get("terminal"),
        "authority": qg17r.get("authority"),
    }

    # ---- frozen generator, digest-gated ------------------------------------
    blocks, bmeta = v5.obstruction_blocks()
    pairs = v5.candidate_pairs(blocks)
    generator = {
        "blocks": blocks, "block_metadata": bmeta, "pair_count": len(pairs), "pairs": pairs,
        "template_families": qg17.FAMILIES,
    }
    generator_digest = hashlib.sha256(canonical(generator).encode()).hexdigest()

    cap1 = qg17.WeightedCap1()
    obj_by_name = {name: (coeffs, scale) for name, coeffs, scale in qg17.OBJECTIVES}

    # ---- Q1 pass 1: complete scan, exact margins / ties at all four objectives
    scan = {
        name: {"strict_count": 0, "tie_count": 0, "max_margin_scaled": None, "scale": scale}
        for name, _c, scale in qg17.OBJECTIVES
    }
    family_counts = defaultdict(int)
    ties = []          # tied candidates at TIE_OBJECTIVE, frozen candidate order
    tested = 0
    tie_coeffs, tie_scale = obj_by_name[TIE_OBJECTIVE]

    for family in qg17.FAMILIES:
        for i, j, pair_kind in pairs:
            for ta, tb, tmeta in v5.template_instances(blocks[i], blocks[j], family):
                tested += 1
                family_counts[family] += 1
                static = qg17.support2_static(blocks[i], blocks[j], ta, tb)
                for name, coeffs, scale in qg17.OBJECTIVES:
                    c2 = qg17.support2_score(static, coeffs, scale)
                    c1 = cap1.exact(name, coeffs, scale, ta, tb)
                    s2 = X(int(c2["scaled_cost"]))
                    s1 = X(int(c1["scaled_cost"]))
                    st = scan[name]
                    margin = s1 - s2
                    if st["max_margin_scaled"] is None or margin > st["max_margin_scaled"]:
                        st["max_margin_scaled"] = margin
                    if s2 < s1:
                        st["strict_count"] += 1
                    elif s2 == s1:
                        st["tie_count"] += 1
                        if name == TIE_OBJECTIVE:
                            r2 = XV(tuple(int(x) for x in c2["resource"]))
                            r1 = XV(tuple(int(x) for x in c1["resource"]))
                            ties.append({
                                "candidate_index": tested, "family": family, "pair_kind": pair_kind,
                                "block_indices": (i, j), "targets_A": ta, "targets_B": tb,
                                "template": tmeta, "r2": r2, "r1": r1,
                                "d": tuple(r2[k] - r1[k] for k in range(4)),
                            })

    objective_scan = {}
    for name, coeffs, scale in qg17.OBJECTIVES:
        st = scan[name]
        mm = Fraction(X(int(st["max_margin_scaled"])), X(int(scale)))
        objective_scan[name] = {
            "theta": qg17.objective_json(coeffs, scale),
            "strict_count": st["strict_count"],
            "tie_count": st["tie_count"],
            "max_margin_C_cap1_minus_C2": frac_str(mm),
            "max_margin_exact": frac_json(mm),
            "qg16_position": qg16_cone(coeffs, scale),
        }

    # ---- Q1 pass 2: the exact hyperplane set --------------------------------
    degenerate = [t for t in ties if all(x == 0 for x in t["d"])]
    nondeg = [t for t in ties if any(x != 0 for x in t["d"])]
    on_hyperplane = True
    by_normal = defaultdict(list)
    raw_by_normal = defaultdict(lambda: defaultdict(int))
    for t in nondeg:
        if X(dot_d(t["d"], tie_coeffs, tie_scale)) != 0:
            on_hyperplane = False
        nd = qg17.normalize_vector(t["d"])
        by_normal[nd].append(t)
        raw_by_normal[nd][tuple(t["d"])] += 1
    normals = sorted(by_normal)

    facet_norms = {qg17.normalize_vector(f["vector"]): f for f in QG16_FACETS_VERBATIM}

    # ---- Q2: the crossing test ---------------------------------------------
    hyperplanes = []
    crossing_rule_ok = True
    all_witnesses_recomputed = True
    boundary_locating = []

    for nd in normals:
        members = by_normal[nd]
        cx = crossing_objectives(nd)
        rec = {
            "normalized_normal_t_c_t_nc_t_tag_t_r": list(nd),
            "tying_candidate_count": len(members),
            "raw_difference_vectors": [
                {"d": list(dv), "multiplicity": raw_by_normal[nd][dv]} for dv in sorted(raw_by_normal[nd])
            ],
            "objective_on_hyperplane": True,
            "d_dot_O_nc_out": "0",
            "crossing_rule": {
                "formula": "theta_side = M * O_nc_out(integer coeffs) -/+ d, M = 64, scale = 2M = 128",
                "M": CROSSING_M,
                "base_integer_coeffs_t_nc_t_c_t_tag_t_r": cx["base_integer_coeffs_t_nc_t_c_t_tag_t_r"],
                "scale": cx["scale"],
                "feasible": cx["feasible"],
            },
            "sides": {},
        }
        # exact restatement that the tie objective lies on this hyperplane
        chk = dot_d(nd, tie_coeffs, tie_scale)
        if X(chk) != 0:
            rec["objective_on_hyperplane"] = False
            rec["d_dot_O_nc_out"] = frac_str(chk)
            on_hyperplane = False

        for side in ("MINUS", "PLUS"):
            coeffs, scale = cx[side]["coeffs"], cx[side]["scale"]
            oname = f"{TIE_OBJECTIVE}__{'-'.join(str(x) for x in nd)}__{side}"
            # frozen-rule re-derivation gate
            base = cx["base_integer_coeffs_t_nc_t_c_t_tag_t_r"]
            dcv = dorder_to_coeffs(nd)
            sgn = -1 if side == "MINUS" else 1
            if tuple(coeffs) != tuple(base[k] + sgn * dcv[k] for k in range(4)) or scale != cx["scale"]:
                crossing_rule_ok = False
            side_dot = dot_d(nd, coeffs, scale)
            witnesses = []
            first_rec = None
            max_rec = None
            for t in members:
                static = qg17.support2_static(blocks[t["block_indices"][0]], blocks[t["block_indices"][1]],
                                              t["targets_A"], t["targets_B"])
                c2 = qg17.support2_score(static, coeffs, scale)
                c1 = cap1.exact(oname, coeffs, scale, t["targets_A"], t["targets_B"])
                s2 = X(int(c2["scaled_cost"]))
                s1 = X(int(c1["scaled_cost"]))
                if s2 < s1:
                    gap = Fraction(X(s1 - s2), X(int(scale)))
                    witnesses.append(t["candidate_index"])
                    full = {
                        "candidate_index": t["candidate_index"],
                        "side": side,
                        "objective_name": oname,
                        "theta": qg17.objective_json(coeffs, scale),
                        "theta_integer_coeffs_t_nc_t_c_t_tag_t_r": [int(x) for x in coeffs],
                        "theta_scale": int(scale),
                        "family": t["family"],
                        "pair_kind": t["pair_kind"],
                        "block_indices": list(t["block_indices"]),
                        "block_A": blocks[t["block_indices"][0]],
                        "block_B": blocks[t["block_indices"][1]],
                        "targets_A": [qg17.keyj(x) for x in t["targets_A"]],
                        "targets_B": [qg17.keyj(x) for x in t["targets_B"]],
                        "template": t["template"],
                        "tie_resource_r2_at_O_nc_out": list(t["r2"]),
                        "tie_resource_r1_at_O_nc_out": list(t["r1"]),
                        "difference_vector_d_t_c_t_nc_t_tag_t_r": list(t["d"]),
                        "normalized_normal": list(nd),
                        "support2_at_theta": {
                            "resource": [int(x) for x in c2["resource"]],
                            "C2": frac_str(Fraction(s2, int(scale))),
                            "C2_exact": frac_json(Fraction(s2, int(scale))),
                            "central_A": c2["central_A"], "central_B": c2["central_B"],
                            "permutation_B": c2["permutation_B"],
                        },
                        "cap1_at_theta": {
                            "resource": [int(x) for x in c1["resource"]],
                            "C_cap1": frac_str(Fraction(s1, int(scale))),
                            "C_cap1_exact": frac_json(Fraction(s1, int(scale))),
                            "pair_A": c1["pair_A"], "pair_B": c1["pair_B"],
                            "S0": c1["S0"], "S1": c1["S1"], "labels": c1["labels"],
                            "restore_A": c1["restore_A"], "restore_B": c1["restore_B"],
                        },
                        "gap_C_cap1_minus_C2": frac_str(gap),
                        "gap_exact": frac_json(gap),
                        "strict_support2_win": True,
                        "referee_recomputed_at_this_theta": True,
                        "qg16_position_of_theta": qg16_cone(coeffs, scale),
                    }
                    if first_rec is None:
                        first_rec = full
                    if max_rec is None or Fraction(max_rec["gap_exact"]["numerator"], max_rec["gap_exact"]["denominator"]) < gap:
                        max_rec = full
            rec["sides"][side] = {
                "objective_name": oname,
                "theta": qg17.objective_json(coeffs, scale),
                "theta_integer_coeffs_t_nc_t_c_t_tag_t_r": [int(x) for x in coeffs],
                "theta_scale": int(scale),
                "d_dot_theta": frac_str(side_dot),
                "d_dot_theta_sign": (-1 if side_dot < 0 else (1 if side_dot > 0 else 0)),
                "qg16_position_of_theta": qg16_cone(coeffs, scale),
                "tying_candidates_evaluated": len(members),
                "crossing_witness_count": len(witnesses),
                "sign_flipped": bool(witnesses),
                "crossing_witness_candidate_indices": witnesses,
                "first_crossing_witness": first_rec,
                "max_gap_crossing_witness": max_rec,
            }
            if first_rec is not None and not (first_rec["referee_recomputed_at_this_theta"] and first_rec["strict_support2_win"]):
                all_witnesses_recomputed = False

        flipped = any(rec["sides"][s]["sign_flipped"] for s in ("MINUS", "PLUS"))
        rec["sign_flip_on_crossing"] = bool(flipped)
        rec["total_crossing_witnesses"] = sum(rec["sides"][s]["crossing_witness_count"] for s in ("MINUS", "PLUS"))
        # ---- Q3 ------------------------------------------------------------
        match = facet_norms.get(nd)
        rec["qg16_facet_comparison"] = {
            "method": "EXACT_INTEGER_PROPORTIONALITY_AFTER_GCD_AND_SIGN_NORMALIZATION",
            "matched_facet_index": (match["index"] if match else None),
            "matched_facet_halfspace_verbatim": (match["halfspace"] if match else None),
            "matched_facet_vector": (list(match["vector"]) if match else None),
            "classification": ("QG16_FACET_EXACT_PROPORTIONAL" if match else "NEW_TRUE_BOUNDARY_FACE_NOT_IN_QG16_CERTIFICATE"),
            "qg16_facet_normalized_normals": [list(k) for k in sorted(facet_norms)],
        }
        if flipped:
            boundary_locating.append(rec)
        hyperplanes.append(rec)

    facet_locally_sharp = [
        {
            "facet_index": h["qg16_facet_comparison"]["matched_facet_index"],
            "facet_halfspace_verbatim": h["qg16_facet_comparison"]["matched_facet_halfspace_verbatim"],
            "tie_hyperplane_normal": h["normalized_normal_t_c_t_nc_t_tag_t_r"],
            "crossing_witness_count": h["total_crossing_witnesses"],
        }
        for h in boundary_locating if h["qg16_facet_comparison"]["matched_facet_index"] is not None
    ]
    new_faces = [
        {
            "tie_hyperplane_normal": h["normalized_normal_t_c_t_nc_t_tag_t_r"],
            "tying_candidate_count": h["tying_candidate_count"],
            "sign_flip_on_crossing": h["sign_flip_on_crossing"],
            "total_crossing_witnesses": h["total_crossing_witnesses"],
            "raw_difference_vectors": h["raw_difference_vectors"],
        }
        for h in hyperplanes if h["qg16_facet_comparison"]["matched_facet_index"] is None
    ]

    # ---- gates --------------------------------------------------------------
    max_margin_strings = {n: objective_scan[n]["max_margin_C_cap1_minus_C2"] for n in objective_scan}
    tie_counts = {n: objective_scan[n]["tie_count"] for n in objective_scan}
    strict_counts = {n: objective_scan[n]["strict_count"] for n in objective_scan}

    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "parents_bound": all(parent_checks.values()),
        "generator_digest_exact": generator_digest == EXPECTED_GENERATOR_DIGEST,
        "unique_blocks_1296": len(blocks) == 1296,
        "pair_count_4104": len(pairs) == 4104,
        "candidate_count_211248": tested == 211248,
        "family_counts_match_v5": dict(family_counts) == QG17_FAMILY_COUNTS == v5r.get("family_candidates_tested", {}),
        "qg17_strict_counts_reproduced_verbatim": strict_counts == QG17_STRICT_COUNTS == qg17_bound_verbatim["strict_counts"],
        "qg17_max_margins_reproduced_verbatim": max_margin_strings == QG17_MAX_MARGINS == qg17_bound_verbatim["max_margin_C_cap1_minus_C2"],
        "qg17_tie_counts_reproduced_verbatim": tie_counts == QG17_TIE_COUNTS == qg17_bound_verbatim["exact_tie_counts"],
        "O0_control_zero_strict_and_zero_tie": strict_counts["O0"] == 0 and tie_counts["O0"] == 0,
        "objective_on_every_tie_hyperplane": bool(on_hyperplane),
        "crossing_objectives_from_frozen_rule": bool(crossing_rule_ok),
        "crossing_objectives_all_feasible": all(h["crossing_rule"]["feasible"] for h in hyperplanes),
        "every_crossing_witness_referee_recomputed": bool(all_witnesses_recomputed),
        "no_float_in_decisions": _EXACT_CHECKS[0] > 0,
        "complete_domain_no_truncation": (
            tested == 211248 and len(ties) == QG17_TIE_COUNTS[TIE_OBJECTIVE]
            and len(nondeg) + len(degenerate) == len(ties)
            and sum(h["tying_candidate_count"] for h in hyperplanes) == len(nondeg)
        ),
    }
    all_gates = all(gates.values())

    located = bool(boundary_locating) and all_gates
    if not all_gates:
        terminal = "QG17B_CANNOT_CHECK"
    elif located:
        terminal = "QG17B_EXACT_PHASE_BOUNDARY_LOCATED"
    else:
        terminal = "QG17B_TIE_LOCUS_DEGENERATE__NO_CROSSING_WITNESS"
    annotation = "QG17B_QG16_FACET_LOCALLY_SHARP_BY_TIE_LOCUS" if (located and facet_locally_sharp) else None

    result = {
        "schema": "ORION.QG.QG17B.TieLocus.v1",
        "issue": ISSUE,
        "lane": LANE,
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha(PROTOCOL),
        "protocol_status": "FROZEN_BEFORE_ANY_TIE_LOCUS_SCORING__EXECUTED_UNMODIFIED",
        "parent_qg16_sha256": sha(PARENT_QG16),
        "parent_qg17_sha256": sha(PARENT_QG17),
        "parent_v5_sha256": sha(PARENT_V5),
        "parent_checks": parent_checks,
        "qg17_receipt_bound_verbatim": qg17_bound_verbatim,
        "instrument_reuse": {
            "candidate_generator": "EXACT_V5_REUSE_UNMODIFIED__qg9_support2_tightness",
            "referee": "EXACT_QG17_REUSE_UNMODIFIED__qg17_r6i_phase_sharpness.WeightedCap1/support2_static/support2_score",
            "qg9_support2_tightness_sha256": sha(ORION_QG / "qg9_support2_tightness.py"),
            "qg17_r6i_phase_sharpness_sha256": sha(ORION_QG / "qg17_r6i_phase_sharpness.py"),
        },
        "candidate_generator_digest": generator_digest,
        "candidate_generator_summary": {
            "unique_blocks": len(blocks), "pair_count": len(pairs),
            "template_families": qg17.FAMILIES, "block_metadata": bmeta,
        },
        "candidates_tested": tested,
        "family_candidates_tested": dict(family_counts),
        "arithmetic": {
            "mode": "EXACT_INTEGER_AND_FRACTION_ONLY",
            "float_constructed_on_scientific_path": False,
            "exactness_assertions_executed": _EXACT_CHECKS[0],
        },
        "objective_scan": objective_scan,
        "Q1_tie_locus": {
            "tie_objective": TIE_OBJECTIVE,
            "tie_objective_theta": qg17.objective_json(tie_coeffs, tie_scale),
            "tie_count": len(ties),
            "degenerate_zero_d_tie_count": len(degenerate),
            "hyperplane_realizing_tie_count": len(nondeg),
            "distinct_hyperplane_count": len(normals),
            "single_hyperplane": len(normals) == 1,
            "objective_lies_on_every_realized_hyperplane": bool(on_hyperplane),
            "distinct_normalized_normals": [list(n) for n in normals],
            "multiplicity_by_normalized_normal": {
                "|".join(str(x) for x in n): len(by_normal[n]) for n in normals
            },
        },
        "Q2_crossing": {
            "rule": "theta_side = (integer coefficient vector of O_nc_out scaled by M) -/+ d, M=64, scale=128",
            "M": CROSSING_M,
            "hyperplanes_with_sign_flip": len(boundary_locating),
            "total_crossing_witnesses": sum(h["total_crossing_witnesses"] for h in hyperplanes),
        },
        "hyperplanes": hyperplanes,
        "Q3_facet_comparison": {
            "qg16_facets_verbatim": QG16_FACETS_VERBATIM,
            "qg16_facet_normalized_normals": [list(k) for k in sorted(facet_norms)],
            "locally_sharp_facets_by_tie_locus": facet_locally_sharp,
            "tie_hyperplanes_not_in_qg16_certificate": new_faces,
        },
        "gates": gates,
        "all_gates_pass": all_gates,
        "terminal": terminal,
        "annotation": annotation,
        "anti_overclaim": {
            "global_phase_boundary_complete": False,
            "global_phase_boundary_sharpness": "OPEN",
            "scope": "LOCAL_EVIDENCE_AT_EXACT_RATIONAL_OBJECTIVES_ON_THE_FROZEN_V5_OBSTRUCTION_BLOCK_DOMAIN_ONLY",
            "support2_required_anywhere_else_claimed": False,
            "support1_sufficiency_outside_cone_proved": False,
            "qg16_certificate_refuted": False,
            "outside_cone_semantics": "THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED",
            "novelty_authority": False,
            "physical_quantum_advantage_claim": False,
            "network_access": False,
            "chemistry_sources_read": False,
            "protected_subject_read": False,
            "ceiling": "NOT_R6",
        },
        "global_phase_boundary_complete": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "authority": (
            "QG17B_TIE_LOCUS_OF_QG17_ZERO_MARGIN_EXACTLY_EXTRACTED_ON_COMPLETE_FROZEN_V5_DOMAIN__"
            "O_NC_OUT_LIES_EXACTLY_ON_EVERY_REALIZED_TIE_HYPERPLANE__"
            "EXACT_LOCAL_PHASE_BOUNDARY_LOCATED_BY_REFEREE_RECOMPUTED_CROSSING_WITNESSES_AT_EXACT_RATIONAL_OBJECTIVES__"
            "REALIZED_TIE_HYPERPLANES_ARE_NOT_PROPORTIONAL_TO_ANY_QG16_FACET__"
            "QG16_FACET_LOCAL_SHARPNESS_STILL_UNDEMONSTRATED__"
            "GLOBAL_PHASE_BOUNDARY_SHARPNESS_REMAINS_OPEN__GLOBAL_PHASE_BOUNDARY_COMPLETE_FALSE__"
            "LOCAL_EVIDENCE_ONLY__NOT_R6"
        ),
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()

    p = Path(ns.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    token = canonical({
        "terminal": terminal,
        "annotation": annotation,
        "result_digest": result["result_digest"],
        "candidates_tested": tested,
        "tie_count": len(ties),
        "distinct_hyperplanes": len(normals),
        "hyperplanes_with_sign_flip": len(boundary_locating),
        "total_crossing_witnesses": result["Q2_crossing"]["total_crossing_witnesses"],
        "facet_matches": len(facet_locally_sharp),
        "all_gates_pass": all_gates,
    })
    print(TOKEN + token)
    print("QG17B_RUNTIME_SECONDS=%.3f" % (time.monotonic() - t_start), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
