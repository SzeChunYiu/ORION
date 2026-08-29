#!/usr/bin/env python3
"""Build anonymous, reader-facing evidence without project identifiers."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-23-responsibility-carrying-state"
TOP = PAPER / "top_tier"
OUTPUT = PAPER / "journal_package/wave1_current/review_materials/evidence.json"


def load_module(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, TOP / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def learned_rows():
    mod = load_module("run_real_responsibility_shift_v1.py", "learned_study")
    bunch = load_digits()
    x = np.asarray(bunch.data, dtype=np.float64)
    y_digit = np.asarray(bunch.target, dtype=int)
    y_parity = y_digit % 2
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20261301)
    policies = ("UNQUALIFIED", "CONFIDENCE_ONLY", "PROVENANCE_ONLY", "ALWAYS_RAW", "RCS")
    public_policy = {
        "UNQUALIFIED": "UNQUALIFIED_REUSE",
        "CONFIDENCE_ONLY": "CONFIDENCE_ONLY",
        "PROVENANCE_ONLY": "PROVENANCE_ONLY",
        "ALWAYS_RAW": "ALWAYS_RAW",
        "RCS": "RESPONSIBILITY_RELATIVE",
    }
    rows = []
    fold_records = []
    for fold, (train_idx, test_idx) in enumerate(cv.split(x, y_digit), 1):
        scaler = StandardScaler().fit(x[train_idx])
        train = scaler.transform(x[train_idx])
        test = scaler.transform(x[test_idx])
        seed = 2026130099 + fold
        parity_model = mod.logistic(seed).fit(train, y_parity[train_idx])
        train_probs = parity_model.predict_proba(train)
        test_probs = parity_model.predict_proba(test)
        parity_pred = np.argmax(test_probs, axis=1).astype(int)
        compact_digit = mod.logistic(seed + 1000).fit(train_probs, y_digit[train_idx]).predict(test_probs).astype(int)
        raw_digit = mod.logistic(seed + 2000).fit(train, y_digit[train_idx]).predict(test).astype(int)
        fold_records.append({
            "fold": fold,
            "train_items": int(len(train_idx)),
            "test_items": int(len(test_idx)),
            "parity_errors": int(np.sum(parity_pred != y_parity[test_idx])),
            "raw_dimension": 64,
            "compact_dimension": 2,
        })
        for local, source_index in enumerate(test_idx):
            probs = test_probs[local]
            for responsibility in ("PARITY", "DIGIT"):
                gold = int(y_parity[source_index]) if responsibility == "PARITY" else int(y_digit[source_index])
                for policy in policies:
                    pred, source, reads, unsupported = mod.decide_policy(
                        policy,
                        "R_PARITY" if responsibility == "PARITY" else "R_DIGIT",
                        probs,
                        int(parity_pred[local]),
                        int(compact_digit[local]),
                        int(raw_digit[local]),
                    )
                    rows.append({
                        "fold": fold,
                        "source_item": int(source_index),
                        "responsibility": responsibility,
                        "policy": public_policy[policy],
                        "gold": gold,
                        "prediction": int(pred),
                        "source": source,
                        "state_values_read": int(reads),
                        "unsupported_reuse": bool(unsupported),
                    })
    return fold_records, rows


def formula_change():
    mod = load_module("run_verifier_responsibility_shift_v1.py", "formula_change_study")
    spec = json.loads((TOP / "p13_verifier_responsibility_cases_v1.json").read_text())
    policies = ("RCS", "ALWAYS_RAW", "CONFIDENCE_ONLY", "PROVENANCE_ONLY")
    public_policy = {"RCS": "RESPONSIBILITY_RELATIVE", **{x: x for x in policies if x != "RCS"}}
    cases, rows = [], []
    for number, case in enumerate(spec["cases"], 1):
        case_key = number
        base = mod.base_cnf(case)
        changed = mod.changed_cnf(case)
        cases.append({
            "case": case_key,
            "variables": int(case["n_vars"]),
            "free_variable": int(case["free_var"]),
            "old_model": list(case["old_model"]),
            "base_formula": base,
            "changed_formula": changed,
        })
        for stage, formula in (("OLD", base), ("CHANGED", changed)):
            for policy in policies:
                if stage == "OLD":
                    prediction = mod.solve(formula, case["n_vars"]) if policy == "ALWAYS_RAW" else list(case["old_model"])
                    reads = mod.raw_reads(formula) if policy == "ALWAYS_RAW" else 0
                    stale = False
                elif policy in ("RCS", "ALWAYS_RAW"):
                    prediction = mod.solve(formula, case["n_vars"])
                    reads = mod.raw_reads(formula)
                    stale = False
                else:
                    prediction = list(case["old_model"])
                    reads = 0
                    stale = True
                rows.append({
                    "case": case_key,
                    "stage": stage,
                    "policy": public_policy[policy],
                    "prediction": prediction,
                    "stale_reuse": stale,
                    "literal_reads": reads,
                })
    return cases, rows


def provenance_comparison():
    mod = load_module("run_d2_donor_baseline_v1.py", "provenance_study")
    spec = json.loads((TOP / "p13_d2_donor_cases_v1.json").read_text())
    public_policy = {
        "D2_CORE": "PROVENANCE_TIER",
        "D2_PLUS": "PROVENANCE_TIER_DEMAND",
        "RCS": "RESPONSIBILITY_RELATIVE",
        "COMPOSED": "COMPOSED_COORDINATES",
        "ALWAYS_RAW": "ALWAYS_RAW",
    }
    cases, rows = [], []
    for number, case in enumerate(spec["cases"], 1):
        key = number
        cases.append({
            "case": key,
            "cell": case["cell"].replace("A_", "").replace("B_", "").replace("C_", "").replace("D_", ""),
            "base_formula": case["base_formula_clauses"],
            "added_clauses": case["added_clauses"],
            "world_formula": case["world_formula_clauses"],
            "stored_model": case["record"]["model"],
            "requested_responsibility_supported": bool(case["gold"]["requested_obligation_supported"]),
        })
        for policy in mod.ARMS:
            answer, reads, solves, served = mod.run_arm(policy, case)
            rows.append({
                "case": key,
                "policy": public_policy[policy],
                "served_compact": bool(served),
                "prediction": answer,
                "literal_reads": int(reads),
                "solver_calls": int(solves),
            })
    return cases, rows


def transport_comparison():
    mod = load_module("run_cert_transport_v1.py", "transport_study")
    spec = json.loads((TOP / "p13_cert_transport_cases_v1.json").read_text())
    public_policy = {
        "UNCONDITIONAL": "UNCONDITIONAL",
        "SIGNATURE_ONLY": "SIGNATURE_EQUALITY",
        "CONDITIONAL_DRIFT_BOUNDED": "LOCAL_DRIFT_BOUND",
        "ALWAYS_RE_ISSUE": "ALWAYS_REISSUE",
    }
    cases, rows = [], []
    for number, case in enumerate(spec["cases"], 1):
        key = number
        cases.append({
            "case": key,
            "stratum": case["stratum"],
            "source_formula": case["source_formula_clauses"],
            "shifted_formula": case["shifted_formula_clauses"],
            "added_clauses": case["added_clauses"],
            "removed_clauses": case["removed_clauses"],
            "stored_model": case["issued_certificate"]["model"],
            "shifted_unsatisfiable": bool(case["gold"]["unsat"]),
        })
        for policy in mod.ARMS:
            transported, answer, unsat_claim, reads, solves = mod.run_arm(policy, case)
            rows.append({
                "case": key,
                "policy": public_policy[policy],
                "transported": bool(transported),
                "prediction": answer,
                "unsatisfiable_claim": bool(unsat_claim),
                "literal_reads": int(reads),
                "solver_calls": int(solves),
            })
    return cases, rows


def main() -> None:
    folds, learned = learned_rows()
    formula_cases, formula_rows = formula_change()
    provenance_cases, provenance_rows = provenance_comparison()
    transport_cases, transport_rows = transport_comparison()
    evidence = {
        "schema": "responsibility_relative_review_data_v1",
        "study_scope": "one learned dataset plus three complete finite constructed panels",
        "learned_data": {
            "source_items": 1797,
            "responsibility_episodes_per_policy": 3594,
            "policy_evaluations": len(learned),
            "folds": folds,
            "rows": learned,
        },
        "verified_responsibility_change": {"cases": formula_cases, "rows": formula_rows},
        "provenance_tier_comparison": {"cases": provenance_cases, "rows": provenance_rows},
        "bounded_drift_transport": {"cases": transport_cases, "rows": transport_rows},
        "retained_adverse_measurement": {
            "enumerated_points": 3840,
            "policy_action_changes_under_certificate_corruption": 2304,
            "positive_independent_harm_opportunities": 0,
            "disposition": "excluded_from_positive_evidence_because_the_harm_label_shared_the_policy_support_bit",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(learned)} learned policy rows and three finite panels to {OUTPUT}")


if __name__ == "__main__":
    main()
