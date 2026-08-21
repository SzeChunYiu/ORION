#!/usr/bin/env python3
"""Stronger-donor wrapper for frozen MAX-R5J ADT3 development.

ADT3's dependent odd frame must use XOR-consistent labels. The canonical TARE
frame is independent and the donor paper leaves labels free, so this wrapper gives
that donor all 24 ordered triples of distinct 2-bit labels before comparison.
"""
from __future__ import annotations

import itertools

import max_r5j_anchored_dependent_tare3_development as q


def strengthened_canonical_best(targets, n):
    rs = q.canonical_frame(n)
    assert all(q.symp(rs[i], rs[j]) == 1 for i in range(3) for j in range(i + 1, 3))
    best = None
    for labels in itertools.permutations(range(4), 3):
        hi_syn = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
        lo_syn = sum(((labels[k] & 1) << k) for k in range(3))
        s_hi_w, s_hi = q.tag_min_weight(rs, hi_syn, n)
        s_lo_w, s_lo = q.tag_min_weight(rs, lo_syn, n)
        for perm in itertools.permutations(range(3)):
            ps = [targets[i] for i in perm]
            ts = [q.mul(ps[j], rs[j]) for j in range(3)]
            for central in range(3):
                c = q.uanti_support(rs, central) + 2 * (s_hi_w + s_lo_w) + sum(q.wt(t) for t in ts)
                rec = {
                    "cost": int(c),
                    "control_labels": list(labels),
                    "target_permutation": list(perm),
                    "central": central,
                    "R": [list(r) for r in rs],
                    "S_high": list(s_hi),
                    "S_low": list(s_lo),
                    "T": [list(t) for t in ts],
                    "tag_weight": int(s_hi_w + s_lo_w),
                    "uanti_support": q.uanti_support(rs, central),
                    "restore_support": int(sum(q.wt(t) for t in ts)),
                }
                key = (rec["cost"], labels, perm, central, s_hi, s_lo)
                if best is None or key < best[0]:
                    best = (key, rec)
    return best[1]


def main():
    q.canonical_best = strengthened_canonical_best
    return q.main()


if __name__ == "__main__":
    main()
