#!/usr/bin/env python3
"""QG-10 independent generic verifier (pure primitives, ACCEPT / REJECT).

Mandated by development/orion-qg-regime-geometry/QG10_INTERVAL_GEOMETRY_PROTOCOL_V1.md
section 6.  This file imports NOTHING from the lane analyzer and NOTHING from
research/extensions/orion-q or research/extensions/orion-qg.  It rebuilds the
frozen unit-cost TARE algebra, the nine-bit acceptance syndrome, the six-bit
QG-10 label-consistency projection, the cost function and the acceptance
predicate from first principles, and then, for every row serialized in
QG10_INTERVAL_GEOMETRY_RESULTS.json:

  1. replays the recorded U witness -- acceptance predicate and cost -- and
     checks that it equals the recorded U;
  2. re-derives L_COL from the instance alone;
  3. re-derives L_SEP as the exact optimum of the projected relaxation;
  4. re-derives C_DP with its own exact nine-bit DP (rows whose referee was
     deliberately withheld are checked for the ABSENCE of a C_DP instead);
  5. re-checks L = max(L_TRIV, L_COL, L_SEP) and the sandwich L <= C_DP <= U.

Any failure prints REJECT.  Only numpy and the standard library are used.
"""
from __future__ import annotations

import collections
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

BIG = 10000
RESULTS = (Path(__file__).resolve().parents[2] / "research" / "extensions"
           / "orion-qg" / "QG10_INTERVAL_GEOMETRY_RESULTS.json")
OUT = Path(__file__).with_name("QG10_GENERIC_VERIFICATION.json")

