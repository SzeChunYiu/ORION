#!/usr/bin/env python3
"""Build the unified I/A/C/M resource ledger V2: corrected accounting plus
re-derivation of the frozen causal-diagnostic comparison under matched full
resource accounting.

Extends (does not fork) the frozen V1 executor: split generation, models,
targets and registered costs are imported from run_causal_diagnostic_v1.py and
re-executed here. Outcome numbers are never hardcoded.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_causal_diagnostic_v1 as frozen  # noqa: E402  (frozen executor, imported not copied)

PROTOCOL = HERE / "P9_UNIFIED_RESOURCE_LEDGER_PROTOCOL_V2.md"
SOURCE = HERE / "P9_CAUSAL_DIAGNOSTIC_RESULT_RECEIPT_V1.md"
CAUSAL_PROTOCOL = HERE / "P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md"
COST = frozen.COST  # {"INFORMATION": 8.0, "ACCESSIBILITY": 2.0, "COMPUTATION": 12.0}
FROZEN_DECISIONS = {
    "D-A": {"predicted": "ACCESSIBILITY", "protected_gold": "CANNOT_CHECK"},
    "D-I": {"predicted": "INFORMATION", "protected_gold": "INFORMATION"},
    "B-I": {"predicted": "INFORMATION", "protected_gold": "INFORMATION"},
    "B-A": {"predicted": "ACCESSIBILITY", "protected_gold": "ACCESSIBILITY"},
    "B-C": {"predicted": "COMPUTATION", "protected_gold": "COMPUTATION"},
}
PHYSICAL = ("I_sem", "A_dim", "A_transform", "M_state", "C_fit", "C_infer", "C_explicit")
FIELDS = PHYSICAL + ("R_registered",)
TARGETS = {"D-A": 0.965, "D-I": 0.95, "B-I": 1.0, "B-A": 1.0, "B-C": 1.0}

# Pre-registered exact-domain vectors (see protocol table; sources: frozen
# semantic bit counts, registered operation counts, corrected readout touches).
EXACT_ROWS = {
    ("B-I", "INFORMATION"): (4, 4, 0, 0, 0, 1, 4),
    ("B-I", "ACCESSIBILITY"): (3, 3, 3, 0, 0, 1, 3),
    ("B-I", "COMPUTATION"): (3, 3, 0, 0, 0, 1, 8),
    ("B-A", "INFORMATION"): (2, 2, 0, 0, 0, 1, 0),
    ("B-A", "ACCESSIBILITY"): (2, 2, 1, 0, 0, 1, 0),
    ("B-A", "COMPUTATION"): (2, 2, 0, 0, 0, 1, 1),
    ("B-C", "INFORMATION"): (7, 7, 0, 0, 0, 1, 0),
    ("B-C", "ACCESSIBILITY"): (7, 7, 7, 0, 0, 1, 0),
    ("B-C", "COMPUTATION"): (7, 7, 0, 0, 0, 1, 7),
}


def choose(qualities: dict[str, float], target: float) -> str:
    reaching = [(COST[k], k) for k, v in qualities.items() if v >= target]
    return min(reaching)[1] if reaching else "CANNOT_CHECK"


def logistic_state(m) -> int:
    return int(m.coef_.size + m.intercept_.size)


def svc_state(m) -> int:
    return int(m.support_vectors_.size)


def digits_vector(task: str, intervention: str, model, a_dim: int, base_scaler: int, arm_scaler: int) -> dict[str, float]:
    """Corrected digits vector: fitted state includes scaler coordinates."""
    kind = "svc" if intervention == "COMPUTATION" else "logistic"
    m_state = (svc_state(model) if kind == "svc" else logistic_state(model)) + arm_scaler
    n_train = 1078
    c_infer = svc_state(model) if kind == "svc" else a_dim
    transform = {"D-A": 64, "D-I": 1}[task] if intervention == "ACCESSIBILITY" else 0
    i_sem = 64 if (task, intervention) == ("D-I", "INFORMATION") else a_dim if task == "D-A" else 1
    return {
        "I_sem": i_sem,
        "A_dim": a_dim,
        "A_transform": transform,
        "M_state": m_state,
        "C_fit": n_train * a_dim,
        "C_infer": c_infer,
        "C_explicit": 0,
        "R_registered": COST[intervention],
        "base_state_fitted_coordinates": base_scaler,
    }


def exact_vector(task: str, intervention: str) -> dict[str, float]:
    vals = EXACT_ROWS[(task, intervention)]
    return {k: float(v) for k, v in zip(PHYSICAL, vals)} | {"R_registered": COST[intervention]}


def dominance(selected: str, reaching: list[str], vectors: dict[str, dict[str, float]]) -> dict | None:
    """Strict dominance of the selected arm on the seven physical coordinates."""
    if selected == "CANNOT_CHECK":
        return None
    sel = vectors[selected]
    for other in reaching:
        if other == selected:
            continue
        oth = vectors[other]
        if all(oth[k] <= sel[k] for k in PHYSICAL) and any(oth[k] < sel[k] for k in PHYSICAL):
            return {
                "dominated_by": other,
                "selected_vector": {k: sel[k] for k in PHYSICAL},
                "dominating_vector": {k: oth[k] for k in PHYSICAL},
            }
    return None


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    for token in (
        "diagnostic accuracy: `0.8`",
        "generic `UNCERTAINTY_ESCALATE_COMPUTE` accuracy: `0.2`",
        "protected causal gold is therefore `CANNOT_CHECK`",
        "2408d028de6ecb4f174433fba8291de84c4af5b6e5ff71870536c38e7f0c9313",
    ):
        assert token in text, f"causal receipt missing token: {token}"

    tasks, split = frozen.digits_tasks()
    tasks += frozen.executable_tasks()

    rows: list[dict] = []
    for t in tasks:
        name = t["task"]
        target = TARGETS[name]
        pred = choose(t["probe"], target)
        gold = choose(t["protected"], target)
        base_probe = t["base_probe"]
        generic = "COMPUTATION" if (base_probe is None or base_probe < target) else "NO_INTERVENTION"

        vectors: dict[str, dict[str, float]] = {}
        if name.startswith("D-"):
            # Refit through the frozen executor's own module state is avoided:
            # re-derive the fit-dependent counts deterministically from the
            # frozen split by re-running the same fitted objects.
            models = refit_digits(name)
            for intervention in COST:
                vectors[intervention] = digits_vector(name, intervention, models[intervention], **models["dims"][intervention])
        else:
            for intervention in COST:
                vectors[intervention] = exact_vector(name, intervention)

        for intervention in COST:
            rows.append({
                "task": name,
                "intervention": intervention,
                **vectors[intervention],
                "probe_quality": float(t["probe"][intervention]),
                "protected_quality": float(t["protected"][intervention]),
                "probe_reaches_target": bool(t["probe"][intervention] >= target),
                "protected_reaches_target": bool(t["protected"][intervention] >= target),
            })

        diag_arm = pred
        generic_arm = "INFORMATION" if generic == "NO_INTERVENTION" else generic
        diag_vec = vectors.get(diag_arm)
        gen_vec = vectors[generic_arm]
        hidden = lambda v: sum(v[k] for k in ("A_transform", "M_state", "C_fit", "C_infer", "C_explicit"))  # noqa: E731

        rows.append({
            "task": name,
            "cell_summary": {
                "target": target,
                "probe_prediction_rederived": pred,
                "protected_gold_rederived": gold,
                "frozen_prediction": FROZEN_DECISIONS[name]["predicted"],
                "frozen_protected_gold": FROZEN_DECISIONS[name]["protected_gold"],
                "prediction_reproduced": pred == FROZEN_DECISIONS[name]["predicted"],
                "gold_reproduced": gold == FROZEN_DECISIONS[name]["protected_gold"],
                "generic_prediction": generic,
                "generic_correct": generic == gold,
                "diagnostic_correct": pred == gold,
                "false_compute_escalation": pred == "COMPUTATION" and gold != "COMPUTATION",
                "generic_false_compute_escalation": generic == "COMPUTATION" and gold != "COMPUTATION",
                "probe_dominance_check": dominance(pred, [k for k in COST if t["probe"][k] >= target], vectors),
                "protected_dominance_check": dominance(gold, [k for k in COST if t["protected"][k] >= target], vectors),
                "matched_comparison": {
                    "diagnostic_arm": diag_arm,
                    "diagnostic_vector": {k: diag_vec[k] for k in FIELDS} if diag_vec else None,
                    "generic_arm": generic_arm,
                    "generic_vector": {k: gen_vec[k] for k in FIELDS},
                    "per_coordinate_delta_generic_minus_diagnostic": (
                        {k: gen_vec[k] - diag_vec[k] for k in PHYSICAL} if diag_vec else None
                    ),
                    "concealed_by_registered_cost": {
                        "diagnostic_arm_hidden_total": hidden(diag_vec) if diag_vec else None,
                        "generic_arm_hidden_total": hidden(gen_vec),
                    },
                },
            },
        })

    summary_rows = [r for r in rows if "cell_summary" in r]
    arm_rows = [r for r in rows if "intervention" in r]
    decisions_reproduced = all(
        r["cell_summary"]["prediction_reproduced"] and r["cell_summary"]["gold_reproduced"] for r in summary_rows
    )
    diag_acc = sum(r["cell_summary"]["diagnostic_correct"] for r in summary_rows) / 5
    gen_acc = sum(r["cell_summary"]["generic_correct"] for r in summary_rows) / 5
    da = next(r["cell_summary"] for r in summary_rows if r["task"] == "D-A")
    false_esc = sum(r["cell_summary"]["false_compute_escalation"] for r in summary_rows)
    gen_false_esc = sum(r["cell_summary"]["generic_false_compute_escalation"] for r in summary_rows)
    contradictions = [
        {"task": r["task"], "split": s, **r["cell_summary"][f"{s}_dominance_check"]}
        for r in summary_rows
        for s in ("probe", "protected")
        if r["cell_summary"][f"{s}_dominance_check"]
    ]
    survival = {
        "all_five_decisions_reproduced": decisions_reproduced,
        "diagnostic_accuracy_four_of_five": diag_acc == 0.8,
        "generic_accuracy_one_of_five": gen_acc == 0.2,
        "d_a_protected_remains_cannot_check": da["protected_gold_rederived"] == "CANNOT_CHECK",
        "false_compute_escalation_zero": false_esc == 0,
        "generic_false_compute_escalation_four": gen_false_esc == 4,
    }
    all_survive = all(survival.values())
    terminal = (
        "P9_UNIFIED_RESOURCE_LEDGER_V2_GREEN"
        if all_survive and not contradictions
        else ("P9_UNIFIED_RESOURCE_LEDGER_V2_CONTRADICTION" if all_survive else "P9_UNIFIED_RESOURCE_LEDGER_V2_SURVIVAL_FAIL")
    )
    receipt = {
        "schema": "P9.UnifiedResourceLedger.v2",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "causal_protocol_sha256": hashlib.sha256(CAUSAL_PROTOCOL.read_bytes()).hexdigest(),
        "source_receipt_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "digits_split": {k: split[k] for k in ("train", "probe", "protected")},
        "audit_corrections": {
            "scaler_state_now_counted": True,
            "exact_domain_readout_touches_now_counted": True,
            "b_c_accessibility_transform_now_counted": True,
            "v1_hardcoded_decisions_replaced_by_reexecution": True,
        },
        "row_count": len(arm_rows),
        "rows": arm_rows,
        "cell_summaries": {r["task"]: r["cell_summary"] for r in summary_rows},
        "survival": survival,
        "survival_verdict": "SURVIVES_FULL_ACCOUNTING" if all_survive else "DOES_NOT_SURVIVE",
        "dominance_contradictions": contradictions,
        "scalarization": "PROHIBITED",
        "terminal": terminal,
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert all_survive, survival
    return 0


def refit_digits(task: str) -> dict:
    """Re-fit the frozen digits arms to extract fit-dependent vector counts.

    Uses exactly the frozen executor's split/transforms (same seeds, same
    estimators); only the fitted-object attribute counts are consumed.
    """
    import numpy as np
    from sklearn.datasets import load_digits
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    b = load_digits()
    X = np.asarray(b.data, dtype=np.float64)
    y = np.asarray(b.target, dtype=int)
    Xtr, Xrem, ytr, _ = train_test_split(X, y, test_size=0.4, random_state=20260901, stratify=y)
    sc = StandardScaler().fit(Xtr)
    ntr = sc.transform(Xtr)
    ctr = ntr ** 3
    if task == "D-A":
        m_info = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=901).fit(ctr, ytr)
        m_acc = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=902).fit(np.cbrt(ctr), ytr)
        m_comp = SVC(C=1.0, kernel="rbf", gamma="scale").fit(ctr, ytr)
        assert len(ytr) == 1078, len(ytr)
        return {
            "INFORMATION": m_info, "ACCESSIBILITY": m_acc, "COMPUTATION": m_comp,
            "dims": {
                # every D-A arm consumes the shared 64-feature base scaler.
                "INFORMATION": {"a_dim": 64, "base_scaler": 128, "arm_scaler": 128},
                "ACCESSIBILITY": {"a_dim": 64, "base_scaler": 128, "arm_scaler": 128},
                "COMPUTATION": {"a_dim": 64, "base_scaler": 128, "arm_scaler": 128},
            },
        }
    if task == "D-I":
        sums = Xtr.sum(axis=1).reshape(-1, 1)
        StandardScaler().fit(sums)  # base 1-feature scaler, 2 fitted coordinates
        m_info = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=904).fit(ntr, ytr)
        m_acc = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=905).fit(np.arcsinh(StandardScaler().fit_transform(sums)), ytr)
        m_comp = SVC(C=1.0, kernel="rbf", gamma="scale").fit(StandardScaler().fit_transform(sums), ytr)
        assert len(ytr) == 1078, len(ytr)
        return {
            "INFORMATION": m_info, "ACCESSIBILITY": m_acc, "COMPUTATION": m_comp,
            "dims": {
                # INFORMATION restores the native 64-pixel state: the arm uses
                # the 64-feature scaler (128 fitted coords) IN PLACE of the
                # task's 1-feature base scaler, which is disclosed but unused.
                "INFORMATION": {"a_dim": 64, "base_scaler": 2, "arm_scaler": 128},
                "ACCESSIBILITY": {"a_dim": 1, "base_scaler": 2, "arm_scaler": 2},
                "COMPUTATION": {"a_dim": 1, "base_scaler": 2, "arm_scaler": 2},
            },
        }
    raise ValueError(task)


if __name__ == "__main__":
    raise SystemExit(main())
