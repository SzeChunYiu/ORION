#!/usr/bin/env python3
"""ORION-08 successor V3: selection-corrected distributional finite-sample law.

Protocol: PROTOCOL_V3.md (committed before any V3 outcome). Derivation:
DERIVATION_V3.md. Actions selected on a DISJOINT half S of the training rows;
Beta-Binomial posterior-predictive MC conditions on the other half E only
(uniform prior primary, Jeffreys sensitivity). Pooled cohort = the exact V2
16 (hard ids; the A1 registry scan is settled). Scale: per-test-row utility
(division by n_te; V2-equivalent at n_te = n_tr).

Cross-checks (registered, gated): R3a oracle_utility == V2's exactly (same
outer split); R3b MC mean of delta == closed form
sum_s q_s (a_t-a_c)(2(k_s+1)/(n_s+2)-1) within 3*MC-SE.

Exit codes: 0 LAW_V3_CALIBRATED, 1 gate failure, 3 incomplete.
"""

from __future__ import annotations

import argparse
import json
import platform
import warnings
from math import comb
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# ---- frozen from run_real_transfer_cc18_v1.py / V2 ----
U = {(1, 1): 1.0, (1, 0): -1.0, (0, 1): 0.0, (0, 0): 0.0}
K_COARSE = 2
K_EXTRA = 2
N_BINS = 3
SPLIT_SEED = 20260830
MC_SEED = 20260903  # new named constant (PROTOCOL_V3)
MC_DRAWS = 10_000
MC_CHUNK = 2_000

# pooled cohort = the exact V2 sixteen (A1 settled the scan)
COHORT = [(31, "credit-g"), (37, "diabetes"), (44, "spambase"),
          (1494, "qsar-biodeg"), (1510, "wdbc"),
          (1485, "openml-1485"), (1486, "openml-1486"), (1487, "openml-1487"),
          (1489, "openml-1489"), (1590, "openml-1590"), (4134, "openml-4134"),
          (6332, "openml-6332"), (23517, "openml-23517"),
          (40701, "openml-40701"), (40983, "openml-40983"),
          (40994, "openml-40994")]
V2_RESULTS = Path(__file__).resolve().parent.parent / "finite-sample-law-v2" / "RESULTS_V2.json"


def optimal_action(p1: float) -> int:
    return 1 if (U[(1, 1)] * p1 + U[(1, 0)] * (1 - p1)) > (U[(0, 1)] * p1 + U[(0, 0)] * (1 - p1)) else 0


def policy_actions(fibres: np.ndarray, y: np.ndarray) -> dict[int, int]:
    out = {}
    for f in np.unique(fibres):
        m = fibres == f
        out[int(f)] = optimal_action(float(y[m].mean()))
    return out


def oracle_utility(y: np.ndarray) -> float:
    return sum(max(U[(1, int(v))], U[(0, int(v))]) for v in y) / len(y)


def binned(X: np.ndarray, cols, edges) -> np.ndarray:
    code = np.zeros(len(X), dtype=np.int64)
    for c in cols:
        b = np.digitize(X[:, c], edges[c])
        code = code * (N_BINS + 2) + b
    return code


def load_openml(data_id: int):
    from sklearn.datasets import fetch_openml
    d = fetch_openml(data_id=data_id, as_frame=True, parser="auto")
    X = d.data.select_dtypes(include=[np.number]).to_numpy(dtype=float)
    classes = list(dict.fromkeys(d.target.tolist()))
    if X.shape[1] < K_COARSE + K_EXTRA + 1 or len(classes) != 2:
        return None
    y = (d.target.to_numpy() == classes[1]).astype(int)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    return X, y


