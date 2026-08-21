#!/usr/bin/env python3
"""Independent generic verifier for ORION-QG QG-7d (the last link).

Pure-primitive rebuild.  This file imports NOTHING from the analyzer lanes:
no `qg7c_classification`, no `max_r6*`, no `qg5b/qg7b`.  The Pauli algebra is
rebuilt from (x, z) bit pairs, the F3 objective from its definition, the frame
charge from the central-optimal multiplier pair, and the whole geometry
inventory from the frozen protocol's role table.  The P1 domination lemma is
re-derived with a deliberately different traversal (grouped by the frame
pattern at the SECOND comm-s2 qubit, with the coverage bitset transposed), so
an implementation bug in the lane script cannot reproduce itself here.

Checks (all read-only; this verifier never writes the receipt):
  V1  primitives: multiplication / symplectic form / weight / F3 / frame charge
  V2  mirror identity on the complete 4^6 x 4^6 domain
  V3  letter-permutation gauge on the complete domain, all 6 permutations
  V4  geometry inventory rebuilt independently (roles, unordered pairs)
  V5  P1 re-derived for EVERY geometry; residue counts and residue rows must
      match the receipt exactly, and every residue row must be re-confirmed as
      a genuine failure by direct evaluation of the whole menu at that state
  V6  census dispatch arithmetic against the committed QG-7c census
  V7  hostile-arm bookkeeping (referee coverage, sandwich, gap rows)
  V8  terminal selection re-derived from the receipt's own values
  V9  result digest recomputed from the receipt minus timing

Prints ACCEPT or REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

RESULTS = (Path(__file__).resolve().parents[2] / "research" / "extensions"
           / "orion-qg" / "QG7D_LAST_LINK_RESULTS.json")
QG7C_RESULTS = (Path(__file__).resolve().parents[2] / "research" / "extensions"
                / "orion-qg" / "QG7C_CLASSIFICATION_RESULTS.json")
PROTOCOL = Path(__file__).resolve().parent / "QG7D_LAST_LINK_PROTOCOL_V1.md"

COMMITTED_CENSUS = {
    "PA_ja0_delta1": 97072, "PA_ja0_delta2": 2376, "PA_ja1_delta1": 3600,
    "PP_ja0_delta1": 30500, "PP_ja0_delta2": 440, "PP_ja1_delta1": 1616,
}

# ---- V1: primitives rebuilt from (x, z) bits --------------------------------
# letter codes on the wire: 0 = I, 1 = X, 2 = Y, 3 = Z
BITS = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
CODE = {v: k for k, v in BITS.items()}


def mul(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return CODE[(ax ^ bx, az ^ bz)]


def sy(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return (ax * bz + az * bx) & 1


def wt(a: int) -> int:
    return 0 if a == 0 else 1


def f3(a: int, b: int, c: int) -> int:
    if a == b == c and a != 0:
        return 1
    return wt(a) + wt(b) + wt(c)


def charge(w0: int, w1: int) -> int:
    """Central-optimal frame charge, normalised so that (1,1) costs 0."""
    return min(2 * w0 + 4 * w1, 4 * w0 + 2 * w1) - 6


MUL = np.array([[mul(a, b) for b in range(4)] for a in range(4)],
               dtype=np.int64)
IDX = np.arange(4096, dtype=np.int64)
DIG = [(IDX >> (2 * (5 - k))) & 3 for k in range(6)]
F3T = np.array([[[f3(a, b, c) for c in range(4)] for b in range(4)]
                for a in range(4)], dtype=np.int8)
GTAB = (F3T[DIG[0], DIG[2], DIG[4]] + F3T[DIG[1], DIG[3], DIG[5]]).astype(
    np.int8)
SWAP = np.zeros(4096, dtype=np.int64)
for _k, _src in enumerate((1, 0, 3, 2, 5, 4)):
    SWAP |= DIG[_src] << (2 * (5 - _k))
FP = np.empty((4096, 4096), dtype=np.int8)
for _fl in range(4096):
    _fd = [(_fl >> (2 * (5 - _k))) & 3 for _k in range(6)]
    _p = np.zeros(4096, dtype=np.int64)
    for _k in range(6):
        _p |= MUL[DIG[_k], _fd[_k]] << (2 * (5 - _k))
    FP[_fl] = GTAB[_p]


def enc(letters) -> int:
    return sum(int(letters[k]) << (2 * (5 - k)) for k in range(6))


def v1_primitives() -> list[str]:
    bad = []
    for a in range(4):
        for b in range(4):
            if mul(a, b) != mul(b, a) or mul(a, mul(a, b)) != b:
                bad.append(f"mul({a},{b})")
            if sy(a, b) != (1 if (a and b and a != b) else 0):
                bad.append(f"sy({a},{b})")
    if charge(1, 1) != 0 or charge(2, 1) != 2 or charge(1, 2) != 2 \
            or charge(2, 2) != 6:
        bad.append("charge")
    if f3(1, 1, 1) != 1 or f3(1, 2, 1) != 3 or f3(0, 0, 0) != 0:
        bad.append("f3")
    for fl in (0, 7, 1365, 4095):
        for st in (0, 42, 4095):
            fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
            sd = [(st >> (2 * (5 - k))) & 3 for k in range(6)]
            o = [mul(sd[k], fd[k]) for k in range(6)]
            if int(FP[fl, st]) != f3(o[0], o[2], o[4]) + f3(o[1], o[3], o[5]):
                bad.append(f"FP[{fl},{st}]")
    return bad


# ---- V2 / V3 gauge checks ---------------------------------------------------

def v2_mirror() -> int:
    bad = 0
    for fl in range(4096):
        fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
        flm = enc([fd[1], fd[0], fd[3], fd[2], fd[5], fd[4]])
        if not np.array_equal(FP[flm][SWAP], FP[fl]):
            bad += 1
    return bad


def v3_gauge() -> int:
    bad = 0
    for perm in itertools.permutations((1, 2, 3)):
        tab = np.array([0, perm[0], perm[1], perm[2]], dtype=np.int64)
        pst = np.zeros(4096, dtype=np.int64)
        for k in range(6):
            pst |= tab[DIG[k]] << (2 * (5 - k))
        for fl in range(4096):
            fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
            flp = enc([int(tab[v]) for v in fd])
            if not np.array_equal(FP[flp][pst], FP[fl]):
                bad += 1
    return bad


# ---- V4: geometry inventory rebuilt independently ---------------------------

def other(*ex):
    return [c for c in (1, 2, 3) if c not in ex][0]


def roles():
    out = []

    def add(name, loc, ext, cs2):
        out.append({"name": name, "loc": tuple(loc), "ext": tuple(ext),
                    "cs2": bool(cs2)})
    add("OUT_ANCH", (0, 0, 0, 0), (1, 1, 0, 1, 1), False)
    add("OUT_PHANTOM", (0, 0, 0, 0), (1, 2, 0, 1, 1), False)
    add("OUT_COMMS2", (0, 0, 0, 0), (2, 1, 0, 1, 1), True)
    for p in (1, 2):
        add("ANCH_B_%d" % p, (3, p, 0, 0), (0, 0, 0, 0, 0), False)
        add("ANCH_A_%d" % p, (0, 0, 3, p), (0, 0, 0, 0, 0), False)
        add("BORROW_B_%d" % p, (0, p, 0, 0), (1, 1, 0, 0, 1), False)
        add("BORROW_A_%d" % p, (0, 0, 0, p), (1, 1, 0, 0, 1), False)
        add("CS2_B_ANTIOUT_%d" % p, (p, 0, 0, 0), (1, 1, 1, 1, 1), True)
        add("CS2_B_ANTIB_%d" % p, (p, other(3, p), 0, 0), (1, 0, 1, 0, 0), True)
        add("CS2_A_ANTIOUT_%d" % p, (0, 0, p, 0), (1, 1, 1, 1, 1), True)
        add("CS2_A_ANTIA_%d" % p, (0, 0, p, other(3, p)), (1, 0, 1, 0, 0), True)
    for u in (1, 2):
        for v in (1, 2):
            add("CS2_BA_ANTIA_%d%d" % (u, v), (u, 0, v, other(3, v)),
                (0, 0, 0, 0, 0), True)
            add("CS2_BA_ANTIB_%d%d" % (u, v), (u, other(3, u), v, 0),
                (0, 0, 0, 0, 0), True)
    return out


OURS = {"name": "COMMS2_OURS", "loc": (1, 0, 1, 2), "ext": (0, 0, 0, 0, 0),
        "cs2": True}


def feasible_block(loc, ext, sb, sa, orient, allow_cs2):
    """All local (b, a) letter assignments this block may take under sigma'."""
    w0e, w1e, s0e, s1e, xe = ext
    res = []
    for l0b in range(4):
        for l1b in range(4):
            for l0a in range(4):
                for l1a in range(4):
                    w0 = wt(l0b) + wt(l0a) + w0e
                    w1 = wt(l1b) + wt(l1a) + w1e
                    if w0 < 1 or w1 < 1 or w0 > 2 or w1 > 2:
                        continue
                    if (sy(sb, l0b) + sy(sa, l0a) + s0e) % 2 != orient[0]:
                        continue
                    if (sy(sb, l1b) + sy(sa, l1a) + s1e) % 2 != orient[1]:
                        continue
                    if (sy(l0b, l1b) + sy(l0a, l1a) + xe) % 2 != 1:
                        continue
                    if not allow_cs2:
                        if orient[0] == 0:
                            fr, fw, ow, es, ew = (l0b, l0a), w0, w1, s0e, w0e
                        else:
                            fr, fw, ow, es, ew = (l1b, l1a), w1, w0, s1e, w1e
                        if fw == 2 and ow == 1 and es == ew and all(
                                sy((sb, sa)[q], fr[q]) == 1
                                for q in range(2) if fr[q]):
                            continue
                    res.append((l0b * 4 + l1b, l0a * 4 + l1a,
                                charge(w0, w1)))
    return res


