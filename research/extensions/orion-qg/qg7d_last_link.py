#!/usr/bin/env python3
"""ORION-QG QG-7d: the last link — closing the comm-s2 pinned sector.

Frozen by development/orion-qg-regime-geometry/QG7D_LAST_LINK_PROTOCOL_V1.md
(frozen BEFORE any outcome under that protocol was computed).

The single link left open by QG-7c was the pinned comm-s2 sector: T4b's
per-block move menu left 135,604 lemma failures over a complete
536,870,912-case domain at worst residue +2.  This lane replaces that lemma by

  P1  a joint (pair/triple) exchange whose alternative is the EXACT local
      optimum of the comm-s2-free family on the two comm-s2 qubits (attack A2:
      domination, not reduction), taken together with the MG mirror image of
      the whole configuration (a receipt-proven cost-preserving involution),
      over the complete raw-target-letter domain 4^6 x 4^6 = 16,777,216 states
      per geometry, for every geometry of the M1-derived inventory - which
      includes both QG-7c declared-open sub-cases (double pinners; comm-s2
      chains).

All frozen machinery is imported UNMODIFIED; the inherited lemmas (MG, M1, T1,
T3, T4a, T4b, T5) are re-derived by calling the committed QG-7c functions.
Authority ceiling NOT_R6.  No chemistry data is read; the protected
stretched-N2 subject is never touched.  The only RNG is the frozen control
stream.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ORION_Q_DIR = Path(__file__).resolve().parents[1] / "orion-q"
sys.path.insert(0, str(ORION_Q_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import qg5b_exact_forecaster as qg5b  # noqa: E402
import qg7_bprime_completeness as qg7  # noqa: E402  (installs the n=4 guard)
import qg7b_hybrid_family as qg7b  # noqa: E402
import qg7c_classification as qg7c  # noqa: E402

INF = 10 ** 9
X, Y, Z = 1, 2, 3
PROTOCOL_NAME = "QG7D_LAST_LINK_PROTOCOL_V1.md"
BASE_REVISION = "509f962c"
SEED_C2_N3 = 20260901
SEED_C2_N4 = 20260902
P1_RESIDUE_VERBATIM_CAP = 200
CENSUS_VERBATIM_CAP = 40
GAP_VERBATIM_CAP = 50
C1_N3_CAP = 40
C1_N4_CAP = 10
C3_CAP = 60
RUNTIME_CAP_SECONDS = 1500
MATCHING = r6m._SYNTHETIC_MATCHING

lmul = qg7c.lmul
lsy = qg7c.lsy
lw = qg7c.lw
lf3 = qg7c.lf3


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


# ---- shared local tables ----------------------------------------------------

_IDX = np.arange(4096, dtype=np.int64)
_DIG = [(_IDX >> (2 * (5 - k))) & 3 for k in range(6)]
_F3 = np.zeros((4, 4, 4), dtype=np.int8)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            _F3[_a, _b, _c] = lf3(_a, _b, _c)
# G[state] = F3 over branch 0 + F3 over branch 1 for the six composed letters
G_TAB = (_F3[_DIG[0], _DIG[2], _DIG[4]]
         + _F3[_DIG[1], _DIG[3], _DIG[5]]).astype(np.int8)
# branch-swap permutation of a six-slot state (per-block target permutation)
SWAP = np.zeros(4096, dtype=np.int64)
for _k, _src in enumerate((1, 0, 3, 2, 5, 4)):
    SWAP |= _DIG[_src] << (2 * (5 - _k))
# GP[fl, state] = F3 total when the six frame letters are `fl`
GP = np.empty((4096, 4096), dtype=np.int8)
for _fl in range(4096):
    _fd = [(_fl >> (2 * (5 - _k))) & 3 for _k in range(6)]
    _perm = np.zeros(4096, dtype=np.int64)
    for _k in range(6):
        _perm |= qg7c.MY_LM[_DIG[_k], _fd[_k]].astype(np.int64) << (2 * (5 - _k))
    GP[_fl] = G_TAB[_perm]


def code6(letters) -> int:
    return sum(int(letters[k]) << (2 * (5 - k)) for k in range(6))


def uanti(w0: int, w1: int) -> int:
    return 4 * (min(w0, w1) - 1) + 2 * (max(w0, w1) - 1)


# ---- G1 table binding -------------------------------------------------------

def bind_tables() -> dict[str, Any]:
    base = qg7c.bind_tables()
    gp_ok = True
    for fl in (0, 1, 273, 4095, 2730):
        fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
        for st in (0, 5, 1234, 4095):
            sd = [(st >> (2 * (5 - k))) & 3 for k in range(6)]
            o = [lmul(sd[k], fd[k]) for k in range(6)]
            want = lf3(o[0], o[2], o[4]) + lf3(o[1], o[3], o[5])
            if int(GP[fl, st]) != want:
                gp_ok = False
    return {"qg7c_tables": base, "gp_table_spotbind_ok": bool(gp_ok),
            "ok": bool(base["ok"] and gp_ok)}


# ---- G2 mirror identity (complete domain) -----------------------------------

def mirror_identity() -> dict[str, Any]:
    """The MG mirror is an exact cost-preserving involution, all n.

    Complete domain: every six-letter frame pattern at one qubit x every
    six-letter target pattern (4^6 x 4^6 = 16,777,216) -- the branch-swapped
    frames read at the branch-swapped targets must reproduce the F3 total
    exactly.  Plus the complete uanti symmetry table and the label flip.
    """
    failures = 0
    for fl in range(4096):
        fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
        fl_m = code6([fd[1], fd[0], fd[3], fd[2], fd[5], fd[4]])
        # cost of the mirrored frames read at the branch-swapped states
        if not np.array_equal(GP[fl_m][SWAP], GP[fl]):
            failures += 1
    uanti_failures = 0
    for w0 in (1, 2):
        for w1 in (1, 2):
            if uanti(w0, w1) != uanti(w1, w0):
                uanti_failures += 1
    label_ok = True
    for l0, l1 in ((0, 1), (1, 0)):
        if (l1, l0) not in ((0, 1), (1, 0)):
            label_ok = False
    dom = 4096 * 4096
    mg = qg7c.mg_gauge()
    return {
        "domain_size": dom,
        "expected_domain_size": 16777216,
        "f3_exchange_failures": failures,
        "uanti_symmetry_failures": uanti_failures,
        "label_orientation_closed": bool(label_ok),
        "qg7c_mg_gauge": mg,
        "holds": (failures == 0 and uanti_failures == 0 and label_ok
                  and dom == 16777216 and bool(mg["holds"])),
    }


# ---- G3 letter-permutation gauge (complete domain) --------------------------

def gauge_permutations() -> dict[str, Any]:
    perms = [p for p in itertools.permutations((1, 2, 3))]
    failures = 0
    checked = 0
    for perm in perms:
        table = np.array([0, perm[0], perm[1], perm[2]], dtype=np.int64)
        pstate = np.zeros(4096, dtype=np.int64)
        for k in range(6):
            pstate |= table[_DIG[k]] << (2 * (5 - k))
        for fl in range(4096):
            fd = [(fl >> (2 * (5 - k))) & 3 for k in range(6)]
            fl_p = code6([int(table[v]) for v in fd])
            checked += 4096
            if not np.array_equal(GP[fl_p][pstate], GP[fl]):
                failures += 1
    return {"permutations": len(perms), "domain_size": checked,
            "expected_domain_size": 6 * 4096 * 4096,
            "failures": failures,
            "holds": failures == 0 and checked == 6 * 4096 * 4096}


# ---- geometry inventory (from the receipt-bound M1 lemma) -------------------

def third(*excluded) -> int:
    for c in (1, 2, 3):
        if c not in excluded:
            return c
    raise AssertionError("no third letter")


def build_roles() -> list[dict[str, Any]]:
    """Every role an M1-irreducible block can take relative to {b, a}."""
    roles: list[dict[str, Any]] = []

    def add(name, loc, ext, was_cs2):
        roles.append({"name": name, "loc": tuple(loc), "ext": tuple(ext),
                      "was_cs2": bool(was_cs2)})

    # OUT: no frame letters at b or a; the three M1 shapes as external profiles
    add("OUT_ANCH", (0, 0, 0, 0), (1, 1, 0, 1, 1), False)
    add("OUT_PHANTOM", (0, 0, 0, 0), (1, 2, 0, 1, 1), False)
    add("OUT_COMMS2", (0, 0, 0, 0), (2, 1, 0, 1, 1), True)
    for p in (X, Y):
        add(f"ANCH_B_{p}", (Z, p, 0, 0), (0, 0, 0, 0, 0), False)
        add(f"ANCH_A_{p}", (0, 0, Z, p), (0, 0, 0, 0, 0), False)
        add(f"BORROW_B_{p}", (0, p, 0, 0), (1, 1, 0, 0, 1), False)
        add(f"BORROW_A_{p}", (0, 0, 0, p), (1, 1, 0, 0, 1), False)
        add(f"CS2_B_ANTIOUT_{p}", (p, 0, 0, 0), (1, 1, 1, 1, 1), True)
        add(f"CS2_B_ANTIB_{p}", (p, third(Z, p), 0, 0), (1, 0, 1, 0, 0), True)
        add(f"CS2_A_ANTIOUT_{p}", (0, 0, p, 0), (1, 1, 1, 1, 1), True)
        add(f"CS2_A_ANTIA_{p}", (0, 0, p, third(Z, p)), (1, 0, 1, 0, 0), True)
    for u in (X, Y):
        for v in (X, Y):
            add(f"CS2_BA_ANTIA_{u}{v}", (u, 0, v, third(Z, v)),
                (0, 0, 0, 0, 0), True)
            add(f"CS2_BA_ANTIB_{u}{v}", (u, third(Z, u), v, 0),
                (0, 0, 0, 0, 0), True)
    return roles


OURS = {"name": "COMMS2_OURS", "loc": (X, 0, X, Y), "ext": (0, 0, 0, 0, 0),
        "was_cs2": True}


def mirror_block(blk: dict[str, Any]) -> dict[str, Any]:
    l0b, l1b, l0a, l1a = blk["loc"]
    w0, w1, s0, s1, xe = blk["ext"]
    return {"name": blk["name"] + "|M", "loc": (l1b, l0b, l1a, l0a),
            "ext": (w1, w0, s1, s0, xe), "was_cs2": blk["was_cs2"]}


def block_shape_ok(blk: dict[str, Any]) -> bool:
    """X's own block must be feasible with sigma_b = sigma_a = Z, labels (0,1)."""
    l0b, l1b, l0a, l1a = blk["loc"]
    w0e, w1e, s0e, s1e, xe = blk["ext"]
    w0 = lw(l0b) + lw(l0a) + w0e
    w1 = lw(l1b) + lw(l1a) + w1e
    if not (1 <= w0 <= 2 and 1 <= w1 <= 2):
        return False
    if (lsy(Z, l0b) + lsy(Z, l0a) + s0e) % 2 != 0:
        return False
    if (lsy(Z, l1b) + lsy(Z, l1a) + s1e) % 2 != 1:
        return False
    if (lsy(l0b, l1b) + lsy(l0a, l1a) + xe) % 2 != 1:
        return False
    return True


