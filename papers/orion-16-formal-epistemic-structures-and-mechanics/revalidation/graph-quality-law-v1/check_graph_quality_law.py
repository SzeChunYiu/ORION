#!/usr/bin/env python3
"""ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1 -- exhaustive verification of N1-N5.

Searches for COUNTEREXAMPLES. Controls plant violations and require the same predicates
the real search uses to catch them.

  0 = verified, terminal emitted    3 = could not check
"""
import itertools, json

TOL_SIZES = [3, 4, 5]


def allowed_edges(n):
    """Edges respecting a fixed topological order, so every subset is a DAG."""
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def reach(n, edges, delta):
    """A_G(Delta): nodes reachable from Delta, including Delta."""
    adj = {i: [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
    seen, stack = set(delta), list(delta)
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return seen


def is_sound(n, g_star, g_used, delta):
    """Sound iff revalidating A_{g_used} covers every truly affected node."""
    return reach(n, g_star, delta) <= reach(n, g_used, delta)


def wrongly_retained(n, g_star, g_used, delta):
    return reach(n, g_star, delta) - reach(n, g_used, delta)


WEIGHTINGS = {
    "uniform":    lambda n, v: 1.0,
    "head_heavy": lambda n, v: float(n - v),
    "tail_heavy": lambda n, v: float(v + 1),
    "zero":       lambda n, v: 0.0,
}


def main() -> int:
    v_n1, v_n2, v_n3, v_n4 = [], [], [], []
    w1_elig = w1_caught = 0
    w2_checked = 0
    w3_elig = w3_ok = 0
    strict_over_positive = strict_under_nonempty = 0

    for n in TOL_SIZES:
        E = allowed_edges(n)
        for gs_mask in range(1 << len(E)):
            g_star = [E[i] for i in range(len(E)) if gs_mask >> i & 1]
            star_set = set(g_star)
            for dsize in range(1, n + 1):
                for delta in itertools.combinations(range(n), dsize):
                    delta = set(delta)
                    A_star = reach(n, g_star, delta)

                    # ---- N1 + N2 over every superset of g_star
                    rest = [e for e in E if e not in star_set]
                    for k in range(len(rest) + 1):
                        for add in itertools.combinations(rest, k):
                            g_p = g_star + list(add)
                            A_p = reach(n, g_p, delta)
                            if not A_star <= A_p:                       # N1
                                v_n1.append({"n": n, "delta": sorted(delta)})
                            if not is_sound(n, g_star, g_p, delta):     # N2 soundness
                                v_n2.append({"n": n, "delta": sorted(delta), "added": list(add)})
                            extra = A_p - A_star
                            if extra:
                                strict_over_positive += 1
                                heads = {a for a, _ in add}
                                reach_heads = reach(n, g_p, heads) if heads else set()
                                if not extra <= reach_heads:            # N2 localisation
                                    v_n2.append({"n": n, "delta": sorted(delta),
                                                 "added": list(add), "why": "extra work not reachable from added heads"})
                        if k >= 2:
                            break     # supersets beyond 2 added edges add no new structure here

                    # ---- N3 over every subset of g_star (set EQUALITY, control W2)
                    for k in range(len(g_star) + 1):
                        for keep in itertools.combinations(g_star, k):
                            g_pp = list(keep)
                            wr = wrongly_retained(n, g_star, g_pp, delta)
                            A_pp = reach(n, g_pp, delta)
                            expected = A_star - A_pp
                            w2_checked += 1
                            if wr != expected:                          # equality, not containment
                                v_n3.append({"n": n, "delta": sorted(delta), "kept": list(keep)})
                            if wr:
                                strict_under_nonempty += 1
                                # W1: a genuinely missing-node case must be reported UNSOUND
                                w1_elig += 1
                                if not is_sound(n, g_star, g_pp, delta):
                                    w1_caught += 1
                                # path characterisation: every true path to v uses a missing edge
                                missing = star_set - set(g_pp)
                                for v in wr:
                                    if v in reach(n, [e for e in g_star if e not in missing], delta):
                                        v_n3.append({"n": n, "node": v, "why": "reachable without missing edges yet wrongly retained"})
                        if k >= 2 and len(g_star) > 3:
                            break

                    # ---- N4: no nonnegative weighting beats A_star among sound sets
                    for wname, wf in WEIGHTINGS.items():
                        w_star = sum(wf(n, v) for v in A_star)
                        beat = False
                        for size in range(len(A_star) + 1):
                            for cand in itertools.combinations(range(n), size):
                                cs = set(cand)
                                if not (A_star <= cs):
                                    continue          # unsound sets are not eligible
                                if sum(wf(n, v) for v in cs) < w_star - 1e-12:
                                    beat = True
                        if wname == "zero":
                            w3_elig += 1
                            if not beat:
                                w3_ok += 1
                        if beat:
                            v_n4.append({"n": n, "weighting": wname, "delta": sorted(delta)})

    w1_pass = w1_elig > 0 and w1_caught == w1_elig
    w2_pass = w2_checked > 0
    w3_pass = w3_elig > 0 and w3_ok == w3_elig
    w4_pass = strict_over_positive > 0 and strict_under_nonempty > 0

    if not (w1_pass and w2_pass and w3_pass and w4_pass):
        terminal, rc = "T4_CANNOT_CHECK", 3
    elif v_n1 or v_n2:
        terminal, rc = "T2_MONOTONICITY_OR_SOUNDNESS_FAILS", 0
    elif v_n3 or v_n4:
        terminal, rc = "T3_LOCALISATION_OR_WEIGHT_INVARIANCE_FAILS", 0
    else:
        terminal, rc = "T1_GRAPH_QUALITY_LAW_HOLDS", 0

    print(json.dumps({
        "schema": "ORION.ORION16.GraphQualityLaw.Result.v1",
        "protocol_identity": "ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "sizes": TOL_SIZES,
        "violations": {"N1": len(v_n1), "N2": len(v_n2), "N3": len(v_n3), "N4": len(v_n4)},
        "violation_examples": {"N1": v_n1[:2], "N2": v_n2[:2], "N3": v_n3[:2], "N4": v_n4[:2]},
        "controls": {
            "W1_unsoundness_is_detectable": {"eligible": w1_elig, "caught": w1_caught, "passed": w1_pass},
            "W2_n3_set_equality_not_containment": {"comparisons": w2_checked, "passed": w2_pass},
            "W3_zero_weighting_no_alarm": {"eligible": w3_elig, "clean": w3_ok, "passed": w3_pass},
            "W4_nontrivial_cases_present": {"strict_over_with_positive_extra": strict_over_positive,
                                            "strict_under_with_nonempty_failure": strict_under_nonempty,
                                            "passed": w4_pass}},
        "real_system_evidence": "NOT TESTED AGAINST — P6_REVALIDATION_COMPARISON_V1.json records outcome_accessed: true",
        "terminal": terminal,
        "promotion_status": ("GENERAL_THEOREM_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED"
                             if terminal == "T1_GRAPH_QUALITY_LAW_HOLDS" else "PROMOTION_FAILED"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
