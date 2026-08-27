#!/usr/bin/env python3
"""Sparse direct exact solver for the frozen ORION-05/R6M support-two grammar.

This module intentionally has **no ORION imports**.  It implements the R11
runtime-theorem candidate directly:

* constructive O(n^3) generation of ordered anticommuting support<=2 pairs;
* O(n) target/local Restore-baseline preprocessing;
* candidate corrections on the <=9-coordinate active union only;
* a 64-state Tag-syndrome DP on that active union; and
* direct enumeration of three frame pairs with sound incumbent pruning.

It does not import/call the historical 512-state R6M DP, does not sweep 4^n
Tags, and does not materialize a 4^(2n) pattern table.  The separate hostile
gate may import the historical DP only as an oracle for equality checks.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

INF = 10**9
LETTER_BITS = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
BITS_LETTER = {bits: letter for letter, bits in LETTER_BITS.items()}
NONZERO = (1, 2, 3)
ORIENTATIONS = ((0, 1), (1, 0))

SparsePauli = tuple[tuple[int, int], ...]
GlobalPauli = tuple[int, int]


def local_symp(a: int, b: int) -> int:
    ax, az = LETTER_BITS[a]
    bx, bz = LETTER_BITS[b]
    return (ax & bz) ^ (az & bx)


def local_mul(a: int, b: int) -> int:
    ax, az = LETTER_BITS[a]
    bx, bz = LETTER_BITS[b]
    return BITS_LETTER[(ax ^ bx, az ^ bz)]


def anti_letters(letter: int) -> tuple[int, int]:
    vals = tuple(v for v in NONZERO if local_symp(letter, v) == 1)
    if len(vals) != 2:
        raise AssertionError((letter, vals))
    return vals


def sparse(entries: Iterable[tuple[int, int]]) -> SparsePauli:
    out = tuple(sorted((int(q), int(letter)) for q, letter in entries if letter != 0))
    if len({q for q, _ in out}) != len(out):
        raise AssertionError({"duplicate_coordinate": out})
    return out


def sp_wt(p: SparsePauli) -> int:
    return len(p)


def sp_local(p: SparsePauli, q: int) -> int:
    for pos, letter in p:
        if pos == q:
            return letter
    return 0


def sp_symp(a: SparsePauli, b: SparsePauli) -> int:
    parity = 0
    for q, letter in a:
        other = sp_local(b, q)
        if other:
            parity ^= local_symp(letter, other)
    return parity


def sp_to_global(p: SparsePauli) -> GlobalPauli:
    x = z = 0
    for q, letter in p:
        bx, bz = LETTER_BITS[letter]
        x |= bx << q
        z |= bz << q
    return x, z


def global_to_letters(p: GlobalPauli, n: int) -> tuple[int, ...]:
    x, z = p
    return tuple(BITS_LETTER[((x >> q) & 1, (z >> q) & 1)] for q in range(n))


def tag_symp_sparse(tag: SparsePauli, frame: SparsePauli) -> int:
    return sp_symp(tag, frame)


def pair_formula(n: int) -> int:
    return 54 * n**3 - 108 * n**2 + 60 * n


@dataclass(frozen=True, slots=True)
class PairRecord:
    r0: SparsePauli
    r1: SparsePauli
    active: tuple[int, ...]
    central: int
    uanti: int

    @property
    def identity(self) -> tuple[SparsePauli, SparsePauli]:
        return self.r0, self.r1


def _record(r0: SparsePauli, r1: SparsePauli) -> PairRecord:
    if not (1 <= sp_wt(r0) <= 2 and 1 <= sp_wt(r1) <= 2):
        raise AssertionError({"support_outside_gate": [r0, r1]})
    if sp_symp(r0, r1) != 1:
        raise AssertionError({"not_anticommuting": [r0, r1]})
    w0, w1 = sp_wt(r0), sp_wt(r1)
    central = 1 if w0 < w1 else 0  # multiplier 2 on heavier; tie -> 0
    uanti = 4 * (min(w0, w1) - 1) + 2 * (max(w0, w1) - 1)
    active = tuple(sorted({q for q, _ in r0} | {q for q, _ in r1}))
    if len(active) > 3:
        raise AssertionError({"pair_union_gt3": [r0, r1, active]})
    return PairRecord(r0=r0, r1=r1, active=active, central=central, uanti=uanti)


def generate_pairs(n: int) -> tuple[PairRecord, ...]:
    """Construct every ordered anticommuting support<=2 pair without all-pairs scan."""
    if n < 1:
        raise ValueError("n must be >=1")
    out: list[PairRecord] = []

    # Weight-one first frame.
    for q in range(n):
        for a in NONZERO:
            r0 = sparse(((q, a),))
            for b in anti_letters(a):
                out.append(_record(r0, sparse(((q, b),))))
            for r in range(n):
                if r == q:
                    continue
                for b in anti_letters(a):
                    for c in NONZERO:
                        out.append(_record(r0, sparse(((q, b), (r, c)))))

    # Weight-two first frame.
    for q in range(n):
        for r in range(q + 1, n):
            for a in NONZERO:
                for b in NONZERO:
                    r0 = sparse(((q, a), (r, b)))
                    # Four weight-one partners.
                    for c in anti_letters(a):
                        out.append(_record(r0, sparse(((q, c),))))
                    for c in anti_letters(b):
                        out.append(_record(r0, sparse(((r, c),))))
                    # Four same-support weight-two partners: exactly one local anti.
                    for c in NONZERO:
                        for d in NONZERO:
                            if local_symp(a, c) ^ local_symp(b, d):
                                out.append(_record(r0, sparse(((q, c), (r, d)))))
                    # Twelve partners per outside coordinate.
                    for s in range(n):
                        if s in (q, r):
                            continue
                        for shared_q, shared_letter in ((q, a), (r, b)):
                            for c in anti_letters(shared_letter):
                                for d in NONZERO:
                                    out.append(_record(r0, sparse(((shared_q, c), (s, d)))))

    identities = [rec.identity for rec in out]
    if len(out) != pair_formula(n):
        raise AssertionError({"pair_count": [n, len(out), pair_formula(n)]})
    if len(set(identities)) != len(identities):
        raise AssertionError({"duplicate_pairs": n})
    out.sort(key=lambda rec: (rec.uanti, rec.identity))
    return tuple(out)


def f3(a: int, b: int, c: int) -> int:
    if a == b == c != 0:
        return 1
    return int(a != 0) + int(b != 0) + int(c != 0)


@dataclass(slots=True)
class Choice:
    pair: PairRecord
    mods: dict[int, tuple[int, int]]


@dataclass(slots=True)
class Prepared:
    n: int
    ordered: dict[tuple[int, int], tuple[tuple[int, ...], tuple[int, ...]]]
    baseline_total: dict[tuple[int, int], int]
    a: tuple[Choice, ...]
    b0: tuple[Choice, ...]
    b1: tuple[Choice, ...]
    c0: tuple[Choice, ...]
    c1: tuple[Choice, ...]


def _choice(pair: PairRecord, ordered_pair: tuple[tuple[int, ...], tuple[int, ...]]) -> Choice:
    t0, t1 = ordered_pair
    mods: dict[int, tuple[int, int]] = {}
    for q in pair.active:
        mods[q] = (
            local_mul(t0[q], sp_local(pair.r0, q)),
            local_mul(t1[q], sp_local(pair.r1, q)),
        )
    return Choice(pair=pair, mods=mods)


def prepare(target_pairs: Sequence[Sequence[GlobalPauli]], n: int, pairs: tuple[PairRecord, ...]) -> Prepared:
    if len(target_pairs) != 3 or any(len(block) != 2 for block in target_pairs):
        raise ValueError("target_pairs must be three ordered target pairs")
    local_blocks = []
    for block in target_pairs:
        local_blocks.append(tuple(global_to_letters(tuple(p), n) for p in block))
    ordered: dict[tuple[int, int], tuple[tuple[int, ...], tuple[int, ...]]] = {}
    for block in range(3):
        p0, p1 = local_blocks[block]
        ordered[(block, 0)] = (p0, p1)
        ordered[(block, 1)] = (p1, p0)

    baseline_total: dict[tuple[int, int], int] = {}
    for perm_b, perm_c in itertools.product((0, 1), repeat=2):
        a0, a1 = ordered[(0, 0)]
        b0, b1 = ordered[(1, perm_b)]
        c0, c1 = ordered[(2, perm_c)]
        total = 0
        for q in range(n):
            total += f3(a0[q], b0[q], c0[q]) + f3(a1[q], b1[q], c1[q])
        baseline_total[(perm_b, perm_c)] = total

    return Prepared(
        n=n,
        ordered=ordered,
        baseline_total=baseline_total,
        a=tuple(_choice(pair, ordered[(0, 0)]) for pair in pairs),
        b0=tuple(_choice(pair, ordered[(1, 0)]) for pair in pairs),
        b1=tuple(_choice(pair, ordered[(1, 1)]) for pair in pairs),
        c0=tuple(_choice(pair, ordered[(2, 0)]) for pair in pairs),
        c1=tuple(_choice(pair, ordered[(2, 1)]) for pair in pairs),
    )


def active_union(a: PairRecord, b: PairRecord, c: PairRecord) -> tuple[int, ...]:
    # At most nine integer identities; set/hash work is constant in n.
    return tuple(sorted({*a.active, *b.active, *c.active}))


def _restore_for_perms(prep: Prepared, ia: int, ib: int, ic: int, active: tuple[int, ...], perm_b: int, perm_c: int) -> int:
    ca = prep.a[ia]
    cb = prep.b0[ib] if perm_b == 0 else prep.b1[ib]
    cc = prep.c0[ic] if perm_c == 0 else prep.c1[ic]
    a0, a1 = prep.ordered[(0, 0)]
    b0, b1 = prep.ordered[(1, perm_b)]
    c0, c1 = prep.ordered[(2, perm_c)]
    total = prep.baseline_total[(perm_b, perm_c)]
    for q in active:
        old = f3(a0[q], b0[q], c0[q]) + f3(a1[q], b1[q], c1[q])
        ar0, ar1 = ca.mods.get(q, (a0[q], a1[q]))
        br0, br1 = cb.mods.get(q, (b0[q], b1[q]))
        cr0, cr1 = cc.mods.get(q, (c0[q], c1[q]))
        new = f3(ar0, br0, cr0) + f3(ar1, br1, cr1)
        total += new - old
    return total


def restore_min(prep: Prepared, ia: int, ib: int, ic: int, active: tuple[int, ...]) -> tuple[int, int, int]:
    best = None
    for perm_b, perm_c in itertools.product((0, 1), repeat=2):
        value = _restore_for_perms(prep, ia, ib, ic, active, perm_b, perm_c)
        order = (value, perm_b, perm_c)
        if best is None or order < best:
            best = order
    assert best is not None
    return best


def _delta_for_letter(letter: int, q: int, frames: tuple[SparsePauli, ...]) -> int:
    delta = 0
    if letter == 0:
        return 0
    for i, frame in enumerate(frames):
        delta |= local_symp(letter, sp_local(frame, q)) << i
    return delta


def tag_dp(frames: tuple[SparsePauli, ...], active: tuple[int, ...], want_witness: bool = False):
    """64-state exact minimum Tag support for both common-label orientations."""
    dp = [INF] * 64
    dp[0] = 0
    histories = []
    for q in active:
        deltas = tuple(_delta_for_letter(letter, q, frames) for letter in range(4))
        nxt = [INF] * 64
        parent = [None] * 64 if want_witness else None
        for state, cost in enumerate(dp):
            if cost >= INF:
                continue
            for letter, delta in enumerate(deltas):
                state2 = state ^ delta
                cost2 = cost + int(letter != 0)
                if cost2 < nxt[state2] or (cost2 == nxt[state2] and want_witness and parent[state2] is not None and (letter, state) < (parent[state2][1], parent[state2][0])):
                    nxt[state2] = cost2
                    if want_witness:
                        parent[state2] = (state, letter)
        if want_witness:
            histories.append(parent)
        dp = nxt

    targets = []
    for orientation in ORIENTATIONS:
        state = 0
        for block in range(3):
            state |= orientation[0] << (2 * block)
            state |= orientation[1] << (2 * block + 1)
        targets.append((dp[state], orientation, state))
    best = min(targets, key=lambda row: (row[0], row[1]))
    if best[0] >= INF:
        return None
    if not want_witness:
        return int(best[0]), tuple(best[1])

    state = int(best[2])
    letters_rev = []
    for parent in reversed(histories):
        rec = parent[state]
        if rec is None:
            raise AssertionError({"tag_backtrack": state})
        prev, letter = rec
        letters_rev.append(letter)
        state = prev
    if state != 0:
        raise AssertionError({"tag_backtrack_nonzero_start": state})
    letters = tuple(reversed(letters_rev))
    tag = sparse((q, letter) for q, letter in zip(active, letters) if letter)
    return int(best[0]), tuple(best[1]), tag


def _frames(pa: PairRecord, pb: PairRecord, pc: PairRecord) -> tuple[SparsePauli, ...]:
    return pa.r0, pa.r1, pb.r0, pb.r1, pc.r0, pc.r1


def _search(prep: Prepared, pairs: tuple[PairRecord, ...], indices: Sequence[int], incumbent: int) -> tuple[int, tuple | None, dict[str, int]]:
    best = incumbent
    best_rec = None
    stats = {"triples_visited": 0, "lower_bound_pruned": 0, "tag_dp_candidates": 0, "max_active_union": 0}
    for ia in indices:
        pa = pairs[ia]
        if best < INF and pa.uanti + 2 >= best:
            stats["lower_bound_pruned"] += 1
            break
        for ib in indices:
            pb = pairs[ib]
            partial = pa.uanti + pb.uanti
            if best < INF and partial + 2 >= best:
                stats["lower_bound_pruned"] += 1
                break
            for ic in indices:
                pc = pairs[ic]
                direct = partial + pc.uanti
                if best < INF and direct + 2 >= best:
                    stats["lower_bound_pruned"] += 1
                    break
                stats["triples_visited"] += 1
                active = active_union(pa, pb, pc)
                stats["max_active_union"] = max(stats["max_active_union"], len(active))
                restore, perm_b, perm_c = restore_min(prep, ia, ib, ic, active)
                if best < INF and direct + restore + 2 >= best:
                    stats["lower_bound_pruned"] += 1
                    continue
                stats["tag_dp_candidates"] += 1
                tag = tag_dp(_frames(pa, pb, pc), active, want_witness=False)
                if tag is None:
                    continue
                tag_wt, orientation = tag
                total = direct + restore + 2 * tag_wt
                order = (total, ia, ib, ic, perm_b, perm_c, orientation)
                if total < best or (total == best and best_rec is not None and order < best_rec[0]):
                    best = total
                    best_rec = (order, ia, ib, ic, perm_b, perm_c, orientation)
                elif total == best and best_rec is None:
                    best_rec = (order, ia, ib, ic, perm_b, perm_c, orientation)
    return best, best_rec, stats


def _verify_and_render(prep: Prepared, pairs: tuple[PairRecord, ...], best_rec: tuple, cost: int) -> dict:
    _order, ia, ib, ic, perm_b, perm_c, orientation = best_rec
    pa, pb, pc = pairs[ia], pairs[ib], pairs[ic]
    active = active_union(pa, pb, pc)
    tag_wt, got_orientation, tag = tag_dp(_frames(pa, pb, pc), active, want_witness=True)
    if tuple(got_orientation) != tuple(orientation):
        raise AssertionError({"orientation_replay": [got_orientation, orientation]})
    restore = _restore_for_perms(prep, ia, ib, ic, active, perm_b, perm_c)
    recomputed = pa.uanti + pb.uanti + pc.uanti + restore + 2 * tag_wt
    syndromes = tuple(tag_symp_sparse(tag, frame) for frame in _frames(pa, pb, pc))
    expected = tuple(orientation) * 3
    checks = {
        "pair_support_and_anticommutation": all(1 <= sp_wt(r) <= 2 for r in _frames(pa, pb, pc)) and all(sp_symp(p.r0, p.r1) == 1 for p in (pa, pb, pc)),
        "active_union_le_9": len(active) <= 9,
        "tag_supported_on_active_union": set(q for q, _ in tag).issubset(active),
        "common_labels": syndromes == expected,
        "tag_weight_recomputed": sp_wt(tag) == tag_wt,
        "cost_recomputed": recomputed == cost,
    }
    if not all(checks.values()):
        raise AssertionError({"witness_checks": checks})
    blocks = []
    for label, pair, idx in zip("ABC", (pa, pb, pc), (ia, ib, ic)):
        blocks.append({
            "block": label,
            "pair_index": idx,
            "R0": list(sp_to_global(pair.r0)),
            "R1": list(sp_to_global(pair.r1)),
            "support": [sp_wt(pair.r0), sp_wt(pair.r1)],
            "central": pair.central,
            "uanti": pair.uanti,
        })
    return {
        "cost": cost,
        "relative_permutation_B": perm_b,
        "relative_permutation_C": perm_c,
        "orientation": list(orientation),
        "S": list(sp_to_global(tag)),
        "tag_weight": tag_wt,
        "active_union": list(active),
        "blocks": blocks,
        "restore_support": restore,
        "checks": checks,
    }


def solve(target_pairs: Sequence[Sequence[GlobalPauli]], n: int) -> dict:
    start = time.perf_counter()
    pairs = generate_pairs(n)
    prep = prepare(target_pairs, n, pairs)
    support1 = tuple(i for i, pair in enumerate(pairs) if sp_wt(pair.r0) == 1 and sp_wt(pair.r1) == 1)
    cap1_cost, cap1_rec, cap1_stats = _search(prep, pairs, support1, INF)
    if cap1_rec is None or cap1_cost >= INF:
        raise AssertionError("support-one family unexpectedly infeasible")
    full_indices = tuple(range(len(pairs)))
    best_cost, best_rec, full_stats = _search(prep, pairs, full_indices, cap1_cost)
    if best_rec is None:
        # No strict improvement: retain the exact support-one witness.
        best_cost, best_rec = cap1_cost, cap1_rec
    witness = _verify_and_render(prep, pairs, best_rec, best_cost)
    return {
        "schema": "ORION.Q1.R11.SparseDirectSolve.v1",
        "n": n,
        "pair_count": len(pairs),
        "pair_formula": pair_formula(n),
        "support1_pair_count": len(support1),
        "support1_incumbent": cap1_cost,
        "C_sparse": best_cost,
        "strict_support2_improvement": best_cost < cap1_cost,
        "witness": witness,
        "stats": {
            "support1": cap1_stats,
            "support2": full_stats,
            "wall_seconds": time.perf_counter() - start,
        },
        "runtime_contract": {
            "pair_generator": "constructive_overlap_cases_O_n3",
            "frame_triple_enumeration": "direct_B_n_cubed_O_n9",
            "target_preprocessing": "O_n_four_permutation_baselines",
            "candidate_scoring": "active_union_at_most_9",
            "tag_solver": "64_state_active_union_DP",
            "historical_r6m_dp_imported": False,
            "global_4_pow_n_tag_sweep": False,
            "pattern_table_4_pow_2n": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--target-pairs-json", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    target_pairs = json.loads(args.target_pairs_json.read_text(encoding="utf-8"))
    result = solve(target_pairs, args.n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"terminal": "Q1_R11_SPARSE_DIRECT_SOLVE_PASS", "C_sparse": result["C_sparse"], "n": args.n}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