# ---- P1: the domination lemma ----------------------------------------------

_OPT_CACHE: dict[tuple, tuple] = {}


def block_options(ext, sb, sa, orient, allow_cs2):
    """Feasible local (b, a) letter assignments for one block under sigma'."""
    key = (tuple(ext), sb, sa, orient, bool(allow_cs2))
    hit = _OPT_CACHE.get(key)
    if hit is not None:
        return hit
    w0e, w1e, s0e, s1e, xe = ext
    bc, ac, uu = [], [], []
    sig = (sb, sa)
    for l0b in range(4):
        for l1b in range(4):
            for l0a in range(4):
                for l1a in range(4):
                    w0 = lw(l0b) + lw(l0a) + w0e
                    w1 = lw(l1b) + lw(l1a) + w1e
                    if not (1 <= w0 <= 2 and 1 <= w1 <= 2):
                        continue
                    if (lsy(sb, l0b) + lsy(sa, l0a) + s0e) % 2 != orient[0]:
                        continue
                    if (lsy(sb, l1b) + lsy(sa, l1a) + s1e) % 2 != orient[1]:
                        continue
                    if (lsy(l0b, l1b) + lsy(l0a, l1a) + xe) % 2 != 1:
                        continue
                    if not allow_cs2:
                        # comm-s2 = symp-0 frame of support 2, every one of its
                        # letters anticommuting the tag, symp-1 frame weight 1
                        if orient[0] == 0:
                            f0, fw0, fw1 = (l0b, l0a), w0, w1
                            e_sy, e_w = s0e, w0e
                        else:
                            f0, fw0, fw1 = (l1b, l1a), w1, w0
                            e_sy, e_w = s1e, w1e
                        if fw0 == 2 and fw1 == 1 and e_sy == e_w and all(
                                lsy(sig[q], f0[q]) == 1
                                for q in range(2) if f0[q]):
                            continue
                    bc.append(l0b * 4 + l1b)
                    ac.append(l0a * 4 + l1a)
                    uu.append(uanti(w0, w1))
    out = (np.array(bc, dtype=np.int64), np.array(ac, dtype=np.int64),
           np.array(uu, dtype=np.int64))
    _OPT_CACHE[key] = out
    return out


def menu_pairs(blocks, orient):
    """min base per (frame pattern at b, frame pattern at a) over the menu."""
    P = np.full(4096 * 4096, 127, dtype=np.int8)
    nconf = 0
    for sb in range(4):
        for sa in range(4):
            opts = [block_options(blk["ext"], sb, sa, orient,
                                  blk["was_cs2"] and j > 0)
                    for j, blk in enumerate(blocks)]
            if any(len(o[0]) == 0 for o in opts):
                continue
            tagw = 2 * (lw(sb) + lw(sa))
            b0, a0, u0 = opts[0]
            b1, a1, u1 = opts[1]
            b2, a2, u2 = opts[2]
            flb = (b0[:, None, None] * 256 + b1[None, :, None] * 16
                   + b2[None, None, :]).ravel()
            fla = (a0[:, None, None] * 256 + a1[None, :, None] * 16
                   + a2[None, None, :]).ravel()
            base = (u0[:, None, None] + u1[None, :, None]
                    + u2[None, None, :]).ravel() + tagw
            nconf += flb.size
            idx = flb * 4096 + fla
            order = np.argsort(-base, kind="stable")
            i_s = idx[order]
            b_s = base[order].astype(np.int8)
            # read-before-write min: duplicates inside this batch are resolved
            # by the descending order, and the batch never raises a value
            # already recorded by an earlier tag choice
            np.minimum(b_s, P[i_s], out=b_s)
            P[i_s] = b_s
    nz = np.nonzero(P < 127)[0]
    return nz // 4096, nz % 4096, P[nz].astype(np.int16), nconf


