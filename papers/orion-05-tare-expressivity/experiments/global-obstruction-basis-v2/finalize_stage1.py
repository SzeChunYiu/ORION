#!/usr/bin/env python3
"""Turn the sharded Stage 1 JSONL into STAGE1_RESULT.json, honestly.

THE FAILURE THIS FILE EXISTS TO PREVENT.

The frozen reference script computes its terminal as:

    terminal = ("SAME_DOMAIN_POSITIVE_CONTROLS_FOUND" if len(positives) >= 3
                else "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS")

`complete` respects --limit but `terminal` does not. So any truncated run that
finds fewer than three positives emits CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_
CONTROLS -- which COMPUTE_PLAN_V2 defines as the terminal that supports O05-C2
and falsifies O05-C3. A partial scan would therefore manufacture a theory-
discriminating negative out of nothing but an exhausted compute budget. The plan
names this exact hazard: truncating "would convert a real negative into an
unreported absence".

This finalizer refuses to do that. The CANNOT_CHECK terminal is emitted ONLY
when the contiguous verified prefix covers the entire 33,755-row domain.
Otherwise the terminal is PARTIAL_SCAN_INCOMPLETE and the artifact carries the
exact prefix depth reached.

FIRST-THREE SEMANTICS. The protocol's selection rule is lexicographic, so a
positive at index k can only be frozen once every index < k has been solved.
Workers are dispatched round-robin, so completed indices form a near-prefix with
a ragged edge; only the contiguous prefix counts. Positives found beyond it are
reported separately as unconfirmed, never as the frozen three.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

DOMAIN_SIZE = 33755


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--emit", required=True)
    ap.add_argument("--mode", choices=["c1", "full"], default="full")
    a = ap.parse_args()

    rows = {}
    for line in Path(a.jsonl).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        rows[r["index"]] = r

    # Contiguous verified prefix: every index below it present AND fully solved.
    def solved(r):
        if r["c1_status"] != "OK":
            return False
        if a.mode == "c1":
            return True
        return r.get("gap") is not None

    prefix = 0
    while prefix in rows and solved(rows[prefix]):
        prefix += 1

    complete = prefix >= DOMAIN_SIZE

    scanned = sorted(rows)
    failures = [rows[i] for i in scanned if rows[i]["c1_status"] != "OK"
                or (a.mode == "full" and rows[i].get("c2_status") not in (None, "OK"))]

    prefix_rows = [rows[i] for i in range(prefix)]
    positives_in_prefix = [r for r in prefix_rows if (r.get("gap") or 0) > 0]
    positives_beyond = [rows[i] for i in scanned
                        if i >= prefix and (rows[i].get("gap") or 0) > 0]

    if a.mode == "c1":
        terminal = ("C1_LANDSCAPE_COMPLETE" if complete
                    else "C1_LANDSCAPE_PARTIAL")
    elif complete:
        terminal = ("SAME_DOMAIN_POSITIVE_CONTROLS_FOUND"
                    if len(positives_in_prefix) >= 3
                    else "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS")
    elif len(positives_in_prefix) >= 3:
        # Three lexicographically-first positives are frozen by a verified
        # prefix; completeness of the tail is irrelevant to the selection rule.
        terminal = "SAME_DOMAIN_POSITIVE_CONTROLS_FOUND"
    else:
        terminal = "PARTIAL_SCAN_INCOMPLETE"

    c1_hist = Counter(r["c1"] for r in rows.values() if r["c1"] is not None)
    gap_hist = Counter(r["gap"] for r in rows.values() if r.get("gap") is not None)

    out = {
        "schema": "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage1.sharded",
        "estimand": "min cost over all 15 perfect matchings; gap = C1 - C2",
        "domain": "combinations_with_replacement(1..15, 6) excluding all-distinct",
        "domain_size_expected": DOMAIN_SIZE,
        "mode": a.mode,
        "rows_emitted": len(rows),
        "contiguous_verified_prefix": prefix,
        "prefix_fraction_of_domain": round(prefix / DOMAIN_SIZE, 6),
        "complete": complete,
        "terminal": terminal,
        "positives_in_verified_prefix": len(positives_in_prefix),
        "first_three_positives": positives_in_prefix[:3],
        "positives_beyond_prefix_unconfirmed": positives_beyond,
        "c1_histogram": {str(k): v for k, v in sorted(c1_hist.items())},
        "gap_histogram": {str(k): v for k, v in sorted(gap_hist.items())},
        "retained_failure_rows": failures,
        "n_retained_failures": len(failures),
        "terminal_semantics": (
            "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS is emitted only when the "
            "verified prefix covers the whole 33,755-row domain. PARTIAL_SCAN_INCOMPLETE "
            "means the scan ran out of budget and is NOT evidence for O05-C2 or against "
            "O05-C3; it asserts nothing about the unscanned tail."
        ),
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("mode", "rows_emitted", "contiguous_verified_prefix",
                       "prefix_fraction_of_domain", "complete", "terminal",
                       "positives_in_verified_prefix", "n_retained_failures")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
