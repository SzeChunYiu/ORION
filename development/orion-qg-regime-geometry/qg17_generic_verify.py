#!/usr/bin/env python3
"""Independent generic-ORION verifier for QG-17 selected sharpness witnesses."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import traceback
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg17-r6i-phase-sharpness.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG17_R6I_PHASE_SHARPNESS_PROTOCOL_V1.md"
QG16 = ROOT / "research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json"
V5 = ROOT / "research/extensions/orion-qg/QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg17-generic-verification.json"
TOKEN = "ORIONQG_QG17_GENERIC="


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def K(x):
    return (int(x[0]), int(x[1]))


def mul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def wt(a):
    return (a[0] | a[1]).bit_count()


def symp(a, b):
    return (((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) & 1)


def labels(s0, s1, a, b):
    return 2 * symp(s0, a) + symp(s1, a), 2 * symp(s0, b) + symp(s1, b)


def frame(a, b):
    return a, b, mul(a, b)


def fraction(x):
    return Fraction(int(x["numerator"]), int(x["denominator"]))


def theta(rec):
    return {k: fraction(v) for k, v in rec["theta"].items()}


def support1_pairs():
    keys = [(x, z) for x in range(4) for z in range(4) if (x, z) != (0, 0) and wt((x, z)) <= 1]
    ps = tuple((a, b) for a in keys for b in keys if symp(a, b) == 1)
    if len(ps) != 12:
        raise AssertionError(len(ps))
    return ps


PAIRS = support1_pairs()
KEYS = tuple((x, z) for x in range(4) for z in range(4))
PERMS = tuple(itertools.permutations(range(3)))


def cap1_exact(ta, tb, th):
    best = None
    for i, pa in enumerate(PAIRS):
        rsa = frame(*pa)
        ra = sum(wt(mul(ta[k], rsa[k])) for k in range(3))
        for j, pb in enumerate(PAIRS):
            rsb = frame(*pb)
            rb = min(sum(wt(mul(tb[p[k]], rsb[k])) for k in range(3)) for p in PERMS)
            tag_best = None
            for s0 in KEYS:
                for s1 in KEYS:
                    la = labels(s0, s1, *pa)
                    lb = labels(s0, s1, *pb)
                    if la != lb or la[0] not in (1, 2, 3) or la[1] not in (1, 2, 3) or la[0] == la[1]:
                        continue
                    z = (wt(s0) + wt(s1), s0, s1, la)
                    if tag_best is None or z < tag_best:
                        tag_best = z
            if tag_best is None:
                continue
            cost = th["t_r"] * (ra + rb) + th["t_tag"] * tag_best[0]
            row = (cost, i, j, tag_best[0], ra + rb, tag_best[1], tag_best[2], tag_best[3])
            if best is None or row < best:
                best = row
    if best is None:
        raise AssertionError("no cap1")
    return {"cost": best[0], "resource": (0, 0, best[3], best[4]), "pair_indices": (best[1], best[2]), "S0": best[5], "S1": best[6], "labels": best[7]}


def support2_exact(rec, th):
    ba, bb = rec["block_A"], rec["block_B"]
    A = (K(ba["R0"]), K(ba["R1"]))
    B = (K(bb["R0"]), K(bb["R1"]))
    s0, s1 = K(ba["S0"]), K(ba["S1"])
    if (s0, s1) != (K(bb["S0"]), K(bb["S1"])):
        raise AssertionError("Tag mismatch")
    if symp(*A) != 1 or symp(*B) != 1:
        raise AssertionError("frame acceptance")
    if labels(s0, s1, *A) != tuple(ba["labels"]) or labels(s0, s1, *B) != tuple(bb["labels"]):
        raise AssertionError("label mismatch")
    ta = tuple(K(x) for x in rec["targets_A"])
    tb = tuple(K(x) for x in rec["targets_B"])

    def frame_choice(pair):
        rs = frame(*pair)
        best = None
        for central in range(3):
            uc = wt(rs[central]) - 1
            unc = sum(wt(rs[k]) - 1 for k in range(3) if k != central)
            z = (th["t_c"] * uc + th["t_nc"] * unc, central, uc, unc)
            if best is None or z < best:
                best = z
        return best

    fa, fb = frame_choice(A), frame_choice(B)
    rsa, rsb = frame(*A), frame(*B)
    rest_a = sum(wt(mul(ta[k], rsa[k])) for k in range(3))
    rest_b = min(sum(wt(mul(tb[p[k]], rsb[k])) for k in range(3)) for p in PERMS)
    tag = wt(s0) + wt(s1)
    uc, unc = fa[2] + fb[2], fa[3] + fb[3]
    cost = th["t_c"] * uc + th["t_nc"] * unc + th["t_tag"] * tag + th["t_r"] * (rest_a + rest_b)
    return {"cost": cost, "resource": (uc, unc, tag, rest_a + rest_b), "targets": (ta, tb)}


def norm(v):
    vals = [int(x) for x in v]
    g = 0
    for x in vals:
        g = math.gcd(g, abs(x))
    if g:
        vals = [x // g for x in vals]
    o0 = (2, 4, 2, 1)
    dot = sum(vals[i] * o0[i] for i in range(4))
    if dot < 0 or (dot == 0 and next((x for x in vals if x), 1) < 0):
        vals = [-x for x in vals]
    return tuple(vals)


def qg16_facets():
    return {(0, 2, 0, -5), (1, 1, 0, -5), (0, 2, -2, -2), (1, 1, -2, -2)}


def verify_rec(rec):
    th = theta(rec)
    s2 = support2_exact(rec, th)
    ta, tb = s2["targets"]
    c1 = cap1_exact(ta, tb, th)
    diff = tuple(s2["resource"][k] - c1["resource"][k] for k in range(4))
    stored_diff = tuple(rec["difference_vector_t_c_t_nc_t_tag_t_r"])
    stored_gap = fraction(rec["gap_cap1_minus_support2"])
    return {
        "strict": s2["cost"] < c1["cost"],
        "cost_gap": c1["cost"] - s2["cost"],
        "stored_gap_match": stored_gap == c1["cost"] - s2["cost"],
        "resource_support2_match": tuple(rec["support2"]["resource"]) == s2["resource"],
        "resource_cap1_match": tuple(rec["cap1"]["resource"]) == c1["resource"],
        "difference_match": stored_diff == diff,
        "normalized_match": tuple(rec["normalized_difference_vector"]) == norm(diff),
        "facet_matches_correct": bool(rec["qg16_facet_matches"]) == (norm(diff) in {norm(f) for f in qg16_facets()}),
    }


def main() -> int:
    a = json.loads(RESULT.read_text())
    u = dict(a)
    obs = u.pop("result_digest", None)
    selected = []
    for name in a.get("outside_objectives_with_strict_witness", []):
        st = a["objectives"][name]
        for role in ("first", "max_gap"):
            rec = st.get(role)
            if rec is not None:
                selected.append((name, role, rec))
    ver = []
    all_selected = True
    for name, role, rec in selected:
        try:
            selected_checks = verify_rec(rec)
            ver.append({"objective": name, "role": role, "checks": selected_checks, "exception": None})
            all_selected &= all(bool(v) for k, v in selected_checks.items() if k != "cost_gap") and bool(selected_checks.get("strict"))
        except Exception as exc:  # diagnostic only; never accepted
            ver.append({
                "objective": name,
                "role": role,
                "checks": {},
                "exception": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                },
            })
            all_selected = False

    v5 = json.loads(V5.read_text())
    q16 = json.loads(QG16.read_text())
    positive = a.get("terminal") == "QG17_SUPPORT2_PHASE_WITNESS_FOUND_AT_FROZEN_OUTSIDE_OBJECTIVE"
    checks = {
        "schema": a.get("schema") == "ORION.QG.QG17.R6IPhaseSharpness.v1",
        "result_digest": obs == hashlib.sha256(canonical(u).encode()).hexdigest(),
        "protocol_hash": a.get("protocol_sha256") == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "generator_digest": a.get("candidate_generator_digest") == v5.get("candidate_generator_digest_before_scoring"),
        "candidate_count": a.get("candidates_tested") == 211248,
        "O0_zero_strict": a.get("objectives", {}).get("O0", {}).get("strict_count") == 0,
        "qg16_parent": q16.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED" and q16.get("global_phase_boundary_sharpness") == "OPEN",
        "selected_present_if_positive": (not positive) or bool(selected),
        "selected_witnesses_independent": all_selected,
        "global_boundary_not_complete": a.get("global_phase_boundary_complete") is False,
        "authority_ceiling": a.get("novelty_authority") is False and a.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT_SUPPORT2_PHASE_WITNESS" if positive and all(checks.values()) else ("ACCEPT_BOUNDED_NEGATIVE" if (not positive) and all(checks.values()) else "REJECT")
    out = {
        "schema": "ORION.QG.QG17.GenericVerificationDiagnostic.v1",
        "issue": "SzeChunYiu/ORION#814",
        "decision": decision,
        "checks": checks,
        "all_checks": all(checks.values()),
        "selected_verification": ver,
        "terminal": a.get("terminal"),
        "novelty_authority": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({"decision": decision, "all_checks": out["all_checks"], "exceptions": [{"objective": x["objective"], "role": x["role"], "exception": x["exception"]} for x in ver if x["exception"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
