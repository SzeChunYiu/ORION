from orion.foundations.integrity import (
    AdoptionWorld,
    EvolutionCertificate,
    AdvanceCase,
    ExecutionScienceCase,
    black_box_synthesis_verification_gap,
    candidate_only_adoption_is_identifying,
    coupled_advance_separations,
    integrity_does_not_identify_science,
    protected_adoption_is_identifying,
)
from orion.foundations.model import ExecutionIntegrity, Terminal


def test_integrity_is_not_scientific_validity() -> None:
    integrity = ExecutionIntegrity(attributable=True, content_bound=True, attested=True)
    cases = (
        ExecutionScienceCase("good", integrity, Terminal.ESTABLISH),
        ExecutionScienceCase("bad", integrity, Terminal.BLOCK),
    )
    assert integrity_does_not_identify_science(cases)


def test_protected_adoption_breaks_candidate_visible_collision() -> None:
    worlds = (
        AdoptionWorld("good", "pass", "fresh-pass", True),
        AdoptionWorld("gaming", "pass", "fresh-fail", False),
    )
    assert not candidate_only_adoption_is_identifying(worlds)
    assert protected_adoption_is_identifying(worlds)


def test_reachability_and_admissibility_are_non_substitutable() -> None:
    cases = (
        AdvanceCase("tt", True, True),
        AdvanceCase("tf", True, False),
        AdvanceCase("ft", False, True),
        AdvanceCase("ff", False, False),
    )
    assert coupled_advance_separations(cases)


def test_governed_evolution_and_synthesis_checking_gap() -> None:
    certificate = EvolutionCertificate(
        "issue", "diagnosis", "candidate", "isolation", "replay",
        "fresh", "assurance", "history", "external-adoption"
    )
    assert certificate.valid
    assert black_box_synthesis_verification_gap(8) == (8, 1)
