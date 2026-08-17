"""Frozen #288 protocol: scientific intent, operational objective, optimizer/evaluator."""
from __future__ import annotations

from pathlib import Path

from orion.goal_evolution.protocol import (
    PROTOCOL_ID,
    LayerKind,
    load_protocol,
    protocol_hash,
    protocol_layers,
)

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = ROOT / "research" / "goal-evolution" / "PROTOCOL_V1.json"


def test_protocol_file_is_design_frozen_and_not_outcome_accessed() -> None:
    protocol = load_protocol()
    assert PROTOCOL_PATH.is_file()
    assert protocol["protocol_id"] == PROTOCOL_ID
    assert protocol["protocol_id"] == "orion.protected-goal-evolution.v1"
    assert protocol["issue"] == 288
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["outcome_accessed"] is False
    assert protocol["scientific_terminal"] == "CANNOT_CHECK"
    assert protocol["v1_protocol_mutated"] is False


def test_protocol_separates_scientific_intent_operational_objective_and_optimizer_evaluator() -> None:
    layers = protocol_layers()
    assert tuple(item.kind for item in layers) == (
        LayerKind.SCIENTIFIC_INTENT,
        LayerKind.OPERATIONAL_OBJECTIVE,
        LayerKind.OPTIMIZER_EVALUATOR,
    )
    intent, objective, machinery = layers
    assert intent.candidate_writable is False
    assert intent.candidate_readable is False
    assert intent.overwrite is False
    assert objective.candidate_writable is False
    assert objective.candidate_proposable is True
    assert objective.overwrite is False
    assert machinery.evaluator_candidate_writable is False
    assert machinery.simultaneous_objective_evaluator_change is False


def test_poor_score_is_declared_insufficient_for_proposal() -> None:
    protocol = load_protocol()
    assert "poor_score_under_old_objective" in protocol["insufficient_for_proposal"]
    assert protocol["process"] == [
        "OBSERVE",
        "DIAGNOSE",
        "DISCRIMINATE",
        "PROPOSE_OBJECTIVE_REVISION",
        "FREEZE",
        "OPTIMIZE",
        "PROTECTED_COMPARE",
        "ADMIT_OR_REJECT",
    ]
    assert protocol["proposal_legal_responsibilities"] == [
        "OBJECTIVE",
        "MEASUREMENT_SPECIFICATION",
    ]


def test_revised_objective_cannot_define_global_positive() -> None:
    protocol = load_protocol()
    assert protocol["global_positive"]["self_definable"] is False
    assert protocol["global_positive"]["external_issue"] == 285
    assert protocol["max_revision_cycles"] >= 1
    assert protocol["max_revision_cycles"] <= 8


def test_protocol_hash_is_stable_content_addressed_commitment() -> None:
    first = protocol_hash()
    second = protocol_hash()
    assert first == second
    assert len(first) == 64
    assert first == protocol_hash(load_protocol())
    mutated = dict(load_protocol())
    mutated["outcome_accessed"] = True
    assert protocol_hash(mutated) != first
