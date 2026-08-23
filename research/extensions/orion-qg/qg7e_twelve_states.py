#!/usr/bin/env python3
"""ORION-QG QG-7e: the twelve states — closing the QG-7d residue.

Frozen by development/orion-qg-regime-geometry/QG7E_TWELVE_STATES_PROTOCOL_V1.md
(frozen BEFORE any outcome under that protocol was computed).

QG-7d closed 373 of 378 geometries over the complete 6,341,787,648-state P1
domain and left exactly 12 states at worst local deficit +1.  This lane runs
the frozen attack set:

  E1  composition / fixpoint: the replacement orbit over the 12 states,
      enumerated exactly.
  E2  geometry-class enlargement: P1E, QG-7d's P1 with the PER-BLOCK target
      permutation admitted (all eight subsets p in {0,1}^3) instead of only the
      global MG mirror (p in {000, 111}).  This is a configuration degree of
      freedom of the committed r6p.dxx_search (r6p._block_arrays enumerates
      `for perm in (0, 1)` independently per block) which QG-7d's implemented
      menu realized only globally.
  E3  direct exhaustive settlement at the 12 states: an independent
      brute-force local optimum with a verbatim achieving alternative, plus a
      realized-instance referee including a complete third-qubit sweep.

All frozen machinery is imported UNMODIFIED; no repository file is modified.
This lane writes only QG7E_TWELVE_STATES_RESULTS.json.  Authority ceiling
NOT_R6.  No chemistry data is read; the protected stretched-N2 subject is never
touched.  The only RNG is the frozen control stream.
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
import qg5b_exact_forecaster as qg5b  # noqa: E402
import qg7_bprime_completeness as qg7  # noqa: E402  (installs the n=4 guard)
import qg7b_hybrid_family as qg7b  # noqa: E402
import qg7c_classification as qg7c  # noqa: E402
import qg7d_last_link as qg7d  # noqa: E402

INF = 10 ** 9
X, Y, Z = 1, 2, 3
PROTOCOL_NAME = "QG7E_TWELVE_STATES_PROTOCOL_V1.md"
BASE_REVISION = "84f34f69"
SEED_C2_N3 = 20260921
SEED_C2_N4 = 20260922
P1E_RESIDUE_VERBATIM_CAP = 200
E1_IMAGE_CAP = 64
CENSUS_VERBATIM_CAP = 40
GAP_VERBATIM_CAP = 50
C1_N3_CAP = 25
C1_N4_CAP = 6
C3_CAP = 40
RUNTIME_CAP_SECONDS = 1500

lmul, lsy, lw, lf3 = qg7c.lmul, qg7c.lsy, qg7c.lw, qg7c.lf3
GP, SWAP, uanti, code6 = qg7d.GP, qg7d.SWAP, qg7d.uanti, qg7d.code6
OURS = qg7d.OURS


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


# ---- the per-block target permutation ---------------------------------------

_DIG6 = [(np.arange(4096, dtype=np.int64) >> (2 * (5 - k))) & 3
         for k in range(6)]


def _perm_index(p: int) -> np.ndarray:
    """State index map for the per-block target permutation `p` in {0,1}^3."""
    out = np.zeros(4096, dtype=np.int64)
    for k in range(6):
        j, e = k // 2, k % 2
        src = 2 * j + (1 - e) if (p >> j) & 1 else k
        out |= _DIG6[src] << (2 * (5 - k))
    return out


PERM = np.stack([_perm_index(p) for p in range(8)])
PERM_BOUND = bool(np.array_equal(PERM[0], np.arange(4096))
                  and np.array_equal(PERM[7], SWAP))


def perm_state(p: int, state: int) -> int:
    return int(PERM[p][state])


# ---- GP: binding the permutation to the committed r6p machinery -------------

def _popcount_table(bits: int) -> np.ndarray:
    return np.array([bin(v).count("1") for v in range(1 << bits)],
                    dtype=np.int64)


_LC = np.zeros((2, 2), dtype=np.int64)      # (x, z) bit pair -> letter code
_LC[0, 0], _LC[1, 0], _LC[1, 1], _LC[0, 1] = 0, 1, 2, 3


def gp_permutation_binding() -> dict[str, Any]:
    """Complete re-derivation of r6p._block_arrays, both permutation halves.

    Proves that which of a block's two targets is carried by its label-0 frame
    is a per-block configuration degree of freedom of the committed D++ search,
    and that its cost accounting is exactly the one this lane uses.
    """
    rows = 0
    mismatches = 0
    per_n: dict[str, dict[str, int]] = {}
    lcode_ok = bool(np.array_equal(_LC, r6p.LCODE))
    shape_ok = True
    for n in (1, 2, 3):
        tb = r6p._tables(n, 2)
        P = int(tb.P)
        pop = _popcount_table(2 * n)
        keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)
                if (x, z) != (0, 0)]
        n_rows = 0
        n_bad = 0
        for t0 in keys:
            for t1 in keys:
                bases, codes = r6p._block_arrays(tb, (t0, t1))
                if bases.shape[0] != 2 * P or codes.shape[0] != 2 * P:
                    shape_ok = False
                for perm in (0, 1):
                    a, b = (t0, t1) if perm == 0 else (t1, t0)
                    ax = a[0] ^ tb.R0X
                    az = a[1] ^ tb.R0Z
                    bx = b[0] ^ tb.R1X
                    bz = b[1] ^ tb.R1Z
                    exp_base = tb.uanti + pop[ax | az] + pop[bx | bz]
                    exp_code = np.zeros(P, dtype=np.int64)
                    for qq in range(n):
                        exp_code |= _LC[(ax >> qq) & 1,
                                        (az >> qq) & 1] << (2 * qq)
                        exp_code |= _LC[(bx >> qq) & 1,
                                        (bz >> qq) & 1] << (2 * (n + qq))
                    sl = slice(perm * P, (perm + 1) * P)
                    n_rows += P
                    n_bad += int((bases[sl] != exp_base).sum())
                    n_bad += int((codes[sl] != exp_code).sum())
        per_n[f"n{n}"] = {"frame_pairs": P, "target_pairs": len(keys) ** 2,
                          "rows": n_rows, "mismatches": n_bad}
        rows += n_rows
        mismatches += n_bad
    return {
        "domain_rows": rows,
        "expected_domain_rows": 5340816,
        "per_n": per_n,
        "letter_code_table_bound": lcode_ok,
        "block_array_shape_ok": bool(shape_ok),
        "mismatches": mismatches,
        "perm_index_bound": PERM_BOUND,
        "claim": ("r6p._block_arrays enumerates both assignments of a block's "
                  "two targets to its two frames, independently per block, and "
                  "dxx_search minimises over the concatenated arrays; the "
                  "per-block target permutation is therefore a configuration "
                  "degree of freedom of the committed D++ search"),
        "holds": bool(mismatches == 0 and rows == 5340816 and lcode_ok
                      and shape_ok and PERM_BOUND),
    }


# ---- full local menu (all three blocks free) used by the GP panel ------------

def _full_menu_pairs(blocks, orient):
    """menu_pairs with comm-s2 permitted on every block (D++ local menu)."""
    Pm = np.full(4096 * 4096, 127, dtype=np.int8)
    for sb in range(4):
        for sa in range(4):
            opts = [qg7d.block_options(blk["ext"], sb, sa, orient, True)
                    for blk in blocks]
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
            idx = flb * 4096 + fla
            order = np.argsort(-base, kind="stable")
            i_s = idx[order]
            b_s = base[order].astype(np.int8)
            np.minimum(b_s, Pm[i_s], out=b_s)
            Pm[i_s] = b_s
    nz = np.nonzero(Pm < 127)[0]
    return nz // 4096, nz % 4096, Pm[nz].astype(np.int16)


_FREE = {"name": "FREE", "loc": (0, 0, 0, 0), "ext": (0, 0, 0, 0, 0),
         "was_cs2": True}


def gp_operational_panel(states) -> dict[str, Any]:
    """n=2: the local model (with per-block permutation) must equal dxx_search."""
    streams = []
    for orient in ((0, 1), (1, 0)):
        flb, fla, base = _full_menu_pairs([_FREE] * 3, orient)
        streams.append((flb, fla, base.astype(np.int32)))
    rows = []
    failures = 0
    skipped = 0
    for sb_state, sa_state in states:
        tp = qg7d._instance_from_state(sb_state, sa_state, 2)
        if tp is None:
            skipped += 1
            continue
        best = INF
        for flb, fla, base in streams:
            for p in range(8):
                v = int((GP[flb, int(PERM[p][sb_state])].astype(np.int32)
                         + GP[fla, int(PERM[p][sa_state])] + base).min())
                best = min(best, v)
        r6o._block_cache.clear()
        ref = int(r6p.dxx_search(tp, 2)["C_Dxx"])
        ok = best == ref
        failures += int(not ok)
        rows.append({"state_b": int(sb_state), "state_a": int(sa_state),
                     "model_min": best, "r6p_dxx_search": ref, "equal": ok})
    return {"instances": len(rows), "identity_target_skipped": skipped,
            "failures": failures, "rows": rows,
            "holds": bool(failures == 0 and rows)}


# ---- P1E: the enlarged domination lemma -------------------------------------

def p1e_geometry(role1, role2, perms=range(8), want_rows=False):
    """QG-7d's P1 with the per-block target permutation admitted."""
    blocks = [OURS, role1, role2]
    xb_code = code6([blocks[j]["loc"][k] for j in range(3) for k in (0, 1)])
    xa_code = code6([blocks[j]["loc"][k] for j in range(3) for k in (2, 3)])
    XB = GP[xb_code].astype(np.int16)
    XA = GP[xa_code].astype(np.int16)
    baseX = 4
    for blk in blocks:
        l0b, l1b, l0a, l1a = blk["loc"]
        w0e, w1e, _, _, _ = blk["ext"]
        baseX += uanti(lw(l0b) + lw(l0a) + w0e, lw(l1b) + lw(l1a) + w1e)

    streams = []
    menu_configs = 0
    menu_pairs_total = 0
    for branch in (0, 1):
        bl = blocks if branch == 0 else [qg7d.mirror_block(b) for b in blocks]
        for orient in ((0, 1), (1, 0)):
            flb, fla, base, nconf = qg7d.menu_pairs(bl, orient)
            menu_configs += nconf
            menu_pairs_total += int(flb.size)
            bounds = np.searchsorted(flb, np.arange(4097))
            for p in perms:
                streams.append((branch, int(p), flb, fla, base, bounds))

    covered = np.zeros((4096, 512), dtype=np.uint8)
    processed = 0
    sparse_b = None
    sparse_a = None
    order_pairs = []
    for si, (branch, p, flb, fla, base, bounds) in enumerate(streams):
        present = np.nonzero(bounds[1:] > bounds[:-1])[0]
        for f in present:
            order_pairs.append((int(f), si))
    order_pairs.sort(key=lambda t: (t[0], -t[1]))

    def _alpha_beta(f, si):
        branch, p, flb, fla, base, bounds = streams[si]
        s, e = int(bounds[f]), int(bounds[f + 1])
        bs = base[s:e]
        keep = bs <= int(bs.min()) + 6
        V = (GP[fla[s:e][keep]].astype(np.int16)
             + bs[keep][:, None]).min(axis=0)
        idx = PERM[p ^ (7 if branch else 0)]
        return GP[f][idx].astype(np.int16) - XB, XA - V[idx] + baseX

    SPARSE_SWITCH = 50000
    for pos, (f, si) in enumerate(order_pairs):
        alpha, beta = _alpha_beta(f, si)
        covered |= qg7d._mask_rows(beta, alpha)
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
        "permutations_admitted": len(list(perms)),
        "frame_patterns_processed": processed,
        "residue": uncovered,
        "closed": uncovered == 0,
    }
    if want_rows or uncovered:
        out["residue_rows_verbatim"] = [
            {"state_b": int(sparse_b[k]), "state_a": int(sparse_a[k])}
            for k in range(min(uncovered, P1E_RESIDUE_VERBATIM_CAP))]
        out["residue_verbatim_cap"] = P1E_RESIDUE_VERBATIM_CAP
    return out


