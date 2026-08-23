#!/usr/bin/env python3
"""Independent generic-ORION verifier for QG-17b — the tie locus.

Re-derives the QG-17b result from primitives and emits an ACCEPT/REJECT token.

Independence discipline (frozen in QG17B_TIE_LOCUS_PROTOCOL_V1.md):
  * this file implements its own phase-free two-qubit Pauli algebra, its own exact
    weighted support-1 optimizer and its own support-2 scorer, from scratch;
  * it MUST NOT import ``qg17b_tie_locus`` or ``qg17_r6i_phase_sharpness``;
  * the only imported instrument is the digest-gated frozen QG-9 V5 candidate
    generator, which owns the domain;
  * every serialized crossing witness is additionally re-checked by a fully naive
    12x12x256 :class:`fractions.Fraction` optimizer with no caching and no envelope,
    so a shared caching bug cannot pass.

All arithmetic is integer / Fraction.  No float is constructed on the scientific path.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time
import traceback
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORION_Q = ROOT / "research/extensions/orion-q"
ORION_QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(ORION_Q))
sys.path.insert(0, str(ORION_QG))

RESULT = ROOT / "research/extensions/orion-qg/QG17B_TIE_LOCUS_RESULTS.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG17B_TIE_LOCUS_PROTOCOL_V1.md"
QG16 = ROOT / "research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json"
QG17 = ROOT / "research/extensions/orion-qg/QG17_R6I_PHASE_SHARPNESS_RESULTS.json"
V5J = ROOT / "research/extensions/orion-qg/QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg17b-generic-verification.json"
TOKEN = "ORIONQG_QG17B_GENERIC="

EXPECTED_GENERATOR_DIGEST = "bb07c127d037f68e2a1f6ca6b5defee0fbadcebdb3ae23aedd4e7266f184a4fa"
CROSSING_M = 64
TIE_OBJECTIVE = "O_nc_out"
SAMPLE_STRIDE = 5003  # deterministic prime stride for the naive cross-implementation check

for _forbidden in ("qg17b_tie_locus", "qg17_r6i_phase_sharpness"):
    if _forbidden in sys.modules:
        raise AssertionError({"verifier_independence_violated": _forbidden})

import qg9_support2_tightness as v5  # noqa: E402  (frozen domain generator only)


# ------------------------------------------------------------------ primitives
def mul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def wt(a):
    return bin(a[0] | a[1]).count("1")


def symp(a, b):
    return (bin(a[0] & b[1]).count("1") + bin(a[1] & b[0]).count("1")) & 1


def labels(s0, s1, r0, r1):
    return (2 * symp(s0, r0) + symp(s1, r0), 2 * symp(s0, r1) + symp(s1, r1))


def frame(a, b):
    return (a, b, mul(a, b))


def K(x):
    return (int(x[0]), int(x[1]))


PERMS = tuple(itertools.permutations(range(3)))
ALL_KEYS = tuple((x, z) for x in range(4) for z in range(4))
S1_KEYS = tuple(k for k in ALL_KEYS if k != (0, 0) and wt(k) <= 1)
PAIRS = tuple((a, b) for a in S1_KEYS for b in S1_KEYS if symp(a, b) == 1)


def build_tag_table():
    table = []
    for pa in PAIRS:
        row = []
        for pb in PAIRS:
            best = None
            for s0 in ALL_KEYS:
                for s1 in ALL_KEYS:
                    la = labels(s0, s1, *pa)
                    if la != labels(s0, s1, *pb):
                        continue
                    if la[0] not in (1, 2, 3) or la[1] not in (1, 2, 3) or la[0] == la[1]:
                        continue
                    cand = (wt(s0) + wt(s1), s0, s1, la)
                    if best is None or cand < best:
                        best = cand
            row.append(best)
        table.append(tuple(row))
    return tuple(table)


TAG = build_tag_table()


# ---------------------------------------------------- exact scoring (own code)
class Referee:
    """Independent exact weighted referee.  Costs are integers at objective scale."""

    def __init__(self):
        self.ra = {}
        self.rb = {}
        self.env = {}

    @staticmethod
    def tk(ts):
        return tuple((int(t[0]), int(t[1])) for t in ts)

    def restore_a(self, ts):
        k = self.tk(ts)
        v = self.ra.get(k)
        if v is None:
            v = tuple(sum(wt(mul(ts[m], frame(*p)[m])) for m in range(3)) for p in PAIRS)
            self.ra[k] = v
        return v

    def restore_b(self, ts):
        k = self.tk(ts)
        v = self.rb.get(k)
        if v is None:
            v = tuple(min(sum(wt(mul(ts[q[m]], frame(*p)[m])) for m in range(3)) for q in PERMS) for p in PAIRS)
            self.rb[k] = v
        return v

    def envelope(self, oname, coeffs, ts):
        """For each A frame pair: cheapest feasible B partner including shared Tag."""
        k = (oname, self.tk(ts))
        v = self.env.get(k)
        if v is None:
            _tnc, _tc, ttag, tr = coeffs
            rb = self.restore_b(ts)
            rows = []
            for i in range(len(PAIRS)):
                best = None
                for j in range(len(PAIRS)):
                    cell = TAG[i][j]
                    if cell is None:
                        continue
                    cand = (tr * rb[j] + ttag * cell[0], j, cell[0], rb[j])
                    if best is None or cand < best:
                        best = cand
                if best is None:
                    raise AssertionError({"no_feasible_partner": i})
                rows.append(best)
            v = tuple(rows)
            self.env[k] = v
        return v

    def cap1(self, oname, coeffs, ta, tb):
        _tnc, _tc, _ttag, tr = coeffs
        ra = self.restore_a(ta)
        env = self.envelope(oname, coeffs, tb)
        best = None
        for i in range(len(PAIRS)):
            cand = (tr * ra[i] + env[i][0], i, env[i][1], ra[i], env[i][3], env[i][2])
            if best is None or cand < best:
                best = cand
        cost, i, j, rA, rB, tag = best
        return int(cost), (0, 0, int(tag), int(rA + rB))

    @staticmethod
    def support2(ba, bb, ta, tb, coeffs):
        tnc, tc, ttag, tr = coeffs
        A = (K(ba["R0"]), K(ba["R1"]))
        B = (K(bb["R0"]), K(bb["R1"]))
        s0, s1 = K(ba["S0"]), K(ba["S1"])
        if (s0, s1) != (K(bb["S0"]), K(bb["S1"])):
            raise AssertionError("shared Tag identity lost")
        if symp(*A) != 1 or symp(*B) != 1:
            raise AssertionError("frame not symplectic")
        if labels(s0, s1, *A) != tuple(ba["labels"]) or labels(s0, s1, *B) != tuple(bb["labels"]):
            raise AssertionError("label drift")

        def choose(pair):
            rs = frame(*pair)
            best = None
            for c in range(3):
                uc = wt(rs[c]) - 1
                unc = sum(wt(rs[m]) - 1 for m in range(3) if m != c)
                cand = (tc * uc + tnc * unc, c, uc, unc)
                if best is None or cand < best:
                    best = cand
            return best

        fa, fb = choose(A), choose(B)
        rsa, rsb = frame(*A), frame(*B)
        rest = sum(wt(mul(ta[m], rsa[m])) for m in range(3))
        rest += min(sum(wt(mul(tb[q[m]], rsb[m])) for m in range(3)) for q in PERMS)
        uc, unc, tag = fa[2] + fb[2], fa[3] + fb[3], wt(s0) + wt(s1)
        cost = tc * uc + tnc * unc + ttag * tag + tr * rest
        return int(cost), (int(uc), int(unc), int(tag), int(rest))


def naive_cap1_fraction(ta, tb, th):
    """Fully naive 12x12x256 Fraction optimizer: no caching, no envelope."""
    best = None
    for i, pa in enumerate(PAIRS):
        rsa = frame(*pa)
        ra = sum(wt(mul(ta[m], rsa[m])) for m in range(3))
        for j, pb in enumerate(PAIRS):
            rsb = frame(*pb)
            rb = min(sum(wt(mul(tb[q[m]], rsb[m])) for m in range(3)) for q in PERMS)
            tag = None
            for s0 in ALL_KEYS:
                for s1 in ALL_KEYS:
                    la = labels(s0, s1, *pa)
                    if la != labels(s0, s1, *pb):
                        continue
                    if la[0] not in (1, 2, 3) or la[1] not in (1, 2, 3) or la[0] == la[1]:
                        continue
                    cand = (wt(s0) + wt(s1), s0, s1)
                    if tag is None or cand < tag:
                        tag = cand
            if tag is None:
                continue
            cost = th["t_r"] * (ra + rb) + th["t_tag"] * tag[0]
            cand = (cost, i, j, tag[0], ra + rb)
            if best is None or cand < best:
                best = cand
    if best is None:
        raise AssertionError("no feasible cap1 configuration")
    return best[0], (0, 0, int(best[3]), int(best[4]))


def naive_support2_fraction(ba, bb, ta, tb, th):
    A = (K(ba["R0"]), K(ba["R1"]))
    B = (K(bb["R0"]), K(bb["R1"]))
    s0, s1 = K(ba["S0"]), K(ba["S1"])
    if symp(*A) != 1 or symp(*B) != 1:
        raise AssertionError("frame not symplectic")
    if labels(s0, s1, *A) != tuple(ba["labels"]) or labels(s0, s1, *B) != tuple(bb["labels"]):
        raise AssertionError("label drift")

    def choose(pair):
        rs = frame(*pair)
        best = None
        for c in range(3):
            uc = wt(rs[c]) - 1
            unc = sum(wt(rs[m]) - 1 for m in range(3) if m != c)
            cand = (th["t_c"] * uc + th["t_nc"] * unc, c, uc, unc)
            if best is None or cand < best:
                best = cand
        return best

    fa, fb = choose(A), choose(B)
    rsa, rsb = frame(*A), frame(*B)
    rest = sum(wt(mul(ta[m], rsa[m])) for m in range(3))
    rest += min(sum(wt(mul(tb[q[m]], rsb[m])) for m in range(3)) for q in PERMS)
    uc, unc, tag = fa[2] + fb[2], fa[3] + fb[3], wt(s0) + wt(s1)
    cost = th["t_c"] * uc + th["t_nc"] * unc + th["t_tag"] * tag + th["t_r"] * rest
    return cost, (int(uc), int(unc), int(tag), int(rest))


# --------------------------------------------------------------------- helpers
def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def norm(v):
    vals = [int(x) for x in v]
    g = 0
    for x in vals:
        g = math.gcd(g, abs(x))
    if g:
        vals = [x // g for x in vals]
    o0 = (2, 4, 2, 1)
    dot = sum(vals[m] * o0[m] for m in range(4))
    if dot < 0 or (dot == 0 and next((x for x in vals if x), 1) < 0):
        vals = [-x for x in vals]
    return tuple(vals)


def frac(rec):
    return Fraction(int(rec["numerator"]), int(rec["denominator"]))


def theta_from_dict(d):
    return {k: frac(v) for k, v in d.items()}


def integer_objective(th):
    """(t_nc,t_c,t_tag,t_r) integer coefficients at a common scale."""
    L = 1
    for k in ("t_nc", "t_c", "t_tag", "t_r"):
        L = L * th[k].denominator // math.gcd(L, th[k].denominator)
    return tuple(int(th[k] * L) for k in ("t_nc", "t_c", "t_tag", "t_r")), int(L)


def dot_d(d, coeffs, scale):
    tnc, tc, ttag, tr = coeffs
    return Fraction(int(d[0]) * tc + int(d[1]) * tnc + int(d[2]) * ttag + int(d[3]) * tr, int(scale))


def frac_str(f):
    return str(int(f)) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def main() -> int:
    t0 = time.monotonic()
    notes = []
    a = json.loads(RESULT.read_text())
    u = dict(a)
    observed_digest = u.pop("result_digest", None)
    qg16 = json.loads(QG16.read_text())
    qg17 = json.loads(QG17.read_text())
    v5r = json.loads(V5J.read_text())

    # ---- objectives taken from the PROTECTED QG-17 receipt, not from the analyzer
    objectives = []
    for o in qg17["objectives"]:
        th = theta_from_dict(o["theta_exact"])
        coeffs, scale = integer_objective(th)
        objectives.append((o["name"], coeffs, scale, th))
    obj_names = [o[0] for o in objectives]

    # ---- domain, digest-gated
    blocks, bmeta = v5.obstruction_blocks()
    pairs = v5.candidate_pairs(blocks)
    families = ["IDENTITY_RESTORE", "ONE_DEFECT_A", "ONE_DEFECT_B", "MATCHED_DEFECT"]
    gdigest = hashlib.sha256(canonical({
        "blocks": blocks, "block_metadata": bmeta, "pair_count": len(pairs),
        "pairs": pairs, "template_families": families,
    }).encode()).hexdigest()

    ref = Referee()
    strict = {n: 0 for n in obj_names}
    tiec = {n: 0 for n in obj_names}
    maxm = {n: None for n in obj_names}
    ties = {}
    tested = 0
    family_counts = defaultdict(int)
    sample_rows = []

    for family in families:
        for i, j, kind in pairs:
            for ta, tb, tmeta in v5.template_instances(blocks[i], blocks[j], family):
                tested += 1
                family_counts[family] += 1
                for name, coeffs, scale, th in objectives:
                    c2, r2 = ref.support2(blocks[i], blocks[j], ta, tb, coeffs)
                    c1, r1 = ref.cap1(name, coeffs, ta, tb)
                    m = c1 - c2
                    if maxm[name] is None or m > maxm[name]:
                        maxm[name] = m
                    if c2 < c1:
                        strict[name] += 1
                    elif c2 == c1:
                        tiec[name] += 1
                        if name == TIE_OBJECTIVE:
                            ties[tested] = {
                                "ij": (i, j), "ta": ta, "tb": tb, "family": family, "kind": kind,
                                "template": tmeta, "r2": r2, "r1": r1,
                                "d": tuple(r2[m2] - r1[m2] for m2 in range(4)),
                            }
                if tested % SAMPLE_STRIDE == 0 and len(sample_rows) < 40:
                    name, coeffs, scale, th = objectives[-1]
                    nc, nr = naive_cap1_fraction(ta, tb, th)
                    fc, fr = ref.cap1(name, coeffs, ta, tb)
                    ns, nsr = naive_support2_fraction(blocks[i], blocks[j], ta, tb, th)
                    fs, fsr = ref.support2(blocks[i], blocks[j], ta, tb, coeffs)
                    sample_rows.append({
                        "candidate_index": tested,
                        "cap1_match": nc == Fraction(fc, scale) and nr == fr,
                        "support2_match": ns == Fraction(fs, scale) and nsr == fsr,
                    })

    max_margin_strings = {}
    for name, coeffs, scale, th in objectives:
        max_margin_strings[name] = frac_str(Fraction(maxm[name], scale))

    # ---- independent hyperplane extraction
    by_normal = defaultdict(list)
    raw_by_normal = defaultdict(lambda: defaultdict(int))
    degenerate = 0
    on_hyperplane = True
    tie_coeffs = tie_scale = None
    for name, coeffs, scale, th in objectives:
        if name == TIE_OBJECTIVE:
            tie_coeffs, tie_scale = coeffs, scale
    for idx in sorted(ties):
        d = ties[idx]["d"]
        if all(x == 0 for x in d):
            degenerate += 1
            continue
        if dot_d(d, tie_coeffs, tie_scale) != 0:
            on_hyperplane = False
        nd = norm(d)
        by_normal[nd].append(idx)
        raw_by_normal[nd][tuple(d)] += 1
    normals = sorted(by_normal)

    # ---- independent crossing re-evaluation
    committed = {tuple(h["normalized_normal_t_c_t_nc_t_tag_t_r"]): h for h in a["hyperplanes"]}
    crossing_rows = []
    crossing_all_ok = True
    witness_rows = []
    witness_all_ok = True

    for nd in normals:
        base = tuple(c * CROSSING_M for c in tie_coeffs)
        bscale = tie_scale * CROSSING_M
        dcv = (nd[1], nd[0], nd[2], nd[3])  # d-order -> (t_nc,t_c,t_tag,t_r)
        sides = {"MINUS": tuple(base[m] - dcv[m] for m in range(4)),
                 "PLUS": tuple(base[m] + dcv[m] for m in range(4))}
        hrec = committed.get(nd)
        row = {"normal": list(nd), "multiplicity": len(by_normal[nd]),
               "committed_present": hrec is not None, "sides": {}}
        if hrec is None:
            crossing_all_ok = False
            crossing_rows.append(row)
            continue
        row["multiplicity_match"] = hrec["tying_candidate_count"] == len(by_normal[nd])
        row["raw_d_match"] = (
            [{"d": list(dv), "multiplicity": raw_by_normal[nd][dv]} for dv in sorted(raw_by_normal[nd])]
            == hrec["raw_difference_vectors"]
        )
        crossing_all_ok &= bool(row["multiplicity_match"] and row["raw_d_match"])
        for side, coeffs in sides.items():
            sd = hrec["sides"][side]
            oname = f"VER__{'-'.join(str(x) for x in nd)}__{side}"
            found = []
            for idx in by_normal[nd]:
                t = ties[idx]
                c2, _r2 = ref.support2(blocks[t["ij"][0]], blocks[t["ij"][1]], t["ta"], t["tb"], coeffs)
                c1, _r1 = ref.cap1(oname, coeffs, t["ta"], t["tb"])
                if c2 < c1:
                    found.append(idx)
            ok_theta = (tuple(sd["theta_integer_coeffs_t_nc_t_c_t_tag_t_r"]) == coeffs
                        and int(sd["theta_scale"]) == bscale)
            ok_list = found == list(sd["crossing_witness_candidate_indices"])
            ok_count = len(found) == sd["crossing_witness_count"]
            ok_flip = bool(found) == bool(sd["sign_flipped"])
            ok_sign = dot_d(nd, coeffs, bscale).numerator * (1 if side == "PLUS" else -1) > 0
            row["sides"][side] = {
                "theta_rule_match": bool(ok_theta), "witness_list_match": bool(ok_list),
                "witness_count_match": bool(ok_count), "flip_flag_match": bool(ok_flip),
                "straddle_sign_correct": bool(ok_sign),
                "independent_witness_count": len(found),
            }
            crossing_all_ok &= bool(ok_theta and ok_list and ok_count and ok_flip and ok_sign)

            # ---- naive Fraction re-check of every serialized witness
            for role in ("first_crossing_witness", "max_gap_crossing_witness"):
                w = sd.get(role)
                if w is None:
                    continue
                try:
                    th = theta_from_dict(w["theta"])
                    icoef, iscale = integer_objective(th)
                    idx = int(w["candidate_index"])
                    t = ties.get(idx)
                    regen_ok = (
                        t is not None
                        and list(t["ij"]) == list(w["block_indices"])
                        and [list(map(int, x)) for x in t["ta"]] == [list(map(int, x)) for x in w["targets_A"]]
                        and [list(map(int, x)) for x in t["tb"]] == [list(map(int, x)) for x in w["targets_B"]]
                        and t["family"] == w["family"] and t["kind"] == w["pair_kind"]
                        and list(t["r2"]) == list(w["tie_resource_r2_at_O_nc_out"])
                        and list(t["r1"]) == list(w["tie_resource_r1_at_O_nc_out"])
                        and list(t["d"]) == list(w["difference_vector_d_t_c_t_nc_t_tag_t_r"])
                    )
                    ba = blocks[w["block_indices"][0]]
                    bb = blocks[w["block_indices"][1]]
                    ta = tuple(K(x) for x in w["targets_A"])
                    tb = tuple(K(x) for x in w["targets_B"])
                    n2, nr2 = naive_support2_fraction(ba, bb, ta, tb, th)
                    n1, nr1 = naive_cap1_fraction(ta, tb, th)
                    checks = {
                        "candidate_regenerated_from_frozen_generator": bool(regen_ok),
                        "block_records_match": ba == w["block_A"] and bb == w["block_B"],
                        "theta_matches_frozen_crossing_rule": tuple(icoef) == tuple(coeffs) and iscale == bscale,
                        "C2_match": n2 == frac(w["support2_at_theta"]["C2_exact"]),
                        "C_cap1_match": n1 == frac(w["cap1_at_theta"]["C_cap1_exact"]),
                        "support2_resource_match": list(nr2) == list(w["support2_at_theta"]["resource"]),
                        "cap1_resource_match": list(nr1) == list(w["cap1_at_theta"]["resource"]),
                        "gap_match": (n1 - n2) == frac(w["gap_exact"]),
                        "strict_support2_win": n2 < n1,
                        "normal_match": norm([nr2[m] - nr1[m] for m in range(4)]) != () and tuple(w["normalized_normal"]) == nd,
                        "on_tie_hyperplane_at_O_nc_out": dot_d(w["difference_vector_d_t_c_t_nc_t_tag_t_r"], tie_coeffs, tie_scale) == 0,
                    }
                    witness_rows.append({"normal": list(nd), "side": side, "role": role,
                                         "candidate_index": w["candidate_index"],
                                         "checks": checks, "exception": None})
                    witness_all_ok &= all(bool(x) for x in checks.values())
                except Exception as exc:  # diagnostic only; never accepted
                    witness_rows.append({"normal": list(nd), "side": side, "role": role,
                                         "candidate_index": w.get("candidate_index"),
                                         "checks": {},
                                         "exception": {"type": type(exc).__name__, "message": str(exc),
                                                       "traceback": traceback.format_exc()}})
                    witness_all_ok = False
        crossing_rows.append(row)

    # ---- facet comparison, re-derived
    facet_vectors = {0: (0, 2, 0, -5), 1: (1, 1, 0, -5), 2: (0, 2, -2, -2), 3: (1, 1, -2, -2)}
    facet_norms = {norm(v): k for k, v in facet_vectors.items()}
    facet_ok = True
    for h in a["hyperplanes"]:
        nd = tuple(h["normalized_normal_t_c_t_nc_t_tag_t_r"])
        expect = facet_norms.get(nd)
        got = h["qg16_facet_comparison"]["matched_facet_index"]
        cls = h["qg16_facet_comparison"]["classification"]
        if got != expect:
            facet_ok = False
        if (cls == "QG16_FACET_EXACT_PROPORTIONAL") != (expect is not None):
            facet_ok = False

    located = [h for h in a["hyperplanes"] if h["sign_flip_on_crossing"]]
    sharp_facets = [h for h in located if h["qg16_facet_comparison"]["matched_facet_index"] is not None]
    expected_terminal = ("QG17B_EXACT_PHASE_BOUNDARY_LOCATED" if located
                         else "QG17B_TIE_LOCUS_DEGENERATE__NO_CROSSING_WITNESS")
    expected_annotation = "QG17B_QG16_FACET_LOCALLY_SHARP_BY_TIE_LOCUS" if (located and sharp_facets) else None
    anti = a.get("anti_overclaim", {})

    checks = {
        "schema": a.get("schema") == "ORION.QG.QG17B.TieLocus.v1",
        "result_digest": observed_digest == hashlib.sha256(canonical(u).encode()).hexdigest(),
        "protocol_hash": a.get("protocol_sha256") == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "generator_digest": gdigest == EXPECTED_GENERATOR_DIGEST == a.get("candidate_generator_digest")
                            == v5r.get("candidate_generator_digest_before_scoring"),
        "domain_sizes": len(blocks) == 1296 and len(pairs) == 4104 and tested == 211248
                        and a.get("candidates_tested") == 211248,
        "family_counts": dict(family_counts) == a.get("family_candidates_tested")
                         == v5r.get("family_candidates_tested"),
        "qg17_strict_counts_reproduced": (strict == {n: 0 for n in obj_names}
                                          and all(a["objective_scan"][n]["strict_count"] == 0 for n in obj_names)),
        "qg17_tie_counts_reproduced": (tiec == {"O0": 0, "O_tag_out": 0, "O_restore_out": 0, "O_nc_out": 4896}
                                       and tiec == {n: a["objective_scan"][n]["tie_count"] for n in obj_names}
                                       and tiec == qg17["post_hoc_diagnostic_not_protocol_frozen"]["exact_tie_counts_C2_equals_C_cap1"]),
        "qg17_max_margins_reproduced": (max_margin_strings
                                        == {n: a["objective_scan"][n]["max_margin_C_cap1_minus_C2"] for n in obj_names}
                                        == qg17["post_hoc_diagnostic_not_protocol_frozen"]["max_margin_C_cap1_minus_C2_over_full_domain"]),
        "O0_control_zero_strict_and_zero_tie": strict["O0"] == 0 and tiec["O0"] == 0,
        "tie_locus_matches": (len(ties) == a["Q1_tie_locus"]["tie_count"]
                              and degenerate == a["Q1_tie_locus"]["degenerate_zero_d_tie_count"]
                              and [list(n) for n in normals] == a["Q1_tie_locus"]["distinct_normalized_normals"]
                              and {"|".join(str(x) for x in n): len(by_normal[n]) for n in normals}
                              == a["Q1_tie_locus"]["multiplicity_by_normalized_normal"]),
        "objective_on_every_tie_hyperplane": on_hyperplane and a["Q1_tie_locus"]["objective_lies_on_every_realized_hyperplane"] is True,
        "crossing_independently_reproduced": bool(crossing_all_ok),
        "every_serialized_witness_reverified_naively": bool(witness_all_ok) and bool(witness_rows) == bool(located),
        "naive_cross_implementation_sample": bool(sample_rows) and all(r["cap1_match"] and r["support2_match"] for r in sample_rows),
        "facet_comparison_reproduced": bool(facet_ok),
        "terminal_consistent": a.get("terminal") == expected_terminal and a.get("annotation") == expected_annotation,
        "gates_all_pass": a.get("all_gates_pass") is True and all(bool(x) for x in a.get("gates", {}).values()),
        "global_boundary_not_complete": a.get("global_phase_boundary_complete") is False
                                        and anti.get("global_phase_boundary_complete") is False
                                        and anti.get("global_phase_boundary_sharpness") == "OPEN",
        "authority_ceiling": (a.get("novelty_authority") is False and a.get("physical_quantum_advantage_claim") is False
                              and anti.get("ceiling") == "NOT_R6"
                              and anti.get("support2_required_anywhere_else_claimed") is False
                              and anti.get("support1_sufficiency_outside_cone_proved") is False),
        "qg16_parent_open": (qg16.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED"
                             and qg16.get("global_phase_boundary_sharpness") == "OPEN"),
        "qg17_parent_negative": qg17.get("terminal") == "QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN",
        "verifier_independent_of_analyzer": ("qg17b_tie_locus" not in sys.modules
                                             and "qg17_r6i_phase_sharpness" not in sys.modules),
    }
    all_ok = all(bool(v) for v in checks.values())
    positive = a.get("terminal") == "QG17B_EXACT_PHASE_BOUNDARY_LOCATED"
    decision = ("ACCEPT_EXACT_PHASE_BOUNDARY" if (all_ok and positive)
                else ("ACCEPT_TIE_LOCUS_NEGATIVE" if all_ok else "REJECT"))

    out = {
        "schema": "ORION.QG.QG17B.GenericVerificationDiagnostic.v1",
        "issue": "SzeChunYiu/ORION#814",
        "lane": "QG-17b — the tie locus",
        "decision": decision,
        "all_checks": all_ok,
        "checks": checks,
        "independent_scan": {
            "candidates_tested": tested,
            "strict_counts": strict,
            "tie_counts": tiec,
            "max_margins": max_margin_strings,
            "distinct_normalized_normals": [list(n) for n in normals],
            "multiplicities": {"|".join(str(x) for x in n): len(by_normal[n]) for n in normals},
            "degenerate_zero_d_ties": degenerate,
        },
        "crossing_verification": crossing_rows,
        "witness_verification": witness_rows,
        "naive_cross_implementation_sample": sample_rows,
        "terminal": a.get("terminal"),
        "annotation": a.get("annotation"),
        "notes": notes,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({
        "decision": decision,
        "all_checks": all_ok,
        "failed": sorted(k for k, v in checks.items() if not v),
        "terminal": a.get("terminal"),
        "distinct_hyperplanes": len(normals),
        "independent_tie_count": len(ties),
        "witnesses_reverified": len(witness_rows),
        "exceptions": [w["role"] for w in witness_rows if w["exception"]],
    }))
    print("QG17B_VERIFIER_RUNTIME_SECONDS=%.3f" % (time.monotonic() - t0), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
