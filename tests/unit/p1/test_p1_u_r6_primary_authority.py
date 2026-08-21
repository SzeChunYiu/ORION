from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
AUTHORITY_PATH = (
    ROOT
    / "research"
    / "claim_expansion"
    / "p1"
    / "gpt_r6"
    / "primary_authority.py"
)


def load_authority():
    spec = importlib.util.spec_from_file_location("p1_u_r6_primary_authority", AUTHORITY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _result(terminal: str) -> dict[str, object]:
    return {
        "schema": "P1U.NativeOrionResult.v1",
        "data": {"complete": True},
        "policy_outcomes_generated": True,
        "terminal": terminal,
        # A large global choice-difference count must not recover missing
        # protected-family/materiality authority.
        "native_base_choice_differences": 52,
    }


def test_positive_frozen_primary_fails_closed_for_mechanism_authority():
    a = load_authority()
    classified = a.classify_primary_authority(_result(a.PASS_TERMINAL))
    assert classified["scientific_terminal_preserved"] == a.PASS_TERMINAL
    assert classified["authority_terminal"] == a.CANNOT_CHECK_TERMINAL
    assert classified["historic_scores_mutated"] is False
    assert classified["thresholds_mutated"] is False
    assert classified["grants_primary_superiority_authority"] is False
    assert classified["grants_replication_closure_authority"] is False
    assert classified["grants_registry_promotion_authority"] is False
    assert classified["requires_prospective_successor_for_mechanism_identification"] is True


def test_negative_frozen_primary_is_not_upgraded():
    a = load_authority()
    classified = a.classify_primary_authority(_result(a.NOT_SUPPORTED_TERMINAL))
    assert classified["scientific_terminal_preserved"] == a.NOT_SUPPORTED_TERMINAL
    assert classified["authority_terminal"] == a.NOT_SUPPORTED_TERMINAL
    assert classified["grants_primary_superiority_authority"] is False
    assert classified["requires_prospective_successor_for_mechanism_identification"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        {"schema": "wrong"},
        {"data": {"complete": False}},
        {"policy_outcomes_generated": False},
        {"terminal": "P1_R6_UNKNOWN"},
    ],
)
def test_authority_classifier_rejects_malformed_or_unbound_results(mutation):
    a = load_authority()
    result = _result(a.PASS_TERMINAL)
    result.update(mutation)
    with pytest.raises(ValueError):
        a.classify_primary_authority(result)
