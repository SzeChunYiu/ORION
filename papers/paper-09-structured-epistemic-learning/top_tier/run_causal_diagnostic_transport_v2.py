#!/usr/bin/env python3
"""P9 causal-diagnostic transport V2 runner (NR-04 revival re-test).

Re-runs the frozen five-cell diagnostic of P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md
under the pre-registered ensemble-level transport channel of
P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V2.md. No V1 artifact is edited.

Single targeted script: no pytest, no suite, no xdist. Deterministic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import platform
import sklearn
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
PROTOCOL_V2 = HERE / "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V2.md"
COST = {"INFORMATION": 8.0, "ACCESSIBILITY": 2.0, "COMPUTATION": 12.0}
R = 24
OUTER0, INNER0 = 20261101, 20261201


def logistic(seed: int) -> LogisticRegression:
    return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)


def choose(levels: dict[str, float], target: float) -> str:
    good = [(COST[k], k) for k, v in levels.items() if v >= target]
    return min(good)[1] if good else "CANNOT_CHECK"


def digits_draw_qualities(k: int) -> dict[str, dict[str, dict[str, float]]]:
    """One partition re-draw; full per-arm pipeline re-executed.

    Returns {"D-A": {"probe": {...}, "protected": {...}, "base_probe": f}, ...}
    """
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
    # --- digits: R frozen re-draws --------------------------------------
    draws = [digits_draw_qualities(k) for k in range(R)]
    digits_cells = {}
    for task, target in (("D-A", 0.965), ("D-I", 0.95)):
        arms = ("INFORMATION", "ACCESSIBILITY", "COMPUTATION")
        probe_levels = {a: float(np.mean([d[task]["probe"][a] for d in draws])) for a in arms}
        prot_levels = {a: float(np.mean([d[task]["protected"][a] for d in draws])) for a in arms}
        base_probe_level = float(np.mean([d[task]["base_probe"] for d in draws]))
        per_draw_sd = {
            a: float(np.std([d[task]["protected"][a] for d in draws], ddof=1)) for a in arms
        }
        half_levels = {}
        for side in ("probe", "protected"):
            for a in arms:
                h0 = float(np.mean([d[task][side][a] for d in draws[: R // 2]]))
                h1 = float(np.mean([d[task][side][a] for d in draws[R // 2 :]]))
                half_levels[f"{side}:{a}:0"] = h0
                half_levels[f"{side}:{a}:1"] = h1
        digits_cells[task] = {
            "task": task,
            "domain": "digits",
            "target": target,
            "probe_levels": probe_levels,
            "protected_levels": prot_levels,
            "base_probe_level": base_probe_level,
            "per_draw_protected_sd": per_draw_sd,
            "half_draw_levels": half_levels,
        }

    # --- executable cells: identity channel ------------------------------
    exec_cells = {}
    for task, target in (("B-I", 1.0), ("B-A", 1.0), ("B-C", 1.0)):
        q_probe = exec_quality(task, range(9100, 9200))
        q_prot = exec_quality(task, range(9900, 10000))
        exec_cells[task] = {
            "task": task,
            "domain": "executable",
            "target": target,
            "probe_levels": q_probe,
            "protected_levels": q_prot,
            "base_probe_level": None,
            "per_draw_protected_sd": {a: 0.0 for a in q_probe},
            "half_draw_levels": None,
        }

    cells = {**digits_cells, **exec_cells}
    order = ("D-A", "D-I", "B-I", "B-A", "B-C")
    rows = []
    for name in order:
        c = cells[name]
        pred = choose(c["probe_levels"], c["target"])
        gold = choose(c["protected_levels"], c["target"])
        generic = (
            "COMPUTATION"
            if (c["base_probe_level"] is None or c["base_probe_level"] < c["target"])
            else "NO_INTERVENTION"
        )
        predq = None if pred == "CANNOT_CHECK" else c["protected_levels"][pred]
        rows.append(
            {
                "task": name,
                "domain": c["domain"],
                "target": c["target"],
                "probe_levels": c["probe_levels"],
                "protected_levels": c["protected_levels"],
                "per_draw_protected_sd": c["per_draw_protected_sd"],
                "half_draw_levels": c["half_draw_levels"],
                "predicted": pred,
                "protected_gold": gold,
                "probe_protected_decision_agreement": pred == gold,
                "diagnosis_correct": pred == gold,
                "generic_prediction": generic,
                "generic_correct": generic == gold,
                "false_compute_escalation": pred == "COMPUTATION" and gold != "COMPUTATION",
                "generic_false_compute_escalation": generic == "COMPUTATION"
                and gold != "COMPUTATION",
                "predicted_protected_level": predq,
                "cost_regret": 0.0
                if gold == "CANNOT_CHECK" or pred == "CANNOT_CHECK"
                else COST[pred] - COST[gold],
            }
        )

    # transport-fidelity: half-draw decision stability (digits cells)
    stability = {}
    for name in ("D-A", "D-I"):
        c = cells[name]
        half_decisions = {}
        for side in ("probe", "protected"):
            for h in (0, 1):
                lv = {
                    a: c["half_draw_levels"][f"{side}:{a}:{h}"]
                    for a in ("INFORMATION", "ACCESSIBILITY", "COMPUTATION")
                }
                half_decisions[f"{side}:{h}"] = choose(lv, c["target"])
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
        or (r["predicted_protected_level"] is not None and r["predicted_protected_level"] >= r["target"])
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
    positive = v1_conditions and decisions_agree and halves_stable

    receipt = {
        "schema": "P9.CausalDiagnosticTransport.v2",
        "protocol_v2_sha256": hashlib.sha256(PROTOCOL_V2.read_bytes()).hexdigest(),
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
        "protected_target_reached_by_prediction": target_ok,
        "probe_protected_decision_agreement_all_cells": decisions_agree,
        "half_draw_decision_stability": stability,
        "half_draw_decision_stability_all_digits": halves_stable,
        "rows": rows,
        "terminal": "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_SUPPORTED"
        if positive
        else "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET",
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
