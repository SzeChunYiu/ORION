from __future__ import annotations

from orion.discovery.harness_identifiability import (
    ClaimVariant,
    assess_identifiability,
    assess_precondition,
    clause_witness_map,
    constant_variant,
    distinguishing_cases,
    unattained_clauses,
)


def test_all_positive_suite_cannot_distinguish_target_from_constant_true() -> None:
    cases = ("p1", "p2", "p3")
    target = ClaimVariant("target", {case: True for case in cases})
    constant = constant_variant("always-true", cases, True)
    report = assess_identifiability(
        (target, constant), target_id="target", case_ids=cases
    )
    assert not report.target_identified
    assert report.equivalent_alternative_ids == ("always-true",)
    assert not report.target_outcomes_mixed


def test_one_negative_witness_kills_constant_true_mutation() -> None:
    cases = ("positive", "negative")
    target = ClaimVariant("target", {"positive": True, "negative": False})
    constant = constant_variant("always-true", cases, True)
    report = assess_identifiability(
        (target, constant), target_id="target", case_ids=cases
    )
    assert report.target_identified
    assert report.separated_alternative_ids == ("always-true",)
    assert report.target_outcomes_mixed
    assert distinguishing_cases(target, constant, cases) == ("negative",)


def test_clause_without_witness_is_reported_unattained() -> None:
    cases = ("clean", "blocked")
    target = ClaimVariant("target", {"clean": "PASS", "blocked": "BLOCK"})
    mutations = {
        "blocker-clause": ClaimVariant(
            "drop-blocker", {"clean": "PASS", "blocked": "PASS"}
        ),
        "unused-epoch-clause": ClaimVariant(
            "drop-epoch", {"clean": "PASS", "blocked": "BLOCK"}
        ),
    }
    witnesses = clause_witness_map(target, mutations, cases)
    assert witnesses["blocker-clause"] == ("blocked",)
    assert witnesses["unused-epoch-clause"] == ()
    assert unattained_clauses(target, mutations, cases) == ("unused-epoch-clause",)


def test_precondition_must_have_an_eligible_case() -> None:
    cases = ("sat-1", "sat-2")
    missing = assess_precondition(cases, {case: False for case in cases})
    assert not missing.attained
    present = assess_precondition(cases, {"sat-1": False, "sat-2": True})
    assert present.attained
    assert present.eligible_case_ids == ("sat-2",)


def test_target_can_be_identified_without_entire_family_being_injective() -> None:
    cases = ("a", "b")
    target = ClaimVariant("target", {"a": 0, "b": 1})
    alt1 = ClaimVariant("alt-1", {"a": 1, "b": 1})
    alt2 = ClaimVariant("alt-2", {"a": 1, "b": 1})
    report = assess_identifiability(
        (target, alt1, alt2), target_id="target", case_ids=cases
    )
    assert report.target_identified
    assert not report.family_injective
    assert report.pairwise_indistinguishable == (("alt-1", "alt-2"),)
