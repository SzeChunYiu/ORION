#!/usr/bin/env python3
"""Outcome-blind fixed/development-frozen A4 baseline routers.

Intervention outcome success and causal gold are intentionally absent from every
selection function except intervention_oracle(), which is marked analysis-only
and must run only after unblinding.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

INTERVENTIONS = ("INFORMATION", "ACCESSIBILITY", "COMPUTATION", "RECONSTRUCTION")
CANNOT_CHECK = "METHOD/CANNOT_CHECK"


def _allowed(record: dict[str, Any]) -> tuple[str, ...]:
    allowed = record.get("allowed_interventions")
    if not isinstance(allowed, list) or not allowed:
        return ()
    if len(set(allowed)) != len(allowed) or any(x not in INTERVENTIONS for x in allowed):
        raise ValueError("allowed_interventions is malformed")
    return tuple(allowed)


def _fixed(record: dict[str, Any], intervention: str) -> str:
    return intervention if intervention in _allowed(record) else CANNOT_CHECK


def compute_first(record: dict[str, Any]) -> str:
    return _fixed(record, "COMPUTATION")


def information_first(record: dict[str, Any]) -> str:
    return _fixed(record, "INFORMATION")


def accessibility_first(record: dict[str, Any]) -> str:
    return _fixed(record, "ACCESSIBILITY")


def restart_reformulate_first(record: dict[str, Any]) -> str:
    return _fixed(record, "RECONSTRUCTION")


def random_uniform(record: dict[str, Any]) -> str:
    """Reproducible uniform baseline over allowed interventions, fixed salt."""
    allowed = _allowed(record)
    task_id = record.get("task_id")
    if not allowed or not isinstance(task_id, str) or not task_id:
        return CANNOT_CHECK
    digest = hashlib.sha256(f"A4-RANDOM-V1|{task_id}".encode()).digest()
    return allowed[int.from_bytes(digest[:8], "big") % len(allowed)]


def majority_development(record: dict[str, Any]) -> str:
    """Uses a single cause frozen from the development split, never primary gold."""
    majority = record.get("development_majority_intervention")
    if majority not in INTERVENTIONS:
        return CANNOT_CHECK
    return _fixed(record, majority)


def cheapest_intervention(record: dict[str, Any]) -> str:
    allowed = _allowed(record)
    costs = record.get("declared_intervention_cost_vectors")
    if not allowed or not isinstance(costs, dict):
        return CANNOT_CHECK
    candidates = []
    for iid in allowed:
        vec = costs.get(iid)
        if not isinstance(vec, list) or not vec:
            return CANNOT_CHECK
        clean = []
        for x in vec:
            if isinstance(x, bool) or not isinstance(x, (int, float)) or float(x) < 0:
                return CANNOT_CHECK
            clean.append(float(x))
        candidates.append((tuple(clean), INTERVENTIONS.index(iid), iid))
    candidates.sort()
    return candidates[0][2]


def uncertainty_to_compute(record: dict[str, Any]) -> str:
    """High frozen development uncertainty -> compute, else cheapest available."""
    score = record.get("uncertainty_score")
    threshold = record.get("development_uncertainty_compute_threshold")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return CANNOT_CHECK
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        return CANNOT_CHECK
    if float(score) >= float(threshold):
        return _fixed(record, "COMPUTATION")
    return cheapest_intervention(record)


def learned_router_development_only(record: dict[str, Any]) -> str:
    """Consumes only a precomputed prediction from a hash-bound dev-trained model.

    The inference implementation/model itself must be separately frozen; this
    adapter prevents fallback to primary-gold fitting when prediction is absent.
    """
    if record.get("learned_router_training_split") != "development_only":
        return CANNOT_CHECK
    if not isinstance(record.get("learned_router_model_sha256"), str) or not record["learned_router_model_sha256"]:
        return CANNOT_CHECK
    prediction = record.get("learned_router_prediction")
    if prediction not in INTERVENTIONS:
        return CANNOT_CHECK
    return _fixed(record, prediction)


def intervention_oracle(record: dict[str, Any]) -> str:
    """Analysis only after unblinding; never allowed in candidate feature space."""
    if record.get("oracle_analysis_only_after_unblinding") is not True:
        raise ValueError("intervention oracle may run only after unblinding")
    gold = record.get("gold_cause")
    if gold in INTERVENTIONS or gold == CANNOT_CHECK:
        return gold
    raise ValueError("oracle gold cause missing/invalid")


OUTCOME_BLIND = {
    "COMPUTE_FIRST": compute_first,
    "INFORMATION_FIRST": information_first,
    "ACCESSIBILITY_FIRST": accessibility_first,
    "RESTART_REFORMULATE_FIRST": restart_reformulate_first,
    "RANDOM_UNIFORM": random_uniform,
    "MAJORITY_DEVELOPMENT": majority_development,
    "CHEAPEST_INTERVENTION": cheapest_intervention,
    "UNCERTAINTY_TO_COMPUTE": uncertainty_to_compute,
    "LEARNED_ROUTER_DEVELOPMENT_ONLY": learned_router_development_only,
}


def evaluate_outcome_blind(record: dict[str, Any]) -> dict[str, str]:
    forbidden = {"gold_cause", "intervention_success", "intervention_outcome", "protected_outcome"} & set(record)
    if forbidden:
        raise ValueError(f"protected/gold fields supplied to outcome-blind routers: {sorted(forbidden)}")
    return {name: fn(record) for name, fn in OUTCOME_BLIND.items()}


def self_test() -> dict[str, Any]:
    record = {
        "task_id": "t1",
        "allowed_interventions": list(INTERVENTIONS),
        "development_majority_intervention": "INFORMATION",
        "declared_intervention_cost_vectors": {
            "INFORMATION": [2, 1], "ACCESSIBILITY": [1, 0], "COMPUTATION": [3, 0], "RECONSTRUCTION": [4, 0]
        },
        "uncertainty_score": 0.8,
        "development_uncertainty_compute_threshold": 0.7,
        "learned_router_training_split": "development_only",
        "learned_router_model_sha256": "fixture-model",
        "learned_router_prediction": "RECONSTRUCTION",
    }
    out = evaluate_outcome_blind(record)
    assert out["COMPUTE_FIRST"] == "COMPUTATION"
    assert out["INFORMATION_FIRST"] == "INFORMATION"
    assert out["ACCESSIBILITY_FIRST"] == "ACCESSIBILITY"
    assert out["RESTART_REFORMULATE_FIRST"] == "RECONSTRUCTION"
    assert out["MAJORITY_DEVELOPMENT"] == "INFORMATION"
    assert out["CHEAPEST_INTERVENTION"] == "ACCESSIBILITY"
    assert out["UNCERTAINTY_TO_COMPUTE"] == "COMPUTATION"
    assert out["LEARNED_ROUTER_DEVELOPMENT_ONLY"] == "RECONSTRUCTION"
    assert out["RANDOM_UNIFORM"] in INTERVENTIONS
    bad = dict(record, gold_cause="COMPUTATION")
    try:
        evaluate_outcome_blind(bad)
    except ValueError as exc:
        assert "protected/gold" in str(exc)
    else:
        raise AssertionError("gold leakage into outcome-blind routers was accepted")
    try:
        intervention_oracle({"oracle_analysis_only_after_unblinding": False, "gold_cause": "COMPUTATION"})
    except ValueError:
        pass
    else:
        raise AssertionError("oracle ran before unblinding")
    return {"decision": "GREEN", "outcome_blind_baselines": list(OUTCOME_BLIND), "protected_gold_consumed": False}


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
