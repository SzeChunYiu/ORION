from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
AUTHORITY_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6" / "primary_authority.py"


def load_authority():
    spec = importlib.util.spec_from_file_location("p1_u_r6_primary_authority", AUTHORITY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _arm(choice: str, *, diagnose: bool = True) -> dict[str, object]:
    operators = ["ORION_SOLVE.v1", "FRAME.v1"]
    if diagnose:
        operators.append("DIAGNOSE.v1")
    return {"result": {"choice": choice, "root": {"operator_ids": operators}}}


def _result(terminal: str, *, adverse_difference: bool = True, base_diagnose: bool = True) -> dict[str, object]:
    a = load_authority()
    families = sorted(a.FROZEN_CLASSES)
    pair_rows = []
    global_differences = 0
    for index, family in enumerate(families):
        adverse_native = "UNRESOLVED"
        if adverse_difference and index == 0:
            adverse_native = family
            global_differences += 1
        pair_rows.append({
            "adverse_class": family,
            "members": {
                "adverse": {
                    "native_ard": _arm(adverse_native),
                    "native_base": _arm("UNRESOLVED", diagnose=base_diagnose),
                },
                "control": {
                    "native_ard": _arm("UNRESOLVED"),
                    "native_base": _arm("UNRESOLVED", diagnose=base_diagnose),
                },
            },
        })
    return {
        "schema": "P1U.NativeOrionResult.v1",
        "data": {"complete": True},
        "policy_outcomes_generated": True,
        "terminal": terminal,
        "native_base_choice_differences": global_differences,
        "pair_rows": pair_rows,
        "unresolved_rows": [{
            "native_ard": _arm("UNRESOLVED"),
            "native_base": _arm("UNRESOLVED", diagnose=base_diagnose),
        }],
    }


def test_positive_scientific_primary_stays_cannot_check_for_ablation_authority():
    a = load_authority()
    classified = a.classify_primary_authority(_result(a.PASS_TERMINAL))
    diagnostic = classified["post_outcome_diagnostic_reconstruction"]
    assert classified["scientific_terminal_preserved"] == a.PASS_TERMINAL
    assert classified["authority_terminal"] == a.CANNOT_CHECK_TERMINAL
    assert diagnostic["complete"] is True
    assert diagnostic["diagnostic_only_no_authority"] is True
    assert classified["authority_verifier_bound_before_scientific_outcome"] is False
    assert classified["grants_primary_mechanism_identification_authority"] is False
    assert classified["grants_issue_649_closure_authority"] is False
    assert classified["grants_registry_promotion_authority"] is False


def test_even_clear_adverse_class_differences_cannot_mint_post_outcome_authority():
    a = load_authority()
    classified = a.classify_primary_authority(_result(a.PASS_TERMINAL, adverse_difference=True))
    diagnostic = classified["post_outcome_diagnostic_reconstruction"]
    assert any(diagnostic["ard_vs_base_adverse_choice_differences_by_class"].values())
    assert classified["authority_terminal"] == a.CANNOT_CHECK_TERMINAL
    assert classified["grants_primary_mechanism_identification_authority"] is False


def test_inert_base_is_visible_but_does_not_change_fail_closed_authority():
    a = load_authority()
    classified = a.classify_primary_authority(_result(a.PASS_TERMINAL, base_diagnose=False))
    diagnostic = classified["post_outcome_diagnostic_reconstruction"]
    assert diagnostic["checks"]["base_diagnose_exercised_on_every_episode"] is False
    assert classified["authority_terminal"] == a.CANNOT_CHECK_TERMINAL


def test_reported_global_difference_count_is_still_independently_reconstructed():
    a = load_authority()
    result = _result(a.PASS_TERMINAL)
    result["native_base_choice_differences"] = 99
    classified = a.classify_primary_authority(result)
    diagnostic = classified["post_outcome_diagnostic_reconstruction"]
    assert diagnostic["checks"]["scientific_global_difference_count_reconstructs"] is False
    assert classified["authority_terminal"] == a.CANNOT_CHECK_TERMINAL


def test_negative_frozen_primary_is_not_upgraded():
    a = load_authority()
    classified = a.classify_primary_authority(_result(a.NOT_SUPPORTED_TERMINAL))
    assert classified["scientific_terminal_preserved"] == a.NOT_SUPPORTED_TERMINAL
    assert classified["authority_terminal"] == a.NOT_SUPPORTED_TERMINAL
    assert classified["grants_primary_mechanism_identification_authority"] is False


@pytest.mark.parametrize("mutation", [
    {"schema": "wrong"},
    {"data": {"complete": False}},
    {"policy_outcomes_generated": False},
    {"terminal": "P1_R6_UNKNOWN"},
])
def test_authority_classifier_rejects_malformed_or_unbound_results(mutation):
    a = load_authority()
    result = _result(a.PASS_TERMINAL)
    result.update(mutation)
    with pytest.raises(ValueError):
        a.classify_primary_authority(result)