def predictive_mc(R_E: np.ndarray, yE: np.ndarray, n_te: int,
                  arm_actions_R: dict[str, dict[int, int]],
                  prior: str = "uniform", draws: int = MC_DRAWS,
                  seed: int = MC_SEED) -> dict[str, np.ndarray]:
    """MC of per-test-row held-out utilities; p|E-counts, q_hat = E masses.

    Scale convention (DERIVATION_V3 s5): U(a) = (1/n_te) * sum_s a_s (2K_s-N_s).
    """
    rng = np.random.default_rng(seed)
    fibres = np.unique(R_E)
    F = len(fibres)
    n_f = np.array([(R_E == f).sum() for f in fibres], dtype=float)
    k_f = np.array([yE[R_E == f].sum() for f in fibres], dtype=float)
    q = n_f / n_f.sum()
    q = q / q.sum()
    if prior == "uniform":  # conjugate posterior to Uniform(0,1): mean (k+1)/(n+2)
        a_p, b_p = k_f + 1.0, n_f - k_f + 1.0
    else:  # Jeffreys: Beta(k+1/2, n-k+1/2)
        a_p, b_p = k_f + 0.5, n_f - k_f + 0.5
    act = {arm: np.array([amap[int(f)] for f in fibres], dtype=float)
           for arm, amap in arm_actions_R.items()}
    out = {arm: [] for arm in arm_actions_R}
    done = 0
    while done < draws:
        c = min(MC_CHUNK, draws - done)
        p = rng.beta(a_p, b_p, size=(c, F))
        N = rng.multinomial(n_te, q, size=c).astype(np.int64)
        K = np.empty_like(N)
        for j in range(F):
            K[:, j] = rng.binomial(N[:, j], p[:, j])
        contrib = 2.0 * K - N
        for arm, av in act.items():
            out[arm].append((contrib * av).sum(axis=1) / n_te)
        done += c
    return {arm: np.concatenate(v) for arm, v in out.items()}


def closed_form_mean_delta(R_E, yE, r_to_c, r_to_t, prior="uniform") -> float:
    """E[delta] = sum_s q_s (a_t-a_c)(2 pbar_s - 1); pbar per DERIVATION_V3 s5."""
    fibres = np.unique(R_E)
    tot = 0.0
    for f in fibres:
        m = R_E == f
        nf, kf = float(m.sum()), float(yE[m].sum())
        if prior == "uniform":
            pbar = (kf + 1.0) / (nf + 2.0)
        else:
            pbar = (kf + 0.5) / (nf + 1.0)
        tot += (nf / float(len(yE))) * (r_to_t[int(f)] - r_to_c[int(f)]) * (2.0 * pbar - 1.0)
    return tot


def run_dataset(X: np.ndarray, y: np.ndarray, name: str, data_id: int) -> dict:
    from sklearn.model_selection import train_test_split
    from sklearn.feature_selection import mutual_info_classif

    # outer split: identical to V2 (same seed) -> byte-identical test sets
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.5, random_state=SPLIT_SEED, stratify=y)
    # inner split: S selects (label-dependent), E estimates (posterior)
    Xs, Xe, ys, ye_h = train_test_split(
        Xtr, ytr, test_size=0.5, random_state=SPLIT_SEED, stratify=ytr)

    edges = {c: np.quantile(Xs[:, c], np.linspace(0, 1, N_BINS + 1)[1:-1])
             for c in range(X.shape[1])}
    coarse_cols = list(range(K_COARSE))
    typed_cols = list(range(K_COARSE + K_EXTRA))
    mi = mutual_info_classif(Xs, ys, random_state=SPLIT_SEED)
    extra = int(np.argsort(-mi)[0])
    ig_cols = coarse_cols + ([extra] if extra not in coarse_cols else [])

    # S-stage: fibre actions per arm partition
    cs, ts, is_ = binned(Xs, coarse_cols, edges), binned(Xs, typed_cols, edges), binned(Xs, ig_cols, edges)
    ca, ta, ia = policy_actions(cs, ys), policy_actions(ts, ys), policy_actions(is_, ys)

    # E-stage: refinement on E rows; lift S-actions onto E R-fibres
    r_cols = sorted(set(typed_cols) | set(ig_cols))
    R_E = binned(Xe, r_cols, edges)
    ce, te_, ie = binned(Xe, coarse_cols, edges), binned(Xe, typed_cols, edges), binned(Xe, ig_cols, edges)
    r_to_c, r_to_t, r_to_i = {}, {}, {}
    for rf in np.unique(R_E):
        m = R_E == rf
        # DERIVATION_V3 s6 fallback: arm codes unseen in S score action 0
        # (E-occupied fibres need not be S-occupied; S and E are disjoint)
        r_to_c[int(rf)] = ca.get(int(ce[m][0]), 0)
        r_to_t[int(rf)] = ta.get(int(te_[m][0]), 0)
        r_to_i[int(rf)] = ia.get(int(ie[m][0]), 0)

    arms_R = {"coarse": r_to_c, "refined_typed": r_to_t, "infogain_refine": r_to_i}
    mc = predictive_mc(R_E, ye_h, len(yte), arms_R, "uniform")
    mc_j = predictive_mc(R_E, ye_h, len(yte), arms_R, "jeffreys")

    def summ(mc_dict):
        d = mc_dict["refined_typed"] - mc_dict["coarse"]
        dig = mc_dict["infogain_refine"] - mc_dict["coarse"]
        return {"mean_delta": float(d.mean()), "std_delta": float(d.std(ddof=1)),
                "p_delta_neg": float((d < 0).mean()),
                "ci80": [float(np.quantile(d, 0.10)), float(np.quantile(d, 0.90))],
                "mean_delta_infogain": float(dig.mean()),
                "p_typed_beats_infogain": float((mc_dict["refined_typed"] > mc_dict["infogain_refine"]).mean()),
                "mc_se_mean": float(d.std(ddof=1) / np.sqrt(len(d)))}

    def observed(ftr, fte, amap):
        a = np.array([amap.get(int(f), 0) for f in fte])
        return sum(U[(int(ai), int(v))] for ai, v in zip(a, yte)) / len(yte)

    arms_obs = {"coarse": observed(cs, binned(Xte, coarse_cols, edges), ca),
                "refined_typed": observed(ts, binned(Xte, typed_cols, edges), ta),
                "infogain_refine": observed(is_, binned(Xte, ig_cols, edges), ia)}
    obs_delta = arms_obs["refined_typed"] - arms_obs["coarse"]

    su, sj = summ(mc), summ(mc_j)
    cf_u = closed_form_mean_delta(R_E, ye_h, r_to_c, r_to_t, "uniform")
    return {
        "data_id": data_id, "name": name, "n": int(len(y)), "d": int(X.shape[1]),
        "n_S": int(len(ys)), "n_E": int(len(ye_h)), "n_te": int(len(yte)),
        "n_R_fibres": int(len(np.unique(R_E))),
        "uniform": su, "jeffreys": sj,
        "closed_form_mean_delta": cf_u,
        "mc_vs_closed_form_diff": abs(su["mean_delta"] - cf_u),
        "observed": {"arms": arms_obs, "oracle_utility": oracle_utility(yte),
                     "typed_delta": obs_delta,
                     "typed_sign": int(np.sign(round(obs_delta, 12)))},
        "confident": abs(su["mean_delta"]) > 2 * su["std_delta"],
        "confident_sign": int(np.sign(round(su["mean_delta"], 12))),
    }


