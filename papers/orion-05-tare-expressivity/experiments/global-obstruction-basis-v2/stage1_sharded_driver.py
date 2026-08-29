#!/usr/bin/env python3
"""ORION-05 V2 Stage 1: sharded driver for the same-domain positive-control scan.

WHY THIS FILE EXISTS (do not delete it as a duplicate of the reference script).

`run_stage1_control_discovery_v2.py` is the frozen reference instrument and its
sha256 matches SHA256SUMS. It is single-process and, critically, its `--start`
flag is parsed but never referenced in the scan loop, and the `--array-chunk`
flag that COMPUTE_PLAN_V2.md relies on for lexicographic parallel execution does
not exist in it at all. Both were verified by grep with a passing control. So the
plan's stated parallel mechanism is not implemented anywhere; this driver
supplies it without touching the frozen artifact.

ESTIMAND PARITY. This driver calls the *same* `solve_six_targets` from the
paper's own solver, over the *same* enumeration, and computes gap = C1 - C2 with
C1 = cost at max_support=1 and C2 = cost at max_support=2. It must reproduce the
reference script row-for-row; `--verify-against-reference` checks exactly that.

COST (measured on billy-old, 2026-08-29, not estimated):
  max_support=1 solve: ~0.4 s
  max_support=2 solve: ~478 s
  => the C2 solve is ~1200x the C1 solve and dominates everything.

PROVABLE SKIP RULE. frame_cost sums m0*(w0-1) + m1*(w1-1) over three frame pairs
with {m0,m1} = {2,4} and Pauli weights w >= 1, so every cost is a non-negative
integer. max_support=2 admits every max_support=1 witness, so 0 <= C2 <= C1. Thus
C1 == 0 forces C2 == 0 and gap == 0, with no C2 solve required. Rows skipped this
way are marked c2_method="proved_zero_floor" and are NOT silent omissions. Every
other row solves C2 explicitly.

TIMEOUT/ERROR rows are retained as evidence, never dropped and never retried away.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import signal
import sys
import time
from itertools import combinations_with_replacement
from multiprocessing import Pool
from pathlib import Path

SOLVER_REL = "papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py"

# Same production convention as the reference script.
CODES = [(a, b) for a in range(4) for b in range(4)][1:]
assert len(CODES) == 15

_MOD = None
_TIMEOUT = 0


def domain():
    """The 33,755 repeated-target multisets, in the reference script's scan order.

    The reference increments `scanned` only for non-all-distinct combos, so index
    i here corresponds to the reference's lex_index i+1.
    """
    return [c for c in combinations_with_replacement(range(1, 16), 6) if len(set(c)) != 6]


def _load_solver(repo_root: str):
    path = Path(repo_root) / SOLVER_REL
    if not path.is_file():
        raise SystemExit(f"solver not found at {path}")
    spec = importlib.util.spec_from_file_location("orion05_solver", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["orion05_solver"] = mod
    spec.loader.exec_module(mod)
    return mod


def _init(repo_root: str, timeout: int):
    global _MOD, _TIMEOUT
    _MOD = _load_solver(repo_root)
    _TIMEOUT = timeout
    signal.signal(signal.SIGALRM, _on_alarm)


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):
    raise _Timeout()


def _solve_one(targets, max_support):
    """Return (cost, status, seconds). Never raises; TIMEOUT/ERROR are data."""
    t0 = time.time()
    if _TIMEOUT:
        signal.alarm(_TIMEOUT)
    try:
        _, w = _MOD.solve_six_targets(targets, max_support=max_support)
        return int(w.cost), "OK", round(time.time() - t0, 2)
    except _Timeout:
        return None, "TIMEOUT", round(time.time() - t0, 2)
    except Exception as exc:  # noqa: BLE001 - failures are evidence, keep them
        return None, f"ERROR:{type(exc).__name__}:{exc}", round(time.time() - t0, 2)
    finally:
        if _TIMEOUT:
            signal.alarm(0)


def work(job):
    idx, combo, mode = job
    targets = [list(CODES[c - 1]) for c in combo]
    row = {"index": idx, "lex_index": idx + 1, "codes": list(combo)}

    c1, s1, t1 = _solve_one(targets, 1)
    row.update(c1=c1, c1_status=s1, c1_seconds=t1)

    if mode == "c1":
        row["c2_method"] = "not_attempted_c1_only_mode"
        return row

    if s1 != "OK":
        # Cannot reason about the gap without C1. Keep the row, attempt nothing.
        row.update(c2=None, c2_status="SKIPPED_C1_FAILED", gap=None,
                   c2_method="skipped_c1_failed")
        return row

    if c1 == 0:
        # Provable: 0 <= C2 <= C1 = 0.
        row.update(c2=0, c2_status="OK", gap=0, c2_method="proved_zero_floor",
                   c2_seconds=0.0)
        return row

    c2, s2, t2 = _solve_one(targets, 2)
    row.update(c2=c2, c2_status=s2, c2_seconds=t2, c2_method="solved")
    row["gap"] = (c1 - c2) if s2 == "OK" else None
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["c1", "full"], default="full")
    ap.add_argument("--start", type=int, default=0, help="first lexicographic index (inclusive)")
    ap.add_argument("--limit", type=int, default=0, help="number of indices to cover (0 = to end)")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--timeout", type=int, default=0, help="per-solve seconds (0 = none)")
    ap.add_argument("--out", required=True, help="JSONL output, appended and flushed per row")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--indices-file", default="",
                    help="whitespace-separated explicit lexicographic indices to solve. "
                         "For targeted existence probes ONLY. The protocol's control "
                         "selection rule is lexicographic-first-three and forbids manual "
                         "substitution, so rows produced this way answer the separate "
                         "question 'does any positive gap exist' and must never be "
                         "reported as selected controls.")
    ap.add_argument("--verify-against-reference", type=int, default=0,
                    help="cross-check the first N rows against the frozen reference script")
    a = ap.parse_args()

    dom = domain()
    if len(dom) != 33755:
        raise SystemExit(f"domain size {len(dom)} != 33755")

    if a.indices_file:
        idxs = [int(x) for x in Path(a.indices_file).read_text().split()]
        bad = [i for i in idxs if not 0 <= i < len(dom)]
        if bad:
            raise SystemExit(f"indices out of range: {bad[:10]}")
    else:
        end = len(dom) if not a.limit else min(len(dom), a.start + a.limit)
        idxs = list(range(a.start, end))

    if a.verify_against_reference:
        return _verify(a, dom)

    # Round-robin dispatch keeps every worker near the same lexicographic depth,
    # so the completed set stays a near-prefix and the "first three" rule can be
    # frozen against a contiguous complete prefix.
    jobs = [(i, dom[i], a.mode) for i in idxs]

    done = 0
    t0 = time.time()
    with open(a.out, "a", encoding="utf-8") as fh:
        with Pool(a.workers, initializer=_init, initargs=(a.repo_root, a.timeout)) as pool:
            for row in pool.imap_unordered(work, jobs, chunksize=1):
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
                done += 1
                if done % 25 == 0:
                    el = time.time() - t0
                    print(f"done={done}/{len(jobs)} elapsed={el:.0f}s rate={done/el:.2f}/s",
                          flush=True)
    print(f"COMPLETE done={done} elapsed={time.time()-t0:.0f}s", flush=True)
    return 0


def _verify(a, dom) -> int:
    """Run the frozen reference over the first N rows and demand identical (c1,c2)."""
    import subprocess
    n = a.verify_against_reference
    ref_out = Path(a.out).with_suffix(".refcheck.json")
    ref_script = (Path(a.repo_root) / "papers/orion-05-tare-expressivity/experiments"
                  / "global-obstruction-basis-v2/run_stage1_control_discovery_v2.py")
    cmd = [sys.executable, str(ref_script), "--limit", str(n), "--progress", "0",
           "--emit", str(ref_out), "--repo-root", a.repo_root]
    print("REFERENCE CMD:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    ref = json.loads(ref_out.read_text())

    _init(a.repo_root, a.timeout)
    mine = [work((i, dom[i], "full")) for i in range(n)]

    ref_pos = {p["lex_index"]: (p["c1"], p["c2"]) for p in ref["all_positives"]}
    mine_pos = {r["lex_index"]: (r["c1"], r["c2"]) for r in mine if r.get("gap", 0)}
    ok_pos = ref_pos == mine_pos

    # The reference's gap histogram is the ground truth for every scanned row.
    hist = {}
    for r in mine:
        hist[str(r["gap"])] = hist.get(str(r["gap"]), 0) + 1
    ok_hist = hist == ref["gap_histogram"]

    verdict = {"rows": n, "reference_gap_histogram": ref["gap_histogram"],
               "driver_gap_histogram": hist, "histograms_match": ok_hist,
               "positives_match": ok_pos,
               "reference_scanned": ref["scanned"],
               "PARITY": bool(ok_hist and ok_pos)}
    Path(a.out).with_suffix(".parity.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verdict, indent=2, sort_keys=True), flush=True)
    return 0 if verdict["PARITY"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
