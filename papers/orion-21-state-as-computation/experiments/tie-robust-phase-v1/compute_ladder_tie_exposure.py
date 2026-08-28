#!/usr/bin/env python3
"""Ladder tie-exposure analysis for ORION-21 NR07.

Reads ONLY the authoritative committed result of LUNARC job 3550337 and reports,
per ladder cell, whether the registered primary quantity n_cross is exposed to
support-selection ties.

This script establishes EXPOSURE, not ambiguity. It cannot compute the admissible
range of n_cross, because the ladder readings record only the realised support
selection, not the equality class. Determining whether n_cross is set-valued
requires re-running the ladder with tie enumeration -- that is the successor
experiment, not this diagnostic.

Usage: compute_ladder_tie_exposure.py <NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json>
"""
import collections
import hashlib
import json
import sys

TAU = 0.95  # registered: prereg_criterion.primary_quantity
EXPECTED_INPUT_SHA256 = "8ef964ecb3c02ab5988ea13ed56678a424e7d5487f64d31c2e66a149e44d9e22"


def main(path: str) -> int:
    raw = open(path, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw)

    criterion = doc["prereg_criterion"]["primary_quantity"]
    readings = doc["readings"]

    cells = collections.defaultdict(list)
    for r in readings:
        cells[tuple(r["cell"])].append(r)

    tie_points = total_points = 0
    for r in readings:
        for _n, separable in r["support_separable_rank_gap"].items():
            total_points += 1
            tie_points += not separable

    per_cell = []
    for cell, rs in sorted(cells.items()):
        rs.sort(key=lambda r: r["seed"])
        sizes = sorted({int(n) for r in rs for n in r["screen_mean_accuracy"]})
        means, tied = {}, {}
        for n in sizes:
            vals = [r["screen_mean_accuracy"][str(n)] for r in rs]
            means[n] = sum(vals) / len(vals)
            tied[n] = sum(1 for r in rs if not r["support_separable_rank_gap"][str(n)])
        n_cross = next((n for n in sizes if means[n] >= TAU), None)
        entry = {
            "cell": list(cell),
            "n_seeds": len(rs),
            "n_cross": n_cross,
            "tie_exposed_at_crossing": None,
        }
        if n_cross is not None:
            idx = sizes.index(n_cross)
            prev = sizes[idx - 1] if idx > 0 else None
            entry.update(
                mean_at_n_cross=means[n_cross],
                margin_above_tau=means[n_cross] - TAU,
                tied_seeds_at_n_cross=tied[n_cross],
                tied_seeds_at_previous_size=(tied[prev] if prev is not None else None),
                previous_size=prev,
                tie_exposed_at_crossing=bool(
                    tied[n_cross] or (prev is not None and tied[prev])
                ),
            )
        per_cell.append(entry)

    exposed = sum(1 for e in per_cell if e["tie_exposed_at_crossing"])
    out = {
        "schema": "orion.orion21.ladder-tie-exposure.v1",
        "protocol_identity": "ORION21.TIE_ROBUST_PHASE.v1",
        "authority": "DIAGNOSTIC_ONLY",
        "scientific_authority_delta": "NONE",
        "input": {
            "path": path,
            "sha256": digest,
            "sha256_matches_authoritative": digest == EXPECTED_INPUT_SHA256,
        },
        "registered_tau": TAU,
        "registered_primary_quantity": criterion,
        "tie_prevalence": {
            "non_separable_rank_gap_points": tie_points,
            "total_points": total_points,
            "fraction": tie_points / total_points if total_points else None,
        },
        "cells_total": len(per_cell),
        "cells_tie_exposed_at_crossing": exposed,
        "per_cell": per_cell,
        "interpretation_bound": (
            "Establishes tie EXPOSURE of the n_cross crossing. Does NOT establish that "
            "n_cross is set-valued: the ladder readings record only the realised support "
            "selection, so the admissible range is not recoverable from these bytes. "
            "The anchor replay instrument (instrument_precondition_p0) and the ladder "
            "sweep (readings) are DIFFERENT instruments and their magnitudes must not be "
            "transferred: at cell (14,3,3), n=64, seed 2026082201 the anchor replay reads "
            "0.949169921875 while the ladder reads 0.8029296875."
        ),
    }
    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