# ---- primitives -------------------------------------------------------------
# Letter codes: 0 = I, 1 = X, 2 = Y, 3 = Z, matching (x bit, z bit) as
# I=(0,0), X=(1,0), Y=(1,1), Z=(0,1).
BITS = {(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}
CODE = {v: k for k, v in BITS.items()}


def gmul(a: int, b: int) -> int:
    if a == 0:
        return b
    if b == 0:
        return a
    if a == b:
        return 0
    return 6 - a - b


def gsym(a: int, b: int) -> int:
    return 1 if (a != 0 and b != 0 and a != b) else 0


def gwt(a: int) -> int:
    return 0 if a == 0 else 1


def f3(a: int, b: int, c: int) -> int:
    return 1 if (a == b == c != 0) else gwt(a) + gwt(b) + gwt(c)


def letters(key, n: int):
    x, z = int(key[0]), int(key[1])
    return [BITS[((x >> q) & 1, (z >> q) & 1)] for q in range(n)]


def key_wt(key, n: int) -> int:
    return sum(1 for l in letters(key, n) if l)


def symp(a, b, n: int) -> int:
    la, lb = letters(a, n), letters(b, n)
    return sum(gsym(la[q], lb[q]) for q in range(n)) & 1


def config_accepts(frames6, s, n: int):
    for j in range(3):
        if symp(frames6[2 * j], frames6[2 * j + 1], n) != 1:
            return False, None
    l0 = symp(s, frames6[0], n)
    l1 = symp(s, frames6[1], n)
    for j in (1, 2):
        if symp(s, frames6[2 * j], n) != l0 or symp(s, frames6[2 * j + 1], n) != l1:
            return False, None
    if l0 == l1:
        return False, None
    if any(tuple(f) == (0, 0) for f in frames6):
        return False, None
    return True, (l0, l1)


def config_cost(t6, frames6, s, centrals, n: int) -> int:
    total = 0
    for j in range(3):
        m0 = 2 if centrals[j] == 0 else 4
        m1 = 2 if centrals[j] == 1 else 4
        total += m0 * key_wt(frames6[2 * j], n) + m1 * key_wt(frames6[2 * j + 1], n)
    total += 2 * key_wt(s, n)
    u = []
    for i in range(6):
        li = letters(t6[i], n)
        lf = letters(frames6[i], n)
        u.append([gmul(li[q], lf[q]) for q in range(n)])
    for k in (0, 1):
        for q in range(n):
            total += f3(u[k][q], u[2 + k][q], u[4 + k][q])
    return total - 18


# ---- local option tables ----------------------------------------------------
OPT = 4 ** 7
D = [((np.arange(OPT, dtype=np.int64) >> (2 * (6 - t))) & 3) for t in range(7)]
SY = np.array([[gsym(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
LM = np.array([[gmul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
LW = np.array([gwt(a) for a in range(4)], dtype=np.int64)
F3T = np.zeros((4, 4, 4), dtype=np.int64)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            F3T[_a, _b, _c] = f3(_a, _b, _c)
A0, A1, B0, B1, C0, C1, S = D
FULL = ((SY[A0, A1] << 0) | (SY[B0, B1] << 1) | (SY[C0, C1] << 2)
        | ((SY[S, A0] ^ SY[S, B0]) << 3) | ((SY[S, A0] ^ SY[S, C0]) << 4)
        | ((SY[S, A1] ^ SY[S, B1]) << 5) | ((SY[S, A1] ^ SY[S, C1]) << 6)
        | (SY[S, A0] << 7) | (SY[S, A1] << 8))
RED = ((SY[A0, A1] << 0) | (SY[B0, B1] << 1) | (SY[C0, C1] << 2)
       | ((SY[S, A0] ^ SY[S, A1]) << 3) | ((SY[S, B0] ^ SY[S, B1]) << 4)
       | ((SY[S, C0] ^ SY[S, C1]) << 5))
ACC = (0b010000111, 0b100000111)
TAG = 2 * LW[S]
CEN = tuple(itertools.product((0, 1), repeat=3))
PRM = tuple(itertools.product((0, 1), repeat=2))
FR = np.zeros((8, OPT), dtype=np.int64)
for _i, _c in enumerate(CEN):
    _v = np.zeros(OPT, dtype=np.int64)
    for _j, _b in enumerate(_c):
        _v += (2 if _b == 0 else 4) * LW[D[2 * _j]]
        _v += (2 if _b == 1 else 4) * LW[D[2 * _j + 1]]
    FR[_i] = _v
XF = np.bitwise_xor(np.arange(512)[:, None], np.arange(512)[None, :]).astype(np.int32)
XR = np.bitwise_xor(np.arange(64)[:, None], np.arange(64)[None, :]).astype(np.int32)
_tab: dict[tuple, tuple] = {}


def tables(col):
    hit = _tab.get(col)
    if hit is not None:
        return hit
    full = np.full((32, 512), BIG, dtype=np.int16)
    red = np.full((32, 64), BIG, dtype=np.int16)
    for pi, (pb, pc) in enumerate(PRM):
        p6 = (col[0], col[1],
              col[2] if pb == 0 else col[3], col[3] if pb == 0 else col[2],
              col[4] if pc == 0 else col[5], col[5] if pc == 0 else col[4])
        base = (TAG + F3T[LM[p6[0], A0], LM[p6[2], B0], LM[p6[4], C0]]
                + F3T[LM[p6[1], A1], LM[p6[3], B1], LM[p6[5], C1]])
        for ci in range(8):
            cost = (base + FR[ci]).astype(np.int64)
            row = pi * 8 + ci
            f = np.full(512, BIG, dtype=np.int64)
            np.minimum.at(f, FULL, cost)
            full[row] = np.minimum(f, BIG)
            r = np.full(64, BIG, dtype=np.int64)
            np.minimum.at(r, RED, cost)
            red[row] = np.minimum(r, BIG)
    _tab[col] = (full, red)
    return full, red


def conv(a, b, x):
    g = np.take(b, x, axis=1)
    g += a[:, :, None]
    out = g.min(axis=1)
    np.minimum(out, np.int16(BIG), out=out)
    return out


_pw: dict[tuple, tuple] = {}


def power(col, m, which):
    key = (col, m, which)
    hit = _pw.get(key)
    if hit is not None:
        return hit
    x = XF if which == 0 else XR
    if m == 1:
        out = tables(col)[which]
    else:
        h = power(col, m // 2, which)
        out = conv(h, h, x)
        if m % 2:
            out = conv(out, tables(col)[which], x)
    _pw[key] = out
    return out


def columns(t6, n):
    ls = [letters(k, n) for k in t6]
    cnt = collections.Counter()
    for q in range(n):
        cnt[tuple(ls[i][q] for i in range(6))] += 1
    return tuple(sorted(cnt.items()))


def dp_value(cols, which):
    x = XF if which == 0 else XR
    tabs = [power(c, m, which) for c, m in cols]
    acc = tabs[0]
    for t in tabs[1:]:
        acc = conv(acc, t, x)
    if which == 0:
        return int(min(acc[:, ACC[0]].min(), acc[:, ACC[1]].min())) - 18
    return int(acc[:, 0b111111].min()) - 18


def l_col_of(cols) -> int:
    w = 0
    mfree = 0
    for col, m in cols:
        w += m * sum(gwt(x) for x in col)
        for k in (0, 1):
            if col[k] == col[2 + k] == col[4 + k] != 0:
                mfree += m
    return 2 + w - 18 - 2 * mfree


def main() -> int:
    raw = RESULTS.read_bytes()
    rec = json.loads(raw)
    rows = rec["rows_for_generic_verifier"]
    fail: list[Any] = []
    checked = collections.Counter()
    for idx, row in enumerate(rows):
        n = int(row["n"])
        tp = [[tuple(a), tuple(b)] for a, b in row["target_pairs"]]
        t6base = [tp[0][0], tp[0][1], tp[1][0], tp[1][1], tp[2][0], tp[2][1]]
        cols = columns(t6base, n)
        # 1. witness replay
        wit = row["witness"]
        frames6 = [tuple(f) for f in wit["frames6"]]
        wt6 = [tuple(t) for t in wit["t6"]]
        ok, _lab = config_accepts(frames6, tuple(wit["s"]), n)
        cost = config_cost(wt6, frames6, tuple(wit["s"]), tuple(wit["centrals"]), n)
        if not ok or cost != int(wit["value"]) or int(wit["value"]) != int(row["U"]):
            fail.append({"row": idx, "why": "witness_replay", "n": n,
                         "accepted": bool(ok), "cost": cost,
                         "recorded_U": int(row["U"])})
        else:
            checked["witness_replay"] += 1
        # the witness targets must be a per-block permutation of the instance
        for j in range(3):
            pair = {wt6[2 * j], wt6[2 * j + 1]}
            if pair != {tp[j][0], tp[j][1]}:
                fail.append({"row": idx, "why": "witness_targets_not_instance",
                             "n": n})
                break
        # 2/3. lower-bound components
        lcol = l_col_of(cols)
        lsep = dp_value(cols, 1)
        checked["L_SEP_rederived"] += 1
        low = max(2, lcol, lsep)
        comp = row["L_components"]
        if (int(comp["L_COL"]) != lcol or int(comp["L_SEP"]) != lsep
                or int(row["L"]) != low):
            fail.append({"row": idx, "why": "lower_bound_mismatch", "n": n,
                         "mine": {"L_COL": lcol, "L_SEP": lsep, "L": low},
                         "recorded": comp})
        # 4/5. referee and sandwich
        if row["referee"] == "WITHHELD_CERTIFICATION_ONLY":
            if row["C_DP"] is not None:
                fail.append({"row": idx, "why": "withheld_row_carries_C_DP"})
            else:
                checked["certification_only"] += 1
            if not (low <= int(row["U"])):
                fail.append({"row": idx, "why": "interval_inverted", "n": n})
        else:
            cdp = dp_value(cols, 0)
            checked["C_DP_rederived"] += 1
            if cdp != int(row["C_DP"]):
                fail.append({"row": idx, "why": "C_DP_mismatch", "n": n,
                             "mine": cdp, "recorded": int(row["C_DP"])})
            if not (low <= cdp <= int(row["U"])):
                fail.append({"row": idx, "why": "sandwich_violated", "n": n,
                             "L": low, "C_DP": cdp, "U": int(row["U"])})
            else:
                checked["sandwich"] += 1
        if int(row["gap"]) != int(row["U"]) - int(row["L"]):
            fail.append({"row": idx, "why": "gap_field_inconsistent"})
    decision = "ACCEPT" if not fail else "REJECT"
    out = {
        "schema": "ORIONQG.QG10.GenericVerification.v1",
        "decision": decision,
        "results_sha256": hashlib.sha256(raw).hexdigest(),
        "results_terminal": rec["terminal"],
        "rows_examined": len(rows),
        "checks": dict(sorted(checked.items())),
        "failures": len(fail),
        "failures_verbatim": fail[:60],
        "independence": ("no import of the lane analyzer and no import of "
                         "research/extensions/orion-q or "
                         "research/extensions/orion-qg; numpy and the standard "
                         "library only"),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("QG10_GENERIC_VERIFY=" + json.dumps(
        {k: v for k, v in out.items() if k != "failures_verbatim"},
        sort_keys=True, separators=(",", ":")))
    print(decision)
    return 0 if decision == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main())
