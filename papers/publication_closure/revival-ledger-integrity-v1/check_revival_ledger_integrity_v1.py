#!/usr/bin/env python3
"""Integrity guard for append-only revival-attempt ledgers.

A revival ledger records adverse attempts that a paper is required to preserve.
It is append-only by intent but sealed by nothing, so a truncation removes an
adverse result and leaves no trace. This checks the three properties that make
such a truncation visible:

1. every counted attempt's custody receipt exists on disk;
2. every custody receipt on disk is cited by a counted attempt;
3. attempt ordinals are 1..N with no gap;
4. remaining_attempts decrements by exactly one per counted attempt.

Property 2 is the one that matters and the one a first version of this checker
did not have. Truncating the LAST attempt leaves ordinals [1..N-1], which is
still gap-free, so end-truncation is invisible from inside the ledger. It is
visible only from outside it: the removed attempt's custody receipt is still on
disk and now nothing cites it.

Exit 0 clean, 1 violation, 3 cannot check. 3 is distinct from 0 on purpose:
"no ledger found" is not "the ledger is fine".
"""
from __future__ import annotations
import json, sys
from pathlib import Path

BUDGET = 100

def check(root: Path):
    ledgers = sorted(root.glob("papers/**/*REVIVAL_ATTEMPT_LEDGER*.jsonl"))
    if not ledgers:
        print("CANNOT_CHECK: no revival ledger found"); return 3
    bad, counted_total = [], 0
    for led in ledgers:
        rel = led.relative_to(root)
        rows = []
        for i, ln in enumerate(led.read_text(encoding="utf-8").splitlines(), 1):
            ln = ln.strip()
            if not ln: continue
            try: rows.append((i, json.loads(ln)))
            except json.JSONDecodeError as e:
                bad.append(f"{rel}:{i} unparseable: {e}"); return_bad = True
        counted = [(i, r) for i, r in rows if r.get("counts_toward_100")]
        counted_total += len(counted)
        print(f"  {rel}: {len(rows)} rows, {len(counted)} counted")
        seen_ord = []
        for i, r in counted:
            aid = r.get("attempt_id", "?")
            rec = r.get("custody_receipt")
            if rec:
                p = root / rec
                if not p.is_file():
                    bad.append(f"{rel}:{i} {aid} cites missing custody receipt {rec}")
            else:
                bad.append(f"{rel}:{i} {aid} counted but cites no custody receipt")
            o = r.get("attempt_ordinal")
            if o is None:
                bad.append(f"{rel}:{i} {aid} counted but has no attempt_ordinal")
            else:
                seen_ord.append(o)
                rem = r.get("remaining_attempts")
                if rem is not None and rem != BUDGET - o:
                    bad.append(f"{rel}:{i} {aid} ordinal {o} but remaining_attempts "
                               f"{rem}, expected {BUDGET - o}")
        if seen_ord and sorted(seen_ord) != list(range(1, len(seen_ord) + 1)):
            bad.append(f"{rel}: counted ordinals {sorted(seen_ord)} are not 1..N "
                       f"-- an attempt has been removed")

        # Orphan detection. A ledger truncated at the end still looks gap-free
        # from the inside; the evidence is outside it.
        cited = {r.get("custody_receipt") for _, r in rows if r.get("custody_receipt")}
        cited |= {r.get("receipt") for _, r in rows if r.get("receipt")}
        paper_root = led.parent.parent
        cited_names = {Path(c).name for c in cited if c}
        # Scope. Rounds that predate the ledger's own first recorded round are not
        # its business: their receipts are prior work, not removed attempts. A first
        # version of this check omitted the scope and reported two such rounds as
        # violations. Only rounds at or after the ledger's earliest cited round are
        # in scope, which still catches an end-truncation because the removed
        # attempt's round sorts after the ones that survive.
        cited_rounds = {Path(c).parts[-2] for c in cited if c and len(Path(c).parts) >= 2}
        cited_rounds.add(led.parent.name)
        floor = min(cited_rounds)
        for cust in sorted(paper_root.glob("*/*CUSTODY*.json")):
            if cust.parent.name < floor:
                continue
            crel = cust.relative_to(root).as_posix()
            if crel not in cited and cust.name not in cited_names:
                bad.append(f"{rel}: custody receipt {crel} is on disk but no ledger "
                           f"row cites it -- an attempt has been removed from the ledger")
    if bad:
        print(f"\nVIOLATIONS ({len(bad)}):")
        for b in bad: print(f"  {b}")
        return 1
    print(f"\nOK: {counted_total} counted attempts, every receipt present, "
          f"ordinals gap-free, budget arithmetic consistent")
    return 0

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(check(root))
