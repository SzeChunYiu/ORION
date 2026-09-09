#!/usr/bin/env python3
"""Aggregate a sharded sweep, prove its coverage was total, and state the verdict.

A sweep that reports "no witness" is only worth the completeness of its coverage. The failure
that matters here is not a wrong answer but a *partial* one: a shard killed at walltime, an array
sized differently from NSHARD, a scratch file half written. Each leaves a gap that looks exactly
like a clean negative. So this script refuses to report a verdict until it has seen one RESULT
line from every shard index, and it checks the shard identifiers the runs themselves recorded
rather than trusting the file names.

Usage:  ./collect.py results/r6_L20
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RESULT = re.compile(
    r"RESULT p=(\d+) r=(\d+) L=(\d+) s=(\d+) shard=(-?\d+)/(\d+) sym=(\d+) "
    r"found=(\d+) leaves=(\d+) nodes=(\d+)"
)


def main(directory: Path) -> int:
    files = sorted(directory.glob("shard_*.txt"))
    if not files:
        print(f"no shard files under {directory}")
        return 2

    seen: dict[int, dict] = {}
    witnesses: list[str] = []
    nshard = None
    params = None

    for path in files:
        text = path.read_text(errors="replace")
        witnesses += [ln for ln in text.splitlines() if ln.startswith("packing<=1:")]
        m = RESULT.search(text)
        if m is None:
            continue  # incomplete; counted as missing below
        p, r, L, s, shard, n, sym, found, leaves, nodes = (int(x) for x in m.groups())
        if nshard is None:
            nshard, params = n, (p, r, L, s, sym)
        elif (n, (p, r, L, s, sym)) != (nshard, params):
            print(f"FATAL: {path.name} ran a different configuration: {m.group(0)}")
            return 3
        if shard in seen:
            print(f"FATAL: shard {shard} recorded twice")
            return 3
        seen[shard] = {"found": found, "leaves": leaves, "nodes": nodes}

    p, r, L, s, sym = params
    missing = sorted(set(range(nshard)) - set(seen))
    total_nodes = sum(v["nodes"] for v in seen.values())
    total_leaves = sum(v["leaves"] for v in seen.values())
    total_found = sum(v["found"] for v in seen.values())

    print(f"configuration  p={p} rank={r} length={L} prune=<={s} orbit-prune={'on' if sym else 'OFF'}")
    print(f"shards         {len(seen)} complete of {nshard}")
    print(f"totals         nodes={total_nodes:,}  leaves={total_leaves:,}  witnesses={total_found}")

    if s != L - r * (p - 1) - 1:
        print(f"FATAL: prune depth {s} is not L-q-1={L - r * (p - 1) - 1}; the runs solved another problem")
        return 3

    if witnesses:
        print()
        print(f"WITNESS FOUND -- {len(witnesses)} sequence(s) of length {L} with packing number <= 1.")
        print(f"So D_2(C_{p}^{r}) >= {L + 1}.")
        for w in witnesses[:5]:
            print("  " + w)
        print()
        print("This conclusion needs no coverage argument: one witness is one witness. Re-check it")
        print("with an independent packing computation before recording it.")
        return 0

    if missing:
        print()
        print(f"INCOMPLETE -- {len(missing)} shard(s) never wrote a RESULT line: "
              f"{missing[:20]}{' ...' if len(missing) > 20 else ''}")
        print("No verdict. Resubmit; completed shards are skipped, so only these will run.")
        return 1

    print()
    print(f"COMPLETE AND EMPTY -- every one of the {nshard} shards finished and none found a")
    print(f"length-{L} sequence over C_{p}^{r} with packing number <= 1.")
    print(f"Hence D_2(C_{p}^{r}) <= {L}.")
    if r == 7 and L == 22:
        print()
        print("That decides the closed form: it predicts 23 and the truth is 22, so")
        print("D_k(C_p^r) = (3/2)r(p-1) + (k-2)p + 2 is FALSE, and the construction class is")
        print("extremal at this point after all.")
    if r == 6 and L == 20:
        print()
        print("D_2(C_3^6) = 20, matching both the construction and the closed form, and giving the")
        print("spanning reduction the rank-7 sweep needs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "results")))
