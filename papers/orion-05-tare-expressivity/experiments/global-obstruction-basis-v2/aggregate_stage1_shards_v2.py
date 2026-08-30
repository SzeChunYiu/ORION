#!/usr/bin/env python3
"""ORION-05 V2 Stage 1: external aggregation of sharded scans.

The Stage-1 runner can only assign a terminal when it is invoked with
--start 0 and walks an uninterrupted prefix. Its own docstring defers the
sharded case to "an external aggregation of the complete earlier prefix".
This is that aggregation, and it is deliberately conservative: it refuses to
assign a terminal whenever the prefix it needs is not provably covered.

Soundness rule enforced here
----------------------------
To certify the globally first three positives, the union of shard coverage
must contain EVERY index from 0 up to and including the third positive. A
single uncovered index below that point admits an earlier positive that no
shard looked at, which would silently change which instances are "first".
To certify the negative terminal, coverage must be the entire domain.

Why shards can under-cover their assigned range: the runner breaks out of its
loop as soon as it holds three positives, and on --limit. So a shard's real
coverage is [start, absolute_end_exclusive), which may be shorter than the
range it was handed. This reads actual coverage from the receipts and never
assumes the launch plan was honoured.

Exit codes: 0 terminal assigned, 1 inconsistent shards, 3 CANNOT_CHECK
(coverage insufficient to assign any terminal).
"""

from __future__ import annotations

import argparse
import glob
import json
import sys

EXPECTED_DOMAIN = 33755
SCHEMA = "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage1"


def merge(intervals):
    """Merge half-open [a,b) intervals. Returns sorted disjoint list."""
    out = []
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def covered_prefix_end(merged):
    """Largest P such that [0,P) is fully covered."""
    if not merged or merged[0][0] > 0:
        return 0
    return merged[0][1]


def gaps_below(merged, bound):
    """Uncovered half-open intervals inside [0,bound)."""
    out, cur = [], 0
    for a, b in merged:
        if a > cur:
            out.append([cur, min(a, bound)])
        cur = max(cur, b)
        if cur >= bound:
            break
    if cur < bound:
        out.append([cur, bound])
    return [g for g in out if g[0] < g[1]]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shards", nargs="+", help="shard JSON files or globs")
    ap.add_argument("--emit", default="STAGE1_AGGREGATE.json")
    a = ap.parse_args()

    paths = sorted({p for pat in a.shards for p in glob.glob(pat)})
    if not paths:
        print("no shard files matched", file=sys.stderr)
        return 3

    problems, intervals, positives, shards = [], [], {}, []
    total_processed = 0

    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception as exc:  # a malformed receipt must never be skipped silently
            problems.append(f"{p}: unreadable ({exc})")
            continue
        if d.get("schema") != SCHEMA:
            problems.append(f"{p}: unexpected schema {d.get('schema')!r}")
            continue

        s = int(d["start"])
        e = int(d["absolute_end_exclusive"])
        proc = int(d["processed_this_invocation"])
        if e - s != proc:
            problems.append(f"{p}: coverage {s}..{e} disagrees with processed={proc}")
        if e > EXPECTED_DOMAIN:
            problems.append(f"{p}: end {e} exceeds domain {EXPECTED_DOMAIN}")

        # Integrity: the gap histogram must account for every solved instance.
        hist_total = sum(int(v) for v in d.get("gap_histogram", {}).values())
        if hist_total != proc:
            problems.append(f"{p}: gap_histogram sums to {hist_total}, processed={proc}")

        for pos in d.get("shard_positives", []):
            i = int(pos["absolute_index_zero_based"])
            if not (s <= i < e):
                problems.append(f"{p}: positive at {i} outside covered range {s}..{e}")
            prev = positives.get(i)
            if prev is not None and (prev["c1"], prev["c2"]) != (pos["c1"], pos["c2"]):
                problems.append(
                    f"index {i}: shards disagree, "
                    f"({prev['c1']},{prev['c2']}) vs ({pos['c1']},{pos['c2']})"
                )
            positives[i] = pos

        intervals.append([s, e])
        total_processed += proc
        shards.append({"file": p, "start": s, "end": e, "stop_reason": d.get("stop_reason")})

    merged = merge(intervals)
    prefix = covered_prefix_end(merged)
    union = sum(b - a for a, b in merged)
    ordered = [positives[i] for i in sorted(positives)]

    if problems:
        terminal = "INCONSISTENT_SHARDS__NO_TERMINAL"
        reason = "shard receipts failed integrity checks; see problems"
        rc = 1
    elif len(ordered) >= 3 and prefix > ordered[2]["absolute_index_zero_based"]:
        terminal = "SAME_DOMAIN_POSITIVE_CONTROLS_FOUND"
        reason = (
            f"prefix [0,{prefix}) is gap-free and contains the third positive at "
            f"index {ordered[2]['absolute_index_zero_based']}"
        )
        rc = 0
    elif union == EXPECTED_DOMAIN and not ordered:
        terminal = "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS"
        reason = "the entire repeated-target domain was covered and contains no positive gap"
        rc = 0
    else:
        terminal = "PARTIAL_SCAN__NO_STAGE1_AUTHORITY"
        need = ordered[2]["absolute_index_zero_based"] + 1 if len(ordered) >= 3 else EXPECTED_DOMAIN
        reason = (
            f"coverage insufficient: gap-free prefix ends at {prefix}, "
            f"need {need}; union covers {union}/{EXPECTED_DOMAIN}"
        )
        rc = 3

    out = {
        "schema": "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage1.aggregate",
        "domain_size_expected": EXPECTED_DOMAIN,
        "shard_count": len(shards),
        "union_covered": union,
        "domain_fully_covered": union == EXPECTED_DOMAIN,
        "gap_free_prefix_end": prefix,
        "instances_solved_total": total_processed,
        "double_counted": total_processed - union,
        "uncovered_below_domain": gaps_below(merged, EXPECTED_DOMAIN)[:20],
        "positives_total": len(ordered),
        "first_three_positives": ordered[:3],
        "terminal": terminal,
        "authority_reason": reason,
        "problems": problems,
        "shards": shards,
        "theory_reading": (
            "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS over the full domain supports "
            "O05-C2 (matching relaxation erases the historical gaps) and falsifies O05-C3; "
            "certified positives are C3's candidate class"
        ),
    }
    with open(a.emit, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print(json.dumps({k: out[k] for k in (
        "shard_count", "union_covered", "domain_fully_covered", "gap_free_prefix_end",
        "positives_total", "terminal", "authority_reason")}, indent=2))
    if problems:
        print("PROBLEMS:", file=sys.stderr)
        for p in problems[:20]:
            print("  " + p, file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