def v2_index() -> dict:
    v2 = json.loads(V2_RESULTS.read_text())
    return {r["name"]: r for r in v2.get("rows", []) if "name" in r}


def binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    pmf = [comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = pmf[k]
    return sum(q for q in pmf if q <= obs + 1e-15)


def binom_two_sided_08(inside: int, n: int) -> float:
    p = 0.8
    pmf = [comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
    obs = pmf[inside]
    return sum(q for q in pmf if q <= obs + 1e-15)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_V3.json")
    a = ap.parse_args()

    v2 = v2_index()
    rows = []
    print("Phase R3 — pooled V2 cohort (16), selection-corrected", flush=True)
    for did, name in COHORT:
        Xy = load_openml(did)
        if Xy is None:
            rows.append({"data_id": did, "name": name, "error": "load returned None"})
            continue
        r = run_dataset(*Xy, name, did)
        rows.append(r)
        print(f"  R3 {name:<14} mean={r['uniform']['mean_delta']:+.5f} "
              f"sd={r['uniform']['std_delta']:.5f} P(neg)={r['uniform']['p_delta_neg']:.3f} "
              f"conf={r['confident']} obs_sign={r['observed']['typed_sign']:+d} "
              f"cfchk={r['mc_vs_closed_form_diff']:.2e}", flush=True)

    # ---- registered cross-checks ----
    ora_pairs = [(r["name"], abs(r["observed"]["oracle_utility"]
                                 - v2[r["name"]]["observed"]["oracle_utility"]))
                 for r in rows if "observed" in r and r["name"] in v2]
    ora_max = max(d for _, d in ora_pairs) if ora_pairs else None
    scored = [r for r in rows if "confident" in r]
    cf_bad = [r["name"] for r in scored
              if r["mc_vs_closed_form_diff"] > 3 * r["uniform"]["mc_se_mean"]]

    # ---- gates ----
    g1_bad = [r["name"] for r in scored if r["confident"]
              and r["confident_sign"] != r["observed"]["typed_sign"]]
    inside = sum(1 for r in scored
                 if r["uniform"]["ci80"][0] <= r["observed"]["typed_delta"] <= r["uniform"]["ci80"][1])
    n_tot = len(scored)
    g2_p = binom_two_sided_08(inside, n_tot)
    g2_pass = (g2_p >= 0.05) and n_tot == 16
    # G4: V1-zero stratum (dhat_v1 from V2 rows) still observes exactly 0
    g4_bad = [r["name"] for r in scored
              if r["name"] in v2 and v2[r["name"]].get("predicted_zero_v1")
              and r["observed"]["typed_sign"] != 0]
    jeff_break = [r["name"] for r in scored
                  if not (abs(r["jeffreys"]["mean_delta"]) < 1e-12 or abs(r["uniform"]["mean_delta"]) < 1e-12)
                  and np.sign(r["jeffreys"]["mean_delta"]) != np.sign(r["uniform"]["mean_delta"])]

    # ---- registered diagnostics (non-vetoing) ----
    z_rows = [r for r in scored if r["uniform"]["std_delta"] > 0]
    zsigns = [int(np.sign((r["observed"]["typed_delta"] - r["uniform"]["mean_delta"])
                          / r["uniform"]["std_delta"])) for r in z_rows]
    z_neg = sum(1 for s in zsigns if s < 0)
    d1_p = binom_two_sided(z_neg, len(zsigns)) if zsigns else None
    both = [r for r in scored if r["name"] in v2
            and r["uniform"]["std_delta"] > 0
            and v2[r["name"]]["uniform"]["std_delta"] > 0]
    d2_le = sum(1 for r in both
                if r["uniform"]["mean_delta"] <= v2[r["name"]]["uniform"]["mean_delta"])
    r6332 = next((r for r in scored if r["name"] == "openml-6332"), None)
    d3 = None if r6332 is None else bool(
        r6332["uniform"]["ci80"][0] <= r6332["observed"]["typed_delta"] <= r6332["uniform"]["ci80"][1])

    gates = {
        "R3a_test_set_reproduction": {"n_compared": len(ora_pairs), "max_abs_diff": ora_max,
                                      "pass": bool(ora_pairs) and ora_max is not None and ora_max < 1e-12},
        "R3b_mc_closed_form": {"violations": cf_bad, "pass": not cf_bad},
        "G1_confident_set": {"violations": g1_bad, "pass": not g1_bad},
        "G2_calibration": {"inside": inside, "n": n_tot, "p_value": round(g2_p, 5),
                           "pass": bool(g2_pass)},
        "G4_zero_stratum_selection_robust": {"violations": g4_bad, "pass": not g4_bad},
        "sensitivity_jeffreys": {"sign_breaks": jeff_break, "pass": not jeff_break},
    }
    diags = {
        "D1_z_balance": {"n_neg": z_neg, "n": len(zsigns), "p_value": round(d1_p, 5) if d1_p is not None else None,
                         "attribution_holds": bool(d1_p is not None and d1_p >= 0.05)},
        "D2_optimism_removed": {"n_v3_le_v2": d2_le, "n_both": len(both),
                                "threshold": 8, "holds": bool(d2_le >= 8)},
        "D3_separator_6332": {"inside80": d3},
    }

    structural_ok = gates["R3a_test_set_reproduction"]["pass"] and gates["R3b_mc_closed_form"]["pass"]
    if n_tot != 16:
        terminal, rc = "V3_INCOMPLETE_NO_VERDICT", 3
    elif not structural_ok:
        terminal, rc = "V3_INCOMPLETE_REPRODUCTION_FAILED", 3
    elif gates["G1_confident_set"]["pass"] and gates["G2_calibration"]["pass"] and gates["G4_zero_stratum_selection_robust"]["pass"]:
        terminal = "LAW_V3_CALIBRATED"
        if not gates["sensitivity_jeffreys"]["pass"]:
            terminal += "__SENSITIVITY_BREAK"
        rc = 0
    else:
        failed = [g for g in ("G1_confident_set", "G2_calibration", "G4_zero_stratum_selection_robust")
                  if not gates[g]["pass"]]
        terminal = "LAW_V3_PARTIAL_" + "_".join(g.split("_")[0] for g in failed)
        rc = 1

    out = {
        "schema": "ORION08.FINITE_SAMPLE_LAW.v3",
        "mc": {"draws": MC_DRAWS, "seed": MC_SEED, "chunk": MC_CHUNK},
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "node": platform.node()},
        "rows": rows, "gates": gates, "diagnostics": diags, "terminal": terminal,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"gates": gates, "diagnostics": diags, "terminal": terminal},
                     indent=2, default=str), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