def geometry_tables(r1, r2):
    bl = [OURS, r1, r2]
    xb = enc([b["loc"][k] for b in bl for k in (0, 1)])
    xa = enc([b["loc"][k] for b in bl for k in (2, 3)])
    base = 4
    for b in bl:
        l0b, l1b, l0a, l1a = b["loc"]
        base += charge(wt(l0b) + wt(l0a) + b["ext"][0],
                       wt(l1b) + wt(l1a) + b["ext"][1])
    return bl, FP[xb].astype(np.int16), FP[xa].astype(np.int16), base


def mirrored(b):
    l0b, l1b, l0a, l1a = b["loc"]
    w0, w1, s0, s1, xe = b["ext"]
    return {"name": b["name"], "loc": (l1b, l0b, l1a, l0a),
            "ext": (w1, w0, s1, s0, xe), "cs2": b["cs2"]}


def menu_streams(bl):
    """(frame pattern at b, frame pattern at a, cost) for the whole menu."""
    out = []
    for branch in (0, 1):
        blocks = bl if branch == 0 else [mirrored(b) for b in bl]
        for orient in ((0, 1), (1, 0)):
            best = {}
            for sb in range(4):
                for sa in range(4):
                    opts = [feasible_block(b["loc"], b["ext"], sb, sa, orient,
                                           b["cs2"] and jj > 0)
                            for jj, b in enumerate(blocks)]
                    if any(not o for o in opts):
                        continue
                    tagw = 2 * (wt(sb) + wt(sa))
                    for o0 in opts[0]:
                        for o1 in opts[1]:
                            for o2 in opts[2]:
                                fb = o0[0] * 256 + o1[0] * 16 + o2[0]
                                fa = o0[1] * 256 + o1[1] * 16 + o2[1]
                                c = o0[2] + o1[2] + o2[2] + tagw
                                k = (fb, fa)
                                if k not in best or c < best[k]:
                                    best[k] = c
            out.append((branch, best))
    return out