def _mask_rows(beta: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    lo = int(alpha.min())
    hi = int(alpha.max())
    masks = np.zeros((hi - lo + 1, 512), dtype=np.uint8)
    for v in range(lo, hi + 1):
        masks[v - lo] = np.packbits(beta >= v)
    return masks[alpha - lo]


def p1_geometry(role1, role2, want_delta=False):
    """Complete-domain domination check for one geometry."""
    blocks = [OURS, role1, role2]
    xb_code = code6([blocks[j]["loc"][k] for j in range(3) for k in (0, 1)])
    xa_code = code6([blocks[j]["loc"][k] for j in range(3) for k in (2, 3)])
    XB = GP[xb_code].astype(np.int16)
    XA = GP[xa_code].astype(np.int16)
    baseX = 2 * 2  # wt(sigma) at b and a, both Z
    for blk in blocks:
        l0b, l1b, l0a, l1a = blk["loc"]
        w0e, w1e, _, _, _ = blk["ext"]
        baseX += uanti(lw(l0b) + lw(l0a) + w0e, lw(l1b) + lw(l1a) + w1e)

    streams = []
    menu_configs = 0
    menu_pairs_total = 0
    for branch in (0, 1):
        bl = blocks if branch == 0 else [mirror_block(b) for b in blocks]
        for orient in ((0, 1), (1, 0)):
            flb, fla, base, nconf = menu_pairs(bl, orient)
            menu_configs += nconf
            menu_pairs_total += int(flb.size)
            # group by frame pattern at b (flb is sorted ascending)
            bounds = np.searchsorted(flb, np.arange(4097))
            streams.append((branch, flb, fla, base, bounds))

    covered = np.zeros((4096, 512), dtype=np.uint8)
    processed = 0
    sparse_b = None
    sparse_a = None
    order_pairs = []
    for si, (branch, flb, fla, base, bounds) in enumerate(streams):
        present = np.nonzero(bounds[1:] > bounds[:-1])[0]
        for f in present:
            order_pairs.append((int(f), si))
    # frozen interleave: by frame-pattern index, later streams first on ties
    order_pairs.sort(key=lambda t: (t[0], -t[1]))
    def _alpha_beta(f, si):
        branch, flb, fla, base, bounds = streams[si]
        s, e = int(bounds[f]), int(bounds[f + 1])
        bs = base[s:e]
        # exact prune: F3 totals lie in [0, 6], so a partner whose base
        # exceeds the group minimum by more than 6 can never attain the min
        keep = bs <= int(bs.min()) + 6
        V = (GP[fla[s:e][keep]].astype(np.int16)
             + bs[keep][:, None]).min(axis=0)
        if branch == 0:
            return GP[f].astype(np.int16) - XB, XA - V + baseX
        return GP[f][SWAP].astype(np.int16) - XB, XA - V[SWAP] + baseX

    SPARSE_SWITCH = 50000
    for pos, (f, si) in enumerate(order_pairs):
        alpha, beta = _alpha_beta(f, si)
        covered |= _mask_rows(beta, alpha)
        processed += 1
        if processed % 128 == 0:
            cnt = int(4096 * 4096
                      - int(np.unpackbits(covered.reshape(-1)).sum()))
            if cnt == 0:
                break
            if cnt <= SPARSE_SWITCH:
                rows = np.argwhere(np.unpackbits(covered, axis=1) == 0)
                sparse_b = rows[:, 0].astype(np.int64)
                sparse_a = rows[:, 1].astype(np.int64)
                for f2, si2 in order_pairs[pos + 1:]:
                    if sparse_b.size == 0:
                        break
                    a2, b2 = _alpha_beta(f2, si2)
                    alive = a2[sparse_b] > b2[sparse_a]
                    processed += 1
                    if not alive.all():
                        sparse_b = sparse_b[alive]
                        sparse_a = sparse_a[alive]
                break
    if sparse_b is None:
        rows = np.argwhere(np.unpackbits(covered, axis=1) == 0)
        sparse_b = rows[:, 0].astype(np.int64)
        sparse_a = rows[:, 1].astype(np.int64)
    uncovered = int(sparse_b.size)
    out = {
        "geometry": [role1["name"], role2["name"]],
        "state_domain": 4096 * 4096,
        "menu_configurations": menu_configs,
        "menu_distinct_frame_pairs": menu_pairs_total,
        "frame_patterns_processed": processed,
        "residue": uncovered,
        "closed": uncovered == 0,
    }
    if want_delta or uncovered:
        out["residue_rows_verbatim"] = [
            {"state_b": int(sparse_b[k]), "state_a": int(sparse_a[k])}
            for k in range(min(int(sparse_b.size), P1_RESIDUE_VERBATIM_CAP))]
        out["residue_verbatim_cap"] = P1_RESIDUE_VERBATIM_CAP
    return out, XB, XA, baseX


def p1_lemma() -> dict[str, Any]:
    roles = build_roles()
    pairs = list(itertools.combinations_with_replacement(range(len(roles)), 2))
    per_geometry = []
    residue_total = 0
    closed_geometries = 0
    for i, j in pairs:
        res, _, _, _ = p1_geometry(roles[i], roles[j])
        residue_total += res["residue"]
        closed_geometries += int(res["closed"])
        per_geometry.append(res)
    sectors = {"unpinned": 0, "single_pinner": 0, "double_pinner": 0,
               "comm_s2_chain": 0}
    for res in per_geometry:
        names = res["geometry"]
        touch_b = sum(1 for n in names
                      if n.startswith(("ANCH_B", "BORROW_B", "CS2_B",
                                       "CS2_BA")))
        if touch_b == 0:
            sectors["unpinned"] += 1
        elif touch_b == 1:
            sectors["single_pinner"] += 1
        else:
            sectors["double_pinner"] += 1
        if any(n.startswith(("CS2_", "OUT_COMMS2")) for n in names):
            sectors["comm_s2_chain"] += 1
    return {
        "roles": [r["name"] for r in roles],
        "role_count": len(roles),
        "geometry_count": len(pairs),
        "state_domain_per_geometry": 4096 * 4096,
        "total_states": len(pairs) * 4096 * 4096,
        "geometries_closed": closed_geometries,
        "residue_total": residue_total,
        "sector_coverage": sectors,
        "per_geometry": per_geometry,
        "holds": residue_total == 0 and closed_geometries == len(pairs),
    }


# ---- P2: QG-7c T4b census dispatch -----------------------------------------

COMMITTED_T4B_CENSUS = {
    "PA_ja0_delta1": 97072, "PA_ja0_delta2": 2376, "PA_ja1_delta1": 3600,
    "PP_ja0_delta1": 30500, "PP_ja0_delta2": 440, "PP_ja1_delta1": 1616,
}


def _pattern_geometry_class(case2: str, ja: int) -> list[str]:
    """P1 geometry classes that contain a T4b pattern of this case."""
    pinner = ["ANCH_B_1", "ANCH_B_2"] if case2 == "PA" else \
        ["BORROW_B_1", "BORROW_B_2"]
    if ja == 0:
        third_roles = ["ANCH_A_1", "ANCH_A_2", "BORROW_A_1", "BORROW_A_2",
                       "CS2_A_ANTIOUT_1", "CS2_A_ANTIOUT_2",
                       "CS2_A_ANTIA_1", "CS2_A_ANTIA_2"]
    else:
        third_roles = ["OUT_ANCH", "OUT_PHANTOM", "OUT_COMMS2"]
    return sorted("+".join(sorted((a, b)))
                  for a in pinner for b in third_roles)


def census_dispatch(t4b: dict[str, Any], p1: dict[str, Any]) -> dict[str, Any]:
    census = t4b["failing_census"]
    verbatim = t4b["failing_verbatim_capped"]
    census_ok = (census == COMMITTED_T4B_CENSUS
                 and int(t4b["domain_size"]) == 536870912
                 and int(t4b["failures_total"]) == 135604
                 and int(t4b["worst_delta"]) == 2)
    geom_names = {"+".join(sorted(g["geometry"])): g for g in p1["per_geometry"]}
    dispatch: dict[str, Any] = {}
    dispatched = 0
    undispatched = 0
    for key, count in sorted(census.items()):
        case2 = key[:2]
        ja = int(key[key.index("ja") + 2])
        classes = _pattern_geometry_class(case2, ja)
        all_closed = True
        missing = []
        for cls in classes:
            g = geom_names.get(cls)
            if g is None or not g["closed"]:
                all_closed = False
                missing.append(cls)
        if all_closed:
            dispatched += count
            status = "CLOSED_BY_P1"
        else:
            undispatched += count
            status = "OPEN"
        dispatch[key] = {
            "patterns": count,
            "status": status,
            "closed_by_attack": "A2_domination_with_A1_joint_exchange"
                                "_and_MG_mirror" if all_closed else None,
            "p1_geometry_classes": classes,
            "geometry_classes_open": missing,
        }
    return {
        "census_reproduced_verbatim": bool(census_ok),
        "committed_census": COMMITTED_T4B_CENSUS,
        "observed_census": census,
        "domain_size": int(t4b["domain_size"]),
        "failures_total": int(t4b["failures_total"]),
        "worst_delta": int(t4b["worst_delta"]),
        "per_key_dispatch": dispatch,
        "patterns_dispatched_closed": dispatched,
        "patterns_open": undispatched,
        "dispatch_sums_to_census": dispatched + undispatched == 135604,
        "verbatim_rows": len(verbatim),
        "verbatim_cap": CENSUS_VERBATIM_CAP,
        "holds": bool(census_ok and undispatched == 0
                      and dispatched + undispatched == 135604),
    }


def t4b_failing_cells() -> dict[str, Any]:
    """Re-derive the QG-7c T4b failing cells (same frozen construction).

    Returns the failing (core, env) coordinates per case so that every
    censused pattern can be mapped into a P1 (geometry, state) and dispatched
    individually.  The reproduced census is gated against the committed one.
    """
    LM = qg7c.MY_LM
    F3E = qg7c.F3E
    F3T = qg7c.F3T
    t4 = np.arange(4, dtype=np.int64)
    t0b = np.repeat(t4, 16)
    t1b = np.tile(np.repeat(t4, 4), 4)
    t21b = np.tile(t4, 16)
    t0a, t1a, t21a = t0b, t1b, t21b
    cells: dict[tuple, np.ndarray] = {}
    census: dict[str, int] = {}
    total = 0
    for case2 in ("PA", "PP"):
        for ja in (0, 1):
            for R_b in (1, 2):
                for R_a in (1, 2):
                    w = lmul(R_a, Z)
                    for pl in (1, 2):
                        o0b = LM[t0b, R_b]
                        o1b_pin = LM[t21b, pl]
                        o0a = LM[t0a, R_a]
                        o1a_our = LM[t1a, w]
                        oldB = (F3E[o0b][:, :, None]
                                + F3T[t1b, o1b_pin][:, None, :])
                        oldA = (F3E[o0a][:, :, None]
                                + F3T[o1a_our, t21a][:, None, :])
                        best = np.full((64, 64, 64, 64), 99, dtype=np.int16)

                        def group(bparts, aparts, struct):
                            fb = np.stack([
                                F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :]
                                - oldB for n0, n1, n1p in bparts]) \
                                .min(axis=0).reshape(64, 64)
                            fa = np.stack([
                                F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :]
                                - oldA for n0, n1, n1p in aparts]) \
                                .min(axis=0).reshape(64, 64)
                            np.minimum(best,
                                       fb[:, :, None, None]
                                       + fa[None, None, :, :]
                                       + np.int16(struct), out=best)

                        for sw in (0, 1):
                            s0b, s1b = (t0b, t1b) if sw == 0 else (t1b, t0b)
                            s0a, s1a = (t0a, t1a) if sw == 0 else (t1a, t0a)
                            group([(s0b, s1b, LM[t21b, pp]) for pp in (1, 2)],
                                  [(LM[s0a, Z], LM[s1a, c], t21a)
                                   for c in (1, 2)], -2)
                            group([(LM[s0b, Z], LM[s1b, c], LM[t21b, pp])
                                   for c in (1, 2) for pp in (1, 2)],
                                  [(s0a, s1a, t21a)], -2 - 2 * ja)
                            if ja:
                                group([(s0b, LM[s1b, le], LM[t21b, pp])
                                       for le in (1, 2) for pp in (1, 2)],
                                      [(LM[s0a, m0], LM[s1a, m1], t21a)
                                       for m0 in (1, 2, 3)
                                       for m1 in (1, 2, 3) if m1 != m0], -2)
                            if case2 == "PA":
                                bparts = [(LM[s0b, m0], LM[s1b, m1],
                                           LM[t21b, m12])
                                          for m0 in (1, 2, 3)
                                          for m1 in (1, 2, 3) if m1 != m0
                                          for m12 in (1, 2)]
                                struct = 0
                            else:
                                bparts = [(LM[s0b, m0], LM[s1b, m1], t21b)
                                          for m0 in (1, 2, 3)
                                          for m1 in (1, 2, 3) if m1 != m0]
                                struct = -2
                            group(bparts,
                                  [(s0a, LM[s1a, le], LM[t21a, l2])
                                   for le in (1, 2) for l2 in (1, 2)], struct)
                        bad = np.argwhere(best > 0)
                        if bad.size:
                            d = best[bad[:, 0], bad[:, 1], bad[:, 2], bad[:, 3]]
                            cells[(case2, ja, R_b, R_a, pl)] = np.concatenate(
                                [bad, d[:, None].astype(np.int64)], axis=1)
                            total += int(bad.shape[0])
                            for dv in np.unique(d):
                                k = f"{case2}_ja{ja}_delta{int(dv)}"
                                census[k] = census.get(k, 0) + int(
                                    (d == dv).sum())
    return {"cells": cells, "census": census, "failures_total": total,
            "census_matches_committed": census == COMMITTED_T4B_CENSUS
            and total == 135604}


