"""EXEC-P11-01 -- state/computation placement phase diagram (OSTC-T16, T18)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


# ---------------- T16: placement phase law
def least_horizon_by_search(K: int, d: int, c: int, umax: int) -> int | None:
    """Least integer U with K+Uc < Ud, found by search rather than by formula."""
    for u in range(1, umax + 1):
        if K + u * c < u * d:
            return u
    return None


def t16(Kmax=40, vmax=8, umax=400) -> dict:
    cells = mism = dominant = 0
    minimal = None
    for K in range(0, Kmax + 1):
        for d in range(1, vmax + 1):
            for c in range(0, d):          # d > c, the theorem's stated branch
                cells += 1
                searched = least_horizon_by_search(K, d, c, umax)
                closed = K // (d - c) + 1
                if searched is not None:
                    dominant += 1
                if searched != closed:
                    mism += 1
                    if minimal is None:
                        minimal = {"K": K, "d": d, "c": c, "searched": searched, "closed_form": closed}
    # The d<=c branch. The closed form does not apply there and compilation must
    # never dominate at any horizon -- without this the phase diagram has only one
    # phase in it, and "compiled dominates" would be unfalsifiable on this grid.
    nondominant_cells = spurious = 0
    spurious_witness = None
    for K in range(0, Kmax + 1):
        for d in range(1, vmax + 1):
            for c in range(d, vmax + 1):   # c >= d
                nondominant_cells += 1
                if least_horizon_by_search(K, d, c, umax) is not None:
                    spurious += 1
                    if spurious_witness is None:
                        spurious_witness = {"K": K, "d": d, "c": c}

    # vector-resource branch: dominance is Pareto/price relative, so a
    # Pareto-incomparable pair must exist with no scalar crossover
    incomparable = 0
    inc_witness = None
    for a in itertools.product(range(1, 5), repeat=2):
        for b in itertools.product(range(1, 5), repeat=2):
            better = all(x <= y for x, y in zip(a, b)) and a != b
            worse = all(x >= y for x, y in zip(a, b)) and a != b
            if not better and not worse and a != b:
                incomparable += 1
                if inc_witness is None:
                    inc_witness = {"cost_vector_a": list(a), "cost_vector_b": list(b),
                                   "note": "neither Pareto-dominates; no scalar crossover without prices"}
    return {"cells": cells, "closed_form_mismatches": mism,
            "compiled_dominant_cells": dominant,
            "nondominant_cells_examined": nondominant_cells,
            "spurious_dominance_in_nondominant_branch": spurious,
            "spurious_witness": spurious_witness,
            "vector_pareto_incomparable": incomparable,
            "vector_witness": inc_witness, "minimal_witness": minimal}


# ---------------- T18: responsibility-relative sufficiency
def partitions(n: int):
    """All set partitions of range(n), as tuples of frozensets."""
    if n == 0:
        yield ()
        return
    def helper(elems):
        if not elems:
            yield []
            return
        first, rest = elems[0], elems[1:]
        for smaller in helper(rest):
            for i in range(len(smaller)):
                yield smaller[:i] + [[first] + smaller[i]] + smaller[i + 1:]
            yield [[first]] + smaller
    for p in helper(list(range(n))):
        yield tuple(frozenset(b) for b in p)


def refines(a, b) -> bool:
    """a refines b: every block of a sits inside some block of b."""
    return all(any(bl <= bb for bb in b) for bl in a)


def sufficient(pz, pr) -> bool:
    """Sufficient for r: pz never merges two elements that pr separates."""
    for bl in pz:
        for x in bl:
            for y in bl:
                if not any(x in bb and y in bb for bb in pr):
                    return False
    return True


def join(ps):
    """Common refinement: intersect blocks across all partitions."""
    cur = [frozenset(range(max(max(b) for p in ps for b in p) + 1))]
    for p in ps:
        nxt = []
        for a in cur:
            for b in p:
                if a & b:
                    nxt.append(a & b)
        cur = nxt
    return tuple(cur)


def t18(n=4) -> dict:
    allp = list(partitions(n))
    pairs = suff_viol = 0
    minimal = None
    for pz in allp:
        for pr in allp:
            pairs += 1
            if sufficient(pz, pr) != refines(pz, pr):
                suff_viol += 1
                if minimal is None:
                    minimal = {"pi_Z": [sorted(b) for b in pz], "pi_r": [sorted(b) for b in pr],
                               "sufficient": sufficient(pz, pr), "refines": refines(pz, pr)}
    # coarsest jointly sufficient == common refinement
    coarsest_viol = 0
    fams = 0
    for fam in itertools.combinations(allp, 2):
        fams += 1
        j = join(list(fam))
        if not all(refines(j, pr) for pr in fam):
            coarsest_viol += 1
            continue
        for cand in allp:
            if cand == j:
                continue
            # strictly coarser than j, and still jointly sufficient -> violation
            if refines(j, cand) and not refines(cand, j) and all(refines(cand, pr) for pr in fam):
                coarsest_viol += 1
                break
    # freshness donor: must fail in BOTH directions
    fresh_unsafe = stale_safe = 0
    for pz in allp:
        for pr in allp:
            safe = refines(pz, pr)
            for fresh in (True, False):
                if fresh and not safe:
                    fresh_unsafe += 1
                if (not fresh) and safe:
                    stale_safe += 1
    return {"pairs": pairs, "sufficiency_violations": suff_viol,
            "families_examined": fams, "coarsest_violations": coarsest_viol,
            "freshness_admits_unsafe": fresh_unsafe, "freshness_refuses_safe": stale_safe,
            "minimal_witness": minimal}


def main() -> None:
    t0 = time.time()
    grid = {"t16_Kmax": 40, "t16_vmax": 8, "t16_umax": 400, "t18_n": 4, "seed": 20260825}
    a = t16(grid["t16_Kmax"], grid["t16_vmax"], grid["t16_umax"])
    b = t18(grid["t18_n"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P11-01",
         "grid": grid, "t16": a, "t18": b,
         "totals": {"cells_enumerated": a["cells"] + b["pairs"] + b["families_examined"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    print("t16 cells", a["cells"], "mismatches", a["closed_form_mismatches"],
          "dominant", a["compiled_dominant_cells"],
          "| d<=c cells", a["nondominant_cells_examined"],
          "spurious_dominance", a["spurious_dominance_in_nondominant_branch"],
          "| pareto_incomparable", a["vector_pareto_incomparable"])
    print("t18 pairs", b["pairs"], "suff_viol", b["sufficiency_violations"],
          "coarsest_viol", b["coarsest_violations"],
          "fresh_unsafe", b["freshness_admits_unsafe"], "stale_safe", b["freshness_refuses_safe"])


if __name__ == "__main__":
    main()