def p1_residue(r1, r2):
    """Independent re-derivation, grouped by the frame pattern at qubit a."""
    bl, XB, XA, baseX = geometry_tables(r1, r2)
    groups = []
    for branch, best in menu_streams(bl):
        bya = {}
        for (fb, fa), c in best.items():
            cur = bya.setdefault(fa, {})
            if fb not in cur or c < cur[fb]:
                cur[fb] = c
        for fa, parts in bya.items():
            groups.append((branch, fa, parts))
    covered_t = np.zeros((4096, 512), dtype=np.uint8)   # [s_a][bits over s_b]
    sparse = None
    for pos, (branch, fa, parts) in enumerate(groups):
        fbs = np.fromiter(parts.keys(), dtype=np.int64, count=len(parts))
        cs = np.fromiter(parts.values(), dtype=np.int16, count=len(parts))
        W = (FP[fbs].astype(np.int16) + cs[:, None]).min(axis=0)
        if branch == 0:
            gamma = FP[fa].astype(np.int16) - XA
            delta = XB - W + baseX
        else:
            gamma = FP[fa][SWAP].astype(np.int16) - XA
            delta = XB - W[SWAP] + baseX
        lo, hi = int(gamma.min()), int(gamma.max())
        masks = np.zeros((hi - lo + 1, 512), dtype=np.uint8)
        for v in range(lo, hi + 1):
            masks[v - lo] = np.packbits(delta >= v)
        covered_t |= masks[gamma - lo]
        if (pos + 1) % 128 == 0:
            cnt = int(4096 * 4096
                      - int(np.unpackbits(covered_t.reshape(-1)).sum()))
            if cnt == 0:
                break
            if cnt <= 50000:
                rows = np.argwhere(np.unpackbits(covered_t, axis=1) == 0)
                sa_l = rows[:, 0].astype(np.int64)
                sb_l = rows[:, 1].astype(np.int64)
                for branch2, fa2, parts2 in groups[pos + 1:]:
                    if sb_l.size == 0:
                        break
                    fbs = np.fromiter(parts2.keys(), dtype=np.int64,
                                      count=len(parts2))
                    cs = np.fromiter(parts2.values(), dtype=np.int16,
                                     count=len(parts2))
                    W = (FP[fbs].astype(np.int16) + cs[:, None]).min(axis=0)
                    if branch2 == 0:
                        g2 = FP[fa2].astype(np.int16) - XA
                        d2 = XB - W + baseX
                    else:
                        g2 = FP[fa2][SWAP].astype(np.int16) - XA
                        d2 = XB - W[SWAP] + baseX
                    alive = g2[sa_l] > d2[sb_l]
                    sa_l, sb_l = sa_l[alive], sb_l[alive]
                sparse = (sb_l, sa_l)
                break
    if sparse is None:
        rows = np.argwhere(np.unpackbits(covered_t, axis=1) == 0)
        sparse = (rows[:, 1].astype(np.int64), rows[:, 0].astype(np.int64))
    return sorted((int(b), int(a)) for b, a in zip(*sparse))


