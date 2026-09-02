#!/usr/bin/env python3
"""ORION-08 successor V4: split-ratio invariance of the selection-corrected law.

Protocol: PROTOCOL_RATIO_V1.md (committed before any outcome). Derivation:
DERIVATION_RATIO_V1.md. Tests the calibrated V3 law's untested prediction:
with S-selection disjoint from the E-posterior, calibration is invariant to
the S:E split fraction. Cohort = the frozen V3 sixteen; inner-split grid
e in {0.25, 0.50 (V3 anchor, exact reproduction), 0.75}; every statistical
primitive is the frozen V3 implementation (imported, never re-implemented).

Cross-checks (gated, abort before verdict): R4a exact reproduction of
RESULTS_V3.json at e=0.50 (per-dataset scalars, max|diff| < 1e-12, n=16);
R4b MC-vs-closed-form < 3*MC-SE at every dataset x ratio.

Exit codes: 0 LAW_V4_RATIO_INVARIANT[+__SENSITIVITY_BREAK], 1 partial,
3 incomplete (reproduction failed / cohort not 16).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent.parent  # papers/orion-08-typed-state
V3_DIR = PARENT / "experiments" / "finite-sample-law-v3"
PROTOCOL = HERE / "PROTOCOL_RATIO_V1.md"

# ---- registered constants (PROTOCOL_RATIO_V1.md) ----
E_FRACS = (0.25, 0.50, 0.75)
ANCHOR = 0.50
R4A_TOL = 1e-12
D4_FRAC = 2.0 / 3.0

# ---- frozen V3 machinery (import, not re-implement) ----
_spec = importlib.util.spec_from_file_location(
    "v3_frozen", V3_DIR / "run_finite_sample_law_v3.py")
v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v3)

binned = v3.binned
policy_actions = v3.policy_actions
predictive_mc = v3.predictive_mc
closed_form_mean_delta = v3.closed_form_mean_delta
oracle_utility = v3.oracle_utility
load_openml = v3.load_openml
binom_two_sided = v3.binom_two_sided
binom_two_sided_08 = v3.binom_two_sided_08
COHORT = v3.COHORT
SPLIT_SEED = v3.SPLIT_SEED
K_COARSE, K_EXTRA, N_BINS = v3.K_COARSE, v3.K_EXTRA, v3.N_BINS
U = v3.U


def run_dataset_ratio(X: np.ndarray, y: np.ndarray, name: str, data_id: int,
                      e_frac: float) -> dict:
    """The frozen V3 run_dataset orchestration with the inner-split E-fraction
    parametrized (registered grid). At e_frac=0.50 the call sequence is
    statement-for-statement identical to the frozen module -> byte-exact."""
    from sklearn.model_selection import train_test_split
    from sklearn.feature_selection import mutual_info_classif

    # outer split: identical to V2/V3 (same seed) -> byte-identical test sets
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.5, random_state=SPLIT_SEED, stratify=y)
    # inner split: S selects (label-dependent), E estimates (posterior)
    Xs, Xe, ys, ye_h = train_test_split(
        Xtr, ytr, test_size=e_frac, random_state=SPLIT_SEED, stratify=ytr)

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


def r4a_diffs(row: dict, v3row: dict) -> float:
    """Max |diff| over the registered R4a scalar set for one dataset."""
    vals = [abs(row["uniform"][k] - v3row["uniform"][k]) for k in
            ("mean_delta", "std_delta", "p_delta_neg")]
    vals += [abs(row["uniform"]["ci80"][i] - v3row["uniform"]["ci80"][i]) for i in (0, 1)]
    vals.append(abs(row["jeffreys"]["mean_delta"] - v3row["jeffreys"]["mean_delta"]))
    vals.append(abs(row["observed"]["typed_delta"] - v3row["observed"]["typed_delta"]))
    vals.append(abs(row["observed"]["oracle_utility"] - v3row["observed"]["oracle_utility"]))
    vals.append(abs(row["n_R_fibres"] - v3row["n_R_fibres"]))
    vals.append(abs(row["closed_form_mean_delta"] - v3row["closed_form_mean_delta"]))
    return max(vals)


def ratio_gates(rows: list, v2: dict) -> dict:
    """V3's gate definitions, evaluated on one ratio's rows."""
    scored = [r for r in rows if "confident" in r]
    g1_bad = [r["name"] for r in scored if r["confident"]
              and r["confident_sign"] != r["observed"]["typed_sign"]]
    inside = sum(1 for r in scored
                 if r["uniform"]["ci80"][0] <= r["observed"]["typed_delta"] <= r["uniform"]["ci80"][1])
    n_tot = len(scored)
    g2_p = binom_two_sided_08(inside, n_tot)
    g4_bad = [r["name"] for r in scored
              if r["name"] in v2 and v2[r["name"]].get("predicted_zero_v1")
              and r["observed"]["typed_sign"] != 0]
    jeff_break = [r["name"] for r in scored
                  if not (abs(r["jeffreys"]["mean_delta"]) < 1e-12 or abs(r["uniform"]["mean_delta"]) < 1e-12)
                  and np.sign(r["jeffreys"]["mean_delta"]) != np.sign(r["uniform"]["mean_delta"])]
    z_rows = [r for r in scored if r["uniform"]["std_delta"] > 0]
    zsigns = [int(np.sign((r["observed"]["typed_delta"] - r["uniform"]["mean_delta"])
                          / r["uniform"]["std_delta"])) for r in z_rows]
    z_neg = sum(1 for s in zsigns if s < 0)
    d1_p = binom_two_sided(z_neg, len(zsigns)) if zsigns else None
    return {
        "G1_confident_set": {"violations": g1_bad, "pass": not g1_bad,
                             "n_confident": sum(1 for r in scored if r["confident"])},
        "G2_calibration": {"inside": inside, "n": n_tot,
                           "p_value": round(g2_p, 5),
                           "pass": bool(g2_p >= 0.05 and n_tot == 16)},
        "G4_zero_stratum_selection_robust": {"violations": g4_bad, "pass": not g4_bad},
        "sensitivity_jeffreys": {"sign_breaks": jeff_break, "pass": not jeff_break},
        "D1_z_balance": {"n_neg": z_neg, "n": len(zsigns),
                         "p_value": round(d1_p, 5) if d1_p is not None else None,
                         "no_one_sided_optimism": bool(d1_p is not None and d1_p >= 0.05)},
        "coverage_inside": inside,
    }


def content_digest(obj: dict) -> str:
    body = {k: v for k, v in obj.items() if k != "result_digest"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
        .encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_RATIO_V1.json")
    ap.add_argument("--smoke", action="store_true",
                    help="truncated 3-dataset pass to stdout only; writes no receipt")
    a = ap.parse_args()

    v2 = v3.v2_index()
    v3res = json.loads((V3_DIR / "RESULTS_V3.json").read_text())
    v3rows = {r["name"]: r for r in v3res.get("rows", []) if "name" in r}
    cohort = COHORT[:3] if a.smoke else COHORT

    all_rows, structural = {}, {"R4a": None, "R4b": {"violations": []}}
    for e in E_FRACS:
        rows = []
        for did, name in cohort:
            Xy = load_openml(did)
            if Xy is None:
                rows.append({"data_id": did, "name": name, "error": "load returned None"})
                continue
            r = run_dataset_ratio(*Xy, name, did, e)
            rows.append(r)
            print(f"  e={e:.2f} {name:<14} mean={r['uniform']['mean_delta']:+.5f} "
                  f"sd={r['uniform']['std_delta']:.5f} nR={r['n_R_fibres']} "
                  f"conf={r['confident']} obs_sign={r['observed']['typed_sign']:+d} "
                  f"cfchk={r['mc_vs_closed_form_diff']:.2e}", flush=True)
        all_rows[e] = rows
        structural["R4b"]["violations"] += [
            f"{r['name']}@{e}" for r in rows if "confident" in r
            and r["mc_vs_closed_form_diff"] > 3 * r["uniform"]["mc_se_mean"]]

    # ---- R4a: exact reproduction of V3 at the anchor ----
    anchor_rows = all_rows[ANCHOR]
    pairs = [(r["name"], r4a_diffs(r, v3rows[r["name"]]))
             for r in anchor_rows if "confident" in r and r["name"] in v3rows]
    r4a_max = max(d for _, d in pairs) if pairs else None
    structural["R4a"] = {
        "n_compared": len(pairs), "max_abs_diff": r4a_max,
        "tol": R4A_TOL,
        "pass": bool(pairs) and r4a_max is not None and r4a_max < R4A_TOL
        and (len(pairs) == 16 or a.smoke)}
    print(f"R4a anchor reproduction: n={len(pairs)} max|diff|={r4a_max} "
          f"{'PASS' if structural['R4a']['pass'] else 'FAIL'}", flush=True)

    # ---- monitoring: anchor coverage must equal V3's 12/16 ----
    anchor_cov = ratio_gates(anchor_rows, v2)["coverage_inside"]
    monitoring = {"anchor_coverage_inside": anchor_cov, "v3_coverage_inside": 12,
                  "match": anchor_cov == 12 or a.smoke}

    gates = {f"{e}": ratio_gates(all_rows[e], v2) for e in E_FRACS if e != ANCHOR}

    # ---- D4 width ordering (diagnostic) ----
    by_name = {e: {r["name"]: r for r in all_rows[e] if "confident" in r} for e in E_FRACS}
    nz = [n for n in by_name[0.25]
          if all(by_name[e][n]["uniform"]["std_delta"] > 0 for e in E_FRACS)]
    mono = [n for n in nz
            if by_name[0.25][n]["uniform"]["std_delta"] >= by_name[0.50][n]["uniform"]["std_delta"]
            >= by_name[0.75][n]["uniform"]["std_delta"]]
    d4 = {"n_stratum": len(nz), "n_monotone": len(mono),
          "threshold": int(-(-len(nz) * 2 // 3)) if nz else 0,
          "holds": bool(nz) and len(mono) >= D4_FRAC * len(nz)}

    # ---- D5 separator dose-response (diagnostic) ----
    r6332 = {e: next((r for r in all_rows[e] if r["name"] == "openml-6332"), None)
             for e in E_FRACS}
    d5 = {f"{e}": (None if r6332[e] is None else {
        "inside80": bool(r6332[e]["uniform"]["ci80"][0] <= r6332[e]["observed"]["typed_delta"]
                         <= r6332[e]["uniform"]["ci80"][1]),
        "n_R_fibres": r6332[e]["n_R_fibres"]}) for e in E_FRACS}

    n_ok = all(len([r for r in all_rows[e] if "confident" in r]) ==
               (3 if a.smoke else 16) for e in E_FRACS)
    struct_ok = structural["R4a"]["pass"] and not structural["R4b"]["violations"]
    core = ("G1_confident_set", "G2_calibration", "G4_zero_stratum_selection_robust")
    if not n_ok:
        terminal, rc = "V4_INCOMPLETE_NO_VERDICT", 3
    elif not struct_ok:
        terminal, rc = ("V4_INCOMPLETE_REPRODUCTION_FAILED"
                        if not structural["R4a"]["pass"] else "V4_INCOMPLETE_MC_CLOSED_FORM"), 3
    else:
        failed = [f"{g}@{e}" for e, gs in gates.items() for g in core if not gs[g]["pass"]]
        if not failed:
            terminal = "LAW_V4_RATIO_INVARIANT"
            if any(not gs["sensitivity_jeffreys"]["pass"] for gs in gates.values()):
                terminal += "__SENSITIVITY_BREAK"
            rc = 0
        else:
            terminal = "LAW_V4_RATIO_PARTIAL_" + "_".join(
                f.replace("_", "-") for f in failed)
            rc = 1

    if a.smoke:
        print(json.dumps({"smoke": True, "structural": structural,
                          "gates": gates, "terminal_preview": terminal},
                         indent=2, default=str), flush=True)
        print("SMOKE DONE (no receipt written)", flush=True)
        return 0

    try:
        base_rev = subprocess.run(
            ["/usr/bin/git", "-C", str(PARENT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        base_rev = "unavailable"

    out = {
        "schema": "ORION08.SPLIT_RATIO_INVARIANCE.v1",
        "design": {"e_fracs": list(E_FRACS), "anchor": ANCHOR,
                   "cohort": "V3_SIXTEEN_HARD_IDS", "mc": v3res.get("mc"),
                   "r4a_tol": R4A_TOL, "d4_frac": D4_FRAC},
        "base_revision": base_rev,
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "structural": structural,
        "monitoring": monitoring,
        "gates": gates,
        "diagnostics": {"D4_width_ordering": d4, "D5_separator_6332": d5},
        "rows": {f"{e}": all_rows[e] for e in E_FRACS},
        "authority": {
            "law_scope": ("SPLIT_FRACTION_INVARIANCE_OF_THE_SELECTION_CORRECTED"
                          "_BETA_BINOMIAL_PREDICTIVE_ON_THE_FROZEN_16_DATASET_"
                          "OPENML_CC18_COHORT"),
            "authority_limits": ("single frozen 16-dataset OpenML-CC18 cohort; "
                                 "registered grid e in {0.25,0.75}; frozen V3 "
                                 "estimator only; no transfer beyond the cohort; "
                                 "no superiority claim over any baseline; no "
                                 "cohort-transfer claim (registry exhausted)"),
            "novelty_authority": False,
            "journal_authority": False,
            "submission_authorized": False,
            "physical_quantum_advantage_claim": False,
        },
        "environment": {"python": platform.python_version(),
                        "numpy": np.__version__, "node": platform.node()},
        "terminal": terminal,
    }
    out["result_digest"] = content_digest(out)
    Path(HERE / a.emit).write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"structural": structural, "monitoring": monitoring,
                      "gates": gates,
                      "diagnostics": {"D4_width_ordering": d4,
                                      "D5_separator_6332": d5},
                      "terminal": terminal}, indent=2, default=str), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