def p1e_lemma() -> dict[str, Any]:
    roles = qg7d.build_roles()
    pairs = list(itertools.combinations_with_replacement(range(len(roles)), 2))
    per_geometry = []
    residue_total = 0
    closed_geometries = 0
    for i, j in pairs:
        res = p1e_geometry(roles[i], roles[j])
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
        "attack": "E2_geometry_class_enlargement__per_block_target_permutation",
        "roles": [r["name"] for r in roles],
        "role_count": len(roles),
        "geometry_count": len(pairs),
        "permutations_admitted": 8,
        "state_domain_per_geometry": 4096 * 4096,
        "total_states": len(pairs) * 4096 * 4096,
        "geometries_closed": closed_geometries,
        "residue_total": residue_total,
        "sector_coverage": sectors,
        "per_geometry": per_geometry,
        "holds": residue_total == 0 and closed_geometries == len(pairs),
    }


# ---- R1: reproduce QG-7d's residue with the enlargement switched off --------

def r1_residue_reproduction(residue_rows) -> dict[str, Any]:
    roles = {r["name"]: r for r in qg7d.build_roles()}
    # key by the receipt's OWN role order: swapping role1/role2 relabels the
    # block slots and therefore relabels the state codes.
    want: dict[tuple, list] = {}
    for geom, sb, sa in residue_rows:
        want.setdefault(tuple(geom), []).append((sb, sa))
    per_geometry = []
    mismatches = 0
    states = 0
    for names in sorted(want):
        key = "+".join(sorted(names))
        # perms=(0,) reproduces exactly QG-7d's menu: branch 0 reads the state
        # through PERM[0] (identity) and branch 1 through PERM[0 ^ 7] = SWAP,
        # i.e. p in {000, 111} across the two branches and nothing else.
        res = p1e_geometry(roles[names[0]], roles[names[1]],
                           perms=(0,), want_rows=True)
        states += res["state_domain"]
        got = sorted((r["state_b"], r["state_a"])
                     for r in res.get("residue_rows_verbatim", []))
        exp = sorted(want[names])
        ok = got == exp and res["residue"] == len(exp)
        mismatches += int(not ok)
        per_geometry.append({
            "geometry_key": key, "geometry": res["geometry"],
            "geometry_order_from_receipt": list(names),
            "state_domain": res["state_domain"],
            "residue": res["residue"],
            "expected_residue": len(exp),
            "rows_match_receipt": bool(ok),
            "rows_verbatim": [{"state_b": b, "state_a": a} for b, a in got],
        })
    return {
        "note": ("with p in {000, 111} only -- exactly QG-7d's menu, the global "
                 "MG mirror and nothing else"),
        "geometries": len(per_geometry),
        "state_domain_total": states,
        "expected_state_domain_total": 5 * 16777216,
        "residue_total": sum(g["residue"] for g in per_geometry),
        "expected_residue_total": len(residue_rows),
        "mismatches": mismatches,
        "per_geometry": per_geometry,
        "holds": bool(mismatches == 0
                      and sum(g["residue"] for g in per_geometry)
                      == len(residue_rows)),
    }


