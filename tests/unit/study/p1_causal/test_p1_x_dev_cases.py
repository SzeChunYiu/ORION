from __future__ import annotations

import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P1X = ROOT / "research" / "claim_expansion" / "p1"
GENERATOR = P1X / "generate_p1_x_dev_cases.py"
CHECKER = P1X / "check_p1_x_protocol.py"
PROTOCOL = P1X / "P1_X_PROTOCOL_V1.md"
SCHEMA = P1X / "SCIENTIFIC_REVISION_RESPONSIBILITY_CASE_V1.schema.json"
REGISTRY = P1X / "P1_X_BASELINE_REGISTRY_V1.json"
LEDGER = P1X / "P1_X_CLAIM_EXPANSION_LEDGER_V1.md"

_gen_spec = importlib.util.spec_from_file_location("p1_x_dev_generator", GENERATOR)
assert _gen_spec is not None and _gen_spec.loader is not None
generator = importlib.util.module_from_spec(_gen_spec)
_gen_spec.loader.exec_module(generator)

_check_spec = importlib.util.spec_from_file_location("p1_x_protocol_checker", CHECKER)
assert _check_spec is not None and _check_spec.loader is not None
checker = importlib.util.module_from_spec(_check_spec)
_check_spec.loader.exec_module(checker)


def _protocol_payloads():
    return (
        PROTOCOL.read_text(),
        json.loads(SCHEMA.read_text()),
        json.loads(REGISTRY.read_text()),
        LEDGER.read_text(),
    )


def test_dev_bundle_is_exactly_200_non_authorizing_cases() -> None:
    bundle = generator.generate_dev_bundle()
    assert bundle["authority"] == "NON_AUTHORIZING_DEV"
    assert bundle["case_count"] == 200
    assert len(bundle["cases"]) == 200
    assert len({case["case_id"] for case in bundle["cases"]}) == 200
    assert len({case["seed_commitment"] for case in bundle["cases"]}) == 200


def test_every_domain_archetype_cell_has_five_variants() -> None:
    counts = Counter((case["domain"], case["archetype"]) for case in generator.generate_dev_cases())
    assert len(counts) == 5 * 8
    assert set(counts.values()) == {5}


def test_candidate_visible_payload_never_contains_protected_gold_fields() -> None:
    protected_names = checker.PROTECTED_GOLD_FIELDS
    for case in generator.generate_dev_cases():
        assert not (set(case["candidate_visible"]) & protected_names)


def test_diagnosis_not_prescription_cases_separate_cause_and_intervention() -> None:
    cases = [
        case
        for case in generator.generate_dev_cases()
        if case["archetype"] == "DIAGNOSIS_NOT_PRESCRIPTION"
    ]
    assert cases
    for case in cases:
        gold = case["protected_gold"]
        assert gold["causal_responsibility_set"] != gold["best_intervention_set"]
        assert gold["best_intervention_set"] == gold["scientifically_justified_revision_set"]


def test_incomparable_minima_never_force_a_revision() -> None:
    cases = [
        case
        for case in generator.generate_dev_cases()
        if case["archetype"] == "INCOMPARABLE_MINIMA"
    ]
    assert cases
    for case in cases:
        gold = case["protected_gold"]
        assert gold["ambiguity_state"] == "INCOMPARABLE_MINIMA"
        assert gold["correct_terminal"] == "REQUEST_DISCRIMINATOR"
        assert len(gold["scientifically_justified_revision_set"]) >= 2


def test_preservation_failure_can_restore_target_but_still_be_unjustified() -> None:
    cases = [
        case
        for case in generator.generate_dev_cases()
        if case["archetype"] == "LOCAL_SUCCESS_PRESERVATION_FAILURE"
    ]
    assert cases
    for case in cases:
        gold = case["protected_gold"]
        justified = set(gold["scientifically_justified_revision_set"])
        evaluations = gold["revision_evaluations"]
        bad = [
            item
            for item in evaluations
            if item["restores_target"] and not item["preserves_invariants"]
        ]
        good = [
            item
            for item in evaluations
            if item["candidate_class"] in justified
            and item["restores_target"]
            and item["preserves_invariants"]
        ]
        assert bad
        assert good
        assert all(item["candidate_class"] not in justified for item in bad)


def test_reopen_scope_mismatch_is_candidate_visible_and_gold_is_separate() -> None:
    cases = [
        case
        for case in generator.generate_dev_cases()
        if case["archetype"] == "REOPEN_SCOPE_MISMATCH"
    ]
    assert cases
    for case in cases:
        gold = case["protected_gold"]
        justified_class = gold["scientifically_justified_revision_set"][0]
        proposal = next(
            item
            for item in case["candidate_visible"]["revision_proposals"]
            if item["candidate_class"] == justified_class
        )
        evaluation = next(
            item
            for item in gold["revision_evaluations"]
            if item["candidate_class"] == justified_class
        )
        assert proposal["proposed_reopen_set"] != gold["exact_reopen_set"]
        assert evaluation["observed_reopen_set"] == gold["exact_reopen_set"]
        assert evaluation["restores_target"] is True


def test_clean_control_family_contains_both_no_change_and_cannot_check() -> None:
    terminals = {
        case["protected_gold"]["correct_terminal"]
        for case in generator.generate_dev_cases()
        if case["archetype"] == "CLEAN_OR_INSUFFICIENT_EVIDENCE_CONTROL"
    }
    assert terminals == {"NO_CHANGE", "CANNOT_CHECK"}


def test_schema_requires_protected_revision_evaluations() -> None:
    protocol, schema, registry, ledger = _protocol_payloads()
    mutated = copy.deepcopy(schema)
    mutated["properties"]["protected_gold"]["required"].remove("revision_evaluations")
    errors = checker.validate_protocol(protocol, mutated, registry, ledger)
    assert "protected_gold_missing_required:revision_evaluations" in errors


def test_schema_requires_candidate_revision_proposals() -> None:
    protocol, schema, registry, ledger = _protocol_payloads()
    mutated = copy.deepcopy(schema)
    mutated["properties"]["candidate_visible"]["required"].remove("revision_proposals")
    errors = checker.validate_protocol(protocol, mutated, registry, ledger)
    assert "candidate_visible_missing_revision_proposals" in errors
