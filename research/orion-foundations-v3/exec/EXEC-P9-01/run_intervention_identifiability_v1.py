"""EXEC-P9-01 -- intervention identifiability of failure location (OSTC-T14)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


def identifiable(H, cause, cols):
    """Cause's row is distinct from every other row on the selected columns."""
    r = tuple(H[cause][c] for c in cols)
    return all(tuple(H[o][c] for c in cols) != r for o in range(len(H)) if o != cause)


def separates_all(H, cols):
    seen = set()
    for row in H:
        k = tuple(row[c] for c in cols)
        if k in seen:
            return False
        seen.add(k)
    return True


def exact_minimum(H, ncols):
    """Smallest column subset separating all rows, by ascending exhaustive search."""
    for k in range(0, ncols + 1):
        for cols in itertools.combinations(range(ncols), k):
            if separates_all(H, cols):
                return k, list(cols)
    return None, None


def greedy_min(H, ncols):
    """Greedy set cover over the pairwise-separation constraints."""
    pairs = [(i, j) for i in range(len(H)) for j in range(i + 1, len(H))]
    unmet = set(pairs)
    chosen = []
    while unmet:
        best, bestcov = None, -1
        for c in range(ncols):
            if c in chosen:
                continue
            cov = sum(1 for (i, j) in unmet if H[i][c] != H[j][c])
            if cov > bestcov:
                best, bestcov = c, cov
        if best is None or bestcov <= 0:
            return None
        chosen.append(best)
        unmet = {(i, j) for (i, j) in unmet if H[i][best] == H[j][best]}
    return len(chosen)


def run(nrows=4, ncols=4, nvals=2):
    cells = ident = unident = viol = 0
    minimal_w = None
    mats = ver_min = non_min = 0
    g_ties = g_worse = g_better = 0

    rows_space = list(itertools.product(range(nvals), repeat=ncols))
    for H in itertools.combinations(rows_space, nrows):
        H = list(H)
        mats += 1
        # identifiability biconditional over all column subsets and causes
        for k in range(0, ncols + 1):
            for cols in itertools.combinations(range(ncols), k):
                for cause in range(nrows):
                    cells += 1
                    a = identifiable(H, cause, cols)
                    # independent notion: no other row collides on these columns
                    r = tuple(H[cause][c] for c in cols)
                    b = sum(1 for o in range(nrows)
                            if tuple(H[o][c] for c in cols) == r) == 1
                    if a:
                        ident += 1
                    else:
                        unident += 1
                    if a != b:
                        viol += 1
                        if minimal_w is None:
                            minimal_w = {"H": [list(x) for x in H], "cols": list(cols), "cause": cause}
        km, _ = exact_minimum(H, ncols)
        if km is None:
            continue
        # verify minimality: no smaller subset separates
        smaller_ok = any(separates_all(H, c)
                         for kk in range(0, km) for c in itertools.combinations(range(ncols), kk))
        if smaller_ok:
            non_min += 1
        else:
            ver_min += 1
        kg = greedy_min(H, ncols)
        if kg is None:
            continue
        if kg == km:
            g_ties += 1
        elif kg > km:
            g_worse += 1
        else:
            g_better += 1

    return {"identifiability": {"cells": cells, "identifiable": ident,
                                "unidentifiable": unident, "violations": viol,
                                "minimal_witness": minimal_w},
            "minimum": {"matrices": mats, "verified_minimum": ver_min, "non_minimum": non_min},
            "greedy": {"ties": g_ties, "greedy_worse": g_worse, "greedy_better": g_better}}


def main() -> None:
    t0 = time.time()
    grid = {"nrows": 4, "ncols": 4, "nvals": 2, "seed": 20260825}
    r = run(grid["nrows"], grid["ncols"], grid["nvals"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P9-01",
         "grid": grid, **r,
         "totals": {"cells_enumerated": r["identifiability"]["cells"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    i = r["identifiability"]
    print("ident cells", i["cells"], "ident", i["identifiable"], "unident",
          i["unidentifiable"], "viol", i["violations"])
    print("minimum verified", r["minimum"]["verified_minimum"], "non_min", r["minimum"]["non_minimum"])
    print("greedy ties", r["greedy"]["ties"], "worse", r["greedy"]["greedy_worse"],
          "better", r["greedy"]["greedy_better"])


if __name__ == "__main__":
    main()
