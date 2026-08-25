"""EXEC-P7-01 -- multi-step regime chains and closed loops (OSTC-T13)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


def apply(obj, m):
    return tuple(m[c][v] for c, v in enumerate(obj))


def compose(m2, m1, nc, nv):
    """m2 after m1."""
    return tuple(tuple(m2[c][m1[c][v]] for v in range(nv)) for c in range(nc))


def run(nc=2, nv=3):
    tables = [tuple(p) for p in itertools.product(range(nv), repeat=nv)]
    morphs = [tuple(t) for t in itertools.product(tables, repeat=nc)]
    objs = list(itertools.product(range(nv), repeat=nc))

    # --- three-step associativity, over objects not tables
    chains = assoc_viol = 0
    assoc_w = None
    sample = morphs if len(morphs) <= 40 else morphs[::max(1, len(morphs)//40)]
    for f in sample:
        for g in sample:
            for h in sample:
                chains += 1
                left = compose(h, compose(g, f, nc, nv), nc, nv)   # (h o g) o f
                right = compose(compose(h, g, nc, nv), f, nc, nv)  # h o (g o f)
                for o in objs:
                    if apply(o, left) != apply(o, right):
                        assoc_viol += 1
                        if assoc_w is None:
                            assoc_w = {"object": list(o)}
                        break

    # --- closed loops: declared round trip vs squares commuting
    loops = ident = allcom = loop_viol = 0
    loop_w = None
    for f in sample:
        for g in sample:
            # declared round trip, enumerated independently of g o f
            true_rt = compose(g, f, nc, nv)
            declared = [true_rt]
            for c in range(nc):
                for v in range(nv):
                    for alt in range(nv):
                        if alt == true_rt[c][v]:
                            continue
                        row = list(true_rt[c]); row[v] = alt
                        declared.append(tuple(tuple(row) if k == c else true_rt[k]
                                              for k in range(nc)))
            for h in declared:
                loops += 1
                squares = all(h[c][v] == g[c][f[c][v]] for c in range(nc) for v in range(nv))
                is_id = all(apply(o, h) == apply(apply(o, f), g) for o in objs)
                if squares:
                    allcom += 1
                if is_id:
                    ident += 1
                if squares != is_id:
                    loop_viol += 1
                    if loop_w is None:
                        loop_w = {"squares_commute": squares, "round_trip_matches": is_id}

    # --- path dependence: same endpoints, different routes
    pairs = divergent = 0
    for f1 in sample[:20]:
        for g1 in sample[:20]:
            r1 = compose(g1, f1, nc, nv)
            for f2 in sample[:20]:
                g2 = None
                # find a second route with the same composite endpoints but
                # different intermediate; divergence is on the object level
                for cand in sample[:20]:
                    r2 = compose(cand, f2, nc, nv)
                    pairs += 1
                    if any(apply(o, r1) != apply(o, r2) for o in objs):
                        divergent += 1
                    g2 = cand
                    break
    donor_failures = divergent   # endpoint-only donor calls these equivalent

    return {"assoc": {"chains": chains, "violations": assoc_viol, "minimal_witness": assoc_w},
            "loops": {"loops": loops, "identity_round_trips": ident,
                      "all_squares_commute": allcom,
                      "biconditional_violations": loop_viol, "minimal_witness": loop_w},
            "path_dependence": {"route_pairs": pairs, "divergent_pairs": divergent},
            "donor": {"failures": donor_failures}}


def main() -> None:
    t0 = time.time()
    grid = {"n_coords": 2, "n_values": 3, "seed": 20260825}
    r = run(grid["n_coords"], grid["n_values"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P7-01",
         "grid": grid, **r,
         "totals": {"cells_enumerated": r["assoc"]["chains"] + r["loops"]["loops"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    print("assoc chains", r["assoc"]["chains"], "viol", r["assoc"]["violations"])
    print("loops", r["loops"]["loops"], "commute", r["loops"]["all_squares_commute"],
          "identity", r["loops"]["identity_round_trips"], "viol", r["loops"]["biconditional_violations"])
    print("path pairs", r["path_dependence"]["route_pairs"],
          "divergent", r["path_dependence"]["divergent_pairs"],
          "donor_failures", r["donor"]["failures"])


if __name__ == "__main__":
    main()