def direct_delta(r1, r2, sb_state, sa_state):
    """Brute-force minimum Delta at one state -- no grouping, no bitsets."""
    bl, XB, XA, baseX = geometry_tables(r1, r2)
    xcost = int(XB[sb_state]) + int(XA[sa_state]) + baseX
    best = 10 ** 6
    for branch, menu in menu_streams(bl):
        for (fb, fa), c in menu.items():
            if branch == 0:
                v = int(FP[fb][sb_state]) + int(FP[fa][sa_state]) + c
            else:
                v = int(FP[fb][SWAP[sb_state]]) \
                    + int(FP[fa][SWAP[sa_state]]) + c
            best = min(best, v)
    return best - xcost


# ---- main -------------------------------------------------------------------

def main() -> int:
    rec = json.loads(RESULTS.read_text())
    qg7c = json.loads(QG7C_RESULTS.read_text())
    checks: list[tuple[str, bool, str]] = []

    bad = v1_primitives()
    checks.append(("V1 primitives", not bad, str(bad[:4])))

    mirror_bad = v2_mirror()
    checks.append(("V2 mirror identity (16,777,216 cases)", mirror_bad == 0,
                   f"failures={mirror_bad}; receipt="
                   f"{rec['g2_mirror_identity']['f3_exchange_failures']}"))
    gauge_bad = v3_gauge()
    checks.append(("V3 letter-permutation gauge (6 x 16,777,216)",
                   gauge_bad == 0,
                   f"failures={gauge_bad}; receipt="
                   f"{rec['g3_gauge_permutations']['failures']}"))

    R = roles()
    names = [r["name"] for r in R]
    pairs = list(itertools.combinations_with_replacement(range(len(R)), 2))
    p1 = rec["p1_domination_lemma"]
    checks.append(("V4 geometry inventory",
                   names == p1["roles"] and len(pairs) == p1["geometry_count"]
                   and p1["state_domain_per_geometry"] == 4096 * 4096
                   and p1["total_states"] == len(pairs) * 4096 * 4096,
                   f"roles={len(R)} geometries={len(pairs)}"))

    by_name = {r["name"]: r for r in R}
    residue_ok = True
    detail = []
    residue_total = 0
    for g in p1["per_geometry"]:
        n1, n2 = g["geometry"]
        got = p1_residue(by_name[n1], by_name[n2])
        residue_total += len(got)
        if len(got) != g["residue"]:
            residue_ok = False
            detail.append(f"{n1}+{n2}: verifier {len(got)} receipt "
                          f"{g['residue']}")
            continue
        if got:
            claimed = sorted((r["state_b"], r["state_a"])
                             for r in g["residue_rows_verbatim"])
            if claimed != got:
                residue_ok = False
                detail.append(f"{n1}+{n2}: residue rows differ")
                continue
            for sb_state, sa_state in got:
                if direct_delta(by_name[n1], by_name[n2],
                                sb_state, sa_state) <= 0:
                    residue_ok = False
                    detail.append(f"{n1}+{n2}: ({sb_state},{sa_state}) is not "
                                  "a genuine failure")
    checks.append(("V5 P1 re-derived for every geometry",
                   residue_ok and residue_total == p1["residue_total"],
                   f"verifier residue={residue_total} receipt="
                   f"{p1['residue_total']}; {detail[:3]}"))

    ps = rec["p2_state_level_dispatch"]
    census_ok = (ps["derived_census"] == COMMITTED_CENSUS
                 == qg7c["t4b_pinned"]["failing_census"]
                 and ps["derived_failures_total"] == 135604
                 == int(qg7c["t4b_pinned"]["failures_total"])
                 and sum(v["closed"] + v["open"]
                         for v in ps["per_key_dispatch"].values()) == 135604
                 and sum(v["closed"] for v in ps["per_key_dispatch"].values())
                 == ps["patterns_dispatched_closed"]
                 and sum(v["open"] for v in ps["per_key_dispatch"].values())
                 == ps["patterns_open"]
                 and ps["patterns_dispatched_closed"] + ps["patterns_open"]
                 == 135604)
    checks.append(("V6 census dispatch arithmetic vs the committed QG-7c "
                   "census", census_ok,
                   f"closed={ps['patterns_dispatched_closed']} "
                   f"open={ps['patterns_open']}"))

    h = rec["p3_hostile_arm"]
    hr = h["hostile_referee"]
    hostile_ok = (hr["rows"] == hr["dxx_witness_rows"]
                  and not hr["sandwich_failures"]
                  and not hr["dxx_witness_failures"]
                  and not hr["replay_failures"]
                  and h["gap_rows_total"] == len(h["gap_rows_verbatim"])
                  and all(r["gap"] == 0
                          for r in h["c3_p1_extremal_panel"]["rows"]))
    checks.append(("V7 hostile arm bookkeeping", hostile_ok,
                   f"rows={hr['rows']} gaps={h['gap_rows_total']}"))

    if h["gap_rows_total"] and any(r.get("replay_confirmed")
                                   for r in h["gap_rows_verbatim"]):
        want = "QG7D_LINK_REFUTED"
    elif not all(rec["gates"].values()) or h["gap_rows_total"] > 0:
        want = "QG7D_CANNOT_CHECK"
    elif p1["holds"] and ps["holds"] and rec["p2_verbatim_dispatch"][
            "all_dispatched"]:
        want = "QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
    elif not p1["holds"]:
        want = "QG7D_PARTIAL__P1_RESIDUE_OPEN"
    else:
        want = "QG7D_PARTIAL__CENSUS_RESIDUE_OPEN"
    checks.append(("V8 terminal selection", want == rec["terminal"],
                   f"{want} vs {rec['terminal']}"))

    body = {k: v for k, v in rec.items()
            if k not in ("timing", "result_digest")}
    digest = hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()
    proto = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    checks.append(("V9 result digest + protocol sha256",
                   digest == rec["result_digest"]
                   and proto == rec["protocol_sha256"],
                   f"{digest[:16]}... / {proto[:16]}..."))

    ok = all(c[1] for c in checks)
    for name, good, info in checks:
        print(f"[{'ok ' if good else 'FAIL'}] {name}: {info}")
    print("QG7D_GENERIC_VERIFY=" + ("ACCEPT" if ok else "REJECT"))
    print("authority_echo=" + rec["authority"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
