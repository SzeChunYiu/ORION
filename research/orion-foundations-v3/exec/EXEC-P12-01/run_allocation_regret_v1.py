"""EXEC-P12-01 -- vector allocation and coarsening regret (OSTC-T17)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


def run(n_actions=3, n_costs=4, n_certs=3):
    """Cases are (certificate, cost-vector). The allocator picks an action.

    A case's cost vector gives the loss of each action. The oracle sees it; the
    certificate-only allocator sees only the certificate, so it must commit to
    one action per certificate value.
    """
    actions = list(range(n_actions))
    costvecs = [v for v in itertools.product(range(n_costs), repeat=n_actions)]

    # oracle: zero hindsight regret by construction, verified not assumed
    oracle_cases = oracle_bad = 0
    for cv in costvecs:
        oracle_cases += 1
        best = min(cv)
        chosen = cv[min(actions, key=lambda a: cv[a])]
        if chosen - best != 0:
            oracle_bad += 1

    # ambiguous classes: two cases sharing a certificate with DIFFERENT unique optima
    def unique_opt(cv):
        m = min(cv)
        winners = [a for a in actions if cv[a] == m]
        return winners[0] if len(winners) == 1 else None

    classes = []
    for cv1, cv2 in itertools.combinations(costvecs, 2):
        o1, o2 = unique_opt(cv1), unique_opt(cv2)
        if o1 is None or o2 is None or o1 == o2:
            continue
        classes.append((cv1, cv2, o1, o2))

    # for EVERY deterministic certificate-only allocator (one action per class),
    # check it pays on at least one member, and the half-gap bound
    zero_regret_escapes = 0
    bound_viol = 0
    tight = 0
    minimal = None
    for cv1, cv2, o1, o2 in classes:
        gaps = []
        best_expected = None
        escaped = False
        for a in actions:                       # the allocator's single choice
            r1 = cv1[a] - min(cv1)
            r2 = cv2[a] - min(cv2)
            if r1 == 0 and r2 == 0:
                escaped = True
            exp = (r1 + r2) / 2.0               # equal prior
            best_expected = exp if best_expected is None else min(best_expected, exp)
        if escaped:
            zero_regret_escapes += 1
        # smaller cross-action loss gap: what each case loses by taking the
        # other's optimum
        g1 = cv1[o2] - cv1[o1]
        g2 = cv2[o1] - cv2[o2]
        smaller_gap = min(g1, g2)
        bound = smaller_gap / 2.0
        if best_expected + 1e-12 < bound:
            bound_viol += 1
            if minimal is None:
                minimal = {"cv1": list(cv1), "cv2": list(cv2), "best_expected": best_expected,
                           "bound": bound, "smaller_gap": smaller_gap}
        if abs(best_expected - bound) < 1e-12:
            tight += 1
        gaps.append(smaller_gap)

    return {
        "oracle": {"cases": oracle_cases, "positive_regret_cases": oracle_bad},
        "ambiguity": {"classes_found": len(classes),
                      "allocators_per_class": n_actions,
                      "classes_with_zero_regret_allocator": zero_regret_escapes},
        "bound": {"classes_checked": len(classes), "violations": bound_viol,
                  "tight_classes": tight, "minimal_witness": minimal},
    }


def main() -> None:
    t0 = time.time()
    grid = {"n_actions": 3, "n_costs": 4, "n_certs": 3, "seed": 20260825}
    r = run(grid["n_actions"], grid["n_costs"], grid["n_certs"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P12-01",
         "grid": grid, **r,
         "totals": {"cases_enumerated": r["oracle"]["cases"] + r["ambiguity"]["classes_found"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    print("oracle cases", r["oracle"]["cases"], "bad", r["oracle"]["positive_regret_cases"])
    print("ambiguous classes", r["ambiguity"]["classes_found"],
          "escapes", r["ambiguity"]["classes_with_zero_regret_allocator"])
    print("bound violations", r["bound"]["violations"], "tight", r["bound"]["tight_classes"])


if __name__ == "__main__":
    main()
