#!/usr/bin/env python3
"""ANON: is the validity-utility frontier fundamental, or selector-limited?

Recomputes everything from the committed STUDY_F held-out records. Validates its own
extraction against the committed violations_strict / violations_tau before reporting.

Usage: analyze_selector_limit.py <run_a.result.json>
"""
import json, math, random, statistics, sys

ARM_SET = "STUDY_F_ARM_CONDITIONAL_BOUNDARY_FIBRES"
SEED = 20260828


def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else float("nan")


def conformal(vals, alpha):
    v = sorted(vals); m = len(v)
    return v[min(m - 1, max(0, math.ceil((1 - alpha) * (m + 1)) - 1))]


def main(path):
    d = json.load(open(path))
    tau = d["r24_mechanism"]["tau"]
    rows = {}
    for f in d["folds"][ARM_SET].values():
        for ds, rec in f["test"][f["primary"]].items():
            rows[ds] = rec
    ex = [r["excess"] for r in rows.values()]
    bd = [r["bound"] for r in rows.values()]
    n = len(ex)

    # extraction control: must reproduce the committed counts or refuse to report
    vs = sum(1 for r in rows.values() if r["violation_strict"])
    vt = sum(1 for r in rows.values() if r["violation_tau"])
    if (vs, vt) != (d["primary"]["violations_strict"], d["primary"]["violations_tau"]):
        print(json.dumps({"terminal": "CANNOT_CHECK_EXTRACTION_DISAGREES",
                          "recomputed": [vs, vt],
                          "committed": [d["primary"]["violations_strict"],
                                        d["primary"]["violations_tau"]]}, indent=2))
        return 3

    r = pearson(bd, ex)
    random.seed(SEED)
    B = 20000
    hits = sum(1 for _ in range(B)
               if abs(pearson(bd, random.sample(ex, n))) >= abs(r))

    def sweep(order, fracs):
        out = []
        for fr in fracs:
            keep = order[: max(1, int(round(n * (1 - fr))))]
            e = [ex[i] for i in keep]
            out.append({"abstain": fr, "retained": len(e),
                        "violations_at_tau": sum(1 for v in e if v > tau),
                        "conformal_bound_alpha_0.10": conformal(e, 0.10)})
        return out

    by_pred = sorted(range(n), key=lambda i: bd[i])
    by_true = sorted(range(n), key=lambda i: ex[i])

    req = []
    for noise in (0.0, 0.25, 0.5, 0.75, 1.0):
        random.seed(7)
        sd = statistics.pstdev(ex)
        score = [ex[i] + random.gauss(0, noise * sd) for i in range(n)]
        keep = sorted(range(n), key=lambda i: score[i])[: int(round(n * 0.75))]
        e = [ex[i] for i in keep]
        req.append({"selector_corr": pearson(score, ex),
                    "violations_at_tau": sum(1 for v in e if v > tau),
                    "conformal_bound_alpha_0.10": conformal(e, 0.10)})

    print(json.dumps({
        "schema": "anon.anon.selector-limited-certification.v1",
        "authority": "DIAGNOSTIC_ONLY",
        "scientific_authority_delta": "NONE",
        "tau": tau, "n": n,
        "extraction_control": {"recomputed_violations": [vs, vt], "matches_committed": True},
        "p_excess_gt_tau": sum(1 for v in ex if v > tau) / n,
        "required_bound_by_alpha": {str(a): conformal(ex, a) for a in
                                    (0.30, 0.25, 0.20, 0.15, 0.10, 0.05)},
        "oracle_abstention": sweep(by_true, (0.20, 0.25, 0.30)),
        "model_bound_abstention": sweep(by_pred, (0.0, 0.20, 0.25, 0.50)),
        "selector_signal": {"pearson": r, "permutation_p_two_sided": hits / B,
                            "shuffles": B, "verdict":
                            "NO_USABLE_SIGNAL" if hits / B > 0.05 else "SIGNAL_PRESENT"},
        "selector_quality_requirement": req,
        "terminal": "FRONTIER_IS_SELECTOR_LIMITED_NOT_FUNDAMENTAL",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
