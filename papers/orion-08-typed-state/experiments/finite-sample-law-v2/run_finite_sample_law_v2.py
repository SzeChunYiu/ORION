#!/usr/bin/env python3
"""ORION-08 successor V2: distributional finite-sample law.

Protocol: PROTOCOL_V2.md (committed before any V2 outcome). Derivation:
DERIVATION_V2.md. Posterior-predictive Monte Carlo of the held-out utility
vector (coarse, refined_typed, infogain_refine) on the common refinement R of
the typed and infogain partitions; quantities P(delta<0), sigma_hat, 80%
central interval, P(typed beats infogain). Phases R2 (retro 5), P2
(prospective fresh 12, continuing V1's ascending scan past openml-1480), D2
(Defects4J, conditional).

Cross-checks (registered): R2 observed arm utilities vs V1 RESULTS (max
|darm| < 1e-9); MC mean of delta vs the closed-form mean of the SAME
R-fibre predictive (max |diff| < 3*MC-SE). V1's parent-posterior dhat is
reported ungated and defines the predicted-zero stratum for G4.

Exit codes: 0 LAW_V2_RETRO_AND_PROSPECTS, 1 gate failure, 3 incomplete.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import urllib.request
import warnings
from math import comb
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# ---- frozen from run_real_transfer_cc18_v1.py ----
U = {(1, 1): 1.0, (1, 0): -1.0, (0, 1): 0.0, (0, 0): 0.0}
K_COARSE = 2
K_EXTRA = 2
N_BINS = 3
SPLIT_SEED = 20260830
MC_SEED = 20260902
MC_DRAWS = 10_000
MC_CHUNK = 2_000

V1_IDS = [31, 37, 44, 1462, 1464, 1494, 1510]
V1P_IDS = [15, 29, 38, 151, 1049, 1050, 1053, 1063, 1067, 1068, 1461, 1480]
RETRO = [(31, "credit-g"), (37, "diabetes"), (44, "spambase"),
         (1494, "qsar-biodeg"), (1510, "wdbc")]
PROSPECT_N = 12
MIN_ROWS = 300
CC18_STUDY_URL = "https://api.openml.org/api/v1/json/study/99"
V1_RESULTS = Path(__file__).resolve().parent.parent / "finite-sample-law-v1" / "RESULTS_V1.json"


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


def predictive_mc(R_tr: np.ndarray, ytr: np.ndarray, n_te: int,
                  arm_actions_R: dict[str, dict[int, int]],
                  prior: str = "uniform", draws: int = MC_DRAWS,
                  seed: int = MC_SEED) -> dict[str, np.ndarray]:
    """MC of held-out utilities of fibre-measurable policies on common
    refinement R, draw-chunked. arm_actions_R: arm -> R-fibre id -> action."""
    rng = np.random.default_rng(seed)
    fibres = np.unique(R_tr)
    F = len(fibres)
    n_f = np.array([(R_tr == f).sum() for f in fibres], dtype=float)
    k_f = np.array([ytr[R_tr == f].sum() for f in fibres], dtype=float)
    q = n_f / n_f.sum()
    q = q / q.sum()
    if prior == "uniform":
        a_p, b_p = k_f + 1.0, n_f - k_f + 2.0
    else:  # Jeffreys: Beta(k+1/2, n-k+1/2)
        a_p, b_p = k_f + 0.5, n_f - k_f + 0.5
    act = {arm: np.array([amap[int(f)] for f in fibres], dtype=float)
           for arm, amap in arm_actions_R.items()}
    n_tr = float(n_f.sum())
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
            out[arm].append((contrib * av).sum(axis=1) / n_tr)
        done += c
    return {arm: np.concatenate(v) for arm, v in out.items()}


def closed_form_mean_delta(R_tr, ytr, n_te, r_to_c, r_to_t, prior="uniform") -> float:
    """E[delta_typed] under the same R-fibre predictive."""
    fibres = np.unique(R_tr)
    tot = 0.0
    n_all = float(len(ytr))
    for f in fibres:
        m = R_tr == f
        nf, kf = float(m.sum()), float(ytr[m].sum())
        if prior == "uniform":
            pbar = (kf + 1.0) / (nf + 2.0)
        else:
            pbar = (kf + 0.5) / (nf + 1.0)
        tot += (nf / n_all) * (r_to_t[int(f)] - r_to_c[int(f)]) * (2.0 * pbar - 1.0)
    return (n_te / n_all) * tot


def uhat_v1(fibres: np.ndarray, y: np.ndarray) -> float:
    """V1 parent-posterior functional (uniform prior) at its own granularity."""
    n = len(y)
    tot = 0.0
    for f in np.unique(fibres):
        m = fibres == f
        nf, kf = int(m.sum()), int(y[m].sum())
        if 2 * kf - nf <= 0:
            continue
        tot += (nf / n) * max(0.0, 2.0 * (kf + 1.0) / (nf + 2.0) - 1.0)
    return tot


def run_dataset(X: np.ndarray, y: np.ndarray, name: str, data_id: int) -> dict:
    from sklearn.model_selection import train_test_split
    from sklearn.feature_selection import mutual_info_classif

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.5, random_state=SPLIT_SEED, stratify=y)
    edges = {c: np.quantile(Xtr[:, c], np.linspace(0, 1, N_BINS + 1)[1:-1])
             for c in range(X.shape[1])}
    coarse_cols = list(range(K_COARSE))
    typed_cols = list(range(K_COARSE + K_EXTRA))
    mi = mutual_info_classif(Xtr, ytr, random_state=SPLIT_SEED)
    extra = int(np.argsort(-mi)[0])
    ig_cols = coarse_cols + ([extra] if extra not in coarse_cols else [])

    ctr, ttr = binned(Xtr, coarse_cols, edges), binned(Xtr, typed_cols, edges)
    itr = binned(Xtr, ig_cols, edges)
    r_cols = sorted(set(typed_cols) | set(ig_cols))
    R_tr = binned(Xtr, r_cols, edges)

    ca, ta, ia = policy_actions(ctr, ytr), policy_actions(ttr, ytr), policy_actions(itr, ytr)
    # lift each arm's action onto R-fibres via a train-row witness (R refines
    # each arm partition on these columns, so the witness is well-defined)
    r_to_c, r_to_t, r_to_i = {}, {}, {}
    for rf in np.unique(R_tr):
        m = R_tr == rf
        r_to_c[int(rf)] = ca[int(ctr[m][0])]
        r_to_t[int(rf)] = ta[int(ttr[m][0])]
        r_to_i[int(rf)] = ia[int(itr[m][0])]

    arms_R = {"coarse": r_to_c, "refined_typed": r_to_t, "infogain_refine": r_to_i}
    mc = predictive_mc(R_tr, ytr, len(yte), arms_R, "uniform")
    mc_j = predictive_mc(R_tr, ytr, len(yte), arms_R, "jeffreys")

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

    arms_obs = {"coarse": observed(ctr, binned(Xte, coarse_cols, edges), ca),
                "refined_typed": observed(ttr, binned(Xte, typed_cols, edges), ta),
                "infogain_refine": observed(itr, binned(Xte, ig_cols, edges), ia)}
    obs_delta = arms_obs["refined_typed"] - arms_obs["coarse"]

    su, sj = summ(mc), summ(mc_j)
    cf_u = closed_form_mean_delta(R_tr, ytr, len(yte), r_to_c, r_to_t, "uniform")
    dhat_v1 = uhat_v1(ttr, ytr) - uhat_v1(ctr, ytr)
    return {
        "data_id": data_id, "name": name, "n": int(len(y)), "d": int(X.shape[1]),
        "n_R_fibres": int(len(np.unique(R_tr))),
        "uniform": su, "jeffreys": sj,
        "closed_form_mean_delta": cf_u,
        "mc_vs_closed_form_diff": abs(su["mean_delta"] - cf_u),
        "dhat_v1_parent_posterior": dhat_v1,
        "predicted_zero_v1": abs(dhat_v1) < 1e-12,
        "observed": {"arms": arms_obs, "oracle_utility": oracle_utility(yte),
                     "typed_delta": obs_delta,
                     "typed_sign": int(np.sign(round(obs_delta, 12)))},
        "confident": abs(su["mean_delta"]) > 2 * su["std_delta"],
        "confident_sign": int(np.sign(round(su["mean_delta"], 12))),
    }


def cc18_ids() -> list[int]:
    req = urllib.request.Request(CC18_STUDY_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        study = json.load(r)
    return sorted({int(x) for x in study["study"]["data"]["data_id"]})


def v1_arm_check(rows: list[dict]) -> dict:
    """Registered R2 cross-check: observed arms vs V1 RESULTS_V1.json."""
    if not V1_RESULTS.is_file():
        return {"status": "V1_RESULTS_ABSENT", "max_abs_diff": None}
    v1 = json.loads(V1_RESULTS.read_text())
    v1_rows = {r["name"]: r for r in v1.get("phase_R", {}).get("rows", []) if "name" in r}
    diffs = []
    for r in rows:
        if "observed" not in r or r["name"] not in v1_rows:
            continue
        for arm, val in r["observed"]["arms"].items():
            vv = v1_rows[r["name"]].get("arms", {}).get(arm)
            if vv is not None:
                diffs.append(abs(val - vv))
    if not diffs:
        return {"status": "V1_ARMS_NOT_COMPARABLE", "max_abs_diff": None}
    return {"status": "OK", "n_compared": len(diffs), "max_abs_diff": max(diffs)}


def binom_two_sided(inside: int, n: int, p: float = 0.8) -> float:
    pmf = [comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
    obs = pmf[inside]
    return sum(q for q in pmf if q <= obs + 1e-15)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_V2.json")
    a = ap.parse_args()

    rows = []
    print("Phase R2 — retro (5)", flush=True)
    for did, name in RETRO:
        r = run_dataset(*load_openml(did), name, did)
        rows.append(r)
        print(f"  R2 {name:<14} mean={r['uniform']['mean_delta']:+.5f} "
              f"sd={r['uniform']['std_delta']:.5f} P(neg)={r['uniform']['p_delta_neg']:.3f} "
              f"conf={r['confident']} obs_sign={r['observed']['typed_sign']:+d} "
              f"cfchk={r['mc_vs_closed_form_diff']:.2e}", flush=True)
    arm_check = v1_arm_check(rows)

    print("Phase P2 — prospective fresh 12 (scan past 1480)", flush=True)
    used = set(V1_IDS) | set(V1P_IDS)
    scored = 0
    for did in [i for i in cc18_ids() if i not in used]:
        if scored >= PROSPECT_N:
            break
        try:
            Xy = load_openml(did)
        except Exception as exc:
            rows.append({"data_id": did, "error": str(exc)[:160]})
            continue
        if Xy is None or len(Xy[1]) < MIN_ROWS:
            continue
        r = run_dataset(*Xy, f"openml-{did}", did)
        rows.append(r)
        scored += 1
        print(f"  P2 openml-{did:<8} mean={r['uniform']['mean_delta']:+.5f} "
              f"sd={r['uniform']['std_delta']:.5f} P(neg)={r['uniform']['p_delta_neg']:.3f} "
              f"conf={r['confident']} obs_sign={r['observed']['typed_sign']:+d}", flush=True)

    d4j_path = Path(os.path.expanduser("~/d4j_data.json"))
    d4j = {"status": "D4J_SKIPPED_DATA_UNAVAILABLE" if not d4j_path.is_file()
           else "D4J_PENDING_RUNNER"}

    # ---- registered gates ----
    scored_rows = [r for r in rows if "confident" in r]
    cf_bad = [r["name"] for r in scored_rows if r["mc_vs_closed_form_diff"] > 3 * r["uniform"]["mc_se_mean"]]
    g1_bad = [r["name"] for r in scored_rows if r["confident"]
              and r["confident_sign"] != r["observed"]["typed_sign"]]
    inside = sum(1 for r in scored_rows
                 if r["uniform"]["ci80"][0] <= r["observed"]["typed_delta"] <= r["uniform"]["ci80"][1])
    n_tot = len(scored_rows)
    g2_p = binom_two_sided(inside, n_tot)
    g2_pass = (g2_p >= 0.05) and n_tot == 17
    g4_bad = [r["name"] for r in scored_rows if r["predicted_zero_v1"]
              and not (r["uniform"]["ci80"][0] <= r["observed"]["typed_delta"] <= r["uniform"]["ci80"][1])]
    jeff_break = [r["name"] for r in scored_rows
                  if not (abs(r["jeffreys"]["mean_delta"]) < 1e-12 or abs(r["uniform"]["mean_delta"]) < 1e-12)
                  and np.sign(r["jeffreys"]["mean_delta"]) != np.sign(r["uniform"]["mean_delta"])]

    gates = {"R2_arm_reproduction": arm_check,
             "R2_mc_closed_form": {"violations": cf_bad, "pass": not cf_bad},
             "G1_confident_set": {"violations": g1_bad, "pass": not g1_bad},
             "G2_calibration": {"inside": inside, "n": n_tot, "p_value": round(g2_p, 5),
                                "pass": bool(g2_pass)},
             "G4_zero_stratum": {"violations": g4_bad, "pass": not g4_bad},
             "sensitivity_jeffreys": {"sign_breaks": jeff_break, "pass": not jeff_break}}
    structural_ok = (arm_check.get("status") == "OK"
                     and arm_check.get("max_abs_diff", 1.0) < 1e-9
                     and not cf_bad)
    if n_tot != 17:
        terminal, rc = "V2_INCOMPLETE_NO_VERDICT", 3
    elif not structural_ok:
        terminal, rc = "V2_INCOMPLETE_REPRODUCTION_FAILED", 3
    elif gates["G1_confident_set"]["pass"] and gates["G2_calibration"]["pass"] and gates["G4_zero_stratum"]["pass"]:
        terminal = "LAW_V2_RETRO_AND_PROSPECTS"
        if not gates["sensitivity_jeffreys"]["pass"]:
            terminal += "__SENSITIVITY_BREAK"
        rc = 0
    else:
        failed = [g for g in ("G1_confident_set", "G2_calibration", "G4_zero_stratum")
                  if not gates[g]["pass"]]
        terminal = "LAW_V2_PARTIAL_" + "_".join(g.split("_")[0] for g in failed)
        rc = 1

    out = {
        "schema": "ORION08.FINITE_SAMPLE_LAW.v2",
        "mc": {"draws": MC_DRAWS, "seed": MC_SEED, "chunk": MC_CHUNK},
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "node": platform.node()},
        "rows": rows, "gates": gates, "phase_D": d4j, "terminal": terminal,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"gates": gates, "terminal": terminal}, indent=2, default=str), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
