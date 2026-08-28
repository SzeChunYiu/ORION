#!/usr/bin/env python3
"""P9 causal-diagnostic transport V3 runner (NR-04 residual revival re-test).

Re-runs the frozen five-cell diagnostic of P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md
under the pre-registered uncertainty-aware transport channel of
P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V3.md. Identical to V2 in every frozen
particular (cells, targets, costs, R=24, seeds, per-draw pipeline); the ONLY
change is the decision rule: an arm reaches the target iff its ensemble 95%
lower confidence bound does. No V1/V2 artifact is edited.

Single targeted script: no pytest, no suite, no xdist. Deterministic.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
PROTOCOL_V3 = HERE / "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V3.md"
PROTOCOL_V2 = HERE / "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V2.md"
COST = {"INFORMATION": 8.0, "ACCESSIBILITY": 2.0, "COMPUTATION": 12.0}
Z = 1.96  # pre-registered: two-sided 95% / one-sided 97.5% normal quantile
R = 24
OUTER0, INNER0 = 20261101, 20261201
ARMS = ("INFORMATION", "ACCESSIBILITY", "COMPUTATION")


def logistic(seed: int) -> LogisticRegression:
    return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)


def reaches(levels_mean: float, levels_sd: float, n: int, target: float) -> bool:
    """Pre-registered uncertainty-aware target satisfaction (V3 protocol)."""
    if n <= 0:
        return False
    se = levels_sd / np.sqrt(n)
    return bool(levels_mean - Z * se >= target)


def choose(means: dict[str, float], sds: dict[str, float], n: int, target: float) -> str:
    good = [(COST[k], k) for k in ARMS if reaches(means[k], sds[k], n, target)]
    return min(good)[1] if good else "CANNOT_CHECK"


def digits_draw_qualities(k: int) -> dict[str, dict[str, dict[str, float]]]:
    """One partition re-draw; full per-arm pipeline re-executed (V2-identical)."""
    b = load_digits()
    X = np.asarray(b.data, dtype=np.float64)
    y = np.asarray(b.target, dtype=int)
    Xtr, Xrem, ytr, yrem = train_test_split(
        X, y, test_size=0.4, random_state=OUTER0 + k, stratify=y
    )
    Xpr, Xte, ypr, yte = train_test_split(
        Xrem, yrem, test_size=0.5, random_state=INNER0 + k, stratify=yrem
    )
    sc = StandardScaler().fit(Xtr)
    ntr, npr, nte = sc.transform(Xtr), sc.transform(Xpr), sc.transform(Xte)

    # D-A: cubic-bijection base; arms per frozen V1 cell.
    ctr, cpr, cte = ntr**3, npr**3, nte**3
    base = logistic(901).fit(ctr, ytr)
    accs = logistic(902).fit(np.cbrt(ctr), ytr)
    comp = SVC(C=1.0, kernel="rbf", gamma="scale").fit(ctr, ytr)
    da_probe = {
        "INFORMATION": accuracy_score(ypr, base.predict(cpr)),
        "ACCESSIBILITY": accuracy_score(ypr, accs.predict(np.cbrt(cpr))),
        "COMPUTATION": accuracy_score(ypr, comp.predict(cpr)),
    }
    da_test = {
        "INFORMATION": accuracy_score(yte, base.predict(cte)),
        "ACCESSIBILITY": accuracy_score(yte, accs.predict(np.cbrt(cte))),
        "COMPUTATION": accuracy_score(yte, comp.predict(cte)),
    }
    da_base_probe = da_probe["INFORMATION"]

    # D-I: one-scalar-intensity base.
    def _col(a: np.ndarray) -> np.ndarray:
        return a.sum(axis=1).reshape(-1, 1)

    str_, spr, ste = _col(Xtr), _col(Xpr), _col(Xte)
    ss = StandardScaler().fit(str_)
    str_, spr, ste = ss.transform(str_), ss.transform(spr), ss.transform(ste)
    base2 = logistic(903).fit(str_, ytr)
    info = logistic(904).fit(ntr, ytr)
    acc2 = logistic(905).fit(np.arcsinh(str_), ytr)
    comp2 = SVC(C=1.0, kernel="rbf", gamma="scale").fit(str_, ytr)
    di_probe = {
        "INFORMATION": accuracy_score(ypr, info.predict(npr)),
        "ACCESSIBILITY": accuracy_score(ypr, acc2.predict(np.arcsinh(spr))),
        "COMPUTATION": accuracy_score(ypr, comp2.predict(spr)),
    }
    di_test = {
        "INFORMATION": accuracy_score(yte, info.predict(nte)),
        "ACCESSIBILITY": accuracy_score(yte, acc2.predict(np.arcsinh(ste))),
        "COMPUTATION": accuracy_score(yte, comp2.predict(ste)),
    }
    di_base_probe = accuracy_score(ypr, base2.predict(spr))

    return {
        "D-A": {"probe": da_probe, "protected": da_test, "base_probe": da_base_probe},
        "D-I": {"probe": di_probe, "protected": di_test, "base_probe": di_base_probe},
    }


def parity(bits: list[int]) -> int:
    return sum(bits) % 2


def exec_quality(task: str, seeds: range) -> dict[str, float]:
    import random

    rows = []
    for seed in seeds:
        r = random.Random(seed)
        if task == "B-I":
            bits = [r.randrange(2) for _ in range(4)]
            gold = parity(bits)
            rows.append((gold, gold, parity(bits[:3]), parity(bits[:3])))
        elif task == "B-A":
            a, b = r.randrange(2), r.randrange(2)
            rows.append((b, a ^ b, b, a ^ (a ^ b)))
        elif task == "B-C":
            x = r.randint(-5, 5)
            maps = [(r.choice((-2, -1, 1, 2)), r.randint(-3, 3)) for _ in range(3)]
            v = x
            for s, o in maps:
                v = s * v + o
            simple = maps[-1][0] * x + maps[-1][1]
            rows.append((v, simple, simple, v))
        else:
            raise ValueError(task)
    return {
        "INFORMATION": sum(g == i for g, i, a, c in rows) / len(rows),
        "ACCESSIBILITY": sum(g == a for g, i, a, c in rows) / len(rows),
        "COMPUTATION": sum(g == c for g, i, a, c in rows) / len(rows),
    }


def main() -> int:
    draws = [digits_draw_qualities(k) for k in range(R)]
    digits_cells = {}
    for task, target in (("D-A", 0.965), ("D-I", 0.95)):
        means = {side: {a: float(np.mean([d[task][side][a] for d in draws])) for a in ARMS}
                 for side in ("probe", "protected")}
        sds = {side: {a: float(np.std([d[task][side][a] for d in draws], ddof=1)) for a in ARMS}
               for side in ("probe", "protected")}
        base_probe_level = float(np.mean([d[task]["base_probe"] for d in draws]))
        half = {}
        for side in ("probe", "protected"):
            for a in ARMS:
                for h in (0, 1):
                    vals = [d[task][side][a] for d in draws[h * (R // 2):(h + 1) * (R // 2)]]
                    half[f"{side}:{a}:{h}"] = {
                        "mean": float(np.mean(vals)),
                        "sd": float(np.std(vals, ddof=1)),
                    }
        digits_cells[task] = {
            "task": task, "domain": "digits", "target": target,
            "probe_levels": means["probe"], "probe_sds": sds["probe"],
            "protected_levels": means["protected"], "protected_sds": sds["protected"],
            "base_probe_level": base_probe_level, "half_draw_levels": half,
        }

    exec_cells = {}
    for task, target in (("B-I", 1.0), ("B-A", 1.0), ("B-C", 1.0)):
        q_probe = exec_quality(task, range(9100, 9200))
        q_prot = exec_quality(task, range(9900, 10000))
        exec_cells[task] = {
            "task": task, "domain": "executable", "target": target,
            "probe_levels": q_probe, "probe_sds": {a: 0.0 for a in q_probe},
            "protected_levels": q_prot, "protected_sds": {a: 0.0 for a in q_prot},
            "base_probe_level": None, "half_draw_levels": None,
        }

    cells = {**digits_cells, **exec_cells}
    order = ("D-A", "D-I", "B-I", "B-A", "B-C")
    rows = []
    for name in order:
        c = cells[name]
        pred = choose(c["probe_levels"], c["probe_sds"], R, c["target"])
        gold = choose(c["protected_levels"], c["protected_sds"], R, c["target"])
        generic = (
            "COMPUTATION"
            if (c["base_probe_level"] is None or c["base_probe_level"] < c["target"])
            else "NO_INTERVENTION"
        )
        predl = None if pred == "CANNOT_CHECK" else (
            c["protected_levels"][pred]
            - Z * c["protected_sds"][pred] / np.sqrt(R)
        )
        rows.append(
            {
                "task": name, "domain": c["domain"], "target": c["target"],
                "probe_levels": c["probe_levels"], "probe_sds": c["probe_sds"],
                "protected_levels": c["protected_levels"], "protected_sds": c["protected_sds"],
                "probe_lcb95": {a: c["probe_levels"][a] - Z * c["probe_sds"][a] / np.sqrt(R) for a in ARMS},
                "protected_lcb95": {a: c["protected_levels"][a] - Z * c["protected_sds"][a] / np.sqrt(R) for a in ARMS},
                "predicted": pred, "protected_gold": gold,
                "probe_protected_decision_agreement": pred == gold,
                "diagnosis_correct": pred == gold,
                "generic_prediction": generic, "generic_correct": generic == gold,
                "false_compute_escalation": pred == "COMPUTATION" and gold != "COMPUTATION",
                "generic_false_compute_escalation": generic == "COMPUTATION" and gold != "COMPUTATION",
                "predicted_protected_lcb95": predl,
                "cost_regret": 0.0 if gold == "CANNOT_CHECK" or pred == "CANNOT_CHECK"
                else COST[pred] - COST[gold],
            }
        )

    # transport-fidelity: half-draw decision stability under the SAME LCB rule,
    # each half deciding only from its own data (V3 protocol, no sd borrowing).
    stability = {}
    for name in ("D-A", "D-I"):
        c = cells[name]
        half_decisions = {}
        for side in ("probe", "protected"):
            for h in (0, 1):
                means = {a: c["half_draw_levels"][f"{side}:{a}:{h}"]["mean"] for a in ARMS}
                sds = {a: c["half_draw_levels"][f"{side}:{a}:{h}"]["sd"] for a in ARMS}
                half_decisions[f"{side}:{h}"] = choose(means, sds, R // 2, c["target"])
        full = {r["task"]: (r["predicted"], r["protected_gold"]) for r in rows}[name]
        stability[name] = {
            "half_decisions": half_decisions,
            "halves_agree_with_full": all(
                half_decisions[f"{side}:{h}"] == full[i]
                for i, side in ((0, "probe"), (1, "protected"))
                for h in (0, 1)
            ),
        }

    acc = sum(r["diagnosis_correct"] for r in rows) / len(rows)
    gacc = sum(r["generic_correct"] for r in rows) / len(rows)
    ex = [r for r in rows if r["domain"] == "executable"]
    dig = [r for r in rows if r["domain"] == "digits"]
    false = sum(r["false_compute_escalation"] for r in rows)
    gfalse = sum(r["generic_false_compute_escalation"] for r in rows)
    mean_regret = sum(r["cost_regret"] for r in rows) / len(rows)
    target_ok = all(
        r["protected_gold"] == "CANNOT_CHECK"
        or (r["predicted_protected_lcb95"] is not None and r["predicted_protected_lcb95"] >= r["target"])
        for r in rows
    )
    decisions_agree = all(r["probe_protected_decision_agreement"] for r in rows)
    halves_stable = all(v["halves_agree_with_full"] for v in stability.values())
    v1_conditions = (
        sum(r["diagnosis_correct"] for r in rows) >= 4
        and acc > gacc
        and all(r["diagnosis_correct"] for r in ex)
        and any(r["diagnosis_correct"] for r in dig)
        and false * 2 <= gfalse
        and target_ok
        and mean_regret <= 1.0
    )
    failing = []
    if not v1_conditions:
        failing.append("v1_mirroring_clauses")
    if not decisions_agree:
        failing.append("probe_protected_decision_agreement")
    if not halves_stable:
        failing.append("half_draw_decision_stability_lcb")
    positive = v1_conditions and decisions_agree and halves_stable

    receipt = {
        "schema": "P9.CausalDiagnosticTransport.v3",
        "protocol_v3_sha256": hashlib.sha256(PROTOCOL_V3.read_bytes()).hexdigest(),
        "protocol_v2_sha256": hashlib.sha256(PROTOCOL_V2.read_bytes()).hexdigest(),
        "decision_rule": {"kind": "ensemble_lcb95", "z": Z, "se": "sd(ddof=1)/sqrt(n_draws)"},
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "transport": {"R": R, "outer_seed0": OUTER0, "inner_seed0": INNER0},
        "task_count": len(rows),
        "diagnosis_accuracy": acc,
        "generic_accuracy": gacc,
        "executable_accuracy": sum(r["diagnosis_correct"] for r in ex) / len(ex),
        "digits_accuracy": sum(r["diagnosis_correct"] for r in dig) / len(dig),
        "false_compute_escalation": false,
        "generic_false_compute_escalation": gfalse,
        "mean_registered_cost_regret": mean_regret,
        "protected_target_reached_by_prediction_lcb": target_ok,
        "probe_protected_decision_agreement_all_cells": decisions_agree,
        "half_draw_decision_stability": stability,
        "half_draw_decision_stability_all_digits": halves_stable,
        "failing_clauses": failing,
        "rows": rows,
        "terminal": "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED"
        if positive
        else "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_GATE_NOT_MET",
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
