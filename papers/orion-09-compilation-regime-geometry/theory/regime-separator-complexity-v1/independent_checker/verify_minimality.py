#!/usr/bin/env python3
"""Independent, exhaustive verification of k* = 4 and of the block attribution.

The k* reported by separator_complexity.py comes from a branch-and-bound search.
A search that returns 4 is not by itself proof that no 3-subset works. This
checker proves it a different way, by exhaustive enumeration, and shares no
search logic with the branch-and-bound.

Route 1 -- exhaustive 3-subset refutation.
    Every subset of size <= 3 of the 127 frozen features is enumerated. For each,
    membership in the hitting-set family is decided by bitset union over the
    minimal discernibility sets. If none covers, k* >= 4 is PROVED.

Route 2 -- direct witness verification.
    The claimed 4-feature witness is re-projected over the full 1146-instance
    matrix and its cell structure recomputed from the definition, independently
    of any discernibility machinery.

Route 3 -- block attribution.
    Per-block and per-block-union floors are recomputed so that the causal
    attribution recorded in the R2 addendum can be checked rather than assumed.

Exit codes
    0  k* = 4 proved and the block attribution table computed
    2  a claim failed verification
    3  inputs missing  -- CANNOT_CHECK
"""

from __future__ import annotations

import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
MATRIX = PACKET / "FROZEN_MATRIX.json"
CLAIMED_WITNESS = [15, 30, 39, 42]
BLOCKS = {"V2_33": (0, 33), "donor_path_53": (33, 86), "state_sign_aware_41": (86, 127)}


def floor_of(rows, labels, subset):
    cells: dict[tuple, list[int]] = {}
    for vec, lab in zip(rows, labels):
        key = tuple(vec[j] for j in subset)
        c = cells.setdefault(key, [0, 0])
        c[1 - lab] += 1
    mixed = [c for c in cells.values() if c[0] and c[1]]
    return len(cells), len(mixed), sum(min(c) for c in mixed)


def minimal_sets(rows, labels, n_feat):
    pos = [i for i, l in enumerate(labels) if l == 1]
    neg = [i for i, l in enumerate(labels) if l == 0]
    seen = set()
    for i in pos:
        ri = rows[i]
        for j in neg:
            rj = rows[j]
            m = 0
            for k in range(n_feat):
                if ri[k] != rj[k]:
                    m |= 1 << k
            seen.add(m)
    masks = sorted(seen, key=lambda m: bin(m).count("1"))
    minimal = []
    for m in masks:
        if not any((m & s) == s for s in minimal):
            minimal.append(m)
    return minimal