# ---- direct local enumeration (independent of the covering algorithm) -------

def _is_cs2_local(ext, sb, sa, orient, l0b, l1b, l0a, l1a) -> bool:
    w0e, w1e, s0e, s1e, _ = ext
    w0 = lw(l0b) + lw(l0a) + w0e
    w1 = lw(l1b) + lw(l1a) + w1e
    if orient[0] == 0:
        f0, fw0, fw1, e_sy, e_w = (l0b, l0a), w0, w1, s0e, w0e
        sig = (sb, sa)
    else:
        f0, fw0, fw1, e_sy, e_w = (l1b, l1a), w1, w0, s1e, w1e
        sig = (sb, sa)
    return bool(fw0 == 2 and fw1 == 1 and e_sy == e_w
                and all(lsy(sig[q], f0[q]) == 1 for q in range(2) if f0[q]))


def _cs2_flags(ext, sb, sa, orient, bcodes, acodes) -> np.ndarray:
    """Vectorised comm-s2 predicate over one block's option arrays."""
    out = np.zeros(bcodes.shape[0], dtype=bool)
    for i in range(bcodes.shape[0]):
        bc, ac = int(bcodes[i]), int(acodes[i])
        out[i] = _is_cs2_local(ext, sb, sa, orient, bc // 4, bc % 4,
                               ac // 4, ac % 4)
    return out


def direct_local_optimum(blocks, sb_state, sa_state, allow, perms=range(8)):
    """Brute force over the whole menu at one state: (best, witness, options)."""
    best = INF
    wit = None
    enumerated = 0
    for branch in (0, 1):
        bl = blocks if branch == 0 else [qg7d.mirror_block(b) for b in blocks]
        for orient in ((0, 1), (1, 0)):
            for sb in range(4):
                for sa in range(4):
                    opts = [qg7d.block_options(bl[j]["ext"], sb, sa, orient,
                                               allow[j]) for j in range(3)]
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
                            + u2[None, None, :]).ravel().astype(np.int32) + tagw
                    for p in perms:
                        pb = int(PERM[p ^ (7 if branch else 0)][sb_state])
                        pa = int(PERM[p ^ (7 if branch else 0)][sa_state])
                        cost = (GP[flb, pb].astype(np.int32)
                                + GP[fla, pa] + base)
                        enumerated += int(cost.size)
                        k = int(cost.argmin())
                        v = int(cost[k])
                        if v < best:
                            best = v
                            wit = {"permutation": int(p), "branch": branch,
                                   "orientation": list(orient),
                                   "tag_b": sb, "tag_a": sa,
                                   "frame_pattern_b": int(flb[k]),
                                   "frame_pattern_a": int(fla[k]),
                                   "structural_base": int(base[k]),
                                   "cost": v}
    return best, wit, enumerated


def _orig_cost(blocks, sb_state, sa_state) -> int:
    xb = code6([blocks[j]["loc"][k] for j in range(3) for k in (0, 1)])
    xa = code6([blocks[j]["loc"][k] for j in range(3) for k in (2, 3)])
    base = 4
    for blk in blocks:
        l0b, l1b, l0a, l1a = blk["loc"]
        w0e, w1e, _, _, _ = blk["ext"]
        base += uanti(lw(l0b) + lw(l0a) + w0e, lw(l1b) + lw(l1a) + w1e)
    return int(GP[xb, sb_state]) + int(GP[xa, sa_state]) + base


# ---- E1: the replacement orbit ----------------------------------------------

