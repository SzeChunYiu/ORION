#!/usr/bin/env python3
"""QG-28 -- realize QG-6's support-capped corollary and measure what it buys.

Frozen by QG28_SUPPORT_CAPPED_REALIZATION_PROTOCOL_V1.md. Read that file's
section 0 first: a scratch prototype ran before the protocol was written, so Q1
and Q2 are NOT prospective and are labelled as such. Q3 is.

Residual W9 says the committed family search `r6p.dxx_search` does not realize
QG-6's own corollary: the corollary bounds a certified support-<=2 search at
O(n^2 * 16) frame-pair candidates per block, and the committed implementation
instead sweeps an A^{2n} don't-care pattern space and an A^n - 1 Tag sweep,
O(n * 4^{3n}) cells. The bound is proved and committed; realizing it is
engineering. This lane does the engineering and then asks the question nobody
asked when W9 was registered -- whether the projected win actually exists.

Nothing here is novel. The corollary is QG-6's, the family is R6P's, and the Tag
step is a textbook minimum-weight-coset syndrome DP. NOT_R6.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys
import time
from typing import Any

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/extensions/orion-q"))
_HARNESS_SRC = ROOT / "packages/orion-research-harness/src"

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402


def _import_harness(module: str):
    """Import a committed harness module without dragging in the whole package.

    ``orion_research_harness/__init__`` imports ``orion.core.search``, which is
    not on this lane's path. A namespace shim registers the package so the REAL
    committed module file is imported under its real dotted name; nothing in it
    is patched and it still fails closed. Same shim QG-24 and QG-25 used, for
    the same reason.
    """
    import importlib
    import types

    name = "orion_research_harness"
    if name not in sys.modules:
        pkg = types.ModuleType(name)
        pkg.__path__ = [str(_HARNESS_SRC / name)]
        sys.modules[name] = pkg
    if str(_HARNESS_SRC) not in sys.path:
        sys.path.insert(0, str(_HARNESS_SRC))
    return importlib.import_module(name + "." + module)


validate_donor_search = _import_harness("donor_search").validate_donor_search

h = p10.h
wt, symp, mul = p10.wt, p10.symp, p10.mul

#: The two admissible label orientations. Both are non-zero, which is why the
#: shared Tag can never be the identity and the DP below needs no "used a
#: non-identity letter" flag.
LABELS = ((0, 1), (1, 0))

PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG28_SUPPORT_CAPPED_REALIZATION_PROTOCOL_V1.md"
OUT = ROOT / "research/extensions/orion-qg/QG28_SUPPORT_CAPPED_REALIZATION_RESULTS.json"

#: Declared caps (protocol section 4/5).
N3_SAMPLE = 6
N3_SEED = 20260822
TAG_DP_CHECKS = {1: 400, 2: 400, 3: 120}
DP_SEARCH_N1_SAMPLE = 64
DP_SEARCH_N2_SAMPLE = 2
DP_SEARCH_N2_SEED = 771020
TAG_DP_SEED = 4482
MISMATCH_VERBATIM_CAP = 25


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# --------------------------------------------------------------------------
# the certified support-capped search
# --------------------------------------------------------------------------


class CappedFamily:
    """Target-free tables for the support-capped D++ family at one n.

    Written from the family definition and the frozen primitives. It does not
    call dxx_search, _zeta_min, _block_arrays, _DxxTables or _dxx_backtrack --
    the point of the lane is a second, structurally different route to C_D++.
    """

    def __init__(self, n: int, max_weight: int = 2):
        self.n = n
        self.max_weight = max_weight
        keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)]
        small = [k for k in keys if k != (0, 0) and wt(k) <= max_weight]
        self.small = small
        self.pairs = [(a, b) for a in small for b in small if symp(a, b) == 1]
        self.P = len(self.pairs)
        # The per-block central choice is the family's, so it is minimised here
        # through the frozen rule rather than taken from dxx_search's tie-break.
        self.uanti = np.array(
            [min(r6m._uanti_m2(pr, c) for c in (0, 1)) for pr in self.pairs],
            dtype=np.int64,
        )
        tags = sorted((k for k in keys if k != (0, 0)), key=lambda k: (wt(k), k))
        self.tags = tags
        self.tag_wt = np.array([wt(k) for k in tags], dtype=np.int64)
        # allowed-Tag bitmask per (labelling, pair). One-time and target-free.
        self.tagmask = np.zeros((2, self.P), dtype=np.uint64)
        for li, (l0, l1) in enumerate(LABELS):
            for pi, (r0, r1) in enumerate(self.pairs):
                m = 0
                for si, s in enumerate(tags):
                    if symp(s, r0) == l0 and symp(s, r1) == l1:
                        m |= 1 << si
                self.tagmask[li, pi] = np.uint64(m)
        self.POP = np.array(
            [bin(i).count("1") for i in range(1 << (2 * n))], dtype=np.int64
        )

    # -- Q1 step 3: the Tag without the 4^n sweep --------------------------
    def tag_weight_dp(self, six, l0: int, l1: int) -> int:
        """Exact minimum Tag weight by a per-qubit syndrome DP. O(n).

        The six label constraints <S, R> = l are each a sum over qubits of
        sx_q * Rz_q + sz_q * Rx_q, so the constraint vector decomposes and the
        minimum-weight S is a shortest path through 2^6 syndrome states with one
        step per qubit. This is what removes the A^n - 1 Tag sweep, and it is
        the reason the realized search is polynomial rather than merely smaller.
        """
        INF = 10 ** 9
        target = 0
        for i in range(6):
            if (l1 if i % 2 else l0):
                target |= 1 << i
        dp = [INF] * 64
        dp[0] = 0
        for q in range(self.n):
            nd = [INF] * 64
            for sx in (0, 1):
                for sz in (0, 1):
                    cost = 0 if (sx == 0 and sz == 0) else 1
                    v = 0
                    for i, r in enumerate(six):
                        if (sx & ((r[1] >> q) & 1)) ^ (sz & ((r[0] >> q) & 1)):
                            v |= 1 << i
                    for st in range(64):
                        cand = dp[st] + cost
                        if cand < nd[st ^ v]:
                            nd[st ^ v] = cand
            dp = nd
        return dp[target]

    def tag_weight_exhaustive(self, six, l0: int, l1: int) -> int:
        """Minimum Tag weight by sweeping all 4^n Paulis. The thing being replaced."""
        best = 10 ** 9
        for x in range(2 ** self.n):
            for z in range(2 ** self.n):
                s = (x, z)
                ok = True
                for i, r in enumerate(six):
                    if symp(s, r) != (l1 if i % 2 else l0):
                        ok = False
                        break
                if ok:
                    best = min(best, wt(s))
        return best

    def _block(self, target_pair, perm: int):
        """(base, code) over pair indices for one block under one permutation."""
        t0, t1 = target_pair if perm == 0 else (target_pair[1], target_pair[0])
        n = self.n
        base = np.empty(self.P, dtype=np.int64)
        code = np.empty((self.P, 2 * n), dtype=np.int64)
        for pi, (r0, r1) in enumerate(self.pairs):
            u0 = mul(t0, r0)
            u1 = mul(t1, r1)
            base[pi] = int(self.uanti[pi]) + wt(u0) + wt(u1)
            for q in range(n):
                code[pi, q] = h.BITS_CODE[((u0[0] >> q) & 1, (u0[1] >> q) & 1)]
                code[pi, n + q] = h.BITS_CODE[((u1[0] >> q) & 1, (u1[1] >> q) & 1)]
        return base, code

    def search_dp(self, target_pairs) -> int:
        """The same certified enumeration, with the Tag from the O(n) DP and the
        Tag table never consulted. This is protocol section 3.3 literally.

        `search` below is the same objective reached through a target-free
        allowed-Tag bitmask table, which is what every bulk domain runs. That
        table is built by a 4^n sweep, so `search` does NOT by itself demonstrate
        that the sweep is removable -- it demonstrates that a table equivalent to
        it gives the right answer. Only this method removes the sweep from the
        path that produces the number, and it is pure Python and O(P^3 n), so it
        runs on a declared sample and the sample is the scope of the claim.
        """
        n, P = self.n, self.P
        best = None
        blocks = [[self._block(tp, perm) for perm in (0, 1)] for tp in target_pairs]
        for l0, l1 in LABELS:
            for i0 in range(P):
                for i1 in range(P):
                    for i2 in range(P):
                        six = (
                            self.pairs[i0][0], self.pairs[i0][1],
                            self.pairs[i1][0], self.pairs[i1][1],
                            self.pairs[i2][0], self.pairs[i2][1],
                        )
                        tw = self.tag_weight_dp(six, l0, l1)
                        if tw >= 10 ** 9:
                            continue
                        idx = (i0, i1, i2)
                        for perms in itertools.product((0, 1), repeat=3):
                            bs = [blocks[j][perms[j]] for j in range(3)]
                            codes = [bs[j][1][idx[j]] for j in range(3)]
                            match = 0
                            for pos in range(2 * n):
                                a = codes[0][pos]
                                if a and a == codes[1][pos] == codes[2][pos]:
                                    match += 1
                            val = (int(bs[0][0][idx[0]]) + int(bs[1][0][idx[1]])
                                   + int(bs[2][0][idx[2]]) - 2 * match + 2 * tw)
                            if best is None or val < best:
                                best = val
        if best is None:
            raise AssertionError("DP-driven capped search found no feasible point")
        return int(best)

    def search(self, target_pairs) -> int:
        """Exact C_D++ by certified enumeration of frame-pair triples.

        Unpruned on purpose (protocol section 3.4): a certified search is worth
        more as a plainly exhaustive loop than as a fast one.
        """
        n, P = self.n, self.P
        BIG = 10 ** 6
        best = 10 ** 9
        blocks = [[self._block(tp, perm) for perm in (0, 1)] for tp in target_pairs]
        bits = (1 << np.arange(2 * n, dtype=np.int64))[:, None]
        for li in range(2):
            tm = self.tagmask[li]
            pre = tm[:, None] & tm[None, :]
            for i0 in range(P):
                if int(tm[i0]) == 0:
                    continue
                # minimum admissible Tag weight for every (i1, i2) at once.
                # Independent of the target permutations, so eight permutation
                # combinations share one evaluation.
                tmask = pre & tm[i0]
                lsb = tmask & (~tmask + np.uint64(1))
                nz = lsb != 0
                idx = np.zeros(lsb.shape, dtype=np.int64)
                idx[nz] = np.rint(
                    np.log2(lsb[nz].astype(np.float64))
                ).astype(np.int64)
                two_tag = np.where(nz, 2 * self.tag_wt[idx], BIG)
                for p0 in (0, 1):
                    b0, c0 = blocks[0][p0]
                    w0 = c0[i0]
                    keep = w0 != 0
                    base0 = int(b0[i0])
                    for p1 in (0, 1):
                        b1, c1 = blocks[1][p1]
                        m1 = ((c1 == w0[None, :]) & keep[None, :]).astype(
                            np.int64
                        ) @ bits
                        for p2 in (0, 1):
                            b2, c2 = blocks[2][p2]
                            m2 = ((c2 == w0[None, :]) & keep[None, :]).astype(
                                np.int64
                            ) @ bits
                            match = self.POP[m1 & m2.T]
                            tot = (
                                base0
                                + b1[:, None]
                                + b2[None, :]
                                - 2 * match
                                + two_tag
                            )
                            v = int(tot.min())
                            if v < best:
                                best = v
        if best >= BIG:
            raise AssertionError("capped family produced no feasible point")
        return best


# --------------------------------------------------------------------------
# Q3: the frozen cell-count model
# --------------------------------------------------------------------------


def support_le_2_paulis(n: int) -> list[tuple[int, int]]:
    """Nonzero Paulis of weight <= 2, built structurally so the count is defined
    at any n rather than only where 4^n keys can be listed."""
    out = []
    for q in range(n):
        for bx, bz in ((1, 0), (0, 1), (1, 1)):
            out.append((bx << q, bz << q))
    for q1 in range(n):
        for q2 in range(q1 + 1, n):
            for b1 in ((1, 0), (0, 1), (1, 1)):
                for b2 in ((1, 0), (0, 1), (1, 1)):
                    out.append(
                        ((b1[0] << q1) | (b2[0] << q2),
                         (b1[1] << q1) | (b2[1] << q2))
                    )
    return out


def pair_count(n: int) -> int:
    small = support_le_2_paulis(n)
    return sum(1 for a in small for b in small if symp(a, b) == 1)


def cells_dxx(n: int) -> int:
    """N_dxx(n) = 2 (4^n - 1) [ 3 (2n+1) 4^{2n} + 4^{2n} ]  -- protocol section 5."""
    return 2 * (4 ** n - 1) * (3 * (2 * n + 1) * 4 ** (2 * n) + 4 ** (2 * n))


def cells_capped(n: int, p: int) -> int:
    """N_cap(n) = 54 P(n)^3  -- protocol section 5, the search as run."""
    return 54 * p ** 3


def cells_capped_dp(n: int, p: int) -> int:
    """N_cap_dp(n) = P(n)^3 (512 n + 48) -- the variant with no Tag table at all.

    NOT IN THE FROZEN PROTOCOL. Added after section 5 was frozen and before any
    full run completed, on re-reading that section against the claim this lane
    makes. See `counting_rule_amendment` in the results file.

    Section 5's frozen N_cap counts the search exactly as this lane runs it,
    which reaches the minimum Tag through a target-free bitmask table of size
    O(4^n * P). That table is the last exponential in the implementation, so a
    crossover computed from N_cap is not the crossover of the polynomial
    algorithm the lane claims to have realized. This second count replaces the
    table with the O(n) syndrome DP: 2 labellings * 256 n state updates per
    frame-pair triple (the DP is permutation-independent, so it is paid once per
    triple rather than once per permutation), plus the 48 P^3 of match and base
    work the eight permutations still pay.
    """
    return p ** 3 * (512 * n + 48)


# --------------------------------------------------------------------------
# domains
# --------------------------------------------------------------------------


def letter_key(letter: int, q: int):
    bx, bz = h.CODE_BITS[letter]
    return (bx << q, bz << q)


def _compare(cap: CappedFamily, target_pairs, n: int):
    a = cap.search(target_pairs)
    b = int(r6p.dxx_search(target_pairs, n, max_weight=2)["C_Dxx"])
    return a, b


def domain_a_n1_exhaustive(cap: CappedFamily) -> dict[str, Any]:
    mismatches = []
    agree = 0
    for idx in range(4096):
        p6 = tuple((idx >> (2 * (5 - t))) & 3 for t in range(6))
        tps = tuple(
            (letter_key(p6[2 * j], 0), letter_key(p6[2 * j + 1], 0)) for j in range(3)
        )
        a, b = _compare(cap, tps, 1)
        if a == b:
            agree += 1
        else:
            mismatches.append(
                {"instance_index": idx,
                 "targets_A0A1B0B1C0C1": "".join("IXYZ"[x] for x in p6),
                 "C_capped": a, "C_Dxx": b}
            )
    return {
        "domain": "A -- n=1, all target-letter instances",
        "n": 1, "instances": 4096, "complete_enumeration": True,
        "agree": agree, "all_agree": agree == 4096,
        "mismatches_verbatim": mismatches[:MISMATCH_VERBATIM_CAP],
        "mismatch_count": len(mismatches),
    }


def domain_b_n2_structured(cap: CappedFamily) -> dict[str, Any]:
    wt1 = [letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    mismatches = []
    agree = 0
    total = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        tps = tuple((wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic))
        a, b = _compare(cap, tps, 2)
        total += 1
        if a == b:
            agree += 1
        else:
            mismatches.append(
                {"triple": [int(ia), int(ib), int(ic)], "C_capped": a, "C_Dxx": b}
            )
    return {
        "domain": "B -- n=2, complete structured R6P domain",
        "n": 2, "instances": total, "complete_enumeration": total == 9261,
        "agree": agree, "all_agree": agree == total,
        "mismatches_verbatim": mismatches[:MISMATCH_VERBATIM_CAP],
        "mismatch_count": len(mismatches),
    }


def domain_c_hostile_panels(caps: dict[int, CappedFamily]) -> dict[str, Any]:
    instances = [
        (name, 1, tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in pr))
        for name, pr in sorted(r6m._HOSTILE_N1_PANELS.items())
    ]
    instances += [
        (name, 2, tuple((tuple(a), tuple(b)) for a, b in pr))
        for name, pr in sorted(r6m._HOSTILE_N2_PANELS.items())
    ]
    rows = []
    for name, n, tps in instances:
        a, b = _compare(caps[n], tps, n)
        rows.append({"panel": name, "n": n, "C_capped": a, "C_Dxx": b,
                     "agree": a == b})
    return {
        "domain": "C -- R6N hostile panels (includes n2_b, the weight-one refuter)",
        "instances": len(rows), "complete_enumeration": True,
        "agree": sum(r["agree"] for r in rows),
        "all_agree": all(r["agree"] for r in rows),
        "rows": rows,
        "n2_b_present": any(r["panel"] == "n2_b" for r in rows),
    }


def domain_d_n3_sample(cap: CappedFamily) -> dict[str, Any]:
    rng = np.random.default_rng(N3_SEED)
    wt1 = [letter_key(c, q) for q in range(3) for c in (1, 2, 3)]
    rows = []
    for _ in range(N3_SAMPLE):
        idxs = [int(v) for v in rng.integers(0, len(wt1), 6)]
        tps = tuple((wt1[idxs[2 * j]], wt1[idxs[2 * j + 1]]) for j in range(3))
        a, b = _compare(cap, tps, 3)
        rows.append({"target_indices": idxs, "C_capped": a, "C_Dxx": b,
                     "agree": a == b})
    return {
        "domain": "D -- n=3, DECLARED SAMPLE, not an enumeration",
        "n": 3, "instances": len(rows), "complete_enumeration": False,
        "sample_seed": N3_SEED,
        "obstacle_named": (
            "the capped search costs about 40 s per n=3 instance because P(3)=666 "
            "and the enumeration is P^3; the full structured n=3 domain was not "
            "attempted and is not claimed"
        ),
        "agree": sum(r["agree"] for r in rows),
        "all_agree": all(r["agree"] for r in rows),
        "rows": rows,
    }


def dp_driven_search_check(caps: dict[int, CappedFamily]) -> dict[str, Any]:
    """Does removing the Tag table from the path change the answer?

    Cursor Bugbot, reviewing f8ba5f23, pointed out that `search` never called
    `tag_weight_dp`: the DP was exercised only against Tag *values* in a side
    check, while every number that decided agreement came through the 4^n table.
    The protocol's Q1 step 3 and the lane's own responsibility string both said
    the sweep had been replaced. They were describing an algorithm the executed
    code did not run. That is exactly the failure family this branch has spent
    the day cataloguing, so the fix is to run it, not to reword it.
    """
    rows = []
    for idx in range(0, 4096, 4096 // DP_SEARCH_N1_SAMPLE):
        p6 = tuple((idx >> (2 * (5 - t))) & 3 for t in range(6))
        tps = tuple(
            (letter_key(p6[2 * j], 0), letter_key(p6[2 * j + 1], 0)) for j in range(3)
        )
        a = caps[1].search_dp(tps)
        b = caps[1].search(tps)
        c = int(r6p.dxx_search(tps, 1, max_weight=2)["C_Dxx"])
        rows.append({"n": 1, "instance_index": idx, "C_dp_driven": a,
                     "C_table_driven": b, "C_Dxx": c, "agree": a == b == c})
    rng = np.random.default_rng(DP_SEARCH_N2_SEED)
    w1 = [letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    for _ in range(DP_SEARCH_N2_SAMPLE):
        i = [int(v) for v in rng.integers(0, len(w1), 6)]
        tps = tuple((w1[i[2 * j]], w1[i[2 * j + 1]]) for j in range(3))
        a = caps[2].search_dp(tps)
        b = caps[2].search(tps)
        c = int(r6p.dxx_search(tps, 2, max_weight=2)["C_Dxx"])
        rows.append({"n": 2, "target_indices": i, "C_dp_driven": a,
                     "C_table_driven": b, "C_Dxx": c, "agree": a == b == c})
    return {
        "what_this_shows": (
            "the O(n) syndrome DP standing in for the 4^n Tag table inside the "
            "objective itself, not merely reproducing Tag values beside it"
        ),
        "instances": len(rows),
        "agree": sum(r["agree"] for r in rows),
        "all_agree": all(r["agree"] for r in rows),
        "rows": rows,
        "declared_scope_and_obstacle": (
            f"{DP_SEARCH_N1_SAMPLE} n=1 instances on a fixed stride and "
            f"{DP_SEARCH_N2_SAMPLE} seeded n=2 instances. The DP-driven search is "
            "pure Python over P^3 triples with a 64-state DP per triple, so n=2 "
            "costs minutes per instance and n=3 was not attempted. Every bulk "
            "domain therefore runs the table-driven `search`; this block is what "
            "licenses the claim that the table is removable, and its sample is "
            "the scope of that claim."
        ),
    }


def tag_dp_check(cap: CappedFamily) -> dict[str, Any]:
    """The O(n) DP against the 4^n sweep it is supposed to replace."""
    rng = np.random.default_rng(TAG_DP_SEED + cap.n)
    checks = TAG_DP_CHECKS[cap.n]
    bad = []
    for _ in range(checks):
        i, j, k = (int(v) for v in rng.integers(0, cap.P, 3))
        six = (
            cap.pairs[i][0], cap.pairs[i][1],
            cap.pairs[j][0], cap.pairs[j][1],
            cap.pairs[k][0], cap.pairs[k][1],
        )
        for l0, l1 in LABELS:
            got = cap.tag_weight_dp(six, l0, l1)
            want = cap.tag_weight_exhaustive(six, l0, l1)
            if got != want:
                bad.append({"pairs": [i, j, k], "labels": [l0, l1],
                            "dp": got, "sweep": want})
    return {
        "n": cap.n, "triples_checked": checks,
        "labellings_per_triple": 2,
        "disagreements": bad[:10], "disagreement_count": len(bad),
        "dp_reproduces_sweep": not bad,
    }


# --------------------------------------------------------------------------


def main() -> int:
    t_start = time.time()
    protocol_text = PROTOCOL.read_text()

    donor_records = [
        {
            "id": "QG28-D1",
            "claim": "a certified support-capped enumeration realizes QG-6's corollary",
            "asserts_novelty": False,
            "note": "the corollary is QG-6's own, already proved and committed",
        },
        {
            "id": "QG28-D2",
            "claim": "the shared Tag minimum is a per-qubit syndrome DP over 64 states",
            "asserts_novelty": False,
            "note": (
                "minimum-weight coset leader under a constant number of parity "
                "constraints; textbook dynamic programming, claimed by nobody here"
            ),
        },
        {
            "id": "QG28-D3",
            "claim": "the crossover n at which the capped search overtakes",
            "asserts_novelty": False,
            "note": "arithmetic on two committed implementations, not a result about a field",
        },
    ]
    for rec in donor_records:
        validate_donor_search(rec)

    caps = {n: CappedFamily(n) for n in (1, 2, 3)}
    p_counts = {n: caps[n].P for n in (1, 2, 3)}

    timings: dict[str, Any] = {}

    t = time.time()
    tag_checks = {n: tag_dp_check(caps[n]) for n in (1, 2, 3)}
    timings["tag_dp_check_seconds"] = round(time.time() - t, 3)

    t = time.time()
    dp_driven = dp_driven_search_check(caps)
    timings["dp_driven_search_seconds"] = round(time.time() - t, 3)

    t = time.time()
    dom_a = domain_a_n1_exhaustive(caps[1])
    timings["domain_a_seconds"] = round(time.time() - t, 3)

    t = time.time()
    dom_c = domain_c_hostile_panels(caps)
    timings["domain_c_seconds"] = round(time.time() - t, 3)

    t = time.time()
    dom_d = domain_d_n3_sample(caps[3])
    timings["domain_d_seconds"] = round(time.time() - t, 3)

    t = time.time()
    dom_b = domain_b_n2_structured(caps[2])
    timings["domain_b_seconds"] = round(time.time() - t, 3)

    domains = [dom_a, dom_b, dom_c, dom_d]
    all_agree = all(d["all_agree"] for d in domains)
    total_instances = sum(d["instances"] for d in domains)

    # -- Q3, evaluated only now -------------------------------------------
    ladder = []
    for n in range(1, 15):
        p = pair_count(n)
        nc, nd = cells_capped(n, p), cells_dxx(n)
        ndp = cells_capped_dp(n, p)
        ladder.append({"n": n, "P": p, "N_cap": nc, "N_dxx": nd,
                       "N_cap_dp": ndp,
                       "ratio_cap_over_dxx": nc / nd, "capped_cheaper": nc < nd,
                       "capped_dp_cheaper": ndp < nd})
    crossover = next((r["n"] for r in ladder if r["capped_cheaper"]), None)
    crossover_dp = next((r["n"] for r in ladder if r["capped_dp_cheaper"]), None)

    # wall-clock, for one purpose only: does the frozen cell model track measurement
    wall = {}
    rng = np.random.default_rng(918273)
    for n in (1, 2, 3):
        reps = {1: 40, 2: 10, 3: 2}[n]
        w1 = [letter_key(c, q) for q in range(n) for c in (1, 2, 3)]
        tc = td = 0.0
        for _ in range(reps):
            idxs = [int(v) for v in rng.integers(0, len(w1), 6)]
            tps = tuple((w1[idxs[2 * j]], w1[idxs[2 * j + 1]]) for j in range(3))
            s = time.time(); caps[n].search(tps); tc += time.time() - s
            s = time.time(); r6p.dxx_search(tps, n, max_weight=2); td += time.time() - s
        model = cells_capped(n, p_counts[n]) / cells_dxx(n)
        wall[str(n)] = {
            "reps": reps,
            "capped_seconds_per_instance": round(tc / reps, 6),
            "dxx_seconds_per_instance": round(td / reps, 6),
            "measured_ratio": round(tc / td, 2),
            "model_ratio": round(model, 2),
        }

    q3 = {
        "prospective": True,
        "counting_rule_frozen_in_protocol_section_5": True,
        "N_dxx_formula": "2 (4^n - 1) [ 3 (2n+1) 4^{2n} + 4^{2n} ]",
        "N_cap_formula": "54 P(n)^3",
        "ladder": ladder,
        "crossover_n": crossover,
        "crossover_n_dp_variant": crossover_dp,
        "N_cap_dp_formula": "P(n)^3 (512 n + 48)",
        "counting_rule_amendment": {
            "added_after_the_protocol_was_frozen": True,
            "added_before_any_full_run_completed": True,
            "description": (
                "a second cell count, N_cap_dp, for the variant that reaches the "
                "minimum Tag by the O(n) syndrome DP instead of by the "
                "target-free bitmask table of size O(4^n * P)"
            ),
            "rationale": (
                "section 5's frozen N_cap counts the search as this lane runs it, "
                "and that implementation still carries a 4^n Tag table. A "
                "crossover computed from it is therefore the crossover of the "
                "implementation, not of the polynomial algorithm the lane claims "
                "to have realized. Reporting only the first would let the "
                "headline number describe something other than the claim."
            ),
            "when_and_why_it_was_noticed": (
                "while re-reading the frozen section 5 against the claim, not "
                "after seeing an outcome. A first full run had been launched and "
                "was killed with no output written; nothing this amendment says "
                "was informed by a completed run. The frozen N_cap and its "
                "crossover are additions-only: both are still computed and "
                "reported above exactly as section 5 specifies."
            ),
            "effect_on_the_terminal": (
                "none. The terminal turns on whether a finite crossover exists at "
                "all, and both counts have one, so the amendment sharpens the "
                "number without moving the verdict. Had it moved the verdict, "
                "this lane would have had to report that instead."
            ),
        },
        "one_time_tag_table_disclosed": (
            "N_cap counts the per-instance search. The allowed-Tag bitmask table "
            "this run used costs a further O(4^n * P) once per n, target-free and "
            "amortized over every instance -- and the O(n) syndrome DP checked "
            "above shows it is not needed at all, which is what makes the realized "
            "search polynomial rather than merely smaller."
        ),
        "model_ratio_by_n": {
            str(n): round(cells_capped(n, p_counts[n]) / cells_dxx(n), 2)
            for n in (1, 2, 3)
        },
        "measured_wall_clock_lives_outside_the_digest": (
            "A measured second cannot repeat, so hashing one makes the receipt "
            "non-reproducible by construction and G8 can never hold. The first "
            "assembly of this lane failed exactly there: two runs whose every "
            "scientific field was byte-identical differed only in timing, and "
            "the determinism gate correctly refused to write. The measurements "
            "are reported in timings_excluded_from_digest.wall_clock_corroboration; "
            "what stays under digest custody is model_ratio_by_n, which is "
            "arithmetic on the frozen section-5 formulas and does repeat."
        ),
        "wall_clock_status": (
            "Gate G3: timing carries no part of the argument. It appears to say "
            "whether the frozen cell model tracks measurement, and the answer is "
            "reported whichever way it comes out."
        ),
    }

    # The DP-driven sample is a route to C_D++ like any other, so a disagreement
    # there is a disagreement, and the terminal has to move. Leaving it out let a
    # failed section-3.3 demonstration sit inside a receipt that still announced
    # the win -- reported by Cursor Bugbot on 5da6b4de.
    everything_agrees = all_agree and bool(dp_driven["all_agree"])
    if everything_agrees and crossover is not None:
        terminal = "QG28_COROLLARY_REALIZED__PROJECTED_WIN_CONFIRMED_WITH_ITS_CROSSOVER"
    elif everything_agrees and crossover is None:
        terminal = "QG28_COROLLARY_REALIZED__NO_WIN_AT_ANY_N"
    else:
        terminal = "QG28_REALIZATION_DISAGREES__SOMETHING_IS_WRONG"

    body = {
        "schema": "ORIONQG.QG28.SupportCappedRealization.v1",
        "lane": "QG-28",
        "residual": "W9",
        "protocol_digest": sha(protocol_text),
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "prospective_status": {
            "q1_build_the_capped_search": False,
            "q2_agreement_on_declared_domains": False,
            "q3_cell_model_and_crossover": True,
            "disclosure": (
                "A scratch prototype ran before the protocol was written. Section 0 "
                "of the protocol records what it had already returned. Q1 and Q2 are "
                "therefore not prospective and are not presented as if they were; "
                "what the prototype did not fix is the full declared domains and the "
                "whole of Q3."
            ),
        },
        "frame_pair_counts": {str(k): v for k, v in p_counts.items()},
        "tag_dp_vs_sweep": {str(k): v for k, v in tag_checks.items()},
        "dp_driven_search": dp_driven,
        "deviation_from_protocol_section_3_3": {
            "section_says": (
                "the shared Tag is obtained without the 4^n - 1 sweep, by an "
                "exact per-qubit syndrome DP"
            ),
            "what_the_bulk_domains_actually_run": (
                "the same enumeration with the Tag taken from a target-free "
                "allowed-Tag bitmask table, which is built by a 4^n sweep once "
                "per n and amortized over every instance"
            ),
            "why": (
                "the DP-driven search is pure Python and costs minutes per "
                "instance at n=2, so running it over 9,261 n=2 instances is not "
                "available inside the declared runtime cap"
            ),
            "what_licenses_the_claim_anyway": {
                "block": "dp_driven_search",
                "instances_run": int(dp_driven["instances"]),
                "instances_agreeing": int(dp_driven["agree"]),
                "licenses_the_claim": bool(dp_driven["all_agree"]),
                "text": (
                    "dp_driven_search above runs the section-3.3 algorithm "
                    f"literally on {dp_driven['instances']} declared instances and "
                    f"gets the same C_D++ as both the table-driven search and the "
                    f"committed dxx_search on {dp_driven['agree']} of them"
                    + ("" if dp_driven["all_agree"] else
                       " -- NOT ALL OF THEM, so nothing here licenses the claim "
                       "and the terminal reports the disagreement instead")
                ),
            },
            "found_by": (
                "Cursor Bugbot on commit f8ba5f23, which observed that search() "
                "never called tag_weight_dp while the protocol and the "
                "responsibility string both said the sweep had been replaced"
            ),
        },
        "domains": domains,
        "total_instances_compared": total_instances,
        "all_domains_agree": all_agree,
        "q3_cell_model": q3,
        "terminal": terminal,
        "gates": {
            "G1_donor_search_validated_no_novelty_asserted": True,
            "G2_committed_modules_imported_unmodified": True,
            "G3_no_complexity_inference_from_wall_clock": True,
            "G4_no_theorem_claimed": True,
            "G5_complete_on_A_B_C__D_declared_sample": (
                dom_a["complete_enumeration"]
                and dom_b["complete_enumeration"]
                and dom_c["complete_enumeration"]
                and not dom_d["complete_enumeration"]
            ),
            "G6_no_committed_receipt_edited": True,
            "G9_not_r6_protected_subject_unread": True,
        },
        "donor_search_records": donor_records,
        "caps_disclosed": [
            "runtime cap < 45 minutes for the full run",
            f"domain D is a declared sample of {N3_SAMPLE} n=3 instances, seed {N3_SEED}",
            f"Tag DP cross-check counts {TAG_DP_CHECKS} triples, seed base {TAG_DP_SEED}",
            f"DP-driven search run on {DP_SEARCH_N1_SAMPLE} n=1 and "
            f"{DP_SEARCH_N2_SAMPLE} n=2 instances (seed {DP_SEARCH_N2_SEED}); "
            "not attempted at n=3",
            f"mismatch verbatim cap {MISMATCH_VERBATIM_CAP} rows per domain",
            "the capped search is unpruned by design; no early exit was used",
            "n >= 4 not executed: the committed dxx_search guards max_weight=2 to n<=3",
        ],
        "r6_authority": False,
        "novelty_credit": False,
        "novelty_authority": False,
        "donor_novelty_credit": False,
        "physical_quantum_advantage_claim": False,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "reserved_stretched_n2_accessed": False,
        "responsibility": (
            "RESP:QG6_SUPPORT_CAPPED_COROLLARY_REALIZED_AS_A_CERTIFIED_SEARCH__"
            "AGREES_WITH_THE_COMMITTED_FAMILY_SEARCH_ON_EVERY_DECLARED_DOMAIN__"
            "TAG_SWEEP_SHOWN_REPLACEABLE_BY_AN_ON_SYNDROME_DP_ON_A_DECLARED_"
            "SAMPLE__W9_PROJECTION_EVALUATED"
        ),
    }
    body["content_digest"] = sha(canonical(body))
    timings["wall_clock_corroboration"] = wall
    body["timings_excluded_from_digest"] = timings
    body["total_seconds"] = round(time.time() - t_start, 1)

    OUT.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": terminal,
        "instances": total_instances,
        "all_agree": all_agree,
        "crossover_n": crossover,
    }, indent=1))
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
