#!/usr/bin/env python3
"""ORION-05 V2 Stage 1: same-domain positive-control discovery.

Protocol: ORION05.GLOBAL_OBSTRUCTION_BASIS.v2, stage_1_positive_control_discovery.

Domain: lexicographic combinations_with_replacement of six codes from 1..15,
excluding the 5,005 all-distinct sets -> 33,755 repeated-target multisets. The
confirmatory 5,005-row distinct-target domain is deliberately NOT touched here.

Estimand: minimum cost over all 15 perfect matchings of the six target slots, at
max_support=1 (C1) and max_support=2 (C2). Gap = C1 - C2. That is exactly what
solve_six_targets computes; it enumerates perfect_matchings internally.

Selection rule: scan in lexicographic order and record the first three instances
with C1 > C2. No manual substitution. A start=0 scan STOPS as soon as those
three are found. If the full repeated-target domain is exhausted with fewer than
three, the terminal is CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS and
confirmation must not run.

Resume rule: --start is a zero-based offset in the repeated-target domain, not in
the 38,760 raw combinations. Any start>0 or limit-truncated invocation is a shard
and MUST emit PARTIAL_SCAN__NO_STAGE1_AUTHORITY. A shard may discover candidates,
but it cannot certify the globally first three without an external aggregation
of the complete earlier prefix.

This also discriminates two of the registered theory candidates: a domain-wide
absence of gaps supports O05-C2 (relaxation law) and falsifies O05-C3
(gap-preservation class); any surviving gaps are C3's candidate class.

HARD CONSTRAINT (inherited from the v1 compute plan): no control or census
solve runs on the Mac. Local use is limited to --smoke, which performs zero
solver instances. Every solving mode here is LUNARC-only.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations_with_replacement

SOLVER_REL = "papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py"
EXPECTED_DOMAIN = 33755
EXPECTED_RAW = 38760
EXPECTED_DISTINCT = 5005


def _load_solver(repo_root: str):
    """Import the paper's own solver. Deliberately lazy: --smoke must not need it."""
    import importlib.util
    from pathlib import Path as _P

    path = _P(repo_root) / SOLVER_REL
    if not path.is_file():
        raise SystemExit(f"solver not found at {path}; pass --repo-root")
    spec = importlib.util.spec_from_file_location("orion05_solver", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["orion05_solver"] = mod
    spec.loader.exec_module(mod)
    return mod


# The 15 non-identity two-qubit Pauli codes, in the production convention:
# a dense Pauli is a pair of local codes (0=I,1=X,2=Y,3=Z); code index 1..15
# enumerates the non-identity pairs in lexicographic order.
CODES = [(a, b) for a in range(4) for b in range(4)][1:]
assert len(CODES) == 15


def solve(mod, targets):
    _, w1 = mod.solve_six_targets(targets, max_support=1)
    _, w2 = mod.solve_six_targets(targets, max_support=2)
    return w1.cost, w2.cost


def _smoke() -> int:
    raw = list(combinations_with_replacement(range(1, 16), 6))
    repeated = [c for c in raw if len(set(c)) != 6]
    distinct = len(raw) - len(repeated)

    # Resume semantics are over the repeated-target stream, not the raw stream.
    # These checks are solver-free and catch an accidental change of indexing.
    resume_probe = {
        "offset_0": list(repeated[0]),
        "offset_1": list(repeated[1]),
        "offset_last": list(repeated[-1]),
        "slice_17_5": [list(x) for x in repeated[17:22]],
    }
    ok = (
        len(CODES) == 15
        and len(raw) == EXPECTED_RAW
        and distinct == EXPECTED_DISTINCT
        and len(repeated) == EXPECTED_DOMAIN
        and len(resume_probe["slice_17_5"]) == 5
    )
    print(
        json.dumps(
            {
                "mode": "smoke",
                "solves_performed": 0,
                "codes": len(CODES),
                "domain_total": len(raw),
                "all_distinct_excluded": distinct,
                "repeated_target_domain": len(repeated),
                "matches_protocol_33755": len(repeated) == EXPECTED_DOMAIN,
                "resume_index_space": "zero-based repeated-target domain",
                "resume_probe": resume_probe,
                "enumeration_ok": ok,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="solve at most N repeated-target candidates in this invocation (0 = no limit)",
    )
    ap.add_argument("--emit", default="STAGE1_RESULT.json")
    ap.add_argument("--progress", type=int, default=200)
    ap.add_argument(
        "--smoke",
        action="store_true",
        help="enumeration and resume-index checks only; performs ZERO solves (safe anywhere)",
    )
    ap.add_argument(
        "--start",
        type=int,
        default=0,
        help="zero-based offset in the 33,755-row repeated-target domain",
    )
    ap.add_argument("--repo-root", default=".")
    a = ap.parse_args()

    if a.start < 0:
        ap.error("--start must be >= 0")
    if a.limit < 0:
        ap.error("--limit must be >= 0")
    if a.start > EXPECTED_DOMAIN:
        ap.error(f"--start must be <= {EXPECTED_DOMAIN}")

    if a.smoke:
        return _smoke()

    mod = _load_solver(a.repo_root)
    positives = []
    processed = 0
    repeated_index = 0  # zero-based absolute index in the repeated-target domain
    skipped_distinct_encountered = 0
    gap_hist = {}
    t0 = time.time()
    domain_exhausted = True
    stop_reason = "domain_exhausted"

    for combo in combinations_with_replacement(range(1, 16), 6):
        if len(set(combo)) == 6:
            skipped_distinct_encountered += 1
            continue

        absolute_index = repeated_index
        repeated_index += 1
        if absolute_index < a.start:
            continue

        targets = [list(CODES[c - 1]) for c in combo]
        c1, c2 = solve(mod, targets)
        processed += 1
        gap = c1 - c2
        gap_hist[gap] = gap_hist.get(gap, 0) + 1
        if gap > 0:
            positives.append(
                {
                    "codes": list(combo),
                    "targets": targets,
                    "c1": c1,
                    "c2": c2,
                    "gap": gap,
                    # One-based human-readable lexicographic index over the
                    # repeated-target domain; absolute_index remains zero-based.
                    "lex_index": absolute_index + 1,
                    "absolute_index_zero_based": absolute_index,
                }
            )

        if a.progress and processed % a.progress == 0:
            elapsed = time.time() - t0
            rate = processed / elapsed if elapsed else 0.0
            print(
                "  processed "
                f"{processed} rows from absolute offset {a.start} "
                f"in {elapsed:.0f}s ({rate:.3f}/s) positives={len(positives)}",
                flush=True,
            )

        # The frozen protocol needs the first three positives, not a census of
        # every later positive. Stopping here is both scientifically sufficient
        # for start=0 and the main cost-control promised by the compute plan.
        if len(positives) >= 3:
            domain_exhausted = False
            stop_reason = "first_three_positives_found"
            break

        if a.limit and processed >= a.limit:
            domain_exhausted = False
            stop_reason = "limit_reached"
            break

    elapsed = time.time() - t0

    authoritative_prefix = a.start == 0
    if authoritative_prefix and len(positives) >= 3:
        terminal = "SAME_DOMAIN_POSITIVE_CONTROLS_FOUND"
        authority_reason = "start=0 and the globally first three positives were reached"
    elif authoritative_prefix and domain_exhausted:
        terminal = "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS"
        authority_reason = "start=0 and the full repeated-target domain was exhausted"
    else:
        terminal = "PARTIAL_SCAN__NO_STAGE1_AUTHORITY"
        authority_reason = (
            "this invocation did not establish the complete lexicographic prefix from zero; "
            "aggregate prior shards before assigning a Stage-1 terminal"
        )

    absolute_end_exclusive = min(a.start + processed, EXPECTED_DOMAIN)
    out = {
        "schema": "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage1",
        "estimand": "min cost over all 15 perfect matchings; gap = C1 - C2",
        "domain": "combinations_with_replacement(1..15, 6) excluding all-distinct",
        "domain_size_expected": EXPECTED_DOMAIN,
        "resume_index_space": "zero-based repeated-target domain",
        "start": a.start,
        "absolute_end_exclusive": absolute_end_exclusive,
        "processed_this_invocation": processed,
        # Backward-compatible alias. It is intentionally invocation-local now.
        "scanned": processed,
        "skipped_all_distinct_encountered": skipped_distinct_encountered,
        "domain_exhausted": domain_exhausted,
        "stop_reason": stop_reason,
        "selection_complete": terminal != "PARTIAL_SCAN__NO_STAGE1_AUTHORITY",
        "complete": terminal != "PARTIAL_SCAN__NO_STAGE1_AUTHORITY",
        "positives_found_this_invocation": len(positives),
        "positives_found": len(positives),
        "first_three_positives": positives[:3] if authoritative_prefix else [],
        "shard_positives": positives,
        # Kept for consumers of the pre-fix schema. On resumed shards these are
        # explicitly local and carry no first-three authority.
        "all_positives": positives,
        "gap_histogram": {str(k): v for k, v in sorted(gap_hist.items())},
        "terminal": terminal,
        "authority_reason": authority_reason,
        "elapsed_seconds": round(elapsed, 1),
        "theory_reading": (
            "only a start=0 authoritative scan may discriminate the registered theories: "
            "full-domain absence of positive gaps supports O05-C2 (matching relaxation erases "
            "the historical gaps) and falsifies O05-C3 (gap-preservation class); the globally "
            "first three surviving gaps are C3's candidate class"
        ),
    }

    with open(a.emit, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print(
        json.dumps(
            {
                k: out[k]
                for k in (
                    "start",
                    "absolute_end_exclusive",
                    "processed_this_invocation",
                    "positives_found",
                    "stop_reason",
                    "terminal",
                    "elapsed_seconds",
                )
            },
            indent=2,
        )
    )
    print("gap histogram:", out["gap_histogram"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