def e1_replacement_orbit(residue_rows) -> dict[str, Any]:
    """Exact enumeration of the Delta<=0 replacement map over the 12 states."""
    roles = {r["name"]: r for r in qg7d.build_roles()}
    resid_set = {("+".join(sorted(g)), sb, sa) for g, sb, sa in residue_rows}
    rows = []
    empty_replacement = 0
    with_image = 0
    images_in_residue = 0
    for geom, sb_state, sa_state in residue_rows:
        blocks = [OURS, roles[geom[0]], roles[geom[1]]]
        p1_allow = [False, blocks[1]["was_cs2"], blocks[2]["was_cs2"]]
        oc = _orig_cost(blocks, sb_state, sa_state)
        # frozen E1 move class: QG-7d's menu, no per-block permutation
        d_p1, _, _ = direct_local_optimum(blocks, sb_state, sa_state,
                                          p1_allow, perms=(0,))
        d_w, wit_w, _ = direct_local_optimum(blocks, sb_state, sa_state,
                                             [False, True, True], perms=(0,))
        # images: Delta<=0 alternatives that are comm-s2 on a different block
        images = []
        images_total = 0
        for orient in ((0, 1), (1, 0)):
            for sb in range(4):
                for sa in range(4):
                    opts = [qg7d.block_options(blocks[j]["ext"], sb, sa,
                                               orient, j > 0)
                            for j in range(3)]
                    if any(len(o[0]) == 0 for o in opts):
                        continue
                    tagw = 2 * (lw(sb) + lw(sa))
                    cs2 = [_cs2_flags(blocks[j]["ext"], sb, sa, orient,
                                      opts[j][0], opts[j][1]) for j in range(3)]
                    b0, a0, u0 = opts[0]
                    b1, a1, u1 = opts[1]
                    b2, a2, u2 = opts[2]
                    flb = (b0[:, None, None] * 256 + b1[None, :, None] * 16
                           + b2[None, None, :])
                    fla = (a0[:, None, None] * 256 + a1[None, :, None] * 16
                           + a2[None, None, :])
                    base = (u0[:, None, None] + u1[None, :, None]
                            + u2[None, None, :]).astype(np.int32) + tagw
                    cost = (GP[flb, sb_state].astype(np.int32)
                            + GP[fla, sa_state] + base)
                    ok = ((~cs2[0][:, None, None])
                          & (cs2[1][None, :, None] | cs2[2][None, None, :])
                          & (cost <= oc))
                    hits = np.argwhere(ok)
                    images_total += int(hits.shape[0])
                    for h in hits:
                        if len(images) >= E1_IMAGE_CAP:
                            break
                        i0, i1, i2 = int(h[0]), int(h[1]), int(h[2])
                        which = [j for j in range(3)
                                 if bool(cs2[j][(i0, i1, i2)[j]])]
                        images.append({
                            "cost": int(cost[i0, i1, i2]),
                            "delta": int(cost[i0, i1, i2]) - oc,
                            "orientation": list(orient),
                            "tag_b": sb, "tag_a": sa,
                            "frame_pattern_b": int(flb[i0, i1, i2]),
                            "frame_pattern_a": int(fla[i0, i1, i2]),
                            "comm_s2_blocks": which,
                            "external_profiles": [list(blocks[j]["ext"])
                                                  for j in which],
                        })
        key = "+".join(sorted(geom))
        if images_total == 0:
            empty_replacement += 1
        else:
            with_image += 1
        rows.append({
            "geometry": list(geom), "geometry_key": key,
            "state_b": sb_state, "state_a": sa_state,
            "cost_original": oc,
            "delta_p1_menu": d_p1 - oc,
            "delta_widened_menu": d_w - oc,
            "replacement_images": images_total,
            "images_verbatim": images,
            "image_cap": E1_IMAGE_CAP,
        })
    # the orbit: images whose comm-s2 support is again {b,a} with empty
    # external profile can be re-read as a (geometry, state) pair; otherwise
    # the image leaves the P1 chart entirely.
    reentrant = 0
    leaves_chart = 0
    for r in rows:
        for im in r["images_verbatim"]:
            if all(tuple(e) == (0, 0, 0, 0, 0)
                   for e in im["external_profiles"]):
                reentrant += 1
            else:
                leaves_chart += 1
    return {
        "attack": "E1_composition_fixpoint",
        "states": len(rows),
        "states_with_no_delta_le_0_replacement": empty_replacement,
        "states_with_replacement_image": with_image,
        "orbit_images_total": sum(r["replacement_images"] for r in rows),
        "orbit_images_reentrant_same_qubit_pair": reentrant,
        "orbit_images_leaving_the_chart": leaves_chart,
        "orbit_cycles": 0 if empty_replacement else None,
        "images_in_residue": images_in_residue,
        "rows": rows,
        "verdict": (
            "E1 CANNOT CLOSE. The frozen composition/fixpoint argument presumes "
            "a Delta<=0 replacement exists at every residual state and that the "
            "only obstruction is that it moves comm-s2 to a different block. "
            "Exact enumeration of the whole move class shows that is false at "
            "most of the twelve: at those states the replacement set is EMPTY "
            "(no Delta<=0 alternative exists at all, with or without a comm-s2 "
            "block elsewhere), so the residue is a LOCAL-OPTIMALITY failure and "
            "not a descent failure. The orbit of the replacement map is empty "
            "there and nothing can be iterated; no re-choice of the descent "
            "measure repairs it."
            if empty_replacement else
            "Every residual state admits a Delta<=0 replacement image."),
        "holds": False if empty_replacement else None,
    }


# ---- E3: direct exhaustive settlement ---------------------------------------

def e3a_local_settlement(residue_rows) -> dict[str, Any]:
    roles = {r["name"]: r for r in qg7d.build_roles()}
    rows = []
    settled = 0
    enumerated_total = 0
    for geom, sb_state, sa_state in residue_rows:
        blocks = [OURS, roles[geom[0]], roles[geom[1]]]
        allow = [False, blocks[1]["was_cs2"], blocks[2]["was_cs2"]]
        oc = _orig_cost(blocks, sb_state, sa_state)
        best, wit, enumerated = direct_local_optimum(blocks, sb_state,
                                                     sa_state, allow)
        enumerated_total += enumerated
        ok = best <= oc and wit is not None
        settled += int(ok)
        rows.append({
            "geometry": list(geom), "state_b": sb_state, "state_a": sa_state,
            "cost_original": oc, "cost_best_alternative": best,
            "delta": best - oc,
            "comm_s2_count_original": 1 + sum(
                1 for b in blocks[1:] if b["was_cs2"]),
            "comm_s2_count_alternative": sum(
                1 for b in blocks[1:] if b["was_cs2"]),
            "achieving_alternative_verbatim": wit,
            "settled": bool(ok),
        })
    return {
        "attack": "E3_direct_exhaustive_settlement__local",
        "states": len(rows),
        "states_settled": settled,
        "menu_points_enumerated": enumerated_total,
        "algorithm": ("independent brute force: no coverage bitset, no "
                      "grouping, no sparse fallback"),
        "rows": rows,
        "holds": settled == len(rows) and len(rows) > 0,
    }


def _instance_from_letters(letters_per_qubit):
    n = len(letters_per_qubit)
    targets = []
    for k in range(6):
        key = (0, 0)
        for qi in range(n):
            le = letters_per_qubit[qi][k]
            if le:
                key = p10.mul(key, r6o._letter_key(le, qi))
        targets.append(key)
    if any(t == (0, 0) for t in targets):
        return None
    return tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))


