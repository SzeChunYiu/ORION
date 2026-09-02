#!/usr/bin/env python3
"""ORION-08 successor: finite-sample refinement law.

Protocol: PROTOCOL_V1.md (committed before any outcome). Derivation:
DERIVATION_V1.md. Reproduces the v1 CC18 setting exactly, adds the
posterior-predictive utility U-hat per arm, retrodicts the recorded
out-of-sample signs (phase R), scores a pre-registered prospective CC18
cohort (phase P), and retrodicts Defects4J when ~/d4j_data.json exists
(phase D, else D4J_SKIPPED_DATA_UNAVAILABLE).

Exit codes: 0 retro+prospective pass, 1 retrodiction refuted, 2 prospective
fail, 3 no contrast or data unavailable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import urllib.request
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# ---- frozen from run_real_transfer_cc18_v1.py (byte-for-byte semantics) ----
U = {(1, 1): 1.0, (1, 0): -1.0, (0, 1): 0.0, (0, 0): 0.0}
K_COARSE = 2
K_EXTRA = 2
N_BINS = 3
MIN_MASS = 1
SPLIT_SEED = 20260830

V1_IDS = [31, 37, 44, 1462, 1464, 1494, 1510]           # declared by v1
RETRO = [(31, "credit-g", -1), (37, "diabetes", -1), (44, "spambase", +1),
         (1494, "qsar-biodeg", 0), (1510, "wdbc", -1)]  # recorded signs
PROSPECT_N = 12
MIN_ROWS = 300
CC18_STUDY_URL = "https://api.openml.org/api/v1/json/study/99"
EPS = 1e-12


def optimal_action(p1: float) -> int:
    return 1 if (U[(1, 1)] * p1 + U[(1, 0)] * (1 - p1)) > (U[(0, 1)] * p1 + U[(0, 0)] * (1 - p1)) else 0


def policy_utility(fibres: np.ndarray, y: np.ndarray):
    total, actions = 0.0, {}
    for f in np.unique(fibres):
        m = fibres == f
        p1 = float(y[m].mean())
        a = optimal_action(p1)
        actions[int(f)] = a
        total += sum(U[(a, int(v))] for v in y[m])
    return total / len(y), actions


def oracle_utility(y: np.ndarray) -> float:
    return sum(max(U[(1, int(v))], U[(0, int(v))]) for v in y) / len(y)


def binned(X: np.ndarray, cols, edges) -> np.ndarray:
    code = np.zeros(len(X), dtype=np.int64)
    for c in cols:
        b = np.digitize(X[:, c], edges[c])
        code = code * (N_BINS + 2) + b
    return code


def uhat(fibres: np.ndarray, y: np.ndarray, prior: str = "uniform") -> float:
    """Posterior-predictive expected utility of the plug-in policy.

    uniform: p̄=(k+1)/(n+2), shrink form max(0,(2k−n)/(n+2)) (lemma).
    jeffreys: p̄=(k+1/2)/(n+1).
    """
    n = len(y)
    tot = 0.0
    for f in np.unique(fibres):
        m = fibres == f
        nf, kf = int(m.sum()), int(y[m].sum())
        a = 1 if (2 * kf - nf) > 0 else 0  # MLE action at threshold 1/2
        if a == 0:
            continue
        if prior == "uniform":
            pbar = (kf + 1.0) / (nf + 2.0)
        elif prior == "jeffreys":
            pbar = (kf + 0.5) / (nf + 1.0)
        else:
            raise ValueError(prior)
        tot += (nf / n) * max(0.0, 2.0 * pbar - 1.0)
    return tot


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


def run_dataset(X: np.ndarray, y: np.ndarray, name: str, data_id: int) -> dict:
    from sklearn.model_selection import train_test_split
    from sklearn.feature_selection import mutual_info_classif

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.5, random_state=SPLIT_SEED, stratify=y)
    edges = {c: np.quantile(Xtr[:, c], np.linspace(0, 1, N_BINS + 1)[1:-1])
             for c in range(X.shape[1])}
    coarse_cols = list(range(K_COARSE))
    refined_cols = list(range(K_COARSE + K_EXTRA))

    ctr, rtr = binned(Xtr, coarse_cols, edges), binned(Xtr, refined_cols, edges)
    mi = mutual_info_classif(Xtr, ytr, random_state=SPLIT_SEED)
    extra = int(np.argsort(-mi)[0])
    ig_cols = coarse_cols + ([extra] if extra not in coarse_cols else [])
    itr = binned(Xtr, ig_cols, edges)

    # ---- predictions: train-only, logged before any test score ----
    preds = {arm: {"uhat_uniform": uhat(fb, ytr, "uniform"),
                   "uhat_jeffreys": uhat(fb, ytr, "jeffreys")}
             for arm, fb in (("coarse", ctr), ("refined_typed", rtr),
                             ("infogain_refine", itr))}
    dhat_typed = preds["refined_typed"]["uhat_uniform"] - preds["coarse"]["uhat_uniform"]
    dhat_ig = preds["infogain_refine"]["uhat_uniform"] - preds["coarse"]["uhat_uniform"]
    predicted_typed_sign = int(np.sign(round(dhat_typed, 12)))
    predicted_winner = ("refined_typed" if dhat_typed >= dhat_ig else "infogain_refine")

    # ---- held-out scoring (v1 arms, same formulas) ----
    cte, rte = binned(Xte, coarse_cols, edges), binned(Xte, refined_cols, edges)
    ite = binned(Xte, ig_cols, edges)
    _, ca = policy_utility(ctr, ytr)
    _, ra = policy_utility(rtr, ytr)
    _, ia = policy_utility(itr, ytr)

    def apply(actions, fib):
        a = np.array([actions.get(int(f), 0) for f in fib])
        return sum(U[(int(ai), int(v))] for ai, v in zip(a, yte)) / len(yte)

    orc = oracle_utility(yte)
    arms = {"coarse": apply(ca, cte), "refined_typed": apply(ra, rte),
            "infogain_refine": apply(ia, ite)}
    gap = orc - arms["coarse"]
    observed_typed_delta = arms["refined_typed"] - arms["coarse"]
    observed_winner = ("refined_typed" if arms["refined_typed"] >= arms["infogain_refine"]
                       else "infogain_refine")
    return {
        "data_id": data_id, "name": name, "n": int(len(y)), "d": int(X.shape[1]),
        "predictions": preds,
        "dhat_typed_uniform": dhat_typed,
        "dhat_typed_jeffreys": (preds["refined_typed"]["uhat_jeffreys"]
                                - preds["coarse"]["uhat_jeffreys"]),
        "predicted_typed_sign": predicted_typed_sign,
        "predicted_arm_winner": predicted_winner,
        "arms": arms, "oracle_utility": orc,
        "observed_typed_delta": observed_typed_delta,
        "observed_typed_sign": int(np.sign(round(observed_typed_delta, 12))),
        "observed_arm_winner": observed_winner,
        "sign_agrees": predicted_typed_sign == int(np.sign(round(observed_typed_delta, 12))),
        "winner_agrees": predicted_winner == observed_winner,
    }


def cc18_ids() -> list[int]:
    """Canonical CC18 member dataset ids from the OpenML study registry.

    Verified structure 2026-09-02: study.data.data_id is the member list.
    """
    req = urllib.request.Request(CC18_STUDY_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        study = json.load(r)
    ids = sorted({int(x) for x in study["study"]["data"]["data_id"]})
    if not ids:
        raise RuntimeError("CC18 study 99 returned no dataset ids")
    return ids


def phase_retro() -> tuple[list[dict], bool, list[str]]:
    rows, notes, ok = [], [], True
    v1_path = Path(__file__).resolve().parents[1] / "real-transfer-cc18-v1" / "RESULTS_V1.json"
    v1_rows = {r["name"]: r for r in json.loads(v1_path.read_text())["rows"]
               if "arms" in r} if v1_path.is_file() else {}
    for did, name, recorded in RETRO:
        try:
            Xy = load_openml(did)
            if Xy is None:
                rows.append({"data_id": did, "name": name,
                             "error": "v1-scored dataset no longer passes filter"})
                ok = False
                continue
            r = run_dataset(*Xy, name, did)
            r["recorded_v1_sign"] = recorded
            r["retro_agrees"] = (r["predicted_typed_sign"] == recorded)
            if not r["retro_agrees"]:
                ok = False
            # protocol cross-check: reproduce v1's scored arms
            if name in v1_rows:
                repro = max(abs(r["arms"][k] - v1_rows[name]["arms"][k])
                            for k in ("coarse", "refined_typed", "infogain_refine"))
                r["v1_arm_reproduction_max_abs_diff"] = repro
                if repro >= 1e-9:
                    ok = False
                    r["retro_agrees"] = False
                    notes.append(f"retro {name}: arm reproduction diff {repro:.3e} >= 1e-9")
            rows.append(r)
            print(f"  R {name:<16} dhat={r['dhat_typed_uniform']:+.5f} "
                  f"pred_sign={r['predicted_typed_sign']:+d} "
                  f"recorded={recorded:+d} ok={r['retro_agrees']}", flush=True)
        except Exception as exc:
            rows.append({"data_id": did, "name": name, "error": str(exc)[:160]})
            notes.append(f"retro {name}: {exc}")  # visible, never silent
            ok = False
    return rows, ok, notes


def phase_prospective() -> tuple[list[dict], dict, bool, bool]:
    rows, scored = [], []
    ids = [i for i in cc18_ids() if i not in V1_IDS]
    print(f"  CC18 registry: {len(ids)} candidate ids after excluding v1's 7", flush=True)
    for did in ids:
        if len(scored) >= PROSPECT_N:
            break
        try:
            Xy = load_openml(did)
        except Exception as exc:
            rows.append({"data_id": did, "error": str(exc)[:160]})
            continue
        if Xy is None:
            continue
        X, y = Xy
        if len(y) < MIN_ROWS:
            continue
        r = run_dataset(X, y, f"openml-{did}", did)
        rows.append(r)
        scored.append(r)
        print(f"  P openml-{did:<8} n={r['n']:<6} dhat={r['dhat_typed_uniform']:+.5f} "
              f"pred={r['predicted_typed_sign']:+d} obs={r['observed_typed_sign']:+d} "
              f"ok={r['sign_agrees']} winner_ok={r['winner_agrees']}", flush=True)
    agree = sum(1 for r in scored if r["sign_agrees"])
    pos = [r for r in scored if r["predicted_typed_sign"] > 0]
    neg = [r for r in scored if r["predicted_typed_sign"] < 0]
    strong_bad = [r for r in scored
                  if r["dhat_typed_uniform"] > 0.005 and r["observed_typed_delta"] < 0]
    stat = {"n_scored": len(scored), "sign_agreements": agree,
            "predicted_pos": len(pos), "predicted_neg": len(neg),
            "strong_contradictions": len(strong_bad)}
    passed = (len(scored) == PROSPECT_N and agree >= 10
              and len(pos) >= 2 and len(neg) >= 2 and not strong_bad)
    return rows, stat, passed, len(scored) == PROSPECT_N


def phase_d4j() -> dict:
    """Retrodict the D4J leg if the metadata cache exists. Never silent.

    The real computation lives in run_d4j_retro_v1.py (runs on the machine
    holding ~/d4j_data.json). Until that sibling exists AND the cache is
    present, this phase reports an explicit skip — unavailable is never
    reported as checked.
    """
    path = Path(os.path.expanduser("~/d4j_data.json"))
    retro = Path(__file__).with_name("run_d4j_retro_v1.py")
    if not path.is_file():
        return {"status": "D4J_SKIPPED_DATA_UNAVAILABLE",
                "reason": "~/d4j_data.json not on this host"}
    if not retro.is_file():
        return {"status": "D4J_SKIPPED_RUNNER_ABSENT",
                "reason": "run_d4j_retro_v1.py not yet written for this host"}
    import subprocess
    proc = subprocess.run([sys.executable, str(retro), "--emit",
                           str(Path(__file__).with_name("RESULTS_D4J_V1.json"))],
                          capture_output=True, text=True, timeout=3600)
    return {"status": "D4J_RAN" if proc.returncode == 0 else "D4J_ERROR",
            "returncode": proc.returncode,
            "tail": (proc.stdout or proc.stderr)[-2000:]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_V1.json")
    a = ap.parse_args()

    here = Path(__file__).parent
    print("Phase R — CC18 retrodiction", flush=True)
    retro_rows, retro_ok, retro_notes = phase_retro()
    print("Phase P — prospective cohort (pre-registered rule)", flush=True)
    pro_rows, pro_stat, pro_ok, pro_complete = phase_prospective()
    print("Phase D — Defects4J (conditional)", flush=True)
    d4j = phase_d4j()

    if not retro_ok:
        terminal, rc = "LAW_FAILS_RETRO", 1
    elif not pro_complete:
        terminal, rc = "P_INCOMPLETE_NO_VERDICT", 3
    elif pro_ok:
        terminal, rc = "LAW_RETRODICTS_AND_PROSPECTS", 0
    else:
        terminal, rc = "LAW_RETRODICTS_ONLY", 2

    def sha(p: str) -> str | None:
        q = here / p
        return hashlib.sha256(q.read_bytes()).hexdigest() if q.is_file() else None

    out = {
        "schema": "ORION08.FINITE_SAMPLE_LAW.v1",
        "protocol_sha256": sha("PROTOCOL_V1.md"),
        "derivation_sha256": sha("DERIVATION_V1.md"),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "node": platform.node()},
        "phase_R": {"rows": retro_rows, "gate_pass": retro_ok, "notes": retro_notes},
        "phase_P": {"rows": pro_rows, "stat": pro_stat, "gate_pass": pro_ok,
                    "complete": pro_complete},
        "phase_D": d4j,
        "terminal": terminal,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"phase_R_gate": retro_ok, "phase_P": pro_stat,
                      "terminal": terminal}, indent=2), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