def main() -> int:
    if not MATRIX.is_file():
        print(json.dumps({"status": "CANNOT_CHECK", "error": f"missing {MATRIX}"}, indent=2))
        return 3
    data = json.loads(MATRIX.read_text())
    rows = [tuple(r) for r in data["matrix"]]
    labels = data["labels"]
    n_feat = data["feature_count"]

    t0 = time.perf_counter()
    minimal = minimal_sets(rows, labels, n_feat)
    n_min = len(minimal)

    # coverage[j] = bitset over minimal-set indices that feature j hits
    coverage = [0] * n_feat
    for idx, m in enumerate(minimal):
        mm = m
        bit = 1 << idx
        while mm:
            b = mm & -mm
            mm ^= b
            coverage[b.bit_length() - 1] |= bit
    full = (1 << n_min) - 1

    # ---- Route 1: exhaustive refutation of every subset of size <= 3 --------
    covers_1 = [j for j in range(n_feat) if coverage[j] == full]
    covers_2, covers_3 = [], []
    for i, j in itertools.combinations(range(n_feat), 2):
        if coverage[i] | coverage[j] == full:
            covers_2.append((i, j))
    pair_union = {}
    for i, j in itertools.combinations(range(n_feat), 2):
        pair_union[(i, j)] = coverage[i] | coverage[j]
    for (i, j), u in pair_union.items():
        for k in range(j + 1, n_feat):
            if u | coverage[k] == full:
                covers_3.append((i, j, k))
                break
    k_star_lower_proved = not (covers_1 or covers_2 or covers_3)
    t_exhaustive = time.perf_counter() - t0

    # ---- Route 2: direct witness verification ------------------------------
    cells_w, mixed_w, floor_w = floor_of(rows, labels, CLAIMED_WITNESS)
    witness_ok = (floor_w == 0 and mixed_w == 0)

    # ---- Route 2b: drop-one guard, no discernibility machinery --------------
    # Routes 1 and 2 both build discernibility sets. If that construction were
    # dropping constraints, both would inherit the fault and k* would be
    # UNDERSTATED. This guard re-derives necessity by direct cell counting only:
    # every 3-subset of the witness must have a strictly positive floor.
    drop_one = {}
    for sub in itertools.combinations(CLAIMED_WITNESS, 3):
        _, _, f = floor_of(rows, labels, list(sub))
        drop_one[",".join(map(str, sub))] = f
    drop_one_ok = all(f > 0 for f in drop_one.values())

    # ---- Route 3: block attribution ----------------------------------------
    table = {}
    for name, (lo, hi) in BLOCKS.items():
        c, m, f = floor_of(rows, labels, list(range(lo, hi)))
        table[name] = {"features": hi - lo, "cells": c, "mixed_cells": m, "floor": f}
    unions = {
        "V2_plus_donor_path": list(range(0, 86)),
        "V2_plus_state": list(range(0, 33)) + list(range(86, 127)),
        "donor_path_plus_state": list(range(33, 127)),
        "all_127": list(range(0, 127)),
    }
    for name, sub in unions.items():
        c, m, f = floor_of(rows, labels, sub)
        table[name] = {"features": len(sub), "cells": c, "mixed_cells": m, "floor": f}

    witness_blocks = Counter()
    for j in CLAIMED_WITNESS:
        for name, (lo, hi) in BLOCKS.items():
            if lo <= j < hi:
                witness_blocks[name] += 1

    report = {
        "schema": "ORION.ORION09.RegimeSeparatorComplexity.MinimalityVerification.v1",
        "independence": ("exhaustive enumeration over subsets; shares no search "
                         "logic with the branch-and-bound in separator_complexity.py"),
        "minimal_discernibility_sets": n_min,
        "route_1_exhaustive_refutation": {
            "subsets_of_size_1_tested": n_feat,
            "subsets_of_size_2_tested": n_feat * (n_feat - 1) // 2,
            "subsets_of_size_3_tested": n_feat * (n_feat - 1) * (n_feat - 2) // 6,
            "covering_subsets_of_size_1": covers_1,
            "covering_subsets_of_size_2": covers_2[:5],
            "covering_subsets_of_size_3": covers_3[:5],
            "k_star_at_least_4_PROVED": k_star_lower_proved,
            "seconds": round(t_exhaustive, 1),
        },
        "route_2_witness": {
            "subset": CLAIMED_WITNESS,
            "size": len(CLAIMED_WITNESS),
            "cells": cells_w,
            "mixed_cells": mixed_w,
            "floor": floor_w,
            "attains_floor_zero": witness_ok,
            "compression_ratio": round(cells_w / len(rows), 6),
            "compression_bound_on_this_map": f"{len(rows) - cells_w}/{len(rows)}",
        },
        "route_2b_drop_one_guard": {
            "purpose": ("independent necessity check by direct cell counting; "
                        "uses no discernibility machinery, so it would expose a "
                        "constraint-dropping fault shared by routes 1 and 2"),
            "floor_of_each_3_subset_of_witness": drop_one,
            "all_strictly_positive": drop_one_ok,
            "reading": ("every coordinate of the witness is individually "
                        "necessary, so the witness is minimal and not merely of "
                        "minimum cardinality"),
        },
        "route_3_block_attribution": {
            "blocks": table,
            "witness_block_composition": dict(witness_blocks),
            "state_block_features_in_witness":
                witness_blocks.get("state_sign_aware_41", 0),
        },
        "k_star": 4 if (k_star_lower_proved and witness_ok and drop_one_ok) else None,
        "status": "PASS" if (k_star_lower_proved and witness_ok and drop_one_ok) else "FAIL",
    }
    (PACKET / "MINIMALITY_VERIFICATION.json").write_text(
        json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