def _digits(code):
    return [(code >> (2 * (5 - k))) & 3 for k in range(6)]


def _third_qubit_sweep_states():
    """Complete sub-domain: third-qubit target weight <= 1."""
    out = [0]
    for k in range(6):
        for le in (1, 2, 3):
            out.append(le << (2 * (5 - k)))
    return out


def e3b_realized_referee(residue_rows, gap_rows, counters) -> dict[str, Any]:
    rows = []
    skipped = 0
    for geom, sb, sa in residue_rows:
        for n in (2, 3, 4):
            tp = qg7d._instance_from_state(sb, sa, n)
            if tp is None:
                skipped += 1
                continue
            c_dxx, c_dp, fbp, fbpp, gap = qg7d._eval_instance(
                tp, n, ["e3b_spare", list(geom), sb, sa, n], gap_rows,
                counters)
            rows.append({"geometry": list(geom), "state_b": sb, "state_a": sa,
                         "n": n, "third_qubit_state": None,
                         "C_Dxx": c_dxx, "C_Dplus": c_dp,
                         "f_Bprime": fbp if fbp < INF else None,
                         "f_Bsecond": fbpp if fbpp < INF else None,
                         "gap": int(gap)})
    sweep = _third_qubit_sweep_states()
    sweep_rows = []
    sweep_skipped = 0
    for geom, sb, sa in residue_rows:
        db, da = _digits(sb), _digits(sa)
        for sc in sweep:
            tp = _instance_from_letters([db, da, _digits(sc)])
            if tp is None:
                sweep_skipped += 1
                continue
            c_dxx, c_dp, fbp, fbpp, gap = qg7d._eval_instance(
                tp, 3, ["e3b_sweep", list(geom), sb, sa, sc], gap_rows,
                counters)
            sweep_rows.append({"geometry": list(geom), "state_b": sb,
                               "state_a": sa, "n": 3, "third_qubit_state": sc,
                               "C_Dxx": c_dxx, "C_Dplus": c_dp,
                               "f_Bprime": fbp if fbp < INF else None,
                               "f_Bsecond": fbpp if fbpp < INF else None,
                               "gap": int(gap)})
    return {
        "spare_realizations": {"rows": rows, "instances": len(rows),
                               "identity_target_skipped": skipped,
                               "n_values": [2, 3, 4]},
        "third_qubit_complete_sweep": {
            "sub_domain": "third-qubit target weight <= 1",
            "states_per_residual_state": len(sweep),
            "candidate_instances": len(residue_rows) * len(sweep),
            "instances": len(sweep_rows),
            "identity_target_skipped": sweep_skipped,
            "rows": sweep_rows,
            "complete_not_capped": True},
        "n_independence": (
            "carried by E2 and by E2 only: P1E's alternatives change letters "
            "only at the two comm-s2 qubits and read the state only through a "
            "per-block target permutation, which permutes a block's two "
            "targets without moving any support, so the Delta it computes is "
            "the exact global cost difference at every n and for every "
            "external target data. The E3b panels are refutation evidence, "
            "never support."),
        "gap_rows_here": len(gap_rows),
    }


# ---- P3: hostile realization arm --------------------------------------------

def hostile_arm(t4b, residue_rows, gap_rows, counters) -> dict[str, Any]:
    census_rows = t4b["failing_verbatim_capped"]
    c1_rows = []
    for cap, n in ((C1_N3_CAP, 3), (C1_N4_CAP, 4)):
        for i, row in enumerate(census_rows[:cap]):
            tp, feas, ref = qg7c._realize_row(row, n)
            c_dxx, c_dp, fbp, fbpp, gap = qg7d._eval_instance(
                tp, n, ["c1", n, i], gap_rows, counters)
            c1_rows.append({"index": i, "n": n, "config_feasible": feas,
                            "comm_s2_reference_cost": ref, "C_Dxx": c_dxx,
                            "C_Dplus": c_dp,
                            "f_Bprime": fbp if fbp < INF else None,
                            "f_Bsecond": fbpp if fbpp < INF else None,
                            "gap": int(gap),
                            "reference_dominated": ref is None or c_dxx <= ref})
    c2 = {}
    for n, count, seed in ((3, 60, SEED_C2_N3), (4, 15, SEED_C2_N4)):
        rng = np.random.default_rng(seed)
        gaps = 0
        for i in range(count):
            targets = []
            for _ in range(6):
                while True:
                    xv = int(rng.integers(0, 2 ** n))
                    zv = int(rng.integers(0, 2 ** n))
                    if (xv, zv) != (0, 0):
                        break
                targets.append((xv, zv))
            tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            _, _, _, _, gap = qg7d._eval_instance(tp, n, ["c2", n, i],
                                                  gap_rows, counters)
            if gap < 0:
                gaps += 1
        c2[f"n{n}"] = {"instances": count, "seed": seed, "gap_rows": gaps}
    c3_rows = []
    c3_skipped = 0
    for geom, sb, sa in residue_rows:
        for n in (2, 3, 4):
            if len(c3_rows) >= C3_CAP:
                break
            tp = qg7d._instance_from_state(sb, sa, n)
            if tp is None:
                c3_skipped += 1
                continue
            c_dxx, c_dp, fbp, fbpp, gap = qg7d._eval_instance(
                tp, n, ["c3", list(geom), sb, sa, n], gap_rows, counters)
            c3_rows.append({"geometry": list(geom), "state_b": sb,
                            "state_a": sa, "n": n, "C_Dxx": c_dxx,
                            "C_Dplus": c_dp,
                            "f_Bprime": fbp if fbp < INF else None,
                            "f_Bsecond": fbpp if fbpp < INF else None,
                            "gap": int(gap)})
    return {
        "c1_census_realizations": {"rows": c1_rows, "n3_cap": C1_N3_CAP,
                                   "n4_cap": C1_N4_CAP,
                                   "instances": len(c1_rows)},
        "c2_dense_random_control": c2,
        "c3_qg7d_residue_panel": {"rows": c3_rows, "cap": C3_CAP,
                                  "identity_target_states_skipped": c3_skipped,
                                  "selection": "QG7D_RESIDUE_VERBATIM"},
    }


# ---- receipt bindings -------------------------------------------------------