def census_state_dispatch(p1: dict[str, Any]) -> dict[str, Any]:
    """Map every censused T4b pattern to its P1 (geometry, state) and dispatch."""
    derived = t4b_failing_cells()
    residue_sets: dict[str, set] = {}
    residue_complete = True
    for g in p1["per_geometry"]:
        if g["residue"]:
            key = "+".join(sorted(g["geometry"]))
            rows = g.get("residue_rows_verbatim", [])
            if len(rows) < g["residue"]:
                residue_complete = False
            residue_sets[key] = {(r["state_b"], r["state_a"]) for r in rows}
    roles = build_roles()
    LM = qg7c.MY_LM
    TAU = {1: np.array([0, 1, 2, 3], dtype=np.int64),
           2: np.array([0, 2, 1, 3], dtype=np.int64)}
    dispatched = 0
    open_patterns = 0
    open_rows: list[dict] = []
    per_key: dict[str, dict[str, int]] = {}
    for (case2, ja, R_b, R_a, pl), arr in sorted(derived["cells"].items()):
        cb, eb, ca, ea, dv = (arr[:, k] for k in range(5))
        t0b, t1b, t21b = cb // 16, (cb // 4) % 4, cb % 4
        u0b, v0b, e1b = (eb // 4) // 4, (eb // 4) % 4, eb % 4
        t0a, t1a, t21a = ca // 16, (ca // 4) % 4, ca % 4
        u0a, v0a, e1a = (ea // 4) // 4, (ea // 4) % 4, ea % 4
        tb, ta = TAU[R_b], TAU[R_a]
        pin_raw_0b = LM[u0b, Z] if case2 == "PA" else u0b
        pin_name = ("ANCH_B_%d" if case2 == "PA" else "BORROW_B_%d") % int(
            tb[pl])
        bad_mask = np.zeros(arr.shape[0], dtype=bool)
        for role in roles:
            l0b, l1b, l0a, l1a = role["loc"]
            third_raw_0b = LM[v0b, l0b] if l0b else v0b
            third_raw_1b = LM[e1b, l1b] if l1b else e1b
            third_raw_0a = LM[v0a, l0a] if l0a else v0a
            third_raw_1a = LM[e1a, l1a] if l1a else e1a
            sb = (tb[t0b] << 10) | (tb[t1b] << 8) | (tb[pin_raw_0b] << 6) \
                | (tb[t21b] << 4) | (tb[third_raw_0b] << 2) | tb[third_raw_1b]
            sa = (ta[t0a] << 10) | (ta[t1a] << 8) | (ta[u0a] << 6) \
                | (ta[t21a] << 4) | (ta[third_raw_0a] << 2) | ta[third_raw_1a]
            key = "+".join(sorted((pin_name, role["name"])))
            rset = residue_sets.get(key)
            if not rset:
                continue
            for k in np.nonzero(~bad_mask)[0]:
                if (int(sb[k]), int(sa[k])) in rset:
                    bad_mask[k] = True
                    if len(open_rows) < P1_RESIDUE_VERBATIM_CAP:
                        open_rows.append({
                            "case": case2, "ja": int(ja), "R_b": int(R_b),
                            "R_a": int(R_a), "p": int(pl),
                            "geometry": key, "state_b": int(sb[k]),
                            "state_a": int(sa[k]), "t4b_delta": int(dv[k])})
        nbad = int(bad_mask.sum())
        dispatched += int(arr.shape[0]) - nbad
        open_patterns += nbad
        for d in (1, 2):
            m = int(((dv == d) & ~bad_mask).sum())
            if m:
                kk = f"{case2}_ja{ja}_delta{d}"
                per_key.setdefault(kk, {"closed": 0, "open": 0})
                per_key[kk]["closed"] += m
            mo = int(((dv == d) & bad_mask).sum())
            if mo:
                kk = f"{case2}_ja{ja}_delta{d}"
                per_key.setdefault(kk, {"closed": 0, "open": 0})
                per_key[kk]["open"] += mo
    return {
        "derived_census": derived["census"],
        "derived_failures_total": derived["failures_total"],
        "census_matches_committed": bool(derived["census_matches_committed"]),
        "residue_serialization_complete": bool(residue_complete),
        "third_block_roles_scanned": len(roles),
        "per_key_dispatch": {k: v for k, v in sorted(per_key.items())},
        "patterns_dispatched_closed": dispatched,
        "patterns_open": open_patterns,
        "open_rows_verbatim": open_rows,
        "dispatch_sums_to_census": dispatched + open_patterns == 135604,
        "closed_by_attack": "A2_domination_with_A1_joint_exchange_and_MG_mirror",
        "holds": bool(derived["census_matches_committed"] and residue_complete
                      and open_patterns == 0
                      and dispatched + open_patterns == 135604),
    }


def explicit_verbatim_dispatch(t4b: dict[str, Any],
                               p1: dict[str, Any]) -> dict[str, Any]:
    """State-level P1 verdict at the exact coordinates of every verbatim row."""
    residue_sets: dict[str, set] = {}
    for g in p1["per_geometry"]:
        if g["residue"]:
            residue_sets["+".join(sorted(g["geometry"]))] = {
                (r["state_b"], r["state_a"])
                for r in g.get("residue_rows_verbatim", [])}
    roles = build_roles()
    LM = qg7c.MY_LM
    TAU = {1: (0, 1, 2, 3), 2: (0, 2, 1, 3)}
    rows = []
    worst = -99
    for i, row in enumerate(t4b["failing_verbatim_capped"]):
        case2, ja = row["case"], int(row["ja"])
        R_b, R_a, pl = int(row["R_b"]), int(row["R_a"]), int(row["p"])
        cb, eb = int(row["coreB"]), int(row["envB"])
        ca, ea = int(row["coreA"]), int(row["envA"])
        t0b, t1b, t21b = cb // 16, (cb // 4) % 4, cb % 4
        u0b, v0b, e1b = (eb // 4) // 4, (eb // 4) % 4, eb % 4
        t0a, t1a, t21a = ca // 16, (ca // 4) % 4, ca % 4
        u0a, v0a, e1a = (ea // 4) // 4, (ea // 4) % 4, ea % 4
        tb, ta = TAU[R_b], TAU[R_a]
        pin_raw_0b = int(LM[u0b, Z]) if case2 == "PA" else u0b
        pin_name = ("ANCH_B_%d" if case2 == "PA" else "BORROW_B_%d") % tb[pl]
        coords = []
        row_ok = True
        for role in roles:
            l0b, l1b, l0a, l1a = role["loc"]
            sb = code6([tb[t0b], tb[t1b], tb[pin_raw_0b], tb[t21b],
                        tb[int(LM[v0b, l0b]) if l0b else v0b],
                        tb[int(LM[e1b, l1b]) if l1b else e1b]])
            sa = code6([ta[t0a], ta[t1a], ta[u0a], ta[t21a],
                        ta[int(LM[v0a, l0a]) if l0a else v0a],
                        ta[int(LM[e1a, l1a]) if l1a else e1a]])
            key = "+".join(sorted((pin_name, role["name"])))
            hit = (sb, sa) in residue_sets.get(key, ())
            if hit:
                row_ok = False
                coords.append({"geometry": key, "state_b": sb, "state_a": sa,
                               "in_p1_residue": True})
        rows.append({
            "index": i,
            "census_row": row,
            "p1_pinner_role": pin_name,
            "p1_geometries_scanned": len(roles),
            "p1_residue_hits": coords,
            "closed_by_p1": bool(row_ok),
        })
        worst = max(worst, int(row["delta"]))
    return {
        "rows": rows,
        "rows_checked": len(rows),
        "all_dispatched": all(r["closed_by_p1"] for r in rows),
        "t4b_worst_delta_in_verbatim": worst,
    }


# ---- P3: hostile realization arm -------------------------------------------

def _clear_caches() -> None:
    r6o._block_cache.clear()
    qg5b._bprime_block_cache.clear()
    qg7b._bsecond_block_cache.clear()
    r6m._local_table.cache_clear()


def _eval_instance(tp, n, where, gap_rows, counters):
    _clear_caches()
    dxx = r6p.dxx_search(tp, n, want_witness=True)
    c_dxx = int(dxx["C_Dxx"])
    c_dplus = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
    fbp, fbp_wit = qg5b.bprime_family_min(tp, n, want_witness=True)
    fbpp, fbpp_wit = qg7b.bsecond_family_min(tp, n, want_witness=True)
    fbp_eff = INF if fbp is None else int(fbp)
    fbpp_eff = INF if fbpp is None else int(fbpp)
    counters["rows"] += 1
    if not (c_dxx <= c_dplus and c_dxx <= fbp_eff and c_dxx <= fbpp_eff):
        counters["sandwich_failures"].append(where)
    counters["dxx_witness_rows"] += 1
    if not r6p.verify_dxx_witness(tp, n, dxx["witness"]):
        counters["dxx_witness_failures"].append(where)
    gap = c_dxx - min(c_dplus, fbp_eff, fbpp_eff)
    if gap < 0:
        terms = r6m._synthetic_terms(tp)
        c_dp = int(r6o.dp_cost_frozen_configs(terms, n))
        wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
        replay_ok = (c_dp == c_dxx and int(wit["C_R6M"]) == c_dp
                     and all(wit["checks"].values()))
        bp_ok = fbp is None or qg5b.verify_bprime_witness(tp, n, fbp_wit)
        bpp_ok = fbpp is None or qg7b.verify_bsecond_witness(tp, n, fbpp_wit)
        counters["replay_rows"] += 1
        if not (replay_ok and bp_ok and bpp_ok):
            counters["replay_failures"].append(where)
        if len(gap_rows) < GAP_VERBATIM_CAP:
            gap_rows.append({
                "where": where, "n": n,
                "target_pairs": [[list(a), list(b)] for a, b in tp],
                "C_Dxx": c_dxx, "C_DP": c_dp, "C_Dplus": c_dplus,
                "f_Bprime": fbp_eff if fbp is not None else None,
                "f_Bsecond": fbpp_eff if fbpp is not None else None,
                "gap": int(gap),
                "replay_confirmed": bool(replay_ok and bp_ok and bpp_ok),
                "dxx_witness_verbatim": dxx["witness"],
            })
    return c_dxx, c_dplus, fbp_eff, fbpp_eff, gap


def _state_letters(state: int):
    return [(state >> (2 * (5 - k))) & 3 for k in range(6)]


def _instance_from_state(state_b: int, state_a: int, n: int):
    lb = _state_letters(state_b)
    la = _state_letters(state_a)
    spare = [Z] + [0] * (n - 3) if n >= 3 else []
    targets = []
    for k in range(6):
        key = (0, 0)
        for q, le in enumerate([lb[k], la[k]] + list(spare)):
            if le:
                key = p10.mul(key, r6o._letter_key(le, q))
        targets.append(key)
    if any(t == (0, 0) for t in targets):
        return None
    return tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))


def hostile_arm(t4b: dict[str, Any], p1: dict[str, Any]) -> dict[str, Any]:
    counters = {"rows": 0, "sandwich_failures": [], "dxx_witness_rows": 0,
                "dxx_witness_failures": [], "replay_rows": 0,
                "replay_failures": []}
    gap_rows: list[dict] = []
    c1_rows = []
    census_rows = t4b["failing_verbatim_capped"]
    for i, row in enumerate(census_rows[:C1_N3_CAP]):
        tp, feas, ref = qg7c._realize_row(row, 3)
        c_dxx, c_dplus, fbp, fbpp, gap = _eval_instance(
            tp, 3, ["c1_n3", i], gap_rows, counters)
        c1_rows.append({
            "index": i, "n": 3, "config_feasible": feas,
            "comm_s2_reference_cost": ref, "C_Dxx": c_dxx,
            "C_Dplus": c_dplus, "f_Bprime": fbp if fbp < INF else None,
            "f_Bsecond": fbpp if fbpp < INF else None, "gap": int(gap),
            "reference_dominated": ref is None or c_dxx <= ref})
    for i, row in enumerate(census_rows[:C1_N4_CAP]):
        tp, feas, ref = qg7c._realize_row(row, 4)
        c_dxx, c_dplus, fbp, fbpp, gap = _eval_instance(
            tp, 4, ["c1_n4", i], gap_rows, counters)
        c1_rows.append({
            "index": i, "n": 4, "config_feasible": feas,
            "comm_s2_reference_cost": ref, "C_Dxx": c_dxx,
            "C_Dplus": c_dplus, "f_Bprime": fbp if fbp < INF else None,
            "f_Bsecond": fbpp if fbpp < INF else None, "gap": int(gap),
            "reference_dominated": ref is None or c_dxx <= ref})
    c2_summary = {}
    for n, count, seed in ((3, 120, SEED_C2_N3), (4, 30, SEED_C2_N4)):
        rng = np.random.default_rng(seed)
        gaps = 0
        for i in range(count):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            _, _, _, _, gap = _eval_instance(
                tp, n, ["c2", n, i], gap_rows, counters)
            if gap < 0:
                gaps += 1
        c2_summary[f"n{n}"] = {"instances": count, "seed": seed,
                               "gap_rows": gaps}
    # C3: P1-extremal panel -- the P1 states of smallest margin, i.e. the
    # residue states first (frozen tie-break by geometry order then by state
    # index); if P1 leaves no residue, the cheapest comm-s2 states instead
    roles = {r["name"]: r for r in build_roles()}
    extremal = []
    for g in p1["per_geometry"]:
        for row in g.get("residue_rows_verbatim", []):
            extremal.append((g["geometry"], row["state_b"], row["state_a"],
                             "P1_RESIDUE"))
    fallback = False
    if not extremal:
        fallback = True
        for names in (("ANCH_B_1", "ANCH_A_1"), ("BORROW_B_1", "ANCH_A_1")):
            _, XB, XA, baseX = p1_geometry(roles[names[0]], roles[names[1]])
            tot = XB[:, None].astype(np.int16) + XA[None, :] + np.int16(baseX)
            idx = np.argwhere(tot == int(tot.min()))
            for r in idx[:10]:
                extremal.append((list(names), int(r[0]), int(r[1]),
                                 "MIN_COMM_S2_COST"))
    c3_rows = []
    skipped = 0
    for gnames, sb_state, sa_state, kind in extremal:
        for n in (2, 3, 4):
            if len(c3_rows) >= C3_CAP:
                break
            tp = _instance_from_state(sb_state, sa_state, n)
            if tp is None:
                skipped += 1
                continue
            c_dxx, c_dplus, fbp, fbpp, gap = _eval_instance(
                tp, n, ["c3", list(gnames), sb_state, sa_state, n],
                gap_rows, counters)
            c3_rows.append({
                "geometry": list(gnames), "kind": kind,
                "state_b": sb_state, "state_a": sa_state, "n": n,
                "C_Dxx": c_dxx, "C_Dplus": c_dplus,
                "f_Bprime": fbp if fbp < INF else None,
                "f_Bsecond": fbpp if fbpp < INF else None,
                "gap": int(gap)})
        if len(c3_rows) >= C3_CAP:
            break
    _clear_caches()
    return {
        "c1_census_realizations": {"rows": c1_rows, "n3_cap": C1_N3_CAP,
                                   "n4_cap": C1_N4_CAP,
                                   "instances": len(c1_rows)},
        "c2_dense_random_control": c2_summary,
        "c3_p1_extremal_panel": {"rows": c3_rows, "cap": C3_CAP,
                                 "identity_target_states_skipped": skipped,
                                 "selection": "P1_RESIDUE_FIRST" if not fallback
                                 else "MIN_COMM_S2_COST_FALLBACK",
                                 "candidate_states": len(extremal)},
        "instances_total": counters["rows"],
        "gap_rows_total": len(gap_rows),
        "gap_rows_verbatim": gap_rows,
        "gap_verbatim_cap": GAP_VERBATIM_CAP,
        "hostile_referee": {
            "rows": counters["rows"],
            "sandwich_failures": counters["sandwich_failures"],
            "dxx_witness_rows": counters["dxx_witness_rows"],
            "dxx_witness_failures": counters["dxx_witness_failures"],
            "replay_rows": counters["replay_rows"],
            "replay_failures": counters["replay_failures"]},
    }


# ---- receipt bindings -------------------------------------------------------

QG7C_TERMINAL = "QG7C_PARTIAL__L4B_OPEN"
QG7C_AUTHORITY = ("ORIONQG_QG7C_PARTIAL__L4B_COMM_S2_PINNED_SECTOR_OPEN__"
                  "L4C_CLOSED_CONDITIONAL__NOT_R6")
QG7C_DIGEST = ("0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1fe"
               "ded656b6")
QG7C_PROTOCOL_SHA = ("14129aea3894bff276d3b4ef625640b1563e3b7b2299ac12ca82d"
                     "578d1592646")
QG7B_TERMINAL = "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS"
QG7B_AUTHORITY = ("ORIONQG_QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS__"
                  "WEIGHT2_TAG_PHANTOM_BORROW_BSECOND__NOT_R6")
R6S_AUTHORITY_PREFIX = "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"


def bind_receipts() -> dict[str, Any]:
    here = Path(__file__).resolve().parent
    qg7_rec = json.loads((here / "QG7_BPRIME_COMPLETENESS_RESULTS.json")
                         .read_text())
    qg7b_rec = json.loads((here / "QG7B_HYBRID_FAMILY_RESULTS.json").read_text())
    qg7c_rec = json.loads((here / "QG7C_CLASSIFICATION_RESULTS.json")
                          .read_text())
    r6s_rec = json.loads(
        (ORION_Q_DIR / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json").read_text())
    ob = qg7_rec["arm2_normalization"]["obligations"]
    l1 = ob["L1_canonical_block_shape"]
    l2 = ob["L2_support_two_orientation"]
    l4 = ob["L4_multi_block_consolidation"]
    lem_e = qg7_rec["arm2_normalization"]["checks"]["N0"]["lemma_e"]
    qg7_bound = (
        qg7_rec["terminal"] == "QG7_FOURTH_SUPPORT2_REGIME_FOUND"
        and l1["domains"] == {"N1": 768, "N5": 27216}
        and l2["domains"] == {"N3": 8, "N0_lemma_e": 18432,
                              "N0_lemma_b": 43688}
        and l4["domains"] == {"N7_checked": 1440}
        and int(lem_e["domain_size"]) == 18432
        and int(lem_e["max_delta_f3"]) == 2)
    qg7b_bound = (qg7b_rec["terminal"] == QG7B_TERMINAL
                  and qg7b_rec["authority"] == QG7B_AUTHORITY
                  and int(qg7b_rec["q2"]["panel_w_witnesses"]
                          ["covered_count"]) == 64)
    c_t4b = qg7c_rec["t4b_pinned"]
    c_m1 = qg7c_rec["m1_inventory"]
    qg7c_bound = (
        qg7c_rec["terminal"] == QG7C_TERMINAL
        and qg7c_rec["authority"] == QG7C_AUTHORITY
        and qg7c_rec["result_digest"] == QG7C_DIGEST
        and qg7c_rec["protocol_sha256"] == QG7C_PROTOCOL_SHA
        and int(c_m1["raw_domain"]) == 262144
        and c_m1["irreducible_shape_counts"] == {"anchored": 288,
                                                 "phantom": 864,
                                                 "comm_s2": 864}
        and int(qg7c_rec["t1_prune"]["domain_size"]) == 12288
        and int(qg7c_rec["t3_consolidation"]["domain_size"]) == 14680064
        and int(qg7c_rec["t3_consolidation"]["failures"]) == 0
        and int(qg7c_rec["t4a_unpinned"]["domain_size"]) == 134217728
        and int(qg7c_rec["t4a_unpinned"]["worst_delta"]) == 0
        and int(c_t4b["domain_size"]) == 536870912
        and int(c_t4b["failures_total"]) == 135604
        and int(c_t4b["worst_delta"]) == 2
        and c_t4b["failing_census"] == COMMITTED_T4B_CENSUS
        and int(qg7c_rec["t5_home_merge"]["cases"]) == 1158)
    r6s_bound = str(r6s_rec["authority"]).startswith(R6S_AUTHORITY_PREFIX)
    return {
        "qg7_receipt_bound": bool(qg7_bound),
        "qg7b_receipt_bound": bool(qg7b_bound),
        "qg7b_result_digest": qg7b_rec["result_digest"],
        "qg7c_receipt_bound": bool(qg7c_bound),
        "qg7c_result_digest": qg7c_rec["result_digest"],
        "qg7c_protocol_sha256": qg7c_rec["protocol_sha256"],
        "qg7c_declared_open_subcases_verbatim":
            c_t4b["declared_open_subcases"],
        "r6s_receipt_bound": bool(r6s_bound),
        "r6s_authority": r6s_rec["authority"],
        "all_bound": bool(qg7_bound and qg7b_bound and qg7c_bound
                          and r6s_bound),
    }


# ---- claim boundary / authorities ------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "The comm-s2 sector of the unit-cost TARE support-<=2 classification: "
        "a complete-local-domain domination lemma (P1) which, for every "
        "geometry an M1-irreducible configuration can present around a comm-s2 "
        "block, compares the configuration against the EXACT local optimum of "
        "the comm-s2-free family on the two comm-s2 qubits and against the "
        "same optimum taken after the MG mirror of the whole configuration. "
        "The inventory of geometries includes the unpinned sector, the pinned "
        "single-pinner sector, the double-pinner sub-case and the comm-s2 "
        "chain sub-case."),
    "proven_components": (
        "P1 is exact and all-n: every alternative it scores changes letters "
        "only at the two comm-s2 qubits (so the cost difference it computes is "
        "the exact global difference), the mirror branch is the receipt-proven "
        "cost-preserving MG involution of the whole configuration, and the "
        "state domain per geometry is the complete product of raw target "
        "letters of all three blocks in both branches at those two qubits. "
        "Composed with the receipt-bound R6S / L1 / L2 / Lemma-E / L4a / M1 / "
        "T1 / T2 / T3 / T5 links and induction on the comm-s2 count, this "
        "yields C_DP == min(C_D+, f_B', f_B'') for all n under the unit "
        "support-count objective."),
    "machine_evidenced_only": (
        "The hostile realization panels (P3) are finite evidence, not proof; "
        "they exist to refute, not to support. The theorem rests on the "
        "complete domains, not on the panels."),
    "does_not_cover": (
        "Other objectives, other grammars, rotation-count trade-offs, "
        "chemistry subjects (no chemistry data is read in this lane), the "
        "protected stretched-N2 subject, or any donor/R6 novelty credit."),
}

AUTHORITY = {
    "THEOREM": (
        "ORIONQG_QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__COMM_S2_PINNED_"
        "SECTOR_CLOSED_BY_JOINT_EXCHANGE_AND_MIRROR_DOMINATION__NOT_R6"),
    "PARTIAL_P1": "ORIONQG_QG7D_PARTIAL__P1_RESIDUE_OPEN__NOT_R6",
    "PARTIAL_CENSUS": "ORIONQG_QG7D_PARTIAL__CENSUS_RESIDUE_OPEN__NOT_R6",
    "REFUTED": (
        "ORIONQG_QG7D_LINK_REFUTED__PINNED_COMM_S2_FIFTH_CONFIGURATION_"
        "WITNESS_REFEREE_CONFIRMED__NOT_R6"),
    "CANNOT": (
        "ORIONQG_QG7D_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6"),
}


# ---- main -------------------------------------------------------------------

def main() -> dict[str, Any]:
    start = time.monotonic()
    seconds: dict[str, float] = {}

    def clock(name, fn):
        t0 = time.monotonic()
        out = fn()
        seconds[name] = round(time.monotonic() - t0, 3)
        return out

    tables = clock("tables", bind_tables)
    protocol_path = (Path(__file__).resolve().parents[3]
                     / "development" / "orion-qg-regime-geometry"
                     / PROTOCOL_NAME)
    protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    bindings = clock("receipts", bind_receipts)
    mirror = clock("g2_mirror", mirror_identity)
    gauge = clock("g3_gauge", gauge_permutations)
    m1 = clock("m1", qg7c.m1_inventory)
    t1 = clock("t1", qg7c.t1_prune)
    t5 = clock("t5", qg7c.t5_home_merge)
    t3 = clock("t3", qg7c.t3_consolidation)
    t4a = clock("t4a", qg7c.t4a_unpinned)
    t4b = clock("t4b", qg7c.t4b_pinned)
    p1 = clock("p1", p1_lemma)
    p2 = clock("p2", lambda: census_dispatch(t4b, p1))
    p2v = clock("p2_verbatim", lambda: explicit_verbatim_dispatch(t4b, p1))
    p2s = clock("p2_state_dispatch", lambda: census_state_dispatch(p1))
    p3 = clock("p3", lambda: hostile_arm(t4b, p1))

    inherited = {
        "m1_inventory": m1, "t1_prune": t1, "t3_consolidation": t3,
        "t4a_unpinned": t4a, "t5_home_merge": t5,
        "t4b_pinned_summary": {
            "domain_size": t4b["domain_size"],
            "worst_delta": t4b["worst_delta"],
            "failures_total": t4b["failures_total"],
            "failing_census": t4b["failing_census"],
            "declared_open_subcases": t4b["declared_open_subcases"],
        },
    }

    hostile = p3["hostile_referee"]
    gates = {
        "G1_tables_bound": bool(tables["ok"]),
        "G2_mirror_identity": bool(mirror["holds"]),
        "G3_gauge_permutations": bool(gauge["holds"]),
        "G4_m1_reproduced": bool(
            m1["holds"] and m1["raw_domain"] == 262144
            and m1["irreducible_shape_counts"] == {"anchored": 288,
                                                   "phantom": 864,
                                                   "comm_s2": 864}),
        "G5_inherited_lemmas_reproduced": bool(
            t1["holds"] and t3["holds"] and t4a["holds"] and t5["holds"]
            and t3["domain_size"] == 14680064
            and t4a["domain_size"] == 134217728),
        "G6_p1_complete_domains": bool(
            all(g["state_domain"] == 16777216 for g in p1["per_geometry"])
            and p1["total_states"] == p1["geometry_count"] * 16777216),
        "G7_census_dispatch": bool(p2["census_reproduced_verbatim"]
                                   and p2["dispatch_sums_to_census"]
                                   and p2s["census_matches_committed"]
                                   and p2s["dispatch_sums_to_census"]),
        "G8_hostile_refereed": bool(
            not hostile["sandwich_failures"]
            and not hostile["dxx_witness_failures"]
            and not hostile["replay_failures"]
            and hostile["dxx_witness_rows"] == hostile["rows"]),
        "G9_receipt_bindings": bool(bindings["all_bound"]),
        "G10_caps_disclosed": bool(
            p3["gap_verbatim_cap"] == GAP_VERBATIM_CAP
            and p2["verbatim_cap"] == CENSUS_VERBATIM_CAP
            and p3["c3_p1_extremal_panel"]["cap"] == C3_CAP),
    }
    integrity_ok = all(gates.values())
    gap_confirmed = any(r.get("replay_confirmed")
                        for r in p3["gap_rows_verbatim"])

    if gap_confirmed and integrity_ok:
        terminal = "QG7D_LINK_REFUTED"
        authority = AUTHORITY["REFUTED"]
        responsibility = ("RESP:PINNED_COMM_S2_FIFTH_CONFIGURATION_WITNESS_"
                          "REFEREE_CONFIRMED__SERIALIZED_VERBATIM")
    elif not integrity_ok or p3["gap_rows_total"] > 0:
        terminal = "QG7D_CANNOT_CHECK"
        authority = AUTHORITY["CANNOT"]
        responsibility = ("RESP:REFEREE_OR_INTEGRITY_FAILURE__EVERYTHING_"
                          "SERIALIZED_VERBATIM")
    elif p1["holds"] and p2s["holds"] and p2v["all_dispatched"]:
        terminal = "QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
        authority = AUTHORITY["THEOREM"]
        responsibility = ("RESP:COMM_S2_SECTOR_CLOSED_ON_COMPLETE_LOCAL_"
                          "DOMAINS_FOR_EVERY_M1_GEOMETRY__CENSUS_FULLY_"
                          "DISPATCHED__CHAIN_ASSEMBLED_END_TO_END")
    elif not p1["holds"]:
        terminal = "QG7D_PARTIAL__P1_RESIDUE_OPEN"
        authority = AUTHORITY["PARTIAL_P1"]
        responsibility = ("RESP:P1_RESIDUE_SERIALIZED_VERBATIM__"
                          "CENSUS_DISPATCH_PARTIAL")
    else:
        terminal = "QG7D_PARTIAL__CENSUS_RESIDUE_OPEN"
        authority = AUTHORITY["PARTIAL_CENSUS"]
        responsibility = "RESP:CENSUS_RESIDUE_SERIALIZED_VERBATIM"

    theorem = terminal == "QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
    proof_audit = {
        "statement": "C_DP == min(C_D+, f_B', f_B'') for all n, unit-cost TARE",
        "chain": [
            {"step": 1, "claim": "C_DP == C_D++ for all n",
             "carried_by": "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json "
                           "(receipt_bindings.r6s_authority)"},
            {"step": 2, "claim": "labels (0,1) WLOG; the mirror is an exact "
                                 "cost-preserving involution of the whole "
                                 "configuration",
             "carried_by": "QG-7c mg_gauge (re-run here) + G2 mirror_identity "
                           "complete 16,777,216-case domain (this receipt)"},
            {"step": 3, "claim": "per-qubit letter permutations are cost "
                                 "gauge; sigma_b = sigma_a = Z and R_b = R_a "
                                 "= X WLOG",
             "carried_by": "G3 gauge_permutations complete domain "
                           "(this receipt)"},
            {"step": 4, "claim": "support->=3 frames, (2,2) blocks, class-(0,0) "
                                 "qubits and out-of-support tag letters all "
                                 "reduce at Delta <= 0",
             "carried_by": "R6S lemmas E/B + QG-7 N1 768 / N5 27,216 / N3 8 / "
                           "N0_e 18,432 / N0_b 43,688 / N7 1,440 "
                           "(receipt_bindings.qg7_receipt_bound)"},
            {"step": 5, "claim": "irreducible blocks are exactly anchored / "
                                 "phantom / comm-s2",
             "carried_by": "QG-7c M1, 262,144-case complete domain, re-run "
                           "here (inherited_lemmas.m1_inventory)"},
            {"step": 6, "claim": "commuting frame-supported tag letters prune "
                                 "(exact refund 2); wt(s) <= 3 + #comm-s2",
             "carried_by": "QG-7c T1 (12,288) + T2 occupancy over M1, re-run "
                           "here"},
            {"step": 7, "claim": "EVERY configuration containing a comm-s2 "
                                 "block is dominated at Delta <= 0 by a "
                                 "configuration with strictly fewer comm-s2 "
                                 "blocks -- for every geometry an "
                                 "M1-irreducible configuration can present, "
                                 "including double pinners and comm-s2 chains",
             "carried_by": "P1 (this receipt): complete 16,777,216-state "
                           "domain per geometry, exact comm-s2-free local "
                           "optimum plus the MG mirror branch"},
            {"step": 8, "claim": "induction on #comm-s2 terminates at a "
                                 "comm-s2-free irreducible configuration",
             "carried_by": "P1 removes exactly one comm-s2 block per "
                           "application and never creates one (menu "
                           "constraint (v)); the measure decreases "
                           "lexicographically"},
            {"step": 9, "claim": "wt-3-tag comm-s2-free configs consolidate "
                                 "into B'/B''-shape at Delta <= 0",
             "carried_by": "QG-7c T3, 14,680,064-case complete domain, re-run "
                           "here"},
            {"step": 10, "claim": "terminal shapes map into the committed "
                                  "grammars D+ / B' / B''",
             "carried_by": "QG-7c T5 (1,158) + M1 structure, re-run here; "
                           "grammar enumerators qg5b/qg7b bound by G1 and by "
                           "the QG-7b receipt"},
            {"step": 11, "claim": "sandwich: C_D++ <= min(C_D+, f_B', f_B'') "
                                  "because each family is a sub-family of "
                                  "D++; with steps 7-10 the reverse "
                                  "inequality holds, hence equality",
             "carried_by": "P3 asserts the sandwich on 100% of realized rows; "
                           "the inclusion itself is definitional in the "
                           "committed enumerators"},
        ],
        "superseded_by_this_lane": [
            "QG-7c T4a (unpinned comm-s2 elimination) -- subsumed by P1's "
            "unpinned geometries",
            "QG-7c T4b (pinned comm-s2 elimination) -- replaced by P1; its "
            "135,604-pattern census is re-derived verbatim and dispatched",
        ],
        "theorem_terminal_reached": bool(theorem),
    }

    result = {
        "schema": "ORIONQG.QG7D.LastLink.v1",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "lane": "QG-7d the last link (wave-2 keystone closure)",
        "protocol": "QG7D_LAST_LINK_PROTOCOL_V1",
        "protocol_sha256": protocol_sha,
        "base_revision": BASE_REVISION,
        "authority": authority,
        "terminal": terminal,
        "responsibility": responsibility,
        "scope": ("COMM_S2_PINNED_SECTOR_CLOSURE__COMPLETE_LOCAL_DOMAIN_"
                  "DOMINATION__UNIT_SUPPORT_COUNT_OBJECTIVE_ONLY__NOT_R6"),
        "question": ("Does every configuration containing a pinned comm-s2 "
                     "block reduce at Delta <= 0 into D+ u B' u B'' shape or "
                     "get strictly dominated by the family min -- closing "
                     "C_DP == min(C_D+, f_B', f_B'') for all n?"),
        "attack_set": {
            "A1_sharper_exchange": "joint pair/triple re-lettering of the "
                                   "comm-s2 block, the pinning block and the "
                                   "third block plus free tag re-choice at "
                                   "both comm-s2 qubits",
            "A2_domination": "the alternative is the EXACT local optimum of "
                             "the comm-s2-free family, plus the MG mirror "
                             "branch (PRIMARY)",
            "A3_subcase_composition": "double pinners and comm-s2 chains "
                                      "enumerated as geometries; induction on "
                                      "the comm-s2 count",
        },
        "tables": tables,
        "g2_mirror_identity": mirror,
        "g3_gauge_permutations": gauge,
        "inherited_lemmas": inherited,
        "p1_domination_lemma": p1,
        "p2_census_dispatch": p2,
        "p2_state_level_dispatch": p2s,
        "p2_verbatim_dispatch": p2v,
        "p3_hostile_arm": p3,
        "proof_audit": proof_audit,
        "receipt_bindings": bindings,
        "gates": gates,
        "claim_boundary": CLAIM_BOUNDARY,
        "novelty_credit": False,
        "donor_novelty_credit": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
        "reserved_stretched_n2_accessed": False,
        "chemistry_data_read": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG7D authority ceiling violated")
    digest = hashlib.sha256(canonical_json(result).encode()).hexdigest()
    result["result_digest"] = digest

    runtime = round(time.monotonic() - start, 3)
    timing = {
        "convention": ("R6P: timing fields excluded from the canonical stdout "
                       "line and the result digest; present only in this file "
                       "section and on stderr"),
        "section_seconds": seconds,
        "runtime_seconds": runtime,
        "runtime_cap_seconds": RUNTIME_CAP_SECONDS,
        "runtime_under_cap": runtime < RUNTIME_CAP_SECONDS,
    }
    print("ORIONQG_QG7D_LAST_LINK=" + canonical_json(result))
    file_result = dict(result)
    file_result["timing"] = timing
    Path(__file__).with_name("QG7D_LAST_LINK_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n")
    print("qg7d_runtime_seconds=%.3f" % runtime, file=sys.stderr)
    print("qg7d_timing_summary=" + canonical_json(
        {k: v for k, v in timing.items() if k != "convention"}),
        file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
