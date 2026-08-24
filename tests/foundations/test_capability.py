from fractions import Fraction

from orion.foundations.capability import (
    AllocationWorld,
    DiagnosticModel,
    MethodLanguage,
    MethodRule,
    PlacementLaw,
    allocation_certificate_sufficient,
    certify_expansion,
    certify_obstruction,
)


def test_diagnostic_identifiability_and_ambiguity() -> None:
    model = DiagnosticModel(
        causes=("information", "compute"),
        interventions=("acquire", "scale"),
        signatures={"information": (1, 0), "compute": (0, 1)},
    )
    assert model.identifiable()
    assert model.minimal_intervention_set() == ("acquire",)
    assert model.compatible_causes({}) == frozenset({"information", "compute"})


def test_exact_obstruction_and_expansion() -> None:
    old = MethodLanguage("old", frozenset({"x"}), (MethodRule(frozenset({"x"}), "linear"),))
    new = MethodLanguage(
        "new",
        frozenset({"x", "square"}),
        old.rules + (MethodRule(frozenset({"square", "x"}), "quadratic"),),
    )
    assert certify_obstruction(old, "quadratic").valid
    assert certify_expansion(old, new, "square", "quadratic", ()).valid


def test_break_even_law() -> None:
    law = PlacementLaw(Fraction(100), Fraction(10), Fraction(2))
    assert law.break_even_horizon() == 13
    assert not law.compiled_is_cheaper(12)
    assert law.compiled_is_cheaper(13)


def test_coarsened_allocation_certificate_is_insufficient() -> None:
    worlds = (
        AllocationWorld("a", "same", "STATE"),
        AllocationWorld("b", "same", "REASON"),
    )
    assert not allocation_certificate_sufficient(worlds)