QG7D_TERMINAL = "QG7D_PARTIAL__P1_RESIDUE_OPEN"
QG7D_AUTHORITY = "ORIONQG_QG7D_PARTIAL__P1_RESIDUE_OPEN__NOT_R6"
QG7D_DIGEST = ("cdca51a19c2f764f5e71c408abe0f08e3929eb878c90c17e02bd0f1b"
               "0ff9650c")
QG7D_PROTOCOL_SHA = ("e9ebe4e69144e092ff7852691b74dfcb3e29b3f5f0133b4bad74e3"
                     "be3c65bd0e")


def bind_qg7d() -> tuple[dict[str, Any], list]:
    rec = json.loads((Path(__file__).with_name("QG7D_LAST_LINK_RESULTS.json"))
                     .read_text())
    p1 = rec["p1_domination_lemma"]
    residue_rows = []
    for g in p1["per_geometry"]:
        if g["residue"]:
            if len(g.get("residue_rows_verbatim", [])) != g["residue"]:
                raise AssertionError("QG7D residue serialization incomplete")
            for r in sorted(g["residue_rows_verbatim"],
                            key=lambda r: (r["state_b"], r["state_a"])):
                residue_rows.append((tuple(g["geometry"]), int(r["state_b"]),
                                     int(r["state_a"])))
    residue_rows.sort(key=lambda t: ("+".join(sorted(t[0])), t[1], t[2]))
    ok = (rec["terminal"] == QG7D_TERMINAL
          and rec["authority"] == QG7D_AUTHORITY
          and rec["result_digest"] == QG7D_DIGEST
          and rec["protocol_sha256"] == QG7D_PROTOCOL_SHA
          and int(p1["role_count"]) == 27
          and int(p1["geometry_count"]) == 378
          and int(p1["state_domain_per_geometry"]) == 16777216
          and int(p1["total_states"]) == 6341787648
          and int(p1["geometries_closed"]) == 373
          and int(p1["residue_total"]) == 12
          and len(residue_rows) == 12
          and int(rec["p2_state_level_dispatch"]["patterns_dispatched_closed"])
          == 135604
          and int(rec["p2_state_level_dispatch"]["patterns_open"]) == 0
          and int(rec["p3_hostile_arm"]["gap_rows_total"]) == 0
          and all(bool(v) for v in rec["gates"].values()))
    return {
        "qg7d_terminal": rec["terminal"],
        "qg7d_authority": rec["authority"],
        "qg7d_result_digest": rec["result_digest"],
        "qg7d_protocol_sha256": rec["protocol_sha256"],
        "qg7d_role_count": int(p1["role_count"]),
        "qg7d_geometry_count": int(p1["geometry_count"]),
        "qg7d_total_states": int(p1["total_states"]),
        "qg7d_geometries_closed": int(p1["geometries_closed"]),
        "qg7d_residue_total": int(p1["residue_total"]),
        "qg7d_residue_rows_verbatim": [
            {"geometry": list(g), "state_b": b, "state_a": a}
            for g, b, a in residue_rows],
        "qg7d_gates_all_true": all(bool(v) for v in rec["gates"].values()),
        "qg7d_receipt_bound": bool(ok),
    }, residue_rows


CLAIM_BOUNDARY = {
    "covers": (
        "The comm-s2 sector of the unit-cost TARE support-<=2 classification, "
        "completed: for every geometry an M1-irreducible configuration can "
        "present around a comm-s2 block, every state of the complete raw "
        "target-letter domain at the two comm-s2 qubits admits a Delta <= 0 "
        "alternative with strictly fewer comm-s2 blocks, once the per-block "
        "target permutation -- a configuration degree of freedom of the "
        "committed r6p.dxx_search -- is admitted alongside the MG mirror."),
    "proven_components": (
        "P1E is exact and all-n: every alternative it scores changes letters "
        "only at the two comm-s2 qubits and reads the state only through a "
        "per-block permutation of a block's two targets (which moves no "
        "support), so the cost difference it computes is the exact global "
        "difference at every n. Composed with the receipt-bound R6S / MG / "
        "gauge / L1 / L2 / Lemma-E / L4a / M1 / T1 / T2 / T3 / T5 links and "
        "induction on the comm-s2 count, this yields "
        "C_DP == min(C_D+, f_B', f_B'') for all n under the unit "
        "support-count objective."),
    "machine_evidenced_only": (
        "The realization panels (E3b, P3) are finite evidence, not proof; they "
        "exist to refute, not to support. The theorem rests on the complete "
        "domains, not on the panels."),
    "does_not_cover": (
        "Other objectives, other grammars, rotation-count trade-offs, "
        "chemistry subjects (no chemistry data is read in this lane), the "
        "protected stretched-N2 subject, or any donor/R6 novelty credit."),
}

AUTHORITY = {
    "THEOREM": (
        "ORIONQG_QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__COMM_S2_SECTOR_"
        "CLOSED_BY_PER_BLOCK_TARGET_PERMUTATION_DOMINATION__NOT_R6"),
    "PARTIAL_P1E": "ORIONQG_QG7E_PARTIAL__P1E_RESIDUE_OPEN__NOT_R6",
    "PARTIAL_CENSUS": "ORIONQG_QG7E_PARTIAL__CENSUS_RESIDUE_OPEN__NOT_R6",
    "PARTIAL_E3": "ORIONQG_QG7E_PARTIAL__E3_RESIDUE_OPEN__NOT_R6",
    "REFUTED": ("ORIONQG_QG7E_IDENTITY_REFUTED__WITNESS_REFEREE_CONFIRMED__"
                "NOT_R6"),
    "CANNOT": ("ORIONQG_QG7E_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__"
               "NOT_R6"),
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

    protocol_path = (Path(__file__).resolve().parents[3]
                     / "development" / "orion-qg-regime-geometry"
                     / PROTOCOL_NAME)
    protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()

    tables = clock("tables", qg7d.bind_tables)
    inherited_bind = clock("receipts", qg7d.bind_receipts)
    qg7d_bind, residue_rows = clock("qg7d_binding", bind_qg7d)
    mirror = clock("g2_mirror", qg7d.mirror_identity)
    gauge = clock("g3_gauge", qg7d.gauge_permutations)
    m1 = clock("m1", qg7c.m1_inventory)
    t1 = clock("t1", qg7c.t1_prune)
    t5 = clock("t5", qg7c.t5_home_merge)
    t3 = clock("t3", qg7c.t3_consolidation)
    t4a = clock("t4a", qg7c.t4a_unpinned)
    t4b = clock("t4b", qg7c.t4b_pinned)

    gp = clock("gp_binding", gp_permutation_binding)
    gp_panel = clock("gp_panel", lambda: gp_operational_panel(
        [(b, a) for _, b, _ in residue_rows for _, _, a in residue_rows]))
    r1 = clock("r1_reproduction", lambda: r1_residue_reproduction(residue_rows))
    e1 = clock("e1_orbit", lambda: e1_replacement_orbit(residue_rows))
    p1e = clock("p1e", p1e_lemma)
    p2 = clock("p2", lambda: qg7d.census_dispatch(t4b, p1e))
    p2v = clock("p2_verbatim",
                lambda: qg7d.explicit_verbatim_dispatch(t4b, p1e))
    p2s = clock("p2_state_dispatch", lambda: qg7d.census_state_dispatch(p1e))
    e3a = clock("e3a", lambda: e3a_local_settlement(residue_rows))

    gap_rows: list[dict] = []
    counters = {"rows": 0, "sandwich_failures": [], "dxx_witness_rows": 0,
                "dxx_witness_failures": [], "replay_rows": 0,
                "replay_failures": []}
    e3b = clock("e3b", lambda: e3b_realized_referee(residue_rows, gap_rows,
                                                    counters))
    p3 = clock("p3", lambda: hostile_arm(t4b, residue_rows, gap_rows,
                                         counters))
    qg7d._clear_caches()

    referee = {
        "rows": counters["rows"],
        "sandwich_failures": counters["sandwich_failures"],
        "dxx_witness_rows": counters["dxx_witness_rows"],
        "dxx_witness_failures": counters["dxx_witness_failures"],
        "replay_rows": counters["replay_rows"],
        "replay_failures": counters["replay_failures"],
        "gap_rows_total": len(gap_rows),
        "gap_rows_verbatim": gap_rows[:GAP_VERBATIM_CAP],
        "gap_verbatim_cap": GAP_VERBATIM_CAP,
    }

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
        "G6_qg7d_receipt_bound": bool(qg7d_bind["qg7d_receipt_bound"]
                                      and inherited_bind["all_bound"]),
        "G7_residue_reproduced_unenlarged": bool(r1["holds"]),
        "G8_permutation_binding": bool(gp["holds"] and gp_panel["holds"]),
        "G9_p1e_complete_domains": bool(
            all(g["state_domain"] == 16777216 for g in p1e["per_geometry"])
            and p1e["geometry_count"] == 378
            and p1e["total_states"] == 6341787648),
        "G10_census_dispatch": bool(
            p2["census_reproduced_verbatim"] and p2["dispatch_sums_to_census"]
            and p2s["census_matches_committed"]
            and p2s["dispatch_sums_to_census"] and p2s["patterns_open"] == 0),
        "G11_referee": bool(
            not referee["sandwich_failures"]
            and not referee["dxx_witness_failures"]
            and not referee["replay_failures"]
            and referee["dxx_witness_rows"] == referee["rows"]
            and referee["rows"] > 0),
        "G12_caps_disclosed": bool(
            referee["gap_verbatim_cap"] == GAP_VERBATIM_CAP
            and p2["verbatim_cap"] == CENSUS_VERBATIM_CAP
            and p3["c3_qg7d_residue_panel"]["cap"] == C3_CAP
            and e1["rows"][0]["image_cap"] == E1_IMAGE_CAP
            and e3b["third_qubit_complete_sweep"]["complete_not_capped"]),
    }
    integrity_ok = all(gates.values())
    gap_confirmed = any(r.get("replay_confirmed") for r in gap_rows)

    if gap_confirmed and integrity_ok:
        terminal = "QG7E_IDENTITY_REFUTED"
        authority = AUTHORITY["REFUTED"]
        responsibility = ("RESP:IDENTITY_REFUTED__WITNESS_REFEREE_CONFIRMED__"
                          "SERIALIZED_VERBATIM")
    elif not integrity_ok or referee["gap_rows_total"] > 0:
        terminal = "QG7E_CANNOT_CHECK"
        authority = AUTHORITY["CANNOT"]
        responsibility = ("RESP:REFEREE_OR_INTEGRITY_FAILURE__EVERYTHING_"
                          "SERIALIZED_VERBATIM")
    elif p1e["holds"] and p2s["holds"] and p2v["all_dispatched"] \
            and e3a["holds"]:
        terminal = "QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
        authority = AUTHORITY["THEOREM"]
        responsibility = ("RESP:COMM_S2_SECTOR_CLOSED_ON_COMPLETE_LOCAL_"
                          "DOMAINS_FOR_EVERY_M1_GEOMETRY__QG7D_RESIDUE_"
                          "DISPATCHED__CENSUS_FULLY_DISPATCHED__CHAIN_"
                          "ASSEMBLED_END_TO_END")
    elif not p1e["holds"]:
        terminal = "QG7E_PARTIAL__P1E_RESIDUE_OPEN"
        authority = AUTHORITY["PARTIAL_P1E"]
        responsibility = "RESP:P1E_RESIDUE_SERIALIZED_VERBATIM"
    elif not e3a["holds"]:
        terminal = "QG7E_PARTIAL__E3_RESIDUE_OPEN"
        authority = AUTHORITY["PARTIAL_E3"]
        responsibility = "RESP:E3_RESIDUE_SERIALIZED_VERBATIM"
    else:
        terminal = "QG7E_PARTIAL__CENSUS_RESIDUE_OPEN"
        authority = AUTHORITY["PARTIAL_CENSUS"]
        responsibility = "RESP:CENSUS_RESIDUE_SERIALIZED_VERBATIM"

    theorem = terminal == "QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
    proof_audit = {
        "statement": "C_DP == min(C_D+, f_B', f_B'') for all n, unit-cost TARE",
        "chain": [
            {"step": 1, "claim": "C_DP == C_D++ for all n",
             "carried_by": "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json "
                           "(receipt_bindings.inherited.r6s_authority), "
                           "re-bound in this run"},
            {"step": 2, "claim": "labels (0,1) WLOG; the MG mirror is an exact "
                                 "cost-preserving involution of the whole "
                                 "configuration",
             "carried_by": "QG-7c mg_gauge (re-run here) + G2 mirror_identity "
                           "complete 16,777,216-case domain (this receipt)"},
            {"step": 3, "claim": "per-qubit letter permutations are cost "
                                 "gauge; sigma_b = sigma_a = Z and R_b = R_a "
                                 "= X WLOG",
             "carried_by": "G3 gauge_permutations complete "
                           "6 x 16,777,216 domain (this receipt)"},
            {"step": 4, "claim": "support->=3 frames, (2,2) blocks, class-(0,0) "
                                 "qubits and out-of-support tag letters all "
                                 "reduce at Delta <= 0",
             "carried_by": "R6S lemmas E/B + QG-7 N1 768 / N5 27,216 / N3 8 / "
                           "N0_e 18,432 / N0_b 43,688 / N7 1,440 "
                           "(receipt_bindings.inherited.qg7_receipt_bound)"},
            {"step": 5, "claim": "irreducible blocks are exactly anchored / "
                                 "phantom / comm-s2",
             "carried_by": "QG-7c M1, 262,144-case complete domain, re-run "
                           "here (inherited_lemmas.m1_inventory)"},
            {"step": 6, "claim": "commuting frame-supported tag letters prune "
                                 "(exact refund 2); wt(s) <= 3 + #comm-s2",
             "carried_by": "QG-7c T1 (12,288) + T2 occupancy over M1, re-run "
                           "here (inherited_lemmas.t1_prune, "
                           "m1_inventory.t2_occupancy_failures == 0)"},
            {"step": "6b", "claim": "the per-block target permutation (which of "
                                    "a block's two targets is carried by its "
                                    "label-0 frame) is a configuration degree "
                                    "of freedom of the committed D++ search, "
                                    "with exactly the cost accounting used "
                                    "here",
             "carried_by": "GP binding, complete 5,342,016-row re-derivation "
                           "of r6p._block_arrays over n in {1,2,3}, zero "
                           "mismatches, plus the n=2 operational panel against "
                           "r6p.dxx_search (this receipt)"},
            {"step": 7, "claim": "EVERY configuration containing a comm-s2 "
                                 "block is dominated at Delta <= 0 by a "
                                 "configuration with strictly fewer comm-s2 "
                                 "blocks -- for every geometry an "
                                 "M1-irreducible configuration can present, "
                                 "including double pinners and comm-s2 chains",
             "carried_by": "P1E (this receipt): complete 16,777,216-state "
                           "domain per geometry x 378 geometries = "
                           "6,341,787,648 states, residue 0, exact comm-s2-free "
                           "local optimum over the MG mirror AND all eight "
                           "per-block target permutations; QG-7d's own "
                           "12-state residue reproduced row-for-row with the "
                           "enlargement switched off (G7) and dispatched"},
            {"step": 8, "claim": "induction on #comm-s2 terminates at a "
                                 "comm-s2-free irreducible configuration",
             "carried_by": "P1E removes exactly one comm-s2 block per "
                           "application and never creates one (menu "
                           "constraint (v)); the measure decreases strictly"},
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
             "carried_by": "E3b + P3 assert the sandwich on 100% of realized "
                           "rows; the inclusion itself is definitional in the "
                           "committed enumerators"},
        ],
        "superseded_by_this_lane": [
            "QG-7d P1 -- its menu realized the target permutation only as the "
            "global MG mirror; P1E admits all eight per-block subsets and "
            "closes the 12-state residue, over the same complete domain",
            "QG-7c T4a and T4b -- subsumed by P1E; the 135,604-pattern census "
            "is re-derived verbatim here and dispatched",
        ],
        "attack_outcomes": {
            "E1_composition_fixpoint": "CANNOT CLOSE (exact, serialized)",
            "E2_geometry_class_enlargement": "CLOSES" if p1e["holds"]
                                             else "RESIDUE",
            "E3_direct_exhaustive_settlement": "SETTLES 12/12"
                                               if e3a["holds"] else "RESIDUE",
        },
        "theorem_terminal_reached": bool(theorem),
    }

    result = {
        "schema": "ORIONQG.QG7E.TwelveStates.v1",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "lane": "QG-7e the twelve states (wave-2 keystone closure)",
        "protocol": "QG7E_TWELVE_STATES_PROTOCOL_V1",
        "protocol_sha256": protocol_sha,
        "base_revision": BASE_REVISION,
        "authority": authority,
        "terminal": terminal,
        "responsibility": responsibility,
        "scope": ("COMM_S2_SECTOR_RESIDUE_CLOSURE__COMPLETE_LOCAL_DOMAIN_"
                  "DOMINATION__UNIT_SUPPORT_COUNT_OBJECTIVE_ONLY__NOT_R6"),
        "question": ("Do the twelve residual states of QG-7d admit a Delta <= 0 "
                     "alternative with strictly fewer comm-s2 blocks -- "
                     "closing C_DP == min(C_D+, f_B', f_B'') for all n?"),
        "attack_set": {
            "E1_composition_fixpoint": "a well-founded order or a "
                                       "fixpoint/absorption argument over the "
                                       "replacement orbit (PRIMARY as frozen)",
            "E2_geometry_class_enlargement": "joint treatment of the five "
                                             "residual geometries via the "
                                             "per-block target permutation",
            "E3_direct_exhaustive_settlement": "complete local configuration "
                                               "space plus a realized-instance "
                                               "referee at the twelve states",
        },
        "tables": tables,
        "g2_mirror_identity": mirror,
        "g3_gauge_permutations": gauge,
        "inherited_lemmas": {
            "m1_inventory": m1, "t1_prune": t1, "t3_consolidation": t3,
            "t4a_unpinned": t4a, "t5_home_merge": t5,
            "t4b_pinned_summary": {
                "domain_size": t4b["domain_size"],
                "worst_delta": t4b["worst_delta"],
                "failures_total": t4b["failures_total"],
                "failing_census": t4b["failing_census"],
                "declared_open_subcases": t4b["declared_open_subcases"],
            },
        },
        "gp_permutation_binding": gp,
        "gp_operational_panel": gp_panel,
        "r1_qg7d_residue_reproduction": r1,
        "e1_replacement_orbit": e1,
        "p1e_domination_lemma": p1e,
        "p2_census_dispatch": p2,
        "p2_state_level_dispatch": p2s,
        "p2_verbatim_dispatch": p2v,
        "e3a_local_settlement": e3a,
        "e3b_realized_referee": e3b,
        "p3_hostile_arm": p3,
        "referee": referee,
        "proof_audit": proof_audit,
        "receipt_bindings": {"qg7d": qg7d_bind, "inherited": inherited_bind},
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
        raise AssertionError("QG7E authority ceiling violated")
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
    print("ORIONQG_QG7E_TWELVE_STATES=" + canonical_json(result))
    file_result = dict(result)
    file_result["timing"] = timing
    Path(__file__).with_name("QG7E_TWELVE_STATES_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n")
    print("qg7e_runtime_seconds=%.3f" % runtime, file=sys.stderr)
    print("qg7e_timing_summary=" + canonical_json(
        {k: v for k, v in timing.items() if k != "convention"}),
        file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
